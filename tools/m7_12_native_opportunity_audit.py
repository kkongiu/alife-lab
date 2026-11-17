"""M7.12: direct untouched M6 candidate-exposure audit of native ring reclosure.

Use first naturally aged spontaneous 4/6/8 ring from unchanged M7.11.
Observe original chemistry._candidate_pairs generator from a TEMPORARY wrapper,
no changed candidate yielded, no RNG use, no changed native physics.
All 640 new seed worlds, including nulls, and first selected in each
fixed 40-world shard independently reproduced without the wrapper.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from math import sqrt
from pathlib import Path

from alife import chemistry
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_2_energy_distribution import ledger
from tools.m7_4_material_feedback import EventTape,native_pairs
from tools.m7_11_ring_fault_tolerance import scan_first_native_aged_ring,excise_refund
from tools.m7_8_frozen_reactions import formation_only_pair_keyed

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_12_reclosure"
PFILE=BASE/"protocol.json"
DATA=BASE/"results.json"
M711=ROOT/"tools/m7_11_ring_fault_tolerance.py"
M6=ROOT/"src/alife/chemistry.py"
FIRST,LAST=30001,30640


def protocol():
    p=json.loads(PFILE.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-12-native-cut-edge-chemical-opportunity-audit-v1"
    assert p["status"]=="preregistered_before_new_runner_and_observed_outcomes"
    s=p["sample"]
    assert (s["seed_first"],s["seed_last"],s["n"])==(FIRST,LAST,640)
    assert len(s["shards"])==16
    assert [i for x in s["shards"] for i in range(x["start"],x["end"]+1)]==list(range(FIRST,LAST+1))
    assert p["integrity"]["no_change_to_src_master_or_M711"]
    return p


def provenance():
    return {
        "m712_protocol_sha256":sha256(PFILE.read_bytes()).hexdigest(),
        "unchanged_M711_ring_selector_sha256":sha256(M711.read_bytes()).hexdigest(),
        "unchanged_M6_chemistry_sha256":sha256(M6.read_bytes()).hexdigest()
    }


def adjacent(w,pair):
    a,b=(w.store.index_of(i) for i in pair)
    dx=abs(w.store.xs[a]-w.store.xs[b])
    dy=abs(w.store.ys[a]-w.store.ys[b])
    if w.periodic:
        dx=min(dx,w.store.width-dx)
        dy=min(dy,w.store.height-dy)
    return dx+dy==1


def initial_static(w,pair,edges):
    a,b=sorted((w.store.index_of(i) for i in pair))
    store=w.store
    assert (a,b) not in store.bonds
    compatible=(store.species[a],store.species[b]) in w.allowed_pairs or (
        store.species[b],store.species[a]) in w.allowed_pairs
    valence=(store.degree[a]<w.max_bonds[store.species[a]]
             and store.degree[b]<w.max_bonds[store.species[b]])
    sufficient=(store.energy[a]>=w.formation_cost and store.energy[b]>=w.formation_cost)
    still_anchored=all(any(i in edge for edge in edges-{pair}) for i in pair)
    return {
        "adjacent":adjacent(w,pair),
        "still_anchored_by_surviving_original_bonds":still_anchored,
        "native_species_compatible":compatible,
        "native_valence_available":valence,
        "native_both_endpoints_energetically_eligible":sufficient,
        "native_formation_probability":w.chemistry.formation_probability,
        "endpoint_energies":[store.energy[a],store.energy[b]],
        "endpoint_degrees":[store.degree[a],store.degree[b]],
        "is_an_actual_native_pair_candidate_now":(
            any({store.ids[i],store.ids[j]}==set(pair) for i,j in chemistry._candidate_pairs(w))
            and pair not in {tuple(sorted((store.ids[i],store.ids[j]))) for i,j in store.bonds}
        )
    }


def advance_with_exact_candidate_audit(w,target):
    """Wrapper mirrors exact native iterator order, draws NO extra random values."""
    previous=chemistry._candidate_pairs
    records=[]
    def auditing(world):
        for i,j in previous(world):
            if tuple(sorted((world.store.ids[i],world.store.ids[j])))==target:
                records.append({
                    "candidate_at_exact_native_formation_stage":True,
                    "pre_draw_endpoint_energy":[world.store.energy[i],world.store.energy[j]],
                    "pre_draw_degree":[world.store.degree[i],world.store.degree[j]],
                    "pair_adjacent":adjacent(world,target)
                })
            yield i,j
    chemistry._candidate_pairs=auditing
    try:
        w.advance(1)
    finally:
        chemistry._candidate_pairs=previous
    assert len(records)<=1
    return records


def run_one(seed,verify=False):
    parent,ring,scan=scan_first_native_aged_ring(seed)
    if ring is None:
        return {"seed":seed,"selected":False,"scan":scan}
    source_hash=parent.state_hash_full()
    source_rng=(parent.rng.fingerprint(),parent.rng.draws)
    ring_ids=tuple(ring["ids"])
    edges=set(ring["edges"])
    target=min(edges)
    cut=clone_world(parent)
    refund=excise_refund(cut,target)
    initial=initial_static(cut,target,edges)
    assert initial["adjacent"] and initial["still_anchored_by_surviving_original_bonds"]
    assert initial["native_species_compatible"] and initial["native_valence_available"]
    assert cut.energy()==parent.energy()
    postcut_hash=cut.state_hash_full()

    # Same frozen geometry/energy, 32 exogenous pair-lottery single chemical
    # sweeps, NOT actual 120-tick native evolution and not 32 seed worlds.
    frozen=[]
    for salt in range(32):
        trial=clone_world(cut)
        formed=formation_only_pair_keyed(trial,ring_ids,seed,salt)
        frozen.append({
            "salt":salt,
            "exact_target_pair_formed":list(target) in formed["formed_all_pair_ids"],
            "native_pairs_attempted":formed["native_pairs_attempted"],
            "final_physical_hash":formed["after_one_formation_sweep_full_hash"]
        })
    assert cut.state_hash_full()==postcut_hash

    w=clone_world(cut)
    tape=EventTape()
    w.event_sink=tape
    exposures=[]
    first_reclosure=None
    first_surviving_break=None
    all_target_native_forms=0
    eligible_n=0
    prebreak_ticks=0
    prebreak_adjacent=0
    prebreak_anchored=0
    for t in range(1,121):
        in_risk=first_reclosure is None and first_surviving_break is None
        if in_risk:
            # These are PREstep physical descriptors; exact chemical-stage
            # admissibility comes from the observed original generator.
            pre=initial_static(w,target,edges)
            prebreak_ticks+=1
            prebreak_adjacent+=bool(pre["adjacent"])
            prebreak_anchored+=bool(pre["still_anchored_by_surviving_original_bonds"])
            records=advance_with_exact_candidate_audit(w,target)
        else:
            records=[]
            w.advance(1)
        events=tape.pop(w.step)
        broken={pair for kind,pair in events if kind=="break" and pair in edges-{target}}
        target_formed=any(kind=="form" and pair==target for kind,pair in events)
        if in_risk:
            if records:
                assert len(records)==1
                eligible_n+=1
            if target_formed:
                assert records,("Real native chemical formation without native candidate",seed,t)
            exposures.append({
                "relative_tick":t,
                "target_at_native_formation_stage":bool(records),
                "prestep_adjacent":pre["adjacent"],
                "prestep_surviving_ring_anchoring":pre["still_anchored_by_surviving_original_bonds"],
                "native_candidate_stage":records[0] if records else None,
                "actual_native_target_FORM_event":target_formed,
                "real_native_break_other_original_ring_edge":bool(broken)
            })
        if first_surviving_break is None and broken:
            first_surviving_break=t
        if target_formed:
            all_target_native_forms+=1
            if first_reclosure is None and target in native_pairs(w):
                first_reclosure=t
        energy_transfer(w,"bond_only")
    w.event_sink=None
    w.check()
    ledger(w,w.configured_energy())
    has_early=first_reclosure is not None and (first_surviving_break is None or first_reclosure<first_surviving_break)
    # Same-tick original break invalidation, even when target reforms.
    if has_early:
        assert any(x["actual_native_target_FORM_event"] and x["relative_tick"]==first_reclosure for x in exposures)
    if verify:
        clone=clone_world(cut)
        for _ in range(120):
            clone.advance(1)
            energy_transfer(clone,"bond_only")
        assert clone.state_hash_full()==w.state_hash_full()
        assert (clone.rng.fingerprint(),clone.rng.draws)==(w.rng.fingerprint(),w.rng.draws)
    assert parent.state_hash_full()==source_hash
    assert (parent.rng.fingerprint(),parent.rng.draws)==source_rng
    return {
        "seed":seed,"selected":True,
        "source_ring":{"ids":list(ring_ids),"edges":[list(x) for x in sorted(edges)],
                       "size":ring["size"],"continuous_snapshot_age":ring["continuous_snapshot_age"]},
        "scan":scan,
        "original_native_source_hash":source_hash,
        "postcut_energy_conserving_hash":postcut_hash,
        "native_full_refund":refund,
        "t0_cut_pair_native_geometry_energy_valence":initial,
        "first_actual_native_target_FORM_tick":first_reclosure,
        "first_other_original_ring_edge_real_break_tick":first_surviving_break,
        "real_native_target_reclosure_before_other_break":has_early,
        "actual_target_pair_candidate_attempts_before_first_event_or_censor":eligible_n,
        "pre_event_or_censor_ticks":prebreak_ticks,
        "prestep_adjacent_at_risk_ticks":prebreak_adjacent,
        "prestep_anchored_at_risk_ticks":prebreak_anchored,
        "native_candidate_exposures":exposures,
        "frozen_same-geometry_32_pair_lotteries":frozen,
        "final":{"full_hash":w.state_hash_full(),"rng":w.rng.fingerprint(),
                 "draws":w.rng.draws,"energy":w.energy(),"injected":w.injected,
                 "unabsorbed":w.unabsorbed,"dissipated":w.dissipated}
    }


def wilson(k,n):
    if not n:return None
    z=1.95996398454
    p=k/n
    m=(p+z*z/(2*n))/(1+z*z/n)
    h=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [round(m-h,6),round(m+h,6)]


def summary(rows):
    assert len(rows)==640 and [x["seed"] for x in rows]==list(range(FIRST,LAST+1))
    selected=[x for x in rows if x["selected"]]
    n=len(selected)
    k=sum(x["real_native_target_reclosure_before_other_break"] for x in selected)
    total=sum(x["actual_target_pair_candidate_attempts_before_first_event_or_censor"] for x in selected)
    # Count first target real FORM before ANY end-of-risk decision: if same-tick
    # surviving edge break, record the form but it is NOT an early repair.
    target_events_at_risk=sum(
        sum(y["actual_native_target_FORM_event"] for y in x["native_candidate_exposures"])
        for x in selected
    )
    missing=sum(
        sum(y["actual_native_target_FORM_event"] and not y["target_at_native_formation_stage"]
            for y in x["native_candidate_exposures"])
        for x in selected
    )
    at_risk_ticks=sum(x["pre_event_or_censor_ticks"] for x in selected)
    candidate_success_ratio=target_events_at_risk/total if total else 0
    gate=(n>=40 and total>=100 and target_events_at_risk>0 and
          missing/target_events_at_risk<=0.05)
    # secondary numerical band is strictly DESCRIPTIVE, not a proof of IID
    return {
        "source_worlds":640,"naturally_aged_native_rings":n,"no_ring":640-n,
        "original_ring_sizes":dict(Counter(str(x["source_ring"]["size"]) for x in selected)),
        "native_exact_pair_early_reclosure":k,
        "native_exact_pair_early_reclosure_fraction":round(k/n,6) if n else None,
        "at_risk_native_ticks":at_risk_ticks,
        "target_pair_exact_native_formation_candidates":total,
        "actual_native_target_FORM_events_during_at_risk":target_events_at_risk,
        "native_forms_without_true_original_pair_candidate":missing,
        "conditional_native_event_per_candidate":round(candidate_success_ratio,6),
        "empirical_approx_wilson95":wilson(target_events_at_risk,total),
        "original_M6_native_formation_probability":0.05,
        "fraction_at_risk_ticks_with_adjacent_endpoints":round(
            sum(x["prestep_adjacent_at_risk_ticks"] for x in selected)/at_risk_ticks,6) if at_risk_ticks else None,
        "fraction_at_risk_ticks_with_surviving_original_edge_anchor":round(
            sum(x["prestep_anchored_at_risk_ticks"] for x in selected)/at_risk_ticks,6) if at_risk_ticks else None,
        "frozen_immediate_pair_keyed_trial_target_forms_across_32_salts":sum(
            sum(y["exact_target_pair_formed"] for y in x["frozen_same-geometry_32_pair_lotteries"]) for x in selected
        ),
        "preregistered_decisions":{
            "native_reclosure_requires_observed_original_M6_candidate":("passed" if gate else "not_met"),
            "native_formation_hazard_within_descriptive_band_003_007":(
                0.03<=candidate_success_ratio<=0.07 if total>=100 else None
            ),
            "native_hazard_band_is_descriptive_not_a_test_of_active_repair":True
        },
        "caveat":"The native 0.05 chance is per eligible pair candidate, not per tick. Early event censoring and correlated within-world RNG mean the Wilson interval is approximate. This is observational verification of original M6 chemistry, not a causal proof of biological adaptation."
    }


def run_shard(start,end):
    p=protocol()
    d={"start":start,"end":end}
    assert d in p["sample"]["shards"]
    out=[]
    first=None
    for seed in range(start,end+1):
        r=run_one(seed,verify=(first is None))
        out.append(r)
        if r["selected"] and first is None:first=seed
        if (seed-start+1)%10==0:
            print(f"M712_PROGRESS {start}-{end} seed={seed} rings={sum(x['selected'] for x in out)}",flush=True)
    chunk={"schema":"alife-m7-12-shard-v1","descriptor":d,
           "provenance":provenance(),"first_selected_no_observer_native_replay":first,"worlds":out}
    path=BASE/"shards"/f"{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(chunk,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M712_SHARD="+json.dumps({"start":start,"end":end,"ring_worlds":sum(x["selected"] for x in out)},sort_keys=True),flush=True)


def merge():
    p=protocol()
    paths=list((BASE/"shards").glob("*.json"))
    assert len(paths)==16
    seen=[]
    allrows=[]
    for path in paths:
        d=json.loads(path.read_text(encoding="utf-8"))
        assert d["schema"]=="alife-m7-12-shard-v1"
        assert d["provenance"]==provenance()
        x=d["descriptor"]
        assert x in p["sample"]["shards"] and x not in seen
        seen.append(x)
        assert [r["seed"] for r in d["worlds"]]==list(range(x["start"],x["end"]+1))
        assert d["first_selected_no_observer_native_replay"]==next((r["seed"] for r in d["worlds"] if r["selected"]),None)
        allrows+=d["worlds"]
    assert all(x in seen for x in p["sample"]["shards"])
    allrows.sort(key=lambda x:x["seed"])
    output={"schema":"alife-m7-12-full-640-native-ring-chemistry-observer-v1",
            "provenance":provenance(),"worlds":allrows,
            "summary":summary(allrows),"strict_640_seed_16_shards_complete":True}
    DATA.parent.mkdir(parents=True,exist_ok=True)
    DATA.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("M712_FINAL_SUMMARY="+json.dumps(output["summary"],sort_keys=True),flush=True)
    print("M712_SUCCESS=640",flush=True)


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    sh=sub.add_parser("shard")
    sh.add_argument("--start",type=int,required=True)
    sh.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    a=ap.parse_args()
    if a.cmd=="shard":run_shard(a.start,a.end)
    else:merge()


if __name__=="__main__":
    main()
