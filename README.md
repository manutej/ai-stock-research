# AI Stock Research Tool

> An intelligent stock research assistant leveraging Polygon.io MCP server to track and analyze AI sector companies using real-time and historical market data.

## Overview

This tool provides comprehensive research capabilities for AI sector investments, focusing on:
- **Large Cap AI Leaders** (NVDA, MSFT, GOOGL, META, AMZN, TSLA, AAPL)
- **AI Startups & IPOs** (C3.ai, Palantir, SoundHound, UiPath)
- **Pre-IPO Tracking** (OpenAI, Anthropic, Databricks via proxies)

## Features

### Core Capabilities
- 📊 **Real-time Market Data** - Live prices, trades, and market snapshots
- 📰 **AI News Monitoring** - Track announcements, funding rounds, product launches
- 📈 **Historical Analysis** - Price trends, trading patterns, performance metrics
- 💰 **Financial Fundamentals** - Revenue, R&D spending, growth analysis
- 🎯 **Smart Alerts** - Custom triggers for price movements and AI-related events
- 🔍 **Sector Comparison** - Compare AI companies across key metrics

### MCP Tools Integration

Leverages 7 Polygon.io MCP tools:

| Tool | Purpose | Example Use |
|------|---------|-------------|
| `get_aggs` | OHLC aggregates | Track NVDA price movements |
| `list_trades` | Historical trades | Analyze trading patterns during AI news |
| `get_last_trade` | Latest trade | Real-time price monitoring |
| `list_ticker_news` | Company news | Track AI announcements, funding rounds |
| `get_snapshot_ticker` | Market snapshot | Quick AI stock performance overview |
| `get_market_status` | Trading hours | Schedule automated analysis |
| `list_stock_financials` | Fundamentals | Revenue growth, R&D spending |

## Installation

