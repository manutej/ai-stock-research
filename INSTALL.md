# FinWiz Installation Guide

## Quick Installation (Recommended)

Make `finwiz` globally accessible from anywhere on your system:

```bash
# Navigate to project directory
cd /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research

# Activate virtual environment
source venv/bin/activate

# Install in editable mode
pip install -e .
```

After installation, you can use `finwiz` from anywhere:

```bash
finwiz NVDA
finwiz -r NVDA MSFT GOOGL
finwiz -w
```

## Alternative: Create Alias

If you don't want to install globally, create an alias in your shell config:

### For Bash (.bashrc or .bash_profile):

```bash
alias finwiz='cd /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research && source venv/bin/activate && python3 finwiz.py'
```

### For Zsh (.zshrc):

```bash
alias finwiz='cd /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research && source venv/bin/activate && python3 finwiz.py'
```

### For Fish (~/.config/fish/config.fish):

```fish
alias finwiz='cd /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research; and source venv/bin/activate; and python3 finwiz.py'
```

After adding the alias, reload your shell:

```bash
source ~/.bashrc   # or ~/.zshrc, or restart terminal
```

## Alternative: Symlink

Create a system-wide symlink (requires sudo):

```bash
# Make script executable
chmod +x /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research/finwiz.py

# Create symlink
sudo ln -s /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research/finwiz.py /usr/local/bin/finwiz
```

**Note**: With symlink, you'll still need to activate the virtual environment first.

## Verify Installation

Test that finwiz is working:

```bash
# Show help
finwiz --help

# Quick quote
finwiz NVDA

# Morning brief
finwiz -b
```

## Uninstallation

### If installed with pip:

```bash
pip uninstall finwiz
```

### If using alias:

Remove the alias line from your shell config file.

### If using symlink:

```bash
sudo rm /usr/local/bin/finwiz
```

## Troubleshooting

### "Command not found: finwiz"

**If installed with pip:**
- Ensure virtual environment is activated: `source venv/bin/activate`
- Check installation: `pip list | grep finwiz`
- Reinstall: `pip install -e .`

**If using alias:**
- Reload shell config: `source ~/.bashrc` (or ~/.zshrc)
- Test alias directly: `alias finwiz`

### "Module not found" errors

Install dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Permission denied

Make script executable:

```bash
chmod +x finwiz.py
```

## Development Mode

If you're developing finwiz and want changes to take effect immediately:

```bash
# Install in editable mode (already done if you followed quick install)
pip install -e .

# Now any changes to finwiz.py will be immediately available
```

## Environment Configuration

Don't forget to configure your `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit with your preferences
vim .env
```

Default configuration uses free YFinance provider (no API key needed).

## Next Steps

- Read [QUICK_START.md](QUICK_START.md) for usage examples
- Check [README.md](README.md) for full documentation
- See [PROVIDER_ARCHITECTURE.md](PROVIDER_ARCHITECTURE.md) for technical details

---

**Recommendation**: Use `pip install -e .` for the best experience. It makes finwiz globally accessible while keeping code editable for development.
