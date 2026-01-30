#!/bin/bash
# Deployment script for 52! World Bot
# Run this on the server: 176.120.21.138

set -e  # Exit on error

echo "==================================="
echo "52! World Bot - Deployment Script"
echo "==================================="

# Configuration
BOT_TOKEN="8417276425:AAG6-UIwgadm4ew8EQKfv_8kGW_SlzTHG2M"
OPENROUTER_API_KEY="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"
INSTALL_DIR="/home/plexmem/plexmem"
SERVICE_NAME="plexmem-bot"

echo ""
echo "Step 1: Stopping existing bot service..."
if systemctl is-active --quiet ${SERVICE_NAME}; then
    sudo systemctl stop ${SERVICE_NAME}
    echo "✓ Service stopped"
else
    echo "✓ Service not running"
fi

echo ""
echo "Step 2: Updating code from git..."
cd ${INSTALL_DIR}
git fetch origin
git checkout main
git pull origin main
echo "✓ Code updated to latest main branch"

echo ""
echo "Step 3: Updating configuration..."
cat > ${INSTALL_DIR}/.env << EOF
# OpenRouter API
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}

# Models per agent
GM_MODEL="deepseek/deepseek-v3.2"
QUANTIZER_MODEL="x-ai/grok-4.1-fast"
SUMMARIZER_MODEL="x-ai/grok-4.1-fast"
TRANSLATOR_MODEL="x-ai/grok-4.1-fast"

# Database
DATABASE_URL=sqlite:///data/plexmem.db

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
DEBUG_VERBOSE=False

# Memory System Configuration
MAX_QUANTS_PER_REQUEST=10
RAW_TURNS_MIN=4
RAW_TURNS_MAX=7
SUMMARY_SIZE_THRESHOLD=20000
QUANTIZER_TRIGGER_TURNS=3

# Telegram Bot
TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
EOF

echo "✓ Configuration updated"

echo ""
echo "Step 4: Installing/updating dependencies..."
cd ${INSTALL_DIR}
# Activate virtual environment if exists, or create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "Step 5: Creating/updating systemd service..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=52! World - Infinite Book Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin"
Environment="PYTHONPATH=${INSTALL_DIR}"
ExecStart=${INSTALL_DIR}/venv/bin/python telegram/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo "✓ Service file created"

echo ""
echo "Step 6: Starting bot service..."
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}
echo "✓ Service started"

echo ""
echo "Step 7: Checking status..."
sleep 2
sudo systemctl status ${SERVICE_NAME} --no-pager -l

echo ""
echo "==================================="
echo "✓ Deployment complete!"
echo "==================================="
echo ""
echo "Useful commands:"
echo "  View logs:    sudo journalctl -u ${SERVICE_NAME} -f"
echo "  Check status: sudo systemctl status ${SERVICE_NAME}"
echo "  Restart:      sudo systemctl restart ${SERVICE_NAME}"
echo "  Stop:         sudo systemctl stop ${SERVICE_NAME}"
echo ""
