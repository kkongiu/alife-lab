"""M6: persistenza e ripristino dello stato di analisi (tracker + rilevatore)."""

from __future__ import annotations

import json

import pytest

from alife.analysis import Analysis, AnalysisError
from alife.config import load_config
from alife.world import World
from support import M3_QUICK


def _analyse(world: World, steps: int, out_dir=None) -> Analysis:
    analysis = Analysis(out_dir)
    analysis.observe(world)
    world.advance(steps, observer=analysis.observe)
    return analysis


def test_roundtrip_preserves_state(tmp_path) -> None:
    world = World.create(load_config(M3_QUICK))
    analysis = _analyse(world, 40)
    path = analysis.save(tmp_path / "analysis.json")

    restored = Analysis.load(path)
    assert restored.tracker.summary() == analysis.tracker.summary()
    assert restored.detector.summary() == analysis.detector.summary()
    assert restored.tracker.last_step == world.step


def test_restore_requires_matching_step(tmp_path) -> None:
    world = World.create(load_config(M3_QUICK))
    analysis = _analyse(world, 10)
    restored = Analysis.load(analysis.save(tmp_path / "analysis.json"))
    with pytest.raises(AnalysisError, match="passo"):
        restored.check_step(world.step + 1)


def test_resume_matches_continuous_run(tmp_path) -> None:
    config = load_config(M3_QUICK)

    continuous_world = World.create(config)
    continuous = _analyse(continuous_world, 60)

    split_world = World.create(config)
    split = _analyse(split_world, 20)
    path = split.save(tmp_path / "analysis.json")
    split.close()

    resumed = Analysis.load(path)
    resumed.check_step(split_world.step)
    split_world.advance(40, observer=resumed.observe)

    assert split_world.state_hash_full() == continuous_world.state_hash_full()
    assert resumed.tracker.summary() == continuous.tracker.summary()
    assert resumed.detector.summary() == continuous.detector.summary()


def test_invalid_format_is_rejected(tmp_path) -> None:
    path = tmp_path / "analysis.json"
    path.write_text(json.dumps({"format": "altro"}))
    with pytest.raises(AnalysisError, match="formato"):
        Analysis.load(path)


def test_missing_file_is_rejected(tmp_path) -> None:
    with pytest.raises(AnalysisError, match="non trovato"):
        Analysis.load(tmp_path / "assente.json")
