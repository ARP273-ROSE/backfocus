#!/usr/bin/env bash
# Backfocus Calculator - Auto Launcher (Linux/macOS)
set -e

echo "============================================"
echo "  Backfocus Calculator - Auto Launcher"
echo "============================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# --- Find Python ---
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python 3.8+ not found."
    echo ""
    if command -v apt-get &>/dev/null; then
        echo "Install with: sudo apt-get install python3 python3-tk python3-venv"
    elif command -v dnf &>/dev/null; then
        echo "Install with: sudo dnf install python3 python3-tkinter"
    elif command -v brew &>/dev/null; then
        echo "Install with: brew install python-tk"
    elif command -v pacman &>/dev/null; then
        echo "Install with: sudo pacman -S python tk"
    else
        echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    fi
    exit 1
fi

PY_VERSION=$("$PYTHON_CMD" --version 2>&1)
echo "[OK] Found: $PY_VERSION"

# --- Check tkinter ---
if ! "$PYTHON_CMD" -c "import tkinter" &>/dev/null; then
    echo "[ERROR] tkinter is not available."
    if command -v apt-get &>/dev/null; then
        echo "Install with: sudo apt-get install python3-tk"
    elif command -v brew &>/dev/null; then
        echo "Install with: brew install python-tk"
    fi
    exit 1
fi
echo "[OK] tkinter available"

# --- Virtual environment ---
if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    # Verify the existing venv actually works (not broken by removed Python)
    if ! "$SCRIPT_DIR/venv/bin/python" -c "import sys; sys.exit(0)" &>/dev/null; then
        echo "[!] Broken virtual environment (base Python removed). Recreating..."
        rm -rf "$SCRIPT_DIR/venv"
    fi
fi

if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    "$PYTHON_CMD" -m venv "$SCRIPT_DIR/venv" || {
        echo "[WARNING] Could not create venv, running directly..."
        PYTHON_CMD="$PYTHON_CMD"
    }
    if [ -d "$SCRIPT_DIR/venv" ]; then
        echo "[OK] Virtual environment created"
    fi
fi

if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
    echo "[OK] Using virtual environment"
fi

# --- Install dependencies ---
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    "$PYTHON_CMD" -m pip install -r "$SCRIPT_DIR/requirements.txt" --quiet 2>/dev/null || true
fi

# --- Launch (detach from terminal) ---
echo ""
echo "Starting Backfocus Calculator..."
echo ""
nohup "$PYTHON_CMD" "$SCRIPT_DIR/backfocus.py" >/dev/null 2>&1 &
disown 2>/dev/null
exit 0
