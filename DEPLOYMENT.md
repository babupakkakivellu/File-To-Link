# Deployment Guide - File-to-Link Bot

## 🚀 Multiple Deployment Options

This bot can be deployed on various platforms. Choose the one that fits your needs:

1. **Docker** (Recommended for VPS)
2. **Koyeb** (Free tier available)
3. **Render** (Free tier available)
4. **Railway** (Free trial)
5. **Traditional VPS** (Manual setup)

---

## 🐳 Docker Deployment (VPS/Local)

### **Prerequisites:**
- Docker installed
- Domain with SSL (recommended)

### **Quick Deploy:**

```bash
# 1. Clone repository
git clone <your-repo>
cd file-to-link-bot

# 2. Create config.env
cp config.env.sample config.env
nano config.env  # Fill in your values

# 3. Build image
docker build -t file-to-link-bot .

# 4. Run container
docker run -d \
  --name file-to-link-bot \
  --env-file config.env \
  -p 8000:8000 \
  --restart unless-stopped \
  file-to-link-bot

# 5. Check logs
docker logs -f file-to-link-bot
```

### **Using Docker Compose (Alternative):**

```yaml
# docker-compose.yml
version: '3.8'

services:
  bot:
    build: .
    container_name: file-to-link-bot
    env_file: config.env
    ports:
      - "8000:8000"
    restart: unless-stopped
    volumes:
      - ./bot.log:/app/bot.log
```

```bash
# Deploy
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## ☁️ Koyeb Deployment

**Free Tier:** Yes (with limitations)  
**Domain:** Provided automatically  
**SSL:** Automatic

### **Steps:**

1. **Fork/Clone Repository**
   - Create GitHub repository with your code

2. **Create Koyeb Account**
   - Sign up at https://www.koyeb.com

3. **Create New App**
   - Click "Create App"
   - Choose "GitHub" as source
   - Select your repository

4. **Configure Build:**
   ```
   Build command: (leave empty, uses Dockerfile)
   Run command: python main.py
   Port: 8000
   ```

5. **Add Environment Variables:**
   ```
   API_ID=your_value
   API_HASH=your_value
   MAIN_BOT_TOKEN=your_value
   WORKER_BOTS=token1,token2
   DUMP_CHANNEL=-1001234567890
   BASE_URL=https://your-app.koyeb.app
   PORT=8000
   OWNER_ID=your_id
   ```

6. **Deploy**
   - Click "Deploy"
   - Wait for build (~3-5 minutes)
   - Your bot will be live!

### **Koyeb Notes:**
- ✅ Free tier: 1 service, 512MB RAM
- ✅ Auto-SSL with custom domain
- ✅ Auto-restart on crash
- ⚠️ Free tier may sleep after inactivity
- 💡 Use health check to prevent sleep

---

## 🎨 Render Deployment

**Free Tier:** Yes (with limitations)  
**Domain:** Provided automatically  
**SSL:** Automatic

### **Steps:**

1. **Push Code to GitHub**

2. **Create Render Account**
   - Sign up at https://render.com

3. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub repository

4. **Configure Service:**
   ```
   Name: file-to-link-bot
   Environment: Docker
   Region: Choose closest
   Branch: main
   Build Command: (auto-detected from Dockerfile)
   Start Command: python main.py
   ```

5. **Set Environment Variables:**
   - Go to "Environment" tab
   - Add all variables from config.env:
   ```
   API_ID=12345678
   API_HASH=abc123
   MAIN_BOT_TOKEN=123:ABC
   WORKER_BOTS=456:DEF,789:GHI
   DUMP_CHANNEL=-1001234567890
   BASE_URL=https://your-app.onrender.com
   PORT=8000
   OWNER_ID=987654321
   ```

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (~5-10 minutes)

### **Render Notes:**
- ✅ Free tier: 750 hours/month
- ✅ Auto-deploy on git push
- ✅ Free SSL
- ⚠️ Free tier spins down after 15 min inactivity
- ⚠️ 512MB RAM limit on free tier
- 💡 Upgrading to paid tier prevents sleep

---

## 🚂 Railway Deployment

**Free Trial:** $5 credit  
**Domain:** Provided automatically  
**SSL:** Automatic

### **Steps:**

1. **Create Railway Account**
   - Sign up at https://railway.app

2. **New Project**
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository

3. **Configure:**
   - Railway auto-detects Dockerfile
   - No build config needed

4. **Add Variables:**
   - Go to "Variables" tab
   - Add all environment variables
   - Set `PORT=8000`

5. **Deploy**
   - Click "Deploy"
   - Get public URL from "Settings"

### **Railway Notes:**
- ✅ $5 free trial
- ✅ Easy setup
- ✅ No sleep on free tier
- ⚠️ Credit-based (no permanent free tier)

---

## 🖥️ Traditional VPS Deployment

**Platforms:** DigitalOcean, Linode, Vultr, AWS, etc.  
**Cost:** $5-10/month  
**Control:** Full

### **Option 1: Docker on VPS**

```bash
# 1. SSH into VPS
ssh user@your-vps-ip

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Clone repo
git clone <your-repo>
cd file-to-link-bot

# 4. Setup config
cp config.env.sample config.env
nano config.env  # Fill values

