"""Aggregate five independent M6.2-B seed artifacts without tuning criteria."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median


def aggregate(folder: Path, protocol_path: Path) -> dict:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    seeds = protocol["seeds"]
    names = list(protocol["arms"])
    items = []
    for seed in seeds:
        path = folder / f"run-{seed}.json"
        if not path.is_file():
            raise ValueError(f"missing preregistered seed result: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["campaign"] != "m6.2-b" or data["seed"] != seed:
            raise ValueError(f"wrong campaign/seed in {path}")
        if data["steps"] != protocol["steps"]:
            raise ValueError(f"wrong step count in {path}")
        if [arm["arm"] for arm in data["arms"]] != names:
            raise ValueError(f"arm names/order differ in {path}")
        if not all(a["world_invariants_valid"] for a in data["arms"]):
            raise ValueError(f"world invariant invalid in {path}")
        off = data["arms"][0]
        expected = next(r for r in protocol["source_runs"] if r["seed"] == seed)
        if off["world_hash"] != expected["expected_off_world_hash"] or not off.get("reproduces_M6_world_hash"):
            raise ValueError(f"M6 baseline mismatch in {path}")
        if not all(a["v21"]["version"] == protocol["detector"] for a in data["arms"]):
            raise ValueError(f"detector version mismatch in {path}")
        items.append(data)

    compared = {}
    for index, name in enumerate(names):
        values = [entry["arms"][index]["target_S0_S1_formations"] for entry in items]
        baseline = [entry["arms"][0]["target_S0_S1_formations"] for entry in items]
        deltas = [v - v0 for v, v0 in zip(values, baseline)]
        criterion = name != "off" and sum(d > 0 for d in deltas) >= 4 and median(deltas) > 0
        compared[name] = {
            "target_formations_by_seed": dict(zip((str(s) for s in seeds), values)),
            "delta_vs_off_by_seed": dict(zip((str(s) for s in seeds), deltas)),
            "median_target_formations": median(values),
            "median_paired_delta": median(deltas),
            "seeds_with_increase": sum(d > 0 for d in deltas),
            "kinetic_effect_criterion_met": criterion,
            "catalyzed_target_formations": sum(
                entry["arms"][index]["target_S0_S1_catalyzed"] for entry in items
            ),
            "total_matched_copy_candidates_v21": sum(
                entry["arms"][index]["v21"]["matched"] for entry in items
            ),
            "total_persistent_copy_candidates_v21": sum(
                entry["arms"][index]["v21"]["persistent"] for entry in items
            ),
        }
    return {
        "campaign": "m6.2-b",
        "protocol_version": 1,
        "steps_per_run": protocol["steps"],
        "seeds": seeds,
        "worlds": len(seeds) * len(names),
        "arms": compared,
        "all_original_m6_off_hashes_reproduced": True,
        "scientific_scope": (
            "Paired kinetic effects of explicit catalysis; NO causal structural "
            "replication or self-catalytic amplification has been demonstrated."
        ),
    }


def report(result: dict) -> str:
    lines = [
        "# M6.2-B — Catalisi locale: risultati preregistrati",
        "",
        "Le 15 simulazioni utilizzano la stessa chimica M6 fed-mid, con la sola "
        "aggiunta configurabile di una regola catalitica per le condizioni attive.",
        "",
        "| Braccio | Mediana S0-S1 formati | Delta mediano vs off | Seed in aumento | Criterio cinetico |",
        "|---|---:|---:|---:|---|",
    ]
    for name, x in result["arms"].items():
        lines.append(
            f"| {name} | {x['median_target_formations']} | "
            f"{x['median_paired_delta']:+} | {x['seeds_with_increase']}/5 | "
            f"{'sì' if x['kinetic_effect_criterion_met'] else 'no'} |"
        )
    lines += [
        "",
        "## Criteri e limiti",
        "",
        "- Predefiniti: mediana del delta positiva e aumento in almeno 4/5 seed.",
        "- I cinque seed sono accoppiati, ma le traiettorie divergono dopo l'attivazione della catalisi.",
        "- Il catalizzatore S3 è esterno al prodotto; S0 è un componente del prodotto, ma il suo numero è conservato.",
        "- Non è stato effettuato un vero controllo shuffled senza cambiare le leggi.",
        "- La somiglianza di forme rilevata da v2.1 non è una prova di copiatura causale.",
        "- Energia e invarianti verificati alla fine di ogni run; baseline off identico a M6.",
        "",
        "## Risultati completi",
        "",
        "Vedi il file JSON allegato alla stessa esecuzione GitHub Actions.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, default=Path("campaigns/m6_2b/protocol.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = aggregate(args.input_dir, args.protocol)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "report.md").write_text(report(result), encoding="utf-8")
    print(report(result))


if __name__ == "__main__":
    main()
