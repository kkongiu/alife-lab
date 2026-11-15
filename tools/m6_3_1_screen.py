"""M6.3-1: access/exposure and specificity screen with original ALife physics.

Protocol committed at 91d62e85 BEFORE this runner. Uses the existing
M6.3-0 fixture builder; no modifications of dynamics, RNG or detectors.
Synthetic four-atom templates are probes, not naturally emerged replicators.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from alife.structures import components, signature
from alife.world import World
from tools.m6_3_0_screen import (
    make_world, signature_of_scaffold, toroidal_distance,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "campaigns/m6_3_1/protocol.json"
OUTPUT = ROOT / "campaigns/m6_3_1/results.json"


def protocol() -> dict:
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"] == "alife-m6-3-1-variant-accessibility-v1"
    assert p["status"] == "frozen_before_runner_or_outcome_inspection"
    assert p["model"]["seed_list"] == list(range(8101,8117))
    assert p["model"]["duration_steps"] == 450
    assert p["model"]["arm_order"] == [
        "A", "B", "A_reverse", "B_reverse", "C"
    ]
    return p


def density_protocol(p: dict, density: str) -> dict:
    cloned = deepcopy(p)
    cloned["model"]["fixture_species_counts"] = p["model"]["densities"][density]
    return cloned


def variants(p: dict) -> dict[str,str]:
    seed = p["model"]["seed_list"][0]
    low = density_protocol(p, "baseline")
    signatures = {
        v:signature_of_scaffold(make_world(seed, v, low))
        for v in ("A", "B", "C")
    }
    assert all(signatures.values())
    assert len(set(signatures.values())) == 3
    assert signature_of_scaffold(make_world(seed,"A_reverse",low)) == signatures["A"]
    assert signature_of_scaffold(make_world(seed,"B_reverse",low)) == signatures["B"]
    return signatures


def take_measurements(world: World, p: dict, arm: str,
                      targets: dict[str,str]) -> dict:
    """Observer never modifies the world, doesn't use RNG, and keeps every zero."""
    src_ids = set(p["model"]["scaffold_particle_ids"])
    anchors = [tuple(site) for site in p["model"]["scaffold_sites"]]
    initial_signature = signature_of_scaffold(world)
    assert initial_signature == targets[arm.replace("_reverse","")] 
    first_failure = None
    active_ticks = 0
    active_intervals = []
    active_start = None
    ever_shared: set[int] = set()
    ever_seen: set[tuple[str,tuple[int,...]]] = set()
    counts: Counter[str] = Counter()
    events: list[dict] = []
    exposed = Counter()
    initial_fingerprint = world.rng.fingerprint()
    initial_rng_draws = world.rng.draws
    initial_energy = world.energy()
    initial_dissipated = world.dissipated
    initial_hash = world.state_hash_full()
    anchors_set = set(anchors)
    sig_to_name = {sig:name for name,sig in targets.items()}

    def observe(w: World) -> None:
        nonlocal first_failure, active_ticks, active_start
        before = w.rng.draws
        store = w.store
        comps = []
        template_component = None
        for indices,bonds in components(store):
            ids = {store.ids[i] for i in indices}
            comps.append((indices,bonds,ids))
            if ids & src_ids:
                ever_shared.update(ids - src_ids)
            if src_ids <= ids:
                template_component = (indices,bonds,ids)

        active = False
        if template_component is not None:
            indices,bonds,ids = template_component
            if ids == src_ids and len(bonds) == 3:
                s = signature(store,indices,bonds,w.species_names)
                active = s.exact and s.key == initial_signature
        if active:
            active_ticks += 1
            if active_start is None:
                active_start = w.step
        else:
            if first_failure is None:
                first_failure = w.step
            if active_start is not None:
                active_intervals.append([active_start,w.step-1])
                active_start = None

        # Count independent *available* monomers, split by source species.
        # A particle adjacent to multiple scaffold sites counts only once/tick.
        for i in range(4,len(store)):
            if store.degree[i] > 0:
                continue
            xy = (store.xs[i],store.ys[i])
            if any(toroidal_distance(xy,a,store.width,store.height) == 1
                   for a in anchors):
                group = "active" if active else "inactive"
                exposed[f"{group}_free_{w.species_names[store.species[i]]}"] += 1

        for indices,bonds,ids in comps:
            if len(indices)!=4 or ids & src_ids:
                continue
            if len(bonds)!=3:
                continue
            s = signature(store,indices,bonds,w.species_names)
            name = sig_to_name.get(s.key) if s.exact else None
            if name is None:
                continue
            ids_key = tuple(sorted(ids))
            key = (s.key,ids_key)
            if key in ever_seen:
                continue
            ever_seen.add(key)
            near = any(
                toroidal_distance((store.xs[i],store.ys[i]),a,
                                  store.width,store.height) <= 2
                for i in indices for a in anchors
            )
            previously_shared = not ids.isdisjoint(ever_shared)
            phase = "active" if active else "inactive"
            distance = "near" if near else "distant"
            counts[f"all_{name}"] += 1
            counts[f"{phase}_{distance}_{name}"] += 1
            if not previously_shared:
                counts[f"strict_{phase}_{distance}_{name}"] += 1
            events.append({
                "tick":w.step,
                "variant":name,
                "ids":list(ids_key),
                "near":near,
                "source_scaffold_intact":active,
                "ever_shared_scaffold_component":previously_shared,
            })
        assert before == w.rng.draws, "observer consumed RNG"

    for _ in range(p["model"]["duration_steps"]):
        world.advance(1,observer=observe)
    if active_start is not None:
        active_intervals.append([active_start,world.step])
    world.check()
    return {
        "seed":world.config.seed,
        "arm":arm,
        "initial_hash":initial_hash,
        "final_hash":world.state_hash_full(),
        "config_hash":world.config.hash(),
        "initial_energy":initial_energy,
        "initial_dissipated":initial_dissipated,
        "final_energy":world.energy(),
        "final_dissipated":world.dissipated,
        "active_template_ticks":active_ticks,
        "first_template_failure_step":first_failure,
        "active_template_intervals":active_intervals,
        "free_monomer_exposure_ticks":dict(sorted(exposed.items())),
        "counts":dict(sorted(counts.items())),
        "new_variant_events":events,
        "bond_formations":world.bonds_formed_total,
        "bond_breaks":world.bonds_broken_total,
        "initial_rng_draws":initial_rng_draws,
        "final_rng_draws":world.rng.draws,
        "initial_rng_fingerprint":initial_fingerprint,
        "final_rng_fingerprint":world.rng.fingerprint(),
        "ticks":world.step,
    }


