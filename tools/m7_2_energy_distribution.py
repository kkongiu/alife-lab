"""M7.2 — preregistered passive-contact energy distribution experiment.

All physical modifications are confined to this NEW experimental module.
Original M6/M7.1 engine and source configurations remain unmodified.
Contact transfer is deterministic and energy conserving, but NOT a
thermodynamically complete or biological transport mechanism.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.config import Config
from alife.world import World
from tools.m7_1_energy_factorial import make_config as m71_make_config
from tools.m7_1_energy_factorial import describe_native_topology, source_features

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_2_energy"
PROTOCOL=BASE/"protocol.json"
RESULTS=BASE/"merged_results.json"

ARMS=(
    "dispersed_no_transfer",
    "clustered_no_transfer",
    "dispersed_contact_transfer",
    "clustered_contact_transfer",
)
CHECKPOINTS=(0,100,200,400,500,600)
HORIZON=600
OFFSETS=((1,0),(0,1))


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-2-paired-source-topology-passive-contact-transport-v1"
    assert p["status"]=="preregistered_before_new_code_and_results"
    assert (p["design"]["seed_first"],p["design"]["seed_last"])==(19001,19080)
    assert p["design"]["paired_worlds"]==320
    assert p["design"]["arm_labels"]==list(ARMS)
    assert len(p["design"]["shards"])==4
    return p


def config_for(seed,arm,p=None):
    p=p if p is not None else protocol()
    assert arm in ARMS
    # Dispersed no-transfer is exactly the original M7.1 driven-no-cat arm
    # for the same seed. No new config schema/core physics changes.
    original=m71_make_config(seed,"driven_no_catalysis")
    if arm.startswith("dispersed"):
        return original
    data=original.to_dict()
    sh=p["controlled_energy"]
    sources=[
        {"x":x,"y":y,"rate_num":sh["generation_per_source_per_tick"],
         "rate_den":1,"capacity":sh["source_capacity_per_site"],
         "overflow":"discard"}
        for y in sh["clustered"]["ys"] for x in sh["clustered"]["xs"]
    ]
    assert len(sources)==sh["sources_count"]==16
    assert sum(s["rate_num"] for s in sources)==32
    data["energy"]["sources"]=sources
    config=Config.from_dict(data).validate()
    assert config.chemistry.catalysis==()
    assert config.energy.movement_cost==1
    return config


def contacts(s):
    """Each undirected nearest-neighbor pair once, sorted by persistent IDs."""
    width,height=s.width,s.height
    pairs=set()
    for i in range(len(s.ids)):
        x,y=s.xs[i],s.ys[i]
        for dx,dy in OFFSETS:
            j=s.grid[((y+dy)%height)*width+((x+dx)%width)]
            if j<0 or j==i:
                continue
            pairs.add((i,j) if s.ids[i]<s.ids[j] else (j,i))
    return sorted(pairs,key=lambda pair:(s.ids[pair[0]],s.ids[pair[1]]))


def diffuse_contact_energy(world):
    """One synchronous source-snapshot pass; returns (transfers, energy_moved).

    For every adjacent pair with snapshot gradient >=2 propose one unit rich
    -> poor. Accept in persistent ID order, spending only if donor remaining
    budget >=1. No RNG, no new mass, no topology or position changes.
    """
    s=world.store
    before_rng=world.rng.fingerprint()
    before_draws=world.rng.draws
    before_energy=world.energy()
    before_sum=sum(s.energy)
    original=tuple(s.energy)
    remaining=list(original)
    delta=[0]*len(original)
    count=0
    for i,j in contacts(s):
        if original[i]-original[j]>=2:
            donor,recipient=i,j
        elif original[j]-original[i]>=2:
            donor,recipient=j,i
        else:
            continue
        if remaining[donor]<1:
            continue
        remaining[donor]-=1
        delta[donor]-=1
        delta[recipient]+=1
        count+=1
    for i,value in enumerate(delta):
        if value:
            s.energy[i]+=value
            assert s.energy[i]>=0
    assert sum(s.energy)==before_sum
    assert world.energy()==before_energy
    assert world.rng.draws==before_draws
    assert world.rng.fingerprint()==before_rng
    return count,count  # each accepted transfer is exactly one energy unit


def gini_nonnegative(values):
    """Descriptive per-particle energy inequality, 0 if all zero."""
    data=sorted(values)
    n=len(data)
    if not n:
        return 0.0
    total=sum(data)
    if total==0:
        return 0.0
    numerator=sum((2*i-n+1)*v for i,v in enumerate(data))
    return round(numerator/(n*total),6)


def ledger(world,initial):
    lhs=world.energy()+world.dissipated+world.unabsorbed
    rhs=initial+world.injected
    assert lhs==rhs,(
        "energy balance violated",world.step,lhs,rhs,
        world.energy(),world.dissipated,world.unabsorbed,world.injected
    )


def snapshot(world,initial,transfer_events,transfer_units):
    ledger(world,initial)
    s=world.store
    return {
        "tick":world.step,
        "energy_injected":world.injected,
        "energy_unabsorbed":world.unabsorbed,
        "energy_dissipated":world.dissipated,
        "energy_stored":world.energy(),
        "particle_energy":world.energy_particles(),
        "bond_energy":world.energy_bonds(),
        "source_buffers_energy":world.energy_sources(),
        "particle_energy_gini":gini_nonnegative(s.energy),
        "zero_energy_particles":sum(e==0 for e in s.energy),
        **source_features(world),
        "moves_cumulative":world.moves_total,
        "bonds_formed_cumulative":world.bonds_formed_total,
        "bonds_broken_cumulative":world.bonds_broken_total,
        "contact_transfer_events_cumulative":transfer_events,
        "contact_transfer_units_cumulative":transfer_units,
        "energy_ledger_pass":True,
    }


def run_world(seed,arm,p=None):
    p=p if p is not None else protocol()
    c=config_for(seed,arm,p)
    w=World.create(c)
    assert w.step==0 and not w.store.bonds
    initial=w.configured_energy()
    assert w.energy()==initial
    ids=tuple(w.store.ids)
    start={
        "ids_positions_species_energy_sha256":sha256(json.dumps(
            [w.store.ids,w.store.xs,w.store.ys,w.store.species,w.store.energy],
            separators=(",",":")).encode()).hexdigest(),
        "rng_fingerprint":w.rng.fingerprint(),
        "rng_draws":w.rng.draws,
        "energy":initial,
        "particles":len(w.store),
    }
    readings={0:snapshot(w,initial,0,0)}
    transport=arm.endswith("contact_transfer")
    transfers=0
    units=0
    for tick in range(1,HORIZON+1):
        w.advance(1)
        if transport:
            t,u=diffuse_contact_energy(w)
            transfers+=t
            units+=u
        if tick in CHECKPOINTS:
            readings[tick]=snapshot(w,initial,transfers,units)
            w.check()
    assert tuple(w.store.ids)==ids
    assert sorted(readings)==list(CHECKPOINTS)
    assert w.step==HORIZON
    assert w.injected==p["controlled_energy"]["total_generated_per_world"]==19200
    ledger(w,initial)
    early=readings[100]
    late0=readings[500]
    late=readings[600]
    result={
        "seed":seed,"arm":arm,
        "config_hash":c.hash(),
        "initial":start,
        "checkpoints":[readings[t] for t in CHECKPOINTS],
        "early_1_100":{
            "moves":early["moves_cumulative"],
            "new_bonds":early["bonds_formed_cumulative"],
            "contact_transfers":early["contact_transfer_events_cumulative"],
        },
        "late_501_600":{
            "moves":late["moves_cumulative"]-late0["moves_cumulative"],
            "new_bonds":late["bonds_formed_cumulative"]-late0["bonds_formed_cumulative"],
            "broken_bonds":late["bonds_broken_cumulative"]-late0["bonds_broken_cumulative"],
            "contact_transfers":late["contact_transfer_events_cumulative"]-late0["contact_transfer_events_cumulative"],
        },
        "native_final_topology":describe_native_topology(w),
        "final":{
            "hash":w.state_hash_full(),
            "rng_fingerprint":w.rng.fingerprint(),
            "rng_draws":w.rng.draws,
            "energy_stored":w.energy(),
            "injected":w.injected,
            "dissipated":w.dissipated,
            "unabsorbed":w.unabsorbed,
            "moves":w.moves_total,
            "formed":w.bonds_formed_total,
            "broken":w.bonds_broken_total,
            "contact_transfers":transfers,
            "contact_transfer_units":units,
        }
    }
    return result


def bare_replay(rec,p):
    """Independently rerun from initial seed, not from a saved world state."""
    new=run_world(rec["seed"],rec["arm"],p)
    assert rec["config_hash"]==new["config_hash"]
    assert rec["initial"]==new["initial"]
    assert rec["final"]==new["final"]
    assert rec["late_501_600"]==new["late_501_600"]
    return {
        "seed":rec["seed"],"arm":rec["arm"],
        "full_hash_and_rng_equal":True,
        "energy_and_transfer_counts_equal":True
    }


def paired_summary(worlds,p):
    keys=[(w["seed"],w["arm"]) for w in worlds]
    expected={(s,a) for s in range(19001,19081) for a in ARMS}
    assert len(keys)==320 and len(set(keys))==320 and set(keys)==expected
    idx={(w["seed"],w["arm"]):w for w in worlds}
    for seed in range(19001,19081):
        records=[idx[(seed,arm)] for arm in ARMS]
        assert len({r["initial"]["ids_positions_species_energy_sha256"] for r in records})==1
        assert len({r["initial"]["rng_fingerprint"] for r in records})==1
        assert len({r["initial"]["rng_draws"] for r in records})==1
        assert len({r["initial"]["energy"] for r in records})==1
        assert all(r["final"]["injected"]==19200 for r in records)

    def mean(values):
        return round(sum(values)/len(values),4)
    per_arm={}
    for arm in ARMS:
        rows=[idx[(s,arm)] for s in range(19001,19081)]
        fin=[r["checkpoints"][-1] for r in rows]
        per_arm[arm]={
            "worlds":80,
            "mean_energy_unabsorbed":mean([r["final"]["unabsorbed"] for r in rows]),
            "mean_energy_absorption_fraction":round(1-mean([r["final"]["unabsorbed"] for r in rows])/19200,6),
            "mean_zero_energy_particles_final":mean([x["zero_energy_particles"] for x in fin]),
            "mean_particle_energy_gini_final":mean([x["particle_energy_gini"] for x in fin]),
            "mean_mobile_energy_eligible_final":mean([x["free_mobile_energy_eligible"] for x in fin]),
            "mean_late_moves":mean([r["late_501_600"]["moves"] for r in rows]),
            "mean_late_new_bonds":mean([r["late_501_600"]["new_bonds"] for r in rows]),
            "mean_all_contact_transfers":mean([r["final"]["contact_transfers"] for r in rows]),
            "mean_energy_stored_final":mean([r["final"]["energy_stored"] for r in rows]),
            "worlds_with_native_ring_final":sum(r["native_final_topology"]["native_simple_ring_components"]>0 for r in rows),
        }
    comparisons=[
        ("source_no_transfer","dispersed_no_transfer","clustered_no_transfer"),
        ("source_with_transfer","dispersed_contact_transfer","clustered_contact_transfer"),
        ("transport_dispersed","dispersed_contact_transfer","dispersed_no_transfer"),
        ("transport_clustered","clustered_contact_transfer","clustered_no_transfer"),
    ]
    metrics={
        "overflow":lambda r:r["final"]["unabsorbed"],
        "zero_energy_particles":lambda r:r["checkpoints"][-1]["zero_energy_particles"],
        "gini":lambda r:r["checkpoints"][-1]["particle_energy_gini"],
        "late_moves":lambda r:r["late_501_600"]["moves"],
        "late_bonds":lambda r:r["late_501_600"]["new_bonds"],
        "eligible_mobile":lambda r:r["checkpoints"][-1]["free_mobile_energy_eligible"],
    }
    contrasts={}
    for label,a,b in comparisons:
        by_metric={}
        for name,getter in metrics.items():
            diffs=[getter(idx[(s,a)])-getter(idx[(s,b)]) for s in range(19001,19081)]
            by_metric[name]={
                "mean_paired_a_minus_b":mean(diffs),
                "a_greater":sum(d>0 for d in diffs),
                "ties":sum(d==0 for d in diffs),
                "a_lower":sum(d<0 for d in diffs)
            }
        contrasts[label]={"arm_a":a,"arm_b":b,"by_metric":by_metric}
    src=contrasts["source_no_transfer"]["by_metric"]
    trans=contrasts["transport_dispersed"]["by_metric"]
    source_gate=src["overflow"]["a_lower"]>=60 and src["late_moves"]["a_greater"]>=48
    transport_gate=(trans["zero_energy_particles"]["a_lower"]>=50
                    and trans["late_moves"]["a_greater"]>=48)
    return {
        "worlds":320,"paired_independent_numeric_seeds":80,
        "per_arm":per_arm,"contrasts":contrasts,
        "preregistered_decisions":{
            "source_distribution": "passed" if source_gate else "not_met",
            "passive_local_transport":"passed" if transport_gate else "not_met",
            "source_thresholds":{"less_overflow_seeds":60,"greater_late_moves_seeds":48},
            "transport_thresholds":{"less_zero_energy_seeds":50,"greater_late_moves_seeds":48}
        },
        "caveats":"Only deterministic local passive redistribution and external energy injection. Synchronized initial seeds but RNG streams can diverge. No hereditary mechanism, selective membrane, organism, reproduction or proof of functional metabolism."
    }


def run_shard(start,end):
    p=protocol()
    shard={"start":start,"end":end}
    assert shard in p["design"]["shards"]
    rows=[]
    replays=[]
    for seed in range(start,end+1):
        pack=[run_world(seed,arm,p) for arm in ARMS]
        assert len({x["initial"]["ids_positions_species_energy_sha256"] for x in pack})==1
        assert len({x["initial"]["rng_fingerprint"] for x in pack})==1
        rows.extend(pack)
        if seed==start:
            replays=[bare_replay(r,p) for r in pack]
        if (seed-start+1)%5==0:
            print(f"M72_PROGRESS={start}-{end} seed={seed} worlds={len(rows)}",flush=True)
    assert len(rows)==(end-start+1)*4
    out={
        "schema":"alife-m7-2-frozen-shard-v1",
        "descriptor":shard,
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":rows,
        "replays":replays,
        "unchanged_original_M6_and_M7_1_core":True
    }
    path=BASE/"shards"/f"{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M72_SHARD="+json.dumps({"start":start,"end":end,"worlds":len(rows),"replays":len(replays)},sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("*.json"))
    assert len(files)==4,("need all four frozen shards",len(files))
    rows=[]
    replays=[]
    seen=[]
    for path in files:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m7-2-frozen-shard-v1"
        assert chunk["protocol_sha256"]==sha256(PROTOCOL.read_bytes()).hexdigest()
        assert chunk["unchanged_original_M6_and_M7_1_core"] is True
        desc=chunk["descriptor"]
        assert desc in p["design"]["shards"] and desc not in seen
        seen.append(desc)
        keys={(r["seed"],r["arm"]) for r in chunk["worlds"]}
        expect={(s,a) for s in range(desc["start"],desc["end"]+1) for a in ARMS}
        assert keys==expect and len(keys)==len(chunk["worlds"])
        assert len(chunk["replays"])==4
        assert {(r["seed"],r["arm"]) for r in chunk["replays"]}=={
            (desc["start"],a) for a in ARMS
        }
        rows.extend(chunk["worlds"])
        replays.extend(chunk["replays"])
    assert all(x in seen for x in p["design"]["shards"])
    summary=paired_summary(rows,p)
    result={
        "schema":"alife-m7-2-complete-paired-source-contact-transport-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":sorted(rows,key=lambda r:(r["seed"],r["arm"])),
        "bare_replays":sorted(replays,key=lambda x:(x["seed"],x["arm"])),
        "summary":summary,
        "historical_data_not_in_primary":True,
        "all_shards_complete":True,
        "original_core_unchanged":True
    }
    RESULTS.parent.mkdir(parents=True,exist_ok=True)
    RESULTS.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M72_FINAL_SUMMARY="+json.dumps(summary,sort_keys=True),flush=True)
    print("M72_SUCCESS="+str(len(rows)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)
    shard=sub.add_parser("shard")
    shard.add_argument("--start",type=int,required=True)
    shard.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    args=parser.parse_args()
    if args.command=="shard":
        run_shard(args.start,args.end)
    else:
        merge()


if __name__=="__main__":
    main()
