"""
VG CRYPTO STRATEGY: EXPECTED LOG OUTPUT
========================================

This file shows what you should see when the bot runs with the new
VG Crypto Strategy and execution guardrails.

Use this for troubleshooting and validation.
"""

# ============================================================================
# BOT STARTUP LOGS
# ============================================================================

print("""
═══════════════════════════════════════════════════════════════════════════
BOT STARTUP SEQUENCE
═══════════════════════════════════════════════════════════════════════════

[2026-02-07 14:23:45] INFO: TradingBot initialization started
[2026-02-07 14:23:45] INFO: Loading config from: config/global.json
[2026-02-07 14:23:45] INFO: Mode: PAPER_TRADING (no real money)
[2026-02-07 14:23:45] INFO: Broker: cryptocom
[2026-02-07 14:23:45] INFO: DataManager: Initializing...
[2026-02-07 14:23:46] INFO: RiskManager: Portfolio initialized | Balance: $10,000.00 USD

[2026-02-07 14:23:46] INFO: Strategy Registry loading...
[2026-02-07 14:23:46] INFO: ✓ Registered: VGCryptoStrategy
[2026-02-07 14:23:46] INFO: ✓ Strategy alias: vg_crypto_btc -> VGCryptoStrategy
[2026-02-07 14:23:46] INFO: ✓ Strategy alias: vg_crypto_eth -> VGCryptoStrategy
[2026-02-07 14:23:46] INFO: ✓ Strategy alias: vg_crypto_xrp -> VGCryptoStrategy
[2026-02-07 14:23:46] INFO: ✓ Strategy alias: vg_crypto_doge -> VGCryptoStrategy
[2026-02-07 14:23:46] INFO: ✓ Strategy alias: vg_crypto_shib -> VGCryptoStrategy
[2026-02-07 14:23:46] INFO: ✓ Strategy alias: vg_crypto_trump -> VGCryptoStrategy

[2026-02-07 14:23:47] INFO: Loading strategy config: config/strategies/strategy_config.json
[2026-02-07 14:23:47] INFO: Active strategies: 6

Strategy Initialization:
  1. VGCryptoStrategy for BTC
     Params: session_lookback=96, ema_period=20, cooldown=8
     Risk: 0.75% | Stop: -0.75% | Target: +5.0%
     ✓ Initialized

  2. VGCryptoStrategy for ETH
     Params: session_lookback=96, ema_period=20, cooldown=8
     Risk: 0.75% | Stop: -0.75% | Target: +5.0%
     ✓ Initialized

  3. VGCryptoStrategy for XRP
     Params: session_lookback=96, ema_period=20, cooldown=8
     Risk: 0.50% | Stop: -0.50% | Target: +5.0%
     ✓ Initialized

  4. VGCryptoStrategy for DOGE
     Params: session_lookback=96, ema_period=20, cooldown=8
     Risk: 0.30% | Stop: -0.30% | Target: +5.0%
     Meme Mode: BUY ONLY ⚠️
     ✓ Initialized

  5. VGCryptoStrategy for SHIB
     Params: session_lookback=96, ema_period=20, cooldown=8
     Risk: 0.20% | Stop: -0.20% | Target: +5.0%
     Meme Mode: BUY ONLY ⚠️
     ✓ Initialized

  6. VGCryptoStrategy for TRUMP
     Params: session_lookback=96, ema_period=20, cooldown=8
     Risk: 0.10% | Stop: -0.10% | Target: +5.0%
     Meme Mode: BUY ONLY ⚠️
     ✓ Initialized

[2026-02-07 14:23:48] INFO: All strategies initialized successfully
[2026-02-07 14:23:48] INFO: DataManager connecting to Crypto.com API...
[2026-02-07 14:23:49] INFO: Crypto.com connection established
[2026-02-07 14:23:49] INFO: Fetching initial price data...
[2026-02-07 14:23:51] INFO: Price data loaded for all pairs
[2026-02-07 14:23:51] INFO: TradingBot ready | Portfolio: $10,000.00 | Strategies: 6
[2026-02-07 14:23:51] INFO: Starting trading loop...

═══════════════════════════════════════════════════════════════════════════
""")

