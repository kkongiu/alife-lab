"""M6.3-0 — protocol-locked diagnostic screen for structural variants A/B.

The protocol is frozen at commit de5e7fb, BEFORE the runner.
This is a SYNTHETIC nonreplicator fixture, not evidence of spontaneous life.
No changes to World, chemistry, RNG, historical campaigns or detectors.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

from alife.config import Config
from alife.particles import ParticleStore
from alife.rng import RNG
from alife.structures import components, signature
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "campaigns/m6_3_0/protocol.json"
SOURCE_CONFIG = ROOT / "campaigns/m6/configs/unfed-6101.json"
RESULTS = ROOT / "campaigns/m6_3_0/results.json"


def frozen_protocol() -> dict:
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"] == "alife-m6-3-0-variant-specificity-screen-v1"
    assert p["status"] == "preregistered-before-runner-and-simulation"
    assert p["historical_safety"]["no_source_modifications"]
    assert p["model"]["duration_steps"] == 300
    assert p["model"]["arm_order"] == [
        "A", "B", "A_reverse", "B_reverse", "unbonded_A", "unbonded_B"
    ]
    return p


def _config(seed: int, protocol: dict) -> Config:
    original = json.loads(SOURCE_CONFIG.read_text(encoding="utf-8"))
    fixture = protocol["model"]
    original["seed"] = seed
    original["grid"] = fixture["fixture_grid"]
    counts = fixture["fixture_species_counts"]
    for spec in original["species"]:
        spec["count"] = counts[spec["name"]]
    return Config.from_dict(original).validate()


def _location_free_cells(width: int, height: int,
                         excluded: set[tuple[int, int]]) -> list[int]:
    return [
        y * width + x
        for y in range(height)
        for x in range(width)
        if (x, y) not in excluded
    ]


def make_world(seed: int, arm: str, protocol: dict | None = None) -> World:
    """Same random background and RNG stream across every arm of a seed.

    Three pre-existing scaffold bonds are a deliberate *initial condition*.
    Their stored energy and formation dissipation are correctly charged to the
    initial ledger, unlike a physically invalid free addition of bonds.
    """
    p = protocol if protocol is not None else frozen_protocol()
    fixture = p["model"]
    assert arm in fixture["arm_order"]
    config = _config(seed, p)
    index = {spec.name: i for i, spec in enumerate(config.species)}
    group = fixture["variant_sites"][arm]
    template_positions = [tuple(site) for site in fixture["scaffold_sites"]]
    template_species = [index[name] for name in group]
    assert Counter(group) == Counter({"S0": 2, "S1": 2})
    expected_total = sum(sp.count for sp in config.species)
    background = []
    for spec in config.species:
        remainder = spec.count - Counter(template_species)[index[spec.name]]
        assert remainder >= 0
        background.extend([index[spec.name]] * remainder)
    assert len(background) + 4 == expected_total
    assert len(template_positions) == len(set(template_positions)) == 4

    rng = RNG(seed)
    positions = list(template_positions)
    choices = _location_free_cells(
        config.grid.width, config.grid.height, set(template_positions)
    )
    for _ in background:
        cell = choices.pop(rng.raw() % len(choices))
        y, x = divmod(cell, config.grid.width)
        positions.append((x, y))

    species = template_species + background
    energy = [config.species[i].energy for i in species]
    initial_bonds = []
    initially_dissipated = 0
    if arm in fixture["bonded_arms"]:
        cost = config.chemistry.bond_cost
        loss = config.energy.formation_dissipation
        for a, b in fixture["scaffold_bonds"]:
            energy[a] -= cost + loss
            energy[b] -= cost + loss
            initial_bonds.append((a, b, 2 * cost))
            initially_dissipated += 2 * loss
    assert all(v >= 0 for v in energy)

    store = ParticleStore(
        config.grid.width, config.grid.height,
        list(range(expected_total)),
        [x for x, y in positions], [y for x, y in positions],
        species, energy, initial_bonds,
    )
    world = World(config, rng, store, dissipated=initially_dissipated)
    world.check()
    return world


def signature_of_scaffold(world: World) -> str | None:
    for indices, bonds in components(world.store):
        ids = {world.store.ids[i] for i in indices}
        if {0, 1, 2, 3} <= ids:
            if ids != {0, 1, 2, 3}:
                return None
            sig = signature(world.store, indices, bonds, world.species_names)
            assert sig.exact and sig.size == 4
            return sig.key
    return None


def toroidal_distance(a: tuple[int, int], b: tuple[int, int], width: int,
                      height: int) -> int:
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return min(dx, width - dx) + min(dy, height - dy)


def event_counts_for_world(world: World, protocol: dict,
                           target_signatures: dict[str, str]) -> dict:
    """Observer only reads world, tracks material overlaps and counts first
    appearance of disjoint exact motif; no RNG or physics modification."""
    parent_ids = set(protocol["model"]["scaffold_particle_ids"])
    anchors = [tuple(site) for site in protocol["model"]["scaffold_sites"]]
    radius = 2
    seen = set()
    ever_shared = set()
    counter = Counter()
    events = []
    opportunity_free_near = 0
    initial_fingerprint = world.rng.fingerprint()
    initial_draws = world.rng.draws
    initial_bonds = world.store.bond_records()
    original_hash = world.state_hash_full()
    original_scaffold = signature_of_scaffold(world)

    def observe(w: World) -> None:
        nonlocal opportunity_free_near
        before = w.rng.draws
        s = w.store
        inside = []
        for indices, bonds in components(s):
            members = {s.ids[i] for i in indices}
            inside.append((indices, bonds, members))
            if members & parent_ids:
                ever_shared.update(members - parent_ids)

        # Exposure is a crude contact-opportunity proxy, NOT a direct measure
        # of catalytic interactions or residence time at individual sites.
        for i in range(4, len(s)):
            if s.degree[i] > 0:
                continue
            p = (s.xs[i], s.ys[i])
            if any(toroidal_distance(p, a, s.width, s.height) <= 1 for a in anchors):
                opportunity_free_near += 1

        for indices, bonds, members in inside:
            if len(indices) != 4 or members & parent_ids:
                continue
            sig = signature(s, indices, bonds, w.species_names)
            if not sig.exact or sig.key not in set(target_signatures.values()):
                continue
            variant = next(
                name for name, key in target_signatures.items() if key == sig.key
            )
            material_ids = tuple(sorted(members))
            identifier = (sig.key, material_ids)
            if identifier in seen:
                continue
            seen.add(identifier)
            near = any(
                toroidal_distance((s.xs[i], s.ys[i]), a, s.width, s.height) <= radius
                for i in indices for a in anchors
            )
            shared = bool(members & ever_shared)
            prefix = "near" if near else "distant"
            counter[f"new_{variant}_anywhere"] += 1
            counter[f"new_{variant}_{prefix}"] += 1
            if shared:
                counter[f"new_{variant}_previously_material_shared"] += 1
            else:
                counter[f"new_{variant}_strict_{prefix}"] += 1
            events.append({
                "step": w.step,
                "variant": variant,
                "particle_ids": list(material_ids),
                "near_scaffold_site": near,
                "previous_material_contact_with_scaffold": shared,
            })
        assert w.rng.draws == before, "Observer consumed RNG!"

    for _ in range(protocol["model"]["duration_steps"]):
        world.advance(1, observer=observe)
    world.check()
    output = {
        "seed": world.config.seed,
        "config_sha256": world.config.hash(),
        "initial_world_hash": original_hash,
        "final_world_hash": world.state_hash_full(),
        "initial_rng_fingerprint": initial_fingerprint,
        "initial_rng_draws": initial_draws,
        "initial_scaffold_bonds": initial_bonds,
        "initial_scaffold_signature": original_scaffold,
        "final_rng_fingerprint": world.rng.fingerprint(),
        "final_rng_draws": world.rng.draws,
        "elapsed_steps": world.step,
        "initial_dissipated": len(initial_bonds) * 2 * world.config.energy.formation_dissipation,
        "initial_scaffold_intact": original_scaffold is not None,
        "opportunity_free_near_site_ticks": opportunity_free_near,
        "bonds_formed_after_start": world.bonds_formed_total,
        "bonds_broken_after_start": world.bonds_broken_total,
        "counts": dict(sorted(counter.items())),
        "new_variant_events": events,
    }
    assert world.step == protocol["model"]["duration_steps"]
    return output


def run() -> dict:
    protocol = frozen_protocol()
    model = protocol["model"]
    first_seed = model["seed_list"][0]
    origin_a = make_world(first_seed, "A", protocol)
    origin_b = make_world(first_seed, "B", protocol)
    sig_a, sig_b = signature_of_scaffold(origin_a), signature_of_scaffold(origin_b)
    assert sig_a and sig_b and sig_a != sig_b
    # Reversal should not change a linear chain's canonical signature.
    assert signature_of_scaffold(make_world(first_seed, "A_reverse", protocol)) == sig_a
    assert signature_of_scaffold(make_world(first_seed, "B_reverse", protocol)) == sig_b
    assert signature_of_scaffold(make_world(first_seed, "unbonded_A", protocol)) is None
    assert signature_of_scaffold(make_world(first_seed, "unbonded_B", protocol)) is None
    signatures = {"A": sig_a, "B": sig_b}

    results = []
    grouped = {arm: [] for arm in model["arm_order"]}
    for seed in model["seed_list"]:
        baseline_background = None
        for arm in model["arm_order"]:
            world = make_world(seed, arm, protocol)
            scaffold = signature_of_scaffold(world)
            if arm in model["bonded_arms"]:
                assert scaffold == sig_a if arm.startswith("A") else scaffold == sig_b
            else:
                assert scaffold is None
            # RNG state is identical after random background placement for all
            # arms; the chemical trajectories are NOT constrained to stay equal.
            aligned = (world.rng.fingerprint(), world.rng.draws,
                       tuple((world.store.xs[i], world.store.ys[i],
                              world.store.species[i]) for i in range(4,len(world.store))))
            if baseline_background is None:
                baseline_background = aligned
            else:
                assert aligned == baseline_background, "initial backgrounds differ"

            obs = event_counts_for_world(world, protocol, signatures)
            obs["arm"] = arm
            grouped[arm].append(obs)
            results.append(obs)
        print(f"seed {seed}: six arms completed", flush=True)

    # One exact replay verifies the deterministic data-generation method.
    replay_world = make_world(first_seed, "A", protocol)
    replay = event_counts_for_world(replay_world, protocol, signatures)
    original = grouped["A"][0]
    assert replay == {k:v for k,v in original.items() if k!="arm"}

    summary = {}
    for arm, runs in grouped.items():
        totals = Counter()
        for item in runs:
            totals.update(item["counts"])
        summary[arm] = {
            "runs": len(runs),
            "strict_near_A": totals["new_A_strict_near"],
            "strict_near_B": totals["new_B_strict_near"],
            "all_near_A": totals["new_A_near"],
            "all_near_B": totals["new_B_near"],
            "all_anywhere_A": totals["new_A_anywhere"],
            "all_anywhere_B": totals["new_B_anywhere"],
            "runs_with_strict_near": sum(
                bool(r["counts"].get("new_A_strict_near",0) +
                     r["counts"].get("new_B_strict_near",0)) for r in runs
            ),
            "cumulative_free_near_site_ticks": sum(
                r["opportunity_free_near_site_ticks"] for r in runs
            ),
            "bonds_formed_after_start": sum(
                r["bonds_formed_after_start"] for r in runs
            ),
        }

    min_per_arm = 5
    enough = all(
        summary[arm]["strict_near_A"] + summary[arm]["strict_near_B"] >= min_per_arm
        for arm in model["bonded_arms"]
    )
    def preferred(arm: str) -> int:
        desired = "A" if arm.startswith("A") else "B"
        other = "B" if desired == "A" else "A"
        return sum(
            r["counts"].get(f"new_{desired}_strict_near",0) >
            r["counts"].get(f"new_{other}_strict_near",0)
            for r in grouped[arm]
        )
    preferred_seeds = {arm:preferred(arm) for arm in model["bonded_arms"]}
    followup_gate = enough and all(n>=8 for n in preferred_seeds.values())

    record = {
        "experiment":"M6.3-0 A/B variant-specificity screen",
        "protocol":str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "preregistered_protocol_commit":"de5e7fbb82bc3049fcdc6bdf3fd34f2e37f6cf92",
        "source_original_config":str(SOURCE_CONFIG.relative_to(ROOT)),
        "source_original_config_sha256":hashlib.sha256(SOURCE_CONFIG.read_bytes()).hexdigest(),
        "frozen_template_signatures":signatures,
        "conditions":model["arm_order"],
        "seeds":model["seed_list"],
        "summary":summary,
        "followup_gate":{
            "minimum_five_strict_near_each_bonded_arm":enough,
            "positive_preference_seeds_by_arm":preferred_seeds,
            "gate_passed":followup_gate
        },
        "results":results,
        "epistemic_status":"screening of synthetic template with unchanged physics, NOT causal reproduction",
        "verdict":"suggestive_specificity_requires_independent_validation" if followup_gate
                  else "no_sufficient_variant_specificity_signal_at_tested_regime",
        "limitations":[
            "Injected scaffold is synthesized at tick zero, not spontaneously emerged.",
            "Chain A and B expose species at different positions; local contact geometry is a confound.",
            "Unbonded A/B controls have different initial bond energy and dissipated ledger.",
            "Global sequential RNG may diverge when local reaction opportunities differ.",
            "No descendant generations, mutation rates or evolutionary fitness are measured.",
            "A null result does not prove impossibility under all regimes."
        ],
    }
    RESULTS.parent.mkdir(parents=True,exist_ok=True)
    RESULTS.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
       "signatures":signatures,"n_runs":len(results),
       "summary":summary,"gate":record["followup_gate"],
       "verdict":record["verdict"],"artifact":str(RESULTS.relative_to(ROOT))
    },indent=2),flush=True)
    return record


if __name__ == "__main__":
    run()
