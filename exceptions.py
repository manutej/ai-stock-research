"""
Custom exceptions for AI Stock Research Tool

Provides semantic error handling for different failure scenarios.
"""


class AIStockResearchError(Exception):
    """Base exception for all application errors"""
    pass


class ConfigurationError(AIStockResearchError):
    """Raised when configuration is invalid or missing"""
    pass


class ProviderError(AIStockResearchError):
    """Base exception for data provider errors"""
    pass


class ProviderConnectionError(ProviderError):
    """Raised when connection to data provider fails"""
    pass


class ProviderAuthenticationError(ProviderError):
    """Raised when API authentication fails"""
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when API rate limit is exceeded"""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class ProviderNotAvailableError(ProviderError):
    """Raised when requested provider is not available"""
    pass


class DataValidationError(AIStockResearchError):
    """Raised when data validation fails"""
    pass


class InvalidTickerError(AIStockResearchError):
    """Raised when ticker symbol is invalid"""
    def __init__(self, ticker: str):
        super().__init__(f"Invalid ticker symbol: {ticker}")
        self.ticker = ticker


class DataNotFoundError(AIStockResearchError):
    """Raised when requested data is not available"""
    pass


class CacheError(AIStockResearchError):
    """Raised when cache operations fail"""
    pass


class RateLimitExceededError(AIStockResearchError):
    """Raised when internal rate limit is exceeded"""
    def __init__(self, limit: int, window: str):
        super().__init__(f"Rate limit exceeded: {limit} requests per {window}")
        self.limit = limit
        self.window = window
