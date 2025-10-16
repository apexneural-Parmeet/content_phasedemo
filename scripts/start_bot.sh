#!/bin/bash
# Start the Telegram bot (standalone)

cd "$(dirname "$0")/.."
echo "🤖 Starting Telegram Bot..."
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
  echo "⚠️ WARNING: Backend server is not running!"
  echo "Please start the backend first:"
  echo "  python run.py"
  echo ""
  read -p "Continue anyway? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Start bot in background
python bot.py > logs/telegram_bot.log 2>&1 &
BOT_PID=$!

sleep 2

# Check if bot is still running
if ps -p $BOT_PID > /dev/null; then
  echo "✅ Telegram bot started successfully (PID: $BOT_PID)"
  echo "📝 Logs: logs/telegram_bot.log"
  echo ""
  echo "📱 Open Telegram and search for your bot!"
  echo ""
  echo "To stop: kill $BOT_PID"
else
  echo "❌ Bot failed to start. Check logs/telegram_bot.log"
fi

