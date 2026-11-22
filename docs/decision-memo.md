# Decision memo — PFTL mainnet cutover readiness

**Date:** 2026-11-22. **Basis:** live testnet probes 2026-11-22 — first probe
14:09–14:21 UTC, canonical re-probe 15:42–15:43 UTC, cadence re-run
15:44–15:54 UTC — plus pinned source (postfiatd `0085a1ff`, postfiatl1v2 `071b6dc4`, VHS
`d301c4ce`, explorer `74161a20`). **Verdict: NOT READY.**

## Recommendation

**Do not schedule a mainnet cutover.** Do not promise testnet holders a
1:1 conversion. Do not freeze a mainnet UNL. The testnet itself is healthy;
the cutover is not ready, because the cutover has no date, no conversion
mechanism, no audit, no merged amendment-regression proof, and no tested
rollback.

## What is actually true

1. **The testnet works.** postfiatd 1.0.9, network 2025, 21 peers, 25-member
   UNL, validation quorum 17. Ledgers close every ~3.030 s (198 ledgers in
   600 s). Fee queue empty. All 25 UNL members run the latest release with
   verified domains.
2. **The money math closes.** Genesis supply is 100,000,000,000 PFT.
   The genesis account holds 96,999,999,999.99988 PFT, other accounts hold
   2,999,999,966.55832 PFT, and 33.4418 PFT has burned in fees. The three
   parts sum exactly to genesis supply. The XRPL genesis and root accounts
   do not exist here — this is a fresh genesis, not XRPL state.
3. **Amendment state is consistent across two independent sources.** RPC
   `feature` and the VHS vote endpoint agree exactly: 101 known
   amendments, 64 enabled, all 64 enabled at ledger 86785 on 2026-02-09.
4. **Mainnet config already ships in-repo** and differs from testnet only
   in network ID (2026), seed peers, and the amendment-majority override.
   That is the smallest possible config delta — a genuine readiness asset.

## What blocks the cutover

1. **No date, no decision (F01).** Mainnet ordering is undecided since
   2026-09-18; the founder leans toward mainnet on postfiatl1v2 after a
   multi-million-dollar audit, but neither the audit nor the date exists
   as a scoped, dated commitment.
2. **No conversion (F02).** The only documented 1:1 path — ERC-20 PFT on
   Base into native PFT at genesis via external lanes — belongs to the
   l1v2 design, not the live testnet. Nothing is deployed on Base
   mainnet, the slice size is open, and the rehearsal ran on Base
   Sepolia plus a local fleet. For the live testnet there is no
   conversion mechanism at all. **Testnet balances must be assumed lost
   at cutover until a mechanism is published.**
3. **Amendment proof is unmerged (F03).** PR #53, the regression test
   proving amendment votes do not depend on validation order, is open
   and unmerged. The two PostFiat-native amendments (vote tracking,
   account exclusion) are not enabled and not in voting.
4. **No audit, open gates (F04).** No external audit is recorded for
   either codebase. The l1v2 gate inventory (2026-09-01) shows 16 of 21
   gates open, including migration/rollback/canary and
   topology/independence thresholds. The QA defect inventory lists 142
   rows, 27 of them P1.
5. **A code change is required before mainnet (F05).** The testnet runs a
   67% validation quorum. The code itself says: "For mainnet, this
   should be reverted to 80%." That change has never run on this network.
6. **The UNL is centrally administered (F06).** One organization runs the
   fleet; independently operated validators are still a proposal; the
   shipped `validators.txt` is a keyless template and no validator-list
   site is configured. There is no published mainnet onboarding or
   UNL-transition procedure.
7. **Rollback is untested (F08).** No cutover has ever been performed, so
   no rollback has ever been exercised. A bad mainnet genesis cannot be
   rolled back in-protocol; it can only be abandoned.

## What would change the verdict

In order, each with a checkable artifact:

1. A published mainnet date and a decided ordering, recorded in a
   primary source (not a chat message).
2. A published conversion mechanism for the live testnet — or an explicit
   statement that testnet balances do not carry over — with the mechanism
   (or the statement) pinned to a commit.
3. PR #53 merged with green CI, plus both PostFiat-native amendments
   enabled on testnet and exercised.
4. The 80% quorum change landed, tested, and measured live.
5. A scoped external audit with a named auditor and a dated engagement,
   and the migration/rollback/canary gate closed with a rehearsed drill.
6. A published mainnet UNL-transition procedure and a frozen UNL with
   the stale member (paymuslam.top, 0.00000 24h agreement) removed or
   repaired.
7. The observability gaps fixed: explorer health, topology link count,
   public WebSocket stream.

## What this memo does not claim

- It does not claim the testnet is unsafe. The testnet is healthy.
- It does not claim l1v2 is behind or ahead. l1v2 is a different
  protocol; its devnet is a controlled six-validator network, and its
  design documents are not evidence about the live testnet.
- It does not assign a date. Any date offered without the artifacts
  above would be a guess, and this pack does not guess.
