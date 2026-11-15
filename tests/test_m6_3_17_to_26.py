"""M6.3-17..26: chemistry visibility, frozen protocol and RNG-safe replay."""
from copy import deepcopy

from alife.chemistry import _candidate_pairs
from tools.m6_3_0_screen import make_world, signature_of_scaffold
from tools.m6_3_1_screen import paired_initial_state
from tools.m6_3_17_to_26 import (
    all_signatures, fixture_protocol, protocol, run_world,
    terminal_s2_opportunities, summarize,
)


def test_protocol_freezes_ten_steps_and_new_seeds():
    p=protocol()
    assert len(p["ten_gates"])==10
    assert [g["step"] for g in p["ten_gates"]]==list(range(17,27))
    assert p["world"]["seed_list"]==list(range(8401,8413))
    assert p["world"]["expected_worlds"]==144
    assert p["world"]["terminal_S1_counts"]=={
        "A":1,"B":1,"A_reverse":1,"B_reverse":1,"C":0,"D":2
    }


def test_four_signatures_and_isoenergetic_six_motifs():
    p=protocol()
    signatures=all_signatures(p)
    assert set(signatures)=={"A","B","C","D"}
    assert len(set(signatures.values()))==4
    for density in p["world"]["densities"]:
        setup=fixture_protocol(p,density)
        worlds=[make_world(8401,arm,setup) for arm in p["world"]["arm_order"]]
        reference=paired_initial_state(worlds[0])
        assert all(paired_initial_state(w)==reference for w in worlds)
        assert all(len(w.store.bonds)==3 and w.dissipated==6 for w in worlds)
        assert all(w.energy()==w.configured_energy()-6 for w in worlds)


def test_initial_A_B_candidate_pairs_equal_and_C_forbids_S2():
    p=protocol()
    for density in p["world"]["densities"]:
        setup=fixture_protocol(p,density)
        for seed in (8401,8402):
            w={arm:make_world(seed,arm,setup)
               for arm in p["world"]["arm_order"]}
            assert list(_candidate_pairs(w["A"]))==list(_candidate_pairs(w["B"]))
            assert list(_candidate_pairs(w["A_reverse"]))==list(
                _candidate_pairs(w["B_reverse"]))
            assert terminal_s2_opportunities(w["C"])["eligible_terminal_S2"]==0
            assert w["C"].species_names[w["C"].store.species[0]]=="S0"
            assert w["D"].species_names[w["D"].store.species[0]]=="S1"


def test_short_observer_is_deterministic_noninvasive():
    p=protocol()
    target=all_signatures(p)
    setup=fixture_protocol(p,"baseline")
    a=make_world(8401,"D",setup)
    b=make_world(8401,"D",setup)
    x=run_world(a,"D",target,duration=11)
    y=run_world(b,"D",target,duration=11)
    assert x==y
    assert a.state_hash_full()==b.state_hash_full()
    assert x["ticks"]==11
    assert sum(x["phase_ticks"].get(f"{phase}_ticks",0)
               for phase in ("pure","grown_with_original_edges",
                             "original_edges_missing"))==11


def test_all_zeros_do_not_produce_mechanism_signal():
    p=deepcopy(protocol())
    datum={
        "initial_s2_opportunities":{"eligible_terminal_S2":0,
                                   "adjacent_terminal_S2":0},
        "terminal_s2_exposure":{},"source_events":{},
        "phase_ticks":{},"first_break_right_censored":True,
        "attachment_species":{},"new_independent_motifs":{},
        "source_terminal_species":["S0","S0"],
    }
    items=[
        dict(datum,density=density,seed=seed,arm=arm)
        for density in p["world"]["densities"]
        for seed in p["world"]["seed_list"]
        for arm in p["world"]["arm_order"]
    ]
    result=summarize(items,p)
    assert result["gate"]["terminal_mechanism_verified"] is False
    assert result["gate"]["hereditary_replication_demonstrated"] is False
