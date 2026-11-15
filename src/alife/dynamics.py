"""Dinamica locale: decadimento, proposta di movimento, conflitti, formazione.

Schema di un passo (dettagli in SPEC.md §4–§5):

1. ROTTURA — ogni legame esistente consuma un'unità RNG e può rompersi; l'energia
   torna alle due particelle.
2. PROPOSTA — ogni particella consuma esattamente due uint64 (decisione e
   direzione). Le particelle legate non si muovono: la loro proposta è nulla, ma
   le estrazioni vengono comunque consumate, così il flusso RNG resta
   esattamente 2·N più le estrazioni della chimica.
3. RISOLUZIONE — priorità deterministica da (indice, passo), accettazione greedy,
   rotazioni chiuse, applicazione simultanea.
4. FORMAZIONE — le coppie adiacenti ammesse consumano un'unità RNG ciascuna e
   possono legarsi pagando il costo energetico.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import chemistry

if TYPE_CHECKING:
    from .world import World

MASK64 = (1 << 64) - 1
VON_NEUMANN = ((0, -1), (1, 0), (0, 1), (-1, 0))


@dataclass(slots=True)
class StepReport:
    moves: int
    bonds_formed: int
    bonds_broken: int


def _mix64(value: int) -> int:
    value &= MASK64
    value ^= value >> 30
    value = (value * 0xBF58476D1CE4E5B9) & MASK64
    value ^= value >> 27
    value = (value * 0x94D049BB133111EB) & MASK64
    value ^= value >> 31
    return value


def particle_priority(identity: int, step: int) -> int:
    """Priorità deterministica per la risoluzione dei conflitti.

    Dipende solo da (identità, passo): nessuna estrazione RNG, nessuna dipendenza
    dall'ordine di scansione della griglia né dalla posizione nell'array.
    """
    mixed = ((identity + 1) * 0x9E3779B97F4A7C15) & MASK64
    mixed ^= ((step + 1) * 0xD6E8FEB86659FD93) & MASK64
    return _mix64(mixed)


def _propose_moves(world: "World") -> dict[int, int]:
    """Ritorna {indice_particella: cella_bersaglio} per le particelle libere."""
    store = world.store
    width = store.width
    height = store.height
    periodic = world.periodic
    thresholds = world.move_thresholds
    movement_cost = world.movement_cost
    raw = world.rng.raw
    xs = store.xs
    ys = store.ys
    sp = store.species
    degree = store.degree
    energy = store.energy
    proposals: dict[int, int] = {}

    for index in range(len(xs)):
        # ordine degli indici = ordine degli ID: l'invariante I17 impone array
        # ordinati per identificativo, quindi il flusso RNG è canonico
        roll = raw()
        direction = raw() & 3
        if degree[index] > 0:
            continue
        if energy[index] < movement_cost:
            continue
        if roll >= thresholds[sp[index]]:
            continue
        dx, dy = VON_NEUMANN[direction]
        if periodic:
            x = (xs[index] + dx) % width
            y = (ys[index] + dy) % height
        else:
            x = xs[index] + dx
            y = ys[index] + dy
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
        proposals[index] = y * width + x
    return proposals


def _find_cycle(
    pending: list[int],
    proposals: dict[int, int],
    grid: list[int],
    accepted: dict[int, int],
) -> list[int] | None:
    """Cerca una rotazione chiusa fra le mosse ancora pendenti."""
    pending_set = set(pending)
    for start in pending:
        seen_at: dict[int, int] = {}
        path: list[int] = []
        current = start
        while True:
            if current in seen_at:
                return path[seen_at[current] :]
            seen_at[current] = len(path)
            path.append(current)
            successor = grid[proposals[current]]
            if successor == -1 or successor in accepted or successor not in pending_set:
                break
            current = successor
    return None


def resolve_moves(
    proposals: dict[int, int],
    grid: list[int],
    step: int,
    identity: list[int] | None = None,
) -> dict[int, int]:
    """Risolve le contese di movimento e ritorna {particella: cella} accettate.

    `identity[i]` è l'identificativo persistente della particella con indice `i`
    (se assente, si usa l'indice: utile nei test e nei mondi in cui coincidono).

    Proprietà garantite:
    - le destinazioni accettate sono tutte distinte (nessuna collisione);
    - il risultato dipende solo da (proposte, griglia, passo, identità), non
      dall'ordine con cui le proposte sono state inserite;
    - nessuna particella resta senza cella o finisce fuori griglia.
    """
    if not proposals:
        return {}

    def priority_of(index: int) -> int:
        return particle_priority(identity[index] if identity is not None else index, step)

    order = sorted(
        proposals,
        key=lambda index: (-priority_of(index), identity[index] if identity is not None else index),
    )
    accepted: dict[int, int] = {}
    reserved: set[int] = set()
    pending = order

    while pending:
        progressed = False
        still_pending: list[int] = []
        for index in pending:
            target = proposals[index]
            if target in reserved:
                still_pending.append(index)
                continue
            occupant = grid[target]
            if occupant == -1 or occupant in accepted:
                accepted[index] = target
                reserved.add(target)
                progressed = True
            else:
                still_pending.append(index)

        if progressed:
            pending = still_pending
            continue

        cycle = _find_cycle(pending, proposals, grid, accepted)
        if cycle is None:
            break
        for index in cycle:
            target = proposals[index]
            accepted[index] = target
            reserved.add(target)
        pending = [index for index in pending if index not in accepted]

    return accepted


def apply_moves(store, accepted: dict[int, int]) -> None:
    """Applica le mosse accettate in modo simultaneo."""
    if not accepted:
        return
    grid = store.grid
    width = store.width
    xs = store.xs
    ys = store.ys

    for index in accepted:
        grid[ys[index] * width + xs[index]] = -1
    for index, cell in accepted.items():
        if grid[cell] != -1:
            raise RuntimeError(f"collisione di movimento sulla cella {cell}")
        grid[cell] = index
        ys[index], xs[index] = divmod(cell, width)


def step(world: "World") -> StepReport:
    """Avanza l'universo di un passo."""
    broken = chemistry.break_bonds(world)
    proposals = _propose_moves(world)
    accepted = resolve_moves(proposals, world.store.grid, world.step, world.store.ids)
    apply_moves(world.store, accepted)
    if accepted:
        cost = world.movement_cost
        if cost:
            for index in sorted(accepted):
                if world.store.energy[index] < cost:
                    raise RuntimeError(
                        f"energia insufficiente per il costo di movimento della particella "
                        f"{world.store.ids[index]}"
                    )
                world.store.energy[index] -= cost
                world.dissipated += cost
    formed = chemistry.form_bonds(world)
    return StepReport(
        moves=len(accepted),
        bonds_formed=len(formed),
        bonds_broken=len(broken),
    )
