# Audit-gating checklist — severity-scored

Each gate names its check, its evidence, and what closes it. A gate is
CLOSED only when its evidence artifact exists and is cited. "Open" gates
are the cutover blockers; the verdict in `docs/decision-memo.md` follows
directly from this table.

## CRITICAL — cutover cannot be scheduled while any is open

| # | Gate | Check | Evidence today | Closes when |
| --- | --- | --- | --- | --- |
| G01 | Mainnet date and ordering decided | A dated mainnet decision in a primary source | None. Ordering undecided since 2026-09-18 (S1); no date anywhere | A dated decision is published and pinned |
| G02 | 1:1 conversion mechanism published (or explicitly disclaimed) | A conversion procedure for the live testnet, or a published statement that balances do not carry over | Neither exists. Only the l1v2 design (ERC-20 on Base) exists, and it is not a live-testnet mechanism | The mechanism (or disclaimer) is published at a pinned commit and, if a mechanism, rehearsed end to end |

## HIGH — production cutover blocked while any is open

| # | Gate | Check | Evidence today | Closes when |
| --- | --- | --- | --- | --- |
| G03 | Amendment vote-replay proof merged | PR #53 merged with green CI | Open, unmerged, `mergeable_state: unstable`, updated 2026-11-13 (`outputs/pr53-summary.json`) | PR merged; CI run linked |
| G04 | PostFiat-native amendments live on testnet | `PF_ValidatorVoteTracking` and `PF_AccountExclusion` enabled and exercised | Both disabled, not in voting (`outputs/rpc-feature.json`) | Both enabled on testnet; voting observed in VHS |
| G05 | Quorum constant set for mainnet | 80% quorum in the mainnet build, measured live | 67% live (quorum 17 of UNL 25); code comment says revert to 80% for mainnet | 80% landed, tested, and measured on a staging network |
| G06 | External audit scoped and dated | Named auditor, scope document, engagement date | None recorded for either codebase (`docs/security/index.md`) | Audit engagement published; findings dispositioned |
| G07 | Migration / rollback / canary gate closed | l1v2 gate 8 closed with a rehearsed drill | OPEN (2026-09-01 inventory); no drill recorded | Drill recorded per `docs/runbook.md` §3.3 |
| G08 | Mainnet UNL-transition procedure published | Onboarding + transition procedure for mainnet | None; UNL centrally administered; shipped `validators.txt` is a keyless template | Procedure published; frozen mainnet UNL published with all members ≥ 0.999 24h agreement |

## MEDIUM — must close before the cutover window

| # | Gate | Check | Evidence today | Closes when |
| --- | --- | --- | --- | --- |
| G09 | Stale UNL member resolved | Every UNL member 24h agreement ≥ 0.999 | 1 of 25 at 0.00000 (paymuslam.top) | Member repaired or removed; re-measured over a full window |
| G10 | Observability gaps fixed | Explorer health 200; topology `link_count` consistent; WS stream subscribable | Health HTTP 500; link_count 0 vs 690/708 sums; WS 401/timeout | All three fixed or formally documented as known limits |
| G11 | Topology / independence thresholds decided | Launch thresholds confirmed by the operator | Proposal only, awaiting confirmation (2026-09-01) | Thresholds confirmed and published |
| G12 | Homepage figures current | Homepage snapshot within 7 days of live values | Snapshot Sep 21, 2026; live values differ on all four figures | Snapshot refreshed |
| G13 | Old builds retired from the fleet | No validator on a build older than the current release | 12 of 66 on 1.0.4/1.0.8/1.0.0 (none on UNL) | All validators on the current release, or formally exempted |

## LOW — fix before any public readiness claim

| # | Gate | Check | Evidence today | Closes when |
| --- | --- | --- | --- | --- |
| G14 | Currency code corrected | `systemCurrencyCode()` returns the network's asset code | Returns `"XRP"` while the asset is PFT | Renamed in source; release cut |
| G15 | VHS test entries removed | `/v1/network/networks` lists only real networks | 2 webhook.site test entries listed | Test entries removed |

## Count

15 gates: 2 CRITICAL (both open), 6 HIGH (all open), 5 MEDIUM (all open),
2 LOW (both open). Zero gates closed. That is the audit verdict in one
line: the cutover has no closed gate to stand on.
