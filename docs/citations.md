# Citations — pinned primary sources

Every measured claim in this pack links to an unedited output in `outputs/`
or a derived file in `outputs/derived/` (recomputed from those outputs by
`scripts/analyze.py`). Every specification-derived claim cites one of the
pinned sources below. No source was accessed with a credential, session, or
account. All live fetches are from the probe window 2026-11-22: first probe
14:09–14:21 UTC, canonical re-probe 15:42–15:43 UTC, cadence re-run
15:44–15:54 UTC, unless stated otherwise.

Two systems are kept apart throughout this pack:

- **Measured (live testnet)** — the running postfiatd testnet, network ID
  2025, an XRP Ledger fork. This is what the probes measured.
- **Specified (l1v2 design)** — the postfiatl1v2 repository, a different,
  future protocol (Consensus v2, Cobalt ratification as protocol state).
  Its documents are design and recorded rehearsal, not live testnet behavior.

## Live public endpoints (measured)

| # | Source | What it establishes | Fetched (UTC) | Output |
| --- | --- | --- | --- | --- |
| L1 | `POST https://rpc.testnet.postfiat.org/` (`server_info`) | postfiatd 1.0.9, network_id 2025, 21 peers, validation_quorum 17, validated seq 8,273,715, complete ledgers 8,200,054–8,273,715, server_state full | 15:42 | `outputs/rpc-server_info.json` |
| L2 | `POST https://rpc.testnet.postfiat.org/` (`ledger`, `ledger_closed`, `ledger_data`, `fee`, `account_info`) | Ledger headers and close times; total_coins 99,999,999,966.55821 PFT; fee base 10 drops, median 5000, queue 0/2000; PostFiat genesis account holds 96,999,999,999.99988 PFT; XRPL genesis and root accounts not found | 15:42 | `outputs/rpc-ledger.json`, `rpc-ledger_closed.json`, `rpc-ledger_data.json`, `rpc-fee.json`, `rpc-account_info-pftl-genesis.json`, `rpc-account_info-xrpl-genesis.json`, `rpc-account_info-xrpl-root.json` |
| L3 | `POST https://rpc.testnet.postfiat.org/` (`validators`, `peers`) | Admin methods blocked at the public proxy: HTTP 403 `Forbidden` | 15:42 | `outputs/rpc-validators.json`, `rpc-peers.json` (+ `.http`) |
| L4 | `POST https://rpc.testnet.postfiat.org/` (`no_such_method`) | Unknown method returns HTTP 200 with `unknownCmd` (error_code 32) | 15:42 | `outputs/rpc-invalid-method.json` |
| L5 | `POST https://rpc.testnet.postfiat.org/` (`feature`) | 101 known amendments, 64 enabled, 37 not enabled; `fixAmendmentMajorityCalc` enabled; `PF_ValidatorVoteTracking` and `PF_AccountExclusion` not enabled | 15:42 | `outputs/rpc-feature.json` |
| L6 | `POST https://rpc.testnet.postfiat.org/` (`server_state`) | Last close: 24 proposers, converge 2001 ms; reserve_base 10,000,000 drops, reserve_inc 2,000,000 drops | 15:42 | `outputs/rpc-server_state.json` |
| L7 | `wss://rpc.testnet.postfiat.org:443` (upgrade probe) | WebSocket upgrade answered HTTP 401 `Invalid protocol.` (Caddy / postfiatd-1.0.9) | 15:42 | `outputs/ws-upgrade-probe.txt` |
| L8 | `wss://rpc.testnet.postfiat.org:6005` (upgrade probe) | No response within 15 s (timeout) | 15:42 | `outputs/ws-upgrade-probe.txt` |
| L9 | `https://vhs.testnet.postfiat.org/v1/network/validators` | 66 validators, 25 UNL, agreement scores, domains, versions | 15:42 | `outputs/vhs-validators.json` |
| L10 | `https://vhs.testnet.postfiat.org/v1/network/topology/nodes` | 72 topology nodes, geo, versions, inbound/outbound counts | 15:42 | `outputs/vhs-topology-nodes.json` |
| L11 | `https://vhs.testnet.postfiat.org/v1/network/topology` | `node_count: 72`, `link_count: 0` (inconsistent with L10 per-node sums 690/708) | 15:42 | `outputs/vhs-topology.json` |
| L12 | `https://vhs.testnet.postfiat.org/v1/network/networks` | 3 networks recorded (test + 2 webhook.site entries) | 15:42 | `outputs/vhs-networks.json` |
| L13 | `https://vhs.testnet.postfiat.org/v1/health`, `/v1/validators` | Health `{"count":"8"}`; `/v1/validators` returns the API index | 15:42 | `outputs/vhs-health.json`, `outputs/vhs-validators-index.json` |
| L14 | `https://vhs.testnet.postfiat.org/v1/network/amendments/info`, `/vote/test` | 103 known amendments; 64 enabled, all at ledger 86785, 2026-02-09T14:31:12Z; names identical to the RPC `feature` set | 15:42 | `outputs/vhs-amendments-info.json`, `outputs/vhs-amendments-vote-test.json` |
| L15 | `https://explorer.testnet.postfiat.org/api/v1/metrics` | base_fee 0.00001, txn_sec 0.09, txn_ledger 0.26, ledger_interval 3.022, avg_fee 0.00001000 | 15:42 | `outputs/explorer-metrics.json` |
| L16 | `https://explorer.testnet.postfiat.org/api/v1/health` | HTTP 500 `{"message":"rippled unreachable"}` while metrics works | 15:42 | `outputs/explorer-health.json` |
| L17 | Cadence run: `server_info` polled every 30 s x 21 samples | 198 ledgers in 600 s of sampling; mean close interval 3.030 s | 15:44–15:54 | `outputs/cadence-run1.jsonl`, `outputs/cadence-run1.log` |
| L18 | `https://api.github.com/repos/postfiatorg/postfiatd/pulls/53` | PR #53 open, unmerged, mergeable_state unstable, updated 2026-11-13T23:18:29Z, +439/−13, 2 files, 2 commits | 15:41 (after a 15:39 rate-limit 403; limit reset 15:41:24Z) | `outputs/pr53-summary.json` |

