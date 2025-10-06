"""
Configuration management for AI Stock Research Tool
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # API Keys
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # Project paths
    BASE_DIR = Path(__file__).parent
    WATCHLISTS_DIR = BASE_DIR / "watchlists"
    DATA_DIR = BASE_DIR / "data"
    CACHE_DIR = BASE_DIR / "cache"

    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)

    # Rate limiting
    POLYGON_RATE_LIMIT = 5  # calls per minute (free tier)
    CACHE_TTL = 300  # 5 minutes cache for repeated queries

    # Analysis settings
    DEFAULT_LOOKBACK_DAYS = 30
    ALERT_THRESHOLD_PERCENT = 5.0

    @classmethod
    def load_watchlist(cls, name: str) -> Dict:
        """Load a watchlist by name"""
        watchlist_path = cls.WATCHLISTS_DIR / f"{name}.json"
        if not watchlist_path.exists():
            raise FileNotFoundError(f"Watchlist not found: {name}")

        with open(watchlist_path) as f:
            return json.load(f)

    @classmethod
    def get_all_tickers(cls) -> List[str]:
        """Get all tickers from all watchlists"""
        tickers = set()

        # Large cap
        large_cap = cls.load_watchlist("ai_large_cap")
        tickers.update(c["ticker"] for c in large_cap["companies"])

        # Startups
        startups = cls.load_watchlist("ai_startups")
        tickers.update(c["ticker"] for c in startups["companies"])

        return sorted(list(tickers))

    @classmethod
    def get_tickers_by_category(cls, category: str) -> List[str]:
        """Get tickers by category (large_cap, startups, etc.)"""
        watchlist = cls.load_watchlist(f"ai_{category}")
        return [c["ticker"] for c in watchlist["companies"]]

    @classmethod
    def get_company_info(cls, ticker: str) -> Optional[Dict]:
        """Get company info for a ticker"""
        # Search in all watchlists
        for watchlist_name in ["ai_large_cap", "ai_startups"]:
            try:
                watchlist = cls.load_watchlist(watchlist_name)
                for company in watchlist["companies"]:
                    if company["ticker"] == ticker:
                        return company
            except FileNotFoundError:
                continue

        return None


class PolygonConfig:
    """Polygon.io specific configuration"""

    BASE_URL = "https://api.polygon.io"

    # Endpoints (for reference - MCP tools handle these)
    ENDPOINTS = {
        "aggs": "/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}",
        "trades": "/v3/trades/{ticker}",
        "last_trade": "/v2/last/trade/{ticker}",
        "ticker_news": "/v2/reference/news",
        "snapshot": "/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}",
        "market_status": "/v1/marketstatus/now",
        "financials": "/vX/reference/financials",
    }

    # Common parameters
    TIMESPAN_OPTIONS = ["minute", "hour", "day", "week", "month", "quarter", "year"]
    DEFAULT_TIMESPAN = "day"
    DEFAULT_LIMIT = 50


class AICompanyCategories:
    """AI company categorization"""

    CATEGORIES = {
        "infrastructure": ["NVDA", "AMD", "ARM"],
        "platforms": ["MSFT", "GOOGL", "AMZN"],
        "research": ["META", "GOOGL"],
        "applications": ["TSLA", "AAPL"],
        "enterprise": ["AI", "PLTR", "SNOW"],
        "automation": ["PATH", "SOUN"],
    }

    @classmethod
    def get_category(cls, ticker: str) -> List[str]:
        """Get categories for a ticker"""
        return [cat for cat, tickers in cls.CATEGORIES.items() if ticker in tickers]

    @classmethod
    def get_tickers_in_category(cls, category: str) -> List[str]:
        """Get all tickers in a category"""
        return cls.CATEGORIES.get(category, [])
