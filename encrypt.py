import zlib
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

def compress_data(data):
    """Compress data using zlib"""
    return zlib.compress(data.encode(), level=zlib.Z_BEST_COMPRESSION)

def decompress_data(data):
    """Decompress zlib data"""
    return zlib.decompress(data).decode()

def base62_encode(data):
    """Encode bytes to base62 string"""
    BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num = int.from_bytes(data, 'big')
    base62 = []
    while num:
        num, rem = divmod(num, 62)
        base62.append(BASE62_ALPHABET[rem])
    return ''.join(reversed(base62)) or '0'

def base62_decode(data):
    """Decode base62 string to bytes"""
    BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num = 0
    for char in data:
        num = num * 62 + BASE62_ALPHABET.index(char)
    return num.to_bytes((num.bit_length() + 7) // 8, 'big') or b'\\0'

async def async_compress_data(data):
    """Async wrapper for compression"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, compress_data, data)

async def async_decompress_data(data):
    """Async wrapper for decompression"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, decompress_data, data)

async def async_base62_encode(data):
    """Async wrapper for base62 encoding"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, base62_encode, data)

async def async_base62_decode(data):
    """Async wrapper for base62 decoding"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, base62_decode, data)

async def encode_string(data):
    """
    Encode dictionary to compressed base62 string
    Example: {"msg_id": 123, "chat_id": 456} -> "3kT9mN2pQ"
    """
    json_data = json.dumps(data)
    compressed_data = await async_compress_data(json_data)
    return await async_base62_encode(compressed_data)

async def decode_string(encoded_data):
    """
    Decode base62 string back to dictionary
    Example: "3kT9mN2pQ" -> {"msg_id": 123, "chat_id": 456}
    """
    compressed_data = await async_base62_decode(encoded_data)
    json_data = await async_decompress_data(compressed_data)
    return json.loads(json_data)
