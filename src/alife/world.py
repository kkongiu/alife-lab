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
        "energy_config",
        "movement_cost",
        "formation_dissipation",
        "breaking_dissipation",
        "formation_cost",
        "particle_decay",
        "bond_decay",
        "sources",
        "source_acc",
        "source_store",
        "injected",
        "dissipated",
        "unabsorbed",
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
        injected: int = 0,
        dissipated: int = 0,
        unabsorbed: int = 0,
        source_acc: list[int] | None = None,
        source_store: list[int] | None = None,
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

        energy_config = config.energy
        self.energy_config = energy_config
        self.movement_cost = energy_config.movement_cost
        self.formation_dissipation = energy_config.formation_dissipation
        self.breaking_dissipation = energy_config.breaking_dissipation
        self.formation_cost = chemistry.bond_cost + self.formation_dissipation
        self.particle_decay = energy_config.particle_decay
        self.bond_decay = energy_config.bond_decay
        self.sources = energy_config.sources
        self.source_acc = (
            list(source_acc) if source_acc is not None else [0] * len(self.sources)
        )
        self.source_store = (
            list(source_store) if source_store is not None else [0] * len(self.sources)
        )
        if len(self.source_acc) != len(self.sources):
            raise InvariantError(
                f"accumulatori delle sorgenti: {len(self.source_acc)} per "
                f"{len(self.sources)} sorgenti"
            )
        if len(self.source_store) != len(self.sources):
            raise InvariantError(
                f"serbatoi delle sorgenti: {len(self.source_store)} per "
                f"{len(self.sources)} sorgenti"
            )
        self.injected = injected
        self.dissipated = dissipated
        self.unabsorbed = unabsorbed

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
        """Esegue ``steps`` passi; dopo ogni passo invoca ``observer(self)``.

        Ordine fissato: dissipazione → iniezione → rottura → movimento →
        risoluzione → formazione. Cambiarlo è un cambio di schema.
        """
        if steps < 0:
            raise ValueError("steps non può essere negativo")
        for _ in range(steps):
            self.dissipate()
            self.inject()
            report = advance_one_step(self)
            self.moves_total += report.moves
            self.step += 1
            if observer is not None:
                observer(self)

    # -- flussi energetici -----------------------------------------------
    def dissipate(self) -> None:
        """Decadimento deterministico: `num` quanti ogni `den` passi, sfasati per ID.

        Ogni particella perde **un** quanto nei passi in cui
        `(step + id) mod den < num`; ogni legame nei passi in cui
        `(step + id_a + id_b) mod den < num`. Non serve stato aggiuntivo, non si
        consumano estrazioni, e il decadimento non dipende dal livello di energia
        (a differenza di un tasso proporzionale, che a basse energie si annulla
        per arrotondamento intero).
        """
        store = self.store
        decay = self.particle_decay
        if decay.num:
            num = decay.num
            den = decay.den
            step = self.step
            for index in range(len(store.energy)):
                if (step + index) % den < num and store.energy[index] > 0:
                    store.energy[index] -= 1
                    self.dissipated += 1
        decay = self.bond_decay
        if decay.num and store.bonds:
            num = decay.num
            den = decay.den
            step = self.step
            for (index_a, index_b) in sorted(store.bonds):
                if store.bonds[(index_a, index_b)] > 0 and (
                    (step + store.ids[index_a] + store.ids[index_b]) % den < num
                ):
                    store.bonds[(index_a, index_b)] -= 1
                    self.dissipated += 1

    def inject(self) -> None:
        """Iniezione localizzata con serbatoio e accumulatori interi.

        Ogni sorgente accumula l'energia emessa in un serbatoio locale (capacità
        `capacity`); la particella presente sulla cella assorbe l'intero
        serbatoio. Il trabocco del serbatoio va in `unabsorbed`: una sorgente non
        crea energia e non la trattiene oltre la propria capacità.
        """
        if not self.sources:
            return
        store = self.store
        width = store.width
        for index, source in enumerate(self.sources):
            accumulated = self.source_acc[index] + source.rate_num
            emitted, accumulated = divmod(accumulated, source.rate_den)
            self.source_acc[index] = accumulated
            if emitted <= 0:
                continue
            self.injected += emitted
            buffer = self.source_store[index] + emitted
            if buffer > source.capacity:
                self.unabsorbed += buffer - source.capacity
                buffer = source.capacity
            particle = store.grid[source.y * width + source.x]
            if particle == EMPTY:
                self.source_store[index] = buffer
                continue
            store.energy[particle] += buffer
            self.source_store[index] = 0

    # -- energia ---------------------------------------------------------
    def energy_particles(self) -> int:
        return sum(self.store.energy)

    def energy_bonds(self) -> int:
        return sum(self.store.bonds.values())

    def energy_sources(self) -> int:
        """Energia immagazzinata nei serbatoi delle sorgenti: è ancora interna."""
        return sum(self.source_store)

    def energy(self) -> int:
        return self.energy_particles() + self.energy_bonds() + self.energy_sources()

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
        """Hash completo: identità, energia, legami e stato dei flussi (schema 3)."""
        schema = 2
        extras = None
        if self.config.schema_version >= 3:
            schema = 3
            extras = {
                "injected": self.injected,
                "dissipated": self.dissipated,
                "unabsorbed": self.unabsorbed,
                "source_acc": list(self.source_acc),
                "source_store": list(self.source_store),
            }
        return self.store.state_hash_full(
            self.species_names, self.config.grid.boundary, schema=schema, extras=extras
        )

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
            "injected": self.injected,
            "dissipated": self.dissipated,
            "unabsorbed": self.unabsorbed,
            "source_acc": list(self.source_acc),
            "source_store": list(self.source_store),
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
            expected_energy = self.accounted_energy()
            actual_energy = self.energy()
            if actual_energy != expected_energy:
                problems.append(
                    f"energia {actual_energy} diversa da {expected_energy} "
                    f"(iniziale {self.configured_energy()}, iniettata {self.injected}, "
                    f"dissipata {self.dissipated}, non assorbita {self.unabsorbed})"
                )

        if self.injected < 0 or self.dissipated < 0 or self.unabsorbed < 0:
            problems.append("ledger energetico con valori negativi")
        if len(self.source_acc) != len(self.sources):
            problems.append(
                f"accumulatori {len(self.source_acc)} per {len(self.sources)} sorgenti"
            )
        else:
            for index, (acc, source) in enumerate(zip(self.source_acc, self.sources)):
                if not 0 <= acc < source.rate_den:
                    problems.append(
                        f"sorgente {index}: accumulatore {acc} fuori da [0, {source.rate_den})"
                    )
        if len(self.source_store) != len(self.sources):
            problems.append(
                f"serbatoi {len(self.source_store)} per {len(self.sources)} sorgenti"
            )
        else:
            for index, (stored, source) in enumerate(zip(self.source_store, self.sources)):
                if not 0 <= stored <= source.capacity:
                    problems.append(
                        f"sorgente {index}: serbatoio {stored} fuori da [0, {source.capacity}]"
                    )

        return problems

    def accounted_energy(self) -> int:
        """Energia attesa secondo il ledger: iniziale + iniettata − dissipata − non assorbita."""
        return (
            self.configured_energy()
            + self.injected
            - self.dissipated
            - self.unabsorbed
        )

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