# 5. Run with Docker
docker build -t file-to-link-bot .
docker run -d \
  --name file-to-link-bot \
  --env-file config.env \
  -p 8000:8000 \
  --restart unless-stopped \
  file-to-link-bot

# 6. Setup Nginx (optional, for custom domain)
sudo apt install nginx
sudo nano /etc/nginx/sites-available/bot
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### **Option 2: Direct Python on VPS**

```bash
# 1. Install Python
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# 2. Clone and setup
git clone <your-repo>
cd file-to-link-bot
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure
cp config.env.sample config.env
nano config.env

# 4. Run with screen/tmux
screen -S bot
python main.py
# Press Ctrl+A then D to detach

# Or use systemd service
sudo nano /etc/systemd/system/file-to-link-bot.service
```

**Systemd Service:**
```ini
[Unit]
Description=File-to-Link Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/file-to-link-bot
Environment="PATH=/path/to/file-to-link-bot/venv/bin"
ExecStart=/path/to/file-to-link-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable file-to-link-bot
sudo systemctl start file-to-link-bot
sudo systemctl status file-to-link-bot

# View logs
sudo journalctl -u file-to-link-bot -f
```

---

## 🌐 Custom Domain Setup

### **For Cloud Platforms (Koyeb/Render/Railway):**

1. Add custom domain in platform dashboard
2. Get CNAME/A record from platform
3. Add DNS record at your domain provider:
   ```
   Type: CNAME
   Name: bot (or @)
   Value: your-app.platform.app
   ```
4. Wait for DNS propagation (5-30 min)
5. Platform auto-provisions SSL

### **For VPS:**
- Setup Nginx (shown above)
- Use Certbot for SSL
- Point domain A record to VPS IP

---

## 📊 Platform Comparison

| Platform | Free Tier | Sleep | RAM | Deploy Time | Difficulty |
|----------|-----------|-------|-----|-------------|------------|
| **Koyeb** | ✅ Yes | ⚠️ Yes | 512MB | 3-5 min | ⭐⭐ |
| **Render** | ✅ Yes | ⚠️ Yes | 512MB | 5-10 min | ⭐⭐ |
| **Railway** | 💵 $5 credit | ❌ No | 8GB | 2-3 min | ⭐ |
| **VPS Docker** | 💵 $5/mo | ❌ No | 1GB+ | 10 min | ⭐⭐⭐ |
| **VPS Direct** | 💵 $5/mo | ❌ No | 1GB+ | 15 min | ⭐⭐⭐⭐ |

**Recommendation:**
- **Testing:** Render (free, easy)
- **Production (Free):** Koyeb + health check
- **Production (Paid):** VPS with Docker ($5/mo)
- **Best Performance:** VPS with 2GB+ RAM

---

## 💡 Tips for Free Tier Deployments

### **Prevent Sleep (Render/Koyeb):**

The bot has built-in health check that pings itself every 20 minutes, but you can add external monitoring:

**Option 1: UptimeRobot**
1. Sign up at https://uptimerobot.com
2. Add monitor:
   - Type: HTTP(s)
   - URL: https://your-bot-url.com/
   - Interval: 5 minutes
3. Free tier prevents sleep!

**Option 2: Cron-job.org**
1. Sign up at https://cron-job.org
2. Create job:
   - URL: https://your-bot-url.com/
   - Interval: Every 15 minutes
3. Keeps bot awake

### **Optimize for Low RAM:**

Already optimized! The bot uses:
- ~50MB idle
- ~100-200MB during streaming
- No database (saves memory)

---

## 🐛 Troubleshooting

### **Docker Issues:**

```bash
# View logs
docker logs file-to-link-bot

# Access container
docker exec -it file-to-link-bot bash

# Restart
docker restart file-to-link-bot

# Rebuild
docker build --no-cache -t file-to-link-bot .
```

### **Cloud Platform Issues:**

**Build fails:**
- Check environment variables are set
- Verify Dockerfile syntax
- Check build logs

**App crashes:**
- Check environment variables
- Verify bot tokens are valid
- Check dump channel ID
- View platform logs

**Slow/timeouts:**
- Upgrade to paid tier for more RAM
- Reduce worker bots on free tier
- Check network connectivity

---

## 📝 Environment Variables Quick Reference

**Required:**
```
API_ID=12345678
API_HASH=your_api_hash
MAIN_BOT_TOKEN=your_main_token
DUMP_CHANNEL=-1001234567890
BASE_URL=https://your-domain.com
PORT=8000
OWNER_ID=your_telegram_id
```

**Optional:**
```
WORKER_BOTS=token1,token2,token3
# OR
MULTI_TOKEN1=token1
MULTI_TOKEN2=token2
MULTI_TOKEN3=token3
```

---

## ✅ Deployment Checklist

Before deploying:
- [ ] Created all bot tokens (@BotFather)
- [ ] Created dump channel (private)
- [ ] Added all bots as admins to dump channel
- [ ] Got channel ID (@userinfobot)
- [ ] Filled all environment variables
- [ ] Set correct BASE_URL for platform
- [ ] Tested locally (optional)

After deploying:
- [ ] Check deployment logs
- [ ] Test /start command
- [ ] Upload test file
- [ ] Verify link works
- [ ] Test download speed
- [ ] Setup monitoring (if free tier)
- [ ] Add custom domain (optional)

---

**Choose your platform and deploy! The bot works the same on all platforms! 🚀**
