# Validator onboarding, UNL-transition, and rollback runbook

**Status: VALIDATED AGAINST LIVE TESTNET DATA WHERE STATED; UNVALIDATED
WHERE MARKED.** This runbook is a procedure derived from the live testnet
and the shipped configs. The rollback section has never been executed
against a real cutover — there has never been one — and is marked as such.
Do not treat this runbook as proof that a cutover works.

Conventions: all commands are read-only unless marked otherwise. Nothing
here spends funds, signs, or touches mainnet. `network_id 2025` is the
live testnet; `2026` is the mainnet value in the shipped config.

## 0. Preconditions (check before anything else)

| # | Check | How (live) | Expected | Observed 2026-11-22 |
| --- | --- | --- | --- | --- |
| 0.1 | RPC reachable, correct network | `POST rpc.testnet.postfiat.org/ server_info` | `network_id` 2025, `build_version` 1.0.9, `server_state` full | PASS — 2025, 1.0.9, full, 21 peers |
| 0.2 | Ledger advancing | `server_info` twice, 30 s apart | seq increases ~10 per 30 s | PASS — 198 ledgers / 600 s, mean close 3.030 s |
| 0.3 | UNL complete | VHS `/v1/network/validators` | 25 UNL, all on latest build | PARTIAL — 25 UNL on 1.0.9, but 1 stale (see 0.4) |
| 0.4 | No stale UNL member | UNL 24h agreement > 0.999 for every member | 25/25 | **FAIL — 1 of 25 at 0.00000** (paymuslam.top, index 8,179,976 vs network 8,273,715 at probe time (~93,700 ledgers behind)) |
| 0.5 | Amendment state sane | RPC `feature` vs VHS vote endpoint | identical 64-name enabled set | PASS — exact match |
| 0.6 | Explorer healthy | `/api/v1/health` | HTTP 200 | **FAIL — HTTP 500 `rippled unreachable`** |
| 0.7 | Quorum matches the 67% formula | `validation_quorum` = max(ceil(0.67×UNL), ceil(0.60×UNL)) | 17 for UNL 25 | PASS — 17 |

**Gate:** do not start onboarding or transition work while 0.4 or 0.6
fails. Both are cutover preconditions in `docs/audit-gates.md`.

## 1. Validator onboarding (testnet, validated)

Onboarding a validator to the **live testnet** is observable end to end;
onboarding to **mainnet** has no published procedure (claim C13,
unresolved). This section documents the testnet path only.

1. **Generate keys.** A validator needs a validation key pair and a
   manifest. Key generation is local to the operator; this pack does not
   generate keys and does not document key handling beyond pointing at
   the operator's own tooling — no key material appears anywhere here.
2. **Configure the node.** Start from `configs/postfiatd-testnet-full.cfg`
   (network_id 2025, `[amendment_majority_time] 3 days`). Set
   `[validators_file]` to a `validators.txt` that lists the trusted
   validator keys. Note: the shipped `configs/validators-testnet.txt`
   is a template with **no keys** — the operator must supply the live
   UNL. There is no validator-list site configured in the repo.
3. **Peer.** Seed from `[ips]`: `rpc.testnet.postfiat.org 2559` plus the
   five seed IPs in the testnet config.
4. **Sync.** Wait for `server_info` to report `server_state: full` and
   `complete_ledgers` covering the validated range. The RPC node's own
   `initial_sync_duration_us` was 144,067,489 (~144 s) at probe time —
   a fresh node should budget at least that, plus ledger acquisition.
5. **Verify.** The node appears in VHS topology
   (`/v1/network/topology/nodes`) with `server_state: full` and a current
   `complete_ledgers` range, and — once validating — in
   `/v1/network/validators` with an agreement score. A validator that
   never appears with a 24h agreement above 0 is not validating; see
   the stale-member case in 0.4.
6. **Join the UNL.** There is no self-service step: UNL membership is
   operator-granted (one organization administers the fleet). A new
   validator is trusted only when the fleet's `validators.txt` / list
   includes its key. Until then it is a non-UNL observer: it validates
   nothing and counts toward nothing.

**Validation performed:** steps 4–5 were verified live for the fleet as
a whole (72 topology nodes, 66 validators, 25 UNL). Steps 1–3 and 6 are
procedures read from the shipped config and VHS docs; no new validator
was onboarded during this assessment.

## 2. UNL transition (testnet → mainnet, NOT validated)

No UNL-transition procedure is published for mainnet (claim C14,
unresolved). What the sources do establish, and what a transition plan
must therefore contain:

1. **Freeze the mainnet UNL first.** The mainnet config ships with no
   UNL. The UNL must be chosen, published, and frozen before genesis —
   it cannot be derived from the testnet UNL, because the testnet UNL
   contains a stale member (0.4) and is administered centrally.
