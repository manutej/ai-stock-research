"""
Stock Data Providers Module

This module provides a unified interface for accessing stock market data
from multiple sources (Polygon, YFinance, etc.) using a provider pattern.
"""
from providers.base import (
    StockDataProvider,
    ProviderType,
    ProviderCapabilities,
    Quote,
    NewsArticle,
    FinancialData,
    OHLCV,
    MarketStatus
)

__all__ = [
    "StockDataProvider",
    "ProviderType",
    "ProviderCapabilities",
    "Quote",
    "NewsArticle",
    "FinancialData",
    "OHLCV",
    "MarketStatus",
    "get_provider",
]


def get_provider(
    provider_type: ProviderType,
    api_key: str = None,
    **kwargs
) -> StockDataProvider:
    """
    Factory function to create a data provider instance

    Args:
        provider_type: Type of provider to create
        api_key: API key for authentication
        **kwargs: Provider-specific configuration

    Returns:
        Instance of StockDataProvider

    Example:
        >>> provider = get_provider(ProviderType.YFINANCE)
        >>> async with provider:
        ...     quote = await provider.get_quote("NVDA")
        ...     print(f"NVDA: ${quote.price}")
    """
    if provider_type == ProviderType.POLYGON:
        from providers.polygon_provider import PolygonProvider
        return PolygonProvider(api_key=api_key, **kwargs)
    elif provider_type == ProviderType.YFINANCE:
        from providers.yfinance_provider import YFinanceProvider
        return YFinanceProvider(**kwargs)
    elif provider_type == ProviderType.ALPHA_VANTAGE:
        raise NotImplementedError("Alpha Vantage provider not yet implemented")
    elif provider_type == ProviderType.IEX_CLOUD:
        raise NotImplementedError("IEX Cloud provider not yet implemented")
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
