"""
Health check system for monitoring service status

Provides detailed health information for providers, cache, and system resources.
"""
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum
import asyncio
from logging_config import get_logger

logger = get_logger(__name__)


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """
    Health check manager

    Monitors system components and returns detailed status.
    """

    def __init__(self):
        self.checks: Dict[str, callable] = {}

    def register_check(self, name: str, check_func: callable):
        """
        Register a health check function

        Args:
            name: Name of the check (e.g., "polygon_api", "cache")
            check_func: Async function that returns (status, details)
        """
        self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")

    async def run_check(self, name: str) -> Dict[str, Any]:
        """
        Run a single health check

        Args:
            name: Name of the check

        Returns:
            Check result with status and details
        """
        if name not in self.checks:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "error": f"Unknown check: {name}"
            }

        try:
            check_func = self.checks[name]
            status, details = await check_func()

            return {
                "status": status.value,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed for {name}: {e}")
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all registered health checks

        Returns:
            Overall health status with individual check results
        """
        results = {}
        tasks = []

        # Run all checks concurrently
        for name in self.checks:
            tasks.append(self.run_check(name))

        check_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect results
        for name, result in zip(self.checks.keys(), check_results):
            if isinstance(result, Exception):
                results[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "error": str(result)
                }
            else:
                results[name] = result

        # Determine overall status
        overall_status = self._calculate_overall_status(results)

        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results
        }

    def _calculate_overall_status(self, results: Dict[str, Any]) -> HealthStatus:
        """
        Calculate overall health status from individual checks

        Args:
            results: Dictionary of check results

        Returns:
            Overall HealthStatus
        """
        statuses = [
            HealthStatus(result["status"])
            for result in results.values()
            if "status" in result
        ]

        if not statuses:
            return HealthStatus.UNHEALTHY

        # If any check is unhealthy, overall is unhealthy
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY

        # If any check is degraded, overall is degraded
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED

        # All checks healthy
        return HealthStatus.HEALTHY


# Example health check functions

async def check_yfinance_provider() -> tuple[HealthStatus, Dict[str, Any]]:
    """Check YFinance provider connectivity"""
    try:
        from providers.yfinance_provider import YFinanceProvider

        provider = YFinanceProvider()
        async with provider:
            # Try to fetch a simple quote
            quote = await provider.get_quote("AAPL")

            if quote and quote.price > 0:
                return HealthStatus.HEALTHY, {
                    "provider": "yfinance",
                    "available": True,
                    "test_ticker": "AAPL",
                    "price": quote.price
                }
            else:
                return HealthStatus.DEGRADED, {
                    "provider": "yfinance",
                    "available": True,
                    "error": "Invalid response"
                }

    except Exception as e:
        return HealthStatus.UNHEALTHY, {
            "provider": "yfinance",
            "available": False,
            "error": str(e)
        }


async def check_polygon_provider() -> tuple[HealthStatus, Dict[str, Any]]:
    """Check Polygon provider connectivity"""
    try:
        from config import Config

        if not Config.POLYGON_API_KEY:
            return HealthStatus.DEGRADED, {
                "provider": "polygon",
                "available": False,
                "reason": "No API key configured"
            }

        from providers.polygon_provider import PolygonProvider

        provider = PolygonProvider(api_key=Config.POLYGON_API_KEY)
        async with provider:
            # Try to fetch market status (available on free tier)
            status = await provider.get_market_status()

            if status:
                return HealthStatus.HEALTHY, {
                    "provider": "polygon",
                    "available": True,
                    "market_open": status.is_open
                }
            else:
                return HealthStatus.DEGRADED, {
                    "provider": "polygon",
                    "available": True,
                    "error": "Invalid response"
                }

    except Exception as e:
        return HealthStatus.UNHEALTHY, {
            "provider": "polygon",
            "available": False,
            "error": str(e)
        }


async def check_system_resources() -> tuple[HealthStatus, Dict[str, Any]]:
    """Check system resources"""
    import os
    from pathlib import Path

    # Check if required directories exist
    base_dir = Path(__file__).parent
    required_dirs = ["watchlists", "data", "cache"]

    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)

    if missing_dirs:
        return HealthStatus.DEGRADED, {
            "missing_directories": missing_dirs
        }

    return HealthStatus.HEALTHY, {
        "directories": "all present",
        "pid": os.getpid()
    }


# Global health check instance
_health_check = HealthCheck()

# Register default checks
_health_check.register_check("yfinance", check_yfinance_provider)
_health_check.register_check("polygon", check_polygon_provider)
_health_check.register_check("system", check_system_resources)


def get_health_check() -> HealthCheck:
    """Get global health check instance"""
    return _health_check
