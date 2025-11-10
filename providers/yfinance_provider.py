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
from logging_config import get_logger
from exceptions import (
    ProviderConnectionError,
    InvalidTickerError,
    DataNotFoundError,
    ProviderError
)
from validation import validate_ticker, validate_tickers
from rate_limiter import get_rate_limiter

# Initialize logger
logger = get_logger(__name__)


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
            logger.error("yfinance library not installed")
            raise ProviderConnectionError(
                "yfinance is not installed. Install it with: pip install yfinance"
            )
        self.rate_limiter = get_rate_limiter()
        logger.info("YFinance provider initialized")

    async def connect(self) -> None:
        """No connection needed for yfinance"""
        try:
            # Test connection with a simple query
            loop = asyncio.get_event_loop()
            test = await loop.run_in_executor(None, yf.Ticker, "AAPL")
            _ = await loop.run_in_executor(None, lambda: test.info)
            self._connected = True
            logger.info("YFinance provider connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to YFinance: {e}", exc_info=True)
            raise ProviderConnectionError(f"YFinance connection failed: {e}")

    async def disconnect(self) -> None:
        """No disconnection needed for yfinance"""
        self._connected = False
        logger.info("YFinance provider disconnected")

    async def get_quote(self, ticker: str) -> Quote:
        """
        Get latest quote for a ticker

        Note: Data is typically delayed 15-20 minutes, but completely free!

        Args:
            ticker: Stock ticker symbol

        Returns:
            Quote object with current price data

        Raises:
            InvalidTickerError: If ticker is invalid
            ProviderError: If data fetch fails
        """
        # Validate ticker
        try:
            ticker = validate_ticker(ticker)
        except ValueError as e:
            logger.warning(f"Invalid ticker format: {ticker}")
            raise InvalidTickerError(ticker)

        # Rate limiting (generous for YFinance)
        try:
            self.rate_limiter.check_limit("yfinance")
        except Exception as e:
            logger.warning(f"Rate limit check failed: {e}")

        logger.debug(f"Fetching quote for {ticker}")

        # Run yfinance in executor to avoid blocking
        loop = asyncio.get_event_loop()

        try:
            stock = await loop.run_in_executor(None, yf.Ticker, ticker)
            info = await loop.run_in_executor(None, lambda: stock.info)

            # Check if we got valid data
            if not info or "currentPrice" not in info and "regularMarketPrice" not in info:
                logger.warning(f"No price data available for {ticker}")
                raise DataNotFoundError(f"No price data available for {ticker}")

            # Extract price data
            current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0.0)
            previous_close = info.get("previousClose", current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0.0

            quote = Quote(
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

            logger.info(f"Successfully fetched quote for {ticker}: ${current_price:.2f}")
            return quote

        except (InvalidTickerError, DataNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Error fetching quote for {ticker}: {e}", exc_info=True)
            raise ProviderError(f"Failed to fetch quote for {ticker}: {e}")

    async def get_quotes(self, tickers: List[str]) -> Dict[str, Quote]:
        """
        Get quotes for multiple tickers efficiently

        Args:
            tickers: List of stock ticker symbols

        Returns:
            Dictionary mapping ticker to Quote object

        Raises:
            ValueError: If tickers list is invalid
            ProviderError: If batch fetch fails
        """
        # Validate tickers
        try:
            tickers = validate_tickers(tickers)
        except ValueError as e:
            logger.warning(f"Invalid tickers list: {e}")
            raise

        logger.info(f"Fetching batch quotes for {len(tickers)} tickers")

        quotes = {}
        failed = []

        # Fetch quotes individually (more reliable than batch)
        for ticker in tickers:
            try:
                quote = await self.get_quote(ticker)
                quotes[ticker] = quote
            except Exception as e:
                logger.warning(f"Failed to fetch {ticker}: {e}")
                failed.append(ticker)

        if failed:
            logger.warning(f"Failed to fetch {len(failed)} tickers: {failed}")

        logger.info(f"Successfully fetched {len(quotes)}/{len(tickers)} quotes")
        return quotes

    async def get_historical(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1d"
    ) -> List[OHLCV]:
        """
        Get historical OHLCV data

        Args:
            ticker: Stock ticker symbol
            start_date: Start date for data
            end_date: End date for data
            timeframe: Bar interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)

        Returns:
            List of OHLCV bars

        Raises:
            InvalidTickerError: If ticker is invalid
            ProviderError: If data fetch fails
        """
        # Validate ticker
        ticker = validate_ticker(ticker)

        logger.info(f"Fetching historical data for {ticker} from {start_date.date()} to {end_date.date()}")

        loop = asyncio.get_event_loop()

        try:
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

            if hist.empty:
                logger.warning(f"No historical data available for {ticker}")
                return []

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

            logger.info(f"Fetched {len(bars)} bars for {ticker}")
            return bars

        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {e}", exc_info=True)
            raise ProviderError(f"Failed to fetch historical data for {ticker}: {e}")

    async def get_news(
        self,
        ticker: Optional[str] = None,
        limit: int = 10
    ) -> List[NewsArticle]:
        """
        Get recent news articles

        Note: YFinance provides limited news compared to Polygon

        Args:
            ticker: Stock ticker symbol (required for YFinance)
            limit: Maximum number of articles to return

        Returns:
            List of NewsArticle objects

        Raises:
            ValueError: If ticker is not provided or invalid
            ProviderError: If news fetch fails
        """
        if not ticker:
            logger.debug("No ticker provided for news query")
            return []

        # Validate ticker
        ticker = validate_ticker(ticker)

        logger.info(f"Fetching news for {ticker}, limit={limit}")

        loop = asyncio.get_event_loop()

        try:
            stock = await loop.run_in_executor(None, yf.Ticker, ticker)
            news = await loop.run_in_executor(None, lambda: stock.news)

            if not news:
                logger.info(f"No news available for {ticker}")
                return []

            articles = []
            for item in news[:limit]:
                try:
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
                except Exception as e:
                    logger.warning(f"Failed to parse news article: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} news articles for {ticker}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}", exc_info=True)
            raise ProviderError(f"Failed to fetch news for {ticker}: {e}")

    async def get_financials(
        self,
        ticker: str,
        limit: int = 4
    ) -> List[FinancialData]:
        """
        Get financial statements

        Args:
            ticker: Stock ticker symbol
            limit: Number of periods to return (most recent first)

        Returns:
            List of FinancialData objects

        Raises:
            InvalidTickerError: If ticker is invalid
            ProviderError: If financials fetch fails
        """
        # Validate ticker
        ticker = validate_ticker(ticker)

        logger.info(f"Fetching financials for {ticker}, limit={limit}")

        loop = asyncio.get_event_loop()

        try:
            stock = await loop.run_in_executor(None, yf.Ticker, ticker)

            # Get quarterly financials
            income_stmt = await loop.run_in_executor(None, lambda: stock.quarterly_income_stmt)
            balance_sheet = await loop.run_in_executor(None, lambda: stock.quarterly_balance_sheet)
            cash_flow = await loop.run_in_executor(None, lambda: stock.quarterly_cashflow)

            if income_stmt.empty:
                logger.warning(f"No financial data available for {ticker}")
                return []

            statements = []

            # Process each quarter
            for i, date in enumerate(income_stmt.columns[:limit]):
                try:
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
                        if not balance_sheet.empty and "Total Assets" in balance_sheet.index else None,
                        total_liabilities=float(balance_sheet.loc["Total Liabilities Net Minority Interest", date])
                        if not balance_sheet.empty and "Total Liabilities Net Minority Interest" in balance_sheet.index else None,
                        stockholders_equity=float(balance_sheet.loc["Stockholders Equity", date])
                        if not balance_sheet.empty and "Stockholders Equity" in balance_sheet.index else None,
                        operating_cash_flow=float(cash_flow.loc["Operating Cash Flow", date])
                        if not cash_flow.empty and "Operating Cash Flow" in cash_flow.index else None,
                        provider="yfinance"
                    ))
                except Exception as e:
                    logger.warning(f"Failed to parse financial period {date}: {e}")
                    continue

            logger.info(f"Fetched {len(statements)} financial statements for {ticker}")
            return statements

        except Exception as e:
            logger.error(f"Error fetching financials for {ticker}: {e}", exc_info=True)
            raise ProviderError(f"Failed to fetch financials for {ticker}: {e}")

    async def get_market_status(self) -> MarketStatus:
        """
        Get market status (inferred from SPY trading)

        Note: Not directly available in YFinance, so we check if SPY is trading

        Returns:
            MarketStatus object

        Raises:
            ProviderError: If status check fails
        """
        logger.debug("Checking market status")

        loop = asyncio.get_event_loop()

        try:
            spy = await loop.run_in_executor(None, yf.Ticker, "SPY")

            # Get 1-minute data from last hour
            hist = await loop.run_in_executor(
                None,
                lambda: spy.history(period="1d", interval="1m")
            )

            # If we have recent data, market is likely open
            is_open = len(hist) > 0 and (
                datetime.now() - hist.index[-1].to_pydatetime()
            ).total_seconds() < 300  # Within 5 minutes

            logger.info(f"Market status: {'OPEN' if is_open else 'CLOSED'}")

            return MarketStatus(
                is_open=is_open,
                server_time=datetime.now(),
                provider="yfinance"
            )

        except Exception as e:
            logger.warning(f"Failed to check market status: {e}")
            # Return closed as safe default
            return MarketStatus(
                is_open=False,
                server_time=datetime.now(),
                provider="yfinance"
            )

    @property
    def provider_name(self) -> str:
        return "Yahoo Finance"
