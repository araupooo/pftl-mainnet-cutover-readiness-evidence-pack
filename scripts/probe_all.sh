#!/bin/bash
# probe_all.sh — re-probe every live public endpoint used by this pack and
# retain the unedited responses under outputs/.
#
# Usage: bash scripts/probe_all.sh [OUTPUT_DIR]
#   OUTPUT_DIR defaults to outputs/ relative to the pack root.
# No credentials, sessions, or accounts are used. All endpoints are public.
# Each output file's full SHA-256 is printed to the probe log so a reader can
# verify that the shipped files are the files this script produced.
set -u
PACK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$PACK_ROOT/outputs}"
mkdir -p "$OUT"
LOG="$OUT/probe-run.log"
: > "$LOG"
log() { echo "$*" | tee -a "$LOG"; }
sha() { sha256sum "$1" | awk '{print $1}'; }

log "probe_all.sh run start: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
log "pack root: $PACK_ROOT"

RPC="https://rpc.testnet.postfiat.org/"
post() { # $1 outfile $2 method-json
  curl -s -m 30 -X POST "$RPC" -H 'Content-Type: application/json' -d "$2" \
    -o "$OUT/$1" -w "%{http_code} %{time_total}s" > "$OUT/$1.http" 2>&1
  log "$1 -> $(cat "$OUT/$1.http") sha256=$(sha "$OUT/$1")"
}
get() { # $1 url $2 outfile
  curl -s -m 30 "$1" -o "$OUT/$2" -w "%{http_code} %{time_total}s %{size_download}B" > "$OUT/$2.http" 2>&1
  log "$2 -> $(cat "$OUT/$2.http") sha256=$(sha "$OUT/$2")"
  rm -f "$OUT/$2.http"
}

# --- postfiatd JSON-RPC (public proxy) ---
post rpc-server_info.json '{"method":"server_info","params":[{}]}'
post rpc-ledger.json '{"method":"ledger","params":[{"ledger_index":"validated","transactions":false,"expand":false}]}'
post rpc-ledger_closed.json '{"method":"ledger_closed","params":[{}]}'
post rpc-ledger_data.json '{"method":"ledger_data","params":[{"ledger_index":"validated","limit":5}]}'
post rpc-fee.json '{"method":"fee","params":[{}]}'
post rpc-account_info-xrpl-genesis.json '{"method":"account_info","params":[{"account":"r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59","ledger_index":"validated"}]}'
post rpc-account_info-xrpl-root.json '{"method":"account_info","params":[{"account":"rrrrrrrrrrrrrrrrrrrrBZbvji","ledger_index":"validated"}]}'
post rpc-account_info-pftl-genesis.json '{"method":"account_info","params":[{"account":"r4vhrMChCsaoFsBoCkRTRGUuc1njfr7bmA","ledger_index":"validated"}]}'
post rpc-validators.json '{"method":"validators","params":[{}]}'
post rpc-peers.json '{"method":"peers","params":[{}]}'
post rpc-invalid-method.json '{"method":"no_such_method","params":[{}]}'
post rpc-feature.json '{"method":"feature","params":[{}]}'
post rpc-server_state.json '{"method":"server_state","params":[{}]}'

# --- Validator History Service ---
get https://vhs.testnet.postfiat.org/v1/network/validators vhs-validators.json
get https://vhs.testnet.postfiat.org/v1/network/validators?unl=true vhs-validators-unl-param.json
get https://vhs.testnet.postfiat.org/v1/network/topology/nodes vhs-topology-nodes.json
get https://vhs.testnet.postfiat.org/v1/network/topology vhs-topology.json
get https://vhs.testnet.postfiat.org/v1/network/networks vhs-networks.json
get https://vhs.testnet.postfiat.org/v1/health vhs-health.json
get https://vhs.testnet.postfiat.org/v1/validators vhs-validators-index.json
get https://vhs.testnet.postfiat.org/v1/network/amendments vhs-amendments.json
get https://vhs.testnet.postfiat.org/v1/network/amendments/info vhs-amendments-info.json
get https://vhs.testnet.postfiat.org/v1/network/amendments/vote/test vhs-amendments-vote-test.json

# --- Explorer ---
get https://explorer.testnet.postfiat.org/api/v1/metrics explorer-metrics.json
get https://explorer.testnet.postfiat.org/api/v1/health explorer-health.json

# --- Published pages ---
get https://postfiat.org/ postfiat-org.html
get https://postfiat.org/whitepaper/ postfiat-whitepaper.html
get https://docs.postfiat.org docs-postfiat-org.html