def paired_initial_state(w: World) -> tuple:
    s=w.store
    return (
        w.config.hash(), w.rng.draws, w.rng.fingerprint(),
        tuple((s.ids[i],s.xs[i],s.ys[i],s.species[i],s.energy[i])
              for i in range(4,len(s))),
        w.energy(),w.dissipated
    )


def analyse_runs(p: dict, runs: list[dict]) -> dict:
    densities = tuple(p["model"]["densities"])
    arms = tuple(p["model"]["arm_order"])
    results = {}
    preference = {}
    by_key={(r["density"],r["seed"],r["arm"]):r for r in runs}
    for density in densities:
        for arm in arms:
            subset=[by_key[(density,s,arm)] for s in p["model"]["seed_list"]]
            near={v:sum(r["counts"].get(f"strict_active_near_{v}",0)
                        for r in subset) for v in ("A","B","C")}
            expo=sum(
                sum(v for key,v in r["free_monomer_exposure_ticks"].items()
                    if key in ("active_free_S0","active_free_S1"))
                for r in subset
            )
            key=f"{density}/{arm}"
            results[key]={
                "seed_count":len(subset),
                "strict_active_near":near,
                "strict_active_distant":{
                    v:sum(r["counts"].get(f"strict_active_distant_{v}",0)
                          for r in subset) for v in ("A","B","C")
                },
                "strict_inactive_near":{
                    v:sum(r["counts"].get(f"strict_inactive_near_{v}",0)
                          for r in subset) for v in ("A","B","C")
                },
                "all_anywhere":{
                    v:sum(r["counts"].get(f"all_{v}",0) for r in subset)
                    for v in ("A","B","C")
                },
                "template_active_ticks":sum(r["active_template_ticks"] for r in subset),
                "runs_active_at_least_100":sum(r["active_template_ticks"]>=100 for r in subset),
                "intact_free_S0_S1_exposure_ticks":expo,
                "strict_active_near_rate_per_1000_exposures":{
                    v:(round(1000*near[v]/expo,5) if expo else None)
                    for v in ("A","B","C")
                },
                "total_bond_formations":sum(r["bond_formations"] for r in subset),
                "runs_with_strict_active_near_AB":sum(
                    r["counts"].get("strict_active_near_A",0)
                    + r["counts"].get("strict_active_near_B",0)>0
                    for r in subset
                )
            }

        for arm in ("A","B","A_reverse","B_reverse"):
            want="A" if arm.startswith("A") else "B"
            other="B" if want=="A" else "A"
            preference[f"{density}/{arm}"]=sum(
                by_key[(density,seed,arm)]["counts"].get(f"strict_active_near_{want}",0)
                >by_key[(density,seed,arm)]["counts"].get(f"strict_active_near_{other}",0)
                for seed in p["model"]["seed_list"]
            )
    high="enriched"
    test_arms=("A","B","A_reverse","B_reverse")
    enough_events=all(
        sum(results[f"{high}/{arm}"]["strict_active_near"][v] for v in ("A","B"))>=8
        for arm in test_arms
    )
    enough_active=all(
        results[f"{high}/{arm}"]["runs_active_at_least_100"]>=8
        for arm in test_arms
    )
    enough=enough_events and enough_active
    preferred=all(preference[f"{high}/{arm}"]>=11 for arm in test_arms)
    return {
        "densities_and_arms":results,
        "preference_seed_count":preference,
        "gates":{
            "enriched_min_eight_near_AB_in_each_arm":enough_events,
            "enriched_min_eight_seeds_100_ticks_intact":enough_active,
            "power_gate":enough,
            "specificity_gate":enough and preferred,
        },
        "verdict":"screen_signal_for_followup" if enough and preferred
                  else "underpowered_or_no_detectable_specificity"
    }


