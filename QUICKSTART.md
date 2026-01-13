# Quick Start Guide 🚀

## Get Running in 5 Minutes!

### Step 1: Get Telegram Credentials (2 min)

1. **API Credentials**
   - Visit: https://my.telegram.org
   - Login → API Development Tools
   - Create app → Copy `API_ID` and `API_HASH`

2. **Bot Tokens**
   - Chat with @BotFather
   - Send `/newbot` → Create main bot
   - Send `/newbot` 2-3 more times → Create worker bots
   - Save all tokens

3. **Dump Channel**
   - Create a private channel
   - Add ALL bots as admins
   - Forward any message to @userinfobot
   - Copy channel ID (e.g., `-1001234567890`)

### Step 2: Install & Configure (2 min)

```bash
# Clone and install
cd file-to-link-bot
pip install -r requirements.txt

# Configure
cp config.env.sample config.env
nano config.env  # Fill in your values
```

**Minimal config.env:**
```env
API_ID=12345678
API_HASH=abc123def456
MAIN_BOT_TOKEN=123:ABC
WORKER_BOTS=456:DEF,789:GHI
DUMP_CHANNEL=-1001234567890
BASE_URL=https://yourdomain.com
PORT=8000
OWNER_ID=987654321
```

### Step 3: Run! (1 min)

```bash
python main.py
```

That's it! 🎉

### Test It

1. Open your bot on Telegram
2. Send `/start`
3. Send any file
4. Get your download link!

### Next Steps

- **Deploy to VPS**: Use ngrok for testing or deploy to a server
- **Add SSL**: Use Certbot for HTTPS
- **Add More Workers**: More bot tokens = better performance

### Quick Deploy with ngrok (Testing)

```bash
# Install ngrok
# Download from https://ngrok.com

# Run ngrok in another terminal
ngrok http 8000

# Copy the HTTPS URL and update BASE_URL in config.env
# Restart the bot
```

### Production Deployment

**Option 1: VPS**
```bash
# On your server
git clone <your-repo>
cd file-to-link-bot
pip install -r requirements.txt

# Configure config.env with your domain
nano config.env

# Run with screen or tmux
screen -S filebot
python main.py
# Press Ctrl+A then D to detach
```

**Option 2: Docker (Coming Soon)**

### Troubleshooting

**Import Error?**
```bash
pip install --upgrade pyrofork fastapi uvicorn
```

**Can't access server?**
```bash
# Check if port is open
sudo ufw allow 8000
```

**Bot not responding?**
- Check bot tokens are correct
- Ensure bots are admins in dump channel
- Verify API credentials

---

Need help? Check the full [README.md](README.md)
