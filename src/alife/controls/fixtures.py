"""Fixture isolate per i controlli di M5.

ATTENZIONE: questo modulo contiene l'unico replicatore codificato del progetto.
È un controllo positivo, vive fuori dal motore e dalle regole dell'universo di
scoperta. Non è importato da nessun modulo del motore.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import Config
from ..particles import ParticleStore
from ..rng import RNG
from ..structures import components, signature
from ..world import World

FIXTURE_VERSION = "m5-fixtures-1"

TEMPLATE_SPECIES = (0, 1, 1, 0)  # A-B-B-A
FUEL_SITES = 9
TEMPLATE_START_X = 5
TEMPLATE_Y = 32


def positive_config() -> Config:
    per_site_a = TEMPLATE_SPECIES.count(0)
    per_site_b = TEMPLATE_SPECIES.count(1)
    total_sites = FUEL_SITES + 1  # template + copie possibili
    return Config.from_dict(
        {
            "schema_version": 3,
            "seed": 1,
            "grid": {"width": 64, "height": 64, "boundary": "periodic"},
            "species": [
                {
                    "name": "A",
                    "count": total_sites * per_site_a,
                    "move_probability": 0.0,
                    "energy": 1,
                    "max_bonds": 2,
                },
                {
                    "name": "B",
                    "count": total_sites * per_site_b,
                    "move_probability": 0.0,
                    "energy": 1,
                    "max_bonds": 2,
                },
            ],
            "chemistry": {
                "enabled": True,
                "bond_cost": 0,
                "formation_probability": 0.0,
                "break_probability": 0.0,
                "allowed_pairs": [["A", "A"], ["A", "B"], ["B", "B"]],
                "catalysis": [],
            },
            "energy": {},
            "metrics": {"every": 1},
        }
    ).validate()


def positive_world() -> World:
    """Template A-B-B-A e nove siti di monomeri A-B-B-A allineati a destra."""
    config = positive_config()
    ids: list[int] = []
    xs: list[int] = []
    ys: list[int] = []
    species: list[int] = []
    bonds: list[tuple[int, int, int]] = []

    def add_chain(start_x: int, species_pattern: tuple[int, ...], with_bonds: bool) -> None:
        base = len(ids)
        for offset, species_index in enumerate(species_pattern):
            ids.append(base + offset)
            xs.append(start_x + offset)
            ys.append(TEMPLATE_Y)
            species.append(species_index)
        if with_bonds:
            for offset in range(len(species_pattern) - 1):
                bonds.append((base + offset, base + offset + 1, 0))

    add_chain(TEMPLATE_START_X, TEMPLATE_SPECIES, with_bonds=True)
    for site in range(FUEL_SITES):
        add_chain(TEMPLATE_START_X + 4 * (site + 1), TEMPLATE_SPECIES, with_bonds=False)

    store = ParticleStore(64, 64, ids, xs, ys, species, [1] * len(ids), bonds)
    world = World(config, RNG(config.seed), store)
    world.check()
    return world


@dataclass(slots=True)
class TemplateCopier:
    """Assemblaggio template-diretto: copia una catena A-B-B-A nel sito a destra.

    Regola esplicita, deterministica, senza RNG: cerca una struttura con la
    firma del template, verifica che il sito immediatamente a destra contenga
    quattro monomeri liberi nella sequenza A-B-B-A e li lega in catena.
    """

    target_key: str
    copies: int = 0

    @classmethod
    def for_world(cls, world: World) -> "TemplateCopier":
        structures = components(world.store)
        if not structures:
            raise ValueError("il controllo positivo richiede un template iniziale")
        indices, bonds = structures[0]
        key = signature(world.store, indices, bonds, world.species_names).key
        return cls(target_key=key)

    def step(self, world: World) -> int:
        store = world.store
        made = 0
        for indices, bonds in components(store):
            sig = signature(store, indices, bonds, world.species_names)
            if sig.key != self.target_key:
                continue
            xs = [store.xs[index] for index in indices]
            ys = [store.ys[index] for index in indices]
            if len(set(ys)) != 1:
                continue
            ordered = sorted(indices, key=lambda index: store.xs[index])
            ordered_xs = [store.xs[index] for index in ordered]
            if ordered_xs != list(range(ordered_xs[0], ordered_xs[0] + 4)):
                continue
            if [store.species[index] for index in ordered] != list(TEMPLATE_SPECIES):
                continue
            site_cells = [
                ((ordered_xs[0] + 4 + offset) % store.width, ys[0]) for offset in range(4)
            ]
            site = [store.grid[y * store.width + x] for x, y in site_cells]
            if any(index == -1 for index in site):
                continue
            if any(store.degree[index] > 0 for index in site):
                continue
            if [store.species[index] for index in site] != list(TEMPLATE_SPECIES):
                continue
            for first, second in zip(site, site[1:]):
                store.add_bond(first, second, 0)
            made += 1
            self.copies += 1
        return made


def _negative_config(
    seed: int,
    species_count: int,
    count_per_species: int,
    move_probability: float,
    chemistry: dict | None,
) -> Config:
    names = ["S0", "S1", "S2", "S3"][:species_count]
    return Config.from_dict(
        {
            "schema_version": 3,
            "seed": seed,
            "grid": {"width": 64, "height": 64, "boundary": "periodic"},
            "species": [
                {
                    "name": name,
                    "count": count_per_species,
                    "move_probability": move_probability,
                    "energy": 10,
                    "max_bonds": 2,
                }
                for name in names
            ],
            "chemistry": chemistry or {"enabled": False},
            "energy": {},
            "metrics": {"every": 1},
        }
    ).validate()


def negative_immobile() -> World:
    """N1: particelle immobili, nessuna reazione. Non deve comparire nulla."""
    config = _negative_config(
        seed=11, species_count=1, count_per_species=100, move_probability=0.0, chemistry=None
    )
    return World.create(config)


def negative_random_aggregation() -> World:
    """N2: aggregazione casuale a densità controllata, senza copiatura."""
    chemistry = {
        "enabled": True,
        "bond_cost": 2,
        "formation_probability": 0.3,
        "break_probability": 0.001,
        "allowed_pairs": [
            ["S0", "S0"],
            ["S0", "S1"],
            ["S0", "S2"],
            ["S0", "S3"],
            ["S1", "S1"],
            ["S1", "S2"],
            ["S1", "S3"],
            ["S2", "S2"],
            ["S2", "S3"],
            ["S3", "S3"],
        ],
        "catalysis": [],
    }
    config = _negative_config(
        seed=12, species_count=4, count_per_species=100, move_probability=0.5, chemistry=chemistry
    )
    return World.create(config)


def negative_reversible() -> World:
    """N3: reazioni reversibili senza ereditarietà: strutture effimere."""
    chemistry = {
        "enabled": True,
        "bond_cost": 2,
        "formation_probability": 0.3,
        "break_probability": 0.05,
        "allowed_pairs": [
            ["S0", "S0"],
            ["S0", "S1"],
            ["S0", "S2"],
            ["S1", "S1"],
            ["S1", "S2"],
            ["S2", "S2"],
        ],
        "catalysis": [],
    }
    config = _negative_config(
        seed=13, species_count=3, count_per_species=120, move_probability=0.5, chemistry=chemistry
    )
    return World.create(config)


def negative_single_species(seed: int = 21, count: int = 200) -> World:
    """Stress: aggregazione casuale con una sola specie, firme molto ripetute."""
    chemistry = {
        "enabled": True,
        "bond_cost": 2,
        "formation_probability": 0.3,
        "break_probability": 0.001,
        "allowed_pairs": [["S0", "S0"]],
        "catalysis": [],
    }
    config = _negative_config(
        seed=seed, species_count=1, count_per_species=count, move_probability=0.5, chemistry=chemistry
    )
    return World.create(config)


def negative_burst(seed: int = 31, count: int = 200) -> World:
    """Stress: formazione al massimo tasso, catene assemblate in pochi passi."""
    chemistry = {
        "enabled": True,
        "bond_cost": 1,
        "formation_probability": 1.0,
        "break_probability": 0.001,
        "allowed_pairs": [["S0", "S0"]],
        "catalysis": [],
    }
    config = _negative_config(
        seed=seed, species_count=1, count_per_species=count, move_probability=0.5, chemistry=chemistry
    )
    return World.create(config)
