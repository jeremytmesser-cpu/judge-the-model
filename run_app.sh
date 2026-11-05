#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ -x "$ROOT_DIR/.venv/bin/python" ]; then
  PYTHON="$ROOT_DIR/.venv/bin/python"
elif [ -x "$ROOT_DIR/.venv/Scripts/python.exe" ]; then
  PYTHON="$ROOT_DIR/.venv/Scripts/python.exe"
elif command -v python >/dev/null 2>&1; then
  PYTHON="$(command -v python)"
else
  echo "Python 3.11 or newer is required. Create the environment with: uv venv .venv && . .venv/bin/activate && uv pip install -r requirements.txt" >&2
  exit 1
fi

if ! "$PYTHON" -c "import streamlit" >/dev/null 2>&1; then
  echo "The project environment is not ready. Install dependencies with:" >&2
  echo "  uv venv .venv" >&2
  echo "  . .venv/bin/activate" >&2
  echo "  uv pip install -r requirements.txt" >&2
  exit 1
fi

echo "Starting the Streamlit app for Judge the Model..."
echo "Open: http://localhost:8501"
echo "Stop with Ctrl+C"
exec "$PYTHON" -m streamlit run streamlit_app.py
