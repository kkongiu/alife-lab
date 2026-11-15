"""Rilevatore di copie strutturali per i controlli di M5.

Criterio **preregistrato** (fissato prima di guardare i risultati):

1. la struttura nasce in un passo in cui esiste almeno un'altra struttura con
   la **stessa firma esatta** entro `radius` celle (distanza di Manhattan,
   toroidale se il bordo è periodico);
2. la firma è esatta e la struttura ha almeno `min_size` particelle (le
   strutture di 2–3 particelle sono indistinguibili da un'associazione casuale a
   queste densità);
3. la copia deve persistere almeno `persist_steps` passi;
4. un run è classificato `replication` solo se ci sono almeno `min_copies`
   copie persistenti **e** almeno una catena di seconda generazione (una copia
   nata vicino a una copia, non solo al template originale).

Il criterio non usa la firma per stabilire la discendenza: quella viene
dall'identità delle particelle (tracker M4). La firma serve a confrontare, la
prossimità a distinguere una copia locale da una ricorrenza lontana.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .particles import ParticleStore
    from .structures import Tracker
    from .world import World

MAX_DISTANCE = 10**9


@dataclass(slots=True)
class CopyCandidate:
    step: int
    signature: str
    child: int
    parent: int
    generation: int
    distance: int
    persistent: bool | None = None


class ReplicationDetector:
    """Osservatore che conta copie candidate e verifica la persistenza."""

    def __init__(
        self,
        radius: int = 2,
        persist_steps: int = 10,
        min_size: int = 4,
        min_copies: int = 5,
        min_generation: int = 2,
    ) -> None:
        self.radius = radius
        self.persist_steps = persist_steps
        self.min_size = min_size
        self.min_copies = min_copies
        self.min_generation = min_generation
        self.candidates: list[CopyCandidate] = []
        self.pending: list[tuple[int, CopyCandidate]] = []
        self.generation: dict[int, int] = {}

    def observe(self, world: "World", tracker: "Tracker") -> None:
        step = world.step

        still_pending: list[tuple[int, CopyCandidate]] = []
        for due, candidate in self.pending:
            if step >= due:
                candidate.persistent = candidate.child in tracker.active
            else:
                still_pending.append((due, candidate))
        self.pending = still_pending

        active_by_key: dict[str, list] = {}
        for tracked in tracker.active.values():
            if tracked.signature.exact:
                active_by_key.setdefault(tracked.signature.key, []).append(tracked)

        for birth in tracker.last_births:
            sig = birth.signature
            if not sig.exact or sig.size < self.min_size:
                continue
            parents = [
                tracked
                for tracked in active_by_key.get(sig.key, [])
                if tracked.structure_id != birth.structure_id
            ]
            if not parents:
                continue
            best_distance = MAX_DISTANCE
            best_parent = None
            for parent in parents:
                distance = _distance(
                    world.store, parent.particles, birth.particles, world.periodic
                )
                if distance < best_distance or (
                    distance == best_distance
                    and best_parent is not None
                    and parent.structure_id < best_parent.structure_id
                ):
                    best_distance = distance
                    best_parent = parent
            if best_parent is None or best_distance > self.radius:
                continue
            generation = self.generation.get(best_parent.structure_id, 0) + 1
            self.generation[birth.structure_id] = generation
            candidate = CopyCandidate(
                step=step,
                signature=sig.key,
                child=birth.structure_id,
                parent=best_parent.structure_id,
                generation=generation,
                distance=best_distance,
            )
            self.candidates.append(candidate)
            self.pending.append((step + self.persist_steps, candidate))

    def summary(self) -> dict:
        persistent = [candidate for candidate in self.candidates if candidate.persistent]
        unresolved = [candidate for candidate in self.candidates if candidate.persistent is None]
        generations = Counter(candidate.generation for candidate in self.candidates)
        max_generation = max(generations, default=0)
        classified = (
            len(persistent) >= self.min_copies and max_generation >= self.min_generation
        )
        return {
            "criteria": {
                "radius": self.radius,
                "persist_steps": self.persist_steps,
                "min_size": self.min_size,
                "min_copies": self.min_copies,
                "min_generation": self.min_generation,
            },
            "candidates": len(self.candidates),
            "persistent": len(persistent),
            "unresolved": len(unresolved),
            "max_generation": max_generation,
            "generations": {str(gen): count for gen, count in sorted(generations.items())},
            "classified": "replication" if classified else "not_replication",
            "examples": [
                {
                    "step": candidate.step,
                    "generation": candidate.generation,
                    "child": candidate.child,
                    "parent": candidate.parent,
                    "distance": candidate.distance,
                    "persistent": candidate.persistent,
                }
                for candidate in self.candidates[:5]
            ],
        }


def _distance(
    store: "ParticleStore",
    particles_a: Iterable[int],
    particles_b: Iterable[int],
    periodic: bool,
) -> int:
    best = MAX_DISTANCE
    width = store.width
    height = store.height
    for identifier_a in particles_a:
        index_a = store.index_of(identifier_a)
        x_a = store.xs[index_a]
        y_a = store.ys[index_a]
        for identifier_b in particles_b:
            index_b = store.index_of(identifier_b)
            dx = abs(x_a - store.xs[index_b])
            dy = abs(y_a - store.ys[index_b])
            if periodic:
                dx = min(dx, width - dx)
                dy = min(dy, height - dy)
            distance = dx + dy
            if distance < best:
                best = distance
    return best
