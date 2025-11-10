"""
Unit tests for rate_limiter module

Test Coverage:
- TC-RATE-001: Basic rate limiting
- TC-RATE-002: Token replenishment
- TC-RATE-003: Thread safety
- TC-RATE-004: Multiple providers

Success Criteria:
- Rate limits enforced accurately
- Tokens replenish correctly over time
- Thread-safe under concurrent access
- Multiple providers isolated
"""
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from rate_limiter import TokenBucket, RateLimiter, get_rate_limiter
from exceptions import RateLimitExceededError


class TestTokenBucket:
    """TC-RATE-001: Basic rate limiting"""

    def test_initial_tokens_equal_rate(self):
        """TokenBucket should start with full capacity"""
        bucket = TokenBucket(rate=5, per=60.0)
        # Allowance should be initialized to rate
        assert bucket.allowance == 5

    def test_first_n_requests_succeed(self):
        """First N requests should succeed where N = rate"""
        bucket = TokenBucket(rate=5, per=60.0)

        # First 5 requests should succeed
        for i in range(5):
            result = bucket.consume(tokens=1)
            assert result is True, f"Request {i+1} should succeed"

    def test_request_after_limit_fails(self):
        """Request after limit should fail"""
        bucket = TokenBucket(rate=5, per=60.0)

        # Consume all tokens
        for _ in range(5):
            bucket.consume()

        # 6th request should fail
        result = bucket.consume()
        assert result is False

    def test_consume_multiple_tokens(self):
        """Should handle consuming multiple tokens at once"""
        bucket = TokenBucket(rate=10, per=60.0)

        # Consume 5 tokens
        assert bucket.consume(tokens=5) is True
        assert bucket.allowance == 5

        # Consume another 5
        assert bucket.consume(tokens=5) is True
        # Allow small floating-point errors
        assert bucket.allowance < 0.001

        # Try to consume 1 more
        assert bucket.consume(tokens=1) is False

    def test_consume_more_tokens_than_available_fails(self):
        """Trying to consume more tokens than available should fail"""
        bucket = TokenBucket(rate=5, per=60.0)

        # Try to consume 10 tokens when only 5 available
        assert bucket.consume(tokens=10) is False
        # Allowance should not change
        assert bucket.allowance == 5


class TestTokenReplenishment:
    """TC-RATE-002: Token replenishment"""

    def test_tokens_replenish_over_time(self):
        """Tokens should replenish proportionally to time passed"""
        bucket = TokenBucket(rate=10, per=1.0)  # 10 tokens per second

        # Consume all tokens
        for _ in range(10):
            bucket.consume()
        # Allow small floating-point errors
        assert bucket.allowance < 0.001

        # Wait 0.5 seconds
        time.sleep(0.5)

        # Should have ~5 tokens (half the rate)
        # Allow some margin for timing precision
        assert bucket.consume(tokens=4) is True

    def test_tokens_capped_at_max_rate(self):
        """Tokens should not exceed the maximum rate"""
        bucket = TokenBucket(rate=5, per=1.0)

        # Wait for tokens to fully replenish and beyond
        time.sleep(2.0)

        # Should still only have 5 tokens
        assert bucket.consume(tokens=5) is True
        assert bucket.consume(tokens=1) is False

    def test_fractional_tokens_handled(self):
        """Fractional token accumulation should work correctly"""
        bucket = TokenBucket(rate=3, per=10.0)  # 0.3 tokens per second

        # Consume all tokens
        for _ in range(3):
            bucket.consume()

        # Wait for 1 second (should add 0.3 tokens)
        time.sleep(1.0)

        # Should not have enough for 1 full token yet
        assert bucket.consume(tokens=1) is False

        # Wait another 3 seconds (total 4s = 1.2 tokens)
        time.sleep(3.0)

        # Should now have at least 1 token
        assert bucket.consume(tokens=1) is True

    def test_wait_time_calculation(self):
        """wait_time() should accurately calculate wait duration"""
        bucket = TokenBucket(rate=10, per=60.0)  # 10 per minute = 1 per 6 seconds

        # Consume all tokens
        for _ in range(10):
            bucket.consume()

        # Wait time for 1 token should be ~6 seconds
        wait_time = bucket.wait_time()
        assert 5.5 <= wait_time <= 6.5, f"Expected ~6s, got {wait_time}s"

    def test_wait_time_zero_when_tokens_available(self):
        """wait_time() should be 0 when tokens are available"""
        bucket = TokenBucket(rate=5, per=60.0)
        assert bucket.wait_time() == 0.0


