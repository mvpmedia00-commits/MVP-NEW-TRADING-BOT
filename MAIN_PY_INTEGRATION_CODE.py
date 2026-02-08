"""
MAIN.PY INTEGRATION GUIDE - Exact Code Changes
===============================================

This file shows the specific modifications needed to integrate
the new components into bot/main.py

STEP 1: Update imports (top of file)
=====================================

ADD these imports:

from .core import (
    PortfolioManager, RiskManager, OrderManager, DataManager,
    TradeStateManager,           # NEW
    RiskEngineV2,               # NEW
    ExecutionGuardrailsManagerV2, # NEW
    RangeAnalyzer,              # NEW
)


STEP 2: Update TradingBot.__init__() 
====================================

CURRENT CODE:
    def __init__(self):
        # ... existing code ...
        self.risk_manager = RiskManager(self.global_config.get('risk_management', {}))

ADD AFTER risk_manager:
    # Initialize enhanced components
    self.trade_state_manager = TradeStateManager(
        self.strategy_config.get('trade_management', {})
    )
    
    self.risk_engine_v2 = RiskEngineV2(
        self.global_config.get('risk_management', {})
    )
    
    self.execution_guardrails = ExecutionGuardrailsManagerV2(
        self.global_config.get('execution', {})
    )
    
    self.range_analyzer = RangeAnalyzer(
        self.global_config.get('range_engine', {})
    )


STEP 3: Update _execute_strategy() method
=========================================

REPLACE entire method with:

def _execute_strategy(self, strategy_name: str, strategy: Any):
    \"\"\"
    Execute a single strategy with full validation, risk checks, and guardrails
    \"\"\"
    try:
        symbol = strategy.parameters.get('symbol', 'BTC/USDT')
        broker_name = next(iter(self.brokers.keys()))
        broker = self.brokers[broker_name]
        
        if not broker:
            logger.warning(f"No broker available for {symbol}")
            return
        
        # ========== STEP 1: FETCH MARKET DATA ==========
        data = self.data_manager.fetch_ohlcv(
            symbol=symbol,
            timeframe=self.global_config.get('data', {}).get('timeframe', '15m'),
            limit=self.global_config.get('data', {}).get('lookback_period', 100),
            broker_name=broker_name
        )
        
        if data is None or not data:
            logger.warning(f"No data available for {symbol}")
            return
        
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # ========== STEP 2: ANALYZE RANGE ==========
        analysis = self.range_analyzer.analyze(symbol, df)
        
        can_trade, range_reason = self.range_analyzer.can_trade(analysis)
        if not can_trade:
            logger.debug(f"{symbol}: {range_reason} - skipping this cycle")
            return
        
        # ========== STEP 3: GET STRATEGY SIGNAL ==========
        signal = strategy.generate_signal(df)
        
        ticker = broker.get_ticker(symbol)
        current_price = ticker.get('last', ticker.get('close', 0))
        bid = ticker.get('bid', current_price * 0.99)
        ask = ticker.get('ask', current_price * 1.01)
        
        # ========== STEP 4: CHECK IF ENTERING NEW TRADE ==========
        if signal in ['BUY', 'SELL']:
            # Can we enter a new trade for this symbol?
            can_enter, cooldown_reason = self.trade_state_manager.can_enter_trade(symbol)
            
            if not can_enter:
                logger.debug(f"{symbol}: {cooldown_reason}")
                return
            
            # ========== STEP 5: RISK VALIDATION ==========
            # Calculate position size (strategy or default)
            position_size = strategy.get_position_size() if hasattr(strategy, 'get_position_size') else 0.1
            
            # Convert to quantity
            qty = position_size / current_price if current_price > 0 else 0
            
            can_open, risk_reason = self.risk_engine_v2.can_open_position(
                symbol=symbol,
                direction=signal,
                qty=qty,
                entry_price=current_price
            )
            
            if not can_open:
                logger.warning(f"{symbol}: Risk blocked - {risk_reason}")
                return
            
            # ========== STEP 6: EXECUTE WITH GUARDRAILS ==========
            success, error, result = self.execution_guardrails.validate_and_execute(
                broker=broker,
                symbol=symbol,
                side=signal,
                qty=qty,
                bid=bid,
                ask=ask
            )
            
            if success:
                # ========== STEP 7: OPEN TRADE IN TRACKING SYSTEMS ==========
                # Record in trade state manager
                trade = self.trade_state_manager.open_trade(
                    symbol=symbol,
                    direction=signal,
                    entry_price=current_price,
                    position_size=qty,
                    range_position=analysis['range_position'],
                    volatility=analysis['volatility_pct']
                )
                
                # Record in risk engine
                self.risk_engine_v2.open_position(
                    symbol=symbol,
                    direction=signal,
                    qty=qty,
                    entry_price=current_price
                )
                
                # Record in portfolio
                self.portfolio.add_position(symbol, signal, qty, current_price)
                
                logger.info(
                    f"✅ TRADE OPENED | {symbol} {signal} {qty:.4f} @ ${current_price:.2f} | "
                    f"Range pos: {analysis['range_position']:.1%}"
                )
            else:
                logger.warning(f"❌ {symbol} execution failed: {error}")
        
        # ========== STEP 8: MANAGE EXISTING TRADE ==========
        current_trade = self.trade_state_manager.get_current_trade(symbol)
        
        if current_trade:
            # Calculate how long we've been in trade
            candles_since_entry = len(df) - (current_trade.entry_candle_index or 0)
            
            # Advance VG checkpoints
            self.trade_state_manager.advance_checkpoint(symbol, candles_since_entry)
            
            # Check exit conditions
            exit_signal = strategy.manage_trade(df)
            
            # Check for volatility exhaustion
            should_exit_exhaustion, exhaustion_reason = self.range_analyzer.should_exit_on_exhaustion(analysis)
            
            if exit_signal == 'EXIT' or should_exit_exhaustion or candles_since_entry > 50:
                # Get exit price
                exit_ticker = broker.get_ticker(symbol)
                exit_price = exit_ticker.get('last', current_price)
                exit_bid = exit_ticker.get('bid', exit_price * 0.99)
                exit_ask = exit_ticker.get('ask', exit_price * 1.01)
                
                # Close position
                close_side = "SELL" if current_trade.direction == "BUY" else "BUY"
                
                success, error, _ = self.execution_guardrails.validate_and_execute(
                    broker=broker,
                    symbol=symbol,
                    side=close_side,
                    qty=current_trade.position_size,
                    bid=exit_bid,
                    ask=exit_ask
                )
                
                if success:
                    # Close in trade state manager
                    exit_reason = exhaustion_reason or exit_signal or "Timeout"
                    closed_trade = self.trade_state_manager.close_trade(
                        symbol=symbol,
                        exit_price=exit_price,
                        reason=exit_reason
                    )
                    
                    # Close in risk engine
                    self.risk_engine_v2.close_position(
                        symbol=symbol,
                        exit_price=exit_price,
                        reason=exit_reason
                    )
                    
                    # Close in portfolio
                    self.portfolio.close_position(symbol, exit_price)
                    
                    logger.info(
                        f"✅ TRADE CLOSED | {symbol} {closed_trade.direction} | "
                        f"PnL: ${closed_trade.pnl:.2f} ({closed_trade.pnl_pct:.2f}%) | "
                        f"Reason: {exit_reason}"
                    )
                else:
                    logger.warning(f"❌ {symbol} close failed: {error}")
        
        # Decrement cooldowns each cycle
        self.trade_state_manager.decrement_cooldowns()
        
    except Exception as e:
        logger.error(f"Error executing strategy {strategy_name}: {e}", exc_info=True)


STEP 4: Add monitoring method
=============================

ADD new method to TradingBot class:

def _log_monitoring_stats(self):
    \"\"\"Log current monitoring statistics\"\"\"
    try:
        # Risk stats
        risk_stats = self.risk_engine_v2.get_stats()
        exposure = self.risk_engine_v2.get_current_exposure()
        
        # Execution stats
        exec_stats = self.execution_guardrails.get_execution_stats()
        
        # Trade stats
        trade_stats = self.trade_state_manager.get_stats()
        
        logger.info(
            f"📊 MONITORING | Balance: ${risk_stats.get('current_balance', 0):.2f} | "
            f"Trades: {trade_stats['total_trades']} "
            f"(W:{trade_stats['winning_trades']} L:{trade_stats['losing_trades']}) | "
            f"Exposure: ${exposure['total_exposure']:.0f} | "
            f"Exec rate: {100-exec_stats['rejection_rate']:.1f}%"
        )
    except Exception as e:
        logger.error(f"Error logging stats: {e}")


STEP 5: Add to main loop
=========================

In _run_cycle(), AFTER strategy execution, add:

        # Log periodic monitoring stats (every 10 cycles)
        if self._cycle_count % 10 == 0:
            self._log_monitoring_stats()


STEP 6: Update global config
=============================

Add to config/global.json:

{
  "trade_management": {
    "cooldown_candles": 8,
    "checkpoint_1_candles": 6,
    "checkpoint_2_candles": 12
  },
  
  "range_engine": {
    "session_lookback": 96,
    "min_range_pct": 0.5,
    "chop_threshold_pct": 1.0,
    "exhaustion_threshold_pct": 10.0
  },
  
  "execution": {
    "fill_timeout": 5,
    "max_retries": 3,
    "retry_delay": 1
  }
}


TESTING THE INTEGRATION:
========================

1. Run with --test-connection flag:
   cd bot && python main.py --test-connection
   
   Should show:
   ✅ Connection test successful!
   Connected brokers: ['cryptocom']
   Initialized strategies: ['vg_crypto_btc', 'vg_crypto_eth', ...]

2. Paper trade for 1 hour and check logs for:
   ✅ Range analysis working (Range: $X-$Y | Position: Z%)
   ✅ Signal generation (IF signal detected, should see BUY/SELL)
   ✅ Risk checks passing/failing (Risk blocked: reason)
   ✅ Execution guardrails (✅ Order executed or ❌ BLOCKED: reason)
   ✅ Trade lifecycle (✅ TRADE OPENED, ✅ TRADE CLOSED)
   ✅ Monitoring stats (Balance, Trades W/L, Exposure %)

3. Check that no trades happen outside liquidity windows
   - Only trade during 00:00-04:00 and 12:00-16:00 UTC

4. Verify risk limits:
   - No more than 6 open positions at once
   - No shorts on DOGE/SHIB/TRUMP
   - Total exposure < 3% of account


DEBUGGING CHECKLIST:
====================

If trades not happening:
□ Check liquidity window (must be UTC 00:00-04:00 or 12:00-16:00)
□ Check range volatility > 0.5% (chop filter)
□ Check position not already open
□ Check risk limits allow position

If execution failing:
□ Check symbol in whitelist
□ Check spread < allowed threshold
□ Check order size > $10
□ Check fill timeout (orders should fill in <5s)

If trades closing immediately:
□ Check checkpoint conditions
□ Check exhaustion threshold (>10% volatility)
□ Check timeout (>50 candles)


PERFORMANCE OPTIMIZATION:
=========================

If running slowly:
- Reduce lookback_period in data config (less candles to process)
- Increase update_interval for less frequent cycles
- Cache range analysis results

If experiencing slippage:
- Reduce limit order discount/premium (currently 0.1%)
- Check spread assumptions match actual market
- Use tighter fill timeout (but be careful of timeouts)
"""
