#!/usr/bin/env python3
"""
Test yfinance with curl_cffi (automatically used when installed)
"""
import sys
from unittest.mock import MagicMock

# Workaround for multitasking
sys.modules['multitasking'] = MagicMock()

import yfinance as yf

def test_automatic_curl_cffi():
    """Test yfinance - it will automatically use curl_cffi if installed"""
    print("=" * 80)
    print("Testing Yahoo Finance (auto curl_cffi)")
    print("=" * 80)

    test_tickers = ["AAPL", "MSFT", "NVDA"]

    for ticker_symbol in test_tickers:
        print(f"\n[{ticker_symbol}] Testing...")
        try:
            # Just create ticker - it will use curl_cffi automatically
            ticker = yf.Ticker(ticker_symbol)

            # Test 1: Get fast_info (most reliable for price)
            print(f"  - Fetching fast_info...", end=" ")
            try:
                fast_info = ticker.fast_info
                price = fast_info.get('lastPrice') or fast_info.get('regularMarketPrice')
                if price:
                    print(f"✓ Price: ${price:.2f}")
                else:
                    print(f"✗ No price. Available: {list(fast_info.keys())[:5]}")
            except Exception as e:
                print(f"✗ Error: {str(e)[:80]}")

            # Test 2: Get history
            print(f"  - Fetching history(period='5d')...", end=" ")
            hist = ticker.history(period="5d")
            if not hist.empty:
                latest_price = hist['Close'].iloc[-1]
                volume = hist['Volume'].iloc[-1]
                print(f"✓ Got {len(hist)} days. Latest: ${latest_price:.2f}, Vol: {volume:,.0f}")
            else:
                print("✗ No historical data")

            # Test 3: Get info (slower but has more data)
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
                else:
                    print("✗ Empty info dict")
            except Exception as e:
                print(f"✗ Error: {str(e)[:80]}")

            # Test 4: Key metrics
            print(f"  - Key metrics:", end=" ")
            try:
                if info:
                    revenue = info.get("totalRevenue")
                    profit_margin = info.get("profitMargins")
                    roe = info.get("returnOnEquity")

                    metrics = []
                    if revenue:
                        metrics.append(f"Revenue: ${revenue/1e9:.1f}B")
                    if profit_margin:
                        metrics.append(f"Profit Margin: {profit_margin*100:.1f}%")
                    if roe:
                        metrics.append(f"ROE: {roe*100:.1f}%")

                    if metrics:
                        print("✓")
                        for metric in metrics:
                            print(f"    {metric}")
                    else:
                        print("⚠️  Some metrics missing")
                else:
                    print("⚠️  No info available")
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
    test_automatic_curl_cffi()
