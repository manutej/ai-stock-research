"""
Simple rate limiter using token bucket algorithm

Prevents API quota exhaustion and enforces fair usage.
"""
import time
from typing import Dict
from threading import Lock
from logging_config import get_logger
from exceptions import RateLimitExceededError

logger = get_logger(__name__)


class TokenBucket:
    """
    Token bucket rate limiter

    Allows bursts while enforcing average rate limit.
    """

    def __init__(self, rate: int, per: float = 60.0):
        """
        Initialize token bucket

        Args:
            rate: Number of tokens (requests) allowed
            per: Time window in seconds (default: 60 = 1 minute)
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens consumed, False if rate limit exceeded
        """
        with self.lock:
            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current

            # Add tokens based on time passed
            self.allowance += time_passed * (self.rate / self.per)

            # Cap at maximum rate
            if self.allowance > self.rate:
                self.allowance = self.rate

            # Try to consume
            if self.allowance >= tokens:
                self.allowance -= tokens
                return True
            else:
                return False

    def wait_time(self) -> float:
        """
        Calculate wait time until next token is available

        Returns:
            Seconds to wait
        """
        with self.lock:
            if self.allowance >= 1:
                return 0.0

            tokens_needed = 1 - self.allowance
            return tokens_needed * (self.per / self.rate)


class RateLimiter:
    """
    Multi-provider rate limiter

    Manages rate limits for different API providers.
    """

    def __init__(self):
        self.limiters: Dict[str, TokenBucket] = {}
        self.lock = Lock()

    def register_provider(self, name: str, rate: int, per: float = 60.0):
        """
        Register a provider with rate limit

        Args:
            name: Provider name (e.g., "polygon", "yfinance")
            rate: Requests allowed
            per: Time window in seconds
        """
        with self.lock:
            self.limiters[name] = TokenBucket(rate, per)
            logger.info(f"Registered rate limiter for {name}: {rate} req/{per}s")

    def check_limit(self, provider: str, tokens: int = 1) -> None:
        """
        Check and consume rate limit

        Args:
            provider: Provider name
            tokens: Number of tokens to consume

        Raises:
            RateLimitExceededError: If rate limit exceeded
        """
        if provider not in self.limiters:
            logger.warning(f"No rate limiter configured for {provider}")
            return

        limiter = self.limiters[provider]

        if not limiter.consume(tokens):
            wait_time = limiter.wait_time()
            logger.warning(
                f"Rate limit exceeded for {provider}. "
                f"Wait {wait_time:.2f}s before retrying."
            )
            raise RateLimitExceededError(
                limit=limiter.rate,
                window=f"{limiter.per}s"
            )

        logger.debug(f"Rate limit check passed for {provider}")

    def get_wait_time(self, provider: str) -> float:
        """
        Get wait time for provider

        Args:
            provider: Provider name

        Returns:
            Seconds to wait, or 0 if ready
        """
        if provider not in self.limiters:
            return 0.0

        return self.limiters[provider].wait_time()


# Global rate limiter instance
_rate_limiter = RateLimiter()

# Register default limits
_rate_limiter.register_provider("polygon", rate=5, per=60.0)  # 5 req/min
_rate_limiter.register_provider("yfinance", rate=2000, per=3600.0)  # 2000 req/hour


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    return _rate_limiter
