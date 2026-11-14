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
    """Picco RSS del processo corrente in byte.

    Su Linux si legge ``VmHWM`` da ``/proc/self/status``: e' il picco
    dell'address space corrente e viene azzerato all'exec. ``ru_maxrss`` non e'
    affidabile in tutti i contesti, perché può ereditare il picco del processo
    genitore (osservato: 590 MiB dichiarati con 44 MiB reali).

    Su macOS ``ru_maxrss`` è espresso in byte; su Linux, come fallback, in KiB.
    """
    if sys.platform.startswith("linux"):
        try:
            with open("/proc/self/status", encoding="ascii") as stream:
                for line in stream:
                    if line.startswith("VmHWM:"):
                        return int(line.split()[1]) * 1024
        except (OSError, ValueError, IndexError):
            pass
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(usage)
    return int(usage) * 1024


# Picco RSS al caricamento del modulo: interprete e NumPy sono già importati,
# quindi il delta rispetto a questo valore isola la memoria della simulazione.
_MEMORY_AT_IMPORT = peak_memory_bytes()


def process_baseline_memory() -> int:
    return _MEMORY_AT_IMPORT


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
        # rispetto al caricamento del modulo stima la memoria della simulazione.
        self.baseline_memory = process_baseline_memory()
        self.peak_memory = max(self.baseline_memory, peak_memory_bytes())

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
        aggregates = world.aggregates()
        return {
            "step": world.step,
            "wall_time_s": round(elapsed, 6),
            "steps_per_second": round(steps_per_second, 3),
            "moves_total": world.moves_total,
            "particles": world.counts(),
            "particles_total": len(world.store),
            "occupancy": round(world.occupancy(), 6),
            "energy_total": world.energy(),
            "energy_particles": world.energy_particles(),
            "energy_bonds": world.energy_bonds(),
            "energy_sources": world.energy_sources(),
            "energy_in": world.injected,
            "energy_out": world.dissipated + world.unabsorbed,
            "energy_identity_delta": world.energy() - world.accounted_energy(),
            "injected": world.injected,
            "dissipated": world.dissipated,
            "unabsorbed": world.unabsorbed,
            "bonds": aggregates["bonds"],
            "bonded_particles": aggregates["bonded_particles"],
            "free_particles": aggregates["free_particles"],
            "aggregates": aggregates["aggregates"],
            "largest_aggregate": aggregates["largest_aggregate"],
            "bonds_formed_total": world.bonds_formed_total,
            "bonds_broken_total": world.bonds_broken_total,
            "state_hash": world.state_hash(),
            "state_hash_full": world.state_hash_full(),
        }

    def summary(self, world: "World") -> dict[str, Any]:
        """Riepilogo finale conforme ai campi obbligatori di M1 e M2."""
        elapsed = time.perf_counter() - self.started
        self.peak_memory = max(self.peak_memory, peak_memory_bytes())
        cells = world.config.grid.cells
        aggregates = world.aggregates()
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
                "internal": world.energy(),
                "initial": world.configured_energy(),
                "particles": world.energy_particles(),
                "bonds": world.energy_bonds(),
                "sources": world.energy_sources(),
                "injected": world.injected,
                "dissipated": world.dissipated,
                "unabsorbed": world.unabsorbed,
                "in": world.injected,
                "out": world.dissipated + world.unabsorbed,
                "delta": world.energy() - world.configured_energy(),
                "identity_delta": world.energy() - world.accounted_energy(),
            },
            "chemistry": {
                "enabled": world.chemistry_enabled,
                "bond_cost": world.bond_cost,
                "bonds": aggregates["bonds"],
                "bond_energy": aggregates["bond_energy"],
                "bonded_particles": aggregates["bonded_particles"],
                "free_particles": aggregates["free_particles"],
                "aggregates": aggregates["aggregates"],
                "largest_aggregate": aggregates["largest_aggregate"],
                "mean_aggregate_size": aggregates["mean_aggregate_size"],
                "size_distribution": aggregates["size_distribution"],
                "formed_total": world.bonds_formed_total,
                "broken_total": world.bonds_broken_total,
            },
            "duration_s": round(elapsed, 6),
            "steps_per_second": round(world.step / elapsed, 3) if elapsed > 0 else 0.0,
            "peak_memory_bytes": self.peak_memory,
            "baseline_memory_bytes": self.baseline_memory,
            "simulation_memory_bytes": max(0, self.peak_memory - self.baseline_memory),
            "state_hash": world.state_hash(),
            "state_hash_full": world.state_hash_full(),
            "seed": world.config.seed,
            "config_hash": world.config.hash(),
            "config_schema_version": world.config.schema_version,
            "metrics_records": self.records,
            "invariants": "ok" if not world.validate() else "violati",
            "versions": runtime_versions(),
        }

    def close(self) -> None:
        self._stream.close()
