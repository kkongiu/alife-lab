"""Persistenza: checkpoint JSON con stato del mondo, RNG, energia e legami.

Schema 2 (M2): particelle con identificativo persistente ed energia, legami con
energia immagazzinata, contatori della chimica.
Schema 1 (M1): solo posizioni e specie. I checkpoint M1 restano leggibili: gli
identificativi sono assegnati in ordine, l'energia delle particelle è quella
iniziale della specie e non ci sono legami.

In lettura vengono verificati formato, versione, hash della configurazione, hash
dello stato (materiale e completo), coerenza energetica e invarianti.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import Config
from .particles import InvariantError, ParticleStore
from .rng import RNG, RNGError
from .world import World

CHECKPOINT_FORMAT = "alife-checkpoint"
CHECKPOINT_SCHEMA = 2


class CheckpointError(ValueError):
    """Checkpoint illeggibile, incoerente o corrotto."""


def world_to_checkpoint(world: World) -> dict[str, Any]:
    return {
        "format": CHECKPOINT_FORMAT,
        "schema_version": CHECKPOINT_SCHEMA,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config": world.config.to_dict(),
        "config_hash": world.config.hash(),
        "step": world.step,
        "moves_total": world.moves_total,
        "next_id": world.next_id,
        "rng": world.rng.state(),
        "particles": world.store.full_records(),
        "bonds": world.store.bond_records(),
        "counts": world.counts(),
        "energy_total": world.energy(),
        "energy_particles": world.energy_particles(),
        "energy_bonds": world.energy_bonds(),
        "bonds_formed_total": world.bonds_formed_total,
        "bonds_broken_total": world.bonds_broken_total,
        "state_hash": world.state_hash(),
        "state_hash_full": world.state_hash_full(),
    }


def save_checkpoint(path: str | Path, world: World) -> Path:
    """Scrittura atomica: nessun checkpoint parziale se il processo si interrompe."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(world_to_checkpoint(world), ensure_ascii=True)
    handle, temporary = tempfile.mkstemp(
        dir=str(destination.parent), prefix=destination.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise
    return destination


def load_checkpoint(path: str | Path) -> World:
    source = Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CheckpointError(f"checkpoint non trovato: {source}") from exc
    except json.JSONDecodeError as exc:
        raise CheckpointError(f"checkpoint JSON non valido ({source}): {exc}") from exc

    if not isinstance(data, dict):
        raise CheckpointError("checkpoint: atteso un oggetto JSON")
    if data.get("format") != CHECKPOINT_FORMAT:
        raise CheckpointError(f"checkpoint: formato inatteso {data.get('format')!r}")
    schema_version = data.get("schema_version")
    if schema_version not in (1, 2):
        raise CheckpointError(
            f"checkpoint: schema {schema_version!r}, atteso 1 o {CHECKPOINT_SCHEMA}"
        )

    config = Config.from_dict(data.get("config"))
    config.validate()
    if config.hash() != data.get("config_hash"):
        raise CheckpointError("checkpoint: hash della configurazione non coerente")

    rng = RNG(0)
    try:
        rng.set_state(data.get("rng", {}))
    except RNGError as exc:
        raise CheckpointError(f"checkpoint: stato RNG non valido ({exc})") from exc

    if schema_version == 1:
        store, next_id = _store_from_v1(data, config)
    else:
        store, next_id = _store_from_v2(data, config)

    world = World(
        config,
        rng,
        store,
        step=int(data.get("step", 0)),
        moves_total=int(data.get("moves_total", 0)),
        next_id=next_id,
        bonds_formed_total=int(data.get("bonds_formed_total", 0)),
        bonds_broken_total=int(data.get("bonds_broken_total", 0)),
    )

    if world.state_hash() != data.get("state_hash"):
        raise CheckpointError("checkpoint: hash dello stato non coerente (file corrotto)")
    if schema_version >= 2 and world.state_hash_full() != data.get("state_hash_full"):
        raise CheckpointError(
            "checkpoint: hash completo dello stato non coerente (file corrotto)"
        )
    if world.energy() != int(data.get("energy_total", -1)):
        raise CheckpointError("checkpoint: bilancio energetico non coerente")
    try:
        world.check()
    except InvariantError as exc:
        raise CheckpointError(f"checkpoint: stato non valido ({exc})") from exc
    return world


def _store_from_v1(data: dict[str, Any], config: Config) -> tuple[ParticleStore, int]:
    particles = data.get("particles")
    if not isinstance(particles, list):
        raise CheckpointError("checkpoint: campo 'particles' non valido")
    try:
        xs = [int(entry[0]) for entry in particles]
        ys = [int(entry[1]) for entry in particles]
        species = [int(entry[2]) for entry in particles]
    except (TypeError, IndexError, ValueError) as exc:
        raise CheckpointError(f"checkpoint: particelle malformate ({exc})") from exc

    ids = list(range(len(particles)))
    energies = [config.species[index].energy for index in species]
    try:
        store = ParticleStore(
            config.grid.width, config.grid.height, ids, xs, ys, species, energies
        )
    except InvariantError as exc:
        raise CheckpointError(f"checkpoint: particelle incoerenti ({exc})") from exc
    if data.get("bonds"):
        raise CheckpointError("checkpoint schema 1: legami non ammessi")
    return store, len(ids)


def _store_from_v2(data: dict[str, Any], config: Config) -> tuple[ParticleStore, int]:
    particles = data.get("particles")
    if not isinstance(particles, list):
        raise CheckpointError("checkpoint: campo 'particles' non valido")
    try:
        ids = [int(entry[0]) for entry in particles]
        xs = [int(entry[1]) for entry in particles]
        ys = [int(entry[2]) for entry in particles]
        species = [int(entry[3]) for entry in particles]
        energy = [int(entry[4]) for entry in particles]
    except (TypeError, IndexError, ValueError) as exc:
        raise CheckpointError(f"checkpoint: particelle malformate ({exc})") from exc

    bonds_raw = data.get("bonds", [])
    if not isinstance(bonds_raw, list):
        raise CheckpointError("checkpoint: campo 'bonds' non valido")
    bonds: list[tuple[int, int, int]] = []
    try:
        for entry in bonds_raw:
            bonds.append((int(entry[0]), int(entry[1]), int(entry[2])))
    except (TypeError, IndexError, ValueError) as exc:
        raise CheckpointError(f"checkpoint: legami malformati ({exc})") from exc

    try:
        store = ParticleStore(
            config.grid.width, config.grid.height, ids, xs, ys, species, energy, bonds
        )
    except InvariantError as exc:
        raise CheckpointError(f"checkpoint: particelle o legami incoerenti ({exc})") from exc

    next_id = int(data.get("next_id", max(ids) + 1 if ids else 0))
    return store, next_id
