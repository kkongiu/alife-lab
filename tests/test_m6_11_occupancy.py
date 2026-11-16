"""M6.11 occupancy audit: synthetic controls, frozen protocol and observer purity."""
from tools.m6_11_occupancy import (
    CLOCKWISE, center_occupation, fixed_time_shells, previous_center,
    protocol, shell_class, shell_edges, shell_from_snapshot, snapshot,
    study_world, summarize
)
from tools.m6_10_pockets import BORDER_OFFSETS
from tools.m6_4_cycles import create_natural, protocol as natural_protocol
from test_m6_10_pockets import synthetic_pocket


def test_frozen_sampling():
    p = protocol()
    assert len(p["sample"]["seeds"]) == 100
    assert p["sample"]["expected_worlds"] == 200
    assert p["sample"]["fixed_checkpoint_stride"] == 20
    assert p["integrity"]["no_changes_to_master_or_src"] is True


def test_native_exact_ring_shell_and_mobile_resident():
    w = synthetic_pocket()
    s = w.store
    bonds = {tuple(sorted((s.ids[a],s.ids[b]))) for a,b in s.bonds}
    assert len(CLOCKWISE) == len(BORDER_OFFSETS) == 8
    assert shell_edges(s,(3,3),bonds) == 8
    occ = center_occupation(s,(3,3),w.config.species)
    assert occ["id"] == 8 and occ["mobile"] and occ["degree"] == 0
    counts,_ = fixed_time_shells(w)
    assert counts["8_shells"] == 1
    assert counts["8_free_mobile"] == 1
    snap = snapshot(s)
    assert shell_from_snapshot(snap,(3,3),s.width,s.height) == 8
    assert previous_center(snap,(3,3),w)["free_mobile"] is True


def test_empty_center_and_torus_wrapping():
    w = synthetic_pocket(cx=0,cy=0,empty=True)
    s = w.store
    bonds = {tuple(sorted((s.ids[a],s.ids[b]))) for a,b in s.bonds}
    assert shell_edges(s,(0,0),bonds) == 8
    assert center_occupation(s,(0,0),w.config.species)["id"] is None
    counts,_ = fixed_time_shells(w)
    assert counts["8_empty"] == 1
    assert shell_class(2) == "0-5"
    assert shell_class(6) == "6"
    assert shell_class(7) == "7"


def test_partial_shell_with_seven_edges_not_classed_complete():
    w = synthetic_pocket(empty=True)
    s = w.store
    key = next(iter(s.bonds))
    s.remove_bond(*key)
    w.check()
    bonds = {tuple(sorted((s.ids[a],s.ids[b]))) for a,b in s.bonds}
    assert shell_edges(s,(3,3),bonds) == 7
    counts,_ = fixed_time_shells(w)
    assert counts["7_shells"] == 1
    assert counts["8_shells"] == 0


def test_short_natural_run_does_not_mutate_physics():
    p = natural_protocol()
    a = create_natural(10001,"baseline",p)
    b = create_natural(10001,"baseline",p)
    result = study_world(a,steps=3,stride=1)
    b.advance(3)
    b.check()
    assert result["final"]["hash"] == b.state_hash_full()
    assert result["final"]["rng"] == b.rng.fingerprint()
    assert result["final"]["draws"] == b.rng.draws
    assert result["final"]["energy"] == b.energy()
    assert len(result["fixed_shell_counts"]) >= 0


def test_world_level_gate_and_missing_controls():
    p = protocol()
    null = {"density":"baseline","seed":10001,"result":{
        "pocket_episodes":[], "birth_counts":{},
        "distinct_pocket_material_sets":0, "fixed_shell_counts":{}
    }}
    summary = summarize([null],p)
    assert summary["decision"] == "no_confirmed_trapping"
    assert summary["by_density"]["baseline"]["fixed_checkpoint_shells"]["7"]["empty_fraction"] is None
    ep = {"center_id":8,"center_mobile":True,"duration_ticks":35,"right_censored":False}
    one = dict(null, result={**null["result"],"pocket_episodes":[ep]})
    assert summarize([one],p)["decision"] == "one_case"
    two = dict(one,seed=10002)
    assert summarize([one,two],p)["decision"] == "replicated_native_geometric_trapping_only"
