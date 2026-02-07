# Oracle Cloud Deployment Guide for MVP Trading Bot

Complete guide for deploying the MVP Trading Bot on Oracle Cloud Free Tier.

## 🎯 Overview

Oracle Cloud Free Tier provides **forever-free** resources perfect for running trading bots 24/7:
- **2 AMD Compute VMs** (1 GB RAM each)
- **4 ARM-based Ampere A1 Compute instances** (up to 24 GB RAM total, 4 OCPUs)
- **200 GB Block Storage**
- **10 TB Outbound Data Transfer per month**

**Recommended:** Use ARM-based instances for better performance and more resources.

---

## 📋 Prerequisites

- Oracle Cloud account (free tier)
- SSH client (built into Windows 10/11, macOS, Linux)
- Basic knowledge of Linux command line
- Your Crypto.com API credentials

---

## 🚀 Step-by-Step Deployment

### Step 1: Create Oracle Cloud Instance

1. **Login to Oracle Cloud Console**
   - Go to https://cloud.oracle.com/
   - Sign in with your account

2. **Create Compute Instance**
   - Navigate to: **Compute** → **Instances** → **Create Instance**
   
3. **Configure Instance**
   - **Name:** `trading-bot-server`
   - **Image:** Ubuntu 22.04 (recommended)
   - **Shape:** 
     - Click "Change Shape"
     - Select **VM.Standard.A1.Flex** (ARM-based)
     - **OCPUs:** 2
     - **Memory:** 12 GB
     - This gives you room for multiple bots/strategies

4. **Networking**
   - Create new VCN (Virtual Cloud Network) or use existing
   - Assign a public IP address
   - Download the SSH private key (save as `trading-bot-key.pem`)

5. **Create the Instance**
   - Click "Create"
   - Wait 2-3 minutes for provisioning

### Step 2: Connect to Your Instance

**Windows (PowerShell):**
```powershell
# Set correct permissions on SSH key
icacls trading-bot-key.pem /inheritance:r
icacls trading-bot-key.pem /grant:r "%username%:R"

# Connect to instance (replace with your public IP)
ssh -i trading-bot-key.pem ubuntu@YOUR_PUBLIC_IP
```

**macOS/Linux:**
```bash
# Set correct permissions
chmod 600 trading-bot-key.pem

# Connect to instance
ssh -i trading-bot-key.pem ubuntu@YOUR_PUBLIC_IP
```

### Step 3: Configure Firewall Rules

**On Oracle Cloud Console:**
1. Go to **Networking** → **Virtual Cloud Networks**
2. Click your VCN → **Security Lists** → **Default Security List**
3. Click **Add Ingress Rules**
4. Add rules:
   - **Port 8000** (for API) - Source: 0.0.0.0/0
   - **Port 22** (SSH) - Already configured

**On Ubuntu Instance:**
```bash
# Update firewall
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo netfilter-persistent save
```

### Step 4: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip git build-essential

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

**Logout and login again for Docker permissions to take effect**

### Step 5: Clone and Setup the Bot

```bash
# Clone repository
cd ~
git clone https://github.com/mvpmedia00-commits/MVP-NEW-TRADING-BOT.git
cd MVP-NEW-TRADING-BOT

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Configure the Bot

```bash
# Create environment file
cp .env.example .env
nano .env
```

**Edit `.env` file:**
```bash
# Environment
ENVIRONMENT=production

# Broker
ACTIVE_BROKER=cryptocom

# Database (SQLite for simplicity on free tier)
DATABASE_URL=sqlite:///./data/trading_bot.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=YOUR_SECURE_RANDOM_KEY_HERE

# Logging
LOG_LEVEL=INFO
```

**Configure Crypto.com credentials:**
```bash
# Edit Crypto.com config
nano config/brokers/cryptocom.json
```

Update with your API credentials:
```json
{
  "name": "cryptocom",
  "type": "crypto",
  "enabled": true,
  "api_credentials": {
    "api_key": "YOUR_CRYPTOCOM_API_KEY",
    "api_secret": "YOUR_CRYPTOCOM_API_SECRET"
  },
  "settings": {
    "testnet": false,
    "enable_rate_limit": true
  }
}
```

### Step 7: Test the Bot

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Test bot connection
python -m bot.main --test-connection

# Run in paper trading mode first
python -m bot.main --paper-trading
```

### Step 8: Run as Background Service (systemd)

Create a systemd service for automatic startup and management:

```bash
# Create service file
sudo nano /etc/systemd/system/trading-bot.service
```

**Service configuration:**
```ini
[Unit]
Description=MVP Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MVP-NEW-TRADING-BOT
Environment="PATH=/home/ubuntu/MVP-NEW-TRADING-BOT/venv/bin"
ExecStart=/home/ubuntu/MVP-NEW-TRADING-BOT/venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start the service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable trading-bot

# Start the service
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot

# View logs
sudo journalctl -u trading-bot -f
```

### Step 9: Run API Server (Optional)

Create separate service for the API:

