"""
Pytest configuration and shared fixtures

Provides common fixtures, marks, and configuration for all tests.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, may use network)"
    )
    config.addinivalue_line(
        "markers", "property: Property-based tests (Hypothesis)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (>1s)"
    )
    config.addinivalue_line(
        "markers", "validation: Validation module tests"
    )
    config.addinivalue_line(
        "markers", "rate_limiter: Rate limiter tests"
    )
    config.addinivalue_line(
        "markers", "logging: Logging tests"
    )
    config.addinivalue_line(
        "markers", "provider: Provider tests"
    )


# ============================================================================
# Shared Fixtures
# ============================================================================

@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests"""
    return tmp_path


@pytest.fixture
def sample_quote_data():
    """Sample quote data for testing"""
    return {
        "currentPrice": 185.04,
        "regularMarketPrice": 185.04,
        "previousClose": 185.50,
        "volume": 45678900,
        "bid": 185.03,
        "ask": 185.05,
        "open": 185.20,
        "regularMarketOpen": 185.20,
        "dayHigh": 186.50,
        "regularMarketDayHigh": 186.50,
        "dayLow": 184.00,
        "regularMarketDayLow": 184.00
    }


@pytest.fixture
def sample_tickers():
    """Sample list of valid tickers"""
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]


@pytest.fixture
def sample_date_range():
    """Sample date range for historical data"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return start_date, end_date


@pytest.fixture
def mock_yfinance_ticker(sample_quote_data):
    """Mock yfinance Ticker object"""
    ticker = Mock()
    ticker.info = sample_quote_data
    ticker.news = [
        {
            "title": "Test News Article 1",
            "summary": "Test summary 1",
            "link": "https://example.com/news1",
            "providerPublishTime": int(datetime.now().timestamp()),
            "publisher": "Test Publisher"
        },
        {
            "title": "Test News Article 2",
            "summary": "Test summary 2",
            "link": "https://example.com/news2",
            "providerPublishTime": int(datetime.now().timestamp() - 3600),
            "publisher": "Test Publisher"
        }
    ]

    # Mock historical data
    import pandas as pd
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), periods=7, freq='D')
    hist_data = pd.DataFrame({
        'Open': [185.0, 186.0, 184.5, 185.5, 187.0, 186.5, 185.0],
        'High': [186.5, 187.0, 185.5, 186.5, 188.0, 187.5, 186.0],
        'Low': [184.0, 185.5, 183.5, 184.5, 186.0, 185.5, 184.0],
        'Close': [185.5, 186.5, 184.0, 186.0, 187.5, 186.0, 185.0],
        'Volume': [50000000, 45000000, 55000000, 48000000, 52000000, 46000000, 49000000]
    }, index=dates)
    ticker.history = Mock(return_value=hist_data)

    # Mock financials
    financial_dates = pd.date_range(end=datetime.now(), periods=4, freq='Q')
    income_stmt = pd.DataFrame({
        financial_dates[0]: {"Total Revenue": 90000000000, "Net Income": 25000000000},
        financial_dates[1]: {"Total Revenue": 95000000000, "Net Income": 26000000000},
        financial_dates[2]: {"Total Revenue": 98000000000, "Net Income": 27000000000},
        financial_dates[3]: {"Total Revenue": 100000000000, "Net Income": 28000000000}
    }).T
    ticker.quarterly_income_stmt = income_stmt

    balance_sheet = pd.DataFrame({
        financial_dates[0]: {
            "Total Assets": 350000000000,
            "Total Liabilities Net Minority Interest": 250000000000,
            "Stockholders Equity": 100000000000
        },
        financial_dates[1]: {
            "Total Assets": 360000000000,
            "Total Liabilities Net Minority Interest": 255000000000,
            "Stockholders Equity": 105000000000
        }
    }).T
    ticker.quarterly_balance_sheet = balance_sheet

    cash_flow = pd.DataFrame({
        financial_dates[0]: {"Operating Cash Flow": 30000000000},
        financial_dates[1]: {"Operating Cash Flow": 31000000000}
    }).T
    ticker.quarterly_cashflow = cash_flow

    return ticker


@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter that always allows requests"""
    limiter = Mock()
    limiter.check_limit = Mock(return_value=None)  # No exception raised
    limiter.get_wait_time = Mock(return_value=0.0)
    return limiter


