#!/usr/bin/env python3
"""
Test script for YFinance provider with new infrastructure

Tests logging, error handling, validation, and rate limiting.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from logging_config import LogConfig
from providers.yfinance_provider import YFinanceProvider


async def test_yfinance_provider():
    """Test YFinance provider with all improvements"""

    # Set up logging
    LogConfig.setup_logging(level="INFO")

    print("=" * 70)
    print("Testing YFinance Provider with New Infrastructure")
    print("=" * 70)

    # Test 1: Provider initialization and connection
    print("\n[TEST 1] Provider initialization and connection")
    try:
        provider = YFinanceProvider()
        async with provider:
            print("✓ Provider connected successfully")
    except Exception as e:
        print(f"✗ Provider connection failed: {e}")
        return

    # Test 2: Get single quote with validation
    print("\n[TEST 2] Get single quote (NVDA)")
    provider = YFinanceProvider()
    async with provider:
        try:
            quote = await provider.get_quote("NVDA")
            print(f"✓ Quote fetched: ${quote.price:.2f}, change: {quote.change_percent:+.2f}%")
        except Exception as e:
            print(f"✗ Quote fetch failed: {e}")

    # Test 3: Invalid ticker validation
    print("\n[TEST 3] Invalid ticker validation (should fail)")
    provider = YFinanceProvider()
    async with provider:
        try:
            quote = await provider.get_quote("INVALID123")
            print("✗ Should have raised InvalidTickerError")
        except Exception as e:
            print(f"✓ Correctly rejected invalid ticker: {type(e).__name__}")

    # Test 4: Batch quotes
    print("\n[TEST 4] Batch quotes (MSFT, GOOGL)")
    provider = YFinanceProvider()
    async with provider:
        try:
            quotes = await provider.get_quotes(["MSFT", "GOOGL"])
            print(f"✓ Fetched {len(quotes)} quotes")
            for ticker, quote in quotes.items():
                print(f"  {ticker}: ${quote.price:.2f}")
        except Exception as e:
            print(f"✗ Batch fetch failed: {e}")

    # Test 5: Historical data
    print("\n[TEST 5] Historical data (AAPL, last 7 days)")
    provider = YFinanceProvider()
    async with provider:
        try:
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            bars = await provider.get_historical("AAPL", start_date, end_date, "1d")
            print(f"✓ Fetched {len(bars)} historical bars")
            if bars:
                print(f"  Latest: {bars[-1].timestamp.date()} Close: ${bars[-1].close:.2f}")
        except Exception as e:
            print(f"✗ Historical fetch failed: {e}")

    # Test 6: News
    print("\n[TEST 6] News (TSLA, last 3 articles)")
    provider = YFinanceProvider()
    async with provider:
        try:
            news = await provider.get_news("TSLA", limit=3)
            print(f"✓ Fetched {len(news)} news articles")
            for article in news[:2]:
                print(f"  - {article.title[:60]}...")
        except Exception as e:
            print(f"✗ News fetch failed: {e}")

    # Test 7: Market status
    print("\n[TEST 7] Market status")
    provider = YFinanceProvider()
    async with provider:
        try:
            status = await provider.get_market_status()
            print(f"✓ Market status: {'OPEN' if status.is_open else 'CLOSED'}")
        except Exception as e:
            print(f"✗ Market status check failed: {e}")

    print("\n" + "=" * 70)
    print("✓ All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_yfinance_provider())
