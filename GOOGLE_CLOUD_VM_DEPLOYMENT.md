"""
GOOGLE CLOUD VM DEPLOYMENT GUIDE
=================================

Complete commands to deploy VG Crypto Trading Bot on Google Cloud VM


═════════════════════════════════════════════════════════════════════════════

SECTION 1: CREATE & CONNECT TO VM
==================================

1. Create VM Instance (via Google Cloud Console or gcloud CLI):

# Using gcloud CLI
gcloud compute instances create trading-bot-vm \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-standard \
    --tags=http-server,https-server


2. SSH into VM:

# From local machine
gcloud compute ssh trading-bot-vm --zone=us-central1-a

# Or use SSH key
ssh -i ~/.ssh/google_compute_engine username@EXTERNAL_IP


3. Update system:

sudo apt update && sudo apt upgrade -y


═════════════════════════════════════════════════════════════════════════════

SECTION 2: INSTALL DEPENDENCIES
================================

1. Install Python 3.11:

sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y


2. Install Git:

sudo apt install git -y


3. Install other dependencies:

sudo apt install build-essential libssl-dev libffi-dev -y


4. Verify installations:

python3.11 --version
git --version


═════════════════════════════════════════════════════════════════════════════

SECTION 3: CLONE & SETUP PROJECT
=================================

1. Clone repository:

cd ~
git clone https://github.com/mvpmedia00-commits/MVP-NEW-TRADING-BOT.git
cd MVP-NEW-TRADING-BOT


2. Create virtual environment:

python3.11 -m venv venv


3. Activate virtual environment:

source venv/bin/activate


4. Install requirements:

pip install --upgrade pip
pip install -r requirements.txt


5. Verify installation:

python -c "import pandas; import ccxt; print('Dependencies OK')"


═════════════════════════════════════════════════════════════════════════════

SECTION 4: CONFIGURE BOT
=========================

1. Update broker credentials (IMPORTANT - use secure method):

# Option A: Use environment variables (recommended)
export CRYPTOCOM_API_KEY="your_api_key_here"
export CRYPTOCOM_API_SECRET="your_api_secret_here"

# Option B: Edit config file directly (less secure)
nano config/brokers/cryptocom.json
# Update api_key and api_secret fields
# Save with Ctrl+O, Exit with Ctrl+X


2. Update global config for production:

nano config/global.json

# Change:
{
  "mode": "live",  # Change from "paper" to "live" when ready
  "logging": {
    "level": "INFO",  # Can use DEBUG for more detail
    "output": "file",  # Write to file instead of console
    "log_file": "logs/trading_bot.log"
  }
}


3. Create logs directory:

mkdir -p logs


═════════════════════════════════════════════════════════════════════════════

SECTION 5: RUN BOT (Manual Testing)
====================================

1. Test connection:

python -m bot.main --test-connection

# Expected output:
# ✅ Connection test successful!
# Connected brokers: ['cryptocom']


2. Run in paper trading mode (test first):

python -m bot.main --paper-trading

# Let it run for 1 hour, verify:
# - Logs show market data fetching
# - Range analysis working
# - Signals generating (if market conditions met)
# - No errors in logs


3. Monitor logs (in another terminal):

tail -f logs/trading_bot.log


4. Stop bot:

# Press Ctrl+C in the terminal running the bot


═════════════════════════════════════════════════════════════════════════════

SECTION 6: RUN BOT AS BACKGROUND SERVICE (24/7)
================================================

1. Create systemd service file:

sudo nano /etc/systemd/system/trading-bot.service

# Paste this content:

[Unit]
Description=VG Crypto Trading Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT
Environment="PATH=/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT/venv/bin"
Environment="CRYPTOCOM_API_KEY=your_api_key_here"
Environment="CRYPTOCOM_API_SECRET=your_api_secret_here"
ExecStart=/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT/venv/bin/python -m bot.main
Restart=always
RestartSec=10
StandardOutput=append:/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT/logs/trading_bot.log
StandardError=append:/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT/logs/trading_bot_error.log

[Install]
WantedBy=multi-user.target

# Save with Ctrl+O, Exit with Ctrl+X
# Replace YOUR_USERNAME with your actual username


2. Reload systemd:

sudo systemctl daemon-reload


3. Enable service to start on boot:

sudo systemctl enable trading-bot.service


4. Start the service:

sudo systemctl start trading-bot.service


5. Check service status:

sudo systemctl status trading-bot.service

# Should show: "Active: active (running)"


6. View logs in real-time:

sudo journalctl -u trading-bot.service -f

# Or:
tail -f logs/trading_bot.log


7. Stop the service:

sudo systemctl stop trading-bot.service


8. Restart the service:

sudo systemctl restart trading-bot.service


═════════════════════════════════════════════════════════════════════════════

SECTION 7: RUN API SERVER (Dashboard Access)
=============================================

1. Install uvicorn if not already installed:

pip install uvicorn[standard]


2. Create API server systemd service:

sudo nano /etc/systemd/system/trading-api.service

# Paste this content:

[Unit]
Description=VG Crypto Trading Bot API Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT
Environment="PATH=/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT/venv/bin"
ExecStart=/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT/venv/bin/uvicorn bot.api.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=append:/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT/logs/api_server.log
StandardError=append:/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT/logs/api_server_error.log

[Install]
WantedBy=multi-user.target


3. Enable and start API service:

sudo systemctl daemon-reload
sudo systemctl enable trading-api.service
sudo systemctl start trading-api.service
sudo systemctl status trading-api.service


4. Configure firewall to allow port 8000:

# Google Cloud: Add firewall rule via console
gcloud compute firewall-rules create allow-trading-api \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Trading Bot API access"

# Or on VM directly:
sudo ufw allow 8000/tcp
sudo ufw enable


5. Access dashboard from browser:

http://YOUR_VM_EXTERNAL_IP:8000/

# Get external IP:
gcloud compute instances describe trading-bot-vm \
    --zone=us-central1-a \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'


═════════════════════════════════════════════════════════════════════════════

SECTION 8: MONITORING & MAINTENANCE
====================================

1. Check both services are running:

sudo systemctl status trading-bot.service
sudo systemctl status trading-api.service


2. View real-time logs:

# Bot logs
tail -f logs/trading_bot.log

# API logs
tail -f logs/api_server.log

# System logs
sudo journalctl -u trading-bot.service -f
sudo journalctl -u trading-api.service -f


3. Check recent trades:

grep "TRADE OPENED" logs/trading_bot.log | tail -20
grep "TRADE CLOSED" logs/trading_bot.log | tail -20


4. Check for errors:

grep "ERROR" logs/trading_bot.log | tail -50


5. Monitor system resources:

# CPU and memory
top
htop  # (install with: sudo apt install htop)

# Disk space
df -h


6. Logrotate (prevent logs from filling disk):

sudo nano /etc/logrotate.d/trading-bot

# Paste:
/home/YOUR_USERNAME/MVP-NEW-TRADING-BOT/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 YOUR_USERNAME YOUR_USERNAME
}

# Test logrotate:
sudo logrotate -f /etc/logrotate.d/trading-bot


═════════════════════════════════════════════════════════════════════════════

SECTION 9: UPDATE BOT (Pull New Changes)
=========================================

1. Stop services:

sudo systemctl stop trading-bot.service
sudo systemctl stop trading-api.service


2. Pull latest code:

cd ~/MVP-NEW-TRADING-BOT
git pull origin main


3. Update dependencies:

source venv/bin/activate
pip install --upgrade -r requirements.txt


4. Restart services:

sudo systemctl start trading-bot.service
sudo systemctl start trading-api.service


5. Verify services restarted:

sudo systemctl status trading-bot.service
sudo systemctl status trading-api.service


═════════════════════════════════════════════════════════════════════════════

SECTION 10: BACKUP & DISASTER RECOVERY
=======================================

1. Backup configuration (run daily via cron):

# Create backup script
nano ~/backup_bot_config.sh

# Paste:
#!/bin/bash
BACKUP_DIR=~/trading_bot_backups
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    ~/MVP-NEW-TRADING-BOT/config/ \
    ~/MVP-NEW-TRADING-BOT/logs/

# Keep only last 7 days
find $BACKUP_DIR -name "config_*.tar.gz" -mtime +7 -delete

# Make executable:
chmod +x ~/backup_bot_config.sh


2. Schedule daily backups:

crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * /home/YOUR_USERNAME/backup_bot_config.sh


3. Download backups to local machine:

# From local machine
gcloud compute scp trading-bot-vm:~/trading_bot_backups/* ./local_backups/ \
    --zone=us-central1-a --recurse


═════════════════════════════════════════════════════════════════════════════

SECTION 11: SECURITY BEST PRACTICES
====================================

1. Never commit API keys to git:

# Make sure .gitignore includes:
config/brokers/*.json
*.env
.env


2. Use environment variables for secrets:

# Edit .bashrc or .profile
nano ~/.bashrc

# Add:
export CRYPTOCOM_API_KEY="your_key"
export CRYPTOCOM_API_SECRET="your_secret"

# Reload:
source ~/.bashrc


3. Restrict SSH access:

# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Set:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

# Restart SSH:
sudo systemctl restart sshd


4. Enable firewall:

sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8000/tcp
sudo ufw enable


5. Set up fail2ban (block brute force):

sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban


═════════════════════════════════════════════════════════════════════════════

SECTION 12: TROUBLESHOOTING
============================

Problem: Service won't start

Solution:
sudo systemctl status trading-bot.service
sudo journalctl -u trading-bot.service -n 100
# Check for dependency errors or permission issues


Problem: Can't access dashboard

Solution:
# Check API service is running:
sudo systemctl status trading-api.service

# Check firewall:
sudo ufw status
gcloud compute firewall-rules list

# Test locally on VM:
curl http://localhost:8000/api/health


Problem: Bot keeps restarting

Solution:
# Check logs for errors:
tail -100 logs/trading_bot_error.log
grep "ERROR" logs/trading_bot.log | tail -50


Problem: Out of memory

Solution:
# Check memory usage:
free -h

# Reduce update_interval in config:
nano config/global.json
# Set "update_interval": 120  (2 minutes instead of 60 seconds)


Problem: Disk full

Solution:
# Check disk usage:
df -h

# Clean old logs:
sudo journalctl --vacuum-time=7d
rm logs/*.log.gz

# Set up logrotate (see Section 8)


═════════════════════════════════════════════════════════════════════════════

SECTION 13: QUICK REFERENCE COMMANDS
=====================================

# SSH into VM
gcloud compute ssh trading-bot-vm --zone=us-central1-a

# Start/Stop/Restart bot
sudo systemctl start trading-bot.service
sudo systemctl stop trading-bot.service
sudo systemctl restart trading-bot.service

# View bot logs
tail -f logs/trading_bot.log
sudo journalctl -u trading-bot.service -f

# Check service status
sudo systemctl status trading-bot.service
sudo systemctl status trading-api.service

# Update bot code
cd ~/MVP-NEW-TRADING-BOT
git pull origin main
sudo systemctl restart trading-bot.service

# View recent trades
grep "TRADE OPENED" logs/trading_bot.log | tail -20
grep "TRADE CLOSED" logs/trading_bot.log | tail -20

# Check for errors
grep "ERROR" logs/trading_bot.log | tail -50

# Monitor system resources
htop

# Access dashboard
http://YOUR_VM_EXTERNAL_IP:8000/


═════════════════════════════════════════════════════════════════════════════

SECTION 14: RECOMMENDED VM SPECS
=================================

Minimum (Testing):
- Machine Type: e2-small (2 vCPU, 2GB RAM)
- Disk: 20GB
- Cost: ~$15/month

Recommended (Production):
- Machine Type: e2-medium (2 vCPU, 4GB RAM)
- Disk: 30GB SSD
- Cost: ~$30/month

High-Volume Trading:
- Machine Type: e2-standard-2 (2 vCPU, 8GB RAM)
- Disk: 50GB SSD
- Cost: ~$50/month


═════════════════════════════════════════════════════════════════════════════

DEPLOYMENT CHECKLIST:
=====================

Pre-Deployment:
□ Create Google Cloud VM
□ SSH into VM
□ Install Python 3.11, Git
□ Clone repository
□ Create virtual environment
□ Install dependencies
□ Configure broker credentials (use env vars)
□ Test connection: python -m bot.main --test-connection

Testing Phase:
□ Run in paper trading mode for 1 week
□ Monitor logs daily
□ Verify signals generating correctly
□ Check dashboard updates in real-time
□ Validate risk limits enforcing
□ No critical errors in logs

Production Deployment:
□ Create systemd service for bot
□ Create systemd service for API server
□ Enable services to start on boot
□ Configure firewall rules
□ Set up log rotation
□ Set up daily config backups
□ Test auto-restart after reboot
□ Change mode to "live" in config
□ Start services
□ Monitor for 24 hours

Post-Deployment:
□ Check logs daily for first week
□ Monitor dashboard regularly
□ Set up alerts for critical events
□ Review trades weekly
□ Backup configs regularly


═════════════════════════════════════════════════════════════════════════════

NOW YOU'RE READY TO DEPLOY!

1. Create VM
2. Run commands from Section 2-4
3. Test with --test-connection
4. Set up systemd services (Section 6-7)
5. Monitor via dashboard

Your bot will run 24/7 on Google Cloud.

═════════════════════════════════════════════════════════════════════════════
"""
