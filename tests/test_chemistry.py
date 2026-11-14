"""Chimica artificiale: formazione, rottura, energia, catalisi, aggregati."""

from __future__ import annotations

from alife import chemistry
from alife.config import load_config
from alife.particles import ParticleStore
from alife.world import World
from support import (
    M2_BASELINE,
    M2_QUICK,
    make_chemistry_config,
    world_with,
)


def test_bond_forms_between_adjacent_allowed_particles() -> None:
    world = world_with(make_chemistry_config(), [(1, 1), (2, 1)], [0, 0])
    formed = chemistry.form_bonds(world)
    assert len(formed) == 1
    assert len(world.store.bonds) == 1
    assert world.store.energy == [8, 8]  # 10 - costo 2 ciascuna
    assert sum(world.store.bonds.values()) == 4  # 2 x costo
    assert sum(world.store.energy) + sum(world.store.bonds.values()) == 20


def test_no_bond_for_non_allowed_species() -> None:
    world = world_with(make_chemistry_config(), [(1, 1), (2, 1)], [1, 1])  # S1-S1 non ammessa
    assert chemistry.form_bonds(world) == []
    assert not world.store.bonds


def test_no_bond_when_species_cannot_bond() -> None:
    config = make_chemistry_config(
        chemistry={
            "enabled": True,
            "bond_cost": 2,
            "formation_probability": 1.0,
            "break_probability": 0.0,
            "allowed_pairs": [["S2", "S2"], ["S0", "S0"]],
            "catalysis": [],
        }
    )
    world = world_with(config, [(1, 1), (2, 1)], [2, 2])  # S2 ha max_bonds 0
    assert chemistry.form_bonds(world) == []


def test_max_bonds_is_respected() -> None:
    species = [
        {"name": "S0", "count": 3, "move_probability": 1.0, "energy": 10, "max_bonds": 1}
    ]
    config = make_chemistry_config(
        species=species,
        chemistry={
            "enabled": True,
            "bond_cost": 1,
            "formation_probability": 1.0,
            "break_probability": 0.0,
            "allowed_pairs": [["S0", "S0"]],
            "catalysis": [],
        },
    )
    world = world_with(config, [(1, 1), (2, 1), (3, 1)], [0, 0, 0])
    chemistry.form_bonds(world)
    assert len(world.store.bonds) == 1
    assert max(world.store.degree) == 1


def test_no_bond_without_enough_energy() -> None:
    world = world_with(
        make_chemistry_config(),
        [(1, 1), (2, 1)],
        [0, 0],
        energy=[1, 10],
    )
    assert chemistry.form_bonds(world) == []


def test_breaking_returns_energy() -> None:
    config = make_chemistry_config(
        chemistry={
            "enabled": True,
            "bond_cost": 2,
            "formation_probability": 0.0,
            "break_probability": 1.0,
            "allowed_pairs": [["S0", "S0"]],
            "catalysis": [],
        }
    )
    world = world_with(config, [(1, 1), (2, 1)], [0, 0], energy=[8, 8], bonds=[(0, 1, 4)])
    world.advance(1)
    assert not world.store.bonds
    assert world.store.energy == [10, 10]
    assert world.bonds_broken_total == 1


def test_bonded_particles_do_not_move() -> None:
    world = world_with(
        make_chemistry_config(),
        [(0, 0), (1, 0), (5, 5)],
        [0, 0, 2],
        energy=[8, 8, 10],
        bonds=[(0, 1, 4)],
    )
    start = [(world.store.xs[i], world.store.ys[i]) for i in range(3)]
    world.advance(10)
    assert [(world.store.xs[i], world.store.ys[i]) for i in (0, 1)] == start[:2]
    assert (world.store.xs[2], world.store.ys[2]) != start[2]


