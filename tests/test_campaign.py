"""M6: integrità della preregistrazione e copertura della campagna."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from alife.config import load_config
from support import ROOT

CAMPAIGN = Path(ROOT) / "campaigns" / "m6"
MANIFEST = CAMPAIGN / "manifest.json"
RESULTS = CAMPAIGN / "results.json"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_is_preregistered() -> None:
    manifest = _manifest()
    assert manifest["campaign"] == "m6"
    assert manifest["version"] == 1
    assert manifest["steps"] == 3000
    assert manifest["seeds"] == [6101, 6102, 6103, 6104, 6105]
    assert len(manifest["runs"]) == 25
    assert len({run["id"] for run in manifest["runs"]}) == 25
    assert len({run["config_hash"] for run in manifest["runs"]}) == 25
    assert {run["condition"] for run in manifest["runs"]} == {
        "closed",
        "unfed",
        "fed-low",
        "fed-mid",
        "fed-high",
    }


def test_manifest_configs_match_their_hashes() -> None:
    manifest = _manifest()
    for run in manifest["runs"]:
        config = load_config(CAMPAIGN / run["config"])
        assert config.hash() == run["config_hash"], run["config"]
        assert config.seed == run["seed"]
        assert config.schema_version == 3


def test_manifest_records_the_decision_rule() -> None:
    manifest = _manifest()
    rule = manifest["decision_rule"]
    assert "candidate_condition" in rule
    assert "otherwise" in rule
    assert "control_check" in rule
    assert manifest["detector"]["min_size"] == 4
    assert manifest["detector"]["min_generation"] == 2


@pytest.mark.skipif(not RESULTS.exists(), reason="campagna non ancora eseguita")
def test_campaign_results_are_complete() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    runs = results["runs"]
    if len(runs) != 25:
        pytest.skip("campagna in corso o incompleta")
    assert {run["condition"] for run in runs} == {
        "closed",
        "unfed",
        "fed-low",
        "fed-mid",
        "fed-high",
    }
    assert all(run["steps"] == 3000 for run in runs)
    assert len({run["state_hash_full"] for run in runs}) == 25
    # i run nulli sono registrati come tali, non omessi
    assert any(run["replication"]["persistent"] == 0 for run in runs)
    assert results["decision"]["verdict"] in {
        "no_evidence",
        "candidate_for_s7",
        "revise_controls",
    }
