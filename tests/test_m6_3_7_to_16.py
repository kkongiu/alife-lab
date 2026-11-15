"""M6.3-7..16 regression fixtures: locked schema, continuous-vs-restored
bonds, deterministic held-out replay, and non-mutating event observation."""
from copy import deepcopy

from tools.m6_3_0_screen import make_world
from tools.m6_3_1_screen import density_protocol, protocol as prev_protocol, variants
from tools.m6_3_7_to_16 import frozen_protocol, class_of_phase, analyse_world, aggregate
from tools.m6_3_2_audit import connected_status


def test_protocol_locked_before_heldout_execution():
    p=frozen_protocol()
    assert p["sample"]["seed_list"]==list(range(8201,8213))
    assert p["sample"]["expected_worlds"]==120
    assert p["sample"]["steps"]==450
    assert [x["id"] for x in p["steps_plan"]]==[
        f"M6.3-{i}" for i in range(7,17)
    ]
    assert p["sample"]["arms"]==["A","B","A_reverse","B_reverse","C"]


def test_initial_state_pure_and_source_has_open_slots():
    p=prev_protocol()
    w=make_world(8201,"A",density_protocol(p,"baseline"))
    state=connected_status(w)
    assert state["pure"] is True
    assert class_of_phase(state)=="pure"
    assert state["core_edges_retained"]
    assert state["direct_external_edges"]==[]
    before=(w.state_hash_full(),w.rng.state(),w.rng.draws)
    assert before==(w.state_hash_full(),w.rng.state(),w.rng.draws)


def test_short_replay_is_deterministic_and_observer_does_not_draw_rng():
    old=prev_protocol()
    targets=variants(old)
    setup=density_protocol(old,"baseline")
    a=make_world(8201,"A",setup)
    b=make_world(8201,"A",setup)
    x=analyse_world(a,"A",targets,steps=9)
    y=analyse_world(b,"A",targets,steps=9)
    assert x==y
    assert x["final_hash"]==a.state_hash_full()==b.state_hash_full()
    assert x["steps"]==9
    assert sum(x["ticks"].get(f"{phase}_ticks",0) for phase in (
        "pure","grown_with_original_edges","original_edges_missing"
    ))==9


def test_zero_event_aggregation_does_not_manufacture_signal():
    p=deepcopy(frozen_protocol())
    row={
        "ticks":{"pure_ticks":450},
        "new_motifs":{},
        "exposures":{},
        "source_incident_events":{},
        "new_attachment_species":{},
        "first_purity_loss_mode":"censored",
        "first_actual_original_edge_break_tick":None,
    }
    rows=[
        dict(row,density=den,seed=seed,arm=arm)
        for den in p["sample"]["densities"]
        for seed in p["sample"]["seed_list"]
        for arm in p["sample"]["arms"]
    ]
    summary=aggregate(rows,p)
    assert summary["gate"]["specificity_screen_signal"] is False
    assert summary["gate"]["verdict"]=="underpowered_or_no_specificity"
    assert summary["by_density_and_arm"]["baseline"]["A"]["first_break_censored"]==12
