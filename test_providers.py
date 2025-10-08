"""
Test script for data provider abstraction layer

Tests both YFinance and Polygon providers to verify the modular architecture.
"""
import asyncio
import sys
from datetime import datetime, timedelta

from config import Config
from providers.factory import ProviderFactory, ProviderStrategy


async def test_yfinance_provider():
    """Test YFinance provider (completely free)"""
    print("\n" + "="*60)
    print("🧪 Testing YFinance Provider (FREE)")
    print("="*60)

    provider = ProviderFactory.create_provider(strategy=ProviderStrategy.YFINANCE_ONLY)

    async with provider:
        print(f"\n✓ Connected to {provider.provider_name}")

        # Test 1: Get Quote
        print("\n1️⃣  Testing get_quote for NVDA...")
        quote = await provider.get_quote("NVDA")
        print(f"   Ticker: {quote.ticker}")
        print(f"   Price: ${quote.price:.2f}")
        print(f"   Change: {quote.change:+.2f} ({quote.change_percent:+.2f}%)")
        print(f"   Volume: {quote.volume:,}" if quote.volume else "   Volume: N/A")
        print(f"   Provider: {quote.provider}")

        # Test 2: Get Multiple Quotes
        print("\n2️⃣  Testing batch quotes for AI stocks...")
        tickers = ["NVDA", "MSFT", "GOOGL"]
        quotes = await provider.get_quotes(tickers)
        for ticker, quote in quotes.items():
            print(f"   {ticker}: ${quote.price:.2f} ({quote.change_percent:+.2f}%)")

        # Test 3: Historical Data
        print("\n3️⃣  Testing historical data for MSFT (last 7 days)...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        bars = await provider.get_historical("MSFT", start_date, end_date, "1d")
        print(f"   Retrieved {len(bars)} daily bars")
        if bars:
            latest = bars[-1]
            print(f"   Latest: O:{latest.open:.2f} H:{latest.high:.2f} L:{latest.low:.2f} C:{latest.close:.2f}")

        # Test 4: News
        print("\n4️⃣  Testing news for NVDA...")
        news = await provider.get_news("NVDA", limit=3)
        print(f"   Retrieved {len(news)} news articles")
        for i, article in enumerate(news[:3], 1):
            print(f"   {i}. {article.title[:60]}...")

        # Test 5: Financials
        print("\n5️⃣  Testing financials for GOOGL...")
        financials = await provider.get_financials("GOOGL", limit=2)
        print(f"   Retrieved {len(financials)} financial reports")
        if financials:
            latest = financials[0]
            print(f"   Period: {latest.period_start.date()} to {latest.period_end.date()}")
            print(f"   Revenue: ${latest.revenue/1e9:.2f}B" if latest.revenue else "   Revenue: N/A")
            print(f"   Net Income: ${latest.net_income/1e9:.2f}B" if latest.net_income else "   Net Income: N/A")

        print("\n✅ YFinance provider tests completed!")


async def test_polygon_provider():
    """Test Polygon provider (requires API key)"""
    print("\n" + "="*60)
    print("🧪 Testing Polygon Provider (API Key Required)")
    print("="*60)

    config = Config()
    if not config.POLYGON_API_KEY:
        print("⚠️  POLYGON_API_KEY not found - skipping Polygon tests")
        return

    provider = ProviderFactory.create_provider(
        strategy=ProviderStrategy.POLYGON_ONLY,
        polygon_api_key=config.POLYGON_API_KEY
    )

    async with provider:
        print(f"\n✓ Connected to {provider.provider_name}")

        # Test 1: Market Status
        print("\n1️⃣  Testing market status...")
        status = await provider.get_market_status()
        print(f"   Market Open: {status.is_open}")
        print(f"   Server Time: {status.server_time}")

        # Test 2: News (works on free tier)
        print("\n2️⃣  Testing news...")
        news = await provider.get_news("NVDA", limit=3)
        print(f"   Retrieved {len(news)} news articles")
        for i, article in enumerate(news[:3], 1):
            print(f"   {i}. {article.title[:60]}...")

        # Test 3: Financials (works on free tier)
        print("\n3️⃣  Testing financials...")
        financials = await provider.get_financials("MSFT", limit=2)
        print(f"   Retrieved {len(financials)} financial reports")
        if financials:
            latest = financials[0]
            print(f"   Period: {latest.fiscal_period} {latest.fiscal_year}")

        print("\n✅ Polygon provider tests completed!")


async def test_hybrid_provider():
    """Test Hybrid provider (best of both worlds)"""
    print("\n" + "="*60)
    print("🧪 Testing Hybrid Provider (YFinance + Polygon)")
    print("="*60)

    config = Config()
    provider = ProviderFactory.create_provider(
        strategy=ProviderStrategy.HYBRID,
        polygon_api_key=config.POLYGON_API_KEY
    )

    async with provider:
        print(f"\n✓ Connected to {provider.provider_name}")

        # Test 1: Quotes (from YFinance - free!)
        print("\n1️⃣  Testing quotes (via YFinance)...")
        quote = await provider.get_quote("NVDA")
        print(f"   NVDA: ${quote.price:.2f} ({quote.change_percent:+.2f}%)")
        print(f"   Data source: {quote.provider}")

        # Test 2: News (from Polygon if available - better quality)
        print("\n2️⃣  Testing news (via Polygon or YFinance)...")
        news = await provider.get_news("NVDA", limit=3)
        print(f"   Retrieved {len(news)} news articles")
        if news:
            print(f"   Data source: {news[0].provider}")

        # Test 3: Financials (from YFinance - comprehensive)
        print("\n3️⃣  Testing financials (via YFinance)...")
        financials = await provider.get_financials("MSFT", limit=2)
        print(f"   Retrieved {len(financials)} financial reports")
        if financials:
            print(f"   Data source: {financials[0].provider}")

        print("\n✅ Hybrid provider tests completed!")


async def test_auto_selection():
    """Test automatic provider selection"""
    print("\n" + "="*60)
    print("🧪 Testing Auto Provider Selection")
    print("="*60)

    config = Config()
    provider = ProviderFactory.from_config(config)

    async with provider:
        print(f"\n✓ Auto-selected: {provider.provider_name}")

        quote = await provider.get_quote("NVDA")
        print(f"\nNVDA Quote: ${quote.price:.2f}")
        print(f"Provider used: {quote.provider}")

        print("\n✅ Auto selection test completed!")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 AI Stock Research - Provider Test Suite")
    print("="*60)

    # Determine which tests to run
    test_mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if test_mode == "yfinance":
        await test_yfinance_provider()
    elif test_mode == "polygon":
        await test_polygon_provider()
    elif test_mode == "hybrid":
        await test_hybrid_provider()
    elif test_mode == "auto":
        await test_auto_selection()
    else:
        # Run all tests
        await test_yfinance_provider()
        await test_polygon_provider()
        await test_hybrid_provider()
        await test_auto_selection()

    print("\n" + "="*60)
    print("✅ All provider tests completed!")
    print("="*60)


if __name__ == "__main__":
    print("\nUsage:")
    print("  python3 test_providers.py           # Run all tests")
    print("  python3 test_providers.py yfinance  # Test YFinance only")
    print("  python3 test_providers.py polygon   # Test Polygon only")
    print("  python3 test_providers.py hybrid    # Test Hybrid provider")
    print("  python3 test_providers.py auto      # Test auto-selection")
    print()

    asyncio.run(main())