# ============================================================================
# SIGNAL GENERATION (NORMAL CANDLE)
# ============================================================================

print("""
═══════════════════════════════════════════════════════════════════════════
TYPICAL TRADING CANDLE (During Liquidity Window)
═══════════════════════════════════════════════════════════════════════════

[14:35:00] Candle close | Time: 2026-02-07 14:35:00 UTC
          ├─ BTC: $42,234.50 | Range: [41,980 – 42,450]
          ├─ ETH: $2,456.80 | Range: [2,420 – 2,480]
          ├─ XRP: $2.45 | Range: [2.38 – 2.52]
          ├─ DOGE: $0.38 | Range: [0.35 – 0.42]
          ├─ SHIB: $0.000024 | Range: [0.000021 – 0.000026]
          └─ TRUMP: $35.50 | Range: [32.00 – 38.00]

[14:35:01] Strategy Analysis: BTC (vg_crypto_btc)
          Liquidity check: ✓ UTC 14:35 in [12:00–16:00] window
          Range calc: High=42,450 | Low=41,980 | Range=$470
          Range position: (42,234 - 41,980) / 470 = 54.1%
          EMA(20): $42,200 | EMA slope: +$34 (bullish trend)
          Volatility: 470 / 42,234 = 1.11% (normal)
          
          Signal: HOLD (range_position 54% in middle zone [30-70%])

[14:35:02] Strategy Analysis: XRP (vg_crypto_xrp)
          Liquidity check: ✓ UTC 14:35 in [12:00–16:00] window
          Range calc: High=2.52 | Low=2.38 | Range=0.14
          Range position: (2.45 - 2.38) / 0.14 = 50%
          EMA(20): $2.44 | EMA slope: +0.01 (bullish)
          Volatility: 0.14 / 2.45 = 5.7% (elevated)
          
          Signal: HOLD (in middle zone)

[14:35:03] Strategy Analysis: TRUMP (vg_crypto_trump)
          Liquidity check: ✓ UTC 14:35 in [12:00–16:00] window
          Range calc: High=38.00 | Low=32.00 | Range=6.00
          Range position: (35.50 - 32.00) / 6.00 = 58.3%
          EMA(20): $35.00 | EMA slope: +0.50 (bullish)
          Volatility: 6.00 / 35.50 = 16.9% (HIGH - approaching exhaustion threshold)
          Gold mode: BUY ONLY ✓
          
          Signal: HOLD (in middle zone)

All pairs: HOLD | Waiting for extremes...

═══════════════════════════════════════════════════════════════════════════
""")

# ============================================================================
# BUY SIGNAL GENERATION
# ============================================================================

