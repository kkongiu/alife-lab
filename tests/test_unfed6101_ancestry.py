"""P2: tests for material genealogy (not reproductive genealogy)."""
from alife.structures import Tracker
from tools.trace_unfed6101_ancestry import (
    SIX, TEMPLATE, CHILD_SEED, common_ancestor_status, contiguous_episodes,
)
from support import make_energy_config, world_with


def test_contiguous_episode_boundaries_are_inclusive():
    observations = [
        {"step": n, "flag": n in (2, 3, 5)}
        for n in range(7)
    ]
    assert contiguous_episodes(observations, "flag") == [
        {"first": 2, "last": 3},
        {"first": 5, "last": 5},
    ]


def test_separated_fragments_are_not_a_shared_ancestor():
    # Two dimers: one contains an earlier template participant and the other
    # contains a future child participant. Physical overlap is absent.
    sp = [
        {"name": "A", "count": max(SIX) + 1, "move_probability": 0,
         "energy": 10, "max_bonds": 2},
    ]
    cfg = make_energy_config(
        width=32, height=32, species=sp,
        chemistry={"enabled": True, "bond_cost": 0,
                   "formation_probability": 0, "break_probability": 0,
                   "allowed_pairs": [["A", "A"]], "catalysis": []},
    )
    pos = [(i % 32, i // 32) for i in range(max(SIX) + 1)]
    w = world_with(cfg, pos, [0] * len(pos), bonds=[
        (TEMPLATE[0], TEMPLATE[1], 0),
        (CHILD_SEED[0], CHILD_SEED[1], 0),
    ])
    t = Tracker()
    t.observe(w)
    a = common_ancestor_status(t)
    assert a["shared_cross_component"] is False
    assert a["all_six_same_component"] is False
    assert a["seed_pair_same_component"] is True


def test_true_common_component_requires_all_six_connected():
    # Choose a compact 2x3 network: particle IDs are canonical identity,
    # while store indices remain 0..5; the tracker must ignore ID ordering.
    cfg = make_energy_config(
        width=8, height=8, species=[
            {"name": "A", "count": 6, "move_probability": 0,
             "energy": 10, "max_bonds": 2},
        ],
        chemistry={"enabled": True, "bond_cost": 0,
                   "formation_probability": 0, "break_probability": 0,
                   "allowed_pairs": [["A", "A"]], "catalysis": []},
    )
    ids = list(SIX)
    pos = [(i, 0) for i in range(6)]
    w = world_with(cfg, pos, [0] * 6,
                   bonds=[(ids[i], ids[i+1], 0) for i in range(5)],
                   ids=ids)
    t = Tracker()
    t.observe(w)
    status = common_ancestor_status(t)
    assert status["all_six_same_component"] is True
    assert status["shared_cross_component"] is True
    assert status["seed_pair_same_component"] is True
    assert status["common_component"]["size"] == 6
