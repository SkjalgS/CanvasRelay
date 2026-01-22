"""Configuration settings for DiscordCanvas application."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")

CANVAS_URL = "https://uit.instructure.com"
COURSE_CODE_3203 = 41013

# Maximum message length for Discord messages (Discord limit is 2000)
MAX_MESSAGE_LENGTH = 1900
STUDENT_ROLE_ID = 1463495777665159304

# Relation between discord channels and courses
CHANNEL_COURSES = {1462804673764528446: [COURSE_CODE_3203]}

COURSE_NAMES = {COURSE_CODE_3203: "INF-3203"}
