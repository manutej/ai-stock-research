#!/bin/bash
# FinWiz Shell Aliases
#
# Add this to your ~/.bashrc or ~/.zshrc:
#   source /Users/manu/ASCIIDocs/CC_MCP/ai-stock-research/finwiz_aliases.sh
#
# Or run these commands directly in your shell

# Define the finwiz base directory
FINWIZ_DIR="/Users/manu/ASCIIDocs/CC_MCP/ai-stock-research"

# Alias to run finwiz from anywhere
alias finwiz="source $FINWIZ_DIR/venv/bin/activate && finwiz"

# Convenience aliases for common commands
alias fwq="source $FINWIZ_DIR/venv/bin/activate && finwiz"           # Quick quote
alias fwn="source $FINWIZ_DIR/venv/bin/activate && finwiz -n"        # News
alias fwf="source $FINWIZ_DIR/venv/bin/activate && finwiz -f"        # Financials
alias fwh="source $FINWIZ_DIR/venv/bin/activate && finwiz -H"        # History
alias fwc="source $FINWIZ_DIR/venv/bin/activate && finwiz -c"        # Compare
alias fww="source $FINWIZ_DIR/venv/bin/activate && finwiz -w"        # Watchlist
alias fwb="source $FINWIZ_DIR/venv/bin/activate && finwiz -b"        # Morning brief

# Function to activate finwiz environment in current shell
finwiz-activate() {
    source "$FINWIZ_DIR/venv/bin/activate"
    echo "✓ FinWiz environment activated"
    echo "Run 'deactivate' to exit"
}

echo "✓ FinWiz aliases loaded"
echo "Available commands:"
echo "  finwiz NVDA       - Run finwiz from anywhere"
echo "  fwq NVDA          - Quick quote"
echo "  fwn NVDA          - Get news"
echo "  fww               - Show watchlist"
echo "  finwiz-activate   - Activate venv in current shell"
