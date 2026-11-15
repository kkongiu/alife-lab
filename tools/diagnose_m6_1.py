"""Diagnostica M6.1: topologie effettive, catalisi, autocatalisi.

Non modifica le leggi del motore. Usa solo configurazioni e osservatori
esistenti; gli artefatti finiscono in `campaigns/diagnostics/m6_1/`.

Uso: .venv/bin/python tools/diagnose_m6_1.py
"""

from __future__ import annotations

import json
import tempfile
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

from alife.analysis import Analysis
from alife.config import Config, load_config
from alife.persistence import load_checkpoint
from alife.structures import components
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "campaigns" / "diagnostics" / "m6_1"


def topology_census() -> dict[str, Any]:
    """Topologie e dimensioni di nascita dai run M6 già registrati."""
    runs = []
    for run_dir in sorted((ROOT / "runs" / "m6").glob("*/*")):
        summary_path = run_dir / "summary.json"
        lineage_path = run_dir / "lineage.jsonl"
        checkpoint_path = run_dir / "checkpoint.json"
        if not (summary_path.exists() and lineage_path.exists() and checkpoint_path.exists()):
            continue
        world = load_checkpoint(checkpoint_path)
        structures = components(world.store)
        degree_histogram: Counter = Counter()
        cyclic = 0
        sizes = []
        for indices, bonds in structures:
            sizes.append(len(indices))
            for index in indices:
                degree_histogram[world.store.degree[index]] += 1
            if len(bonds) - len(indices) + 1 > 0:
                cyclic += 1
        birth_sizes: Counter = Counter()
        with lineage_path.open(encoding="utf-8") as stream:
            for line in stream:
                event = json.loads(line)
                if event.get("kind") == "birth":
                    birth_sizes[int(event["size"])] += 1
        runs.append(
            {
                "run": f"{run_dir.parent.name}/{run_dir.name}",
                "condition": run_dir.parent.name,
                "structures": len(structures),
                "max_size": max(sizes, default=0),
                "mean_size": round(sum(sizes) / len(sizes), 3) if sizes else 0.0,
                "cyclic_components": cyclic,
                "max_degree": max(degree_histogram, default=0),
                "degree_histogram": {str(key): value for key, value in sorted(degree_histogram.items())},
                "birth_sizes": {str(key): value for key, value in sorted(birth_sizes.items())},
            }
        )

    by_condition: dict[str, Any] = {}
    for condition in sorted({run["condition"] for run in runs}):
        subset = [run for run in runs if run["condition"] == condition]
        births: Counter = Counter()
        for run in subset:
            births.update({int(size): count for size, count in run["birth_sizes"].items()})
        by_condition[condition] = {
            "runs": len(subset),
            "median_structures": median(run["structures"] for run in subset),
            "median_max_size": median(run["max_size"] for run in subset),
            "cyclic_components_total": sum(run["cyclic_components"] for run in subset),
            "max_degree": max(run["max_degree"] for run in subset),
            "birth_sizes_total": {str(size): count for size, count in sorted(births.items())},
        }
    return {"runs": runs, "by_condition": by_condition}


def _probe_config(base_path: Path, with_catalysis: bool) -> tuple[Config, str]:
    raw = json.loads(base_path.read_text(encoding="utf-8"))
    if with_catalysis:
        raw["chemistry"]["catalysis"] = [
            {"catalyst": "S3", "pair": ["S0", "S1"], "factor": 1000.0}
        ]
    else:
        raw["chemistry"]["catalysis"] = []
    config = Config.from_dict(raw).validate()
    return config, config.hash()


def _run_analysis(config: Config, steps: int) -> dict[str, Any]:
    world = World.create(config)
    with tempfile.TemporaryDirectory() as temporary:
        analysis = Analysis(Path(temporary))
        analysis.observe(world)
        world.advance(steps, observer=analysis.observe)
        summary = analysis.summary()
        analysis.close()
    structures = summary["structures"]
    replication = summary["replication"]
    return {
        "structures": structures["active_structures"],
        "births": structures["events"].get("birth", 0),
        "growths": structures["events"].get("growth", 0),
        "max_size": max((int(size) for size in structures["size_distribution"]), default=0),
        "size_distribution": structures["size_distribution"],
        "exact_observations": structures["signatures"]["exact_observations"],
        "fuzzy_observations": structures["signatures"]["fuzzy_observations"],
        "ambiguous_steps": structures["signatures"]["ambiguous_steps"],
        "candidates": replication["candidates"],
        "persistent": replication["persistent"],
        "classified": replication["classified"],
        "world_hash": world.state_hash_full(),
    }


def catalysis_probe() -> dict[str, Any]:
    base = ROOT / "campaigns" / "m6" / "configs" / "fed-mid-6101.json"
    off, off_hash = _probe_config(base, with_catalysis=False)
    on, on_hash = _probe_config(base, with_catalysis=True)
    return {
        "steps": 1500,
        "base_config": str(base.relative_to(ROOT)),
        "off": {"config_hash": off_hash, **_run_analysis(off, 1500)},
        "on": {"config_hash": on_hash, **_run_analysis(on, 1500)},
    }


