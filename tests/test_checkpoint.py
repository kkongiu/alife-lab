"""Salvataggio, caricamento e ripresa senza alterare l'evoluzione."""

from __future__ import annotations

import json

import pytest

from alife.config import load_config
from alife.persistence import (
    CHECKPOINT_FORMAT,
    CheckpointError,
    load_checkpoint,
    save_checkpoint,
    world_to_checkpoint,
)
from alife.world import World
from support import M2_QUICK, M3_QUICK, make_config


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


# --- schema 2: legami, energia, identificativi ------------------------------


def test_v2_roundtrip_preserves_bonds_and_energy(tmp_path) -> None:
    world = World.create(load_config(M2_QUICK))
    world.advance(80)
    assert world.store.bonds, "il test richiede almeno un legame"
    path = save_checkpoint(tmp_path / "m2.json", world)

    restored = load_checkpoint(path)
    assert restored.snapshot() == world.snapshot()
    assert restored.store.bond_records() == world.store.bond_records()
    assert restored.store.full_records() == world.store.full_records()
    assert restored.next_id == world.next_id
    assert restored.bonds_formed_total == world.bonds_formed_total
    assert restored.bonds_broken_total == world.bonds_broken_total


def test_v2_resume_is_equivalent_to_continuous_run(tmp_path) -> None:
    config = load_config(M2_QUICK)

    continuous = World.create(config)
    continuous.advance(120)

    interrupted = World.create(config)
    interrupted.advance(50)
    path = save_checkpoint(tmp_path / "m2.json", interrupted)
    resumed = load_checkpoint(path)
    resumed.advance(70)

    assert resumed.state_hash_full() == continuous.state_hash_full()
    assert resumed.store.bond_records() == continuous.store.bond_records()
    assert resumed.rng.fingerprint() == continuous.rng.fingerprint()


def test_detects_tampered_bond_energy(tmp_path) -> None:
    world = World.create(load_config(M2_QUICK))
    world.advance(40)
    path = save_checkpoint(tmp_path / "m2.json", world)
    data = json.loads(path.read_text())
    data["bonds"][0][2] += 1
    path.write_text(json.dumps(data))

    with pytest.raises(CheckpointError, match="hash completo"):
        load_checkpoint(path)


def test_detects_tampered_particle_energy(tmp_path) -> None:
    world = World.create(load_config(M2_QUICK))
    world.advance(40)
    path = save_checkpoint(tmp_path / "m2.json", world)
    data = json.loads(path.read_text())
    data["particles"][0][4] += 1
    path.write_text(json.dumps(data))

    with pytest.raises(CheckpointError, match="hash completo"):
        load_checkpoint(path)


def test_detects_tampered_identity(tmp_path) -> None:
    world = World.create(load_config(M2_QUICK))
    path = save_checkpoint(tmp_path / "m2.json", world)
    data = json.loads(path.read_text())
    data["particles"][0][0] = 100000
    path.write_text(json.dumps(data))

    # l'identità entra nell'hash completo: alterarla rende il file incoerente
    with pytest.raises(CheckpointError, match="hash completo"):
        load_checkpoint(path)


def test_v1_checkpoint_is_migrated(tmp_path) -> None:
    config = make_config(seed=55)
    world = World.create(config)
    world.advance(6)
    payload = {
        "format": CHECKPOINT_FORMAT,
        "schema_version": 1,
        "created_utc": "2026-01-01T00:00:00+00:00",
        "config": config.to_dict(),
        "config_hash": config.hash(),
        "step": world.step,
        "moves_total": world.moves_total,
        "rng": world.rng.state(),
        "particles": world.store.records(),
        "counts": world.counts(),
        "energy_total": world.energy(),
        "state_hash": world.state_hash(),
    }
    path = tmp_path / "v1.json"
    path.write_text(json.dumps(payload))

    migrated = load_checkpoint(path)
    assert migrated.store.ids == list(range(len(migrated.store)))
    assert migrated.store.energy == [
        config.species[index].energy for index in migrated.store.species
    ]
    assert not migrated.store.bonds
    assert migrated.state_hash() == world.state_hash()
    assert migrated.energy() == world.energy()
    assert migrated.next_id == len(migrated.store)


