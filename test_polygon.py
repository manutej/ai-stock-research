"""
Test script for Polygon MCP integration

This script tests the connection to Polygon.io MCP server and validates
that all tools are working correctly with real market data.
"""
import asyncio
import json
from polygon_mcp import PolygonMCPClient, PolygonDataFormatter
from config import Config


async def test_all_tools():
    """
    Comprehensive test of all Polygon MCP tools
    """
    print("\n🧪 AI Stock Research Tool - Polygon MCP Test Suite")
    print("=" * 60)

    client = PolygonMCPClient()
    config = Config()

    try:
        await client.connect()

        # Test 1: Market Status
        print("\n📊 Test 1: Market Status")
        print("-" * 60)
        status = await client.get_market_status()
        print(json.dumps(status, indent=2))

        # Test 2: Get Latest Trade for NVDA
        print("\n💰 Test 2: Latest Trade - NVDA")
        print("-" * 60)
        trade = await client.get_last_trade("NVDA")
        print(json.dumps(trade, indent=2))

        # Test 3: Market Snapshot for AI Leaders
        print("\n📈 Test 3: Market Snapshots - AI Large Cap")
        print("-" * 60)
        ai_leaders = ["NVDA", "MSFT", "GOOGL"]
        for ticker in ai_leaders:
            print(f"\n{ticker}:")
            snapshot = await client.get_snapshot(ticker)
            print(PolygonDataFormatter.format_snapshot(snapshot))
            await asyncio.sleep(1)  # Rate limiting

        # Test 4: Recent News
        print("\n📰 Test 4: Recent News - AI Sector")
        print("-" * 60)
        news = await client.get_news("NVDA", limit=5)
        print(PolygonDataFormatter.format_news(news))

        # Test 5: Historical Aggregates
        print("\n📊 Test 5: Historical Data - MSFT (Last 30 Days)")
        print("-" * 60)
        from datetime import datetime, timedelta
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        aggs = await client.get_aggregates(
            ticker="MSFT",
            timespan="day",
            from_date=from_date,
            to_date=to_date,
            limit=30
        )
        print(f"Retrieved {len(aggs.get('results', []))} daily bars")
        if aggs.get("results"):
            latest = aggs["results"][-1]
            print(f"Latest bar: O:{latest['o']:.2f} H:{latest['h']:.2f} L:{latest['l']:.2f} C:{latest['c']:.2f}")

        # Test 6: Financial Data
        print("\n💼 Test 6: Financial Data - GOOGL")
        print("-" * 60)
        financials = await client.get_financials("GOOGL", limit=2)
        print(f"Retrieved {len(financials.get('results', []))} financial reports")
        if financials.get("results"):
            latest_fin = financials["results"][0]
            print(f"Period: {latest_fin.get('start_date')} to {latest_fin.get('end_date')}")
            print(f"Fiscal Year: {latest_fin.get('fiscal_year')}")

        # Test 7: Recent Trades
        print("\n🔄 Test 7: Recent Trades - PLTR")
        print("-" * 60)
        trades = await client.list_trades("PLTR", limit=10)
        print(f"Retrieved {len(trades.get('results', []))} trades")
        if trades.get("results"):
            for i, trade in enumerate(trades["results"][:3], 1):
                print(f"Trade {i}: Price=${trade.get('price', 0):.2f} Size={trade.get('size', 0)}")

        print("\n" + "=" * 60)
        print("✅ All Polygon MCP tools tested successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()
        print("\n🔌 Disconnected from Polygon MCP server")


async def test_ai_watchlist():
    """
    Test querying all companies in AI watchlists
    """
    print("\n🎯 Testing AI Watchlist Companies")
    print("=" * 60)

    client = PolygonMCPClient()
    config = Config()

    try:
        await client.connect()

        # Get all AI companies
        large_cap = config.load_watchlist("ai_large_cap")
        startups = config.load_watchlist("ai_startups")

        print("\n📊 Large Cap AI Leaders:")
        print("-" * 60)
        for company in large_cap["companies"][:3]:  # Test first 3
            ticker = company["ticker"]
            name = company["name"]

            print(f"\n{ticker} - {name}")
            snapshot = await client.get_snapshot(ticker)

            if snapshot and "ticker" in snapshot:
                ticker_data = snapshot.get("ticker", {})
                day = ticker_data.get("day", {})
                price = day.get("c", 0)
                print(f"  Price: ${price:.2f}")
            else:
                print("  No data available")

            await asyncio.sleep(1)  # Rate limiting

        print("\n\n🚀 AI Startups & IPOs:")
        print("-" * 60)
        for company in startups["companies"][:3]:  # Test first 3
            ticker = company["ticker"]
            name = company["name"]

            print(f"\n{ticker} - {name}")
            snapshot = await client.get_snapshot(ticker)

            if snapshot and "ticker" in snapshot:
                ticker_data = snapshot.get("ticker", {})
                day = ticker_data.get("day", {})
                price = day.get("c", 0)
                print(f"  Price: ${price:.2f}")
            else:
                print("  No data available")

            await asyncio.sleep(1)  # Rate limiting

        print("\n✅ Watchlist test completed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()


async def quick_test():
    """
    Quick test to verify connection is working
    """
    print("\n⚡ Quick Connection Test")
    print("=" * 40)

    client = PolygonMCPClient()

    try:
        print("Connecting to Polygon MCP server...")
        await client.connect()
        print("✓ Connected")

        print("\nGetting market status...")
        status = await client.get_market_status()
        print(f"✓ Market: {status.get('market', 'unknown').upper()}")

        print("\nGetting NVDA latest trade...")
        trade = await client.get_last_trade("NVDA")
        print(f"✓ NVDA Latest: ${trade.get('price', 0):.2f}")

        print("\n✅ Connection working!")

    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            asyncio.run(quick_test())
        elif sys.argv[1] == "watchlist":
            asyncio.run(test_ai_watchlist())
        else:
            asyncio.run(test_all_tools())
    else:
        # Default: run all tests
        asyncio.run(test_all_tools())