def _autocatalysis_config(rate: float, with_catalysis: bool) -> Config:
    chemistry: dict[str, Any] = {
        "enabled": True,
        "bond_cost": 1,
        "formation_probability": rate,
        "break_probability": 0.0,
        "allowed_pairs": [["A", "B"]],
        "catalysis": [],
    }
    if with_catalysis:
        chemistry["catalysis"] = [{"catalyst": "A", "pair": ["A", "B"], "factor": 1000.0}]
    return Config.from_dict(
        {
            "schema_version": 3,
            "seed": 7001,
            "grid": {"width": 64, "height": 64, "boundary": "periodic"},
            "species": [
                {"name": "A", "count": 150, "move_probability": 0.5, "energy": 10, "max_bonds": 1},
                {"name": "B", "count": 150, "move_probability": 0.5, "energy": 10, "max_bonds": 1},
            ],
            "chemistry": chemistry,
            "energy": {},
            "metrics": {"every": 100},
        }
    ).validate()


def autocatalysis_probe() -> dict[str, Any]:
    results = {}
    for name, with_catalysis in (("off", False), ("on", True)):
        config = _autocatalysis_config(0.002, with_catalysis)
        world = World.create(config)
        curve = [0]
        for step in range(2000):
            world.advance(1)
            if (step + 1) % 100 == 0:
                curve.append(len(world.store.bonds))
        results[name] = {
            "config_hash": config.hash(),
            "final_bonds": len(world.store.bonds),
            "bond_curve_every_100": curve,
            "world_hash": world.state_hash_full(),
        }
    results["steps"] = 2000
    results["formation_probability"] = 0.002
    results["catalysis_factor"] = 1000.0
    return results


def same_species_probe() -> dict[str, Any]:
    """Auto-catalisi di una sola specie: il rilevatore può scattare per caso?"""
    config = Config.from_dict(
        {
            "schema_version": 3,
            "seed": 7002,
            "grid": {"width": 64, "height": 64, "boundary": "periodic"},
            "species": [
                {"name": "A", "count": 200, "move_probability": 0.5, "energy": 10, "max_bonds": 2},
            ],
            "chemistry": {
                "enabled": True,
                "bond_cost": 1,
                "formation_probability": 0.01,
                "break_probability": 0.001,
                "allowed_pairs": [["A", "A"]],
                "catalysis": [{"catalyst": "A", "pair": ["A", "A"], "factor": 1000.0}],
            },
            "energy": {},
            "metrics": {"every": 100},
        }
    ).validate()
    world = World.create(config)
    with tempfile.TemporaryDirectory() as temporary:
        analysis = Analysis(Path(temporary))
        analysis.observe(world)
        world.advance(2000, observer=analysis.observe)
        summary = analysis.summary()
        birth_sizes: Counter = Counter()
        lineage_path = Path(temporary) / "lineage.jsonl"
        with lineage_path.open(encoding="utf-8") as stream:
            for line in stream:
                event = json.loads(line)
                if event.get("kind") == "birth":
                    birth_sizes[int(event["size"])] += 1
        analysis.close()
    structures = summary["structures"]
    replication = summary["replication"]
    return {
        "config_hash": config.hash(),
        "structures": structures["active_structures"],
        "max_size": max((int(size) for size in structures["size_distribution"]), default=0),
        "birth_sizes": {str(size): count for size, count in sorted(birth_sizes.items())},
        "candidates": replication["candidates"],
        "persistent": replication["persistent"],
        "max_generation": replication["max_generation"],
        "classified": replication["classified"],
        "world_hash": world.state_hash_full(),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "milestone": "m6.1",
        "engine_unchanged": True,
        "topology_census": topology_census(),
        "catalysis_probe": catalysis_probe(),
        "autocatalysis_probe": autocatalysis_probe(),
        "same_species_probe": same_species_probe(),
    }
    path = OUT / "diagnostics.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    census = payload["topology_census"]["by_condition"]
    print("| condizione | strutture (mediana) | dimensione max (mediana) | componenti cicliche | grado max |")
    print("|---|---|---|---|---|")
    for condition, block in census.items():
        print(
            f"| {condition} | {block['median_structures']} | {block['median_max_size']} "
            f"| {block['cyclic_components_total']} | {block['max_degree']} |"
        )
    print()
    print("nascite per dimensione (tutte le condizioni):")
    for condition, block in census.items():
        print(f"  {condition}: {block['birth_sizes_total']}")
    print()
    cat = payload["catalysis_probe"]
    print(
        f"catalisi (1500 passi): strutture {cat['off']['structures']} -> {cat['on']['structures']}, "
        f"nascite {cat['off']['births']} -> {cat['on']['births']}, "
        f"candidate {cat['off']['candidates']} -> {cat['on']['candidates']}"
    )
    auto = payload["autocatalysis_probe"]
    print(
        f"autocatalisi (2000 passi): legami {auto['off']['final_bonds']} -> {auto['on']['final_bonds']}"
    )
    same = payload["same_species_probe"]
    print(
        f"auto-catalisi di specie (2000 passi): nascite {same['birth_sizes']}, "
        f"candidate {same['candidates']}, classificato {same['classified']}"
    )
    print(f"JSON: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