## Public repositories (pinned clones, shallow, 2026-11-22)

| # | Source | Commit | What it establishes |
| --- | --- | --- | --- |
| R1 | `github.com/postfiatorg/postfiatd` | `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10, PR #50 merge, release v1.0.9) | Genesis account selection by network ID (2025/2026 -> `r4vhrMChCsaoFsBoCkRTRGUuc1njfr7bmA`); INITIAL_XRP 100B; 67% quorum with the "revert to 80% for mainnet" comment; amendment thresholds 67/100 post-fix, 204/256 pre-fix, 2-week default majority time; PF amendments in `features.macro`; mainnet/testnet configs differing only in network_id, seeds, amendment majority time; shipped `validators.txt` is a keyless template |
| R2 | `github.com/postfiatorg/validator-history-service` | `d301c4ce78e109f1771d4429e17876a97e2654f3` (2026-09-17) | VHS config defaults (amendment majority time 14 days, threshold 0.8); UNL fetched from the admin `validators` RPC; amendments info/vote routes |
| R3 | `github.com/postfiatorg/postfiatl1v2` | `071b6dc461efc7a9105b2d3cac6acd3686901e7d` (2026-11-22) | l1v2 design only: no external audit; release gates 4 DONE / 16 OPEN / 1 UNKNOWN (2026-09-01); gate 8 migration/rollback/canary OPEN; gate 20 topology/independence OPEN; QA defects 142 (27 P1, 77 P2, 38 P3); genesis external lanes (ERC-20 PFT on Base, one-for-one into native PFT at mainnet genesis); Base Sepolia rehearsal only, nothing on Base mainnet; launch gates L1–L6; launch-topology thresholds are a proposal awaiting operator confirmation; only running network is the controlled devnet `postfiat-wan-devnet-2` (6 Foundation validators, not audited) |
| R4 | `github.com/postfiatorg/explorer` | `74161a20f200b6ad093e9d6d884fc4c370acb93c` (2026-10-09) | Explorer server routes (`/api/v1/metrics`, `/api/v1/health`); rippled WS connection model behind the health failure in L16 |

## Published pages

| # | Source | Fetched (UTC) | What it establishes |
| --- | --- | --- | --- |
| P1 | `https://postfiat.org/` | 15:42 | "53 validators, 3,000+ community members"; validator snapshot dated Sep 21, 2026: 53 validators, 39 verified domains, 52 at 24h agreement 99.9%+, 6.5M ledger index — stale against live values (66 / 55 / 63 / 8.27M) |
| P2 | `https://postfiat.org/whitepaper/` (Sept 2026) | 15:42 | ML-DSA-65 from genesis; quorum q=24 of 35 validators (design target); "one organization administers the current validator fleet"; "independently operated validators" still a proposal; "Neither word means independently audited"; zero occurrences of "testnet", "conversion", "1:1", "carryover" — the whitepaper publishes no testnet-to-mainnet migration mechanism |
| P3 | `https://docs.postfiat.org` | 15:42 | Notion-hosted docs site exists and is reachable (23,385 B; JS-required stub) |

## Statements not independently re-fetchable in this session

| # | Source | Status |
| --- | --- | --- |
| S1 | Founder (goodalexander), #validator-ops, 2026-09-18: mainnet ordering undecided, leaning toward "the painful option", likely option 2 (mainnet on postfiatl1v2 with inherited validator governance after a multi-million-dollar audit) vs option 1 (faster XRP fork + NAVCoin infra, postfiatl1v2 later) | Recorded from the task brief's pinned facts; the statement lives in a community chat channel that is not fetchable from public web sources in this session, and a web search for the statement returned no public mirror. The "painful option = option 2" link is an inference, never explicitly stated by the founder — marked as such in the claim index. No mainnet/TGE date exists in any source consulted. |

## What was NOT used

- No signed-in session, account, wallet, credential, or private surface was
  used for any observation.
- The live testnet runs `postfiatd` (a rippled fork). The `postfiatl1v2`
  repository (R3) describes a *different, future* protocol. This pack keeps
  the two apart: live measurements are labeled **measured (live testnet)**;
  R3 claims are labeled **specified (l1v2 design)**.
- The stdlib WebSocket client (`src/ws_probe.py`) could not complete TLS
  through this environment's egress proxy — it fails identically on the XRPL
  public-testnet control, so the failure is environmental, not
  endpoint-specific. The curl upgrade probe (L7/L8) is the authoritative
  WebSocket result. The stdlib client's unedited error records are shipped
  as `outputs/ws-ledger-443.json`, `ws-ledger-6005.json`, `ws-control-xrpl.json`.
- GitHub API rate limit: the unauthenticated quota (60/hour, shared egress
  IP) was exhausted at 15:39Z during the probe run; it reset at 15:41:24Z
  and the PR #53 summary was fetched successfully after the reset (L18).
- Fetched pages (`outputs/postfiat-org.html`, `outputs/postfiat-whitepaper.html`)
  are stored byte-for-byte as retrieved; they are third-party pages and
  contain that site's own navigation links. They are evidence for the
  homepage-snapshot and whitepaper claims, not links published by this pack:
  no pack-authored document links to any chat, community, or announcement
  channel.
