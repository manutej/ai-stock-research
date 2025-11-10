"""
Property-based tests for validation module using Hypothesis

These tests use property-based testing to automatically generate edge cases
and verify that invariants hold across a wide range of inputs.

Success Criteria:
- Properties hold for all generated inputs
- Edge cases automatically discovered
- No failures in 100+ generated examples per test
"""
import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta

from validation import (
    validate_ticker,
    validate_tickers,
    TickerRequest,
    QuoteRequest,
    HistoricalDataRequest
)


# Custom strategies for generating test data

# Valid ticker: 1-5 uppercase ASCII letters (A-Z only)
valid_ticker_strategy = st.text(
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ',  # ASCII uppercase only
    min_size=1,
    max_size=5
)

# Invalid ticker: either too long, has numbers, or special characters
invalid_ticker_strategy = st.one_of(
    # Too long
    st.text(min_size=6, max_size=20),
    # Contains numbers
    st.from_regex(r'[A-Z]*[0-9]+[A-Z0-9]*', fullmatch=True),
    # Contains special characters
    st.from_regex(r'[A-Z]*[^A-Z0-9]+[A-Z]*', fullmatch=True),
    # Empty
    st.just("")
)


class TestTickerValidationProperties:
    """Property tests for ticker validation"""

    @given(valid_ticker_strategy)
    @settings(max_examples=200)
    def test_all_valid_tickers_accepted(self, ticker: str):
        """
        Property: Any 1-5 uppercase letter string should be valid

        This tests the positive case - all strings matching the pattern
        should be accepted and normalized correctly.
        """
        result = validate_ticker(ticker)

        # Postconditions
        assert result == ticker, "Valid ticker should be returned as-is"
        assert result.isupper(), "Result should be uppercase"
        assert 1 <= len(result) <= 5, "Result should be 1-5 characters"
        assert result.isalpha(), "Result should contain only letters"

    @given(st.text(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=1, max_size=5))
    @settings(max_examples=200)
    def test_case_normalization_property(self, ticker: str):
        """
        Property: Any valid ticker in any case should normalize to uppercase

        Tests that case normalization works correctly for all valid inputs.
        """
        # Only test if it's all letters
        assume(ticker.isalpha())

        result = validate_ticker(ticker)

        # Should be normalized to uppercase
        assert result == ticker.upper()
        assert result.isupper()

    @given(st.text(min_size=6, max_size=100))
    @settings(max_examples=100)
    def test_long_tickers_always_rejected(self, ticker: str):
        """
        Property: Any string > 5 characters should be rejected

        This is a negative property test - all inputs should fail.
        """
        with pytest.raises(ValueError) as exc_info:
            validate_ticker(ticker)

        # Error message should mention length
        error_msg = str(exc_info.value)
        assert "1-5" in error_msg or "5" in error_msg or "Invalid" in error_msg

    @given(st.from_regex(r'[0-9]+', fullmatch=True))
    @settings(max_examples=100)
    def test_numeric_tickers_always_rejected(self, ticker: str):
        """
        Property: All-numeric strings should be rejected
        """
        with pytest.raises(ValueError):
            validate_ticker(ticker)

    @given(st.from_regex(r'[A-Za-z]*[^A-Za-z0-9]+[A-Za-z]*', fullmatch=True))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
    def test_special_characters_rejected(self, ticker: str):
        """
        Property: Strings with special characters should be rejected
        """
        # Skip if it happens to match valid pattern
        assume(not ticker.isalpha() or len(ticker) > 5)

        with pytest.raises(ValueError):
            validate_ticker(ticker)


