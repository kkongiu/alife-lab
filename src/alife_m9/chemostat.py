"""M9.0: a minimal open-flow, well-mixed count-based molecular reaction engine.

Chemistry is deliberately a toy: four oriented dimer products, reversible
synthesis/hydrolysis, feed/washout, and a configurable catalyst-per-reaction
map. No hardcoded reproduction, daughter, organism, fitness or genome.

Molecular bonds are stored energy tokens (one per dimer), with an exact
open-system mass/energy ledger checked at EVERY tick. This is not a
thermodynamically realistic chemistry model.
"""
from __future__ import annotations

from collections import Counter
from hashlib import blake2b, sha256
import json

LAW = "M9.0-nonspatial-open-chemostat-v1"
MONOMERS = ("A", "B")
DIMERS = ("AA", "AB", "BA", "BB")
SPECIES = MONOMERS + DIMERS
MODES = ("on", "off", "switch_off")

FEED_EACH_MONOMER = 3
ENERGY_FEED = 8
ENERGY_POOL_CAP = 64
P_WASHOUT = 0.04
P_HYDROLYSIS = 0.03
P_LIGATION_BACKGROUND = 0.004
P_LIGATION_CATALYZED = 0.65
SWITCH_OFF_AFTER = 150


def catalyst_map(network_id: int | str) -> dict[str, str | None]:
    """Declared prior to trials; fixed independent hash per reaction rule."""
    if network_id == "positive":
        return {"AA": "AA", "AB": None, "BA": None, "BB": None}
    if not isinstance(network_id, int) or not 0 <= network_id < 12:
        raise ValueError("M9.0 network IDs must be integers 0..11")
    choices = (*DIMERS, None)
    result = {}
    for product in DIMERS:
        payload = f"{LAW}|chemistry-map-v1|{network_id}|{product}".encode()
        n = int.from_bytes(blake2b(payload, digest_size=8).digest(), "little")
        result[product] = choices[n % len(choices)]
    return result


def directed_cycle(catalysts: dict[str, str | None]) -> bool:
    """Structural feedback in the RULES, not evidence that it was realized."""
    edges = {s: [] for s in DIMERS}
    for product, catalyst in catalysts.items():
        if catalyst is not None:
            edges[catalyst].append(product)
    active = set()
    visited = set()

    def explore(node: str) -> bool:
        if node in active:
            return True
        if node in visited:
            return False
        active.add(node)
        for nxt in edges[node]:
            if explore(nxt):
                return True
        active.remove(node)
        visited.add(node)
        return False

    return any(explore(n) for n in DIMERS if n not in visited)


