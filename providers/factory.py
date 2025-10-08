"""
Provider Factory and Manager

Handles creation and selection of data providers with automatic fallback
and hybrid strategies (e.g., use YFinance for prices, Polygon for news).
"""
from typing import Optional, Dict
from enum import Enum

from providers.base import (
    StockDataProvider,
    Quote,
    NewsArticle,
    FinancialData,
    OHLCV,
    MarketStatus,
    ProviderType
)


class ProviderStrategy(Enum):
    """Provider selection strategy"""
    POLYGON_ONLY = "polygon"
    YFINANCE_ONLY = "yfinance"
    AUTO = "auto"  # Smart selection based on task
    HYBRID = "hybrid"  # Use both for best results


class HybridProvider(StockDataProvider):
    """
    Hybrid provider that intelligently routes requests to different providers

    Strategy:
    - Quotes: YFinance (free, real-time-ish)
    - News: Polygon (better quality)
    - Financials: YFinance (faster, free)
    - Historical: YFinance (free, comprehensive)
    """

    def __init__(self, polygon_api_key: Optional[str] = None):
        super().__init__(api_key=polygon_api_key)
        self._polygon = None
        self._yfinance = None

    async def connect(self) -> None:
        """Initialize both providers"""
        from providers.yfinance_provider import YFinanceProvider

        # Always initialize YFinance (free, no API key needed)
        self._yfinance = YFinanceProvider()
        await self._yfinance.connect()

        # Initialize Polygon if API key available
        if self.api_key:
            from providers.polygon_provider import PolygonProvider
            self._polygon = PolygonProvider(api_key=self.api_key)
            await self._polygon.connect()

        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect both providers"""
        if self._yfinance:
            await self._yfinance.disconnect()
        if self._polygon:
            await self._polygon.disconnect()
        self._connected = False

    async def get_quote(self, ticker: str) -> Quote:
        """Use YFinance for quotes (free and real-time-ish)"""
        return await self._yfinance.get_quote(ticker)

    async def get_quotes(self, tickers: list) -> Dict[str, Quote]:
        """Use YFinance for batch quotes"""
        return await self._yfinance.get_quotes(tickers)

    async def get_historical(self, ticker: str, start_date, end_date, timeframe: str = "1d"):
        """Use YFinance for historical data (free and comprehensive)"""
        return await self._yfinance.get_historical(ticker, start_date, end_date, timeframe)

    async def get_news(self, ticker: Optional[str] = None, limit: int = 10):
        """Use Polygon for news if available (better quality), fallback to YFinance"""
        if self._polygon:
            try:
                return await self._polygon.get_news(ticker, limit)
            except Exception as e:
                print(f"Polygon news failed: {e}, falling back to YFinance")

        # Fallback to YFinance
        if ticker:
            return await self._yfinance.get_news(ticker, limit)
        return []

    async def get_financials(self, ticker: str, limit: int = 4):
        """Use YFinance for financials (faster and free)"""
        return await self._yfinance.get_financials(ticker, limit)

    async def get_market_status(self) -> MarketStatus:
        """Use Polygon if available, fallback to YFinance"""
        if self._polygon:
            try:
                return await self._polygon.get_market_status()
            except Exception:
                pass

        return await self._yfinance.get_market_status()

    @property
    def provider_name(self) -> str:
        return "Hybrid (YFinance + Polygon)"


class ProviderFactory:
    """
    Factory for creating and managing data providers

    Supports multiple provider strategies and automatic provider selection
    based on configuration and available API keys.
    """

    _instances: Dict[str, StockDataProvider] = {}

    @classmethod
    def create_provider(
        cls,
        strategy: ProviderStrategy = ProviderStrategy.AUTO,
        polygon_api_key: Optional[str] = None,
        **kwargs
    ) -> StockDataProvider:
        """
        Create a data provider based on strategy

        Args:
            strategy: Provider selection strategy
            polygon_api_key: Polygon.io API key (required for Polygon access)
            **kwargs: Additional provider configuration

        Returns:
            StockDataProvider instance

        Example:
            >>> provider = ProviderFactory.create_provider(
            ...     strategy=ProviderStrategy.HYBRID,
            ...     polygon_api_key="your-key"
            ... )
            >>> async with provider:
            ...     quote = await provider.get_quote("NVDA")
        """
        # Check cache
        cache_key = f"{strategy.value}_{polygon_api_key}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]

        # Create provider based on strategy
        if strategy == ProviderStrategy.POLYGON_ONLY:
            if not polygon_api_key:
                raise ValueError("Polygon API key required for polygon-only strategy")
            from providers.polygon_provider import PolygonProvider
            provider = PolygonProvider(api_key=polygon_api_key, **kwargs)

        elif strategy == ProviderStrategy.YFINANCE_ONLY:
            from providers.yfinance_provider import YFinanceProvider
            provider = YFinanceProvider(**kwargs)

        elif strategy == ProviderStrategy.AUTO:
            # Auto-select: use YFinance if no Polygon key, else use Hybrid
            if polygon_api_key:
                provider = HybridProvider(polygon_api_key=polygon_api_key)
            else:
                from providers.yfinance_provider import YFinanceProvider
                provider = YFinanceProvider(**kwargs)

        elif strategy == ProviderStrategy.HYBRID:
            provider = HybridProvider(polygon_api_key=polygon_api_key)

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        # Cache instance
        cls._instances[cache_key] = provider

        return provider

    @classmethod
    def from_config(cls, config) -> StockDataProvider:
        """
        Create provider from configuration object

        Args:
            config: Config instance with DEFAULT_PROVIDER and POLYGON_API_KEY

        Returns:
            StockDataProvider instance
        """
        strategy_map = {
            "polygon": ProviderStrategy.POLYGON_ONLY,
            "yfinance": ProviderStrategy.YFINANCE_ONLY,
            "auto": ProviderStrategy.AUTO,
            "hybrid": ProviderStrategy.HYBRID,
        }

        strategy = strategy_map.get(
            config.DEFAULT_PROVIDER.lower(),
            ProviderStrategy.AUTO
        )

        return cls.create_provider(
            strategy=strategy,
            polygon_api_key=config.POLYGON_API_KEY
        )

    @classmethod
    def clear_cache(cls):
        """Clear cached provider instances"""
        cls._instances.clear()
