#!/usr/bin/env bash
# Setup for CPH Agentic Hack (macOS / Linux). Run from the repository root:
#   ./src/scripts/setup.sh
# Optional: PYTHON=/path/to/python3.12 ./src/scripts/setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"

# An existing .venv is reused only if it has Python 3.11+ and a working pip.
venv_ok() {
  [ -x "$PY" ] \
    && "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null \
    && "$PY" -m pip --version >/dev/null 2>&1
}

# Pick the first Python 3.11+ on PATH (macOS often ships an older python3).
find_python() {
  for candidate in "${PYTHON:-}" python3.13 python3.12 python3.11 python3; do
    if [ -n "$candidate" ] && command -v "$candidate" >/dev/null 2>&1 \
      && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

echo "==> 1/4 Creating virtual environment in .venv"
if ! venv_ok; then
  if [ -d .venv ]; then
    echo "    Existing .venv is broken or uses Python < 3.11: recreating it."
    rm -rf .venv
  fi
  if ! PYTHON_BIN="$(find_python)"; then
    echo "ERROR: Python 3.11+ not found. Install it (python.org, or 'brew install python@3.12') and rerun." >&2
    exit 1
  fi
  if ! "$PYTHON_BIN" -m venv .venv; then
    rm -rf .venv
    echo "ERROR: could not create .venv. On Ubuntu/Debian run: sudo apt install python3-venv" >&2
    exit 1
  fi
fi

echo "==> 2/4 Installing dependencies"
"$PY" -m pip install --upgrade pip --quiet
"$PY" -m pip install -e ".[dev]" --quiet

echo "==> 3/4 Downloading the Copilot SDK runtime (optional)"
if ! "$PY" -m copilot download-runtime; then
  echo "WARNING: could not download the Copilot runtime now. The SDK will retry on first use. The app still works without it." >&2
fi

echo "==> 4/4 Seeding the SQLite database with synthetic data"
"$PY" src/backend/scripts/seed.py

cat <<'EOF'

Done! Next steps:
  source .venv/bin/activate
  python src/scripts/check_env.py
  uvicorn backend.app.main:app --app-dir src --reload
  then open http://localhost:8000
EOF
