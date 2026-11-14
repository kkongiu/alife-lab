"""Benchmark riproducibile del motore M1.

Misura passi/s, spostamenti/s, memoria e verifica l'equivalenza fra run continuo
e run interrotto+ripreso alla scala della configurazione baseline.

Uso:
    .venv/bin/python tools/benchmark.py [--steps 1000] [--out reports/benchmark.json]
"""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from typing import Any

from alife.config import Config, load_config
from alife.metrics import peak_memory_bytes, runtime_versions
from alife.persistence import load_checkpoint, save_checkpoint
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
WARMUP = 20


def _density_config(density: float, seed: int = 424242) -> Config:
    cells = 128 * 128
    return Config.from_dict(
        {
            "schema_version": 1,
            "seed": seed,
            "grid": {"width": 128, "height": 128, "boundary": "periodic"},
            "neighborhood": "von_neumann",
            "placement": "random_uniform",
            "species": [
                {
                    "name": "S0",
                    "count": round(density * cells),
                    "move_probability": 0.5,
                    "energy": 1,
                }
            ],
            "metrics": {"every": 100},
        }
    ).validate()


def measure(name: str, config: Config, steps: int) -> dict[str, Any]:
    world = World.create(config)
    world.advance(WARMUP)  # riscaldamento non conteggiato
    memory_before = peak_memory_bytes()
    moves_before = world.moves_total
    started = time.perf_counter()
    world.advance(steps)
    elapsed = time.perf_counter() - started
    peak = peak_memory_bytes()
    moves = world.moves_total - moves_before
    return {
        "case": name,
        "particles": len(world.store),
        "cells": config.grid.cells,
        "occupancy": round(len(world.store) / config.grid.cells, 4),
        "steps": steps,
        "seconds": round(elapsed, 4),
        "steps_per_second": round(steps / elapsed, 2),
        "moves": moves,
        "moves_per_second": round(moves / elapsed, 2),
        "particle_updates_per_second": round(len(world.store) * steps / elapsed, 2),
        "peak_memory_bytes": peak,
        "simulation_memory_bytes": max(0, peak - memory_before),
        "state_hash": world.state_hash()[:16],
    }


def equivalence(steps: int) -> dict[str, Any]:
    config = load_config(ROOT / "configs" / "baseline.json")

    continuous = World.create(config)
    continuous.advance(steps)

    interrupted = World.create(config)
    interrupted.advance(steps // 2)
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "checkpoint.json"
        save_checkpoint(path, interrupted)
        size = path.stat().st_size
        resumed = load_checkpoint(path)
        resumed.advance(steps - steps // 2)

    return {
        "steps": steps,
        "checkpoint_bytes": size,
        "continuous_hash": continuous.state_hash(),
        "resumed_hash": resumed.state_hash(),
        "hashes_equal": continuous.state_hash() == resumed.state_hash(),
        "rng_equal": continuous.rng.fingerprint() == resumed.rng.fingerprint(),
        "moves_equal": continuous.moves_total == resumed.moves_total,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark del motore M1")
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--out", default=str(ROOT / "reports" / "benchmark.json"))
    args = parser.parse_args()

    cases = [
        ("quick (32x32)", load_config(ROOT / "configs" / "quick.json")),
        ("baseline (128x128, 6 specie)", load_config(ROOT / "configs" / "baseline.json")),
        ("densita 2.5%", _density_config(0.025)),
        ("densita 25%", _density_config(0.25)),
        ("densita 50%", _density_config(0.50)),
    ]

    results = [measure(name, config, args.steps) for name, config in cases]
    equivalence_result = equivalence(args.steps * 2)

    payload = {
        "steps_per_case": args.steps,
        "warmup_steps": WARMUP,
        "versions": runtime_versions(),
        "cases": results,
        "equivalence": equivalence_result,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("| caso | particelle | passi | secondi | passi/s | spostamenti/s | MB picco | MB sim |")
    print("|---|---|---|---|---|---|---|---|")
    for row in results:
        print(
            f"| {row['case']} | {row['particles']} | {row['steps']} | {row['seconds']:.2f} "
            f"| {row['steps_per_second']:.1f} | {row['moves_per_second']:.0f} "
            f"| {row['peak_memory_bytes'] / 2**20:.1f} "
            f"| {row['simulation_memory_bytes'] / 2**20:.1f} |"
        )
    print()
    print(
        "equivalenza continuo/ripreso: "
        f"hash uguali={equivalence_result['hashes_equal']}, "
        f"rng uguali={equivalence_result['rng_equal']}, "
        f"mosse uguali={equivalence_result['moves_equal']}, "
        f"checkpoint={equivalence_result['checkpoint_bytes']} byte"
    )
    print(f"JSON: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
