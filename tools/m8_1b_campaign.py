"""M8.1b preregistered single-new-law local-hop trial.

The only physical change vs M8.0 is movement of completely B/H-unbound
monomers at cost of one finite energy unit. This runner NEVER constructs
a template, product or parent. All primary outcomes and nulls are recorded.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from alife_m8.sandbox import WorldM8, LAW_VERSION as M80_LAW
from alife_m8.hopping_v1 import WorldM81b, HOP_LAW_VERSION
from tools.m8_1a_native_origin import (
    initial_feedstock, first_native_source, native_daughters,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "campaigns/m8_1b"
PFILE = BASE / "protocol.json"
OUT = BASE / "results.json"
REPORT = ROOT / "reports/M8_1b_results.md"

MODES = ("static_templated", "hop_templated", "hop_shuffled", "hop_no_template")
SEEDS = range(620001, 620065)
TICKS = 240
CHEMISTRY = {
    "static_templated": "templated",
    "hop_templated": "templated",
    "hop_shuffled": "shuffled_identity",
    "hop_no_template": "no_template",
}


def protocol() -> dict:
    d = json.loads(PFILE.read_text(encoding="utf-8"))
    assert d["schema"] == "alife-m8-1b-single-local-hop-v1"
    assert d["status"] == "frozen_before_m8_1b_physics_implementation_or_result"
    assert d["physics"]["new_law_version"] == HOP_LAW_VERSION
    assert d["physics"]["inherited_law"] == M80_LAW
    assert d["physics"]["attempt_probability"] == 0.25
    assert d["physics"]["hop_energy_cost"] == 1
    assert d["frozen_experiment"]["seed_start"] == SEEDS.start
    assert d["frozen_experiment"]["seed_end_inclusive"] == SEEDS.stop - 1
    assert d["frozen_experiment"]["modes"] == list(MODES)
    assert d["frozen_experiment"]["horizon_ticks"] == TICKS
    return d


def initial_world(seed: int, arm: str):
    assert arm in MODES
    base_type = WorldM8 if arm == "static_templated" else WorldM81b
    w = base_type(seed=seed, mode=CHEMISTRY[arm], template_sequence=None)
    feedstock = initial_feedstock(seed)
    initial = []
    for x, y, species in feedstock:
        w.bath[species] -= 1
        identifier = w._place(x, y, species)
        initial.append({
            "material_id": identifier, "x": x, "y": y, "species": species
        })
    assert len(initial) == 20 and len(w.particles) == 20
    assert w.bath == {0: 30, 1: 30}
    assert w.initial_matter == 80 and w.initial_energy == 500
    assert not w.B and not w.H
    assert sorted(p.species for p in w.particles.values()).count(0) == 10
    assert sorted(p.species for p in w.particles.values()).count(1) == 10
    w.check()
    return w, initial


def intact_native_source(w, source: dict) -> bool:
    if source is None:
        return False
    ids = source["material_ids"]
    if any(w.grid.get((source["x"] + dx, source["y"])) != parent
           for dx, parent in enumerate(ids)):
        return False
    if not all(w._key(a, b) in w.B for a, b in zip(ids, ids[1:])):
        return False
    return True


def free_four_corridor(w, source: dict) -> bool:
    """Only a LIVE B-connected parent can be credited with an empty corridor."""
    if not intact_native_source(w, source):
        return False
    for y in (source["y"] - 1, source["y"] + 1):
        if not 0 <= y < 5:
            continue
        if all((source["x"] + dx, y) not in w.grid for dx in range(4)):
            return True
    return False


def strictly_traced_daughters(w, source: dict, initial_ids: set[int],
                             captures: dict[int, dict]) -> list[dict]:
    if not intact_native_source(w, source):
        return []
    result = []
    for daughter in native_daughters(w, source, initial_ids, captures):
        ids = daughter["material_ids"]
        y = daughter["y"]
        for dx, ident in enumerate(ids):
            e = captures[ident]
            if (e["x"], e["y"]) != (source["x"] + dx, y):
                break
            if w.particles[ident].birth_tick != e["tick"]:
                break
        else:
            result.append(daughter)
    return result


def run_world(seed: int, arm: str, ticks: int = TICKS) -> dict:
    w, initial = initial_world(seed, arm)
    original_ids = {p["material_id"] for p in initial}
    native_B_pairs = set()
    captures_by_id = {}
    source = None
    corridor_at_birth = False
    first_corridor_tick = None
    live_corridor_ticks = 0
    live_source_ticks = 0
    source_captures = 0
    first_product = None
    first_informative = None
    prior_streaks = {}
    snapshots = []

    for _ in range(ticks):
        mark = len(w.events)
        w.step()
        new = w.events[mark:]
        for e in new:
            if e["kind"] == "B_form":
                native_B_pairs.add(tuple(e["pair"]))
            elif e["kind"] == "adsorb":
                captures_by_id[e["new_material_id"]] = e
                if source is not None and e["tick"] > source["tick"] and (
                        e["source_material_id"] in source["material_ids"]):
                    source_captures += 1
            elif e["kind"] == "hop":
                assert arm != "static_templated"
                assert e["energy_cost"] == 1
                assert (abs(e["from_x"] - e["to_x"]) +
                        abs(e["from_y"] - e["to_y"]) == 1)
                assert e["material_id"] in w.particles

        if source is None:
            source = first_native_source(w, original_ids, native_B_pairs)
            if source is not None:
                corridor_at_birth = free_four_corridor(w, source)

        if source is not None:
            live = intact_native_source(w, source)
            if live:
                live_source_ticks += 1
            corridor = free_four_corridor(w, source)
            if corridor:
                live_corridor_ticks += 1
                if first_corridor_tick is None:
                    first_corridor_tick = w.tick

        current_streaks = {}
        if source is not None and w.tick > source["tick"]:
            for daughter in strictly_traced_daughters(
                w, source, original_ids, captures_by_id
            ):
                label = tuple(daughter["material_ids"])
                count = prior_streaks.get(label, 0) + 1
                current_streaks[label] = count
                if count >= 20:
                    record = {"first_persistent_tick": w.tick,
                              "observed_consecutive_ticks": count, **daughter}
                    if first_product is None:
                        first_product = record
                    if record["exact_sequence_match"] and first_informative is None:
                        first_informative = record
        prior_streaks = current_streaks
        if w.tick in (1, 50, 100, 150, 200, 240):
            snapshots.append({
                "tick": w.tick, "hash": w.full_hash(),
                "matter": len(w.particles) + sum(w.bath.values()),
                "energy": w.free_energy + sum(w.B.values()) + sum(w.H.values()) + w.dissipated,
                "occupied_sites": len(w.grid),
            })
    by_kind = Counter(e["kind"] for e in w.events)
    w.check()
    assert by_kind.get("hop", 0) == 0 or arm != "static_templated"
    return {
        "seed": seed, "arm": arm, "ticks": ticks,
        "law": M80_LAW if arm == "static_templated" else HOP_LAW_VERSION,
        "initial": {
            "feedstock": initial,
            "B0": 0, "H0": 0, "bath0": {0: 30, 1: 30},
            "total_matter": 80, "total_energy": 500,
        },
        "first_source": source,
        "first_source_corridor_free_at_birth": corridor_at_birth,
        "first_source_live_corridor_seen_at_or_after_birth": first_corridor_tick is not None,
        "first_source_live_corridor_first_tick": first_corridor_tick,
        "first_source_live_corridor_ticks": live_corridor_ticks,
        "first_source_live_B_chain_ticks": live_source_ticks,
        "first_source_adsorptions_after_birth": source_captures,
        "first_strict_persistent_material_product": first_product,
        "first_strict_informative_product": first_informative,
        "native_event_counts": dict(by_kind),
        "all_real_native_events": w.events,
        "snapshots": snapshots,
        "final_physical_metrics": w.physical_metrics(),
        "full_physical_ledger_passed_every_tick": True,
    }


def summarize(records: list[dict], p: dict) -> dict:
    assert [r["seed"] for r in records] == list(SEEDS)
    groups = {}
    for arm in MODES:
        entries = [r["arms"][arm] for r in records]
        groups[arm] = {
            "independent_seed_worlds": len(entries),
            "native_first_B4_source_worlds": sum(
                e["first_source"] is not None for e in entries
            ),
            "source_corridor_empty_at_birth_worlds": sum(
                e["first_source_corridor_free_at_birth"] for e in entries
            ),
            "source_live_corridor_available_at_or_after_birth_worlds": sum(
                e["first_source_live_corridor_seen_at_or_after_birth"]
                for e in entries
            ),
            "total_source_live_corridor_ticks": sum(
                e["first_source_live_corridor_ticks"] for e in entries
            ),
            "source_H_capture_total": sum(
                e["first_source_adsorptions_after_birth"] for e in entries
            ),
            "persistent_material_product_worlds": sum(
                e["first_strict_persistent_material_product"] is not None
                for e in entries
            ),
            "persistent_informative_product_worlds": sum(
                e["first_strict_informative_product"] is not None
                for e in entries
            ),
            "physical_hops": sum(e["native_event_counts"].get("hop", 0) for e in entries),
            "total_adsorptions": sum(
                e["native_event_counts"].get("adsorb", 0) for e in entries
            ),
            "total_B_formations": sum(
                e["native_event_counts"].get("B_form", 0) for e in entries
            ),
        }
    source_static = groups["static_templated"]["source_live_corridor_available_at_or_after_birth_worlds"]
    source_hop = groups["hop_templated"]["source_live_corridor_available_at_or_after_birth_worlds"]
    info_active = groups["hop_templated"]["persistent_informative_product_worlds"]
    info_shuffled = groups["hop_shuffled"]["persistent_informative_product_worlds"]
    integrity = all(
        item["full_physical_ledger_passed_every_tick"]
        for row in records for item in row["arms"].values()
    )
    return {
        "status": "pre-registered single-law M8.1b research",
        "physical_worlds": 256, "independent_numeric_seeds": 64,
        "ticks_per_world": TICKS,
        "groups": groups,
        "gates": {
            "physics_integrity": "PASS" if integrity else "INVALID",
            "mobility_corridor_effect": (
                "PASS" if source_hop >= 8 and source_hop - source_static >= 5
                else "NO_GO"
            ),
            "informative_persistent_offspring": (
                "PASS" if info_active >= 3 and info_active - info_shuffled >= 3
                else "NO_GO"
            ),
        },
        "limitations": "No metabolism, no 3-generation heredity, no artificial-life claim; isolated hopping only, bonded particles immobilized, no desorption."
    }


def execute():
    p = protocol()
    data = []
    for seed in SEEDS:
        arms = {arm: run_world(seed, arm) for arm in MODES}
        expected_start = arms["static_templated"]["initial"]
        assert all(x["initial"] == expected_start for x in arms.values())
        data.append({"seed": seed, "arms": arms})
        if (seed - SEEDS.start + 1) % 8 == 0:
            print(f"M81B_PROGRESS={seed - SEEDS.start + 1}/64", flush=True)
    result = summarize(data, p)
    assert result["gates"]["physics_integrity"] == "PASS"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "frozen_protocol": p, "summary": result, "all_256_physical_worlds": data
    }, indent=2) + "\n", encoding="utf-8")
    g = result["groups"]
    lines = [
        "# M8.1b — One new finite-energy isolated-monomer hop mechanism",
        "",
        "**Frozen protocol before implementation/outcomes.** New numeric seed sample.",
        "Original M8.0 chemistry untouched. M8.1a original NO_GO unchanged.",
        "256 worlds, four matched arms, 64 independent seed worlds, 240 ticks each.",
        "",
        "| Metric (world-level unless stated otherwise) | Static active | Hop active | Hop shuffled | Hop no-template |",
        "|---|---:|---:|---:|---:|",
    ]
    metrics = [
        ("Native first B4", "native_first_B4_source_worlds"),
        ("4-cell corridor free at source birth", "source_corridor_empty_at_birth_worlds"),
        ("4-cell corridor available while parent intact", "source_live_corridor_available_at_or_after_birth_worlds"),
        ("Source H captures (events, not worlds)", "source_H_capture_total"),
        ("Strict persistent material daughter", "persistent_material_product_worlds"),
        ("Strict informative persistent daughter", "persistent_informative_product_worlds"),
        ("Native physical hops", "physical_hops"),
        ("All adsorption events", "total_adsorptions"),
        ("All native B formations", "total_B_formations"),
    ]
    for label, field in metrics:
        lines.append("| " + label + " | " + " | ".join(str(g[m][field]) for m in MODES) + " |")
    lines.extend([
        "", "## Frozen gates",
        *[f"- **{k}**: {v}" for k,v in result["gates"].items()],
        "", "## Scope",
        "This is a stationary-lattice surface chemistry model with **one added motion law**, "
        "not a biological cell, metabolism, multicellular lineage or self-replicating life.",
        "Any failure is a **scientific NO_GO**, not a failed software test; "
        "do not revise seeds, thresholds, probability or horizon posthoc.",
        "Raw reaction + hop event trails, initial IDs and seed-level nulls: "
        "`campaigns/m8_1b/results.json` CI artifact.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("M81B_FINAL_SUMMARY=" + json.dumps(result, sort_keys=True), flush=True)
    return result


if __name__ == "__main__":
    execute()
