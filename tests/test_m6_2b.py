"""Protocol and small smoke checks for M6.2-B (no expensive campaign in pytest)."""

from __future__ import annotations

import json
from pathlib import Path

from alife.config import load_config
from alife.world import World
from tools.aggregate_m6_2b import aggregate
from tools.experiment_m6_2b import PROTOCOL_PATH, M6_DIR, config_for_run, run_seed


def _protocol():
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def test_m6_2b_protocol_is_fixed_before_full_campaign() -> None:
    p = _protocol()
    assert p["campaign"] == "m6.2-b"
    assert p["protocol_version"] == 1
    assert p["steps"] == 3000
    assert p["seeds"] == [6101, 6102, 6103, 6104, 6105]
    assert list(p["arms"]) == ["off", "external_S3", "incorporated_S0"]
    assert p["arms"]["off"] == []
    assert p["arms"]["external_S3"] == [
        {"catalyst": "S3", "pair": ["S0", "S1"], "factor": 5.0}
    ]
    assert p["arms"]["incorporated_S0"] == [
        {"catalyst": "S0", "pair": ["S0", "S1"], "factor": 5.0}
    ]
    assert p["detector"] == "v2.1"
    assert len(p["source_runs"]) == 5


def test_catalysis_conditions_change_only_catalysis() -> None:
    p = _protocol()
    for run in p["source_runs"]:
        baseline = load_config(M6_DIR / run["config"])
        assert baseline.hash() == run["config_hash"]
        for rules in p["arms"].values():
            config = config_for_run(run, rules)
            d = config.to_dict()
            base = baseline.to_dict()
            d["chemistry"]["catalysis"] = []
            assert d == base


def test_short_trial_is_deterministic_and_keeps_m6_off_world() -> None:
    p = _protocol()
    seed = 6101
    result = run_seed(seed, steps_override=10)
    again = run_seed(seed, steps_override=10)
    assert result == again
    assert len(result["arms"]) == 3
    assert all(a["world_invariants_valid"] for a in result["arms"])
    run = next(x for x in p["source_runs"] if x["seed"] == seed)
    original = World.create(load_config(M6_DIR / run["config"]))
    original.advance(10)
    assert original.state_hash_full() == result["arms"][0]["world_hash"]
    assert all(a["v21"]["version"] == "v2.1" for a in result["arms"])


def test_aggregator_requires_all_seeds_and_paired_effects(tmp_path: Path) -> None:
    p = _protocol()
    for run in p["source_runs"]:
        seed = run["seed"]
        arms = []
        for name, value in (("off", 10), ("external_S3", 20), ("incorporated_S0", 12)):
            arms.append({
                "arm": name,
                "world_hash": run["expected_off_world_hash"] if name == "off" else "synthetic",
                "reproduces_M6_world_hash": name == "off",
                "target_S0_S1_formations": value,
                "target_S0_S1_catalyzed": 0 if name == "off" else 4,
                "world_invariants_valid": True,
                "v21": {"version": "v2.1", "matched": 0, "persistent": 0},
            })
        (tmp_path / f"run-{seed}.json").write_text(
            json.dumps({
                "campaign": "m6.2-b",
                "seed": seed,
                "steps": 3000,
                "arms": arms,
            }),
            encoding="utf-8",
        )
    result = aggregate(tmp_path, PROTOCOL_PATH)
    assert result["worlds"] == 15
    assert result["all_original_m6_off_hashes_reproduced"]
    assert result["arms"]["external_S3"]["median_paired_delta"] == 10
    assert result["arms"]["external_S3"]["kinetic_effect_criterion_met"] is True
    assert result["arms"]["incorporated_S0"]["kinetic_effect_criterion_met"] is True
    (tmp_path / "run-6105.json").unlink()
    try:
        aggregate(tmp_path, PROTOCOL_PATH)
    except ValueError as error:
        assert "missing preregistered seed" in str(error)
    else:
        raise AssertionError("An incomplete campaign must fail")
