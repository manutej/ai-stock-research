"""
AI Stock Research Tool - Main Client
Leverages Polygon MCP server for financial data analysis
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from config import Config, PolygonConfig, AICompanyCategories


class AIStockResearchTool:
    """
    Main client for AI stock research using Polygon MCP server
    """

    def __init__(self):
        self.config = Config()
        self.polygon_config = PolygonConfig()
        self.categories = AICompanyCategories()

        # Verify API key
        if not self.config.POLYGON_API_KEY:
            raise ValueError("POLYGON_API_KEY not found in environment variables")

    async def research_query(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for research queries

        Args:
            query: Natural language research question

        Returns:
            Structured research results
        """
        # Parse intent from query
        intent = await self._parse_intent(query)

        # Route to appropriate handler
        if intent["type"] == "morning_brief":
            return await self.morning_brief()
        elif intent["type"] == "company_analysis":
            return await self.analyze_company(intent["ticker"])
        elif intent["type"] == "sector_comparison":
            return await self.compare_sector(intent["tickers"])
        elif intent["type"] == "price_check":
            return await self.get_price(intent["ticker"])
        else:
            return {"error": "Unknown query type", "query": query}

    async def _parse_intent(self, query: str) -> Dict[str, Any]:
        """
        Parse user intent from natural language query

        TODO: Integrate LLM for better understanding
        """
        query_lower = query.lower()

        # Simple keyword-based intent detection
        if "morning" in query_lower or "brief" in query_lower:
            return {"type": "morning_brief"}

        # Check for company-specific queries
        for ticker in self.config.get_all_tickers():
            if ticker.lower() in query_lower:
                if "compare" in query_lower:
                    # Find other tickers mentioned
                    tickers = [t for t in self.config.get_all_tickers()
                              if t.lower() in query_lower]
                    return {"type": "sector_comparison", "tickers": tickers}
                else:
                    return {"type": "company_analysis", "ticker": ticker}

        # Price check
        if "price" in query_lower or "quote" in query_lower:
            for ticker in self.config.get_all_tickers():
                if ticker.lower() in query_lower:
                    return {"type": "price_check", "ticker": ticker}

        return {"type": "unknown", "query": query}

    async def morning_brief(self) -> Dict[str, Any]:
        """
        Generate AI sector morning brief

        Uses Polygon MCP tools:
        - get_market_status: Check if markets are open
        - get_snapshot_ticker: Get current prices for AI stocks
        - list_ticker_news: Fetch overnight news
        """
        print("\n📊 AI Sector Morning Brief")
        print("=" * 50)

        # Note: In actual implementation, these would be MCP tool calls
        # For now, showing the structure

        brief = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "market_status": "Pre-market",  # From get_market_status
            "top_movers": [],  # From get_snapshot_ticker for each stock
            "news_summary": [],  # From list_ticker_news
        }

        print(f"\nDate: {brief['date']}")
        print(f"Market Status: {brief['market_status']}")
        print("\n📈 Top Movers:")
        print("└─ (Connect Polygon MCP to see live data)")

        return brief

    async def analyze_company(self, ticker: str) -> Dict[str, Any]:
        """
        Comprehensive company analysis

        Uses Polygon MCP tools:
        - get_snapshot_ticker: Current market data
        - list_ticker_news: Recent news
        - get_aggs: Historical price data
        - list_stock_financials: Fundamental data
        """
        company_info = self.config.get_company_info(ticker)

        if not company_info:
            return {"error": f"Company not found: {ticker}"}

        print(f"\n🔍 Analyzing {ticker} - {company_info['name']}")
        print("=" * 50)
        print(f"Sector: {company_info['sector']}")
        print(f"Focus: {company_info['focus']}")

        analysis = {
            "ticker": ticker,
            "company": company_info,
            "snapshot": {},  # From get_snapshot_ticker
            "news": [],  # From list_ticker_news
            "price_history": [],  # From get_aggs
            "financials": {},  # From list_stock_financials
        }

        return analysis

    async def compare_sector(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Compare multiple AI companies

        Uses Polygon MCP tools for each ticker:
        - get_snapshot_ticker: Current metrics
        - list_stock_financials: Financial comparison
        """
        print(f"\n📊 Comparing {len(tickers)} AI Companies")
        print("=" * 50)

        comparison = {
            "tickers": tickers,
            "metrics": {},
        }

        for ticker in tickers:
            info = self.config.get_company_info(ticker)
            if info:
                print(f"• {ticker}: {info['name']}")

        return comparison

    async def get_price(self, ticker: str) -> Dict[str, Any]:
        """
        Get latest price for a ticker

        Uses Polygon MCP tool:
        - get_last_trade: Latest trade data
        """
        print(f"\n💰 Latest Price for {ticker}")

        # Note: This would call Polygon MCP get_last_trade
        price_data = {
            "ticker": ticker,
            "price": None,  # From get_last_trade
            "timestamp": datetime.now().isoformat(),
        }

        return price_data

    async def setup_alert(self, ticker: str, threshold_percent: float = 5.0):
        """
        Set up price movement alert

        Uses Polygon MCP tools:
        - get_last_trade: Monitor current price
        - get_aggs: Calculate baseline
        - list_ticker_news: Filter AI-related news
        """
        print(f"\n🔔 Setting up alert for {ticker}")
        print(f"Threshold: {threshold_percent}% movement")

        alert_config = {
            "ticker": ticker,
            "threshold": threshold_percent,
            "active": True,
        }

        return alert_config


async def main():
    """
    Main entry point for CLI usage
    """
    print("\n🤖 AI Stock Research Tool")
    print("=" * 50)
    print("Powered by Polygon.io MCP Server\n")

    tool = AIStockResearchTool()

    # Example queries
    print("Example queries you can run:")
    print("1. 'Give me a morning brief on AI stocks'")
    print("2. 'How is NVDA performing?'")
    print("3. 'Compare MSFT and GOOGL'")
    print("4. 'What's the latest price for PLTR?'")
    print("\nNote: Connect to Polygon MCP server for live data\n")

    # Demo query
    result = await tool.research_query("Give me a morning brief")
    print("\n📋 Query Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
