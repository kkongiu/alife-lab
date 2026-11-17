"""Independent same-640-world M7.13 fully physical posthoc implementation audit.

Rebuild same M7.11 natural original aged ring from numeric seed. This file
DOES NOT call M7.13 first lesion treatment, zero-bond-energy sham, full
followup, native event observer, or original study outcome classifiers.
Implement own native bond refund and transient zero-bond-energy intervention;
use original World.advance(1) and original M7.3 energy_transfer for ALL
branches. Inspect native original M6 BondEvents via independent observer.
Replay all 627*3=1881 full 240-tick physical histories, not new samples.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_2_energy_distribution import ledger
from tools.m7_11_ring_fault_tolerance import scan_first_native_aged_ring
from tools.m7_5_posthoc_independent_replay import (
    IndependentEvents,source_component_size_from_scratch
)

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_13_history"
RAW=BASE/"results.json"
ARMS=("first_lesion","energy_only_first_sham","no_first_lesion")
TIMES=(1,30,60,120,121,150,180,240)
FIRST,LAST=31001,31640


def native_ids_of_edges(w):
    s=w.store
    return {tuple(sorted((s.ids[a],s.ids[b]))) for a,b in s.bonds}


def independent_refund(w,pair,keep_bond=False):
    s=w.store
    i,j=sorted((s.index_of(x) for x in pair))
    k=(i,j)
    assert k in s.bonds
    prior=(w.energy(),w.dissipated,w.rng.fingerprint(),w.rng.draws)
    stored=s.bonds[k]
    if keep_bond:
        s.bonds[k]=0
    else:
        s.remove_bond(*k)
    s.energy[i]+=stored-stored//2
    s.energy[j]+=stored//2
    assert (w.energy(),w.dissipated,w.rng.fingerprint(),w.rng.draws)==prior
    w.check()
    ledger(w,w.configured_energy())
    return stored


def physical_info(w,ids,original,first,second):
    now=native_ids_of_edges(w)
    return {
        "first_original_ring_edge_present":first in now,
        "second_precommitted_ring_edge_present":second in now,
        "all_original_edges_present":original.issubset(now),
        "original_ring_material_connected":source_component_size_from_scratch(w,ids) is not None,
        "original_ring_particle_energy":sum(w.store.energy[w.store.index_of(i)] for i in ids),
        "world_full_hash":w.state_hash_full(),
        "world_rng":w.rng.fingerprint(),
        "world_draws":w.rng.draws
    }


def physical_replay(parent,ring,raw):
    ids=tuple(ring["ids"])
    originals=set(ring["edges"])
    first,second=sorted(originals)[:2]
    assert first!=second
    assert list(first)==raw["first_original_cut_ID_pair"]
    assert list(second)==raw["second_original_precommitted_distinct_cut_ID_pair"]
    worlds={a:clone_world(parent) for a in ARMS}
    assert len({w.state_hash_full() for w in worlds.values()})==1
    oldtotal=parent.energy()
    refunded=independent_refund(worlds["first_lesion"],first,False)
    shammed=independent_refund(worlds["energy_only_first_sham"],first,True)
    assert refunded==shammed==raw["t0_intervention_energy_metadata"]["first_lesion_full_refund"]["native_bond_energy_fully_refunded"]
    assert worlds["first_lesion"].store.energy==worlds["energy_only_first_sham"].store.energy
    assert all(w.energy()==oldtotal for w in worlds.values())
    tape={a:IndependentEvents() for a in ARMS}
    for a in ARMS:worlds[a].event_sink=tape[a]
    outcomes={}
    for a in ARMS:
        outcomes[a]={
            "first_t120":None,"second_cut":False,
            "first_formation_tick":None,"first_phase_breaks":0,
            "first_other_break_second":None,"second_prebreak_reformed":False,
            "second_first_form":None,"second_form_events":0,
            "second_other_breaks":0,
            "checkpoints":[]
        }
    for t in range(1,241):
        if t==121:
            for arm,w in worlds.items():
                h=outcomes[arm]
                h["first_t120"]=physical_info(w,ids,originals,first,second)
                assert h["first_t120"]==raw["arms"][arm]["first_t120"],(raw["seed"],arm,"t120")
                if second in native_ids_of_edges(w):
                    stored=independent_refund(w,second,False)
                    assert stored==raw["arms"][arm]["second_cut_full_refund"]["native_bond_energy_fully_refunded"]
                    h["second_cut"]=True
                else:
                    assert raw["arms"][arm]["second_cut_full_refund"] is None
                assert h["second_cut"]==raw["arms"][arm]["second_target_chemically_cut_at_t120"]
        for arm,w in worlds.items():
            w.advance(1)
            events=tape[arm].events(w.step)
            h=outcomes[arm]
            if t<=120:
                if h["first_formation_tick"] is None and any(kind=="form" and edge==first for kind,edge in events):
                    h["first_formation_tick"]=t
                h["first_phase_breaks"]+=sum(kind=="break" and edge in originals for kind,edge in events)
            else:
                t2=t-120
                other_breaks=sum(kind=="break" and edge in originals-{second} for kind,edge in events)
                h["second_other_breaks"]+=other_breaks
                if h["first_other_break_second"] is None and other_breaks:
                    h["first_other_break_second"]=t2
                for kind,edge in events:
                    if kind=="form" and edge==second:
                        h["second_form_events"]+=1
                        if h["second_first_form"] is None:h["second_first_form"]=t2
                        if h["second_cut"] and h["first_other_break_second"] is None and second in native_ids_of_edges(w):
                            h["second_prebreak_reformed"]=True
            energy_transfer(w,"bond_only")
            if t in TIMES:
                data=physical_info(w,ids,originals,first,second)
                data["relative_tick_since_initial"]=t
                h["checkpoints"].append(data)
                raw_data=raw["arms"][arm]["checkpoints"][len(h["checkpoints"])-1]
                assert data==raw_data,(raw["seed"],arm,t,"physical checkpoint")
                w.check()
                ledger(w,w.configured_energy())
    for arm,w in worlds.items():
        obs=raw["arms"][arm]
        h=outcomes[arm]
        assert len(h["checkpoints"])==8
        assert h["first_formation_tick"]==obs["first_original_target_native_FORM_tick"]
        assert h["first_phase_breaks"]==obs["first_phase_original_ring_edge_break_events"]
        assert h["first_other_break_second"]==obs["first_other_original_ring_BREAK_second_phase_tick"]
        assert h["second_prebreak_reformed"]==obs["second_target_reclosed_before_any_OTHER_original_ring_break"]
        assert h["second_form_events"]==obs["native_exact_second_target_formation_events_second_phase"]
        assert h["second_other_breaks"]==obs["second_phase_another_edge_break_count"]
        assert h["second_first_form"]==obs["second_target_first_real_FORM_after_second_cut"]
        assert h["second_cut"]==obs["second_target_present_at_t120"]
        assert (h["second_cut"] and h["second_prebreak_reformed"])==obs["second_challenge_ITT_success"]
        assert obs["all_original_ring_connected_at_t240"]==(source_component_size_from_scratch(w,ids) is not None)
        assert obs["exact_original_ring_closed_at_t240"]==originals.issubset(native_ids_of_edges(w))
        assert obs["first_edge_present_at_t120"]==h["first_t120"]["first_original_ring_edge_present"]
        assert (obs["second_challenge_ITT_success"] and obs["all_original_ring_connected_at_t240"])==obs["second_challenge_and_connected_at_t240"]
        f=obs["final"]
        assert f["full_hash"]==w.state_hash_full(),(raw["seed"],arm,"full hash")
        assert f["rng"]==w.rng.fingerprint() and f["draws"]==w.rng.draws
        assert f["energy"]==w.energy()
        assert f["injected"]==w.injected
        assert f["unabsorbed"]==w.unabsorbed
        assert f["dissipated"]==w.dissipated
        assert f["formed"]==w.bonds_formed_total and f["broken"]==w.bonds_broken_total
        w.check()
        ledger(w,w.configured_energy())
    return True


def audit_shard(start,end):
    assert start in range(FIRST,LAST+1,40) and end==start+39
    data=json.loads(RAW.read_text(encoding="utf-8"))
    assert data["schema"]=="alife-m7-13-640-native-ring-experience-v1"
    assert data["all_640_seed_worlds_16_fixed_shards_and_nulls"]
    allrows=data["worlds"]
    assert len(allrows)==640 and [r["seed"] for r in allrows]==list(range(FIRST,LAST+1))
    rows=allrows[start-FIRST:end-FIRST+1]
    assert len(rows)==40
    positive=0
    records=Counter()
    for i,r in enumerate(rows):
        w,ring,sc=scan_first_native_aged_ring(r["seed"])
        assert r["selected"]==(ring is not None)
        assert sc==r["scan"],(r["seed"],"selection metadata")
        if ring is None:
            records["nulls"]+=1
        else:
            positive+=1
            assert w.state_hash_full()==r["original_source_full_hash"]
            assert (w.rng.fingerprint(),w.rng.draws)==(r["original_source_rng"],r["original_source_rng_draws"])
            assert list(ring["ids"])==r["native_first_aged_ring"]["ids"]
            assert [list(e) for e in ring["edges"]]==r["native_first_aged_ring"]["edges"]
            assert physical_replay(w,ring,r)
            records["forks"]+=3
            for arm in ARMS:
                records[arm+"_success"]+=bool(r["arms"][arm]["second_challenge_ITT_success"])
                records[arm+"_eligible_target"]+=bool(r["arms"][arm]["second_target_chemically_cut_at_t120"])
        if (i+1)%10==0:
            print(f"M713_POSTHOC_PROGRESS {start}-{end} checked={i+1}/40",flush=True)
    output={"schema":"alife-m7-13-independent-physical-shard-v1",
            "descriptor":{"start":start,"end":end},
            "native_sources":40,"selected_original_rings":positive,
            "null_original_worlds":40-positive,
            "forks_fully_replayed":records["forks"],
            "per_arm_success_and_eligibility":{arm:{
                "success":records[arm+"_success"],
                "eligible":records[arm+"_eligible_target"]} for arm in ARMS},
            "complete_original_M6_M73_hash_RNG_bond_event_and_energy_replay":True,
            "same_frozen_primary_seeds_no_new_sampling":True}
    path=BASE/"independent_shards"/f"{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("M713_POSTHOC_SHARD="+json.dumps(output,sort_keys=True),flush=True)


def audit_merge():
    files=list((BASE/"independent_shards").glob("*.json"))
    assert len(files)==16
    seen=set()
    total=Counter()
    for f in files:
        r=json.loads(f.read_text(encoding="utf-8"))
        d=r["descriptor"]
        assert r["schema"]=="alife-m7-13-independent-physical-shard-v1"
        assert d["start"] in range(FIRST,LAST+1,40) and d["end"]==d["start"]+39
        assert d["start"] not in seen
        seen.add(d["start"])
        assert r["native_sources"]==40
        assert r["forks_fully_replayed"]==3*r["selected_original_rings"]
        assert r["complete_original_M6_M73_hash_RNG_bond_event_and_energy_replay"]
        total.update({"worlds":40,"selected":r["selected_original_rings"],
                      "null":r["null_original_worlds"],"forks":r["forks_fully_replayed"]})
        for arm,data in r["per_arm_success_and_eligibility"].items():
            total[arm+"_success"]+=data["success"]
            total[arm+"_eligible"]+=data["eligible"]
    assert len(seen)==16
    assert total["worlds"]==640 and total["selected"]==627 and total["null"]==13 and total["forks"]==1881,total
    assert [total[a+"_success"] for a in ARMS]==[366,421,399],total
    assert [total[a+"_eligible"] for a in ARMS]==[566,583,577],total
    output={
        "schema":"alife-m7-13-complete-independent-native-physical-audit-v1",
        "all_640_source_worlds_rebuilt_from_original_M711_selector":True,
        "all_627_first_naturally_aged_rings_reproduced":True,
        "all_13_nulls_retained":True,
        "all_1881_threearm_full_240step_native_M6_M73_forks_exact_match":True,
        "all_real_bond_FORM_BREAK_events_and_frozen_ITT_outcomes_verified":True,
        "all_physics_full_hashes_rng_draws_and_energy_ledgers_match":True,
        "original_M713_intervention_and_observers_not_used":True,
        "same_original_640_worlds_not_additional_statistical_replication":True,
        "preregistered_gates_unchanged":True,
        "counts":dict(total)
    }
    target=BASE/"posthoc_independent_1881_forks.json"
    target.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("M713_POSTHOC_FINAL="+json.dumps(output,sort_keys=True),flush=True)


def main():
    ap=argparse.ArgumentParser()
    cmd=ap.add_subparsers(dest="cmd",required=True)
    sh=cmd.add_parser("shard")
    sh.add_argument("--start",type=int,required=True)
    sh.add_argument("--end",type=int,required=True)
    cmd.add_parser("merge")
    x=ap.parse_args()
    if x.cmd=="shard":audit_shard(x.start,x.end)
    else:audit_merge()


if __name__=="__main__":main()
