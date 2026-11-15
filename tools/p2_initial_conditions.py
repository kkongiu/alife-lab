"""P2 frozen-protocol initial-condition intervention for unfed-6101.

The protocol JSON was committed BEFORE this runner and BEFORE any experiment.
This selected *post hoc* case is descriptive, not evidence of reproduction.

The only intervention is translating initially unbonded S0 particles in a
COPY of the post-placement world at tick 0. This is NOT a simulator law.
Original M6 hash and physical engine code remain unchanged.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from alife.config import load_config
from alife.particles import EMPTY, ParticleStore
from alife.rng import RNG
from alife.structures import components, signature
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "campaigns/m6_2e/p2_initial_conditions_protocol.json"
MANIFEST = ROOT / "campaigns/m6_2e/manifest.json"
OUT = ROOT / "campaigns/m6_2e/p2_initial_conditions_results.json"


def duplicate_world(world: World) -> World:
    """Deep-copy ALL mutable material and PRNG/ledger state."""
    store = world.store
    replica_store = ParticleStore(
        store.width, store.height, store.ids, store.xs, store.ys,
        store.species, store.energy, store.bond_records(),
    )
    rng = RNG(world.config.seed)
    rng.set_state(world.rng.state())
    rng.draws = world.rng.draws
    replica = World(
        world.config, rng, replica_store, step=world.step,
        moves_total=world.moves_total, next_id=world.next_id,
        bonds_formed_total=world.bonds_formed_total,
        bonds_broken_total=world.bonds_broken_total,
        injected=world.injected, dissipated=world.dissipated,
        unabsorbed=world.unabsorbed, source_acc=world.source_acc,
        source_store=world.source_store,
    )
    assert replica.state_hash_full() == world.state_hash_full()
    assert replica.rng.draws == world.rng.draws
    assert replica.rng.state() == world.rng.state()
    replica.check()
    return replica


def translate_initial_group(world: World, ids: tuple[int, ...],
                            shift: tuple[int, int]) -> tuple[bool, str | None]:
    """Move four unbonded particles; preserve identities, energy, RNG, bonds."""
    s = world.store
    if not ids or len(set(ids)) != len(ids):
        return False, "invalid_group"
    indices = [s.index_of(identity) for identity in ids]
    if any(s.degree[i] != 0 for i in indices):
        return False, "not_initially_unbonded"
    if shift == (0, 0):
        return False, "no_intervention"
    width, height = s.width, s.height
    new_positions = [
        ((s.xs[i] + shift[0]) % width, (s.ys[i] + shift[1]) % height)
        for i in indices
    ]
    if len(set(new_positions)) != len(new_positions):
        return False, "duplicate_target"
    own = set(indices)
    if any(
        s.grid[y * width + x] != EMPTY and
        s.grid[y * width + x] not in own
        for x, y in new_positions
    ):
        return False, "occupied_target"
    for i in indices:
        s.grid[s.ys[i] * width + s.xs[i]] = EMPTY
    for i, (x, y) in zip(indices, new_positions):
        s.xs[i], s.ys[i] = x, y
        s.grid[y * width + x] = i
    world.check()
    return True, None


def toroidal_distance(world: World, a: int, b: int) -> int:
    s = world.store
    i, j = s.index_of(a), s.index_of(b)
    dx, dy = abs(s.xs[i] - s.xs[j]), abs(s.ys[i] - s.ys[j])
    if world.periodic:
        dx, dy = min(dx, s.width - dx), min(dy, s.height - dy)
    return dx + dy


def local_occupancy(world: World, identity: int, radius: int = 2) -> int:
    """Number of occupied cells at Manhattan distance <= radius."""
    s = world.store
    idx = s.index_of(identity)
    cx, cy = s.xs[idx], s.ys[idx]
    count = 0
    for dx in range(-radius, radius + 1):
        for dy in range(-radius + abs(dx), radius - abs(dx) + 1):
            if dx == 0 and dy == 0:
                continue
            x, y = cx + dx, cy + dy
            if world.periodic:
                x, y = x % s.width, y % s.height
            if 0 <= x < s.width and 0 <= y < s.height:
                count += s.grid[y * s.width + x] != EMPTY
    return count


def choose_shams(world: World, parents: tuple[int, ...],
                 seeds: tuple[int, ...], quantity: int = 2) -> list[tuple[int, ...]]:
    """Match sham particles on original t=0 geometry/species/energy only.

    Greedy matching is deterministic, tied by ID, and explicitly not a
    statistical randomization. The entire procedure is frozen in protocol.
    """
    s = world.store
    excluded = set(parents) | set(seeds)
    target = []
    for pid in parents:
        i = s.index_of(pid)
        target.append((
            s.species[i], s.energy[i],
            toroidal_distance(world, pid, seeds[0]),
            toroidal_distance(world, pid, seeds[1]),
            local_occupancy(world, pid),
        ))
    sets = []
    for _ in range(quantity):
        selected = []
        for species, energy, d0, d1, density in target:
            eligible = []
            for pid in s.ids:
                if pid in excluded:
                    continue
                i = s.index_of(pid)
                if s.degree[i] != 0:
                    continue
                if (s.species[i], s.energy[i]) != (species, energy):
                    continue
                dist = (
                    abs(toroidal_distance(world, pid, seeds[0]) - d0) +
                    abs(toroidal_distance(world, pid, seeds[1]) - d1)
                )
                eligible.append(((dist, abs(local_occupancy(world, pid)-density), pid),pid))
            if not eligible:
                raise AssertionError("insufficient matched sham particles")
            chosen = min(eligible)[1]
            selected.append(chosen)
            excluded.add(chosen)
        sets.append(tuple(selected))
    assert len(set(x for group in sets for x in group)) == quantity * len(parents)
    return sets


def readout(world: World, parents: tuple[int, ...],
            seeds: tuple[int, ...], expected: str) -> dict:
    """Physical membership only; never equate tracker ID with causality."""
    s = world.store
    comp_ids = []
    comps = {}
    for i, (indices, bonds) in enumerate(components(s)):
        ids = set(s.ids[k] for k in indices)
        comps[i] = (indices, bonds, ids)
        if ids.intersection(set(parents + seeds)):
            comp_ids.append((i, ids))
    def which(pid):
        return next((idx for idx, ids in comp_ids if pid in ids), None)
    group = which(seeds[0])
    together = group is not None and which(seeds[1]) == group
    data = {
        "step": world.step,
        "rng_draws": world.rng.draws,
        "rng_state_sha": world.rng.fingerprint(),
        "any_cross": any(
            which(child) is not None and which(child) == which(parent)
            for child in seeds for parent in parents
        ),
        "all_six": (
            group is not None and
            all(which(pid) == group for pid in parents + seeds)
        ),
        "seed_component_signature": None,
        "seed_component_members": [],
        "exact_target": False,
        "contains_no_parent_particles": False,
    }
    if together:
        indices, bonds, ids = comps[group]
        sig = signature(s, indices, bonds, world.species_names)
        data["seed_component_signature"] = sig.key
        data["seed_component_members"] = sorted(ids)
        data["contains_no_parent_particles"] = ids.isdisjoint(parents)
        data["exact_target"] = sig.exact and sig.key == expected
    return data


def run_arm(initial: World, group: tuple[int, ...], shift: tuple[int, int],
            parent: tuple[int, ...], seeds: tuple[int, ...],
            expected: str, max_step: int, key_steps: tuple[int, ...],
            original: dict[int, dict]) -> dict:
    world = duplicate_world(initial)
    before_rng = world.rng.fingerprint()
    before_draws = world.rng.draws
    before_energy = world.energy()
    ok, reason = translate_initial_group(world, group, shift)
    if not ok:
        return {"valid": False, "invalid_reason": reason}
    assert world.rng.fingerprint() == before_rng and world.rng.draws == before_draws
    assert world.energy() == before_energy

    first_rng_div = None
    first_seed_div = None
    capture = {}
    for _ in range(max_step):
        world.advance(1)
        state = readout(world, parent, seeds, expected)
        original_step = original[world.step]
        if first_rng_div is None and (
            state["rng_draws"] != original_step["rng_draws"] or
            state["rng_state_sha"] != original_step["rng_state_sha"]
        ):
            first_rng_div = world.step
        if first_seed_div is None and (
            state["seed_component_signature"] != original_step["seed_component_signature"] or
            state["seed_component_members"] != original_step["seed_component_members"]
        ):
            first_seed_div = world.step
        if world.step in key_steps:
            capture[str(world.step)] = {
                "seed_component_signature": state["seed_component_signature"],
                "seed_component_members": state["seed_component_members"],
                "exact_target": state["exact_target"],
                "contains_no_parent_particles": state["contains_no_parent_particles"],
                "any_cross": state["any_cross"],
                "all_six": state["all_six"],
                "rng_draws_delta_from_baseline":
                    state["rng_draws"] - original_step["rng_draws"],
            }
    world.check()
    match_835 = capture["835"]["exact_target"] and capture["835"]["contains_no_parent_particles"]
    match_845 = capture["845"]["exact_target"] and capture["845"]["contains_no_parent_particles"]
    return {
        "valid": True,
        "first_rng_divergence_step": first_rng_div,
        "first_seed_component_divergence_step": first_seed_div,
        "matches_step_835": match_835,
        "matches_step_845": match_845,
        "matches_both": match_835 and match_845,
        "same_original_four_at_835": (
            capture["835"]["seed_component_members"] == [40, 93, 245, 477]
        ),
        "same_original_four_at_845": (
            capture["845"]["seed_component_members"] == [40, 93, 245, 477]
        ),
        "all_six_common_at_step_770": capture["770"]["all_six"],
        "key_steps": capture,
        "final_hash_at_845": world.state_hash_full(),
    }


def run() -> dict:
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"] == "alife-m6-2e-p2-ic-counterfactual-v1"
    assert p["status"] == "preregistered-before-execution"
    assert p["criteria"]["end_step"] == 845
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    spec = next(x for x in m["runs"] if x["id"] == p["input"]["run_id"])
    assert spec["config_hash"] == p["input"]["expected_config_hash"]
    assert spec["expected_world_hash"] == p["input"]["expected_world_hash"]
    config = load_config(ROOT / "campaigns/m6" / spec["config"])
    assert config.hash() == spec["config_hash"]
    initial = World.create(config)
    assert initial.step == 0 and not initial.store.bonds
    parent = tuple(p["hypothetical_parent_particle_ids"])
    seeds = tuple(p["daughter_seed_particle_ids"])
    expected = p["final_signature"]
    shams = choose_shams(initial, parent, seeds)
    shifts = [tuple(v) for v in p["criteria"]["shifts"]]
    max_step = p["criteria"]["end_step"]
    keys = tuple(p["criteria"]["important_ticks"])
    assert 835 in keys and 845 in keys and 770 in keys

    # Unaltered baseline is replayed once and verified against original M6.
    baseline = duplicate_world(initial)
    reference = {}
    for step in range(1, max_step+1):
        baseline.advance(1)
        reference[step] = readout(baseline, parent, seeds, expected)
    baseline_835 = reference[835]
    baseline_845 = reference[845]
    assert baseline_835["exact_target"] and baseline_845["exact_target"]
    assert baseline_835["seed_component_members"] == [40, 93, 245, 477]
    assert reference[770]["all_six"]
    baseline.advance(3000-max_step)
    baseline.check()
    assert baseline.state_hash_full() == spec["expected_world_hash"]

    attempts = []
    for shift in shifts:
        labels = ("relocate_future_parent","relocate_matched_sham_a","relocate_matched_sham_b")
        group_ids = (parent, shams[0], shams[1])
        # Prevalidate *all* arms, independent of all future outcomes.
        probes = []
        for group in group_ids:
            probe = duplicate_world(initial)
            valid, reason = translate_initial_group(probe, group, shift)
            probes.append({"valid": valid, "reason": reason})
        paired_valid = all(check["valid"] for check in probes)
        trial = {
            "shift": list(shift),
            "valid_for_all_three": paired_valid,
            "validity": {label: state for label, state in zip(labels, probes)},
            "arms": {},
        }
        if paired_valid:
            for label, group in zip(labels, group_ids):
                trial["arms"][label] = run_arm(
                    initial, group, shift, parent, seeds, expected,
                    max_step, keys, reference,
                )
        attempts.append(trial)

    valid = [x for x in attempts if x["valid_for_all_three"]]
    totals = {}
    for label in ("relocate_future_parent","relocate_matched_sham_a","relocate_matched_sham_b"):
        selected = [a["arms"][label] for a in valid]
        totals[label] = {
            "trials": len(selected),
            "matched_at_835": sum(v["matches_step_835"] for v in selected),
            "matched_at_845": sum(v["matches_step_845"] for v in selected),
            "matched_both": sum(v["matches_both"] for v in selected),
            "same_original_four_at_835": sum(v["same_original_four_at_835"] for v in selected),
            "common_ancestor_at_770": sum(v["all_six_common_at_step_770"] for v in selected),
            "first_rng_divergence_by_shift": [v["first_rng_divergence_step"] for v in selected],
        }
    insufficient = len(valid) < p["criteria"]["min_valid_triplets"]
    every_arm_rng_diverged = bool(valid) and all(
        arm["first_rng_divergence_step"] is not None and
        arm["first_rng_divergence_step"] <= 835
        for t in valid for arm in t["arms"].values()
    )
    r = {
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "protocol_version": p["schema"],
        "epistemic_status": p["epistemic_scope"],
        "world_laws_unchanged": True,
        "source_m6_hash_verified": True,
        "initial_step": 0,
        "future_parent_particle_ids": list(parent),
        "daughter_seed_particle_ids": list(seeds),
        "matched_shams": [list(s) for s in shams],
        "initial_group_profiles": {
            label: {
                "ids": list(group),
                "species": [initial.species_names[initial.store.species[initial.store.index_of(pid)]] for pid in group],
                "energy": [initial.store.energy[initial.store.index_of(pid)] for pid in group],
                "distance_vectors_to_daughter_seeds": [
                    [toroidal_distance(initial, pid, seed) for seed in seeds] for pid in group
                ],
                "local_density": [local_occupancy(initial, pid) for pid in group],
            }
            for label, group in [
                ("future_parent",parent),("sham_a",shams[0]),("sham_b",shams[1])
            ]
        },
        "baseline": {
            "matched_at_835": baseline_835["exact_target"],
            "matched_at_845": baseline_845["exact_target"],
            "matched_particles_at_835": baseline_835["seed_component_members"],
            "common_ancestor_at_770": reference[770]["all_six"],
        },
        "attempts": attempts,
        "summary": {
            "total_shifts": len(shifts),
            "valid_matched_triplets": len(valid),
            "invalid_shifts": len(shifts) - len(valid),
            "insufficient_valid_triplets": insufficient,
            "all_valid_arm_rngs_diverged_by_835": every_arm_rng_diverged,
            "arms": totals,
        },
        "interpretation": (
            "Descriptive initial-condition sensitivity of a post-selected case only. "
            "Moving unrelated S0 controls can change outcomes via the sequential RNG. "
            "No result is treated as a causal reproduction demonstration."
        ),
        "verdict": "inconclusive_for_causal_replication",
    }
    OUT.write_text(json.dumps(r, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({
        "world_hash_verified": True,
        "matched_shams": r["matched_shams"],
        "baseline": r["baseline"],
        "summary": r["summary"],
        "scientific_verdict": r["verdict"],
        "artifact": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return r


if __name__ == "__main__":
    run()
