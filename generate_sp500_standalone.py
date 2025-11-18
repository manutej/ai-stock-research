#!/usr/bin/env python3
"""
Standalone S&P 500 Stock Analysis & CSV Generator

Direct implementation using yfinance with robust error handling and rate limiting.
Generates comprehensive financial data including fundamentals, market data, and growth metrics.

Usage:
    python generate_sp500_standalone.py                    # All companies
    python generate_sp500_standalone.py --sector Technology # Filter by sector
    python generate_sp500_standalone.py --limit 15          # Limit to 15 companies
"""
import csv
import argparse
import time
from datetime import datetime
from typing import List, Dict, Optional
import sys
from unittest.mock import MagicMock

# Workaround for multitasking issue
sys.modules['multitasking'] = MagicMock()

import yfinance as yf


# S&P 500 Companies Database
SP500_COMPANIES = [
    # Technology
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
    {"ticker": "META", "name": "Meta Platforms Inc.", "sector": "Technology"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Technology"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Technology"},
    {"ticker": "AVGO", "name": "Broadcom Inc.", "sector": "Technology"},
    {"ticker": "ORCL", "name": "Oracle Corporation", "sector": "Technology"},
    {"ticker": "ADBE", "name": "Adobe Inc.", "sector": "Technology"},
    {"ticker": "CRM", "name": "Salesforce Inc.", "sector": "Technology"},
    {"ticker": "INTC", "name": "Intel Corporation", "sector": "Technology"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "sector": "Technology"},

    # Financials
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials"},
    {"ticker": "BAC", "name": "Bank of America Corp.", "sector": "Financials"},
    {"ticker": "WFC", "name": "Wells Fargo & Company", "sector": "Financials"},
    {"ticker": "GS", "name": "Goldman Sachs Group", "sector": "Financials"},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Financials"},
    {"ticker": "BLK", "name": "BlackRock Inc.", "sector": "Financials"},

    # Healthcare
    {"ticker": "UNH", "name": "UnitedHealth Group", "sector": "Healthcare"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
    {"ticker": "LLY", "name": "Eli Lilly", "sector": "Healthcare"},
    {"ticker": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare"},
    {"ticker": "MRK", "name": "Merck & Co.", "sector": "Healthcare"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare"},

    # Consumer
    {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples"},
    {"ticker": "HD", "name": "Home Depot Inc.", "sector": "Consumer Discretionary"},
    {"ticker": "PG", "name": "Procter & Gamble", "sector": "Consumer Staples"},
    {"ticker": "KO", "name": "Coca-Cola Company", "sector": "Consumer Staples"},
    {"ticker": "MCD", "name": "McDonald's Corp.", "sector": "Consumer Discretionary"},
    {"ticker": "COST", "name": "Costco Wholesale", "sector": "Consumer Staples"},

    # Energy
    {"ticker": "XOM", "name": "Exxon Mobil Corp.", "sector": "Energy"},
    {"ticker": "CVX", "name": "Chevron Corporation", "sector": "Energy"},

    # Industrials
    {"ticker": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials"},
    {"ticker": "BA", "name": "Boeing Company", "sector": "Industrials"},
    {"ticker": "UPS", "name": "UPS", "sector": "Industrials"},
]


def safe_get(data, key, default="N/A"):
    """Safely get value from dict"""
    value = data.get(key, default)
    if value is None or (isinstance(value, float) and value != value):  # None or NaN
        return default
    return value


def format_number(value, format_type="number", decimals=2):
    """Format numbers for display"""
    if value == "N/A" or value is None:
        return "N/A"

    try:
        if format_type == "billions":
            return f"${value/1e9:,.{decimals}f}B"
        elif format_type == "millions":
            return f"${value/1e6:,.{decimals}f}M"
        elif format_type == "currency":
            return f"${value:,.{decimals}f}"
        elif format_type == "percentage":
            return f"{value*100:.{decimals}f}%"
        else:
            return f"{value:,.{decimals}f}"
    except:
        return "N/A"


def get_stock_data(ticker: str, retry_count=3) -> Dict:
    """
    Fetch comprehensive stock data with retry logic.

    Returns dict with market data, fundamentals, and analyst info.
    """
    for attempt in range(retry_count):
        try:
            print(f"    Fetching data (attempt {attempt + 1}/{retry_count})...", end=" ")

            # Let yfinance handle the session with curl_cffi
            stock = yf.Ticker(ticker)

            # Get current price data
            hist = stock.history(period="5d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            prev_close = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price

            # Get info (with error handling for missing keys)
            try:
                info = stock.info
            except:
                info = {}

            # Calculate changes
            price_change = (current_price - prev_close) if current_price and prev_close else None
            price_change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else None

            data = {
                # Market Data
                "currentPrice": current_price or safe_get(info, "currentPrice"),
                "previousClose": safe_get(info, "previousClose"),
                "open": safe_get(info, "open"),
                "dayHigh": safe_get(info, "dayHigh"),
                "dayLow": safe_get(info, "dayLow"),
                "volume": safe_get(info, "volume"),
                "priceChange": price_change,
                "priceChangePct": price_change_pct,

                # Valuation
                "marketCap": safe_get(info, "marketCap"),
                "enterpriseValue": safe_get(info, "enterpriseValue"),
                "trailingPE": safe_get(info, "trailingPE"),
                "forwardPE": safe_get(info, "forwardPE"),
                "priceToBook": safe_get(info, "priceToBook"),
                "priceToSales": safe_get(info, "priceToSalesTrailing12Months"),
                "pegRatio": safe_get(info, "pegRatio"),

                # Financial Performance
                "totalRevenue": safe_get(info, "totalRevenue"),
                "revenueGrowth": safe_get(info, "revenueGrowth"),
                "earningsGrowth": safe_get(info, "earningsGrowth"),
                "earningsQuarterlyGrowth": safe_get(info, "earningsQuarterlyGrowth"),

                # Profitability
                "profitMargin": safe_get(info, "profitMargins"),
                "operatingMargin": safe_get(info, "operatingMargins"),
                "grossMargin": safe_get(info, "grossMargins"),
                "returnOnEquity": safe_get(info, "returnOnEquity"),
                "returnOnAssets": safe_get(info, "returnOnAssets"),

                # Per Share
                "eps": safe_get(info, "trailingEps"),
                "forwardEps": safe_get(info, "forwardEps"),
                "bookValue": safe_get(info, "bookValue"),

                # Dividends
                "dividendYield": safe_get(info, "dividendYield"),
                "payoutRatio": safe_get(info, "payoutRatio"),

                # Risk & Targets
                "beta": safe_get(info, "beta"),
                "52WeekHigh": safe_get(info, "fiftyTwoWeekHigh"),
                "52WeekLow": safe_get(info, "fiftyTwoWeekLow"),
                "targetMeanPrice": safe_get(info, "targetMeanPrice"),
                "recommendationKey": safe_get(info, "recommendationKey", "N/A"),
            }

            print("✓")
            return data

        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                print(f"    Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"    Failed after {retry_count} attempts")
                return {}


def generate_csv(output_file: str, sector: Optional[str] = None, limit: Optional[int] = None):
    """Generate comprehensive CSV with all metrics"""

    print(f"\n{'='*80}")
    print(f"📊 S&P 500 Financial Analysis Tool")
    print(f"{'='*80}\n")

    # Filter companies
    companies = SP500_COMPANIES
    if sector:
        companies = [c for c in companies if c["sector"].lower() == sector.lower()]
        print(f"📌 Sector Filter: {sector}")

    if limit:
        companies = companies[:limit]

    print(f"📈 Analyzing {len(companies)} companies\n")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    csv_rows = []

    for idx, company in enumerate(companies, 1):
        ticker = company["ticker"]
        print(f"[{idx}/{len(companies)}] {ticker} - {company['name']}")

        data = get_stock_data(ticker)

        if not data:
            print(f"    ⚠️  Skipping due to data fetch failure\n")
            continue

        # Build CSV row
        row = {
            # Company Info
            "Ticker": ticker,
            "Company Name": company["name"],
            "Sector": company["sector"],

            # Market Data
            "Price": format_number(data.get("currentPrice"), "currency"),
            "Change": format_number(data.get("priceChange"), "currency"),
            "Change %": format_number(data.get("priceChangePct")/100, "percentage") if (data.get("priceChangePct") not in [None, "N/A"]) else "N/A",
            "Open": format_number(data.get("open"), "currency"),
            "High": format_number(data.get("dayHigh"), "currency"),
            "Low": format_number(data.get("dayLow"), "currency"),
            "Volume": f"{data.get('volume'):,}" if data.get("volume") != "N/A" else "N/A",

            # Valuation
            "Market Cap": format_number(data.get("marketCap"), "billions"),
            "Enterprise Value": format_number(data.get("enterpriseValue"), "billions"),
            "P/E Ratio": format_number(data.get("trailingPE")),
            "Forward P/E": format_number(data.get("forwardPE")),
            "P/B Ratio": format_number(data.get("priceToBook")),
            "P/S Ratio": format_number(data.get("priceToSales")),
            "PEG Ratio": format_number(data.get("pegRatio")),

            # Growth
            "Revenue": format_number(data.get("totalRevenue"), "billions"),
            "Revenue Growth": format_number(data.get("revenueGrowth"), "percentage"),
            "Earnings Growth": format_number(data.get("earningsGrowth"), "percentage"),
            "Quarterly Earnings Growth": format_number(data.get("earningsQuarterlyGrowth"), "percentage"),

            # Profitability
            "Profit Margin": format_number(data.get("profitMargin"), "percentage"),
            "Operating Margin": format_number(data.get("operatingMargin"), "percentage"),
            "Gross Margin": format_number(data.get("grossMargin"), "percentage"),
            "ROE": format_number(data.get("returnOnEquity"), "percentage"),
            "ROA": format_number(data.get("returnOnAssets"), "percentage"),

            # Per Share
            "EPS": format_number(data.get("eps"), "currency"),
            "Forward EPS": format_number(data.get("forwardEps"), "currency"),
            "Book Value": format_number(data.get("bookValue"), "currency"),

            # Dividends
            "Dividend Yield": format_number(data.get("dividendYield"), "percentage"),
            "Payout Ratio": format_number(data.get("payoutRatio"), "percentage"),

            # Risk & Targets
            "Beta": format_number(data.get("beta")),
            "52-Week High": format_number(data.get("52WeekHigh"), "currency"),
            "52-Week Low": format_number(data.get("52WeekLow"), "currency"),
            "Analyst Target": format_number(data.get("targetMeanPrice"), "currency"),
            "Recommendation": str(data.get("recommendationKey", "N/A")).upper(),

            # Metadata
            "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        csv_rows.append(row)

        # Rate limiting - be respectful to Yahoo Finance
        if idx < len(companies):
            time.sleep(1.5)  # 1.5 second delay between requests

        print()

    # Write CSV
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

        print(f"{'='*80}")
        print(f"✅ SUCCESS!")
        print(f"{'='*80}")
        print(f"📄 Output file: {output_file}")
        print(f"📊 Companies analyzed: {len(csv_rows)}")
        print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Show summary
        print(f"\n📈 Top 5 by Market Cap:")
        print(f"{'-'*80}")
        print(f"{'Ticker':<8} {'Company':<30} {'Price':<12} {'Market Cap':<15} {'P/E':<10}")
        print(f"{'-'*80}")

        for row in csv_rows[:5]:
            print(
                f"{row['Ticker']:<8} "
                f"{row['Company Name'][:28]:<30} "
                f"{row['Price']:<12} "
                f"{row['Market Cap']:<15} "
                f"{row['P/E Ratio']:<10}"
            )
        print()
    else:
        print(f"\n❌ No data collected. Please check network connectivity and try again.\n")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="S&P 500 Financial Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_sp500_standalone.py
  python generate_sp500_standalone.py --sector Technology
  python generate_sp500_standalone.py --sector Healthcare --limit 10
  python generate_sp500_standalone.py --output my_stocks.csv

Available Sectors:
  Technology, Financials, Healthcare, Consumer Discretionary,
  Consumer Staples, Energy, Industrials
        """
    )

    parser.add_argument('--sector', '-s', type=str, help='Filter by sector')
    parser.add_argument('--limit', '-l', type=int, help='Limit number of companies')
    parser.add_argument('--output', '-o', type=str, default='sp500_analysis.csv', help='Output CSV filename')

    args = parser.parse_args()

    try:
        generate_csv(args.output, args.sector, args.limit)
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
