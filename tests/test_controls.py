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
from alife.structures import Signature, Tracker, TrackedStructure
from support import make_energy_config, world_with
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


# --- regressioni sul rilevatore -------------------------------------------


class _FakeTracker:
    """Tracker minimo per testare il rilevatore su stati controllati."""

    def __init__(self) -> None:
        self.active: dict[int, TrackedStructure] = {}
        self.last_births: list[TrackedStructure] = []


def _structure(structure_id: int, particles, born_step: int, key: str = "T:test"):
    size = len(particles)
    return TrackedStructure(
        structure_id=structure_id,
        lineage_id=structure_id,
        born_step=born_step,
        last_step=born_step,
        size=size,
        max_size=size,
        signature=Signature(key, size, size - 1, (), True),
        particles=frozenset(particles),
    )


def test_simultaneous_identical_structures_are_not_copies() -> None:
    """Due strutture identiche nate nello stesso passo non sono l'una copia dell'altra."""
    config = make_energy_config(chemistry={"enabled": False})
    world = world_with(config, [(index, 0) for index in range(8)], [0] * 8)
    tracker = _FakeTracker()
    first = _structure(0, range(4), 0)
    second = _structure(1, range(4, 8), 0)
    tracker.active = {0: first, 1: second}
    tracker.last_births = [first, second]

    detector = ReplicationDetector()
    detector.observe(world, tracker)
    assert detector.summary()["candidates"] == 0


def test_transient_second_generation_does_not_classify() -> None:
    """Una seconda generazione transitoria non deve bastare per la classificazione."""
    config = make_energy_config(chemistry={"enabled": False}, width=16, height=8)
    world = world_with(config, [(index, 0) for index in range(12)], [0] * 12)
    tracker = _FakeTracker()
    detector = ReplicationDetector(persist_steps=10, min_copies=1, min_generation=2)

    template = _structure(0, [0, 1, 2, 3], 0)
    world.step = 1
    first = _structure(1, [4, 5, 6, 7], 1)
    tracker.active = {0: template, 1: first}
    tracker.last_births = [first]
    detector.observe(world, tracker)

    world.step = 2
    second = _structure(2, [8, 9, 10, 11], 2)
    tracker.active = {0: template, 1: first, 2: second}
    tracker.last_births = [second]
    detector.observe(world, tracker)

    # la prima copia muore prima della verifica di persistenza (passo 11)
    world.step = 11
    tracker.active = {0: template, 2: second}
    tracker.last_births = []
    detector.observe(world, tracker)

    # la seconda copia supera la verifica al passo 12
    world.step = 12
    tracker.active = {0: template, 2: second}
    detector.observe(world, tracker)

    summary = detector.summary()
    assert summary["persistent"] == 1
    assert summary["max_generation_all"] == 2
    assert summary["max_generation"] == 0
    assert summary["classified"] == "not_replication"
