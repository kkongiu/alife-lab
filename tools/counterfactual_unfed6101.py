"""Exploratory, post-hoc counterfactual for the sole M6.2-E match.

IMPORTANT:
- This does NOT alter the preregistered M6/M6.2-E worlds or their results.
- Teleporting a bonded component is an EXTERNAL intervention, not a new
  physical law. Never use intervened runs as natural ALife observations.
- This single selected event cannot establish reproduction or significance.
- Matching random streams is a coupling, not proof that local trajectories
  stay identical after the first altered chemical interaction.
"""
from __future__ import annotations

import json
from pathlib import Path

from alife.config import load_config
from alife.particles import EMPTY, ParticleStore
from alife.rng import RNG
from alife.structures import Tracker, components, signature
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
M6 = ROOT / "campaigns" / "m6"
OUT = ROOT / "campaigns" / "m6_2e" / "unfed_6101_counterfactual.json"
RUN_ID = "unfed-6101"

# Chosen after the published event was discovered: explicitly exploratory.
INTERVENTION_STEP = 791
BIRTH_STEP = 792
MATCH_STEP = 835
PERSIST_STEP = 845
TEMPLATE_STRUCTURE_ID = 850
CHILD_STRUCTURE_ID = 872
SHIFTS = ((64, 64), (64, 0), (0, 64), (32, 32),
          (96, 32), (32, 96), (48, 80), (80, 48))


def clone_world(world: World) -> World:
    """Clone ALL material, RNG and energy state without touching the source."""
    s = world.store
    store = ParticleStore(
        s.width, s.height, s.ids, s.xs, s.ys, s.species, s.energy,
        s.bond_records(),
    )
    rng = RNG(world.config.seed)
    rng.set_state(world.rng.state())
    rng.draws = world.rng.draws
    result = World(
        world.config, rng, store, step=world.step,
        moves_total=world.moves_total, next_id=world.next_id,
        bonds_formed_total=world.bonds_formed_total,
        bonds_broken_total=world.bonds_broken_total,
        injected=world.injected, dissipated=world.dissipated,
        unabsorbed=world.unabsorbed,
        source_acc=world.source_acc, source_store=world.source_store,
    )
    assert result.state_hash_full() == world.state_hash_full()
    assert result.rng.state() == world.rng.state()
    result.check()
    return result


def relocate(world: World, particle_ids: tuple[int, ...], shift: tuple[int, int]) -> bool:
    """Rigidly teleport one component to empty cells, conserving every particle,
    bond, species and energy value. Return False on any occupancy collision."""
    s = world.store
    indices = tuple(s.index_of(pid) for pid in particle_ids)
    occupied = set(indices)
    width, height = s.width, s.height
    targets = [
        ((s.xs[i] + shift[0]) % width, (s.ys[i] + shift[1]) % height)
        for i in indices
    ]
    if len(set(targets)) != len(targets):
        return False
    if any(
        s.grid[y * width + x] not in occupied and
        s.grid[y * width + x] != EMPTY
        for x, y in targets
    ):
        return False
    for i in indices:
        s.grid[s.ys[i] * width + s.xs[i]] = EMPTY
    for i, (x, y) in zip(indices, targets):
        s.xs[i], s.ys[i] = x, y
        s.grid[y *width + x] = i
    world.check()
    return True


def connected_seed_component(world: World, seed_ids: tuple[int, ...]) -> dict | None:
    """Find the component containing ALL baseline child-birth seed particles."""
    if not seed_ids:
        return None
    store = world.store
    wanted = set(seed_ids)
    for indices, bonds in components(store):
        ids = {store.ids[i] for i in indices}
        if wanted <= ids:
            sig = signature(store, indices, bonds, world.species_names)
            return {
                "size": sig.size,
                "signature": sig.key,
                "exact": sig.exact,
                "particle_ids": sorted(ids),
            }
    return None


