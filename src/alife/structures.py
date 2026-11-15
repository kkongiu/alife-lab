"""Osservabilità: strutture connesse, firme canoniche e tracciamento nel tempo.

Una "struttura" è una componente connessa di particelle unite da legami, di
dimensione ≥ 2. Il modulo non introduce nessuna nozione di organismo, genoma o
sequenza: descrive forma e composizione, e dichiara esplicitamente quando la
descrizione non è sufficiente a distinguere due strutture.

Due livelli di firma:

- **esatta** per gli alberi (numero di legami = particelle − 1): codice
  canonico radicato calcolato su tutte le radici (AHU). Due alberi hanno lo
  stesso codice se e solo se sono isomorfi.
- **impronta** per i grafi con cicli: raffinamento di Weisfeiler-Lehman. È veloce
  e invariante, ma non completo: due grafi non isomorfi possono condividerla.
  In quel caso la firma è marcata `exact = False` e la collisione viene
  contata come ambiguità, non nascosta.

Il tracciamento usa l'**identità delle particelle**, non la firma: una struttura
continua se condivide particelle con una sola struttura precedente. La firma
serve a descrivere e a confrontare, non a stabilire discendenze.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .particles import ParticleStore
    from .world import World

SIGNATURE_EXAMPLE_LIMIT = 3
LIFETIME_BUCKETS = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000)


@dataclass(frozen=True, slots=True)
class Signature:
    """Descrizione canonica di una struttura connessa."""

    key: str
    size: int
    bonds: int
    composition: tuple[tuple[str, int], ...]
    exact: bool


@dataclass
class TrackedStructure:
    structure_id: int
    lineage_id: int
    born_step: int
    last_step: int
    size: int
    max_size: int
    signature: Signature
    particles: frozenset[int]
    parents: tuple[int, ...] = ()


def components(
    store: "ParticleStore",
) -> list[tuple[tuple[int, ...], tuple[tuple[int, int], ...]]]:
    """Componenti connesse dai legami, in ordine canonico di identificativo."""
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

    groups: dict[int, list[int]] = defaultdict(list)
    for index in range(count):
        if store.degree[index] > 0:
            groups[find(index)].append(index)

    sorted_bonds = sorted(store.bonds)
    bond_lists: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for index_a, index_b in sorted_bonds:
        bond_lists[find(index_a)].append((index_a, index_b))

    result: list[tuple[tuple[int, ...], tuple[tuple[int, int], ...]]] = []
    for root, indices in groups.items():
        if len(indices) < 2:
            continue
        indices.sort()
        result.append((tuple(indices), tuple(bond_lists[root])))
    result.sort(key=lambda entry: entry[0][0])
    return result


def signature(
    store: "ParticleStore",
    indices: tuple[int, ...],
    bonds: tuple[tuple[int, int], ...],
    species_names: list[str],
) -> Signature:
    """Firma della struttura: esatta per gli alberi, impronta per i cicli."""
    adjacency: dict[int, list[int]] = {index: [] for index in indices}
    for index_a, index_b in bonds:
        adjacency[index_a].append(index_b)
        adjacency[index_b].append(index_a)
    for neighbours in adjacency.values():
        neighbours.sort()

    composition = tuple(
        sorted(Counter(species_names[store.species[index]] for index in indices).items())
    )
    size = len(indices)
    bond_count = len(bonds)

    if bond_count == size - 1:
        code = min(
            _rooted_code(root, -1, adjacency, store, species_names) for root in indices
        )
        return Signature("T:" + code, size, bond_count, composition, True)

    digest = _wl_fingerprint(store, indices, adjacency, bonds, composition, species_names)
    return Signature("F:" + digest, size, bond_count, composition, False)


def _rooted_code(
    node: int,
    parent: int,
    adjacency: dict[int, list[int]],
    store: "ParticleStore",
    species_names: list[str],
) -> str:
    children = sorted(
        _rooted_code(neighbour, node, adjacency, store, species_names)
        for neighbour in adjacency[node]
        if neighbour != parent
    )
    return "(" + species_names[store.species[node]] + ":" + ",".join(children) + ")"


def _wl_fingerprint(
    store: "ParticleStore",
    indices: tuple[int, ...],
    adjacency: dict[int, list[int]],
    bonds: tuple[tuple[int, int], ...],
    composition: tuple[tuple[str, int], ...],
    species_names: list[str],
) -> str:
    colors: dict[int, tuple] = {
        index: (species_names[store.species[index]],) for index in indices
    }
    for _ in range(len(indices)):
        signatures = {
            index: (colors[index], tuple(sorted(colors[neighbour] for neighbour in adjacency[index])))
            for index in indices
        }
        unique = sorted(set(signatures.values()))
        rank = {value: position for position, value in enumerate(unique)}
        colors = {index: (rank[signatures[index]],) for index in indices}

    histogram = sorted(Counter(colors[index] for index in indices).items())
    payload = {
        "size": len(indices),
        "bonds": len(bonds),
        "composition": composition,
        "colors": histogram,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class Tracker:
    """Osservatore che registra strutture, eventi e persistenza.

    Non consuma estrazioni casuali e non modifica il mondo: è un livello di
    analisi, non una regola della simulazione.
    """

    def __init__(self, out_dir: str | Path | None = None) -> None:
        self.out_dir = Path(out_dir) if out_dir is not None else None
        self._structures_stream = None
        self._lineage_stream = None
        if self.out_dir is not None:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            self._structures_stream = (self.out_dir / "structures.jsonl").open(
                "w", encoding="utf-8"
            )
            self._lineage_stream = (self.out_dir / "lineage.jsonl").open("w", encoding="utf-8")

        self.active: dict[int, TrackedStructure] = {}
        self.next_structure_id = 0
        self.next_lineage_id = 0
        self.steps_tracked = 0
        self.last_step = 0
        self.events: Counter = Counter()
        self.completed_lifetimes: list[int] = []
        self.max_lifetime = 0
        self.seen_keys: set[str] = set()
        self.exact_signatures = 0
        self.fuzzy_signatures = 0
        self.ambiguous_steps = 0
        self.ambiguous_structures = 0
        self.examples: dict[str, list[dict]] = defaultdict(list)
        self.last_births: list[TrackedStructure] = []

    # -- osservazione ----------------------------------------------------
    def observe(self, world: "World") -> None:
        step = world.step
        store = world.store
        species_names = world.species_names

        current: list[tuple[Signature, frozenset[int], int]] = []
        for indices, bonds in components(store):
            current.append(
                (
                    signature(store, indices, bonds, species_names),
                    frozenset(store.ids[index] for index in indices),
                    len(indices),
                )
            )

        previous_by_particle: dict[int, int] = {}
        for structure_id, tracked in self.active.items():
            for identifier in tracked.particles:
                previous_by_particle[identifier] = structure_id

        parents_of: list[set[int]] = []
        for _, particles, _ in current:
            parents_of.append(
                {
                    previous_by_particle[identifier]
                    for identifier in particles
                    if identifier in previous_by_particle
                }
            )
        children_of: dict[int, list[int]] = defaultdict(list)
        for position, parents in enumerate(parents_of):
            for structure_id in parents:
                children_of[structure_id].append(position)

        new_active: dict[int, TrackedStructure] = {}
        consumed: set[int] = set()
        step_events: Counter = Counter()
        self.last_births = []

        for position, (sig, particles, size) in enumerate(current):
            parents = sorted(parents_of[position])
            consumed.update(parents)
            self._observe_signature(sig)

            if not parents:
                tracked = self._new_structure(sig, particles, size, step, ())
                step_events["birth"] += 1
                self.last_births.append(tracked)
                self._record("birth", step, tracked)
            elif len(parents) == 1 and len(children_of[parents[0]]) == 1:
                parent = self.active[parents[0]]
                tracked = TrackedStructure(
                    structure_id=parent.structure_id,
                    lineage_id=parent.lineage_id,
                    born_step=parent.born_step,
                    last_step=step,
                    size=size,
                    max_size=max(parent.max_size, size),
                    signature=sig,
                    particles=particles,
                    parents=parent.parents,
                )
                if size > parent.size:
                    step_events["growth"] += 1
                    self._record("growth", step, tracked)
                elif size < parent.size:
                    step_events["shrink"] += 1
                    self._record("shrink", step, tracked)
                elif sig.key != parent.signature.key:
                    step_events["transform"] += 1
                    self._record("transform", step, tracked)
                else:
                    step_events["persist"] += 1
            elif len(parents) >= 2:
                parent_states = [self.active[structure_id] for structure_id in parents]
                tracked = self._new_structure(
                    sig,
                    particles,
                    size,
                    step,
                    tuple(state.lineage_id for state in parent_states),
                )
                step_events["merge"] += 1
                self._record("merge", step, tracked)
            else:
                # split: una struttura precedente ha più figli
                parent_id = parents[0]
                siblings = children_of[parent_id]
                largest = max(siblings, key=lambda pos: (current[pos][2], -pos))
                inherits = position == largest
                tracked = self._new_structure(
                    sig,
                    particles,
                    size,
                    step,
                    (self.active[parent_id].lineage_id,),
                    reuse_lineage=self.active[parent_id].lineage_id if inherits else None,
                )
                step_events["split"] += 1
                self._record("split", step, tracked)

            new_active[tracked.structure_id] = tracked

        for structure_id, tracked in self.active.items():
            if structure_id in new_active:
                continue
            lifetime = tracked.last_step - tracked.born_step + 1
            self.completed_lifetimes.append(lifetime)
            self.max_lifetime = max(self.max_lifetime, lifetime)
            if structure_id not in consumed:
                step_events["death"] += 1
                self._record("death", step, tracked)
            # se è stato consumato da split/merge, l'identità termina qui ma
            # l'evento non è una morte: la struttura è continuata nei figli

        self.active = new_active
        self.steps_tracked += 1
        self.last_step = step
        self.events.update(step_events)

        key_counts: Counter = Counter()
        key_exact: dict[str, bool] = {}
        for sig, _, _ in current:
            key_counts[sig.key] += 1
            key_exact[sig.key] = sig.exact
        collisions = sum(count for count in key_counts.values() if count > 1)
        ambiguous_keys = [
            key for key, count in key_counts.items() if count > 1 and not key_exact[key]
        ]
        ambiguous_here = sum(key_counts[key] for key in ambiguous_keys)
        if ambiguous_here:
            self.ambiguous_steps += 1
            self.ambiguous_structures += ambiguous_here

        record = {
            "step": step,
            "structures": len(current),
            "bonded_particles": sum(size for _, _, size in current),
            "births": step_events["birth"],
            "deaths": step_events["death"],
            "splits": step_events["split"],
            "merges": step_events["merge"],
            "growths": step_events["growth"],
            "shrinks": step_events["shrink"],
            "transforms": step_events["transform"],
            "distinct_signatures": len(key_counts),
            "signature_collisions": collisions,
            "ambiguous_structures": ambiguous_here,
            "largest": max((size for _, _, size in current), default=0),
            "signatures_sha": hashlib.sha256(
                "|".join(sorted(key_counts)).encode("utf-8")
            ).hexdigest()[:16],
        }
        if self._structures_stream is not None:
            self._structures_stream.write(json.dumps(record, ensure_ascii=True) + "\n")
            self._structures_stream.flush()

    def _observe_signature(self, sig: Signature) -> None:
        self.seen_keys.add(sig.key)
        if sig.exact:
            self.exact_signatures += 1
        else:
            self.fuzzy_signatures += 1

    def _new_structure(
        self,
        sig: Signature,
        particles: frozenset[int],
        size: int,
        step: int,
        parents: tuple[int, ...],
        reuse_lineage: int | None = None,
    ) -> TrackedStructure:
        structure_id = self.next_structure_id
        self.next_structure_id += 1
        if reuse_lineage is None:
            lineage_id = self.next_lineage_id
            self.next_lineage_id += 1
        else:
            lineage_id = reuse_lineage
        return TrackedStructure(
            structure_id=structure_id,
            lineage_id=lineage_id,
            born_step=step,
            last_step=step,
            size=size,
            max_size=size,
            signature=sig,
            particles=particles,
            parents=parents,
        )

    def _record(
        self,
        kind: str,
        step: int,
        tracked: TrackedStructure,
    ) -> None:
        payload = {
            "kind": kind,
            "step": step,
            "structure": tracked.structure_id,
            "lineage": tracked.lineage_id,
            "parents": list(tracked.parents),
            "size": tracked.size,
            "exact": tracked.signature.exact,
            "signature": tracked.signature.key[:160],
        }
        if self._lineage_stream is not None:
            self._lineage_stream.write(json.dumps(payload, ensure_ascii=True) + "\n")
            self._lineage_stream.flush()
        if len(self.examples[kind]) < SIGNATURE_EXAMPLE_LIMIT:
            self.examples[kind].append(payload)

    # -- riepilogo -------------------------------------------------------
    def summary(self) -> dict:
        lifetimes = list(self.completed_lifetimes)
        active_lifetimes = [
            tracked.last_step - tracked.born_step + 1 for tracked in self.active.values()
        ]
        all_lifetimes = lifetimes + active_lifetimes
        histogram: Counter = Counter()
        for lifetime in lifetimes:
            histogram[_bucket(lifetime)] += 1
        sizes = Counter(tracked.size for tracked in self.active.values())
        return {
            "steps_tracked": self.steps_tracked,
            "last_step": self.last_step,
            "active_structures": len(self.active),
            "lineages": self.next_lineage_id,
            "events": dict(sorted(self.events.items())),
            "lifetime": {
                "completed": len(lifetimes),
                "mean": round(sum(all_lifetimes) / len(all_lifetimes), 3)
                if all_lifetimes
                else 0.0,
                "max": max(all_lifetimes) if all_lifetimes else 0,
                "histogram": {str(bucket): count for bucket, count in sorted(histogram.items())},
            },
            "signatures": {
                "distinct": len(self.seen_keys),
                "exact_observations": self.exact_signatures,
                "fuzzy_observations": self.fuzzy_signatures,
                "ambiguous_steps": self.ambiguous_steps,
                "ambiguous_structures": self.ambiguous_structures,
            },
            "size_distribution": {str(size): count for size, count in sorted(sizes.items())},
            "examples": {kind: entries for kind, entries in sorted(self.examples.items())},
        }

    def close(self) -> None:
        if self._structures_stream is not None:
            self._structures_stream.close()
            self._structures_stream = None
        if self._lineage_stream is not None:
            self._lineage_stream.close()
            self._lineage_stream = None


def _bucket(lifetime: int) -> int:
    for bound in LIFETIME_BUCKETS:
        if lifetime <= bound:
            return bound
    return LIFETIME_BUCKETS[-1]
