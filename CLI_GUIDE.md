# FinWiz - Command Line Interface Guide

**Version**: 1.0
**Philosophy**: Simple, intuitive, powerful

---

## Design Principles

### 1. Zero Configuration Required
- **Works immediately**: `finwiz NVDA` runs without setup
- **No API keys needed**: Uses free YFinance data by default
- **Smart defaults**: Sensible values for all options

### 2. Intuitive Command Structure
- **Natural language**: Commands read like sentences
- **Consistent patterns**: Same structure across all operations
- **Minimal typing**: Short flags for common tasks

### 3. Clear Visual Feedback
- **Emoji indicators**: 📊 for quotes, 📰 for news, 💼 for financials
- **Formatted output**: Tables, alignment, thousands separators
- **Context-aware**: Different views for single vs. multiple tickers

---

## Quick Reference

### Most Common Commands (90% of usage)

```bash
# Get a stock quote (THE most common use)
finwiz NVDA

# Multiple quotes
finwiz NVDA MSFT GOOGL

# Latest news
finwiz -n NVDA

# Show your watchlist
finwiz -w
```

**That's it!** These 4 commands cover most use cases.

---

## Complete Command Reference

### Basic Quote Operations

#### Single Stock Quote (Default)
```bash
finwiz NVDA
```
**Shows**: Price, change, open/high/low, volume, timestamp

#### Multiple Stock Quotes
```bash
finwiz NVDA MSFT GOOGL
# or explicitly
finwiz -r NVDA MSFT GOOGL
```
**Shows**: Compact table with all tickers

---

### News & Information

#### Latest News for Stock
```bash
finwiz -n NVDA
```
**Shows**: 5 most recent articles (title, source, date, URL)

#### More Articles
```bash
finwiz -n NVDA --limit 10
```
**Shows**: 10 most recent articles

#### General Market News
```bash
finwiz -n
```
**Shows**: Top market news (no specific ticker)

---

### Financial Analysis

#### Financial Statements
```bash
finwiz -f GOOGL
```
**Shows**: Last 4 quarters (revenue, net income, EPS, assets)

#### More Periods
```bash
finwiz -f GOOGL --periods 8
```
**Shows**: Last 8 quarters

---

### Historical Data

#### Price History (30 days)
```bash
finwiz -H MSFT
```
**Shows**: Last 10 days + statistics (avg, high, low, change)

#### Custom Period
```bash
finwiz -H MSFT --days 90
```
**Shows**: 90-day statistics

---

### Comparison & Analysis

#### Compare Stocks
```bash
finwiz -c NVDA AMD INTC
```
**Shows**: Side-by-side comparison table

---

### Watchlists & Briefs

#### AI Stock Watchlist
```bash
finwiz -w
```
**Shows**:
- Large cap AI leaders (NVDA, MSFT, GOOGL, etc.)
- AI startups & high growth stocks

#### Morning Brief
```bash
finwiz -b
```
**Shows**:
- Market status (open/closed)
- Major AI stock quotes
- Latest AI sector news

---

## Command Line Flags

### Operation Flags (pick one)

| Flag | Long Form | Description | Example |
|------|-----------|-------------|---------|
| `-r` | `--quotes` | Multiple stock quotes | `finwiz -r NVDA MSFT` |
| `-n` | `--news` | Recent news articles | `finwiz -n NVDA` |
| `-f` | `--financials` | Financial statements | `finwiz -f GOOGL` |
| `-H` | `--history` | Price history chart | `finwiz -H MSFT` |
| `-c` | `--compare` | Compare stocks | `finwiz -c NVDA AMD` |
| `-w` | `--watchlist` | Show watchlist | `finwiz -w` |
| `-b` | `--morning-brief` | Morning market brief | `finwiz -b` |

### Option Flags (modifiers)

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--limit N` | int | 5 | Number of news articles |
| `--periods N` | int | 4 | Number of financial periods |
| `--days N` | int | 30 | Number of days for history |

---

## Smart Behaviors

### Automatic Uppercase
All ticker symbols are automatically converted to uppercase:
```bash
finwiz nvda      # Same as: finwiz NVDA
finwiz msft googl  # Same as: finwiz MSFT GOOGL
```

### Intelligent Defaults
- **No flags**: Shows detailed quote for single ticker, compact table for multiple
- **News without ticker**: Shows general market news
- **Smart number formatting**: Volumes show "45.6M" instead of "45678900"

### Error Handling
Clear, actionable error messages:
```bash
$ finwiz -c NVDA
Error: Please specify at least 2 tickers to compare

