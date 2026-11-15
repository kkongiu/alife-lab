"""Esegue i controlli di M5 e produce `reports/controls.json`.

Il criterio del rilevatore è preregistrato in `alife/replication.py`. Lo script
esce con codice 0 solo se il positivo è classificato `replication` e ogni
negativo `not_replication`.

Uso: .venv/bin/python tools/run_controls.py [--out reports/controls.json]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from alife.controls import (
    FIXTURE_VERSION,
    TemplateCopier,
    negative_burst,
    negative_immobile,
    negative_random_aggregation,
    negative_reversible,
    negative_single_species,
    positive_world,
)
from alife.replication import ReplicationDetector
from alife.structures import Tracker

ROOT = Path(__file__).resolve().parents[1]


@dataclass(slots=True)
class Fixture:
    name: str
    expected: str
    steps: int
    builder: Callable[[], object]
    with_copier: bool = False


def run_fixture(fixture: Fixture) -> dict:
    world = fixture.builder()
    tracker = Tracker()
    detector = ReplicationDetector()
    copier = TemplateCopier.for_world(world) if fixture.with_copier else None

    tracker.observe(world)
    detector.observe(world, tracker)
    for _ in range(fixture.steps):
        if copier is not None:
            copier.step(world)
        world.advance(1)
        tracker.observe(world)
        detector.observe(world, tracker)

    tracker_summary = tracker.summary()
    detector_summary = detector.summary()
    return {
        "name": fixture.name,
        "expected": fixture.expected,
        "steps": fixture.steps,
        "structures": tracker_summary["active_structures"],
        "births": tracker_summary["events"].get("birth", 0),
        "copies_made_by_fixture": copier.copies if copier is not None else 0,
        "detector": detector_summary,
        "ok": detector_summary["classified"] == fixture.expected,
        "world_hash": world.state_hash_full(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Controlli positivi e negativi M5")
    parser.add_argument("--out", default=str(ROOT / "reports" / "controls.json"))
    args = parser.parse_args()

    fixtures = [
        Fixture("positivo-template", "replication", 40, positive_world, with_copier=True),
        Fixture("N1-immobile", "not_replication", 100, negative_immobile),
        Fixture("N2-aggregazione-casuale", "not_replication", 1000, negative_random_aggregation),
        Fixture("N3-reazioni-reversibili", "not_replication", 1000, negative_reversible),
        Fixture("stress-specie-unica", "not_replication", 1000, negative_single_species),
        Fixture("stress-formazione-massima", "not_replication", 1000, negative_burst),
    ]

    results = [run_fixture(fixture) for fixture in fixtures]
    payload = {
        "fixture_version": FIXTURE_VERSION,
        "criteria": results[0]["detector"]["criteria"],
        "fixtures": results,
        "ok": all(result["ok"] for result in results),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("| fixture | strutture | nascite | copie | persistenti | max gen | esito | atteso |")
    print("|---|---|---|---|---|---|---|---|")
    for result in results:
        detector = result["detector"]
        print(
            f"| {result['name']} | {result['structures']} | {result['births']} "
            f"| {detector['candidates']} | {detector['persistent']} "
            f"| {detector['max_generation']} | {detector['classified']} "
            f"| {result['expected']} |"
        )
    print()
    print("tutti i controlli superati" if payload["ok"] else "CONTROLLI NON SUPERATI")
    print(f"JSON: {out}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
