"""Chimica artificiale: legami reversibili con costo energetico esplicito.

Regole (dettagli in SPEC.md §5):

- un legame può formarsi solo fra due particelle **adiacenti** (von Neumann),
  di specie ammesse dalla tabella `allowed_pairs`, entrambe sotto il proprio
  `max_bonds` e con energia sufficiente a pagare `bond_cost`;
- l'energia pagata non si perde: viene immagazzinata nel legame e restituita
  alle due particelle quando il legame si rompe (sistema chiuso, M2);
- alla rottura, il resto della divisione intera va alla particella con
  identificativo minore (regola deterministica, documentata);
- ogni coppia candidata e ogni legame esistente consumano una estrazione RNG,
  in ordine canonico: il flusso resta riproducibile e verificabile;
- la catalisi è un fattore moltiplicativo sulla probabilità di formazione,
  applicato se una particella di una specie catalizzatrice è adiacente alla
  coppia. Non riconosce sequenze né strutture: dipende solo da specie locali.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterator

from .particles import EMPTY

if TYPE_CHECKING:
    from .world import World

VON_NEUMANN = ((0, -1), (1, 0), (0, 1), (-1, 0))


@dataclass(slots=True)
class BondEvent:
    kind: str
    step: int
    id_a: int
    id_b: int
    energy: int
    catalyzed: bool = False
    dissipated: int = 0


def break_bonds(world: "World") -> list[BondEvent]:
    """Rottura spontanea (decadimento) dei legami esistenti, in ordine canonico."""
    store = world.store
    if not store.bonds:
        return []
    threshold = world.break_threshold
    raw = world.rng.raw
    events: list[BondEvent] = []
    for index_a, index_b in sorted(store.bonds):
        if raw() >= threshold:
            continue
        bond_energy = store.bonds[(index_a, index_b)]
        loss = world.breaking_dissipation
        if loss > bond_energy:
            loss = bond_energy
        returned = bond_energy - loss
        store.remove_bond(index_a, index_b)
        remainder = returned - returned // 2
        store.energy[index_a] += remainder  # l'ID minore riceve il resto
        store.energy[index_b] += returned // 2
        world.dissipated += loss
        event = BondEvent(
            kind="break",
            step=world.step,
            id_a=store.ids[index_a],
            id_b=store.ids[index_b],
            energy=returned,
            dissipated=loss,
        )
        events.append(event)
        world.bonds_broken_total += 1
        world.record_bond_event(event)
    return events


def form_bonds(world: "World") -> list[BondEvent]:
    """Formazione dei legami fra vicini, dopo il movimento."""
    if not world.chemistry_enabled:
        return []
    threshold = world.formation_threshold
    raw = world.rng.raw
    cost = world.formation_cost
    extra = world.formation_dissipation
    max_bonds = world.max_bonds
    store = world.store
    events: list[BondEvent] = []

    for index_a, index_b in _candidate_pairs(world):
        factor = _catalysis_factor(world, index_a, index_b)
        limit = threshold
        if factor > 1.0:
            limit = int(min(1.0, world.chemistry.formation_probability * factor) * (1 << 64))
        if raw() >= limit:
            continue
        # riverifica: una formazione precedente nello stesso passo può aver
        # occupato gli slot o consumato l'energia
        if store.degree[index_a] >= max_bonds[store.species[index_a]]:
            continue
        if store.degree[index_b] >= max_bonds[store.species[index_b]]:
            continue
        if store.energy[index_a] < cost or store.energy[index_b] < cost:
            continue
        if (index_a, index_b) in store.bonds or (index_b, index_a) in store.bonds:
            continue
        store.energy[index_a] -= cost
        store.energy[index_b] -= cost
        store.add_bond(index_a, index_b, 2 * (cost - extra))
        world.dissipated += 2 * extra
        event = BondEvent(
            kind="form",
            step=world.step,
            id_a=store.ids[index_a],
            id_b=store.ids[index_b],
            energy=2 * (cost - extra),
            catalyzed=factor > 1.0,
            dissipated=2 * extra,
        )
        events.append(event)
        world.bonds_formed_total += 1
        world.record_bond_event(event)
    return events


def _candidate_pairs(world: "World") -> Iterator[tuple[int, int]]:
    """Coppie (indice_a < indice_b) che rispettano le condizioni statiche."""
    store = world.store
    max_bonds = world.max_bonds
    allowed = world.allowed_pairs
    cost = world.formation_cost
    width = store.width
    height = store.height
    periodic = world.periodic
    grid = store.grid
    xs = store.xs
    ys = store.ys
    species = store.species
    degree = store.degree
    energy = store.energy

    for index_a in range(len(store)):
        species_a = species[index_a]
        if degree[index_a] >= max_bonds[species_a]:
            continue
        if energy[index_a] < cost:
            continue
        x = xs[index_a]
        y = ys[index_a]
        for dx, dy in VON_NEUMANN:
            if periodic:
                nx = (x + dx) % width
                ny = (y + dy) % height
            else:
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
            index_b = grid[ny * width + nx]
            if index_b == EMPTY or index_b <= index_a:
                continue
            species_b = species[index_b]
            if degree[index_b] >= max_bonds[species_b]:
                continue
            if energy[index_b] < cost:
                continue
            if (species_a, species_b) not in allowed and (species_b, species_a) not in allowed:
                continue
            yield index_a, index_b


def _catalysis_factor(world: "World", index_a: int, index_b: int) -> float:
    """Massimo fattore catalitico fra i vicini della coppia (esclusi gli estremi)."""
    rules = world.catalysis_lookup.get(
        (world.store.species[index_a], world.store.species[index_b])
    )
    if not rules:
        rules = world.catalysis_lookup.get(
            (world.store.species[index_b], world.store.species[index_a])
        )
        if not rules:
            return 1.0
    best = 1.0
    for index in (index_a, index_b):
        for neighbor in _neighbors(world, index):
            if neighbor == index_a or neighbor == index_b:
                continue
            factor = rules.get(world.store.species[neighbor])
            if factor is not None and factor > best:
                best = factor
    return best


def _neighbors(world: "World", index: int) -> Iterator[int]:
    store = world.store
    x = store.xs[index]
    y = store.ys[index]
    for dx, dy in VON_NEUMANN:
        if world.periodic:
            nx = (x + dx) % store.width
            ny = (y + dy) % store.height
        else:
            nx = x + dx
            ny = y + dy
            if nx < 0 or nx >= store.width or ny < 0 or ny >= store.height:
                continue
        occupant = store.grid[ny * store.width + nx]
        if occupant != EMPTY:
            yield occupant


def aggregate_stats(store) -> dict[str, object]:
    """Statistiche sugli aggregati connessi dai legami (componenti di dimensione >= 2)."""
    count = len(store)
    parent = list(range(count))

    def find(node: int) -> int:
        root = node
        while parent[root] != root:
            root = parent[root]
        while parent[node] != root:
            parent[node], node = root, parent[node]
        return root

    for index_a, index_b in store.bonds:
        root_a = find(index_a)
        root_b = find(index_b)
        if root_a != root_b:
            parent[root_b] = root_a

    sizes = Counter(find(index) for index in range(count) if store.degree[index] > 0)
    aggregates = [size for size in sizes.values() if size >= 2]
    return {
        "bonds": len(store.bonds),
        "bond_energy": sum(store.bonds.values()),
        "bonded_particles": sum(1 for value in store.degree if value > 0),
        "aggregates": len(aggregates),
        "largest_aggregate": max(aggregates) if aggregates else 0,
        "mean_aggregate_size": round(sum(aggregates) / len(aggregates), 4) if aggregates else 0.0,
        "free_particles": sum(1 for value in store.degree if value == 0),
        "size_distribution": {str(size): value for size, value in sorted(Counter(aggregates).items())},
    }
