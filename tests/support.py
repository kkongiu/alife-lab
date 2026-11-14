"""Helper condivisi dai test."""

from __future__ import annotations

from pathlib import Path

from alife.config import Config

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "configs" / "baseline.json"
QUICK = ROOT / "configs" / "quick.json"


def make_config(
    seed: int = 11,
    width: int = 16,
    height: int = 16,
    boundary: str = "periodic",
    species: list[dict] | None = None,
    every: int = 5,
) -> Config:
    if species is None:
        species = [
            {"name": "A", "count": 12, "move_probability": 0.8, "energy": 3},
            {"name": "B", "count": 8, "move_probability": 0.3, "energy": 5},
        ]
    return Config.from_dict(
        {
            "schema_version": 1,
            "seed": seed,
            "grid": {"width": width, "height": height, "boundary": boundary},
            "neighborhood": "von_neumann",
            "placement": "random_uniform",
            "species": species,
            "metrics": {"every": every},
        }
    ).validate()
