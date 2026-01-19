#!/bin/bash

# PlexMem - Script to start all services
# Author: PlexMem Team
# Description: Starts API server and Telegram bot

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║                                       ║"
echo "║        PlexMem Startup Script         ║"
echo "║  Predictive-Associative Memory System ║"
echo "║                                       ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check if we're in the right directory
if [ ! -f "run_api.py" ]; then
    echo -e "${RED}Error: run_api.py not found. Are you in the plexmem directory?${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create .env from .env.example and add your API keys${NC}"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate venv
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Check/install dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
if ! pip show fastapi > /dev/null 2>&1; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

# Create necessary directories
mkdir -p data logs

echo -e "${GREEN}✓ Directories ready${NC}"

# Kill existing processes - AGGRESSIVE
echo -e "${BLUE}Checking for existing processes...${NC}"
pkill -9 -f "python.*run_api" 2>/dev/null || true
pkill -9 -f "python.*run_bot" 2>/dev/null || true
pkill -9 -f "uvicorn" 2>/dev/null || true
# Kill by port
if command -v fuser &> /dev/null; then
    fuser -k 8000/tcp 2>/dev/null || true
fi
sleep 2
echo -e "${GREEN}✓ All old processes stopped${NC}"

# Start services
echo ""
echo -e "${BLUE}Starting services...${NC}"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
        wait $API_PID 2>/dev/null || true
    fi
    if [ ! -z "$BOT_PID" ]; then
        kill $BOT_PID 2>/dev/null || true
        wait $BOT_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}Services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start API server
echo -e "${BLUE}[1/2] Starting API server...${NC}"
python run_api.py > logs/api.log 2>&1 &
API_PID=$!
echo -e "${GREEN}✓ API server started (PID: $API_PID)${NC}"
echo -e "      Logs: logs/api.log"
echo -e "      URL:  http://localhost:8000"
echo -e "      Docs: http://localhost:8000/docs"

# Wait for API to be ready
echo -e "${BLUE}   Waiting for API to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Error: API failed to start${NC}"
        echo -e "${YELLOW}Check logs/api.log for details${NC}"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Start Telegram bot
echo -e "${BLUE}[2/2] Starting Telegram bot...${NC}"
python run_bot.py > logs/bot.log 2>&1 &
BOT_PID=$!
echo -e "${GREEN}✓ Telegram bot started (PID: $BOT_PID)${NC}"
echo -e "      Logs: logs/bot.log"

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}║                                     ║${NC}"
echo -e "${GREEN}║   PlexMem services are running!     ║${NC}"
echo -e "${GREEN}║                                     ║${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Services:${NC}"
echo -e "  • API Server:    http://localhost:8000"
echo -e "  • Telegram Bot:  Active"
echo -e ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  • API:  ${YELLOW}tail -f logs/api.log${NC}"
echo -e "  • Bot:  ${YELLOW}tail -f logs/bot.log${NC}"
echo -e "  • Full: ${YELLOW}tail -f logs/plexmem_*.log${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for both processes (wait for any to exit, then cleanup)
wait -n $API_PID $BOT_PID
cleanup

