"""M6.4 exact-cycle detector v2: read-only dual-tracker verification.

Reanalyses (NOT independent replication) the 24 historical natural-ring
conditions. Legacy Tracker and signature() remain unchanged by default.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from alife.structures import ExactCycleTrackerV2, Tracker
from tools.m6_4_cycles import create_natural, protocol

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"campaigns/m6_4_cycles/detector_v2_audit.json"


def run():
    p=protocol()
    rows=[]
    for density in p["world"]["densities"]:
        for seed in p["world"]["seeds"]:
            w=create_natural(seed,density,p)
            original=Tracker()
            corrected=ExactCycleTrackerV2()
            initial_state=w.state_hash_full()
            def observe(world):
                draws=world.rng.draws
                original.observe(world)
                corrected.observe(world)
                assert world.rng.draws==draws
            w.advance(p["world"]["steps"],observer=observe)
            w.check()
            a,b=original.summary(),corrected.summary()
            # The existing tracker uses particles, not signatures, for
            # its continuity / birth/merge/split. That must not change.
            for k in ("birth","death","growth","shrink","merge","split"):
                assert a["events"].get(k,0)==b["events"].get(k,0)
            assert a["steps_tracked"]==b["steps_tracked"]==p["world"]["steps"]
            assert b["signatures"]["exact_observations"]>=a["signatures"]["exact_observations"]
            assert b["signatures"]["fuzzy_observations"]<=a["signatures"]["fuzzy_observations"]
            row={
                "density":density,"seed":seed,
                "world_hash_start":initial_state,
                "world_hash_end":w.state_hash_full(),
                "rng_fingerprint_end":w.rng.fingerprint(),
                "rng_draws_end":w.rng.draws,
                "old":a["signatures"],
                "new":b["signatures"],
                "old_events":a["events"],
                "new_events":b["events"],
                "difference_in_distinct_signature_keys":
                    b["signatures"]["distinct"]-a["signatures"]["distinct"],
            }
            rows.append(row)
            print(f"{density}/{seed}: legacy {a['signatures']['distinct']}, v2 {b['signatures']['distinct']}",flush=True)
    replay=[]
    for density,seed in p["integrity"]["replay_fixed"]:
        row=next(r for r in rows if r["density"]==density and r["seed"]==seed)
        w=create_natural(seed,density,p)
        w.advance(p["world"]["steps"])
        w.check()
        assert w.state_hash_full()==row["world_hash_end"]
        assert w.rng.fingerprint()==row["rng_fingerprint_end"]
        assert w.rng.draws==row["rng_draws_end"]
        replay.append({"density":density,"seed":seed,"hash":w.state_hash_full()})
    report={
        "schema":"m6-4-detector-v2-retrospective-v1",
        "provenance":"same 24 M6.4 natural worlds, new observer only",
        "n_worlds":len(rows),
        "summary":{
            "old_exact_observations":sum(r["old"]["exact_observations"] for r in rows),
            "new_exact_observations":sum(r["new"]["exact_observations"] for r in rows),
            "old_fuzzy_observations":sum(r["old"]["fuzzy_observations"] for r in rows),
            "new_fuzzy_observations":sum(r["new"]["fuzzy_observations"] for r in rows),
            "old_distinct_keys_sum_per_world":sum(r["old"]["distinct"] for r in rows),
            "new_distinct_keys_sum_per_world":sum(r["new"]["distinct"] for r in rows),
            "worlds_with_more_distinct_keys":sum(r["difference_in_distinct_signature_keys"]>0 for r in rows),
        },
        "reference_replay":replay,
        "runs":rows,
        "laws_unchanged":True,
        "legacy_tracker_default_unchanged":True,
        "no_heredity_claim":True
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("EXACT_CYCLE_DETECTOR_V2_SUMMARY="+json.dumps(report["summary"],sort_keys=True),flush=True)
    return report


if __name__=="__main__":
    run()
