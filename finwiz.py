#!/usr/bin/env python3
"""
FinWiz - AI Stock Research Command Line Tool

A simple, safe command-line interface for researching AI sector stocks.
Uses free YFinance data by default, with optional Polygon integration.

Usage:
    # Quick quote (default)
    finwiz NVDA

    # Multiple quotes
    finwiz -r NVDA MSFT GOOGL
    finwiz --quotes NVDA MSFT GOOGL

    # News
    finwiz -n NVDA
    finwiz --news NVDA --limit 10

    # Financials
    finwiz -f GOOGL
    finwiz --financials GOOGL

    # History
    finwiz -H MSFT
    finwiz --history MSFT --days 90

    # Compare
    finwiz -c NVDA AMD INTC
    finwiz --compare NVDA AMD INTC

    # Watchlist & Brief
    finwiz -w
    finwiz --watchlist
    finwiz -b
    finwiz --morning-brief
"""
import asyncio
import sys
import argparse
from datetime import datetime, timedelta
from typing import List, Optional

from config import Config
from providers.factory import ProviderFactory, ProviderStrategy


class FinWiz:
    """Main CLI application"""

    def __init__(self):
        self.config = Config()
        self.provider = None

    async def __aenter__(self):
        """Initialize provider connection"""
        self.provider = ProviderFactory.from_config(self.config)
        await self.provider.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up provider connection"""
        if self.provider:
            await self.provider.disconnect()

    def format_quote(self, quote) -> str:
        """Format a single quote for display"""
        change_color = "+" if quote.change >= 0 else ""
        return (
            f"{quote.ticker:6s} "
            f"${quote.price:8.2f} "
            f"{change_color}{quote.change:+7.2f} "
            f"({change_color}{quote.change_percent:+6.2f}%) "
            f"Vol: {quote.volume:,}" if quote.volume else ""
        )

    async def cmd_quote(self, ticker: str):
        """Get quote for a single ticker"""
        print(f"\n📊 Quote for {ticker}")
        print("=" * 60)

        quote = await self.provider.get_quote(ticker)

        print(f"\nPrice:     ${quote.price:.2f}")
        print(f"Change:    {quote.change:+.2f} ({quote.change_percent:+.2f}%)")
        if quote.open:
            print(f"Open:      ${quote.open:.2f}")
        if quote.high:
            print(f"High:      ${quote.high:.2f}")
        if quote.low:
            print(f"Low:       ${quote.low:.2f}")
        if quote.volume:
            print(f"Volume:    {quote.volume:,}")
        print(f"Provider:  {quote.provider}")
        print(f"Updated:   {quote.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    async def cmd_quotes(self, tickers: List[str]):
        """Get quotes for multiple tickers"""
        print(f"\n📊 Quotes for {len(tickers)} stocks")
        print("=" * 60)

        quotes = await self.provider.get_quotes(tickers)

        print("\nTicker  Price      Change    Change%   Volume")
        print("-" * 60)
        for ticker, quote in quotes.items():
            print(self.format_quote(quote))
        print()

    async def cmd_news(self, ticker: Optional[str] = None, limit: int = 5):
        """Get recent news articles"""
        if ticker:
            print(f"\n📰 Latest news for {ticker}")
        else:
            print("\n📰 Latest market news")
        print("=" * 60)

        articles = await self.provider.get_news(ticker, limit)

        if not articles:
            print("\nNo news articles found.")
            return

        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article.title}")
            print(f"   Source: {article.source or 'Unknown'}")
            print(f"   Date: {article.published_at.strftime('%Y-%m-%d %H:%M')}")
            if article.description:
                # Truncate description to 100 chars
                desc = article.description[:100] + "..." if len(article.description) > 100 else article.description
                print(f"   {desc}")
            print(f"   URL: {article.url}")
        print()

    async def cmd_financials(self, ticker: str, periods: int = 4):
        """Get financial statements"""
        print(f"\n💼 Financial data for {ticker}")
        print("=" * 60)

        financials = await self.provider.get_financials(ticker, periods)

        if not financials:
            print("\nNo financial data found.")
            return

        for i, fin in enumerate(financials, 1):
            print(f"\n{i}. {fin.fiscal_period} {fin.fiscal_year}")
            print(f"   Period: {fin.period_start.date()} to {fin.period_end.date()}")

            if fin.revenue:
                print(f"   Revenue:      ${fin.revenue/1e9:.2f}B")
            if fin.net_income:
                print(f"   Net Income:   ${fin.net_income/1e9:.2f}B")
            if fin.earnings_per_share:
                print(f"   EPS:          ${fin.earnings_per_share:.2f}")
            if fin.total_assets:
                print(f"   Total Assets: ${fin.total_assets/1e9:.2f}B")
        print()

    async def cmd_history(self, ticker: str, days: int = 30):
        """Get historical price data"""
        print(f"\n📈 Price history for {ticker} (last {days} days)")
        print("=" * 60)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        bars = await self.provider.get_historical(ticker, start_date, end_date, "1d")

        if not bars:
            print("\nNo historical data found.")
            return

        print("\nDate       Open     High     Low      Close    Volume")
        print("-" * 60)
        for bar in bars[-10:]:  # Show last 10 days
            print(
                f"{bar.timestamp.strftime('%Y-%m-%d')} "
                f"${bar.open:7.2f} "
                f"${bar.high:7.2f} "
                f"${bar.low:7.2f} "
                f"${bar.close:7.2f} "
                f"{bar.volume:,}"
            )

        # Calculate simple statistics
        prices = [bar.close for bar in bars]
        avg_price = sum(prices) / len(prices)
        high_price = max(prices)
        low_price = min(prices)
        current_price = prices[-1]
        change = current_price - prices[0]
        change_pct = (change / prices[0]) * 100

        print(f"\nStatistics ({days} days):")
        print(f"  Average:  ${avg_price:.2f}")
        print(f"  High:     ${high_price:.2f}")
        print(f"  Low:      ${low_price:.2f}")
        print(f"  Change:   ${change:+.2f} ({change_pct:+.2f}%)")
        print()

    async def cmd_watchlist(self):
        """Display AI stock watchlist with current prices"""
        print("\n🎯 AI Stock Watchlist")
        print("=" * 60)

        # Get large cap AI leaders
        large_cap = self.config.load_watchlist("ai_large_cap")
        startups = self.config.load_watchlist("ai_startups")

        print("\n📊 Large Cap AI Leaders:")
        print("-" * 60)
        tickers = [c["ticker"] for c in large_cap["companies"][:5]]
        quotes = await self.provider.get_quotes(tickers)

        print("Ticker  Price      Change    Change%   Volume")
        print("-" * 60)
        for ticker in tickers:
            if ticker in quotes:
                print(self.format_quote(quotes[ticker]))

        print("\n\n🚀 AI Startups & High Growth:")
        print("-" * 60)
        tickers = [c["ticker"] for c in startups["companies"][:5]]
        quotes = await self.provider.get_quotes(tickers)

        print("Ticker  Price      Change    Change%   Volume")
        print("-" * 60)
        for ticker in tickers:
            if ticker in quotes:
                print(self.format_quote(quotes[ticker]))

        print()

    async def cmd_morning_brief(self):
        """Generate AI sector morning brief"""
        print("\n☀️  AI Sector Morning Brief")
        print("=" * 60)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # Get market status
        status = await self.provider.get_market_status()
        market_status = "OPEN" if status.is_open else "CLOSED"
        print(f"Market Status: {market_status}")

        # Get quotes for major AI stocks
        tickers = ["NVDA", "MSFT", "GOOGL", "META", "AMZN"]
        print(f"\n📊 Major AI Stocks:")
        print("-" * 60)

        quotes = await self.provider.get_quotes(tickers)

        print("Ticker  Price      Change    Change%")
        print("-" * 60)
        for ticker in tickers:
            if ticker in quotes:
                quote = quotes[ticker]
                change_color = "+" if quote.change >= 0 else ""
                print(
                    f"{quote.ticker:6s} "
                    f"${quote.price:8.2f} "
                    f"{change_color}{quote.change:+7.2f} "
                    f"({change_color}{quote.change_percent:+6.2f}%)"
                )

        # Get latest news
        print(f"\n📰 Latest AI News:")
        print("-" * 60)
        news = await self.provider.get_news("NVDA", limit=3)
        for i, article in enumerate(news[:3], 1):
            print(f"{i}. {article.title[:70]}...")

        print("\n" + "=" * 60)
        print(f"Powered by {self.provider.provider_name}")
        print()

    async def cmd_compare(self, tickers: List[str]):
        """Compare multiple stocks side by side"""
        print(f"\n📊 Comparing {len(tickers)} stocks")
        print("=" * 60)

        quotes = await self.provider.get_quotes(tickers)

        # Display comparison table
        print("\nMetric        " + "".join(f"{t:>12s}" for t in tickers))
        print("-" * 60)

        # Current Price
        print("Price         ", end="")
        for ticker in tickers:
            if ticker in quotes:
                print(f"${quotes[ticker].price:>11.2f}", end="")
        print()

        # Change %
        print("Change %      ", end="")
        for ticker in tickers:
            if ticker in quotes:
                print(f"{quotes[ticker].change_percent:>11.2f}%", end="")
        print()

        # Volume
        print("Volume        ", end="")
        for ticker in tickers:
            if ticker in quotes and quotes[ticker].volume:
                vol_m = quotes[ticker].volume / 1e6
                print(f"{vol_m:>10.1f}M", end="")
        print()

        print()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="FinWiz - AI Stock Research Command Line Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  finwiz NVDA                    # Quick quote (default)
  finwiz -r NVDA MSFT GOOGL      # Multiple quotes
  finwiz -n NVDA                 # Latest news
  finwiz -f GOOGL                # Financial statements
  finwiz -H MSFT --days 90       # Price history
  finwiz -c NVDA AMD INTC        # Compare stocks
  finwiz -w                      # Show watchlist
  finwiz -b                      # Morning brief

Operation Flags:
  -r, --quotes          Get quotes for multiple stocks
  -n, --news            Get recent news articles
  -f, --financials      Get financial statements
  -H, --history         Get price history
  -c, --compare         Compare multiple stocks
  -w, --watchlist       Show AI stock watchlist
  -b, --morning-brief   Generate morning brief

Options:
  --limit N             Number of news articles (default: 5)
  --periods N           Number of financial periods (default: 4)
  --days N              Number of days for history (default: 30)

Notes:
  - Without flags, defaults to single stock quote
  - All tickers are automatically uppercased
  - Uses free YFinance data by default (no API key needed!)
        """
    )

    # Operation flags (mutually exclusive)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--quotes', action='store_true',
                      help='Get quotes for multiple stocks')
    group.add_argument('-n', '--news', action='store_true',
                      help='Get recent news articles')
    group.add_argument('-f', '--financials', action='store_true',
                      help='Get financial statements')
    group.add_argument('-H', '--history', action='store_true',
                      help='Get price history')
    group.add_argument('-c', '--compare', action='store_true',
                      help='Compare multiple stocks')
    group.add_argument('-w', '--watchlist', action='store_true',
                      help='Show AI stock watchlist')
    group.add_argument('-b', '--morning-brief', action='store_true',
                      help='Generate morning brief')

    # Positional arguments (tickers)
    parser.add_argument('tickers', nargs='*',
                       help='Stock ticker symbols (e.g., NVDA MSFT GOOGL)')

    # Optional parameters
    parser.add_argument('--limit', type=int, default=5,
                       help='Number of news articles (default: 5)')
    parser.add_argument('--periods', type=int, default=4,
                       help='Number of financial periods (default: 4)')
    parser.add_argument('--days', type=int, default=30,
                       help='Number of days for history (default: 30)')

    args = parser.parse_args()

    # Determine operation
    if args.watchlist:
        # Watchlist - no tickers needed
        async with FinWiz() as finwiz:
            await finwiz.cmd_watchlist()

    elif args.morning_brief:
        # Morning brief - no tickers needed
        async with FinWiz() as finwiz:
            await finwiz.cmd_morning_brief()

    elif not args.tickers:
        # No tickers provided
        parser.print_help()
        return

    else:
        # Operations requiring tickers
        tickers = [t.upper() for t in args.tickers]

        async with FinWiz() as finwiz:
            if args.quotes:
                # Multiple quotes
                await finwiz.cmd_quotes(tickers)

            elif args.news:
                # News for first ticker (or all if no ticker)
                ticker = tickers[0] if tickers else None
                await finwiz.cmd_news(ticker, args.limit)

            elif args.financials:
                # Financials for first ticker
                if not tickers:
                    print("Error: Please specify a ticker symbol")
                    return
                await finwiz.cmd_financials(tickers[0], args.periods)

            elif args.history:
                # History for first ticker
                if not tickers:
                    print("Error: Please specify a ticker symbol")
                    return
                await finwiz.cmd_history(tickers[0], args.days)

            elif args.compare:
                # Compare multiple tickers
                if len(tickers) < 2:
                    print("Error: Please specify at least 2 tickers to compare")
                    return
                await finwiz.cmd_compare(tickers)

            else:
                # Default: single quote
                if len(tickers) > 1:
                    # Multiple tickers without -r flag? Show quotes
                    await finwiz.cmd_quotes(tickers)
                else:
                    # Single ticker - detailed quote
                    await finwiz.cmd_quote(tickers[0])


def main_sync():
    """Synchronous wrapper for console script entry point"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_sync()
