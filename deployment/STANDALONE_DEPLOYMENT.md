# Standalone Telegram Bot Deployment Guide

## 🎯 Overview

This guide shows how to deploy **ONLY the Telegram bot** without the backend or frontend. The bot is fully self-contained with its own scheduler.

---

## ✅ What You're Deploying

**Single service:**
- ✅ Telegram Bot (with integrated scheduler)
- ✅ AI content generation
- ✅ Multi-platform posting
- ✅ Scheduling functionality
- ✅ All features working

**NOT deploying:**
- ❌ FastAPI Backend
- ❌ React Frontend
- ❌ Web interface

---

## 📋 Prerequisites

- Ubuntu/Debian server (CloudPanel or any VPS)
- Python 3.12+
- Root or sudo access
- API keys ready

---

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Prepare Server

```bash
# SSH to your server
ssh root@your-server-ip

# Create directory
mkdir -p /home/socialhub
cd /home/socialhub
```

---

### Step 2: Upload Files

**From your local machine:**

```bash
# Navigate to project
cd "/Users/parmeetsingh/Documents/dbaas/facebook try"

# Upload ONLY needed files (no frontend, no backend routes)
rsync -avz --progress \
  --exclude 'frontend' \
  --exclude 'node_modules' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude 'tests' \
  --exclude 'docs' \
  --exclude 'logs' \
  --exclude '.git' \
  --include 'app/***' \
  --include 'data/***' \
  --include 'standalone_bot.py' \
  --include 'requirements.txt' \
  --exclude '*' \
  . root@your-server-ip:/home/socialhub/
```

**OR manually copy these files/folders:**
- `app/` (entire folder)
- `data/` (entire folder)
- `standalone_bot.py`
- `requirements.txt`

---

### Step 3: Install Dependencies

```bash
# On the server
cd /home/socialhub

# Install Python 3.12
apt update
apt install python3.12 python3.12-venv python3-pip -y

# Create virtual environment
python3.12 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 4: Create .env File

```bash
nano .env
```

**Add your configuration:**

```env
# Telegram Bot (REQUIRED)
TELEGRAM_BOT_TOKEN=8071693389:AAE-1xci3i0hqE7Yk9Rd1opRJIkAUgRCF64
TELEGRAM_LOGIN_ID=apex
TELEGRAM_LOGIN_PASSWORD=apexbeta

# OpenAI (REQUIRED for AI features)
OPENAI_API_KEY=your_openai_key_here

# Fal.ai (for Nano Banana fast images)
FAL_KEY=your_fal_key_here

# These are loaded from data/credentials/user_credentials.json
# No need to add here if already in JSON file
```

**Save:** Ctrl+X, Y, Enter

---

### Step 5: Set Permissions

```bash
cd /home/socialhub

# Create logs directory
mkdir -p logs

