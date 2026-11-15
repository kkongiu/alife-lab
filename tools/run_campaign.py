"""Esegue la campagna M6 preregistrata.

Verifica che ogni configurazione corrisponda all'hash del manifest, esegue i run
mancanti, salva tutti i risultati (compresi quelli nulli) e applica la regola di
decisione preregistrata. È riavviabile: i run con `summary.json` già presente
vengono saltati, salvo `--force`.

Uso: .venv/bin/python tools/run_campaign.py [--limit N] [--force] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from statistics import median
from typing import Any

from alife.analysis import Analysis
from alife.cli import _execute
from alife.config import load_config
from alife.metrics import git_commit, runtime_versions
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "campaigns" / "m6"
RUNS_DIR = ROOT / "runs" / "m6"


def load_manifest() -> dict:
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("campaign") != "m6":
        raise SystemExit("manifest: campagna inattesa")
    if not manifest.get("runs"):
        raise SystemExit("manifest: nessun run")
    return manifest


def verify_configs(manifest: dict) -> None:
    for run in manifest["runs"]:
        config = load_config(CAMPAIGN / run["config"])
        if config.hash() != run["config_hash"]:
            raise SystemExit(
                f"configurazione modificata dopo la preregistrazione: {run['config']}"
            )
        if config.seed != run["seed"]:
            raise SystemExit(f"seed incoerente in {run['config']}")


def engine_unchanged(commit: str | None) -> bool | None:
    if not commit:
        return None
    result = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--quiet", commit, "--", "src/alife"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def run_one(run: dict, steps: int) -> dict[str, Any]:
    condition = run["condition"]
    seed = run["seed"]
    out_dir = RUNS_DIR / condition / f"seed-{seed}"
    summary_path = out_dir / "summary.json"

    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    else:
        config = load_config(CAMPAIGN / run["config"])
        world = World.create(config)
        analysis = Analysis(out_dir)
        summary = _execute(
            world,
            steps,
            out_dir,
            config.metrics.every,
            "campaign",
            {
                "campaign": "m6",
                "run": run["id"],
                "condition": condition,
                "seed": seed,
                "config_hash": run["config_hash"],
            },
            track=True,
            analysis=analysis,
        )

    structures = summary["structures"]
    events = structures["events"]
    replication = summary["replication"]
    return {
        "id": run["id"],
        "condition": condition,
        "seed": seed,
        "config_hash": run["config_hash"],
        "steps": summary["steps"],
        "duration_s": summary["duration_s"],
        "steps_per_second": summary["steps_per_second"],
        "energy": {
            "internal": summary["energy"]["internal"],
            "initial": summary["energy"]["initial"],
            "injected": summary["energy"]["injected"],
            "dissipated": summary["energy"]["dissipated"],
            "unabsorbed": summary["energy"]["unabsorbed"],
            "identity_delta": summary["energy"]["identity_delta"],
        },
        "structures": {
            "active": structures["active_structures"],
            "births": events.get("birth", 0),
            "deaths": events.get("death", 0),
            "splits": events.get("split", 0),
            "merges": events.get("merge", 0),
            "transforms": events.get("transform", 0),
            "lifetime_mean": structures["lifetime"]["mean"],
            "lifetime_max": structures["lifetime"]["max"],
            "distinct_signatures": structures["signatures"]["distinct"],
            "ambiguous_steps": structures["signatures"]["ambiguous_steps"],
            "ambiguous_structures": structures["signatures"]["ambiguous_structures"],
        },
        "replication": {
            "candidates": replication["candidates"],
            "persistent": replication["persistent"],
            "unresolved": replication["unresolved"],
            "max_generation": replication["max_generation"],
            "max_generation_all": replication["max_generation_all"],
            "classified": replication["classified"],
        },
        "state_hash_full": summary["state_hash_full"],
    }


def aggregate(results: list[dict]) -> dict[str, Any]:
    conditions: dict[str, list[dict]] = {}
    for result in results:
        conditions.setdefault(result["condition"], []).append(result)

    summary: dict[str, Any] = {}
    for name, runs in sorted(conditions.items()):
        classified = sum(1 for run in runs if run["replication"]["classified"] == "replication")
        persistent = [run["replication"]["persistent"] for run in runs]
        summary[name] = {
            "runs": len(runs),
            "classified_replication": classified,
            "median_persistent_copies": median(persistent) if persistent else 0,
            "max_generation": max(run["replication"]["max_generation"] for run in runs),
            "median_structures": median(run["structures"]["active"] for run in runs),
            "median_lifetime_mean": median(run["structures"]["lifetime_mean"] for run in runs),
            "median_ambiguous_steps": median(
                run["structures"]["ambiguous_steps"] for run in runs
            ),
            "candidate": classified >= 3 and (median(persistent) if persistent else 0) >= 5,
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
    parser = argparse.ArgumentParser(description="Esegue la campagna M6 preregistrata")
    parser.add_argument("--limit", type=int, default=None, help="esegue solo i primi N run")
    parser.add_argument("--force", action="store_true", help="riesegue anche i run completati")
    parser.add_argument("--dry-run", action="store_true", help="mostra la matrice senza eseguire")
    args = parser.parse_args()

    manifest = load_manifest()
    verify_configs(manifest)

    runs = manifest["runs"][: args.limit] if args.limit else manifest["runs"]
    if args.dry_run:
        print(f"{len(runs)} run da eseguire, {manifest['steps']} passi ciascuno")
        for run in runs:
            print(f"  {run['id']:<16} {run['config']}")
        return 0

    if args.force:
        for run in runs:
            summary = RUNS_DIR / run["condition"] / f"seed-{run['seed']}" / "summary.json"
            if summary.exists():
                summary.unlink()

    results = []
    for position, run in enumerate(runs, start=1):
        print(f"[{position}/{len(runs)}] {run['id']} …", flush=True)
        results.append(run_one(run, manifest["steps"]))

    aggregates = aggregate(results)
    decision = decide(aggregates)
    payload = {
        "campaign": "m6",
        "manifest_version": manifest["version"],
        "preregistered_utc": manifest["preregistered_utc"],
        "preregistration_commit": manifest.get("git_commit"),
        "run_commit": git_commit(ROOT),
        "engine_unchanged_since_preregistration": engine_unchanged(
            manifest.get("git_commit")
        ),
        "versions": runtime_versions(),
        "steps": manifest["steps"],
        "runs": results,
        "conditions": aggregates,
        "decision": decision,
    }
    out = CAMPAIGN / "results.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print()
    print("| condizione | run | replication | copie pers. (mediana) | gen. max | strutture (mediana) |")
    print("|---|---|---|---|---|---|")
    for name, block in aggregates.items():
        print(
            f"| {name} | {block['runs']} | {block['classified_replication']} "
            f"| {block['median_persistent_copies']} | {block['max_generation']} "
            f"| {block['median_structures']} |"
        )
    print()
    print(f"verdetto: {decision['verdict']}")
    print(f"JSON: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
