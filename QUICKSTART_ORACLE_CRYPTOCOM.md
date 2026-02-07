# Quick Start Guide - Crypto.com on Oracle Cloud

Get your trading bot running on Oracle Cloud Free Tier in under 30 minutes!

## 🎯 What You'll Get

- ✅ Trading bot running 24/7 on Oracle Cloud (FREE forever)
- ✅ Crypto.com exchange integration
- ✅ REST API for monitoring
- ✅ Automatic restarts and logging
- ✅ Paper trading mode for safe testing

---

## ⚡ Quick Setup (5 Steps)

### 1️⃣ Create Oracle Cloud Instance

1. Go to https://cloud.oracle.com/ and sign in
2. Navigate to: **Compute** → **Instances** → **Create Instance**
3. Configure:
   - **Name:** trading-bot
   - **Image:** Ubuntu 22.04
   - **Shape:** VM.Standard.A1.Flex (ARM) - 2 OCPU, 12 GB RAM
   - Download SSH key as `trading-bot-key.pem`
4. Click **Create**

### 2️⃣ Connect to Server

**Windows PowerShell:**
```powershell
ssh -i trading-bot-key.pem ubuntu@YOUR_PUBLIC_IP
```

**macOS/Linux:**
```bash
chmod 600 trading-bot-key.pem
ssh -i trading-bot-key.pem ubuntu@YOUR_PUBLIC_IP
```

### 3️⃣ Run Setup Script

```bash
# Clone repository
git clone https://github.com/mvpmedia00-commits/MVP-NEW-TRADING-BOT.git
cd MVP-NEW-TRADING-BOT

# Run automated setup
chmod +x scripts/oracle_setup.sh
./scripts/oracle_setup.sh
```

The script will:
- Install Python 3.11 and dependencies
- Set up virtual environment
- Install required packages
- Create configuration files

### 4️⃣ Configure Crypto.com

```bash
# Edit Crypto.com config
nano config/brokers/cryptocom.json
```

Update these fields:
```json
{
  "enabled": true,
  "api_credentials": {
    "api_key": "YOUR_API_KEY_HERE",
    "api_secret": "YOUR_API_SECRET_HERE"
  },
  "settings": {
    "testnet": false
  }
}
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### 5️⃣ Start Trading

**Paper Trading (Test Mode):**
```bash
source venv/bin/activate
python -m bot.main --paper-trading
```

**Live Trading:**
```bash
# Set up as background service
sudo cp deployment/trading-bot.service /etc/systemd/system/
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot
```

---

## 🔑 Get Crypto.com API Keys

1. Login to https://crypto.com/exchange/
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Enable permissions:
   - ✅ Read (required)
   - ✅ Trade (required)
   - ✅ Withdraw (optional - not recommended for bots)
5. Copy API Key and Secret
6. Add to `config/brokers/cryptocom.json`

---

## 📊 Monitor Your Bot

### View Logs
```bash
# Real-time logs
sudo journalctl -u trading-bot -f

# Last 100 lines
sudo journalctl -u trading-bot -n 100
```

### Check Status
```bash
sudo systemctl status trading-bot
```

### Restart Bot
```bash
sudo systemctl restart trading-bot
```

### Access API (if running)
```
http://YOUR_PUBLIC_IP:8000/docs
```

---

## 🎮 Basic Commands

```bash
# Activate Python environment
source venv/bin/activate

# Test connection
python -m bot.main --test-connection

# Paper trading (simulation)
python -m bot.main --paper-trading

# Start bot service
sudo systemctl start trading-bot

# Stop bot service
sudo systemctl stop trading-bot

# View logs
sudo journalctl -u trading-bot -f
```

---

## 🛡️ Safety Tips

1. **Always test with paper trading first**
   ```bash
   python -m bot.main --paper-trading
   ```

2. **Start with small amounts**
   - Set `max_position_size: 100` in config

3. **Enable risk management**
   - `stop_loss_percentage: 2.0`
   - `take_profit_percentage: 5.0`

4. **Monitor regularly**
   - Check logs daily
   - Review trades in Crypto.com app

5. **Use testnet first** (if available)
   - Set `testnet: true` in config

---

## 🎯 Choose a Strategy

Edit `config/strategies/default.json`:

**SMA Crossover (Simple, recommended for beginners):**
```json
{
  "name": "sma_crossover",
  "enabled": true,
  "params": {
    "fast_period": 10,
    "slow_period": 30
  }
}
```

**RSI + Bollinger Bands (Advanced):**
```json
{
  "name": "rsi_bollinger",
  "enabled": true,
  "params": {
    "rsi_period": 14,
    "bb_period": 20,
    "oversold": 30,
    "overbought": 70
  }
}
```

---

## 🆘 Troubleshooting

**Bot won't start:**
```bash
# Check logs for errors
sudo journalctl -u trading-bot -xe

# Verify config
cat config/brokers/cryptocom.json
```

**API connection failed:**
```bash
# Test Crypto.com connection
python -c "import ccxt; e = ccxt.cryptocom({'apiKey': 'YOUR_KEY', 'secret': 'YOUR_SECRET'}); print(e.fetch_balance())"
```

**Out of memory:**
```bash
# Check memory
free -h

# Reduce workers in config or upgrade Oracle instance
```

---

## 💰 Oracle Cloud Free Tier

**What's Free Forever:**
- 2 AMD VMs or 4 ARM VMs (24 GB RAM total)
- 200 GB storage
- 10 TB bandwidth/month
- **No credit card charges**

**Recommended Setup:**
- 1 ARM VM: 2 OCPU, 12 GB RAM
- Ubuntu 22.04
- Perfect for 1-3 trading strategies

---

## 📚 Full Documentation

For complete details, see:
- [ORACLE_CLOUD_DEPLOYMENT.md](ORACLE_CLOUD_DEPLOYMENT.md) - Complete deployment guide
- [CONFIGURATION.md](CONFIGURATION.md) - All configuration options
- [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md) - Create custom strategies
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation

---

## ✅ Checklist

- [ ] Oracle Cloud instance created
- [ ] Connected via SSH
- [ ] Setup script completed
- [ ] Crypto.com API keys configured
- [ ] Bot tested in paper trading mode
- [ ] Strategy configured
- [ ] Bot running as service
- [ ] Monitoring setup

---

**🎉 You're Ready to Trade!**

Start with paper trading, monitor for 24 hours, then switch to live trading with small amounts.

**Questions?** Check [ORACLE_CLOUD_DEPLOYMENT.md](ORACLE_CLOUD_DEPLOYMENT.md) for detailed troubleshooting.
