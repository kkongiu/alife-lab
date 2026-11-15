"""M6.2-E P1: non-invasive particle/bond timeline of unfed-6101.

Replay the ORIGINAL M6 world with the original config and seed. Existing
detectors, physical laws and preregistered results are not modified.
Events are emitted by the existing world.event_sink hook; observer does not
call RNG or mutate the world. Event.step is the old/pre-advance tick; the
corresponding post-step observation is event.step+1.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from alife.config import load_config
from alife.replication import _distance
from alife.structures import Tracker
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
M6 = ROOT / "campaigns" / "m6"
MANIFEST = ROOT / "campaigns" / "m6_2e" / "manifest.json"
DEFAULT_OUT = ROOT / "campaigns" / "m6_2e" / "unfed_6101_trace.json"

START_STEP = 770
END_STEP = 846
BIRTH_STEP = 792
MATCH_STEP = 835
PERSIST_STEP = 845
TEMPLATE_STRUCTURE_ID = 850
CHILD_STRUCTURE_ID = 872
TEMPLATE_IDS = (143, 290, 388, 414)
CHILD_BIRTH_IDS = (93, 245)
CHILD_MATCH_IDS = (40, 93, 245, 477)
WATCH_IDS = tuple(sorted(set(TEMPLATE_IDS + CHILD_MATCH_IDS)))
EXPECTED_SIGNATURE = "T:(S0:(S0:(S0:(S0:))))"
LOCAL_RADIUS = 3


def _xy(store, identity: int) -> tuple[int, int]:
    i = store.index_of(identity)
    return store.xs[i], store.ys[i]


def _distance_positions(a: tuple[int, int], b: tuple[int, int],
                        width: int, height: int, periodic: bool) -> int:
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    if periodic:
        dx, dy = min(dx, width - dx), min(dy, height - dy)
    return dx + dy


def structure_record(world: World, structure) -> dict | None:
    """Tracked component snapshot; tracker ID does not signify parenthood."""
    if structure is None:
        return None
    s = world.store
    ids = sorted(structure.particles)
    return {
        "structure_id": structure.structure_id,
        "lineage_id": structure.lineage_id,
        "born_step": structure.born_step,
        "signature": structure.signature.key,
        "exact": structure.signature.exact,
        "size": structure.size,
        "parents": list(structure.parents),
        "particles": ids,
        "bonds": [
            [s.ids[a], s.ids[b]]
            for (a, b) in sorted(s.bonds)
            if s.ids[a] in structure.particles and s.ids[b] in structure.particles
        ],
    }


def structure_containing(tracker: Tracker, ids: tuple[int, ...]):
    """Require all requested IDs in the SAME bonded component."""
    wanted = set(ids)
    for structure in tracker.active.values():
        if wanted <= structure.particles:
            return structure
    return None


def snapshot(world: World, tracker: Tracker, event_counts: Counter,
             selected_events: list[dict]) -> dict:
    s = world.store
    by_id = {
        identity: {
            "species": world.species_names[s.species[s.index_of(identity)]],
            "position": list(_xy(s, identity)),
            "energy": s.energy[s.index_of(identity)],
            "degree": s.degree[s.index_of(identity)],
        }
        for identity in WATCH_IDS
    }

    component = structure_containing(tracker, CHILD_BIRTH_IDS)
    template = tracker.active.get(TEMPLATE_STRUCTURE_ID)
    child = tracker.active.get(CHILD_STRUCTURE_ID)
    surroundings = []
    for i, identity in enumerate(s.ids):
        if identity in WATCH_IDS:
            continue
        xy = (s.xs[i], s.ys[i])
        nearest = min(
            _distance_positions(xy, _xy(s, other), s.width, s.height, world.periodic)
            for other in WATCH_IDS
        )
        if nearest <= LOCAL_RADIUS:
            surroundings.append({
                "id": identity,
                "species": world.species_names[s.species[i]],
                "position": [xy[0], xy[1]],
                "distance_to_watch": nearest,
                "degree": s.degree[i],
            })

    separation = None
    if template is not None and component is not None and (
        not template.particles.intersection(component.particles)
    ):
        separation = _distance(s, template.particles, component.particles, world.periodic)

    return {
        "step": world.step,
        "rng_draws": world.rng.draws,
        "rng_fingerprint": world.rng.fingerprint(),
        "energy_total": world.energy(),
        "injected": world.injected,
        "dissipated": world.dissipated,
        "unabsorbed": world.unabsorbed,
        "watch_particles": by_id,
        "nearby_particles": surroundings,
        "template": structure_record(world, template),
        "child": structure_record(world, child),
        "component_containing_child_birth_ids": structure_record(world, component),
        "template_child_min_distance": separation,
        "bond_events_in_this_transition": dict(sorted(event_counts.items())),
        "local_bond_events": selected_events,
    }


class ReadOnlyEventCollector:
    """Records every chemical event count; retains only local/incident detail."""

    def __init__(self, world: World) -> None:
        self.world = world
        self.present_watch_ids = tuple(i for i in WATCH_IDS if i in world.store.ids)
        self.counts: dict[int, Counter] = {}
        self.selected: dict[int, list[dict]] = {}

    def emit(self, event) -> None:
        observed_step = event.step + 1
        if not START_STEP <= observed_step <= END_STEP:
            return
        self.counts.setdefault(observed_step, Counter())[event.kind] += 1
        s = self.world.store
        endpoints = (event.id_a, event.id_b)
        positions = (_xy(s, endpoints[0]), _xy(s, endpoints[1]))
        incident = any(identifier in self.present_watch_ids for identifier in endpoints)
        nearest = min(
            (_distance_positions(pos, _xy(s, watched), s.width, s.height, self.world.periodic)
             for pos in positions for watched in self.present_watch_ids),
            default=s.width + s.height + 1,
        )
        if not (incident or nearest <= LOCAL_RADIUS):
            return
        self.selected.setdefault(observed_step, []).append({
            "event_step_pre_advance": event.step,
            "observed_step_post_advance": observed_step,
            "kind": event.kind,
            "id_a": event.id_a,
            "id_b": event.id_b,
            "positions_at_event": [list(p) for p in positions],
            "catalyzed": bool(event.catalyzed),
            "energy": event.energy,
            "dissipated": event.dissipated,
            "incident_to_watch": incident,
            "distance_to_watch_at_event": nearest,
            "rng_draws_at_event": self.world.rng.draws,
        })


def baseline_signature_frequency(path: Path) -> dict:
    """Events and IDs are reported separately, not treated as independent births."""
    events = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry["step"] < BIRTH_STEP and entry["signature"] == EXPECTED_SIGNATURE:
                events.append(entry)
    return {
        "signature": EXPECTED_SIGNATURE,
        "events_before_child_birth": len(events),
        "distinct_structure_ids": len({e["structure"] for e in events}),
        "event_kinds": dict(sorted(Counter(e["kind"] for e in events).items())),
        "independent_births": None,
        "note": "Tracker ID is not independent reproduction; this is a frequency-of-background measure.",
    }


def run(out: Path = DEFAULT_OUT) -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    run_spec = next(item for item in manifest["runs"] if item["id"] == "unfed-6101")
    config = load_config(M6 / run_spec["config"])
    assert config.hash() == run_spec["config_hash"]
    world = World.create(config)
    collector = ReadOnlyEventCollector(world)
    world.event_sink = collector
    tracker = Tracker()
    tracker.observe(world)
    timeline: list[dict] = []
    no_observer_rng_draws = True

    def observe(w: World) -> None:
        nonlocal no_observer_rng_draws
        before = w.rng.draws
        tracker.observe(w)
        if START_STEP <= w.step <= END_STEP:
            timeline.append(snapshot(
                w, tracker, collector.counts.pop(w.step, Counter()),
                collector.selected.pop(w.step, []),
            ))
        no_observer_rng_draws &= w.rng.draws == before

    # Original continuous trajectory, observer attached from step 0 so that
    # M4 structure identities agree with the stored M6 lineage data.
    world.advance(END_STEP, observer=observe)
    assert len(timeline) == END_STEP - START_STEP + 1
    at = {item["step"]: item for item in timeline}
    assert at[BIRTH_STEP]["child"]["structure_id"] == CHILD_STRUCTURE_ID
    assert at[BIRTH_STEP]["child"]["particles"] == list(CHILD_BIRTH_IDS)
    assert at[MATCH_STEP]["child"]["signature"] == EXPECTED_SIGNATURE
    assert at[MATCH_STEP]["child"]["particles"] == list(CHILD_MATCH_IDS)
    assert at[PERSIST_STEP]["child"]["signature"] == EXPECTED_SIGNATURE
    assert at[MATCH_STEP]["template"]["signature"] == EXPECTED_SIGNATURE
    assert not set(at[MATCH_STEP]["child"]["particles"]).intersection(
        at[MATCH_STEP]["template"]["particles"]
    )

    # The trace is observational: continuing without the observer must
    # reproduce the originally frozen world hash at step 3000.
    world.advance(3000 - END_STEP)
    world.check()
    final_hash = world.state_hash_full()
    hash_match = final_hash == run_spec["expected_world_hash"]
    report = {
        "schema": "unfed6101-particle-event-trace-v1",
        "run": "unfed-6101",
        "range_inclusive": [START_STEP, END_STEP],
        "reference_steps": {
            "template_first_recorded": 771,
            "child_birth": BIRTH_STEP, "signature_match": MATCH_STEP,
            "persist_check": PERSIST_STEP,
        },
        "world_hash_matches_frozen_M6": hash_match,
        "final_state_hash": final_hash,
        "expected_state_hash": run_spec["expected_world_hash"],
        "no_rng_draws_in_observer": no_observer_rng_draws,
        "background_signature_frequency": baseline_signature_frequency(
            ROOT / "runs" / "m6" / "unfed" / "seed-6101" / "lineage.jsonl"
        ),
        "transition_event_step_semantics": (
            "BondEvent.step=t is emitted during world.advance from t to t+1; "
            "step=t+1 snapshot records the post-transition state."
        ),
        "timeline": timeline,
        "limitations": [
            "Observing an incident bond event or proximity does not prove templated copying.",
            "Structure IDs track overlapping particle identity, not causal ancestry.",
            "No physical world law, probability, RNG or preregistered detector is modified.",
        ],
        "verdict": "observational_trace_only_causal_replication_not_demonstrated",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = {
        "run": report["run"],
        "steps_recorded": len(timeline),
        "hash_match": hash_match,
        "observer_rng_unchanged": no_observer_rng_draws,
        "template_first_recorded": 771,
        "child_birth": BIRTH_STEP,
        "child_match": MATCH_STEP,
        "local_bond_events": sum(len(r["local_bond_events"]) for r in timeline),
        "local_event_details": [
            {"post_step": t["step"], "kind": e["kind"],
             "bond_ids": [e["id_a"], e["id_b"]],
             "incident_to_target": e["incident_to_watch"],
             "nearest_watch_distance": e["distance_to_watch_at_event"]}
            for t in timeline for e in t["local_bond_events"]
        ],
        "key_steps": [
            {"step": step,
             "template_exists": at[step]["template"] is not None,
             "child_component_size": (
                 at[step]["component_containing_child_birth_ids"]["size"]
                 if at[step]["component_containing_child_birth_ids"] else None),
             "child_component_bonds": (
                 at[step]["component_containing_child_birth_ids"]["bonds"]
                 if at[step]["component_containing_child_birth_ids"] else []),
             "template_child_distance": at[step]["template_child_min_distance"]}
            for step in (770, 771, 792, 800, 835, 845)
        ],
        "background_structure_ids": report["background_signature_frequency"]["distinct_structure_ids"],
        "output": str(out.relative_to(ROOT)) if out.is_relative_to(ROOT) else str(out),
    }
    print(json.dumps(summary, indent=2))
    if not hash_match or not no_observer_rng_draws:
        raise SystemExit("FAIL: observer changed RNG or world hash")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    run(args.out)


if __name__ == "__main__":
    main()
