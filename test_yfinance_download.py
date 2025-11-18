#!/usr/bin/env python3
"""
Test yfinance using download function (more reliable)
"""
import sys
from unittest.mock import MagicMock

# Workaround for multitasking
sys.modules['multitasking'] = MagicMock()

from curl_cffi import requests
import yfinance as yf
import pandas as pd

def test_with_download():
    """Test yfinance using download function"""
    print("=" * 80)
    print("Testing Yahoo Finance with download() function")
    print("=" * 80)

    # Create curl_cffi session
    session = requests.Session(impersonate="chrome")

    test_tickers = ["AAPL", "MSFT", "NVDA"]

    # Test 1: Batch download (most reliable method)
    print("\n=== Test 1: Batch Download ===")
    try:
        print(f"Downloading data for: {', '.join(test_tickers)}")
        data = yf.download(
            tickers=' '.join(test_tickers),
            period="5d",
            session=session,
            progress=False
        )

        if not data.empty:
            print(f"✓ Downloaded {len(data)} days of data")
            print("\nLatest prices:")
            for ticker in test_tickers:
                try:
                    if 'Close' in data:
                        if len(test_tickers) > 1:
                            latest_price = data['Close'][ticker].iloc[-1]
                            volume = data['Volume'][ticker].iloc[-1]
                        else:
                            latest_price = data['Close'].iloc[-1]
                            volume = data['Volume'].iloc[-1]
                        print(f"  {ticker}: ${latest_price:.2f}, Volume: {volume:,.0f}")
                except Exception as e:
                    print(f"  {ticker}: Error - {e}")
        else:
            print("✗ No data downloaded")
    except Exception as e:
        print(f"✗ Download failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Individual ticker with basic_info
    print("\n=== Test 2: Individual Ticker Tests ===")
    for ticker_symbol in test_tickers:
        print(f"\n[{ticker_symbol}]")
        try:
            ticker = yf.Ticker(ticker_symbol, session=session)

            # Try basic_info (more reliable than info)
            print(f"  - Getting basic_info...", end=" ")
            try:
                basic_info = ticker.basic_info
                if basic_info:
                    print("✓")
                    for key in ['previousClose', 'regularMarketOpen', 'dayHigh', 'dayLow', 'volume']:
                        if key in basic_info:
                            print(f"    {key}: {basic_info[key]}")
                else:
                    print("✗ No data")
            except AttributeError:
                print("⚠️  basic_info not available in this version")
            except Exception as e:
                print(f"✗ {str(e)[:60]}")

            # Try get_info() directly
            print(f"  - Getting get_info()...", end=" ")
            try:
                info = ticker.get_info()
                if info and len(info) > 0:
                    print("✓")
                    name = info.get("longName") or info.get("shortName")
                    if name:
                        print(f"    Name: {name}")
                    price = info.get("currentPrice") or info.get("regularMarketPrice")
                    if price:
                        print(f"    Price: ${price:.2f}")
                    mcap = info.get("marketCap")
                    if mcap:
                        print(f"    Market Cap: ${mcap/1e9:.2f}B")
                else:
                    print("✗ No info")
            except Exception as e:
                print(f"✗ {str(e)[:60]}")

        except Exception as e:
            print(f"  ✗ Failed: {e}")

    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_with_download()
