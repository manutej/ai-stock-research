#!/usr/bin/env python3
"""
FinWiz - AI Stock Research Command Line Tool

A simple, safe command-line interface for researching AI sector stocks.
Uses free YFinance data by default, with optional Polygon integration.

Usage:
    finwiz quote NVDA
    finwiz quotes NVDA MSFT GOOGL
    finwiz news NVDA
    finwiz financials GOOGL
    finwiz history MSFT --days 30
    finwiz watchlist
    finwiz morning-brief
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
  finwiz quote NVDA
  finwiz quotes NVDA MSFT GOOGL
  finwiz news NVDA
  finwiz financials GOOGL
  finwiz history MSFT --days 30
  finwiz watchlist
  finwiz morning-brief
  finwiz compare NVDA AMD INTC
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Quote command
    quote_parser = subparsers.add_parser('quote', help='Get quote for a single stock')
    quote_parser.add_argument('ticker', help='Stock ticker symbol')

    # Quotes command
    quotes_parser = subparsers.add_parser('quotes', help='Get quotes for multiple stocks')
    quotes_parser.add_argument('tickers', nargs='+', help='Stock ticker symbols')

    # News command
    news_parser = subparsers.add_parser('news', help='Get recent news')
    news_parser.add_argument('ticker', nargs='?', help='Stock ticker symbol (optional)')
    news_parser.add_argument('--limit', type=int, default=5, help='Number of articles')

    # Financials command
    fin_parser = subparsers.add_parser('financials', help='Get financial statements')
    fin_parser.add_argument('ticker', help='Stock ticker symbol')
    fin_parser.add_argument('--periods', type=int, default=4, help='Number of periods')

    # History command
    hist_parser = subparsers.add_parser('history', help='Get price history')
    hist_parser.add_argument('ticker', help='Stock ticker symbol')
    hist_parser.add_argument('--days', type=int, default=30, help='Number of days')

    # Watchlist command
    subparsers.add_parser('watchlist', help='Show AI stock watchlist')

    # Morning brief command
    subparsers.add_parser('morning-brief', help='Generate morning brief')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare multiple stocks')
    compare_parser.add_argument('tickers', nargs='+', help='Stock ticker symbols')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Run command
    async with FinWiz() as finwiz:
        if args.command == 'quote':
            await finwiz.cmd_quote(args.ticker.upper())
        elif args.command == 'quotes':
            await finwiz.cmd_quotes([t.upper() for t in args.tickers])
        elif args.command == 'news':
            ticker = args.ticker.upper() if args.ticker else None
            await finwiz.cmd_news(ticker, args.limit)
        elif args.command == 'financials':
            await finwiz.cmd_financials(args.ticker.upper(), args.periods)
        elif args.command == 'history':
            await finwiz.cmd_history(args.ticker.upper(), args.days)
        elif args.command == 'watchlist':
            await finwiz.cmd_watchlist()
        elif args.command == 'morning-brief':
            await finwiz.cmd_morning_brief()
        elif args.command == 'compare':
            await finwiz.cmd_compare([t.upper() for t in args.tickers])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
