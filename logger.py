import logging
from logging import getLogger, FileHandler, StreamHandler, INFO, ERROR, Formatter, basicConfig
from datetime import datetime
import pytz

# Set timezone (you can change this to your timezone)
TIMEZONE = pytz.timezone("UTC")  # or "Asia/Kolkata", "America/New_York", etc.

class TimezoneFormatter(Formatter):
    """Custom formatter with timezone support"""
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, TIMEZONE)
        return dt.strftime(datefmt or "%d-%b-%y %I:%M:%S %p")

# File and console handlers
file_handler = FileHandler("bot.log")
stream_handler = StreamHandler()

# Custom formatter
formatter = TimezoneFormatter(
    "[%(asctime)s] [%(levelname)s] - %(name)s - %(message)s", 
    "%d-%b-%y %I:%M:%S %p"
)

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Basic config
basicConfig(
    handlers=[file_handler, stream_handler],
    level=INFO
)

# Reduce noise from third-party libraries
getLogger("httpx").setLevel(ERROR)
getLogger("pyrogram").setLevel(ERROR)
getLogger("fastapi").setLevel(ERROR)
getLogger("uvicorn").setLevel(ERROR)
getLogger("uvicorn.access").setLevel(ERROR)

# Main logger
LOGGER = getLogger(__name__)
LOGGER.setLevel(INFO)

LOGGER.info(f"Logger initialized with {TIMEZONE.zone} timezone")
