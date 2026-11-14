"""Persistenza: checkpoint JSON con stato del mondo e del generatore.

Il checkpoint contiene la configurazione risolta, l'hash della configurazione, lo
stato del RNG, il contatore del passo e le particelle. In lettura vengono
verificati: formato, versione, hash della configurazione, hash dello stato,
coerenza energetica e invarianti strutturali.
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
CHECKPOINT_SCHEMA = 1


class CheckpointError(ValueError):
    """Checkpoint illeggibile, incoerente o corrotto."""


def world_to_checkpoint(world: World) -> dict[str, Any]:
    store = world.store
    return {
        "format": CHECKPOINT_FORMAT,
        "schema_version": CHECKPOINT_SCHEMA,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config": world.config.to_dict(),
        "config_hash": world.config.hash(),
        "step": world.step,
        "moves_total": world.moves_total,
        "rng": world.rng.state(),
        "particles": store.records(),
        "counts": world.counts(),
        "energy_total": world.energy(),
        "state_hash": world.state_hash(),
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
    if data.get("schema_version") != CHECKPOINT_SCHEMA:
        raise CheckpointError(
            f"checkpoint: schema {data.get('schema_version')!r}, atteso {CHECKPOINT_SCHEMA}"
        )

    config = Config.from_dict(data.get("config"))
    config.validate()
    if config.hash() != data.get("config_hash"):
        raise CheckpointError("checkpoint: hash della configurazione non coerente")

    particles = data.get("particles")
    if not isinstance(particles, list):
        raise CheckpointError("checkpoint: campo 'particles' non valido")
    try:
        xs = [int(entry[0]) for entry in particles]
        ys = [int(entry[1]) for entry in particles]
        species = [int(entry[2]) for entry in particles]
    except (TypeError, IndexError, ValueError) as exc:
        raise CheckpointError(f"checkpoint: particelle malformate ({exc})") from exc

    rng = RNG(0)
    try:
        rng.set_state(data.get("rng", {}))
    except RNGError as exc:
        raise CheckpointError(f"checkpoint: stato RNG non valido ({exc})") from exc

    try:
        store = ParticleStore(config.grid.width, config.grid.height, xs, ys, species)
    except InvariantError as exc:
        raise CheckpointError(f"checkpoint: particelle incoerenti ({exc})") from exc
    world = World(
        config,
        rng,
        store,
        step=int(data.get("step", 0)),
        moves_total=int(data.get("moves_total", 0)),
    )

    if world.state_hash() != data.get("state_hash"):
        raise CheckpointError("checkpoint: hash dello stato non coerente (file corrotto)")
    if world.energy() != int(data.get("energy_total", -1)):
        raise CheckpointError("checkpoint: bilancio energetico non coerente")
    world.check()
    return world
