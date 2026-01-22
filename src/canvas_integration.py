"""Module for integrating with the Canvas API to manage course content."""

import canvasapi
import config


class CanvasIntegration:
    """Integrates with the Canvas API to manage course content."""

    def __init__(self, api_url, api_key, course_id):
        self.canvas = canvasapi.Canvas(api_url, api_key)
        self._set_course(course_id)

    def _set_course(self, course_id: int) -> None:
        """Sets the course for the integration.

        Args:
            course_id (int): The ID of the course to integrate with.
        """

        self.course_id = course_id
        self.course = self.canvas.get_course(self.course_id)

    def get_announcements(self) -> list:
        """Retrieves announcements for the course.

        Returns:
            list: A list of announcements for the course.
        """

        # Fetch announcements for the course
        course_text = f"course_{self.course_id}"
        announcements = self.canvas.get_announcements(
            context_codes=[course_text], active_only=True
        )

        # Convert announcements from paginated list to regular list
        return list(announcements)


if __name__ == "__main__":
    # Example usage

    # Initialize Canvas integration
    canvas = CanvasIntegration(
        config.CANVAS_URL, config.CANVAS_TOKEN, config.COURSE_CODE_3203
    )

    # Fetch and print announcements
    course_announcements = canvas.get_announcements()
    for announcement in course_announcements:
        print(f"Announcement Title: {announcement.title}")
        print(f"Announcement Text: {announcement.message}\n")
