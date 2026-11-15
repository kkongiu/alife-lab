"""M6.2-E: preregistra e applica il rilevatore v2 ai 25 run M6.

`--preregister` scrive `campaigns/m6_2e/manifest.json` con criteri, parametri e
hash delle sorgenti. L'esecuzione riesegue i mondi M6 con le stesse
configurazioni e seed — non nuove leggi — e verifica che l'hash completo del
mondo coincida con quello registrato in M6: l'analisi è quindi sugli stessi
percorsi, non su run nuovi.

Uso:
    .venv/bin/python tools/reanalyze_m6_2e.py --preregister
    .venv/bin/python tools/reanalyze_m6_2e.py
    .venv/bin/python tools/reanalyze_m6_2e.py --force
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

from alife import __version__
from alife.config import load_config
from alife.metrics import git_commit, runtime_versions
from alife.replication import ReplicationDetector
from alife.replication_v2 import DETECTOR_VERSION, ProgressiveDetector
from alife.structures import Tracker
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
M6 = ROOT / "campaigns" / "m6"
CAMPAIGN = ROOT / "campaigns" / "m6_2e"
MANIFEST = CAMPAIGN / "manifest.json"
RESULTS = CAMPAIGN / "results.json"

CRITERIA = {
    "radius": 2,
    "window": 150,
    "persist_steps": 10,
    "min_size": 4,
    "min_copies": 5,
    "min_generation": 2,
}
DECISION_RULE = {
    "candidate_condition": "almeno 3 seed su 5 classificati 'replication' dal v2 e mediana delle copie persistenti >= 5",
    "otherwise": "nessuna evidenza di replicazione progressiva in questa ri-analisi",
    "control_check": "se 'closed' o 'unfed' risultano 'replication', il criterio v2 è invalido: REVISE",
    "world_check": "ogni run deve riprodurre l'hash completo del mondo registrato in M6",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preregister(force: bool) -> int:
    if MANIFEST.exists() and not force:
        print(f"preregistrazione già presente: {MANIFEST}")
        print("usare --force solo per una revisione esplicita")
        return 1
    m6_manifest = json.loads((M6 / "manifest.json").read_text(encoding="utf-8"))
    m6_results = json.loads((M6 / "results.json").read_text(encoding="utf-8"))
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    expected = {run["id"]: run["state_hash_full"] for run in m6_results["runs"]}

    runs = []
    for run in m6_manifest["runs"]:
        runs.append(
            {
                "id": run["id"],
                "condition": run["condition"],
                "seed": run["seed"],
                "config": run["config"],
                "config_hash": run["config_hash"],
                "expected_world_hash": expected[run["id"]],
            }
        )

    payload = {
        "campaign": "m6.2-e",
        "version": 1,
        "preregistered_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool_version": __version__,
        "git_commit": git_commit(ROOT),
        "versions": runtime_versions(),
        "detector_version": DETECTOR_VERSION,
        "criteria": CRITERIA,
        "source_campaign": "m6",
        "source_manifest_sha256": _sha256(M6 / "manifest.json"),
        "source_results_sha256": _sha256(M6 / "results.json"),
        "hypothesis": (
            "Verificare se il rilevatore v2, che riconosce copie che raggiungono "
            "progressivamente la firma di un template, trova candidati che il v1 "
            "(solo nascite complete) non poteva vedere. Nessun candidato è atteso; "
            "un candidato va trattato come ipotesi da verificare, non come risultato."
        ),
        "method": (
            "Riesecuzione deterministica dei 25 mondi M6 con le stesse configurazioni "
            "e seed; verifica dell'hash completo del mondo contro M6; v1 e v2 "
            "applicati agli stessi percorsi. Nessuna nuova legge."
        ),
        "decision_rule": DECISION_RULE,
        "runs": runs,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"preregistrazione scritta: {MANIFEST}")
    print(f"{len(runs)} run, criteri {CRITERIA}")
    return 0


def verify_manifest(manifest: dict) -> None:
    if manifest.get("detector_version") != DETECTOR_VERSION:
        raise SystemExit("manifest: versione del rilevatore diversa dal codice")
    if manifest.get("criteria") != CRITERIA:
        raise SystemExit("manifest: criteri diversi dal codice")
    if len(manifest.get("runs", [])) != 25:
        raise SystemExit("manifest: attesi 25 run")


def run_one(run: dict, steps: int) -> dict[str, Any]:
    config = load_config(M6 / run["config"])
    if config.hash() != run["config_hash"]:
        raise SystemExit(f"configurazione modificata: {run['config']}")

    world = World.create(config)
    tracker = Tracker()
    v1 = ReplicationDetector()
    v2 = ProgressiveDetector(**CRITERIA)

    def observe(current: World) -> None:
        tracker.observe(current)
        v1.observe(current, tracker)
        v2.observe(current, tracker)

    observe(world)
    world.advance(steps, observer=observe)

    hash_match = world.state_hash_full() == run["expected_world_hash"]
    v1_summary = v1.summary()
    v2_summary = v2.summary()
    return {
        "id": run["id"],
        "condition": run["condition"],
        "seed": run["seed"],
        "world_hash_match": hash_match,
        "world_hash": world.state_hash_full(),
        "v1": {
            "candidates": v1_summary["candidates"],
            "persistent": v1_summary["persistent"],
            "classified": v1_summary["classified"],
        },
        "v2": {
            "candidates": v2_summary["candidates"],
            "matched": v2_summary["matched"],
            "persistent": v2_summary["persistent"],
            "max_generation": v2_summary["max_generation"],
            "discarded": v2_summary["discarded"],
            "ambiguous_births": v2_summary["ambiguous_births"],
            "classified": v2_summary["classified"],
        },
    }


def aggregate(results: list[dict]) -> dict[str, Any]:
    conditions: dict[str, list[dict]] = {}
    for result in results:
        conditions.setdefault(result["condition"], []).append(result)
    summary = {}
    for name, runs in sorted(conditions.items()):
        v2_persistent = [run["v2"]["persistent"] for run in runs]
        v2_classified = sum(1 for run in runs if run["v2"]["classified"] == "replication")
        v1_classified = sum(1 for run in runs if run["v1"]["classified"] == "replication")
        summary[name] = {
            "runs": len(runs),
            "v1_classified": v1_classified,
            "v2_classified": v2_classified,
            "median_candidates": median(run["v2"]["candidates"] for run in runs),
            "median_matched": median(run["v2"]["matched"] for run in runs),
            "median_persistent": median(v2_persistent),
            "max_generation": max(run["v2"]["max_generation"] for run in runs),
            "candidate": v2_classified >= 3 and median(v2_persistent) >= 5,
        }
    return summary


def decide(aggregates: dict[str, Any]) -> dict[str, Any]:
    controls_ok = not aggregates.get("closed", {}).get("candidate", False) and not aggregates.get(
        "unfed", {}
    ).get("candidate", False)
    candidates = [name for name, block in aggregates.items() if block["candidate"]]
    if not controls_ok:
        verdict = "revise_controls"
    elif candidates:
        verdict = "candidate_for_s7"
    else:
        verdict = "no_evidence"
    return {
        "controls_ok": controls_ok,
        "candidate_conditions": candidates,
        "verdict": verdict,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="M6.2-E: rilevatore v2 sui run M6")
    parser.add_argument("--preregister", action="store_true")
    parser.add_argument("--force", action="store_true", help="riesegue la ri-analisi")
    args = parser.parse_args()

    if args.preregister:
        return preregister(args.force)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    verify_manifest(manifest)

    if RESULTS.exists() and not args.force:
        payload = json.loads(RESULTS.read_text(encoding="utf-8"))
        print(f"ri-analisi già presente: {RESULTS} (usare --force per rieseguire)")
    else:
        results = []
        for position, run in enumerate(manifest["runs"], start=1):
            print(f"[{position}/{len(manifest['runs'])}] {run['id']} …", flush=True)
            results.append(run_one(run, 3000))
        aggregates = aggregate(results)
        payload = {
            "campaign": "m6.2-e",
            "preregistered_utc": manifest["preregistered_utc"],
            "preregistration_commit": manifest["git_commit"],
            "run_commit": git_commit(ROOT),
            "detector_version": manifest["detector_version"],
            "criteria": manifest["criteria"],
            "source_campaign": manifest["source_campaign"],
            "runs": results,
            "conditions": aggregates,
            "decision": decide(aggregates),
            "all_world_hashes_match": all(run["world_hash_match"] for run in results),
        }
        RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print()
    print("| condizione | run | v1 replication | v2 candidate (mediana) | v2 persistenti (mediana) | v2 gen. max |")
    print("|---|---|---|---|---|---|")
    for name, block in payload["conditions"].items():
        print(
            f"| {name} | {block['runs']} | {block['v1_classified']} "
            f"| {block['median_candidates']} | {block['median_persistent']} "
            f"| {block['max_generation']} |"
        )
    print()
    print(f"hash del mondo identici a M6: {payload['all_world_hashes_match']}")
    print(f"verdetto: {payload['decision']['verdict']}")
    print(f"JSON: {RESULTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
