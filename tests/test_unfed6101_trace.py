"""Unit checks for the non-mutating unfed-6101 trace utilities."""
from __future__ import annotations

from alife.structures import Tracker
from tools.trace_unfed6101 import (
    _distance_positions, ReadOnlyEventCollector, snapshot, structure_containing,
    WATCH_IDS, START_STEP,
)
from support import make_energy_config, world_with


def test_periodic_distance_uses_shorter_wraparound():
    assert _distance_positions((0, 0), (7, 0), 8, 8, True) == 1
    assert _distance_positions((0, 0), (7, 0), 8, 8, False) == 7


def test_structure_containing_requires_all_particles_in_one_component():
    config = make_energy_config(
        width=8, height=8, species=[
            {"name": "S0", "count": 4, "move_probability": 0.0,
             "energy": 10, "max_bonds": 2},
        ],
        chemistry={"enabled": True, "bond_cost": 0,
                   "formation_probability": 0.0, "break_probability": 0.0,
                   "allowed_pairs": [["S0", "S0"]], "catalysis": []},
    )
    world = world_with(config, [(0, 0), (1, 0), (4, 0), (5, 0)], [0] * 4,
                       bonds=[(0, 1, 0), (2, 3, 0)])
    tracker = Tracker()
    tracker.observe(world)
    assert structure_containing(tracker, (0, 1)) is not None
    assert structure_containing(tracker, (1, 2)) is None
    assert structure_containing(tracker, (99,)) is None


def test_event_collector_records_post_advance_step_without_consuming_rng():
    # WATCH_IDS are fixed to the known 1400-particle M6 case. This tiny
    # fixture checks the event counter, not incident relevance.
    config = make_energy_config(
        width=8, height=8, species=[
            {"name": "S0", "count": 2, "move_probability": 0.0,
             "energy": 10, "max_bonds": 2},
        ],
        chemistry={"enabled": True, "bond_cost": 0,
                   "formation_probability": 1.0, "break_probability": 0.0,
                   "allowed_pairs": [["S0", "S0"]], "catalysis": []},
    )
    world = world_with(config, [(0, 0), (1, 0)], [0, 0])
    world.step = START_STEP - 2
    sink = ReadOnlyEventCollector(world)
    world.event_sink = sink
    # Event is emitted at old step=769, visible in observed step=770.
    world.advance(1)
    before = world.rng.draws
    assert sink.counts.get(START_STEP, {}).get("form") == 1
    assert world.step == START_STEP - 1
    assert world.rng.draws == before
    world.check()
