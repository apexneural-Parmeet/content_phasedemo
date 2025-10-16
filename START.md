# 🚀 Social Hub - Quick Start Guide

## ✅ Setup Complete!

Your Social Hub is fully configured and ready to use!

---

## 📱 Start Telegram Bot (Recommended)

```bash
cd /Users/parmeetsingh/Documents/final/content-phase1-master
python3 standalone_bot.py
```

**Features:**
- ✅ AI content generation (GPT-4 + DALL-E 3 + Nano Banana)
- ✅ Multi-platform posting (Facebook, Instagram, Twitter, Reddit)
- ✅ Scheduling with integrated scheduler
- ✅ Caption editing
- ✅ Platform selection
- ✅ Full Telegram interface

**Login Credentials:**
- ID: `apex`
- Password: `apexbeta`

---

## 🌐 Start Full Stack (Backend + Frontend)

### Terminal 1 - Backend:
```bash
cd /Users/parmeetsingh/Documents/final/content-phase1-master
python3 run.py
```

### Terminal 2 - Frontend:
```bash
cd /Users/parmeetsingh/Documents/final/content-phase1-master/frontend
npm install  # First time only
npm run dev
```

Then open: http://localhost:5173

---

## 🧪 Test Your Bot

1. Open Telegram
2. Search for your bot (token: ...vuaXRsK8)
3. Send `/start`
4. Login with `apex` / `apexbeta`
5. Try "Generate AI Content"

---

## 📋 Available Platforms

All platforms are configured and ready:
- ✅ Facebook
- ✅ Instagram
- ✅ Twitter/X
- ✅ Reddit

---

## ⚠️ SECURITY REMINDER

**Your API keys were exposed in the conversation!**

Please rotate these keys ASAP:
- Telegram Bot Token (via @BotFather)
- OpenAI API Key
- Fal.ai Key
- Social media credentials

---

## 🛠️ Management Commands

```bash
# View logs (if running in background)
tail -f logs/bot.log

# Stop bot (Ctrl+C in terminal)

# Restart backend
pkill -f "python3 run.py" && python3 run.py
```

---

## 📚 Documentation

- Project structure: PROJECT_STRUCTURE.md
- Deployment guide: deployment/STANDALONE_DEPLOYMENT.md
- Full README: README.md

---

## 💡 Quick Tips

1. **Best image provider**: Nano Banana (2-3s) for speed, DALL-E 3 (15-20s) for quality
2. **Best tone for engagement**: Casual or Storytelling
3. **Schedule posts**: Use "Tomorrow 9 AM" quick button
4. **Edit captions**: Select platform → Edit → Send new text

---

## ❓ Troubleshooting

**Bot not responding?**
- Check bot is running: `ps aux | grep standalone_bot`
- Check logs: `tail logs/bot.log`
- Restart: Ctrl+C then `python3 standalone_bot.py`

**"Module not found"?**
- Reinstall: `pip3 install -r requirements.txt`

**API errors?**
- Check .env file has all keys
- Verify keys are valid (not expired)

---

🎉 **You're all set! Enjoy your Social Hub!**
