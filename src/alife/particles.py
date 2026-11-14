"""Rappresentazione delle particelle, dell'energia e dei legami.

Stato: array paralleli (identificativo, posizione x, posizione y, indice di
specie, energia) più una griglia piatta cella -> indice di particella.

L'identificativo è persistente: assegnato alla creazione, salvato nel checkpoint
e mai riutilizzato. In M2 non esistono nascita né morte, quindi identificativo e
indice coincidono sempre; il formato è però già quello che M3 userà quando gli
array verranno compattati.

I legami sono memorizzati come dizionario `{ (indice_a, indice_b): energia }` con
`indice_a < indice_b`; l'energia del legame è energia sottratta alle particelle e
immagazzinata nel legame, non dispersa (sistema chiuso).
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Iterable, Sequence

if TYPE_CHECKING:
    from .config import Config
    from .rng import RNG


class InvariantError(RuntimeError):
    """Violazione di un invariante fisico o computazionale."""


EMPTY = -1


class ParticleStore:
    """Particelle, energia e legami, mantenuti coerenti con la griglia."""

    __slots__ = (
        "width",
        "height",
        "ids",
        "xs",
        "ys",
        "species",
        "energy",
        "grid",
        "degree",
        "bonds",
        "_index_of_id",
    )

    def __init__(
        self,
        width: int,
        height: int,
        ids: Sequence[int],
        xs: Sequence[int],
        ys: Sequence[int],
        species: Sequence[int],
        energy: Sequence[int],
        bonds: Iterable[tuple[int, int, int]] = (),
    ) -> None:
        if width < 1 or height < 1:
            raise InvariantError("dimensioni della griglia non valide")
        sizes = {len(ids), len(xs), len(ys), len(species), len(energy)}
        if len(sizes) != 1:
            raise InvariantError("array delle particelle di lunghezze diverse")

        self.width = width
        self.height = height
        self.ids = list(ids)
        self.xs = list(xs)
        self.ys = list(ys)
        self.species = list(species)
        self.energy = list(energy)
        self.grid = [EMPTY] * (width * height)
        self.degree = [0] * len(self.ids)
        self.bonds = {}
        self._index_of_id = {}

        for index, identifier in enumerate(self.ids):
            if identifier < 0:
                raise InvariantError(f"identificativo negativo: {identifier}")
            if identifier in self._index_of_id:
                raise InvariantError(f"identificativo duplicato: {identifier}")
            self._index_of_id[identifier] = index

        for index, (x, y) in enumerate(zip(self.xs, self.ys)):
            if self.energy[index] < 0:
                raise InvariantError(f"energia negativa per la particella {self.ids[index]}")
            if not (0 <= x < width and 0 <= y < height):
                raise InvariantError(
                    f"particella {self.ids[index]} fuori griglia: ({x}, {y})"
                )
            cell = y * width + x
            if self.grid[cell] != EMPTY:
                raise InvariantError(
                    f"doppia occupazione della cella ({x}, {y}) "
                    f"da parte delle particelle {self.grid[cell]} e {index}"
                )
            self.grid[cell] = index

        for identifier_a, identifier_b, bond_energy in bonds:
            self._insert_bond(identifier_a, identifier_b, bond_energy)

    # -- costruzione -----------------------------------------------------
    @classmethod
    def place_random(cls, config: "Config", rng: "RNG") -> "ParticleStore":
        """Collocazione uniforme senza sostituzione, riproducibile.

        Una sola estrazione RNG per particella piazzata; gli identificativi sono
        assegnati in ordine crescente e mai riutilizzati.
        """
        width = config.grid.width
        height = config.grid.height
        cells = width * height
        total = sum(species.count for species in config.species)
        if total > cells:
            raise InvariantError("piu' particelle che celle")

        free = list(range(cells))
        ids: list[int] = []
        xs: list[int] = []
        ys: list[int] = []
        species: list[int] = []
        energy: list[int] = []
        next_id = 0
        for species_index, species_config in enumerate(config.species):
            for _ in range(species_config.count):
                pick = rng.raw() % len(free)
                cell = free[pick]
                free[pick] = free[-1]
                free.pop()
                y, x = divmod(cell, width)
                ids.append(next_id)
                next_id += 1
                xs.append(x)
                ys.append(y)
                species.append(species_index)
                energy.append(species_config.energy)
        return cls(width, height, ids, xs, ys, species, energy)

    # -- interrogazione --------------------------------------------------
    def __len__(self) -> int:
        return len(self.ids)

    def index_of(self, identifier: int) -> int:
        return self._index_of_id[identifier]

    def counts(self, species_names: Sequence[str]) -> dict[str, int]:
        counts = [0] * len(species_names)
        for species_index in self.species:
            counts[species_index] += 1
        return {name: counts[index] for index, name in enumerate(species_names)}

    def records(self) -> list[list[int]]:
        """Rappresentazione materiale (compatibile M1): [[x, y, specie], ...]."""
        return [
            [x, y, species_index]
            for x, y, species_index in zip(self.xs, self.ys, self.species)
        ]

    def full_records(self) -> list[list[int]]:
        """Rappresentazione completa: [[id, x, y, specie, energia], ...]."""
        return [
            [identifier, x, y, species_index, energy]
            for identifier, x, y, species_index, energy in zip(
                self.ids, self.xs, self.ys, self.species, self.energy
            )
        ]

    def bond_records(self) -> list[list[int]]:
        pairs = []
        for (index_a, index_b), bond_energy in self.bonds.items():
            pairs.append([self.ids[index_a], self.ids[index_b], bond_energy])
        pairs.sort(key=lambda entry: (entry[0], entry[1]))
        return pairs

    def state_hash(self, species_names: Sequence[str], boundary: str) -> str:
        """Hash materiale: posizioni e specie. Definizione invariata da M1."""
        payload = {
            "schema": 1,
            "width": self.width,
            "height": self.height,
            "boundary": boundary,
            "species": list(species_names),
            "particles": self.records(),
        }
        return _hash(payload)

    def state_hash_full(
        self,
        species_names: Sequence[str],
        boundary: str,
        schema: int = 2,
        extras: dict | None = None,
    ) -> str:
        """Hash completo: identità, energia e legami (e, dallo schema 3, i flussi)."""
        payload = {
            "schema": schema,
            "width": self.width,
            "height": self.height,
            "boundary": boundary,
            "species": list(species_names),
            "particles": self.full_records(),
            "bonds": self.bond_records(),
        }
        if extras:
            payload.update(extras)
        return _hash(payload)

    def occupied_cells(self) -> int:
        return sum(1 for cell in self.grid if cell != EMPTY)

    def position_of(self, index: int) -> tuple[int, int]:
        return self.xs[index], self.ys[index]

    # -- legami ----------------------------------------------------------
    def _bond_key(self, index_a: int, index_b: int) -> tuple[int, int]:
        return (index_a, index_b) if index_a < index_b else (index_b, index_a)

    def _insert_bond(self, identifier_a: int, identifier_b: int, bond_energy: int) -> None:
        if identifier_a == identifier_b:
            raise InvariantError(f"legame di una particella con se stessa: {identifier_a}")
        if bond_energy < 0:
            raise InvariantError(f"energia del legame negativa: {bond_energy}")
        try:
            index_a = self._index_of_id[identifier_a]
            index_b = self._index_of_id[identifier_b]
        except KeyError as exc:
            raise InvariantError(f"legame con particella inesistente: {exc}") from exc
        key = self._bond_key(index_a, index_b)
        if key in self.bonds:
            raise InvariantError(
                f"legame duplicato fra {self.ids[key[0]]} e {self.ids[key[1]]}"
            )
        self.bonds[key] = bond_energy
        self.degree[index_a] += 1
        self.degree[index_b] += 1

    def add_bond(self, index_a: int, index_b: int, bond_energy: int) -> None:
        self._insert_bond(self.ids[index_a], self.ids[index_b], bond_energy)

    def remove_bond(self, index_a: int, index_b: int) -> int:
        key = self._bond_key(index_a, index_b)
        bond_energy = self.bonds.pop(key)
        self.degree[key[0]] -= 1
        self.degree[key[1]] -= 1
        return bond_energy


def _hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
