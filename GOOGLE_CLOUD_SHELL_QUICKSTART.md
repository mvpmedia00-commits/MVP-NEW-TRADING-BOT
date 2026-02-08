"""
GOOGLE CLOUD SHELL - QUICK START COMMANDS
==========================================

Copy-paste these commands into your Cloud Shell terminal:


STEP 1: Clone Repository
=========================
cd ~
git clone https://github.com/mvpmedia00-commits/MVP-NEW-TRADING-BOT.git
cd MVP-NEW-TRADING-BOT


STEP 2: Setup Python Environment
=================================
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip


STEP 3: Install Dependencies
=============================
pip install -r requirements.txt

# If requirements.txt is missing, install manually:
pip install pandas numpy ccxt fastapi uvicorn python-dotenv pydantic


STEP 4: Configure Bot (IMPORTANT)
==================================
# Set your API credentials as environment variables
export CRYPTOCOM_API_KEY="your_api_key_here"
export CRYPTOCOM_API_SECRET="your_api_secret_here"

# OR edit the config file:
nano config/brokers/cryptocom.json
# Update api_key and api_secret, then save (Ctrl+O, Ctrl+X)


STEP 5: Test Connection
========================
python -m bot.main --test-connection

# Expected output:
# ✅ Connection test successful!
# Connected brokers: ['cryptocom']


STEP 6: Start Bot in Paper Trading Mode
========================================
# Option A: Run in foreground (you'll see logs live)
python -m bot.main --paper-trading

# Option B: Run in background
nohup python -m bot.main --paper-trading > bot.log 2>&1 &

# View logs in background mode:
tail -f bot.log


STEP 7: Start API Server (Separate Terminal)
==============================================
# Open new Cloud Shell tab (+ icon at top)
cd ~/MVP-NEW-TRADING-BOT
source venv/bin/activate
uvicorn bot.api.server:app --host 0.0.0.0 --port 8080

# Cloud Shell uses port 8080 (not 8000)


STEP 8: Access Dashboard
=========================
# Click "Web Preview" button in Cloud Shell
# Select "Preview on port 8080"
# Dashboard will open in new tab


TROUBLESHOOTING:
================

Problem: "No module named 'bot'"
Fix: Make sure you're in MVP-NEW-TRADING-BOT directory and venv is activated

Problem: "No module named uvicorn"  
Fix: pip install uvicorn[standard]

Problem: ModuleNotFoundError for pandas, ccxt, etc.
Fix: pip install -r requirements.txt

Problem: Can't access dashboard
Fix: Use Cloud Shell Web Preview on port 8080 (not external IP)


QUICK COMMANDS:
===============

# View bot logs
tail -f bot.log

# Stop background bot
pkill -f "bot.main"

# Check if bot is running
ps aux | grep "bot.main"

# Pull latest code
git pull origin main

# Restart everything
pkill -f "bot.main"
pkill -f "uvicorn"
source venv/bin/activate
nohup python -m bot.main --paper-trading > bot.log 2>&1 &
uvicorn bot.api.server:app --host 0.0.0.0 --port 8080
"""
