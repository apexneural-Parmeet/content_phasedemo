#!/bin/bash
# Stop all Social Hub services

echo "🛑 Stopping all services..."

# Kill backend server
ps aux | grep 'run.py\|python.*server\|uvicorn' | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
echo "✓ Backend stopped"

# Kill Telegram bot
ps aux | grep 'bot.py' | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
echo "✓ Telegram bot stopped"

# Kill any remaining python processes on ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

echo "✅ All servers stopped"

