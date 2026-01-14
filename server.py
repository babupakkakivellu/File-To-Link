import math
import secrets
import mimetypes
from typing import Tuple
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from encrypt import decode_string
from byte_streamer import ByteStreamer
from bot import WorkerBots, get_least_loaded_bot
from config import Config
from logger import LOGGER

app = FastAPI(title="File-to-Link Bot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for ByteStreamer instances
class_cache = {}


def parse_range_header(range_header: str, file_size: int) -> Tuple[int, int]:
    """Parse HTTP Range header"""
    if not range_header:
        return 0, file_size - 1
    
    try:
        range_value = range_header.replace("bytes=", "")
        from_str, until_str = range_value.split("-")
        from_bytes = int(from_str)
        until_bytes = int(until_str) if until_str else file_size - 1
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Range header: {e}")

    if (until_bytes > file_size - 1) or (from_bytes < 0) or (until_bytes < from_bytes):
        raise HTTPException(
            status_code=416,
            detail="Requested Range Not Satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    return from_bytes, until_bytes


@app.get("/")
async def root():
    """API info endpoint"""
    return {
        "status": "online",
        "bot": "File-to-Link Bot",
        "version": "1.0.0",
        "endpoints": {
            "download": "/dl/{id}/{name}"
        }
    }


@app.get("/dl/{id}/{name}")
@app.head("/dl/{id}/{name}")
async def stream_handler(request: Request, id: str, name: str):
    """
    Main streaming endpoint
    Decodes the file ID and streams the file from Telegram
    """
    # Decode the encrypted ID
    try:
        decoded_data = await decode_string(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file ID: {e}")
    
    if not decoded_data.get("msg_id"):
        raise HTTPException(status_code=400, detail="Missing message ID")
    
    # Reconstruct full chat_id by adding -100 prefix (like Telegram-Stremio)
    # Converts 2318728082 -> -1002318728082
    channel_id_str = str(decoded_data['chat_id'])
    if not channel_id_str.startswith("-"):
        chat_id = f"-100{channel_id_str}"
    else:
        chat_id = channel_id_str
    
    message_id = decoded_data["msg_id"]
    
    # Get file info to validate
    from bot import MainBot
    try:
        message = await MainBot.get_messages(int(chat_id), int(message_id))
        file = message.video or message.document or message.audio or message.voice
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_hash = file.file_unique_id[:6]
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    return await media_streamer(
        request,
        chat_id=int(chat_id),
        id=int(message_id),
        secure_hash=file_hash
    )


async def media_streamer(
    request: Request,
    chat_id: int,
    id: int,
    secure_hash: str,
) -> StreamingResponse:
    """
    Stream media file from Telegram
    Supports byte-range requests for seeking/resuming
    """
    range_header = request.headers.get("Range", "")
    
    # Get the least loaded worker bot
    index = get_least_loaded_bot()
    if index is None:
        raise HTTPException(status_code=503, detail="No worker bots available")
    
    faster_client = WorkerBots[index]

    # Get or create ByteStreamer instance
    tg_connect = class_cache.get(index)
    if not tg_connect:
        tg_connect = ByteStreamer(faster_client)
        class_cache[index] = tg_connect

    # Get file properties
    try:
        file_id = await tg_connect.get_file_properties(chat_id=chat_id, message_id=id)
    except Exception as e:
        LOGGER.error(f"Error getting file properties: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=f"File not found: {e}")
    
    # Validate file hash
    if file_id.unique_id[:6] != secure_hash:
        raise HTTPException(status_code=403, detail="Invalid file hash")

    file_size = file_id.file_size
    from_bytes, until_bytes = parse_range_header(range_header, file_size)

    # Calculate chunk parameters
    chunk_size = 1024 * 1024  # 1MB chunks
    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = (until_bytes % chunk_size) + 1
    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

    # Log streaming parameters for debugging
    LOGGER.info(f"📡 Streaming request: {from_bytes}-{until_bytes} of {file_size} bytes ({req_length} bytes expected)")
    LOGGER.debug(f"   Chunk size: {chunk_size}, Offset: {offset}, Parts: {part_count}")
    LOGGER.debug(f"   First cut: {first_part_cut}, Last cut: {last_part_cut}")

    # Determine filename and MIME type
    file_name = file_id.file_name or f"{secrets.token_hex(2)}.unknown"
    mime_type = file_id.mime_type or mimetypes.guess_type(file_name)[0] or "application/octet-stream"
    
    if not file_id.file_name and "/" in mime_type:
        file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"

    # Create error-wrapped generator
    async def safe_stream_generator():
        """Wrapper that catches exceptions in the generator"""
        try:
            async for chunk in tg_connect.yield_file(
                file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
            ):
                yield chunk
        except Exception as e:
            LOGGER.error(f"❌ Stream generator error: {e}", exc_info=True)
            # Generator already started, can't change status code
            # Just stop yielding - client will see incomplete response
            return

    # Build response headers
    # IMPORTANT: Not setting Content-Length to use chunked transfer encoding
    # This prevents crashes when stream fails partway through
    headers = {
        "Content-Type": mime_type,
        "Content-Disposition": f'inline; filename="{file_name}"',
        "Accept-Ranges": "bytes",
        "Cache-Control": "public, max-age=3600, immutable",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "Content-Length, Content-Range, Accept-Ranges",
    }
    
    # Add Content-Range header if range request
    if range_header:
        headers["Content-Range"] = f"bytes {from_bytes}-{until_bytes}/{file_size}"
        headers["Content-Length"] = str(req_length)  # Safe for range requests since we know exact size
        status_code = 206  # Partial Content
    else:
        # For full file requests, we'll use chunked encoding (no Content-Length)
        # This prevents the "Response content shorter than Content-Length" crash
        status_code = 200  # OK
    
    return StreamingResponse(
        status_code=status_code,
        content=safe_stream_generator(),
        headers=headers,
        media_type=mime_type,
    )


def get_readable_file_size(size_in_bytes):
    """Convert bytes to human-readable format"""
    size_in_bytes = int(size_in_bytes) if str(size_in_bytes).isdigit() else 0
    if not size_in_bytes:
        return '0B'
    
    index, SIZE_UNITS = 0, ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1
    
    return f'{size_in_bytes:.2f}{SIZE_UNITS[index]}' if index > 0 else f'{size_in_bytes:.0f}B'


def start_server():
    """Create and return uvicorn server instance"""
    config = uvicorn.Config(
        app=app, 
        host='0.0.0.0', 
        port=Config.PORT,
        log_level="error",  # Reduce noise
        access_log=False
    )
    return uvicorn.Server(config)
