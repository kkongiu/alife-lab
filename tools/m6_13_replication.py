"""M6.13 preregistered independent-seed replication of native seven-edge cages.

Runs unchanged M6.12 physical observer in disjoint frozen 200-world shards.
A distinct numeric seed (across both density arms) is the primary independent
unit. Historical M6.11/M6.12 discoveries are excluded from the numerator.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from math import sqrt
from pathlib import Path
import json

from tools.m6_4_cycles import create_natural, protocol as natural_protocol
from tools.m6_12_precursors import study_world

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m6_13_replication/protocol.json"
BASE=ROOT/"campaigns/m6_13_replication"
RESULTS=BASE/"results.json"


def protocol():
    payload=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert payload["schema"]=="alife-m6-13-independent-geometric-confinement-replication-v1"
    assert payload["status"]=="preregistered_before_code_and_run"
    assert payload["sample"]["seeds"]=={"start":12001,"end_inclusive":12400,"count":400}
    assert payload["sample"]["worlds"]==800
    assert len(payload["sample"]["frozen_shards"])==4
    return payload


def replay(world_record, natural, horizon):
    """Complete no-observer equivalence; special attention to all positives."""
    seed=world_record["seed"]
    density=world_record["density"]
    result=world_record["result"]
    bare=create_natural(seed,density,natural)
    assert bare.state_hash_full()==result["initial"]["hash"]
    assert bare.rng.fingerprint()==result["initial"]["rng"]
    assert bare.rng.draws==result["initial"]["draws"]
    bare.advance(horizon)
    bare.check()
    f=result["final"]
    assert bare.state_hash_full()==f["hash"]
    assert bare.rng.fingerprint()==f["rng"]
    assert bare.rng.draws==f["draws"]
    assert bare.energy()==f["energy"]
    assert bare.dissipated==f["dissipated"]
    assert bare.bonds_formed_total==f["formed"]
    assert bare.bonds_broken_total==f["broken"]
    return {"density":density,"seed":seed,"full_hash":f["hash"],"rng":f["rng"]}


def is_long_episode(ep, ticks=30):
    return ep["resident_mobile"] and ep["duration_ticks"]>=ticks


def run_shard(density, start, end):
    p=protocol()
    shard={"density":density,"start":start,"end":end}
    assert shard in p["sample"]["frozen_shards"],"unregistered shard"
    natural=natural_protocol()
    worlds=[]
    replays=[]
    for seed in range(start,end+1):
        world=create_natural(seed,density,natural)
        record=study_world(world,p["sample"]["horizon_ticks"])
        full={"density":density,"seed":seed,"result":record}
        worlds.append(full)
        if seed==p["sample"]["seeds"]["start"] or any(
                is_long_episode(ep) for ep in record["episodes"]):
            replays.append(replay(full,natural,p["sample"]["horizon_ticks"]))
        if (seed-start+1)%25==0:
            positive=sum(any(is_long_episode(ep) for ep in w["result"]["episodes"]) for w in worlds)
            print(f"M613_PROGRESS={density}:{seed} worlds={len(worlds)} positive_worlds={positive}",flush=True)
    assert len(worlds)==end-start+1
    output={
        "schema":"alife-m6-13-shard-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "shard":shard,"worlds":worlds,"replays":replays,
        "unmodified_physics":True
    }
    path=BASE/"shards"/f"{density}-{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M613_SHARD_RESULT="+json.dumps({
        "path":str(path),"worlds":len(worlds),
        "positive_worlds":sum(any(is_long_episode(e) for e in w["result"]["episodes"]) for w in worlds),
        "replays":len(replays)},sort_keys=True),flush=True)
    return output


def wilson(success,total):
    """Two-sided descriptive Wilson 95% interval for independent seed units."""
    if total==0:
        return None
    z=1.959963984540054
    proportion=success/total
    den=1+(z*z)/total
    center=(proportion+(z*z)/(2*total))/den
    half=z*sqrt((proportion*(1-proportion)/total)+(z*z/(4*total*total)))/den
    return {"rate":round(proportion,6),"low":round(max(0,center-half),6),
            "high":round(min(1,center+half),6)}


def summarize(worlds,p):
    expected_seeds=set(range(p["sample"]["seeds"]["start"],
                             p["sample"]["seeds"]["end_inclusive"]+1))
    by_density={}
    by_seed=defaultdict(list)
    cutoffs=p["secondary"]["nested_duration_cutoffs"]
    examples=[]
    for density in p["sample"]["densities"]:
        group=[w for w in worlds if w["density"]==density]
        assert {w["seed"] for w in group}==expected_seeds
        counts=Counter()
        qualified_seeds=set()
        qualified_first=set()
        censored_long=0
        event_counts=Counter()
        for w in group:
            by_seed[w["seed"]].append(w)
            eps=w["result"]["episodes"]
            counts["all_episodes"]+=len(eps)
            counts["first_material_episodes"]+=sum(e["first_of_material_set"] for e in eps)
            counts["empty_start"]+=sum(e["stratum"]=="empty" for e in eps)
            counts["mobile_center_start"]+=sum(e["resident_mobile"] for e in eps)
            counts["eighth_edge_closed"]+=sum(e["closure_observed"] for e in eps)
            for cutoff in cutoffs:
                if any(is_long_episode(e,cutoff) for e in eps):
                    event_counts[f"worlds_ge_{cutoff}"]+=1
                event_counts[f"episodes_ge_{cutoff}"]+=sum(is_long_episode(e,cutoff) for e in eps)
            if any(is_long_episode(e) for e in eps):
                qualified_seeds.add(w["seed"])
            if any(is_long_episode(e) and e["first_of_material_set"] for e in eps):
                qualified_first.add(w["seed"])
            censored_long+=sum(is_long_episode(e) and e["right_censored"] for e in eps)
            for ep in eps:
                if ep["resident_mobile"]:
                    examples.append({
                        "density":density,"seed":w["seed"],
                        "world_first_material_episode":ep["first_of_material_set"],
                        "start_tick":ep["start_tick"],"duration_ticks":ep["duration_ticks"],
                        "center":ep["center"],"resident_id":ep["resident_id"],
                        "first_closure_tick":ep["first_closure_tick"],
                        "right_censored":ep["right_censored"],
                        "ended_by":ep["ended_by"]
                    })
        by_density[density]={
            "worlds":len(group),"worlds_with_ge_30":len(qualified_seeds),
            "worlds_with_ge_30_first_material":len(qualified_first),
            "ge_30_rate_wilson95":wilson(len(qualified_seeds),len(group)),
            "episodes_and_sources":dict(counts),
            "predefined_duration_thresholds":dict(event_counts),
            "ge_30_right_censored_episodes":censored_long,
            "qualifying_seeds":sorted(qualified_seeds),
            "qualifying_first_material_seeds":sorted(qualified_first)
        }
    assert set(by_seed)==expected_seeds
    assert all(len(v)==len(p["sample"]["densities"]) for v in by_seed.values())
    unique_pass=set()
    unique_first=set()
    for seed,units in by_seed.items():
        if any(any(is_long_episode(e) for e in w["result"]["episodes"]) for w in units):
            unique_pass.add(seed)
        if any(any(is_long_episode(e) and e["first_of_material_set"]
                   for e in w["result"]["episodes"]) for w in units):
            unique_first.add(seed)
    number=len(unique_pass)
    decision=("replicated_30tick_native_geometric_confinement_only" if number>=2
              else "single_not_independently_replicated" if number==1
              else "no_30tick_replication")
    return {
        "worlds":len(worlds),"unique_numeric_seeds":len(expected_seeds),
        "by_density":by_density,
        "primary_distinct_seeds_ge_30":number,
        "primary_qualifying_seeds":sorted(unique_pass),
        "first_material_distinct_seeds_ge_30":len(unique_first),
        "first_material_qualifying_seeds":sorted(unique_first),
        "primary_rate_wilson95":wilson(number,len(expected_seeds)),
        "decision":decision,
        "mobile_center_episodes":sorted(examples,key=lambda x:(-x["duration_ticks"],x["seed"])),
        "limitations":"Observational, baseline/enriched same numeric seed paired conservatively. Episodes within worlds dependent. All geometry arises from original M6 static bonded matter; no metabolism, inheritance, self-replication or biological membrane."
    }


def merge():
    p=protocol()
    expected_shards=p["sample"]["frozen_shards"]
    paths=list((BASE/"shards").glob("*.json"))
    assert len(paths)==len(expected_shards),(len(paths),paths)
    all_worlds=[]
    all_replays=[]
    actual_shards=[]
    for path in paths:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m6-13-shard-v1"
        assert chunk["protocol_sha256"]==sha256(PROTOCOL.read_bytes()).hexdigest()
        assert chunk["unmodified_physics"] is True
        descriptor=chunk["shard"]
        assert descriptor in expected_shards
        assert descriptor not in actual_shards
        actual_shards.append(descriptor)
        keys={(w["density"],w["seed"]) for w in chunk["worlds"]}
        assert keys=={(descriptor["density"],s) for s in range(descriptor["start"],descriptor["end"]+1)}
        all_worlds.extend(chunk["worlds"])
        all_replays.extend(chunk["replays"])
    assert all(e in actual_shards for e in expected_shards)
    expected={(d,s) for d in p["sample"]["densities"]
              for s in range(p["sample"]["seeds"]["start"],
                             p["sample"]["seeds"]["end_inclusive"]+1)}
    keys=[(w["density"],w["seed"]) for w in all_worlds]
    assert len(keys)==p["sample"]["worlds"]==len(set(keys))
    assert set(keys)==expected
    target={(w["density"],w["seed"]) for w in all_worlds
            if any(is_long_episode(ep) for ep in w["result"]["episodes"])}
    target.update((d,p["sample"]["seeds"]["start"]) for d in p["sample"]["densities"])
    assert {(x["density"],x["seed"]) for x in all_replays}==target, "missing positive bare replay"
    all_worlds.sort(key=lambda x:(x["density"],x["seed"]))
    result={
        "schema":"alife-m6-13-independent-geometric-replication-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":all_worlds,"replays":sorted(all_replays,key=lambda x:(x["density"],x["seed"])),
        "summary":summarize(all_worlds,p),"shards":expected_shards,
        "historical_data_excluded":True,
        "physics_unchanged":True
    }
    RESULTS.parent.mkdir(parents=True,exist_ok=True)
    RESULTS.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M613_FINAL_SUMMARY="+json.dumps(result["summary"],sort_keys=True),flush=True)
    print("M613_SUCCESS total="+str(len(all_worlds))+" replayed="+str(len(all_replays)),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)
    run=sub.add_parser("shard")
    run.add_argument("--density",choices=["baseline","enriched"],required=True)
    run.add_argument("--start",type=int,required=True)
    run.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    args=parser.parse_args()
    if args.command=="shard":
        run_shard(args.density,args.start,args.end)
    else:
        merge()


if __name__=="__main__":
    main()
