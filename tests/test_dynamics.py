"""Movimento locale, risoluzione dei conflitti, uso del generatore."""

from __future__ import annotations

from alife.dynamics import VON_NEUMANN, resolve_moves
from alife.rng import RNG
from alife.world import World
from support import make_config


def _grid(width: int, height: int, occupants: dict[tuple[int, int], int]) -> list[int]:
    grid = [-1] * (width * height)
    for (x, y), index in occupants.items():
        grid[y * width + x] = index
    return grid


def test_free_move_accepted() -> None:
    grid = _grid(8, 8, {(2, 2): 0})
    accepted = resolve_moves({0: 2 * 8 + 3}, grid, step=0)
    assert accepted == {0: 2 * 8 + 3}


def test_contention_produces_single_winner() -> None:
    grid = _grid(8, 8, {(2, 2): 0, (2, 3): 1})
    target = 2 * 8 + 4
    accepted = resolve_moves({0: target, 1: target}, grid, step=5)
    assert len(accepted) == 1
    assert next(iter(accepted.values())) == target


def test_swap_is_resolved_as_rotation() -> None:
    grid = _grid(8, 8, {(0, 0): 0, (1, 0): 1})
    accepted = resolve_moves({0: 0 * 8 + 1, 1: 0 * 8 + 0}, grid, step=3)
    assert accepted == {0: 1, 1: 0}


def test_chain_towards_empty_cell_moves_entirely() -> None:
    grid = _grid(8, 8, {(0, 0): 0, (1, 0): 1})
    accepted = resolve_moves({0: 1, 1: 2}, grid, step=1)
    assert accepted == {0: 1, 1: 2}


def test_three_particle_cycle() -> None:
    grid = _grid(8, 8, {(0, 0): 0, (1, 0): 1, (2, 0): 2})
    accepted = resolve_moves({0: 1, 1: 2, 2: 0}, grid, step=2)
    assert accepted == {0: 1, 1: 2, 2: 0}


def test_blocked_chain_leaves_head_stuck() -> None:
    # 1 non si muove: la particella 0 vuole la sua cella e non puo' passare.
    grid = _grid(8, 8, {(0, 0): 0, (1, 0): 1})
    accepted = resolve_moves({0: 1}, grid, step=4)
    assert accepted == {}


def test_resolution_is_insertion_order_independent() -> None:
    grid = _grid(8, 8, {(0, 0): 0, (1, 0): 1, (2, 0): 2, (3, 0): 3})
    proposals = {0: 1, 1: 2, 2: 3, 3: 0}
    forward = resolve_moves(dict(proposals), grid, step=9)
    backward = resolve_moves(dict(reversed(list(proposals.items()))), grid, step=9)
    assert forward == backward


def test_single_particle_moves_exactly_one_cell() -> None:
    config = make_config(
        width=16,
        height=16,
        species=[{"name": "A", "count": 1, "move_probability": 1.0, "energy": 1}],
    )
    world = World.create(config)
    for _ in range(20):
        before_x, before_y = world.store.position_of(0)
        world.advance(1)
        x, y = world.store.position_of(0)
        dx = min(abs(x - before_x), 16 - abs(x - before_x))
        dy = min(abs(y - before_y), 16 - abs(y - before_y))
        assert dx + dy == 1
    assert world.step == 20
    assert world.moves_total == 20


def test_immobile_species_never_moves() -> None:
    config = make_config(
        width=12,
        height=12,
        species=[{"name": "F", "count": 6, "move_probability": 0.0, "energy": 1}],
    )
    world = World.create(config)
    before = world.store.records()
    world.advance(30)
    assert world.store.records() == before
    assert world.moves_total == 0


def test_closed_boundary_keeps_particles_inside() -> None:
    config = make_config(
        width=10,
        height=10,
        boundary="closed",
        species=[{"name": "A", "count": 20, "move_probability": 1.0, "energy": 1}],
    )
    world = World.create(config)
    world.advance(50)
    for x, y in zip(world.store.xs, world.store.ys):
        assert 0 <= x < 10 and 0 <= y < 10
    assert not world.validate()


def test_rng_stream_is_two_draws_per_particle_per_step() -> None:
    config = make_config(
        width=12,
        height=12,
        species=[{"name": "A", "count": 10, "move_probability": 0.5, "energy": 1}],
    )
    world = World.create(config)
    world.advance(7)

    reference = RNG(config.seed)
    for _ in range(10):  # collocazione iniziale
        reference.raw()
    for _ in range(2 * 10 * 7):  # 2 estrazioni per particella per passo
        reference.raw()
    assert world.rng.fingerprint() == reference.fingerprint()


def test_direction_set_is_von_neumann() -> None:
    assert len(VON_NEUMANN) == 4
    assert sum(abs(dx) + abs(dy) for dx, dy in VON_NEUMANN) == 4
