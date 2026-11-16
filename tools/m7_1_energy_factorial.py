"""M7.1 — preregistered energy-driven native chemistry, four-arm factorial study.

This is a NEW CONFIGURATION REGIME of existing M3/M6 validated physics, NOT
a new engine and NOT a codepath added to historical M6 physical evolution.
No rings or organisms are placed; all bonds start absent and form naturally.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.config import Config
from alife.structures import components
from alife.world import World
from tools.m6_4_cycles import M6
from tools.m6_12_precursors import precursor_candidates

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_1_energy"
PROTOCOL=BASE/"protocol.json"
OUTPUT=BASE/"merged_results.json"
ARMS=("closed_no_catalysis","driven_no_catalysis","closed_catalysis","driven_catalysis")
CHECKPOINTS=(0,100,200,400,500,600)
LATE_START=500
HORIZON=600


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-1-open-energy-local-catalysis-factorial-v1"
    assert p["status"]=="preregistered_before_code_and_outcomes"
    assert p["sample"]["seeds"]=={"start":18001,"end_inclusive":18080,"count":80}
    assert p["sample"]["total_worlds"]==320
    assert p["sample"]["factorial_arms"]==list(ARMS)
    assert len(p["sample"]["frozen_shards"])==4
    assert p["sample"]["horizon_ticks"]==HORIZON
    return p


def make_config(seed, arm, p=None):
    p=p if p is not None else protocol()
    assert arm in ARMS
    native=json.loads(M6.read_text(encoding="utf-8"))
    native["seed"]=seed
    native["grid"]=dict(p["sample"]["grid"])
    for spec in native["species"]:
        spec["count"]=p["sample"]["counts"][spec["name"]]
    native["energy"]["movement_cost"]=p["physical_config"]["movement_cost_all_arms"]
    driven=arm.startswith("driven_")
    cat=arm.endswith("_catalysis") and not arm.endswith("no_catalysis")
    if driven:
        spec=p["physical_config"]["driven_sources"]
        native["energy"]["sources"]=[
            {"x":x,"y":y,"rate_num":spec["each_rate_num"],
             "rate_den":spec["each_rate_den"],
             "capacity":spec["each_capacity"],"overflow":spec["overflow"]}
            for y in spec["coordinates_y"] for x in spec["coordinates_x"]
        ]
    else:
        native["energy"]["sources"]=[]
    native["chemistry"]["catalysis"]=(
        [dict(p["physical_config"]["catalysis_enabled_rule"])]
        if cat else []
    )
    config=Config.from_dict(native).validate()
    assert len(config.energy.sources)==(16 if driven else 0)
    assert len(config.chemistry.catalysis)==(1 if cat else 0)
    assert sum(s.count for s in config.species)==264
    assert config.energy.movement_cost==1
    return config


def source_features(world):
    s=world.store
    viable=sum(
        deg==0 and s.energy[i]>=world.movement_cost
        and world.config.species[s.species[i]].move_probability>0
        for i,deg in enumerate(s.degree)
    )
    zero_energy=sum(en==0 for en in s.energy)
    return {
        "free_mobile_energy_eligible":viable,
        "particles_at_zero_energy":zero_energy,
        "bonded_particles":sum(deg>0 for deg in s.degree),
        "source_stored_energy":world.energy_sources()
    }


def describe_native_topology(world):
    rings=0
    rings4=0
    ring8=0
    for indices,bonds in components(world.store):
        if len(indices)>=4 and len(indices)==len(bonds) and all(
            world.store.degree[i]==2 for i in indices
        ):
            rings+=1
            if len(indices)==4:
                rings4+=1
            if len(indices)==8:
                ring8+=1
    # Exact lattice 7-edge perimeters, not planted in the starting state.
    precursors=precursor_candidates(world)
    return {
        "native_simple_ring_components":rings,
        "native_four_ring_components":rings4,
        "native_eight_ring_components":ring8,
        "native_seven_edge_3x3_precursors":len(precursors),
        "native_seven_edge_with_mobile_resident":sum(
            x["resident_mobile"] for x in precursors)
    }


def ledger(world,initial):
    # Includes energy in particle stores, bonds and source buffers.
    # unabsorbed overflow is an external energy sink not in 'dissipated'.
    stored=world.energy()
    spent=world.dissipated
    rejected=world.unabsorbed
    supplied=world.injected
    assert stored+spent+rejected==initial+supplied,(
        "M7.1 energy ledger failed",world.step,stored,spent,rejected,
        initial,supplied
    )
    return {
        "stored_energy":stored,
        "dissipated":spent,
        "unabsorbed":rejected,
        "injected":supplied,
        "energy_ledger_verified":True
    }


def snapshot(world,initial):
    return {
        "tick":world.step,
        "moves_cumulative":world.moves_total,
        "formed_cumulative":world.bonds_formed_total,
        "broken_cumulative":world.bonds_broken_total,
        **ledger(world,initial),
        **source_features(world)
    }


def sample_world(seed,arm,p=None):
    p=p if p is not None else protocol()
    w=World.create(make_config(seed,arm,p))
    assert w.step==0 and not w.store.bonds
    initial=w.configured_energy()
    assert w.energy()==initial
    start_ids=tuple(w.store.ids)
    start_positions=tuple(zip(w.store.xs,w.store.ys))
    start_species=tuple(w.store.species)
    start_energy=tuple(w.store.energy)
    rng_start=w.rng.fingerprint()
    start_draws=w.rng.draws
    readings={0:snapshot(w,initial)}
    for tick in range(1,HORIZON+1):
        w.advance(1)
        if tick in CHECKPOINTS:
            readings[tick]=snapshot(w,initial)
            w.check()
    assert sorted(readings)==list(CHECKPOINTS)
    assert w.step==HORIZON
    assert tuple(w.store.ids)==start_ids
    assert w.energy()+w.dissipated+w.unabsorbed==initial+w.injected
    late={
        "accepted_moves":readings[600]["moves_cumulative"]-readings[500]["moves_cumulative"],
        "new_native_bonds":readings[600]["formed_cumulative"]-readings[500]["formed_cumulative"],
        "native_bonds_broken":readings[600]["broken_cumulative"]-readings[500]["broken_cumulative"],
        "energy_injected":readings[600]["injected"]-readings[500]["injected"]
    }
    early={
        "accepted_moves":readings[100]["moves_cumulative"],
        "new_native_bonds":readings[100]["formed_cumulative"],
        "native_bonds_broken":readings[100]["broken_cumulative"],
        "energy_injected":readings[100]["injected"]
    }
    result={
        "seed":seed,"arm":arm,
        "initial_state":{
            "particles":len(start_ids),
            "positions_species_energy_sha256":sha256(json.dumps(
                [start_ids,start_positions,start_species,start_energy],
                separators=(",",":")).encode()).hexdigest(),
            "rng":rng_start,"rng_draws":start_draws,
            "initial_stored_energy":initial
        },
        "checkpoints":[readings[t] for t in CHECKPOINTS],
        "early_1_100":early,
        "late_501_600":late,
        "final_topology":describe_native_topology(w),
        "final":{
            "full_hash":w.state_hash_full(),
            "rng":w.rng.fingerprint(),
            "draws":w.rng.draws,
            "stored_energy":w.energy(),
            "injected":w.injected,
            "dissipated":w.dissipated,
            "unabsorbed":w.unabsorbed,
            "moves":w.moves_total,
            "formed":w.bonds_formed_total,
            "broken":w.bonds_broken_total,
        }
    }
    return result


def replay(record,p=None):
    p=p if p is not None else protocol()
    world=World.create(make_config(record["seed"],record["arm"],p))
    assert world.rng.fingerprint()==record["initial_state"]["rng"]
    assert world.rng.draws==record["initial_state"]["rng_draws"]
    world.advance(HORIZON)
    world.check()
    fin=record["final"]
    assert world.state_hash_full()==fin["full_hash"]
    assert world.rng.fingerprint()==fin["rng"]
    assert world.rng.draws==fin["draws"]
    assert world.energy()==fin["stored_energy"]
    assert world.injected==fin["injected"]
    assert world.dissipated==fin["dissipated"]
    assert world.unabsorbed==fin["unabsorbed"]
    assert world.moves_total==fin["moves"]
    assert world.bonds_formed_total==fin["formed"]
    assert world.bonds_broken_total==fin["broken"]
    return {"seed":record["seed"],"arm":record["arm"],
            "bare_replay_full_hash":fin["full_hash"],"success":True}


def paired_summary(worlds,p):
    rows=sorted(worlds,key=lambda x:(x["seed"],x["arm"]))
    index={(r["seed"],r["arm"]):r for r in rows}
    expected={(seed,arm) for seed in range(18001,18081) for arm in ARMS}
    assert len(rows)==320 and len(index)==320 and set(index)==expected
    for seed in range(18001,18081):
        pack=[index[(seed,a)] for a in ARMS]
        assert len({x["initial_state"]["positions_species_energy_sha256"] for x in pack})==1
        assert len({x["initial_state"]["rng"] for x in pack})==1
        assert len({x["initial_state"]["rng_draws"] for x in pack})==1
    arms={}
    for arm in ARMS:
        sub=[index[(seed,arm)] for seed in range(18001,18081)]
        def avg(v):
            return round(sum(v)/len(v),3)
        arms[arm]={
            "worlds":len(sub),
            "late_100_mean_accepted_moves":avg([r["late_501_600"]["accepted_moves"] for r in sub]),
            "late_100_moving_worlds":sum(r["late_501_600"]["accepted_moves"]>0 for r in sub),
            "late_100_mean_new_native_bonds":avg([r["late_501_600"]["new_native_bonds"] for r in sub]),
            "late_100_bond_forming_worlds":sum(r["late_501_600"]["new_native_bonds"]>0 for r in sub),
            "mean_energy_injected_total":avg([r["final"]["injected"] for r in sub]),
            "mean_total_energy_final":avg([r["final"]["stored_energy"] for r in sub]),
            "mean_total_moves":avg([r["final"]["moves"] for r in sub]),
            "final_worlds_with_native_ring":sum(r["final_topology"]["native_simple_ring_components"]>0 for r in sub)
        }
    contrasts={}
    comparisons=[
        ("energy_no_catalysis","driven_no_catalysis","closed_no_catalysis"),
        ("energy_with_catalysis","driven_catalysis","closed_catalysis"),
        ("catalysis_closed","closed_catalysis","closed_no_catalysis"),
        ("catalysis_driven","driven_catalysis","driven_no_catalysis")
    ]
    for name,a,b in comparisons:
        stats={}
        for period,key in (("early_1_100","accepted_moves"),
                           ("early_bonds_1_100","new_native_bonds"),
                           ("late_501_600","accepted_moves"),
                           ("late_bonds_501_600","new_native_bonds")):
            field=("early_1_100" if period.startswith("early") else "late_501_600")
            v1=key if not period.endswith("_bonds_1_100") and not period.endswith("_bonds_501_600") else "new_native_bonds"
            if "bonds" in period:
                v1="new_native_bonds"
            else:
                v1="accepted_moves"
            differences=[
                index[(seed,a)][field][v1]-index[(seed,b)][field][v1]
                for seed in range(18001,18081)
            ]
            stats[period]={
                "paired_mean_difference":round(sum(differences)/80,3),
                "seeds_raised":sum(x>0 for x in differences),
                "seeds_tied":sum(x==0 for x in differences),
                "seeds_lowered":sum(x<0 for x in differences)
            }
        contrasts[name]=stats
    primary=contrasts["energy_no_catalysis"]["late_501_600"]["seeds_raised"]>=60 and arms["driven_no_catalysis"]["late_100_moving_worlds"]>=60
    chemistry=contrasts["energy_no_catalysis"]["late_bonds_501_600"]["seeds_raised"]>=48
    return {
        "independent_paired_numeric_seeds":80,"total_worlds":320,
        "per_arm":arms,"paired_contrasts":contrasts,
        "preregistered_decisions":{
            "sustained_driven_mobility":("passed" if primary else "not_met"),
            "late_chemical_turnover_benefit":("passed" if chemistry else "not_met"),
            "none_of_these_is_life_evidence":True,
            "thresholds_preserved":{"mobility_seed_advantage_min":60,
                                    "driven_worlds_with_late_moves_min":60,
                                    "new_bond_seed_advantage_min":48}
        },
        "caveat":"Same-seed arms have same starting particles but RNG streams diverge under different dynamics; differences in energy input, catalysis and random schedule are whole-regime treatment effects. Native rings descriptive only, NO heredity or reproduction test."
    }


def run_shard(start,end):
    p=protocol()
    target={"start":start,"end":end}
    assert target in p["sample"]["frozen_shards"]
    rows=[]
    replays=[]
    for seed in range(start,end+1):
        pack=[sample_world(seed,arm,p) for arm in ARMS]
        assert len({r["initial_state"]["positions_species_energy_sha256"] for r in pack})==1
        assert len({r["initial_state"]["rng"] for r in pack})==1
        assert len({r["initial_state"]["rng_draws"] for r in pack})==1
        rows.extend(pack)
        if seed==start:
            replays.extend(replay(row,p) for row in pack)
        if (seed-start+1)%5==0:
            print(f"M71_PROGRESS {start}-{end} seed={seed} worlds={len(rows)}",flush=True)
    assert len(rows)==(end-start+1)*4
    chunk={
        "schema":"alife-m7-1-four-arm-shard-v1",
        "shard":target,
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":rows,"bare_replays":replays,
        "no_original_M6_engine_changes":True
    }
    path=BASE/"shards"/f"seeds-{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(chunk,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M71_SHARD="+json.dumps({"start":start,"end":end,"worlds":len(rows),"replays":len(replays)},sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("*.json"))
    assert len(files)==4,(len(files),files)
    all_rows=[]
    all_replays=[]
    seen=[]
    for path in files:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m7-1-four-arm-shard-v1"
        assert chunk["protocol_sha256"]==sha256(PROTOCOL.read_bytes()).hexdigest()
        assert chunk["no_original_M6_engine_changes"] is True
        d=chunk["shard"]
        assert d in p["sample"]["frozen_shards"] and d not in seen
        seen.append(d)
        expected={(seed,arm) for seed in range(d["start"],d["end"]+1) for arm in ARMS}
        actual={(r["seed"],r["arm"]) for r in chunk["worlds"]}
        assert len(actual)==len(chunk["worlds"]) and expected==actual
        assert len(chunk["bare_replays"])==4
        assert all(x["seed"]==d["start"] and x["success"] is True for x in chunk["bare_replays"])
        all_rows+=chunk["worlds"]
        all_replays+=chunk["bare_replays"]
    assert all(d in seen for d in p["sample"]["frozen_shards"])
    summary=paired_summary(all_rows,p)
    out={
        "schema":"alife-m7-1-complete-four-arm-results-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "total_worlds":len(all_rows),
        "paired_numeric_seeds":80,
        "worlds":sorted(all_rows,key=lambda r:(r["seed"],r["arm"])),
        "replays":all_replays,
        "summary":summary,
        "complete_four_shard_coverage":True,
        "original_M6_core_unchanged":True
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("M71_FINAL_SUMMARY="+json.dumps(summary,sort_keys=True),flush=True)
    print("M71_SUCCESS="+str(len(all_rows)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)
    s=sub.add_parser("shard")
    s.add_argument("--start",type=int,required=True)
    s.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    args=parser.parse_args()
    if args.command=="shard":
        run_shard(args.start,args.end)
    else:
        merge()


if __name__=="__main__":
    main()
