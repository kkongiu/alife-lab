"""Interfaccia a riga di comando: run, resume, inspect."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from alife.config import load_config
from alife.persistence import load_checkpoint
from alife.world import World
from support import M2_QUICK, QUICK, ROOT


def _cli(args: list[str], cwd) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "alife", *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def _reference(steps: int) -> dict:
    world = World.create(load_config(QUICK))
    world.advance(steps)
    return world.snapshot()


def test_run_produces_artifacts(tmp_path) -> None:
    out = tmp_path / "run"
    result = _cli(["run", "--config", str(QUICK), "--steps", "20", "--out", str(out)], tmp_path)
    assert result.returncode == 0, result.stderr
    for name in (
        "config.resolved.json",
        "manifest.json",
        "metrics.jsonl",
        "checkpoint.json",
        "summary.json",
    ):
        assert (out / name).is_file()

    summary = json.loads((out / "summary.json").read_text())
    assert summary["steps"] == 20
    assert summary["config_hash"] == load_config(QUICK).hash()
    assert summary["energy"]["delta"] == 0
    assert summary["invariants"] == "ok"
    assert summary["state_hash"] == _reference(20)["state_hash"]

    records = [json.loads(line) for line in (out / "metrics.jsonl").read_text().splitlines()]
    assert records[0]["step"] == 0
    assert records[-1]["step"] == 20


def test_resume_matches_continuous_run(tmp_path) -> None:
    first = tmp_path / "first"
    result = _cli(["run", "--config", str(QUICK), "--steps", "15", "--out", str(first)], tmp_path)
    assert result.returncode == 0, result.stderr

    result = _cli(
        ["resume", "--checkpoint", str(first / "checkpoint.json"), "--steps", "15"],
        tmp_path,
    )
    assert result.returncode == 0, result.stderr

    resumed = load_checkpoint(first / "resume" / "checkpoint.json")
    assert resumed.step == 30
    assert resumed.state_hash() == _reference(30)["state_hash"]


def test_seed_override(tmp_path) -> None:
    out = tmp_path / "seed"
    result = _cli(
        ["run", "--config", str(QUICK), "--steps", "5", "--seed", "999", "--out", str(out)],
        tmp_path,
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads((out / "summary.json").read_text())
    assert summary["seed"] == 999
    assert summary["config_hash"] != load_config(QUICK).hash()


def test_inspect_reads_checkpoint(tmp_path) -> None:
    out = tmp_path / "run"
    assert _cli(["run", "--config", str(QUICK), "--steps", "6", "--out", str(out)], tmp_path).returncode == 0
    result = _cli(["inspect", "--checkpoint", str(out / "checkpoint.json")], tmp_path)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["step"] == 6
    assert payload["invariants"] == "ok"


def test_negative_steps_rejected(tmp_path) -> None:
    result = _cli(["run", "--config", str(QUICK), "--steps", "-5", "--out", str(tmp_path / "x")], tmp_path)
    assert result.returncode == 2
    assert "--steps" in result.stderr


def test_invalid_config_reports_error(tmp_path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text('{"seed": 1}')
    result = _cli(["run", "--config", str(broken), "--steps", "1", "--out", str(tmp_path / "x")], tmp_path)
    assert result.returncode == 2
    assert "errore" in result.stderr


@pytest.mark.parametrize("command", [["--version"]])
def test_version(command) -> None:
    result = _cli(command, ROOT)
    assert result.returncode == 0
    assert "alife" in result.stdout


# --- M2: chimica, eventi, ripresa ------------------------------------------


def test_run_m2_writes_events_and_checkpoint(tmp_path) -> None:
    out = tmp_path / "m2"
    result = _cli(
        ["run", "--config", str(M2_QUICK), "--steps", "20", "--out", str(out), "--events"],
        tmp_path,
    )
    assert result.returncode == 0, result.stderr

    events = [json.loads(line) for line in (out / "events.jsonl").read_text().splitlines()]
    assert events
    assert {event["kind"] for event in events} <= {"form", "break"}
    assert all({"step", "id_a", "id_b", "energy", "catalyzed"} <= set(event) for event in events)

    summary = json.loads((out / "summary.json").read_text())
    assert summary["chemistry"]["enabled"] is True
    assert summary["chemistry"]["bonds"] > 0
    assert summary["energy"]["delta"] == 0
    assert summary["state_hash_full"] != summary["state_hash"]

    restored = load_checkpoint(out / "checkpoint.json")
    assert restored.state_hash_full() == summary["state_hash_full"]


def test_m2_resume_matches_continuous_run(tmp_path) -> None:
    first = tmp_path / "m2a"
    result = _cli(["run", "--config", str(M2_QUICK), "--steps", "15", "--out", str(first)], tmp_path)
    assert result.returncode == 0, result.stderr

    result = _cli(
        ["resume", "--checkpoint", str(first / "checkpoint.json"), "--steps", "15"],
        tmp_path,
    )
    assert result.returncode == 0, result.stderr

    resumed = load_checkpoint(first / "resume" / "checkpoint.json")
    assert resumed.step == 30

    reference = World.create(load_config(M2_QUICK))
    reference.advance(30)
    assert resumed.state_hash_full() == reference.state_hash_full()
    assert resumed.store.bond_records() == reference.store.bond_records()
