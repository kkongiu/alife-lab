"""Helper condivisi dai test."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from alife.config import Config
from alife.particles import ParticleStore
from alife.rng import RNG
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "configs" / "baseline.json"
QUICK = ROOT / "configs" / "quick.json"
M2_QUICK = ROOT / "configs" / "m2_quick.json"
M2_BASELINE = ROOT / "configs" / "m2_baseline.json"
M2_CATALYSIS = ROOT / "configs" / "m2_catalysis.json"
M3_QUICK = ROOT / "configs" / "m3_quick.json"
M3_BASELINE = ROOT / "configs" / "m3_baseline.json"
M3_UNFED = ROOT / "configs" / "m3_unfed.json"


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


def make_chemistry_config(
    seed: int = 3,
    width: int = 8,
    height: int = 8,
    species: list[dict] | None = None,
    chemistry: dict | None = None,
) -> Config:
    """Configurazione M2 minima, con chimica attiva e parametri deterministici."""
    if species is None:
        species = [
            {"name": "S0", "count": 4, "move_probability": 1.0, "energy": 10, "max_bonds": 2},
            {"name": "S1", "count": 4, "move_probability": 1.0, "energy": 10, "max_bonds": 2},
            {"name": "S2", "count": 2, "move_probability": 1.0, "energy": 10, "max_bonds": 0},
        ]
    if chemistry is None:
        chemistry = {
            "enabled": True,
            "bond_cost": 2,
            "formation_probability": 1.0,
            "break_probability": 0.0,
            "allowed_pairs": [["S0", "S0"], ["S0", "S1"]],
            "catalysis": [],
        }
    return Config.from_dict(
        {
            "schema_version": 2,
            "seed": seed,
            "grid": {"width": width, "height": height, "boundary": "periodic"},
            "neighborhood": "von_neumann",
            "placement": "random_uniform",
            "species": species,
            "chemistry": chemistry,
            "metrics": {"every": 5},
        }
    ).validate()


def make_energy_config(
    seed: int = 3,
    width: int = 8,
    height: int = 8,
    species: list[dict] | None = None,
    chemistry: dict | None = None,
    energy: dict | None = None,
) -> Config:
    """Configurazione M3 minima: schema 3, flussi disattivati salvo diversa indicazione."""
    if species is None:
        species = [
            {"name": "S0", "count": 4, "move_probability": 1.0, "energy": 10, "max_bonds": 2},
            {"name": "S1", "count": 4, "move_probability": 1.0, "energy": 10, "max_bonds": 2},
            {"name": "S2", "count": 2, "move_probability": 1.0, "energy": 10, "max_bonds": 0},
        ]
    if chemistry is None:
        chemistry = {
            "enabled": True,
            "bond_cost": 2,
            "formation_probability": 1.0,
            "break_probability": 0.0,
            "allowed_pairs": [["S0", "S0"], ["S0", "S1"]],
            "catalysis": [],
        }
    if energy is None:
        energy = {}
    return Config.from_dict(
        {
            "schema_version": 3,
            "seed": seed,
            "grid": {"width": width, "height": height, "boundary": "periodic"},
            "neighborhood": "von_neumann",
            "placement": "random_uniform",
            "species": species,
            "chemistry": chemistry,
            "energy": energy,
            "metrics": {"every": 5},
        }
    ).validate()


def world_with(
    config: Config,
    positions: Sequence[tuple[int, int]],
    species: Sequence[int],
    energy: Sequence[int] | None = None,
    bonds: Sequence[tuple[int, int, int]] = (),
) -> World:
    """Mondo costruito a mano per test deterministici sulla chimica."""
    ids = list(range(len(positions)))
    xs = [position[0] for position in positions]
    ys = [position[1] for position in positions]
    if energy is None:
        energy = [config.species[index].energy for index in species]
    store = ParticleStore(
        config.grid.width,
        config.grid.height,
        ids,
        xs,
        ys,
        list(species),
        list(energy),
        bonds,
    )
    return World(config, RNG(config.seed), store)
