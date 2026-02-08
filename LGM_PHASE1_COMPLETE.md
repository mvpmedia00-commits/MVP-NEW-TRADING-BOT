# LGM Trading Bot - Phase 1 Implementation

## ✅ Completed: Indicator/Signal Layer

**Status:** Phase 1 Complete (Indicator Layer)  
**Date:** 2026-02-08  
**Architecture Alignment:** LGM System Architecture v1

---

## What Was Implemented

### 1. LGM Indicator Engine (`bot/indicators/__init__.py`)

A clean, isolated layer that enriches raw OHLCV data with LGM-required signals:

**Inputs:**
- Raw OHLCV candles (timestamp, open, high, low, close, volume)

**Outputs (added columns):**
- `arrow_color`: "red", "green", "gold", "purple"
- `line_of_scrimmage`: 5 PM EST daily open price
- `adr`: Average Daily Range (14-day lookback)
- `daily_high`: Session high
- `daily_low`: Session low
- `pb1_level`: First pullback level (38.2% Fibonacci)
- `pb2_level`: Second pullback level (50% Fibonacci)
- `x_signal`: X pattern detected (bool)
- `candle_reversal_confirmed`: X confirmation via candle close (bool)
- `range_position`: Normalized position in daily range (0.0 = bottom, 1.0 = top)
- `ema_fast`: 20-period EMA
- `ema_slow`: 50-period EMA
- `ema_slope`: Directional momentum

**Arrow Color Logic:**
- **GOLD**: Bottom 25% of range + upward slope → LGM entry allowed
- **PURPLE**: Top 75% of range + downward slope → LGM entry allowed
- **GREEN**: Mid-range + upward slope → LGM blocked
- **RED**: Mid-range + downward slope → LGM blocked

**X Signal Detection:**
- Price crosses EMA with >0.5% strength
- Volume spike >1.5x average
- Next candle confirms direction

---

### 2. Integration into Main Bot

**File:** `bot/main.py`

**Changes:**
1. Import `LGMIndicatorEngine`
2. Initialize in `TradingBot.__init__()`
3. Call `enrich()` in `_execute_strategy()` before strategy signal generation

**Data Flow:**
```
Raw OHLCV → LGMIndicatorEngine.enrich() → Enriched DataFrame → LGM Strategy → Trade Decision
```

---

### 3. LGM Strategy (`bot/strategies/lgm_strategy.py`)

**Status:** Already created, now fully functional with indicator layer.

The strategy now receives all required columns:
- Uses `arrow_color` for entry filtering (gold/purple only)
- Uses `line_of_scrimmage` for distance validation
- Uses `adr`, `daily_high`, `daily_low` for ADR exhaustion logic
- Uses `x_signal` for exit decisions
- Uses `pb1_level`, `pb2_level` for pending order placement

---

### 4. Configuration

**File:** `config/global.json`

Added `lgm_indicators` section:
```json
{
  "lgm_indicators": {
    "timezone": "US/Eastern",
    "adr_lookback": 14,
    "ema_fast": 20,
    "ema_slow": 50
  }
}
```

**File:** `config/strategies/strategy_config.json`

Active strategies switched to LGM:
```json
{
  "active_strategies": [
    "LGM_btc",
    "LGM_eth",
    "LGM_xrp",
    "LGM_doge",
    "LGM_shib",
    "LGM_trump"
  ]
}
```

---

## Architecture Layer Status

| Layer | Status | Files |
|-------|--------|-------|
| **1. Market Data Layer** | ✅ Existing | `bot/core/data_manager.py` |
| **2. Indicator/Signal Layer** | ✅ **NEW** | `bot/indicators/__init__.py` |
| **3. LGM Decision Engine** | ✅ Ready | `bot/strategies/LGM_strategy.py` |
| **4. Execution Layer** | ✅ Existing | `bot/utils/execution_guardrails.py` |
| **5. State & Audit Layer** | ✅ Existing | `bot/core/trade_state_manager.py` |
| **6. Dashboard/Viewer Layer** | ⏳ Phase 2 | `bot/api/static/dashboard.html` |

---

## Testing the Indicator Layer

### 1. Verify Indicator Columns

```python
from bot.indicators import LGMIndicatorEngine
import pandas as pd

# Sample OHLCV data
df = pd.DataFrame({
    'timestamp': [1707350400000] * 100,  # Example timestamps
    'open': [50000] * 100,
    'high': [51000] * 100,
    'low': [49000] * 100,
    'close': [50500] * 100,
    'volume': [1000] * 100
})

engine = LGMIndicatorEngine()
enriched = engine.enrich(df)

print(enriched.columns)
# Expected: arrow_color, adr, line_of_scrimmage, pb1_level, pb2_level, x_signal, etc.
```

### 2. Check Arrow Colors

```python
print(enriched[['close', 'range_position', 'ema_slope', 'arrow_color']].tail())
```

Expected output:
- GOLD when price is low + momentum up
- PURPLE when price is high + momentum down

### 3. Verify ADR Calculation

