"""Configurazione dell'esperimento: parsing, validazione, hashing canonico.

La configurazione e' l'unica fonte di verita' per i parametri della simulazione.
Il suo hash canonico identifica senza ambiguita' l'esperimento ed e' registrato
in ogni artefatto prodotto (manifest, metriche, checkpoint).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = 1
MAX_SPECIES = 6
VALID_BOUNDARIES = ("periodic", "closed")
VALID_NEIGHBORHOODS = ("von_neumann",)
VALID_PLACEMENTS = ("random_uniform",)


class ConfigError(ValueError):
    """Configurazione assente, malformata o non valida."""


def _reject_unknown(mapping: Mapping[str, Any], allowed: set[str], where: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ConfigError(f"{where}: chiavi sconosciute {unknown}")


def _int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{name}: atteso un intero, ricevuto {value!r}")
    return value


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{name}: atteso un numero, ricevuto {value!r}")
    number = float(value)
    if not math.isfinite(number):
        raise ConfigError(f"{name}: valore non finito")
    return number


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{name}: attesa una stringa non vuota")
    return value


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConfigError(f"{name}: atteso un oggetto JSON")
    return value


@dataclass(frozen=True, slots=True)
class GridConfig:
    width: int
    height: int
    boundary: str = "periodic"

    @property
    def cells(self) -> int:
        return self.width * self.height

    def to_dict(self) -> dict[str, Any]:
        return {"width": self.width, "height": self.height, "boundary": self.boundary}


@dataclass(frozen=True, slots=True)
class SpeciesConfig:
    """Specie di particella: solo proprieta' locali, nessun comportamento codificato."""

    name: str
    count: int
    move_probability: float
    energy: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "count": self.count,
            "move_probability": self.move_probability,
            "energy": self.energy,
        }


@dataclass(frozen=True, slots=True)
class MetricsConfig:
    every: int = 100

    def to_dict(self) -> dict[str, Any]:
        return {"every": self.every}


@dataclass(frozen=True, slots=True)
class Config:
    seed: int
    grid: GridConfig
    species: tuple[SpeciesConfig, ...]
    neighborhood: str = "von_neumann"
    placement: str = "random_uniform"
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    schema_version: int = SCHEMA_VERSION

    # -- serializzazione -------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "seed": self.seed,
            "grid": self.grid.to_dict(),
            "neighborhood": self.neighborhood,
            "placement": self.placement,
            "species": [species.to_dict() for species in self.species],
            "metrics": self.metrics.to_dict(),
        }

    def canonical_json(self) -> str:
        """Serializzazione stabile: stessa config -> stessa stringa -> stesso hash."""
        return json.dumps(
            self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )

    def hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    # -- costruzione -----------------------------------------------------
    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Config":
        data = _mapping(data, "config")
        _reject_unknown(
            data,
            {
                "schema_version",
                "seed",
                "grid",
                "neighborhood",
                "placement",
                "species",
                "metrics",
            },
            "config",
        )

        grid_raw = _mapping(data.get("grid"), "grid")
        _reject_unknown(grid_raw, {"width", "height", "boundary"}, "grid")
        grid = GridConfig(
            width=_int(grid_raw.get("width"), "grid.width"),
            height=_int(grid_raw.get("height"), "grid.height"),
            boundary=_string(grid_raw.get("boundary", "periodic"), "grid.boundary"),
        )

        metrics_raw = _mapping(data.get("metrics", {}), "metrics")
        _reject_unknown(metrics_raw, {"every"}, "metrics")
        metrics = MetricsConfig(every=_int(metrics_raw.get("every", 100), "metrics.every"))

        species_raw = data.get("species")
        if not isinstance(species_raw, list) or not species_raw:
            raise ConfigError("species: attesa una lista non vuota")
        species = tuple(
            _species_from_dict(entry, index) for index, entry in enumerate(species_raw)
        )

        return cls(
            seed=_int(data.get("seed"), "seed"),
            grid=grid,
            species=species,
            neighborhood=_string(data.get("neighborhood", "von_neumann"), "neighborhood"),
            placement=_string(data.get("placement", "random_uniform"), "placement"),
            metrics=metrics,
            schema_version=_int(data.get("schema_version", SCHEMA_VERSION), "schema_version"),
        )

    # -- validazione -----------------------------------------------------
    def validate(self) -> "Config":
        if self.schema_version != SCHEMA_VERSION:
            raise ConfigError(
                f"schema_version: atteso {SCHEMA_VERSION}, ricevuto {self.schema_version}"
            )
        if self.grid.width < 2 or self.grid.height < 2:
            raise ConfigError("grid: larghezza e altezza devono essere >= 2")
        if self.grid.boundary not in VALID_BOUNDARIES:
            raise ConfigError(
                f"grid.boundary: atteso uno di {VALID_BOUNDARIES}, ricevuto {self.grid.boundary!r}"
            )
        if self.neighborhood not in VALID_NEIGHBORHOODS:
            raise ConfigError(
                f"neighborhood: atteso uno di {VALID_NEIGHBORHOODS}, "
                f"ricevuto {self.neighborhood!r}"
            )
        if self.placement not in VALID_PLACEMENTS:
            raise ConfigError(
                f"placement: atteso uno di {VALID_PLACEMENTS}, ricevuto {self.placement!r}"
            )
        if self.seed < 0:
            raise ConfigError("seed: deve essere un intero non negativo")
        if self.metrics.every < 1:
            raise ConfigError("metrics.every: deve essere >= 1")
        if len(self.species) > MAX_SPECIES:
            raise ConfigError(f"species: massimo {MAX_SPECIES} specie, ricevute {len(self.species)}")

        names = [species.name for species in self.species]
        if len(set(names)) != len(names):
            raise ConfigError(f"species: nomi duplicati in {names}")

        for species in self.species:
            if species.count < 0:
                raise ConfigError(f"species[{species.name}].count: deve essere >= 0")
            if not 0.0 <= species.move_probability <= 1.0:
                raise ConfigError(
                    f"species[{species.name}].move_probability: deve essere in [0, 1]"
                )
            if species.energy < 0:
                raise ConfigError(f"species[{species.name}].energy: deve essere >= 0")

        total = sum(species.count for species in self.species)
        if total > self.grid.cells:
            raise ConfigError(
                f"species: {total} particelle richieste su {self.grid.cells} celle disponibili"
            )
        return self


def _species_from_dict(entry: Any, index: int) -> SpeciesConfig:
    entry = _mapping(entry, f"species[{index}]")
    _reject_unknown(entry, {"name", "count", "move_probability", "energy"}, f"species[{index}]")
    return SpeciesConfig(
        name=_string(entry.get("name"), f"species[{index}].name"),
        count=_int(entry.get("count"), f"species[{index}].count"),
        move_probability=_number(
            entry.get("move_probability"), f"species[{index}].move_probability"
        ),
        energy=_int(entry.get("energy"), f"species[{index}].energy"),
    )


def load_config(path: str | Path) -> Config:
    """Legge e valida una configurazione JSON."""
    source = Path(path)
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"configurazione non trovata: {source}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"configurazione JSON non valida ({source}): {exc}") from exc
    return Config.from_dict(raw).validate()
