from pyrogram import Client
from config import Config
from logger import LOGGER
from asyncio import gather, create_task
from os import environ

# Main bot - handles user interactions
MainBot = Client(
    name='main_bot',
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.MAIN_BOT_TOKEN,
    plugins={"root": "plugins"},
    sleep_threshold=100,
    workers=6,
    max_concurrent_transmissions=10
)

# Worker bots - handle streaming (load balancing)
WorkerBots = {}
WorkLoads = {}

class TokenParser:
    """Parse worker bot tokens from environment or config"""
    @staticmethod
    def parse_from_config():
        """Parse tokens from Config.WORKER_BOTS list"""
        tokens = {
            c + 1: t
            for c, t in enumerate(Config.WORKER_BOTS)
            if t.strip()
        }
        return tokens
    
    @staticmethod
    def parse_from_env():
        """Parse tokens from environment variables (MULTI_TOKEN1, MULTI_TOKEN2, etc.)"""
        tokens = {
            c + 1: t
            for c, (_, t) in enumerate(
                filter(
                    lambda n: n[0].startswith("MULTI_TOKEN"), 
                    sorted(environ.items())
                )
            )
        }
        return tokens

async def start_client(client_id, token):
    """Start a single worker bot client"""
    try:
        LOGGER.info(f"Starting Worker Bot {client_id}...")
        client = await Client(
            name=f"worker_{client_id}",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=token,
            sleep_threshold=100,
            no_updates=True,
            in_memory=True
        ).start()
        WorkLoads[client_id] = 0
        LOGGER.info(f"✅ Worker Bot {client_id} started: @{client.me.username}")
        return client_id, client
    except Exception as e:
        LOGGER.error(f"❌ Failed to start Worker Bot {client_id}: {e}", exc_info=True)
        return None

async def initialize_workers():
    """Initialize all worker bot clients with load balancing"""
    # MainBot is worker 0
    WorkerBots[0] = MainBot
    WorkLoads[0] = 0
    
    # Get tokens from config or environment
    all_tokens = TokenParser.parse_from_config()
    if not all_tokens:
        all_tokens = TokenParser.parse_from_env()
    
    if not all_tokens:
        LOGGER.info("⚠️  No additional worker bots found, using only main bot for streaming")
        return
    
    LOGGER.info(f"🔄 Initializing {len(all_tokens)} worker bots...")
    
    # Start all worker bots concurrently
    tasks = [create_task(start_client(i, token)) for i, token in all_tokens.items()]
    clients = await gather(*tasks)
    
    # Filter out failed clients
    clients = {client_id: client for client_id, client in clients if client}
    WorkerBots.update(clients)
    
    if len(WorkerBots) > 1:
        LOGGER.info(f"🚀 Multi-Client Mode Enabled with {len(WorkerBots)} total bots")
    else:
        LOGGER.info("⚠️  No additional worker bots initialized, using only main bot")

def get_least_loaded_bot():
    """Get the worker bot with least load for load balancing"""
    if not WorkLoads:
        return None
    return min(WorkLoads, key=WorkLoads.get)
