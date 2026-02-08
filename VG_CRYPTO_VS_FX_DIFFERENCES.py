"""
VG CRYPTO vs VG FX/INDICES: QUICK REFERENCE
============================================

This file shows the KEY DIFFERENCES between the original VG strategy
(for FX/Indices) and the new VG Crypto adaptation.

VG CORE CONCEPT STAYS THE SAME:
- Range extremes trading
- Directional bias filter (EMA slope)
- Volatility exhaustion exits
- Cooldown to prevent overtrading

WHAT CHANGES FOR CRYPTO:
- Time filtering
- Position entry zones
- Meme handling
- Range lookback period
"""

# ============================================================================
# COMPARISON TABLE
# ============================================================================

COMPARISON = """

┌─────────────────┬────────────────────────┬────────────────────────┐
│ DIMENSION       │ VG FX/INDICES          │ VG CRYPTO              │
├─────────────────┼────────────────────────┼────────────────────────┤
│ Time Filter     │ Kill Zone: 2–12 EST    │ Liquidity Windows:     │
│ (Session)       │ (US equity hours)      │ • 00:00–04:00 UTC      │
│                 │                        │ • 12:00–16:00 UTC      │
│                 │                        │ Trade 24/7 but only in │
│                 │                        │ high-liquidity periods │
├─────────────────┼────────────────────────┼────────────────────────┤
│ Trading Hours   │ 9:30–16:00 EST only    │ 24/7 but filtered      │
│                 │ (dead inside kill zone)│ (peak liquidity hours) │
├─────────────────┼────────────────────────┼────────────────────────┤
│ Range Lookback  │ 50 candles             │ 96 candles (~4h on     │
│                 │                        │ 15min bars = full day) │
├─────────────────┼────────────────────────┼────────────────────────┤
│ BUY Entry Zone  │ Bottom 20%              │ Major: 20%             │
│                 │ + upward pressure      │ Meme: 15%              │
│                 │ + no shorts            │ (Meme tighter + BUY OK)│
├─────────────────┼────────────────────────┼────────────────────────┤
│ SELL Entry Zone │ Top 85%                │ Major: 85%             │
│ (Shorts)        │ + downward pressure    │ Meme: NO SELLS         │
│                 │                        │ (Gold mode only)       │
├─────────────────┼────────────────────────┼────────────────────────┤
│ Meme Handling   │ N/A (FX/Indices)       │ Gold-Mode:             │
│                 │                        │ • DOGE/SHIB/TRUMP      │
│                 │                        │ • BUY ONLY             │
│                 │                        │ • Tighter entries      │
│                 │                        │ • Lower risk (0.1–0.3%)│
├─────────────────┼────────────────────────┼────────────────────────┤
│ ADR Assumption  │ "Stable range"         │ "Explosive + asymmetric│
│                 │ (predictable)          │ (violent expansion)"   │
├─────────────────┼────────────────────────┼────────────────────────┤
│ Fake Breakout   │ "Chop in kill zone"    │ "Fake moves in low-    │
│ Risk            │                        │ liquidity windows"     │
├─────────────────┼────────────────────────┼────────────────────────┤
│ Risk Per Pair   │ 0.75% (all pairs)      │ Tiered by volatility:  │
│                 │                        │ • BTC/ETH: 0.75%       │
│                 │                        │ • XRP: 0.50%           │
│                 │                        │ • DOGE: 0.30%          │
│                 │                        │ • SHIB: 0.20%          │
│                 │                        │ • TRUMP: 0.10%         │
├─────────────────┼────────────────────────┼────────────────────────┤
│ Execution Layer │ Basic: Market orders   │ INSTITUTIONAL:         │
│                 │ (likely slippage)      │ • Limit orders only    │
│                 │                        │ • 7 guardrails         │
│                 │                        │ • Spread filters       │
│                 │                        │ • Partial fill timeout │
└─────────────────┴────────────────────────┴────────────────────────┘

"""

print(COMPARISON)

# ============================================================================
# CODE DIFFERENCES (SIDE BY SIDE)
# ============================================================================

print("\n" + "="*80)
print("VG FX STRATEGY (OLD): kill_zone() method")
print("="*80)
print("""
def in_kill_zone(self, timestamp) -> bool:
    \"\"\"
    FX Kill Zone: 2 AM - 12 PM EST
    Trade only this window.
    \"\"\"
    est = timestamp.tz_convert("America/New_York").time()
    trading_hours = time(2, 0) <= est <= time(12, 0)
    return trading_hours
""")