print("""
═══════════════════════════════════════════════════════════════════════════
BUY SIGNAL DETECTED
═══════════════════════════════════════════════════════════════════════════

[14:40:00] Candle close | Time: 2026-02-07 14:40:00 UTC

[14:40:01] Strategy Analysis: BTC (vg_crypto_btc)
          Liquidity check: ✓ UTC 14:40 in [12:00–16:00] window
          Range calc: High=42,500 | Low=41,800 | Range=$700
          Range position: (41,900 - 41,800) / 700 = 1.4%
          ✓ BOTTOM ZONE (1.4% <= 20% threshold)
          EMA(20): $42,100 | EMA slope: +80 (strong upward pressure)
          ✓ BULLISH BIAS (EMA slope > 0)
          Volatility: 0.83% (normal)
          Cooldown: 0 (ready)
          
          🔥 SIGNAL: BUY
          Entry zone: Bottom 1.4% | Momentum: Strong up | Time: Liquid window
          
          → Forwarding to execution layer...

[14:40:02] Execution Layer: execute_trade()
          
          Order Parameters:
          - Symbol: BTC_USD
          - Side: BUY
          - Quantity: 0.1 BTC
          - Current Bid: $41,900
          - Current Ask: $42,050
          - Spread: ($42,050 - $41,900) / $42,050 = 0.36%
          
          GUARDRAIL 1: Symbol whitelist
          ✓ BTC_USD in ALLOWED_SYMBOLS
          
          GUARDRAIL 2: Spread filter
          ✓ 0.36% <= 0.05% limit?
          ✗ SPREAD TOO WIDE: 0.36% > 0.05% allowed for BTC
          
          ❌ ORDER BLOCKED: SPREAD TOO WIDE
          
          Reason: Bid-Ask spread exceeds 0.05% threshold
          Bid: $41,900
          Ask: $42,050
          Spread: 0.36% (too wide for entry)
          
          Action: Hold order, wait for tighter market

[14:40:03] Market monitoring...

[14:40:15] Candle close | Time: 2026-02-07 14:40:15 UTC

[14:40:15] Market improved!
          
          Current Bid: $41,920
          Current Ask: $41,980
          Spread: ($41,980 - $41,920) / $41,980 = 0.07%
          ✓ Spread now tight enough (0.07% <= 0.05%)?
          Still slightly wide, but monitoring...

[14:41:00] Candle close | Time: 2026-02-07 14:41:00 UTC

[14:41:00] Market: $41,945 | Spread: 0.04%
          ✓ SPREAD OK (0.04% <= 0.05%)
          
          Retrying BUY order...
          
          GUARDRAIL 1: Symbol whitelist
          ✓ BTC_USD in ALLOWED_SYMBOLS
          
          GUARDRAIL 2: Spread filter
          ✓ 0.04% <= 0.05%
          
          GUARDRAIL 3: Meme restrictions
          ✓ BTC is not meme (BUY allowed)
          
          GUARDRAIL 4: Duplicate prevention
          ✓ Last order: never (first trade) | cooldown expired
          
          GUARDRAIL 5: Build limit price
          Side: BUY | Bid: $41,945
          Limit price = $41,945 × 0.999 = $41,904.06
          
          GUARDRAIL 6: Order size validation
          Size: 0.1 BTC | Price: $41,904 | Notional: $4,190.40
          ✓ $4,190.40 >= $10 minimum
          
          GUARDRAIL 7: No meme restrictions for BTC
          ✓ Allowed
          
          ✅ All guardrails passed!
          
          Placing order:
          - Symbol: BTC_USD
          - Side: BUY
          - Amount: 0.1 BTC
          - Price: $41,904.06 (limit)
          
          [API] Order placed | ID: order_8392847
          
          Waiting for fill (timeout: 5 seconds)...
          [0.5s] Status: PENDING
          [1.0s] Status: PENDING
          [1.5s] Status: PENDING
          [2.0s] Status: FILLED
          
          ✅ ORDER FILLED!
          
          Execution Details:
          Order ID: order_8392847
          Symbol: BTC_USD
          Side: BUY
          Fill price: $41,904.06
          Amount: 0.1 BTC
          Notional: $4,190.41
          Timestamp: 2026-02-07T14:41:02.345Z
          
          Position opened: LONG 0.1 BTC @ $41,904

[14:41:02] Portfolio Update:
          Cash before: $10,000.00
          Order cost: $4,190.41
          Cash after: $5,809.59
          BTC holding: 0.1 BTC (cost: $4,190.41, current: $4,189.06)
          Position P&L: -$1.35 (immediate slippage)
          Portfolio value: $9,998.65

═══════════════════════════════════════════════════════════════════════════
""")

# ============================================================================
# TRADE MANAGEMENT (EXIT)
# ============================================================================

