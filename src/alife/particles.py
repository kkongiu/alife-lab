"""Rappresentazione delle particelle e dell'occupazione della griglia.

Stato: array paralleli (posizione x, posizione y, indice di specie) piu' una
griglia piatta che mappa cella -> indice di particella (-1 = vuota).

L'indice di particella e' anche il suo identificatore stabile: in M1 non esiste
nascita, morte o riordinamento, quindi l'ordine dell'array e' canonico. Questa
semplificazione e' documentata in SPEC.md come punto da rivedere in M2.
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from .config import Config
    from .rng import RNG


class InvariantError(RuntimeError):
    """Violazione di un invariante fisico o computazionale."""


EMPTY = -1


class ParticleStore:
    """Particelle + griglia di occupazione, mantenute sempre coerenti."""

    __slots__ = ("width", "height", "xs", "ys", "species", "grid")

    def __init__(
        self,
        width: int,
        height: int,
        xs: Sequence[int],
        ys: Sequence[int],
        species: Sequence[int],
    ) -> None:
        if width < 1 or height < 1:
            raise InvariantError("dimensioni della griglia non valide")
        if not (len(xs) == len(ys) == len(species)):
            raise InvariantError("array delle particelle di lunghezze diverse")

        self.width = width
        self.height = height
        self.xs = list(xs)
        self.ys = list(ys)
        self.species = list(species)
        self.grid = [EMPTY] * (width * height)

        for index, (x, y) in enumerate(zip(self.xs, self.ys)):
            if not (0 <= x < width and 0 <= y < height):
                raise InvariantError(f"particella {index} fuori griglia: ({x}, {y})")
            cell = y * width + x
            if self.grid[cell] != EMPTY:
                raise InvariantError(
                    f"doppia occupazione della cella ({x}, {y}) "
                    f"da parte delle particelle {self.grid[cell]} e {index}"
                )
            self.grid[cell] = index

    # -- costruzione -----------------------------------------------------
    @classmethod
    def place_random(cls, config: "Config", rng: "RNG") -> "ParticleStore":
        """Collocazione uniforme senza sostituzione, riproducibile.

        Una sola estrazione RNG per particella piazzata: il flusso consumato
        dall'inizializzazione dipende solo dal numero totale di particelle.
        """
        width = config.grid.width
        height = config.grid.height
        cells = width * height
        total = sum(species.count for species in config.species)
        if total > cells:
            raise InvariantError("piu' particelle che celle")

        free = list(range(cells))
        xs: list[int] = []
        ys: list[int] = []
        species: list[int] = []
        for species_index, species_config in enumerate(config.species):
            for _ in range(species_config.count):
                pick = rng.raw() % len(free)
                cell = free[pick]
                free[pick] = free[-1]
                free.pop()
                y, x = divmod(cell, width)
                xs.append(x)
                ys.append(y)
                species.append(species_index)
        return cls(width, height, xs, ys, species)

    # -- interrogazione --------------------------------------------------
    def __len__(self) -> int:
        return len(self.xs)

    def counts(self, species_names: Sequence[str]) -> dict[str, int]:
        counts = [0] * len(species_names)
        for species_index in self.species:
            counts[species_index] += 1
        return {name: counts[index] for index, name in enumerate(species_names)}

    def records(self) -> list[list[int]]:
        """Rappresentazione canonica ordinata: [[x, y, specie], ...]."""
        return [
            [x, y, species_index]
            for x, y, species_index in zip(self.xs, self.ys, self.species)
        ]

    def state_hash(self, species_names: Sequence[str], boundary: str) -> str:
        payload = {
            "schema": 1,
            "width": self.width,
            "height": self.height,
            "boundary": boundary,
            "species": list(species_names),
            "particles": self.records(),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def occupied_cells(self) -> int:
        """Numero di celle occupate (coerente con len(self) se la griglia è integra)."""
        return sum(1 for cell in self.grid if cell != EMPTY)

    def position_of(self, index: int) -> tuple[int, int]:
        return self.xs[index], self.ys[index]
