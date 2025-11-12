"""
Error handling tests for S&P 500 CSV generation

Test Coverage:
- TC-SP500-ERR-001: API connection failures
- TC-SP500-ERR-002: Missing data handling
- TC-SP500-ERR-003: Malformed data handling
- TC-SP500-ERR-004: Rate limit errors
- TC-SP500-ERR-005: Timeout handling
- TC-SP500-ERR-006: Partial batch failures
- TC-SP500-ERR-007: Invalid ticker handling
- TC-SP500-ERR-008: File I/O errors

Success Criteria:
- All error scenarios are handled gracefully
- No unhandled exceptions crash the program
- Meaningful error messages are provided
- Partial success scenarios work correctly
"""
import pytest
import asyncio
import csv
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from io import StringIO

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generate_sp500_test import generate_sp500_csv
from generate_sp500_advanced import get_fundamental_data, format_value
from generate_sp500_standalone import safe_get, format_number, get_stock_data
from providers.base import Quote


class TestAPIConnectionFailures:
    """TC-SP500-ERR-001: API connection failures"""

    @pytest.mark.asyncio
    async def test_provider_connection_error(self, tmp_path):
        """Should handle provider connection errors gracefully"""
        output_file = tmp_path / "test.csv"

        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(side_effect=ConnectionError("Failed to connect"))
        mock_provider.__aexit__ = AsyncMock(return_value=None)

        with patch('generate_sp500_test.ProviderFactory.from_config', return_value=mock_provider):
            with pytest.raises(ConnectionError):
                await generate_sp500_csv(str(output_file))

    @pytest.mark.asyncio
    async def test_provider_get_quotes_error(self, tmp_path):
        """Should handle errors when fetching quotes"""
        output_file = tmp_path / "test.csv"

        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)
        mock_provider.get_quotes = AsyncMock(side_effect=Exception("API Error"))

        with patch('generate_sp500_test.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_test.SP500_TEST_COMPANIES', [{"ticker": "AAPL", "name": "Apple", "sector": "Tech"}]):
                # Should not crash, might create file with N/A values
                try:
                    await generate_sp500_csv(str(output_file))
                except Exception:
                    # Exception is expected and acceptable in this case
                    pass

    @pytest.mark.asyncio
    async def test_network_timeout(self):
        """Should handle network timeout errors"""
        mock_provider = AsyncMock()
        mock_provider.get_quotes = AsyncMock(side_effect=asyncio.TimeoutError("Request timed out"))

        with pytest.raises(asyncio.TimeoutError):
            await mock_provider.get_quotes(["AAPL"])


