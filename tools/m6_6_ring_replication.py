"""M6.6: independent new-seed confirmation of the frozen M6.5 fork gate.

Read-only analysis and intervention applied to cloned natural rings, reusing
the EXACT M6.5 code and threshold; original M6 physical laws unchanged.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from tools.m6_5_ring_forks import (
    protocol as m65_protocol,
    sample_density,
    summary as m65_summary,
)

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m6_6_ring_replication/protocol.json"
OUTPUT=ROOT/"campaigns/m6_6_ring_replication/results.json"


def registered():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-6-independent-fork-replication-v1"
    assert p["status"]=="frozen-before-code-and-outcomes"
    assert p["fixed_sampling"]["seeds"]==list(range(9001,9021))
    assert p["fixed_sampling"]["expected_worlds"]==40
    assert p["fixed_sampling"]["followup_steps"]==120
    assert p["original_M65_gate_unchanged"]["keep_vs_lowest_required_absolute_difference_each_density"]==.2
    return p


def compatible_original(p):
    """Alter only prospective seed set; everything else stays original M6.5."""
    old=m65_protocol()
    assert old["sampling"]["followup_steps"]==p["fixed_sampling"]["followup_steps"]
    assert old["sampling"]["precursor_max_tick"]==p["fixed_sampling"]["max_precursor_tick"]
    assert old["sampling"]["arms"]==p["fixed_sampling"]["arms"]
    assert old["sampling"]["densities"]==p["fixed_sampling"]["densities"]
    assert old["decision"]["min_selected_pairs"]==p["original_M65_gate_unchanged"]["min_selected_pairs"]
    old["sampling"]["seeds"]=p["fixed_sampling"]["seeds"]
    return old


def secondary(forks,p):
    results={}
    for den in p["fixed_sampling"]["densities"]:
        group=[f for f in forks if f["density"]==den]
        details={}
        for arm in p["fixed_sampling"]["arms"]:
            subset=[f["arms"][arm] for f in group]
            firsts=[r["first_ring_observed_tick"] for r in subset
                    if r["first_ring_observed_tick"] is not None]
            snapshot_counts={}
            for t in (1,10,50,120):
                n=sum(
                    any(s["step_since_fork"]==t and s["isolated"]
                        for s in r["snapshots"])
                    for r in subset
                )
                snapshot_counts[str(t)]=n
            details[arm]={
                "rings_with_any_reclosure":len(firsts) if arm!="keep_ring" else None,
                "rings_reclosed_by_step10":sum(v<=10 for v in firsts)
                    if arm!="keep_ring" else None,
                "mean_first_reclosure_tick_if_observed":
                    round(sum(firsts)/len(firsts),3)
                    if arm!="keep_ring" and firsts else None,
                "isolated_at_selected_steps":snapshot_counts,
                "first_loss_reasons":dict(Counter(
                    r["first_loss_reason"] or "right_censored"
                    for r in subset
                )),
            }
        by_seed={}
        for seed in p["fixed_sampling"]["seeds"]:
            c=[f for f in group if f["precursor_seed"]==seed]
            by_seed[str(seed)]={
                "selected_ring_forks":len(c),
                "keep_isolated":sum(f["arms"]["keep_ring"]["final_isolated"] for f in c),
                "lowest_isolated":sum(f["arms"]["open_lowest_edge"]["final_isolated"] for f in c),
                "opposite_isolated":sum(f["arms"]["open_opposite_edge"]["final_isolated"] for f in c),
                "all_fork_world_snapshots":len(set(f["fork_world_step"] for f in c)),
            }
        results[den]={
            "fork_count":len(group),
            "arm_measurements":details,
            "by_seed":by_seed,
        }
    return results


def run():
    p=registered()
    compatible=compatible_original(p)
    cases=[]
    worlds=[]
    for den in p["fixed_sampling"]["densities"]:
        world_results, selected=sample_density(den,compatible)
        worlds.extend(world_results)
        cases.extend(selected)
    assert len(worlds)==40
    assert len(cases)<=80
    assert all(f["ring"]["sig"].startswith("C2:") for f in cases)
    score=m65_summary(cases,compatible)
    assert score["verdict"] in (
        "ring_closure_protection_signal",
        "no_robust_ring_closure_protection",
        "underpowered",
    )
    outcome=(
        "replicated_original_gate" if score["gate_passed"]
        else "underpowered" if score["verdict"]=="underpowered"
        else "not_confirmed_under_original_gate"
    )
    result={
        "schema":"alife-m6-6-confirmatory-results-v1",
        "preregistered_protocol_commit":"0019d1e4e024b3689a481bdbe8e37ddc938327fd",
        "preregistered_protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "n_worlds":len(worlds),
        "n_paired_forks":len(cases),
        "original_M65_gate_reapplied_without_change":score,
        "confirmatory_verdict":outcome,
        "secondary_ring_reclosure":secondary(cases,p),
        "worlds":worlds,
        "forks":cases,
        "no_law_changes":True,
        "no_replication_or_heredity_claim":True,
        "epistemic_limit":"opening includes bond-energy redistribution and free valence, not isolated topology"
    }
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M66_REPLICATION_SUMMARY="+json.dumps({
        "worlds":result["n_worlds"],
        "forks":result["n_paired_forks"],
        "original_gate":score,
        "verdict":outcome,
        "reclosure":{
            den:{
                arm:{k:v for k,v in vals.items() if k not in ("isolated_at_selected_steps","first_loss_reasons")}
                for arm,vals in info["arm_measurements"].items()
            } for den,info in result["secondary_ring_reclosure"].items()
        }
    },sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    run()
