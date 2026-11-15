"""M6.2-E: rilevatore v2 per copie progressive, validato sui controlli M5."""

from __future__ import annotations

from alife.controls import (
    TemplateCopier,
    negative_burst,
    negative_immobile,
    negative_random_aggregation,
    negative_reversible,
    negative_single_species,
    positive_world,
)
from alife.replication_v2 import DETECTOR_VERSION, ProgressiveDetector
from alife.structures import Tracker
from support import make_energy_config, world_with


def _run(world, steps: int, copier: TemplateCopier | None = None, detector=None):
    detector = detector or ProgressiveDetector()
    tracker = Tracker()
    tracker.observe(world)
    detector.observe(world, tracker)
    for _ in range(steps):
        if copier is not None:
            copier.step(world)
        world.advance(1)
        tracker.observe(world)
        detector.observe(world, tracker)
    return tracker, detector


def test_detector_version_is_declared() -> None:
    assert DETECTOR_VERSION == "v2"


def test_positive_control_is_detected() -> None:
    world = positive_world()
    tracker, detector = _run(world, 40, TemplateCopier.for_world(world))
    summary = detector.summary()
    assert summary["candidates"] == 9
    assert summary["persistent"] == 9
    assert summary["max_generation"] == 9
    assert summary["classified"] == "replication"


def test_negative_controls_are_not_replication() -> None:
    for builder, steps in (
        (negative_immobile, 100),
        (negative_random_aggregation, 300),
        (negative_reversible, 300),
        (negative_single_species, 300),
        (negative_burst, 300),
    ):
        _, detector = _run(builder(), steps)
        summary = detector.summary()
        assert summary["classified"] == "not_replication", builder.__name__
        assert summary["persistent"] == 0, builder.__name__


def _progressive_world():
    config = make_energy_config(
        width=16,
        height=8,
        species=[
            {"name": "S0", "count": 8, "move_probability": 0.0, "energy": 10, "max_bonds": 2},
            {"name": "S1", "count": 8, "move_probability": 0.0, "energy": 10, "max_bonds": 2},
        ],
        chemistry={"enabled": False},
    )
    positions = [(x, 0) for x in range(4)] + [(x, 2) for x in range(4)]
    species = [0, 1, 1, 0, 0, 1, 1, 0]
    world = world_with(config, positions, species, bonds=[(0, 1, 0), (1, 2, 0), (2, 3, 0)])
    return world


def test_progressive_assembly_is_detected() -> None:
    world = _progressive_world()
    tracker = Tracker()
    detector = ProgressiveDetector(min_copies=1, min_generation=1)
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 1
    world.store.add_bond(4, 5, 0)  # nascita: dimero accanto al template
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 2
    world.store.add_bond(5, 6, 0)  # crescita
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 3
    world.store.add_bond(6, 7, 0)  # raggiunge la firma del template
    tracker.observe(world)
    detector.observe(world, tracker)

    for step in range(4, 14):
        world.step = step
        tracker.observe(world)
        detector.observe(world, tracker)

    summary = detector.summary()
    assert summary["candidates"] == 1
    assert summary["matched"] == 1
    assert summary["persistent"] == 1
    assert summary["max_generation"] == 1
    assert summary["classified"] == "replication"


def test_default_threshold_requires_two_generations() -> None:
    world = _progressive_world()
    tracker = Tracker()
    detector = ProgressiveDetector()
    tracker.observe(world)
    detector.observe(world, tracker)
    world.step = 1
    world.store.add_bond(4, 5, 0)
    tracker.observe(world)
    detector.observe(world, tracker)
    world.step = 2
    world.store.add_bond(5, 6, 0)
    tracker.observe(world)
    detector.observe(world, tracker)
    world.step = 3
    world.store.add_bond(6, 7, 0)
    tracker.observe(world)
    detector.observe(world, tracker)
    for step in range(4, 14):
        world.step = step
        tracker.observe(world)
        detector.observe(world, tracker)

    summary = detector.summary()
    assert summary["persistent"] == 1
    assert summary["max_generation"] == 1
    assert summary["classified"] == "not_replication"


def test_simultaneous_identical_structures_are_not_copies() -> None:
    config = make_energy_config(
        width=16,
        height=8,
        species=[
            {"name": "S0", "count": 8, "move_probability": 0.0, "energy": 10, "max_bonds": 2},
            {"name": "S1", "count": 8, "move_probability": 0.0, "energy": 10, "max_bonds": 2},
        ],
        chemistry={"enabled": False},
    )
    positions = [(x, 0) for x in range(4)] + [(x, 2) for x in range(4)]
    species = [0, 1, 1, 0, 0, 1, 1, 0]
    world = world_with(
        config,
        positions,
        species,
        bonds=[(0, 1, 0), (1, 2, 0), (2, 3, 0), (4, 5, 0), (5, 6, 0), (6, 7, 0)],
    )
    tracker = Tracker()
    detector = ProgressiveDetector()
    tracker.observe(world)
    detector.observe(world, tracker)
    assert detector.summary()["candidates"] == 0


def test_detector_is_deterministic() -> None:
    first = positive_world()
    second = positive_world()
    _, detector_first = _run(first, 40, TemplateCopier.for_world(first))
    _, detector_second = _run(second, 40, TemplateCopier.for_world(second))
    assert detector_first.summary() == detector_second.summary()


def test_match_after_window_is_rejected() -> None:
    """A match at birth+window+1 must not bypass the preregistered bound."""
    world = _progressive_world()
    tracker = Tracker()
    detector = ProgressiveDetector(window=2, min_copies=1, min_generation=1)
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 1
    world.store.add_bond(4, 5, 0)
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 2
    world.store.add_bond(5, 6, 0)
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 4  # birth+3, strictly outside window 2
    world.store.add_bond(6, 7, 0)
    tracker.observe(world)
    detector.observe(world, tracker)

    summary = detector.summary()
    assert summary["candidates"] == 1
    assert summary["matched"] == 0
    assert summary["discarded"]["window_expired"] == 1


def test_matched_copy_must_keep_signature_until_persistence_due() -> None:
    """Same tracker identity is insufficient if the copied graph changes."""
    world = _progressive_world()
    tracker = Tracker()
    detector = ProgressiveDetector(min_copies=1, min_generation=1)
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 1
    world.store.add_bond(4, 5, 0)
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 2
    world.store.add_bond(5, 6, 0)
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 3
    world.store.add_bond(6, 7, 0)
    tracker.observe(world)
    detector.observe(world, tracker)
    assert detector.summary()["matched"] == 1

    world.step = 4
    world.store.remove_bond(6, 7)
    tracker.observe(world)
    detector.observe(world, tracker)

    # The largest fragment retains its tracker identity, but not the copied form.
    for step in range(5, 15):
        world.step = step
        tracker.observe(world)
        detector.observe(world, tracker)

    summary = detector.summary()
    assert summary["matched"] == 1
    assert summary["persistent"] == 0
    assert summary["classified"] == "not_replication"
    assert summary["discarded"]["signature_changed_after_match"] == 1


def test_match_at_exact_window_boundary_is_allowed() -> None:
    world = _progressive_world()
    tracker = Tracker()
    detector = ProgressiveDetector(window=2, min_copies=1, min_generation=1)
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 1
    world.store.add_bond(4, 5, 0)
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 2
    world.store.add_bond(5, 6, 0)
    tracker.observe(world)
    detector.observe(world, tracker)

    world.step = 3  # birth+window, inclusive
    world.store.add_bond(6, 7, 0)
    tracker.observe(world)
    detector.observe(world, tracker)

    assert detector.summary()["matched"] == 1
