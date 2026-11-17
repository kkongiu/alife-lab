"""M7.13 — intent-to-treat first lesion history and a second distinct ring cut.

All 640 ORIGINAL native seed-worlds, no selection on successful first repair.
Same one naturally aged first ring in each world. First 120 native steps:
  experienced: native first ring-edge excision + exact bond energy refund
  energy sham: EXACT SAME particle energy redistribution without bond excision,
               by setting that bond energy to zero (explicit nonnative sham)
  naive: untouched first ring
At t120, precommitted SECOND original ID bond is excised if currently present;
if missing, endpoint FALSE (never substitute another target).
All three fork histories advance the SAME number of native M6/M7.3 steps.
No learning, heredity, metabolism or life claims from changed probabilities.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from tools.m6_5_ring_forks import clone_world
from tools.m7_2_energy_distribution import ledger
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_4_material_feedback import EventTape,native_pairs,coherent_root_size
from tools.m7_11_ring_fault_tolerance import scan_first_native_aged_ring,excise_refund

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_13_history"
PFILE=BASE/"protocol.json"
DATA=BASE/"results.json"
ORIGINAL_SCAN=ROOT/"tools/m7_11_ring_fault_tolerance.py"
ORIGINAL_M73=ROOT/"tools/m7_3_bond_energy.py"
FIRST,LAST=31001,31640
ARMS=("first_lesion","energy_only_first_sham","no_first_lesion")
FIRST_PHASE=120
SECOND_PHASE=120
CHECKPOINTS=(1,30,60,120,121,150,180,240)


def protocol():
    p=json.loads(PFILE.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-13-first-damage-history-and-second-challenge-v1"
    assert p["status"]=="preregistered_before_M712_outcomes_and_M713_runner"
    s=p["sample"]
    assert (s["seed_first"],s["seed_last"],s["n"])==(FIRST,LAST,640)
    assert len(s["shards"])==16
    assert [j for d in s["shards"] for j in range(d["start"],d["end"]+1)]==list(range(FIRST,LAST+1))
    assert p["arms"]["timepoints"]==list(CHECKPOINTS)
    assert p["integrity"]["never_filter_first_repair_success"]
    return p


def provenance():
    return {
        "m713_protocol_sha256":sha256(PFILE.read_bytes()).hexdigest(),
        "original_M711_native_ring_scanner_sha256":sha256(ORIGINAL_SCAN.read_bytes()).hexdigest(),
        "original_M73_native_energy_conduction_sha256":sha256(ORIGINAL_M73.read_bytes()).hexdigest()
    }


def energy_only_refund_keep_bond(world,pair):
    """Artificial zero-bond-energy control: t0 particle energy equal to cut."""
    i,j=sorted((world.store.index_of(v) for v in pair))
    assert (i,j) in world.store.bonds
    old=(world.energy(),world.dissipated,world.rng.fingerprint(),world.rng.draws)
    stored=world.store.bonds[(i,j)]
    world.store.bonds[(i,j)]=0
    world.store.energy[i]+=(stored+1)//2
    world.store.energy[j]+=stored//2
    assert (world.energy(),world.dissipated,world.rng.fingerprint(),world.rng.draws)==old
    assert tuple(pair) in native_pairs(world)
    world.check()
    ledger(world,world.configured_energy())
    return {"zeroed_original_bond_energy":stored,
            "bond_and_valence_unchanged":True,
            "exact_total_world_energy_and_RNG":True}


def apply_first(parent,first_edge):
    arms={a:clone_world(parent) for a in ARMS}
    assert len({x.state_hash_full() for x in arms.values()})==1
    original_rng=(parent.rng.fingerprint(),parent.rng.draws)
    original_energy=parent.energy()
    cut=excise_refund(arms["first_lesion"],first_edge)
    sham=energy_only_refund_keep_bond(arms["energy_only_first_sham"],first_edge)
    assert cut["native_bond_energy_fully_refunded"]==sham["zeroed_original_bond_energy"]
    assert arms["first_lesion"].store.energy==arms["energy_only_first_sham"].store.energy
    assert arms["first_lesion"].store.bonds!=arms["energy_only_first_sham"].store.bonds
    assert len({x.energy() for x in arms.values()})==1 and original_energy==arms["no_first_lesion"].energy()
    assert all((x.rng.fingerprint(),x.rng.draws)==original_rng for x in arms.values())
    return arms,{"first_lesion_full_refund":cut,"energy_only_zero_bond_sham":sham,
                 "same_postfirst_lesion_and_energy_sham_particle_energy":True}


def summarize_arm(world,ids,edges,first_edge,second_edge):
    current=native_pairs(world)
    return {
        "first_original_ring_edge_present":first_edge in current,
        "second_precommitted_ring_edge_present":second_edge in current,
        "all_original_edges_present":edges.issubset(current),
        "original_ring_material_connected":coherent_root_size(world,ids) is not None,
        "original_ring_particle_energy":sum(world.store.energy[world.store.index_of(i)] for i in ids),
        "world_full_hash":world.state_hash_full(),
        "world_rng":world.rng.fingerprint(),"world_draws":world.rng.draws
    }


def follow(parent,ring,validate=False):
    edges=set(ring["edges"])
    ids=tuple(ring["ids"])
    assert len(edges)>=4
    first_edge,second_edge=sorted(edges)[:2]
    assert first_edge!=second_edge
    assert edges.issubset(native_pairs(parent))
    source_hash=parent.state_hash_full()
    source_rng=(parent.rng.fingerprint(),parent.rng.draws)
    copies,metadata=apply_first(parent,first_edge)
    tapes={a:EventTape() for a in ARMS}
    track={}
    for arm,w in copies.items():
        w.event_sink=tapes[arm]
        track[arm]={
            "first_initial_ring_cut":arm=="first_lesion",
            "first_original_target_native_FORM_tick":None,
            "first_phase_original_ring_edge_break_events":0,
            "first_t120":None,
            "second_target_present_at_t120":False,
            "second_target_chemically_cut_at_t120":False,
            "second_target_first_real_FORM_after_second_cut":None,
            "second_target_reclosed_before_any_OTHER_original_ring_break":False,
            "first_other_original_ring_BREAK_second_phase_tick":None,
            "native_exact_second_target_formation_events_second_phase":0,
            "all_original_ring_connected_at_t240":False,
            "exact_original_ring_closed_at_t240":False,
            "second_phase_another_edge_break_count":0,
            "checkpoints":[],
            "second_cut_full_refund":None
        }
    for t in range(1,FIRST_PHASE+SECOND_PHASE+1):
        if t==FIRST_PHASE+1:
            for arm,w in copies.items():
                h=track[arm]
                # This captures state at exactly t120 BEFORE second lesions.
                h["first_t120"]=summarize_arm(w,ids,edges,first_edge,second_edge)
                present=second_edge in native_pairs(w)
                h["second_target_present_at_t120"]=present
                old_total=(w.energy(),w.dissipated,w.rng.fingerprint(),w.rng.draws)
                if present:
                    h["second_cut_full_refund"]=excise_refund(w,second_edge)
                    h["second_target_chemically_cut_at_t120"]=True
                assert (w.energy(),w.dissipated,w.rng.fingerprint(),w.rng.draws)==old_total
                w.check()
                ledger(w,w.configured_energy())
        for arm,w in copies.items():
            w.advance(1)
            native_events=tapes[arm].pop(w.step)
            h=track[arm]
            if t<=FIRST_PHASE:
                if any(kind=="form" and pair==first_edge for kind,pair in native_events):
                    if h["first_original_target_native_FORM_tick"] is None:
                        h["first_original_target_native_FORM_tick"]=t
                h["first_phase_original_ring_edge_break_events"]+=sum(
                    1 for kind,pair in native_events if kind=="break" and pair in edges
                )
            else:
                relative=t-FIRST_PHASE
                other={pair for kind,pair in native_events if kind=="break" and pair in edges-{second_edge}}
                h["second_phase_another_edge_break_count"]+=sum(
                    1 for kind,pair in native_events if kind=="break" and pair in edges-{second_edge}
                )
                if other and h["first_other_original_ring_BREAK_second_phase_tick"] is None:
                    h["first_other_original_ring_BREAK_second_phase_tick"]=relative
                real_target=any(kind=="form" and pair==second_edge for kind,pair in native_events)
                if real_target:
                    h["native_exact_second_target_formation_events_second_phase"]+=1
                    if h["second_target_first_real_FORM_after_second_cut"] is None:
                        h["second_target_first_real_FORM_after_second_cut"]=relative
                    if (h["second_target_chemically_cut_at_t120"]
                            and h["first_other_original_ring_BREAK_second_phase_tick"] is None
                            and second_edge in native_pairs(w)):
                        h["second_target_reclosed_before_any_OTHER_original_ring_break"]=True
            energy_transfer(w,"bond_only")
            if t in CHECKPOINTS:
                w.check()
                ledger(w,w.configured_energy())
                snap=summarize_arm(w,ids,edges,first_edge,second_edge)
                snap["relative_tick_since_initial"]=t
                h["checkpoints"].append(snap)
    assert parent.state_hash_full()==source_hash
    assert (parent.rng.fingerprint(),parent.rng.draws)==source_rng
    for arm,w in copies.items():
        w.event_sink=None
        h=track[arm]
        assert h["first_t120"] is not None
        h["all_original_ring_connected_at_t240"]=coherent_root_size(w,ids) is not None
        h["exact_original_ring_closed_at_t240"]=edges.issubset(native_pairs(w))
        h["first_edge_present_at_t120"]=h["first_t120"]["first_original_ring_edge_present"]
        h["second_challenge_ITT_success"]=bool(h["second_target_chemically_cut_at_t120"]
                                              and h["second_target_reclosed_before_any_OTHER_original_ring_break"])
        h["second_challenge_and_connected_at_t240"]=bool(
            h["second_challenge_ITT_success"] and h["all_original_ring_connected_at_t240"])
        assert len(h["checkpoints"])==len(CHECKPOINTS)
        w.check()
        ledger(w,w.configured_energy())
        h["final"]={"full_hash":w.state_hash_full(),"rng":w.rng.fingerprint(),
                    "draws":w.rng.draws,"energy":w.energy(),
                    "injected":w.injected,"unabsorbed":w.unabsorbed,
                    "dissipated":w.dissipated,"formed":w.bonds_formed_total,
                    "broken":w.bonds_broken_total}
        if not h["second_target_chemically_cut_at_t120"]:
            assert h["second_challenge_ITT_success"] is False
    if validate:
        final=track["no_first_lesion"]
        # The untreated reference is cut ONLY at t120 when second edge exists;
        # replay the complete alternative native path, including that cut.
        shadow=clone_world(parent)
        for t in range(1,241):
            if t==121 and second_edge in native_pairs(shadow):
                excise_refund(shadow,second_edge)
            shadow.advance(1)
            energy_transfer(shadow,"bond_only")
        assert shadow.state_hash_full()==final["final"]["full_hash"]
        assert (shadow.rng.fingerprint(),shadow.rng.draws)==(final["final"]["rng"],final["final"]["draws"])
    return {"first_original_cut_ID_pair":list(first_edge),
            "second_original_precommitted_distinct_cut_ID_pair":list(second_edge),
            "t0_intervention_energy_metadata":metadata,
            "arms":track}


def run_one(seed,verify=False):
    parent,ring,scan=scan_first_native_aged_ring(seed)
    if ring is None:return {"seed":seed,"selected":False,"scan":scan}
    src=(parent.state_hash_full(),parent.rng.fingerprint(),parent.rng.draws)
    outcome=follow(parent,ring,validate=verify)
    assert (parent.state_hash_full(),parent.rng.fingerprint(),parent.rng.draws)==src
    return {
        "seed":seed,"selected":True,
        "scan":scan,
        "native_first_aged_ring":{"ids":list(ring["ids"]),"edges":[list(x) for x in ring["edges"]],
                                  "size":ring["size"],"age":ring["continuous_snapshot_age"]},
        "original_source_full_hash":src[0],"original_source_rng":src[1],
        "original_source_rng_draws":src[2],
        **outcome
    }


def paired(rows,control):
    count={"experienced_only":0,"control_only":0,"both":0,"neither":0}
    for r in rows:
        a=bool(r["arms"]["first_lesion"]["second_challenge_ITT_success"])
        b=bool(r["arms"][control]["second_challenge_ITT_success"])
        if a and not b:count["experienced_only"]+=1
        elif b and not a:count["control_only"]+=1
        elif a and b:count["both"]+=1
        else:count["neither"]+=1
    count["discordant"]=count["experienced_only"]+count["control_only"]
    count["favor_experienced_fraction"]=round(count["experienced_only"]/count["discordant"],6) if count["discordant"] else None
    assert sum(count[x] for x in ("experienced_only","control_only","both","neither"))==len(rows)
    return count


def summarize(rows):
    assert len(rows)==640 and [x["seed"] for x in rows]==list(range(FIRST,LAST+1))
    sample=[x for x in rows if x["selected"]]
    n=len(sample)
    p=paired(sample,"no_first_lesion")
    s=paired(sample,"energy_only_first_sham")
    def gate(x):
        if n<40:return "not_met_insufficient_natural_rings"
        if x["discordant"]<25:return "not_met_insufficient_discordant_worlds"
        return "passed" if 3*x["experienced_only"]>=2*x["discordant"] else "not_met_favorable_fraction"
    def avg(xs):return round(sum(xs)/len(xs),5) if xs else None
    a={}
    for arm in ARMS:
        group=[r["arms"][arm] for r in sample]
        a[arm]={
            "all_eligible_native_ring_source_seeds":n,
            "second_original_target_present_and_cut_at_t120":sum(x["second_target_chemically_cut_at_t120"] for x in group),
            "missing_second_target_counted_ITT_failure":sum(not x["second_target_chemically_cut_at_t120"] for x in group),
            "second_original_pair_true_FORM_preother_break_ITT_success":sum(x["second_challenge_ITT_success"] for x in group),
            "success_AND_coherent_all_original_IDs_t240":sum(x["second_challenge_and_connected_at_t240"] for x in group),
            "all_original_ring_IDs_connected_t240":sum(x["all_original_ring_connected_at_t240"] for x in group),
            "exact_original_ring_closed_t240":sum(x["exact_original_ring_closed_at_t240"] for x in group),
            "first_original_edge_present_after_120_ticks":sum(x["first_edge_present_at_t120"] for x in group),
            "mean_native_exact_second_target_reclosure_tick_among_succeeded":avg([
                x["second_target_first_real_FORM_after_second_cut"] for x in group
                if x["second_challenge_ITT_success"]
            ])
        }
    return {
        "seed_worlds":640,"selected_naturally_aged_native_ring_worlds":n,"no_ring_worlds":640-n,
        "ring_sizes":dict(Counter(str(r["native_first_aged_ring"]["size"]) for r in sample)),
        "arms":a,
        "paired_second_challenge":{
            "preregistered_primary_first_lesion_vs_no_first_lesion":p,
            "preregistered_secondary_first_lesion_vs_energy_only_first_sham":s
        },
        "preregistered_decisions":{
            "first_damage_history_improves_second_native_recovery":gate(p),
            "first_topology_damage_beats_same_particle_energy_refund_sham":gate(s),
            "min_selected_worlds":40,
            "min_discordant_worlds":25,
            "required_favorable_fraction":"2/3",
            "ITT_all_absent_second_targets_counted_as_failures":True,
            "not_evidence_of_learning_or_active_repair":True
        },
        "limitation":"After t0 first intervention, normal M6 chemistry and RNG may diverge, and initial first damage is not identical to energy-only sham in topology or valence. A post-second-damage improvement could be passive survivor composition or changed energy/geometry, not adaptive memory. The protocol includes ALL first-damage nonrecoverers as ITT, so selection-on-survivors is avoided."
    }


def run_shard(start,end):
    p=protocol()
    d={"start":start,"end":end}
    assert d in p["sample"]["shards"]
    rows=[]
    first=None
    for seed in range(start,end+1):
        r=run_one(seed,verify=first is None)
        rows.append(r)
        if r["selected"] and first is None:first=seed
        if (seed-start+1)%10==0:
            print(f"M713_PROGRESS {start}-{end}: {seed} native_ring={sum(x['selected'] for x in rows)}",flush=True)
    chunk={"schema":"alife-m7-13-shard-v1","descriptor":d,
           "provenance":provenance(),"first_selected_unmodified_M6_replay":first,
           "worlds":rows}
    path=BASE/"shards"/f"{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(chunk,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M713_SHARD="+json.dumps({"start":start,"end":end,"sources":len(rows),"rings":sum(x["selected"] for x in rows)},sort_keys=True),flush=True)


def merge():
    p=protocol()
    paths=list((BASE/"shards").glob("*.json"))
    assert len(paths)==16
    seen=[]
    rows=[]
    for path in paths:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m7-13-shard-v1"
        assert chunk["provenance"]==provenance()
        d=chunk["descriptor"]
        assert d in p["sample"]["shards"] and d not in seen
        seen.append(d)
        assert [r["seed"] for r in chunk["worlds"]]==list(range(d["start"],d["end"]+1))
        assert chunk["first_selected_unmodified_M6_replay"]==next((r["seed"] for r in chunk["worlds"] if r["selected"]),None)
        rows+=chunk["worlds"]
    assert all(d in seen for d in p["sample"]["shards"])
    rows.sort(key=lambda r:r["seed"])
    result={"schema":"alife-m7-13-640-native-ring-experience-v1",
            "provenance":provenance(),"worlds":rows,"summary":summarize(rows),
            "all_640_seed_worlds_16_fixed_shards_and_nulls":True}
    DATA.parent.mkdir(parents=True,exist_ok=True)
    DATA.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M713_FINAL_SUMMARY="+json.dumps(result["summary"],sort_keys=True),flush=True)
    print("M713_SUCCESS=640",flush=True)


def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    sh=sub.add_parser("shard")
    sh.add_argument("--start",type=int,required=True)
    sh.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    args=p.parse_args()
    if args.cmd=="shard":run_shard(args.start,args.end)
    else:merge()


if __name__=="__main__":main()
