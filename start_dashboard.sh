#!/bin/bash

# Start Dashboard with Trading Bot
# This script starts both the trading bot and the API dashboard server

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== MVP Trading Bot Dashboard Startup ===${NC}"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo -e "${RED}Virtual environment not found. Please run setup first.${NC}"
    exit 1
fi

# Check if running on Oracle Cloud
if [ -f "/etc/oracle-cloud-agent/version" ]; then
    echo -e "${GREEN}Running on Oracle Cloud${NC}"
fi

echo -e "${YELLOW}Starting components...${NC}"

# Start the trading bot in background
echo "Starting trading bot..."
python -m bot.main --paper-trading &
BOT_PID=$!
echo -e "${GREEN}Bot started (PID: $BOT_PID)${NC}"

# Wait a moment for bot to initialize
sleep 2

# Start the API server
echo "Starting API dashboard server..."
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

# If we get here, user terminated the API server
echo -e "${YELLOW}Stopping bot...${NC}"
kill $BOT_PID 2>/dev/null || true
echo -e "${GREEN}Dashboard shutdown complete${NC}"
