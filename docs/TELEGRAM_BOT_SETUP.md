# 🤖 Telegram Bot Setup Guide

## ✅ What Was Fixed

### The Problem
The Telegram bot was trying to run **inside** the FastAPI server using `asyncio.create_task()`, which caused:
- **Event loop conflicts** - Two async applications fighting for control
- **Crashes** - Bot and FastAPI couldn't share the same event loop
- **Unreliable startup** - Process would fail to initialize properly

### The Solution
The bot now runs as a **separate, independent process**:
- ✅ Backend (FastAPI) runs independently
- ✅ Telegram bot runs independently  
- ✅ Both can communicate via shared services
- ✅ No more event loop conflicts
- ✅ Clean, production-ready architecture

---

## 🚀 How to Run Everything

### Method 1: Run All Services at Once (Recommended for Development)

```bash
./scripts/dev.sh
```

This will start:
- ✅ Backend API (port 8000)
- ✅ Telegram Bot (if token is configured)
- You'll need to manually start the frontend:
  ```bash
  cd frontend && npm run dev
  ```

### Method 2: Run Services Individually (Recommended for Production)

#### Step 1: Start Backend
```bash
python run.py
```
Backend will be available at `http://localhost:8000`

#### Step 2: Start Telegram Bot (Optional)
```bash
python bot.py
```
The bot will start polling Telegram servers.

#### Step 3: Start Frontend (Optional)
```bash
cd frontend
npm run dev
```
Frontend will be available at `http://localhost:5173`

---

## 🛑 How to Stop Everything

```bash
./scripts/stop_server.sh
```

This stops:
- Backend server
- Telegram bot
- All related processes

---

## 📱 How the Bot Works

### 1. Bot Architecture
```
Telegram User
    ↓
Telegram Bot API
    ↓
Your Bot (bot.py)
    ↓
Backend Services (AI, Social Media, Scheduler)
    ↓
Social Media Platforms
```

### 2. Bot Features
- ✅ AI content generation (GPT-4o-mini)
- ✅ Image generation (DALL-E 3)
- ✅ Manual post creation
- ✅ Multi-platform publishing (Facebook, Instagram, Twitter, Reddit)
- ✅ Post scheduling
- ✅ Platform status checking

### 3. Bot Commands
- `/start` - Main menu
- `/cancel` - Cancel current operation

---

## 🔧 Configuration

### Required: Telegram Bot Token

