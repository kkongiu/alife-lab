"""M7.3: preregistered native chemical bonds as energy conduction paths.

All three arms use identical native M7.2 dispersed-source physics and starting
states. The optional conduction pass is implemented HERE after a native step.
No retroactive M6/M7.1/M7.2 law edits, no artificial bonds or replicators.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from alife.world import World
from tools.m7_2_energy_distribution import (
    config_for as m72_config, contacts, gini_nonnegative, ledger,
)
from tools.m7_1_energy_factorial import describe_native_topology, source_features

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_3_bond_energy"
PROTOCOL=BASE/"protocol.json"
OUTPUT=BASE/"results.json"
ARMS=("no_transfer","bond_only","all_contacts")
CHECKPOINTS=(0,100,200,400,500,600)
HORIZON=600


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-3-bond-only-vs-contact-energy-transport-v1"
    assert p["status"]=="preregistered_before_code_and_results"
    assert (p["design"]["seed_first"],p["design"]["seed_last"])==(20001,20100)
    assert p["design"]["worlds"]==300
    assert p["design"]["arms"]==list(ARMS)
    assert len(p["design"]["shards"])==4
    return p


def config_for(seed,arm):
    assert arm in ARMS
    # Exactly identical to M7.2 dispersed_no_transfer config for this seed.
    return m72_config(seed,"dispersed_no_transfer")


def bond_pairs(world):
    s=world.store
    return sorted(
        s.bonds,
        key=lambda pair:(
            min(s.ids[pair[0]],s.ids[pair[1]]),
            max(s.ids[pair[0]],s.ids[pair[1]])
        )
    )


def energy_transfer(world,arm):
    """(total, along_original_bonds, across_unbonded_contacts), all RNG-free.

    Snapshot gradient; accept a one-unit proposal in fixed material-id order
    if donor has remaining energy, then apply all delta values together.
    """
    assert arm in ARMS
    if arm=="no_transfer":
        return (0,0,0)
    s=world.store
    old_rng=world.rng.fingerprint()
    old_draws=world.rng.draws
    old_energy=world.energy()
    old_particle_energy=sum(s.energy)
    snapshot_energy=tuple(s.energy)
    remaining=list(snapshot_energy)
    delta=[0]*len(snapshot_energy)
    native_bonds=set(s.bonds)
    candidates=bond_pairs(world) if arm=="bond_only" else contacts(s)
    total=bonded=nonbonded=0
    for i,j in candidates:
        if snapshot_energy[i]-snapshot_energy[j]>=2:
            donor,recipient=i,j
        elif snapshot_energy[j]-snapshot_energy[i]>=2:
            donor,recipient=j,i
        else:
            continue
        if remaining[donor]<1:
            continue
        remaining[donor]-=1
        delta[donor]-=1
        delta[recipient]+=1
        total+=1
        if (i,j) in native_bonds or (j,i) in native_bonds:
            bonded+=1
        else:
            nonbonded+=1
    for i,d in enumerate(delta):
        if d:
            s.energy[i]+=d
            assert s.energy[i]>=0
    assert total==bonded+nonbonded
    if arm=="bond_only":
        assert nonbonded==0
    assert sum(s.energy)==old_particle_energy
    assert world.energy()==old_energy
    assert world.rng.fingerprint()==old_rng and world.rng.draws==old_draws
    return total,bonded,nonbonded


def checkpoint(w,initial,totals):
    ledger(w,initial)
    s=w.store
    bonded_indices=[i for i,d in enumerate(s.degree) if d>0]
    free_indices=[i for i,d in enumerate(s.degree) if d==0]
    return {
        "tick":w.step,
        "stored":w.energy(),
        "injected":w.injected,
        "dissipated":w.dissipated,
        "unabsorbed":w.unabsorbed,
        "particle_energy":w.energy_particles(),
        "bond_energy":w.energy_bonds(),
        "source_energy":w.energy_sources(),
        "zero_energy_particles":sum(e==0 for e in s.energy),
        "gini":gini_nonnegative(s.energy),
        "bonded_particle_count":len(bonded_indices),
        "free_particle_count":len(free_indices),
        "energy_in_bonded_particles":sum(s.energy[i] for i in bonded_indices),
        "energy_in_free_particles":sum(s.energy[i] for i in free_indices),
        "mean_energy_per_bonded_particle":round(
            sum(s.energy[i] for i in bonded_indices)/len(bonded_indices),4)
            if bonded_indices else None,
        "mean_energy_per_free_particle":round(
            sum(s.energy[i] for i in free_indices)/len(free_indices),4)
            if free_indices else None,
        "moves":w.moves_total,
        "formed":w.bonds_formed_total,
        "broken":w.bonds_broken_total,
        "transfers":totals[0],
        "transfers_along_bonds":totals[1],
        "transfers_across_nonbonded_contacts":totals[2],
        **source_features(w),
        "energy_ledger_verified":True
    }


def run_world(seed,arm):
    p=protocol()
    w=World.create(config_for(seed,arm))
    assert w.step==0 and not w.store.bonds
    initial=w.configured_energy()
    sig={
        "initial_particles_hash":sha256(json.dumps([
            w.store.ids,w.store.xs,w.store.ys,w.store.species,w.store.energy],
            separators=(",",":")).encode()).hexdigest(),
        "rng":w.rng.fingerprint(),
        "draws":w.rng.draws,
        "initial_energy":initial,
        "initial_bonds":len(w.store.bonds)
    }
    totals=[0,0,0]
    snaps={0:checkpoint(w,initial,totals)}
    for t in range(1,HORIZON+1):
        w.advance(1)
        values=energy_transfer(w,arm)
        for i,n in enumerate(values):
            totals[i]+=n
        if t in CHECKPOINTS:
            snaps[t]=checkpoint(w,initial,totals)
            w.check()
    assert sorted(snaps)==list(CHECKPOINTS)
    assert w.injected==19200
    assert sum(totals[1:])==totals[0]
    ledger(w,initial)
    a,b=snaps[500],snaps[600]
    final={
        "full_hash":w.state_hash_full(),
        "rng":w.rng.fingerprint(),"draws":w.rng.draws,
        "stored":w.energy(),"injected":w.injected,
        "dissipated":w.dissipated,"unabsorbed":w.unabsorbed,
        "moves":w.moves_total,"formed":w.bonds_formed_total,
        "broken":w.bonds_broken_total,
        "transfer_events":totals[0],
        "bond_route_events":totals[1],
        "nonbonded_route_events":totals[2]
    }
    return {
        "seed":seed,"arm":arm,
        "config_hash":w.config.hash(),
        "initial":sig,
        "checkpoints":[snaps[t] for t in CHECKPOINTS],
        "late_501_600":{
            "moves":b["moves"]-a["moves"],
            "new_bonds":b["formed"]-a["formed"],
            "broken_bonds":b["broken"]-a["broken"],
            "all_transfers":b["transfers"]-a["transfers"],
            "bond_route_transfers":b["transfers_along_bonds"]-a["transfers_along_bonds"],
            "nonbonded_route_transfers":b["transfers_across_nonbonded_contacts"]-a["transfers_across_nonbonded_contacts"]
        },
        "topology_at_600":describe_native_topology(w),
        "final":final
    }


def bare_replay(r):
    new=run_world(r["seed"],r["arm"])
    assert new["config_hash"]==r["config_hash"]
    assert new["initial"]==r["initial"]
    assert new["final"]==r["final"]
    assert new["late_501_600"]==r["late_501_600"]
    return {"seed":r["seed"],"arm":r["arm"],"full_hash_rng_energy_and_routes_match":True}


def summary(worlds,p):
    idx={(r["seed"],r["arm"]):r for r in worlds}
    expected={(s,a) for s in range(p["design"]["seed_first"],p["design"]["seed_last"]+1) for a in ARMS}
    assert len(worlds)==len(idx)==len(expected)==300 and set(idx)==expected
    for seed in range(20001,20101):
        records=[idx[(seed,arm)] for arm in ARMS]
        assert len({r["initial"]["initial_particles_hash"] for r in records})==1
        assert len({r["initial"]["rng"] for r in records})==1
        assert len({r["initial"]["draws"] for r in records})==1
        assert len({r["config_hash"] for r in records})==1
        assert all(r["final"]["injected"]==19200 for r in records)
    def avg(vals):
        return round(sum(vals)/len(vals),4)
    arm_stats={}
    for arm in ARMS:
        group=[idx[(seed,arm)] for seed in range(20001,20101)]
        end=[r["checkpoints"][-1] for r in group]
        arm_stats[arm]={
            "worlds":100,
            "mean_late_moves":avg([r["late_501_600"]["moves"] for r in group]),
            "mean_late_new_bonds":avg([r["late_501_600"]["new_bonds"] for r in group]),
            "mean_source_overflow":avg([r["final"]["unabsorbed"] for r in group]),
            "mean_zero_energy_particles_final":avg([e["zero_energy_particles"] for e in end]),
            "mean_eligible_free_mobile_final":avg([e["free_mobile_energy_eligible"] for e in end]),
            "mean_energy_bonded_particles_final":avg([e["energy_in_bonded_particles"] for e in end]),
            "mean_energy_free_particles_final":avg([e["energy_in_free_particles"] for e in end]),
            "mean_energy_gini_final":avg([e["gini"] for e in end]),
            "mean_all_transfer_events":avg([r["final"]["transfer_events"] for r in group]),
            "mean_bond_route_events":avg([r["final"]["bond_route_events"] for r in group]),
            "mean_nonbonded_route_events":avg([r["final"]["nonbonded_route_events"] for r in group]),
            "worlds_with_any_bond_transport":sum(r["final"]["bond_route_events"]>0 for r in group),
            "worlds_with_native_ring_final":sum(r["topology_at_600"]["native_simple_ring_components"]>0 for r in group)
        }
    metrics={
        "late_moves":lambda r:r["late_501_600"]["moves"],
        "late_new_bonds":lambda r:r["late_501_600"]["new_bonds"],
        "zero_energy_particles_final":lambda r:r["checkpoints"][-1]["zero_energy_particles"],
        "energy_bonded_particles_final":lambda r:r["checkpoints"][-1]["energy_in_bonded_particles"],
        "eligible_free_mobile_final":lambda r:r["checkpoints"][-1]["free_mobile_energy_eligible"],
        "overflow":lambda r:r["final"]["unabsorbed"]
    }
    pairs={}
    for label,a,b in [
        ("bond_vs_none","bond_only","no_transfer"),
        ("contacts_vs_bond","all_contacts","bond_only"),
        ("contacts_vs_none","all_contacts","no_transfer")]:
        outcome={}
        for name,getter in metrics.items():
            diffs=[getter(idx[(seed,a)])-getter(idx[(seed,b)]) for seed in range(20001,20101)]
            outcome[name]={
                "mean_paired_a_minus_b":avg(diffs),
                "a_greater":sum(x>0 for x in diffs),
                "a_lower":sum(x<0 for x in diffs),
                "ties":sum(x==0 for x in diffs),
            }
        pairs[label]={"a":a,"b":b,"metrics":outcome}
    network_events=arm_stats["bond_only"]["worlds_with_any_bond_transport"]
    network_formations=pairs["bond_vs_none"]["metrics"]["late_new_bonds"]["a_greater"]
    generic_moves=pairs["contacts_vs_bond"]["metrics"]["late_moves"]["a_greater"]
    generic_zero=pairs["contacts_vs_bond"]["metrics"]["zero_energy_particles_final"]["a_lower"]
    return {
        "independent_numeric_seeds":100,"total_worlds":300,
        "arms":arm_stats,"paired_comparisons":pairs,
        "preregistered_decisions":{
            "bond_network_chemical_benefit":"passed" if network_events>=70 and network_formations>=60 else "not_met",
            "generic_contacts_exceed_bond_transport":"passed" if generic_moves>=75 and generic_zero>=70 else "not_met",
            "component_thresholds":{
                "bond_worlds_with_transport":network_events,
                "bond_more_late_formations_seeds":network_formations,
                "generic_more_late_moves_seeds":generic_moves,
                "generic_fewer_zero_energy_seeds":generic_zero,
                "required":[70,60,75,70]
            }
        },
        "caution":"Bond-driven transport is deliberately enabled; bonded atoms are immobile in original M6 dynamics, and direct native bond-break hazard is constant. Bond and nonbonded transfer arms diverge in energy, geometry and global RNG. No life, active self-maintenance, genetically inherited replication or natural metabolism."
    }


def run_shard(start,end):
    p=protocol()
    d={"start":start,"end":end}
    assert d in p["design"]["shards"]
    rows=[]
    replays=[]
    for seed in range(start,end+1):
        pack=[run_world(seed,arm) for arm in ARMS]
        assert len({r["initial"]["initial_particles_hash"] for r in pack})==1
        assert len({r["initial"]["rng"] for r in pack})==1
        rows.extend(pack)
        if seed==start:
            replays=[bare_replay(r) for r in pack]
        if (seed-start+1)%5==0:
            print(f"M73_PROGRESS shard={start}-{end} seed={seed} completed_worlds={len(rows)}",flush=True)
    assert len(rows)==(end-start+1)*len(ARMS)
    out={
        "schema":"alife-m7-3-bond-transport-shard-v1",
        "descriptor":d,"protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":rows,"bare_replays":replays,
        "original_M6_M7_1_M7_2_core_unchanged":True,
    }
    file=BASE/"shards"/f"{start}-{end}.json"
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(out,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M73_SHARD="+json.dumps({"start":start,"end":end,"worlds":len(rows),"replays":len(replays)},sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("*.json"))
    assert len(files)==4
    rows=[]
    reps=[]
    seen=[]
    for path in files:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m7-3-bond-transport-shard-v1"
        assert chunk["protocol_sha256"]==sha256(PROTOCOL.read_bytes()).hexdigest()
        assert chunk["original_M6_M7_1_M7_2_core_unchanged"] is True
        d=chunk["descriptor"]
        assert d in p["design"]["shards"] and d not in seen
        seen.append(d)
        keys=[(r["seed"],r["arm"]) for r in chunk["worlds"]]
        assert len(keys)==len(set(keys))
        assert set(keys)=={(seed,arm) for seed in range(d["start"],d["end"]+1) for arm in ARMS}
        assert {(x["seed"],x["arm"]) for x in chunk["bare_replays"]}=={(d["start"],arm) for arm in ARMS}
        assert all(x["full_hash_rng_energy_and_routes_match"] for x in chunk["bare_replays"])
        rows.extend(chunk["worlds"])
        reps.extend(chunk["bare_replays"])
    assert all(x in seen for x in p["design"]["shards"])
    s=summary(rows,p)
    out={
        "schema":"alife-m7-3-native-bond-route-results-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":sorted(rows,key=lambda r:(r["seed"],r["arm"])),
        "bare_replays":reps,
        "summary":s,"all_shards_complete":True,
        "historical_m6_and_m7_results_excluded":True,
        "no_core_src_changes":True
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("M73_FINAL_SUMMARY="+json.dumps(s,sort_keys=True),flush=True)
    print("M73_SUCCESS="+str(len(rows)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)
    s=sub.add_parser("shard")
    s.add_argument("--start",type=int,required=True)
    s.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    args=parser.parse_args()
    if args.command=="shard":run_shard(args.start,args.end)
    else:merge()


if __name__=="__main__":
    main()
