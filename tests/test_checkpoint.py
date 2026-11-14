"""Salvataggio, caricamento e ripresa senza alterare l'evoluzione."""

from __future__ import annotations

import json

import pytest

from alife.persistence import (
    CheckpointError,
    load_checkpoint,
    save_checkpoint,
    world_to_checkpoint,
)
from alife.world import World
from support import make_config


def test_roundtrip_preserves_state(tmp_path) -> None:
    world = World.create(make_config(seed=42))
    world.advance(17)
    path = save_checkpoint(tmp_path / "checkpoint.json", world)

    restored = load_checkpoint(path)
    assert restored.snapshot() == world.snapshot()
    assert restored.config == world.config
    assert restored.rng.fingerprint() == world.rng.fingerprint()
    assert restored.step == 17
    assert not restored.validate()


def test_resume_is_equivalent_to_continuous_run(tmp_path) -> None:
    config = make_config(seed=77)

    continuous = World.create(config)
    continuous.advance(60)

    interrupted = World.create(config)
    interrupted.advance(20)
    path = save_checkpoint(tmp_path / "mid.json", interrupted)
    resumed = load_checkpoint(path)
    resumed.advance(40)

    assert resumed.state_hash() == continuous.state_hash()
    assert resumed.moves_total == continuous.moves_total
    assert resumed.rng.fingerprint() == continuous.rng.fingerprint()


def test_repeated_save_load_cycles_are_stable(tmp_path) -> None:
    world = World.create(make_config(seed=8))
    path = tmp_path / "ckpt.json"
    for index in range(3):
        world.advance(10)
        save_checkpoint(path, world)
        world = load_checkpoint(path)
        assert world.step == 10 * (index + 1)


def test_checkpoint_does_not_mutate_world(tmp_path) -> None:
    world = World.create(make_config(seed=3))
    world.advance(5)
    before = world.snapshot()
    save_checkpoint(tmp_path / "c.json", world)
    assert world.snapshot() == before


def test_detects_tampered_particle(tmp_path) -> None:
    world = World.create(make_config(seed=4))
    world.advance(3)
    path = save_checkpoint(tmp_path / "c.json", world)

    data = json.loads(path.read_text())
    species_index = data["particles"][0][2]
    data["particles"][0][2] = (species_index + 1) % 2
    path.write_text(json.dumps(data))

    with pytest.raises(CheckpointError, match="hash dello stato"):
        load_checkpoint(path)


def test_detects_tampered_config_hash(tmp_path) -> None:
    world = World.create(make_config(seed=4))
    path = save_checkpoint(tmp_path / "c.json", world)
    data = json.loads(path.read_text())
    data["config"]["seed"] = 12345
    path.write_text(json.dumps(data))

    with pytest.raises(CheckpointError):
        load_checkpoint(path)


def test_detects_energy_imbalance(tmp_path) -> None:
    world = World.create(make_config(seed=4))
    world.advance(2)
    path = save_checkpoint(tmp_path / "c.json", world)
    data = json.loads(path.read_text())
    data["energy_total"] = int(data["energy_total"]) + 1
    path.write_text(json.dumps(data))

    with pytest.raises(CheckpointError, match="bilancio energetico"):
        load_checkpoint(path)


def test_detects_invalid_json(tmp_path) -> None:
    path = tmp_path / "c.json"
    path.write_text('{"format": "alife-checkpoint", ')
    with pytest.raises(CheckpointError, match="JSON non valido"):
        load_checkpoint(path)


def test_detects_wrong_format(tmp_path) -> None:
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"format": "altro"}))
    with pytest.raises(CheckpointError, match="formato"):
        load_checkpoint(path)


def test_detects_missing_rng_state(tmp_path) -> None:
    world = World.create(make_config(seed=4))
    data = world_to_checkpoint(world)
    del data["rng"]
    path = tmp_path / "c.json"
    path.write_text(json.dumps(data))
    with pytest.raises(CheckpointError, match="stato RNG"):
        load_checkpoint(path)


def test_missing_file(tmp_path) -> None:
    with pytest.raises(CheckpointError, match="non trovato"):
        load_checkpoint(tmp_path / "assente.json")


def test_no_temporary_file_left_behind(tmp_path) -> None:
    world = World.create(make_config(seed=4))
    save_checkpoint(tmp_path / "c.json", world)
    assert [path.name for path in tmp_path.iterdir()] == ["c.json"]
