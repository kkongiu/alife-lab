"""Separate M8.1b physical law: finite-energy hop of isolated monomers ONLY.

Inherits exactly the original M8.0 capture/B/H/bath physics unchanged.
A *new* locally stochastic transport step for unbound monomers is inserted
between native bond breaking and native adsorption. No global offspring,
no genome-reading, no special handling of initial source material IDs.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256

from alife_m8.sandbox import WIDTH, HEIGHT, WorldM8

HOP_LAW_VERSION = "M8.1b-local-isolated-monomer-hop-v1"
P_HOP_ATTEMPT = 0.25
HOP_COST = 1
DIRECTIONS = ((0, -1), (0, 1), (-1, 0), (1, 0))


class WorldM81b(WorldM8):
    """Native M8.0 simulator with exactly one added isolated-monomer hop law."""

    def __init__(self, *, seed: int, mode: str, template_sequence=None,
                 initial_free_energy: int = 500, bath_each_species: int = 40):
        super().__init__(seed=seed, mode=mode, template_sequence=template_sequence,
                         initial_free_energy=initial_free_energy,
                         bath_each_species=bath_each_species)

    def _isolated_local_hops(self) -> None:
        # Sorted persistent IDs: every monomer gets at most one independent
        # chance per tick, even if a previous monomer enters its former site.
        for ident in sorted(tuple(self.particles)):
            p = self.particles[ident]
            if self.backbone_neighbors(ident) or self.weak_neighbors(ident):
                continue
            if self.free_energy < HOP_COST:
                continue
            if self.roll("m8.1b-isolated-hop-attempt", p.x, p.y, ident) >= P_HOP_ATTEMPT:
                continue
            choice = self.roll("m8.1b-cardinal-direction", p.x, p.y, ident)
            dx, dy = DIRECTIONS[min(int(choice * 4), 3)]
            xnew, ynew = p.x + dx, p.y + dy
            if not (0 <= xnew < WIDTH and 0 <= ynew < HEIGHT):
                continue
            if (xnew, ynew) in self.grid:
                continue
            assert self.grid[(p.x, p.y)] == ident
            assert not self.backbone_neighbors(ident) and not self.weak_neighbors(ident)
            del self.grid[(p.x, p.y)]
            self.grid[(xnew, ynew)] = ident
            self.particles[ident] = replace(p, x=xnew, y=ynew)
            self.free_energy -= HOP_COST
            self.dissipated += HOP_COST
            self.events.append({
                "tick": self.tick, "kind": "hop",
                "material_id": ident, "species": p.species,
                "from_x": p.x, "from_y": p.y,
                "to_x": xnew, "to_y": ynew, "energy_cost": HOP_COST,
            })

    def step(self) -> None:
        self.tick += 1
        # Original M8.0 stages, in original relative order; one isolated hop
        # phase is added as specified in the immutable M8.1b protocol.
        self._break_existing_contacts()
        self._isolated_local_hops()
        self._capture_from_finite_bath()
        self._form_horizontal_backbones()
        self.check()

    def full_hash(self) -> str:
        # Avoid a different physical law masquerading as the M8.0 hash.
        return sha256((HOP_LAW_VERSION + "|" + super().full_hash()).encode()).hexdigest()
