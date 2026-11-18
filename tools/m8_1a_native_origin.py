"""M8.1a frozen-source experiment: unbound initial monomers, no planted polymer.

This observer never builds a chain or daughter. Only WorldM8.step() changes
chemistry after initial unbonded feedstock is distributed. Scientific NO_GO
outcomes are recorded as data and do not cause CI to fail.
"""
from __future__ import annotations

from collections import Counter
from hashlib import blake2b
from pathlib import Path
import json

from alife_m8.sandbox import HEIGHT, WIDTH, LAW_VERSION, WorldM8

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "campaigns" / "m8_1a"
PROTOCOL = BASE / "protocol.json"
OUT = BASE / "results.json"
REPORT = ROOT / "reports" / "M8_1a_results.md"


def protocol() -> dict:
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"] == "alife-m8-1a-unbound-monomer-origin-v1"
    assert p["status"] == "preregistered_before_implementation_or_outcomes"
    assert p["physics"]["law"] == LAW_VERSION
    assert p["frozen_campaign"]["modes"] == [
        "templated", "shuffled_identity", "no_template"
    ]
    assert p["frozen_campaign"]["ticks_per_world"] == 200
    assert p["frozen_campaign"]["seeds"]["count"] == 64
    return p


def site_hash(seed: int, purpose: str, x: int, y: int) -> int:
    """Unbiased deterministic hash ranking; independent of all M8 physical draws."""
    s = f"M8.1a-init-v1|{seed}|{purpose}|{x}|{y}".encode()
    return int.from_bytes(blake2b(s, digest_size=16).digest(), "little")


def initial_feedstock(seed: int) -> list[tuple[int, int, int]]:
    """Exactly 20 unbound particles, 10 of each species, uniformly drawn sites."""
    sites = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)]
    sites.sort(key=lambda q: (site_hash(seed, "position", *q), q[1], q[0]))
    selected = sites[:20]
    by_species = sorted(
        selected, key=lambda q: (site_hash(seed, "species", *q), q[1], q[0])
    )
    zero_sites = set(by_species[:10])
    return [(x, y, 0 if (x, y) in zero_sites else 1)
            for x, y in sorted(selected, key=lambda q: (q[1], q[0]))]


def initial_world(seed: int, mode: str) -> tuple[WorldM8, list[dict]]:
    w = WorldM8(seed=seed, mode=mode, template_sequence=None)
    initial = []
    for x, y, species in initial_feedstock(seed):
        assert w.bath[species] > 0
        w.bath[species] -= 1
        material_id = w._place(x, y, species)
        initial.append({
            "material_id": material_id, "x": x, "y": y, "species": species
        })
    assert w.tick == 0 and not w.B and not w.H
    assert len(w.particles) == 20
    assert Counter(p.species for p in w.particles.values()) == {0: 10, 1: 10}
    assert w.bath == {0: 30, 1: 30}
    assert w.initial_matter == 80 and w.initial_energy == 500
    w.check()
    return w, initial


def first_native_source(w: WorldM8, initial_ids: set[int],
                        native_B_form_pairs: set[tuple[int, int]]) -> dict | None:
    """First qualifying native four-site segment; scan deterministic (tick,y,x)."""
    for y in range(HEIGHT):
        for x in range(WIDTH - 3):
            ids = [w.grid.get((x + dx, y)) for dx in range(4)]
            if any(i is None or i not in initial_ids for i in ids):
                continue
            pairs = [w._key(a, b) for a, b in zip(ids, ids[1:])]
            if all(pair in w.B and pair in native_B_form_pairs for pair in pairs):
                return {
                    "tick": w.tick, "y": y, "x": x,
                    "material_ids": ids,
                    "sequence": "".join(str(w.particles[i].species) for i in ids),
                    "native_B_pairs": [list(pair) for pair in pairs],
                }
    return None


def B_component(w: WorldM8, start: int) -> set[int]:
    component = {start}
    waiting = [start]
    while waiting:
        item = waiting.pop()
        for neighbor in w.backbone_neighbors(item):
            if neighbor not in component:
                component.add(neighbor)
                waiting.append(neighbor)
    return component


