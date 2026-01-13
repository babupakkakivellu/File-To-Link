import asyncio
from asyncio import sleep as asleep
from traceback import format_exc
from pyrogram import idle
import logging

from logger import LOGGER
from bot import MainBot, WorkerBots, initialize_workers
from config import Config

# Version
__version__ = "1.0.0"

async def start_services():
    """Start all services in proper sequence"""
    try:
        LOGGER.info(f"🚀 Initializing File-to-Link Bot v{__version__}")
        await asleep(1)
        
        # Start main bot
        LOGGER.info("Starting main bot...")
        await MainBot.start()
        MainBot.username = MainBot.me.username
        LOGGER.info(f"✅ Main Bot: @{MainBot.username}")
        await asleep(1)
        
        # Initialize worker bots
        LOGGER.info("Initializing worker bots for load balancing...")
        await initialize_workers()
        await asleep(1.5)
        
        # Start FastAPI server
        LOGGER.info('Starting FastAPI web server...')
        from server import start_server
        server = start_server()
        asyncio.create_task(server.serve())
        await asleep(1)
        
        # Start health ping (keep-alive)
        if Config.BASE_URL:
            LOGGER.info("Starting health check service...")
            asyncio.create_task(health_ping())
        
        LOGGER.info("="*50)
        LOGGER.info(f"✅ File-to-Link Bot Started Successfully!")
        LOGGER.info(f"📡 Base URL: {Config.BASE_URL}")
        LOGGER.info(f"🔧 Port: {Config.PORT}")
        LOGGER.info(f"📂 Dump Channel: {Config.DUMP_CHANNEL}")
        LOGGER.info(f"🤖 Worker Bots: {len(WorkerBots)}")
        LOGGER.info("="*50)
        
        # Keep running
        await idle()
        
    except Exception as e:
        LOGGER.error(f"❌ Error during startup:\n{format_exc()}")
        raise

async def stop_services():
    """Stop all services gracefully"""
    try:
        LOGGER.info("⏸️  Stopping services...")
        
        # Cancel all pending tasks
        pending_tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in pending_tasks:
            task.cancel()
        
        await asyncio.gather(*pending_tasks, return_exceptions=True)
        
        # Stop main bot
        await MainBot.stop()
        LOGGER.info("✅ Main bot stopped")
        
        # Stop all worker bots
        for index, worker in WorkerBots.items():
            if index != 0:  # Don't stop main bot again
                try:
                    await worker.stop()
                except:
                    pass
        
        LOGGER.info("✅ All services stopped successfully")
        
    except Exception:
        LOGGER.error(f"❌ Error during shutdown:\n{format_exc()}")

async def health_ping():
    """Ping the server periodically to keep it alive"""
    import aiohttp
    
    sleep_time = 1200  # 20 minutes
    ping_url = f"{Config.BASE_URL}/"
    
    LOGGER.info(f"🏥 Health check enabled: Will ping every {sleep_time//60} minutes")
    
    while True:
        await asyncio.sleep(sleep_time)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(ping_url) as resp:
                    LOGGER.info(f"🏥 Health check - Status: {resp.status}")
        except asyncio.TimeoutError:
            LOGGER.warning("⚠️ Health check timeout")
        except Exception as e:
            LOGGER.error(f"❌ Health check failed: {e}")

def main():
    """Main entry point"""
    loop = asyncio.get_event_loop()
    
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        LOGGER.info('⚠️  Service stopping (Keyboard Interrupt)...')
    except Exception:
        LOGGER.error(f"❌ Fatal error:\n{format_exc()}")
    finally:
        loop.run_until_complete(stop_services())
        loop.stop()
        logging.shutdown()
        LOGGER.info("👋 Goodbye!")

if __name__ == "__main__":
    main()
