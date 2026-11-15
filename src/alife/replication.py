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
   copie persistenti **e** una catena di generazioni costruita **solo con copie
   persistenti**: una seconda generazione transitoria non conta.

Il genitore deve esistere **prima** del passo in cui la copia compare: due
strutture identiche nate nello stesso passo non possono essere l'una il genitore
dell'altra.

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
        self.by_child: dict[int, CopyCandidate] = {}

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
            if not tracked.signature.exact:
                continue
            # un genitore deve esistere PRIMA del passo della presunta copia:
            # due strutture nate insieme non possono essere l'una il genitore
            # dell'altra
            if tracked.born_step >= step:
                continue
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
            self.by_child[birth.structure_id] = candidate
            self.pending.append((step + self.persist_steps, candidate))

    def _persistent_generation(self, candidate: CopyCandidate) -> int:
        """Lunghezza della catena di copie persistenti fino al genitore originale.

        0 significa che il genitore era una copia non persistente: la catena è
        interrotta e questa copia non appartiene a una discendenza persistente.
        """
        chain = 0
        current = candidate
        while True:
            parent = self.by_child.get(current.parent)
            if parent is None:
                return chain + 1  # il genitore è una struttura originale
            if not parent.persistent:
                return 0
            chain += 1
            current = parent


    # -- persistenza dello stato -----------------------------------------
    def to_dict(self) -> dict:
        index_of = {id(candidate): position for position, candidate in enumerate(self.candidates)}
        return {
            "radius": self.radius,
            "persist_steps": self.persist_steps,
            "min_size": self.min_size,
            "min_copies": self.min_copies,
            "min_generation": self.min_generation,
            "candidates": [
                {
                    "step": candidate.step,
                    "signature": candidate.signature,
                    "child": candidate.child,
                    "parent": candidate.parent,
                    "generation": candidate.generation,
                    "distance": candidate.distance,
                    "persistent": candidate.persistent,
                }
                for candidate in self.candidates
            ],
            "pending": [
                [due, index_of[id(candidate)]] for due, candidate in self.pending
            ],
            "generation": {str(key): value for key, value in self.generation.items()},
            "by_child": {
                str(key): index_of[id(value)] for key, value in self.by_child.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReplicationDetector":
        detector = cls(
            radius=int(data.get("radius", 2)),
            persist_steps=int(data.get("persist_steps", 10)),
            min_size=int(data.get("min_size", 4)),
            min_copies=int(data.get("min_copies", 5)),
            min_generation=int(data.get("min_generation", 2)),
        )
        detector.candidates = [
            CopyCandidate(
                step=int(entry["step"]),
                signature=str(entry["signature"]),
                child=int(entry["child"]),
                parent=int(entry["parent"]),
                generation=int(entry["generation"]),
                distance=int(entry["distance"]),
                persistent=entry.get("persistent"),
            )
            for entry in data.get("candidates", [])
        ]
        detector.pending = [
            (int(due), detector.candidates[index])
            for due, index in data.get("pending", [])
        ]
        detector.generation = {int(key): int(value) for key, value in data.get("generation", {}).items()}
        detector.by_child = {
            int(key): detector.candidates[index]
            for key, index in data.get("by_child", {}).items()
        }
        return detector

    def summary(self) -> dict:
        persistent = [candidate for candidate in self.candidates if candidate.persistent]
        unresolved = [candidate for candidate in self.candidates if candidate.persistent is None]
        raw_generations = Counter(candidate.generation for candidate in self.candidates)
        persistent_generations = Counter(
            generation
            for generation in (self._persistent_generation(candidate) for candidate in persistent)
            if generation > 0
        )
        max_generation = max(persistent_generations, default=0)
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
            "generations": {
                str(gen): count for gen, count in sorted(persistent_generations.items())
            },
            "max_generation_all": max(raw_generations, default=0),
            "generations_all": {
                str(gen): count for gen, count in sorted(raw_generations.items())
            },
            "classified": "replication" if classified else "not_replication",
            "examples": [
                {
                    "step": candidate.step,
                    "generation": candidate.generation,
                    "persistent_generation": self._persistent_generation(candidate)
                    if candidate.persistent
                    else None,
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
