"""Parallel CI wrapper over SAME M7.11 frozen primary data for independent audit.

Only cuts up existing fixed 640 seed-world audit into 16 independent compute
shards to reduce elapsed execution time; outcomes, audit implementation,
and source population all unchanged. Never resample or use new seed IDs.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from tools.m7_11_independent_posthoc import (
    RAW,BASE,scan_fresh_original,follow_fixed
)

FIRST,LAST=29001,29640


def fixed_shards():
    return [{"start":29001+40*i,"end":29040+40*i} for i in range(16)]


def source():
    d=json.loads(RAW.read_text(encoding="utf-8"))
    assert d["schema"]=="alife-m7-11-full-640-native-aged-cyclic-fault-tolerance-v1"
    assert d["all_640_seed_worlds_16_preregistered_shards_complete"]
    rows=d["worlds"]
    assert [r["seed"] for r in rows]==list(range(FIRST,LAST+1))
    assert len(rows)==640
    return rows


def shard(first,last):
    assert {"start":first,"end":last} in fixed_shards()
    rows=source()
    chosen=rows[first-FIRST:last-FIRST+1]
    assert [r["seed"] for r in chosen]==list(range(first,last+1))
    selected=0
    failures=Counter()
    for i,row in enumerate(chosen):
        parent,ring,meta=scan_fresh_original(row["seed"])
        assert row["selected"]==(parent is not None)
        assert meta["original_initial_full_hash"]==row["scan"]["original_initial_full_hash"]
        assert meta["native_ring_episodes_seen"]==row["scan"]["native_ring_episodes_seen"]
        if parent is None:
            assert meta["reason"]==row["scan"]["reason"]
            failures[meta["reason"]]+=1
        else:
            selected+=1
            source_row=row["native_original_ring"]
            assert meta["selected_tick"]==row["scan"]["selected_tick"]
            assert meta["candidate_aged_rings_same_tick"]==row["scan"]["candidate_aged_rings_same_tick"]
            assert parent.state_hash_full()==row["original_full_hash"]
            assert parent.rng.fingerprint()==row["original_rng"]
            assert parent.rng.draws==row["original_rng_draws"]
            assert list(ring["ids"])==source_row["ids"]
            assert [list(x) for x in ring["edges"]]==source_row["edges"]
            assert ring["age"]==source_row["continuous_snapshot_age"]
            assert ring["exact"]==source_row["exact"]
            assert follow_fixed(parent,ring,row)
        if (i+1)%10==0:
            print(f"M711_AUDIT_SHARD_PROGRESS {first}-{last}: {i+1}/40 fully rechecked",flush=True)
    result={
        "schema":"alife-m7-11-independent-physical-audit-fixed-shard-v1",
        "descriptor":{"start":first,"end":last},
        "sources":40,"selected":selected,
        "full_followup_forks_verified":4*selected,
        "null_reasons":dict(failures),
        "all_worlds_and_forks_matched_original_native_M6_M7_3":True,
        "no_new_statistical_samples":True
    }
    path=BASE/"independent_shards"/f"{first}-{last}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M711_AUDIT_SHARD="+json.dumps(result,sort_keys=True),flush=True)


def merge():
    paths=list((BASE/"independent_shards").glob("*.json"))
    assert len(paths)==16,(len(paths),"exact fixed 16 shards")
    desc=[]
    total=Counter()
    reasons=Counter()
    for path in paths:
        r=json.loads(path.read_text(encoding="utf-8"))
        assert r["schema"]=="alife-m7-11-independent-physical-audit-fixed-shard-v1"
        d=r["descriptor"]
        assert d in fixed_shards() and d not in desc
        desc.append(d)
        assert r["sources"]==40
        assert r["full_followup_forks_verified"]==4*r["selected"]
        assert r["all_worlds_and_forks_matched_original_native_M6_M7_3"]
        total.update({"sources":40,"selected":r["selected"],"forks":r["full_followup_forks_verified"]})
        reasons.update(r["null_reasons"])
    assert all(d in desc for d in fixed_shards())
    assert total=={"sources":640,"selected":626,"forks":2504}
    assert reasons=={"native_cycles_observed_but_none_aged_20_by_600":5,
                     "no_native_simple_4_6_8_ring_by_600":9}
    out={
        "schema":"alife-m7-11-complete-parallel-posthoc-independent-native-audit-v1",
        "original_native_worlds_fully_recreated":640,
        "naturally_aged_rings_identically_reselected":626,
        "null_worlds_reproduced":14,
        "full_original_M6_M7_3_physical_forks_replayed_with_independent_observer":2504,
        "all_16_fixed_audit_shards_pass":True,
        "preregistered_primary_and_secondary_verdict_unchanged":True,
        "same_frozen_640_seed_worlds_not_new_statistical_replication":True,
        "null_reasons":dict(reasons)
    }
    output=BASE/"posthoc_independent_physics_parallel.json"
    output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("M711_AUDIT_FINAL="+json.dumps(out,sort_keys=True),flush=True)


def main():
    p=argparse.ArgumentParser()
    subs=p.add_subparsers(dest="cmd",required=True)
    s=subs.add_parser("shard")
    s.add_argument("--start",required=True,type=int)
    s.add_argument("--end",required=True,type=int)
    subs.add_parser("merge")
    a=p.parse_args()
    if a.cmd=="shard":shard(a.start,a.end)
    else:merge()


if __name__=="__main__":
    main()
