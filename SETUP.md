# FinWiz Setup Guide

This guide shows you how to set up FinWiz so you can run it from anywhere without manually activating the virtual environment.

## Current Setup

FinWiz is installed in a virtual environment at:
```
/Users/manu/ASCIIDocs/CC_MCP/ai-stock-research/venv
```

## Option 1: Use Activation Script (Recommended)

We've created a convenient activation script that handles everything for you.

### Quick Commands

```bash
# From the ai-stock-research directory:
./activate_finwiz.sh NVDA              # Run finwiz with arguments
./activate_finwiz.sh -w                # Show watchlist
./activate_finwiz.sh -r NVDA MSFT      # Multiple quotes

# Or activate the environment in your current shell:
source activate_finwiz.sh              # Activates venv
finwiz NVDA                            # Then use finwiz directly
```

## Option 2: Add Shell Aliases (Best for Daily Use)

Add FinWiz aliases to your shell configuration for permanent access.

### For Zsh (macOS default)

Add this line to `~/.zshrc`:
```bash
source /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research/finwiz_aliases.sh
```

Then reload your shell:
```bash
source ~/.zshrc
```

### For Bash

Add this line to `~/.bashrc`:
```bash
source /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research/finwiz_aliases.sh
```

Then reload your shell:
```bash
source ~/.bashrc
```

### Available Aliases

Once loaded, you can use these commands from anywhere:

```bash
finwiz NVDA          # Quick quote
fwq NVDA             # Quick quote (short)
fwn NVDA             # Get news
fwf GOOGL            # Financial statements
fwh MSFT --days 90   # Price history
fwc NVDA AMD INTC    # Compare stocks
fww                  # Show watchlist
fwb                  # Morning brief
finwiz-activate      # Activate environment in current shell
```

## Option 3: Manual Activation

If you prefer to activate the environment manually each time:

```bash
# Navigate to the directory
cd /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research

# Activate the virtual environment
source venv/bin/activate

# Now use finwiz
finwiz NVDA

# When done, deactivate
deactivate
```

## Verification

Test that everything works:

```bash
# Test help
finwiz --help

# Test a quote
finwiz NVDA

# Test watchlist
finwiz -w
```

## Troubleshooting

### "finwiz: command not found"

If you get this error:
1. Make sure you've activated the environment (see options above)
2. Verify the installation: `source venv/bin/activate && which finwiz`
3. Reinstall if needed: `source venv/bin/activate && pip install -e .`

### Virtual environment not found

If the venv is missing, recreate it:
```bash
cd /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Permission denied

Make the activation script executable:
```bash
chmod +x activate_finwiz.sh
```

## Recommended Setup

For the best experience, we recommend **Option 2** (shell aliases):

1. Add the source line to your shell config (~/.zshrc or ~/.bashrc)
2. Reload your shell
3. Use `finwiz` or the short aliases from anywhere

This gives you:
- ✅ Run finwiz from any directory
- ✅ No need to remember the path
- ✅ Automatic environment activation
- ✅ Convenient short aliases
- ✅ Always available in new terminal windows

## Next Steps

Once set up, check out:
- [QUICK_START.md](QUICK_START.md) - Common commands and examples
- [README.md](README.md) - Full documentation
- [PROVIDER_ARCHITECTURE.md](PROVIDER_ARCHITECTURE.md) - Technical details
