#!/bin/bash

# PlexMem - Debug Startup Script
# Starts services with console output and DEBUG_VERBOSE enabled

set -e

# Export debug flag
export DEBUG_VERBOSE=True

echo "╔═══════════════════════════════════════╗"
echo "║      PlexMem DEBUG MODE STARTUP       ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "run_api.py" ]; then
    echo "❌ Error: run_api.py not found. Are you in the plexmem directory?"
    exit 1
fi

# Kill existing processes - AGGRESSIVE
echo "🧹 Очистка старых процессов..."
pkill -9 -f "python.*run_api" 2>/dev/null || true
pkill -9 -f "python.*run_bot" 2>/dev/null || true
pkill -9 -f "uvicorn" 2>/dev/null || true
# Kill by port
if command -v fuser &> /dev/null; then
    fuser -k 8000/tcp 2>/dev/null || true
fi
sleep 2
echo "✅ Готово"
echo ""

# Check venv
if [ -d "venv" ]; then
    echo "📦 Активация venv..."
    source venv/bin/activate
else
    echo "❌ Venv не найден! Создайте: python -m venv venv"
    exit 1
fi
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Остановка сервисов..."
    kill $API_PID 2>/dev/null || true
    kill $BOT_PID 2>/dev/null || true
    pkill -9 -f "uvicorn|run_api|run_bot" 2>/dev/null || true
    echo "✅ Сервисы остановлены"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start API (foreground with output to console)
echo "╔════════════════════════════════════════════╗"
echo "║  [1/2] Запуск API (вывод в консоль)       ║"
echo "╚════════════════════════════════════════════╝"
echo ""
python run_api.py &
API_PID=$!

# Wait for API to be ready
echo ""
echo "⏳ Ждём запуска API (5 сек)..."
sleep 5

# Check if API is running
if ! kill -0 $API_PID 2>/dev/null; then
    echo "❌ API не запустился! Проверьте ошибки выше."
    exit 1
fi

# Start Bot (foreground with output to console)
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  [2/2] Запуск Telegram Bot (консоль)      ║"
echo "╚════════════════════════════════════════════╝"
echo ""
python run_bot.py &
BOT_PID=$!

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║      🎯 DEBUG РЕЖИМ: ВСЁ РАБОТАЕТ!        ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📊 API PID:  $API_PID"
echo "🤖 Bot PID:  $BOT_PID"
echo ""
echo "💡 Логи видны в консоли выше"
echo "⚠️  Нажми Ctrl+C для остановки"
echo ""

wait -n $API_PID $BOT_PID
cleanup
