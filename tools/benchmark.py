"""Benchmark riproducibile del motore M1.

Misura passi/s e memoria con ripetizioni indipendenti (mediana e intervallo) e
verifica l'equivalenza fra run continuo e run interrotto+ripreso.

Uso:
    .venv/bin/python tools/benchmark.py [--repeats 3] [--out reports/benchmark.json]
"""

from __future__ import annotations

import argparse
import json
import statistics
import tempfile
import time
from pathlib import Path
from typing import Any

from alife.config import Config, load_config
from alife.metrics import peak_memory_bytes, process_baseline_memory, runtime_versions
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


def _single_run(name: str, config: Config, steps: int) -> dict[str, Any]:
    world = World.create(config)
    world.advance(WARMUP)  # riscaldamento non conteggiato
    moves_before = world.moves_total
    started = time.perf_counter()
    world.advance(steps)
    elapsed = time.perf_counter() - started
    moves = world.moves_total - moves_before
    return {
        "particles": len(world.store),
        "seconds": elapsed,
        "steps_per_second": steps / elapsed,
        "moves_per_second": moves / elapsed,
        "peak_memory_bytes": peak_memory_bytes(),
        "state_hash": world.state_hash()[:16],
    }


def measure(name: str, config: Config, steps: int, repeats: int) -> dict[str, Any]:
    runs = [_single_run(name, config, steps) for _ in range(repeats)]
    steps_per_second = [run["steps_per_second"] for run in runs]
    seconds = [run["seconds"] for run in runs]
    peak = max(run["peak_memory_bytes"] for run in runs)
    baseline = process_baseline_memory()
    return {
        "case": name,
        "particles": runs[0]["particles"],
        "cells": config.grid.cells,
        "occupancy": round(runs[0]["particles"] / config.grid.cells, 4),
        "steps_per_run": steps,
        "repeats": repeats,
        "seconds_median": round(statistics.median(seconds), 4),
        "steps_per_second_median": round(statistics.median(steps_per_second), 2),
        "steps_per_second_min": round(min(steps_per_second), 2),
        "steps_per_second_max": round(max(steps_per_second), 2),
        "moves_per_second_median": round(
            statistics.median(run["moves_per_second"] for run in runs), 2
        ),
        "peak_memory_bytes": peak,
        "simulation_memory_bytes": max(0, peak - baseline),
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
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--out", default=str(ROOT / "reports" / "benchmark.json"))
    args = parser.parse_args()

    # Passi diversi per caso: il costo per passo cresce con la densità.
    cases = [
        ("quick (32x32)", load_config(ROOT / "configs" / "quick.json"), 1000),
        ("baseline (128x128, 6 specie)", load_config(ROOT / "configs" / "baseline.json"), 500),
        ("densita 2.5%", _density_config(0.025), 500),
        ("densita 25%", _density_config(0.25), 200),
        ("densita 50%", _density_config(0.50), 100),
    ]

    results = [measure(name, config, steps, args.repeats) for name, config, steps in cases]
    equivalence_result = equivalence(2000)

    payload = {
        "repeats": args.repeats,
        "warmup_steps": WARMUP,
        "versions": runtime_versions(),
        "baseline_memory_bytes": process_baseline_memory(),
        "cases": results,
        "equivalence": equivalence_result,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("| caso | particelle | passi | secondi | passi/s (mediana) | min–max | MB sim |")
    print("|---|---|---|---|---|---|---|")
    for row in results:
        print(
            f"| {row['case']} | {row['particles']} | {row['steps_per_run']} "
            f"| {row['seconds_median']:.2f} "
            f"| {row['steps_per_second_median']:.1f} "
            f"| {row['steps_per_second_min']:.1f}–{row['steps_per_second_max']:.1f} "
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
