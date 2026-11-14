"""Universo: stato, avanzamento, invarianti e hash.

Il mondo e' un sistema chiuso in M1: nessuna reazione, nessuna sorgente, nessun
pozzo. L'energia e' quindi una quantita' intera conservata per costruzione.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from .config import Config, load_config
from .dynamics import step as advance_one_step
from .particles import EMPTY, InvariantError, ParticleStore
from .rng import RNG

Observer = Callable[["World"], None]


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
    )

    def __init__(
        self,
        config: Config,
        rng: RNG,
        store: ParticleStore,
        step: int = 0,
        moves_total: int = 0,
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
        # soglia intera: p * 2**64, così il confronto resta in aritmetica esatta
        self.move_thresholds = [
            int(species.move_probability * (1 << 64)) for species in config.species
        ]

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

    # -- evoluzione ------------------------------------------------------
    def advance(self, steps: int, observer: Observer | None = None) -> None:
        """Esegue ``steps`` passi; dopo ogni passo invoca ``observer(self)``."""
        if steps < 0:
            raise ValueError("steps non può essere negativo")
        for _ in range(steps):
            moves = advance_one_step(self)
            self.step += 1
            self.moves_total += moves
            if observer is not None:
                observer(self)

    # -- metriche --------------------------------------------------------
    def counts(self) -> dict[str, int]:
        return self.store.counts(self.species_names)

    def energy(self) -> int:
        per_species = [species.energy for species in self.config.species]
        total = 0
        for species_index in self.store.species:
            total += per_species[species_index]
        return total

    def configured_energy(self) -> int:
        return sum(species.count * species.energy for species in self.config.species)

    def occupancy(self) -> float:
        return len(self.store) / self.config.grid.cells

    def state_hash(self) -> str:
        return self.store.state_hash(self.species_names, self.config.grid.boundary)

    def snapshot(self) -> dict:
        """Fotografia compatta dello stato, usata nei test e nei confronti."""
        return {
            "step": self.step,
            "moves_total": self.moves_total,
            "state_hash": self.state_hash(),
            "rng": self.rng.state(),
            "energy": self.energy(),
            "counts": self.counts(),
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

        if width * height != cells:
            problems.append(f"dimensione griglia {width}x{height} diversa da {cells} celle")
        if len(store.grid) != cells:
            problems.append(f"griglia di occupazione con {len(store.grid)} celle, attese {cells}")

        seen: set[int] = set()
        invalid_species = 0
        actual_counts = [0] * species_count
        for index in range(len(store.xs)):
            x = store.xs[index]
            y = store.ys[index]
            species_index = store.species[index]
            if not 0 <= species_index < species_count:
                invalid_species += 1
                problems.append(f"particella {index}: specie {species_index} inesistente")
            else:
                actual_counts[species_index] += 1
            if not (0 <= x < width and 0 <= y < height):
                problems.append(f"particella {index}: posizione ({x}, {y}) fuori griglia")
                continue
            cell = y * width + x
            if cell in seen:
                problems.append(f"cella ({x}, {y}) occupata da più particelle")
            seen.add(cell)
            if store.grid[cell] != index:
                problems.append(
                    f"cella ({x}, {y}): la griglia indica {store.grid[cell]}, "
                    f"la particella {index} la rivendica"
                )

        occupied = sum(1 for cell in store.grid if cell != EMPTY)
        if occupied != len(seen):
            problems.append(f"griglia con {occupied} celle occupate ma {len(seen)} posizioni valide")

        expected_counts = {species.name: species.count for species in self.config.species}
        found_counts = {
            name: actual_counts[position] for position, name in enumerate(self.species_names)
        }
        if found_counts != expected_counts:
            problems.append(f"conteggi per specie {found_counts} diversi da {expected_counts}")

        if invalid_species == 0:
            expected_energy = self.configured_energy()
            actual_energy = self.energy()
            if actual_energy != expected_energy:
                problems.append(f"energia {actual_energy} diversa da {expected_energy}")

        return problems

    def check(self) -> None:
        problems = self.validate()
        if problems:
            raise InvariantError("stato non valido:\n- " + "\n- ".join(problems))

    # -- diagnostica -----------------------------------------------------
    def describe(self) -> str:
        counts = ", ".join(f"{name}={count}" for name, count in self.counts().items())
        return (
            f"passo={self.step} particelle={len(self.store)} "
            f"({counts}) spostamenti={self.moves_total} "
            f"occupazione={self.occupancy():.4f} energia={self.energy()} "
            f"hash={self.state_hash()[:16]}"
        )

    def __repr__(self) -> str:
        return f"World({self.describe()})"
