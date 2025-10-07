"""
Polygon MCP Integration Module

This module provides a clean interface to interact with the Polygon.io MCP server
that's configured in Claude CLI. It wraps the available MCP tools for use in the
AI Stock Research Tool.
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class PolygonMCPClient:
    """
    Client for interacting with Polygon.io MCP server

    Available MCP Tools:
    - get_aggs: Stock aggregates (OHLC) data
    - list_trades: Historical trade data
    - get_last_trade: Latest trade for a symbol
    - list_ticker_news: Recent news articles
    - get_snapshot_ticker: Current market snapshot
    - get_market_status: Trading hours status
    - list_stock_financials: Fundamental financial data
    """

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self._connected = False
        self._read = None
        self._write = None
        self._exit_stack = None

    async def connect(self):
        """
        Connect to the Polygon MCP server

        The server should be configured via:
        claude mcp add polygon -e POLYGON_API_KEY=<key> -- uvx --from git+https://github.com/polygon-io/mcp_polygon@v0.4.1 mcp_polygon
        """
        if self._connected:
            return

        # Load API key from environment
        import os
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("POLYGON_API_KEY")
        if not api_key:
            raise ValueError("POLYGON_API_KEY not found in environment variables or .env file")

        # Server parameters matching Claude CLI configuration
        server_params = StdioServerParameters(
            command="uvx",
            args=[
                "--from",
                "git+https://github.com/polygon-io/mcp_polygon@v0.4.1",
                "mcp_polygon"
            ],
            env={
                "POLYGON_API_KEY": api_key
            }
        )

        # Connect to MCP server and keep connection open
        from contextlib import AsyncExitStack
        self._exit_stack = AsyncExitStack()

        read, write = await self._exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self._exit_stack.enter_async_context(ClientSession(read, write))

        # Initialize the connection
        await self.session.initialize()

        self._connected = True
        print("✓ Connected to Polygon MCP server")

    async def disconnect(self):
        """Disconnect from MCP server"""
        if self._exit_stack:
            await self._exit_stack.aclose()
        self._connected = False
        self.session = None
        print("✓ Disconnected from Polygon MCP server")

    def _parse_tool_result(self, result) -> Dict[str, Any]:
        """
        Parse MCP CallToolResult into dictionary

        MCP tools return CallToolResult objects with content array
        """
        if not result or not result.content:
            return {}

        # Extract text content from first content item
        if len(result.content) > 0:
            content_item = result.content[0]
            if hasattr(content_item, 'text'):
                # Parse JSON string from text content
                import json
                try:
                    return json.loads(content_item.text)
                except json.JSONDecodeError:
                    return {"raw": content_item.text}

        return {}

    async def get_snapshot(self, ticker: str) -> Dict[str, Any]:
        """
        Get current market snapshot for a ticker

        Args:
            ticker: Stock symbol (e.g., "NVDA", "MSFT")

        Returns:
            Current price, volume, and market data
        """
        if not self._connected:
            await self.connect()

        result = await self.session.call_tool(
            "get_snapshot_ticker",
            arguments={"ticker": ticker}
        )

        # Parse MCP CallToolResult
        return self._parse_tool_result(result)

    async def get_last_trade(self, ticker: str) -> Dict[str, Any]:
        """
        Get the latest trade for a ticker

        Args:
            ticker: Stock symbol

        Returns:
            Latest trade price, size, and timestamp
        """
        if not self._connected:
            await self.connect()

        result = await self.session.call_tool(
            "get_last_trade",
            arguments={"ticker": ticker}
        )

        return self._parse_tool_result(result)

    async def get_aggregates(
        self,
        ticker: str,
        timespan: str = "day",
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 120
    ) -> Dict[str, Any]:
        """
        Get aggregate bars (OHLC) for a ticker

        Args:
            ticker: Stock symbol
            timespan: Bar timespan (minute, hour, day, week, month, quarter, year)
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            limit: Number of bars to return

        Returns:
            Historical OHLC data
        """
        if not self._connected:
            await self.connect()

        # Default to last 120 days if no dates provided
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if not from_date:
            from_dt = datetime.now() - timedelta(days=120)
            from_date = from_dt.strftime("%Y-%m-%d")

        result = await self.session.call_tool(
            "get_aggs",
            arguments={
                "ticker": ticker,
                "multiplier": 1,
                "timespan": timespan,
                "from": from_date,
                "to": to_date,
                "limit": limit
            }
        )

        return self._parse_tool_result(result)

    async def get_news(
        self,
        ticker: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get recent news for a ticker or general market news

        Args:
            ticker: Stock symbol (optional, for company-specific news)
            limit: Number of articles to return

        Returns:
            List of news articles with titles, descriptions, URLs
        """
        if not self._connected:
            await self.connect()

        arguments = {"limit": limit}
        if ticker:
            arguments["ticker"] = ticker

        result = await self.session.call_tool(
            "list_ticker_news",
            arguments=arguments
        )

        return self._parse_tool_result(result)

    async def get_market_status(self) -> Dict[str, Any]:
        """
        Get current market status (open/closed, hours)

        Returns:
            Market status information
        """
        if not self._connected:
            await self.connect()

        result = await self.session.call_tool(
            "get_market_status",
            arguments={}
        )

        return self._parse_tool_result(result)

    async def get_financials(
        self,
        ticker: str,
        limit: int = 4
    ) -> Dict[str, Any]:
        """
        Get financial statements for a ticker

        Args:
            ticker: Stock symbol
            limit: Number of periods to return

        Returns:
            Financial data (balance sheet, income statement, cash flow)
        """
        if not self._connected:
            await self.connect()

        result = await self.session.call_tool(
            "list_stock_financials",
            arguments={
                "ticker": ticker,
                "limit": limit
            }
        )

        return self._parse_tool_result(result)

    async def list_trades(
        self,
        ticker: str,
        timestamp: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get historical trades for a ticker

        Args:
            ticker: Stock symbol
            timestamp: Timestamp to query from
            limit: Number of trades to return

        Returns:
            List of historical trades
        """
        if not self._connected:
            await self.connect()

        arguments = {
            "ticker": ticker,
            "limit": limit
        }

        if timestamp:
            arguments["timestamp"] = timestamp

        result = await self.session.call_tool(
            "list_trades",
            arguments=arguments
        )

        return self._parse_tool_result(result)


class PolygonDataFormatter:
    """
    Helper class to format Polygon API responses for display
    """

    @staticmethod
    def format_snapshot(data: Dict) -> str:
        """Format snapshot data for display"""
        if not data or "ticker" not in data:
            return "No data available"

        ticker = data.get("ticker", {})
        day = ticker.get("day", {})
        prev_day = ticker.get("prevDay", {})

        price = day.get("c", 0)
        change = price - prev_day.get("c", price)
        change_pct = (change / prev_day.get("c", 1)) * 100 if prev_day.get("c") else 0

        return f"""
Ticker: {data.get("ticker")}
Price: ${price:.2f} ({'+' if change >= 0 else ''}{change:.2f}, {change_pct:+.2f}%)
Volume: {ticker.get("todaysVolume", 0):,}
Day Range: ${day.get("l", 0):.2f} - ${day.get("h", 0):.2f}
"""

    @staticmethod
    def format_news(data: Dict) -> str:
        """Format news data for display"""
        if not data or "results" not in data:
            return "No news available"

        articles = data.get("results", [])
        output = []

        for article in articles[:5]:  # Show top 5
            title = article.get("title", "No title")
            published = article.get("published_utc", "")
            url = article.get("article_url", "")

            output.append(f"• {title}")
            output.append(f"  {published[:10]} - {url[:50]}...")

        return "\n".join(output)

    @staticmethod
    def format_market_status(data: Dict) -> str:
        """Format market status for display"""
        if not data:
            return "Market status unavailable"

        market = data.get("market", "unknown")
        server_time = data.get("serverTime", "")

        return f"Market: {market.upper()} | Server Time: {server_time}"


async def test_polygon_connection():
    """
    Test function to verify Polygon MCP connection and tools
    """
    print("\n🔌 Testing Polygon MCP Connection...")
    print("=" * 50)

    client = PolygonMCPClient()

    try:
        # Test 1: Market Status
        print("\n1️⃣  Testing get_market_status...")
        status = await client.get_market_status()
        print(PolygonDataFormatter.format_market_status(status))

        # Test 2: Latest Trade
        print("\n2️⃣  Testing get_last_trade for NVDA...")
        trade = await client.get_last_trade("NVDA")
        print(f"Latest trade: {json.dumps(trade, indent=2)}")

        # Test 3: News
        print("\n3️⃣  Testing list_ticker_news for AI sector...")
        news = await client.get_news("NVDA", limit=3)
        print(PolygonDataFormatter.format_news(news))

        # Test 4: Snapshot
        print("\n4️⃣  Testing get_snapshot_ticker for MSFT...")
        snapshot = await client.get_snapshot("MSFT")
        print(PolygonDataFormatter.format_snapshot(snapshot))

        print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_polygon_connection())
