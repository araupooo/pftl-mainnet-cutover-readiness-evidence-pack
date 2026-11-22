# Methodology

## Question

Is the PFTL testnet ready to cut over to mainnet, and what would the
cutover have to carry across? This pack answers from measurements of the
live testnet and pinned primary sources only. It performs no cutover,
touches no mainnet, spends no funds, and signs nothing.

## Two systems, kept apart

The name "PFTL" covers two different systems, and conflating them is the
most common error in readiness claims:

1. **The live testnet** — `postfiatd`, a fork of rippled (XRPL), network ID
   2025, public RPC at `rpc.testnet.postfiat.org`. This is what the probes
   measured. It has real validators, real ledgers (sequence ~8.27M), and a
   real genesis account.
2. **The l1v2 design** — `postfiatl1v2`, a separate Rust codebase
   (Consensus v2, Cobalt governance, ML-DSA-65, genesis external lanes).
   Its only running network is the controlled devnet
   `postfiat-wan-devnet-2` (six Foundation-administered validators). Its
   documents are design, rehearsal records, and gate inventories — not
   live testnet behavior.

Every claim in this pack is labeled **measured (live testnet)** or
**specified (l1v2 design)**. A claim that needs both (for example, "the
1:1 conversion path") is marked unresolved unless a single system supports
it end to end. None does.

## Probes

All probes are public, anonymous, and read-only:

- **JSON-RPC** (`scripts/probe_all.sh`): `server_info`, `ledger`,
  `ledger_closed`, `ledger_data`, `fee`, `account_info` (three accounts:
  the XRPL genesis account, the XRPL root account, and the PostFiat
  genesis account from pinned source), `validators`, `peers`,
  `no_such_method`, `feature`, `server_state`. Responses are stored
  unedited with their HTTP status lines (`*.http` sidecars).
- **VHS REST** (`scripts/probe_all.sh`): validators, topology nodes,
  topology summary, networks, health, API index, amendments info and vote.
- **Explorer REST**: `/api/v1/metrics`, `/api/v1/health`.
- **Pages**: `postfiat.org`, `postfiat.org/whitepaper/`,
  `docs.postfiat.org` (HTML stored unedited; `whitepaper.txt` is a
  mechanical tag-stripped copy for keyword search).
- **WebSocket**: curl upgrade probe on `:443` and `:6005`. The stdlib
  client (`src/ws_probe.py`) is retained for reproducibility but cannot
  complete TLS through this environment's egress proxy — it fails
  identically on the XRPL public-testnet control, so that failure is
  environmental and the curl probe is authoritative.
- **Cadence** (`scripts/cadence.py`): `server_info` every 30 s, 21 samples
  (10 minutes). Ledger-sequence deltas give the mean close interval.
- **GitHub API**: PR #53 status (public; the `user` object is stripped
  before the summary is written — no account IDs, handles, or display
  names are retained anywhere in the pack).

## Source pinning

Four repositories were cloned shallow (`--depth 1`) on 2026-11-22 and
pinned by commit in `fixtures/source-hashes.json` (full SHA-256 of every
cited source file). Line numbers in this pack were verified with `grep -n`
and `sed -n` against those clones — never copied from a browser fetch of
a raw file. Excerpts of the exact cited regions are shipped under
`fixtures/source-excerpts/`.

## Derivation

`scripts/analyze.py` reads only `outputs/` and `fixtures/` and writes
`outputs/derived/*.json`, `findings.json`, and `run-manifest.json`. It
prints the full SHA-256 of every input it reads. Derived numbers:

- **Supply reconciliation**: genesis supply is 100,000,000,000 PFT
  (`INITIAL_XRP`, `SystemParameters.h:43`). Burned-by-fees =
  genesis supply − `total_coins` (live ledger header). Other accounts =
  `total_coins` − genesis-account balance (live `account_info`).
  The reconciliation closes iff the three parts sum to genesis supply.
- **Quorum check**: live `validation_quorum` against
  `max(ceil(0.67 × UNL), ceil(0.60 × UNL))` from
  `ValidatorList::calculateQuorum`.
- **Amendment agreement**: the set of enabled names from RPC `feature`
  compared with the set from the VHS vote endpoint; both the count and
  the names must match.
- **Validator health**: agreement scores, versions, and staleness from
  the VHS validators list; topology sums recomputed from the per-node
  list and compared with the summary endpoint's `link_count`.
- **Homepage staleness**: the four homepage snapshot figures parsed from
  `outputs/postfiat-org.html` and compared with live values.

## Severity scoring

| Severity | Meaning |
| --- | --- |
| CRITICAL | Blocks any cutover decision outright; no workaround exists in published material |
| HIGH | Blocks a production cutover until a code change, merge, or published procedure lands |
| MEDIUM | Must be fixed or rehearsed before the cutover window; does not by itself invalidate the design |
| LOW | Should be fixed before any public readiness claim; no cutover impact |
| INFO | Verified healthy; recorded so the verdict is not one-sided |

## Limitations

- L1. All live measurements are from the probe window 2026-11-22
  (first probe 14:09–14:21 UTC, canonical re-probe 15:42–15:43 UTC) plus
  one 10-minute cadence (15:44–15:54 UTC). Ledger sequence, counts,
  and agreement scores move with time; the reproduce run re-measures
  them with tolerances instead of exact equality.
- L2. The public RPC proxy blocks admin methods (`validators`, `peers`,
  HTTP 403), so the live UNL is observable only through VHS, which
  itself reads the admin RPC. UNL membership cannot be independently
  confirmed from the public RPC.
- L3. The founder's mainnet-ordering statement (S1) could not be
  re-fetched live: it lives in a community chat channel, and no public mirror
  was found by web search. It is cited from the brief's pinned record
  and labeled as such.
- L4. The rollback runbook (`docs/runbook.md`) is validated against
  live read-only behavior and shipped configs only. No cutover — and
  therefore no real rollback — has ever been performed on either
  codebase, so the rollback section is a procedure, not an executed
  drill.
- L5. The WebSocket ledger stream could not be subscribed to from this
  environment (L7/L8 plus the proxy limitation). Ledger-close timing
  rests on the HTTP cadence instead.
- L6. The l1v2 gate inventory is dated 2026-09-01 and its own text says
  it "is not a recomputed total for today's source"; it is cited as a
  dated inventory, not as today's gate state.
- L7. GitHub's unauthenticated API quota is shared on this egress IP;
  the PR #53 fetch hit HTTP 403 at 15:39Z and succeeded after the
  15:41:24Z reset. `scripts/probe_all.sh` records such failures in
  `pr53-fetch-error.json` instead of writing null-filled summaries.