```bash
sudo nano /etc/systemd/system/trading-bot-api.service
```

```ini
[Unit]
Description=MVP Trading Bot API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MVP-NEW-TRADING-BOT
Environment="PATH=/home/ubuntu/MVP-NEW-TRADING-BOT/venv/bin"
ExecStart=/home/ubuntu/MVP-NEW-TRADING-BOT/venv/bin/gunicorn api.server:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Service]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot-api
sudo systemctl start trading-bot-api
sudo systemctl status trading-bot-api
```

---

## 🐳 Alternative: Docker Deployment

If you prefer Docker:

```bash
# Build and run with Docker Compose
cd ~/MVP-NEW-TRADING-BOT

# Build image
docker-compose build

# Run in detached mode
docker-compose up -d trading_bot

# View logs
docker-compose logs -f trading_bot

# Stop
docker-compose down
```

---

## 📊 Monitoring and Management

### Check Bot Status
```bash
# System service
sudo systemctl status trading-bot

# Docker
docker-compose ps
```

### View Logs
```bash
# System service
sudo journalctl -u trading-bot -f --lines=100

# Docker
docker-compose logs -f trading_bot

# Direct log files
tail -f data/logs/trading_bot.log
```

### Restart Bot
```bash
# System service
sudo systemctl restart trading-bot

# Docker
docker-compose restart trading_bot
```

### Update Bot
```bash
# Stop services
sudo systemctl stop trading-bot trading-bot-api

# Pull latest code
cd ~/MVP-NEW-TRADING-BOT
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart services
sudo systemctl start trading-bot trading-bot-api
```

---

## 🔒 Security Best Practices

1. **SSH Security**
   ```bash
   # Disable password authentication
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart sshd
   ```

2. **Firewall**
   ```bash
   # Only allow necessary ports
   sudo ufw allow 22/tcp
   sudo ufw allow 8000/tcp
   sudo ufw enable
   ```

3. **API Security**
   - Use strong API_SECRET_KEY
   - Enable HTTPS with Let's Encrypt (optional)
   - Restrict API access by IP if possible

4. **Backup Configuration**
   ```bash
   # Backup configs and database
   cd ~
   tar -czf trading-bot-backup-$(date +%Y%m%d).tar.gz \
     MVP-NEW-TRADING-BOT/.env \
     MVP-NEW-TRADING-BOT/config/ \
     MVP-NEW-TRADING-BOT/data/
   ```

---

## 🎯 Quick Command Reference

```bash
# Start bot
sudo systemctl start trading-bot

# Stop bot
sudo systemctl stop trading-bot

# Restart bot
sudo systemctl restart trading-bot

# View logs
sudo journalctl -u trading-bot -f

# Check status
sudo systemctl status trading-bot

# Update bot
cd ~/MVP-NEW-TRADING-BOT && git pull && \
  source venv/bin/activate && \
  pip install -r requirements.txt --upgrade && \
  sudo systemctl restart trading-bot
```

---

## 🆘 Troubleshooting

### Bot Won't Start
```bash
# Check logs
sudo journalctl -u trading-bot -xe

# Check permissions
ls -la /home/ubuntu/MVP-NEW-TRADING-BOT

# Verify Python environment
source venv/bin/activate
python --version
pip list | grep ccxt
```

### API Connection Issues
```bash
# Check if port is listening
sudo netstat -tlnp | grep 8000

# Test locally
curl http://localhost:8000/health

# Check firewall
sudo iptables -L -n
```

### Memory Issues
```bash
# Check memory usage
free -h

# Check process memory
top
# Press 'M' to sort by memory
```

### Crypto.com API Errors
```bash
# Verify credentials
cat config/brokers/cryptocom.json

# Test connection
python -c "import ccxt; exchange = ccxt.cryptocom(); print(exchange.fetch_markets())"
```

---

## 💰 Cost Optimization

**Oracle Free Tier is FREE forever**, but to maximize efficiency:

1. **Use ARM instances** - More resources, same cost ($0)
2. **Monitor usage** - Check Oracle Cloud dashboard
3. **Auto-shutdown during maintenance** - Save compute hours (though unlimited on free tier)
4. **Single instance for multiple strategies** - 12GB RAM can run several bots

---

## 📈 Next Steps

1. ✅ Deploy bot to Oracle Cloud
2. ✅ Configure Crypto.com credentials
3. ✅ Test in paper trading mode
4. ✅ Monitor for 24 hours
5. ✅ Enable live trading
6. ✅ Set up monitoring alerts
7. ✅ Configure automatic backups

---

## 📚 Additional Resources

- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
- [Crypto.com Exchange API Docs](https://exchange-docs.crypto.com/)
- [Bot Configuration Guide](CONFIGURATION.md)
- [Strategy Guide](STRATEGY_GUIDE.md)
- [API Documentation](API_REFERENCE.md)

---

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs: `sudo journalctl -u trading-bot -f`
3. Verify config files are correct
4. Ensure API credentials are valid

**Happy Trading! 🚀**