def test_v1_checkpoint_with_bonds_is_rejected(tmp_path) -> None:
    config = make_config(seed=55)
    world = World.create(config)
    payload = {
        "format": CHECKPOINT_FORMAT,
        "schema_version": 1,
        "config": config.to_dict(),
        "config_hash": config.hash(),
        "step": 0,
        "moves_total": 0,
        "rng": world.rng.state(),
        "particles": world.store.records(),
        "energy_total": world.energy(),
        "state_hash": world.state_hash(),
        "bonds": [[0, 1, 2]],
    }
    path = tmp_path / "v1.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(CheckpointError, match="legami non ammessi"):
        load_checkpoint(path)


# --- schema 3: ledger, sorgenti, flussi ------------------------------------


def test_v3_roundtrip_preserves_ledger(tmp_path) -> None:
    world = World.create(load_config(M3_QUICK))
    world.advance(40)
    assert world.injected > 0
    path = save_checkpoint(tmp_path / "m3.json", world)

    restored = load_checkpoint(path)
    assert restored.snapshot() == world.snapshot()
    assert restored.injected == world.injected
    assert restored.dissipated == world.dissipated
    assert restored.unabsorbed == world.unabsorbed
    assert restored.source_acc == world.source_acc
    assert restored.source_store == world.source_store
    assert restored.rng.draws == world.rng.draws
    assert restored.state_hash_full() == world.state_hash_full()


def test_v3_resume_is_equivalent_with_flows(tmp_path) -> None:
    config = load_config(M3_QUICK)
    continuous = World.create(config)
    continuous.advance(120)

    interrupted = World.create(config)
    interrupted.advance(50)
    path = save_checkpoint(tmp_path / "m3.json", interrupted)
    resumed = load_checkpoint(path)
    resumed.advance(70)

    assert resumed.state_hash_full() == continuous.state_hash_full()
    assert resumed.injected == continuous.injected
    assert resumed.dissipated == continuous.dissipated
    assert resumed.source_acc == continuous.source_acc


def test_detects_tampered_ledger(tmp_path) -> None:
    world = World.create(load_config(M3_QUICK))
    world.advance(10)
    path = save_checkpoint(tmp_path / "m3.json", world)
    data = json.loads(path.read_text())
    data["ledger"]["injected"] += 1
    path.write_text(json.dumps(data))

    with pytest.raises(CheckpointError, match="hash completo"):
        load_checkpoint(path)


def test_detects_wrong_source_accumulators(tmp_path) -> None:
    world = World.create(load_config(M3_QUICK))
    path = save_checkpoint(tmp_path / "m3.json", world)
    data = json.loads(path.read_text())
    data["source_acc"] = data["source_acc"][:-1]
    path.write_text(json.dumps(data))

    with pytest.raises(CheckpointError, match="accumulatori"):
        load_checkpoint(path)


def test_v2_checkpoint_is_migrated_to_v3(tmp_path) -> None:
    config = load_config(M2_QUICK)
    world = World.create(config)
    world.advance(30)
    payload = {
        "format": CHECKPOINT_FORMAT,
        "schema_version": 2,
        "config": config.to_dict(),
        "config_hash": config.hash(),
        "step": world.step,
        "moves_total": world.moves_total,
        "next_id": world.next_id,
        "rng": world.rng.state(),
        "particles": world.store.full_records(),
        "bonds": world.store.bond_records(),
        "energy_total": world.energy(),
        "state_hash": world.state_hash(),
        "state_hash_full": world.state_hash_full(),
    }
    path = tmp_path / "v2.json"
    path.write_text(json.dumps(payload))

    migrated = load_checkpoint(path)
    assert migrated.injected == migrated.dissipated == migrated.unabsorbed == 0
    assert migrated.source_acc == []
    assert migrated.state_hash_full() == world.state_hash_full()
    assert migrated.step == world.step
