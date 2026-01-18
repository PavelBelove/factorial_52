#!/bin/bash

# PlexMem - Debug Startup Script
# Starts services with console output and DEBUG_VERBOSE enabled

set -e

# Export debug flag
export DEBUG_VERBOSE=True

echo "╔═══════════════════════════════════════╗"
echo "║      PlexMem DEBUG MODE STARTUP       ║"
echo "╚═══════════════════════════════════════╝"

# Check venv
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $API_PID 2>/dev/null || true
    kill $BOT_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start API
echo "[1/2] Starting API server (Console Output)..."
python run_api.py &
API_PID=$!

# Wait for API to be ready
echo "Waiting for API..."
sleep 5

# Start Bot
echo "[2/2] Starting Telegram bot (Console Output)..."
python run_bot.py &
BOT_PID=$!

echo "Check console for [DEBUG_VERBOSE] logs!"
echo "Press Ctrl+C to stop."

wait -n $API_PID $BOT_PID
cleanup