class TestThreadSafety:
    """TC-RATE-003: Thread safety"""

    def test_concurrent_access_respects_limit(self):
        """Multiple threads should not exceed rate limit"""
        bucket = TokenBucket(rate=10, per=60.0)
        successful = []
        failed = []

        def try_consume():
            if bucket.consume():
                successful.append(1)
            else:
                failed.append(1)

        # Spawn 100 threads trying to consume
        threads = [threading.Thread(target=try_consume) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactly 10 should succeed
        assert len(successful) == 10, f"Expected 10 successful, got {len(successful)}"
        assert len(failed) == 90, f"Expected 90 failed, got {len(failed)}"

    def test_no_deadlocks_under_load(self):
        """High concurrent load should not cause deadlocks"""
        bucket = TokenBucket(rate=100, per=1.0)

        def consume_with_timeout():
            # Try to consume with a timeout to detect deadlocks
            return bucket.consume()

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(consume_with_timeout) for _ in range(200)]

            # All futures should complete within reasonable time
            results = []
            for future in as_completed(futures, timeout=5.0):
                results.append(future.result())

        # Should complete without timeout
        assert len(results) == 200

    def test_race_condition_on_replenishment(self):
        """Token replenishment should handle race conditions"""
        bucket = TokenBucket(rate=50, per=1.0)

        # Consume all tokens
        for _ in range(50):
            bucket.consume()

        # Wait for partial replenishment
        time.sleep(0.1)  # Should add ~5 tokens

        successful = []

        def try_consume():
            if bucket.consume():
                successful.append(1)

        # Multiple threads try to consume the replenished tokens
        threads = [threading.Thread(target=try_consume) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have approximately 5 successful (may vary due to timing)
        assert 3 <= len(successful) <= 7, f"Expected ~5, got {len(successful)}"


class TestRateLimiter:
    """TC-RATE-004: Multiple providers"""

    def test_register_provider(self):
        """Should be able to register providers with limits"""
        limiter = RateLimiter()
        limiter.register_provider("test_provider", rate=10, per=60.0)

        # Should not raise when checking limit
        limiter.check_limit("test_provider")

    def test_different_providers_independent(self):
        """Different providers should have independent limits"""
        limiter = RateLimiter()
        limiter.register_provider("provider_a", rate=5, per=60.0)
        limiter.register_provider("provider_b", rate=5, per=60.0)

        # Exhaust provider_a
        for _ in range(5):
            limiter.check_limit("provider_a")

        # provider_a should be rate limited
        with pytest.raises(RateLimitExceededError):
            limiter.check_limit("provider_a")

        # provider_b should still work
        limiter.check_limit("provider_b")

    def test_check_limit_raises_on_exceeded(self):
        """check_limit() should raise RateLimitExceededError when exceeded"""
        limiter = RateLimiter()
        limiter.register_provider("test", rate=3, per=60.0)

        # Consume all tokens
        for _ in range(3):
            limiter.check_limit("test")

        # Should raise on next attempt
        with pytest.raises(RateLimitExceededError) as exc_info:
            limiter.check_limit("test")

        # Exception should have correct attributes
        assert exc_info.value.limit == 3
        assert exc_info.value.window == "60.0s"

    def test_unregistered_provider_warning(self):
        """Checking limit for unregistered provider should not error"""
        limiter = RateLimiter()

        # Should not raise, just log warning
        limiter.check_limit("unknown_provider")

    def test_get_wait_time(self):
        """get_wait_time() should return correct wait duration"""
        limiter = RateLimiter()
        limiter.register_provider("test", rate=10, per=60.0)

        # Exhaust tokens
        for _ in range(10):
            limiter.check_limit("test")

        # Should have non-zero wait time
        wait_time = limiter.get_wait_time("test")
        assert wait_time > 0

    def test_get_wait_time_zero_when_ready(self):
        """get_wait_time() should be 0 when tokens available"""
        limiter = RateLimiter()
        limiter.register_provider("test", rate=5, per=60.0)

        assert limiter.get_wait_time("test") == 0.0

    def test_get_wait_time_unknown_provider(self):
        """get_wait_time() for unknown provider should return 0"""
        limiter = RateLimiter()
        assert limiter.get_wait_time("unknown") == 0.0


class TestGlobalRateLimiter:
    """Test global rate limiter instance"""

    def test_get_rate_limiter_returns_singleton(self):
        """get_rate_limiter() should return same instance"""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        assert limiter1 is limiter2

    def test_default_providers_registered(self):
        """Default providers (polygon, yfinance) should be pre-registered"""
        limiter = get_rate_limiter()

        # Should not raise for default providers
        limiter.check_limit("polygon")
        limiter.check_limit("yfinance")


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_zero_rate_limit(self):
        """Rate of 0 should effectively block all requests"""
        bucket = TokenBucket(rate=0, per=60.0)
        assert bucket.consume() is False

    def test_very_high_rate_limit(self):
        """Very high rate limits should work correctly"""
        bucket = TokenBucket(rate=10000, per=1.0)

        # Should be able to consume many tokens
        for _ in range(1000):
            assert bucket.consume() is True

    def test_very_small_time_window(self):
        """Very small time windows should work"""
        bucket = TokenBucket(rate=10, per=0.1)  # 10 per 0.1s = 100/s

        # Consume all
        for _ in range(10):
            bucket.consume()

        # Wait a tiny bit
        time.sleep(0.01)  # 10ms

        # Should have replenished some tokens
        # 0.01s * (10 / 0.1) = 1 token
        assert bucket.consume() is True

    def test_very_large_time_window(self):
        """Very large time windows should work"""
        bucket = TokenBucket(rate=100, per=3600.0)  # 100 per hour

        # Should start with 100 tokens
        for _ in range(100):
            assert bucket.consume() is True

        assert bucket.consume() is False


class TestPerformance:
    """PERF-001: Rate limiter performance"""

    def test_performance_single_threaded(self):
        """10,000 calls should complete quickly (<1s)"""
        bucket = TokenBucket(rate=100000, per=1.0)  # High limit to avoid blocking

        start = time.time()
        for _ in range(10000):
            bucket.consume()
        duration = time.time() - start

        # Should complete in under 1 second
        assert duration < 1.0, f"Too slow: {duration}s for 10k calls"

    def test_performance_multithreaded(self):
        """100 threads × 100 calls should complete quickly"""
        bucket = TokenBucket(rate=100000, per=1.0)

        def worker():
            for _ in range(100):
                bucket.consume()

        start = time.time()
        threads = [threading.Thread(target=worker) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        duration = time.time() - start

        # Should complete in under 2 seconds
        assert duration < 2.0, f"Too slow: {duration}s for 10k concurrent calls"


# Pytest marks
pytestmark = [
    pytest.mark.unit,
    pytest.mark.rate_limiter
]
