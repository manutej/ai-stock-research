# Provider Architecture

## Overview

The AI Stock Research Tool uses a **modular provider architecture** that allows seamless switching between different stock market data sources. This design enables the application to use the best provider for each task while maintaining a consistent interface.

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│         AIStockResearchTool (Client)        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│       ProviderFactory (Factory Pattern)     │
│  - Auto-selection based on configuration   │
│  - Provider caching and management          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│    StockDataProvider (Abstract Base Class)  │
│  - get_quote()        - get_news()          │
│  - get_historical()   - get_financials()    │
│  - get_market_status()                      │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┴───────┬──────────┐
         ▼               ▼          ▼
   ┌──────────┐   ┌──────────┐  ┌──────────┐
   │ Polygon  │   │ YFinance │  │  Hybrid  │
   │ Provider │   │ Provider │  │ Provider │
   └──────────┘   └──────────┘  └──────────┘
```

## Supported Providers

### 1. YFinance Provider
**Cost**: 100% Free
**Real-time**: ~15 min delayed
**Best for**: Development, testing, price quotes

**Capabilities**:
- ✅ **Quotes**: Free real-time-ish prices (15-20 min delay)
- ✅ **Historical Data**: Full access to OHLCV data
- ✅ **News**: Basic news feed
- ✅ **Financials**: Complete financial statements
- ✅ **Market Status**: Inferred from trading activity

**Limitations**:
- 15-20 minute price delay
- Limited news quality compared to Polygon
- No official rate limits (but respect fair use)

### 2. Polygon Provider
**Cost**: Freemium (limited on free tier)
**Real-time**: True real-time (on paid plans)
**Best for**: Production, news analysis, financial research

**Capabilities**:
- ⚠️ **Quotes**: Requires paid plan ($99/mo+)
- ⚠️ **Historical Data**: Limited on free tier
- ✅ **News**: Excellent quality, works on free tier
- ✅ **Financials**: Full access on free tier
- ✅ **Market Status**: Real-time status, free tier

**Limitations**:
- Free tier: 5 API calls/minute
- Real-time prices require Starter plan ($99/mo)
- Trade history requires Developer plan ($249/mo)

### 3. Hybrid Provider (Recommended)
**Cost**: Free tier + optional Polygon API
**Real-time**: Yes (via YFinance)
**Best for**: Production use with optimal cost/feature balance

**Strategy**:
- **Quotes**: YFinance (free, real-time-ish)
- **News**: Polygon if available (better quality), else YFinance
- **Financials**: YFinance (comprehensive, free)
- **Historical**: YFinance (unlimited, free)
- **Market Status**: Polygon if available, else YFinance

**Benefits**:
- ✅ Real-time prices without paid API
- ✅ High-quality news from Polygon (if API key provided)
- ✅ No rate limit issues
- ✅ Automatic fallback if one provider fails

## Provider Selection Strategies

### Auto Strategy (Default)
Automatically selects the best provider based on available API keys:

- **With Polygon API key**: Uses Hybrid Provider
- **Without Polygon API key**: Uses YFinance Provider

```python
from providers.factory import ProviderFactory, ProviderStrategy

provider = ProviderFactory.create_provider(
    strategy=ProviderStrategy.AUTO,
    polygon_api_key="your-key-or-none"
)
```

### Explicit Strategy Selection

```python
# Force YFinance only (100% free)
provider = ProviderFactory.create_provider(
    strategy=ProviderStrategy.YFINANCE_ONLY
)

# Force Polygon only (requires API key)
provider = ProviderFactory.create_provider(
    strategy=ProviderStrategy.POLYGON_ONLY,
    polygon_api_key="your-key"
)

# Use Hybrid (best of both worlds)
provider = ProviderFactory.create_provider(
    strategy=ProviderStrategy.HYBRID,
    polygon_api_key="your-key-or-none"
)
```

### Configuration-based Selection

Set in `.env` file:
```bash
DEFAULT_PROVIDER=auto  # Options: auto, yfinance, polygon, hybrid
```

Then use:
```python
from config import Config
from providers.factory import ProviderFactory

config = Config()
provider = ProviderFactory.from_config(config)
```

## Usage Examples

### Basic Quote Retrieval

```python
import asyncio
from providers.factory import ProviderFactory, ProviderStrategy

async def get_stock_price(ticker: str):
    provider = ProviderFactory.create_provider(
        strategy=ProviderStrategy.YFINANCE_ONLY
    )

    async with provider:
        quote = await provider.get_quote(ticker)
        print(f"{quote.ticker}: ${quote.price:.2f}")
        print(f"Change: {quote.change_percent:+.2f}%")
        print(f"Provider: {quote.provider}")

asyncio.run(get_stock_price("NVDA"))
```

**Output**:
```
NVDA: $185.04
Change: -0.25%
Provider: yfinance
```

### Batch Quote Retrieval

```python
async def get_portfolio_prices():
    provider = ProviderFactory.create_provider(
        strategy=ProviderStrategy.YFINANCE_ONLY
    )

    async with provider:
        tickers = ["NVDA", "MSFT", "GOOGL", "META", "AMZN"]
        quotes = await provider.get_quotes(tickers)

        for ticker, quote in quotes.items():
            print(f"{ticker:6s} ${quote.price:7.2f} ({quote.change_percent:+6.2f}%)")
```

**Output**:
```
NVDA   $ 185.04 ( -0.25%)
MSFT   $ 523.98 ( -0.87%)
GOOGL  $ 245.76 ( -1.86%)
META   $ 634.25 ( +1.23%)
AMZN   $ 245.89 ( -0.54%)
```

### Historical Data Analysis

```python
from datetime import datetime, timedelta