print("\n" + "="*80)
print("VG CRYPTO STRATEGY (NEW): in_liquidity_window() method")
print("="*80)
print("""
def in_liquidity_window(self, timestamp) -> bool:
    \"\"\"
    Crypto Liquidity Windows (UTC):
    - Asia: 00:00 – 04:00 UTC
    - London-NY: 12:00 – 16:00 UTC
    
    Avoid: 20:00 – 23:59 UTC (thin + fakes)
    \"\"\"
    utc = timestamp.tz_convert("UTC").time()
    
    asia = time(0, 0) <= utc <= time(4, 0)
    london_ny = time(12, 0) <= utc <= time(16, 0)
    
    return asia or london_ny
""")

print("\n" + "="*80)
print("VG (BOTH): Entry Zone Definition")
print("="*80)
print("""
# ENTRY POSITIONING:
# range_position = 0.0 (bottom) → 1.0 (top)

# -------- FX/INDICES --------
# BUY: range_position <= 0.20 (bottom 20%)
# SELL: range_position >= 0.85 (top 15%)
# Both allowed always

# -------- CRYPTO --------
# BUY: majors <= 0.20, memes <= 0.15
# SELL: majors >= 0.85, memes NEVER
# Memes restricted to BUY only
""")

print("\n" + "="*80)
print("VG (BOTH): Signal Generation Logic")
print("="*80)
print("""
# IDENTICAL CORE:
if (
    not self.trade_open
    and latest["range_position"] <= ENTRY_ZONE  # 0.20 for majors
    and latest["ema_slope"] > 0  # Upward pressure
):
    return "BUY"

# MEME EXCEPTION (CRYPTO ONLY):
if asset in ["DOGE", "SHIB", "TRUMP"]:
    return "NO SELL ORDERS"  # Gold mode
else:
    if latest["range_position"] >= 0.85 and latest["ema_slope"] < 0:
        return "SELL"  # Major pairs only
""")

print("\n" + "="*80)
print("EXECUTION LAYER: VG FX vs VG CRYPTO")
print("="*80)
print("""
┌─────────────────────────────────────────────────────────────────┐
│ VG FX (BASIC EXECUTION)                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ if signal == "BUY":                                             │
│     order = client.place_market_order(symbol, qty)             │
│                                                                 │
│ Problems:                                                       │
│ ✗ Market orders = slippage death                              │
│ ✗ No spread checking                                           │
│ ✗ No duplicate prevention                                      │
│ ✗ No position size validation                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ VG CRYPTO (INSTITUTIONAL GUARDRAILS)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ from bot.utils.execution_guardrails import execute_trade       │
│                                                                 │
│ success, msg = execute_trade(                                  │
│     client=broker,                                             │
│     symbol=symbol,                                             │
│     side="BUY",                                                │
│     qty=qty,                                                   │
│     bid=bid,                                                   │
│     ask=ask                                                    │
│ )                                                               │
│                                                                 │
│ Improvements:                                                  │
│ ✓ Symbol whitelist (approved pairs only)                       │
│ ✓ Spread validation (no fake moves)                            │
│ ✓ Limit orders (0.999× bid, 1.001× ask)                       │
│ ✓ Meme restrictions (no DOGE/SHIB/TRUMP sells)                │
│ ✓ Duplicate blocker (10s cooldown per symbol)                 │
│ ✓ Size validation (min $10 notional)                           │
│ ✓ Fill timeout (cancel if not filled in 5 seconds)            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
""")

# ============================================================================
# PARAMETER TUNING DIFFERENCES
# ============================================================================

print("\n" + "="*80)
print("PARAMETER TUNING DIFFERENCES")
print("="*80)
print("""
VG FX/INDICES:
  range_lookback: 50 candles (tighter, intraday)
  ema_period: 20 candles (standard momentum)
  cooldown: 8 candles

VG CRYPTO:
  session_lookback: 96 candles (4 hours on 15min = full session)
  ema_period: 20 candles (same momentum period)
  cooldown: 8 candles (same overtrading prevention)
  volatility_threshold: 0.10 (10% exhaustion exit)

Why 96?
  - Crypto has 24h liquidity → use longer lookback
  - Better noise filtering on 24/7 noise
  - Captures full "session" range (4h blocks)
  - Still responsive enough for tactical entries
""")

print("\n" + "="*80)
print("WEEKLY/WEEKEND HANDLING")
print("="*80)
print("""
VG FX/INDICES:
  Weekends: Markets CLOSED (ignore)
  Weekend filter: Optional

VG CRYPTO:
  Weekends: Markets OPEN but THIN
  Strategy: Can trade but spreads widen
  
Options:
  1. Hard weekend filter (skip Sat-Sun)
     if today.weekday() >= 5: return "HOLD"
  
  2. Soft filter (trade but require better conditions)
     if today.weekday() >= 5:
         require spread <= 0.03% (tighter)
  
  Recommended: Hard filter until you have stats
""")