class TestBatchValidationProperties:
    """Property tests for batch ticker validation"""

    @given(st.lists(valid_ticker_strategy, min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_valid_list_preserves_all_tickers(self, tickers: list):
        """
        Property: Valid list should preserve all tickers (after normalization)
        """
        result = validate_tickers(tickers)

        # Should have same length
        assert len(result) == len(tickers)

        # All should be uppercase
        assert all(t.isupper() for t in result)

        # All should be in valid format
        assert all(1 <= len(t) <= 5 and t.isalpha() for t in result)

    @given(st.lists(valid_ticker_strategy, min_size=51, max_size=100))
    @settings(max_examples=50)
    def test_list_over_limit_rejected(self, tickers: list):
        """
        Property: Lists with > 50 tickers should be rejected
        """
        with pytest.raises(ValueError):
            validate_tickers(tickers)

    @given(st.lists(st.just(""), min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_list_with_empty_strings_rejected(self, tickers: list):
        """
        Property: List containing empty strings should be rejected
        """
        with pytest.raises(ValueError):
            validate_tickers(tickers)


class TestHistoricalDataRequestProperties:
    """Property tests for historical data requests"""

    @given(
        st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 12, 31)),
        st.integers(min_value=1, max_value=365)
    )
    @settings(max_examples=100)
    def test_end_after_start_property(self, start_date: datetime, days_diff: int):
        """
        Property: For any start_date and positive days_diff, request should be valid
        """
        end_date = start_date + timedelta(days=days_diff)

        request = HistoricalDataRequest(
            ticker="AAPL",
            start_date=start_date,
            end_date=end_date
        )

        # Postconditions
        assert request.end_date > request.start_date
        assert request.ticker == "AAPL"

    @given(
        st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 12, 31)),
        st.integers(min_value=1, max_value=365)
    )
    @settings(max_examples=100)
    def test_start_after_end_always_rejected(self, end_date: datetime, days_diff: int):
        """
        Property: start_date > end_date should always be rejected
        """
        start_date = end_date + timedelta(days=days_diff)

        with pytest.raises(ValueError):
            HistoricalDataRequest(
                ticker="AAPL",
                start_date=start_date,
                end_date=end_date
            )

    @given(valid_ticker_strategy, st.sampled_from(["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]))
    @settings(max_examples=100)
    def test_valid_timeframes_accepted(self, ticker: str, timeframe: str):
        """
        Property: All valid timeframes should be accepted
        """
        start = datetime.now() - timedelta(days=7)
        end = datetime.now()

        request = HistoricalDataRequest(
            ticker=ticker,
            start_date=start,
            end_date=end,
            timeframe=timeframe
        )

        assert request.timeframe == timeframe


class TestTickerFormatInvariants:
    """Test invariants that should always hold"""

    @given(valid_ticker_strategy)
    @settings(max_examples=200)
    def test_idempotent_validation(self, ticker: str):
        """
        Property: Validating a valid ticker twice should give same result

        validate_ticker(validate_ticker(x)) == validate_ticker(x)
        """
        first_validation = validate_ticker(ticker)
        second_validation = validate_ticker(first_validation)

        assert first_validation == second_validation

    @given(valid_ticker_strategy)
    @settings(max_examples=200)
    def test_validation_preserves_length(self, ticker: str):
        """
        Property: Validation should not change length of valid ticker
        """
        result = validate_ticker(ticker)
        assert len(result) == len(ticker)

    @given(st.lists(valid_ticker_strategy, min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_batch_validation_order_preserved(self, tickers: list):
        """
        Property: Batch validation should preserve order
        """
        result = validate_tickers(tickers)

        # Order should be preserved (after normalization)
        for i, ticker in enumerate(tickers):
            assert result[i] == ticker.upper()


class TestEquivalenceClasses:
    """Test that equivalent inputs produce equivalent outputs"""

    @given(st.text(alphabet="ABCDE", min_size=1, max_size=5))
    @settings(max_examples=100)
    def test_case_variations_equivalent(self, ticker: str):
        """
        Property: Different case variations of same ticker are equivalent
        """
        variations = [
            ticker.upper(),
            ticker.lower(),
            ticker.capitalize(),
            ticker.swapcase() if len(ticker) > 1 else ticker
        ]

        # All should validate to same result
        results = set()
        for variation in variations:
            try:
                result = validate_ticker(variation)
                results.add(result)
            except ValueError:
                # If one fails, we're only testing valid inputs
                pass

        if results:
            # All non-failing results should be identical
            assert len(results) == 1


# Integration property tests

class TestRateLimiterProperties:
    """Property-based tests for rate limiter"""

    @given(
        st.integers(min_value=1, max_value=1000),
        st.floats(min_value=1.0, max_value=3600.0)
    )
    @settings(max_examples=50, deadline=None)
    def test_rate_limiter_never_exceeds_limit(self, rate: int, window: float):
        """
        Property: Rate limiter should never allow more than 'rate' requests

        This is a critical invariant - no matter what the rate and window are,
        the number of successful requests should never exceed the rate.
        """
        from rate_limiter import TokenBucket

        bucket = TokenBucket(rate, window)

        successful = 0
        # Try to consume double the rate
        for _ in range(rate * 2):
            if bucket.consume():
                successful += 1

        assert successful == rate, f"Rate limit violated: expected {rate}, got {successful}"

    @given(
        st.integers(min_value=5, max_value=100),
        st.floats(min_value=0.5, max_value=60.0),
        st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=30, deadline=None)
    def test_token_replenishment_property(self, rate: int, window: float, time_fraction: float):
        """
        Property: After time T, tokens should be approximately rate * (T / window)

        This tests that token replenishment is proportional to time.
        """
        from rate_limiter import TokenBucket
        import time

        bucket = TokenBucket(rate, window)

        # Consume all tokens
        for _ in range(rate):
            bucket.consume()

        # Wait for a fraction of the window
        time.sleep(time_fraction * window)

        # Calculate expected tokens (approximately)
        expected_tokens = rate * time_fraction

        # Try to consume expected tokens (with some margin for timing precision)
        successful = 0
        for _ in range(int(expected_tokens * 0.8)):  # 80% of expected to account for timing
            if bucket.consume():
                successful += 1

        # Should have consumed roughly the expected amount
        assert successful >= int(expected_tokens * 0.5), \
            f"Expected ~{expected_tokens} tokens, only consumed {successful}"


# Pytest configuration
pytestmark = [
    pytest.mark.property,
    pytest.mark.slow
]
