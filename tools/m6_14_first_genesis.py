"""M6.14 strict first-observed native 3x3 perimeter material-genesis audit.

Preregistered new seeds, no physics modifications. Unlike M6.13, an eight-ID
set previously seen as ANY exact 3x3 seven-edge perimeter path OR native exact
eight-edge ring cannot qualify as a first-genesis event after a reappearance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json

from tools.m6_4_cycles import BreakRecorder, create_natural, protocol as natural_protocol
from tools.m6_10_pockets import observed_cycles
from tools.m6_12_precursors import precursor_candidates, material_intact
from tools.m6_13_replication import wilson, replay

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m6_14_first_genesis/protocol.json"
BASE=ROOT/"campaigns/m6_14_first_genesis"
OUTPUT=BASE/"merged_results.json"


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-14-independent-first-native-cage-genesis-v1"
    assert p["status"]=="frozen_before_runner_or_results"
    assert p["sample"]["seed_first"]==13001
    assert p["sample"]["seed_last"]==14600
    assert p["sample"]["seed_count"]==1600
    assert p["sample"]["expected_worlds"]==1600
    assert len(p["sample"]["shards"])==8
    return p


def first_birth_provenance(material_ids,first_kind,episodes_seen,last_stop,tick):
    """Pure audit: first material shape may be a ring BEFORE seven-edge path."""
    assert len(material_ids)==8 and tuple(material_ids)==tuple(sorted(material_ids))
    previous=episodes_seen.get(material_ids,0)
    kind=first_kind.get(material_ids)
    last=last_stop.get(material_ids)
    return {
        "first_material_ever_seen":kind is None,
        "historical_first_kind":kind if kind is not None else "seven",
        "prior_seven_edge_episodes":previous,
        "ticks_since_prior_ending":None if last is None else tick-last,
        "new_material_first_seven_edge":kind is None and previous==0
    }


def is_long(ep,cutoff=30):
    return ep["resident_mobile"] and ep["duration_ticks"]>=cutoff


def is_primary(ep,cutoff=30):
    return is_long(ep,cutoff) and ep["new_material_first_seven_edge"]


def study_world(world,steps=600):
    assert world.step==0 and not world.store.bonds
    world.check()
    original={"hash":world.state_hash_full(),"rng":world.rng.fingerprint(),
              "draws":world.rng.draws}
    recorder=BreakRecorder()
    world.event_sink=recorder
    active={}
    finished=[]
    counts=Counter()
    first_kind={}
    episodes_seen=Counter()
    last_stop={}
    ring_only_examples=[]

    def close_episode(key,tick,why,censored=False):
        ep=active.pop(key)
        length=tick-ep["start_tick"]+(1 if censored else 0)
        assert length>=1
        record={
            "start_tick":ep["start_tick"],
            "duration_ticks":length,
            "last_observed_tick":tick if censored else tick-1,
            "ended_by":why,
            "right_censored":censored,
            "center":list(ep["center"]),
            "ids":list(ep["ids"]),
            "original_edges":[list(edge) for edge in sorted(ep["edges"])],
            "resident_mobile":ep["resident_mobile"],
            "resident_id":ep["resident_id"],
            "center_start_state":ep["stratum"],
            "terminal_pair":ep["pair"],
            "first_eighth_bond_tick":ep["first_closed_tick"],
            "first_material_ever_seen":ep["first_material_ever_seen"],
            "historical_first_kind":ep["historical_first_kind"],
            "prior_seven_edge_episodes":ep["prior_seven_edge_episodes"],
            "ticks_since_prior_ending":ep["ticks_since_prior_ending"],
            "new_material_first_seven_edge":ep["new_material_first_seven_edge"]
        }
        finished.append(record)
        last_stop[ep["ids"]]=tick
        if ep["new_material_first_seven_edge"]:
            counts["first_seven_edge_episodes"]+=1
        if ep["resident_mobile"]:
            counts["mobile_center_episodes"]+=1
            if ep["new_material_first_seven_edge"]:
                counts["first_mobile_center_episodes"]+=1
        if ep["resident_mobile"] and length>=30:
            counts["mobile_30_tick_episodes"]+=1
        if ep["new_material_first_seven_edge"] and ep["resident_mobile"] and length>=30:
            counts["first_genesis_30_tick_episodes"]+=1

    def observer(w):
        before=w.rng.draws
        t=w.step
        broken=recorder.pop(t)
        # Finish original-edge interruptions BEFORE recognizing re-formed episodes.
        for key,ep in list(active.items()):
            intact,why=material_intact(w,ep,broken)
            if not intact:
                close_episode(key,t,why)
                continue
            missing=ep["missing"]
            ia,ib=(w.store.index_of(q) for q in missing)
            full=tuple(sorted((ia,ib))) in w.store.bonds
            if full and ep["first_closed_tick"] is None:
                ep["first_closed_tick"]=t

        # Prior exact eight-rings count as material history even if no prior
        # seven-edge path was observed in a post-step snapshot.
        rings,_=observed_cycles(w)
        ring_sets={ring["ids"] for ring in rings
                   if ring["size"]==8 and ring.get("pocket") is True}
        # For each candidate, first-time classification sees history from
        # prior ticks. A single connected material set cannot be both a
        # seven-bond path and eight-bond ring at the SAME tick.
        candidates=precursor_candidates(w)
        for obj in candidates:
            key=(obj["center"],obj["ids"],obj["edges"])
            if key in active:
                continue
            ids=obj["ids"]
            provenance=first_birth_provenance(ids,first_kind,episodes_seen,last_stop,t)
            if ids not in first_kind:
                first_kind[ids]="seven"
            episodes_seen[ids]+=1
            record={**obj,**provenance,
                    "start_tick":t,"first_closed_tick":None}
            active[key]=record
            counts["seven_edge_episodes_started"]+=1
            if provenance["new_material_first_seven_edge"]:
                counts["seven_first_born_materials"]+=1
            else:
                counts["recurrent_seven_edge_episodes"]+=1
        for ids in ring_sets:
            if ids not in first_kind:
                first_kind[ids]="eight"
                counts["native_full_ring_before_any_seven_path"]+=1
                if len(ring_only_examples)<10:
                    ring_only_examples.append({"tick":t,"ids":list(ids)})
        assert w.rng.draws==before, "observer changed physical RNG"

    world.advance(steps,observer=observer)
    for key in list(active):
        close_episode(key,world.step,"right_censored_at_horizon",censored=True)
    world.check()
    # Keep all material episodes; sort chronologically so first/recurrent
    # behavior is visible in downloaded data.
    finished.sort(key=lambda ep:(ep["start_tick"],ep["ids"]))
    return {
        "initial":original,
        "final":{"hash":world.state_hash_full(),"rng":world.rng.fingerprint(),
                 "draws":world.rng.draws,"energy":world.energy(),
                 "dissipated":world.dissipated,"formed":world.bonds_formed_total,
                 "broken":world.bonds_broken_total},
        "episodes":finished,
        "counts":dict(counts),
        "first_material_shapes":dict(Counter(first_kind.values())),
        "ring_first_examples":ring_only_examples
    }


def summarize(worlds,p):
    total=p["sample"]["expected_worlds"]
    assert len(worlds)==total
    seed_set={w["seed"] for w in worlds}
    assert seed_set==set(range(p["sample"]["seed_first"],p["sample"]["seed_last"]+1))
    first_seeds=set()
    any_seeds=set()
    recurrent_seeds=set()
    counts=Counter()
    all_episodes=[]
    events_by_cutoff=Counter()
    for w in worlds:
        eps=w["result"]["episodes"]
        counts.update(w["result"]["counts"])
        counts["episodes_total"]+=len(eps)
        counts["right_censored"]+=sum(e["right_censored"] for e in eps)
        if any(is_primary(e) for e in eps):
            first_seeds.add(w["seed"])
        if any(is_long(e) for e in eps):
            any_seeds.add(w["seed"])
        if any(is_long(e) and not e["new_material_first_seven_edge"] for e in eps):
            recurrent_seeds.add(w["seed"])
        for threshold in p["secondary"]["duration_cutoffs"]:
            if any(is_primary(e,threshold) for e in eps):
                events_by_cutoff[f"worlds_first_ge_{threshold}"]+=1
            if any(is_long(e,threshold) for e in eps):
                events_by_cutoff[f"worlds_any_ge_{threshold}"]+=1
            events_by_cutoff[f"first_episodes_ge_{threshold}"]+=sum(is_primary(e,threshold) for e in eps)
            events_by_cutoff[f"all_mobile_episodes_ge_{threshold}"]+=sum(is_long(e,threshold) for e in eps)
        for ep in eps:
            if ep["resident_mobile"]:
                all_episodes.append({
                    "seed":w["seed"],
                    "center":ep["center"],
                    "resident":ep["resident_id"],
                    "start_tick":ep["start_tick"],
                    "duration_ticks":ep["duration_ticks"],
                    "right_censored":ep["right_censored"],
                    "new_material_first_seven_edge":ep["new_material_first_seven_edge"],
                    "historical_first_kind":ep["historical_first_kind"],
                    "prior_seven_edge_episodes":ep["prior_seven_edge_episodes"],
                    "first_eighth_bond_tick":ep["first_eighth_bond_tick"],
                    "ended_by":ep["ended_by"]
                })
    first_n=len(first_seeds)
    decision=("replicated_first_genesis_native_geometric_confinement_only" if first_n>=2
              else "one_first_genesis_world" if first_n==1
              else "no_first_genesis_replication")
    return {
        "status":decision,
        "worlds":total,"density":"enriched",
        "primary_qualifying_first_genesis_seeds":sorted(first_seeds),
        "primary_first_genesis_worlds_ge30":first_n,
        "all_episode_worlds_ge30":len(any_seeds),
        "all_episode_world_seeds_ge30":sorted(any_seeds),
        "recurrent_only_world_seeds_ge30":sorted(recurrent_seeds-first_seeds),
        "recurrent_longepisode_world_seeds_ge30":sorted(recurrent_seeds),
        "primary_first_genesis_rate_wilson95":wilson(first_n,total),
        "any_episode_rate_wilson95":wilson(len(any_seeds),total),
        "counts":dict(counts),
        "prespecified_cutoff_breakdown":dict(events_by_cutoff),
        "native_mobile_episodes":sorted(all_episodes,key=lambda a:(-a["duration_ticks"],a["seed"])),
        "interpretation":"New first genesis is a first observed exact 7-edge or 8-edge 3x3 perimeter material set; it is NOT the first ever interaction of its atoms. Geometric confinement is passive. Reclosures are dependent. No cell, heredity, metabolism, biologically active repair or self-replication."
    }


def run_shard(start,end):
    p=protocol()
    descriptor={"start":start,"end":end}
    assert descriptor in p["sample"]["shards"],"shard not preregistered"
    natural=natural_protocol()
    worlds=[]
    replays=[]
    for seed in range(start,end+1):
        w=create_natural(seed,"enriched",natural)
        result=study_world(w,steps=p["sample"]["horizon_ticks"])
        item={"seed":seed,"density":"enriched","result":result}
        worlds.append(item)
        if seed==p["sample"]["seed_first"] or any(is_long(e) for e in result["episodes"]):
            replays.append(replay(item,natural,p["sample"]["horizon_ticks"]))
        if (seed-start+1)%25==0:
            first_positive=sum(any(is_primary(e) for e in item["result"]["episodes"]) for item in worlds)
            any_positive=sum(any(is_long(e) for e in item["result"]["episodes"]) for item in worlds)
            print(f"M614_PROGRESS={start}-{end} through={seed} worlds={len(worlds)} primary={first_positive} any={any_positive}",flush=True)
    assert len(worlds)==end-start+1
    output={
        "schema":"alife-m6-14-shard-v1",
        "descriptor":descriptor,
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":worlds,"replays":replays,
        "unchanged_original_M6_laws":True
    }
    path=BASE/"shards"/f"enriched-{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M614_SHARD_RESULT="+json.dumps({
        "start":start,"end":end,"worlds":len(worlds),
        "primary_positive_worlds":sum(any(is_primary(e) for e in w["result"]["episodes"]) for w in worlds),
        "any_positive_worlds":sum(any(is_long(e) for e in w["result"]["episodes"]) for w in worlds),
        "replays":len(replays)},sort_keys=True),flush=True)
    return output


def merge():
    p=protocol()
    expected=p["sample"]["shards"]
    paths=list((BASE/"shards").glob("*.json"))
    assert len(paths)==len(expected),("missing or extra shard",len(paths),len(expected))
    worlds=[]
    replays=[]
    found=[]
    for path in paths:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m6-14-shard-v1"
        assert chunk["protocol_sha256"]==sha256(PROTOCOL.read_bytes()).hexdigest()
        assert chunk["unchanged_original_M6_laws"] is True
        desc=chunk["descriptor"]
        assert desc in expected and desc not in found
        found.append(desc)
        assert [(w["density"],w["seed"]) for w in chunk["worlds"]]==[
            ("enriched",i) for i in range(desc["start"],desc["end"]+1)]
        worlds.extend(chunk["worlds"])
        replays.extend(chunk["replays"])
    assert all(x in found for x in expected)
    worlds.sort(key=lambda w:w["seed"])
    assert len({w["seed"] for w in worlds})==len(worlds)==p["sample"]["expected_worlds"]
    assert [w["seed"] for w in worlds]==list(range(p["sample"]["seed_first"],p["sample"]["seed_last"]+1))
    positives={w["seed"] for w in worlds if any(is_long(e) for e in w["result"]["episodes"])}
    positives.add(p["sample"]["seed_first"])
    assert {x["seed"] for x in replays}==positives
    assert len(replays)==len(positives)
    summary=summarize(worlds,p)
    final={
        "schema":"alife-m6-14-independent-first-genesis-results-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":worlds,"replays":sorted(replays,key=lambda x:x["seed"]),
        "summary":summary,
        "all_shards_complete":True,
        "historical_M6_11_13_events_excluded":True,
        "physics_unchanged":True
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(final,indent=2)+"\n",encoding="utf-8")
    print("M614_FINAL_SUMMARY="+json.dumps(summary,sort_keys=True),flush=True)
    print("M614_SUCCESS="+str(len(worlds)),flush=True)
    return final


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)
    run=sub.add_parser("shard")
    run.add_argument("--start",type=int,required=True)
    run.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    args=parser.parse_args()
    if args.command=="shard":
        run_shard(args.start,args.end)
    else:
        merge()


if __name__=="__main__":
    main()