$ finwiz -f
Error: Please specify a ticker symbol
```

---

## Output Examples

### Single Quote Output
```
📊 Quote for NVDA
============================================================

Price:     $495.23
Change:    +12.45 (+2.58%)
Open:      $482.78
High:      $497.12
Low:       $481.90
Volume:    45,678,900
Provider:  yfinance
Updated:   2025-11-10 16:00:00
```

### Multiple Quotes Output
```
📊 Quotes for 3 stocks
============================================================

Ticker  Price      Change    Change%   Volume
------------------------------------------------------------
NVDA    $495.23    +12.45    (+2.58%)  Vol: 45,678,900
MSFT    $372.89    +3.21     (+0.87%)  Vol: 23,456,789
GOOGL   $142.67    -1.23     (-0.85%)  Vol: 18,234,567
```

### Comparison Output
```
📊 Comparing 3 stocks
============================================================

Metric             NVDA        MSFT       GOOGL
------------------------------------------------------------
Price           $495.23     $372.89     $142.67
Change %          +2.58%      +0.87%      -0.85%
Volume            45.6M       23.4M       18.2M
```

---

## Common Workflows

### Daily Research Routine
```bash
# 1. Morning brief
finwiz -b

# 2. Check specific stocks
finwiz NVDA MSFT GOOGL

# 3. Read news on interesting movers
finwiz -n NVDA

# 4. Deep dive on one stock
finwiz -f NVDA
finwiz -H NVDA --days 90
```

### Quick Price Check
```bash
finwiz NVDA
```
That's it. 11 characters including spaces.

### Compare Competitors
```bash
# AI chip makers
finwiz -c NVDA AMD INTC

# Cloud providers
finwiz -c MSFT GOOGL AMZN

# EV makers
finwiz -c TSLA RIVN LCID
```

---

## Tips & Tricks

### 1. Alias for Even Faster Access
```bash
# Add to ~/.bashrc or ~/.zshrc
alias fz='finwiz'

# Now you can:
fz NVDA            # Instead of: finwiz NVDA
fz -w              # Instead of: finwiz -w
```

### 2. Combine with Shell Tools
```bash
# Save news to file
finwiz -n NVDA > nvda_news.txt

# Watch a stock (refresh every 60 seconds)
watch -n 60 finwiz NVDA

# Compare against a saved baseline
finwiz NVDA > baseline.txt
# Later:
diff baseline.txt <(finwiz NVDA)
```

### 3. Batch Research
```bash
# Create a script to check your portfolio
cat > check_portfolio.sh <<EOF
#!/bin/bash
echo "=== My Portfolio ==="
finwiz NVDA MSFT GOOGL AAPL AMZN
EOF
chmod +x check_portfolio.sh
./check_portfolio.sh
```

---

## Configuration

### Provider Selection (Advanced)

By default, FinWiz uses free YFinance data (no API key required).

For premium features, set environment variables:

```bash
# Use Polygon.io (requires API key)
export POLYGON_API_KEY="your-key-here"
export PROVIDER="polygon"

# Use hybrid (Polygon with YFinance fallback)
export PROVIDER="hybrid"
```

**Note**: 95% of users don't need to configure anything!

---

## Keyboard Shortcuts

### In Your Terminal

| Key | Action |
|-----|--------|
| `Ctrl+C` | Cancel current operation |
| `Ctrl+L` | Clear screen |
| `↑` / `↓` | Navigate command history |
| `Tab` | Autocomplete ticker (if configured) |

### Useful Terminal Commands

```bash
# See command history
history | grep finwiz

# Re-run last finwiz command
!finwiz

