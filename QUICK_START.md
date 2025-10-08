# FinWiz Quick Start Guide

**Get stock market data in seconds - no API keys required!**

## Installation (30 seconds)

```bash
# 1. Navigate to project
cd /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies (if not already done)
pip install -r requirements.txt

# 4. You're ready! No API keys needed for basic functionality
```

## Quick Examples

### Get a Stock Quote (FREE!)

```bash
python3 finwiz.py quote NVDA
```

**Output:**
```
📊 Quote for NVDA
============================================================

Price:     $185.04
Change:    -0.47 (-0.25%)
Open:      $185.50
High:      $186.30
Low:       $183.80
Volume:    139,132,055
Provider:  yfinance
Updated:   2025-10-07 16:00:00
```

### Get Multiple Quotes

```bash
python3 finwiz.py quotes NVDA MSFT GOOGL
```

**Output:**
```
📊 Quotes for 3 stocks
============================================================

Ticker  Price      Change    Change%   Volume
------------------------------------------------------------
NVDA     $185.04    -0.47    (-0.25%)  Vol: 139,132,055
MSFT     $523.98    -4.59    (-0.87%)  Vol: 18,234,567
GOOGL    $245.76    -4.65    (-1.86%)  Vol: 12,456,789
```

### Morning Brief

```bash
python3 finwiz.py morning-brief
```

**Output:**
```
☀️  AI Sector Morning Brief
============================================================
Date: 2025-10-07 09:30
Market Status: OPEN

📊 Major AI Stocks:
------------------------------------------------------------
Ticker  Price      Change    Change%
------------------------------------------------------------
NVDA     $185.04    -0.47    (-0.25%)
MSFT     $523.98    -4.59    (-0.87%)
GOOGL    $245.76    -4.65    (-1.86%)
META     $634.25   +7.64    (+1.23%)
AMZN     $245.89    -1.33    (-0.54%)

📰 Latest AI News:
------------------------------------------------------------
1. AMD's OpenAI Deal Could Spark A New AI Arms Race With Nvidia...
2. Is Nvidia Stock a Buy After AI Partnerships with Intel...
3. 1 Reason I'm Watching Palantir (PLTR) Stock in 2026...

============================================================
Powered by Hybrid (YFinance + Polygon)
```

### Check Your Watchlist

```bash
python3 finwiz.py watchlist
```

Shows curated AI stocks with real-time prices.

### Get Latest News

```bash
# Company-specific news
python3 finwiz.py news NVDA

# More articles
python3 finwiz.py news NVDA --limit 10
```

### View Financial Data

```bash
python3 finwiz.py financials GOOGL
```

**Output:**
```
💼 Financial data for GOOGL
============================================================

1. Q2 2025
   Period: 2025-04-01 to 2025-06-30
   Revenue:      $96.43B
   Net Income:   $28.20B
   EPS:          $2.31
   Total Assets: $425.37B

2. Q1 2025
   Period: 2025-01-01 to 2025-03-31
   Revenue:      $94.12B
   Net Income:   $26.89B
   ...
```

### Get Price History

```bash
# Last 30 days
python3 finwiz.py history MSFT

# Custom period
python3 finwiz.py history MSFT --days 90
```

**Output:**
```
📈 Price history for MSFT (last 30 days)
============================================================

Date       Open     High     Low      Close    Volume
------------------------------------------------------------
2025-09-08 $522.50 $525.30 $520.10 $523.98  18,234,567
2025-09-09 $524.00 $527.50 $522.80 $526.45  19,456,123
...

Statistics (30 days):
  Average:  $521.34
  High:     $529.80
  Low:      $515.22
  Change:   +$8.76 (+1.70%)
```

### Compare Stocks

```bash
python3 finwiz.py compare NVDA AMD INTC
```

**Output:**
```
📊 Comparing 3 stocks
============================================================

Metric              NVDA         AMD        INTC
------------------------------------------------------------
Price            $185.04     $142.50      $45.23
Change %          -0.25%      +1.34%      -2.10%
Volume           139.1M       42.3M       28.5M
```

## All Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `quote` | Get single stock quote | `finwiz.py quote NVDA` |
| `quotes` | Get multiple quotes | `finwiz.py quotes NVDA MSFT` |
| `news` | Get recent news | `finwiz.py news NVDA --limit 5` |
| `financials` | Get financial data | `finwiz.py financials GOOGL` |
| `history` | Get price history | `finwiz.py history MSFT --days 30` |
| `watchlist` | Show AI watchlist | `finwiz.py watchlist` |
| `morning-brief` | Daily market brief | `finwiz.py morning-brief` |
| `compare` | Compare stocks | `finwiz.py compare NVDA AMD` |

## Tips & Tricks

### 1. Create an Alias

Add to your `.bashrc` or `.zshrc`:

```bash
alias finwiz='cd /path/to/ai-stock-research && source venv/bin/activate && python3 finwiz.py'
```

