"""M4: firme canoniche, componenti, tracciamento ed eventi."""

from __future__ import annotations

import json

from alife.structures import Signature, Tracker, components, signature
from alife.world import World
from support import make_energy_config, world_with

SPECIES = [
    {"name": "S0", "count": 8, "move_probability": 0.0, "energy": 10, "max_bonds": 2},
    {"name": "S1", "count": 8, "move_probability": 0.0, "energy": 10, "max_bonds": 2},
]


def _config():
    return make_energy_config(species=SPECIES, chemistry={"enabled": False})


def _world(positions, species, bonds=()):
    return world_with(_config(), positions, species, bonds=bonds)


def _sig(store, names):
    structures = components(store)
    assert len(structures) == 1
    indices, bonds = structures[0]
    return signature(store, indices, bonds, names)


# --- firme ----------------------------------------------------------------


def test_chain_signature_is_invariant_under_relabeling() -> None:
    first = _world([(0, 0), (1, 0), (2, 0)], [0, 0, 1], bonds=[(0, 1, 4), (1, 2, 4)])
    second = _world([(2, 0), (1, 0), (0, 0)], [1, 0, 0], bonds=[(0, 1, 4), (1, 2, 4)])
    assert _sig(first.store, first.species_names).key == _sig(
        second.store, second.species_names
    ).key


def test_chain_signature_distinguishes_composition() -> None:
    aab = _world([(0, 0), (1, 0), (2, 0)], [0, 0, 1], bonds=[(0, 1, 4), (1, 2, 4)])
    abb = _world([(0, 0), (1, 0), (2, 0)], [0, 1, 1], bonds=[(0, 1, 4), (1, 2, 4)])
    assert _sig(aab.store, aab.species_names).key != _sig(abb.store, abb.species_names).key


def test_tree_signature_distinguishes_shape() -> None:
    chain = _world(
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [0, 1, 0, 0],
        bonds=[(0, 1, 4), (1, 2, 4), (2, 3, 4)],
    )
    star = _world(
        [(1, 1), (1, 0), (0, 1), (2, 1)],
        [1, 0, 0, 0],
        bonds=[(0, 1, 4), (0, 2, 4), (0, 3, 4)],
    )
    chain_sig = _sig(chain.store, chain.species_names)
    star_sig = _sig(star.store, star.species_names)
    assert chain_sig.composition == star_sig.composition
    assert chain_sig.exact and star_sig.exact
    assert chain_sig.key != star_sig.key