class Chemostat:
    def __init__(self, seed: int, catalysts: dict[str, str | None],
                 mode: str, seeded_positive: bool = False):
        if mode not in MODES:
            raise ValueError(f"unknown M9.0 mode {mode!r}")
        if set(catalysts) != set(DIMERS) or any(
            c is not None and c not in DIMERS for c in catalysts.values()
        ):
            raise ValueError("invalid dimer catalyst map")
        self.seed = int(seed)
        self.mode = mode
        self.catalysts = dict(catalysts)
        self.tick = 0
        self.counts = {s: 0 for s in SPECIES}
        if seeded_positive:
            self.counts["AA"] = 1  # EXPLICIT lab fixture, never spontaneous
        self.initial_matter = self.internal_atoms()
        self.initial_energy = self.bond_energy()
        self.total_atoms_fed = 0
        self.total_atoms_exported = 0
        self.total_energy_fed = 0
        self.total_bond_energy_exported = 0
        self.free_energy = 0
        self.dissipated_energy = 0
        self.events: list[dict] = []
        self.check()

    def internal_atoms(self) -> int:
        return sum(len(s) * count for s, count in self.counts.items())

    def bond_energy(self) -> int:
        return sum(self.counts[s] for s in DIMERS)

    def catalytic_channel_enabled(self) -> bool:
        return self.mode == "on" or (
            self.mode == "switch_off" and self.tick <= SWITCH_OFF_AFTER
        )

    def roll(self, stage: str, molecule: str, index: int = 0) -> float:
        data = f"{LAW}|{self.seed}|{self.tick}|{stage}|{molecule}|{index}".encode()
        return int.from_bytes(blake2b(data, digest_size=8).digest(), "little") / (1 << 64)

    def _feed(self) -> None:
        for monomer in MONOMERS:
            self.counts[monomer] += FEED_EACH_MONOMER
        self.total_atoms_fed += len(MONOMERS) * FEED_EACH_MONOMER
        self.free_energy += ENERGY_FEED
        self.total_energy_fed += ENERGY_FEED
        self.events.append({
            "tick": self.tick, "kind": "feed",
            "A": FEED_EACH_MONOMER, "B": FEED_EACH_MONOMER,
            "free_energy_in": ENERGY_FEED
        })

    def _washout(self) -> None:
        for s in SPECIES:
            available = self.counts[s]
            removed = sum(
                self.roll("washout", s, i) < P_WASHOUT
                for i in range(available)
            )
            if not removed:
                continue
            self.counts[s] -= removed
            self.total_atoms_exported += len(s) * removed
            if s in DIMERS:
                self.total_bond_energy_exported += removed
            self.events.append({
                "tick": self.tick, "kind": "washout",
                "species": s, "molecules": removed,
                "atoms_out": len(s) * removed,
                "bond_energy_out": (removed if s in DIMERS else 0),
            })

    def _hydrolysis(self) -> None:
        for s in DIMERS:
            available = self.counts[s]
            broken = sum(
                self.roll("hydrolysis", s, i) < P_HYDROLYSIS
                for i in range(available)
            )
            if not broken:
                continue
            self.counts[s] -= broken
            for monomer in s:
                self.counts[monomer] += broken
            self.free_energy += broken
            self.events.append({
                "tick": self.tick, "kind": "hydrolysis",
                "dimer": s, "molecules": broken,
                "bond_energy_released": broken
            })

    def _ligations(self) -> None:
        for product in DIMERS:
            a, b = tuple(product)
            if self.counts[a] <= 0 or self.counts[b] <= 0:
                continue
            if a == b and self.counts[a] < 2:
                continue
            if self.free_energy < 1:
                continue
            catalyst = self.catalysts[product]
            active = (
                self.catalytic_channel_enabled()
                and catalyst is not None
                and self.counts[catalyst] > 0
            )
            chance = (
                P_LIGATION_CATALYZED if active
                else P_LIGATION_BACKGROUND
            )
            if self.roll("ligation", product) >= chance:
                continue
            self.counts[a] -= 1
            self.counts[b] -= 1
            self.counts[product] += 1
            self.free_energy -= 1  # stored in the newly created dimer bond
            self.events.append({
                "tick": self.tick, "kind": "ligation",
                "product": product, "reactants": [a, b],
                "catalyst": catalyst if active else None,
                "catalytic_channel_used": active,
                "energy_to_bond": 1
            })

    def _drain_excess_energy(self) -> None:
        if self.free_energy <= ENERGY_POOL_CAP:
            return
        amount = self.free_energy - ENERGY_POOL_CAP
        self.free_energy -= amount
        self.dissipated_energy += amount
        self.events.append({
            "tick": self.tick, "kind": "energy_leak",
            "dissipated": amount
        })

    def step(self) -> dict:
        self.tick += 1
        self._feed()
        self._washout()
        self._hydrolysis()
        self._ligations()
        self._drain_excess_energy()
        self.check()
        return self.snapshot()

    def snapshot(self) -> dict:
        return {
            "tick": self.tick,
            "counts": dict(self.counts),
            "dimer_count": sum(self.counts[s] for s in DIMERS),
            "atoms_inside": self.internal_atoms(),
            "atoms_fed": self.total_atoms_fed,
            "atoms_out": self.total_atoms_exported,
            "energy_pool": self.free_energy,
            "energy_bonds_inside": self.bond_energy(),
            "energy_bonds_out": self.total_bond_energy_exported,
            "energy_fed": self.total_energy_fed,
            "energy_dissipated": self.dissipated_energy,
        }

    def check(self) -> None:
        assert set(self.counts) == set(SPECIES)
        assert all(type(n) is int and n >= 0 for n in self.counts.values())
        assert self.free_energy >= 0 and self.dissipated_energy >= 0
        assert self.internal_atoms() + self.total_atoms_exported == (
            self.initial_matter + self.total_atoms_fed
        )
        assert (self.free_energy + self.bond_energy()
                + self.total_bond_energy_exported + self.dissipated_energy) == (
                    self.initial_energy + self.total_energy_fed
                )

    def full_hash(self) -> str:
        state = {
            "law": LAW, "seed": self.seed, "mode": self.mode,
            "catalysts": self.catalysts, "snapshot": self.snapshot()
        }
        return sha256(json.dumps(state, sort_keys=True,
                                 separators=(",", ":")).encode()).hexdigest()
