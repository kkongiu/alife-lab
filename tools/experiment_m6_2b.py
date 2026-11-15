"""M6.2-B: preregistered, paired catalysis experiment; no physics changes.

Usage: python tools/experiment_m6_2b.py --seed 6101 --output /tmp/run-6101.json

Each arm starts a FRESH world from the original M6 fed-mid seed. Compare the
total S0-S1 formation events with the same original configuration except for
one catalysis rule. No claims of autocatalysis or structural replication.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from alife.chemistry import aggregate_stats
from alife.config import Config
from alife.replication_v21 import ProgressiveDetector
from alife.structures import Tracker
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "campaigns" / "m6_2b" / "protocol.json"
M6_DIR = ROOT / "campaigns" / "m6"


class BondCounter:
    """Read-only event sink for event-count outcomes, independent of tracking."""

    def __init__(self, world: World) -> None:
        self.world = world
        self.formations = 0
        self.breaks = 0
        self.target_formations = 0
        self.target_catalyzed = 0

    def emit(self, event) -> None:
        if event.kind == "break":
            self.breaks += 1
            return
        if event.kind != "form":
            return
        self.formations += 1
        store = self.world.store
        pair = {
            self.world.species_names[store.species[store.index_of(event.id_a)]],
            self.world.species_names[store.species[store.index_of(event.id_b)]],
        }
        if pair == {"S0", "S1"}:
            self.target_formations += 1
            self.target_catalyzed += int(event.catalyzed)


def config_for_run(run: dict, rules: list[dict]) -> Config:
    raw = json.loads((M6_DIR / run["config"]).read_text(encoding="utf-8"))
    assert raw["seed"] == run["seed"], "source seed must be unchanged"
    assert raw["chemistry"]["catalysis"] == [], "source must be uncatalyzed M6 fed-mid"
    raw["chemistry"]["catalysis"] = rules
    config = Config.from_dict(raw).validate()
    if not rules:
        assert config.hash() == run["config_hash"], "M6 base config changed"
    return config


def run_one(run: dict, arm: str, rules: list[dict], steps: int) -> dict:
    config = config_for_run(run, rules)
    world = World.create(config)
    tracker = Tracker()
    detector = ProgressiveDetector()
    sink = BondCounter(world)
    world.event_sink = sink

    def observe(current: World) -> None:
        tracker.observe(current)
        detector.observe(current, tracker)

    observe(world)
    world.advance(steps, observer=observe)
    world.check()
    signature = detector.summary()
    result = {
        "arm": arm,
        "seed": run["seed"],
        "steps": steps,
        "config_hash": config.hash(),
        "world_hash": world.state_hash_full(),
        "formations": sink.formations,
        "breaks": sink.breaks,
        "target_S0_S1_formations": sink.target_formations,
        "target_S0_S1_catalyzed": sink.target_catalyzed,
        "active_structures": len(tracker.active),
        "aggregate_stats": aggregate_stats(world.store),
        "v21": {
            "version": signature["version"],
            "candidates": signature["candidates"],
            "matched": signature["matched"],
            "persistent": signature["persistent"],
            "classified": signature["classified"],
            "max_generation": signature["max_generation"],
        },
        "energy": {
            "final": world.energy(),
            "injected": world.injected,
            "dissipated": world.dissipated,
            "unabsorbed": world.unabsorbed,
        },
        "world_invariants_valid": True,
    }
    if steps == 3000 and arm == "off":
        if result["world_hash"] != run["expected_off_world_hash"]:
            raise AssertionError("M6 off baseline world hash changed")
        result["reproduces_M6_world_hash"] = True
    return result


def run_seed(seed: int, *, steps_override: int | None = None) -> dict:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    assert protocol["campaign"] == "m6.2-b"
    assert protocol["protocol_version"] == 1
    assert seed in protocol["seeds"]
    run = next(item for item in protocol["source_runs"] if item["seed"] == seed)
    steps = protocol["steps"] if steps_override is None else steps_override
    arms = [
        run_one(run, arm, rules, steps)
        for arm, rules in protocol["arms"].items()
    ]
    return {
        "campaign": protocol["campaign"],
        "protocol_version": protocol["protocol_version"],
        "seed": seed,
        "steps": steps,
        "arms": arms,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=None, help="diagnostics only; published trial is 3000")
    args = parser.parse_args()
    if args.steps is not None and args.steps <= 0:
        parser.error("--steps must be positive")
    result = run_seed(args.seed, steps_override=args.steps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("M6.2-B seed", args.seed)
    for arm in result["arms"]:
        print(
            f"  {arm['arm']:20} S0-S1 formations={arm['target_S0_S1_formations']:5d}"
            f" catalyzed={arm['target_S0_S1_catalyzed']:5d}"
            f" v2.1 persistent={arm['v21']['persistent']}"
        )
    print("Saved:", args.output)


if __name__ == "__main__":
    main()
