"""M6.2-E: preregistrazione e risultati della ri-analisi con il rilevatore v2."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from alife.config import load_config
from support import ROOT

CAMPAIGN = Path(ROOT) / "campaigns" / "m6_2e"
MANIFEST = CAMPAIGN / "manifest.json"
RESULTS = CAMPAIGN / "results.json"
M6 = Path(ROOT) / "campaigns" / "m6"

EXPECTED_CRITERIA = {
    "radius": 2,
    "window": 150,
    "persist_steps": 10,
    "min_size": 4,
    "min_copies": 5,
    "min_generation": 2,
}


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_freezes_v2_criteria() -> None:
    manifest = _manifest()
    assert manifest["campaign"] == "m6.2-e"
    assert manifest["detector_version"] == "v2"
    assert manifest["criteria"] == EXPECTED_CRITERIA
    assert len(manifest["runs"]) == 25


def test_manifest_references_identical_m6_runs() -> None:
    manifest = _manifest()
    m6_manifest = json.loads((M6 / "manifest.json").read_text(encoding="utf-8"))
    m6_results = json.loads((M6 / "results.json").read_text(encoding="utf-8"))
    expected = {run["id"]: run["state_hash_full"] for run in m6_results["runs"]}
    m6_configs = {run["id"]: run for run in m6_manifest["runs"]}

    for run in manifest["runs"]:
        source = m6_configs[run["id"]]
        assert run["config_hash"] == source["config_hash"]
        assert run["expected_world_hash"] == expected[run["id"]]
        config = load_config(M6 / run["config"])
        assert config.hash() == run["config_hash"]


@pytest.mark.skipif(not RESULTS.exists(), reason="ri-analisi non ancora eseguita")
def test_reanalysis_is_complete_and_matches_m6_worlds() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    assert results["campaign"] == "m6.2-e"
    assert results["detector_version"] == "v2"
    assert len(results["runs"]) == 25
    assert results["all_world_hashes_match"] is True
    assert results["decision"]["verdict"] in {
        "no_evidence",
        "candidate_for_s7",
        "revise_controls",
    }
    for run in results["runs"]:
        assert run["world_hash_match"] is True
        assert set(run["v1"]) == {"candidates", "persistent", "classified"}
        assert {"candidates", "matched", "persistent", "classified"} <= set(run["v2"])
