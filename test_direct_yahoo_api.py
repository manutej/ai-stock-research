#!/usr/bin/env python3
"""
Test direct Yahoo Finance API access
"""
from curl_cffi import requests
import json

def test_direct_api():
    """Test direct API calls to Yahoo Finance"""
    print("=" * 80)
    print("Testing Direct Yahoo Finance API Access")
    print("=" * 80)

    session = requests.Session(impersonate="chrome")

    test_tickers = ["AAPL", "MSFT", "NVDA"]

    for ticker in test_tickers:
        print(f"\n[{ticker}]")

        # Test 1: Chart API (for price history)
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {
            "range": "5d",
            "interval": "1d",
        }

        print(f"  Fetching chart data...", end=" ")
        try:
            response = session.get(url, params=params)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    meta = result.get('meta', {})
                    quotes = result.get('indicators', {}).get('quote', [{}])[0]

                    current_price = meta.get('regularMarketPrice')
                    previous_close = meta.get('previousClose')
                    volume = meta.get('regularMarketVolume')

                    print(f"    ✓ SUCCESS")
                    print(f"    Price: ${current_price:.2f}")
                    print(f"    Previous Close: ${previous_close:.2f}")
                    print(f"    Volume: {volume:,}")

                    # Get historical data
                    timestamps = result.get('timestamp', [])
                    closes = quotes.get('close', [])
                    if timestamps and closes:
                        print(f"    Historical: {len(closes)} days of data")
                else:
                    print(f"    ✗ Unexpected response format")
            else:
                print(f"    ✗ Error: HTTP {response.status_code}")
                print(f"    Response: {response.text[:200]}")

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

        # Test 2: Quotesummary API (for fundamentals)
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        params = {
            "modules": "price,summaryDetail,financialData,defaultKeyStatistics"
        }

        print(f"\n  Fetching fundamentals...", end=" ")
        try:
            response = session.get(url, params=params)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if 'quoteSummary' in data and 'result' in data['quoteSummary']:
                    result = data['quoteSummary']['result'][0]

                    # Extract key metrics
                    price_info = result.get('price', {})
                    summary = result.get('summaryDetail', {})
                    financial = result.get('financialData', {})
                    key_stats = result.get('defaultKeyStatistics', {})

                    print(f"    ✓ SUCCESS")

                    # Market cap
                    mcap = price_info.get('marketCap', {}).get('raw')
                    if mcap:
                        print(f"    Market Cap: ${mcap/1e9:.2f}B")

                    # P/E ratio
                    pe = summary.get('trailingPE', {}).get('raw')
                    if pe:
                        print(f"    P/E Ratio: {pe:.2f}")

                    # Profit margin
                    profit_margin = financial.get('profitMargins', {}).get('raw')
                    if profit_margin:
                        print(f"    Profit Margin: {profit_margin*100:.2f}%")

                    # ROE
                    roe = financial.get('returnOnEquity', {}).get('raw')
                    if roe:
                        print(f"    ROE: {roe*100:.2f}%")

                else:
                    print(f"    ✗ Unexpected response format")
            else:
                print(f"    ✗ Error: HTTP {response.status_code}")

        except Exception as e:
            print(f"✗ Error: {e}")

    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_direct_api()
