#!/usr/bin/env bash
# Setup for CPH Agentic Hack (macOS / Linux). Run from the repository root:
#   ./src/scripts/setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON:-python3}"

echo "==> 1/4 Creating virtual environment in .venv"
if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi
PY="$ROOT/.venv/bin/python"
"$PY" -c "import sys; assert sys.version_info >= (3, 11), f'Python 3.11+ required, found {sys.version}'"

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
