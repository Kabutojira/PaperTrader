#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 -m py_compile \
  scripts/validate_repo.py \
  scripts/validate_signal.py \
  Skills/papertrader/scripts/validate_signal.py

python3 scripts/validate_repo.py
python3 scripts/validate_signal.py Skills/papertrader/templates/signal.example.json

echo "ALL CHECKS PASSED"