def run_arm(snapshot: World, seed_ids: tuple[int, ...],
            target_sig: str, target_ids: tuple[int, ...],
            mode: str, group: tuple[int, ...] | None = None,
            shift: tuple[int, int] | None = None) -> dict:
    world = clone_world(snapshot)
    before_hash = world.state_hash_full()
    if group is not None:
        assert shift is not None and shift != (0, 0)
        if not relocate(world, group, shift):
            return {"mode": mode, "shift": list(shift), "valid": False,
                    "reason": "occupied_destination"}
        assert world.state_hash_full() != before_hash
    record = {"mode": mode, "valid": True, "shift": list(shift) if shift else None,
              "intervention_state_hash": world.state_hash_full(),
              "measurements": {}}
    for step in range(INTERVENTION_STEP + 1, PERSIST_STEP + 1):
        world.advance(1)
        if step in (BIRTH_STEP, MATCH_STEP, PERSIST_STEP):
            component = connected_seed_component(world, seed_ids)
            record["measurements"][str(step)] = {
                "seed_component": component,
                "seed_has_target_signature": bool(component and
                   component["exact"] and component["signature"] == target_sig),
                "same_four_particles_as_baseline": bool(component and
                   tuple(component["particle_ids"]) == target_ids),
            }
    world.check()
    record["final_state_hash"] = world.state_hash_full()
    record["final_rng_fingerprint"] = world.rng.fingerprint()
    return record


def choose_sham(tracker: Tracker, template, world: World):
    """Select before running interventions, never based on their outcomes."""
    store = world.store
    original = tuple(sorted(template.particles))
    # Distinct, same structural signature; choose the smallest structure ID far
    # from the template to avoid directly perturbing the candidate environment.
    origin_coords = [
        (store.xs[store.index_of(pid)], store.ys[store.index_of(pid)])
        for pid in original
    ]

    def far_enough(other):
        w, h = store.width, store.height
        for pid in other.particles:
            i = store.index_of(pid)
            x, y = store.xs[i], store.ys[i]
            for ox, oy in origin_coords:
                dx, dy = abs(x - ox), abs(y - oy)
                if min(dx, w - dx) + min(dy, h - dy) < 20:
                    return False
        return True

    choices = sorted(
        (s for s in tracker.active.values() if
         s.structure_id != template.structure_id and
         s.signature.exact and s.signature.key == template.signature.key
         and far_enough(s)),
        key=lambda s: s.structure_id,
    )
    return choices[0] if choices else None


