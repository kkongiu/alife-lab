"""Rilevatore v2.1: copie progressive con controllo continuo della firma (audit M6.2-E).

Il rilevatore v2 originale (`alife.replication_v2`) rimane congelato per
riprodurre la campagna preregistrata M6.2-E. Questa versione verifica la
persistenza continua della firma e applica il limite di finestra prima del
matching, senza modificare il motore fisico.

Il rilevatore v1 (`alife.replication`) riconosce solo strutture che nascono già
complete accanto a una struttura simile: è cieco a un replicatore che si
assembla per accrezione. Il v2 estende il criterio senza modificare v1, che resta
la versione usata dalle campagne M5 e M6.

Criterio preregistrato del v2:

1. una struttura nasce (di qualsiasi dimensione) entro `radius` celle da un
   template con firma **esatta** e dimensione ≥ `min_size`; il template deve
   essere nato in un passo precedente;
2. entro `window` passi la struttura raggiunge **la stessa firma del template**,
   mentre il template è ancora attivo;
3. la copia persiste almeno `persist_steps` passi dopo il raggiungimento;
4. un run è `replication` se ci sono almeno `min_copies` copie persistenti e una
   catena di generazioni costruita solo con copie persistenti.

Differenza rispetto a v1: il requisito non è "nasce completa", ma "raggiunge la
forma del template". Il caso v1 (nascita già completa) resta incluso.

Limite dichiarato: il criterio misura l'acquisizione di una forma vicino a un
template, non dimostra che il template l'abbia causata. La prossimità è una
condizione necessaria, non una prova di causalità.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .replication import _distance

if TYPE_CHECKING:
    from .structures import Tracker
    from .world import World

DETECTOR_VERSION = "v2.1"


@dataclass(slots=True)
class ProgressiveCandidate:
    birth_step: int
    child: int
    template: int
    target_key: str
    target_size: int
    distance: int
    ambiguous_templates: bool = False
    matched_step: int | None = None
    persistent: bool | None = None
    discarded: str | None = None


class ProgressiveDetector:
    """Osserva nascite, crescita e raggiungimento della firma del template."""

    def __init__(
        self,
        radius: int = 2,
        window: int = 150,
        persist_steps: int = 10,
        min_size: int = 4,
        min_copies: int = 5,
        min_generation: int = 2,
    ) -> None:
        self.version = DETECTOR_VERSION
        self.radius = radius
        self.window = window
        self.persist_steps = persist_steps
        self.min_size = min_size
        self.min_copies = min_copies
        self.min_generation = min_generation
        self.candidates: list[ProgressiveCandidate] = []
        self.pending: dict[int, ProgressiveCandidate] = {}
        self.by_child: dict[int, ProgressiveCandidate] = {}
        self.persistence: list[tuple[int, ProgressiveCandidate]] = []
        self.ambiguous_births = 0

    def observe(self, world: "World", tracker: "Tracker") -> None:
        step = world.step
        active = tracker.active

        still_pending: list[tuple[int, ProgressiveCandidate]] = []
        for due, candidate in self.persistence:
            tracked = active.get(candidate.child)
            # "Persistent" means the *copied form* survives continuously, not
            # merely that some structure keeps the same tracker identity.
            if tracked is None:
                candidate.persistent = False
                candidate.discarded = "dead_after_match"
            elif not tracked.signature.exact or tracked.signature.key != candidate.target_key:
                candidate.persistent = False
                candidate.discarded = "signature_changed_after_match"
            elif step >= due:
                candidate.persistent = True
            else:
                still_pending.append((due, candidate))
        self.persistence = still_pending

        for child_id in list(self.pending):
            candidate = self.pending[child_id]
            tracked = active.get(child_id)
            if tracked is None:
                candidate.discarded = "dead_before_match"
                del self.pending[child_id]
                continue
            if candidate.template not in active:
                candidate.discarded = "template_dead"
                del self.pending[child_id]
                continue
            # Apply the preregistered limit BEFORE testing for a match.
            if step - candidate.birth_step > self.window:
                candidate.discarded = "window_expired"
                del self.pending[child_id]
                continue
            if tracked.signature.exact and tracked.signature.key == candidate.target_key:
                candidate.matched_step = step
                del self.pending[child_id]
                self.persistence.append((step + self.persist_steps, candidate))

        templates = [
            tracked
            for tracked in active.values()
            if tracked.signature.exact and tracked.signature.size >= self.min_size
        ]
        for birth in tracker.last_births:
            options: list[tuple[int, int, object]] = []
            for template in templates:
                if template.structure_id == birth.structure_id:
                    continue
                if template.born_step >= step:
                    continue
                distance = _distance(
                    world.store, template.particles, birth.particles, world.periodic
                )
                if distance <= self.radius:
                    options.append((distance, template.structure_id, template))
            if not options:
                continue
            options.sort(key=lambda entry: (entry[0], entry[1]))
            distance, _, template = options[0]
            ambiguous = sum(1 for entry_distance, _, _ in options if entry_distance == distance) > 1
            candidate = ProgressiveCandidate(
                birth_step=step,
                child=birth.structure_id,
                template=template.structure_id,
                target_key=template.signature.key,
                target_size=template.signature.size,
                distance=distance,
                ambiguous_templates=ambiguous,
            )
            self.candidates.append(candidate)
            self.by_child[birth.structure_id] = candidate
            if ambiguous:
                self.ambiguous_births += 1
            if birth.signature.exact and birth.signature.key == candidate.target_key:
                candidate.matched_step = step
                self.persistence.append((step + self.persist_steps, candidate))
            else:
                self.pending[birth.structure_id] = candidate

    def _persistent_generation(self, candidate: ProgressiveCandidate) -> int:
        chain = 0
        current = candidate
        while True:
            template = self.by_child.get(current.template)
            if template is None:
                return chain + 1
            if not template.persistent:
                return 0
            chain += 1
            current = template

    def summary(self) -> dict:
        matched = [candidate for candidate in self.candidates if candidate.matched_step is not None]
        persistent = [candidate for candidate in matched if candidate.persistent]
        unresolved = [
            candidate for candidate in matched if candidate.persistent is None
        ]
        discarded = Counter(
            candidate.discarded for candidate in self.candidates if candidate.discarded
        )
        generations = Counter(
            generation
            for generation in (self._persistent_generation(candidate) for candidate in persistent)
            if generation > 0
        )
        max_generation = max(generations, default=0)
        classified = (
            len(persistent) >= self.min_copies and max_generation >= self.min_generation
        )
        return {
            "version": self.version,
            "criteria": {
                "radius": self.radius,
                "window": self.window,
                "persist_steps": self.persist_steps,
                "min_size": self.min_size,
                "min_copies": self.min_copies,
                "min_generation": self.min_generation,
            },
            "candidates": len(self.candidates),
            "matched": len(matched),
            "persistent": len(persistent),
            "unresolved": len(unresolved),
            "discarded": dict(sorted(discarded.items())),
            "ambiguous_births": self.ambiguous_births,
            "max_generation": max_generation,
            "generations": {str(gen): count for gen, count in sorted(generations.items())},
            "classified": "replication" if classified else "not_replication",
            "examples": [
                {
                    "birth_step": candidate.birth_step,
                    "child": candidate.child,
                    "template": candidate.template,
                    "target_size": candidate.target_size,
                    "matched_step": candidate.matched_step,
                    "persistent": candidate.persistent,
                    "distance": candidate.distance,
                }
                for candidate in self.candidates[:5]
            ],
        }
