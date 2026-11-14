"""Invarianti fisiche e computazionali, incluso il rilevamento di violazioni."""

from __future__ import annotations

import pytest

from alife.particles import InvariantError, ParticleStore
from alife.world import World
from support import make_config


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
    world.store.xs.pop()
    world.store.ys.pop()
    world.store.species.pop()
    problems = world.validate()
    assert any("conteggi" in problem for problem in problems)


def test_validate_detects_invalid_species_index() -> None:
    world = World.create(make_config())
    world.store.species[0] = 7
    assert any("specie 7 inesistente" in problem for problem in world.validate())


def test_store_rejects_double_placement() -> None:
    with pytest.raises(InvariantError, match="doppia occupazione"):
        ParticleStore(4, 4, [1, 1], [1, 1], [0, 0])


def test_store_rejects_out_of_grid_particle() -> None:
    with pytest.raises(InvariantError, match="fuori griglia"):
        ParticleStore(4, 4, [4], [0], [0])