# --- WebSocket upgrade probe (curl; the stdlib client in src/ws_probe.py
# cannot complete TLS through this environment's egress proxy) ---
{
  echo "== wss://rpc.testnet.postfiat.org:443 =="
  timeout 20 curl -s -i -m 15 --http1.1 -H "Connection: Upgrade" -H "Upgrade: websocket" \
    -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" -H "Sec-WebSocket-Version: 13" \
    https://rpc.testnet.postfiat.org/ | head -12 || echo "curl exit $?"
  echo "== wss://rpc.testnet.postfiat.org:6005 =="
  timeout 20 curl -s -i -m 15 --http1.1 -H "Connection: Upgrade" -H "Upgrade: websocket" \
    -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" -H "Sec-WebSocket-Version: 13" \
    https://rpc.testnet.postfiat.org:6005/ | head -12 || echo "curl exit $? (no response within timeout)"
} > "$OUT/ws-upgrade-probe.txt" 2>&1
log "ws-upgrade-probe.txt sha256=$(sha "$OUT/ws-upgrade-probe.txt")"

# --- GitHub API: amendment-test PR status (public; user object stripped) ---
# Unauthenticated GitHub API calls share a 60/hour quota on this egress IP
# and can return HTTP 403 when it is exhausted. A failed fetch must never
# silently produce a null-filled summary: on failure the error body is kept
# and no summary is written (analyze.py then records the fetch as unavailable).
HTTP_CODE="$(curl -s -m 30 -o "$OUT/.pr53-api.tmp" -w "%{http_code}" \
  "https://api.github.com/repos/postfiatorg/postfiatd/pulls/53")"
if [ "$HTTP_CODE" = "200" ] && python3 -c "import json; json.load(open('$OUT/.pr53-api.tmp'))['number']" 2>/dev/null; then
python3 - "$OUT/.pr53-api.tmp" "$OUT/pr53-summary.json" <<'PYEOF'
import json, sys
from datetime import datetime, timezone
raw = json.load(open(sys.argv[1]))
summary = {
    "repo": "postfiatorg/postfiatd",
    "number": raw.get("number"),
    "title": raw.get("title"),
    "state": raw.get("state"),
    "merged": raw.get("merged"),
    "mergeable": raw.get("mergeable"),
    "mergeable_state": raw.get("mergeable_state"),
    "draft": raw.get("draft"),
    "head_ref": (raw.get("head") or {}).get("ref"),
    "base_ref": (raw.get("base") or {}).get("ref"),
    "created_at": raw.get("created_at"),
    "updated_at": raw.get("updated_at"),
    "closed_at": raw.get("closed_at"),
    "merged_at": raw.get("merged_at"),
    "additions": raw.get("additions"),
    "deletions": raw.get("deletions"),
    "changed_files": raw.get("changed_files"),
    "commits": raw.get("commits"),
    "html_url": raw.get("html_url"),
    "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "note": "User object stripped: no account ids, handles, or display names are retained in this pack.",
}
json.dump(summary, open(sys.argv[2], "w"), indent=1)
print("pr53 state=%s merged=%s mergeable_state=%s updated=%s" % (
    summary["state"], summary["merged"], summary["mergeable_state"], summary["updated_at"]))
PYEOF
log "pr53-summary.json sha256=$(sha "$OUT/pr53-summary.json")"
else
  cp "$OUT/.pr53-api.tmp" "$OUT/pr53-fetch-error.json"
  log "pr53 fetch FAILED (HTTP $HTTP_CODE); error body kept in pr53-fetch-error.json; no summary written"
fi
rm -f "$OUT/.pr53-api.tmp"

# --- Whitepaper plain text (derived, for keyword search; HTML is the source) ---
python3 - "$OUT/postfiat-whitepaper.html" "$OUT/whitepaper.txt" <<'PYEOF'
import re, html, sys
s = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
s = re.sub(r"<script.*?</script>", "", s, flags=re.S | re.I)
s = re.sub(r"<style.*?</style>", "", s, flags=re.S | re.I)
s = re.sub(r"<[^>]+>", " ", s)
s = html.unescape(s)
s = re.sub(r"\s+", " ", s)
open(sys.argv[2], "w").write(s)
print("whitepaper.txt chars=%d" % len(s))
PYEOF
log "whitepaper.txt sha256=$(sha "$OUT/whitepaper.txt")"
log "probe_all.sh run end: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
