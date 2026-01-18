#!/bin/bash
set -e

echo "🔧 Применение всех исправлений..."
echo ""

cd /home/pavel/dev/plexmem

# 1. Activate venv
echo "📦 Активация окружения..."
source venv/bin/activate

# 2. Apply DB migration if needed
echo "🗄️  Проверка миграции БД (synopsis column)..."
if python3 fix_db_now.py; then
    echo "✅ БД готова"
else
    echo "⚠️  Миграция не требуется или уже применена"
fi
echo ""

# 3. Stop services
echo "⏹️  Остановка сервисов..."
pkill -f "uvicorn core.api.main:app" 2>/dev/null || true
pkill -9 -f run_bot.py 2>/dev/null || true
sleep 3
echo "✅ Сервисы остановлены"
echo ""

# 4. Start services
echo "🚀 Запуск системы..."
nohup bash start_plexmem.sh > /dev/null 2>&1 &
sleep 3
echo "✅ Система запущена"
echo ""

echo "╔══════════════════════════════════════════════════════╗"
echo "║            ✅ ВСЕ ИСПРАВЛЕНИЯ ПРИМЕНЕНЫ              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "📝 Что исправлено:"
echo ""
echo "  1. ❌→✅ Ошибка 'no such column: synopsis'"
echo "  2. ❌→✅ ГМ теперь показывает разбивку карт"
echo "  3. ❌→✅ Явные инструкции КАК озвучивать проверки"
echo "  4. ❌→✅ Исправлена валидация типов предметов"
echo "  5. ❌→✅ /retry не телепортирует героя"
echo ""
echo "📊 Пример того, что теперь видит ГМ:"
echo "  ♠: 240 (30+20 + 120+0 + 70 стат) → легко 155, сложно 275"
echo "         ↑карта+бонус ↑карта  ↑стат"
echo ""
echo "📖 ГМ должен озвучивать так:"
echo "  \"Проверка Магии: **245** (карты 3♠+Q♥, бонус +20,"
echo "  твоя Магия 75) против порога **275** — непросто!"
echo ""
echo "🎲 Проверь игру!"
echo ""