# Run multiple commands
finwiz NVDA && finwiz -n NVDA
```

---

## Troubleshooting

### Common Issues

#### "No module named 'finwiz'"
**Solution**: Install the package
```bash
pip install -e .
```

#### "Connection timeout"
**Solution**: Check internet connection, provider might be down
```bash
# Try the free provider
unset PROVIDER
finwiz NVDA
```

#### "Invalid ticker symbol: XYZ"
**Solution**:
- Verify ticker exists (use Google Finance to confirm)
- Some tickers have suffixes (e.g., BRK.A for Berkshire Hathaway Class A)
- Currently, only simple tickers are supported (AAPL, MSFT, etc.)

#### No data returned
**Solution**:
- Stock might be delisted
- Markets might be closed (historical data still works)
- Provider rate limit reached (wait 60 seconds)

---

## Design Philosophy

### Why This CLI is Simple

1. **Sensible defaults**: `finwiz NVDA` just works
2. **Progressive disclosure**: Basic usage is simple, advanced features available
3. **Consistent patterns**: All commands follow same structure
4. **Visual hierarchy**: Emoji, alignment, spacing guide the eye
5. **Minimal configuration**: Works out of the box

### What We Avoided

❌ **Complex subcommands**: `finwiz stock get quote NVDA` → Too verbose
❌ **Required configuration**: API keys → Barrier to entry
❌ **Ambiguous output**: Raw JSON → Hard to read
❌ **Silent failures**: Errors → Clear messages instead
❌ **Hidden features**: Undocumented flags → All in `--help`

### What We Optimized For

✅ **Speed**: Fewest keystrokes for common tasks
✅ **Clarity**: Obvious what each command does
✅ **Forgiveness**: Mistakes don't break things
✅ **Discoverability**: `--help` shows everything
✅ **Consistency**: Same patterns everywhere

---

## Future Enhancements (Planned)

### Coming Soon
- Color output (green gains, red losses)
- Interactive mode with autocomplete
- Historical chart visualization (ASCII art)
- Export to CSV/JSON
- Alerts and notifications

### Under Consideration
- Custom watchlists
- Technical indicators (RSI, MACD)
- Sector analysis
- Portfolio tracking

---

## Examples by User Type

### Casual Investor
```bash
# Check your stocks once a day
finwiz AAPL MSFT GOOGL

# Read news when something moves
finwiz -n AAPL
```

### Active Trader
```bash
# Morning routine
finwiz -b

# Quick price checks throughout the day
finwiz NVDA
finwiz NVDA    # Again 30 min later

# Research before buying
finwiz -f NVDA
finwiz -H NVDA --days 180
finwiz -c NVDA AMD INTC
```

### Developer / Researcher
```bash
# Scripting
finwiz NVDA | tee data.txt

# Historical analysis
finwiz -H NVDA --days 365 > nvda_year.txt

# Batch processing
for ticker in NVDA MSFT GOOGL; do
  finwiz $ticker >> all_quotes.txt
done
```

### Financial Analyst
```bash
# Deep dive
finwiz -f NVDA --periods 12
finwiz -H NVDA --days 365
finwiz -c NVDA AMD INTC
finwiz -n NVDA --limit 20

# Compare sectors
finwiz -c NVDA AMD INTC  # Chips
finwiz -c MSFT GOOGL AMZN  # Cloud
```

---

## Getting Help

### Command Line Help
```bash
finwiz --help          # Full documentation
finwiz -h              # Short version (same as above)
```

### Documentation
- **This file**: CLI usage guide
- **README.md**: Project overview
- **TESTING_STRATEGY.md**: For contributors

### Support
- **Issues**: Report bugs on GitHub
- **Discussions**: Ask questions in GitHub Discussions
- **Email**: support@example.com

---

## Philosophy: Less is More

The best CLI is one you don't have to think about:

1. **Type less, do more**: `finwiz NVDA` beats `stock-tool --provider yfinance --ticker NVDA --output table`
2. **Learn once, use forever**: Consistent patterns mean no re-learning
3. **Fail gracefully**: Errors explain what went wrong and how to fix it
4. **No surprises**: Commands do exactly what you expect

**Remember**: If you find yourself reading this guide for basic usage, we've failed. The CLI should be self-explanatory.

---

**Last Updated**: 2025-11-10
**Maintained By**: FinWiz Core Team
