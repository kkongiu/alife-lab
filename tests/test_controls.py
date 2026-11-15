"""M5: controllo positivo, controlli negativi e rilevatore preregistrato."""

from __future__ import annotations

from pathlib import Path

from alife.controls import (
    FIXTURE_VERSION,
    TemplateCopier,
    negative_burst,
    negative_immobile,
    negative_random_aggregation,
    negative_reversible,
    negative_single_species,
    positive_world,
)
from alife.replication import ReplicationDetector
from alife.structures import Tracker
from support import ROOT


def _track(world, steps: int, copier: TemplateCopier | None = None):
    tracker = Tracker()
    detector = ReplicationDetector()
    tracker.observe(world)
    detector.observe(world, tracker)
    for _ in range(steps):
        if copier is not None:
            copier.step(world)
        world.advance(1)
        tracker.observe(world)
        detector.observe(world, tracker)
    return tracker, detector


def _positive(steps: int = 40):
    world = positive_world()
    copier = TemplateCopier.for_world(world)
    tracker, detector = _track(world, steps, copier)
    return world, tracker, detector, copier


def test_positive_control_is_detected() -> None:
    world, tracker, detector, copier = _positive()
    summary = detector.summary()
    assert summary["classified"] == "replication"
    assert summary["persistent"] >= 5
    assert summary["max_generation"] >= 2
    assert summary["candidates"] == copier.copies == 9
    assert world.validate() == []
    assert tracker.summary()["events"]["birth"] >= 10


def test_positive_control_is_reproducible() -> None:
    first = _positive()
    second = _positive()
    assert first[0].state_hash_full() == second[0].state_hash_full()
    assert first[2].summary() == second[2].summary()


def test_negative_immobile_is_not_replication() -> None:
    tracker, detector = _track(negative_immobile(), 100)
    summary = detector.summary()
    assert tracker.summary()["active_structures"] == 0
    assert summary["candidates"] == 0
    assert summary["classified"] == "not_replication"


def test_negative_random_aggregation_is_not_replication() -> None:
    tracker, detector = _track(negative_random_aggregation(), 500)
    summary = detector.summary()
    assert tracker.summary()["active_structures"] > 0
    assert summary["candidates"] == 0
    assert summary["classified"] == "not_replication"


def test_negative_reversible_is_not_replication() -> None:
    tracker, detector = _track(negative_reversible(), 500)
    summary = detector.summary()
    assert tracker.summary()["active_structures"] > 0
    assert summary["classified"] == "not_replication"


def test_negative_stress_cases_are_not_replication() -> None:
    for builder in (negative_single_species, negative_burst):
        tracker, detector = _track(builder(), 400)
        summary = detector.summary()
        assert tracker.summary()["active_structures"] > 0
        assert summary["classified"] == "not_replication"


def test_engine_does_not_import_controls() -> None:
    package = Path(ROOT) / "src" / "alife"
    for path in sorted(package.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        assert "controls" not in source, f"{path.name} importa i controlli"


def test_fixture_version_is_declared() -> None:
    assert FIXTURE_VERSION.startswith("m5-")