def run() -> dict:
    p=protocol()
    targets=variants(p)
    runs=[]
    for density in p["model"]["densities"]:
        setup=density_protocol(p,density)
        first_seed=p["model"]["seed_list"][0]
        scaffold_keys={
            arm:signature_of_scaffold(make_world(first_seed,arm,setup))
            for arm in p["model"]["arm_order"]
        }
        assert scaffold_keys == {
            "A":targets["A"],"B":targets["B"],
            "A_reverse":targets["A"],"B_reverse":targets["B"],
            "C":targets["C"]
        }
        for seed in p["model"]["seed_list"]:
            reference=None
            for arm in p["model"]["arm_order"]:
                w=make_world(seed,arm,setup)
                initial=paired_initial_state(w)
                if reference is None:
                    reference=initial
                assert initial==reference, "not isoenergetic or paired initial backgrounds"
                row=take_measurements(w,p,arm,targets)
                row["density"]=density
                runs.append(row)
            print(f"{density} seed {seed} completed, five arms",flush=True)

        # Strict deterministic repeat from fresh construction, not cached.
        original=next(r for r in runs if r["density"]==density
                      and r["seed"]==first_seed and r["arm"]=="A")
        rerun=take_measurements(
            make_world(first_seed,"A",setup),p,"A",targets
        )
        assert rerun == {k:v for k,v in original.items() if k!="density"}
    assert len(runs)==160
    summary=analyse_runs(p,runs)
    record={
        "schema":"m6-3-1-accessibility-results-v1",
        "protocol_commit":"91d62e85b611a764f9ac34ea543025c38d071f23",
        "protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "sources":"Existing original M6 physics and existing M6.3-0 fixture helper only",
        "target_signatures":targets,
        "n_runs":len(runs),
        "per_run":runs,
        "summary":summary,
        "interpretation":"synthetic probe of candidate structural specificity, not reproduction",
        "limitations":p["analyses"]["reported_confounds"],
    }
    OUTPUT.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "runs":record["n_runs"],
        "signatures":targets,
        "summary":summary,
        "artifact":str(OUTPUT.relative_to(ROOT))
    },indent=2),flush=True)
    return record


if __name__=="__main__":
    run()