def native_daughters(w: WorldM8, source: dict, initial_ids: set[int],
                     captures_by_material_id: dict[int, dict]) -> list[dict]:
    """Read actual aligned B4 products with native source->capture evidence."""
    results = []
    source_ids = source["material_ids"]
    for y in (source["y"] - 1, source["y"] + 1):
        if not 0 <= y < HEIGHT:
            continue
        ids = [w.grid.get((source["x"] + dx, y)) for dx in range(4)]
        if any(i is None or i in initial_ids for i in ids):
            continue
        if len(set(ids)) != 4:
            continue
        events = [captures_by_material_id.get(i) for i in ids]
        if any(e is None or e["tick"] <= source["tick"] or
               e["source_material_id"] != parent
               for e, parent in zip(events, source_ids)):
            continue
        pairs = [w._key(a, b) for a, b in zip(ids, ids[1:])]
        if not all(pair in w.B for pair in pairs):
            continue
        if B_component(w, ids[0]) != set(ids):
            continue
        if any(w._key(child, parent) in w.H
               for child in ids for parent in source_ids):
            continue
        seq = "".join(str(w.particles[i].species) for i in ids)
        results.append({
            "y": y, "material_ids": ids, "sequence": seq,
            "parent_sequence": source["sequence"],
            "exact_sequence_match": seq == source["sequence"],
            "native_B_pairs": [list(pair) for pair in pairs],
            "H_capture_events": events,
        })
    return results


def run_world(seed: int, mode: str, ticks: int = 200) -> dict:
    w, initial = initial_world(seed, mode)
    initial_ids = {p["material_id"] for p in initial}
    native_B_form_pairs: set[tuple[int, int]] = set()
    captures_by_id: dict[int, dict] = {}
    source = None
    best_streaks: dict[tuple[int, ...], int] = {}
    first_product = None
    first_informative = None
    checkpoint_hashes = []
    source_captures = 0

    for _ in range(ticks):
        old_len = len(w.events)
        w.step()  # real unchanged M8.0 physics + exact per-tick ledger assert
        for event in w.events[old_len:]:
            if event["kind"] == "B_form":
                native_B_form_pairs.add(tuple(event["pair"]))
            elif event["kind"] == "adsorb":
                captures_by_id[event["new_material_id"]] = event
                if source is not None and event["tick"] > source["tick"] and (
                    event["source_material_id"] in source["material_ids"]
                ):
                    source_captures += 1
        if source is None:
            source = first_native_source(w, initial_ids, native_B_form_pairs)

        current: dict[tuple[int, ...], tuple[int, dict]] = {}
        if source is not None and w.tick > source["tick"]:
            for daughter in native_daughters(w, source, initial_ids, captures_by_id):
                key = tuple(daughter["material_ids"])
                length = best_streaks.get(key, 0) + 1
                current[key] = (length, daughter)
                if length >= 20:
                    product = {
                        "first_persistent_tick": w.tick,
                        "survival_ticks": length, **daughter
                    }
                    if first_product is None:
                        first_product = product
                    if product["exact_sequence_match"] and first_informative is None:
                        first_informative = product
        best_streaks = {k: value[0] for k, value in current.items()}
        if w.tick in (1, 50, 100, 150, 200):
            checkpoint_hashes.append({"tick": w.tick, "hash": w.full_hash()})

    w.check()
    by_kind = Counter(e["kind"] for e in w.events)
    return {
        "seed": seed, "mode": mode, "ticks": ticks,
        "law_version": LAW_VERSION,
        "initial_state": {
            "feedstock": initial, "initial_B_count": 0, "initial_H_count": 0,
            "bath_after_feedstock": {0: 30, 1: 30},
            "matter_total": 80, "energy_total": 500,
        },
        "first_source": source,
        "first_persistent_material_product": first_product,
        "first_persistent_informative_product": first_informative,
        "captured_from_first_source_after_origin": source_captures,
        "event_counts": dict(by_kind),
        "all_native_physical_events": w.events,
        "checkpoint_hashes": checkpoint_hashes,
        "final_state": w.physical_metrics(),
        "integrity_passed": True,
    }


