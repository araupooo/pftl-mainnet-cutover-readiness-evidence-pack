# Claim-to-evidence index

Status meanings: **VERIFIED** — measured against live data or pinned
source in this pack. **SPECIFIED** — stated in a design document for the
l1v2 protocol, not observed on the live testnet. **UNRESOLVED** — no
primary source in this pack supports the claim; it must not be stated as
fact. **OPEN** — a real gap with a known fix, not yet done.

## Ledger-state carryover and genesis

| # | Claim | Status | Evidence |
| --- | --- | --- | --- |
| C01 | The live testnet is a postfiatd ledger, network ID 2025, build 1.0.9 | VERIFIED | L1, `outputs/rpc-server_info.json` |
| C02 | Genesis supply is 100,000,000,000 PFT | VERIFIED (source) + VERIFIED (live reconciliation) | R1 `SystemParameters.h:43`; `outputs/derived/live-testnet-snapshot.json` — supply closes exactly |
| C03 | The PostFiat genesis account is `r4vhrMChCsaoFsBoCkRTRGUuc1njfr7bmA` and holds 96,999,999,999.99988 PFT | VERIFIED | R1 `Ledger.cpp:183-197`; `outputs/rpc-account_info-pftl-genesis.json` |
| C04 | The XRPL genesis and root accounts do not exist on this network | VERIFIED | `outputs/rpc-account_info-xrpl-genesis.json`, `outputs/rpc-account_info-xrpl-root.json` (both `actNotFound`) |
| C05 | Fees burn: 33.4418 PFT burned to date; ~3B PFT sits in non-genesis accounts | VERIFIED | `outputs/derived/live-testnet-snapshot.json` |
| C06 | Testnet balances carry over 1:1 to mainnet | **UNRESOLVED** | No mechanism is published for the live testnet. The whitepaper has zero hits for "testnet", "conversion", "1:1", "carryover". postfiatd genesis is a fresh ledger (`Ledger::Ledger(create_genesis_t)`), not a state import. |
| C07 | ERC-20 PFT on Base converts one-for-one into native PFT at PFTL mainnet genesis | SPECIFIED (l1v2 design only) | R3 `docs/architecture/pft-token-on-base.md`: "PFT is to list first as an ERC-20 on Base, with a one-for-one path into native PFT at PFTL's mainnet genesis". Nothing is deployed on Base mainnet; the slice size is open; rehearsal is Base Sepolia + local fleet only. This is a design for the l1v2 protocol, not a mechanism for the live postfiatd testnet. |
| C08 | Mainnet genesis reuses the testnet ledger state | **UNRESOLVED** | Contradicted in direction by C06's sources: both codebases describe a fresh genesis (postfiatd `create_genesis_t`; l1v2 genesis registry + launch spec). No state-import procedure exists in either repo. |
| C09 | Mainnet network ID will be 2026 | SPECIFIED | R1: mainnet config ships `[network_id] 2026`; genesis code treats 2025/2026 identically. A config value is not a launch. |

## Validator onboarding, UNL transition, rollback

| # | Claim | Status | Evidence |
| --- | --- | --- | --- |
| C10 | Live UNL has 25 members, all on 1.0.9, all domains verified | VERIFIED | `outputs/vhs-validators.json` |
| C11 | One UNL member is stale (0.00000 24h agreement, ~3 days behind) | VERIFIED | `outputs/derived/validators.json` — paymuslam.top, index 8,179,976 vs network 8,273,715 at probe time (~93,700 ledgers behind) |
| C12 | The testnet UNL is administered by one organization | SPECIFIED | Whitepaper: "one organization administers the current validator fleet"; "independently operated validators" remains a proposal |
| C13 | A new validator can join the mainnet UNL by following a published procedure | **UNRESOLVED** | No published mainnet onboarding procedure exists. Shipped `validators.txt` is a keyless template; no validator-list site is configured; the live UNL is operator-supplied and only observable via VHS. |
| C14 | The UNL can transition from testnet to mainnet membership without a restart | **UNRESOLVED** | No transition procedure is published in either repo. The l1v2 Dynamic UNL machinery is design + rehearsal; the postfiatd UNL is a static file/list. |
| C15 | Mainnet quorum will be 80% | OPEN (code change required) | R1 `ValidatorList.cpp`: "For mainnet, this should be reverted to 80%." Testnet runs 67% (live quorum 17 = ceil(25×0.67), verified in `outputs/derived/validators.json`). The 80% quorum has never run on this network. |
| C16 | Rollback after a failed cutover is a tested procedure | **UNRESOLVED** | l1v2 gate 8 (migration, rollback, canary) is OPEN. No rollback has ever been exercised on either codebase in a cutover context. postfiatd has no in-protocol rollback: a bad mainnet genesis can only be abandoned and re-created. |
| C17 | Amendment vote outcomes are independent of validation order | **UNRESOLVED** | PR #53 (the regression test proving exactly this) is open and unmerged since 2026-11-13. `fixAmendmentMajorityCalc` is enabled, so the 67% threshold is live, but order-independence is unproven. |
| C18 | The two PostFiat-native amendments (vote tracking, account exclusion) are ready for mainnet | **UNRESOLVED** | Both exist in code (`features.macro` lines 45–46) but are NOT enabled on testnet and are not in voting. They cannot be exercised before cutover. |
| C19 | A mainnet amendment takes 2 weeks to activate after majority | SPECIFIED | R1: default majority time is 2 weeks; the mainnet config carries no override (testnet overrides it to 3 days). |

## Audit gating

| # | Claim | Status | Evidence |
| --- | --- | --- | --- |
| C20 | The code has passed an external security audit | **UNRESOLVED** | R3 `docs/security/index.md`: "No external security audit is recorded in this repository." QA defect inventory: 142 rows (27 P1). |
| C21 | A multi-million-dollar audit is scoped, with an auditor and a date | **UNRESOLVED** | Founder statement (S1) mentions a multi-million-dollar audit as an intention. No auditor, scope document, or date is published in any source consulted. |
| C22 | Release gates are closed for a public launch | **UNRESOLVED** | R3 gate inventory (2026-09-01): 4 DONE, 16 OPEN, 1 UNKNOWN. Gates 8, 12, 13, 20 are OPEN. The inventory itself says it is not a recomputed total for today's source. |
| C23 | Launch topology/independence thresholds are decided | **UNRESOLVED** | R3 `launch-topology-thresholds.md`: "Status: Proposal — awaiting the operator's thresholds" (2026-09-01). Proposed minimum: registry n_S ≥ 12, ratification quorum q_S = ceil(4n/5). |

## Dates and ordering

| # | Claim | Status | Evidence |
| --- | --- | --- | --- |
| C24 | There is an official mainnet or TGE date | **UNRESOLVED** | No date in the whitepaper, either repo, the homepage, or the founder statement. |
| C25 | Mainnet ordering is decided (postfiatl1v2 first vs XRP fork first) | **UNRESOLVED** | S1: ordering undecided as of 2026-09-18, leaning toward the "painful option", likely option 2. The "painful option = option 2" link is an inference, not a quotation. |
| C26 | The testnet is healthy and advancing normally | VERIFIED | 198 ledgers / 600 s, mean close 3.030 s; fee queue empty; amendment state agrees across RPC and VHS; all 25 UNL members on the latest release. Testnet health is not mainnet readiness. |

## Count

26 claims: 8 VERIFIED, 4 SPECIFIED, 1 OPEN, 13 UNRESOLVED. The
unresolved set is the verdict: a cutover cannot be scheduled, a 1:1
conversion cannot be promised, and a rollback cannot be relied on until
those claims move.