print("""
═══════════════════════════════════════════════════════════════════════════
TRADE MANAGEMENT: EXIT DECISION
═══════════════════════════════════════════════════════════════════════════

Time: 2026-02-07 14:43:00 UTC (2 minutes in trade)

[14:43:00] Strategy: BTC manage_trade() check...

          Position: LONG 0.1 BTC | Entry: $41,904 | Current: $42,100
          Candles in trade: 2 (12 min)
          Current P&L: +$19.60 (0.47% profit)
          
          VG Checkpoint (6+ candles):
          Candles: 2 < 6 required
          → Don't check revert exit yet
          
          Volatility exhaustion check:
          Range: [41,850 – 42,200] = $350
          Volatility: 350 / 42,100 = 0.83%
          Threshold: 10%
          0.83% < 10%
          → No volatility exit
          
          Decision: HOLD (continue trade)
          Next check: In 1 more candle (6 candles total)

[14:44:00] Candle close | P&L: +$195.60 (4.67% profit)

[14:44:00] Strategy: BTC manage_trade() check...
          
          Position: LONG 0.1 BTC | Entry: $41,904 | Current: $42,099.60
          Candles in trade: 3 (15 min)
          
          Still < 6 candles, but monitoring...
          
          Decision: HOLD

[14:48:00] Candle close | P&L: -$80.00 (reversing)

[14:48:00] Strategy: BTC manage_trade() check...
          
          Position: LONG 0.1 BTC | Entry: $41,904 | Current: $41,823.57
          Candles in trade: 6 (exactly 6)
          Current P&L: -$80.43 (micro loss)
          
          ✓ VG Checkpoint triggered (6 candles)
          Entry price: $41,904
          Current: $41,823.57
          Position: BUY (long)
          
          Exit condition: current <= entry?
          $41,823.57 <= $41,904?
          ✓ YES (price reversed below entry)
          
          🔴 SIGNAL: EXIT (VG revert condition met)
          
          → Closing position...
          
[14:48:01] Execution: Close LONG position
          
          GUARDRAIL 1: Symbol whitelist
          ✓ BTC_USD allowed
          
          GUARDRAIL 2: Spread filter
          Current bid: $41,823
          Current ask: $41,834
          Spread: 0.027%
          ✓ 0.027% <= 0.05%
          
          GUARDRAIL 3: Meme restrictions
          ✓ BTC not meme
          
          GUARDRAIL 4: Duplicate prevention
          ✓ Cooldown active (prevent flip)
          
          GUARDRAIL 6: Build limit price
          Side: SELL | Ask: $41,834
          Limit price = $41,834 × 1.001 = $41,875.83
          
          Placing exit order:
          - Symbol: BTC_USD
          - Side: SELL
          - Amount: 0.1 BTC
          - Price: $41,875.83 (limit)
          
          [API] Order placed | ID: order_8392903
          
          [0.5s] Status: FILLED
          
          ✅ POSITION CLOSED
          
          Trade Summary:
          Entry: $41,904.00 | Exit: $41,875.83
          Quantity: 0.1 BTC
          P&L: -$28.17 (loss)
          P&L %: -0.067% (-6.7 basis points)
          Duration: 7 minutes
          
[14:48:02] Portfolio Update:
          Cash before: $5,809.59
          Exit proceeds: $4,187.58
          Cash now: $9,997.17
          BTC: 0 (position closed)
          Portfolio value: $9,997.17
          
          Trade stats:
          Total loss: $28.17
          Reason: VG revert exit (price returned to entry)
          
          Cooldown activated: 8 candles
          (prevents re-entry for 8×15min = 2 hours)

═══════════════════════════════════════════════════════════════════════════
""")

# ============================================================================
# REJECTED ORDERS (GUARDRAILS)
# ============================================================================