@pytest.fixture
def sample_sp500_companies():
    """Sample S&P 500 companies for testing"""
    return [
        {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
        {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
        {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials"},
        {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
        {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples"},
    ]


@pytest.fixture
def sample_advanced_companies():
    """Sample S&P 500 companies with industry info for advanced tests"""
    return [
        {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics"
        },
        {
            "ticker": "MSFT",
            "name": "Microsoft Corporation",
            "sector": "Technology",
            "industry": "Software"
        },
        {
            "ticker": "JPM",
            "name": "JPMorgan Chase & Co.",
            "sector": "Financials",
            "industry": "Banking"
        },
    ]


@pytest.fixture
def mock_quote():
    """Mock quote object for testing"""
    from providers.base import Quote
    return Quote(
        ticker="AAPL",
        price=150.25,
        timestamp=datetime.now(),
        volume=50000000,
        bid=150.20,
        ask=150.30,
        open=149.50,
        high=151.00,
        low=149.00,
        previous_close=149.00,
        change=1.25,
        change_percent=0.84,
        provider="mock"
    )


@pytest.fixture
def mock_quotes(sample_sp500_companies):
    """Mock quotes dictionary for multiple tickers"""
    from providers.base import Quote
    quotes = {}
    for i, company in enumerate(sample_sp500_companies):
        quotes[company["ticker"]] = Quote(
            ticker=company["ticker"],
            price=150.0 + i * 50,
            timestamp=datetime.now(),
            volume=50000000 - i * 5000000,
            change=1.25 - i * 0.5,
            change_percent=0.84 - i * 0.2,
            open=149.0 + i * 50,
            high=152.0 + i * 50,
            low=148.0 + i * 50,
            provider="mock"
        )
    return quotes


@pytest.fixture
def mock_stock_provider():
    """Mock stock data provider for testing"""
    from unittest.mock import AsyncMock
    provider = AsyncMock()
    provider.__aenter__ = AsyncMock(return_value=provider)
    provider.__aexit__ = AsyncMock(return_value=None)
    provider.provider_name = "mock"
    return provider


@pytest.fixture
def sample_fundamental_data():
    """Sample fundamental data from yfinance"""
    return {
        "marketCap": 2500000000000,
        "enterpriseValue": 2600000000000,
        "trailingPE": 28.5,
        "forwardPE": 25.3,
        "priceToBook": 45.2,
        "priceToSales": 7.5,
        "pegRatio": 2.1,
        "revenue": 383000000000,
        "revenueGrowth": 0.08,
        "earningsGrowth": 0.12,
        "earningsQuarterlyGrowth": 0.10,
        "profitMargin": 0.25,
        "operatingMargin": 0.30,
        "grossMargin": 0.42,
        "returnOnEquity": 1.47,
        "returnOnAssets": 0.20,
        "eps": 6.05,
        "forwardEps": 6.50,
        "bookValue": 3.35,
        "dividendYield": 0.005,
        "payoutRatio": 0.15,
        "beta": 1.2,
        "fiftyTwoWeekHigh": 180.00,
        "fiftyTwoWeekLow": 125.00,
        "targetMeanPrice": 170.00,
        "recommendationKey": "buy",
    }


@pytest.fixture
def mock_yfinance_ticker(sample_fundamental_data):
    """Mock yfinance Ticker object with comprehensive data"""
    ticker = Mock()
    ticker.info = sample_fundamental_data

    # Mock history data
    import pandas as pd
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), periods=7, freq='D')
    hist_data = pd.DataFrame({
        'Open': [185.0, 186.0, 184.5, 185.5, 187.0, 186.5, 185.0],
        'High': [186.5, 187.0, 185.5, 186.5, 188.0, 187.5, 186.0],
        'Low': [184.0, 185.5, 183.5, 184.5, 186.0, 185.5, 184.0],
        'Close': [185.5, 186.5, 184.0, 186.0, 187.5, 186.0, 185.0],
        'Volume': [50000000, 45000000, 55000000, 48000000, 52000000, 46000000, 49000000]
    }, index=dates)
    ticker.history = Mock(return_value=hist_data)

    return ticker


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state between tests"""
    yield
    # Clean up any global state here if needed


# ============================================================================
# Hypothesis Configuration
# ============================================================================

from hypothesis import settings, Verbosity

# Configure Hypothesis profiles
settings.register_profile("ci", max_examples=100, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=10)
settings.register_profile("thorough", max_examples=1000, verbosity=Verbosity.verbose)

# Load profile from environment or use default
import os
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))


# ============================================================================
# Custom Assertions
# ============================================================================

def assert_valid_quote(quote):
    """Assert that a quote object has all required valid fields"""
    assert quote is not None
    assert quote.ticker is not None
    assert isinstance(quote.ticker, str)
    assert len(quote.ticker) > 0
    assert quote.price >= 0
    assert isinstance(quote.price, (int, float))
    assert quote.timestamp is not None
    assert isinstance(quote.timestamp, datetime)
    assert quote.provider is not None


def assert_valid_news_article(article):
    """Assert that a news article has all required valid fields"""
    assert article is not None
    assert article.title is not None
    assert isinstance(article.title, str)
    assert len(article.title) > 0
    assert article.url is not None
    assert article.published_at is not None
    assert isinstance(article.published_at, datetime)


def assert_valid_ohlcv_bar(bar):
    """Assert that an OHLCV bar has valid data"""
    assert bar is not None
    assert bar.high >= bar.low
    assert bar.high >= bar.open
    assert bar.high >= bar.close
    assert bar.low <= bar.open
    assert bar.low <= bar.close
    assert bar.volume >= 0
    assert bar.timestamp is not None


# Make custom assertions available to tests
pytest.assert_valid_quote = assert_valid_quote
pytest.assert_valid_news_article = assert_valid_news_article
pytest.assert_valid_ohlcv_bar = assert_valid_ohlcv_bar
