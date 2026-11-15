"""P2 observation-only ancestry audit for the six particles of unfed-6101.

Records when the future template and prospective daughter first shared a
bonded ancestor. The case was selected *post hoc*. All interventions, if
proposed later, require their own frozen manifest before execution.

No physical-engine modification, no new RNG consumers, no detector changes.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from alife.config import load_config
from alife.structures import Tracker
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
M6 = ROOT / "campaigns/m6"
MANIFEST = ROOT / "campaigns/m6_2e/manifest.json"
OUT = ROOT / "campaigns/m6_2e/unfed_6101_ancestry.json"

TEMPLATE = (143, 290, 388, 414)
CHILD_SEED = (93, 245)
SIX = tuple(sorted(TEMPLATE + CHILD_SEED))
CUT_STEP = 771
JOINED_CHECK_STEP = 770
END_STEP = 3000


def component_for(tracker: Tracker, particle_id: int):
    return next(
        (s for s in tracker.active.values() if particle_id in s.particles),
        None,
    )


def common_ancestor_status(tracker: Tracker) -> dict:
    """All membership queries use particle ID, not lineage labels."""
    groups = {pid: component_for(tracker, pid) for pid in SIX}
    template_group = groups[TEMPLATE[0]]
    all_six = (
        template_group is not None and
        all(group is not None and
            group.structure_id == template_group.structure_id
            for group in groups.values())
    )
    shared_cross = any(
        groups[child] is not None and groups[parent] is not None and
        groups[child].structure_id == groups[parent].structure_id
        for child in CHILD_SEED for parent in TEMPLATE
    )
    seed_pair = (
        groups[CHILD_SEED[0]] is not None and
        groups[CHILD_SEED[1]] is not None and
        groups[CHILD_SEED[0]].structure_id == groups[CHILD_SEED[1]].structure_id
    )
    return {
        "shared_cross_component": shared_cross,
        "all_six_same_component": all_six,
        "seed_pair_same_component": seed_pair,
        "structure_ids": {
            str(pid): (groups[pid].structure_id if groups[pid] else None)
            for pid in SIX
        },
        "common_component": (
            {"structure_id": template_group.structure_id,
             "lineage_id": template_group.lineage_id,
             "size": template_group.size,
             "particles": sorted(template_group.particles),
             "signature": template_group.signature.key}
            if all_six else None
        ),
    }


class BondCollector:
    """Existing event_sink callback; counts all reactions, keeps those
    directly incident on the six monitored persistent particle identities."""
    def __init__(self) -> None:
        self.global_counts = Counter()
        self.incident = []

    def emit(self, event) -> None:
        if event.step >= CUT_STEP:
            return
        self.global_counts[event.kind] += 1
        if event.id_a in SIX or event.id_b in SIX:
            self.incident.append({
                "pre_step": event.step,
                "post_step": event.step + 1,
                "kind": event.kind,
                "particles": [event.id_a, event.id_b],
                "energy": event.energy,
                "dissipated": event.dissipated,
                "catalyzed": event.catalyzed,
            })


def contiguous_episodes(observations: list[dict], property_name: str) -> list[dict]:
    """Consecutive true intervals, inclusive; no smoothing or resampling."""
    episodes = []
    start = None
    for obs in observations:
        if obs[property_name] and start is None:
            start = obs["step"]
        if not obs[property_name] and start is not None:
            episodes.append({"first": start, "last": obs["step"] - 1})
            start = None
    if start is not None:
        episodes.append({"first": start, "last": observations[-1]["step"]})
    return episodes


def record_state(world: World, tracker: Tracker) -> dict:
    status = common_ancestor_status(tracker)
    store = world.store
    status.update({
        "step": world.step,
        "rng_draws": world.rng.draws,
        "bonds_among_six": [
            [store.ids[a], store.ids[b]]
            for (a, b) in sorted(store.bonds)
            if store.ids[a] in SIX and store.ids[b] in SIX
        ],
        "positions": {
            str(pid): [
                store.xs[store.index_of(pid)],
                store.ys[store.index_of(pid)],
            ] for pid in SIX
        },
    })
    return status


def run(output: Path = OUT) -> dict:
    manifest = json.loads(MANIFEST.read_text())
    item = next(r for r in manifest["runs"] if r["id"] == "unfed-6101")
    config = load_config(M6 / item["config"])
    assert config.hash() == item["config_hash"]
    world = World.create(config)
    tracker = Tracker()
    tracker.observe(world)
    collector = BondCollector()
    world.event_sink = collector

    timeline = [record_state(world, tracker)]
    rng_observer_unchanged = True

    def observe(current: World) -> None:
        nonlocal rng_observer_unchanged
        before = current.rng.draws
        tracker.observe(current)
        timeline.append(record_state(current, tracker))
        rng_observer_unchanged &= current.rng.draws == before

    world.advance(CUT_STEP, observer=observe)
    assert len(timeline) == CUT_STEP + 1
    step770, step771 = timeline[JOINED_CHECK_STEP], timeline[CUT_STEP]
    if not step770["all_six_same_component"]:
        raise AssertionError("expected common precursor is not present at step 770")
    assert not step771["all_six_same_component"]
    assert [93, 414] in step770["bonds_among_six"]
    assert [93, 414] not in step771["bonds_among_six"]

    episodes_all = contiguous_episodes(timeline, "all_six_same_component")
    episodes_cross = contiguous_episodes(timeline, "shared_cross_component")
    episodes_seed_pair = contiguous_episodes(timeline, "seed_pair_same_component")
    assert episodes_all and episodes_all[-1]["last"] == JOINED_CHECK_STEP

    # No observer is attached after the split. Full M6 hash must still match.
    world.advance(END_STEP - CUT_STEP)
    world.check()
    match = world.state_hash_full() == item["expected_world_hash"]
    out = {
        "schema": "unfed6101-material-ancestry-v1",
        "epistemic_status": "observational post-hoc single case",
        "run": "unfed-6101",
        "observed_ticks": [0, CUT_STEP],
        "world_hash_matches_original_M6": match,
        "rng_untouched_by_observer": rng_observer_unchanged,
        "six_particle_ids": list(SIX),
        "material_groups": {
            "future_template": list(TEMPLATE),
            "future_child_seed": list(CHILD_SEED),
        },
        "first_shared_cross_component": episodes_cross[0]["first"] if episodes_cross else None,
        "first_all_six_shared_component": episodes_all[0]["first"],
        "all_six_episodes": episodes_all,
        "any_cross_component_episodes": episodes_cross,
        "child_seed_pair_episodes": episodes_seed_pair,
        "prior_chemical_events_incident_to_six": collector.incident,
        "global_bond_event_counts_through_cut": dict(sorted(collector.global_counts.items())),
        "precursor_770": step770,
        "split_771": step771,
        "timeline_flags": [
            {
                "step": t["step"],
                "shared_cross_component": t["shared_cross_component"],
                "all_six_same_component": t["all_six_same_component"],
                "seed_pair_same_component": t["seed_pair_same_component"],
            }
            for t in timeline
        ],
        "interpretation": (
            "Material common ancestry and an associated split are observed; "
            "these are not evidence of template-mediated reproduction."
        ),
        "next_phase": (
            "Any intervention date, group, controls, efficacy measure and "
            "decision rule must be fixed in a separate manifest commit "
            "before counterfactual runs are inspected."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, indent=2) + "\n")
    summary = {
        "origin_first_shared_cross": out["first_shared_cross_component"],
        "origin_first_all_six": out["first_all_six_shared_component"],
        "last_all_six_episode": episodes_all[-1],
        "cross_connection_episodes": episodes_cross,
        "events_incident_to_six": len(collector.incident),
        "hash_match": match,
        "observer_rng_unchanged": rng_observer_unchanged,
        "output": str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),
    }
    print(json.dumps(summary, indent=2))
    if not match or not rng_observer_unchanged:
        raise SystemExit("ERROR: observational run changed original trajectory")
    return out


if __name__ == "__main__":
    run()
