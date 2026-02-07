# Quick Dashboard Start Guide

Get your MVP Trading Bot Dashboard running in 5 minutes!

## For Oracle Cloud Users

### Step 1: SSH into Your Instance

```bash
ssh -i your_key.key ubuntu@YOUR_INSTANCE_IP
```

### Step 2: Navigate to Project

```bash
cd ~/MVP-NEW-TRADING-BOT
source venv/bin/activate
```

### Step 3: Start the Dashboard

**Option A: Use the startup script (Recommended)**
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

The script will:
1. Activate virtual environment
2. Start the trading bot in background
3. Start the API server on port 8000

**Option B: Manual startup** (if script has issues)

Terminal 1:
```bash
python -m bot.main --paper-trading
```

Terminal 2:
```bash
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### Step 4: Open Dashboard

In your browser, go to:
```
http://YOUR_INSTANCE_IP:8000/dashboard
```

### Step 5: Verify Connection

You should see:
✅ Green "Connected" status in top-right  
✅ Bot trading in "paper-trading" mode  
✅ Portfolio value showing initial capital  
✅ Real-time market data updating  

## For Local Testing

### Prerequisites
- Python 3.8+
- FastAPI installed: `pip install fastapi uvicorn`

### Start

Terminal 1:
```bash
python -m bot.main --paper-trading
```

Terminal 2:
```bash
python -m uvicorn api.server:app --reload
```

Open browser:
```
http://localhost:8000/dashboard
```

## Dashboard Features

| Feature | What It Shows |
|---------|---------------|
| Bot Status | Running mode, connected brokers, active strategies |
| Portfolio | Total value, P&L, win rate, open positions |
| Market Data | Live prices for BTC/ETH and other symbols |
| Positions | All open trades with P&L and percentage |
| Brokers | Connected exchanges and current balances |
| Strategies | List of active trading strategies |

## Auto-Refresh

- **Enabled by default**: Refreshes every 5 seconds
- **Toggle**: Click "⏱️ Auto Refresh" button to turn on/off
- **Manual refresh**: Click "🔄 Refresh" button for immediate update

## Customize Dashboard

### Change Refresh Speed
Edit `api/static/index.html`, find:
```javascript
refreshInterval = setInterval(refreshData, 5000);
```

Change `5000` (milliseconds):
- `2000` = 2 seconds (faster)
- `10000` = 10 seconds (slower)

### Add More Symbols to Market Data
Edit the same file, find:
```javascript
fetch('/api/dashboard/market-data?symbols=BTC/USDT,ETH/USDT')
```

Change to:
```javascript
fetch('/api/dashboard/market-data?symbols=BTC/USDT,ETH/USDT,CRO/USDT')
```

## Troubleshooting

### Dashboard Page Doesn't Load

1. Check API server is running:
   ```bash
   curl http://localhost:8000/api/dashboard/health
   ```
   Should return: `{"status":"ok","timestamp":"..."}`

2. Check firewall (Oracle Cloud):
   ```bash
   sudo firewall-cmd --list-all | grep 8000
   ```
   Should show `8000/tcp`

### Bot Shows as Disconnected

1. Check bot is actually running:
   ```bash
   ps aux | grep bot.main
   ```

2. Check bot logs for errors:
   ```bash
   tail -f bot.log  # if logging to file
   ```

### Market Data Shows Errors

This usually means the broker connection is slow. The dashboard will retry automatically.

### Port 8000 Already in Use

Change API port:
```bash
python -m uvicorn api.server:app --host 0.0.0.0 --port 8001
```

Then access at: `http://localhost:8001/dashboard`

## Available API Endpoints

Test these with curl:

```bash
# Bot status
curl http://localhost:8000/api/dashboard/bot-status

# Portfolio details
curl http://localhost:8000/api/dashboard/portfolio

# Market data (default: BTC/USDT, ETH/USDT)
curl "http://localhost:8000/api/dashboard/market-data?symbols=BTC/USDT,ETH/USDT"

# Open positions
curl http://localhost:8000/api/dashboard/positions

# Connected brokers
curl http://localhost:8000/api/dashboard/brokers

# Active strategies
curl http://localhost:8000/api/dashboard/strategies

# Health check
curl http://localhost:8000/api/dashboard/health
```

All return JSON responses that the dashboard frontend displays.

## Set Up 24/7 Operation (Oracle Cloud)

To keep dashboard running after you disconnect:

```bash
# Create systemd service
sudo nano /etc/systemd/system/trading-dashboard.service
```

Paste this content:
```ini
[Unit]
Description=MVP Trading Bot Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MVP-NEW-TRADING-BOT
Environment="PATH=/home/ubuntu/MVP-NEW-TRADING-BOT/venv/bin"
ExecStart=/usr/bin/python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable:
```bash
sudo systemctl enable trading-dashboard.service
sudo systemctl start trading-dashboard.service

# Check status
sudo systemctl status trading-dashboard.service
```

## Performance Tips

1. **Disable auto-refresh when not watching** - Saves bandwidth and API calls
2. **Increase refresh interval to 10-15 seconds** if on slow connection
3. **Close dashboard tab** if not monitoring - API still runs fine

## What's Next?

1. ✅ Dashboard is running and monitoring the bot
2.📊 Watch portfolio growth in real-time
3. 🎯 Adjust trading strategies based on live performance
4. 💾 Monitor P&L and win rates
5. 🔧 Fine-tune strategy parameters for better results

## Need Help?

Detailed documentation: See [DASHBOARD.md](DASHBOARD.md)

For more info: See [README.md](README.md)

---

Happy trading! 🚀
