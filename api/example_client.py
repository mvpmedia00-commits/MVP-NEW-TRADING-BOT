#!/usr/bin/env python3
"""
Example client usage for the Trading Bot API.
Shows how to interact with the API endpoints.
"""

import requests
from datetime import datetime

class TradingBotClient:
    """Client for interacting with the Trading Bot API."""
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the API (e.g., http://localhost:8000)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {"X-API-Key": api_key}
    
    def health_check(self):
        """Check API health."""
        return requests.get(f"{self.base_url}/health").json()
    
    # Portfolio methods
    def get_portfolio_status(self):
        """Get current portfolio status."""
        return requests.get(
            f"{self.base_url}/api/v1/portfolio/status",
            headers=self.headers
        ).json()
    
    def get_positions(self, symbol=None):
        """Get portfolio positions."""
        params = {"symbol": symbol} if symbol else {}
        return requests.get(
            f"{self.base_url}/api/v1/portfolio/positions",
            headers=self.headers,
            params=params
        ).json()
    
    def get_performance(self, period="all"):
        """Get portfolio performance metrics."""
        return requests.get(
            f"{self.base_url}/api/v1/portfolio/performance",
            headers=self.headers,
            params={"period": period}
        ).json()
    
    # Trade methods
    def get_trade_history(self, page=1, page_size=50, symbol=None, strategy=None):
        """Get trade history."""
        params = {
            "page": page,
            "page_size": page_size
        }
        if symbol:
            params["symbol"] = symbol
        if strategy:
            params["strategy"] = strategy
        
        return requests.get(
            f"{self.base_url}/api/v1/trades/history",
            headers=self.headers,
            params=params
        ).json()
    
    def get_active_trades(self, symbol=None):
        """Get active trades."""
        params = {"symbol": symbol} if symbol else {}
        return requests.get(
            f"{self.base_url}/api/v1/trades/active",
            headers=self.headers,
            params=params
        ).json()
    
    def get_trade(self, trade_id):
        """Get specific trade details."""
        return requests.get(
            f"{self.base_url}/api/v1/trades/{trade_id}",
            headers=self.headers
        ).json()
    
    # Strategy methods
    def list_strategies(self, enabled_only=None):
        """List all strategies."""
        params = {"enabled_only": enabled_only} if enabled_only is not None else {}
        return requests.get(
            f"{self.base_url}/api/v1/strategies/list",
            headers=self.headers,
            params=params
        ).json()
    
    def get_strategy(self, strategy_id):
        """Get strategy details."""
        return requests.get(
            f"{self.base_url}/api/v1/strategies/{strategy_id}",
            headers=self.headers
        ).json()
    
    def enable_strategy(self, strategy_id, reason=None):
        """Enable a strategy."""
        data = {"reason": reason} if reason else {}
        return requests.post(
            f"{self.base_url}/api/v1/strategies/{strategy_id}/enable",
            headers=self.headers,
            json=data
        ).json()
    
    def disable_strategy(self, strategy_id, reason=None):
        """Disable a strategy."""
        data = {"reason": reason} if reason else {}
        return requests.post(
            f"{self.base_url}/api/v1/strategies/{strategy_id}/disable",
            headers=self.headers,
            json=data
        ).json()
    
    # Bot control methods
    def start_bot(self):
        """Start the trading bot."""
        return requests.post(
            f"{self.base_url}/api/v1/control/start",
            headers=self.headers
        ).json()
    
    def stop_bot(self):
        """Stop the trading bot."""
        return requests.post(
            f"{self.base_url}/api/v1/control/stop",
            headers=self.headers
        ).json()
    
    def get_bot_status(self):
        """Get bot status."""
        return requests.get(
            f"{self.base_url}/api/v1/control/status",
            headers=self.headers
        ).json()
    
    def emergency_stop(self, close_positions=True, reason="Manual emergency stop"):
        """Execute emergency stop."""
        return requests.post(
            f"{self.base_url}/api/v1/control/emergency-stop",
            headers=self.headers,
            json={
                "close_positions": close_positions,
                "reason": reason
            }
        ).json()


def main():
    """Example usage of the client."""
    # Initialize client
    client = TradingBotClient(
        base_url="http://localhost:8000",
        api_key="your-secret-api-key-change-this"
    )
    
    print("Trading Bot API Client Example")
    print("=" * 60)
    
    # Check health
    print("\n1. Health Check")
    health = client.health_check()
    print(f"   Status: {health['status']}")
    
    # Get portfolio status
    print("\n2. Portfolio Status")
    portfolio = client.get_portfolio_status()
    print(f"   Equity: ${portfolio['total_equity']:,.2f}")
    print(f"   Cash: ${portfolio['cash']:,.2f}")
    print(f"   P&L: ${portfolio['total_pnl']:,.2f} ({portfolio['total_pnl_percent']}%)")
    
    # Get positions
    print("\n3. Current Positions")
    positions = client.get_positions()
    for pos in positions['positions'][:3]:  # Show first 3
        print(f"   {pos['symbol']}: {pos['quantity']} @ ${pos['current_price']:.2f}")
    
    # Get trade history
    print("\n4. Recent Trades")
    trades = client.get_trade_history(page=1, page_size=5)
    print(f"   Total trades: {trades['total_trades']}")
    for trade in trades['trades'][:3]:  # Show first 3
        print(f"   {trade['symbol']}: {trade['side']} {trade['quantity']} @ ${trade['price']:.2f}")
    
    # List strategies
    print("\n5. Strategies")
    strategies = client.list_strategies()
    print(f"   Total: {strategies['total_strategies']}, Active: {strategies['active_strategies']}")
    for strategy in strategies['strategies']:
        status = "✓" if strategy['enabled'] else "✗"
        print(f"   {status} {strategy['name']}")
    
    # Get bot status
    print("\n6. Bot Status")
    bot_status = client.get_bot_status()
    print(f"   Status: {bot_status['status']}")
    print(f"   Active strategies: {bot_status['active_strategies']}")
    print(f"   Active positions: {bot_status['active_positions']}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
