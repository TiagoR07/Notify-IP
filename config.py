import logging
import os
import platform
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
USER_ID_RAW = os.getenv("DISCORD_USER_ID", "").strip()

if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN in environment")

if not USER_ID_RAW.isdigit():
    raise RuntimeError("DISCORD_USER_ID must be a valid number")

USER_ID = int(USER_ID_RAW)
IS_WINDOWS = platform.system() == "Windows"

logger.info("Bot starting...")
logger.info(f"Platform: {platform.system()}")
logger.info(f"User ID: {USER_ID}")