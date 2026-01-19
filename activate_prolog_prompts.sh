#!/bin/bash

echo "🔄 Активация Prolog-промптов..."
echo ""

cd /home/pavel/dev/plexmem/prompts

# Backup current prompts
echo "📦 Создание резервных копий..."
cp gm_system.md gm_system_natural.md 2>/dev/null || true
cp quantizer_system.md quantizer_system_natural.md 2>/dev/null || true
cp summarizer_system.md summarizer_system_natural.md 2>/dev/null || true
echo "✅ Резервные копии созданы"
echo ""

# Activate Prolog prompts
echo "⚡ Активация Prolog-промптов..."
cp gm_system_prolog.md gm_system.md
cp quantizer_system_prolog.md quantizer_system.md
cp summarizer_system_prolog.md summarizer_system.md
echo "✅ Prolog-промпты активированы"
echo ""

# Show what was done
echo "╔════════════════════════════════════════════╗"
echo "║     ✅ PROLOG PROMPTS ACTIVATED           ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Активированы промпты:"
echo "  📝 gm_system.md         (GM с Prolog правилами)"
echo "  📝 quantizer_system.md  (Quantizer с Prolog)"
echo "  📝 summarizer_system.md (Summarizer с Prolog)"
echo ""
echo "Старые промпты сохранены как *_natural.md"
echo ""
echo "💡 Перезапусти систему для применения:"
echo "   pkill -9 -f 'python.*run_api'"
echo "   ./start_simple.sh"
echo ""