print("""
═══════════════════════════════════════════════════════════════════════════
REJECTED ORDER EXAMPLES (Why Guardrails Matter)
═══════════════════════════════════════════════════════════════════════════

TIME: 2026-02-07 15:50:00 UTC (Outside liquidity window)

[15:50:00] Strategy: DOGE (vg_crypto_doge) generates BUY
          
          Range: [0.375 – 0.385] | Position: 8% (bottom zone)
          EMA slope: +0.002 (bullish)
          ✓ Signal: BUY
          
          BUT: UTC time is 15:50
          Liquidity check: 15:50 UTC NOT in [00:00–04:00] or [12:00–16:00]
          
          ❌ SIGNAL BLOCKED BY STRATEGY
          Not in liquidity window - no order even sent

TIME: 2026-02-07 14:30:00 UTC (Spread explosion)

[14:30:00] Strategy: ETH (vg_crypto_eth) generates BUY
          Position: 12% (bottom zone) + bullish EMA
          ✓ Signal: BUY
          
          Market volatility spike:
          Bid: $2,400
          Ask: $2,500
          Spread: 4.17% (!!)
          
          execute_trade() called:
          GUARDRAIL 2: spread_ok()?
          Spread 4.17% > 0.05% threshold
          
          ❌ BLOCKED: SPREAD TOO WIDE
          Message: "BLOCKED: SPREAD too wide ETH/USD"
          Action: Hold until market stabilizes

TIME: 2026-02-07 14:35:00 UTC (Meme selling attempt)

[14:35:00] Strategy: SHIB (vg_crypto_shib) calculates
          Range: [0.000023 – 0.000026] | Position: 85%
          EMA slope: -0.000001 (bearish)
          ✓ Would be SELL signal in normal strategy
          
          BUT: Meme coin check
          SHIB in ["DOGE", "SHIB", "TRUMP"]
          Gold mode enabled: BUY ONLY
          
          ❌ SIGNAL BLOCKED BY STRATEGY
          No SELL signal generated (returns HOLD instead)
          
          OR if somehow bypassed:
          execute_trade() called with side="SELL"
          
          GUARDRAIL 7: meme_restrictions()?
          meme_restrictions("SHIB_USD", "SELL") → False
          
          ❌ BLOCKED: MEME RULE
          Message: "BLOCKED: MEME RULE SHIB_USD no SELL orders"

TIME: 2026-02-07 14:40:00 UTC (Duplicate prevention)

[14:40:00] Strategy: BTC generated BUY → FILLED

[14:40:05] Strategy: BTC generates ANOTHER BUY (API glitch retry)
          
          execute_trade() called:
          
          GUARDRAIL 4: prevent_duplicate()?
          Last order: 5 seconds ago
          Cooldown: 10 seconds required
          5 < 10
          
          ❌ BLOCKED: DUPLICATE
          Message: "BLOCKED: DUPLICATE BTC_USD on cooldown"
          Action: Order rejected, no duplicate trade

TIME: 2026-02-07 14:45:00 UTC (Tiny order size)

[14:45:00] Strategy: XRP generates BUY
          qty=0.001 XRP | price=$2.45
          Notional: $0.00245 (tiny)
          
          execute_trade() called:
          
          GUARDRAIL 6: order_size_ok()?
          Notional $0.00245 < $10 minimum
          
          ❌ BLOCKED: SIZE TOO SMALL
          Message: "BLOCKED: SIZE too small XRP_USD"
          Reason: Ghost orders on Crypto.com (too small → rejected)

TIME: 2026-02-07 14:50:00 UTC (Partial fill timeout)

[14:50:00] Order placed: TRUMP BUY
          [1s] Status: PARTIALLY FILLED (0.5x filled)
          [2s] Status: PARTIALLY FILLED (still 0.5x)
          [3s] Status: PARTIALLY FILLED (still 0.5x)
          [4s] Status: PARTIALLY FILLED (still 0.5x)
          [5s] Status: PARTIALLY FILLED (timeout!)
          
          wait_for_fill() timeout expired
          
          ✅ execute_trade() cancels:
          [API] Cancel order → cancelled
          
          ❌ CANCELLED: NO FILL
          Message: "CANCELLED: NO FILL TRUMP_USD within 5 seconds"
          Reason: Partial fills are worse than no fill
          (half position = directional imbalance + risk!)

═══════════════════════════════════════════════════════════════════════════
""")

print("""
═══════════════════════════════════════════════════════════════════════════

This is what you should see in real trading logs.

Key observations:
✓ Strategies filter their own best cases (liquidity windows, range zones)
✓ Guardrails reject edge cases (spreads, sizes, duplicates)
✓ Both layers working together = maximum safety
✓ Better to reject 100 orders than execute 1 bad one

VG Crypto is CONSERVATIVE by design:
  • Fewer trades (only during liquid hours)
  • Better quality entries (range extremes)
  • Safer execution (all guardrails)
  • Meme protection (no liquidation traps)

Trade less → Survive longer → Win bigger

═══════════════════════════════════════════════════════════════════════════
""")
