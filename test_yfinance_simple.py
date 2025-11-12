#!/usr/bin/env python3
"""
Simple yfinance test with proper multitasking mock
"""
import sys
from unittest.mock import MagicMock

# Create a proper multitasking mock with task decorator
class MockMultitasking:
    @staticmethod
    def cpu_count():
        return 4

    @staticmethod
    def task(func):
        """Mock task decorator that just returns the function"""
        return func

    class set_max_threads:
        """Mock set_max_threads context manager"""
        def __init__(self, n):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

sys.modules['multitasking'] = MockMultitasking()

from curl_cffi import requests
import yfinance as yf

def test_simple():
    """Test yfinance with simple individual queries"""
    print("=" * 80)
    print("Testing Yahoo Finance - Simple Individual Queries")
    print("=" * 80)

    # Create curl_cffi session
    session = requests.Session(impersonate="chrome")

    test_tickers = ["AAPL", "MSFT", "NVDA"]

    for ticker_symbol in test_tickers:
        print(f"\n[{ticker_symbol}]")
        try:
            ticker = yf.Ticker(ticker_symbol, session=session)

            # Test history (usually most reliable)
            print(f"  Fetching 5-day history...", end=" ")
            try:
                hist = ticker.history(period="5d", auto_adjust=True)
                if not hist.empty:
                    latest = hist.iloc[-1]
                    print(f"✓ SUCCESS")
                    print(f"    Latest Close: ${latest['Close']:.2f}")
                    print(f"    Volume: {int(latest['Volume']):,}")
                    print(f"    Date: {hist.index[-1].strftime('%Y-%m-%d')}")

                    # If history works, we have pricing data!
                    success = True
                else:
                    print(f"✗ No data")
                    success = False
            except Exception as e:
                print(f"✗ Error: {str(e)[:80]}")
                success = False

            # If history failed, that's a problem
            if not success:
                print(f"  ⚠️  WARNING: Cannot fetch data for {ticker_symbol}")

        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_simple()
