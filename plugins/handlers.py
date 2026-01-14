from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from encrypt import encode_string
from logger import LOGGER
import re
import os


def sanitize_filename(filename: str, max_length: int = 60) -> str:
    """
    Sanitize filename by removing special characters, replacing spaces with underscores,
    and limiting length while preserving extension.
    """
    # Get file extension
    name, ext = os.path.splitext(filename)
    
    # Remove special characters and replace spaces
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    name = re.sub(r'_+', '_', name)  # Replace multiple underscores with single
    name = name.strip('_')
    
    # Limit length
    if len(name) > max_length:
        name = name[:max_length]
    
    # Return with extension
    return f"{name}{ext}"


@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    """Handle /start command"""
    user_name = message.from_user.first_name if message.from_user else "User"
    
    welcome_text = f"""
👋 **Hello {user_name}!**

📁 **File-to-Link Bot**

Send me any file (document, video, audio) and I'll generate a direct download link for you!

✨ **Features:**
• Fast streaming links (50-100 MB/s)
• Support for files up to 4GB
• Byte-range support (seekable videos)
• No expiration

📤 **How to use:**
Just send me a file and I'll do the rest!

Powered by Telegram's infrastructure 🚀
    """
    
    await message.reply_text(welcome_text)


@Client.on_message(filters.document | filters.video | filters.audio | filters.voice)
async def file_handler(client: Client, message: Message):
    """
    Handle file uploads
    1. Copy file to dump channel
    2. Generate encrypted link
    3. Send link to user
    """
    # Send processing message
    status_msg = await message.reply_text("⏳ Processing your file...")
    
    try:
        # Get file info
        file = message.document or message.video or message.audio or message.voice
        file_name = getattr(file, 'file_name', 'file')
        file_size = getattr(file, 'file_size', 0)
        
        # Get file size in readable format
        from server import get_readable_file_size
        readable_size = get_readable_file_size(file_size)
        
        # Forward/copy file to dump channel
        try:
            await status_msg.edit_text("📤 Copying file to storage...")
        except Exception:
            pass  # Ignore edit errors
        
        # Use forward instead of copy (more reliable)
        try:
            forwarded = await client.forward_messages(
                chat_id=Config.DUMP_CHANNEL,
                from_chat_id=message.chat.id,
                message_ids=message.id
            )
            
            # Handle different return types from forward_messages
            dump_message = None
            if forwarded:
                if isinstance(forwarded, list):
                    dump_message = forwarded[0] if len(forwarded) > 0 else None
                else:
                    # Single message returned
                    dump_message = forwarded
            
            # Validate dump_message has required attributes
            if not dump_message or not hasattr(dump_message, 'id'):
                raise Exception("Failed to forward message to dump channel - invalid message returned")
                
        except Exception as e:
            LOGGER.error(f"Error forwarding to dump channel: {e}", exc_info=True)
            try:
                await status_msg.edit_text(f"❌ **Error:** Could not copy file to storage. Please try again.")
            except Exception:
                pass  # Ignore edit errors
            return
        
        # Generate encrypted link
        try:
            await status_msg.edit_text("🔐 Generating download link...")
        except Exception:
            pass  # Ignore edit errors
        
        # Extract channel ID without -100 prefix (like Telegram-Stremio)
        # Converts -1002318728082 -> 2318728082
        channel_id = str(Config.DUMP_CHANNEL).replace("-100", "", 1) if str(Config.DUMP_CHANNEL).startswith("-100") else str(Config.DUMP_CHANNEL)
        
        data = {
            "msg_id": dump_message.id,
            "chat_id": channel_id  # Store without -100 prefix
        }
        
        encrypted_id = await encode_string(data)
        
        # Sanitize filename for URL
        safe_filename = sanitize_filename(file_name)
        download_url = f"{Config.BASE_URL}/dl/{encrypted_id}/{safe_filename}"
        
        # Send link to user
        response_text = f"""
✅ **File Uploaded Successfully!**

📄 **File:** `{file_name}`
📦 **Size:** {readable_size}

🔗 **Download Link:**
`{download_url}`

💡 **Tip:** This link will never expire and supports seeking in video players!

⚡ **Speed:** 50-100 MB/s (from Telegram's CDN)
        """
        
        try:
            await status_msg.edit_text(response_text)
        except Exception:
            # If edit fails, send as new message
            await message.reply_text(response_text)
        
        # Log to console (check if from_user exists for channel forwards)
        user_id = message.from_user.id if message.from_user else "Unknown"
        LOGGER.info(f"✅ Generated link for: {file_name} ({readable_size})")
        LOGGER.info(f"   User: {user_id}")
        LOGGER.info(f"   Link: {download_url}")
        
    except Exception as e:
        error_text = f"❌ **Error:** {str(e)}"
        try:
            await status_msg.edit_text(error_text)
        except Exception:
            await message.reply_text(error_text)
        LOGGER.error(f"❌ Error processing file: {e}", exc_info=True)


@Client.on_message(filters.command("stats") & filters.user(Config.OWNER_ID))
async def stats_handler(client: Client, message: Message):
    """Show bot statistics (owner only)"""
    from bot import WorkLoads
    
    stats_text = "📊 **Bot Statistics**\n\n"
    stats_text += f"👥 **Worker Bots:** {len(WorkLoads)}\n\n"
    
    stats_text += "**Load Distribution:**\n"
    for index, load in WorkLoads.items():
        stats_text += f"• Worker {index}: {load} active streams\n"
    
    await message.reply_text(stats_text)


@Client.on_message(filters.command("log") & filters.user(Config.OWNER_ID))
async def log_handler(client: Client, message: Message):
    """Send bot log file (owner only)"""
    from os import path as ospath
    
    try:
        log_path = ospath.abspath('bot.log')
        if not ospath.exists(log_path):
            return await message.reply_text("❌ Log file not found.")
        
        await message.reply_document(
            document=log_path,
            caption="📄 Bot Log File",
            quote=True,
            disable_notification=True
        )
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")
        LOGGER.error(f"Error in /log: {e}")
