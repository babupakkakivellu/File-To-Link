import asyncio
from pyrogram import utils, raw
from pyrogram.errors import AuthBytesInvalid
from pyrogram.file_id import FileId, FileType, ThumbnailSource
from pyrogram.session import Session, Auth
from typing import Dict, Union
from pyrogram import Client
from logger import LOGGER

class ByteStreamer:
    """
    Handles streaming files from Telegram using ByteRange support
    Same algorithm as Telegram-Stremio
    """
    
    def __init__(self, client: Client):
        self.clean_timer = 30 * 60  # 30 minutes
        self.client: Client = client
        self.__cached_file_ids: Dict[int, FileId] = {}
        asyncio.create_task(self.clean_cache())

    async def get_file_properties(self, chat_id: int, message_id: int) -> FileId:
        """Get or cache file properties from a message"""
        if message_id not in self.__cached_file_ids:
            file_id = await self._get_file_ids(chat_id, message_id)
            if not file_id:
                raise Exception(f'Message with ID {message_id} not found!')
            self.__cached_file_ids[message_id] = file_id
        return self.__cached_file_ids[message_id]

    async def _get_file_ids(self, chat_id: int, message_id: int) -> FileId:
        """Extract file ID from message"""
        try:
            message = await self.client.get_messages(chat_id, message_id)
            if message.empty:
                raise Exception("Message not found or empty")
            
            # Get media from message
            media = message.video or message.document or message.audio or message.voice
            if not media:
                raise Exception("No supported media found in message")
            
            # Decode file ID
            file_id_obj = FileId.decode(media.file_id)
            file_unique_id = media.file_unique_id
            
            # Add file properties
            setattr(file_id_obj, 'file_name', getattr(media, 'file_name', ''))
            setattr(file_id_obj, 'file_size', getattr(media, 'file_size', 0))
            setattr(file_id_obj, 'mime_type', getattr(media, 'mime_type', ''))
            setattr(file_id_obj, 'unique_id', file_unique_id)
            
            return file_id_obj
        except Exception as e:
            LOGGER.error(f"Error getting file IDs: {e}")
            raise

    async def yield_file(
        self, 
        file_id: FileId, 
        index: int, 
        offset: int, 
        first_part_cut: int, 
        last_part_cut: int, 
        part_count: int, 
        chunk_size: int
    ):
        """
        Stream file chunks from Telegram
        Supports byte-range requests for seeking/resuming
        """
        from bot import WorkLoads
        
        client = self.client
        WorkLoads[index] += 1
        
        # Debug logging
        LOGGER.info(f"📤 Starting stream with worker bot {index}")
        LOGGER.debug(f"   Offset: {offset}, First cut: {first_part_cut}, Last cut: {last_part_cut}")
        LOGGER.debug(f"   Part count: {part_count}, Chunk size: {chunk_size}")
        
        media_session = None
        current_part = 1
        total_bytes_yielded = 0  # Track total bytes
        max_retries = 3
        retry_delay = 1  # seconds
        
        try:
            media_session = await self.generate_media_session(client, file_id)
            if not media_session:
                raise Exception("Failed to generate media session")
            
            location = await self.get_location(file_id)
            
            # Initial request with retry logic
            r = None
            for attempt in range(max_retries):
                try:
                    r = await asyncio.wait_for(
                        media_session.send(
                            raw.functions.upload.GetFile(location=location, offset=offset, limit=chunk_size)
                        ),
                        timeout=15.0  # 15 second timeout
                    )
                    break  # Success
                except asyncio.TimeoutError:
                    if attempt < max_retries - 1:
                        LOGGER.warning(f"⚠️ Request timeout on attempt {attempt + 1}, retrying...")
                        await asyncio.sleep(retry_delay)
                    else:
                        raise Exception("Request timed out after multiple attempts")
            
            if not r:
                raise Exception("Failed to get initial response from Telegram")
            
            if isinstance(r, raw.types.upload.File):
                while True:
                    chunk = r.bytes
                    if not chunk:
                        LOGGER.debug(f"   ℹ️ Empty chunk received at part {current_part}, ending stream")
                        break
                    
                    # Log chunk details
                    LOGGER.debug(f"   Part {current_part}/{part_count}: Received {len(chunk)} bytes")
                    
                    # Handle different parts of the range request
                    if part_count == 1:
                        cut_chunk = chunk[first_part_cut:last_part_cut]
                        LOGGER.debug(f"   Single part: Cut from {first_part_cut} to {last_part_cut} = {len(cut_chunk)} bytes")
                        yield cut_chunk
                        total_bytes_yielded += len(cut_chunk)
                    elif current_part == 1:
                        cut_chunk = chunk[first_part_cut:]
                        LOGGER.debug(f"   First part: Cut from {first_part_cut} = {len(cut_chunk)} bytes")
                        yield cut_chunk
                        total_bytes_yielded += len(cut_chunk)
                    elif current_part == part_count:
                        cut_chunk = chunk[:last_part_cut]
                        LOGGER.debug(f"   Last part: Cut to {last_part_cut} = {len(cut_chunk)} bytes")
                        yield cut_chunk
                        total_bytes_yielded += len(cut_chunk)
                    else:
                        LOGGER.debug(f"   Middle part: Full chunk = {len(chunk)} bytes")
                        yield chunk
                        total_bytes_yielded += len(chunk)

                    current_part += 1
                    offset += chunk_size

                    if current_part > part_count:
                        LOGGER.debug(f"   ✅ Reached part count limit ({part_count})")
                        break
                    
                    # Request next chunk with timeout and retry
                    r = None
                    for attempt in range(max_retries):
                        try:
                            r = await asyncio.wait_for(
                                media_session.send(
                                    raw.functions.upload.GetFile(
                                        location=location, offset=offset, limit=chunk_size
                                    )
                                ),
                                timeout=15.0
                            )
                            break  # Success
                        except asyncio.TimeoutError:
                            if attempt < max_retries - 1:
                                LOGGER.warning(f"⚠️ Chunk request timeout on attempt {attempt + 1}, retrying...")
                                await asyncio.sleep(retry_delay)
                            else:
                                LOGGER.error(f"❌ Chunk request timed out after {max_retries} attempts")
                                raise Exception("Request timed out")
                    
                    if not r:
                        LOGGER.error("❌ Failed to get next chunk")
                        break
            else:
                LOGGER.error(f"❌ Unexpected response type: {type(r)}")
                raise Exception(f"Unexpected response type from Telegram: {type(r)}")
                
        except asyncio.TimeoutError:
            LOGGER.error(f"❌ Stream error: Request timed out")
            raise
        except AttributeError as e:
            LOGGER.error(f"❌ Stream error: AttributeError - {e}", exc_info=True)
            raise
        except Exception as e:
            LOGGER.error(f"❌ Unexpected stream error: {e}", exc_info=True)
            raise
        finally:
            LOGGER.info(f"✅ Stream complete: {current_part-1} parts, {total_bytes_yielded} bytes total")
            WorkLoads[index] -= 1

    async def generate_media_session(self, client: Client, file_id: FileId) -> Session:
        """Generate or get cached media session for a specific DC"""
        media_session = client.media_sessions.get(file_id.dc_id, None)
        
        if media_session is None:
            if file_id.dc_id != await client.storage.dc_id():
                media_session = Session(
                    client,
                    file_id.dc_id,
                    await Auth(client, file_id.dc_id, await client.storage.test_mode()).create(),
                    await client.storage.test_mode(),
                    is_media=True,
                )
                await media_session.start()
                
                for _ in range(6):
                    exported_auth = await client.invoke(
                        raw.functions.auth.ExportAuthorization(dc_id=file_id.dc_id)
                    )
                    try:
                        await media_session.send(
                            raw.functions.auth.ImportAuthorization(
                                id=exported_auth.id, bytes=exported_auth.bytes
                            )
                        )
                        break
                    except AuthBytesInvalid:
                        LOGGER.debug(f"Invalid authorization bytes for DC {file_id.dc_id}, retrying...")
                    except OSError:
                        LOGGER.debug(f"Connection error, retrying...")
                        await asyncio.sleep(2)
                else:
                    await media_session.stop()
                    LOGGER.error(f"Failed to establish media session for DC {file_id.dc_id}")
                    return None
            else:
                media_session = Session(
                    client,
                    file_id.dc_id,
                    await client.storage.auth_key(),
                    await client.storage.test_mode(),
                    is_media=True,
                )
                await media_session.start()
            
            LOGGER.debug(f"Created media session for DC {file_id.dc_id}")
            client.media_sessions[file_id.dc_id] = media_session
        else:
            LOGGER.debug(f"Using cached media session for DC {file_id.dc_id}")
        
        return media_session

    @staticmethod
    async def get_location(file_id: FileId):
        """Get Telegram file location based on file type"""
        file_type = file_id.file_type
        
        if file_type == FileType.CHAT_PHOTO:
            if file_id.chat_id > 0:
                peer = raw.types.InputPeerUser(
                    user_id=file_id.chat_id, 
                    access_hash=file_id.chat_access_hash
                )
            else:
                if file_id.chat_access_hash == 0:
                    peer = raw.types.InputPeerChat(chat_id=-file_id.chat_id)
                else:
                    peer = raw.types.InputPeerChannel(
                        channel_id=utils.get_channel_id(file_id.chat_id), 
                        access_hash=file_id.chat_access_hash
                    )
            
            location = raw.types.InputPeerPhotoFileLocation(
                peer=peer,
                volume_id=file_id.volume_id,
                local_id=file_id.local_id,
                big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG
            )
        elif file_type == FileType.PHOTO:
            location = raw.types.InputPhotoFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size
            )
        else:
            location = raw.types.InputDocumentFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size
            )
        
        return location

    async def clean_cache(self) -> None:
        """Periodically clean the file ID cache"""
        while True:
            await asyncio.sleep(self.clean_timer)
            self.__cached_file_ids.clear()
            LOGGER.debug("🧹 Cleaned the file ID cache")
