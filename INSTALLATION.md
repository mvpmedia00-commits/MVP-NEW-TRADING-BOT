# 📦 Installation Guide

Complete installation instructions for the MVP Trading Bot on all major platforms.

---

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Platform-Specific Instructions](#platform-specific-instructions)
  - [Ubuntu/Debian Linux](#ubuntudebian-linux)
  - [macOS](#macos)
  - [Windows](#windows)
  - [Docker (All Platforms)](#docker-all-platforms)
- [Post-Installation Setup](#post-installation-setup)
- [Verifying Installation](#verifying-installation)
- [Troubleshooting](#troubleshooting)
- [Upgrading](#upgrading)
- [Uninstallation](#uninstallation)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **CPU** | 2+ cores, 2.0 GHz |
| **RAM** | 4 GB (8 GB recommended) |
| **Storage** | 10 GB free space |
| **OS** | Ubuntu 20.04+, macOS 11+, Windows 10+ |
| **Python** | 3.11 or higher |
| **PostgreSQL** | 15.x |
| **Redis** | 7.x |
| **Internet** | Stable broadband connection |

### Recommended Requirements

| Component | Requirement |
|-----------|-------------|
| **CPU** | 4+ cores, 3.0 GHz |
| **RAM** | 16 GB |
| **Storage** | 50 GB SSD |
| **OS** | Ubuntu 22.04 LTS, macOS 13+, Windows 11 |

### Software Prerequisites

- **Git**: Version control
- **Python**: 3.11+ with pip
- **PostgreSQL**: 15.x database server
- **Redis**: 7.x cache server
- **TA-Lib**: Technical analysis library
- **Docker** (optional): For containerized deployment

---

## Installation Methods

Choose the method that best suits your needs:

| Method | Best For | Difficulty | Time |
|--------|----------|------------|------|
| **Docker** | Production, quick start | ⭐ Easy | 10 min |
| **Local** | Development, customization | ⭐⭐ Medium | 30 min |
| **Manual** | Advanced users, specific setups | ⭐⭐⭐ Advanced | 60 min |

---

## Platform-Specific Instructions

### Ubuntu/Debian Linux

#### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

#### Step 2: Install System Dependencies

```bash
# Install required packages
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    wget \
    build-essential \
    postgresql-15 \
    postgresql-contrib \
    redis-server \
    libpq-dev

# Verify versions
python3.11 --version  # Should be 3.11.x
psql --version        # Should be 15.x
redis-server --version # Should be 7.x
```

#### Step 3: Install TA-Lib

```bash
# Download and install TA-Lib
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/

# Configure and build
./configure --prefix=/usr
make
sudo make install

# Update library cache
sudo ldconfig

# Verify installation
ls -la /usr/lib/libta_lib.* 
```

#### Step 4: Setup PostgreSQL

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE USER trader WITH PASSWORD 'secure_password_change_this';
CREATE DATABASE trading_bot OWNER trader;
GRANT ALL PRIVILEGES ON DATABASE trading_bot TO trader;
\q
EOF

# Test connection
psql -h localhost -U trader -d trading_bot -c "SELECT version();"
```

#### Step 5: Setup Redis

```bash
# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping  # Should respond with "PONG"
```

#### Step 6: Clone Repository

```bash
# Clone the trading bot
cd ~
git clone https://github.com/yourusername/MVP-NEW-TRADING-BOT.git
cd MVP-NEW-TRADING-BOT
```

#### Step 7: Setup Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Verify TA-Lib Python wrapper
python -c "import talib; print(talib.__version__)"
```

#### Step 8: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env

# Set the following minimum values:
# BOT_MODE=paper
# DB_PASSWORD=secure_password_change_this
# API_KEY=your-secure-api-key-change-this
```

#### Step 9: Initialize Database

```bash
# Run database migrations (if available)
python scripts/init_db.py

# Or manually create tables using PostgreSQL
psql -h localhost -U trader -d trading_bot < scripts/schema.sql
```

#### Step 10: Test Installation

```bash
# Run in paper trading mode
./scripts/start_bot.sh

# In another terminal, test API
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

---

### macOS

#### Step 1: Install Homebrew

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Update Homebrew
brew update
```

#### Step 2: Install System Dependencies

```bash
# Install Python 3.11
brew install python@3.11

# Install PostgreSQL
brew install postgresql@15

# Install Redis
brew install redis

# Install TA-Lib
brew install ta-lib

# Install Git (if not already installed)
brew install git

# Verify installations
python3.11 --version
psql --version
redis-server --version
```

#### Step 3: Start Services

```bash
# Start PostgreSQL
brew services start postgresql@15

# Start Redis
brew services start redis

# Verify services are running
brew services list
```

#### Step 4: Setup PostgreSQL

```bash
# Create database and user
psql postgres <<EOF
CREATE USER trader WITH PASSWORD 'secure_password_change_this';
CREATE DATABASE trading_bot OWNER trader;
GRANT ALL PRIVILEGES ON DATABASE trading_bot TO trader;
\q
EOF

# Test connection
psql -h localhost -U trader -d trading_bot -c "SELECT version();"
```

#### Step 5: Clone Repository

```bash
# Clone repository
cd ~
git clone https://github.com/yourusername/MVP-NEW-TRADING-BOT.git
cd MVP-NEW-TRADING-BOT
```

#### Step 6: Setup Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Verify TA-Lib
python -c "import talib; print('TA-Lib installed successfully')"
```

#### Step 7: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your preferred editor
nano .env  # or: code .env, vim .env

# Set minimum required values:
# BOT_MODE=paper
# DB_PASSWORD=secure_password_change_this
# API_KEY=your-secure-api-key
```

#### Step 8: Initialize Database

```bash
# Initialize database schema
python scripts/init_db.py
```

#### Step 9: Test Installation

```bash
# Start the bot
./scripts/start_bot.sh

# In another terminal:
# Test API
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

---

### Windows

#### Step 1: Install Python

1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Run installer
3. **Important**: Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:

```powershell
python --version
pip --version
```

#### Step 2: Install Git

1. Download Git from [git-scm.com](https://git-scm.com/download/win)
2. Run installer with default settings
3. Verify:

```powershell
git --version
```

#### Step 3: Install PostgreSQL

1. Download PostgreSQL 15 from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run installer
3. Set password for `postgres` user (remember this!)
4. Accept default port 5432
5. Complete installation
6. Open pgAdmin 4
7. Create database:

```sql
CREATE USER trader WITH PASSWORD 'secure_password_change_this';
CREATE DATABASE trading_bot OWNER trader;
GRANT ALL PRIVILEGES ON DATABASE trading_bot TO trader;
```

#### Step 4: Install Redis

**Option A: Using WSL2 (Recommended)**

```powershell
# Install WSL2
wsl --install

# In WSL terminal:
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**Option B: Using Docker**

```powershell
# Install Docker Desktop for Windows
# Then run:
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

**Option C: Using Memurai (Redis alternative)**

1. Download Memurai from [memurai.com](https://www.memurai.com/get-memurai)
2. Install and start service

#### Step 5: Install TA-Lib

**Important**: TA-Lib on Windows requires pre-built wheels.

```powershell
# Download pre-built wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

# For Python 3.11 64-bit:
# TA_Lib‑0.4.28‑cp311‑cp311‑win_amd64.whl

# Install the wheel
pip install TA_Lib‑0.4.28‑cp311‑cp311‑win_amd64.whl

# Verify
python -c "import talib; print('TA-Lib installed')"
```

#### Step 6: Clone Repository

```powershell
# Open PowerShell
cd $HOME
git clone https://github.com/yourusername/MVP-NEW-TRADING-BOT.git
cd MVP-NEW-TRADING-BOT
```

#### Step 7: Setup Python Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

#### Step 8: Configure Environment

```powershell
# Copy environment template
copy .env.example .env

# Edit with Notepad
notepad .env

# Set:
# BOT_MODE=paper
# DB_HOST=localhost
# DB_PASSWORD=your_postgres_password
# REDIS_HOST=localhost  # or host.docker.internal if using Docker Redis
# API_KEY=your-secure-api-key
```

#### Step 9: Initialize Database

```powershell
# Run database initialization
python scripts/init_db.py
```

#### Step 10: Test Installation

```powershell
# Start the bot
python -m bot.main

# In another PowerShell terminal:
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

---

### Docker (All Platforms)

Docker provides the easiest cross-platform installation.

#### Step 1: Install Docker

**Ubuntu/Debian:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin
```

**macOS:**
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Install and start Docker Desktop

**Windows:**
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Install Docker Desktop
3. Enable WSL2 integration in settings

#### Step 2: Verify Docker

```bash
docker --version
docker-compose --version

# Test Docker
docker run hello-world
```

#### Step 3: Clone Repository

```bash
git clone https://github.com/yourusername/MVP-NEW-TRADING-BOT.git
cd MVP-NEW-TRADING-BOT
```

#### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or your preferred editor

# Minimum required settings:
# BOT_MODE=paper
# API_KEY=your-secure-api-key
# DB_PASSWORD=secure_password

# Docker-specific settings:
# DB_HOST=postgres  # Use service name from docker-compose.yml
# REDIS_HOST=redis  # Use service name from docker-compose.yml
```

#### Step 5: Build and Start Services

```bash
# Build images
docker-compose build

# Start all services in background
docker-compose up -d

# View logs
docker-compose logs -f trading_bot

# Check service status
docker-compose ps
```

#### Step 6: Verify Installation

```bash
# Check all services are running
docker-compose ps

# Should show:
# - postgres (healthy)
# - redis (running)
# - trading_bot (running)
# - trading_bot_api (running)

# Test API
curl -H "X-API-Key: your-api-key" http://localhost:8000/health

# View bot logs
docker-compose logs trading_bot

# Access PostgreSQL
docker-compose exec postgres psql -U trader -d trading_bot

# Access Redis
docker-compose exec redis redis-cli ping
```

#### Step 7: Managing Services

```bash
# Stop all services
docker-compose down

# Start services
docker-compose up -d

# Restart specific service
docker-compose restart trading_bot

# View logs
docker-compose logs -f trading_bot

# Execute command in container
docker-compose exec trading_bot python --version

# Rebuild after code changes
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Post-Installation Setup

### 1. Configure Broker API Keys

Edit `.env` with your broker credentials:

```bash
# Example for Binance testnet
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=true
```

See [BROKER_SETUP.md](BROKER_SETUP.md) for detailed broker configuration.

### 2. Configure Trading Strategy

Edit `config/strategies/strategies.json`:

```json
{
  "active_strategies": ["sma_crossover"],
  "strategies": {
    "sma_crossover": {
      "enabled": true,
      "parameters": {
        "symbol": "BTC/USDT",
        "fast_period": 10,
        "slow_period": 30,
        "position_size": 100
      },
      "risk_settings": {
        "stop_loss_pct": 2.0,
        "take_profit_pct": 5.0
      }
    }
  }
}
```

### 3. Set Up Logging

Configure logging in `config/global.json`:

```json
{
  "logging": {
    "level": "INFO",
    "format": "json",
    "log_file": "logs/trading_bot.log"
  }
}
```

### 4. Configure Risk Management

Edit risk settings in `config/global.json`:

```json
{
  "risk_management": {
    "max_position_size": 1000,
    "max_daily_loss": 500,
    "max_open_positions": 5,
    "emergency_stop_loss": 10.0
  }
}
```

---

## Verifying Installation

### Run System Check

```bash
# Activate virtual environment (if not using Docker)
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Run system check
python scripts/system_check.py
```

Expected output:
```
✓ Python version: 3.11.x
✓ PostgreSQL connection: OK
✓ Redis connection: OK
✓ TA-Lib installed: OK
✓ All dependencies installed: OK
✓ Configuration files: OK
✓ Broker configuration: OK
✓ Strategy configuration: OK

System check passed! Ready to run.
```

### Test Individual Components

```bash
# Test database connection
python -c "
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(f'postgresql://{os.getenv(\"DB_USER\")}:{os.getenv(\"DB_PASSWORD\")}@{os.getenv(\"DB_HOST\")}:{os.getenv(\"DB_PORT\")}/{os.getenv(\"DB_NAME\")}')
conn = engine.connect()
print('Database connection: OK')
conn.close()
"

# Test Redis connection
python -c "
import redis
import os
from dotenv import load_dotenv
load_dotenv()
r = redis.Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')))
r.ping()
print('Redis connection: OK')
"

# Test TA-Lib
python -c "import talib; print(f'TA-Lib version: {talib.__version__}')"

# Test broker connection (requires API keys)
python -c "
from bot.brokers import BinanceBroker
broker = BinanceBroker({'testnet': True})
if broker.connect():
    print('Broker connection: OK')
else:
    print('Broker connection: FAILED')
"
```

---

## Troubleshooting

### TA-Lib Installation Issues

**Problem**: `pip install TA-Lib` fails

**Solutions**:

**Linux**:
```bash
# Install from source
sudo apt install -y build-essential wget
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
sudo ldconfig
pip install TA-Lib
```

**macOS**:
```bash
brew install ta-lib
pip install TA-Lib
```

**Windows**:
Download pre-built wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

### PostgreSQL Connection Issues

**Problem**: Cannot connect to PostgreSQL

**Solutions**:

```bash
# Check PostgreSQL is running
# Linux:
sudo systemctl status postgresql

# macOS:
brew services list | grep postgresql

# Windows:
# Check Services app for PostgreSQL service

# Test connection
psql -h localhost -U trader -d trading_bot

# Check pg_hba.conf allows local connections
# Linux: /etc/postgresql/15/main/pg_hba.conf
# macOS: /usr/local/var/postgres/pg_hba.conf
# Should have line: local all all md5
```

### Redis Connection Issues

**Problem**: Cannot connect to Redis

**Solutions**:

```bash
# Check Redis is running
# Linux:
sudo systemctl status redis-server

# macOS:
brew services list | grep redis

# Test connection
redis-cli ping  # Should return PONG

# Check Redis configuration
# Linux: /etc/redis/redis.conf
# macOS: /usr/local/etc/redis.conf
# Ensure: bind 127.0.0.1 ::1
```

### Docker Issues

**Problem**: Docker containers won't start

**Solutions**:

```bash
# Check Docker is running
docker info

# Check docker-compose.yml syntax
docker-compose config

# View container logs
docker-compose logs

# Rebuild containers
docker-compose down -v  # Warning: removes volumes
docker-compose build --no-cache
docker-compose up -d

# Check resource usage
docker stats
```

### Permission Issues (Linux)

**Problem**: Permission denied errors

**Solutions**:

```bash
# Fix ownership of project directory
sudo chown -R $USER:$USER ~/MVP-NEW-TRADING-BOT

# Fix log directory permissions
chmod 755 logs/
chmod 644 logs/*.log

# Fix script permissions
chmod +x scripts/*.sh
```

### Import Errors

**Problem**: `ModuleNotFoundError` when running bot

**Solutions**:

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify package installation
pip list | grep -E "(ccxt|fastapi|pandas)"
```

---

## Upgrading

### Upgrading from Previous Version

```bash
# Backup current installation
cp -r ~/MVP-NEW-TRADING-BOT ~/MVP-NEW-TRADING-BOT.backup

# Pull latest changes
cd ~/MVP-NEW-TRADING-BOT
git pull origin main

# Backup .env file
cp .env .env.backup

# Update dependencies
pip install -r requirements.txt --upgrade

# Run database migrations (if any)
python scripts/migrate_db.py

# Restart services
# Local:
./scripts/start_bot.sh

# Docker:
docker-compose down
docker-compose build
docker-compose up -d
```

### Upgrading Python Version

```bash
# Install new Python version
# Ubuntu:
sudo apt install python3.12

# macOS:
brew install python@3.12

# Create new virtual environment
python3.12 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements.txt

# Test with new version
python --version
./scripts/start_bot.sh

# If successful, replace old venv
rm -rf venv
mv venv_new venv
```

---

## Uninstallation

### Local Installation

```bash
# Stop the bot
pkill -f "python.*bot.main"

# Deactivate virtual environment
deactivate

# Remove project directory
rm -rf ~/MVP-NEW-TRADING-BOT

# Remove database (optional)
sudo -u postgres psql -c "DROP DATABASE trading_bot;"
sudo -u postgres psql -c "DROP USER trader;"

# Stop and remove services (optional)
# Ubuntu:
sudo systemctl stop postgresql redis-server
sudo apt remove postgresql redis-server

# macOS:
brew services stop postgresql@15 redis
brew uninstall postgresql@15 redis ta-lib
```

### Docker Installation

```bash
# Stop and remove containers
cd ~/MVP-NEW-TRADING-BOT
docker-compose down -v  # -v removes volumes (database data)

# Remove images
docker-compose down --rmi all

# Remove project directory
cd ~
rm -rf MVP-NEW-TRADING-BOT

# Remove unused Docker resources (optional)
docker system prune -a
```

---

## Next Steps

After successful installation:

1. **Configure Brokers**: See [BROKER_SETUP.md](BROKER_SETUP.md)
2. **Create Strategies**: See [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md)
3. **Test in Paper Mode**: Run bot with `BOT_MODE=paper`
4. **Backtest Strategies**: Use `scripts/backtest.py`
5. **Monitor via API**: See [API_REFERENCE.md](API_REFERENCE.md)
6. **Go Live**: Switch to `BOT_MODE=live` when ready

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs in `logs/trading_bot.log`
3. Search existing GitHub issues
4. Create a new issue with:
   - Operating system and version
   - Python version
   - Full error message
   - Steps to reproduce

---

**[⬆ Back to Top](#-installation-guide)**
