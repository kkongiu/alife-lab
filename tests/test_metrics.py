"""Metriche: picco di memoria, versioni, riepilogo finale."""

from __future__ import annotations

import json

from alife.metrics import MetricsRecorder, peak_memory_bytes, runtime_versions
from alife.world import World
from support import make_config


def test_peak_memory_is_plausible() -> None:
    value = peak_memory_bytes()
    assert 1_000_000 < value < 64 * 1024**3


def test_runtime_versions_are_recorded() -> None:
    versions = runtime_versions()
    assert {"python", "numpy", "platform", "machine"} <= set(versions)
    assert versions["python"].count(".") >= 1


def test_summary_contains_required_fields(tmp_path) -> None:
    world = World.create(make_config(seed=21))
    recorder = MetricsRecorder(tmp_path, every=2)
    try:
        recorder.observe(world)
        world.advance(6, observer=recorder.observe)
        summary = recorder.summary(world)
    finally:
        recorder.close()

    required = {
        "steps",
        "moves_total",
        "particles",
        "occupancy",
        "energy",
        "duration_s",
        "steps_per_second",
        "peak_memory_bytes",
        "simulation_memory_bytes",
        "state_hash",
        "seed",
        "config_hash",
        "config_schema_version",
        "versions",
        "invariants",
    }
    assert required <= set(summary)
    assert summary["steps"] == 6
    assert summary["energy"]["delta"] == 0
    assert summary["energy"]["identity_delta"] == 0
    assert summary["energy"]["injected"] == 0
    assert summary["energy"]["dissipated"] == 0
    assert summary["state_hash_full"] != summary["state_hash"]
    assert summary["invariants"] == "ok"
    assert summary["config_hash"] == world.config.hash()

    records = [json.loads(line) for line in (tmp_path / "metrics.jsonl").read_text().splitlines()]
    assert [record["step"] for record in records] == [0, 2, 4, 6]
    for record in records:
        assert record["particles"] == {"A": 12, "B": 8}
        assert record["energy_in"] == 0
        assert record["energy_out"] == 0
