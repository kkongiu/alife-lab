"""M7.6 confirmation must execute UNCHANGED M7.5 selection and decision logic."""
from tools import m7_5_mature_feedback as original
from tools.m7_6_heldout_replication import (
    protocol, source_provenance, heldout_summary,
    NEW_SEEDS, OLD_SEEDS
)


def test_frozen_heldout_plan_and_strict_disjointness():
    p=protocol()
    assert p["status"]=="preregistered_before_runner_or_outcomes"
    assert list(NEW_SEEDS)==list(range(24001,24321))
    assert list(OLD_SEEDS)==list(range(23001,23321))
    assert not set(NEW_SEEDS).intersection(OLD_SEEDS)
    assert p["endpoints"]["no_organism_claims"]
    assert p["integrity"]["original_M7_5_module_bytes_unchanged"]
    assert p["integrity"]["original_M7_5_protocol_bytes_unchanged"]
    assert p["integrity"]["master_unchanged"]
    assert p["integrity"]["strict_all_eight_shards_and_320_seeds"]
    assert [s for d in p["heldout"]["fixed_shards"] for s in range(d["start"],d["end"]+1)]==list(NEW_SEEDS)


def test_original_predefined_method_is_the_only_decision_method():
    p=protocol()
    old=original.protocol()
    assert old["design"]["followup_steps"]==p["heldout"]["fork_steps"]==120
    assert old["design"]["parent_scan_start_tick"]==p["heldout"]["first_allowed_selection_tick"]
    assert old["design"]["parent_scan_stop_tick"]==p["heldout"]["last_allowed_selection_tick"]
    assert old["gates"]["no_posthoc_threshold_changes"] and p["endpoints"]["independent_unit"].startswith("Numerical")
    assert p["endpoints"]["primary_gate"].startswith("UNCHANGED M7.5")
    assert p["endpoints"]["secondary_gate"].startswith("UNCHANGED M7.5")
    s=source_provenance()
    assert len(s["old_m7_5_source_sha256"])==64
    assert len(s["old_m7_5_protocol_sha256"])==64
    assert len(s["new_m7_6_protocol_sha256"])==64
    assert len(set(s.values()))==3


def fake(seed,growth_bond,growth_control,survival_bond,survival_control):
    arm={}
    for name in original.ARMS:
        grow=growth_bond if name=="bond_only" else growth_control if name=="no_transfer" else False
        survive=survival_bond if name=="bond_only" else survival_control if name=="no_transfer" else False
        arm[name]={
            "coherent_growth_at_120":grow,
            "ever_coherent_growth":grow,
            "all_original_bonds_never_broken_120":survive,
            "root_incident_new_bond_events":1 if grow else 0,
            "root_incident_bond_events_before_any_original_break":1 if grow and survive else 0,
            "world_new_bonds_120":1 if grow else 0,
            "flux_on_original_bond":1 if name=="bond_only" else 0,
            "flux_internal_root":1 if name=="bond_only" else 0,
            "flux_into_root":0,
            "flux_out_of_root":0,
            "source_net_passive_flow":0
        }
    return {
        "seed":seed,"selected":True,
        "fork_tick":120,
        "source":{"size":7,"cyclomatic_number":0,"original_edges_aged_at_least20":3},
        "outcomes":arm
    }


def test_exact_old_m75_gates_without_new_thresholds():
    p=protocol()
    rows=[]
    for i,seed in enumerate(NEW_SEEDS):
        # 59 paired discordant like M7.5: original code should pass 41 of 59
        bond=i<41
        control=41<=i<59
        rows.append(fake(seed,bond,control,bond,control))
    m=heldout_summary(rows,p)
    assert m["preregistered_decisions"]["coherent_growth_benefit"]=="passed"
    assert m["preregistered_decisions"]["original_bond_survival_benefit"]=="passed"
    assert m["paired_comparisons"]["coherent_growth_at_120"]["favorable_bond_only"]==41
    assert m["paired_comparisons"]["coherent_growth_at_120"]["favorable_no_transfer"]==18
    assert m["paired_comparisons"]["coherent_growth_at_120"]["discordant"]==59
    assert m["physically_simulated_new_seed_first"]==24001
    assert m["physically_simulated_new_seed_last"]==24320

    # Marginally fail fixed criterion, without changing sample or decision logic.
    for i in (0,1):
        rows[i]["outcomes"]["bond_only"]["coherent_growth_at_120"]=False
        rows[i]["outcomes"]["no_transfer"]["coherent_growth_at_120"]=True
    failed=heldout_summary(rows,p)
    assert failed["preregistered_decisions"]["coherent_growth_benefit"]=="not_met_or_underpowered"
    assert failed["preregistered_decisions"]["original_bond_survival_benefit"]=="passed"


def test_one_new_real_seed_uses_original_selector_and_followup_unchanged():
    # This full 120-tick source fork is a software test, not part of the
    # preregistered confirmation sample's statistical counting.
    old=original.protocol()
    record=original.study(24001,old,replay=True)
    assert record["seed"]==24001
    assert record["selected"]
    assert record["fork_tick"]>=120 and record["fork_tick"]<=500
    assert record["source"]["size"]>=5
    assert record["source"]["original_edges_aged_at_least20"]>=2
    assert set(record["outcomes"])==set(original.ARMS)
    assert all(len(r["checkpoints"])==5 for r in record["outcomes"].values())
    first={tuple(tuple(x) for x in r["first_step_original_break_pairs"]) for r in record["outcomes"].values()}
    assert len(first)==1
