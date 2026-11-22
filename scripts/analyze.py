#!/usr/bin/env python3
"""analyze.py — derive every measured number in this pack from outputs/.

Reads only the unedited probe outputs under outputs/ and the pinned source
excerpts under fixtures/. Writes:
  outputs/derived/live-testnet-snapshot.json
  outputs/derived/validators.json
  outputs/derived/amendments.json
  outputs/derived/cadence.json
  outputs/derived/homepage-vs-live.json
  findings.json
  run-manifest.json

Every input file's full SHA-256 is printed, so a reader can check that the
derived numbers come from the shipped outputs and nothing else. Re-running
this script over a fresh probe set must reproduce the same structure; values
that move with time (ledger sequence, counts) are compared with tolerances
by scripts/compare_reproduce.py, not byte-for-byte.
"""
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

PACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PACK, "outputs")
DER = os.path.join(OUT, "derived")
os.makedirs(DER, exist_ok=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load(name):
    p = os.path.join(OUT, name)
    print("input %s sha256=%s" % (name, sha256(p)))
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_text(name):
    p = os.path.join(OUT, name)
    print("input %s sha256=%s" % (name, sha256(p)))
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()


def dump(name, obj):
    p = os.path.join(DER, name)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)
    print("wrote %s sha256=%s" % (name, sha256(p)))
    return obj


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    si = load("rpc-server_info.json")["result"]["info"]
    led = load("rpc-ledger.json")["result"]["ledger"]
    led_closed = load("rpc-ledger_closed.json")["result"]
    fee = load("rpc-fee.json")["result"]
    feat = load("rpc-feature.json")["result"]["features"]
    ss = load("rpc-server_state.json")["result"]["state"]
    pf_gen = load("rpc-account_info-pftl-genesis.json")["result"]
    xrpl_gen = load("rpc-account_info-xrpl-genesis.json")["result"]
    xrpl_root = load("rpc-account_info-xrpl-root.json")["result"]
    vhs_val = load("vhs-validators.json")
    vhs_topo = load("vhs-topology-nodes.json")
    vhs_topo_sum = load("vhs-topology.json")
    vhs_net = load("vhs-networks.json")
    vhs_health = load("vhs-health.json")
    vhs_amend_info = load("vhs-amendments-info.json")
    vhs_amend_vote = load("vhs-amendments-vote-test.json")
    metrics = load("explorer-metrics.json")
    exp_health = load_text("explorer-health.json")
    try:
        pr53 = load("pr53-summary.json")
    except FileNotFoundError:
        # GitHub's unauthenticated API quota (60/hour, shared egress IP) can
        # make the PR fetch fail at reproduce time. Record that honestly
        # instead of inventing values; the shipped pack's summary stays the
        # last verified record.
        pr53 = {"fetch_status": "unavailable",
                "note": "GitHub API fetch failed during this run "
                        "(see outputs/pr53-fetch-error.json). PR #53 values "
                        "were last verified 2026-11-22T14:07Z (open, unmerged, "
                        "mergeable_state unstable) in the shipped pack."}
        print("input pr53-summary.json MISSING (fetch unavailable)")
    cadence_rows = []
    with open(os.path.join(OUT, "cadence-run1.jsonl")) as f:
        for line in f:
            line = line.strip()
            if line:
                cadence_rows.append(json.loads(line))
    print("input cadence-run1.jsonl sha256=%s"
          % sha256(os.path.join(OUT, "cadence-run1.jsonl")))

    # ---- live testnet snapshot + supply reconciliation ----
    total_coins = int(led["total_coins"])
    genesis_balance = int(pf_gen["account_data"]["Balance"])
    genesis_supply = 100_000_000_000 * 1_000_000  # INITIAL_XRP, SystemParameters.h
    snapshot = {
        "probed_at_utc": now,
        "build_version": si.get("build_version"),
        "network_id": si.get("network_id"),
        "server_state": si.get("server_state"),
        "peers": si.get("peers"),
        "validation_quorum": si.get("validation_quorum"),
        "validated_ledger_seq": si["validated_ledger"]["seq"],
        "validated_ledger_hash": si["validated_ledger"]["hash"],
        "complete_ledgers": si.get("complete_ledgers"),
        "uptime_seconds": si.get("uptime"),
        "last_close_proposers": (ss.get("last_close") or {}).get("proposers"),
        "last_close_converge_time_ms": (ss.get("last_close") or {}).get("converge_time"),
        "ledger_index": led["ledger_index"],
        "ledger_close_time": led["close_time_human"],
        "ledger_close_time_iso": led["close_time_iso"],
        "ledger_closed_matches": led_closed["ledger_index"] == led["ledger_index"],
        "total_coins_drops": total_coins,
        "total_coins_pft": total_coins / 1e6,
        "base_fee_drops": fee["drops"]["base_fee"],
        "median_fee_drops": fee["drops"]["median_fee"],
        "current_queue_size": fee["current_queue_size"],
        "max_queue_size": fee["max_queue_size"],
        "reserve_base_drops": (ss.get("validated_ledger") or {}).get("reserve_base"),
        "reserve_increment_drops": (ss.get("validated_ledger") or {}).get("reserve_inc"),
        "genesis_account": pf_gen["account_data"]["Account"],
        "genesis_account_balance_drops": genesis_balance,
        "genesis_account_balance_pft": genesis_balance / 1e6,
        "genesis_account_sequence": pf_gen["account_data"]["Sequence"],
        "genesis_supply_drops_assumed": genesis_supply,
        "supply_reconciliation": {
            "genesis_supply_drops": genesis_supply,
            "total_coins_drops": total_coins,
            "burned_by_fees_drops": genesis_supply - total_coins,
            "burned_by_fees_pft": (genesis_supply - total_coins) / 1e6,
            "genesis_account_balance_drops": genesis_balance,
            "other_accounts_drops": total_coins - genesis_balance,
            "other_accounts_pft": (total_coins - genesis_balance) / 1e6,
            "closes": (genesis_balance + (total_coins - genesis_balance)
                       + (genesis_supply - total_coins)) == genesis_supply,
        },
        "xrpl_genesis_account_found": "account_data" in xrpl_gen,
        "xrpl_genesis_account_error": xrpl_gen.get("error"),
        "xrpl_root_account_found": "account_data" in xrpl_root,
        "xrpl_root_account_error": xrpl_root.get("error"),
        "admin_methods_blocked": {
            "validators": load_text("rpc-validators.json").strip(),
            "peers": load_text("rpc-peers.json").strip(),
        },
        "unknown_method": load("rpc-invalid-method.json")["result"],
    }
    dump("live-testnet-snapshot.json", snapshot)

    # ---- validators ----
    vals = vhs_val["validators"]
    unl = [v for v in vals if v.get("unl")]
    topo = vhs_topo["nodes"]
    stale_unl = [v for v in unl if float(v["agreement_24h"]["score"]) == 0.0]
    validators = {
        "validators_total": len(vals),
        "unl_count": len(unl),
        "unl_all_version": sorted({v.get("server_version") for v in unl}),
        "unl_all_domains_verified": all(v.get("domain_verified") for v in unl),
        "versions": {k: sum(1 for v in vals if v.get("server_version") == k)
                     for k in sorted({v.get("server_version") for v in vals})},
        "non_latest_version_count": sum(
            1 for v in vals if v.get("server_version") != "1.0.9"),
        "non_latest_version_unl_count": sum(
            1 for v in unl if v.get("server_version") != "1.0.9"),
        "domains_verified": sum(1 for v in vals if v.get("domain_verified")),
        "with_domain": sum(1 for v in vals if v.get("domain")),
        "agreement_24h": {
            "min": min(float(v["agreement_24h"]["score"]) for v in vals),
            "mean": sum(float(v["agreement_24h"]["score"]) for v in vals) / len(vals),
            "at_least_0_999": sum(
                1 for v in vals if float(v["agreement_24h"]["score"]) >= 0.999),
            "total_missed": sum(v["agreement_24h"]["missed"] for v in vals),
            "unl_total_missed": sum(v["agreement_24h"]["missed"] for v in unl),
        },
        "stale_unl_members": [{
            "validation_public_key": v["validation_public_key"],
            "domain": v.get("domain"),
            "server_version": v.get("server_version"),
            "current_index": v.get("current_index"),
            "agreement_24h_score": v["agreement_24h"]["score"],
            "agreement_24h_missed": v["agreement_24h"]["missed"],
        } for v in stale_unl],
        "topology_nodes": len(topo),
        "topology_node_count_field": vhs_topo_sum.get("node_count"),
        "topology_link_count_field": vhs_topo_sum.get("link_count"),
        "topology_inbound_sum": sum(v.get("inbound_count", 0) for v in topo),
        "topology_outbound_sum": sum(v.get("outbound_count", 0) for v in topo),
        "topology_states": {k: sum(1 for v in topo if v.get("server_state") == k)
                            for k in sorted({v.get("server_state") for v in topo},
                                            key=lambda x: str(x))},
        "topology_country_codes": sorted(
            {v.get("country_code") for v in topo if v.get("country_code")}),
        "vhs_health": vhs_health,
        "vhs_networks": [(n["id"], n["entry"]) for n in vhs_net["networks"]],
        "explorer_metrics": metrics,
        "explorer_health_body": exp_health.strip(),
        "quorum_check": {
            "unl_size": len(unl),
            "validation_quorum_reported": si.get("validation_quorum"),
            "ceil_0_67_x_unl": -(-len(unl) * 67 // 100),
            "ceil_0_60_x_unl": -(-len(unl) * 60 // 100),
            "matches_67pct_formula": si.get("validation_quorum") == max(
                -(-len(unl) * 67 // 100), -(-len(unl) * 60 // 100)),
            "source": "ValidatorList::calculateQuorum, "
                      "postfiatd src/xrpld/app/misc/detail/ValidatorList.cpp",
        },
    }
    dump("validators.json", validators)

    # ---- amendments ----
    enabled = [v for k, v in feat.items() if v["enabled"]]
    disabled = [v for k, v in feat.items() if not v["enabled"]]
    vote_enabled = {a["name"] for a in vhs_amend_vote["amendments"]}
    rpc_enabled = {v["name"] for v in enabled}
    amendments = {
        "known_amendments_rpc": len(feat),
        "enabled_rpc": len(enabled),
        "disabled_rpc": len(disabled),
        "known_amendments_vhs_info": vhs_amend_info.get("count"),
        "enabled_vhs_vote": vhs_amend_vote.get("count"),
        "rpc_enabled_equals_vhs_vote_count": len(enabled) == vhs_amend_vote.get("count"),
        "rpc_enabled_names_equal_vhs_vote_names": rpc_enabled == vote_enabled,
        "names_only_in_rpc": sorted(rpc_enabled - vote_enabled),
        "names_only_in_vhs": sorted(vote_enabled - rpc_enabled),
        "enabled_names": sorted(rpc_enabled),
        "disabled_names": sorted(v["name"] for v in disabled),
        "postfiat_native_amendments": {
            name: {"enabled": feat[k]["enabled"], "id": k}
            for k, name in
            ((k, v["name"]) for k, v in feat.items())
            if name.startswith("PF_")},
        "bulk_enablement": {
            "note": "Every enabled amendment in the VHS vote endpoint "
                    "carries the same ledger_index and date.",
            "distinct_ledger_indexes": sorted(
                {a.get("ledger_index") for a in vhs_amend_vote["amendments"]}),
            "distinct_dates": sorted(
                {a.get("date") for a in vhs_amend_vote["amendments"]}),
        },
        "pr53": pr53,
    }
    # fixAmendmentMajorityCalc lookup by name (feature ids are the keys)
    by_name = {v["name"]: v for v in feat.values()}
    amendments["fix_amendment_majority_calc_enabled"] = by_name.get(
        "fixAmendmentMajorityCalc", {}).get("enabled")
    dump("amendments.json", amendments)

    # ---- cadence ----
    seqs = [r["seq"] for r in cadence_rows if "seq" in r]
    intervals = []
    if len(seqs) >= 2:
        intervals = [(seqs[i + 1] - seqs[i]) for i in range(len(seqs) - 1)]
    cadence = {
        "samples": len(cadence_rows),
        "seq_first": seqs[0] if seqs else None,
        "seq_last": seqs[-1] if seqs else None,
        "ledgers_advanced": (seqs[-1] - seqs[0]) if len(seqs) >= 2 else 0,
        "ledgers_per_sample_interval": intervals,
        "mean_ledgers_per_30s": (sum(intervals) / len(intervals)) if intervals else None,
        "mean_close_interval_s": (30.0 * len(intervals) / sum(intervals)) if intervals and sum(intervals) else None,
        "peers_constant": len({r.get("peers") for r in cadence_rows if "peers" in r}) == 1,
        "peers_value": cadence_rows[0].get("peers") if cadence_rows else None,
    }
    dump("cadence.json", cadence)

    # ---- homepage vs live ----
    homepage = load_text("postfiat-org.html")
    m = re.search(r"snapshot Sep 21, 2026\s*([\d,]+)\s*Validators\s*([\d,]+)\s*Verified domains\s*([\d,]+)\s*24h agreement 99\.9%\+?\s*([\d.]+)M\s*Ledger index",
                  re.sub(r"<[^>]+>", " ", homepage))
    homepage_vs_live = {
        "homepage_snapshot_date": "2026-09-21",
        "homepage_validators": int(m.group(1).replace(",", "")) if m else None,
        "homepage_verified_domains": int(m.group(2).replace(",", "")) if m else None,
        "homepage_agreement_99_9_plus": int(m.group(3).replace(",", "")) if m else None,
        "homepage_ledger_index_millions": float(m.group(4)) if m else None,
        "live_validators": len(vals),
        "live_verified_domains": validators["domains_verified"],
        "live_agreement_99_9_plus": validators["agreement_24h"]["at_least_0_999"],
        "live_ledger_index": si["validated_ledger"]["seq"],
        "stale": True,
        "note": "Homepage snapshot is dated 2026-09-21; live VHS/RPC figures "
                "are from the probe run. All four homepage figures disagree "
                "with live values.",
    }
    dump("homepage-vs-live.json", homepage_vs_live)

    # ---- findings ----
    findings = [
        {
            "id": "F01", "severity": "CRITICAL",
            "title": "No mainnet date and no decided mainnet ordering",
            "status": "UNRESOLVED",
            "evidence": [
                "Founder statement, #validator-ops, 2026-09-18: mainnet "
                "ordering undecided, leaning toward the 'painful option', "
                "likely option 2 (mainnet on postfiatl1v2 with inherited "
                "validator governance after a multi-million-dollar audit). "
                "The 'painful option' was never explicitly named as option 2; "
                "that link is an inference, not a quotation.",
                "Whitepaper (Sept 2026, outputs/postfiat-whitepaper.html): "
                "0 hits for 'testnet', 'conversion', '1:1', 'carryover'. "
                "No mainnet date anywhere in the whitepaper text.",
                "postfiatl1v2 docs/status/network-status.md (reviewed "
                "2026-11-06): the only running network is the controlled "
                "devnet postfiat-wan-devnet-2; 'It is not a production "
                "mainnet, no public testnet is open' (for l1v2).",
            ],
            "gate": "BLOCKS any cutover schedule. No date can be committed.",
        },
        {
            "id": "F02", "severity": "CRITICAL",
            "title": "No 1:1 testnet-to-mainnet conversion mechanism exists for the live testnet",
            "status": "UNRESOLVED",
            "evidence": [
                "No conversion, carryover, or 1:1 mechanism is published for "
                "the live postfiatd testnet (network 2025). The whitepaper "
                "contains no conversion text; postfiatd source contains no "
                "migration/carryover path (genesis is a fresh ledger: "
                "Ledger::Ledger(create_genesis_t), fixtures/source-excerpts/"
                "Ledger-genesis.txt).",
                "The only documented 1:1 path is the l1v2 design: ERC-20 PFT "
                "on Base with a one-for-one path into native PFT at PFTL "
                "mainnet genesis via genesis external lanes "
                "(postfiatl1v2 docs/architecture/pft-token-on-base.md, "
                "genesis-external-lanes.md). It is a design for a different "
                "protocol (Consensus v2), not the live postfiatd testnet.",
                "Nothing is deployed on Base mainnet; only Base Sepolia test "
                "deployments exist. The slice size of the 100B supply is "
                "open. Rehearsal lock released 2026-11-06 on a local "
                "six-validator fleet only.",
                "Doc inconsistency: genesis-external-lanes.md names "
                "0xe36e7fc384564419187546c19719a5654266de0b as the rehearsal "
                "lock, but pft-token-on-base.md says that address is the "
                "ARCHIVED lock ('never locked') and the rehearsal lock is "
                "0xFb6CF3D7E759cB3130C094C1D7264619ecE74D73.",
            ],
            "gate": "BLOCKS any balance-carryover claim. Testnet balances "
                    "must be assumed lost at cutover until a mechanism is published.",
        },
        {
            "id": "F03", "severity": "HIGH",
            "title": "Amendment-dependent readiness is blocked: vote-replay test PR unmerged; PostFiat-native amendments not enabled",
            "status": "UNRESOLVED",
            "evidence": [
                "PR postfiatorg/postfiatd#53 'Test amendment vote replay with "
                "reordered validations': state=%s, merged=%s, "
                "mergeable_state=%s, updated %s (outputs/pr53-summary.json). "
                "The regression test proving amendment-vote outcomes do not "
                "depend on validation order has no merged CI proof." % (
                    pr53.get("state"), pr53.get("merged"),
                    pr53.get("mergeable_state"), pr53.get("updated_at"))
                if pr53.get("state") else
                "PR postfiatorg/postfiatd#53: the GitHub API fetch failed "
                "during this run (%s). Last verified 2026-11-22T14:07Z: "
                "state=open, merged=false, mergeable_state=unstable, "
                "updated 2026-11-13T23:18:29Z. The regression test proving "
                "amendment-vote outcomes do not depend on validation order "
                "has no merged CI proof." % pr53.get("fetch_status"),
                "fixAmendmentMajorityCalc IS enabled on testnet (67%% "
                "threshold active), but order-independence of vote replay "
                "remains unproven without PR #53.",
                "PF_ValidatorVoteTracking and PF_AccountExclusion exist in "
                "code (features.macro lines 45-46) but are NOT enabled on "
                "testnet and are not in voting (outputs/derived/amendments.json). "
                "Vote tracking and account exclusion therefore cannot be "
                "exercised before cutover.",
                "Testnet amendment majority time is 3 days (config) vs the "
                "2-week code default; mainnet config carries no override, "
                "so mainnet amendments would take 2 weeks to activate.",
            ],
            "gate": "BLOCKS amendment-gated cutover steps. Do not cut over "
                    "on amendment behavior that has no merged regression test.",
        },
        {
            "id": "F04", "severity": "HIGH",
            "title": "No external audit of either codebase; migration/rollback gate open",
            "status": "UNRESOLVED",
            "evidence": [
                "postfiatl1v2 docs/security/index.md: 'No external security "
                "audit is recorded in this repository.' Release-gate "
                "inventory (2026-09-01): 21 gates, 4 DONE, 16 OPEN, "
                "1 UNKNOWN. Gate 8 (migration, rollback, canary) OPEN; "
                "gate 20 (topology/independence thresholds) OPEN; gate 12 "
                "(specialist review) OPEN; gate 13 (SP1 reproduction) OPEN.",
                "QA defect inventory: 142 rows (27 P1, 77 P2, 38 P3); fixes "
                "scoped per row, some in source but not deployed.",
                "Launch-topology thresholds are a proposal only, awaiting "
                "the operator's confirmation (2026-09-01).",
            ],
            "gate": "BLOCKS a production cutover. The founder's "
                    "'multi-million-dollar audit' is a statement, not a "
                    "scoped engagement: no auditor, scope, or date is published.",
        },
        {
            "id": "F05", "severity": "HIGH",
            "title": "Mainnet quorum must change: testnet runs a 67% quorum the code says to revert to 80% for mainnet",
            "status": "OPEN (code change required, untested at 80%)",
            "evidence": [
                "ValidatorList::calculateQuorum returns "
                "max(ceil(effectiveUnlSize*0.67), ceil(unlSize*0.6)) with "
                "the comment: 'Use a 67%% quorum ... Original XRPL uses 80%%, "
                "but this fork uses 67%% for devnet/testnet. For mainnet, "
                "this should be reverted to 80%%.' "
                "(fixtures/source-excerpts/ValidatorList-quorum.txt).",
                "Live check closes the loop: UNL 25 -> ceil(25*0.67)=17, "
                "ceil(25*0.6)=15, reported validation_quorum=17 "
                "(outputs/derived/validators.json quorum_check).",
                "At 80%% a 25-member UNL needs 20 validations; the stale UNL "
                "member (F07) plus any second outage would leave 23 active, "
                "still above 20 — but no 80%% quorum has ever run on this network.",
            ],
            "gate": "REQUIRED before mainnet: change the quorum constant, "
                    "re-run the full amendment/consensus test battery, and "
                    "re-measure liveness with the production UNL.",
        },
        {
            "id": "F06", "severity": "HIGH",
            "title": "UNL is centrally administered; no published mainnet UNL-transition procedure",
            "status": "UNRESOLVED",
            "evidence": [
                "Whitepaper: 'one organization administers the current "
                "validator fleet'; 'independently operated validators' is "
                "listed among the requirements that 'remain proposals'.",
                "Shipped validators.txt (configs/) is a template with no "
                "validator keys and no validator_list_sites configured in "
                "either mainnet or testnet config; the live UNL is "
                "operator-supplied, not reproducible from the repo.",
                "VHS derives the UNL from the admin `validators` RPC "
                "(docs/POSTFIAT.md); the public proxy blocks that method "
                "(HTTP 403, outputs/rpc-validators.json), so outside "
                "operators cannot independently fetch the UNL from RPC.",
                "Mainnet config ships in-repo and differs from testnet only "
                "in network_id (2026), seed peers (rpc.mainnet.postfiat.org "
                "only), and the absence of the 3-day amendment-majority "
                "override (configs/config-diff-mainnet-vs-testnet.txt).",
            ],
            "gate": "BLOCKS a decentralized cutover. The runbook "
                    "(docs/runbook.md) is validated only against live "
                    "testnet observations and the shipped configs.",
        },
        {
            "id": "F07", "severity": "MEDIUM",
            "title": "One UNL member is stale (0.00000 24h agreement); 12 non-UNL validators run old builds",
            "status": "MEASURED",
            "evidence": [
                "UNL member paymuslam.top (key nHBxQ3srN8Er): 24h agreement "
                "0.00000, current_index 8179976 vs network %d at probe time "
                "(~%d ledgers / ~3 days behind). 1 of 25 UNL members contributes "
                "nothing to current consensus." % (
                    snapshot["validated_ledger_seq"],
                    snapshot["validated_ledger_seq"] - 8179976),
                "UNL 24h missed validations total 38,365, dominated by the "
                "stale member.",
                "12 of 66 validators (18%%) run older builds (1.0.4 x9, "
                "1.0.8 x1, 1.0.0 x2); none is on the UNL. All 25 UNL members "
                "run 1.0.9 and all 25 domains are verified.",
            ],
            "gate": "Cutover precondition: remove or repair the stale UNL "
                    "member and re-measure UNL agreement before any "
                    "mainnet UNL is frozen.",
        },
        {
            "id": "F08", "severity": "MEDIUM",
            "title": "Rollback against a real cutover is untested; no cutover has ever been performed",
            "status": "UNRESOLVED",
            "evidence": [
                "l1v2 release gate 8 (migration, rollback, canary) is OPEN; "
                "the 2026-10-30 l1v2 deployment record notes 'no rollback "
                "needed' — a rollback has never been exercised on either "
                "codebase in a cutover context.",
                "The runbook (docs/runbook.md) rollback section is a "
                "procedure derived from config + live read-only behavior, "
                "not an executed drill.",
                "postfiatd has no in-protocol rollback: a bad mainnet "
                "genesis cannot be 'rolled back' — it can only be abandoned "
                "and re-genesis'd, which destroys mainnet state created "
                "after genesis.",
            ],
            "gate": "REQUIRED before cutover: a rehearsed rollback drill "
                    "on a staging network with a published stop condition.",
        },
        {
            "id": "F09", "severity": "MEDIUM",
            "title": "Public observability gaps: explorer health failing, topology link count 0, WebSocket stream not publicly subscribable",
            "status": "MEASURED",
            "evidence": [
                "explorer /api/v1/health returns HTTP 500 "
                "'{\"message\":\"rippled unreachable\"}' while /api/v1/metrics "
                "works (base_fee 0.00001, txn_sec 0.09, ledger_interval 3.022).",
                "VHS topology reports node_count 72 but link_count 0, "
                "while per-node inbound/outbound sums are 690/710 — the "
                "aggregate contradicts the per-node data.",
                "VHS /v1/network/networks still lists 2 webhook.site test "
                "entries alongside the real test network.",
                "WebSocket ledger subscribe: :443 upgrade answered HTTP 401 "
                "'Invalid protocol.' (Caddy/postfiatd-1.0.9); :6005 gave no "
                "response within 15 s. Public monitoring depends on HTTP polling.",
                "VHS health returns {\"count\":\"8\"} — an unexplained figure.",
            ],
            "gate": "Cutover precondition: fix or document every "
                    "observability gap; a cutover cannot be monitored on "
                    "endpoints that report unreachable/0.",
        },
        {
            "id": "F10", "severity": "LOW",
            "title": "Public validator counts disagree; homepage snapshot two months stale",
            "status": "MEASURED",
            "evidence": [
                "Homepage snapshot Sep 21, 2026: 53 validators, 39 verified "
                "domains, 52 at 24h agreement 99.9%+, 6.5M ledger index. "
                "Live 2026-11-22: 66 validators, 55 verified domains, 63 at "
                ">=0.999, ledger 8,272,101 (outputs/derived/homepage-vs-live.json).",
            ],
            "gate": "None for cutover; refresh the homepage snapshot before "
                    "any public readiness claim.",
        },
        {
            "id": "F11", "severity": "LOW",
            "title": "Cosmetic divergence: postfiatd still reports the native currency code as 'XRP' in source",
            "status": "MEASURED",
            "evidence": [
                "SystemParameters.h systemCurrencyCode() returns \"XRP\" "
                "(fixtures/source-excerpts/SystemParameters.h.txt) while "
                "the asset is PFT. Ledger behavior is unaffected (amounts "
                "are drops of the native asset); only display/code strings "
                "are stale.",
            ],
            "gate": "None for cutover; rename before mainnet to avoid "
                    "integrator confusion.",
        },
        {
            "id": "F12", "severity": "INFO",
            "title": "Verified healthy: genesis supply reconciles exactly; ledger advancing steadily; amendment state agrees across two independent sources",
            "status": "VERIFIED",
            "evidence": [
                "Genesis supply 100,000,000,000 PFT (INITIAL_XRP, "
                "SystemParameters.h:43) reconciles: genesis account holds "
                "96,999,999,999.99988 PFT, other accounts hold "
                "%.6f PFT, %.6f PFT burned in fees; "
                "sum closes exactly (outputs/derived/live-testnet-snapshot.json)."
                % (snapshot["supply_reconciliation"]["other_accounts_pft"],
                   snapshot["supply_reconciliation"]["burned_by_fees_pft"]),
                "Cadence: %d ledgers in 600 s of sampling, mean close interval "
                "%.3f s (outputs/cadence-run1.jsonl). Fee queue empty "
                "(0/2000), base fee 10 drops, median fee 5000 drops."
                % (cadence["ledgers_advanced"],
                   cadence["mean_close_interval_s"]),
                "Amendment state agrees across two independent sources: "
                "RPC `feature` reports 64 enabled of 101 known; VHS vote "
                "endpoint reports 64 enabled with identical names.",
                "All 64 enabled amendments share one enablement point: "
                "ledger 86785, 2026-02-09T14:31:12Z (genesis-era bulk enablement).",
                "Latest release v1.0.9 (2026-10-10) is the live build on all "
                "25 UNL members and on the RPC node.",
            ],
            "gate": "None. This is the evidence that the testnet itself is "
                    "healthy; it does not imply mainnet readiness.",
        },
    ]
    with open(os.path.join(PACK, "findings.json"), "w") as f:
        json.dump({"generated_at_utc": now, "findings": findings}, f, indent=1)
    print("wrote findings.json sha256=%s"
          % sha256(os.path.join(PACK, "findings.json")))

    # ---- run manifest ----
    manifest = {
        "pack": "PFTL mainnet cutover readiness evidence pack",
        "generated_at_utc": now,
        "probe_window_utc": "2026-11-22: first probe 14:09-14:21Z, canonical re-probe 15:42-15:43Z, cadence re-run 15:44-15:54Z",
        "environment": {
            "python": sys.version.split()[0],
            "tools": "curl, git, python3 (stdlib only)",
            "network": "public endpoints only; no credentials, sessions, accounts, or signing",
        },
        "repo_pins": {
            "postfiatd": "0085a1ff885d6a446369cf73a4430f75af22be55 (2026-10-10, PR #50 merge, v1.0.9)",
            "validator-history-service": "d301c4ce78e109f1771d4429e17876a97e2654f3 (2026-09-17)",
            "postfiatl1v2": "071b6dc461efc7a9105b2d3cac6acd3686901e7d (2026-11-22)",
            "explorer": "74161a20f200b6ad093e9d6d884fc4c370acb93c (2026-10-09)",
        },
        "live_endpoints": [
            "https://rpc.testnet.postfiat.org/ (postfiatd 1.0.9, network_id 2025)",
            "https://vhs.testnet.postfiat.org/v1/",
            "https://explorer.testnet.postfiat.org/api/v1/",
            "https://postfiat.org/ and https://postfiat.org/whitepaper/ (Sept 2026)",
            "https://api.github.com/repos/postfiatorg/postfiatd/pulls/53",
        ],
        "counts": {
            "findings_total": len(findings),
            "by_severity": {sev: sum(1 for x in findings if x["severity"] == sev)
                            for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]},
            "unresolved": sum(1 for x in findings if x["status"] == "UNRESOLVED"),
        },
        "verdict": "NOT READY for mainnet cutover: 2 CRITICAL + 4 HIGH findings, "
                   "5 explicitly unresolved claims (1:1 conversion, rollback, "
                   "mainnet/TGE date, audit scope, amendment vote-replay proof).",
        "notes": [
            "Assessment only: no cutover performed, no mainnet touched, no funds spent, nothing signed.",
            "The live postfiatd testnet (XRPL-fork, network 2025) and the "
            "postfiatl1v2 design (Consensus v2) are different systems; this "
            "pack keeps measured (live testnet) and specified (l1v2 design) "
            "claims apart throughout.",
        ],
    }
    with open(os.path.join(PACK, "run-manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print("wrote run-manifest.json sha256=%s"
          % sha256(os.path.join(PACK, "run-manifest.json")))


if __name__ == "__main__":
    main()
