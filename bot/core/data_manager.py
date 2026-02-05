"""
Data Manager - Handles data fetching, caching, and management from brokers
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
from collections import deque
import time

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MarketData:
    """Represents market data for a symbol"""
    
    def __init__(self, symbol: str, timeframe: str):
        self.symbol = symbol
        self.timeframe = timeframe
        self.ohlcv: deque = deque(maxlen=1000)  # Store max 1000 candles
        self.last_update: Optional[datetime] = None
        self.ticker: Optional[Dict[str, Any]] = None
        self.ticker_update: Optional[datetime] = None
    
    def add_candle(self, candle: List):
        """
        Add OHLCV candle
        
        Args:
            candle: [timestamp, open, high, low, close, volume]
        """
        self.ohlcv.append(candle)
        self.last_update = datetime.utcnow()
    
    def add_candles(self, candles: List[List]):
        """Add multiple OHLCV candles"""
        for candle in candles:
            self.ohlcv.append(candle)
        self.last_update = datetime.utcnow()
    
    def update_ticker(self, ticker: Dict[str, Any]):
        """Update ticker data"""
        self.ticker = ticker
        self.ticker_update = datetime.utcnow()
    
    def get_latest_price(self) -> Optional[float]:
        """Get latest price from ticker or OHLCV"""
        if self.ticker and 'last' in self.ticker:
            return float(self.ticker['last'])
        
        if self.ohlcv:
            # Return close price of latest candle
            return float(self.ohlcv[-1][4])
        
        return None
    
    def get_candles(self, limit: Optional[int] = None) -> List[List]:
        """
        Get OHLCV candles
        
        Args:
            limit: Number of candles to return (latest)
            
        Returns:
            List of OHLCV candles
        """
        if limit:
            return list(self.ohlcv)[-limit:]
        return list(self.ohlcv)
    
    def is_stale(self, max_age_seconds: int = 300) -> bool:
        """
        Check if data is stale
        
        Args:
            max_age_seconds: Maximum age in seconds
            
        Returns:
            True if data is stale
        """
        if not self.last_update:
            return True
        
        age = (datetime.utcnow() - self.last_update).total_seconds()
        return age > max_age_seconds


class DataManager:
    """
    Manages market data fetching, caching, and distribution.
    Thread-safe for concurrent access.
    """
    
    def __init__(
        self,
        brokers: Optional[Dict[str, Any]] = None,
        default_timeframe: str = '1h',
        cache_size: int = 1000
    ):
        """
        Initialize the data manager
        
        Args:
            brokers: Dictionary of broker instances
            default_timeframe: Default timeframe for data
            cache_size: Maximum number of candles to cache per symbol
        """
        self.brokers = brokers or {}
        self.default_timeframe = default_timeframe
        self.cache_size = cache_size
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Data cache: (symbol, timeframe) -> MarketData
        self._market_data: Dict[tuple, MarketData] = {}
        
        # Account data cache
        self._balances: Dict[str, Dict[str, float]] = {}  # broker -> balances
        self._positions: Dict[str, List[Dict[str, Any]]] = {}  # broker -> positions
        self._balance_update: Dict[str, datetime] = {}
        self._position_update: Dict[str, datetime] = {}
        
        # Statistics
        self._fetch_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
        logger.info(
            f"Data manager initialized | Default timeframe: {default_timeframe} | "
            f"Cache size: {cache_size}"
        )
    
    def set_broker(self, broker_name: str, broker_instance: Any):
        """
        Add or update broker instance
        
        Args:
            broker_name: Broker identifier
            broker_instance: Broker instance
        """
        with self._lock:
            self.brokers[broker_name] = broker_instance
            logger.info(f"Broker registered: {broker_name}")
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: Optional[str] = None,
        limit: int = 100,
        broker_name: Optional[str] = None,
        force_refresh: bool = False
    ) -> Optional[List[List]]:
        """
        Fetch OHLCV data for a symbol
        
        Args:
            symbol: Trading symbol
            timeframe: Data timeframe
            limit: Number of candles to fetch
            broker_name: Specific broker to use
            force_refresh: Force refresh from broker
            
        Returns:
            List of OHLCV candles or None if error
        """
        with self._lock:
            try:
                timeframe = timeframe or self.default_timeframe
                cache_key = (symbol, timeframe)
                
                # Check cache if not forcing refresh
                if not force_refresh and cache_key in self._market_data:
                    market_data = self._market_data[cache_key]
                    
                    # Return cached data if not stale
                    if not market_data.is_stale():
                        self._cache_hits += 1
                        logger.debug(f"Cache hit: {symbol} {timeframe}")
                        return market_data.get_candles(limit)
                
                self._cache_misses += 1
                
                # Fetch from broker
                broker = self._get_broker(broker_name)
                if not broker:
                    logger.error("No broker available for data fetch")
                    return None
                
                candles = broker.get_ohlcv(symbol, timeframe, limit)
                
                if candles:
                    # Update cache
                    if cache_key not in self._market_data:
                        self._market_data[cache_key] = MarketData(symbol, timeframe)
                    
                    self._market_data[cache_key].add_candles(candles)
                    self._fetch_count += 1
                    
                    logger.debug(
                        f"OHLCV fetched: {symbol} {timeframe} | "
                        f"{len(candles)} candles"
                    )
                
                return candles
                
            except Exception as e:
                logger.error(
                    f"Error fetching OHLCV for {symbol}: {e}",
                    exc_info=True
                )
                return None
    
    def fetch_ticker(
        self,
        symbol: str,
        broker_name: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch current ticker/price data
        
        Args:
            symbol: Trading symbol
            broker_name: Specific broker to use
            use_cache: Use cached data if available
            
        Returns:
            Ticker data or None if error
        """
        with self._lock:
            try:
                cache_key = (symbol, self.default_timeframe)
                
                # Check cache
                if use_cache and cache_key in self._market_data:
                    market_data = self._market_data[cache_key]
                    if market_data.ticker and not self._is_ticker_stale(market_data):
                        self._cache_hits += 1
                        return market_data.ticker
                
                self._cache_misses += 1
                
                # Fetch from broker
                broker = self._get_broker(broker_name)
                if not broker:
                    logger.error("No broker available for ticker fetch")
                    return None
                
                ticker = broker.get_ticker(symbol)
                
                if ticker:
                    # Update cache
                    if cache_key not in self._market_data:
                        self._market_data[cache_key] = MarketData(
                            symbol,
                            self.default_timeframe
                        )
                    
                    self._market_data[cache_key].update_ticker(ticker)
                    logger.debug(f"Ticker fetched: {symbol} | Price: {ticker.get('last')}")
                
                return ticker
                
            except Exception as e:
                logger.error(f"Error fetching ticker for {symbol}: {e}", exc_info=True)
                return None
    
    def get_current_price(
        self,
        symbol: str,
        broker_name: Optional[str] = None
    ) -> Optional[float]:
        """
        Get current price for a symbol
        
        Args:
            symbol: Trading symbol
            broker_name: Specific broker to use
            
        Returns:
            Current price or None
        """
        ticker = self.fetch_ticker(symbol, broker_name)
        if ticker:
            return float(ticker.get('last', 0))
        return None
    
    def fetch_balance(
        self,
        broker_name: str,
        force_refresh: bool = False
    ) -> Optional[Dict[str, float]]:
        """
        Fetch account balance from broker
        
        Args:
            broker_name: Broker name
            force_refresh: Force refresh from broker
            
        Returns:
            Balance dictionary or None
        """
        with self._lock:
            try:
                # Check cache
                if not force_refresh and broker_name in self._balances:
                    if not self._is_balance_stale(broker_name):
                        self._cache_hits += 1
                        return self._balances[broker_name]
                
                self._cache_misses += 1
                
                # Fetch from broker
                broker = self.brokers.get(broker_name)
                if not broker:
                    logger.error(f"Broker not found: {broker_name}")
                    return None
                
                balance = broker.get_balance()
                
                if balance:
                    self._balances[broker_name] = balance
                    self._balance_update[broker_name] = datetime.utcnow()
                    logger.debug(f"Balance fetched: {broker_name}")
                
                return balance
                
            except Exception as e:
                logger.error(
                    f"Error fetching balance for {broker_name}: {e}",
                    exc_info=True
                )
                return None
    
    def fetch_positions(
        self,
        broker_name: str,
        force_refresh: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch open positions from broker
        
        Args:
            broker_name: Broker name
            force_refresh: Force refresh from broker
            
        Returns:
            List of positions or None
        """
        with self._lock:
            try:
                # Check cache
                if not force_refresh and broker_name in self._positions:
                    if not self._is_position_stale(broker_name):
                        self._cache_hits += 1
                        return self._positions[broker_name]
                
                self._cache_misses += 1
                
                # Fetch from broker
                broker = self.brokers.get(broker_name)
                if not broker:
                    logger.error(f"Broker not found: {broker_name}")
                    return None
                
                positions = broker.get_positions()
                
                if positions is not None:
                    self._positions[broker_name] = positions
                    self._position_update[broker_name] = datetime.utcnow()
                    logger.debug(
                        f"Positions fetched: {broker_name} | Count: {len(positions)}"
                    )
                
                return positions
                
            except Exception as e:
                logger.error(
                    f"Error fetching positions for {broker_name}: {e}",
                    exc_info=True
                )
                return None
    
    def get_cached_price(self, symbol: str, timeframe: Optional[str] = None) -> Optional[float]:
        """
        Get price from cache without fetching
        
        Args:
            symbol: Trading symbol
            timeframe: Data timeframe
            
        Returns:
            Cached price or None
        """
        with self._lock:
            timeframe = timeframe or self.default_timeframe
            cache_key = (symbol, timeframe)
            
            if cache_key in self._market_data:
                return self._market_data[cache_key].get_latest_price()
            
            return None
    
    def get_multiple_prices(
        self,
        symbols: List[str],
        broker_name: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Get current prices for multiple symbols
        
        Args:
            symbols: List of trading symbols
            broker_name: Specific broker to use
            
        Returns:
            Dictionary of symbol -> price
        """
        prices = {}
        
        for symbol in symbols:
            price = self.get_current_price(symbol, broker_name)
            if price:
                prices[symbol] = price
        
        return prices
    
    def clear_cache(self, symbol: Optional[str] = None, timeframe: Optional[str] = None):
        """
        Clear data cache
        
        Args:
            symbol: Specific symbol to clear (None = all)
            timeframe: Specific timeframe to clear
        """
        with self._lock:
            if symbol and timeframe:
                cache_key = (symbol, timeframe)
                if cache_key in self._market_data:
                    del self._market_data[cache_key]
                    logger.info(f"Cache cleared: {symbol} {timeframe}")
            elif symbol:
                # Clear all timeframes for symbol
                keys_to_remove = [
                    k for k in self._market_data.keys()
                    if k[0] == symbol
                ]
                for key in keys_to_remove:
                    del self._market_data[key]
                logger.info(f"Cache cleared for symbol: {symbol}")
            else:
                # Clear all
                self._market_data.clear()
                self._balances.clear()
                self._positions.clear()
                logger.info("All cache cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get data manager statistics"""
        with self._lock:
            cache_hit_rate = 0.0
            total_requests = self._cache_hits + self._cache_misses
            
            if total_requests > 0:
                cache_hit_rate = (self._cache_hits / total_requests) * 100
            
            return {
                'total_fetches': self._fetch_count,
                'cache_hits': self._cache_hits,
                'cache_misses': self._cache_misses,
                'cache_hit_rate': cache_hit_rate,
                'cached_symbols': len(self._market_data),
                'registered_brokers': len(self.brokers)
            }
    
    def _get_broker(self, broker_name: Optional[str] = None) -> Optional[Any]:
        """Get broker instance"""
        if broker_name and broker_name in self.brokers:
            return self.brokers[broker_name]
        
        # Return first available broker
        if self.brokers:
            return next(iter(self.brokers.values()))
        
        return None
    
    def _is_ticker_stale(self, market_data: MarketData, max_age_seconds: int = 60) -> bool:
        """Check if ticker data is stale"""
        if not market_data.ticker_update:
            return True
        
        age = (datetime.utcnow() - market_data.ticker_update).total_seconds()
        return age > max_age_seconds
    
    def _is_balance_stale(self, broker_name: str, max_age_seconds: int = 300) -> bool:
        """Check if balance data is stale"""
        if broker_name not in self._balance_update:
            return True
        
        age = (datetime.utcnow() - self._balance_update[broker_name]).total_seconds()
        return age > max_age_seconds
    
    def _is_position_stale(self, broker_name: str, max_age_seconds: int = 300) -> bool:
        """Check if position data is stale"""
        if broker_name not in self._position_update:
            return True
        
        age = (datetime.utcnow() - self._position_update[broker_name]).total_seconds()
        return age > max_age_seconds
    
    def reset(self):
        """Reset data manager (for testing)"""
        with self._lock:
            self.clear_cache()
            self._fetch_count = 0
            self._cache_hits = 0
            self._cache_misses = 0
            logger.info("Data manager reset")
