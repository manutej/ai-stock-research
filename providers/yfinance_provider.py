"""
Yahoo Finance Data Provider Implementation

Uses yfinance library to access free stock market data from Yahoo Finance.
Provides real-time quotes, historical data, and company information.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import yfinance as yf
except ImportError:
    yf = None

from providers.base import (
    StockDataProvider,
    ProviderCapabilities,
    Quote,
    NewsArticle,
    FinancialData,
    OHLCV,
    MarketStatus
)


class YFinanceProvider(StockDataProvider):
    """
    Yahoo Finance data provider using yfinance library

    Capabilities:
    - Real-time quotes: ✅ Free (15-20 minute delay)
    - Historical data: ✅ Free
    - News: ✅ Free (limited)
    - Financials: ✅ Free
    - Market status: ⚠️ Inferred from data
    """

    CAPABILITIES = ProviderCapabilities(
        real_time_quotes=True,   # Actually ~15 min delayed, but free!
        historical_data=True,    # Full access
        news=True,               # Basic news access
        financials=True,         # Full access
        market_status=False,     # Not directly available
        rate_limit=None,         # No official rate limit
        requires_api_key=False,
        cost="free"
    )

    def __init__(self, **kwargs):
        super().__init__(api_key=None, **kwargs)
        if yf is None:
            raise ImportError(
                "yfinance is not installed. Install it with: pip install yfinance"
            )

    async def connect(self) -> None:
        """No connection needed for yfinance"""
        self._connected = True

    async def disconnect(self) -> None:
        """No disconnection needed for yfinance"""
        self._connected = False

    async def get_quote(self, ticker: str) -> Quote:
        """
        Get latest quote for a ticker

        Note: Data is typically delayed 15-20 minutes, but completely free!
        """
        # Run yfinance in executor to avoid blocking
        loop = asyncio.get_event_loop()
        stock = await loop.run_in_executor(None, yf.Ticker, ticker)

        try:
            # Get current price info
            info = await loop.run_in_executor(None, lambda: stock.info)

            # Extract price data
            current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0.0)
            previous_close = info.get("previousClose", current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0.0

            return Quote(
                ticker=ticker,
                price=current_price,
                timestamp=datetime.now(),
                volume=info.get("volume"),
                bid=info.get("bid"),
                ask=info.get("ask"),
                open=info.get("open") or info.get("regularMarketOpen"),
                high=info.get("dayHigh") or info.get("regularMarketDayHigh"),
                low=info.get("dayLow") or info.get("regularMarketDayLow"),
                previous_close=previous_close,
                change=change,
                change_percent=change_percent,
                provider="yfinance"
            )

        except Exception as e:
            print(f"Error fetching quote for {ticker}: {e}")
            return Quote(
                ticker=ticker,
                price=0.0,
                timestamp=datetime.now(),
                provider="yfinance"
            )

    async def get_quotes(self, tickers: List[str]) -> Dict[str, Quote]:
        """Get quotes for multiple tickers efficiently"""
        # yfinance can fetch multiple tickers at once
        loop = asyncio.get_event_loop()

        try:
            # Download all tickers at once
            data = await loop.run_in_executor(
                None,
                lambda: yf.download(
                    tickers=" ".join(tickers),
                    period="1d",
                    interval="1m",
                    group_by="ticker",
                    auto_adjust=True,
                    prepost=False,
                    threads=True,
                    progress=False
                )
            )

            quotes = {}
            for ticker in tickers:
                try:
                    quote = await self.get_quote(ticker)
                    quotes[ticker] = quote
                except Exception as e:
                    print(f"Error fetching {ticker}: {e}")

            return quotes

        except Exception as e:
            print(f"Error batch fetching quotes: {e}")
            # Fallback to individual fetches
            return await super().get_quotes(tickers)

    async def get_historical(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1d"
    ) -> List[OHLCV]:
        """Get historical OHLCV data"""
        loop = asyncio.get_event_loop()
        stock = await loop.run_in_executor(None, yf.Ticker, ticker)

        # Map timeframe to yfinance interval
        interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "1d": "1d",
            "1wk": "1wk",
            "1mo": "1mo"
        }
        interval = interval_map.get(timeframe, "1d")

        # Fetch historical data
        hist = await loop.run_in_executor(
            None,
            lambda: stock.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
        )

        bars = []
        for timestamp, row in hist.iterrows():
            bars.append(OHLCV(
                timestamp=timestamp.to_pydatetime(),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"]),
                ticker=ticker,
                provider="yfinance"
            ))

        return bars

    async def get_news(
        self,
        ticker: Optional[str] = None,
        limit: int = 10
    ) -> List[NewsArticle]:
        """
        Get recent news articles

        Note: YFinance provides limited news compared to Polygon
        """
        if not ticker:
            # YFinance requires a ticker for news
            return []

        loop = asyncio.get_event_loop()
        stock = await loop.run_in_executor(None, yf.Ticker, ticker)

        try:
            news = await loop.run_in_executor(None, lambda: stock.news)

            articles = []
            for item in news[:limit]:
                articles.append(NewsArticle(
                    title=item.get("title", ""),
                    description=item.get("summary"),
                    url=item.get("link", ""),
                    published_at=datetime.fromtimestamp(
                        item.get("providerPublishTime", 0)
                    ),
                    source=item.get("publisher"),
                    tickers=[ticker],
                    provider="yfinance"
                ))

            return articles

        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
            return []

    async def get_financials(
        self,
        ticker: str,
        limit: int = 4
    ) -> List[FinancialData]:
        """Get financial statements"""
        loop = asyncio.get_event_loop()
        stock = await loop.run_in_executor(None, yf.Ticker, ticker)

        try:
            # Get quarterly financials
            income_stmt = await loop.run_in_executor(None, lambda: stock.quarterly_income_stmt)
            balance_sheet = await loop.run_in_executor(None, lambda: stock.quarterly_balance_sheet)
            cash_flow = await loop.run_in_executor(None, lambda: stock.quarterly_cashflow)

            statements = []

            # Process each quarter
            for i, date in enumerate(income_stmt.columns[:limit]):
                # Determine fiscal period (Q1, Q2, Q3, Q4)
                quarter = ((date.month - 1) // 3) + 1
                fiscal_period = f"Q{quarter}"

                statements.append(FinancialData(
                    ticker=ticker,
                    period_start=date.to_pydatetime() - timedelta(days=90),
                    period_end=date.to_pydatetime(),
                    fiscal_year=date.year,
                    fiscal_period=fiscal_period,
                    revenue=float(income_stmt.loc["Total Revenue", date])
                    if "Total Revenue" in income_stmt.index else None,
                    net_income=float(income_stmt.loc["Net Income", date])
                    if "Net Income" in income_stmt.index else None,
                    total_assets=float(balance_sheet.loc["Total Assets", date])
                    if "Total Assets" in balance_sheet.index else None,
                    total_liabilities=float(balance_sheet.loc["Total Liabilities Net Minority Interest", date])
                    if "Total Liabilities Net Minority Interest" in balance_sheet.index else None,
                    stockholders_equity=float(balance_sheet.loc["Stockholders Equity", date])
                    if "Stockholders Equity" in balance_sheet.index else None,
                    operating_cash_flow=float(cash_flow.loc["Operating Cash Flow", date])
                    if "Operating Cash Flow" in cash_flow.index else None,
                    provider="yfinance"
                ))

            return statements

        except Exception as e:
            print(f"Error fetching financials for {ticker}: {e}")
            return []

    async def get_market_status(self) -> MarketStatus:
        """
        Get market status (inferred from SPY trading)

        Note: Not directly available in YFinance, so we check if SPY is trading
        """
        loop = asyncio.get_event_loop()
        spy = await loop.run_in_executor(None, yf.Ticker, "SPY")

        try:
            # Get 1-minute data from last hour
            hist = await loop.run_in_executor(
                None,
                lambda: spy.history(period="1d", interval="1m")
            )

            # If we have recent data, market is likely open
            is_open = len(hist) > 0 and (
                datetime.now() - hist.index[-1].to_pydatetime()
            ).total_seconds() < 300  # Within 5 minutes

            return MarketStatus(
                is_open=is_open,
                server_time=datetime.now(),
                provider="yfinance"
            )

        except Exception:
            return MarketStatus(
                is_open=False,
                server_time=datetime.now(),
                provider="yfinance"
            )

    @property
    def provider_name(self) -> str:
        return "Yahoo Finance"
