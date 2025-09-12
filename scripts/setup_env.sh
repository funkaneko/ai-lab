#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env 2>/dev/null || true
echo "\n✅ Environment ready. Activate with: source .venv/bin/activate"
