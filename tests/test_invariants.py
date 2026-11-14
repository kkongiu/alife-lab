"""Invarianti fisiche e computazionali, incluso il rilevamento di violazioni."""

from __future__ import annotations

import pytest

from alife.config import load_config
from alife.particles import InvariantError, ParticleStore
from alife.world import World
from support import M2_QUICK, make_config


def test_particle_count_conserved() -> None:
    world = World.create(make_config())
    initial = len(world.store)
    world.advance(150)
    assert len(world.store) == initial
    assert world.validate() == []


def test_species_quantities_conserved() -> None:
    world = World.create(make_config())
    initial = world.counts()
    world.advance(150)
    assert world.counts() == initial == {"A": 12, "B": 8}


def test_no_multiple_occupancy() -> None:
    world = World.create(make_config())
    world.advance(150)
    assert world.store.occupied_cells() == len(world.store)
    assert len(set(zip(world.store.xs, world.store.ys))) == len(world.store)


def test_periodic_boundaries() -> None:
    world = World.create(make_config(boundary="periodic", width=20, height=20))
    world.advance(200)
    assert all(0 <= x < 20 for x in world.store.xs)
    assert all(0 <= y < 20 for y in world.store.ys)


def test_energy_is_conserved() -> None:
    world = World.create(make_config())
    initial = world.energy()
    assert initial == world.configured_energy()
    for _ in range(10):
        world.advance(20)
        assert world.energy() == initial
    assert world.validate() == []


def test_state_hash_is_stable_and_sensitive() -> None:
    world = World.create(make_config())
    first = world.state_hash()
    assert first == world.state_hash()
    world.advance(1)
    assert world.state_hash() != first


def test_validate_detects_duplicate_cell() -> None:
    world = World.create(make_config())
    world.store.xs[1] = world.store.xs[0]
    world.store.ys[1] = world.store.ys[0]
    problems = world.validate()
    assert problems
    with pytest.raises(InvariantError, match="non valido"):
        world.check()


def test_validate_detects_out_of_bounds_particle() -> None:
    world = World.create(make_config())
    world.store.xs[0] = -1
    assert any("fuori griglia" in problem for problem in world.validate())


def test_validate_detects_grid_desynchronisation() -> None:
    world = World.create(make_config())
    cell = world.store.ys[0] * world.store.width + world.store.xs[0]
    world.store.grid[cell] = 999
    assert any("griglia indica" in problem for problem in world.validate())


def test_validate_detects_missing_particle() -> None:
    world = World.create(make_config())
    arrays = (
        world.store.ids,
        world.store.xs,
        world.store.ys,
        world.store.species,
        world.store.energy,
        world.store.degree,
    )
    for array in arrays:
        array.pop()
    problems = world.validate()
    assert any("conteggi" in problem for problem in problems)
    assert any("griglia" in problem for problem in problems)


def test_validate_detects_invalid_species_index() -> None:
    world = World.create(make_config())
    world.store.species[0] = 7
    assert any("specie 7 inesistente" in problem for problem in world.validate())


def test_store_rejects_double_placement() -> None:
    with pytest.raises(InvariantError, match="doppia occupazione"):
        ParticleStore(4, 4, [0, 1], [1, 1], [1, 1], [0, 0], [5, 5])


def test_store_rejects_out_of_grid_particle() -> None:
    with pytest.raises(InvariantError, match="fuori griglia"):
        ParticleStore(4, 4, [0], [4], [0], [0], [5])


# --- M2: legami, energia, identità -----------------------------------------


def test_energy_with_bonds_is_conserved() -> None:
    world = World.create(load_config(M2_QUICK))
    world.advance(300)
    assert world.energy_bonds() > 0
    assert world.energy_particles() + world.energy_bonds() == world.configured_energy()
    assert world.energy() == world.configured_energy()
    assert world.validate() == []


def test_validate_detects_non_adjacent_bond() -> None:
    world = World.create(load_config(M2_QUICK))
    pair = next(
        (i, j)
        for i in range(len(world.store))
        for j in range(i + 1, len(world.store))
        if not world._adjacent(i, j)
    )
    world.store.add_bond(pair[0], pair[1], 0)
    assert any("non adiacenti" in problem for problem in world.validate())


def test_validate_detects_bond_beyond_max_bonds() -> None:
    world = World.create(load_config(M2_QUICK))
    pair = next(
        (index_a, index_b)
        for index_a in range(len(world.store))
        for index_b in range(index_a + 1, len(world.store))
        if world._adjacent(index_a, index_b)
        and (
            world.max_bonds[world.store.species[index_a]] == 0
            or world.max_bonds[world.store.species[index_b]] == 0
        )
    )
    world.store.add_bond(pair[0], pair[1], 0)
    assert any("oltre il massimo" in problem for problem in world.validate())


def test_validate_detects_degree_mismatch() -> None:
    world = World.create(load_config(M2_QUICK))
    world.store.degree[0] = 1
    assert any("grado" in problem for problem in world.validate())


def test_validate_detects_bonds_without_chemistry() -> None:
    world = World.create(make_config())
    pair = next(
        (index_a, index_b)
        for index_a in range(len(world.store))
        for index_b in range(index_a + 1, len(world.store))
        if world._adjacent(index_a, index_b)
    )
    world.store.add_bond(pair[0], pair[1], 0)
    assert any("chimica disabilitata" in problem for problem in world.validate())


def test_validate_detects_identity_above_next_id() -> None:
    world = World.create(load_config(M2_QUICK))
    world.next_id = 0
    assert any("next_id" in problem for problem in world.validate())


def test_store_rejects_duplicate_identifiers() -> None:
    with pytest.raises(InvariantError, match="identificativo duplicato"):
        ParticleStore(4, 4, [0, 0], [1, 2], [1, 1], [0, 0], [5, 5])
