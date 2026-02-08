# Crypto.com Exchange Setup Guide

## Quick Start

### 1. Get API Credentials

#### For Testnet (Sandbox - Recommended for testing):
1. Visit **Crypto.com Exchange Sandbox**: https://exchange-sandbox.crypto.com/
2. Create a sandbox account (separate from main account)
3. Go to **API Management** section
4. Click **Create API Key**
5. Set permissions:
   - ✅ Read (required for market data)
   - ✅ Trade (required for placing orders)
   - ❌ Withdraw (not needed, keep disabled for security)
6. Copy and save:
   - API Key
   - API Secret
   - **Store these securely!**

#### For Live Trading (Production):
⚠️ **Warning**: Only use after thorough testing in sandbox!

1. Visit **Crypto.com Exchange**: https://crypto.com/exchange
2. Log in to your verified account
3. Go to **Settings** → **API Management**
4. Create API Key with appropriate permissions
5. Consider IP whitelisting for security

---

## Configuration Methods

### Method 1: Environment Variables (Recommended - Most Secure)

**Create a `.env` file** in the project root:

```bash
# Copy the example file
cp .env.example .env
```

**Edit `.env` and add your credentials:**

```bash
# Crypto.com Exchange
CRYPTOCOM_API_KEY=your_actual_api_key_here
CRYPTOCOM_API_SECRET=your_actual_secret_here
CRYPTOCOM_TESTNET=true  # Set to false for live trading
```

**Important**: 
- Never commit `.env` file to Git (already in .gitignore)
- Keep credentials secret
- Use different keys for testnet and production

---

### Method 2: Direct Config File (Less Secure)

Edit `config/brokers/cryptocom.json`:

```json
{
  "enabled": true,
  "api_credentials": {
    "api_key": "your_actual_api_key_here",
    "api_secret": "your_actual_secret_here"
  },
  "settings": {
    "testnet": true
  }
}
```

⚠️ **Warning**: Don't commit API keys to Git!

---

## Supported Trading Pairs

The bot supports these pairs on Crypto.com Exchange:
- BTC/USDT, ETH/USDT, XRP/USDT
- DOGE/USDT, SHIB/USDT
- TRUMP/USDT (if available)
- CRO/USDT (Crypto.com's native token)
- SOL/USDT, ADA/USDT, DOT/USDT
- MATIC/USDT, AVAX/USDT, BNB/USDT

---

## Testing the Connection

### Local Testing (Windows):

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run bot with connection test
python -m bot.main --test-connection
```

### Google Cloud Shell:

```bash
# Navigate to project
cd ~/MVP-NEW-TRADING-BOT
source venv/bin/activate

# Set environment variables (temporary)
export CRYPTOCOM_API_KEY="your_key"
export CRYPTOCOM_API_SECRET="your_secret"
export CRYPTOCOM_TESTNET="true"

# Test connection
python -m bot.main --test-connection
```

### With API Server:

```bash
# Cloud Shell
BOT_AUTOSTART=1 CRYPTOCOM_API_KEY="your_key" CRYPTOCOM_API_SECRET="your_secret" uvicorn bot.api.server:app --host 0.0.0.0 --port 8080
```

---

## Verification Checklist

- [ ] Created Crypto.com Exchange account (sandbox or live)
- [ ] Generated API key with Read + Trade permissions
- [ ] Saved API credentials securely
- [ ] Set environment variables or updated config file
- [ ] Enabled broker in `config/brokers/cryptocom.json` (`"enabled": true`)
- [ ] Set `testnet: true` for sandbox testing
- [ ] Tested connection successfully
- [ ] Dashboard shows "Crypto.com connected"

---

## Troubleshooting

### "No brokers connected" Error
- Check `config/brokers/cryptocom.json` has `"enabled": true`
- Verify API credentials are set (check .env file or config)
- Confirm environment variables are exported in Cloud Shell

### "Invalid API Key" Error
- Verify API key and secret are correct (no extra spaces)
- Check you're using sandbox credentials with `testnet: true`
- Ensure API key has Read + Trade permissions

### "Rate Limit Exceeded"
- Crypto.com has rate limits (default: enabled in config)
- Bot already has `enableRateLimit: true` setting
- Wait 1-2 minutes and retry

### "Symbol Not Supported"
- Check `supported_pairs` list in `config/brokers/cryptocom.json`
- Verify symbol format: `BTC/USDT` (not `BTCUSDT`)
- Confirm pair is available on Crypto.com Exchange

---

## Security Best Practices

1. **Never commit API keys to Git**
   - `.env` is in `.gitignore`
   - Don't put real keys in config files you commit

2. **Use IP Whitelisting**
   - Add your Cloud Shell IP to API key restrictions
   - Limits access even if key is compromised

3. **Separate Keys for Testing/Production**
   - Use sandbox keys for development
   - Different keys for live trading

4. **Minimal Permissions**
   - Only enable Read + Trade
   - Never enable Withdraw for bot keys

5. **Regular Key Rotation**
   - Generate new keys every 90 days
   - Delete old/unused keys immediately

---

## Next Steps

After successful connection:
1. Monitor dashboard at `http://localhost:8080` (local) or Cloud Shell URL
2. Verify "Crypto.com Exchange" shows as connected
3. Check trade statistics and risk exposure panels
4. Start with paper trading mode (`BOT_MODE=paper`)
5. Validate with small amounts before scaling up

---

## Additional Resources

- **Crypto.com Exchange API Docs**: https://exchange-docs.crypto.com/
- **Sandbox Environment**: https://exchange-sandbox.crypto.com/
- **API Rate Limits**: https://exchange-docs.crypto.com/#rate-limits
- **CCXT Library (underlying)**: https://docs.ccxt.com/

---

**Support**: If you encounter issues, check logs at `logs/bot.log` for detailed error messages.