### Prerequisites
- Python 3.10+
- Polygon.io API key ([Get free key](https://polygon.io/dashboard/signup))
- Claude CLI with Polygon MCP server configured

### Setup

1. **Clone and navigate:**
   ```bash
   cd /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Verify Polygon MCP connection:**
   ```bash
   claude mcp list
   # Should show: polygon - ✓ Connected
   ```

## Usage

### Quick Start Examples

#### 1. Morning AI Sector Brief
```python
from client import AIStockResearchTool

tool = AIStockResearchTool()
await tool.research_query("Give me a morning brief on AI stocks")
```

**Output:**
```
AI Sector Morning Brief (2025-10-06)
═══════════════════════════════════

Market Status: Pre-market (Opens in 45 minutes)

Top Movers:
├─ NVDA: $825.50 (+2.3%) - New AI chip announcement
├─ MSFT: $412.25 (-0.5%) - Azure earnings preview
└─ GOOGL: $165.80 (+1.2%) - Gemini 2.0 launch
```

#### 2. Track AI Startup Performance
```python
await tool.research_query("How is Palantir performing this quarter?")
```

#### 3. Real-time Alert Setup
```python
await tool.research_query("Alert me when NVDA moves >5% on AI-related news")
```

#### 4. Comparative Analysis
```python
await tool.research_query("Compare R&D spending across NVDA, GOOGL, and MSFT")
```

### Command Line Interface

```bash
# Run interactive research session
python client.py

# Run specific query
python client.py --query "Latest price for NVDA"

# Morning brief automation
python queries/morning_brief.py

# IPO tracker
python queries/ipo_tracker.py
```

## Project Structure

```
ai-stock-research/
├── server.py              # MCP server implementation (future)
├── client.py              # Main research tool client
├── config.py              # Configuration management
│
├── watchlists/            # Curated AI stock lists
│   ├── ai_large_cap.json  # NVDA, MSFT, GOOGL, etc.
│   ├── ai_startups.json   # Recent IPOs, high-growth
│   └── ai_watchlist.json  # Pre-IPO tracking
│
├── analyzers/             # Analysis modules
│   ├── sentiment.py       # News sentiment analysis
│   ├── fundamentals.py    # Financial metrics
│   └── technical.py       # Price pattern analysis
│
├── queries/               # Pre-built query workflows
│   ├── morning_brief.py   # Daily AI sector summary
│   ├── ipo_tracker.py     # New listing monitor
│   └── event_scanner.py   # AI news impact analysis
│
└── tests/                 # Test suite
    └── test_polygon.py    # Polygon MCP integration tests
```

## Use Cases

### 1. Daily AI Sector Monitoring
Track your AI portfolio with automated morning briefs and real-time alerts for significant moves.

### 2. IPO Research & Analysis
Analyze newly public AI companies with historical performance data, fundamentals, and news sentiment.

### 3. Pre-IPO Proxy Tracking
Monitor public companies with significant stakes in private AI leaders (MSFT for OpenAI, GOOGL for Anthropic).

### 4. Event-Driven Trading Research
Correlate AI product launches, earnings, and news events with stock price movements.

### 5. Sector Comparison & Benchmarking
Compare AI companies across metrics like R&D spend, revenue growth, and market performance.

## Market Coverage

| Coverage | Status | Notes |
|----------|--------|-------|
| **US Stocks** | ✅ Full | NYSE, NASDAQ, OTC |
| **US Options** | ✅ Available | Polygon support |
| **Crypto** | ✅ Major coins | BTC, ETH, AI tokens |
| **International** | ⏳ Limited | US-listed ADRs only (BIDU, BABA) |
| **Pre-IPO** | 💡 Proxy | Track via invested companies |

## Configuration

### API Keys Required

1. **Polygon.io** (Required)
   - Free tier: 5 API calls/minute
   - Get key: https://polygon.io/dashboard/signup

2. **OpenAI** (Optional - for advanced NLP)
   - Enhanced query understanding
   - Sentiment analysis

3. **Anthropic Claude** (Optional - for analysis)
   - Deep analysis reports
   - Pattern recognition

### Watchlist Customization

Edit JSON files in `/watchlists/` to customize tracked companies:

```json
{
  "ticker": "NVDA",
  "name": "NVIDIA Corporation",
  "sector": "AI Infrastructure - Chips",
  "focus": "GPU computing, AI accelerators"
}
```

## Development Roadmap

### Phase 1: MVP (Current)
- [x] Basic Polygon MCP integration
- [x] AI company watchlists
- [x] Simple query patterns
- [ ] Core client implementation
- [ ] Basic analysis tools

### Phase 2: Intelligence Layer
- [ ] LLM-powered query parsing
- [ ] Multi-tool orchestration
- [ ] News sentiment analysis
- [ ] Alert system

### Phase 3: Advanced Features
- [ ] Real-time WebSocket monitoring
- [ ] Historical backtesting
- [ ] Portfolio simulation
- [ ] Custom strategy builder

### Phase 4: International Expansion
- [ ] Track Chinese AI leaders (when available)
- [ ] European AI startups
- [ ] Asian semiconductor companies

## Contributing

This is a research tool under active development. Contributions welcome!

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Type checking
mypy .

# Linting
ruff check .
```

### Adding New Watchlists

1. Create JSON file in `/watchlists/`
2. Follow schema in existing files
3. Update `config.py` to load new list

### Adding New Analysis Modules

1. Create module in `/analyzers/`
2. Implement analysis interface
3. Add tests in `/tests/`

## Limitations & Known Issues

1. **International Markets**: Currently limited to US markets. International expansion pending Polygon.io roadmap.

2. **Pre-IPO Companies**: Cannot track private companies (OpenAI, Anthropic) directly. Use proxy investments instead.

3. **Rate Limits**: Free tier has 5 calls/minute. Consider paid tier for production use.

4. **Real-time Data**: REST API polling. WebSocket streaming planned for future release.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [Polygon.io](https://polygon.io) financial data API
- Uses [Model Context Protocol (MCP)](https://modelcontextprotocol.io) for tool integration
- Inspired by the need for AI-focused investment research tools

## Support

- Issues: Create GitHub issue
- Documentation: See `/docs` folder
- Examples: See `/examples` folder

---

**Disclaimer**: This tool is for research purposes only. Not financial advice. Always do your own due diligence before making investment decisions.
