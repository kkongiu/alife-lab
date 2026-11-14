"""Configurazione dell'esperimento: parsing, validazione, hashing canonico.

Schema 1: motore fisico (M1) — solo specie con mobilità ed energia iniziale.
Schema 2: chimica (M2) — aggiunge `max_bonds` per specie e il blocco `chemistry`
con costo dei legami, probabilità di formazione/rottura, coppie ammesse e
catalisi. Le configurazioni schema 1 restano serializzabili e hashabili
esattamente come in M1.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = 3
MAX_SPECIES = 6
VALID_BOUNDARIES = ("periodic", "closed")
VALID_NEIGHBORHOODS = ("von_neumann",)
VALID_PLACEMENTS = ("random_uniform",)
MAX_BONDS_PER_PARTICLE = 4


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
    """Specie di particella: proprietà locali, nessun comportamento codificato."""

    name: str
    count: int
    move_probability: float
    energy: int
    max_bonds: int = 0

    def to_dict(self, include_max_bonds: bool = True) -> dict[str, Any]:
        payload = {
            "name": self.name,
            "count": self.count,
            "move_probability": self.move_probability,
            "energy": self.energy,
        }
        if include_max_bonds:
            payload["max_bonds"] = self.max_bonds
        return payload


@dataclass(frozen=True, slots=True)
class CatalysisRule:
    """Una specie catalizza la formazione di un tipo di legame."""

    catalyst: str
    pair: tuple[str, str]
    factor: float

    def to_dict(self) -> dict[str, Any]:
        return {"catalyst": self.catalyst, "pair": list(self.pair), "factor": self.factor}


@dataclass(frozen=True, slots=True)
class ChemistryConfig:
    enabled: bool = False
    bond_cost: int = 0
    formation_probability: float = 0.0
    break_probability: float = 0.0
    allowed_pairs: tuple[tuple[str, str], ...] = ()
    catalysis: tuple[CatalysisRule, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "bond_cost": self.bond_cost,
            "formation_probability": self.formation_probability,
            "break_probability": self.break_probability,
            "allowed_pairs": [list(pair) for pair in self.allowed_pairs],
            "catalysis": [rule.to_dict() for rule in self.catalysis],
        }


DISABLED_CHEMISTRY = ChemistryConfig()


@dataclass(frozen=True, slots=True)
class DecayConfig:
    """Decadimento deterministico: `num` quanti ogni `den` passi."""

    num: int = 0
    den: int = 1

    def to_dict(self) -> dict[str, int]:
        return {"num": self.num, "den": self.den}


@dataclass(frozen=True, slots=True)
class SourceConfig:
    """Sorgente localizzata con tasso razionale e capacità per particella."""

    x: int
    y: int
    rate_num: int
    rate_den: int
    capacity: int
    overflow: str = "discard"

    def to_dict(self) -> dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "rate_num": self.rate_num,
            "rate_den": self.rate_den,
            "capacity": self.capacity,
            "overflow": self.overflow,
        }


@dataclass(frozen=True, slots=True)
class EnergyConfig:
    """Flussi energetici, dissipazione e costi (schema 3)."""

    movement_cost: int = 0
    formation_dissipation: int = 0
    breaking_dissipation: int = 0
    particle_decay: DecayConfig = field(default_factory=DecayConfig)
    bond_decay: DecayConfig = field(default_factory=DecayConfig)
    sources: tuple[SourceConfig, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "movement_cost": self.movement_cost,
            "formation_dissipation": self.formation_dissipation,
            "breaking_dissipation": self.breaking_dissipation,
            "particle_decay": self.particle_decay.to_dict(),
            "bond_decay": self.bond_decay.to_dict(),
            "sources": [source.to_dict() for source in self.sources],
        }


DISABLED_ENERGY = EnergyConfig()


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
    chemistry: ChemistryConfig = field(default_factory=ChemistryConfig)
    energy: EnergyConfig = field(default_factory=EnergyConfig)
    schema_version: int = SCHEMA_VERSION

    # -- serializzazione -------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        include_bonds = self.schema_version >= 2
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "seed": self.seed,
            "grid": self.grid.to_dict(),
            "neighborhood": self.neighborhood,
            "placement": self.placement,
            "species": [
                species.to_dict(include_max_bonds=include_bonds) for species in self.species
            ],
            "metrics": self.metrics.to_dict(),
        }
        if include_bonds:
            payload["chemistry"] = self.chemistry.to_dict()
        if self.schema_version >= 3:
            payload["energy"] = self.energy.to_dict()
        return payload

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
                "chemistry",
                "energy",
            },
            "config",
        )
        schema_version = _int(data.get("schema_version", SCHEMA_VERSION), "schema_version")
        if schema_version not in (1, 2, 3):
            raise ConfigError(f"schema_version: attesa 1, 2 o 3, ricevuta {schema_version}")

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
            _species_from_dict(entry, index, schema_version)
            for index, entry in enumerate(species_raw)
        )

        if schema_version >= 2 and "chemistry" in data:
            chemistry = _chemistry_from_dict(_mapping(data["chemistry"], "chemistry"))
        else:
            if schema_version == 1 and "chemistry" in data:
                raise ConfigError("chemistry: non ammesso nello schema 1")
            chemistry = DISABLED_CHEMISTRY

        if schema_version >= 3 and "energy" in data:
            energy = _energy_from_dict(_mapping(data["energy"], "energy"))
        else:
            if schema_version < 3 and "energy" in data:
                raise ConfigError(f"energy: non ammesso nello schema {schema_version}")
            energy = DISABLED_ENERGY

        return cls(
            seed=_int(data.get("seed"), "seed"),
            grid=grid,
            species=species,
            neighborhood=_string(data.get("neighborhood", "von_neumann"), "neighborhood"),
            placement=_string(data.get("placement", "random_uniform"), "placement"),
            metrics=metrics,
            chemistry=chemistry,
            energy=energy,
            schema_version=schema_version,
        )

    # -- validazione -----------------------------------------------------
    def validate(self) -> "Config":
        if self.schema_version not in (1, 2, 3):
            raise ConfigError(f"schema_version: attesa 1, 2 o 3, ricevuta {self.schema_version}")
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
            if self.schema_version == 1 and species.max_bonds != 0:
                raise ConfigError(
                    f"species[{species.name}].max_bonds: non ammesso nello schema 1"
                )
            if not 0 <= species.max_bonds <= MAX_BONDS_PER_PARTICLE:
                raise ConfigError(
                    f"species[{species.name}].max_bonds: deve essere in [0, {MAX_BONDS_PER_PARTICLE}]"
                )

        total = sum(species.count for species in self.species)
        if total > self.grid.cells:
            raise ConfigError(
                f"species: {total} particelle richieste su {self.grid.cells} celle disponibili"
            )

        self._validate_chemistry(set(names))
        self._validate_energy()
        return self

    def _validate_chemistry(self, names: set[str]) -> None:
        chemistry = self.chemistry
        if self.schema_version == 1:
            if chemistry.enabled:
                raise ConfigError("chemistry: non ammesso nello schema 1")
            return

        if chemistry.bond_cost < 0:
            raise ConfigError("chemistry.bond_cost: deve essere >= 0")
        for field_name, value in (
            ("formation_probability", chemistry.formation_probability),
            ("break_probability", chemistry.break_probability),
        ):
            if not 0.0 <= value <= 1.0:
                raise ConfigError(f"chemistry.{field_name}: deve essere in [0, 1]")

        for pair in chemistry.allowed_pairs:
            if len(pair) != 2 or pair[0] not in names or pair[1] not in names:
                raise ConfigError(f"chemistry.allowed_pairs: coppia non valida {pair!r}")

        if not chemistry.enabled:
            return

        if not chemistry.allowed_pairs:
            raise ConfigError("chemistry.allowed_pairs: almeno una coppia con chimica attiva")
        capable = {
            species.name for species in self.species if species.max_bonds > 0
        }
        usable = [
            pair for pair in chemistry.allowed_pairs if pair[0] in capable and pair[1] in capable
        ]
        if not usable:
            raise ConfigError(
                "chemistry: nessuna coppia ammessa fra specie con max_bonds > 0"
            )
        for rule in chemistry.catalysis:
            if rule.catalyst not in names:
                raise ConfigError(f"chemistry.catalysis: catalizzatore {rule.catalyst!r} inesistente")
            if rule.pair not in chemistry.allowed_pairs:
                raise ConfigError(
                    f"chemistry.catalysis: la coppia {rule.pair!r} non è fra quelle ammesse"
                )
            if rule.factor < 1.0:
                raise ConfigError("chemistry.catalysis.factor: deve essere >= 1")

    def _validate_energy(self) -> None:
        if self.schema_version < 3:
            if self.energy != DISABLED_ENERGY:
                raise ConfigError(
                    f"energy: non ammesso nello schema {self.schema_version}"
                )
            return

        block = self.energy
        for field_name in (
            "movement_cost",
            "formation_dissipation",
            "breaking_dissipation",
        ):
            if getattr(block, field_name) < 0:
                raise ConfigError(f"energy.{field_name}: deve essere >= 0")
        if (
            block.formation_dissipation or block.breaking_dissipation
        ) and not self.chemistry.enabled:
            raise ConfigError(
                "energy: formation/breaking_dissipation richiedono chemistry.enabled"
            )
        for name, decay in (
            ("particle_decay", block.particle_decay),
            ("bond_decay", block.bond_decay),
        ):
            if decay.num < 0:
                raise ConfigError(f"energy.{name}.num: deve essere >= 0")
            if decay.den < 1:
                raise ConfigError(f"energy.{name}.den: deve essere >= 1")
            if decay.num > decay.den:
                raise ConfigError(
                    f"energy.{name}.num: non può superare den ({decay.num} > {decay.den})"
                )

        seen: set[tuple[int, int]] = set()
        for index, source in enumerate(block.sources):
            if not (0 <= source.x < self.grid.width and 0 <= source.y < self.grid.height):
                raise ConfigError(
                    f"energy.sources[{index}]: posizione ({source.x}, {source.y}) fuori griglia"
                )
            if (source.x, source.y) in seen:
                raise ConfigError(f"energy.sources[{index}]: cella duplicata")
            seen.add((source.x, source.y))
            if source.rate_num < 0:
                raise ConfigError(f"energy.sources[{index}].rate_num: deve essere >= 0")
            if source.rate_den < 1:
                raise ConfigError(f"energy.sources[{index}].rate_den: deve essere >= 1")
            if source.capacity < 0:
                raise ConfigError(f"energy.sources[{index}].capacity: deve essere >= 0")
            if source.overflow != "discard":
                raise ConfigError(
                    f"energy.sources[{index}].overflow: unico valore ammesso è 'discard'"
                )


def _decay_from_dict(entry: Any, name: str) -> DecayConfig:
    entry = _mapping(entry, name)
    _reject_unknown(entry, {"num", "den"}, name)
    return DecayConfig(
        num=_int(entry.get("num", 0), f"{name}.num"),
        den=_int(entry.get("den", 1), f"{name}.den"),
    )


def _energy_from_dict(data: Mapping[str, Any]) -> EnergyConfig:
    _reject_unknown(
        data,
        {
            "movement_cost",
            "formation_dissipation",
            "breaking_dissipation",
            "particle_decay",
            "bond_decay",
            "sources",
        },
        "energy",
    )
    sources_raw = data.get("sources", [])
    if not isinstance(sources_raw, list):
        raise ConfigError("energy.sources: attesa una lista")
    sources: list[SourceConfig] = []
    for index, entry in enumerate(sources_raw):
        entry = _mapping(entry, f"energy.sources[{index}]")
        _reject_unknown(
            entry,
            {"x", "y", "rate_num", "rate_den", "capacity", "overflow"},
            f"energy.sources[{index}]",
        )
        sources.append(
            SourceConfig(
                x=_int(entry.get("x"), f"energy.sources[{index}].x"),
                y=_int(entry.get("y"), f"energy.sources[{index}].y"),
                rate_num=_int(entry.get("rate_num", 0), f"energy.sources[{index}].rate_num"),
                rate_den=_int(entry.get("rate_den", 1), f"energy.sources[{index}].rate_den"),
                capacity=_int(entry.get("capacity", 0), f"energy.sources[{index}].capacity"),
                overflow=_string(
                    entry.get("overflow", "discard"), f"energy.sources[{index}].overflow"
                ),
            )
        )
    # forma canonica: ordine (y, x), così gli accumulatori sono serializzati in
    # un ordine indipendente da come l'utente ha scritto il file
    sources.sort(key=lambda source: (source.y, source.x))

    return EnergyConfig(
        movement_cost=_int(data.get("movement_cost", 0), "energy.movement_cost"),
        formation_dissipation=_int(
            data.get("formation_dissipation", 0), "energy.formation_dissipation"
        ),
        breaking_dissipation=_int(
            data.get("breaking_dissipation", 0), "energy.breaking_dissipation"
        ),
        particle_decay=_decay_from_dict(
            data.get("particle_decay", {}), "energy.particle_decay"
        ),
        bond_decay=_decay_from_dict(data.get("bond_decay", {}), "energy.bond_decay"),
        sources=tuple(sources),
    )


def _species_from_dict(entry: Any, index: int, schema_version: int) -> SpeciesConfig:
    entry = _mapping(entry, f"species[{index}]")
    allowed = {"name", "count", "move_probability", "energy"}
    if schema_version >= 2:
        allowed.add("max_bonds")
    _reject_unknown(entry, allowed, f"species[{index}]")
    return SpeciesConfig(
        name=_string(entry.get("name"), f"species[{index}].name"),
        count=_int(entry.get("count"), f"species[{index}].count"),
        move_probability=_number(
            entry.get("move_probability"), f"species[{index}].move_probability"
        ),
        energy=_int(entry.get("energy"), f"species[{index}].energy"),
        max_bonds=_int(entry.get("max_bonds", 0), f"species[{index}].max_bonds")
        if schema_version >= 2
        else 0,
    )


def _chemistry_from_dict(data: Mapping[str, Any]) -> ChemistryConfig:
    _reject_unknown(
        data,
        {
            "enabled",
            "bond_cost",
            "formation_probability",
            "break_probability",
            "allowed_pairs",
            "catalysis",
        },
        "chemistry",
    )
    pairs_raw = data.get("allowed_pairs", [])
    if not isinstance(pairs_raw, list):
        raise ConfigError("chemistry.allowed_pairs: attesa una lista")
    pairs: list[tuple[str, str]] = []
    for entry in pairs_raw:
        if not isinstance(entry, list) or len(entry) != 2:
            raise ConfigError(f"chemistry.allowed_pairs: coppia malformata {entry!r}")
        pairs.append((_string(entry[0], "allowed_pairs"), _string(entry[1], "allowed_pairs")))
    # forma canonica: coppia ordinata, lista ordinata e senza duplicati
    normalized = sorted({tuple(sorted(pair)) for pair in pairs})

    catalysis_raw = data.get("catalysis", [])
    if not isinstance(catalysis_raw, list):
        raise ConfigError("chemistry.catalysis: attesa una lista")
    rules: list[CatalysisRule] = []
    for entry in catalysis_raw:
        rule_raw = _mapping(entry, "catalysis")
        _reject_unknown(rule_raw, {"catalyst", "pair", "factor"}, "catalysis")
        pair_raw = rule_raw.get("pair")
        if not isinstance(pair_raw, list) or len(pair_raw) != 2:
            raise ConfigError("chemistry.catalysis.pair: attesa una coppia")
        pair = tuple(sorted((_string(pair_raw[0], "pair"), _string(pair_raw[1], "pair"))))
        rules.append(
            CatalysisRule(
                catalyst=_string(rule_raw.get("catalyst"), "chemistry.catalysis.catalyst"),
                pair=pair,
                factor=_number(rule_raw.get("factor"), "chemistry.catalysis.factor"),
            )
        )
    rules.sort(key=lambda rule: (rule.pair, rule.catalyst))

    return ChemistryConfig(
        enabled=bool(data.get("enabled", False)),
        bond_cost=_int(data.get("bond_cost", 0), "chemistry.bond_cost"),
        formation_probability=_number(
            data.get("formation_probability", 0.0), "chemistry.formation_probability"
        ),
        break_probability=_number(
            data.get("break_probability", 0.0), "chemistry.break_probability"
        ),
        allowed_pairs=tuple(normalized),
        catalysis=tuple(rules),
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