Then use from anywhere:
```bash
finwiz quote NVDA
```

### 2. Make it Globally Executable

```bash
# Create symlink (macOS/Linux)
sudo ln -s /path/to/ai-stock-research/finwiz.py /usr/local/bin/finwiz

# Then use from anywhere
finwiz quote NVDA
```

### 3. Pipe to Less for Long Output

```bash
python3 finwiz.py news NVDA --limit 20 | less
```

### 4. Save Output to File

```bash
python3 finwiz.py morning-brief > ~/Desktop/ai-brief-$(date +%Y%m%d).txt
```

### 5. Create a Daily Brief Script

Create `daily-brief.sh`:
```bash
#!/bin/bash
cd /path/to/ai-stock-research
source venv/bin/activate
python3 finwiz.py morning-brief
```

Run with cron every morning at 9:30 AM:
```bash
30 9 * * 1-5 /path/to/daily-brief.sh | mail -s "AI Market Brief" you@email.com
```

## Configuration

### Choose Your Data Provider

Edit `.env` file:

```bash
# Option 1: Auto (recommended - uses best available)
DEFAULT_PROVIDER=auto

# Option 2: YFinance only (100% free, no API key)
DEFAULT_PROVIDER=yfinance

# Option 3: Hybrid (free prices + quality news)
DEFAULT_PROVIDER=hybrid
POLYGON_API_KEY=your-key-here  # Optional
```

### Customize Watchlists

Edit files in `watchlists/` directory:

```bash
# Add your favorite stocks
vim watchlists/ai_large_cap.json
```

## Troubleshooting

### "Command not found: python3"

Try `python` instead:
```bash
python finwiz.py quote NVDA
```

### "No module named 'yfinance'"

Install dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Rate limit exceeded"

You're using Polygon on free tier. Switch to YFinance:
```bash
# Set in .env
DEFAULT_PROVIDER=yfinance
```

### Slow Response

First request may be slow as data loads. Subsequent requests are faster.

## Real-World Use Cases

### 1. Pre-Market Check (Before 9:30 AM)

```bash
python3 finwiz.py morning-brief
```

### 2. Quick Price Check During Trading

```bash
python3 finwiz.py quote NVDA
```

### 3. End-of-Day Review

```bash
python3 finwiz.py watchlist
python3 finwiz.py news NVDA --limit 10
```

### 4. Weekend Research

```bash
# Compare chip makers
python3 finwiz.py compare NVDA AMD INTC

# Check financials
python3 finwiz.py financials NVDA
python3 finwiz.py history NVDA --days 90
```

### 5. Monitor Portfolio

Create a script `my-portfolio.sh`:
```bash
#!/bin/bash
python3 finwiz.py quotes NVDA MSFT GOOGL META AMZN TSLA
```

## Advanced Usage

### Custom Scripts

```python
#!/usr/bin/env python3
from finwiz import FinWiz
import asyncio

async def custom_analysis():
    async with FinWiz() as fw:
        # Your custom logic
        await fw.cmd_quote("NVDA")
        await fw.cmd_news("NVDA", limit=3)

asyncio.run(custom_analysis())
```

### Batch Processing

```bash
# Check multiple stocks
for ticker in NVDA MSFT GOOGL META AMZN; do
    python3 finwiz.py quote $ticker
    sleep 1
done
```

### Export to CSV

```bash
python3 finwiz.py quotes NVDA MSFT GOOGL | awk '{print $1","$2","$3","$4}' > stocks.csv
```

## Getting Help

```bash
# General help
python3 finwiz.py --help

# Command-specific help
python3 finwiz.py quote --help
python3 finwiz.py history --help
```

## What's FREE vs What Requires API Key

### 100% FREE (No API Key):
- ✅ Real-time stock quotes (~15 min delay)
- ✅ Historical price data (unlimited)
- ✅ Basic news feed
- ✅ Financial statements
- ✅ All FinWiz commands

### Enhanced with Polygon API (Optional):
- 🔥 Higher quality news articles
- 🔥 More news sources
- 🔥 Market status details

**Bottom Line**: FinWiz works perfectly without any API keys!

## Next Steps

1. **Try it now**: `python3 finwiz.py morning-brief`
2. **Set up alias**: Add to your shell config
3. **Customize watchlists**: Edit JSON files
4. **Schedule daily brief**: Use cron
5. **Explore providers**: Read [PROVIDER_ARCHITECTURE.md](PROVIDER_ARCHITECTURE.md)

## Support

- **Issues**: Create GitHub issue
- **Documentation**: See [README.md](README.md)
- **Architecture**: See [PROVIDER_ARCHITECTURE.md](PROVIDER_ARCHITECTURE.md)
- **Tests**: Run `python3 test_providers.py`

---

**Happy Trading! 📈**

*Remember: This tool is for research purposes only. Not financial advice. Always do your own due diligence.*