print("\n" + "="*80)
print("ADR / VOLATILITY ASSUMPTIONS")
print("="*80)
print("""
VG FX:
  ADR = fairly stable (avg daily range)
  Volatility = predictable
  
  → Use fixed stop-loss (0.5% below entry)
  → Use fixed take-profit (range × 0.3)

VG CRYPTO:
  ADR = EXPLOSIVE + ASYMMETRIC
  Volatility = wild, expansion phases
  
  → Use volatility-adjusted stops
  → Use time-based exits (exhaustion detector)
  → Use partial profit-taking
  
Example: BTC ADR can be:
  • 1% on boring days
  • 5% on FOMC days
  • 15% on network upgrade hype days
→ Solution: volatility_threshold filter exit
""")

# ============================================================================
# RISK MANAGEMENT DIFFERENCES
# ============================================================================

print("\n" + "="*80)
print("RISK MANAGEMENT TIERS")
print("="*80)
print("""
VG FX/INDICES (flat):
  All pairs: 0.75% risk per trade

VG CRYPTO (tiered):
  Liquidity-based:
  ✓ BTC/ETH: 0.75% (highest liquidity)
  ✓ XRP: 0.50% (good liquidity)
  ✓ DOGE: 0.30% (retail favorite, volatile)
  ✓ SHIB: 0.20% (micro-liquidity, meme)
  ✓ TRUMP: 0.10% (ultra-risky, pure meme)

Why tiered?
  Lower liquidity = worse fills = risk multiplier
  Meme coins = beta × 2-3 vs market
  TRUMP specifically = 9x+ leverage equivalent
  
Risk per $10k account:
  BTC: $75 stop-loss allocation
  ETH: $75 stop-loss allocation
  XRP: $50 stop-loss allocation
  DOGE: $30 stop-loss allocation
  SHIB: $20 stop-loss allocation
  TRUMP: $10 stop-loss allocation
  
  Total max daily risk: $260 (2.6% of account)
  → Conservative but allows 6 concurrent "hot" trades
""")

# ============================================================================
# SUMMARY: WHEN TO USE WHICH
# ============================================================================

print("\n" + "="*80)
print("WHEN TO USE WHICH STRATEGY")
print("="*80)
print("""
Use VG FX/INDICES (vg_extreme_range.py) when:
  ✓ Trading FX pairs (GBP/USD, EUR/USD, etc.)
  ✓ Trading stock indices (SPY, NDX, etc.)
  ✓ Trading during market hours (US equities 9:30–16:00 EST)
  ✓ Range is predictable and stable
  ✗ NOT for 24/7 markets

Use VG CRYPTO (vg_crypto_strategy.py) when:
  ✓ Trading cryptocurrency (BTC, ETH, etc.)
  ✓ Trading 24/7 markets with liquidity windows
  ✓ Need meme coin restrictions (DOGE, SHIB, TRUMP)
  ✓ Need institutional guardrails (spread/size/fill checks)
  ✓ Trading on Crypto.com or similar exchanges
  ✓ Want tiered risk management by pair

Hybrid approach:
  • Run VG FX on equities during market hours
  • Run VG CRYPTO on crypto 24/7
  • Both use same core VG logic
  • Execute layer differs (guardrails for crypto)
""")

print("\n" + "="*80)
print("FINAL: THE VG ADAPTATION PRINCIPLE")
print("="*80)
print("""
VG is not a strategy → it's a FRAMEWORK

Framework stays:
✓ Range + EMA slot logic
✓ Entry at extremes (bottom/top)
✓ Exit on volatility exhaustion
✓ Cooldown to prevent overtrading

Adapt to market:
✓ Time filters (kill zone → liquidity windows)
✓ Position sizing (flat → tiered by asset)
✓ Meme handling (add restrictions)
✓ Execution (basic limit orders → guaranteed guardrails)

The VG TRUTH HOLDS:
"Trade less, survives longer"
"Fewer trades, higher quality"
"Extremes + momentum = edge"

Crypto needs more guardrails because:
• 24/7 = more chop
• Spreads = wider + variable
• Memes = bankruptcy traps
• Fills = unreliable without limit logic

The guardrails aren't changing VG.
They're making VG SURVIVABLE in crypto.

That's adaptation without corruption of the framework.
""")
