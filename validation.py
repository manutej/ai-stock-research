"""
Input validation and data models using Pydantic

Ensures type safety and validates data from external sources.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re


class TickerRequest(BaseModel):
    """Request model for ticker operations"""
    ticker: str = Field(..., description="Stock ticker symbol")

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Validate ticker symbol format"""
        if not v:
            raise ValueError("Ticker cannot be empty")

        # Ticker should be 1-5 uppercase letters
        if not re.match(r'^[A-Z]{1,5}$', v.upper()):
            raise ValueError(
                f"Invalid ticker format: {v}. "
                "Ticker must be 1-5 uppercase letters"
            )

        return v.upper()


class QuoteRequest(BaseModel):
    """Request model for quote operations"""
    tickers: List[str] = Field(..., min_length=1, max_length=50)

    @field_validator('tickers')
    @classmethod
    def validate_tickers(cls, v: List[str]) -> List[str]:
        """Validate list of ticker symbols"""
        validated = []
        for ticker in v:
            # Use TickerRequest validation
            validated_ticker = TickerRequest(ticker=ticker).ticker
            validated.append(validated_ticker)

        return validated


class HistoricalDataRequest(BaseModel):
    """Request model for historical data"""
    ticker: str
    start_date: datetime
    end_date: datetime
    timeframe: str = Field(default="1d", pattern=r"^(1m|5m|15m|30m|1h|1d|1wk|1mo)$")

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        return TickerRequest(ticker=v).ticker

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v: datetime, info) -> datetime:
        """Ensure end_date is after start_date"""
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError("end_date must be after start_date")
        return v


class NewsRequest(BaseModel):
    """Request model for news"""
    ticker: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return TickerRequest(ticker=v).ticker
        return None


class FinancialsRequest(BaseModel):
    """Request model for financial data"""
    ticker: str
    limit: int = Field(default=4, ge=1, le=20)

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        return TickerRequest(ticker=v).ticker


class EnvironmentConfig(BaseModel):
    """Validation model for environment configuration"""

    # Optional API keys (None means provider not available)
    polygon_api_key: Optional[str] = Field(None, min_length=10)
    openai_api_key: Optional[str] = Field(None, min_length=10)
    anthropic_api_key: Optional[str] = Field(None, min_length=10)

    # Provider selection
    default_provider: str = Field(
        default="auto",
        pattern=r"^(auto|polygon|yfinance|hybrid)$"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )

    # Performance
    cache_ttl: int = Field(default=300, ge=0, le=3600)
    rate_limit: int = Field(default=5, ge=1, le=1000)

    class Config:
        """Pydantic config"""
        str_strip_whitespace = True
        use_enum_values = True


def validate_ticker(ticker: str) -> str:
    """
    Validate and normalize a ticker symbol

    Args:
        ticker: Stock ticker symbol

    Returns:
        Normalized ticker (uppercase)

    Raises:
        ValueError: If ticker is invalid

    Example:
        >>> validate_ticker("nvda")
        'NVDA'
        >>> validate_ticker("invalid123")
        ValueError: Invalid ticker format
    """
    return TickerRequest(ticker=ticker).ticker


def validate_tickers(tickers: List[str]) -> List[str]:
    """
    Validate and normalize a list of ticker symbols

    Args:
        tickers: List of stock ticker symbols

    Returns:
        List of normalized tickers

    Raises:
        ValueError: If any ticker is invalid
    """
    return QuoteRequest(tickers=tickers).tickers
