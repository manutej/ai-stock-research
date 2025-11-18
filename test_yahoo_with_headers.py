#!/usr/bin/env python3
"""
Test Yahoo Finance API with proper headers
"""
from curl_cffi import requests
import json

def test_with_headers():
    """Test with proper browser headers"""
    print("=" * 80)
    print("Testing Yahoo Finance API with proper headers")
    print("=" * 80)

    # Create session with Chrome impersonation
    session = requests.Session(impersonate="chrome")

    # Add additional headers that Yahoo Finance expects
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://finance.yahoo.com/',
        'Origin': 'https://finance.yahoo.com',
    }

    test_tickers = ["AAPL", "MSFT", "NVDA"]

    for ticker in test_tickers:
        print(f"\n[{ticker}]")

        # Test Chart API
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {
            "range": "5d",
            "interval": "1d",
        }

        print(f"  Fetching data...", end=" ")
        try:
            response = session.get(url, params=params, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    meta = result.get('meta', {})

                    current_price = meta.get('regularMarketPrice')
                    previous_close = meta.get('previousClose')
                    volume = meta.get('regularMarketVolume')
                    currency = meta.get('currency', 'USD')

                    print(f"    ✓ SUCCESS!")
                    print(f"    Price: ${current_price:.2f} {currency}")
                    print(f"    Previous Close: ${previous_close:.2f}")
                    print(f"    Volume: {volume:,}")

                    # Get historical closes
                    quotes = result.get('indicators', {}).get('quote', [{}])[0]
                    closes = quotes.get('close', [])
                    if closes:
                        valid_closes = [c for c in closes if c is not None]
                        if valid_closes:
                            print(f"    5-day avg: ${sum(valid_closes)/len(valid_closes):.2f}")
                else:
                    print(f"    ✗ No data in response")
                    print(f"    Response keys: {list(data.keys())}")
            else:
                print(f"    ✗ HTTP {response.status_code}")
                if response.status_code == 403:
                    print(f"    Still blocked. Yahoo Finance may be blocking this IP.")
                print(f"    Response: {response.text[:100]}")

        except Exception as e:
            print(f"    ✗ Error: {e}")

    print("\n" + "=" * 80)
    print("Analysis:")
    print("- If still getting 403 errors, Yahoo Finance is likely blocking programmatic access")
    print("- Alternative solutions:")
    print("  1. Use the existing Polygon provider with API key")
    print("  2. Implement yfinance_cache with request caching")
    print("  3. Use Alpha Vantage or other free APIs")
    print("=" * 80)

if __name__ == "__main__":
    test_with_headers()
