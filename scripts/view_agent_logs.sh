#!/bin/bash
# Quick agent logs viewer

LOGS_DIR="logs/agents"

echo "====================================="
echo "PlexMem Agent Logs Viewer"
echo "====================================="
echo ""

if [ ! -d "$LOGS_DIR" ]; then
    echo "❌ Logs directory not found: $LOGS_DIR"
    exit 1
fi

# Check for available logs
echo "📂 Available logs:"
echo ""

for log_file in "$LOGS_DIR"/*.log; do
    if [ -f "$log_file" ]; then
        filename=$(basename "$log_file")
        filesize=$(du -h "$log_file" | cut -f1)
        timestamp=$(stat -c %y "$log_file" | cut -d' ' -f1-2 | cut -d'.' -f1)
        echo "  ✓ $filename ($filesize) - Last updated: $timestamp"
    fi
done

if ! ls "$LOGS_DIR"/*.log &> /dev/null; then
    echo "  ℹ️  No logs yet. Make a turn in the game to generate logs."
    echo ""
    echo "Logs will appear after:"
    echo "  - GM responds to player"
    echo "  - Quantizer creates/updates quants"
    echo "  - Summarizer condenses history"
    echo "  - Translator converts turn to English JSON"
    exit 0
fi

echo ""
echo "====================================="
echo "Commands:"
echo "  cat logs/agents/gm_last.log          - View full GM log"
echo "  cat logs/agents/quantizer_last.log   - View Quantizer log"
echo "  cat logs/agents/translator_last.log  - View Translator log"
echo ""
echo "  # View only response (skip context):"
echo "  grep -A 9999 'RESPONSE' logs/agents/gm_last.log"
echo ""
echo "  # View only context (skip response):"
echo "  sed -n '/CONTEXT/,/RESPONSE/p' logs/agents/gm_last.log | head -n -2"
echo "====================================="

