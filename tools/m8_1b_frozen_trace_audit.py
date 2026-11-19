"""M8.1b post-hoc independent event reconstruction and bottleneck audit.

INPUT: completed immutable M8.1b Actions artifact #14512363685 only.
NEVER import physics, instantiate worlds, call step, sample random values, or
alter the original preregistered gates. All 256 original nulls retained.
This audit reconstructs states by applying original native event transcripts.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "campaigns/m8_1b/results.json"
OUTPUT = ROOT / "campaigns/m8_1b/posthoc_geometry.json"
REPORT = ROOT / "reports/M8_1b_posthoc_geometry.md"
ARMS = ("static_templated", "hop_templated", "hop_shuffled", "hop_no_template")
WIDTH, HEIGHT, TICKS = 10, 5, 240


def pair(a, b):
    return (a, b) if a < b else (b, a)


def degrees(edges):
    result = Counter()
    for a, b in edges:
        result[a] += 1
        result[b] += 1
    return result


def native_source(grid, species, original, b, formed):
    """Read earliest real four-ID B segment; observer only, no chemistry."""
    for y in range(HEIGHT):
        for x in range(WIDTH - 3):
            ids = [grid.get((x + dx, y)) for dx in range(4)]
            if any(i not in original for i in ids):
                continue
            p = [pair(a, z) for a, z in zip(ids, ids[1:])]
            if all(edge in b and edge in formed for edge in p):
                return {
                    "x": x, "y": y, "material_ids": ids,
                    "sequence": "".join(str(species[i]) for i in ids)
                }
    return None


def parent_intact(source, grid, b):
    if source is None:
        return False
    ids = source["material_ids"]
    return (all(grid.get((source["x"] + i, source["y"])) == mid
                for i, mid in enumerate(ids))
            and all(pair(a, z) in b for a, z in zip(ids, ids[1:])))


def corridor_rows(source, grid, original, b, h):
    bd = degrees(b)
    hd = degrees(h)
    result = []
    for y in (source["y"] - 1, source["y"] + 1):
        if not 0 <= y < HEIGHT:
            continue
        occ = []
        for dx in range(4):
            mid = grid.get((source["x"] + dx, y))
            if mid is None:
                category = "free"
            elif bd[mid]:
                category = "B_locked"
            elif hd[mid]:
                category = "H_only"
            else:
                category = "isolated"
            occ.append({
                "material_id": mid, "category": category,
                "initial_monomer": mid in original if mid is not None else None,
            })
        result.append({
            "y": y, "cells": occ,
            "free": sum(c["category"] == "free" for c in occ),
            "B_locked": sum(c["category"] == "B_locked" for c in occ),
            "H_only": sum(c["category"] == "H_only" for c in occ),
            "isolated": sum(c["category"] == "isolated" for c in occ),
        })
    return result


def source_available_capture_slots(source, grid, b, h, free_energy, bath):
    """At END of tick: vacancies where original source would win _vertical_template.

    This is a diagnostic potential opportunity only, NOT actual next-tick
    lottery/occupancy after contact breaks + local hops.
    """
    bd, hd = degrees(b), degrees(h)
    candidate = 0
    feasible = 0
    competing = 0
    for y in (source["y"] - 1, source["y"] + 1):
        if not 0 <= y < HEIGHT:
            continue
        for dx in range(4):
            x = source["x"] + dx
            if (x, y) in grid:
                continue
            possibilities = []
            for ddy in (-1, 1):
                mid = grid.get((x, y + ddy))
                if mid is not None and bd[mid] and hd[mid] < 2:
                    possibilities.append(mid)
            if not possibilities:
                continue
            expected = source["material_ids"][dx]
            if expected in possibilities:
                if min(possibilities) == expected:
                    candidate += 1
                    if free_energy >= 2 and sum(bath.values()) > 0:
                        feasible += 1
                else:
                    competing += 1
    return candidate, feasible, competing


def replay(original_world):
    seed = original_world["seed"]
    arm = original_world["arm"]
    assert original_world["ticks"] == TICKS
    assert original_world["initial"]["B0"] == 0
    assert original_world["initial"]["H0"] == 0
    feedstock = original_world["initial"]["feedstock"]
    assert len(feedstock) == 20
    initial_ids = {v["material_id"] for v in feedstock}
    assert len(initial_ids) == 20
    grid = {}
    coords = {}
    species = {}
    for v in feedstock:
        mid = v["material_id"]
        xy = v["x"], v["y"]
        assert xy not in grid
        grid[xy] = mid
        coords[mid] = xy
        species[mid] = v["species"]
    assert Counter(species.values()) == Counter({0: 10, 1: 10})

    bath = {0: 30, 1: 30}
    b, h, formed = set(), set(), set()
    free_energy = 500
    dissipated = 0
    native_events = original_world["all_real_native_events"]
    grouped = defaultdict(list)
    for e in native_events:
        assert 1 <= e["tick"] <= TICKS
        grouped[e["tick"]].append(e)
    counts = Counter()
    first = None
    birth = None
    totals = Counter()
    max_free_live = 0
    live_rows = 0
    live_parent_ticks = 0
    origin_free_corridor = False
    all_live_corridor = False
    max_open_tick = None
    longest_blocker_streak = 0
    current_blocker_streak = 0
    first_source_captures = 0
    sample_most_open = None
    first_source_captures_by_tick = Counter()
    first_eligible_tick = None
    first_occupancy_40_tick = None
    first_occupancy_45_tick = None
    first_energy_lt_2_tick = None

    for tick in range(1, TICKS + 1):
        for e in grouped[tick]:
            kind = e["kind"]
            counts[kind] += 1
            if kind == "H_release":
                edge = tuple(e["pair"])
                assert edge in h, (seed, tick, "invalid H_release", edge)
                h.remove(edge)
                dissipated += 1
            elif kind == "B_break":
                edge = tuple(e["pair"])
                assert edge in b, (seed, tick, "invalid B_break", edge)
                b.remove(edge)
                free_energy += 1
            elif kind == "hop":
                assert arm != "static_templated"
                mid = e["material_id"]
                old = e["from_x"], e["from_y"]
                new = e["to_x"], e["to_y"]
                assert coords[mid] == old and grid[old] == mid
                assert new not in grid
                assert 0 <= new[0] < WIDTH and 0 <= new[1] < HEIGHT
                assert abs(old[0] - new[0]) + abs(old[1] - new[1]) == 1
                assert e["species"] == species[mid] and e["energy_cost"] == 1
                assert all(mid not in edge for edge in b | h), (
                    seed, tick, mid, "linked particle moved"
                )
                del grid[old]
                grid[new] = mid
                coords[mid] = new
                free_energy -= 1
                dissipated += 1
            elif kind == "adsorb":
                mid = e["new_material_id"]
                xy = e["x"], e["y"]
                sp = e["species"]
                assert xy not in grid and mid not in coords
                assert bath[sp] > 0
                parent = e["source_material_id"]
                assert parent is not None, (seed, tick, "zero background should forbid spontaneous adsorption")
                assert parent in coords and abs(coords[parent][1] - xy[1]) == 1
                assert coords[parent][0] == xy[0]
                assert any(parent in edge for edge in b)
                assert sum(parent in edge for edge in h) < 2
                assert e["source_species"] == species[parent]
                assert free_energy >= 2
                bath[sp] -= 1
                grid[xy], coords[mid], species[mid] = mid, xy, sp
                free_energy -= 2
                dissipated += 1
                edge = pair(mid, parent)
                assert edge not in h
                h.add(edge)
                if first is not None and tick > first["tick"] and parent in first["material_ids"]:
                    first_source_captures += 1
                    first_source_captures_by_tick[tick] += 1
            elif kind == "B_form":
                edge = tuple(e["pair"])
                assert edge not in b
                a, z = edge
                assert a in coords and z in coords
                assert coords[a][1] == coords[z][1]
                assert abs(coords[a][0] - coords[z][0]) == 1
                bd = degrees(b)
                assert bd[a] < 2 and bd[z] < 2
                assert free_energy >= 2
                free_energy -= 2
                dissipated += 1
                b.add(edge)
                formed.add(edge)
            else:
                raise AssertionError(("unrecognized native event", seed, kind))
            assert free_energy >= 0
            assert free_energy + len(b) + len(h) + dissipated == 500
            assert len(coords) + sum(bath.values()) == 80

        assert len(grid) == len(coords)
        assert all(grid[xy] == mid for mid, xy in coords.items())
        assert all(0 <= xy[0] < WIDTH and 0 <= xy[1] < HEIGHT
                   for xy in coords.values())

        if len(coords) >= 40 and first_occupancy_40_tick is None:
            first_occupancy_40_tick = tick
        if len(coords) >= 45 and first_occupancy_45_tick is None:
            first_occupancy_45_tick = tick
        if free_energy < 2 and first_energy_lt_2_tick is None:
            first_energy_lt_2_tick = tick

        if first is None:
            observed = native_source(grid, species, initial_ids, b, formed)
            if observed:
                first = {"tick": tick, **observed}

        if first is not None:
            live = parent_intact(first, grid, b)
            if live:
                live_parent_ticks += 1
                lanes = corridor_rows(first, grid, initial_ids, b, h)
                best_lane = max(lanes, key=lambda row: (row["free"], -row["B_locked"], -row["H_only"]))
                max_free_live = max(max_free_live, best_lane["free"])
                all_live_corridor = all_live_corridor or best_lane["free"] == 4
                if sample_most_open is None or best_lane["free"] > sample_most_open["free"]:
                    sample_most_open = {
                        "tick": tick, "y": best_lane["y"], "free": best_lane["free"],
                        "B_locked": best_lane["B_locked"], "H_only": best_lane["H_only"],
                        "isolated": best_lane["isolated"],
                    }
                if best_lane["free"] == 4 and max_open_tick is None:
                    max_open_tick = tick
                if best_lane["free"] < 4:
                    current_blocker_streak += 1
                    longest_blocker_streak = max(longest_blocker_streak, current_blocker_streak)
                else:
                    current_blocker_streak = 0
                for row in lanes:
                    live_rows += 1
                    totals["side_rows_at_live_parent_ticks"] += 1
                    totals["side_cell_ticks"] += 4
                    for group in ("free", "B_locked", "H_only", "isolated"):
                        totals[group + "_cell_ticks"] += row[group]
                    if row["B_locked"]:
                        totals["side_row_ticks_with_B_obstruction"] += 1
                    elif row["H_only"]:
                        totals["side_row_ticks_H_only_obstruction_without_B"] += 1
                    elif row["isolated"]:
                        totals["side_row_ticks_isolated_only_obstruction"] += 1
                    else:
                        totals["side_row_ticks_completely_free"] += 1
                slots, funded, competed = source_available_capture_slots(
                    first, grid, b, h, free_energy, bath
                )
                totals["eligible_source_slot_ticks"] += slots
                totals["funded_source_slot_ticks"] += funded
                totals["competitor_selected_instead_slot_ticks"] += competed
                if funded and first_eligible_tick is None:
                    first_eligible_tick = tick
                if birth is None:
                    origin_free_corridor = any(row["free"] == 4 for row in lanes)
                    birth = {
                        "tick": tick,
                        "occupancy": len(coords),
                        "energy": free_energy,
                        "bath_total": sum(bath.values()),
                        "side_lanes": lanes,
                        "side_best_free": best_lane["free"],
                        "side_B_occupied_cells": sum(row["B_locked"] for row in lanes),
                        "side_H_only_occupied_cells": sum(row["H_only"] for row in lanes),
                        "side_isolated_occupied_cells": sum(row["isolated"] for row in lanes),
                        "birth_source_selected_slots": slots,
                        "birth_source_funded_slots": funded,
                    }

    assert counts == Counter(original_world["native_event_counts"]), (seed, arm, "event kind counts")
    assert (first is None) == (original_world["first_source"] is None)
    if first:
        expected = original_world["first_source"]
        assert all(expected[k] == first[k] for k in (
            "tick", "x", "y", "material_ids", "sequence"
        )), (seed, arm, "first source differs")
    assert origin_free_corridor == original_world["first_source_corridor_free_at_birth"]
    assert all_live_corridor == original_world["first_source_live_corridor_seen_at_or_after_birth"]
    assert max_open_tick == original_world["first_source_live_corridor_first_tick"]
    assert totals["side_rows_at_live_parent_ticks"] == live_rows
    assert live_parent_ticks == original_world["first_source_live_B_chain_ticks"]
    assert first_source_captures == original_world["first_source_adsorptions_after_birth"]

    final = original_world["final_physical_metrics"]
    assert final["n_particles"] == len(coords)
    assert final["B_backbones"] == len(b)
    assert final["H_contacts"] == len(h)
    assert final["free_energy"] == free_energy if "free_energy" in final else True
    assert final["available_energy"] == free_energy
    assert final["dissipated_energy"] == dissipated
    assert final["bond_stored_energy"] == len(b) + len(h)
    assert all(final["bath_remaining"][str(sp)] == bath[sp] for sp in (0, 1))
    assert free_energy + len(b) + len(h) + dissipated == 500
    assert len(coords) + sum(bath.values()) == 80

    return {
        "seed": seed, "arm": arm,
        "source": birth,
        "live_first_source_ticks": live_parent_ticks,
        "birth_has_empty_corridor": origin_free_corridor,
        "ever_live_source_has_empty_corridor": all_live_corridor,
        "best_free_cells_in_same_adjacent_row_while_parent_intact": max_free_live if first else None,
        "closest_to_empty_corridor": sample_most_open,
        "source_H_capture_count_after_birth": first_source_captures,
        "first_source_funded_capture_opportunity_tick": first_eligible_tick,
        "first_occupancy_40_tick": first_occupancy_40_tick,
        "first_occupancy_45_tick": first_occupancy_45_tick,
        "first_energy_below_two_tick": first_energy_lt_2_tick,
        "full_native_events_replayed": sum(counts.values()),
        "native_event_types": dict(counts),
        "geometry_counters": dict(totals),
        "strict_reconstruction_pass": True,
    }


def statmedian(values):
    return statistics.median(values) if values else None


def aggregate(rows):
    sources = [x for x in rows if x["source"] is not None]
    birth = [x["source"] for x in sources]
    hits = [x for x in sources if x["source_H_capture_count_after_birth"] > 0]
    cat = Counter(x["best_free_cells_in_same_adjacent_row_while_parent_intact"] for x in sources)
    geom = Counter()
    for r in sources:
        geom.update(r["geometry_counters"])
    denom = geom["side_cell_ticks"]
    return {
        "worlds_total": len(rows),
        "worlds_with_native_first_B4": len(sources),
        "source_birth_tick_median": statmedian([x["tick"] for x in birth]),
        "source_birth_occupancy_median_out_of_50": statmedian([x["occupancy"] for x in birth]),
        "source_birth_free_energy_median_out_of_500": statmedian([x["energy"] for x in birth]),
        "source_birth_best_free_adjacent_cells_median_out_of_4":
            statmedian([x["side_best_free"] for x in birth]),
        "source_birth_with_at_least_one_B_locked_side_cell": sum(
            x["side_B_occupied_cells"] > 0 for x in birth
        ),
        "source_birth_with_only_isolated_side_obstruction": sum(
            x["side_B_occupied_cells"] == 0 and x["side_H_only_occupied_cells"] == 0
            for x in birth
        ),
        "source_birth_with_no_complete_four_site_side": sum(
            x["side_best_free"] < 4 for x in birth
        ),
        "source_worlds_max_free_adjacent_cells_distribution": {
            str(n): cat[n] for n in range(5)
        },
        "source_worlds_ever_reached_three_free_adjacent_cells":
            sum(x["best_free_cells_in_same_adjacent_row_while_parent_intact"] >= 3 for x in sources),
        "source_worlds_ever_reached_all_four_free_adjacent_cells":
            sum(x["best_free_cells_in_same_adjacent_row_while_parent_intact"] == 4 for x in sources),
        "source_worlds_with_real_postbirth_H_captures": len(hits),
        "source_H_captures_postbirth_total":
            sum(x["source_H_capture_count_after_birth"] for x in sources),
        "source_worlds_with_energy_at_birth_at_least_two":
            sum(x["energy"] >= 2 for x in birth),
        "worlds_first_hit_40_occupied_cells":
            sum(x["first_occupancy_40_tick"] is not None for x in rows),
        "worlds_first_hit_45_occupied_cells":
            sum(x["first_occupancy_45_tick"] is not None for x in rows),
        "source_side_B_locked_fraction_of_all_live_side_cell_ticks":
            round(geom["B_locked_cell_ticks"] / denom, 5) if denom else None,
        "source_side_H_only_fraction_of_all_live_side_cell_ticks":
            round(geom["H_only_cell_ticks"] / denom, 5) if denom else None,
        "source_side_isolated_fraction_of_all_live_side_cell_ticks":
            round(geom["isolated_cell_ticks"] / denom, 5) if denom else None,
        "source_side_vacancy_fraction_of_all_live_side_cell_ticks":
            round(geom["free_cell_ticks"] / denom, 5) if denom else None,
        "source_side_row_ticks_with_at_least_one_B_locked_cell":
            geom["side_row_ticks_with_B_obstruction"],
        "source_side_row_ticks_H_only_obstruction_no_B":
            geom["side_row_ticks_H_only_obstruction_without_B"],
        "source_side_row_ticks_only_isolated_obstruction":
            geom["side_row_ticks_isolated_only_obstruction"],
        "source_funded_capture_opportunity_site_ticks":
            geom["funded_source_slot_ticks"],
        "source_energy_agnostic_capture_opportunity_site_ticks":
            geom["eligible_source_slot_ticks"],
        "competing_older_source_wins_site_ticks":
            geom["competitor_selected_instead_slot_ticks"],
        "mean_source_intact_duration_ticks_in_source_worlds":
            round(statistics.mean(x["live_first_source_ticks"] for x in sources), 2) if sources else None,
        "all_native_event_reconstruction_ok": all(r["strict_reconstruction_pass"] for r in rows)
    }


def execute():
    original = json.loads(INPUT.read_text(encoding="utf-8"))
    assert original["summary"]["physical_worlds"] == 256
    assert original["summary"]["gates"]["physics_integrity"] == "PASS"
    assert original["summary"]["gates"]["mobility_corridor_effect"] == "NO_GO"
    assert original["summary"]["gates"]["informative_persistent_offspring"] == "NO_GO"
    worlds = original["all_256_physical_worlds"]
    assert len(worlds) == 64
    assert [row["seed"] for row in worlds] == list(range(620001, 620065))
    data = []
    for n, row in enumerate(worlds, start=1):
        assert set(row["arms"]) == set(ARMS)
        data.append({
            "seed": row["seed"],
            "arms": {arm: replay(row["arms"][arm]) for arm in ARMS}
        })
        if n % 16 == 0:
            print("M81B_AUDIT_REPLAY_PROGRESS=" + str(n) + "/64", flush=True)
    aggs = {arm: aggregate([row["arms"][arm] for row in data]) for arm in ARMS}
    counts = original["summary"]["groups"]
    for arm in ARMS:
        assert aggs[arm]["worlds_total"] == 64
        assert aggs[arm]["worlds_with_native_first_B4"] == counts[arm]["native_first_B4_source_worlds"]
        assert (aggs[arm]["source_worlds_ever_reached_all_four_free_adjacent_cells"]
                == counts[arm]["source_live_corridor_available_at_or_after_birth_worlds"])
        assert sum(row["arms"][arm]["native_event_types"].get("hop", 0) for row in data) == counts[arm]["physical_hops"]
    result = {
        "status": "posthoc_mechanistic_diagnostic_only_not_confirmatory",
        "source_original_run_id": 44491013828,
        "source_original_artifact_id": 14512363685,
        "new_physical_worlds": 0,
        "new_random_draws": 0,
        "old_primary_gate_verdicts_unchanged": original["summary"]["gates"],
        "all_256_native_event_traces_reconstructed_with_exact_matter_energy": True,
        "aggregate": aggs,
        "per_seed": data,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    lines = [
        "# M8.1b — Audit retrospettivo dei soli eventi fisici originali",
        "",
        "**Questo NON è un nuovo esperimento**. Il ricercatore diagnostico non importa",
        "l'implementazione fisica né esegue reazioni; riapplica gli eventi archiviati",
        "della [campagna originale #44491013828](https://github.com/kkongiu/alife-lab/actions/runs/44491013828).",
        "",
        "## Principali indicatori",
        "",
        "| Indicatore | Statico attivo | Mobile attivo | Mobile rimescolato | Mobile senza templating |",
        "|---|---:|---:|---:|---:|",
    ]
    fields = [
        ("Prime catene native (mondi)", "worlds_with_native_first_B4"),
        ("Tick mediano di comparsa della prima catena", "source_birth_tick_median"),
        ("Occupazione mediana alla prima catena (su 50)", "source_birth_occupancy_median_out_of_50"),
        ("Energia libera mediana alla prima catena (su 500)", "source_birth_free_energy_median_out_of_500"),
        ("Siti liberi mediani nella migliore fila adiacente (su 4)", "source_birth_best_free_adjacent_cells_median_out_of_4"),
        ("Prime catene con almeno un blocco B in fila adiacente", "source_birth_with_at_least_one_B_locked_side_cell"),
        ("Prime catene con solo ostacoli isolati nelle file adiacenti", "source_birth_with_only_isolated_side_obstruction"),
        ("Prime catene senza quattro celle laterali tutte libere", "source_birth_with_no_complete_four_site_side"),
        ("Mondi con prima catena e almeno tre celle laterali libere in un tick", "source_worlds_ever_reached_three_free_adjacent_cells"),
        ("Mondi con prima catena e quattro celle laterali libere", "source_worlds_ever_reached_all_four_free_adjacent_cells"),
        ("Mondi con almeno una cattura H dalla prima catena", "source_worlds_with_real_postbirth_H_captures"),
        ("Catture H totali dalla prima catena", "source_H_captures_postbirth_total"),
        ("Celle-tick B-bloccate / celle-tick adiacenti (frazione)", "source_side_B_locked_fraction_of_all_live_side_cell_ticks"),
        ("Celle-tick H-only / celle-tick adiacenti (frazione)", "source_side_H_only_fraction_of_all_live_side_cell_ticks"),
        ("Celle-tick isolate / celle-tick adiacenti (frazione)", "source_side_isolated_fraction_of_all_live_side_cell_ticks"),
        ("Celle-tick libere / celle-tick adiacenti (frazione)", "source_side_vacancy_fraction_of_all_live_side_cell_ticks"),
        ("Opportunità cattura dalla prima catena a fine tick con energia", "source_funded_capture_opportunity_site_ticks"),
        ("Concorrente prevalente per minimo material ID", "competing_older_source_wins_site_ticks"),
    ]
    for label, field in fields:
        line = "| " + label + " | " + " | ".join(
            str(aggs[a][field]) if aggs[a][field] is not None else "—" for a in ARMS
        ) + " |"
        lines.append(line)
    lines.extend([
        "",
        "Tutte le celle-tick sono conteggi ripetuti dei medesimi mondi, NON",
        "unità statistiche indipendenti. B-bloccata significa che il monomero",
        "ha almeno un legame B; H-only indica H ma nessun B; isolato significa",
        "nessun legame. La presenza di una cella vuota non garantisce una cattura.",
        "",
        "Un'opportunità di cattura è calcolata sulla fotografia fisica a FINE tick,",
        "richiedendo che la prima catena sia ancora integra, che il sito adiacente",
        "sia vuoto, che la sorgente vinca la scelta del minimo ID, che ci siano",
        "energia libera ≥2 e monomeri nel bagno. Non è un tiro di probabilità",
        "durante il tick successivo, quando rotture e hop possono cambiare lo stato.",
        "",
        "## Verifiche",
        "",
        "- Ricostruzione evento-per-evento dei 256 mondi e verifica dei bilanci",
        "  di materia/energia dopo ogni evento, inclusi gli hop.",
        "- Riconoscimento della stessa prima catena nativa e degli stessi corridoi",
        "  del rilevatore originario: verifiche assertive per tutti i 256 mondi.",
        "- Nessuna nuova simulazione, nessun cambiamento ai parametri M8.0/M8.1b,",
        "  nessuna modifica ai gate di risultato preregistrati.",
        "",
        "## Limiti e prossima ipotesi",
        "",
        "Questa è una descrizione post-hoc di occupazione e legami, non identifica",
        "da sola un effetto causale del desorbimento. La scelta tra mobilità",
        "di legami, desorbimento o scambio richiederà una sola legge fisica",
        "separatamente versionata e preregistrata, con veri controlli causali.",
        "",
        "Il verdetto scientifico originario rimane **NO_GO** per corridoi",
        "e per copie informative persistenti nel braccio mobile attivo.",
        "Dati diagnostici dettagliati per seed nell'artefatto Actions di questo audit.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("M81B_POSTHOC_AUDIT=" + json.dumps(aggs, sort_keys=True), flush=True)
    return result


if __name__ == "__main__":
    execute()
