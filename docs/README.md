# 📚 Documentation Index

Complete documentation for the Social Media AI Manager project.

---

## 🚀 Getting Started

- **[Quick Start Guide](./QUICK_START.md)** - Get up and running in 5 minutes
- **[Backend Architecture](./BACKEND_ARCHITECTURE.md)** - System design and structure

---

## 🤖 AI Features

- **[AI Content Generator](./AI_GENERATOR_GUIDE.md)** - How AI generation works
- **[Tone & Style Guide](./TONE_AND_STYLE_GUIDE.md)** - Available tones and image styles
- **[Content-Image Coordination](./CONTENT_IMAGE_COORDINATION.md)** - How images match content
- **[Nano Banana Integration](./NANO_BANANA_INTEGRATION.md)** - Ultra-fast image generation with Fal.ai

---

## 📱 Platform Management

- **[Platform Connections](./PLATFORM_CONNECTIONS.md)** - Managing social media credentials
- **[Credentials Migration](./ENV_TO_CREDENTIALS_MIGRATION.md)** - Loading from .env file
- **[Credentials UX](./CREDENTIALS_UX_UPDATE.md)** - How the credentials UI works

---

## 📅 Scheduling

- **[Scheduler Guide](./SCHEDULER_GUIDE.md)** - How to schedule posts
- **[Publish to All Feature](./PUBLISH_TO_ALL_FEATURE.md)** - Multi-platform publishing

---

## 🤖 Telegram Bot

- **[Telegram Bot Setup](./TELEGRAM_BOT_SETUP.md)** - How to configure the bot
- **[Bot Provider Choice](./TELEGRAM_BOT_PROVIDER_CHOICE.md)** - Choosing Nano Banana vs DALL-E
- **[Bot Cancel Feature](./TELEGRAM_CANCEL_FEATURE.md)** - Cancel & restart functionality
- **[Bot Regenerate with Provider](./TELEGRAM_REGENERATE_WITH_PROVIDER_CHOICE.md)** - Provider selection on regenerate

---

## 🎨 Frontend Features

- **[YouTube-Style UI](./YOUTUBE_UI_GUIDE.md)** - UI design philosophy
- **[Frontend Regenerate with Provider](./FRONTEND_REGENERATE_WITH_PROVIDER_CHOICE.md)** - Image regeneration modal

---

## 📊 Feature Summaries

- **[Complete Features Summary](./COMPLETE_FEATURES_SUMMARY.md)** - All implemented features
- **[AI Generator Complete](./AI_CONTENT_GENERATOR_COMPLETE.md)** - AI system overview
- **[Refactor Summary](./REFACTOR_SUMMARY.md)** - Code reorganization history

---

## 📋 Quick Reference

### Rate Limits
- AI Generation: 10/minute
- Image Regeneration: 15/minute  
- Content Regeneration: 20/minute
- Content Refinement: 30/minute
- Posting: 30/minute

### Supported Platforms
- Facebook (Page Access Token)
- Instagram (Access Token + Account ID)
- Twitter (API Keys + Tokens)
- Reddit (Client ID + Secret + Credentials)
- Telegram (Bot Token + Channel ID)

### Image Providers
- 🍌 Nano Banana (Fal.ai) - 2-3 seconds, $0.001/image
- 🎨 DALL-E 3 (OpenAI) - 15-20 seconds, $0.04/image

### Image Styles
- Realistic, Minimal, Anime, 2D Art, Comic Book, Sketch, Vintage, Disney

### Content Tones
- Casual, Professional, Corporate, Funny, Inspirational, Educational, Storytelling, Promotional

---

## 🔧 Development

### Start Services
```bash
# Backend
python run.py

# Frontend
cd frontend && npm run dev

# Telegram Bot
python bot.py
```

### Project Structure
```
/
├── app/              # Backend application
│   ├── routes/       # API endpoints
│   ├── services/     # Business logic
│   ├── clients/      # External API clients
│   ├── scheduler/    # Post scheduling
│   └── config.py     # Configuration
├── frontend/         # React frontend
│   └── src/
│       ├── pages/    # Page components
│       ├── components/ # Reusable components
│       └── context/  # React context
├── docs/             # Documentation (you are here!)
├── scripts/          # Utility scripts
├── logs/             # Server logs
└── uploads/          # User uploads & AI images
```

---

## 📞 Support

For issues or questions, check the specific guides above or review the main [README](../README.md).

---

**Last Updated:** October 14, 2025  
**Version:** 1.0.0

