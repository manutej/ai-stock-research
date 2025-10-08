"""
Polygon.io Data Provider Implementation

Wraps the Polygon MCP client to conform to the StockDataProvider interface.
Provides access to Polygon's financial data API through MCP protocol.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from providers.base import (
    StockDataProvider,
    ProviderCapabilities,
    Quote,
    NewsArticle,
    FinancialData,
    OHLCV,
    MarketStatus
)
from polygon_mcp import PolygonMCPClient


class PolygonProvider(StockDataProvider):
    """
    Polygon.io data provider using MCP protocol

    Capabilities:
    - Real-time quotes: Requires paid plan
    - Historical data: Limited on free tier
    - News: Full access on free tier
    - Financials: Full access on free tier
    - Market status: Full access on free tier
    """

    CAPABILITIES = ProviderCapabilities(
        real_time_quotes=False,  # Requires paid plan
        historical_data=True,    # Limited on free tier
        news=True,              # Works on free tier
        financials=True,        # Works on free tier
        market_status=True,     # Works on free tier
        rate_limit=5,           # 5 calls/minute on free tier
        requires_api_key=True,
        cost="freemium"
    )

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self._client: Optional[PolygonMCPClient] = None

    async def connect(self) -> None:
        """Establish connection to Polygon MCP server"""
        if self._connected:
            return

        self._client = PolygonMCPClient()
        await self._client.connect()
        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from Polygon MCP server"""
        if self._client:
            await self._client.disconnect()
            self._client = None
        self._connected = False

    async def get_quote(self, ticker: str) -> Quote:
        """
        Get latest quote for a ticker

        Note: Free tier returns limited data. Paid plan required for real-time prices.
        """
        if not self._connected:
            await self.connect()

        # Try to get snapshot first (most complete data)
        try:
            snapshot = await self._client.get_snapshot(ticker)

            if snapshot and "ticker" in snapshot:
                ticker_data = snapshot.get("ticker", {})
                day = ticker_data.get("day", {})
                prev_day = ticker_data.get("prevDay", {})
                last_quote = ticker_data.get("lastQuote", {})

                price = day.get("c", 0.0)
                prev_close = prev_day.get("c", price)
                change = price - prev_close if prev_close else 0.0
                change_percent = (change / prev_close * 100) if prev_close else 0.0

                return Quote(
                    ticker=ticker,
                    price=price,
                    timestamp=datetime.now(),
                    volume=ticker_data.get("todaysVolume"),
                    bid=last_quote.get("P") if last_quote else None,
                    ask=last_quote.get("p") if last_quote else None,
                    open=day.get("o"),
                    high=day.get("h"),
                    low=day.get("l"),
                    previous_close=prev_close,
                    change=change,
                    change_percent=change_percent,
                    provider="polygon"
                )
        except Exception:
            pass  # Snapshot failed, try last trade

        # Fallback to last trade (requires paid plan)
        try:
            trade = await self._client.get_last_trade(ticker)
            if trade and "price" in trade:
                return Quote(
                    ticker=ticker,
                    price=trade.get("price", 0.0),
                    timestamp=datetime.fromtimestamp(trade.get("timestamp", 0) / 1e9),
                    volume=trade.get("size"),
                    provider="polygon"
                )
        except Exception:
            pass

        # No data available
        return Quote(
            ticker=ticker,
            price=0.0,
            timestamp=datetime.now(),
            provider="polygon"
        )

    async def get_quotes(self, tickers: List[str]) -> Dict[str, Quote]:
        """Get quotes for multiple tickers"""
        quotes = {}
        for ticker in tickers:
            try:
                quotes[ticker] = await self.get_quote(ticker)
                await asyncio.sleep(0.2)  # Rate limiting
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
        return quotes

    async def get_historical(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1d"
    ) -> List[OHLCV]:
        """Get historical OHLCV data"""
        if not self._connected:
            await self.connect()

        # Map timeframe to Polygon format
        timespan_map = {
            "1m": "minute",
            "5m": "minute",
            "1h": "hour",
            "1d": "day",
            "1wk": "week",
            "1mo": "month"
        }
        timespan = timespan_map.get(timeframe, "day")

        aggs = await self._client.get_aggregates(
            ticker=ticker,
            timespan=timespan,
            from_date=start_date.strftime("%Y-%m-%d"),
            to_date=end_date.strftime("%Y-%m-%d"),
            limit=5000
        )

        bars = []
        for bar in aggs.get("results", []):
            bars.append(OHLCV(
                timestamp=datetime.fromtimestamp(bar["t"] / 1000),
                open=bar["o"],
                high=bar["h"],
                low=bar["l"],
                close=bar["c"],
                volume=bar["v"],
                ticker=ticker,
                provider="polygon"
            ))

        return bars

    async def get_news(
        self,
        ticker: Optional[str] = None,
        limit: int = 10
    ) -> List[NewsArticle]:
        """Get recent news articles"""
        if not self._connected:
            await self.connect()

        news_data = await self._client.get_news(ticker=ticker, limit=limit)

        articles = []
        for article in news_data.get("results", []):
            articles.append(NewsArticle(
                title=article.get("title", ""),
                description=article.get("description"),
                url=article.get("article_url", ""),
                published_at=datetime.fromisoformat(
                    article.get("published_utc", "").replace("Z", "+00:00")
                ),
                source=article.get("publisher", {}).get("name"),
                author=article.get("author"),
                tickers=article.get("tickers", []),
                provider="polygon"
            ))

        return articles

    async def get_financials(
        self,
        ticker: str,
        limit: int = 4
    ) -> List[FinancialData]:
        """Get financial statements"""
        if not self._connected:
            await self.connect()

        financials_data = await self._client.get_financials(ticker=ticker, limit=limit)

        statements = []
        for report in financials_data.get("results", []):
            financials = report.get("financials", {})
            income_statement = financials.get("income_statement", {})
            balance_sheet = financials.get("balance_sheet", {})
            cash_flow = financials.get("cash_flow_statement", {})

            statements.append(FinancialData(
                ticker=ticker,
                period_start=datetime.fromisoformat(report.get("start_date")),
                period_end=datetime.fromisoformat(report.get("end_date")),
                fiscal_year=report.get("fiscal_year", 0),
                fiscal_period=report.get("fiscal_period", ""),
                revenue=income_statement.get("revenues", {}).get("value"),
                net_income=income_statement.get("net_income_loss", {}).get("value"),
                earnings_per_share=income_statement.get("basic_earnings_per_share", {}).get("value"),
                total_assets=balance_sheet.get("assets", {}).get("value"),
                total_liabilities=balance_sheet.get("liabilities", {}).get("value"),
                stockholders_equity=balance_sheet.get("equity", {}).get("value"),
                operating_cash_flow=cash_flow.get("net_cash_flow_from_operating_activities", {}).get("value"),
                provider="polygon"
            ))

        return statements

    async def get_market_status(self) -> MarketStatus:
        """Get current market status"""
        if not self._connected:
            await self.connect()

        status_data = await self._client.get_market_status()

        return MarketStatus(
            is_open=status_data.get("market") == "open",
            server_time=datetime.fromisoformat(
                status_data.get("serverTime", "").replace("-04:00", "+00:00")
            ) if status_data.get("serverTime") else None,
            provider="polygon"
        )

    @property
    def provider_name(self) -> str:
        return "Polygon.io"
