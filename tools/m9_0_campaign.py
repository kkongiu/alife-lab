"""M9.0 frozen paired experiment for seeded calibration and unseeded chemistry.

No organism, template-construction or genotype manipulation. Historical
negative campaigns unchanged. All random chemistry maps and seeds fixed in
campaigns/m9_0/protocol.json BEFORE this code was written.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import statistics

from alife_m9.chemostat import (
    Chemostat, catalyst_map, directed_cycle, LAW, SPECIES, DIMERS,
    FEED_EACH_MONOMER, ENERGY_FEED, ENERGY_POOL_CAP,
    P_WASHOUT, P_HYDROLYSIS,
    P_LIGATION_BACKGROUND, P_LIGATION_CATALYZED,
    SWITCH_OFF_AFTER,
)

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "campaigns/m9_0"
PROTOCOL = FOLDER / "protocol.json"
OUT = FOLDER / "results.json"
REPORT = ROOT / "reports/M9_0_results.md"

SEEDS = range(730001, 730009)
CHEMISTRIES = range(12)
MODES = ("on", "off", "switch_off")
TICKS = 300
LATE = range(220, 301)


def protocol() -> dict:
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"] == "alife-m9-0-chemostat-prereg-v1"
    assert p["status"] == "frozen_prior_to_M9_implementation_or_results"
    a = p["fixed_campaign"]
    assert a["total_worlds"] == 312 and a["ticks_per_world"] == TICKS
    assert a["seed_start"] == SEEDS.start
    assert a["seed_end_inclusive"] == SEEDS.stop - 1
    assert a["switch_off_after_tick"] == SWITCH_OFF_AFTER
    assert a["late_measurement_ticks"] == "220..300 inclusive, 81 observations per world"
    q = p["physical_rules"]
    assert q["system"].startswith("Well-stirred")
    assert q["random"].startswith("blake2b")
    assert q["feed"] if "feed" in q else True
    assert P_WASHOUT == 0.04 and P_HYDROLYSIS == 0.03
    assert P_LIGATION_BACKGROUND == 0.004
    assert P_LIGATION_CATALYZED == 0.65
    assert FEED_EACH_MONOMER == 3 and ENERGY_FEED == 8
    assert ENERGY_POOL_CAP == 64
    return p


def execute_world(seed: int, chemistry_id: int | str, mode: str) -> dict:
    known = chemistry_id == "positive"
    if not known:
        assert chemistry_id in CHEMISTRIES
    net = catalyst_map(chemistry_id)
    w = Chemostat(
        seed=seed, catalysts=net, mode=mode, seeded_positive=known
    )
    initial = w.snapshot()
    assert initial["atoms_inside"] == (2 if known else 0)
    assert initial["energy_bonds_inside"] == (1 if known else 0)
    assert all(v == 0 for v in initial["counts"].values()) if not known else initial["counts"]["AA"] == 1

    series = [w.step() for _ in range(TICKS)]
    assert len(series) == TICKS
    assert [x["tick"] for x in series] == list(range(1, TICKS + 1))
    assert all(s["atoms_inside"] + s["atoms_out"] ==
               initial["atoms_inside"] + s["atoms_fed"] for s in series)
    assert all(s["energy_pool"] + s["energy_bonds_inside"] +
               s["energy_bonds_out"] + s["energy_dissipated"] ==
               initial["energy_bonds_inside"] + s["energy_fed"] for s in series)

    late = [series[t-1] for t in LATE]
    event_counts = Counter(e["kind"] for e in w.events)
    catalytic_ligations = sum(
        e["kind"] == "ligation" and e["catalytic_channel_used"]
        for e in w.events
    )
    if mode == "off":
        assert catalytic_ligations == 0
    if mode == "switch_off":
        assert all(
            e["tick"] <= SWITCH_OFF_AFTER
            for e in w.events if
            e["kind"] == "ligation" and e["catalytic_channel_used"]
        )
    assert sum(s["counts"]["AA"] for s in late) >= 0
    return {
        "seed": seed, "chemistry": chemistry_id, "mode": mode,
        "law": LAW, "catalyst_map": net, "has_rule_graph_cycle": directed_cycle(net),
        "explicitly_seeded_positive_fixture": known,
        "initial": initial,
        "late_mean_AA": statistics.mean(s["counts"]["AA"] for s in late),
        "late_mean_total_dimers": statistics.mean(s["dimer_count"] for s in late),
        "last_molecules": series[-1]["counts"],
        "native_reaction_counts": dict(event_counts),
        "catalyst_used_ligations": catalytic_ligations,
        "all_tick_snapshots": series,
        "full_native_events": w.events,
        "last_world_hash": w.full_hash(),
        "exact_atom_and_energy_ledgers_all_steps": True,
    }


def paired_delta(arms, metric: str) -> dict:
    active = arms["on"][metric]
    off = arms["off"][metric]
    ablated = arms["switch_off"][metric]
    return {
        "on": active, "off": off, "switch_off": ablated,
        "delta_on_minus_off": active - off,
        "delta_on_minus_switch_off": active - ablated,
        "causal_effect_both_ge_3": (
            (active - off) >= 3 and (active - ablated) >= 3
        ),
    }


def summarize(records: list[dict], p: dict) -> dict:
    assert len(records) == 13
    assert [r["chemistry"] for r in records] == [
        "positive", *list(CHEMISTRIES)
    ]
    all_worlds = 0
    all_valid = True
    chemistries = []
    for rec in records:
        assert [r["seed"] for r in rec["seed_pairs"]] == list(SEEDS)
        net = catalyst_map(rec["chemistry"])
        assert rec["catalyst_map"] == net
        assert rec["has_rule_graph_cycle"] == directed_cycle(net)
        effects = []
        for row in rec["seed_pairs"]:
            arms = row["arms"]
            assert set(arms) == set(MODES)
            assert all(arms[m]["initial"] == arms["on"]["initial"] for m in MODES)
            all_worlds += len(arms)
            all_valid = all_valid and all(
                arms[m]["exact_atom_and_energy_ledgers_all_steps"]
                for m in MODES
            )
            metric = (
                "late_mean_AA" if rec["chemistry"] == "positive"
                else "late_mean_total_dimers"
            )
            effects.append({
                "seed": row["seed"],
                **paired_delta(arms, metric),
            })
        positive_pairs = sum(e["causal_effect_both_ge_3"] for e in effects)
        chemistries.append({
            "network": rec["chemistry"],
            "map": rec["catalyst_map"],
            "has_rule_graph_cycle": rec["has_rule_graph_cycle"],
            "seed_pairs_both_causal_deltas_ge_3": positive_pairs,
            "on_late_mean_over_seeds": statistics.mean(e["on"] for e in effects),
            "off_late_mean_over_seeds": statistics.mean(e["off"] for e in effects),
            "switched_off_late_mean_over_seeds": statistics.mean(
                e["switch_off"] for e in effects
            ),
            "paired_effects": effects,
        })
    assert all_worlds == 312
    assert all_valid
    calibration = chemistries[0]["seed_pairs_both_causal_deltas_ge_3"] >= 6
    spontaneous_hit = [
        c["network"] for c in chemistries[1:] if
        c["has_rule_graph_cycle"] and
        c["seed_pairs_both_causal_deltas_ge_3"] >= 5
    ]
    return {
        "physical_worlds": all_worlds,
        "distinct_unseeded_chemistries": 12,
        "independent_stochastic_seeds_per_chemistry": 8,
        "ticks_per_world": TICKS,
        "rule_maps": chemistries,
        "unseeded_networks_meeting_frozen_maintenance_effect": spontaneous_hit,
        "frozen_gates": {
            "integrity": "PASS" if all_valid else "INVALID",
            "known_seeded_autocatalysis_calibration": (
                "PASS" if calibration else "NO_GO"
            ),
            "unseeded_causal_network_maintenance_at_least_2_of_12": (
                "PASS" if len(spontaneous_hit) >= 2 else "NO_GO"
            ),
        },
        "scope": (
            "Catalytic molecule-level feedback in abstract chemostat. "
            "No inherited organism, no self-contained cell, no genotype, "
            "no multigenerational reproduction or digital life claim."
        ),
    }


def execute() -> dict:
    p = protocol()
    records = []
    for chemistry in ("positive", *CHEMISTRIES):
        arms_by_seed = []
        for seed in SEEDS:
            arms = {
                mode: execute_world(seed, chemistry, mode) for mode in MODES
            }
            arms_by_seed.append({"seed": seed, "arms": arms})
        records.append({
            "chemistry": chemistry,
            "catalyst_map": catalyst_map(chemistry),
            "has_rule_graph_cycle": directed_cycle(catalyst_map(chemistry)),
            "seed_pairs": arms_by_seed,
        })
        print(f"M90_PROGRESS_NETWORK={chemistry}", flush=True)

    summary = summarize(records, p)
    full = {
        "frozen_protocol": p, "summary": summary,
        "all_312_native_worlds": records,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(full, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# M9.0 — Reattore astratto aperto e autocatalisi",
        "",
        "**Preregistrazione precedente all'implementazione e agli esiti.**",
        "312 mondi, 300 tick, 12 reti generate da hashing fisso e 1 controllo positivo",
        "intenzionalmente *preseminato* con un dimero AA. Nessuna griglia o cellula.",
        "",
        "| Rete | Ciclo catalitico nelle regole | Seed con entrambi i delta >=3 (su 8) | Dimeri medi ON | Dimeri medi OFF | Dimeri medi spenti |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for rec in summary["rule_maps"]:
        lines.append(
            f"| {rec['network']} | {'sì' if rec['has_rule_graph_cycle'] else 'no'} "
            f"| {rec['seed_pairs_both_causal_deltas_ge_3']}/8 "
            f"| {rec['on_late_mean_over_seeds']:.2f} "
            f"| {rec['off_late_mean_over_seeds']:.2f} "
            f"| {rec['switched_off_late_mean_over_seeds']:.2f} |"
        )
    lines += [
        "", "Nota: nella prima riga (controllo positivo) il delta è misurato",
        "sul solo dimero **AA**; per le 12 reti non preseminate è sul totale",
        "dei dimери. Il positivo non può essere prova di origine spontanea.",
        "",
        "## Gate preregistrati",
        *[f"- **{k}**: {v}" for k, v in summary["frozen_gates"].items()],
        "",
        "## Limitazioni",
        "È un modello di reazioni dichiaratamente programmato, con input continuo",
        "di energia e risorse e senza organizzazioni individuali identificabili.",
        "La sola presenza di una rete a feedback nella mappa non è vita;",
        "un aumento della densità dei dimеры nel braccio catalitico indica",
        "dipendenza causale dalla catalisi nel reattore, non eredità o evoluzione.",
        "Ogni mondo e la sequenza completa dei suoi eventi sono disponibili",
        "nell'artefatto GitHub Actions `campaigns/m9_0/results.json`.",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines).replace("димеры", "dimeri") + "\n", encoding="utf-8")
    print("M90_FINAL_SUMMARY=" + json.dumps({
        "frozen_gates": summary["frozen_gates"],
        "unseeded_networks_meeting_frozen_maintenance_effect":
            summary["unseeded_networks_meeting_frozen_maintenance_effect"],
        "networks": [{
            "id": r["network"],
            "cycle": r["has_rule_graph_cycle"],
            "paired_seed_positive": r["seed_pairs_both_causal_deltas_ge_3"],
            "mean_on": round(r["on_late_mean_over_seeds"], 4),
            "mean_off": round(r["off_late_mean_over_seeds"], 4),
            "mean_switched": round(r["switched_off_late_mean_over_seeds"], 4),
        } for r in summary["rule_maps"]],
    }, sort_keys=True), flush=True)
    return summary


if __name__ == "__main__":
    execute()
