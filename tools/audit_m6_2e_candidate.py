"""Targeted, read-only reconstruction of the sole M6.2-E signature match.

Runs unfed-6101 using the preregistered M6 configuration. No world laws are
changed. Records the child and template identity, geometry, graph signature
and copied-form persistence over time. This is NOT a causal experiment.
"""

from __future__ import annotations

import json
from pathlib import Path

from alife.config import load_config
from alife.replication_v2 import ProgressiveDetector
from alife.structures import Tracker
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
M6 = ROOT / "campaigns" / "m6"
M62 = ROOT / "campaigns" / "m6_2e"
RUN_ID = "unfed-6101"


def _snapshot(world, tracked):
    if tracked is None:
        return None
    store = world.store
    return {
        "structure_id": tracked.structure_id,
        "lineage_id": tracked.lineage_id,
        "born_step": tracked.born_step,
        "size": tracked.size,
        "signature": tracked.signature.key,
        "exact": tracked.signature.exact,
        "parents": tracked.parents,
        "particles": [
            {
                "id": identifier,
                "species": world.species_names[store.species[store.index_of(identifier)]],
                "position": [
                    store.xs[store.index_of(identifier)],
                    store.ys[store.index_of(identifier)],
                ],
            }
            for identifier in sorted(tracked.particles)
        ],
    }


def main() -> None:
    manifest = json.loads((M62 / "manifest.json").read_text(encoding="utf-8"))
    run = next(entry for entry in manifest["runs"] if entry["id"] == RUN_ID)
    world = World.create(load_config(M6 / run["config"]))
    tracker = Tracker()
    detector = ProgressiveDetector(**manifest["criteria"])
    matches = []
    observed_matches = set()

    def observe(current):
        tracker.observe(current)
        detector.observe(current, tracker)
        for candidate in detector.candidates:
            if candidate.matched_step is not None and candidate.child not in observed_matches:
                observed_matches.add(candidate.child)
                template = tracker.active.get(candidate.template)
                child = tracker.active.get(candidate.child)
                matches.append({
                    "birth_step": candidate.birth_step,
                    "matched_step": candidate.matched_step,
                    "child_id": candidate.child,
                    "template_id": candidate.template,
                    "target_signature": candidate.target_key,
                    "target_size": candidate.target_size,
                    "birth_distance": candidate.distance,
                    "ambiguous_templates": candidate.ambiguous_templates,
                    "template_at_match": _snapshot(current, template),
                    "child_at_match": _snapshot(current, child),
                    "continuous_form_checks": [],
                })
        for match in matches:
            if match["matched_step"] <= current.step <= match["matched_step"] + detector.persist_steps:
                child = tracker.active.get(match["child_id"])
                match["continuous_form_checks"].append({
                    "step": current.step,
                    "alive": child is not None,
                    "matches_target": child is not None
                    and child.signature.exact
                    and child.signature.key == match["target_signature"],
                    "signature": child.signature.key if child is not None else None,
                })

    observe(world)
    world.advance(3000, observer=observe)

    candidates = {c.child: c for c in detector.candidates}
    for match in matches:
        candidate = candidates[match["child_id"]]
        match["persistent_with_corrected_detector"] = candidate.persistent
        match["discarded_reason"] = candidate.discarded
        child = match["child_at_match"]
        template = match["template_at_match"]
        if child is not None and template is not None:
            match["shared_particle_ids_at_match"] = sorted(
                set(p["id"] for p in child["particles"]) &
                set(p["id"] for p in template["particles"])
            )

    report = {
        "run": RUN_ID,
        "world_hash_matches_m6": world.state_hash_full() == run["expected_world_hash"],
        "world_hash": world.state_hash_full(),
        "detector_summary": detector.summary(),
        "signature_matches": matches,
        "interpretation": (
            "Observational association only; proximity and structural identity "
            "do not establish that the template caused assembly."
        ),
    }
    output = M62 / "unfed_6101_audit.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({\n        "run": RUN_ID,\n        "world_hash_matches_m6": report["world_hash_matches_m6"],\n        "summary": {key: detector.summary()[key] for key in ("candidates", "matched", "persistent", "classified")},\n        "matches": [{\n            "birth_step": m["birth_step"],\n            "matched_step": m["matched_step"],\n            "child_id": m["child_id"],\n            "template_id": m["template_id"],\n            "signature": m["target_signature"],\n            "persistent": m["persistent_with_corrected_detector"],\n            "continuous_checks": len(m["continuous_form_checks"]),\n            "shared_particle_ids_at_match": m.get("shared_particle_ids_at_match"),\n        } for m in matches],\n    }, indent=2))
    if not report["world_hash_matches_m6"]:
        raise SystemExit("ERROR: world diverged from preregistered M6")


if __name__ == "__main__":
    main()
