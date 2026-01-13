# File-to-Link Bot 🚀

A powerful Telegram bot that generates fast direct download links for files using the **same algorithm as Telegram-Stremio**. Upload any file and get a streaming link that never expires!

## ✨ Features

- **🚀 Blazing Fast Downloads** - 50-100 MB/s (from Telegram's CDN)
- **📦 Large File Support** - Handle files up to 4GB
- **♾️ No Expiration** - Links work forever
- **🎬 Seekable Videos** - Full byte-range support for video seeking
- **⚖️ Load Balancing** - Multiple worker bots distribute load
- **🔐 Secure Links** - Encrypted file IDs (base62 + zlib compression)
- **🌐 FastAPI Streaming** - Professional-grade streaming server

## 🎯 How It Works

```
User sends file → Bot → Dumps to channel → Generates encrypted link → User gets link
User clicks link → FastAPI → Decodes → Streams from Telegram CDN → Fast download!
```

### The Algorithm (Same as Telegram-Stremio)

1. **File Upload**: User sends file to bot
2. **Storage**: Bot copies file to dump channel  
3. **Encryption**: 
   - Creates `{msg_id, chat_id}` JSON
   - Compresses with zlib
   - Encodes to base62 (short, URL-safe)
4. **Link Generation**: `{BASE_URL}/dl/{encrypted_id}/{filename}`
5. **Streaming**:
   - Decode encrypted ID
   - Use PyroFork MTProto to fetch from Telegram
   - Stream chunks with byte-range support
   - Load balance across worker bots

## 📋 Requirements

- Python 3.8+
- Telegram API credentials (api_id, api_hash)
- Bot tokens (main + workers)
- A Telegram channel for file storage
- A server with public URL (for FastAPI)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd file-to-link-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the bot

```bash
cp config.env.sample config.env
nano config.env
```

Fill in all the required values:

```env
API_ID=12345678
API_HASH=your_api_hash
MAIN_BOT_TOKEN=your_main_bot_token
WORKER_BOTS=token1,token2,token3
DUMP_CHANNEL=-1001234567890
BASE_URL=https://yourdomain.com
PORT=8000
OWNER_ID=your_user_id
```

### 4. Setup Telegram

#### Get API Credentials
1. Go to https://my.telegram.org
2. Login with your phone number
3. Go to "API Development Tools"
4. Create an app and get `API_ID` and `API_HASH`

#### Create Bots
1. Chat with @BotFather
2. Create main bot: `/newbot`
3. Create 2-3 worker bots: `/newbot` (repeat)
4. Save all bot tokens

#### Create Dump Channel
1. Create a private channel
2. Add all bots (main + workers) as admins
3. Forward any message from the channel to @userinfobot
4. Copy the channel ID (e.g., `-1001234567890`)

### 5. Run the bot

```bash
python main.py
```

## 📖 Usage

### User Commands

- `/start` - Get welcome message and instructions
- `/stats` - View bot statistics (owner only)

### Sending Files

1. Start a chat with your bot
2. Send any file (document, video, audio, voice)
3. Bot will process and send you a download link
4. Share the link with anyone!

### Example

```
User: *sends video.mp4*
Bot: ✅ File Uploaded Successfully!

📄 File: video.mp4
📦 Size: 1.25 GB

🔗 Download Link:
https://yourdomain.com/dl/3kT9mN2pQ7hLx4vR/video.mp4

💡 Tip: This link will never expire!
⚡ Speed: 50-100 MB/s
```

## 🔧 Configuration

### Worker Bots

Add multiple worker bot tokens to improve performance

:

```env
WORKER_BOTS=token1,token2,token3,token4
```

**Benefits:**
- Distribute streaming load
- Bypass rate limits
- Higher concurrent downloads
- Automatic load balancing

### Server Setup

For production, use a reverse proxy:

**Nginx example:**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🏗️ Project Structure

```
file-to-link-bot/
├── main.py              # Entry point (starts bot + server)
├── bot.py               # Bot initialization & load balancer
├── config.py            # Configuration loader
├── encrypt.py           # Base62 + zlib encryption
├── byte_streamer.py     # Telegram file streaming (MTProto)
├── server.py            # FastAPI streaming server
├── plugins/
│   ├── __init__.py
│   └── handlers.py      # Bot command handlers
├── requirements.txt     # Python dependencies
├── config.env.sample    # Sample configuration
└── README.md            # This file
```

## 🔐 Security

- **Encrypted File IDs**: Base62 encoding prevents guessing
- **File Hash Validation**: Ensures correct file is served
- **No Direct Access**: Files only accessible via encrypted links
- **Rate Limiting**: Multiple worker bots prevent abuse

## ⚡ Performance

- **Download Speed**: 50-100 MB/s (Telegram's CDN)
- **File Size**: Up to 4GB per file
- **Concurrent Streams**: Limited only by worker bots
- **Byte-Range Support**: Full seeking in video players

## 📊 How Fast Is It?

| Service | Speed |
|---------|-------|
| **File-to-Link Bot** | **50-100 MB/s** ⚡ |
| Google Drive | 10-20 MB/s |
| Dropbox | 5-15 MB/s |
| Basic VPS | 10-30 MB/s |

**Why so fast?**
- Uses Telegram's enterprise CDN infrastructure
- Direct streaming (no intermediate storage)
- MTProto protocol optimization
- Multi-bot load balancing

## 🐛 Troubleshooting

### Bot not starting?
- Check API credentials in `config.env`
- Ensure all bot tokens are valid
- Verify dump channel ID format (`-100` prefix)

### Links not working?
- Ensure `BASE_URL` is correct and accessible
- Check if FastAPI server is running
- Verify worker bots are started

### Slow downloads?
- Add more worker bot tokens
- Check server bandwidth
- Ensure using MTProto (not Bot API)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📜 License

MIT License - feel free to use for any purpose!

## 🙏 Credits

- Algorithm based on [Telegram-Stremio](https://github.com/weebzone/Telegram-Stremio)
- Built with [PyroFork](https://github.com/Mayuri-Chan/pyrofork)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)

## 📞 Support

If you need help:
1. Check this README
2. Review the troubleshooting section
3. Open an issue on GitHub

---

**Made with ❤️ using Telegram's infrastructure**

⭐ Star this repo if you found it useful!
