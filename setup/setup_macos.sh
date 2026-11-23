#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Error: $PYTHON_BIN was not found. Please install Python 3 first."
    exit 1
fi

echo "[1/4] Creating virtual environment at $ROOT_DIR/.venv"
"$PYTHON_BIN" -m venv .venv

source .venv/bin/activate

echo "[2/4] Upgrading pip"
python -m pip install --upgrade pip setuptools wheel

echo "[3/4] Installing required packages (MPS preferred, CPU fallback)"
python scripts/install_dependencies.py

echo "[4/4] Checking environment"
python scripts/check_environment.py

echo
echo "Setup complete."
echo "On Apple Silicon, PyTorch may use the MPS backend when available."
echo "Activate the environment with:"
echo "  source .venv/bin/activate"
echo "Then launch Jupyter with:"
echo "  jupyter lab"