1. **Get your bot token** from [@BotFather](https://t.me/botfather) on Telegram
2. **Add to `.env` file** (in project root):
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   ```

### Optional: Social Media API Keys

Add these to `.env` for full functionality:
```env
# OpenAI (for AI content generation)
OPENAI_API_KEY=your_key

# Facebook
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id

# Instagram
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_ACCOUNT_ID=your_account_id

# Twitter
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_secret

# Reddit
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

---

## 🧪 Testing the Bot

### 1. Start the Backend
```bash
python run.py
```
Wait for: `✅ Server is ready on http://localhost:8000`

### 2. Start the Bot
```bash
python bot.py
```
You should see:
```
🤖 Social Hub Telegram Bot
✅ Bot token configured
🔗 Backend API: http://localhost:8000
📱 Starting bot polling...
✅ Telegram bot handlers configured
🤖 Starting Telegram bot...
✅ Telegram bot started successfully!
📱 Open Telegram and search for your bot
⏳ Bot is running... Press Ctrl+C to stop
```

### 3. Test in Telegram
1. Open Telegram
2. Search for your bot (use the username you set with @BotFather)
3. Send `/start`
4. You should see the main menu with 4 options

---

## 🐛 Troubleshooting

### Bot won't start
**Check 1:** Is `TELEGRAM_BOT_TOKEN` in `.env`?
```bash
grep TELEGRAM_BOT_TOKEN .env
```

**Check 2:** Is the backend running?
```bash
curl http://localhost:8000/api/health
```

**Check 3:** Check bot logs
```bash
tail -f logs/telegram_bot.log
```

### Backend won't start
**Check 1:** Install dependencies
```bash
pip install -r requirements.txt
```

**Check 2:** Check backend logs
```bash
tail -f logs/server.log
```

### Bot commands not working
**Check 1:** Make sure bot is running
```bash
ps aux | grep bot.py
```

**Check 2:** Try `/cancel` then `/start` to reset

---

## 📂 File Structure

```
├── bot.py                          # Telegram bot entry point (NEW)
├── run.py                          # Backend entry point
├── app/
│   ├── main.py                    # FastAPI app (bot integration removed)
│   ├── services/
│   │   └── telegram_bot_service.py  # Bot logic (updated)
│   └── ...
├── scripts/
│   ├── dev.sh                      # Start all services (updated)
│   ├── start_bot.sh                # Start bot only (updated)
│   └── stop_server.sh              # Stop all services (updated)
└── logs/
    ├── server.log                  # Backend logs
    └── telegram_bot.log            # Bot logs
```

---

## ✨ What's Different Now

| Before | After |
|--------|-------|
| Bot ran inside FastAPI | Bot runs independently |
| Event loop conflicts | Clean separation |
| Crashes on startup | Stable startup |
| Hard to debug | Clear logs for each service |
| Single point of failure | Services can restart independently |

---

## 🎯 Next Steps

1. ✅ **Test the bot** - Send `/start` and try generating content
2. ✅ **Monitor logs** - Watch `logs/telegram_bot.log` and `logs/server.log`
3. ✅ **Add error handling** - Bot will handle most errors gracefully
4. ✅ **Deploy** - Both services can be deployed separately (recommended)

---

## 📞 Need Help?

Check the logs first:
```bash
# Backend logs
tail -f logs/server.log

# Bot logs
tail -f logs/telegram_bot.log
```

**Common Issues:**
- Event loop conflict → Fixed! Bot runs separately now
- Port already in use → Run `./scripts/stop_server.sh`
- Bot not responding → Check if backend is running
- Commands timeout → Check your API keys in `.env`

---

---

## 🆕 **Latest Features**

### **1. Image Provider Choice** 🍌🎨

When generating content, users can choose between two image generators:

**🍌 Nano Banana (Fal.ai)**
- Ultra-fast (2-3 seconds)
- Cost-effective ($0.001/image)
- Great quality

**🎨 DALL-E 3 (OpenAI)**  
- Premium quality (15-20 seconds)
- Higher cost ($0.04/image)
- Excellent results

**Flow:**
```
Select Tone → Select Provider → Select Style → Generate
```

Users can choose different providers on regeneration!

---

### **2. Cancel & Start Over** 🔙

Added "Cancel & Start Over" buttons at every stage:

**Where:**
- ✅ Image approval stage
- ✅ Platform selection stage  
- ✅ Publish options stage
- ✅ Manual post creation

**What It Does:**
- Clears all progress
- Returns to main menu
- No need to type `/cancel`
- Quick restart

---

### **3. Regenerate with Provider Choice** 🔄

When clicking "Regenerate", bot asks:

```
🔄 Select Image Generator for Regeneration:

🍌 Nano Banana (Ultra Fast 2-3s)
🎨 DALL-E 3 (Premium 15-20s)
```

**Benefits:**
- Try Nano Banana for quick iterations
- Switch to DALL-E for final quality
- Full control every time

---

## 🎯 **Complete Bot Workflow**

```
/start
  ↓
Main Menu
  ↓
Generate AI Content
  ↓
Enter Topic
  ↓
Select Tone (Casual, Professional, etc.)
  ↓
Select Provider (🍌 Nano Banana or 🎨 DALL-E) ← NEW
  ↓
Select Style (Realistic, Anime, etc.)
  ↓
[Generating... 2-3s or 15-20s]
  ↓
Image Preview
├─ ✅ Approve
├─ ❌ Reject
├─ 🔄 Regenerate (Choose Provider) ← NEW
└─ 🔙 Cancel & Start Over ← NEW
  ↓
Platform Selection
├─ ✅ Approve platforms
├─ 🚀 Continue
└─ 🔙 Cancel & Start Over ← NEW
  ↓
Publish Options
├─ 🚀 Publish Now
├─ 📅 Schedule
└─ 🔙 Cancel & Start Over ← NEW
```

---

🎉 **Congratulations! Your Telegram bot is now properly configured with all latest features and ready to use!**