2. **Decide the quorum constant before genesis.** Mainnet needs the 80%
   quorum the code calls for (claim C15). The constant lives in
   `ValidatorList::calculateQuorum`; changing it after genesis changes
   fork-safety assumptions for every node at once. It must be changed,
   tested, and measured **before** the mainnet UNL is frozen.
3. **Amendment majority time.** Mainnet config carries no override, so
   the 2-week default applies (testnet: 3 days). Any amendment the
   cutover depends on needs 2 weeks of majority hold after genesis —
   plan the schedule around that, or publish an override deliberately.
4. **Publish the list.** The mainnet `validators.txt` (or a
   validator-list site, which neither config currently sets) must be
   published with the keys, and every mainnet node must point at the
   same list. Two nodes with different UNLs and a 67% quorum tolerate
   under one-third unique validators between them (see the Theorem 8
   analysis in `ValidatorList.cpp`); at 80% the tolerance is tighter.
   Divergent UNLs are a fork risk, not a config detail.
5. **Measure agreement before declaring readiness.** Every UNL member
   must show 24h agreement ≥ 0.999 for a full window before the
   cutover, the way the live testnet's 24 of 25 members do today.

**Validation performed:** none of steps 1–5 has been executed for
mainnet, because there is no mainnet. Steps 2–4 are derived from pinned
source; step 5 is the live testnet's own standard, applied as the bar.

## 3. Rollback (NOT validated — no cutover has ever occurred)

**Read this section as a plan to rehearse, not a procedure that works.**
l1v2 release gate 8 (migration, rollback, canary) is OPEN. No rollback
has been exercised on either codebase in a cutover context.

### 3.1 What rollback means here — and what it cannot mean

- postfiatd has **no in-protocol rollback**. A ledger that has validated
  cannot be un-validated. A bad mainnet genesis cannot be "rolled back":
  it can only be **abandoned** and replaced by a new genesis, which
  destroys all mainnet state created after the abandoned genesis.
- The only meaningful rollback is therefore **pre-genesis**: halt before
  genesis is published, fix the cause, re-genesis. After genesis is
  published and the network is live, "rollback" is really "abandon and
  restart", with total loss of post-genesis state.
- The l1v2 design has the same shape: its launch gates (L1–L6) are
  pre-launch checks, and its release process step 4 (migration,
  rollback, canary) is an open gate, not a tested drill.

### 3.2 Stop conditions (decide these before any cutover window)

Abort the cutover — i.e. do not publish genesis — if any of these holds
at the go/no-go check:

| # | Condition | Check |
| --- | --- | --- |
| S1 | Any frozen-UNL member below 0.999 24h agreement | VHS validators list |
| S2 | Quorum constant still 67% in the mainnet build | `ValidatorList.cpp` + live `server_info` on a staging node |
| S3 | PR #53 (or its equivalent) unmerged | GitHub API |
| S4 | Any release gate in the cutover scope still OPEN | Gate inventory |
| S5 | Explorer health failing on the staging network | `/api/v1/health` |
| S6 | No signed launch decision (l1v2 L6) | Gate registry |

### 3.3 Rollback drill (to be rehearsed on staging, not yet done)

1. Stand up a staging network from the mainnet config (network_id 2026
   on an isolated network — **not** the public testnet, **not** mainnet).
2. Publish a staging genesis with the frozen UNL.
3. Inject a fault (for example: a UNL member taken offline, a bad
   amendment vote, a config error) and confirm the stop condition fires.
4. Abandon the staging genesis, fix the fault, re-genesis, and confirm
   the network reaches full state with the corrected UNL.
5. Record the drill: genesis hash, UNL, fault, stop condition, time to
   re-genesis. A drill without a record did not happen.

Until a drill like this is recorded, every rollback claim in this pack
stays unresolved (claim C16).

## 4. Monitoring during a cutover window (when one exists)

Poll, do not subscribe: the public WebSocket ledger stream is not
subscribable (HTTP 401 on :443, timeout on :6005). The monitoring loop
that works today, verified live:

- `server_info` every 30 s: `validated_ledger.seq` must advance ~10 per
  sample; `server_state` must stay `full`; `peers` must stay ≥ 15.
- VHS validators every 5 min: every UNL member's 24h agreement ≥ 0.999;
  no member's `current_index` more than ~100 ledgers behind the network.
- `fee` every 5 min: queue size 0; base fee 10 drops.
- Explorer `/api/v1/metrics` every 5 min: `ledger_interval` ~3.0;
  `/api/v1/health` must return HTTP 200 (it does not today — fix first).
- `feature` once per window: enabled-amendment set must equal the VHS
  vote set exactly (64 names today).
