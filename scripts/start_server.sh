#!/bin/bash
# Start the Social Hub backend server

cd "$(dirname "$0")/.."
echo "Starting Social Hub backend server..."
python run.py > logs/server.log 2>&1 &
BACKEND_PID=$!

sleep 3

if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
  echo "✓ Server started successfully (PID: $BACKEND_PID)"
  echo "✓ Server running at http://localhost:8000"
  echo "✓ Logs: logs/server.log"
else
  echo "⚠ Server may not be running. Check logs/server.log"
fi