async def analyze_volatility(ticker: str, days: int = 30):
    provider = ProviderFactory.create_provider(
        strategy=ProviderStrategy.YFINANCE_ONLY
    )

    async with provider:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        bars = await provider.get_historical(
            ticker, start_date, end_date, "1d"
        )

        # Calculate daily returns
        returns = []
        for i in range(1, len(bars)):
            ret = (bars[i].close - bars[i-1].close) / bars[i-1].close
            returns.append(ret * 100)

        avg_return = sum(returns) / len(returns)
        volatility = (sum((r - avg_return)**2 for r in returns) / len(returns))**0.5

        print(f"{ticker} Analysis ({days} days):")
        print(f"  Average Daily Return: {avg_return:+.2f}%")
        print(f"  Volatility: {volatility:.2f}%")

asyncio.run(analyze_volatility("NVDA", 30))
```

### News Monitoring with Hybrid Provider

```python
async def monitor_ai_news():
    from config import Config

    config = Config()
    provider = ProviderFactory.create_provider(
        strategy=ProviderStrategy.HYBRID,
        polygon_api_key=config.POLYGON_API_KEY
    )

    async with provider:
        tickers = ["NVDA", "MSFT", "GOOGL", "META"]

        for ticker in tickers:
            news = await provider.get_news(ticker, limit=3)
            print(f"\n📰 Latest {ticker} News:")

            for article in news:
                print(f"  • {article.title}")
                print(f"    {article.published_at.strftime('%Y-%m-%d')} - {article.source}")
                print(f"    Provider: {article.provider}")
```

## Adding New Providers

### Step 1: Create Provider Class

Create a new file in `providers/` directory:

```python
# providers/alpha_vantage_provider.py
from providers.base import StockDataProvider, Quote

class AlphaVantageProvider(StockDataProvider):
    async def connect(self) -> None:
        # Connect to Alpha Vantage API
        self._connected = True

    async def get_quote(self, ticker: str) -> Quote:
        # Implement quote retrieval
        pass

    # Implement other required methods...

    @property
    def provider_name(self) -> str:
        return "Alpha Vantage"
```

### Step 2: Register in Factory

Update `providers/__init__.py`:

```python
def get_provider(provider_type: ProviderType, **kwargs) -> StockDataProvider:
    if provider_type == ProviderType.ALPHA_VANTAGE:
        from providers.alpha_vantage_provider import AlphaVantageProvider
        return AlphaVantageProvider(**kwargs)
    # ... existing providers
```

### Step 3: Add to ProviderType Enum

Update `providers/base.py`:

```python
class ProviderType(Enum):
    POLYGON = "polygon"
    YFINANCE = "yfinance"
    ALPHA_VANTAGE = "alpha_vantage"  # Add new provider
```

## Data Structures

All providers return standardized data structures:

### Quote
```python
@dataclass
class Quote:
    ticker: str
    price: float
    timestamp: datetime
    volume: Optional[int]
    change: Optional[float]
    change_percent: Optional[float]
    provider: Optional[str]
    # ... additional fields
```

### OHLCV
```python
@dataclass
class OHLCV:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    ticker: Optional[str]
    provider: Optional[str]
```

### NewsArticle
```python
@dataclass
class NewsArticle:
    title: str
    url: str
    published_at: datetime
    description: Optional[str]
    source: Optional[str]
    tickers: Optional[List[str]]
    provider: Optional[str]
```

## Testing

### Test All Providers
```bash
python3 test_providers.py
```

### Test Specific Provider
```bash
python3 test_providers.py yfinance  # Test YFinance only
python3 test_providers.py polygon   # Test Polygon only
python3 test_providers.py hybrid    # Test Hybrid provider
python3 test_providers.py auto      # Test auto-selection
```

## Performance Comparison

| Feature | YFinance | Polygon Free | Polygon Paid | Hybrid |
|---------|----------|--------------|--------------|--------|
| **Price** | Free | Free | $99-499/mo | Free |
| **Real-time Quotes** | ~15min delay | ❌ | ✅ | ✅ (via YF) |
| **Historical Data** | ✅ Unlimited | ⚠️ Limited | ✅ | ✅ (via YF) |
| **News Quality** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Financials** | ✅ | ✅ | ✅ | ✅ |
| **Rate Limit** | None | 5/min | Higher | None |
| **Best For** | Dev/Testing | Research | Production | **Recommended** |

## Recommendations

### Development
Use **YFinance Only**:
```bash
DEFAULT_PROVIDER=yfinance
```

### Production (Free Tier)
Use **Hybrid** without Polygon key:
```bash
DEFAULT_PROVIDER=hybrid
# Don't set POLYGON_API_KEY
```

### Production (Paid)
Use **Hybrid** with Polygon key:
```bash
DEFAULT_PROVIDER=hybrid
POLYGON_API_KEY=your-key
```

## Troubleshooting

### "Module not found: yfinance"
```bash
source venv/bin/activate
pip install yfinance
```

### "NOT_AUTHORIZED" from Polygon
This is expected on free tier for real-time prices. The hybrid provider automatically falls back to YFinance.

### Rate Limit Errors
Switch to YFinance or upgrade Polygon plan:
```python
provider = ProviderFactory.create_provider(
    strategy=ProviderStrategy.YFINANCE_ONLY
)
```

## Future Providers

Planned additions:
- **Alpha Vantage**: Free API with good coverage
- **IEX Cloud**: Professional-grade data
- **Finnhub**: Real-time WebSocket support
- **Tiingo**: Crypto and forex support

---

**Last Updated**: October 8, 2025
**Version**: 2.0
**Architecture**: Modular Provider Pattern
