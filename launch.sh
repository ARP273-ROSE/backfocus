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
        echo "Install with: sudo apt-get install python3 python3-venv python3-pip"
    elif command -v dnf &>/dev/null; then
        echo "Install with: sudo dnf install python3 python3-pip"
    elif command -v brew &>/dev/null; then
        echo "Install with: brew install python"
    elif command -v pacman &>/dev/null; then
        echo "Install with: sudo pacman -S python"
    else
        echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    fi
    exit 1
fi

PY_VERSION=$("$PYTHON_CMD" --version 2>&1)
echo "[OK] Found: $PY_VERSION"

# === Venv local to each PC (not in the synced NAS folder) ===
VENV_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/BackfocusCalculator/venv"

# --- Check if venv exists and works ---
VENV_OK=0
if [ -x "$VENV_DIR/bin/python" ]; then
    "$VENV_DIR/bin/python" -c "print('ok')" &>/dev/null && VENV_OK=1
fi

if [ "$VENV_OK" = "0" ]; then
    if [ -d "$VENV_DIR" ]; then
        echo "[!] Broken virtual environment. Recreating..."
        rm -rf "$VENV_DIR"
    fi
    echo ""
    echo "Creating virtual environment..."
    mkdir -p "$(dirname "$VENV_DIR")"
    "$PYTHON_CMD" -m venv "$VENV_DIR" || {
        echo "[WARNING] Could not create venv, running directly..."
        # Fall through to launch without venv
        echo ""
        echo "Starting Backfocus Calculator..."
        echo ""
        nohup "$PYTHON_CMD" "$SCRIPT_DIR/backfocus.py" >/dev/null 2>&1 &
        disown 2>/dev/null
        exit 0
    }
    echo "[OK] Virtual environment created"
fi

PYTHON_CMD="$VENV_DIR/bin/python"
echo "[OK] Using virtual environment: $VENV_DIR"

# --- Install dependencies (skip if requirements.txt unchanged) ---
MARKER="$VENV_DIR/.deps_installed"
if [ ! -f "$MARKER" ] || ! diff -q "$SCRIPT_DIR/requirements.txt" "$MARKER" &>/dev/null; then
    echo "Installing dependencies..."
    "$PYTHON_CMD" -m pip install -q -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || true
    cp "$SCRIPT_DIR/requirements.txt" "$MARKER" 2>/dev/null || true
    echo "[OK] Dependencies installed"
fi

# --- Launch (detach from terminal) ---
echo ""
echo "Starting Backfocus Calculator..."
echo ""
nohup "$PYTHON_CMD" "$SCRIPT_DIR/backfocus.py" >/dev/null 2>&1 &
disown 2>/dev/null
exit 0
