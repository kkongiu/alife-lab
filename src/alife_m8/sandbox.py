"""Explicit NEW local physical rules, unrelated to unchanged native M6/M7.

A stationary anisotropic 2D chemical lattice:
* two monomer species represented by persistent material IDs;
* horizontal backbone B (max-degree=2, weak spontaneous break);
* vertical matching contact H (max-degree=2, stochastic release);
* monomers adsorb stochastically from a finite bath, with NO command to
  construct a daughter or to copy a source sequence;
* a local H partner's actual species can affect adsorption kinetics;
* H alignment across an existing B bond can boost NEW B formation;
* energy for capture and bonds is paid and all sinks tracked exactly.

Fixtures may have an EXPLICITLY artificial 4-unit parent polymer. Passing
those fixtures is microphysics calibration, NOT spontaneous origin/life.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b, sha256
import json

LAW_VERSION = "M8.0-local-B-H-sandbox-v1"
MONOMER_SPECIES = (0, 1)
MODES = ("templated", "shuffled_identity", "no_template", "unpowered")

WIDTH = 10
HEIGHT = 5
P_CAPTURE = 0.55
P_MATCH = 0.90
P_BACKGROUND = 0.00
P_B_BASE = 0.03
P_B_CATALYZED = 0.90
P_H_RELEASE = 0.035
P_B_BREAK = 0.0005
H_COST = 2
B_COST = 2


@dataclass(frozen=True, slots=True)
class Monomer:
    id: int
    species: int
    x: int
    y: int
    birth_tick: int


class WorldM8:
    """Finite material/energy reaction lattice with state-free keyed RNG.

    Every random value is keyed to seed/tick/law/site, not event order, so
    matched source edits use the identical underlying microscopic lottery.
    """

    def __init__(
        self,
        seed: int,
        mode: str = "templated",
        template_sequence: str | None = "0101",
        initial_free_energy: int = 500,
        bath_each_species: int = 40,
    ) -> None:
        if mode not in MODES:
            raise ValueError(f"unknown physical experimental mode: {mode}")
        if initial_free_energy < 0 or bath_each_species < 0:
            raise ValueError("negative initial energy or material reservoir")
        if template_sequence is not None and (
            len(template_sequence) != 4 or any(c not in "01" for c in template_sequence)
        ):
            raise ValueError("laboratory sequence must contain four 0/1 monomers")
        self.seed = int(seed)
        self.mode = mode
        self.tick = 0
        self.grid: dict[tuple[int, int], int] = {}
        self.particles: dict[int, Monomer] = {}
        self.next_id = 0
        self.B: dict[tuple[int, int], int] = {}
        self.H: dict[tuple[int, int], int] = {}
        self.bath = {0: int(bath_each_species), 1: int(bath_each_species)}
        self.free_energy = int(initial_free_energy)
        self.dissipated = 0
        self.events: list[dict] = []
        self.initial_template_material_ids: tuple[int, ...] = ()
        if template_sequence is not None:
            # EXPLICIT lab-made positive-control fixture. Never call this when
            # claiming an unbiased world without an initially constructed chain.
            ids = tuple(self._place(3 + i, 1, int(symbol)) for i, symbol in enumerate(template_sequence))
            for a, b in zip(ids, ids[1:]):
                self.B[self._key(a, b)] = 1
            self.initial_template_material_ids = ids
        self.initial_matter = len(self.particles) + sum(self.bath.values())
        self.initial_energy = self.free_energy + sum(self.B.values()) + sum(self.H.values())
        self.check()

    @staticmethod
    def _key(a: int, b: int) -> tuple[int, int]:
        return (a, b) if a < b else (b, a)

    def roll(self, label: str, x: int, y: int, lane: int = 0) -> float:
        data = f"{LAW_VERSION}|{self.seed}|{self.tick}|{label}|{x}|{y}|{lane}".encode()
        n = int.from_bytes(blake2b(data, digest_size=8).digest(), "little")
        return n / (1 << 64)

    def _place(self, x: int, y: int, species: int) -> int:
        assert (x, y) not in self.grid
        assert species in MONOMER_SPECIES
        identifier = self.next_id
        self.next_id += 1
        self.particles[identifier] = Monomer(identifier, species, x, y, self.tick)
        self.grid[(x, y)] = identifier
        return identifier

    def backbone_neighbors(self, material_id: int) -> list[int]:
        return [b if a == material_id else a
                for a, b in self.B if material_id in (a, b)]

    def weak_neighbors(self, material_id: int) -> list[int]:
        return [b if a == material_id else a
                for a, b in self.H if material_id in (a, b)]

    def _vertical_template(self, x: int, y: int) -> int | None:
        if self.mode == "no_template":
            return None
        choices = []
        for step in (-1, 1):
            source_id = self.grid.get((x, y + step))
            if source_id is None:
                continue
            if self.backbone_neighbors(source_id) and len(self.weak_neighbors(source_id)) < 2:
                choices.append(source_id)
        return min(choices) if choices else None

    def _pseudo_identity(self, x: int, y: int) -> int:
        # Fixed coordinate-specific reference independent of source genotype
        # and tick; a physically matched but informationally scrambled arm.
        raw = blake2b(f"{LAW_VERSION}|pseudo|{self.seed}|{x}|{y}".encode(), digest_size=8).digest()
        return int.from_bytes(raw, "little") & 1

    def _break_existing_contacts(self) -> None:
        for pair in sorted(tuple(self.H)):
            if pair not in self.H:
                continue
            a, b = pair
            # Per-pair keyed draws are source edit stable while the bond exists.
            if self.roll("H-release", a, b) < P_H_RELEASE:
                del self.H[pair]
                self.dissipated += 1
                self.events.append({"tick": self.tick, "kind": "H_release", "pair": [a, b]})
        for pair in sorted(tuple(self.B)):
            if pair not in self.B:
                continue
            a, b = pair
            if self.roll("B-break", a, b) < P_B_BREAK:
                self.free_energy += self.B.pop(pair)
                self.events.append({"tick": self.tick, "kind": "B_break", "pair": [a, b]})

    def _capture_from_finite_bath(self) -> None:
        # Original particles or newly adsorbed backbone polymers both can act
        # as templates; NO parent-ID special casing occurs in this physics.
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (x, y) in self.grid:
                    continue
                source = self._vertical_template(x, y)
                adsorb_probability = P_CAPTURE if source is not None else P_BACKGROUND
                if self.roll("capture", x, y) >= adsorb_probability:
                    continue
                budget = H_COST if source is not None else 1
                if self.free_energy < budget:
                    continue
                choice = self.roll("species", x, y)
                if source is None:
                    species = int(choice >= 0.5)
                else:
                    preferred = (self.particles[source].species if self.mode == "templated"
                                 else self._pseudo_identity(x, y))
                    species = preferred if choice < P_MATCH else 1 - preferred
                if self.bath[species] <= 0:
                    continue
                self.bath[species] -= 1
                self.free_energy -= budget
                self.dissipated += 1
                new_id = self._place(x, y, species)
                if source is not None:
                    assert len(self.weak_neighbors(new_id)) == 0
                    self.H[self._key(new_id, source)] = 1
                self.events.append({
                    "tick": self.tick, "kind": "adsorb",
                    "new_material_id": new_id, "x": x, "y": y,
                    "species": species, "source_material_id": source,
                    "source_species": None if source is None else self.particles[source].species,
                    "chance": adsorb_probability,
                    "same_keyed_species_lottery": choice
                })

    def _has_aligned_H_backbone(self, left_id: int, right_id: int) -> bool:
        for left_partner in self.weak_neighbors(left_id):
            for right_partner in self.weak_neighbors(right_id):
                if self._key(left_partner, right_partner) in self.B:
                    return True
        return False

    def _form_horizontal_backbones(self) -> None:
        for y in range(HEIGHT):
            for x in range(WIDTH - 1):
                a = self.grid.get((x, y))
                b = self.grid.get((x + 1, y))
                if a is None or b is None:
                    continue
                key = self._key(a, b)
                if key in self.B:
                    continue
                if len(self.backbone_neighbors(a)) >= 2 or len(self.backbone_neighbors(b)) >= 2:
                    continue
                is_aligned = self._has_aligned_H_backbone(a, b)
                chance = P_B_CATALYZED if is_aligned else P_B_BASE
                if self.free_energy < B_COST or self.roll("B-formation", x, y) >= chance:
                    continue
                self.free_energy -= B_COST
                self.dissipated += 1
                self.B[key] = 1
                self.events.append({
                    "tick": self.tick, "kind": "B_form",
                    "pair": list(key), "x": x, "y": y,
                    "aligned_H_pair": is_aligned, "probability": chance
                })

    def step(self) -> None:
        self.tick += 1
        self._break_existing_contacts()
        self._capture_from_finite_bath()
        self._form_horizontal_backbones()
        self.check()

    def check(self) -> None:
        assert self.free_energy >= 0 and self.dissipated >= 0
        assert set(self.bath) == {0, 1}
        assert all(v >= 0 for v in self.bath.values())
        assert len(self.particles) + sum(self.bath.values()) == self.initial_matter
        assert self.free_energy + sum(self.B.values()) + sum(self.H.values()) + self.dissipated == self.initial_energy
        assert len(self.grid) == len(self.particles)
        assert len({p.id for p in self.particles.values()}) == len(self.particles)
        assert all(self.particles[ident].x == x and self.particles[ident].y == y
                   for (x, y), ident in self.grid.items())
        assert all(0 <= x < WIDTH and 0 <= y < HEIGHT for x, y in self.grid)
        assert all(p.id == i and p.species in MONOMER_SPECIES for i, p in self.particles.items())
        assert all(len(self.backbone_neighbors(i)) <= 2 and len(self.weak_neighbors(i)) <= 2
                   for i in self.particles)
        for kind, bonds in (("B", self.B), ("H", self.H)):
            for (a, b), units in bonds.items():
                assert a != b and a in self.particles and b in self.particles and units == 1
                pa, pb = self.particles[a], self.particles[b]
                if kind == "B":
                    assert pa.y == pb.y and abs(pa.x - pb.x) == 1
                else:
                    assert pa.x == pb.x and abs(pa.y - pb.y) == 1
        assert set(self.B).isdisjoint(self.H)

    def full_hash(self) -> str:
        state = {
            "law": LAW_VERSION, "seed": self.seed, "mode": self.mode,
            "tick": self.tick, "materials": sorted(
                (p.id, p.species, p.x, p.y, p.birth_tick) for p in self.particles.values()),
            "B": sorted(self.B), "H": sorted(self.H), "bath": self.bath,
            "free_energy": self.free_energy, "dissipated": self.dissipated,
            "initial_matter": self.initial_matter, "initial_energy": self.initial_energy,
            "next_id": self.next_id
        }
        return sha256(json.dumps(state,sort_keys=True,separators=(",",":")).encode()).hexdigest()

    def physical_metrics(self) -> dict:
        return {
            "n_particles": len(self.particles),
            "bath_remaining": dict(self.bath),
            "B_backbones": len(self.B),
            "H_contacts": len(self.H),
            "available_energy": self.free_energy,
            "bond_stored_energy": sum(self.B.values())+sum(self.H.values()),
            "dissipated_energy": self.dissipated,
            "exact_mass_and_energy_invariants": True,
            "full_hash": self.full_hash()
        }
