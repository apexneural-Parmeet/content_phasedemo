# Social Hub - Multi-Platform Social Media Manager

> AI-powered content generation and scheduling for Facebook, Instagram, Twitter & Reddit

## 🌟 Features

- **🤖 AI Content Generation** - Create platform-optimized content with GPT-4
- **🎨 Dual Image Providers** - Choose between Nano Banana (fast) or DALL-E 3 (premium)
- **📅 Smart Scheduling** - Schedule posts across all platforms
- **💬 Telegram Bot** - Full feature parity with web interface
- **🔄 Multi-Platform** - Post to Facebook, Instagram, Twitter, Reddit simultaneously
- **✏️ Caption Editing** - Customize content for each platform
- **📊 Connection Management** - Secure credential storage

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- API Keys (OpenAI, Fal.ai, Social Media platforms)

### 1. Backend Setup
```bash
cd "/Users/parmeetsingh/Documents/dbaas/facebook try"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start backend server
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 3. Telegram Bot (Optional)
```bash
# In project root with venv activated
python bot.py
```

## 📁 Project Structure

```
/
├── app/                    # Backend
│   ├── clients/           # API clients
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   │   ├── ai/           # AI services (organized)
│   │   └── ...
│   ├── telegram/          # Telegram bot modules
│   │   ├── handlers/     # (Future: handler modules)
│   │   └── utils/        # Keyboards, formatters
│   ├── scheduler/        # Background jobs
│   └── main.py           # FastAPI app
├── bot.py                # Telegram bot entry
├── frontend/             # React frontend
│   └── src/
│       ├── components/
│       ├── pages/
│       └── App.jsx
├── logs/                 # Application logs
├── uploads/              # User uploads
└── docs/                 # Documentation
```

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI (required for content & DALL-E images)
OPENAI_API_KEY=sk-...

# Fal.ai (required for Nano Banana images)
FAL_KEY=...

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=...
TELEGRAM_LOGIN_ID=apex
TELEGRAM_LOGIN_PASSWORD=apexbeta

# Social Media (configure via Connections page or .env)
FACEBOOK_ACCESS_TOKEN=...
INSTAGRAM_ACCESS_TOKEN=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USERNAME=...
REDDIT_PASSWORD=...
```

## 🎯 Usage

### Web Interface

1. **Generate AI Content** (`/generate`)
   - Enter a topic
   - Choose tone (casual, professional, etc.)
   - Select image provider (Nano Banana or DALL-E)
   - Select image style
   - Edit content per platform
   - Post now or schedule

2. **Create Manual Post** (`/`)
   - Upload image
   - Write caption
   - Select platforms
   - Post or schedule

3. **View Schedule** (`/schedule`)
   - Calendar view
   - List view
   - Manage scheduled posts

4. **Manage Connections** (`/connections`)
   - Add/edit credentials
   - Test connections
   - View status

### Telegram Bot

```
/start  - Show main menu
/login  - Login (ID: apex, Pass: apexbeta)
/logout - Logout

Features:
• Generate AI Content
• Create Manual Post
• View Scheduled Posts
• Platform Status
• Caption Editing
• Provider Selection
```

## 🧪 Testing

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for comprehensive testing instructions.

Quick test:
```bash
# Test all imports
python -c "from app.main import app; from app.services.telegram_bot_service import TelegramBotService; print('✅ All OK')"

# Test backend health
curl http://localhost:8000/api/health
```

## 📚 Documentation

- [Code Organization](./CODE_ORGANIZATION.md) - Project structure
- [Testing Guide](./TESTING_GUIDE.md) - How to test features
- [Refactoring Plan](./REFACTORING_PLAN.md) - Future improvements

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Web framework
- OpenAI GPT-4 - Content generation
- DALL-E 3 - Premium images
- Fal.ai Nano Banana - Fast images
- APScheduler - Job scheduling
- Python-Telegram-Bot - Bot framework

**Frontend:**
- React - UI framework
- Vite - Build tool
- CSS - Styling

**Infrastructure:**
- uvicorn - ASGI server
- httpx - HTTP client

## 🔒 Security

- ✅ API keys stored in `.env` (not committed)
- ✅ Credentials stored locally in `user_credentials.json`
- ✅ Telegram bot requires authentication
- ✅ Rate limiting on API endpoints
- ✅ Input validation on all requests
- ✅ Sensitive files in `.gitignore`

## 🐛 Troubleshooting

### Bot: "Conflict: terminated by other getUpdates"
```bash
pkill -f "python bot.py"
sleep 2
python bot.py
```

### Frontend: 500 errors
- Check backend is running: `curl http://localhost:8000/api/health`
- Check logs in terminal

### Images not generating
- Verify OpenAI API key: `cat .env | grep OPENAI_API_KEY`
- Verify Fal.ai key: `cat .env | grep FAL_KEY`

### Scheduled posts not executing
- Check backend logs for scheduler errors
- Verify `scheduled_posts.json` is valid JSON

## 📝 Recent Improvements

### Code Organization ✅
- Extracted Telegram utilities (keyboards, formatters)
- Organized AI style configuration
- Added session manager
- Better documentation

### Structure Benefits
- ✅ Modular code
- ✅ Reusable components
- ✅ Easy to maintain
- ✅ Zero breaking changes
- ✅ All features working

## 🤝 Contributing

This is a personal project, but feel free to:
1. Report issues
2. Suggest features
3. Submit pull requests

## 📄 License

Private project - All rights reserved

## 🙏 Acknowledgments

- OpenAI for GPT-4 and DALL-E 3
- Fal.ai for Nano Banana model
- FastAPI and React communities

---

**Status:** ✅ Production Ready  
**Last Updated:** October 15, 2025  
**Version:** 2.0 (Organized Structure)
