# Broker Setup Guide

Complete guide to configuring and connecting supported brokers with the MVP Trading Bot.

## Table of Contents

1. [Overview](#overview)
2. [Supported Brokers](#supported-brokers)
3. [General Setup Steps](#general-setup-steps)
4. [Binance Setup](#binance-setup)
5. [Binance US Setup](#binance-us-setup)
6. [Coinbase Pro Setup](#coinbase-pro-setup)
7. [Gemini Setup](#gemini-setup)
8. [MetaTrader 4 Setup](#metatrader-4-setup)
9. [API Key Security](#api-key-security)
10. [Testing Connections](#testing-connections)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The MVP Trading Bot supports multiple cryptocurrency exchanges and traditional brokers through a unified interface. This guide walks you through configuring each supported broker.

### Prerequisites

- Trading bot installed and configured
- Account with your chosen broker/exchange
- API access enabled on your account
- Basic understanding of API keys and secrets

---

## Supported Brokers

| Broker | Type | Testnet | Paper Trading | Live Trading |
|--------|------|---------|---------------|--------------|
| Binance | Crypto | ✅ | ✅ | ✅ |
| Binance US | Crypto | ✅ | ✅ | ✅ |
| Coinbase Pro | Crypto | ✅ (Sandbox) | ✅ | ✅ |
| Gemini | Crypto | ✅ (Sandbox) | ✅ | ✅ |
| MetaTrader 4 | Forex/CFD | ❌ | ✅ | ✅ |

**Legend:**
- ✅ = Supported
- ❌ = Not available

---

## General Setup Steps

All brokers follow a similar setup process:

### 1. Create API Keys

Log into your broker account and create API keys with appropriate permissions.

### 2. Configure Environment Variables

Add credentials to `.env` file:

```bash
# Broker API Credentials
BROKER_NAME_API_KEY=your_api_key_here
BROKER_NAME_API_SECRET=your_api_secret_here
```

### 3. Configure Broker Settings

Edit `config/brokers/broker_name.json`:

```json
{
  "name": "broker_name",
  "type": "crypto",
  "enabled": true,
  "api_credentials": {
    "api_key": "${BROKER_NAME_API_KEY}",
    "api_secret": "${BROKER_NAME_API_SECRET}"
  }
}
```

### 4. Test Connection

```bash
python scripts/test_broker_connection.py --broker broker_name
```

---

## Binance Setup

Binance is the world's largest cryptocurrency exchange with high liquidity and low fees.

### Step 1: Create Binance Account

1. Go to [binance.com](https://www.binance.com)
2. Sign up for an account
3. Complete identity verification (KYC)
4. Enable 2FA security

### Step 2: Create API Keys

1. Log into your Binance account
2. Go to **Account** → **API Management**
3. Click **Create API**
4. Enter label (e.g., "Trading Bot")
5. Complete 2FA verification
6. **Save your API Key and Secret Key** (Secret shown only once!)

**Recommended API Restrictions:**
- ✅ Enable Reading
- ✅ Enable Spot & Margin Trading
- ❌ Disable Withdrawals (for security)
- Optional: Restrict to specific IP addresses

### Step 3: Enable Testnet (Recommended)

For testing without real money:

1. Go to [testnet.binance.vision](https://testnet.binance.vision)
2. Log in with GitHub account
3. Generate testnet API keys
4. Use testnet keys in configuration

### Step 4: Configure Environment Variables

Add to `.env`:

```bash
# Binance API Configuration
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
BINANCE_TESTNET=true  # Set to false for live trading
```

### Step 5: Create Broker Configuration

Create `config/brokers/binance.json`:

```json
{
  "name": "binance",
  "type": "crypto",
  "enabled": true,
  "description": "Binance cryptocurrency exchange",
  "api_credentials": {
    "api_key": "${BINANCE_API_KEY}",
    "api_secret": "${BINANCE_API_SECRET}"
  },
  "settings": {
    "testnet": true,
    "rate_limit": true,
    "timeout": 30000,
    "enable_rate_limit": true,
    "recv_window": 5000
  },
  "supported_pairs": [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "ADA/USDT",
    "DOT/USDT",
    "MATIC/USDT",
    "LINK/USDT",
    "UNI/USDT",
    "AVAX/USDT"
  ],
  "trading_settings": {
    "default_order_type": "limit",
    "default_time_in_force": "GTC",
    "enable_margin": false,
    "enable_futures": false
  },
  "risk_management": {
    "max_position_size": 10000,
    "max_leverage": 1,
    "stop_loss_percentage": 2.0,
    "take_profit_percentage": 5.0
  }
}
```

### Step 6: Test Connection

```bash
# Test testnet connection
python scripts/test_broker_connection.py --broker binance

# Or use Python
python -c "
from bot.brokers.binance_broker import BinanceBroker
import json

with open('config/brokers/binance.json') as f:
    config = json.load(f)

broker = BinanceBroker(config)
if broker.connect():
    print('✅ Connected to Binance!')
    balance = broker.get_balance()
    print(f'Balance: {balance}')
    broker.disconnect()
else:
    print('❌ Connection failed')
"
```

### Binance-Specific Features

**Supported Order Types:**
- Market orders
- Limit orders
- Stop-loss orders
- Stop-limit orders
- OCO (One-Cancels-Other) orders

**Fee Structure:**
- Standard: 0.1% maker/taker
- With BNB discount: 0.075%
- VIP levels: Lower fees based on volume

**Rate Limits:**
- 1200 requests per minute
- Weight-based limit system
- Automatic rate limiting enabled in config

### Going Live

When ready for live trading:

1. Update `.env`:
```bash
BINANCE_TESTNET=false
BINANCE_API_KEY=your_live_api_key
BINANCE_API_SECRET=your_live_api_secret
```

2. Update `config/brokers/binance.json`:
```json
{
  "settings": {
    "testnet": false
  }
}
```

3. Update `config/global.json`:
```json
{
  "mode": "live"
}
```

---

## Binance US Setup

Binance US is the US-specific version of Binance with different trading pairs and regulations.

### Key Differences from Binance

- Separate platform for US users
- Different trading pairs
- US regulatory compliance
- Different fee structure

### Setup Steps

Almost identical to Binance setup, with these differences:

### Step 1: Create Account

Go to [binance.us](https://www.binance.us)

### Step 2: Configure Environment

Add to `.env`:

```bash
# Binance US API Configuration
BINANCE_US_API_KEY=your_binance_us_api_key
BINANCE_US_API_SECRET=your_binance_us_api_secret
BINANCE_US_TESTNET=true
```

### Step 3: Create Configuration

Create `config/brokers/binance_us.json`:

```json
{
  "name": "binance_us",
  "type": "crypto",
  "enabled": true,
  "description": "Binance US cryptocurrency exchange",
  "api_credentials": {
    "api_key": "${BINANCE_US_API_KEY}",
    "api_secret": "${BINANCE_US_API_SECRET}"
  },
  "settings": {
    "testnet": true,
    "rate_limit": true,
    "timeout": 30000,
    "enable_rate_limit": true
  },
  "supported_pairs": [
    "BTC/USD",
    "ETH/USD",
    "BTC/USDT",
    "ETH/USDT",
    "ADA/USD",
    "DOT/USD",
    "LINK/USD"
  ],
  "trading_settings": {
    "default_order_type": "limit",
    "default_time_in_force": "GTC",
    "enable_margin": false
  }
}
```

---

## Coinbase Pro Setup

Coinbase Pro (now Advanced Trade) is a US-based cryptocurrency exchange with strong security and regulatory compliance.

### Step 1: Create Coinbase Pro Account

1. Go to [pro.coinbase.com](https://pro.coinbase.com) or [coinbase.com/advanced](https://www.coinbase.com/advanced)
2. Sign up or log in with existing Coinbase account
3. Complete identity verification
4. Enable 2FA

### Step 2: Create API Keys

1. Go to **Settings** → **API**
2. Click **New API Key**
3. Select permissions:
   - ✅ View
   - ✅ Trade
   - ❌ Transfer (for security)
4. **Save API Key, Secret, and Passphrase** (shown only once!)

**Important:** Coinbase requires all three credentials:
- API Key
- API Secret
- Passphrase

### Step 3: Use Sandbox for Testing

Coinbase provides a sandbox environment:

1. Go to [public.sandbox.pro.coinbase.com](https://public.sandbox.pro.coinbase.com)
2. Create sandbox API keys
3. Use for testing before live trading

### Step 4: Configure Environment

Add to `.env`:

```bash
# Coinbase Pro API Configuration
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_API_SECRET=your_coinbase_api_secret
COINBASE_PASSPHRASE=your_coinbase_passphrase
COINBASE_SANDBOX=true  # Set to false for live trading
```

### Step 5: Create Configuration

Create `config/brokers/coinbase.json`:

```json
{
  "name": "coinbase_pro",
  "type": "crypto",
  "enabled": true,
  "description": "Coinbase Pro cryptocurrency exchange",
  "api_credentials": {
    "api_key": "${COINBASE_API_KEY}",
    "api_secret": "${COINBASE_API_SECRET}",
    "passphrase": "${COINBASE_PASSPHRASE}"
  },
  "settings": {
    "sandbox": true,
    "rate_limit": true,
    "timeout": 30000,
    "enable_rate_limit": true
  },
  "supported_pairs": [
    "BTC/USD",
    "ETH/USD",
    "BTC/USDT",
    "ETH/USDT",
    "LINK/USD",
    "UNI/USD",
    "AAVE/USD",
    "COMP/USD"
  ],
  "trading_settings": {
    "default_order_type": "limit",
    "default_time_in_force": "GTC",
    "post_only": false
  },
  "risk_management": {
    "max_position_size": 10000,
    "stop_loss_percentage": 2.0,
    "take_profit_percentage": 5.0
  }
}
```

### Coinbase Pro Features

**Fee Structure:**
- Taker: 0.05% - 0.50% (volume-based)
- Maker: 0.00% - 0.50% (volume-based)
- Lower fees for higher volume

**Rate Limits:**
- Public endpoints: 3 requests/second
- Private endpoints: 5 requests/second

**Sandbox Environment:**
- Full API functionality
- Test data and fake funds
- Perfect for development

### Going Live

Update configuration:

```bash
# .env
COINBASE_SANDBOX=false
COINBASE_API_KEY=your_live_api_key
COINBASE_API_SECRET=your_live_api_secret
COINBASE_PASSPHRASE=your_live_passphrase
```

```json
// config/brokers/coinbase.json
{
  "settings": {
    "sandbox": false
  }
}
```

---

## Gemini Setup

Gemini is a regulated US cryptocurrency exchange known for security and compliance.

### Step 1: Create Gemini Account

1. Go to [gemini.com](https://www.gemini.com)
2. Sign up for account
3. Complete identity verification
4. Enable 2FA and other security features

### Step 2: Create API Keys

1. Go to **Account Settings** → **API**
2. Click **Create a New API Key**
3. Select API settings:
   - **Primary:** Trading
   - **Require 2FA:** Recommended
   - **IP Whitelist:** Optional but recommended
4. Select scopes:
   - ✅ Fund Manager
   - ✅ Trading
   - ✅ Auditor
5. **Save API Key and Secret**

### Step 3: Use Sandbox

Gemini provides a sandbox at [exchange.sandbox.gemini.com](https://exchange.sandbox.gemini.com)

### Step 4: Configure Environment

Add to `.env`:

```bash
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_SECRET=your_gemini_api_secret
GEMINI_SANDBOX=true  # Set to false for live trading
```

### Step 5: Create Configuration

Create `config/brokers/gemini.json`:

```json
{
  "name": "gemini",
  "type": "crypto",
  "enabled": true,
  "description": "Gemini cryptocurrency exchange",
  "api_credentials": {
    "api_key": "${GEMINI_API_KEY}",
    "api_secret": "${GEMINI_API_SECRET}"
  },
  "settings": {
    "sandbox": true,
    "rate_limit": true,
    "timeout": 30000,
    "enable_rate_limit": true
  },
  "supported_pairs": [
    "BTC/USD",
    "ETH/USD",
    "BTC/USDT",
    "ETH/USDT",
    "LINK/USD",
    "UNI/USD",
    "AAVE/USD"
  ],
  "trading_settings": {
    "default_order_type": "limit",
    "enable_auction": false
  },
  "risk_management": {
    "max_position_size": 10000,
    "stop_loss_percentage": 2.0,
    "take_profit_percentage": 5.0
  }
}
```

### Gemini Features

**Fee Structure:**
- API trading: 0.20% - 0.35% (volume-based)
- Lower fees for maker orders
- ActiveTrader™ interface: Lower fees

**Rate Limits:**
- Public API: 120 requests/minute
- Private API: 600 requests/minute

**Security Features:**
- SOC 2 Type 2 certified
- Cold storage for majority of funds
- Insurance coverage

---

## MetaTrader 4 Setup

MetaTrader 4 (MT4) is a popular platform for forex and CFD trading.

**Note:** MT4 integration requires Windows OS.

### Step 1: Install MetaTrader 4

1. Download MT4 from your broker
2. Install and launch MT4
3. Log in with your broker account

### Step 2: Install Python MT4 Package

```bash
pip install MetaTrader5
```

**Note:** This package only works on Windows.

### Step 3: Enable Algo Trading in MT4

1. Open MT4
2. Go to **Tools** → **Options**
3. Go to **Expert Advisors** tab
4. Enable:
   - ✅ Allow automated trading
   - ✅ Allow DLL imports
   - ✅ Allow imports of external experts

### Step 4: Configure Environment

Add to `.env`:

```bash
# MetaTrader 4 Configuration
MT4_LOGIN=your_mt4_account_number
MT4_PASSWORD=your_mt4_password
MT4_SERVER=your_broker_server
MT4_PATH=C:\Program Files\MetaTrader 4\terminal64.exe
```

### Step 5: Create Configuration

Create `config/brokers/mt4.json`:

```json
{
  "name": "metatrader4",
  "type": "forex",
  "enabled": true,
  "description": "MetaTrader 4 forex trading platform",
  "api_credentials": {
    "login": "${MT4_LOGIN}",
    "password": "${MT4_PASSWORD}",
    "server": "${MT4_SERVER}"
  },
  "settings": {
    "path": "${MT4_PATH}",
    "timeout": 60000,
    "magic_number": 123456
  },
  "supported_pairs": [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "NZDUSD",
    "EURGBP",
    "EURJPY"
  ],
  "trading_settings": {
    "default_order_type": "market",
    "slippage": 3,
    "deviation": 10
  },
  "risk_management": {
    "max_position_size": 1.0,
    "max_leverage": 100,
    "stop_loss_pips": 50,
    "take_profit_pips": 100
  }
}
```

### MT4-Specific Considerations

**Important Notes:**
- Must run on Windows
- MT4 must be running while bot operates
- Test on demo account first
- Verify broker allows automated trading

**Connection Test:**

```python
import MetaTrader5 as mt5

# Initialize MT5
if mt5.initialize():
    print("✅ MT5 initialized")
    
    # Connect to account
    authorized = mt5.login(
        login=your_account,
        password="your_password",
        server="your_server"
    )
    
    if authorized:
        print("✅ Connected to MT4 account")
        account_info = mt5.account_info()
        print(f"Balance: {account_info.balance}")
    else:
        print("❌ Failed to connect")
    
    mt5.shutdown()
else:
    print("❌ MT5 initialization failed")
```

---

## API Key Security

### Best Practices

#### 1. Never Commit API Keys

**Always** use environment variables:

```bash
# ✅ Good: .env file (gitignored)
BINANCE_API_KEY=your_key_here

# ❌ Bad: Hardcoded in config
{
  "api_key": "abc123xyz789"
}
```

#### 2. Use Restricted API Keys

Only enable necessary permissions:

- ✅ Enable: View, Trade
- ❌ Disable: Withdraw, Transfer

#### 3. IP Whitelist

Restrict API keys to specific IP addresses:

```
Your Trading Server IP: 123.456.789.012
```

#### 4. Separate Keys for Testing

Use different API keys for:
- Testing/development (testnet/sandbox)
- Paper trading
- Live trading

#### 5. Rotate Keys Regularly

Change API keys periodically:
- Every 90 days minimum
- Immediately if compromised
- After team member changes

#### 6. Store Secrets Securely

```bash
# Set restrictive permissions
chmod 600 .env

# Or use secret management
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
```

#### 7. Monitor API Activity

- Regularly review API usage
- Set up alerts for unusual activity
- Monitor from exchange dashboard

### Environment Variables Template

Create `.env` from `.env.example`:

```bash
cp .env.example .env
chmod 600 .env
```

Edit `.env`:

```bash
# =================================
# TRADING BOT CONFIGURATION
# =================================

# Bot Mode
BOT_MODE=paper  # paper or live

# API Configuration
API_KEY=your-secure-api-key-change-this

# =================================
# BROKER API KEYS
# =================================

# Binance
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_TESTNET=true

# Binance US
BINANCE_US_API_KEY=
BINANCE_US_API_SECRET=
BINANCE_US_TESTNET=true

# Coinbase Pro
COINBASE_API_KEY=
COINBASE_API_SECRET=
COINBASE_PASSPHRASE=
COINBASE_SANDBOX=true

# Gemini
GEMINI_API_KEY=
GEMINI_API_SECRET=
GEMINI_SANDBOX=true

# MetaTrader 4 (Windows only)
MT4_LOGIN=
MT4_PASSWORD=
MT4_SERVER=
MT4_PATH=

# =================================
# DO NOT COMMIT THIS FILE!
# =================================
```

---

## Testing Connections

### Test Script

Create `scripts/test_broker_connection.py`:

```python
#!/usr/bin/env python3
"""
Test broker connection
Usage: python scripts/test_broker_connection.py --broker binance
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.brokers.binance_broker import BinanceBroker
from bot.brokers.coinbase_broker import CoinbaseBroker
from bot.brokers.gemini_broker import GeminiBroker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BROKERS = {
    'binance': BinanceBroker,
    'binance_us': BinanceBroker,
    'coinbase': CoinbaseBroker,
    'gemini': GeminiBroker
}


def test_broker(broker_name: str):
    """Test broker connection and basic functionality"""
    
    print(f"\n{'='*60}")
    print(f"Testing {broker_name.upper()} Connection")
    print(f"{'='*60}\n")
    
    # Load config
    config_path = f"config/brokers/{broker_name}.json"
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return False
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Get broker class
    broker_class = BROKERS.get(broker_name)
    if not broker_class:
        print(f"❌ Broker {broker_name} not supported")
        return False
    
    try:
        # Initialize broker
        print("1. Initializing broker...")
        broker = broker_class(config)
        print("   ✅ Broker initialized\n")
        
        # Connect
        print("2. Connecting to exchange...")
        if not broker.connect():
            print("   ❌ Connection failed")
            return False
        print("   ✅ Connected successfully\n")
        
        # Get balance
        print("3. Fetching account balance...")
        balance = broker.get_balance()
        print("   ✅ Balance retrieved:")
        for currency, amounts in balance.items():
            if amounts['total'] > 0:
                print(f"      {currency}: {amounts['total']}")
        print()
        
        # Get ticker
        print("4. Fetching ticker data...")
        symbol = config.get('supported_pairs', ['BTC/USDT'])[0]
        ticker = broker.get_ticker(symbol)
        print(f"   ✅ Ticker for {symbol}:")
        print(f"      Last: {ticker.get('last', 'N/A')}")
        print(f"      Bid: {ticker.get('bid', 'N/A')}")
        print(f"      Ask: {ticker.get('ask', 'N/A')}")
        print()
        
        # Get OHLCV
        print("5. Fetching OHLCV data...")
        ohlcv = broker.get_ohlcv(symbol, '1h', 5)
        print(f"   ✅ Retrieved {len(ohlcv)} candles")
        print(f"      Latest close: {ohlcv[-1][4]}")
        print()
        
        # Disconnect
        print("6. Disconnecting...")
        broker.disconnect()
        print("   ✅ Disconnected\n")
        
        print(f"{'='*60}")
        print(f"✅ All tests passed for {broker_name.upper()}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing {broker_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Test broker connection')
    parser.add_argument('--broker', required=True, 
                       choices=list(BROKERS.keys()),
                       help='Broker to test')
    
    args = parser.parse_args()
    
    success = test_broker(args.broker)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

### Run Tests

```bash
# Test Binance
python scripts/test_broker_connection.py --broker binance

# Test Coinbase
python scripts/test_broker_connection.py --broker coinbase

# Test all brokers
for broker in binance coinbase gemini; do
    python scripts/test_broker_connection.py --broker $broker
done
```

### Quick Connection Test

```python
# Quick Python test
from bot.brokers.binance_broker import BinanceBroker
import json

with open('config/brokers/binance.json') as f:
    config = json.load(f)

broker = BinanceBroker(config)
print("Connected:", broker.connect())
print("Balance:", broker.get_balance())
broker.disconnect()
```

---

## Troubleshooting

### Common Issues

#### 1. "Invalid API Key" Error

**Causes:**
- Incorrect API key or secret
- Wrong environment (testnet vs mainnet)
- API key disabled or deleted

**Solutions:**
```bash
# Verify credentials in .env
cat .env | grep BINANCE_API_KEY

# Check if using testnet
cat .env | grep TESTNET

# Regenerate API keys if needed
```

#### 2. "IP Not Whitelisted" Error

**Solution:**
- Add your server IP to allowed list in exchange settings
- Or remove IP whitelist restriction (less secure)

#### 3. "Insufficient Permissions" Error

**Solution:**
Check API key permissions:
- ✅ Reading enabled
- ✅ Trading enabled
- Regenerate key with correct permissions

#### 4. "Rate Limit Exceeded" Error

**Solution:**
```json
{
  "settings": {
    "enable_rate_limit": true,
    "rate_limit": true
  }
}
```

#### 5. Connection Timeout

**Causes:**
- Network issues
- Firewall blocking
- Exchange downtime

**Solutions:**
```json
{
  "settings": {
    "timeout": 60000  // Increase timeout
  }
}
```

#### 6. SSL Certificate Errors

**Solution:**
```bash
# Update certificates
pip install --upgrade certifi

# Or disable SSL verification (not recommended for production)
# Only for testing
```

#### 7. "Signature Invalid" Error

**Causes:**
- System time out of sync
- Incorrect secret key
- Request timeout

**Solutions:**
```bash
# Sync system time
sudo ntpdate pool.ntp.org

# Or increase recv_window
{
  "settings": {
    "recv_window": 10000
  }
}
```

### Debug Mode

Enable detailed logging:

```bash
# .env
LOG_LEVEL=DEBUG
```

```python
# In code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. Check exchange status page
2. Review API documentation
3. Check bot logs: `logs/trading_bot.log`
4. Test with curl/Postman first
5. Contact exchange support if needed

### Verification Checklist

Before going live:

- [ ] API keys created with correct permissions
- [ ] Keys stored in `.env` file securely
- [ ] Configuration file created for broker
- [ ] Connection test passed
- [ ] Balance retrieved successfully
- [ ] Ticker data retrieved
- [ ] Test orders executed (testnet/sandbox)
- [ ] Risk limits configured
- [ ] IP whitelist configured (optional)
- [ ] 2FA enabled on exchange account
- [ ] Withdrawal disabled on API key
- [ ] Backup of API keys stored securely

---

## Conclusion

You should now be able to:
- Create and configure API keys for supported brokers
- Set up testnet/sandbox environments
- Test broker connections
- Secure your API credentials
- Troubleshoot common issues

**Next Steps:**
- Configure your trading strategies ([STRATEGY_GUIDE.md](STRATEGY_GUIDE.md))
- Set up risk management ([CONFIGURATION.md](CONFIGURATION.md))
- Start paper trading
- Monitor and optimize

**Remember:** Always test thoroughly in sandbox/testnet before using real funds!

For additional help:
- [ADDING_BROKERS.md](ADDING_BROKERS.md) - Add new broker integrations
- [CONFIGURATION.md](CONFIGURATION.md) - Detailed configuration reference
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
