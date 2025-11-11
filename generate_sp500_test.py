#!/usr/bin/env python3
"""
Generate a test CSV with real S&P 500 companies and live data.

This script fetches real-time quotes for a diverse selection of S&P 500 companies
across different sectors and exports them to a CSV file.
"""
import asyncio
import csv
from datetime import datetime
from typing import List, Dict

from config import Config
from providers.factory import ProviderFactory


# Selection of real S&P 500 companies across different sectors
SP500_TEST_COMPANIES = [
    # Technology
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
    {"ticker": "GOOGL", "name": "Alphabet Inc. Class A", "sector": "Technology"},
    {"ticker": "META", "name": "Meta Platforms Inc.", "sector": "Technology"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Technology"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Technology"},
    {"ticker": "AVGO", "name": "Broadcom Inc.", "sector": "Technology"},
    {"ticker": "ORCL", "name": "Oracle Corporation", "sector": "Technology"},
    {"ticker": "ADBE", "name": "Adobe Inc.", "sector": "Technology"},

    # Financial Services
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials"},
    {"ticker": "BAC", "name": "Bank of America Corp.", "sector": "Financials"},
    {"ticker": "WFC", "name": "Wells Fargo & Company", "sector": "Financials"},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc.", "sector": "Financials"},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Financials"},

    # Healthcare
    {"ticker": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
    {"ticker": "LLY", "name": "Eli Lilly and Company", "sector": "Healthcare"},
    {"ticker": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare"},
    {"ticker": "MRK", "name": "Merck & Co. Inc.", "sector": "Healthcare"},

    # Consumer
    {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples"},
    {"ticker": "HD", "name": "Home Depot Inc.", "sector": "Consumer Discretionary"},
    {"ticker": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Staples"},
    {"ticker": "KO", "name": "Coca-Cola Company", "sector": "Consumer Staples"},
    {"ticker": "MCD", "name": "McDonald's Corporation", "sector": "Consumer Discretionary"},

    # Energy
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy"},
    {"ticker": "CVX", "name": "Chevron Corporation", "sector": "Energy"},

    # Industrials
    {"ticker": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials"},
    {"ticker": "BA", "name": "Boeing Company", "sector": "Industrials"},
    {"ticker": "UPS", "name": "United Parcel Service Inc.", "sector": "Industrials"},
]


async def generate_sp500_csv(output_file: str = "sp500_test_data.csv"):
    """
    Generate a CSV file with live data for S&P 500 companies.

    Args:
        output_file: Name of the output CSV file
    """
    print(f"📊 Generating S&P 500 Test Data CSV")
    print("=" * 70)
    print(f"\nFetching live data for {len(SP500_TEST_COMPANIES)} companies...")

    # Initialize provider
    config = Config()
    provider = ProviderFactory.from_config(config)

    async with provider:
        # Extract tickers
        tickers = [company["ticker"] for company in SP500_TEST_COMPANIES]

        # Fetch quotes in batches to respect rate limits
        batch_size = 10
        all_quotes = {}

        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            print(f"  Fetching batch {i//batch_size + 1}/{(len(tickers)-1)//batch_size + 1}...")

            try:
                quotes = await provider.get_quotes(batch)
                all_quotes.update(quotes)

                # Small delay to respect rate limits
                if i + batch_size < len(tickers):
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"  ⚠️  Warning: Error fetching batch: {e}")
                continue

        print(f"\n✅ Successfully fetched data for {len(all_quotes)} companies")

        # Prepare CSV data
        csv_rows = []
        for company in SP500_TEST_COMPANIES:
            ticker = company["ticker"]

            if ticker in all_quotes:
                quote = all_quotes[ticker]
                row = {
                    "Ticker": ticker,
                    "Company Name": company["name"],
                    "Sector": company["sector"],
                    "Price": f"{quote.price:.2f}",
                    "Change": f"{quote.change:+.2f}",
                    "Change %": f"{quote.change_percent:+.2f}",
                    "Open": f"{quote.open:.2f}" if quote.open else "N/A",
                    "High": f"{quote.high:.2f}" if quote.high else "N/A",
                    "Low": f"{quote.low:.2f}" if quote.low else "N/A",
                    "Volume": f"{quote.volume:,}" if quote.volume else "N/A",
                    "Provider": quote.provider,
                    "Timestamp": quote.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                }
            else:
                # Company data not available
                row = {
                    "Ticker": ticker,
                    "Company Name": company["name"],
                    "Sector": company["sector"],
                    "Price": "N/A",
                    "Change": "N/A",
                    "Change %": "N/A",
                    "Open": "N/A",
                    "High": "N/A",
                    "Low": "N/A",
                    "Volume": "N/A",
                    "Provider": "N/A",
                    "Timestamp": "N/A",
                }

            csv_rows.append(row)

        # Write to CSV
        fieldnames = [
            "Ticker", "Company Name", "Sector", "Price", "Change", "Change %",
            "Open", "High", "Low", "Volume", "Provider", "Timestamp"
        ]

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

        print(f"\n✅ CSV file generated: {output_file}")
        print(f"   Total companies: {len(csv_rows)}")
        print(f"   Companies with data: {len(all_quotes)}")
        print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Show sample data
        print(f"\n📈 Sample Data (first 5 companies):")
        print("-" * 70)
        print(f"{'Ticker':<8} {'Price':<10} {'Change':<10} {'Change %':<10} {'Sector':<20}")
        print("-" * 70)

        for row in csv_rows[:5]:
            print(
                f"{row['Ticker']:<8} "
                f"{row['Price']:<10} "
                f"{row['Change']:<10} "
                f"{row['Change %']:<10} "
                f"{row['Sector']:<20}"
            )
        print()


async def main():
    """Main entry point"""
    try:
        await generate_sp500_csv()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