```python
print(f"ADR: {enriched['adr'].iloc[-1]:.2f}")
print(f"Daily High: {enriched['daily_high'].iloc[-1]:.2f}")
print(f"Daily Low: {enriched['daily_low'].iloc[-1]:.2f}")
```

---

## Next Steps (Phase 2)

### Dashboard/Viewer Layer Redesign

**Goal:** Implement the LGM Viewer Experience spec.

**Components to Build:**
1. **Global Status Bar** - Kill Zone, Day Quality, Bot State
2. **Market Watch Panel** - Arrow display, ADR %, eligibility
3. **Trade Lifecycle Panel** - Pending/Live state, checkpoint timeline
4. **Checkpoint Timeline Visual** - Entry → CP1 → CP2 → CP3
5. **X & Exit Awareness Panel** - X detection, confirmation, exit reasons
6. **Daily Guard Panel** - Trade limits, loss tracking, lock status
7. **Confidence Mode Panel** - Expectancy curve, play tracking

**Files to Update:**
- `bot/api/static/dashboard.html` - Complete UI redesign
- `bot/api/routes/monitoring.py` - New endpoints for LGM metrics
- `bot/core/trade_state_manager.py` - Checkpoint progress tracking

---

## Phase 3 (Future)

### Additional Layers
- **Backtest Replay Viewer** - Visual replay of historical LGM trades
- **Rule Violation Heatmap** - Audit where rules were tested/broken
- **Mobile Read-Only Viewer** - Minimal viewer for monitoring
- **VG Dashboard** - Separate app for Vector Games logic (no LGM mixing)

---

## Key Design Principles Maintained

✅ **Separation of Concerns**  
- Indicators never make trade decisions
- Strategies never calculate indicators
- Execution never overrides signals

✅ **Clean Interfaces**  
- `enrich()` method is single entry point
- DataFrame in → DataFrame out (immutable pattern)
- No side effects

✅ **Testability**  
- Every indicator can be tested independently
- No external dependencies in calculation logic
- Deterministic outputs

✅ **Extensibility**  
- Easy to add new indicators
- Easy to adjust thresholds via config
- No hardcoded magic numbers

---

## Configuration Reference

### Global Config (`config/global.json`)

```json
{
  "LGM_indicators": {
    "timezone": "US/Eastern",      // Trading session timezone
    "adr_lookback": 14,            // Days for ADR calculation
    "ema_fast": 20,                // Fast EMA period
    "ema_slow": 50                 // Slow EMA period
  }
}
```

### Strategy Config (`config/strategies/strategy_config.json`)

```json
{
  "LGM_btc": {
    "enabled": true,
    "parameters": {
      "symbol": "BTC/USDT",
      "timezone": "US/Eastern",
      "killzone_start": "02:00",
      "killzone_end": "12:00",
      "allowed_days": ["tuesday", "wednesday", "thursday"],
      "max_trades_per_day": 3,
      "max_trades_per_pair_per_day": 1,
      "distance_from_line_pct": 0.35,  // Min distance from scrimmage
      "adr_low_pct": 0.70,             // ADR exhaustion threshold (low)
      "adr_high_pct": 0.85,            // ADR exhaustion threshold (high)
      "checkpoints": [8, 16, 20],      // Candle checkpoints
      "disable_after_losses": 2        // Daily loss limit
    },
    "risk_settings": {
      "position_size": 10.0            // Fixed lot size (LGM minimum)
    }
  }
}
```

---

## Troubleshooting

### Issue: Missing Columns Warning

**Symptom:**
```
LGM missing column: arrow_color
```

**Cause:** Indicator layer not being called.

**Fix:** Check that `_execute_strategy()` calls `self.LGM_indicators.enrich(df)`.

---

### Issue: All Arrows Show "red"

**Cause:** Insufficient historical data for EMA calculation.

**Fix:** Increase `lookback_period` in `config/global.json` data section to at least 100 candles.

---

### Issue: X Signals Never Trigger

**Cause:** Volume data missing or zero.

**Fix:** Verify exchange provides volume data. If not, set volume spike filter to `False` in indicator logic.

---

## Files Changed in Phase 1

```
bot/indicators/__init__.py          [NEW] - LGM indicator engine
bot/main.py                         [MODIFIED] - Integrated indicator layer
bot/strategies/LGM_strategy.py     [EXISTING] - Now uses enriched data
config/global.json                  [MODIFIED] - Added LGM_indicators config
config/strategies/strategy_config.json  [MODIFIED] - Switched to LGM strategies
```

---

## Summary

✅ **Phase 1 Complete**: Indicator/Signal Layer fully implemented and integrated.  
✅ **LGM Strategy Operational**: Strategy now receives all required signals.  
⏳ **Phase 2 Next**: Dashboard redesign to match LGM Viewer Experience spec.

The bot will now:
1. Fetch OHLCV data
2. Enrich with arrows, ADR, line of scrimmage, X signals
3. Pass to LGM strategy for rule-based decisions
4. Execute only when all filters pass

**No trade decisions are made in the indicator layer** — maintaining clean separation of concerns as specified in the architecture.
