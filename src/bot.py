"""Discord bot that integrates with Canvas to provide announcements."""

import asyncio
import logging
import datetime
import sys

import discord
import html2text

import config
from canvas_integration import CanvasIntegration

# Configure dual logging: console (for Docker) + file (for local debugging)
console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("app.log")

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])

log = logging.getLogger(__name__)


class CanvasRelay(discord.Client):
    """Discord bot that integrates with Canvas to provide announcements."""

    def __init__(self):
        log.info("Initializing Bot...")

        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.files = {}
        self.announcements = {}
        self.courses = {}
        self.course_names = config.COURSE_NAMES
        self._set_channels(config.CHANNEL_COURSES)
        self._tasks_started = False

        self.converter = html2text.HTML2Text()
        self.converter.body_width = 0
        self.converter.ignore_links = False

        self.canvas_courses: dict[str, CanvasIntegration] = {}
        self.seen_announcements: set[int] = set()

    def _set_channels(self, channels: dict) -> None:
        """Initialize the internal course-to-channel mapping.

        Args:
            channels (dict): Discord channel IDs mapped to lists of Canvas course IDs.
        """
        self.channels = channels

        # Invert the mapping to get courses to channels
        for channel, course_list in self.channels.items():
            for course in course_list:
                self.courses.setdefault(course, []).append(channel)
                log.info("Registered channel %s for course %s", channel, course)

    async def _sleep_until_next_minute(self) -> None:
        """Sleep until the start of the next minute."""

        # Get current time and calculate next minute
        now = datetime.datetime.now(datetime.timezone.utc)
        next_minute = (now + datetime.timedelta(minutes=1)).replace(
            second=0, microsecond=0
        )

        # Calculate sleep duration and sleep
        wait_seconds = max(0, (next_minute - now).total_seconds())
        await asyncio.sleep(wait_seconds)

    async def on_ready(self) -> None:
        """Called when the bot is ready and connected to Discord"""
        log.info("Bot connected as %s", self.user)

        # Start background tasks once after ready
        if not self._tasks_started:
            self.loop.create_task(self.check_canvas())
            self._tasks_started = True

    async def check_canvas(self) -> None:
        """Periodically check Canvas and send updates to Discord channels."""
        await self.wait_until_ready()

        # Initialize Canvas integrations for each course
        self.canvas_courses = {
            course_id: CanvasIntegration(
                config.CANVAS_URL,
                config.CANVAS_TOKEN,
                course_id,
            )
            for course_id in self.courses
        }

        # Initialize seen announcements to avoid duplicates on startup
        await self._initialize_seen_announcements()

        # Main loop to check for announcements
        while not self.is_closed():
            log.info("Starting Canvas check cycle...")
            try:
                await self.check_announcements()
            except Exception as e:
                log.exception("Error occurred while checking Canvas: %s", e)

            await self._sleep_until_next_minute()

    async def check_announcements(self) -> None:
        """Check for new announcements periodically and send them to Discord channels."""
        log.info("Checking for new announcements...")

        # Iterate through each course and its associated channels
        for course_id, channel_ids in self.courses.items():
            announcements = self.canvas_courses[course_id].get_announcements()

            # Process each announcement
            for announcement in announcements:
                # Skip already seen announcements
                if announcement.id in self.seen_announcements:
                    continue

                # Get announcement details
                title = announcement.title
                raw_message = announcement.message
                url = announcement.url
                course_name = self.course_names.get(course_id, f"Course {course_id}")

                # Format the announcement message
                message = self._format_announcement_message(
                    course_name, title, raw_message, url
                )

                # Send the announcement to all associated channels
                for channel_id in channel_ids:
                    channel = self.get_channel(channel_id)
                    if channel is not None:
                        await channel.send(message)
                        log.info(
                            'Sent announcement "%s" to channel "%s" (ID: %s)',
                            title,
                            channel.name,
                            channel.id,
                        )
                    else:
                        log.warning("Channel %s not found", channel_id)

                # Mark the announcement as seen
                self.seen_announcements.add(announcement.id)

    async def _initialize_seen_announcements(self) -> None:
        """Initialize the set of seen announcements to avoid duplicates on startup."""
        log.info("Fetching existing announcements...")

        if not self.canvas_courses:
            log.warning("Canvas courses not initialized yet.")
            return

        # Iterate through each course to fetch existing announcements
        for course_id in self.courses:
            # Fetch announcements for each course
            announcements = self.canvas_courses[course_id].get_announcements()

            # Mark all existing announcements as seen
            for announcement in announcements:
                self.seen_announcements.add(announcement.id)

        log.info(
            "Initialized seen announcements with %d entries",
            len(self.seen_announcements),
        )

    def _format_announcement_message(
        self, course_name: str, title: str, raw_message: str, url: str | None
    ) -> str:
        """Format the announcement message for Discord.

        Args:
            course_name (str): Course name
            title (str): Message title
            raw_message (str): Raw HTML message
            url (str | None): Announcement URL

        Returns:
            str: Formatted announcement message
        """

        # Create header, message body, and footer
        header = (
            f"<@&{config.STUDENT_ROLE_ID}>\n"
            f"**New Announcement in {course_name}**\n\n"
            f"**{title}**\n\n"
        )
        canvas_message = self.converter.handle(raw_message).strip()
        footer = f"\n\n[View Announcement]({url})" if url else ""

        # Check if the full message exceeds the maximum length
        full_message = f"{header}{canvas_message}{footer}"
        if len(full_message) > config.MAX_MESSAGE_LENGTH:
            truncation_suffix = "...\n\n[MESSAGE TRUNCATED]"

            # Calculate available length for the canvas message
            available_length = (
                config.MAX_MESSAGE_LENGTH
                - len(header)
                - len(footer)
                - len(truncation_suffix)
            )

            # Truncate the canvas message accordingly
            canvas_message = (
                canvas_message[:available_length].rstrip() + truncation_suffix
            )

        return f"{header}{canvas_message}{footer}"


if __name__ == "__main__":
    # Initialize and run the Discord bot
    client = CanvasRelay()
    client.run(config.DISCORD_TOKEN)
