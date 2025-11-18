#!/usr/bin/env python3
"""
Test yfinance with explicit curl_cffi session
"""
import sys
from unittest.mock import MagicMock

# Workaround for multitasking
sys.modules['multitasking'] = MagicMock()

from curl_cffi import requests
import yfinance as yf

def test_with_explicit_session():
    """Test yfinance with explicit curl_cffi session"""
    print("=" * 80)
    print("Testing Yahoo Finance with explicit curl_cffi session")
    print("=" * 80)

    # Create curl_cffi session that impersonates Chrome
    session = requests.Session(impersonate="chrome")

    print(f"\nSession type: {type(session)}")
    print(f"Session headers: {dict(session.headers)}\n")

    test_tickers = ["AAPL", "MSFT", "NVDA"]

    for ticker_symbol in test_tickers:
        print(f"\n[{ticker_symbol}] Testing...")
        try:
            # Pass the curl_cffi session explicitly
            ticker = yf.Ticker(ticker_symbol, session=session)

            # Test 1: Get history (most reliable)
            print(f"  - Fetching history(period='5d')...", end=" ")
            hist = ticker.history(period="5d")
            if not hist.empty:
                latest_price = hist['Close'].iloc[-1]
                volume = hist['Volume'].iloc[-1]
                print(f"✓ Got {len(hist)} days. Latest: ${latest_price:.2f}, Vol: {volume:,.0f}")
            else:
                print("✗ No historical data")

            # Test 2: Get fast_info
            print(f"  - Fetching fast_info...", end=" ")
            try:
                fast_info = ticker.fast_info
                price = fast_info.get('lastPrice') or fast_info.get('regularMarketPrice')
                if price:
                    print(f"✓ Price: ${price:.2f}")
                else:
                    print(f"⚠️  No price. Keys: {list(fast_info.keys())[:5]}")
            except Exception as e:
                print(f"✗ Error: {str(e)[:80]}")

            # Test 3: Get info
            print(f"  - Fetching info...", end=" ")
            try:
                info = ticker.info
                if info and len(info) > 0:
                    company_name = info.get("longName") or info.get("shortName", "Unknown")
                    market_cap = info.get("marketCap")
                    pe_ratio = info.get("trailingPE")
                    print(f"✓ {company_name}")
                    if market_cap:
                        print(f"    Market Cap: ${market_cap/1e9:.2f}B", end="")
                    if pe_ratio:
                        print(f", P/E: {pe_ratio:.2f}", end="")
                    print()

                    # Show more metrics
                    revenue = info.get("totalRevenue")
                    profit_margin = info.get("profitMargins")
                    roe = info.get("returnOnEquity")

                    if revenue:
                        print(f"    Revenue: ${revenue/1e9:.1f}B")
                    if profit_margin:
                        print(f"    Profit Margin: {profit_margin*100:.1f}%")
                    if roe:
                        print(f"    ROE: {roe*100:.1f}%")
                else:
                    print("✗ Empty info dict")
            except Exception as e:
                print(f"✗ Error: {str(e)[:80]}")

            print(f"  ✓ SUCCESS - {ticker_symbol} data retrieved!")

        except Exception as e:
            print(f"\n  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_with_explicit_session()
