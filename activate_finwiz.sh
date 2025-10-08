#!/bin/bash
# FinWiz Quick Activation Script
#
# This script activates the virtual environment and runs finwiz
#
# Usage:
#   source activate_finwiz.sh        # Activate the environment
#   ./activate_finwiz.sh NVDA        # Run finwiz command directly
#   ./activate_finwiz.sh -w          # Show watchlist

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -e ."
    exit 1
fi

# If script is being sourced, just activate the environment
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    source "$VENV_PATH/bin/activate"
    echo "✓ FinWiz environment activated"
    echo "You can now run: finwiz NVDA"
else
    # Script is being executed, run finwiz with arguments
    source "$VENV_PATH/bin/activate"
    finwiz "$@"
fi