def main() -> None:
    manifest = json.loads((ROOT / "campaigns" / "m6_2e" / "manifest.json").read_text())
    run = next(x for x in manifest["runs"] if x["id"] == RUN_ID)
    config = load_config(M6 / run["config"])
    assert config.hash() == run["config_hash"]
    assert not config.chemistry.catalysis, "M6 control should have catalysis off"

    world = World.create(config)
    tracker = Tracker()
    tracker.observe(world)
    world.advance(INTERVENTION_STEP, observer=tracker.observe)
    template = tracker.active.get(TEMPLATE_STRUCTURE_ID)
    assert template is not None, "published parent identity not found at intervention step"
    template_ids = tuple(sorted(template.particles))
    sham = choose_sham(tracker, template, world)
    snapshot = clone_world(world)

    child_birth = None
    child_at_match = None
    child_after = None
    for step in range(INTERVENTION_STEP + 1, PERSIST_STEP + 1):
        world.advance(1, observer=tracker.observe)
        if step == BIRTH_STEP:
            child_birth = tracker.active.get(CHILD_STRUCTURE_ID)
            assert child_birth is not None, "published child identity not found at birth"
        elif step == MATCH_STEP:
            child_at_match = tracker.active.get(CHILD_STRUCTURE_ID)
            assert child_at_match is not None
        elif step == PERSIST_STEP:
            child_after = tracker.active.get(CHILD_STRUCTURE_ID)

    assert child_birth is not None and child_at_match is not None
    seed_ids = tuple(sorted(child_birth.particles))
    target_ids = tuple(sorted(child_at_match.particles))
    target_sig = child_at_match.signature.key
    assert len(target_ids) == 4 and len(seed_ids) == 2
    assert child_at_match.signature.exact
    assert set(seed_ids) <= set(target_ids)
    assert child_after is not None and child_after.signature.key == target_sig

    baseline = run_arm(snapshot, seed_ids, target_sig, target_ids, "baseline")
    assert baseline["final_state_hash"] == world.state_hash_full(), "clone does not reproduce baseline"
    assert baseline["final_rng_fingerprint"] == world.rng.fingerprint()
    assert baseline["measurements"][str(MATCH_STEP)]["seed_has_target_signature"]
    assert baseline["measurements"][str(PERSIST_STEP)]["seed_has_target_signature"]

    arms = []
    for shift in SHIFTS:
        arms.append(run_arm(snapshot, seed_ids, target_sig, target_ids,
                            "move_template", template_ids, shift))
        if sham is not None:
            arms.append(run_arm(snapshot, seed_ids, target_sig, target_ids,
                                "move_remote_sham", tuple(sorted(sham.particles)), shift))

    valid = [arm for arm in arms if arm["valid"]]
    summary = {}
    for mode in ("move_template", "move_remote_sham"):
        selected = [arm for arm in valid if arm["mode"] == mode]
        summary[mode] = {
            "valid_runs": len(selected),
            "matched_at_original_step": sum(
                a["measurements"][str(MATCH_STEP)]["seed_has_target_signature"]
                for a in selected),
            "matched_at_persistence_step": sum(
                a["measurements"][str(PERSIST_STEP)]["seed_has_target_signature"]
                for a in selected),
            "baseline_identical_state_at_end": sum(
                a["final_state_hash"] == baseline["final_state_hash"]
                for a in selected),
        }

    result = {
        "experiment": "m6.2e-single-event-counterfactual",
        "epistemic_status": "post-hoc exploratory, not preregistered",
        "source_run": RUN_ID,
        "source_config_hash": run["config_hash"],
        "intervention_step": INTERVENTION_STEP,
        "source_birth_step": BIRTH_STEP,
        "source_match_step": MATCH_STEP,
        "source_persistence_step": PERSIST_STEP,
        "target_signature": target_sig,
        "template_structure_id": TEMPLATE_STRUCTURE_ID,
        "child_structure_id": CHILD_STRUCTURE_ID,
        "template_particle_ids": list(template_ids),
        "child_birth_seed_ids": list(seed_ids),
        "child_matched_particle_ids": list(target_ids),
        "sham_structure_id": sham.structure_id if sham else None,
        "sham_same_signature": bool(sham),
        "baseline": baseline,
        "arms": arms,
        "summary": summary,
        "limitations": [
            "Relocation is an external nonphysical intervention, not an ALife rule.",
            "Changing occupancy can alter RNG consumption in later chemistry.",
            "One post-selected event cannot establish statistical significance.",
            "An effect of relocation would establish sensitivity to spatial intervention, not templated copying.",
            "Absence of an effect under chosen shifts is not a proof of causal independence under all interventions.",
            "The template is an all-S0 chain; identity of a common motif is weak informational evidence.",
        ],
        "scientific_verdict": "causal_replication_not_demonstrated",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source": RUN_ID,
        "baseline_reproduced": True,
        "template": TEMPLATE_STRUCTURE_ID,
        "child": CHILD_STRUCTURE_ID,
        "template_particles": list(template_ids),
        "seed_particles": list(seed_ids),
        "target_particles": list(target_ids),
        "target_signature": target_sig,
        "sham": sham.structure_id if sham else None,
        "summary": summary,
        "verdict": result["scientific_verdict"],
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
