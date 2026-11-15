"""P0 regression gates for the strictly versioned progressive detector v2.1.

Manual fixtures manipulate bonds only in isolated tests; this does not alter
the ALife physical engine or count as natural replication evidence.
"""
from __future__ import annotations

import pytest

from alife.controls import (
    TemplateCopier, positive_world, negative_immobile,
    negative_random_aggregation, negative_reversible,
    negative_single_species, negative_burst,
)
from alife.replication_v21 import ProgressiveDetector
from alife.structures import Tracker
from support import make_energy_config, world_with


def _world(with_bridge=False):
    """One 4-particle template and prospective child with exact same tree sig."""
    positions = ([(x, 0) for x in range(4)]
                 + [(0, 2), (1, 2), (1, 3), (0, 3)]
                 + ([(1, 1)] if with_bridge else []))
    species = [0, 1, 1, 0, 0, 1, 1, 0] + ([0] if with_bridge else [])
    config = make_energy_config(
        width=12, height=8,
        species=[
            {"name": "S0", "count": species.count(0),
             "move_probability": 0.0, "energy": 10, "max_bonds": 2},
            {"name": "S1", "count": species.count(1),
             "move_probability": 0.0, "energy": 10, "max_bonds": 2},
        ],
        chemistry={"enabled": False},
    )
    return world_with(config, positions, species,
                      bonds=[(0, 1, 0), (1, 2, 0), (2, 3, 0)])


def _observe(w, tracker, detector, step):
    w.step = step
    tracker.observe(w)
    detector.observe(w, tracker)


def _matched(with_bridge=False):
    w = _world(with_bridge)
    t, d = Tracker(), ProgressiveDetector(min_copies=1, min_generation=1)
    _observe(w, t, d, 0)
    w.store.add_bond(4, 5, 0)
    _observe(w, t, d, 1)
    w.store.add_bond(5, 6, 0)
    _observe(w, t, d, 2)
    w.store.add_bond(6, 7, 0)
    _observe(w, t, d, 3)
    assert d.summary()["matched"] == 1
    return w, t, d


def test_v21_break_and_restore_signature_does_not_count_as_continuous():
    w, t, d = _matched()
    w.store.add_bond(4, 7, 0)  # temporary cycle, same members and tracker ID
    _observe(w, t, d, 4)
    w.store.remove_bond(4, 7)
    _observe(w, t, d, 5)
    for s in range(6, 15):
        _observe(w, t, d, s)
    assert d.candidates[0].persistent is False
    assert d.candidates[0].discarded == "signature_changed_after_match"
    assert d.summary()["classified"] == "not_replication"


def test_v21_split_rejects_matched_copy():
    w, t, d = _matched()
    w.store.remove_bond(6, 7)
    _observe(w, t, d, 4)
    for s in range(5, 15):
        _observe(w, t, d, s)
    assert d.summary()["persistent"] == 0
    assert d.candidates[0].persistent is False


def test_v21_merge_rejects_matched_copy():
    w, t, d = _matched(with_bridge=True)
    # Adjacent bridge spans y=0(template) to y=2(child). Merging does not
    # create a new daughter, and cannot preserve original child identity.
    w.store.add_bond(5, 8, 0)
    w.store.add_bond(8, 1, 0)
    _observe(w, t, d, 4)
    assert d.candidates[0].persistent is False
    assert d.summary()["persistent"] == 0


def test_v21_equidistant_parent_templates_are_reported_as_ambiguous():
    positions = [(x, 0) for x in range(4)] + [
        (x, 4) for x in range(4)
    ] + [(x, 2) for x in range(4)]
    species = [0, 1, 1, 0] * 3
    config = make_energy_config(
        width=12, height=8,
        species=[
            {"name": "S0", "count": 6, "move_probability": 0.0,
             "energy": 10, "max_bonds": 2},
            {"name": "S1", "count": 6, "move_probability": 0.0,
             "energy": 10, "max_bonds": 2},
        ],
        chemistry={"enabled": False},
    )
    w = world_with(config, positions, species, bonds=[
        (0, 1, 0), (1, 2, 0), (2, 3, 0),
        (4, 5, 0), (5, 6, 0), (6, 7, 0),
    ])
    t, d = Tracker(), ProgressiveDetector()
    _observe(w, t, d, 0)
    w.store.add_bond(8, 9, 0)
    _observe(w, t, d, 1)
    assert d.summary()["candidates"] == 1
    assert d.summary()["ambiguous_births"] == 1
    assert d.candidates[0].ambiguous_templates is True
    assert d.candidates[0].template == 0  # deterministic tie-break, not cause


@pytest.mark.parametrize("builder,steps", [
    (negative_immobile, 100), (negative_random_aggregation, 300),
    (negative_reversible, 300), (negative_single_species, 300),
    (negative_burst, 300),
])
def test_v21_m5_negative_controls(builder, steps):
    w, t, d = builder(), Tracker(), ProgressiveDetector()
    _observe(w, t, d, 0)
    for _ in range(steps):
        w.advance(1)
        t.observe(w)
        d.observe(w, t)
    assert d.summary()["persistent"] == 0
    assert d.summary()["classified"] == "not_replication"


def test_v21_m5_positive_detects_control_not_natural_replicator():
    w = positive_world()
    copier = TemplateCopier.for_world(w)
    t, d = Tracker(), ProgressiveDetector()
    _observe(w, t, d, 0)
    for _ in range(40):
        copier.step(w)
        w.advance(1)
        t.observe(w)
        d.observe(w, t)
    assert d.summary()["classified"] == "replication"
    assert d.summary()["persistent"] >= 5
    assert d.summary()["max_generation"] >= 2
