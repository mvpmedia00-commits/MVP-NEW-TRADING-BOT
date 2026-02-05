#!/usr/bin/env python3
"""
Quick test script for the Trading Bot API server.
Tests basic functionality and endpoints.
"""

import sys
import time
import requests
from datetime import datetime

API_BASE = "http://localhost:8000"
API_KEY = "test-api-key-12345"

def test_health():
    """Test health endpoint (no auth required)."""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check passed")
    return data

def test_root():
    """Test root endpoint (no auth required)."""
    print("\nTesting root endpoint...")
    response = requests.get(f"{API_BASE}/")
    assert response.status_code == 200
    data = response.json()
    assert "Trading Bot API" in data["name"]
    print("✓ Root endpoint passed")
    return data

def test_portfolio_status():
    """Test portfolio status endpoint."""
    print("\nTesting portfolio status...")
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{API_BASE}/api/v1/portfolio/status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_equity" in data
    print(f"✓ Portfolio status: ${data['total_equity']:,.2f}")
    return data

def test_portfolio_positions():
    """Test portfolio positions endpoint."""
    print("\nTesting portfolio positions...")
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{API_BASE}/api/v1/portfolio/positions", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "positions" in data
    print(f"✓ Portfolio positions: {data['total_positions']} positions")
    return data

def test_trade_history():
    """Test trade history endpoint."""
    print("\nTesting trade history...")
    headers = {"X-API-Key": API_KEY}
    response = requests.get(
        f"{API_BASE}/api/v1/trades/history?page=1&page_size=10",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "trades" in data
    print(f"✓ Trade history: {data['total_trades']} total trades")
    return data

def test_strategies():
    """Test strategies list endpoint."""
    print("\nTesting strategies list...")
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{API_BASE}/api/v1/strategies/list", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "strategies" in data
    print(f"✓ Strategies: {data['total_strategies']} total, {data['active_strategies']} active")
    return data

def test_bot_status():
    """Test bot status endpoint."""
    print("\nTesting bot status...")
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{API_BASE}/api/v1/control/status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    print(f"✓ Bot status: {data['status']}")
    return data

def test_invalid_api_key():
    """Test that invalid API key is rejected."""
    print("\nTesting invalid API key...")
    headers = {"X-API-Key": "invalid-key"}
    response = requests.get(f"{API_BASE}/api/v1/portfolio/status", headers=headers)
    assert response.status_code == 401
    print("✓ Invalid API key correctly rejected")

def test_openapi_docs():
    """Test OpenAPI documentation is available."""
    print("\nTesting OpenAPI documentation...")
    response = requests.get(f"{API_BASE}/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    print("✓ OpenAPI documentation available")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Trading Bot API Test Suite")
    print("=" * 60)
    print(f"\nAPI Base URL: {API_BASE}")
    print(f"API Key: {API_KEY}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    for i in range(30):
        try:
            requests.get(f"{API_BASE}/health", timeout=1)
            print("✓ Server is ready")
            break
        except requests.exceptions.RequestException:
            if i == 29:
                print("✗ Server did not start in time")
                sys.exit(1)
            time.sleep(1)
            print(f"  Waiting... ({i+1}/30)")
    
    try:
        # Run tests
        test_health()
        test_root()
        test_openapi_docs()
        test_invalid_api_key()
        test_portfolio_status()
        test_portfolio_positions()
        test_trade_history()
        test_strategies()
        test_bot_status()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