# Set proper permissions
chmod 700 data/credentials
chmod 600 data/credentials/*.json
chmod 755 data/storage
chmod 644 data/storage/*.json

# Make bot executable
chmod +x standalone_bot.py
```

---

### Step 6: Test Run (Optional but Recommended)

```bash
# Activate venv
source venv/bin/activate

# Test run
python standalone_bot.py
```

**Expected output:**
```
🚀 Standalone Telegram Bot - No Backend Required!

======================================================================
🤖 Social Hub Telegram Bot (Standalone Mode)
======================================================================

✅ Configuration validated

📅 Initializing scheduler...
✅ Scheduler started successfully
🔄 Restoring scheduled posts...
✅ Scheduled jobs restored

----------------------------------------------------------------------
📱 Starting Telegram bot polling...
----------------------------------------------------------------------

✨ Bot is now running!
   • AI content generation enabled
   • Scheduling enabled
   • All platforms ready

💡 Send /start to your bot in Telegram to begin

Press Ctrl+C to stop the bot
----------------------------------------------------------------------
```

**Test in Telegram:** Send `/start` to your bot

**Stop test:** Press Ctrl+C

---

### Step 7: Create Systemd Service

```bash
nano /etc/systemd/system/socialhub-bot.service
```

**Add this content:**

```ini
[Unit]
Description=Social Hub Standalone Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/socialhub
Environment="PATH=/home/socialhub/venv/bin"
ExecStart=/home/socialhub/venv/bin/python standalone_bot.py
Restart=always
RestartSec=10
StandardOutput=append:/home/socialhub/logs/bot.log
StandardError=append:/home/socialhub/logs/bot_error.log

[Install]
WantedBy=multi-user.target
```

**Save:** Ctrl+X, Y, Enter

---

### Step 8: Start the Service

```bash
# Reload systemd
systemctl daemon-reload

# Enable auto-start on boot
systemctl enable socialhub-bot

# Start the service
systemctl start socialhub-bot

# Check status
systemctl status socialhub-bot
```

**Expected output:**
```
● socialhub-bot.service - Social Hub Standalone Telegram Bot
   Loaded: loaded (/etc/systemd/system/socialhub-bot.service; enabled)
   Active: active (running) since ...
```

---

### Step 9: Verify Everything Works

**Check logs:**
```bash
tail -f /home/socialhub/logs/bot.log
```

**Test in Telegram:**
1. Open Telegram
2. Find your bot
3. Send `/start`
4. Login with `apex` / `apexbeta`
5. Test AI generation
6. Test scheduling

---

## 🔧 Management Commands

### View Logs
```bash
# Real-time logs
tail -f /home/socialhub/logs/bot.log

# Error logs
tail -f /home/socialhub/logs/bot_error.log

# Last 50 lines
tail -n 50 /home/socialhub/logs/bot.log
```

### Control Service
```bash
# Start
systemctl start socialhub-bot

# Stop
systemctl stop socialhub-bot

# Restart
systemctl restart socialhub-bot

# Status
systemctl status socialhub-bot

# Disable auto-start
systemctl disable socialhub-bot
```

### Monitor
```bash
# Check if running
systemctl is-active socialhub-bot

# View service logs
journalctl -u socialhub-bot -f

# Last 100 lines
journalctl -u socialhub-bot -n 100
```

---

## 🛠️ Troubleshooting

### Issue: Bot not starting

**Check logs:**
```bash
journalctl -u socialhub-bot -n 50 --no-pager
```

**Common fixes:**
```bash
# Check Python path
which python
# Should be: /home/socialhub/venv/bin/python

# Reinstall dependencies
cd /home/socialhub
source venv/bin/activate
pip install -r requirements.txt

# Check permissions
ls -la data/credentials/
```

---

### Issue: "Module not found"

```bash
# Activate venv
cd /home/socialhub
source venv/bin/activate

# Check if app folder exists
ls -la app/

# Reinstall
pip install -r requirements.txt
```

---

### Issue: "TELEGRAM_BOT_TOKEN not found"

```bash
# Check .env file
cat .env | grep TELEGRAM_BOT_TOKEN

# Should not be empty
# If empty, edit .env:
nano .env
```

---

### Issue: Scheduled posts not executing

```bash
# Check scheduler is running
tail -f logs/bot.log | grep -i scheduler

# Should see:
# ✅ Scheduler started successfully
# ✅ Scheduled jobs restored
```

---

## 📊 Resource Usage

**Expected:**
- RAM: ~150-200MB
- CPU: <5% idle, 20-40% when generating
- Disk: ~100MB (without uploads)

**Monitor:**
```bash
# Memory usage
ps aux | grep standalone_bot.py

# Resource limits
systemctl show socialhub-bot | grep -i memory
```

---

## 🔄 Updates

**To update the bot:**

```bash
# Stop service
systemctl stop socialhub-bot

# Upload new files (from local machine)
rsync -avz standalone_bot.py root@server:/home/socialhub/
rsync -avz app/ root@server:/home/socialhub/app/

# Restart
systemctl start socialhub-bot

# Verify
systemctl status socialhub-bot
```

---

## 🔐 Security Tips

1. **Firewall:** No ports needed (bot connects out to Telegram)
2. **Permissions:** Keep credentials at 600
3. **Backups:** Backup `data/` directory regularly
4. **Logs:** Rotate logs to prevent disk filling

```bash
# Setup log rotation
nano /etc/logrotate.d/socialhub
```

Add:
```
/home/socialhub/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

---

## ✅ Deployment Checklist

- [ ] Server prepared
- [ ] Files uploaded
- [ ] Python 3.12 installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured with API keys
- [ ] Permissions set correctly
- [ ] Test run successful
- [ ] Systemd service created
- [ ] Service started and enabled
- [ ] Bot responds in Telegram
- [ ] AI generation works
- [ ] Scheduling works
- [ ] Logs are clean

---

## 🎉 Success!

Your standalone Telegram bot is now running 24/7!

**Features working:**
- ✅ AI content generation (DALL-E & Nano Banana)
- ✅ Multi-platform posting (FB, IG, X, Reddit)
- ✅ Scheduling (integrated scheduler)
- ✅ Caption editing
- ✅ Platform selection
- ✅ Authentication

**Only 1 service to manage!**

---

## 📞 Quick Reference

```bash
# Start bot
systemctl start socialhub-bot

# Stop bot
systemctl stop socialhub-bot

# View logs
tail -f /home/socialhub/logs/bot.log

# Check status
systemctl status socialhub-bot
```

**That's it! Simple and standalone!** 🚀