def test_catalysis_multiplies_only_when_adjacent() -> None:
    base_chemistry = {
        "enabled": True,
        "bond_cost": 1,
        "formation_probability": 0.0,
        "break_probability": 0.0,
        "allowed_pairs": [["S0", "S1"]],
        "catalysis": [{"catalyst": "S2", "pair": ["S0", "S1"], "factor": 1e12}],
    }
    world = world_with(
        make_chemistry_config(chemistry=base_chemistry),
        [(1, 1), (2, 1), (1, 2)],
        [0, 1, 2],
    )
    # probabilità base 0: il fattore moltiplicativo non può creare legami dal nulla
    assert chemistry.form_bonds(world) == []

    boosted = dict(base_chemistry)
    boosted["formation_probability"] = 1e-12  # 1e-12 x 1e12 = 1.0
    world = world_with(
        make_chemistry_config(chemistry=boosted),
        [(1, 1), (2, 1), (1, 2)],
        [0, 1, 2],
    )
    assert len(chemistry.form_bonds(world)) == 1

    far_away = world_with(
        make_chemistry_config(chemistry=boosted),
        [(1, 1), (2, 1), (6, 6)],
        [0, 1, 2],
    )
    assert chemistry.form_bonds(far_away) == []


def test_aggregate_statistics() -> None:
    store = ParticleStore(
        8,
        8,
        [0, 1, 2, 3, 4, 5],
        [1, 2, 4, 5, 6, 0],
        [1, 1, 4, 4, 6, 0],
        [0, 0, 0, 0, 0, 0],
        [10, 10, 10, 10, 10, 10],
        [(0, 1, 4), (2, 3, 4)],
    )
    stats = chemistry.aggregate_stats(store)
    assert stats["bonds"] == 2
    assert stats["aggregates"] == 2
    assert stats["largest_aggregate"] == 2
    assert stats["size_distribution"] == {"2": 2}
    assert stats["free_particles"] == 2
    assert stats["bonded_particles"] == 4


def test_chains_grow_to_max_bonds() -> None:
    species = [
        {"name": "S0", "count": 4, "move_probability": 0.0, "energy": 10, "max_bonds": 2}
    ]
    config = make_chemistry_config(
        species=species,
        chemistry={
            "enabled": True,
            "bond_cost": 1,
            "formation_probability": 1.0,
            "break_probability": 0.0,
            "allowed_pairs": [["S0", "S0"]],
            "catalysis": [],
        },
    )
    world = world_with(config, [(1, 1), (2, 1), (3, 1), (4, 1)], [0, 0, 0, 0])
    chemistry.form_bonds(world)
    assert len(world.store.bonds) == 3  # catena lineare completa
    assert world.store.degree == [1, 2, 2, 1]


def test_m2_quick_is_deterministic() -> None:
    first = World.create(load_config(M2_QUICK))
    second = World.create(load_config(M2_QUICK))
    first.advance(200)
    second.advance(200)
    assert first.state_hash_full() == second.state_hash_full()
    assert first.snapshot() == second.snapshot()
    assert len(first.store.bonds) > 0


def test_m2_baseline_produces_structures_and_conserves_energy() -> None:
    world = World.create(load_config(M2_BASELINE))
    world.advance(500)
    stats = world.aggregates()
    assert stats["bonds"] > 0
    assert stats["aggregates"] > 0
    assert stats["largest_aggregate"] >= 2
    assert world.energy() == world.configured_energy()
    assert not world.validate()


def test_catalysis_config_changes_chemistry() -> None:
    import json

    from alife.config import Config

    # regime limitato dalla probabilità, non dagli slot: senza catalisi non si
    # forma praticamente nulla, con la catalisi la coppia S0-S1 si forma
    raw = json.loads(M2_QUICK.read_text())
    raw["chemistry"]["formation_probability"] = 1e-9
    raw["chemistry"]["catalysis"] = []
    plain = World.create(Config.from_dict(raw).validate())

    raw = json.loads(M2_QUICK.read_text())
    raw["chemistry"]["formation_probability"] = 1e-9
    raw["chemistry"]["catalysis"] = [
        {"catalyst": "S3", "pair": ["S0", "S1"], "factor": 1e9}
    ]
    catalyzed = World.create(Config.from_dict(raw).validate())

    plain.advance(300)
    catalyzed.advance(300)
    assert plain.bonds_formed_total == 0
    assert catalyzed.bonds_formed_total > 0