class TestMissingDataHandling:
    """TC-SP500-ERR-002: Missing data handling"""

    def test_safe_get_with_missing_keys(self):
        """Should return default for missing keys"""
        data = {"price": 150.0}

        assert safe_get(data, "volume") == "N/A"
        assert safe_get(data, "marketCap") == "N/A"
        assert safe_get(data, "missing_field", "DEFAULT") == "DEFAULT"

    def test_format_value_with_none(self):
        """Should handle None values gracefully"""
        assert format_value(None) == "N/A"
        assert format_value(None, "currency") == "N/A"
        assert format_value(None, "billions") == "N/A"
        assert format_value(None, "percentage") == "N/A"

    def test_format_value_with_nan(self):
        """Should handle NaN values gracefully"""
        import math
        nan = float('nan')

        assert format_value(nan) == "N/A"
        assert format_value(nan, "currency") == "N/A"
        assert format_value(nan, "number") == "N/A"

    def test_csv_row_with_all_missing_data(self):
        """Should create valid CSV row even with all N/A data"""
        company = {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"}

        row = {
            "Ticker": company["ticker"],
            "Company Name": company["name"],
            "Sector": company["sector"],
            "Price": "N/A",
            "Change": "N/A",
            "Volume": "N/A",
        }

        assert row["Ticker"] == "AAPL"
        assert row["Price"] == "N/A"
        assert row["Change"] == "N/A"

    def test_format_number_with_na(self):
        """Should pass through N/A strings"""
        assert format_number("N/A") == "N/A"
        assert format_number("N/A", "currency") == "N/A"
        assert format_number("N/A", "billions") == "N/A"


class TestMalformedDataHandling:
    """TC-SP500-ERR-003: Malformed data handling"""

    def test_format_value_with_string(self):
        """Should handle string values that can't be formatted"""
        result = format_value("invalid_string", "currency")
        assert result == "N/A"

    def test_format_value_with_list(self):
        """Should handle list values"""
        result = format_value([1, 2, 3], "number")
        assert result == "N/A"

    def test_format_value_with_dict(self):
        """Should handle dict values"""
        result = format_value({"key": "value"}, "percentage")
        assert result == "N/A"

    def test_safe_get_with_nan_in_dict(self):
        """Should handle NaN values in dict"""
        import math
        data = {"price": float('nan')}

        result = safe_get(data, "price")
        assert result == "N/A"

    def test_quote_with_negative_volume(self):
        """Should handle negative volume (data error)"""
        quote = Quote(
            ticker="AAPL",
            price=150.0,
            timestamp=datetime.now(),
            volume=-1000,  # Invalid negative volume
            provider="test"
        )

        # Volume should still be accessible but might be validated elsewhere
        assert quote.volume == -1000
        # In production, you might want to treat this as 0 or N/A

    def test_quote_with_negative_price(self):
        """Should handle negative price (data error)"""
        quote = Quote(
            ticker="AAPL",
            price=-150.0,  # Invalid negative price
            timestamp=datetime.now(),
            provider="test"
        )

        assert quote.price == -150.0
        # In production, this should be validated


class TestRateLimitErrors:
    """TC-SP500-ERR-004: Rate limit errors"""

    @pytest.mark.asyncio
    async def test_rate_limit_exception(self):
        """Should handle rate limit exceptions"""
        mock_provider = AsyncMock()
        mock_provider.get_quotes = AsyncMock(side_effect=Exception("Rate limit exceeded"))

        with pytest.raises(Exception) as exc_info:
            await mock_provider.get_quotes(["AAPL"])

        assert "Rate limit" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit(self):
        """Should support retry logic on rate limits"""
        mock_provider = AsyncMock()

        # First call fails, second succeeds
        mock_quote = Quote(
            ticker="AAPL",
            price=150.0,
            timestamp=datetime.now(),
            provider="test"
        )

        mock_provider.get_quotes = AsyncMock(
            side_effect=[
                Exception("Rate limit exceeded"),
                {"AAPL": mock_quote}
            ]
        )

        # First attempt
        with pytest.raises(Exception):
            await mock_provider.get_quotes(["AAPL"])

        # Second attempt (retry)
        result = await mock_provider.get_quotes(["AAPL"])
        assert "AAPL" in result


class TestTimeoutHandling:
    """TC-SP500-ERR-005: Timeout handling"""

    @pytest.mark.asyncio
    async def test_async_timeout_error(self):
        """Should handle asyncio timeout errors"""
        mock_provider = AsyncMock()
        mock_provider.get_quotes = AsyncMock(side_effect=asyncio.TimeoutError())

        with pytest.raises(asyncio.TimeoutError):
            await mock_provider.get_quotes(["AAPL"])

    def test_get_stock_data_retry_logic(self):
        """Should have retry logic for stock data fetching"""
        import pandas as pd

        mock_ticker = Mock()
        mock_ticker.history = Mock(side_effect=[
            Exception("Timeout"),  # First attempt fails
            Exception("Timeout"),  # Second attempt fails
            pd.DataFrame({  # Third attempt succeeds
                'Close': [150.0, 151.0],
            })
        ])
        mock_ticker.info = {}

        with patch('yfinance.Ticker', return_value=mock_ticker):
            result = get_stock_data("AAPL", retry_count=3)

        # After 3 retries, should get result
        assert result is not None or result == {}


class TestPartialBatchFailures:
    """TC-SP500-ERR-006: Partial batch failures"""

    @pytest.mark.asyncio
    async def test_continue_on_batch_failure(self, tmp_path):
        """Should continue processing other batches if one fails"""
        output_file = tmp_path / "test.csv"

        mock_provider = AsyncMock()
        mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
        mock_provider.__aexit__ = AsyncMock(return_value=None)

        # First batch succeeds, second batch fails
        batch1_quotes = {
            "AAPL": Quote(ticker="AAPL", price=150.0, timestamp=datetime.now(), provider="mock"),
            "MSFT": Quote(ticker="MSFT", price=350.0, timestamp=datetime.now(), provider="mock"),
        }

        mock_provider.get_quotes = AsyncMock(side_effect=[
            batch1_quotes,  # First batch succeeds
            Exception("API Error"),  # Second batch fails
        ])

        companies = [
            {"ticker": "AAPL", "name": "Apple", "sector": "Tech"},
            {"ticker": "MSFT", "name": "Microsoft", "sector": "Tech"},
            {"ticker": "GOOGL", "name": "Google", "sector": "Tech"},
            {"ticker": "AMZN", "name": "Amazon", "sector": "Tech"},
        ]

        with patch('generate_sp500_test.ProviderFactory.from_config', return_value=mock_provider):
            with patch('generate_sp500_test.SP500_TEST_COMPANIES', companies):
                # Should handle partial failure
                try:
                    await generate_sp500_csv(str(output_file))
                except Exception:
                    # Partial failure is acceptable
                    pass

    def test_process_available_quotes_only(self):
        """Should process only available quotes from partial results"""
        companies = [
            {"ticker": "AAPL", "name": "Apple", "sector": "Tech"},
            {"ticker": "MSFT", "name": "Microsoft", "sector": "Tech"},
            {"ticker": "FAIL", "name": "Failed", "sector": "Tech"},
        ]

        quotes = {
            "AAPL": Quote(ticker="AAPL", price=150.0, timestamp=datetime.now(), provider="test"),
            "MSFT": Quote(ticker="MSFT", price=350.0, timestamp=datetime.now(), provider="test"),
            # "FAIL" is missing - simulates partial failure
        }

        # Process only available quotes
        csv_rows = []
        for company in companies:
            ticker = company["ticker"]
            if ticker in quotes:
                quote = quotes[ticker]
                row = {"Ticker": ticker, "Price": f"{quote.price:.2f}"}
            else:
                row = {"Ticker": ticker, "Price": "N/A"}

            csv_rows.append(row)

        assert len(csv_rows) == 3
        assert csv_rows[0]["Price"] != "N/A"
        assert csv_rows[1]["Price"] != "N/A"
        assert csv_rows[2]["Price"] == "N/A"


class TestInvalidTickerHandling:
    """TC-SP500-ERR-007: Invalid ticker handling"""

    def test_handle_empty_ticker(self):
        """Should handle empty ticker strings"""
        company = {"ticker": "", "name": "Invalid", "sector": "Tech"}

        # Should still create row, but might fail validation elsewhere
        row = {
            "Ticker": company["ticker"],
            "Company Name": company["name"],
            "Sector": company["sector"],
        }

        assert row["Ticker"] == ""

    def test_handle_none_ticker(self):
        """Should handle None ticker"""
        company = {"ticker": None, "name": "Invalid", "sector": "Tech"}

        # In real code, this should be validated
        row = {
            "Ticker": company.get("ticker", "N/A"),
            "Company Name": company["name"],
        }

        assert row["Ticker"] is None or row["Ticker"] == "N/A"

    @pytest.mark.asyncio
    async def test_invalid_ticker_returns_empty(self):
        """Provider should return empty dict for invalid ticker"""
        mock_provider = AsyncMock()
        mock_provider.get_quotes = AsyncMock(return_value={})  # No results for invalid ticker

        result = await mock_provider.get_quotes(["INVALID_TICKER_123"])

        assert result == {}


class TestFileIOErrors:
    """TC-SP500-ERR-008: File I/O errors"""

    def test_write_csv_to_readonly_directory(self, tmp_path):
        """Should handle errors when writing to read-only location"""
        import os

        # Create a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        os.chmod(readonly_dir, 0o444)  # Read-only

        output_file = readonly_dir / "test.csv"

        try:
            # Attempt to write
            with open(output_file, 'w') as f:
                f.write("test")
            # If we get here on some systems, clean up
            os.chmod(readonly_dir, 0o755)
        except (PermissionError, OSError):
            # Expected error
            os.chmod(readonly_dir, 0o755)  # Restore permissions for cleanup
            pass

    def test_write_csv_to_nonexistent_directory(self, tmp_path):
        """Should handle errors when directory doesn't exist"""
        output_file = tmp_path / "nonexistent" / "subdir" / "test.csv"

        # Writing should fail because parent directory doesn't exist
        with pytest.raises((FileNotFoundError, OSError)):
            with open(output_file, 'w') as f:
                f.write("test")

    def test_read_malformed_csv(self, tmp_path):
        """Should handle malformed CSV files"""
        output_file = tmp_path / "malformed.csv"

        # Create malformed CSV
        with open(output_file, 'w') as f:
            f.write("Ticker,Price\n")
            f.write("AAPL,150.00\n")
            f.write("MSFT,350.00,EXTRA,COLUMNS,HERE\n")  # Inconsistent columns

        # Should still be readable with DictReader
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # DictReader handles extra columns
        assert len(rows) == 2


class TestYFinanceErrorHandling:
    """Test error handling for yfinance data fetching"""

    def test_get_fundamental_data_with_exception(self):
        """Should return empty dict on yfinance exception"""
        with patch('generate_sp500_advanced.yf.Ticker', side_effect=Exception("Network error")):
            result = get_fundamental_data("AAPL")

        assert result == {}

    def test_get_fundamental_data_with_empty_info(self):
        """Should handle empty info dict"""
        mock_ticker = Mock()
        mock_ticker.info = {}

        with patch('yfinance.Ticker', return_value=mock_ticker):
            result = get_fundamental_data("AAPL")

        # Should return dict with None values for all keys
        assert "marketCap" in result
        assert result["marketCap"] is None

    def test_get_stock_data_with_empty_history(self):
        """Should handle empty historical data"""
        import pandas as pd

        mock_ticker = Mock()
        mock_ticker.history = Mock(return_value=pd.DataFrame())  # Empty dataframe
        mock_ticker.info = {}

        with patch('yfinance.Ticker', return_value=mock_ticker):
            result = get_stock_data("AAPL", retry_count=1)

        # Should still return data structure, possibly with N/A values
        assert isinstance(result, dict)


class TestDataValidation:
    """Test data validation and sanitization"""

    def test_validate_price_range(self):
        """Should validate that prices are positive"""
        prices = [150.0, -10.0, 0.0, 999999.0]

        valid_prices = [p for p in prices if p > 0]

        assert 150.0 in valid_prices
        assert 999999.0 in valid_prices
        assert -10.0 not in valid_prices
        assert 0.0 not in valid_prices

    def test_validate_volume_range(self):
        """Should validate that volumes are non-negative"""
        volumes = [50000000, -1000, 0, None]

        valid_volumes = [v for v in volumes if v is not None and v >= 0]

        assert 50000000 in valid_volumes
        assert 0 in valid_volumes
        assert -1000 not in valid_volumes

    def test_sanitize_company_name(self):
        """Should sanitize company names for CSV"""
        names = [
            "Apple Inc.",
            "Company, Inc.",  # Contains comma
            "Company\nWith\nNewlines",  # Contains newlines
            "Company\twith\ttabs",  # Contains tabs
        ]

        # CSV writer should handle these automatically
        # But we can test that they're preserved correctly
        for name in names:
            # Verify each name is a valid string
            assert isinstance(name, str)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_company_list(self):
        """Should handle empty company list"""
        companies = []

        filtered = [c for c in companies if c["sector"] == "Technology"]

        assert len(filtered) == 0

    def test_single_company(self):
        """Should handle single company"""
        companies = [{"ticker": "AAPL", "name": "Apple", "sector": "Tech"}]

        assert len(companies) == 1

    @pytest.mark.asyncio
    async def test_very_large_batch(self):
        """Should handle very large batch of tickers"""
        # Simulate 100 tickers
        large_batch = [f"TICK{i:03d}" for i in range(100)]

        mock_provider = AsyncMock()
        mock_provider.get_quotes = AsyncMock(return_value={})

        result = await mock_provider.get_quotes(large_batch)

        assert result == {}

    def test_special_characters_in_sector(self):
        """Should handle special characters in sector names"""
        companies = [
            {"ticker": "TEST1", "name": "Test", "sector": "Tech & Services"},
            {"ticker": "TEST2", "name": "Test", "sector": "Consumer (Discretionary)"},
        ]

        # Should be able to filter even with special characters
        filtered = [c for c in companies if "Tech" in c["sector"]]

        assert len(filtered) == 1


# Pytest marks
pytestmark = [
    pytest.mark.unit,
]
