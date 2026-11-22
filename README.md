# PFTL Mainnet Cutover Readiness — Evidence Pack

**Verdict: NOT READY for mainnet cutover.** 2 CRITICAL + 4 HIGH findings,
13 of 26 claims explicitly unresolved, 0 of 15 audit gates closed. The
live testnet itself is healthy — the cutover is not ready.

## Headline numbers (measured 2026-11-22, live testnet, network 2025)

| Measurement | Value |
| --- | --- |
| Build / network / state | postfiatd 1.0.9, network_id 2025, `full`, 21 peers |
| Validated ledger | seq 8,273,715 (probe), complete 8,200,054–8,273,715 |
| Ledger cadence | 198 ledgers / 600 s, mean close interval 3.030 s |
| Validation quorum | 17 of UNL 25 (67% formula; code says revert to 80% for mainnet) |
| Validators / UNL | 66 validators, 25 UNL (all 1.0.9, all domains verified) |
| Stale UNL member | 1 of 25 at 0.00000 24h agreement (~3 days behind) |
| Genesis supply reconciliation | 100B PFT = 96,999,999,999.99988 (genesis) + 2,999,999,966.55832 (other accounts) + 33.4418 burned — closes exactly |
| Amendments | 101 known, 64 enabled (RPC `feature` == VHS vote endpoint, exact name match); all 64 enabled at ledger 86785, 2026-02-09 |
| PostFiat-native amendments | `PF_ValidatorVoteTracking` and `PF_AccountExclusion` NOT enabled |
| Fees | base 10 drops, median 5000, queue 0/2000 |
| Amendment vote-replay test | PR #53 open, unmerged, `mergeable_state: unstable` |
| External audit | none recorded for either codebase |
| 1:1 conversion | no mechanism for the live testnet; the only documented path (ERC-20 PFT on Base) is an l1v2 design, nothing on Base mainnet |
| Mainnet date | none published anywhere |

## What this pack is

An assessment of PFTL testnet-to-mainnet readiness, built from live
probes of the running testnet and pinned primary sources. It performs no
cutover, touches no mainnet, spends no funds, and signs nothing.

Two systems are kept apart throughout: the **live testnet** (postfiatd,
an XRP Ledger fork, network 2025 — measured) and the **l1v2 design**
(postfiatl1v2, Consensus v2 — specified, not observed live). Conflating
them is the most common error in readiness claims.

## Contents

- `docs/decision-memo.md` — the verdict, what is true, what blocks the
  cutover, and what would change the verdict.
- `docs/claim-index.md` — 26 claims with status: 8 verified, 4
  specified, 1 open, 13 explicitly unresolved.
- `docs/runbook.md` — validator onboarding, UNL-transition, and rollback
  runbook, validated against live testnet data where stated, marked
  unvalidated where it is not.
- `docs/audit-gates.md` — 15 severity-scored audit gates; 0 closed.
- `docs/citations.md` — every pinned primary source (live endpoints and
  repo commits).
- `docs/methodology.md` — how each number was produced, and limitations.
- `docs/evidence-index.md` — every claim traced to an unedited output.
- `docs/index.html` — results page (GitHub Pages: serve `docs/`).
- `findings.json` — 12 findings by severity (2 CRITICAL, 4 HIGH,
  3 MEDIUM, 2 LOW, 1 INFO).
- `run-manifest.json` — probe window, environment, repo pins, verdict.
- `configs/` — shipped mainnet + testnet configs and the config diff
  (mainnet differs from testnet only in network_id, seeds, and the
  amendment-majority override) plus the keyless `validators.txt` template.
- `fixtures/` — pinned source excerpts with verified line numbers and
  full SHA-256 of every cited source file (`source-hashes.json`).
- `outputs/` — unedited probe outputs (RPC, VHS, explorer, pages,
  cadence, WebSocket probe, PR #53 summary) and derived numbers
  (`outputs/derived/`).
- `scripts/` — the probe, cadence, analysis, comparison, and digest
  scripts. `src/ws_probe.py` is the stdlib WebSocket client.

## Reproduce

```bash
bash scripts/run_all.sh          # fresh probes + 21-sample cadence + analysis
bash scripts/verify_digests.sh   # SHA256SUMS check (must pass)
bash scripts/clean_reproduce.sh  # fresh-environment run in a temp dir;
                                 # exits 0 only if all comparison checks pass
```

`clean_reproduce.sh` prints its workdir (e.g.
`/tmp/pftl-cutover-repro.XXXXXXXX`) and copies the fresh probe set into
`outputs/fresh-clone-*` with `outputs/fresh-clone-compare.log`. The
fresh-clone files are intentionally excluded from `SHA256SUMS` (they are
generated after the digest is made) and are verified by the comparison
log instead.

## Requirements

`curl`, `git`, `python3` (standard library only). No credentials, no
accounts, no signing. All endpoints are public.
