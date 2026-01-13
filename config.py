from os import getenv
from dotenv import load_dotenv

load_dotenv("config.env")

class Config:
    # Telegram API credentials
    API_ID = int(getenv("API_ID", "0"))
    API_HASH = getenv("API_HASH", "")
    
    # Bot tokens
    MAIN_BOT_TOKEN = getenv("MAIN_BOT_TOKEN", "")
    WORKER_BOTS = [token.strip() for token in getenv("WORKER_BOTS", "").split(",") if token.strip()]
    
    # Dump channel
    DUMP_CHANNEL = int(getenv("DUMP_CHANNEL", "0"))
    
    # Server configuration
    BASE_URL = getenv("BASE_URL", "").rstrip('/')
    PORT = int(getenv("PORT", "8000"))
    
    # Owner ID (for admin commands)
    OWNER_ID = int(getenv("OWNER_ID", "0"))