def summarize(records: list[dict], p: dict) -> dict:
    expected = list(range(610001, 610065))
    assert [r["seed"] for r in records] == expected
    modes = tuple(p["frozen_campaign"]["modes"])
    counts = {}
    for mode in modes:
        rows = [r["arms"][mode] for r in records]
        counts[mode] = {
            "source_worlds": sum(r["first_source"] is not None for r in rows),
            "material_product_worlds": sum(
                r["first_persistent_material_product"] is not None for r in rows
            ),
            "informative_product_worlds": sum(
                r["first_persistent_informative_product"] is not None for r in rows
            ),
            "source_H_captures": sum(
                r["captured_from_first_source_after_origin"] for r in rows
            ),
            "total_adsorptions": sum(
                r["event_counts"].get("adsorb", 0) for r in rows
            ),
            "total_B_forms": sum(
                r["event_counts"].get("B_form", 0) for r in rows
            ),
            "first_native_source_seed_ids": [
                r["seed"] for r in rows if r["first_source"] is not None
            ],
            "informative_product_seed_ids": [
                r["seed"] for r in rows
                if r["first_persistent_informative_product"] is not None
            ],
        }
    all_integrity = all(
        arm["integrity_passed"] for row in records for arm in row["arms"].values()
    )
    origin_pass = counts["no_template"]["source_worlds"] >= 12
    active = counts["templated"]["informative_product_worlds"]
    shuffled = counts["shuffled_identity"]["informative_product_worlds"]
    info_pass = active >= 4 and active - shuffled >= 3
    return {
        "scope": "NO planted template; M8.0 laws unchanged; NO life or multigeneration claim",
        "independent_seed_worlds": 64,
        "physical_worlds_including_controls": 192,
        "ticks_per_world": 200,
        "mode_world_counts": counts,
        "all_exact_material_energy_ledgers_passed": all_integrity,
        "frozen_decision_gates": {
            "physical_integrity": "PASS" if all_integrity else "INVALID",
            "origin_at_least_12_of_64_no_template": "PASS" if origin_pass else "NO_GO",
            "informational_active_at_least_4_and_delta_at_least_3": (
                "PASS" if info_pass else "NO_GO"
            ),
        },
        "interpretation": (
            "Native unbound feedstock originated some informative persistent products "
            "under declared M8.0 surface chemistry; not heredity or life."
            if origin_pass and info_pass
            else "Frozen M8.1a go/no-go threshold NOT fully met; do not seed-fish or "
                 "claim informational reproduction. Ordinary B polymer chemistry may occur."
        ),
    }


def execute() -> dict:
    p = protocol()
    s = p["frozen_campaign"]["seeds"]
    records = []
    for seed in range(s["start"], s["end_inclusive"] + 1):
        arms = {mode: run_world(seed, mode) for mode in p["frozen_campaign"]["modes"]}
        baseline = arms["no_template"]["initial_state"]
        assert all(arm["initial_state"] == baseline for arm in arms.values())
        records.append({"seed": seed, "arms": arms})
        if seed % 8 == 1:
            print(f"M8.1a audited {seed - s['start'] + 1}/64 source seeds", flush=True)
    summary = summarize(records, p)
    assert summary["all_exact_material_energy_ledgers_passed"]
    result = {"preregistered_protocol": p, "summary": summary, "all_worlds": records}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    c = summary["mode_world_counts"]
    lines = [
        "# M8.1a — Frozen unbound-monomer native-origin experiment",
        "",
        "This is static-surface chemistry, not digital life or three-generation heredity.",
        "No B/H bonds or parent polymer were planted at tick 0.",
        "M8.0 chemistry, energy/mass accounting and stochastic reaction rates unchanged.",
        "",
        "| Arm | Native origin worlds | Persistent material products | Exact informative products | Captures from first source |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for m in p["frozen_campaign"]["modes"]:
        x = c[m]
        lines.append(f"| {m} | {x['source_worlds']}/64 | "
                     f"{x['material_product_worlds']}/64 | "
                     f"{x['informative_product_worlds']}/64 | "
                     f"{x['source_H_captures']} |")
    lines.extend([
        "", "## Frozen gates", "",
        *[f"- **{k}**: {v}" for k, v in summary["frozen_decision_gates"].items()],
        "", "## Interpretation", "", summary["interpretation"], "",
        "All 192 actual event logs, initial feedstock IDs and hashes: "
        "`campaigns/m8_1a/results.json` CI artifact.", "",
        "No altered laws, no retroactive gate changes, all 64 source seeds included.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("M81A_FINAL_SUMMARY=" + json.dumps(summary, sort_keys=True), flush=True)
    return summary


if __name__ == "__main__":
    execute()
