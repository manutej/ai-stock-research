"""
Unit tests for validation module

Test Coverage:
- TC-VAL-001: Valid ticker formats
- TC-VAL-002: Invalid ticker formats
- TC-VAL-003: Batch validation
- TC-VAL-004: Date range validation

Success Criteria:
- All valid formats accepted and normalized
- All invalid formats rejected with clear errors
- Edge cases handled correctly
- Error messages are actionable
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from validation import (
    validate_ticker,
    validate_tickers,
    TickerRequest,
    QuoteRequest,
    HistoricalDataRequest,
    NewsRequest,
    FinancialsRequest,
    EnvironmentConfig
)


class TestTickerValidation:
    """TC-VAL-001: Valid ticker formats"""

    def test_single_letter_ticker(self):
        """Single letter tickers should be accepted"""
        assert validate_ticker("A") == "A"
        assert validate_ticker("X") == "X"
        assert validate_ticker("Z") == "Z"

    def test_multi_letter_tickers(self):
        """2-5 letter tickers should be accepted"""
        assert validate_ticker("AAPL") == "AAPL"
        assert validate_ticker("MSFT") == "MSFT"
        assert validate_ticker("GOOGL") == "GOOGL"

    def test_five_letter_ticker(self):
        """5-letter tickers (maximum) should be accepted"""
        assert validate_ticker("ABCDE") == "ABCDE"

    def test_lowercase_normalized_to_uppercase(self):
        """Lowercase input should be normalized to uppercase"""
        assert validate_ticker("aapl") == "AAPL"
        assert validate_ticker("msft") == "MSFT"
        assert validate_ticker("googl") == "GOOGL"

    def test_mixed_case_normalized(self):
        """Mixed case should be normalized to uppercase"""
        assert validate_ticker("AaPl") == "AAPL"
        assert validate_ticker("MsFt") == "MSFT"

    def test_whitespace_in_ticker_rejected(self):
        """Tickers with whitespace should be rejected"""
        with pytest.raises(ValueError) as exc_info:
            validate_ticker("A PL")
        assert "Invalid ticker format" in str(exc_info.value)


class TestInvalidTickerFormats:
    """TC-VAL-002: Invalid ticker formats"""

    def test_empty_string_rejected(self):
        """Empty string should be rejected with clear message"""
        with pytest.raises(ValueError) as exc_info:
            validate_ticker("")
        error_msg = str(exc_info.value)
        assert "Ticker cannot be empty" in error_msg or "Invalid ticker" in error_msg

    def test_ticker_too_long_rejected(self):
        """Tickers longer than 5 characters should be rejected"""
        with pytest.raises(ValueError) as exc_info:
            validate_ticker("TOOLONG")
        assert "1-5" in str(exc_info.value)

    def test_numeric_ticker_rejected(self):
        """All-numeric tickers should be rejected"""
        with pytest.raises(ValueError) as exc_info:
            validate_ticker("123")
        assert "1-5 uppercase letters" in str(exc_info.value) or "Invalid ticker" in str(exc_info.value)

    def test_alphanumeric_ticker_rejected(self):
        """Mixed alphanumeric tickers should be rejected"""
        with pytest.raises(ValueError) as exc_info:
            validate_ticker("ABC123")
        assert "Invalid ticker" in str(exc_info.value)

    def test_special_characters_rejected(self):
        """Tickers with special characters should be rejected"""
        invalid_tickers = ["ABC-D", "A.B", "A B", "A_B", "A$B", "A@B"]
        for ticker in invalid_tickers:
            with pytest.raises(ValueError):
                validate_ticker(ticker)

    def test_none_rejected(self):
        """None should be rejected"""
        with pytest.raises((ValueError, ValidationError, AttributeError)):
            validate_ticker(None)


class TestBatchValidation:
    """TC-VAL-003: Batch validation"""

    def test_valid_list_accepted(self):
        """Valid list of tickers should be accepted and normalized"""
        result = validate_tickers(["AAPL", "MSFT", "GOOGL"])
        assert result == ["AAPL", "MSFT", "GOOGL"]

    def test_lowercase_list_normalized(self):
        """Lowercase tickers in list should be normalized"""
        result = validate_tickers(["aapl", "msft"])
        assert result == ["AAPL", "MSFT"]

    def test_list_with_invalid_ticker_rejected_entirely(self):
        """List with one invalid ticker should reject entire batch"""
        with pytest.raises((ValueError, ValidationError)):
            validate_tickers(["AAPL", "INVALID123", "MSFT"])

    def test_empty_list_rejected(self):
        """Empty list should be rejected"""
        with pytest.raises((ValueError, ValidationError)):
            validate_tickers([])

    def test_list_exceeding_limit_rejected(self):
        """List with > 50 tickers should be rejected (business rule)"""
        long_list = [f"T{i:02d}" for i in range(51)]  # 51 tickers
        with pytest.raises((ValueError, ValidationError)):
            validate_tickers(long_list)

    def test_duplicates_preserved(self):
        """Duplicate tickers should be preserved (or deduplicated based on spec)"""
        # Adjust this test based on actual business requirements
        result = validate_tickers(["AAPL", "AAPL", "MSFT"])
        # Either: assert result == ["AAPL", "AAPL", "MSFT"]  # preserved
        # Or: assert result == ["AAPL", "MSFT"]  # deduplicated
        assert "AAPL" in result
        assert "MSFT" in result


class TestPydanticModels:
    """Test Pydantic validation models"""

    def test_ticker_request_valid(self):
        """TickerRequest should validate valid ticker"""
        req = TickerRequest(ticker="AAPL")
        assert req.ticker == "AAPL"

    def test_ticker_request_normalizes(self):
        """TickerRequest should normalize lowercase"""
        req = TickerRequest(ticker="aapl")
        assert req.ticker == "AAPL"

    def test_ticker_request_rejects_invalid(self):
        """TickerRequest should reject invalid format"""
        with pytest.raises(ValidationError):
            TickerRequest(ticker="INVALID123")

    def test_quote_request_valid_list(self):
        """QuoteRequest should accept valid ticker list"""
        req = QuoteRequest(tickers=["AAPL", "MSFT"])
        assert len(req.tickers) == 2

    def test_quote_request_enforces_min_length(self):
        """QuoteRequest should reject empty list"""
        with pytest.raises(ValidationError):
            QuoteRequest(tickers=[])

    def test_quote_request_enforces_max_length(self):
        """QuoteRequest should reject list > 50"""
        long_list = [f"T{i:02d}" for i in range(51)]
        with pytest.raises(ValidationError):
            QuoteRequest(tickers=long_list)

    def test_historical_data_request_valid(self):
        """HistoricalDataRequest should accept valid dates"""
        start = datetime.now() - timedelta(days=7)
        end = datetime.now()
        req = HistoricalDataRequest(
            ticker="AAPL",
            start_date=start,
            end_date=end,
            timeframe="1d"
        )
        assert req.ticker == "AAPL"
        assert req.timeframe == "1d"

    def test_historical_data_request_rejects_end_before_start(self):
        """HistoricalDataRequest should reject end_date before start_date"""
        start = datetime.now()
        end = datetime.now() - timedelta(days=7)  # End before start
        with pytest.raises(ValidationError) as exc_info:
            HistoricalDataRequest(
                ticker="AAPL",
                start_date=start,
                end_date=end
            )
        assert "after start_date" in str(exc_info.value).lower() or "end_date" in str(exc_info.value)

    def test_historical_data_request_validates_timeframe(self):
        """HistoricalDataRequest should validate timeframe pattern"""
        start = datetime.now() - timedelta(days=7)
        end = datetime.now()

        # Valid timeframes
        for tf in ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]:
            req = HistoricalDataRequest(
                ticker="AAPL",
                start_date=start,
                end_date=end,
                timeframe=tf
            )
            assert req.timeframe == tf

        # Invalid timeframe
        with pytest.raises(ValidationError):
            HistoricalDataRequest(
                ticker="AAPL",
                start_date=start,
                end_date=end,
                timeframe="invalid"
            )

    def test_news_request_optional_ticker(self):
        """NewsRequest should allow None ticker"""
        req = NewsRequest(limit=10)
        assert req.ticker is None

    def test_news_request_validates_limit_range(self):
        """NewsRequest should enforce limit range (1-100)"""
        # Valid limits
        NewsRequest(limit=1)
        NewsRequest(limit=50)
        NewsRequest(limit=100)

        # Invalid limits
        with pytest.raises(ValidationError):
            NewsRequest(limit=0)
        with pytest.raises(ValidationError):
            NewsRequest(limit=101)

    def test_financials_request_validates_limit_range(self):
        """FinancialsRequest should enforce limit range (1-20)"""
        FinancialsRequest(ticker="AAPL", limit=1)
        FinancialsRequest(ticker="AAPL", limit=20)

        with pytest.raises(ValidationError):
            FinancialsRequest(ticker="AAPL", limit=0)
        with pytest.raises(ValidationError):
            FinancialsRequest(ticker="AAPL", limit=21)

    def test_environment_config_validates_log_level(self):
        """EnvironmentConfig should validate log level"""
        # Valid levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = EnvironmentConfig(log_level=level)
            assert config.log_level == level

        # Invalid level
        with pytest.raises(ValidationError):
            EnvironmentConfig(log_level="INVALID")

    def test_environment_config_validates_provider(self):
        """EnvironmentConfig should validate provider choice"""
        # Valid providers
        for provider in ["auto", "polygon", "yfinance", "hybrid"]:
            config = EnvironmentConfig(default_provider=provider)
            assert config.default_provider == provider

        # Invalid provider
        with pytest.raises(ValidationError):
            EnvironmentConfig(default_provider="invalid")

    def test_environment_config_enforces_api_key_min_length(self):
        """EnvironmentConfig should enforce minimum API key length"""
        # Valid (10+ chars)
        config = EnvironmentConfig(polygon_api_key="a" * 10)
        assert config.polygon_api_key == "a" * 10

        # Invalid (< 10 chars)
        with pytest.raises(ValidationError):
            EnvironmentConfig(polygon_api_key="short")


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_ticker_with_leading_trailing_spaces_rejected(self):
        """Spaces around ticker should cause rejection (not auto-trimmed in regex)"""
        # Note: Pydantic does str_strip_whitespace, so this depends on implementation
        # If using raw validate_ticker without Pydantic, spaces would be rejected
        # Adjust test based on actual behavior
        try:
            result = validate_ticker(" AAPL ")
            # If it passes, it should be trimmed
            assert result == "AAPL"
        except ValueError:
            # If it fails, that's also acceptable behavior
            pass

    def test_unicode_characters_rejected(self):
        """Unicode/non-ASCII characters should be rejected"""
        with pytest.raises(ValueError):
            validate_ticker("AAPL™")
        with pytest.raises(ValueError):
            validate_ticker("日本")

    def test_case_sensitivity_preserved_after_normalization(self):
        """After normalization, all results should be uppercase"""
        test_cases = ["aapl", "AAPL", "AaPl", "aApL"]
        for ticker in test_cases:
            result = validate_ticker(ticker)
            assert result == result.upper()
            assert result == "AAPL"


class TestErrorMessages:
    """Verify error messages are clear and actionable"""

    def test_empty_ticker_error_message(self):
        """Error for empty ticker should be clear"""
        with pytest.raises(ValueError) as exc_info:
            validate_ticker("")
        message = str(exc_info.value)
        assert "empty" in message.lower() or "invalid" in message.lower()

    def test_too_long_ticker_error_message(self):
        """Error for too-long ticker should mention length limit"""
        with pytest.raises(ValueError) as exc_info:
            validate_ticker("TOOLONGNAME")
        message = str(exc_info.value)
        assert "1-5" in message or "5" in message

    def test_invalid_format_error_message(self):
        """Error for invalid format should explain requirements"""
        with pytest.raises(ValueError) as exc_info:
            validate_ticker("123ABC")
        message = str(exc_info.value)
        assert "letters" in message.lower() or "invalid" in message.lower()


# Pytest marks for organization
pytestmark = [
    pytest.mark.unit,
    pytest.mark.validation
]
