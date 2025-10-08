# FinWiz Quick Start Guide

**Get stock market data in seconds - no API keys required!**

## Installation (60 seconds)

```bash
# 1. Navigate to project
cd /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies (if not already done)
pip install -r requirements.txt

# 4. Install finwiz globally (optional but recommended)
pip install -e .

# 5. You're ready! No API keys needed for basic functionality
```

**Note**: Step 4 makes `finwiz` accessible from anywhere. Without it, use `python3 finwiz.py` instead.

See [INSTALL.md](INSTALL.md) for detailed installation options.

## Quick Examples

### Get a Stock Quote (FREE!)

```bash
# New simple syntax
finwiz NVDA

# Old syntax (still works)
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
# New simple syntax
finwiz -r NVDA MSFT GOOGL
finwiz --quotes NVDA MSFT GOOGL

# Or just list multiple tickers (auto-detects)
finwiz NVDA MSFT GOOGL

# Old syntax (still works)
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
# New simple syntax
finwiz -b
finwiz --morning-brief

# Old syntax (still works)
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
# New simple syntax
finwiz -w
finwiz --watchlist

# Old syntax (still works)
python3 finwiz.py watchlist
```

Shows curated AI stocks with real-time prices.

### Get Latest News

```bash
# New simple syntax
finwiz -n NVDA
finwiz -n NVDA --limit 10

# Old syntax (still works)
python3 finwiz.py news NVDA
python3 finwiz.py news NVDA --limit 10
```

### View Financial Data

```bash
# New simple syntax
finwiz -f GOOGL
finwiz -f GOOGL --periods 8

# Old syntax (still works)
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
# New simple syntax (last 30 days)
finwiz -H MSFT

# Custom period
finwiz -H MSFT --days 90
finwiz --history MSFT --days 90

# Old syntax (still works)
python3 finwiz.py history MSFT
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
# New simple syntax
finwiz -c NVDA AMD INTC
finwiz --compare NVDA AMD INTC

# Old syntax (still works)
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

| Flag | Long Form | Description | Example |
|------|-----------|-------------|---------|
| (none) | - | Single stock quote | `finwiz NVDA` |
| `-r` | `--quotes` | Multiple quotes | `finwiz -r NVDA MSFT` |
| `-n` | `--news` | Recent news | `finwiz -n NVDA --limit 5` |
| `-f` | `--financials` | Financial data | `finwiz -f GOOGL` |
| `-H` | `--history` | Price history | `finwiz -H MSFT --days 30` |
| `-w` | `--watchlist` | AI watchlist | `finwiz -w` |
| `-b` | `--morning-brief` | Market brief | `finwiz -b` |
| `-c` | `--compare` | Compare stocks | `finwiz -c NVDA AMD` |

## Tips & Tricks

### 1. Install Globally (Recommended)

Make `finwiz` accessible from anywhere:

```bash
cd /path/to/ai-stock-research
source venv/bin/activate
pip install -e .
```

Then use from any directory:
```bash
finwiz NVDA
finwiz -r NVDA MSFT GOOGL
```

See [INSTALL.md](INSTALL.md) for more installation options.

### 2. Get Help Anytime

```bash
finwiz --help
```

Shows all available commands and options.

### 3. Pipe to Less for Long Output

```bash
finwiz -n NVDA --limit 20 | less
```

### 4. Save Output to File

```bash
finwiz -b > ~/Desktop/ai-brief-$(date +%Y%m%d).txt
```

### 5. Create a Daily Brief Script

Create `daily-brief.sh`:
```bash
#!/bin/bash
finwiz -b
```

Run with cron every morning at 9:30 AM:
```bash
30 9 * * 1-5 finwiz -b | mail -s "AI Market Brief" you@email.com
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

### "Command not found: finwiz"

Install globally:
```bash
source venv/bin/activate
pip install -e .
```

Or use old syntax:
```bash
python3 finwiz.py NVDA
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
finwiz -b
```

### 2. Quick Price Check During Trading

```bash
finwiz NVDA
```

### 3. End-of-Day Review

```bash
finwiz -w
finwiz -n NVDA --limit 10
```

### 4. Weekend Research

```bash
# Compare chip makers
finwiz -c NVDA AMD INTC

# Check financials and history
finwiz -f NVDA
finwiz -H NVDA --days 90
```

### 5. Monitor Portfolio

Create a script `my-portfolio.sh`:
```bash
#!/bin/bash
finwiz -r NVDA MSFT GOOGL META AMZN TSLA
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
    finwiz $ticker
    sleep 1
done
```

### Export to CSV

```bash
finwiz -r NVDA MSFT GOOGL | awk '{print $1","$2","$3","$4}' > stocks.csv
```

## Getting Help

```bash
# General help
finwiz --help

# Shows all commands, flags, and options
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

1. **Install globally**: `pip install -e .`
2. **Try it now**: `finwiz -b`
3. **Get help**: `finwiz --help`
4. **Customize watchlists**: Edit JSON files
5. **Schedule daily brief**: Use cron
6. **Explore providers**: Read [PROVIDER_ARCHITECTURE.md](PROVIDER_ARCHITECTURE.md)

## Support

- **Issues**: Create GitHub issue
- **Documentation**: See [README.md](README.md)
- **Architecture**: See [PROVIDER_ARCHITECTURE.md](PROVIDER_ARCHITECTURE.md)
- **Tests**: Run `python3 test_providers.py`

---

**Happy Trading! 📈**

*Remember: This tool is for research purposes only. Not financial advice. Always do your own due diligence.*
