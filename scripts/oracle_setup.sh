#!/bin/bash
# Quick setup script for Oracle Cloud deployment

set -e

echo "🚀 MVP Trading Bot - Oracle Cloud Setup"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Ubuntu
if [ ! -f /etc/lsb-release ]; then
    echo "⚠️  This script is designed for Ubuntu. Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${YELLOW}Step 1: Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${YELLOW}Step 2: Installing Python 3.11 and dependencies...${NC}"
sudo apt install -y python3.11 python3.11-venv python3-pip git build-essential \
    wget curl software-properties-common

echo -e "${YELLOW}Step 3: Installing TA-Lib (required for technical analysis)...${NC}"
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
sudo ./configure --prefix=/usr
sudo make
sudo make install
cd ~

echo -e "${YELLOW}Step 4: Creating Python virtual environment...${NC}"
python3.11 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}Step 5: Installing Python packages...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo -e "${YELLOW}Step 6: Setting up configuration...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env with your settings${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create necessary directories
mkdir -p data/logs
mkdir -p data/backtest
mkdir -p user_strategies

echo -e "${YELLOW}Step 7: Testing installation...${NC}"
python -c "import ccxt; print('CCXT version:', ccxt.__version__)"
python -c "import pandas; print('Pandas version:', pandas.__version__)"

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your settings:"
echo "   nano .env"
echo ""
echo "2. Configure Crypto.com credentials:"
echo "   nano config/brokers/cryptocom.json"
echo ""
echo "3. Test the bot:"
echo "   source venv/bin/activate"
echo "   python -m bot.main --test-connection"
echo ""
echo "4. Run in paper trading mode:"
echo "   python -m bot.main --paper-trading"
echo ""
echo "5. Set up as service (see ORACLE_CLOUD_DEPLOYMENT.md)"
echo ""
echo "📚 Documentation:"
echo "   - ORACLE_CLOUD_DEPLOYMENT.md - Complete deployment guide"
echo "   - CONFIGURATION.md - Configuration options"
echo "   - STRATEGY_GUIDE.md - Strategy development"
echo ""
