"""
Abstract Base Class for Stock Data Providers

This module defines the interface that all stock data providers must implement,
allowing the application to switch between different data sources (Polygon, YFinance, etc.)
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ProviderType(Enum):
    """Enumeration of supported data providers"""
    POLYGON = "polygon"
    YFINANCE = "yfinance"
    ALPHA_VANTAGE = "alpha_vantage"
    IEX_CLOUD = "iex_cloud"


@dataclass
class Quote:
    """Standardized quote data structure"""
    ticker: str
    price: float
    timestamp: datetime
    volume: Optional[int] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    previous_close: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    provider: Optional[str] = None


@dataclass
class NewsArticle:
    """Standardized news article structure"""
    title: str
    description: Optional[str]
    url: str
    published_at: datetime
    source: Optional[str] = None
    author: Optional[str] = None
    tickers: Optional[List[str]] = None
    provider: Optional[str] = None


@dataclass
class FinancialData:
    """Standardized financial statement structure"""
    ticker: str
    period_start: datetime
    period_end: datetime
    fiscal_year: int
    fiscal_period: str  # Q1, Q2, Q3, Q4, FY
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    earnings_per_share: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    stockholders_equity: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    provider: Optional[str] = None


@dataclass
class OHLCV:
    """Standardized OHLCV bar structure"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    ticker: Optional[str] = None
    provider: Optional[str] = None


@dataclass
class MarketStatus:
    """Standardized market status structure"""
    is_open: bool
    next_open: Optional[datetime] = None
    next_close: Optional[datetime] = None
    server_time: Optional[datetime] = None
    provider: Optional[str] = None


class StockDataProvider(ABC):
    """
    Abstract base class for stock data providers

    All data providers must implement these methods to provide
    consistent access to stock market data regardless of source.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the data provider

        Args:
            api_key: API key for authentication (if required)
            **kwargs: Provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
        self._connected = False

    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the data provider

        Raises:
            ConnectionError: If connection fails
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the data provider"""
        pass

    @abstractmethod
    async def get_quote(self, ticker: str) -> Quote:
        """
        Get latest quote for a ticker

        Args:
            ticker: Stock symbol (e.g., "NVDA", "MSFT")

        Returns:
            Quote object with current price and market data

        Raises:
            ValueError: If ticker is invalid
            ConnectionError: If provider is not connected
        """
        pass

    @abstractmethod
    async def get_quotes(self, tickers: List[str]) -> Dict[str, Quote]:
        """
        Get quotes for multiple tickers

        Args:
            tickers: List of stock symbols

        Returns:
            Dictionary mapping ticker to Quote object
        """
        pass

    @abstractmethod
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
            ticker: Stock symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            timeframe: Bar interval (1m, 5m, 1h, 1d, 1wk, 1mo)

        Returns:
            List of OHLCV bars
        """
        pass

    @abstractmethod
    async def get_news(
        self,
        ticker: Optional[str] = None,
        limit: int = 10
    ) -> List[NewsArticle]:
        """
        Get recent news articles

        Args:
            ticker: Stock symbol (None for general market news)
            limit: Maximum number of articles to return

        Returns:
            List of NewsArticle objects
        """
        pass

    @abstractmethod
    async def get_financials(
        self,
        ticker: str,
        limit: int = 4
    ) -> List[FinancialData]:
        """
        Get financial statements

        Args:
            ticker: Stock symbol
            limit: Number of periods to return

        Returns:
            List of FinancialData objects
        """
        pass

    @abstractmethod
    async def get_market_status(self) -> MarketStatus:
        """
        Get current market status

        Returns:
            MarketStatus object
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider"""
        pass

    @property
    def is_connected(self) -> bool:
        """Check if provider is connected"""
        return self._connected

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


class ProviderCapabilities:
    """
    Defines capabilities of different providers

    This helps the application choose the best provider for specific tasks
    """

    def __init__(
        self,
        real_time_quotes: bool = False,
        historical_data: bool = True,
        news: bool = False,
        financials: bool = False,
        market_status: bool = False,
        rate_limit: Optional[int] = None,
        requires_api_key: bool = False,
        cost: str = "free"
    ):
        self.real_time_quotes = real_time_quotes
        self.historical_data = historical_data
        self.news = news
        self.financials = financials
        self.market_status = market_status
        self.rate_limit = rate_limit  # calls per minute
        self.requires_api_key = requires_api_key
        self.cost = cost  # "free", "paid", "freemium"

    def supports(self, feature: str) -> bool:
        """Check if provider supports a specific feature"""
        return getattr(self, feature, False)
