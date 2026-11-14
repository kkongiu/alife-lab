"""M3: flussi energetici, dissipazione, costi e contabilità esatta."""

from __future__ import annotations

from pathlib import Path

from alife.config import load_config
from alife.rng import RNG
from alife.world import World
from support import ROOT, make_energy_config, world_with


def _initial_energy(world: World) -> int:
    return world.energy()


def test_closed_system_keeps_identity() -> None:
    world = World.create(make_energy_config())
    initial = world.configured_energy()
    world.advance(200)
    assert world.injected == 0
    assert world.dissipated == 0
    assert world.energy() == initial == world.accounted_energy()
    assert not world.validate()


def test_particle_decay_is_exact() -> None:
    config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 0.0, "energy": 100, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"particle_decay": {"num": 1, "den": 3}},
    )
    world = world_with(config, [(2, 2)], [0], energy=[100])
    before = _initial_energy(world)
    world.advance(9)  # perde 1 quanto ai passi 0, 3, 6
    assert world.store.energy == [97]
    assert world.dissipated == 3
    assert world.energy() == before - 3


def test_bond_decay_is_exact() -> None:
    config = make_energy_config(
        energy={"bond_decay": {"num": 1, "den": 1}},
    )
    world = world_with(config, [(1, 1), (2, 1)], [0, 0], energy=[10, 10], bonds=[(0, 1, 100)])
    world.advance(3)
    assert world.store.bonds[(0, 1)] == 97
    assert world.dissipated == 3


def test_source_accumulator_is_exact() -> None:
    config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 0.0, "energy": 0, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"sources": [{"x": 2, "y": 2, "rate_num": 1, "rate_den": 4, "capacity": 1000}]},
    )
    world = world_with(config, [(2, 2)], [0], energy=[0])
    world.advance(1000)
    assert world.injected == 250
    assert world.store.energy == [250]
    assert world.unabsorbed == 0
    assert world.source_acc == [0]


def test_source_capacity_and_unabsorbed() -> None:
    # cella vuota: il serbatoio si riempie fino alla capacità e poi trabocca
    config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 0.0, "energy": 0, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"sources": [{"x": 2, "y": 2, "rate_num": 1, "rate_den": 1, "capacity": 10}]},
    )
    world = world_with(config, [(5, 5)], [0], energy=[0])
    world.advance(20)
    assert world.injected == 20
    assert world.source_store == [10]
    assert world.unabsorbed == 10
    assert world.energy() == 10  # il serbatoio è energia interna
    assert world.energy() == world.accounted_energy()


def test_source_on_empty_cell_is_unabsorbed() -> None:
    config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 0.0, "energy": 10, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"sources": [{"x": 5, "y": 5, "rate_num": 1, "rate_den": 1, "capacity": 4}]},
    )
    world = world_with(config, [(2, 2)], [0])
    world.advance(5)
    assert world.injected == 5
    assert world.source_store == [4]
    assert world.unabsorbed == 1
    assert world.store.energy == [10]


def test_source_buffer_is_delivered_to_a_visiting_particle() -> None:
    config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 0.0, "energy": 0, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"sources": [{"x": 2, "y": 2, "rate_num": 3, "rate_den": 1, "capacity": 30}]},
    )
    world = world_with(config, [(2, 2)], [0], energy=[0])
    world.advance(1)
    assert world.source_store == [0]
    assert world.store.energy == [3]
    assert world.unabsorbed == 0


def test_movement_cost_charged_per_move() -> None:
    config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 1.0, "energy": 10, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"movement_cost": 1},
    )
    world = world_with(config, [(2, 2)], [0], energy=[10])
    world.advance(10)
    assert world.moves_total == 10
    assert world.store.energy == [0]
    assert world.dissipated == 10
    assert world.energy() == 0

    world.advance(5)
    assert world.moves_total == 10  # senza energia non si muove


