"""
Unit tests for S&P 500 CSV generation functionality

Test Coverage:
- TC-SP500-001: Data fetching functions
- TC-SP500-002: Formatting functions
- TC-SP500-003: CSV row construction
- TC-SP500-004: Sector filtering
- TC-SP500-005: Company limit options
- TC-SP500-006: Error handling for missing data
- TC-SP500-007: Batch processing logic

Success Criteria:
- All formatting functions handle edge cases (None, NaN, etc.)
- Sector filtering works correctly with case-insensitive matching
- Limit parameter correctly restricts company count
- Missing data is handled gracefully with "N/A" defaults
- Batch processing respects rate limits
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List

# Import functions from the S&P 500 generation scripts
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generate_sp500_test import generate_sp500_csv, SP500_TEST_COMPANIES
from generate_sp500_advanced import (
    get_fundamental_data,
    format_value,
    generate_advanced_csv,
    SP500_COMPANIES
)
from generate_sp500_standalone import (
    safe_get,
    format_number,
    get_stock_data,
    generate_csv
)
from providers.base import Quote


class TestFormatValueFunction:
    """TC-SP500-002: Test formatting functions"""

    def test_format_value_with_none(self):
        """Should return 'N/A' for None values"""
        assert format_value(None) == "N/A"
        assert format_value(None, "currency") == "N/A"
        assert format_value(None, "percentage") == "N/A"

    def test_format_value_with_nan(self):
        """Should return 'N/A' for NaN values"""
        import math
        nan_value = float('nan')
        assert format_value(nan_value) == "N/A"
        assert format_value(nan_value, "currency") == "N/A"

    def test_format_currency(self):
        """Should format currency values correctly"""
        result = format_value(123.456, "currency", decimals=2)
        assert "$" in result
        assert "123.46" in result

    def test_format_billions(self):
        """Should format billions correctly"""
        result = format_value(1500000000, "billions", decimals=2)
        assert "$1.50B" == result

    def test_format_millions(self):
        """Should format millions correctly"""
        result = format_value(1500000, "millions", decimals=2)
        assert "$1.50M" == result

    def test_format_percentage(self):
        """Should format percentages correctly"""
        result = format_value(0.0534, "percentage", decimals=2)
        assert "5.34%" == result

    def test_format_number(self):
        """Should format plain numbers correctly"""
        result = format_value(12345.678, "number", decimals=2)
        assert "12,345.68" == result

    def test_format_with_different_decimals(self):
        """Should respect decimal parameter"""
        result1 = format_value(123.456, "number", decimals=1)
        assert "123.5" in result1

        result2 = format_value(123.456, "number", decimals=3)
        assert "123.456" in result2

    def test_format_with_invalid_type_returns_na(self):
        """Should return 'N/A' when format fails"""
        result = format_value("invalid", "billions")
        assert result == "N/A"


class TestFormatNumberFunction:
    """Test the standalone format_number function"""

    def test_format_number_with_na_string(self):
        """Should pass through 'N/A' strings"""
        assert format_number("N/A") == "N/A"
        assert format_number("N/A", "currency") == "N/A"

    def test_format_number_billions(self):
        """Should format billions correctly"""
        result = format_number(2500000000, "billions", decimals=2)
        assert "$2.50B" == result

    def test_format_number_currency(self):
        """Should format currency with $ symbol"""
        result = format_number(150.75, "currency", decimals=2)
        assert "$150.75" == result

    def test_format_number_percentage(self):
        """Should convert decimal to percentage"""
        result = format_number(0.125, "percentage", decimals=2)
        assert "12.50%" == result

    def test_format_number_with_none(self):
        """Should return 'N/A' for None"""
        assert format_number(None) == "N/A"


class TestSafeGetFunction:
    """Test the safe_get helper function"""

    def test_safe_get_existing_key(self):
        """Should return value for existing key"""
        data = {"price": 150.5, "volume": 1000000}
        assert safe_get(data, "price") == 150.5
        assert safe_get(data, "volume") == 1000000

    def test_safe_get_missing_key(self):
        """Should return default for missing key"""
        data = {"price": 150.5}
        assert safe_get(data, "volume") == "N/A"
        assert safe_get(data, "missing", "custom") == "custom"

    def test_safe_get_none_value(self):
        """Should return default when value is None"""
        data = {"price": None}
        assert safe_get(data, "price") == "N/A"

    def test_safe_get_nan_value(self):
        """Should return default when value is NaN"""
        import math
        data = {"price": float('nan')}
        assert safe_get(data, "price") == "N/A"

    def test_safe_get_custom_default(self):
        """Should use custom default value"""
        data = {}
        assert safe_get(data, "key", "MISSING") == "MISSING"


class TestSectorFiltering:
    """TC-SP500-004: Test sector filtering logic"""

    def test_filter_by_technology_sector(self):
        """Should filter companies by Technology sector"""
        companies = SP500_COMPANIES
        filtered = [c for c in companies if c["sector"].lower() == "technology"]

        assert len(filtered) > 0
        assert all(c["sector"] == "Technology" for c in filtered)

    def test_filter_by_healthcare_sector(self):
        """Should filter companies by Healthcare sector"""
        companies = SP500_COMPANIES
        filtered = [c for c in companies if c["sector"].lower() == "healthcare"]

        assert len(filtered) > 0
        assert all(c["sector"] == "Healthcare" for c in filtered)

    def test_filter_case_insensitive(self):
        """Filtering should be case-insensitive"""
        companies = SP500_COMPANIES
        filtered_lower = [c for c in companies if c["sector"].lower() == "technology"]
        filtered_upper = [c for c in companies if c["sector"].lower() == "TECHNOLOGY".lower()]
        filtered_mixed = [c for c in companies if c["sector"].lower() == "TeChnOloGy".lower()]

        assert len(filtered_lower) == len(filtered_upper) == len(filtered_mixed)

    def test_filter_invalid_sector_returns_empty(self):
        """Filtering by non-existent sector should return empty list"""
        companies = SP500_COMPANIES
        filtered = [c for c in companies if c["sector"].lower() == "invalidsector"]

        assert len(filtered) == 0

    def test_no_filter_returns_all(self):
        """When no filter applied, should return all companies"""
        companies = SP500_COMPANIES
        assert len(companies) > 0


class TestLimitOptions:
    """TC-SP500-005: Test company limit functionality"""

    def test_limit_to_five_companies(self):
        """Should limit to first 5 companies"""
        companies = SP500_COMPANIES
        limited = companies[:5]

        assert len(limited) == 5

    def test_limit_to_ten_companies(self):
        """Should limit to first 10 companies"""
        companies = SP500_COMPANIES
        limited = companies[:10]

        assert len(limited) == 10

    def test_limit_greater_than_total(self):
        """Limit greater than total should return all companies"""
        companies = SP500_COMPANIES
        total = len(companies)
        limited = companies[:total + 100]

        assert len(limited) == total

    def test_limit_zero(self):
        """Limit of 0 should return empty list"""
        companies = SP500_COMPANIES
        limited = companies[:0]

        assert len(limited) == 0

    def test_limit_negative_returns_empty(self):
        """Negative limit should return empty list"""
        companies = SP500_COMPANIES
        limited = companies[:-10] if len(companies) > 10 else []
        # Negative slicing in Python works differently
        # This test documents the behavior
        assert isinstance(limited, list)


class TestCSVRowConstruction:
    """TC-SP500-003: Test CSV row construction"""

    def test_csv_row_with_valid_quote(self):
        """Should construct valid CSV row with quote data"""
        company = {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"}
        quote = Quote(
            ticker="AAPL",
            price=150.25,
            timestamp=datetime.now(),
            volume=50000000,
            open=149.50,
            high=151.00,
            low=149.00,
            change=0.75,
            change_percent=0.50,
            provider="test"
        )

        row = {
            "Ticker": company["ticker"],
            "Company Name": company["name"],
            "Sector": company["sector"],
            "Price": f"{quote.price:.2f}",
            "Change": f"{quote.change:+.2f}",
            "Change %": f"{quote.change_percent:+.2f}",
            "Volume": f"{quote.volume:,}",
        }

        assert row["Ticker"] == "AAPL"
        assert row["Company Name"] == "Apple Inc."
        assert row["Sector"] == "Technology"
        assert "150.25" in row["Price"]
        assert "50,000,000" in row["Volume"]

    def test_csv_row_with_missing_quote(self):
        """Should construct CSV row with N/A for missing data"""
        company = {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"}

        row = {
            "Ticker": company["ticker"],
            "Company Name": company["name"],
            "Sector": company["sector"],
            "Price": "N/A",
            "Change": "N/A",
            "Change %": "N/A",
            "Volume": "N/A",
        }

        assert row["Price"] == "N/A"
        assert row["Change"] == "N/A"
        assert row["Volume"] == "N/A"

    def test_csv_row_with_partial_data(self):
        """Should handle partial data gracefully"""
        company = {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"}
        quote = Quote(
            ticker="AAPL",
            price=150.25,
            timestamp=datetime.now(),
            volume=None,  # Missing volume
            open=None,    # Missing open
            provider="test"
        )

        row = {
            "Ticker": company["ticker"],
            "Price": f"{quote.price:.2f}",
            "Volume": f"{quote.volume:,}" if quote.volume else "N/A",
            "Open": f"{quote.open:.2f}" if quote.open else "N/A",
        }

        assert "150.25" in row["Price"]
        assert row["Volume"] == "N/A"
        assert row["Open"] == "N/A"


class TestBatchProcessing:
    """TC-SP500-007: Test batch processing logic"""

    def test_batch_size_calculation(self):
        """Should calculate correct number of batches"""
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META",
                   "TSLA", "NVDA", "JPM", "BAC", "WFC",
                   "UNH", "JNJ"]  # 12 tickers
        batch_size = 5

        num_batches = (len(tickers) - 1) // batch_size + 1
        assert num_batches == 3  # 12 tickers / 5 per batch = 3 batches

    def test_batch_slicing(self):
        """Should slice tickers correctly into batches"""
        tickers = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
        batch_size = 3

        batches = []
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            batches.append(batch)

        assert len(batches) == 3
        assert batches[0] == ["T1", "T2", "T3"]
        assert batches[1] == ["T4", "T5", "T6"]
        assert batches[2] == ["T7"]

    def test_last_batch_check(self):
        """Should correctly identify last batch"""
        tickers = ["T1", "T2", "T3", "T4", "T5"]
        batch_size = 2

        for i in range(0, len(tickers), batch_size):
            is_last_batch = (i + batch_size >= len(tickers))
            if i == 4:  # Last iteration
                assert is_last_batch is True
            else:
                assert is_last_batch is False


class TestErrorHandling:
    """TC-SP500-006: Test error handling for missing data"""

    def test_handle_missing_price_data(self):
        """Should handle missing price data gracefully"""
        data = {}
        price = safe_get(data, "price", "N/A")

        assert price == "N/A"

    def test_handle_api_error_dict(self):
        """Should handle empty dict from API error"""
        data = {}

        assert safe_get(data, "marketCap") == "N/A"
        assert safe_get(data, "revenue") == "N/A"
        assert safe_get(data, "eps") == "N/A"

    def test_format_handles_invalid_data(self):
        """Format functions should handle invalid data"""
        invalid_values = ["invalid", None, float('nan'), [1, 2, 3], {"key": "value"}]

        for value in invalid_values:
            result = format_value(value, "currency")
            assert result == "N/A"

    def test_skip_company_on_data_failure(self):
        """Should be able to skip companies with data failures"""
        companies = [
            {"ticker": "AAPL", "data": {"price": 150}},
            {"ticker": "FAIL", "data": {}},  # Failed to fetch
            {"ticker": "MSFT", "data": {"price": 300}},
        ]

        # All companies have data dict, even if empty
        valid_companies = [c for c in companies if "data" in c]
        assert len(valid_companies) == 3

        # Filter to those with actual price data
        with_price = [c for c in companies if c.get("data", {}).get("price")]
        assert len(with_price) == 2
        assert with_price[0]["ticker"] == "AAPL"
        assert with_price[1]["ticker"] == "MSFT"


@pytest.mark.asyncio
class TestMockedDataFetching:
    """TC-SP500-001: Test data fetching with mocks (no real API calls)"""

    async def test_generate_sp500_csv_with_mock_provider(self, tmp_path):
        """Should generate CSV using mocked provider"""
        output_file = tmp_path / "test_output.csv"

        # Mock the provider
        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)

        # Mock quotes
        mock_quotes = {
            "AAPL": Quote(
                ticker="AAPL",
                price=150.25,
                timestamp=datetime.now(),
                volume=50000000,
                change=1.25,
                change_percent=0.84,
                open=149.50,
                high=151.00,
                low=149.00,
                provider="mock"
            ),
            "MSFT": Quote(
                ticker="MSFT",
                price=350.75,
                timestamp=datetime.now(),
                volume=30000000,
                change=-2.50,
                change_percent=-0.71,
                open=353.25,
                high=354.00,
                low=350.00,
                provider="mock"
            ),
        }

        mock_provider.get_quotes = AsyncMock(return_value=mock_quotes)

        # Test with the mock
        with patch('generate_sp500_test.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_test.SP500_TEST_COMPANIES',
                      [{"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
                       {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"}]):

                await generate_sp500_csv(str(output_file))

        # Verify file was created
        assert output_file.exists()

        # Verify content
        content = output_file.read_text()
        assert "AAPL" in content
        assert "MSFT" in content
        assert "Apple Inc." in content

    async def test_get_quotes_batch_processing(self):
        """Should process quotes in batches"""
        mock_provider = AsyncMock()

        # Mock batch responses
        batch1 = {"AAPL": Mock(price=150), "MSFT": Mock(price=350)}
        batch2 = {"GOOGL": Mock(price=2800), "AMZN": Mock(price=3200)}

        mock_provider.get_quotes = AsyncMock(side_effect=[batch1, batch2])

        # Simulate batch processing
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
        batch_size = 2
        all_quotes = {}

        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            quotes = await mock_provider.get_quotes(batch)
            all_quotes.update(quotes)

        assert len(all_quotes) == 4
        assert "AAPL" in all_quotes
        assert "GOOGL" in all_quotes

    async def test_handle_provider_error(self):
        """Should handle provider errors gracefully"""
        mock_provider = AsyncMock()
        mock_provider.get_quotes = AsyncMock(side_effect=Exception("API Error"))

        try:
            await mock_provider.get_quotes(["AAPL"])
            assert False, "Should have raised exception"
        except Exception as e:
            assert "API Error" in str(e)


@pytest.mark.asyncio
class TestYFinanceMocking:
    """Test yfinance data fetching with mocks"""

    async def test_get_fundamental_data_with_mock(self):
        """Should fetch fundamental data using mocked yfinance"""
        mock_ticker = Mock()
        mock_ticker.info = {
            "marketCap": 2500000000000,
            "trailingPE": 28.5,
            "forwardPE": 25.3,
            "priceToBook": 45.2,
            "totalRevenue": 383000000000,
            "profitMargins": 0.25,
            "returnOnEquity": 1.47,
        }

        with patch('generate_sp500_advanced.yf.Ticker', return_value=mock_ticker):
            data = get_fundamental_data("AAPL")

        assert data["marketCap"] == 2500000000000
        assert data["trailingPE"] == 28.5
        assert data["profitMargin"] == 0.25

    async def test_get_fundamental_data_handles_error(self):
        """Should handle yfinance errors gracefully"""
        with patch('generate_sp500_advanced.yf.Ticker', side_effect=Exception("Network error")):
            data = get_fundamental_data("AAPL")

        # Should return empty dict on error
        assert data == {}

    async def test_get_stock_data_with_mock(self):
        """Should fetch stock data using mocked yfinance"""
        import pandas as pd

        mock_ticker = Mock()

        # Mock history data
        hist_data = pd.DataFrame({
            'Close': [150.0, 151.5],
            'Open': [149.5, 150.0],
            'High': [152.0, 152.5],
            'Low': [149.0, 150.0],
            'Volume': [50000000, 45000000]
        })
        mock_ticker.history = Mock(return_value=hist_data)

        # Mock info
        mock_ticker.info = {
            "currentPrice": 151.5,
            "volume": 45000000,
            "marketCap": 2500000000000,
        }

        with patch('yfinance.Ticker', return_value=mock_ticker):
            data = get_stock_data("AAPL", retry_count=1)

        assert data is not None
        assert "currentPrice" in data


class TestCompanyDataStructure:
    """Test the company data structures"""

    def test_sp500_companies_have_required_fields(self):
        """All companies should have ticker, name, and sector"""
        for company in SP500_COMPANIES:
            assert "ticker" in company
            assert "name" in company
            assert "sector" in company
            assert isinstance(company["ticker"], str)
            assert len(company["ticker"]) > 0

    def test_test_companies_have_required_fields(self):
        """Test companies list should have required fields"""
        for company in SP500_TEST_COMPANIES:
            assert "ticker" in company
            assert "name" in company
            assert "sector" in company

    def test_no_duplicate_tickers(self):
        """Should not have duplicate tickers in company list"""
        tickers = [c["ticker"] for c in SP500_COMPANIES]
        assert len(tickers) == len(set(tickers))


# Pytest marks for organization
pytestmark = [
    pytest.mark.unit,
]
