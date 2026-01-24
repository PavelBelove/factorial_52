#!/bin/bash

# Quick deployment script for server
# Run this on the production server

set -e

echo "🚀 Factorial 52! - Quick Deploy Script"
echo "======================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as plexmem user (or root)
if [ "$USER" != "plexmem" ] && [ "$USER" != "root" ]; then
    echo -e "${YELLOW}⚠️  Recommended to run as plexmem user${NC}"
fi

# Navigate to app directory
cd /home/plexmem/plexmem || {
    echo -e "${RED}✗ App directory not found${NC}"
    exit 1
}

echo -e "${GREEN}✓ In app directory${NC}"

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git fetch origin
git reset --hard origin/main
echo -e "${GREEN}✓ Code updated${NC}"

# Activate virtual environment
source venv/bin/activate || {
    echo -e "${YELLOW}⚠️  Creating virtual environment...${NC}"
    python3.11 -m venv venv
    source venv/bin/activate
}

# Update dependencies
echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt --upgrade --quiet
echo -e "${GREEN}✓ Dependencies updated${NC}"

# Check .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from example...${NC}"
    cp .env.example .env
    echo -e "${RED}✗ Please edit .env file with production credentials!${NC}"
    exit 1
fi

# Ensure data directory exists
mkdir -p data logs logs/agents

# Restart services
echo "🔄 Restarting services..."
if [ "$USER" = "root" ]; then
    systemctl restart plexmem-api
    systemctl restart plexmem-bot
    echo -e "${GREEN}✓ Services restarted${NC}"
    
    # Check status
    sleep 2
    if systemctl is-active --quiet plexmem-api && systemctl is-active --quiet plexmem-bot; then
        echo -e "${GREEN}✓ All services running${NC}"
    else
        echo -e "${RED}✗ Some services failed to start${NC}"
        systemctl status plexmem-api --no-pager
        systemctl status plexmem-bot --no-pager
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Run with sudo to restart services:${NC}"
    echo "    sudo systemctl restart plexmem-api plexmem-bot"
fi

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📊 Check status:"
echo "  sudo systemctl status plexmem-api"
echo "  sudo systemctl status plexmem-bot"
echo ""
echo "📋 View logs:"
echo "  sudo journalctl -u plexmem-api -f"
echo "  sudo journalctl -u plexmem-bot -f"
echo "  tail -f logs/api.log"
echo ""
echo "🌐 API: http://localhost:8000"
echo "🤖 Bot: @factorial_52_bot"

