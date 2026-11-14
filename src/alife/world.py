"""Universo: stato, avanzamento, invarianti e hash.

M2: sistema ancora chiuso (nessuna sorgente, nessun pozzo). L'energia totale è
`Σ energia delle particelle + Σ energia dei legami` ed è conservata per
costruzione.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from .chemistry import aggregate_stats
from .config import Config, load_config
from .dynamics import step as advance_one_step
from .particles import EMPTY, InvariantError, ParticleStore
from .rng import RNG

Observer = Callable[["World"], None]
TWO64 = 1 << 64


class World:
    """Stato completo e riproducibile della simulazione."""

    __slots__ = (
        "config",
        "rng",
        "store",
        "step",
        "moves_total",
        "periodic",
        "species_names",
        "move_thresholds",
        "chemistry",
        "chemistry_enabled",
        "bond_cost",
        "max_bonds",
        "allowed_pairs",
        "formation_threshold",
        "break_threshold",
        "catalysis_lookup",
        "next_id",
        "bonds_formed_total",
        "bonds_broken_total",
        "event_sink",
    )

    def __init__(
        self,
        config: Config,
        rng: RNG,
        store: ParticleStore,
        step: int = 0,
        moves_total: int = 0,
        next_id: int | None = None,
        bonds_formed_total: int = 0,
        bonds_broken_total: int = 0,
    ) -> None:
        if store.width != config.grid.width or store.height != config.grid.height:
            raise InvariantError("la griglia delle particelle non corrisponde alla configurazione")
        self.config = config
        self.rng = rng
        self.store = store
        self.step = step
        self.moves_total = moves_total
        self.periodic = config.grid.boundary == "periodic"
        self.species_names = [species.name for species in config.species]
        self.move_thresholds = [
            int(species.move_probability * TWO64) for species in config.species
        ]

        chemistry = config.chemistry
        self.chemistry = chemistry
        self.chemistry_enabled = chemistry.enabled
        self.bond_cost = chemistry.bond_cost
        self.max_bonds = [species.max_bonds for species in config.species]
        self.allowed_pairs = self._species_pairs(chemistry.allowed_pairs)
        self.formation_threshold = int(chemistry.formation_probability * TWO64)
        self.break_threshold = int(chemistry.break_probability * TWO64)
        self.catalysis_lookup = self._build_catalysis_lookup(chemistry.catalysis)
        self.next_id = next_id if next_id is not None else _next_id(store)
        self.bonds_formed_total = bonds_formed_total
        self.bonds_broken_total = bonds_broken_total
        self.event_sink = None

    # -- costruzione -----------------------------------------------------
    @classmethod
    def create(cls, config: Config) -> "World":
        config.validate()
        rng = RNG(config.seed)
        store = ParticleStore.place_random(config, rng)
        world = cls(config, rng, store)
        world.check()
        return world

    @classmethod
    def from_config_file(cls, path: str | Path) -> "World":
        return cls.create(load_config(path))

    # -- chimica ---------------------------------------------------------
    def _species_pairs(self, pairs: tuple[tuple[str, str], ...]) -> set[tuple[int, int]]:
        index = {name: position for position, name in enumerate(self.species_names)}
        return {(index[a], index[b]) for a, b in pairs}

    def _build_catalysis_lookup(self, rules) -> dict[tuple[int, int], dict[int, float]]:
        index = {name: position for position, name in enumerate(self.species_names)}
        lookup: dict[tuple[int, int], dict[int, float]] = {}
        for rule in rules:
            pair = tuple(sorted((index[rule.pair[0]], index[rule.pair[1]])))
            lookup.setdefault(pair, {})[index[rule.catalyst]] = float(rule.factor)
        return lookup

    def record_bond_event(self, event) -> None:
        if self.event_sink is not None:
            self.event_sink.emit(event)

    # -- evoluzione ------------------------------------------------------
    def advance(self, steps: int, observer: Observer | None = None) -> None:
        """Esegue ``steps`` passi; dopo ogni passo invoca ``observer(self)``."""
        if steps < 0:
            raise ValueError("steps non può essere negativo")
        for _ in range(steps):
            report = advance_one_step(self)
            self.moves_total += report.moves
            self.step += 1
            if observer is not None:
                observer(self)

    # -- energia ---------------------------------------------------------
    def energy_particles(self) -> int:
        return sum(self.store.energy)

    def energy_bonds(self) -> int:
        return sum(self.store.bonds.values())

    def energy(self) -> int:
        return self.energy_particles() + self.energy_bonds()

    def configured_energy(self) -> int:
        return sum(species.count * species.energy for species in self.config.species)

    # -- metriche --------------------------------------------------------
    def counts(self) -> dict[str, int]:
        return self.store.counts(self.species_names)

    def occupancy(self) -> float:
        return len(self.store) / self.config.grid.cells

    def aggregates(self) -> dict[str, int | float]:
        return aggregate_stats(self.store)

    def state_hash(self) -> str:
        """Hash materiale (definizione M1, invariata)."""
        return self.store.state_hash(self.species_names, self.config.grid.boundary)

    def state_hash_full(self) -> str:
        """Hash completo: identità, energia e legami."""
        return self.store.state_hash_full(self.species_names, self.config.grid.boundary)

    def snapshot(self) -> dict:
        """Fotografia compatta dello stato, usata nei test e nei confronti."""
        return {
            "step": self.step,
            "moves_total": self.moves_total,
            "state_hash": self.state_hash(),
            "state_hash_full": self.state_hash_full(),
            "rng": self.rng.state(),
            "energy": self.energy(),
            "energy_particles": self.energy_particles(),
            "energy_bonds": self.energy_bonds(),
            "counts": self.counts(),
            "bonds": len(self.store.bonds),
            "next_id": self.next_id,
        }

    # -- invarianti ------------------------------------------------------
    def validate(self) -> list[str]:
        """Ritorna l'elenco dei problemi rilevati (vuoto = stato integro)."""
        problems: list[str] = []
        store = self.store
        width = store.width
        height = store.height
        cells = self.config.grid.cells
        species_count = len(self.config.species)

        sizes = {len(store.ids), len(store.xs), len(store.ys), len(store.species), len(store.energy)}
        if len(sizes) != 1:
            problems.append(f"array delle particelle di lunghezze diverse: {sorted(sizes)}")
            return problems
        if len(store.degree) != len(store.ids):
            problems.append("array dei gradi di lunghezza diversa dalle particelle")
            return problems
        if width * height != cells:
            problems.append(f"dimensione griglia {width}x{height} diversa da {cells} celle")
        if len(store.grid) != cells:
            problems.append(f"griglia di occupazione con {len(store.grid)} celle, attese {cells}")

        seen_ids = set()
        for index, identifier in enumerate(store.ids):
            if identifier < 0:
                problems.append(f"particella {index}: identificativo negativo")
            elif identifier in seen_ids:
                problems.append(f"identificativo duplicato: {identifier}")
            seen_ids.add(identifier)
            if identifier >= self.next_id:
                problems.append(
                    f"particella {identifier}: identificativo non inferiore a next_id "
                    f"({self.next_id})"
                )

        seen_cells: set[int] = set()
        invalid_species = 0
        actual_counts = [0] * species_count
        for index in range(len(store.ids)):
            x = store.xs[index]
            y = store.ys[index]
            species_index = store.species[index]
            if not 0 <= species_index < species_count:
                invalid_species += 1
                problems.append(f"particella {index}: specie {species_index} inesistente")
            else:
                actual_counts[species_index] += 1
            if store.energy[index] < 0:
                problems.append(f"particella {index}: energia negativa")
            if not (0 <= x < width and 0 <= y < height):
                problems.append(f"particella {index}: posizione ({x}, {y}) fuori griglia")
                continue
            cell = y * width + x
            if cell in seen_cells:
                problems.append(f"cella ({x}, {y}) occupata da più particelle")
            seen_cells.add(cell)
            if store.grid[cell] != index:
                problems.append(
                    f"cella ({x}, {y}): la griglia indica {store.grid[cell]}, "
                    f"la particella {index} la rivendica"
                )

        occupied = sum(1 for cell in store.grid if cell != EMPTY)
        if occupied != len(seen_cells):
            problems.append(f"griglia con {occupied} celle occupate ma {len(seen_cells)} posizioni valide")

        expected_counts = {species.name: species.count for species in self.config.species}
        found_counts = {
            name: actual_counts[position] for position, name in enumerate(self.species_names)
        }
        if found_counts != expected_counts:
            problems.append(f"conteggi per specie {found_counts} diversi da {expected_counts}")

        problems.extend(self._validate_bonds())

        if invalid_species == 0:
            expected_energy = self.configured_energy()
            actual_energy = self.energy()
            if actual_energy != expected_energy:
                problems.append(f"energia {actual_energy} diversa da {expected_energy}")

        return problems

    def _validate_bonds(self) -> list[str]:
        problems: list[str] = []
        store = self.store
        if store.bonds and not self.chemistry_enabled:
            problems.append("legami presenti ma chimica disabilitata")

        degrees = [0] * len(store.ids)
        for (index_a, index_b), bond_energy in store.bonds.items():
            if not (0 <= index_a < len(store.ids) and 0 <= index_b < len(store.ids)):
                problems.append(f"legame con indice inesistente: ({index_a}, {index_b})")
                continue
            if index_a == index_b:
                problems.append(f"legame di una particella con se stessa: {store.ids[index_a]}")
                continue
            if bond_energy < 0:
                problems.append(f"energia negativa nel legame ({index_a}, {index_b})")
            degrees[index_a] += 1
            degrees[index_b] += 1
            if not self._adjacent(index_a, index_b):
                problems.append(
                    f"legame fra particelle non adiacenti: {store.ids[index_a]} e {store.ids[index_b]}"
                )

        for index, degree in enumerate(degrees):
            if degree != store.degree[index]:
                problems.append(
                    f"particella {store.ids[index]}: grado {store.degree[index]} "
                    f"diverso dai legami registrati ({degree})"
                )
            species_index = store.species[index]
            if 0 <= species_index < len(self.max_bonds):
                limit = self.max_bonds[species_index]
                if degree > limit:
                    problems.append(
                        f"particella {store.ids[index]}: {degree} legami oltre il massimo "
                        f"{limit}"
                    )
        return problems

    def _adjacent(self, index_a: int, index_b: int) -> bool:
        store = self.store
        dx = abs(store.xs[index_a] - store.xs[index_b])
        dy = abs(store.ys[index_a] - store.ys[index_b])
        if self.periodic:
            dx = min(dx, store.width - dx)
            dy = min(dy, store.height - dy)
        return dx + dy == 1

    def check(self) -> None:
        problems = self.validate()
        if problems:
            raise InvariantError("stato non valido:\n- " + "\n- ".join(problems))

    # -- diagnostica -----------------------------------------------------
    def describe(self) -> str:
        counts = ", ".join(f"{name}={count}" for name, count in self.counts().items())
        return (
            f"passo={self.step} particelle={len(self.store)} ({counts}) "
            f"spostamenti={self.moves_total} legami={len(self.store.bonds)} "
            f"occupazione={self.occupancy():.4f} energia={self.energy()} "
            f"hash={self.state_hash_full()[:16]}"
        )

    def __repr__(self) -> str:
        return f"World({self.describe()})"


def _next_id(store: ParticleStore) -> int:
    return max(store.ids) + 1 if store.ids else 0
