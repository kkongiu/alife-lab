"""M8.1a post-hoc diagnostic: replay FROZEN EVENT RECORDS, not physical worlds.

No import of WorldM8, no new random seeds, no WorldM8.step calls, no alteration
of preregistered scientific gates. Each physical trajectory is reconstructed
only from archived material positions + native B/H/adsorption events.

Source artifact GitHub Actions #44412124197 / artifact #14476369876.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "campaigns/m8_1a/results.json"
OUTPUT = ROOT / "campaigns/m8_1a/posthoc_diagnostic.json"
REPORT = ROOT / "reports/M8_1a_posthoc_diagnostic.md"
MODES = ("templated", "shuffled_identity", "no_template")
WIDTH, HEIGHT, TICKS = 10, 5, 200


def key(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def first_original_four(grid, material, bonds, original, native_b):
    for y in range(HEIGHT):
        for x in range(WIDTH - 3):
            ids = [grid.get((x + i, y)) for i in range(4)]
            if any(i not in original for i in ids):
                continue
            pairs = [key(a, b) for a, b in zip(ids, ids[1:])]
            if all(p in bonds and p in native_b for p in pairs):
                return {
                    "x": x, "y": y, "material_ids": ids,
                    "sequence": "".join(str(material[i]["species"]) for i in ids)
                }
    return None


def spaces(grid, source):
    if source is None:
        return []
    result = []
    for dy in (-1, 1):
        y = source["y"] + dy
        if 0 <= y < HEIGHT:
            empty = [grid.get((source["x"] + dx, y)) is None for dx in range(4)]
            result.append({"y": y, "empty": sum(empty), "free_positions": empty})
    return result


def remaining_energy_after_event(event, free, lost, b, h):
    kind = event["kind"]
    if kind == "adsorb":
        is_template_capture = event["source_material_id"] is not None
        cost = 2 if is_template_capture else 1
        free -= cost
        lost += 1
    elif kind == "B_form":
        free -= 2
        lost += 1
    elif kind == "B_break":
        free += 1
    elif kind == "H_release":
        lost += 1
    else:
        raise AssertionError(f"Unexpected physical event {kind}")
    assert free >= 0 and lost >= 0
    assert free + len(b) + len(h) + lost == 500, (
        event, free, lost, len(b), len(h)
    )
    return free, lost


def eligible_slots(grid, b, h, source, free_energy, bath):
    """Exactly the physical M8 vertical source-choice restrictions at tick start.

    This is opportunity bookkeeping only: it is NOT a counterfactual reaction,
    and eligible cell-ticks are NOT statistically independent observations.
    """
    if source is None:
        return 0, 0
    src = set(source["material_ids"])
    backbone_degree = Counter(i for pair in b for i in pair)
    weak_degree = Counter(i for pair in h for i in pair)
    candidate = 0
    feasible = 0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if (x, y) in grid:
                continue
            choices = []
            for dy in (-1, 1):
                p = grid.get((x, y + dy))
                if p is not None and backbone_degree[p] and weak_degree[p] < 2:
                    choices.append(p)
            if choices and min(choices) in src:
                candidate += 1
                if free_energy >= 2 and sum(bath.values()) > 0:
                    feasible += 1
    return candidate, feasible


def reconstruct_world(world):
    assert world["ticks"] == TICKS
    feedstock = world["initial_state"]["feedstock"]
    assert len(feedstock) == 20
    original = {i["material_id"] for i in feedstock}
    assert len(original) == 20
    grid = {}
    material = {}
    for i in feedstock:
        xy = i["x"], i["y"]
        assert xy not in grid
        grid[xy] = i["material_id"]
        material[i["material_id"]] = dict(i)
    b = set()
    h = set()
    native_b = set()
    free, lost = 500, 0
    bath = {0: 30, 1: 30}
    events = world["all_native_physical_events"]
    events_by_tick = defaultdict(list)
    for event in events:
        assert 1 <= event["tick"] <= TICKS
        events_by_tick[event["tick"]].append(event)
    first = None
    first_stats = None
    source_ids = set()
    source_capture_events = []
    h_durations = []
    h_start = {}
    all_source_exposures = 0
    funded_source_exposures = 0
    occupied_post_source = []
    source_4_bonded_ticks = 0
    number_events = Counter()
    observed_source_pairs = None

    for tick in range(1, TICKS + 1):
        # Opportunities are computed on the actual frozen physical state
        # before this tick; no reaction is simulated.
        if first is not None:
            e, funded = eligible_slots(grid, b, h, first, free, bath)
            all_source_exposures += e
            funded_source_exposures += funded
            occupied_post_source.append(len(grid))
        for event in events_by_tick[tick]:
            k = event["kind"]
            number_events[k] += 1
            if k == "H_release":
                pair = tuple(event["pair"])
                assert pair in h, (world["seed"], tick, pair, "missing H")
                h.remove(pair)
                if pair in h_start:
                    h_durations.append(tick - h_start.pop(pair))
            elif k == "B_break":
                pair = tuple(event["pair"])
                assert pair in b, (world["seed"], tick, pair, "missing B")
                b.remove(pair)
            elif k == "adsorb":
                ident = event["new_material_id"]
                xy = event["x"], event["y"]
                specie = event["species"]
                assert ident not in material and xy not in grid
                assert bath[specie] > 0
                bath[specie] -= 1
                material[ident] = {"material_id": ident, "x": xy[0],
                                   "y": xy[1], "species": specie}
                grid[xy] = ident
                parent = event["source_material_id"]
                if parent is not None:
                    assert parent in material
                    p = key(ident, parent)
                    assert p not in h
                    h.add(p)
                    if first is not None and tick > first["tick"] and parent in source_ids:
                        h_start[p] = tick
                        source_capture_events.append({
                            "tick": tick, "new_material_id": ident,
                            "source_material_id": parent, "x": xy[0],
                            "y": xy[1], "species": specie
                        })
            elif k == "B_form":
                p = tuple(event["pair"])
                assert p not in b and all(i in material for i in p)
                b.add(p)
                native_b.add(p)
            else:
                raise AssertionError((world["seed"], tick, k))
            free, lost = remaining_energy_after_event(event, free, lost, b, h)

        candidate = first_original_four(grid, material, b, original, native_b)
        if first is None and candidate is not None:
            first = {"tick": tick, **candidate}
            source_ids = set(candidate["material_ids"])
            observed_source_pairs = [
                key(a, z) for a, z in zip(first["material_ids"], first["material_ids"][1:])
            ]
            sides = spaces(grid, first)
            first_stats = {
                "source_tick": tick,
                "occupancy_at_origin": len(grid),
                "initial_source_row_y": first["y"],
                "first_source_x": first["x"],
                "side_empty_counts_at_origin": [i["empty"] for i in sides],
                "fully_empty_side_at_origin": any(i["empty"] == 4 for i in sides),
                "at_least_one_empty_adjoining_site": any(i["empty"] > 0 for i in sides),
                "all_sides_blocked": all(i["empty"] == 0 for i in sides),
                "available_energy_at_origin": free,
                "bath_at_origin": sum(bath.values()),
            }
        if first is not None:
            if all(pair in b for pair in observed_source_pairs):
                source_4_bonded_ticks += 1

        assert free + len(b) + len(h) + lost == 500
        assert len(material) + sum(bath.values()) == 80

    assert (first is None) == (world["first_source"] is None)
    if first:
        src = world["first_source"]
        assert all(first[k] == src[k] for k in (
            "tick", "x", "y", "material_ids", "sequence"
        )), (world["seed"], "original detector mismatch", first, src)

    assert number_events == Counter(world["event_counts"])
    end = world["final_state"]
    assert end["n_particles"] == len(material)
    assert end["B_backbones"] == len(b) and end["H_contacts"] == len(h)
    assert end["available_energy"] == free
    assert end["dissipated_energy"] == lost
    assert end["bond_stored_energy"] == len(b) + len(h)
    assert all(int(end["bath_remaining"][str(i)]) == bath[i] for i in (0, 1))
    assert len(source_capture_events) == world["captured_from_first_source_after_origin"]
    assert len(source_capture_events) <= number_events.get("adsorb", 0)

    # Posthoc progression ladder, NEVER a replacement preregistered outcome.
    per_side = defaultdict(set)
    per_parent = set()
    for cap in source_capture_events:
        if cap["x"] >= first["x"] and cap["x"] < first["x"] + 4 and (
            abs(cap["y"] - first["y"]) == 1
        ):
            per_side[cap["y"]].add(cap["x"])
            per_parent.add(cap["source_material_id"])
    max_aligned = max((len(s) for s in per_side.values()), default=0)
    total_four_after_origin = int(max_aligned >= 4)
    return {
        "seed": world["seed"], "mode": world["mode"],
        "source": first_stats,
        "source_capture_count": len(source_capture_events),
        "source_capture_event_ids": [e["new_material_id"] for e in source_capture_events],
        "source_captures_at_distinct_parent_positions": len(per_parent),
        "max_aligned_distinct_after_source_capture_sites_same_row": max_aligned,
        "source_made_four_aligned_post_origin_captures": bool(total_four_after_origin),
        "source_H_release_durations_of_completed_contacts": h_durations,
        "source_H_contacts_still_attached_at_end": len(h_start),
        "source_free_target_cell_ticks": all_source_exposures,
        "source_energy_feasible_target_cell_ticks": funded_source_exposures,
        "source_fully_B_bonded_post_origin_ticks": source_4_bonded_ticks,
        "mean_occupancy_after_source": (
            round(statistics.mean(occupied_post_source), 3) if occupied_post_source else None
        ),
        "posthoc_reconstruction_exact_energy_material_event_validation": True,
    }


def aggregate(entries):
    source_entries = [x for x in entries if x["source"] is not None]
    capture_entries = [x for x in source_entries if x["source_capture_count"] > 0]
    times = sorted(x["source"]["source_tick"] for x in source_entries)
    occupancies = sorted(x["source"]["occupancy_at_origin"] for x in source_entries)
    slots = sorted(x["source_free_target_cell_ticks"] for x in source_entries)
    hdur = [a for x in entries for a in x["source_H_release_durations_of_completed_contacts"]]
    return {
        "n_worlds": len(entries),
        "source_worlds": len(source_entries),
        "source_tick_median": statistics.median(times) if times else None,
        "source_tick_min": min(times) if times else None,
        "source_tick_max": max(times) if times else None,
        "source_tick_by_50": sum(t <= 50 for t in times),
        "source_tick_by_100": sum(t <= 100 for t in times),
        "source_occupancy_median_out_of_50": statistics.median(occupancies) if occupancies else None,
        "source_occupancy_min_max": [min(occupancies), max(occupancies)] if occupancies else None,
        "source_worlds_any_fully_empty_adjacent_four_site_row_at_origin":
            sum(x["source"]["fully_empty_side_at_origin"] for x in source_entries),
        "source_worlds_all_neighbour_sides_blocked_at_origin":
            sum(x["source"]["all_sides_blocked"] for x in source_entries),
        "source_worlds_with_at_least_one_adjacent_open_cell_at_origin":
            sum(x["source"]["at_least_one_empty_adjoining_site"] for x in source_entries),
        "source_worlds_at_least_one_actual_H_capture_after_birth": len(capture_entries),
        "source_worlds_at_least_four_actual_H_captures_after_birth":
            sum(x["source_capture_count"] >= 4 for x in source_entries),
        "source_worlds_four_distinct_aligned_postbirth_H_capture_sites_same_row":
            sum(x["source_made_four_aligned_post_origin_captures"] for x in source_entries),
        "total_actual_source_H_captures": sum(x["source_capture_count"] for x in entries),
        "total_possible_source_cell_ticks": sum(x["source_free_target_cell_ticks"] for x in entries),
        "total_energy_feasible_source_cell_ticks":
            sum(x["source_energy_feasible_target_cell_ticks"] for x in entries),
        "median_source_possible_cell_ticks": statistics.median(slots) if slots else None,
        "total_observed_source_H_releases": len(hdur),
        "source_H_contact_duration_median_if_released": statistics.median(hdur) if hdur else None,
        "source_H_contacts_censored_at_tick200": sum(
            x["source_H_contacts_still_attached_at_end"] for x in entries
        ),
        "source_4_B_link_persistence_ticks_all_worlds": sum(
            x["source_fully_B_bonded_post_origin_ticks"] for x in entries
        ),
    }


def execute():
    result = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = result["all_worlds"]
    assert len(rows) == 64
    assert [r["seed"] for r in rows] == list(range(610001, 610065))
    assert result["summary"]["all_exact_material_energy_ledgers_passed"]
    raw = []
    for row in rows:
        assert set(row["arms"]) == set(MODES)
        raw.append({
            "seed": row["seed"],
            "arms": {m: reconstruct_world(row["arms"][m]) for m in MODES}
        })
    grouped = {
        m: aggregate([r["arms"][m] for r in raw]) for m in MODES
    }
    assert grouped["templated"]["total_actual_source_H_captures"] == 16
    assert grouped["shuffled_identity"]["total_actual_source_H_captures"] == 16
    assert grouped["no_template"]["total_actual_source_H_captures"] == 0
    assert grouped["templated"]["source_worlds"] == 30
    assert grouped["shuffled_identity"]["source_worlds"] == 30
    assert grouped["no_template"]["source_worlds"] == 29

    diagnostic = {
        "status": "posthoc_diagnostic_only_not_a_new_preregistered_scientific_test",
        "source_run": 44412124197,
        "source_artifact": 14476369876,
        "no_new_physical_worlds": True, "no_new_seeds": True,
        "no_original_physics_import_or_step": True,
        "all_worlds_exact_event_energy_mass_reconstructed": 192,
        "mode_aggregate": grouped, "per_seed": raw,
        "frozen_primary_science_verdict_unchanged":
            result["summary"]["frozen_decision_gates"],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(diagnostic, indent=2) + "\n", encoding="utf-8")
    a = grouped["templated"]
    n = grouped["no_template"]
    lines = [
        "# M8.1a — Audit retrospettivo dei soli eventi congelati",
        "",
        "> Questo è un audit diagnostico POST-HOC, non un nuovo esperimento, "
        "non una ripetizione indipendente della fisica e non un nuovo gate.",
        "",
        "- Fonte: [run #44412124197](https://github.com/kkongiu/alife-lab/actions/runs/44412124197), "
        "[artifact #14476369876](https://github.com/kkongiu/alife-lab/actions/runs/44412124197/artifacts/14476369876).",
        "- Tre bracci x 64 seed = **192/192** log di eventi ricostruiti, "
        "controllando ogni formazione/rottura B, rilascio H, cattura e bilancio energetico/materiale.",
        "- **Zero nuove simulazioni:** nessuna chiamata a WorldM8.step e nessun nuovo seed.",
        "",
        "## Misure diagnostiche — per modo",
        "",
        "| Misura | Templating | Identity shuffled | No-template |",
        "|---|---:|---:|---:|",
    ]
    fields = [
        ("Sorgenti native", "source_worlds"),
        ("Prima sorgente entro tick 50", "source_tick_by_50"),
        ("Prima sorgente entro tick 100", "source_tick_by_100"),
        ("Mediana tick prima sorgente", "source_tick_median"),
        ("Mediana siti occupati (su 50) alla nascita sorgente", "source_occupancy_median_out_of_50"),
        ("Sorgenti con fila laterale di 4 siti completamente vuota", "source_worlds_any_fully_empty_adjacent_four_site_row_at_origin"),
        ("Sorgenti con tutte le file laterali già bloccate", "source_worlds_all_neighbour_sides_blocked_at_origin"),
        ("Sorgenti con ≥1 cella laterale vuota", "source_worlds_with_at_least_one_adjacent_open_cell_at_origin"),
        ("Mondi con ≥1 reale cattura H dalla prima sorgente", "source_worlds_at_least_one_actual_H_capture_after_birth"),
        ("Mondi con ≥4 catture H dalla prima sorgente", "source_worlds_at_least_four_actual_H_captures_after_birth"),
        ("Mondi con 4 posizioni allineate catturate da prima sorgente", "source_worlds_four_distinct_aligned_postbirth_H_capture_sites_same_row"),
        ("Catture H realmente avvenute dalla prima sorgente", "total_actual_source_H_captures"),
        ("Cella-tick esposte dalla prima sorgente (opportunità, non esperimenti)", "total_possible_source_cell_ticks"),
        ("Cella-tick esposte con energia disponibile ≥2", "total_energy_feasible_source_cell_ticks"),
        ("Rilasci H dei nuovi contatti con prima sorgente", "total_observed_source_H_releases"),
        ("Durata mediana H dei contatti rilasciati, tick", "source_H_contact_duration_median_if_released"),
    ]
    for label, field in fields:
        items = [grouped[m][field] for m in MODES]
        lines.append("| " + label + " | " + " | ".join(
            str(x) if x is not None else "—" for x in items
        ) + " |")
    lines.extend([
        "", "## Interpretazione limitata",
        "",
        "La chimica M8.0 e i criteri dell'esperimento M8.1a non sono stati alterati. "
        "Una cattura H o una posizione vuota non equivalgono a copiatura; "
        "una cella-tick non è una replica statistica indipendente.",
        "",
        "Il rilevatore originario richiede quattro nuove catture **successive** alla nascita "
        "della prima catena, nella stessa fila adiacente, con genealogia puntuale, "
        "legami B, distacco completo e persistenza ≥20 tick. "
        "Il confronto tra '4 siti liberi', '4 catture effettive' e 'figlia persistente' "
        "localizza quale requisito blocca materialmente la riuscita.",
        "",
        "I risultati sono diagnostici esplorativi: nessuna conclusione causale "
        "sulla mobilità, nessun cambio di parametri basato su questi numeri "
        "senza un nuovo protocollo M8.1b distinto.",
        "",
        "## Verdetto primario congelato — INVARIATO",
        "",
        *[f"- {k}: **{v}**" for k, v in
          result["summary"]["frozen_decision_gates"].items()],
        "",
        "Tutte le misure per singolo seed nel file "
        "`campaigns/m8_1a/posthoc_diagnostic.json` allegato al workflow.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("M81A_POSTHOC_SUMMARY=" + json.dumps(grouped, sort_keys=True), flush=True)
    return diagnostic


if __name__ == "__main__":
    execute()
