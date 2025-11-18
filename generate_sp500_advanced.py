#!/usr/bin/env python3
"""
Advanced S&P 500 Stock Analysis & CSV Generator

This script acts as a financial analyst, fetching comprehensive fundamental
and market data for S&P 500 companies. It can filter by sector/domain and
generates CSV reports with:
- Real-time market data (price, volume, changes)
- Fundamental metrics (revenue, earnings, growth)
- Valuation ratios (P/E, P/B, P/S)
- Profitability metrics (margins, ROE, ROA)
- Growth metrics (revenue growth, earnings growth)

Usage:
    python generate_sp500_advanced.py                    # All companies
    python generate_sp500_advanced.py --sector Technology # Filter by sector
    python generate_sp500_advanced.py --limit 20          # Limit to 20 companies
"""
import asyncio
import csv
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# Workaround for yfinance multitasking issue
import sys
from unittest.mock import MagicMock
sys.modules['multitasking'] = MagicMock()

import yfinance as yf

from config import Config
from providers.factory import ProviderFactory


# Comprehensive S&P 500 company database with sectors
SP500_COMPANIES = [
    # Technology Sector
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "GOOGL", "name": "Alphabet Inc. Class A", "sector": "Technology", "industry": "Internet"},
    {"ticker": "META", "name": "Meta Platforms Inc.", "sector": "Technology", "industry": "Social Media"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Technology", "industry": "E-commerce"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Technology", "industry": "Electric Vehicles"},
    {"ticker": "AVGO", "name": "Broadcom Inc.", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "ORCL", "name": "Oracle Corporation", "sector": "Technology", "industry": "Software"},
    {"ticker": "ADBE", "name": "Adobe Inc.", "sector": "Technology", "industry": "Software"},
    {"ticker": "CRM", "name": "Salesforce Inc.", "sector": "Technology", "industry": "Software"},
    {"ticker": "CSCO", "name": "Cisco Systems Inc.", "sector": "Technology", "industry": "Networking"},
    {"ticker": "INTC", "name": "Intel Corporation", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "QCOM", "name": "Qualcomm Inc.", "sector": "Technology", "industry": "Semiconductors"},

    # Financial Services
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials", "industry": "Banking"},
    {"ticker": "BAC", "name": "Bank of America Corp.", "sector": "Financials", "industry": "Banking"},
    {"ticker": "WFC", "name": "Wells Fargo & Company", "sector": "Financials", "industry": "Banking"},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc.", "sector": "Financials", "industry": "Investment Banking"},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Financials", "industry": "Investment Banking"},
    {"ticker": "BLK", "name": "BlackRock Inc.", "sector": "Financials", "industry": "Asset Management"},
    {"ticker": "C", "name": "Citigroup Inc.", "sector": "Financials", "industry": "Banking"},
    {"ticker": "SCHW", "name": "Charles Schwab Corp.", "sector": "Financials", "industry": "Brokerage"},

    # Healthcare
    {"ticker": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare", "industry": "Health Insurance"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"ticker": "LLY", "name": "Eli Lilly and Company", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"ticker": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"ticker": "MRK", "name": "Merck & Co. Inc.", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific", "sector": "Healthcare", "industry": "Life Sciences"},
    {"ticker": "ABT", "name": "Abbott Laboratories", "sector": "Healthcare", "industry": "Medical Devices"},

    # Consumer Discretionary
    {"ticker": "HD", "name": "Home Depot Inc.", "sector": "Consumer Discretionary", "industry": "Home Improvement"},
    {"ticker": "MCD", "name": "McDonald's Corporation", "sector": "Consumer Discretionary", "industry": "Restaurants"},
    {"ticker": "NKE", "name": "Nike Inc.", "sector": "Consumer Discretionary", "industry": "Apparel"},
    {"ticker": "SBUX", "name": "Starbucks Corporation", "sector": "Consumer Discretionary", "industry": "Restaurants"},
    {"ticker": "TGT", "name": "Target Corporation", "sector": "Consumer Discretionary", "industry": "Retail"},

    # Consumer Staples
    {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples", "industry": "Retail"},
    {"ticker": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Staples", "industry": "Consumer Products"},
    {"ticker": "KO", "name": "Coca-Cola Company", "sector": "Consumer Staples", "industry": "Beverages"},
    {"ticker": "PEP", "name": "PepsiCo Inc.", "sector": "Consumer Staples", "industry": "Beverages"},
    {"ticker": "COST", "name": "Costco Wholesale Corp.", "sector": "Consumer Staples", "industry": "Retail"},

    # Energy
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Oil & Gas"},
    {"ticker": "CVX", "name": "Chevron Corporation", "sector": "Energy", "industry": "Oil & Gas"},
    {"ticker": "COP", "name": "ConocoPhillips", "sector": "Energy", "industry": "Oil & Gas"},
    {"ticker": "SLB", "name": "Schlumberger NV", "sector": "Energy", "industry": "Oilfield Services"},

    # Industrials
    {"ticker": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials", "industry": "Machinery"},
    {"ticker": "BA", "name": "Boeing Company", "sector": "Industrials", "industry": "Aerospace"},
    {"ticker": "UPS", "name": "United Parcel Service Inc.", "sector": "Industrials", "industry": "Logistics"},
    {"ticker": "HON", "name": "Honeywell International", "sector": "Industrials", "industry": "Conglomerate"},
    {"ticker": "RTX", "name": "RTX Corporation", "sector": "Industrials", "industry": "Aerospace"},

    # Communication Services
    {"ticker": "VZ", "name": "Verizon Communications", "sector": "Communication Services", "industry": "Telecom"},
    {"ticker": "T", "name": "AT&T Inc.", "sector": "Communication Services", "industry": "Telecom"},
    {"ticker": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services", "industry": "Streaming"},
    {"ticker": "DIS", "name": "Walt Disney Company", "sector": "Communication Services", "industry": "Entertainment"},

    # Utilities
    {"ticker": "NEE", "name": "NextEra Energy Inc.", "sector": "Utilities", "industry": "Electric Utilities"},
    {"ticker": "DUK", "name": "Duke Energy Corporation", "sector": "Utilities", "industry": "Electric Utilities"},
    {"ticker": "SO", "name": "Southern Company", "sector": "Utilities", "industry": "Electric Utilities"},

    # Real Estate
    {"ticker": "PLD", "name": "Prologis Inc.", "sector": "Real Estate", "industry": "Industrial REIT"},
    {"ticker": "AMT", "name": "American Tower Corp.", "sector": "Real Estate", "industry": "Infrastructure REIT"},
]


def get_fundamental_data(ticker: str) -> Dict:
    """
    Fetch comprehensive fundamental data using yfinance.

    Returns dict with key financial metrics:
    - Revenue, earnings, growth rates
    - Valuation ratios (P/E, P/B, P/S)
    - Profitability metrics (margins, ROE, ROA)
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            # Valuation Metrics
            "marketCap": info.get("marketCap"),
            "enterpriseValue": info.get("enterpriseValue"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "priceToBook": info.get("priceToBook"),
            "priceToSales": info.get("priceToSalesTrailing12Months"),
            "pegRatio": info.get("pegRatio"),

            # Financial Metrics
            "revenue": info.get("totalRevenue"),
            "revenuePerShare": info.get("revenuePerShare"),
            "revenueGrowth": info.get("revenueGrowth"),
            "earningsGrowth": info.get("earningsGrowth"),
            "earningsQuarterlyGrowth": info.get("earningsQuarterlyGrowth"),

            # Profitability
            "profitMargin": info.get("profitMargins"),
            "operatingMargin": info.get("operatingMargins"),
            "grossMargin": info.get("grossMargins"),
            "ebitdaMargins": info.get("ebitdaMargins"),
            "returnOnEquity": info.get("returnOnEquity"),
            "returnOnAssets": info.get("returnOnAssets"),

            # Per Share Metrics
            "eps": info.get("trailingEps"),
            "forwardEps": info.get("forwardEps"),
            "bookValue": info.get("bookValue"),
            "cashPerShare": info.get("totalCashPerShare"),

            # Dividends
            "dividendYield": info.get("dividendYield"),
            "payoutRatio": info.get("payoutRatio"),

            # Other
            "beta": info.get("beta"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "targetMeanPrice": info.get("targetMeanPrice"),
            "recommendationKey": info.get("recommendationKey"),
        }
    except Exception as e:
        print(f"  ⚠️  Error fetching fundamentals for {ticker}: {e}")
        return {}


def format_value(value, format_type="number", decimals=2):
    """Format values for CSV output"""
    if value is None or (isinstance(value, float) and (value != value)):  # Check for None or NaN
        return "N/A"

    try:
        if format_type == "currency":
            return f"${value:,.{decimals}f}"
        elif format_type == "billions":
            return f"${value/1e9:,.{decimals}f}B"
        elif format_type == "millions":
            return f"${value/1e6:,.{decimals}f}M"
        elif format_type == "percentage":
            return f"{value*100:.{decimals}f}%"
        elif format_type == "number":
            return f"{value:,.{decimals}f}"
        else:
            return str(value)
    except:
        return "N/A"


async def generate_advanced_csv(
    output_file: str = "sp500_advanced_analysis.csv",
    sector: Optional[str] = None,
    limit: Optional[int] = None,
):
    """
    Generate comprehensive CSV with market data and fundamentals.

    Args:
        output_file: Output CSV filename
        sector: Filter by sector (e.g., "Technology", "Healthcare")
        limit: Maximum number of companies to analyze
    """
    print(f"📊 Advanced S&P 500 Financial Analysis")
    print("=" * 80)

    # Filter companies
    companies = SP500_COMPANIES
    if sector:
        companies = [c for c in companies if c["sector"].lower() == sector.lower()]
        print(f"📌 Filtering by sector: {sector}")

    if limit:
        companies = companies[:limit]

    print(f"📈 Analyzing {len(companies)} companies...\n")

    # Initialize provider for market data
    config = Config()
    provider = ProviderFactory.from_config(config)

    async with provider:
        # Fetch market quotes
        tickers = [c["ticker"] for c in companies]
        print(f"🔄 Fetching real-time market data...")

        all_quotes = {}
        batch_size = 10
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            try:
                quotes = await provider.get_quotes(batch)
                all_quotes.update(quotes)
                print(f"  ✓ Batch {i//batch_size + 1}/{(len(tickers)-1)//batch_size + 1} complete")
                if i + batch_size < len(tickers):
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"  ⚠️  Warning: {e}")

        print(f"\n🔄 Fetching fundamental data...")

        # Prepare CSV data
        csv_rows = []
        for idx, company in enumerate(companies, 1):
            ticker = company["ticker"]
            print(f"  [{idx}/{len(companies)}] Analyzing {ticker}...")

            # Get market data
            quote = all_quotes.get(ticker)

            # Get fundamental data
            fundamentals = get_fundamental_data(ticker)

            # Compile row
            row = {
                # Company Info
                "Ticker": ticker,
                "Company Name": company["name"],
                "Sector": company["sector"],
                "Industry": company["industry"],

                # Market Data
                "Price": format_value(quote.price, "currency") if quote else "N/A",
                "Change": format_value(quote.change, "currency") if quote else "N/A",
                "Change %": format_value(quote.change_percent/100, "percentage") if quote else "N/A",
                "Volume": f"{quote.volume:,}" if quote and quote.volume else "N/A",

                # Valuation
                "Market Cap": format_value(fundamentals.get("marketCap"), "billions"),
                "Enterprise Value": format_value(fundamentals.get("enterpriseValue"), "billions"),
                "P/E Ratio": format_value(fundamentals.get("trailingPE"), "number"),
                "Forward P/E": format_value(fundamentals.get("forwardPE"), "number"),
                "P/B Ratio": format_value(fundamentals.get("priceToBook"), "number"),
                "P/S Ratio": format_value(fundamentals.get("priceToSales"), "number"),
                "PEG Ratio": format_value(fundamentals.get("pegRatio"), "number"),

                # Growth
                "Revenue": format_value(fundamentals.get("revenue"), "billions"),
                "Revenue Growth": format_value(fundamentals.get("revenueGrowth"), "percentage"),
                "Earnings Growth": format_value(fundamentals.get("earningsGrowth"), "percentage"),
                "Quarterly Earnings Growth": format_value(fundamentals.get("earningsQuarterlyGrowth"), "percentage"),

                # Profitability
                "Profit Margin": format_value(fundamentals.get("profitMargin"), "percentage"),
                "Operating Margin": format_value(fundamentals.get("operatingMargin"), "percentage"),
                "Gross Margin": format_value(fundamentals.get("grossMargin"), "percentage"),
                "ROE": format_value(fundamentals.get("returnOnEquity"), "percentage"),
                "ROA": format_value(fundamentals.get("returnOnAssets"), "percentage"),

                # Per Share
                "EPS": format_value(fundamentals.get("eps"), "currency"),
                "Forward EPS": format_value(fundamentals.get("forwardEps"), "currency"),
                "Book Value": format_value(fundamentals.get("bookValue"), "currency"),

                # Dividends
                "Dividend Yield": format_value(fundamentals.get("dividendYield"), "percentage"),
                "Payout Ratio": format_value(fundamentals.get("payoutRatio"), "percentage"),

                # Risk & Targets
                "Beta": format_value(fundamentals.get("beta"), "number"),
                "52-Week High": format_value(fundamentals.get("fiftyTwoWeekHigh"), "currency"),
                "52-Week Low": format_value(fundamentals.get("fiftyTwoWeekLow"), "currency"),
                "Analyst Target": format_value(fundamentals.get("targetMeanPrice"), "currency"),
                "Recommendation": fundamentals.get("recommendationKey", "N/A").upper() if fundamentals.get("recommendationKey") else "N/A",

                # Metadata
                "Data Timestamp": quote.timestamp.strftime('%Y-%m-%d %H:%M:%S') if quote else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

            csv_rows.append(row)

            # Small delay to avoid overwhelming APIs
            await asyncio.sleep(0.5)

        # Write to CSV
        fieldnames = list(csv_rows[0].keys()) if csv_rows else []

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

        print(f"\n{'='*80}")
        print(f"✅ Analysis complete!")
        print(f"📄 CSV file: {output_file}")
        print(f"📊 Companies analyzed: {len(csv_rows)}")
        print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Show top 5 by market cap
        if csv_rows:
            print(f"\n📈 Top 5 Companies by Market Cap:")
            print("-" * 80)
            print(f"{'Ticker':<8} {'Company':<35} {'Market Cap':<15} {'P/E':<10}")
            print("-" * 80)
            for row in csv_rows[:5]:
                print(
                    f"{row['Ticker']:<8} "
                    f"{row['Company Name'][:33]:<35} "
                    f"{row['Market Cap']:<15} "
                    f"{row['P/E Ratio']:<10}"
                )
        print()


async def main():
    """Main entry point with CLI arguments"""
    parser = argparse.ArgumentParser(
        description="Advanced S&P 500 Financial Analysis & CSV Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_sp500_advanced.py
  python generate_sp500_advanced.py --sector Technology
  python generate_sp500_advanced.py --sector Healthcare --limit 10
  python generate_sp500_advanced.py --output my_analysis.csv

Available Sectors:
  Technology, Financials, Healthcare, Consumer Discretionary,
  Consumer Staples, Energy, Industrials, Communication Services,
  Utilities, Real Estate
        """
    )

    parser.add_argument(
        '--sector', '-s',
        type=str,
        help='Filter by sector (e.g., Technology, Healthcare)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Maximum number of companies to analyze'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='sp500_advanced_analysis.csv',
        help='Output CSV filename (default: sp500_advanced_analysis.csv)'
    )

    args = parser.parse_args()

    try:
        await generate_advanced_csv(
            output_file=args.output,
            sector=args.sector,
            limit=args.limit
        )
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
