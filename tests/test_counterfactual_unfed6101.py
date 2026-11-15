"""Invariant and reproducibility checks for the *external* causal audit."""
from __future__ import annotations

from alife.structures import components
from tools.counterfactual_unfed6101 import clone_world, relocate, connected_seed_component
from support import make_energy_config, world_with


def make_world(obstacle: bool = False):
    species = [{
        "name": "A", "count": 4 if obstacle else 3,
        "move_probability": 0.0, "energy": 10, "max_bonds": 2,
    }]
    config = make_energy_config(
        width=8, height=8, species=species,
        chemistry={"enabled": False},
    )
    positions = [(0, 0), (1, 0), (2, 0)]
    if obstacle:
        positions.append((1, 1))
    return world_with(config, positions, [0] * len(positions),
                      bonds=[(0, 1, 0), (1, 2, 0)])


def test_clone_preserves_world_and_rng_and_future():
    source = make_world()
    duplicate = clone_world(source)
    assert duplicate is not source
    assert duplicate.store is not source.store
    assert duplicate.state_hash_full() == source.state_hash_full()
    assert duplicate.rng.state() == source.rng.state()
    source.advance(5)
    duplicate.advance(5)
    assert duplicate.state_hash_full() == source.state_hash_full()
    assert duplicate.rng.state() == source.rng.state()


def test_rigid_relocation_is_external_and_conserves_invariants():
    source = make_world()
    reference = source.state_hash_full()
    before_energy = source.energy()
    before_rng = source.rng.state()
    duplicate = clone_world(source)
    assert relocate(duplicate, (0, 1, 2), (0, 1))
    assert duplicate.state_hash_full() != reference
    assert source.state_hash_full() == reference
    assert duplicate.energy() == before_energy
    assert duplicate.rng.state() == before_rng
    assert len(components(duplicate.store)) == 1
    assert {tuple((duplicate.store.xs[i], duplicate.store.ys[i])) for i in (0, 1, 2)} == {
        (0, 1), (1, 1), (2, 1)
    }
    duplicate.check()


def test_relocation_rejects_occupied_target_without_side_effects():
    world = make_world(obstacle=True)
    before_hash = world.state_hash_full()
    before_rng = world.rng.state()
    assert not relocate(world, (0, 1, 2), (0, 1))
    assert world.state_hash_full() == before_hash
    assert world.rng.state() == before_rng
    world.check()


def test_seed_component_requires_all_birth_particles_in_same_aggregate():
    world = make_world()
    found = connected_seed_component(world, (0, 1))
    assert found is not None
    assert found["size"] == 3
    assert found["particle_ids"] == [0, 1, 2]
    assert connected_seed_component(world, (0, 99)) is None
