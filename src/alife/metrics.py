"""Metriche: registrazione incrementale, riepilogo finale, ambiente di esecuzione."""

from __future__ import annotations

import json
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from .world import World


def peak_memory_bytes() -> int:
    """Picco RSS del processo in byte.

    ``ru_maxrss`` e' espresso in kilobyte su Linux e in byte su macOS: la
    conversione esplicita evita un errore di fattore 1024 nei report.
    """
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(usage)
    return int(usage) * 1024


def runtime_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "n/d",
    }


def git_commit(directory: Path) -> str | None:
    """Commit corrente, se la directory e' un repository git. Mai bloccante."""
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


class MetricsRecorder:
    """Scrive ``metrics.jsonl`` un record ogni ``every`` passi."""

    def __init__(self, out_dir: str | Path, every: int) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.every = max(1, int(every))
        self.path = self.out_dir / "metrics.jsonl"
        self._stream = self.path.open("w", encoding="utf-8")
        self.started = time.perf_counter()
        self.wall_time_s = 0.0
        self.records = 0
        # Il picco assoluto include l'interprete e le librerie (NumPy); il delta
        # rispetto a questo valore stima la memoria attribuibile alla simulazione.
        self.baseline_memory = peak_memory_bytes()
        self.peak_memory = self.baseline_memory

    def observe(self, world: "World") -> None:
        if world.step % self.every != 0:
            return
        now = time.perf_counter()
        self.wall_time_s = now - self.started
        self.peak_memory = max(self.peak_memory, peak_memory_bytes())
        record = self._record(world, now)
        self._stream.write(json.dumps(record, ensure_ascii=True) + "\n")
        self._stream.flush()
        self.records += 1

    def _record(self, world: "World", now: float) -> dict[str, Any]:
        elapsed = now - self.started
        steps_per_second = world.step / elapsed if elapsed > 0 and world.step else 0.0
        return {
            "step": world.step,
            "wall_time_s": round(elapsed, 6),
            "steps_per_second": round(steps_per_second, 3),
            "moves_total": world.moves_total,
            "particles": world.counts(),
            "particles_total": len(world.store),
            "occupancy": round(world.occupancy(), 6),
            "energy_total": world.energy(),
            "energy_in": 0,
            "energy_out": 0,
            "state_hash": world.state_hash(),
        }

    def summary(self, world: "World") -> dict[str, Any]:
        """Riepilogo finale conforme ai campi obbligatori di M1."""
        elapsed = time.perf_counter() - self.started
        self.peak_memory = max(self.peak_memory, peak_memory_bytes())
        cells = world.config.grid.cells
        return {
            "steps": world.step,
            "moves_total": world.moves_total,
            "moves_per_step": round(world.moves_total / world.step, 6) if world.step else 0.0,
            "particles": world.counts(),
            "particles_total": len(world.store),
            "occupancy": round(world.occupancy(), 6),
            "grid": {
                "width": world.config.grid.width,
                "height": world.config.grid.height,
                "cells": cells,
                "boundary": world.config.grid.boundary,
            },
            "energy": {
                "total": world.energy(),
                "initial": world.configured_energy(),
                "in": 0,
                "out": 0,
                "delta": world.energy() - world.configured_energy(),
            },
            "duration_s": round(elapsed, 6),
            "steps_per_second": round(world.step / elapsed, 3) if elapsed > 0 else 0.0,
            "peak_memory_bytes": self.peak_memory,
            "baseline_memory_bytes": self.baseline_memory,
            "simulation_memory_bytes": max(0, self.peak_memory - self.baseline_memory),
            "state_hash": world.state_hash(),
            "seed": world.config.seed,
            "config_hash": world.config.hash(),
            "config_schema_version": world.config.schema_version,
            "metrics_records": self.records,
            "invariants": "ok" if not world.validate() else "violati",
            "versions": runtime_versions(),
        }

    def close(self) -> None:
        self._stream.close()
