#!/usr/bin/env python3
"""
Diagnostic test for yfinance 403 errors
"""
import sys
from unittest.mock import MagicMock

# Workaround for multitasking
sys.modules['multitasking'] = MagicMock()

import yfinance as yf

def test_basic_fetch():
    """Test basic yfinance data fetch"""
    print("=" * 80)
    print("Testing Yahoo Finance API Access")
    print("=" * 80)

    test_tickers = ["AAPL", "MSFT", "NVDA"]

    for ticker in test_tickers:
        print(f"\n[{ticker}] Testing...")
        try:
            stock = yf.Ticker(ticker)

            # Test 1: Get info
            print(f"  - Fetching info()...", end=" ")
            info = stock.info
            if info:
                price = info.get("currentPrice") or info.get("regularMarketPrice")
                if price:
                    print(f"✓ Got price: ${price:.2f}")
                else:
                    print(f"✗ No price in info. Keys: {list(info.keys())[:5]}")
            else:
                print("✗ No info data")

            # Test 2: Get history
            print(f"  - Fetching history()...", end=" ")
            hist = stock.history(period="5d")
            if not hist.empty:
                latest_price = hist['Close'].iloc[-1]
                print(f"✓ Got {len(hist)} days. Latest: ${latest_price:.2f}")
            else:
                print("✗ No historical data")

            # Test 3: Get fast_info (newer API)
            print(f"  - Fetching fast_info...", end=" ")
            try:
                fast_info = stock.fast_info
                if fast_info:
                    price = fast_info.get('lastPrice')
                    print(f"✓ Got price: ${price:.2f}")
                else:
                    print("✗ No fast_info data")
            except Exception as e:
                print(f"✗ Error: {str(e)[:50]}")

        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_basic_fetch()