def test_movement_cost_blocks_when_insufficient() -> None:
    config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 1.0, "energy": 1, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"movement_cost": 2},
    )
    world = world_with(config, [(2, 2)], [0], energy=[1])
    world.advance(10)
    assert world.moves_total == 0
    assert world.store.energy == [1]


def test_formation_dissipation() -> None:
    config = make_energy_config(
        energy={"formation_dissipation": 1},
    )
    world = world_with(config, [(1, 1), (2, 1)], [0, 0])
    from alife import chemistry

    chemistry.form_bonds(world)
    assert world.store.energy == [7, 7]
    assert sum(world.store.bonds.values()) == 4
    assert world.dissipated == 2
    assert world.energy() == 18


def test_breaking_dissipation() -> None:
    config = make_energy_config(
        chemistry={
            "enabled": True,
            "bond_cost": 2,
            "formation_probability": 0.0,
            "break_probability": 1.0,
            "allowed_pairs": [["S0", "S0"]],
            "catalysis": [],
        },
        energy={"breaking_dissipation": 1},
    )
    world = world_with(config, [(1, 1), (2, 1)], [0, 0], energy=[8, 8], bonds=[(0, 1, 4)])
    world.advance(1)
    assert not world.store.bonds
    assert world.store.energy == [10, 9]  # 3 restituiti: 2 al minore, 1 all'altro
    assert world.dissipated == 1
    assert world.energy() == 19


def test_open_run_keeps_identity() -> None:
    world = World.create(load_config(ROOT / "configs" / "m3_quick.json"))
    world.advance(200)
    assert world.injected > 0
    assert world.dissipated + world.unabsorbed > 0
    assert world.energy() == world.accounted_energy()
    assert all(value >= 0 for value in world.store.energy)
    assert not world.validate()


def test_open_run_is_deterministic() -> None:
    config = load_config(ROOT / "configs" / "m3_quick.json")
    first = World.create(config)
    second = World.create(config)
    first.advance(150)
    second.advance(150)
    assert first.state_hash_full() == second.state_hash_full()
    assert first.snapshot() == second.snapshot()
    assert first.injected == second.injected
    assert first.dissipated == second.dissipated


def test_rng_budget_with_flows_disabled() -> None:
    config = make_energy_config(
        species=[{"name": "S0", "count": 10, "move_probability": 0.5, "energy": 5, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={},
    )
    world = World.create(config)
    steps = 7
    world.advance(steps)

    draws = len(world.store) + 2 * len(world.store) * steps
    assert world.rng.draws == draws

    reference = RNG(config.seed)
    for _ in range(draws):
        reference.raw()
    assert world.rng.fingerprint() == reference.fingerprint()


def test_golden_hash_m2_is_preserved() -> None:
    # valore prodotto da M2: il codice M3 con schema 2 non deve cambiare nulla
    world = World.create(load_config(ROOT / "configs" / "m2_quick.json"))
    world.advance(200)
    assert world.state_hash_full() == (
        "31c33e342e37737c804cf8ac9b92b966686c958f8003b4d91a75937a152330d6"
    )
    assert world.injected == world.dissipated == world.unabsorbed == 0


def test_source_accumulator_out_of_range_is_detected() -> None:
    world = World.create(load_config(ROOT / "configs" / "m3_quick.json"))
    world.source_acc[0] = world.sources[0].rate_den
    assert any("accumulatore" in problem for problem in world.validate())


def test_ledger_tampering_is_detected() -> None:
    world = World.create(load_config(ROOT / "configs" / "m3_quick.json"))
    world.advance(20)
    world.injected += 1
    assert any("energia" in problem for problem in world.validate())


def test_core_modules_do_not_import_nondeterministic_sources() -> None:
    forbidden = ("import time", "import random", "import secrets", "os.urandom")
    allowed = {"metrics.py", "events.py", "cli.py", "persistence.py"}
    package = Path(ROOT) / "src" / "alife"
    for path in sorted(package.glob("*.py")):
        if path.name in allowed:
            continue
        source = path.read_text(encoding="utf-8")
        for module in forbidden:
            assert module not in source, f"{path.name} usa {module}"
