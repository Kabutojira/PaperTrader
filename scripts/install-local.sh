#!/usr/bin/env bash
set -euo pipefail

MODE="link"
case "${1:-}" in
  "") ;;
  --copy) MODE="copy" ;;
  -h|--help)
    cat <<'USAGE'
Usage: ./scripts/install-local.sh [--copy]

Default: create a safe symlink in ~/.hermes/skills/papertrader.
--copy:  copy the skill directory instead.

The script never overwrites an existing non-matching destination.
USAGE
    exit 0
    ;;
  *)
    echo "Unknown option: $1" >&2
    exit 2
    ;;
esac

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/Skills/papertrader"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
DESTINATION="$HERMES_HOME/skills/papertrader"

if [[ ! -f "$SOURCE/SKILL.md" ]]; then
  echo "Missing source skill: $SOURCE/SKILL.md" >&2
  exit 1
fi

mkdir -p "$(dirname "$DESTINATION")"

if [[ -L "$DESTINATION" ]]; then
  CURRENT="$(readlink "$DESTINATION")"
  if [[ "$CURRENT" == "$SOURCE" ]]; then
    echo "PaperTrader skill is already linked: $DESTINATION"
    exit 0
  fi
  echo "Destination is an existing symlink to a different target: $DESTINATION -> $CURRENT" >&2
  exit 1
fi

if [[ -e "$DESTINATION" ]]; then
  echo "Destination already exists; refusing to overwrite: $DESTINATION" >&2
  echo "Back it up or remove it explicitly, then rerun this script." >&2
  exit 1
fi

if [[ "$MODE" == "copy" ]]; then
  cp -R "$SOURCE" "$DESTINATION"
  echo "Copied PaperTrader skill to: $DESTINATION"
else
  ln -s "$SOURCE" "$DESTINATION"
  echo "Linked PaperTrader skill: $DESTINATION -> $SOURCE"
fi

echo "Start a new Hermes session, then run: /papertrader review system readiness"
