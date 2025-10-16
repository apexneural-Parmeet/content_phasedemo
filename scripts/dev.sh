#!/bin/bash
# Development script - Start backend, frontend, and Telegram bot

echo "🚀 Starting Social Hub Development Environment..."
echo ""

cd "$(dirname "$0")/.."

# Start backend
echo "📡 Starting backend server..."
python run.py > logs/server.log 2>&1 &
BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
  echo "✓ Backend is healthy at http://localhost:8000"
else
  echo "⚠ Backend may not be running properly. Check logs/server.log"
fi

# Start Telegram bot if token is configured
if grep -q "TELEGRAM_BOT_TOKEN=.*[^[:space:]]" .env 2>/dev/null; then
  echo ""
  echo "🤖 Starting Telegram bot..."
  python bot.py > logs/telegram_bot.log 2>&1 &
  BOT_PID=$!
  sleep 2
  if ps -p $BOT_PID > /dev/null; then
    echo "✓ Telegram bot started (PID: $BOT_PID)"
  else
    echo "⚠ Telegram bot failed to start. Check logs/telegram_bot.log"
  fi
else
  echo ""
  echo "⚠ Telegram bot token not configured (skipping bot)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Services Running:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: cd frontend && npm run dev (http://localhost:5173)"
echo "  Bot:      Check Telegram"
echo ""
echo "📝 Logs:"
echo "  Backend:  tail -f logs/server.log"
echo "  Bot:      tail -f logs/telegram_bot.log"
echo ""
echo "🛑 To stop: ./scripts/stop_server.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

