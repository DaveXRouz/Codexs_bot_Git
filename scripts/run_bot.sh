#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

pip install --upgrade pip >/dev/null
pip install -e . >/dev/null

export PYTHONPATH="src:${PYTHONPATH:-}"
python -m codexs_bot.bot

