"""M7.6 strict held-out replication of the original preregistered M7.5 trial.

No copied or altered natural-source selection or followup physics. Both come
DIRECTLY from unchanged tools.m7_5_mature_feedback; only numeric seed range
and artifact destinations differ. Evaluation also uses original M7.5
summarize() on relabeled-only rows, so decision code is exactly identical.

The relabeling is applied ONLY to the temporary decision input, not the
physical simulation, recorded source rows, full-state hashes, or RNG.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from tools import m7_5_mature_feedback as original

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_6_confirmation"
PFILE=BASE/"protocol.json"
OUT=BASE/"results.json"
SOURCE=ROOT/"tools/m7_5_mature_feedback.py"
OLD_PROTOCOL=ROOT/"campaigns/m7_5_mature/protocol.json"
OLD_SEEDS=range(23001,23321)
NEW_SEEDS=range(24001,24321)


def protocol():
    p=json.loads(PFILE.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-6-heldout-exact-m7-5-growth-replication-v1"
    assert p["status"]=="preregistered_before_runner_or_outcomes"
    held=p["heldout"]
    assert (held["seeds_first"],held["seeds_last"],held["count"])==(24001,24320,320)
    assert held["first_allowed_selection_tick"]==120
    assert held["last_allowed_selection_tick"]==500
    assert held["fork_steps"]==120
    assert held["fork_arms"]==list(original.ARMS)
    assert len(held["fixed_shards"])==8
    old=original.protocol()
    assert (old["design"]["parent_scan_start_tick"],old["design"]["parent_scan_stop_tick"],old["design"]["followup_steps"])==(120,500,120)
    assert original.HORIZON==120
    assert p["integrity"]["use_original_M7_5_selector_and_follow_functions"] is True
    assert all(k not in NEW_SEEDS for k in OLD_SEEDS)
    coverage=[
        s for d in held["fixed_shards"]
        for s in range(d["start"],d["end"]+1)
    ]
    assert coverage==list(NEW_SEEDS)
    return p


def source_provenance():
    return {
        "old_m7_5_source_sha256":sha256(SOURCE.read_bytes()).hexdigest(),
        "old_m7_5_protocol_sha256":sha256(OLD_PROTOCOL.read_bytes()).hexdigest(),
        "new_m7_6_protocol_sha256":sha256(PFILE.read_bytes()).hexdigest()
    }


def heldout_summary(records,p):
    """Use ORIGINAL M7.5 summarizer, with temporary seed-label remapping only.

    That exact original code performs BOTH original preregistered 2/3 gates,
    the minimum n/discordance eligibility, the same source size/topology and
    source flux aggregation. No condition/endpoint logic is rewritten here.
    """
    assert len(records)==320
    assert [r["seed"] for r in records]==list(NEW_SEEDS)
    aliases=[{**row,"seed":23001+i} for i,row in enumerate(records)]
    old_summary=original.summarize(aliases,original.protocol())
    assert old_summary["source_seeds"]==320
    assert old_summary["preregistered_decisions"]["minimum_sources"]==40
    assert old_summary["preregistered_decisions"]["minimum_discordant"]==25
    assert old_summary["preregistered_decisions"]["minimum_favorable_discordance"]=="2/3"
    output={
        **old_summary,
        "physically_simulated_new_seed_first":24001,
        "physically_simulated_new_seed_last":24320,
        "old_seed_aliases_used_only_inside_original_summary":True,
        "preregistered_logic_from_original_M7_5_summarize_unchanged":True,
        "primary_endpoint_unchanged":"coherent_growth_at_120",
        "secondary_endpoint_unchanged":"all_original_bonds_never_broken_120"
    }
    return output


def run_shard(start,end):
    p=protocol()
    desc={"start":start,"end":end}
    assert desc in p["heldout"]["fixed_shards"]
    old=original.protocol()
    source=source_provenance()
    rows=[]
    sham=None
    for seed in range(start,end+1):
        # NOTE: original.study() calls original.select_parent and
        # original.follow, including the ORIGINAL 20-tick age rules.
        row=original.study(seed,old,replay=sham is None)
        assert row["seed"]==seed
        rows.append(row)
        if row["selected"] and sham is None:
            sham=seed
        if (seed-start+1)%10==0:
            print(
                f"M76_PROGRESS {start}-{end} seed={seed}"
                f" selected={sum(r['selected'] for r in rows)}",
                flush=True
            )
    assert len(rows)==end-start+1
    shard={
        "schema":"alife-m7-6-heldout-seed-shard-v1",
        "descriptor":desc,
        "source_provenance":source,
        "worlds":rows,
        "sham_replayed_first_selected_seed":sham,
        "no_original_code_or_physics_change":True
    }
    path=BASE/"shards"/f"seeds-{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(shard,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M76_SHARD="+json.dumps({
        "start":start,"end":end,
        "source_worlds":len(rows),
        "selected":sum(r["selected"] for r in rows),
        "sham_replay_seed":sham
    },sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("seeds-*.json"))
    assert len(files)==8
    provenance=source_provenance()
    seen=[]
    records=[]
    shams=[]
    for path in files:
        shard=json.loads(path.read_text(encoding="utf-8"))
        assert shard["schema"]=="alife-m7-6-heldout-seed-shard-v1"
        assert shard["source_provenance"]==provenance
        assert shard["no_original_code_or_physics_change"] is True
        d=shard["descriptor"]
        assert d in p["heldout"]["fixed_shards"] and d not in seen
        seen.append(d)
        rows=shard["worlds"]
        assert [r["seed"] for r in rows]==list(range(d["start"],d["end"]+1))
        first=next((r["seed"] for r in rows if r["selected"]),None)
        assert shard["sham_replayed_first_selected_seed"]==first
        records.extend(rows)
        if first is not None:
            shams.append(first)
    assert all(d in seen for d in p["heldout"]["fixed_shards"])
    records.sort(key=lambda r:r["seed"])
    summary=heldout_summary(records,p)
    out={
        "schema":"alife-m7-6-confirmatory-320-new-source-seeds-v1",
        "provenance":provenance,
        "worlds":records,
        "sham_replay_first_selected_per_nonempty_shard":shams,
        "summary":summary,
        "all_320_heldout_seeds_included":True,
        "original_M7_5_protocol_and_runner_untouched":True,
        "historic_original_M7_5_result_not_included_in_decision":True
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("M76_FINAL_SUMMARY="+json.dumps(summary,sort_keys=True),flush=True)
    print("M76_SUCCESS="+str(len(records)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="cmd",required=True)
    s=sub.add_parser("shard")
    s.add_argument("--start",type=int,required=True)
    s.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    a=parser.parse_args()
    if a.cmd=="shard":
        run_shard(a.start,a.end)
    else:
        merge()


if __name__=="__main__":
    main()
