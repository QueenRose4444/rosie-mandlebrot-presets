#!/bin/bash
# Build index.json and, when it changed, sign it with the index key.
set -euo pipefail
cd "$(dirname "$0")/.."
# Without the key an unsigned index would be refused by every app: leave the
# signed one as it is.
if [ -z "${INDEX_SIGNING_KEY:-}" ]; then
  echo "::warning::INDEX_SIGNING_KEY is not set: the index was not refreshed"
  exit 0
fi
if [ "$(python tools/build_index.py)" = "unchanged" ]; then
  echo "index unchanged"
  exit 0
fi
command -v minisign >/dev/null || { sudo apt-get update -qq; sudo apt-get install -y -qq minisign; }
printf '%s\n' "$INDEX_SIGNING_KEY" > "$RUNNER_TEMP/index.key"
# The key has no password; minisign still asks for one on stdin.
echo | minisign -S -s "$RUNNER_TEMP/index.key" -m index.json -x index.json.minisig -t "Rosie_Mandlebrot community list"
rm -f "$RUNNER_TEMP/index.key"
minisign -V -p index.pub -m index.json -x index.json.minisig
