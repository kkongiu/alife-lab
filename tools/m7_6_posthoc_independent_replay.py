"""POSTHOC independent physical audit of the fixed M7.6 heldout replication.

Uses M7.5's SEPARATE posthoc implementation, which reruns native sources
from seed, applies ORIGINAL M7.3 conduction and traverses source material
connectivity independently of the M7.5 outcome observer. This verifies the
new source/FORK records but introduces no new independent seeds. M7.6's
pre-registered verdict remains exactly as saved in the primary artifact.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from tools.m7_5_posthoc_independent_replay import verify as verify_original_physics

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_6_confirmation"
SOURCE=BASE/"results.json"
OUT=BASE/"posthoc_independent_replay.json"


def run():
    primary=json.loads(SOURCE.read_text(encoding="utf-8"))
    assert primary["schema"]=="alife-m7-6-confirmatory-320-new-source-seeds-v1"
    assert primary["original_M7_5_protocol_and_runner_untouched"] is True
    assert primary["historic_original_M7_5_result_not_included_in_decision"] is True
    worlds=primary["worlds"]
    assert len(worlds)==320
    assert [r["seed"] for r in worlds]==list(range(24001,24321))
    complete=[]
    for i,r in enumerate(worlds):
        assert r["selected"],(r["seed"],"unexpected missing selected cohort: posthoc audit needs separately coded null handling")
        complete.append(verify_original_physics(r))
        if (i+1)%20==0:
            print(f"M76_INDEPENDENT_PROGRESS verified={i+1}/320",flush=True)
    assert len(complete)==320
    growth=Counter((
        x["arms"]["bond_only"]["growth"],x["arms"]["no_transfer"]["growth"]
    ) for x in complete)
    bonds=Counter((
        x["arms"]["bond_only"]["original_edges_unbroken"],
        x["arms"]["no_transfer"]["original_edges_unbroken"]
    ) for x in complete)
    src=primary["summary"]["paired_comparisons"]
    def compare(counts,expected):
        assert counts[(True,False)]==expected["favorable_bond_only"]
        assert counts[(False,True)]==expected["favorable_no_transfer"]
        assert counts[(True,True)]==expected["both"]
        assert counts[(False,False)]==expected["neither"]
    compare(growth,src["coherent_growth_at_120"])
    compare(bonds,src["all_original_bonds_unbroken_120"])
    out={
        "schema":"alife-m7-6-heldout-posthoc-320-source-960-fork-physical-audit-v1",
        "full_independent_replay_of_same_320_not_new_seeds":True,
        "original_M7_3_energy_transfer_used_not_M7_5_fork_tracer":True,
        "separate_independent_original_material_graph_traversal":True,
        "all_320_parent_source_full_hash_rng_recreated":True,
        "all_960_fork_full_hash_rng_energy_break_growth_recreated":True,
        "original_preregistered_main_decisions_unmodified":True,
        "replayed_source_worlds":320,"replayed_forks":960,
        "matched_growth_discordants":{
            "bond_only_only":growth[(True,False)],
            "no_transfer_only":growth[(False,True)],
            "both":growth[(True,True)],
            "neither":growth[(False,False)]
        },
        "matched_original_survival_discordants":{
            "bond_only_only":bonds[(True,False)],
            "no_transfer_only":bonds[(False,True)],
            "both":bonds[(True,True)],
            "neither":bonds[(False,False)]
        },
        "results":complete
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("M76_INDEPENDENT_FINAL="+json.dumps({
        "replayed_sources":320,
        "replayed_forks":960,
        "bond_only_growth_only":growth[(True,False)],
        "no_transfer_growth_only":growth[(False,True)],
        "all_verified":True
    },sort_keys=True),flush=True)


if __name__=="__main__":
    run()
