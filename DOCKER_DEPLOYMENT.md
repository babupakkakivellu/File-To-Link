# 🚀 Docker & Deployment - Complete Guide

## What Was Added

### ✅ Docker Support
- **Dockerfile** - Optimized multi-stage container
- Health checks for platform compatibility
- Automatic builds on cloud platforms
- Small image size (~200MB)

### ✅ Deployment Options
1. **Koyeb** - Free tier, auto-SSL
2. **Render** - Free tier, GitHub integration
3. **Railway** - $5 credit, fast deployment
4. **Heroku** - One-click deploy button
5. **VPS** - Docker or direct Python
6. **Local** - Docker for development

---

## 🐳 Dockerfile Features

```dockerfile
# Python 3.11 slim (small size)
# System dependencies (gcc for pyrofork)
# Cached layers for fast rebuilds
# Health check for cloud platforms
# Auto-restart support
# Log directory creation
# Port 8000 exposed
```

**Optimizations:**
- ✅ Multi-stage caching
- ✅ Minimal base image
- ✅ Health check endpoint
- ✅ Environment variable support
- ✅ Auto-restart on crash

---

## 🌐 Platform Support

| Platform | Free Tier | Deploy Time | Difficulty | Best For |
|----------|-----------|-------------|------------|----------|
| **Koyeb** | ✅ 512MB | 3-5 min | ⭐⭐ | Production (free) |
| **Render** | ✅ 512MB | 5-10 min | ⭐⭐ | Testing |
| **Railway** | 💵 $5 credit | 2-3 min | ⭐ | Quick setup |
| **Heroku** | 💵 $7/mo | 5 min | ⭐ | One-click |
| **VPS Docker** | 💵 $5/mo | 10 min | ⭐⭐⭐ | Full control |

---

## 📋 Quick Start Commands

### **Local Docker:**
```bash
docker build -t file-to-link-bot .
docker run -d --env-file config.env -p 8000:8000 file-to-link-bot
```

### **VPS Docker:**
```bash
git clone <repo>
cd file-to-link-bot
cp config.env.sample config.env
nano config.env
docker build -t file-to-link-bot .
docker run -d --name bot --env-file config.env -p 8000:8000 --restart unless-stopped file-to-link-bot
```

### **Check Logs:**
```bash
docker logs -f file-to-link-bot
```

---

## 🔧 Environment Variables

All platforms need these:

```env
API_ID=12345678
API_HASH=your_api_hash
MAIN_BOT_TOKEN=your_bot_token
WORKER_BOTS=token1,token2
DUMP_CHANNEL=-1001234567890
BASE_URL=https://your-domain.com
PORT=8000
OWNER_ID=your_telegram_id
```

---

## 💡 Platform-Specific Tips

### **Koyeb:**
- Auto-detects Dockerfile
- Provides free subdomain
- Add health monitor to prevent sleep
- Free SSL with custom domain

### **Render:**
- Enable auto-deploy from GitHub
- Use UptimeRobot to prevent sleep
- Upgrade to paid for no sleep ($7/mo)

### **Railway:**
- Easiest setup
- No sleep on paid plan
- Great for testing

### **VPS:**
- Full control
- No sleep issues
- Best performance
- Requires setup

---

## 📊 Deployment Comparison

**FREE OPTIONS:**
1. **Best: Koyeb + UptimeRobot**
   - No sleep with monitoring
   - Auto-SSL
   - 512MB RAM

2. **Alternative: Render**
   - Easy GitHub integration
   - Sleeps after 15 min (use UptimeRobot)

**PAID OPTIONS ($5-7/mo):**
1. **Best Value: VPS with Docker**
   - Full control
   - No limitations
   - 1GB+ RAM
   - No sleep

2. **Easiest: Railway**
   - Simple setup
   - No sleep
   - 8GB RAM

---

## 🎯 Recommendation

**For Testing:**
→ Render (free + easy)

**For Production (Free):**
→ Koyeb + UptimeRobot monitoring

**For Production (Paid):**
→ VPS ($5/mo DigitalOcean/Linode) with Docker

**For Quick Demo:**
→ Railway ($5 credit)

---

## 📝 Files Added

1. **Dockerfile** - Container definition
2. **DEPLOYMENT.md** - Complete deployment guide
3. **app.json** - Heroku one-click deploy
4. **Updated requirements.txt** - Added `requests` for health checks

---

## ✅ Deployment Checklist

Before deploying:
- [ ] Get bot tokens from @BotFather
- [ ] Create dump channel (private)
- [ ] Add bots as admin to channel
- [ ] Get channel ID from @userinfobot
- [ ] Choose deployment platform
- [ ] Prepare environment variables

After deploying:
- [ ] Test /start command
- [ ] Upload test file
- [ ] Verify link works
- [ ] Check download speed
- [ ] Setup monitoring (if free tier)
- [ ] Add custom domain (optional)

---

## 🚀 You Can Now Deploy To:

✅ Koyeb (free)  
✅ Render (free)  
✅ Railway ($5 credit)  
✅ Heroku (one-click)  
✅ Any VPS (Docker)  
✅ Local machine (Docker)  

**See DEPLOYMENT.md for detailed instructions for each platform!**
