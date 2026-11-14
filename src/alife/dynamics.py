"""Dinamica locale: proposta di movimento e risoluzione esplicita dei conflitti.

Schema (dettagli in SPEC.md §4):

1. PROPOSTA — ogni particella, in ordine canonico di indice, consuma esattamente
   due uint64 dal generatore: il primo decide se si muove, il secondo sceglie una
   delle quattro direzioni. Se la specia non si muove, la direzione viene comunque
   estratta: il flusso RNG e' cosi' esattamente 2*N per passo.
2. RISOLUZIONE — le proposte sono accettate in ordine di priorita' decrescente
   (hash deterministico di indice e passo, nessun consumo RNG). Una mossa e'
   accettata se la cella bersaglio e' vuota o sara' liberata da una mossa gia'
   accettata, e se nessun'altra mossa accettata punta alla stessa cella.
3. CICLI — le rotazioni chiuse (scambi e cicli piu' lunghi) non hanno una cella
   vuota da cui partire: vengono rilevate e accettate come gruppo.
4. APPLICAZIONE — simultanea su una copia della griglia: prima si svuotano tutte
   le celle di partenza, poi si scrivono tutte le destinazioni.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World

MASK64 = (1 << 64) - 1
TWO64 = 1 << 64
VON_NEUMANN = ((0, -1), (1, 0), (0, 1), (-1, 0))


def _mix64(value: int) -> int:
    value &= MASK64
    value ^= value >> 30
    value = (value * 0xBF58476D1CE4E5B9) & MASK64
    value ^= value >> 27
    value = (value * 0x94D049BB133111EB) & MASK64
    value ^= value >> 31
    return value


def particle_priority(index: int, step: int) -> int:
    """Priorita' deterministica per la risoluzione dei conflitti.

    Dipende solo da (indice, passo): nessuna estrazione RNG, nessuna dipendenza
    dall'ordine di scansione della griglia.
    """
    mixed = ((index + 1) * 0x9E3779B97F4A7C15) & MASK64
    mixed ^= ((step + 1) * 0xD6E8FEB86659FD93) & MASK64
    return _mix64(mixed)


def _propose_moves(world: "World") -> dict[int, int]:
    """Ritorna {indice_particella: cella_bersaglio} per le particelle che si muovono."""
    store = world.store
    width = store.width
    height = store.height
    periodic = world.periodic
    thresholds = world.move_thresholds
    raw = world.rng.raw
    xs = store.xs
    ys = store.ys
    sp = store.species
    proposals: dict[int, int] = {}

    for index in range(len(xs)):
        roll = raw()
        direction = raw() & 3
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
    proposals: dict[int, int], grid: list[int], step: int
) -> dict[int, int]:
    """Risolve le contese di movimento e ritorna {particella: cella} accettate.

    Proprieta' garantite:
    - le destinazioni accettate sono tutte distinte (nessuna collisione);
    - il risultato dipende solo da (proposte, griglia, passo), non dall'ordine
      con cui le proposte sono state inserite;
    - nessuna particella resta senza cella o finisce fuori griglia.
    """
    if not proposals:
        return {}

    order = sorted(
        proposals,
        key=lambda index: (-particle_priority(index, step), index),
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


def step(world: "World") -> int:
    """Avanza l'universo di un passo. Ritorna il numero di spostamenti."""
    proposals = _propose_moves(world)
    accepted = resolve_moves(proposals, world.store.grid, world.step)
    apply_moves(world.store, accepted)
    return len(accepted)
