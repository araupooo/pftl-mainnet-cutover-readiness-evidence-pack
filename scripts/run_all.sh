#!/bin/bash
# run_all.sh — full measurement run: probes + cadence + analysis.
# Usage: bash scripts/run_all.sh
# Writes fresh outputs/ files, then derives findings.json and run-manifest.json.
set -eu
PACK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PACK_ROOT"
bash scripts/probe_all.sh
python3 scripts/cadence.py --samples "${CADENCE_SAMPLES:-21}" --interval 30 \
  --out-prefix outputs/cadence-run1 > outputs/cadence-run1.log 2>&1 || {
    echo "cadence failed; see outputs/cadence-run1.log"; exit 1; }
python3 src/ws_probe.py 20 || true
# ws_probe.py writes ws-*.json into the current directory; move them into outputs/
for f in ws-ledger-443.json ws-ledger-6005.json ws-control-xrpl.json; do
  [ -f "$f" ] && mv "$f" outputs/
done
python3 scripts/analyze.py
echo "run_all.sh complete."