def test_cycles_are_fingerprints_not_exact() -> None:
    ring = _world(
        [(0, 0), (1, 0), (1, 1), (0, 1)],
        [0, 1, 0, 1],
        bonds=[(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
    )
    ring_sig = _sig(ring.store, ring.species_names)
    assert ring_sig.exact is False
    assert ring_sig.key.startswith("F:")


# --- tracciamento ---------------------------------------------------------


def test_birth_and_death() -> None:
    world = _world([(0, 0), (1, 0)], [0, 0])
    tracker = Tracker()
    tracker.observe(world)
    assert tracker.summary()["active_structures"] == 0

    world.step = 1
    world.store.add_bond(0, 1, 4)
    tracker.observe(world)
    summary = tracker.summary()
    assert summary["events"]["birth"] == 1
    assert summary["active_structures"] == 1

    world.step = 2
    world.store.remove_bond(0, 1)
    tracker.observe(world)
    summary = tracker.summary()
    assert summary["events"]["death"] == 1
    assert summary["active_structures"] == 0
    assert summary["lifetime"]["completed"] == 1


def test_growth_and_shrink_keep_identity() -> None:
    world = _world([(0, 0), (1, 0), (2, 0)], [0, 0, 0], bonds=[(0, 1, 4)])
    tracker = Tracker()
    tracker.observe(world)
    structure_id = next(iter(tracker.active))

    world.step = 1
    world.store.add_bond(1, 2, 4)
    tracker.observe(world)
    tracked = tracker.active[structure_id]
    assert tracked.size == 3
    assert tracker.summary()["events"]["growth"] == 1

    world.step = 2
    world.store.remove_bond(1, 2)
    tracker.observe(world)
    assert tracker.active[structure_id].size == 2
    assert tracker.summary()["events"]["shrink"] == 1


def test_split_creates_two_structures() -> None:
    world = _world(
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [0, 0, 0, 0],
        bonds=[(0, 1, 4), (1, 2, 4), (2, 3, 4)],
    )
    tracker = Tracker()
    tracker.observe(world)

    world.step = 1
    world.store.remove_bond(1, 2)
    tracker.observe(world)
    summary = tracker.summary()
    assert summary["events"]["split"] == 2
    assert summary["events"].get("death", 0) == 0
    assert summary["active_structures"] == 2


def test_merge_creates_one_structure() -> None:
    world = _world([(0, 0), (1, 0), (2, 0), (3, 0)], [0, 0, 0, 0], bonds=[(0, 1, 4), (2, 3, 4)])
    tracker = Tracker()
    tracker.observe(world)
    assert tracker.summary()["active_structures"] == 2

    world.step = 1
    world.store.add_bond(1, 2, 4)
    tracker.observe(world)
    summary = tracker.summary()
    assert summary["events"]["merge"] == 1
    assert summary["active_structures"] == 1
    assert len(tracker.active[next(iter(tracker.active))].parents) == 2


def test_transform_same_size_new_topology() -> None:
    world = _world(
        [(0, 0), (1, 0), (1, 1), (0, 1)],
        [0, 0, 0, 0],
        bonds=[(0, 1, 4), (1, 2, 4), (2, 3, 4)],
    )
    tracker = Tracker()
    tracker.observe(world)
    before = next(iter(tracker.active))
    was_exact = tracker.active[before].signature.exact

    world.step = 1
    world.store.add_bond(3, 0, 4)
    tracker.observe(world)
    summary = tracker.summary()
    assert summary["events"]["transform"] == 1
    assert tracker.active[before].signature.exact is False
    assert was_exact is True


def test_exact_signature_collision_is_not_ambiguity() -> None:
    world = _world(
        [(0, 0), (1, 0), (4, 4), (5, 4)],
        [0, 0, 0, 0],
        bonds=[(0, 1, 4), (2, 3, 4)],
    )
    tracker = Tracker()
    tracker.observe(world)
    summary = tracker.summary()
    assert summary["signatures"]["ambiguous_structures"] == 0
    assert summary["signatures"]["distinct"] == 1


def test_fuzzy_collision_is_reported_as_ambiguity() -> None:
    world = _world(
        [(0, 0), (1, 0), (1, 1), (0, 1), (5, 5), (6, 5), (6, 6), (5, 6)],
        [0, 1, 1, 0, 0, 1, 1, 0],
        bonds=[
            (0, 1, 4),
            (1, 2, 4),
            (2, 3, 4),
            (3, 0, 4),
            (4, 5, 4),
            (5, 6, 4),
            (6, 7, 4),
            (7, 4, 4),
        ],
    )
    tracker = Tracker()
    tracker.observe(world)
    summary = tracker.summary()
    assert summary["active_structures"] == 2
    assert summary["signatures"]["distinct"] == 1
    assert summary["signatures"]["ambiguous_structures"] == 2
    assert summary["signatures"]["ambiguous_steps"] == 1


def test_tracking_does_not_change_the_world() -> None:
    world = World.create(make_energy_config(species=SPECIES, chemistry={"enabled": False}))
    world.advance(10)
    before = world.snapshot()
    tracker = Tracker()
    tracker.observe(world)
    tracker.observe(world)
    assert world.snapshot() == before


def test_tracker_is_deterministic() -> None:
    config = make_energy_config(species=SPECIES, chemistry={"enabled": False})
    first = World.create(config)
    second = World.create(config)
    first.advance(20)
    second.advance(20)

    tracker_first = Tracker()
    tracker_second = Tracker()
    tracker_first.observe(first)
    tracker_second.observe(second)
    assert tracker_first.summary() == tracker_second.summary()


def test_tracker_writes_jsonl_files(tmp_path) -> None:
    world = _world(
        [(0, 0), (1, 0), (2, 0)],
        [0, 0, 0],
        bonds=[(0, 1, 4), (1, 2, 4)],
    )
    tracker = Tracker(tmp_path)
    tracker.observe(world)
    world.step = 1
    world.store.remove_bond(1, 2)
    tracker.observe(world)
    tracker.close()

    structures = [
        json.loads(line) for line in (tmp_path / "structures.jsonl").read_text().splitlines()
    ]
    lineage = [json.loads(line) for line in (tmp_path / "lineage.jsonl").read_text().splitlines()]
    assert structures[0]["structures"] == 1
    assert {entry["kind"] for entry in lineage} <= {
        "birth",
        "death",
        "growth",
        "shrink",
        "split",
        "merge",
        "transform",
    }
    assert any(entry["kind"] == "shrink" for entry in lineage)


def test_signature_is_a_signature_instance() -> None:
    world = _world([(0, 0), (1, 0)], [0, 0], bonds=[(0, 1, 4)])
    result = _sig(world.store, world.species_names)
    assert isinstance(result, Signature)
    assert result.size == 2
    assert result.bonds == 1


def test_lifetime_counts_steps_alive() -> None:
    world = _world([(0, 0), (1, 0)], [0, 0])
    tracker = Tracker()
    tracker.observe(world)  # passo 0: nessuna struttura
    world.step = 1
    world.store.add_bond(0, 1, 4)
    tracker.observe(world)
    world.step = 2
    tracker.observe(world)
    world.step = 3
    world.store.remove_bond(0, 1)
    tracker.observe(world)

    summary = tracker.summary()
    assert summary["lifetime"]["completed"] == 1
    assert summary["lifetime"]["max"] == 2
    assert summary["lifetime"]["mean"] == 2.0
