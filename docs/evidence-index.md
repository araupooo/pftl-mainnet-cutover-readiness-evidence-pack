# Evidence index

Every finding traces to an unedited output or a derived file recomputed
from one. "Shipped" means the file in this pack; hashes are in
`SHA256SUMS`.

## Measured claims

| Claim | Value | Evidence |
| --- | --- | --- |
| Testnet build / network | postfiatd 1.0.9, network_id 2025, state full | `outputs/rpc-server_info.json` |
| Validated ledger at probe | seq 8,273,715, hash in file | `outputs/rpc-server_info.json` |
| Complete ledgers | 8,200,054–8,273,715 | `outputs/rpc-server_info.json` |
| Peers / quorum | 21 peers, validation_quorum 17 | `outputs/rpc-server_info.json` |
| Last close | 24 proposers, converge 2001 ms | `outputs/rpc-server_state.json` |
| Ledger close time | 2026-11-22 14:10:10 UTC (ledger 8,271,883, first probe) | `outputs/rpc-ledger.json` |
| Total coins | 99,999,999,966.55821 PFT | `outputs/rpc-ledger.json`, `outputs/derived/live-testnet-snapshot.json` |
| Fee levels | base 10 drops, median 5000, queue 0/2000 | `outputs/rpc-fee.json` |
| Reserves | base 10,000,000 drops, increment 2,000,000 drops | `outputs/rpc-server_state.json` |
| Genesis account balance | 96,999,999,999.99988 PFT, seq 13 | `outputs/rpc-account_info-pftl-genesis.json` |
| XRPL genesis account | not found (`actNotFound`, error 19) | `outputs/rpc-account_info-xrpl-genesis.json` |
| XRPL root account | not found (`actNotFound`, error 19) | `outputs/rpc-account_info-xrpl-root.json` |
| Supply reconciliation closes | 100B = 96,999,999,999.99988 + 2,999,999,966.55832 + 33.4418 burned | `outputs/derived/live-testnet-snapshot.json` |
| Amendments known/enabled | 101 known, 64 enabled, 37 not enabled | `outputs/rpc-feature.json`, `outputs/derived/amendments.json` |
| RPC/VHS amendment agreement | identical 64-name set | `outputs/rpc-feature.json`, `outputs/vhs-amendments-vote-test.json` |
| Bulk enablement point | ledger 86785, 2026-02-09T14:31:12Z, all 64 | `outputs/vhs-amendments-vote-test.json` |
| PF amendments disabled | PF_ValidatorVoteTracking, PF_AccountExclusion | `outputs/rpc-feature.json` |
| Cadence | 198 ledgers / 600 s, mean close 3.030 s, peers constant 21 | `outputs/cadence-run1.jsonl`, `outputs/derived/cadence.json` |
| Validators / UNL | 66 validators, 25 UNL | `outputs/vhs-validators.json`, `outputs/derived/validators.json` |
| UNL versions / domains | all 25 on 1.0.9, all 25 domains verified | `outputs/vhs-validators.json` |
| Stale UNL member | paymuslam.top, 24h agreement 0.00000, index 8,179,976 | `outputs/vhs-validators.json`, `outputs/derived/validators.json` |
| Old builds (non-UNL) | 12 of 66 on 1.0.4/1.0.8/1.0.0 | `outputs/vhs-validators.json` |
| Topology | 72 nodes; link_count 0 vs inbound 690 / outbound 708 | `outputs/vhs-topology.json`, `outputs/vhs-topology-nodes.json` |
| Explorer metrics | base_fee 0.00001, txn_sec 0.09, ledger_interval 3.022 | `outputs/explorer-metrics.json` |
| Explorer health | HTTP 500 `{"message":"rippled unreachable"}` | `outputs/explorer-health.json` |
| Admin methods blocked | `validators`, `peers` → HTTP 403 `Forbidden` | `outputs/rpc-validators.json`, `outputs/rpc-peers.json` |
| Unknown method | HTTP 200, `unknownCmd`, error_code 32 | `outputs/rpc-invalid-method.json` |
| WS upgrade :443 | HTTP 401 `Invalid protocol.` | `outputs/ws-upgrade-probe.txt` |
| WS upgrade :6005 | no response within 15 s | `outputs/ws-upgrade-probe.txt` |
| Homepage snapshot | Sep 21, 2026: 53 / 39 / 52 / 6.5M vs live 66 / 55 / 63 / 8.27M | `outputs/postfiat-org.html`, `outputs/derived/homepage-vs-live.json` |
| PR #53 | open, unmerged, mergeable_state unstable, updated 2026-11-13T23:18:29Z | `outputs/pr53-summary.json` |

## Specification-derived claims

| Claim | Evidence |
| --- | --- |
| Genesis account for networks 2025/2026 is `r4vhrMChCsaoFsBoCkRTRGUuc1njfr7bmA` | `fixtures/source-excerpts/Ledger-genesis.txt` (postfiatd `Ledger.cpp:183-197` @ `0085a1ff`) |
| Genesis supply 100,000,000,000 PFT | `fixtures/source-excerpts/SystemParameters.h.txt` (`INITIAL_XRP`, line 43) |
| Amendment threshold 67/100 post-fix, 204/256 pre-fix; majority time 2 weeks default | `fixtures/source-excerpts/SystemParameters.h.txt`, `fixtures/source-excerpts/AmendmentTable-threshold.txt` |
| Quorum 67% with "revert to 80% for mainnet" | `fixtures/source-excerpts/ValidatorList-quorum.txt` |
| PF amendments exist in code, DefaultNo voting | `fixtures/source-excerpts/features-macro-pf-amendments.txt` |
| Mainnet config: network_id 2026, seed `rpc.mainnet.postfiat.org` only; testnet: 2025, 3-day majority time, 5 seed IPs | `configs/postfiatd-mainnet-full.cfg`, `configs/postfiatd-testnet-full.cfg`, `configs/config-diff-mainnet-vs-testnet.txt` |
| Shipped `validators.txt` is a keyless template; no validator_list_sites configured | `configs/validators-testnet.txt` |
| VHS defaults: majority time 14 days, threshold 0.8 | `fixtures/source-excerpts/vhs-config-defaults.txt` |
| No external audit; gates 4 DONE / 16 OPEN / 1 UNKNOWN (2026-09-01); gate 8 and gate 20 OPEN | `fixtures/source-excerpts/l1v2-security-index.txt` |
| Only running l1v2 network is devnet `postfiat-wan-devnet-2`, 6 Foundation validators, not audited | `fixtures/source-excerpts/l1v2-network-status.txt` |
| ERC-20 PFT on Base: one-for-one into native PFT at mainnet genesis; nothing on Base mainnet; Base Sepolia test deployments only; slice size open | `fixtures/source-excerpts/l1v2-pft-token-on-base.txt` |
| Whitepaper: ML-DSA-65 from genesis; q=24 of 35 (design); one org administers the fleet; no testnet/conversion text | `outputs/postfiat-whitepaper.html`, `outputs/whitepaper.txt` |

## Unresolved claims

See `docs/claim-index.md`. The four claims the pack was asked to trace
that remain explicitly unresolved are: 1:1 testnet-to-mainnet conversion,
rollback against a real cutover, mainnet/TGE date, and audit scope/cost.
A fifth — amendment vote-replay order-independence (PR #53) — is also
unresolved pending merge.
