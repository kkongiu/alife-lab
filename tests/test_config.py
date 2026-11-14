"""Validazione e hashing canonico della configurazione."""

from __future__ import annotations

import json

import pytest

from alife.config import Config, ConfigError, load_config
from support import BASELINE, make_config


def test_baseline_config_is_valid() -> None:
    config = load_config(BASELINE)
    assert config.grid.width == 128
    assert config.grid.height == 128
    assert len(config.species) == 6
    assert sum(species.count for species in config.species) == 1638


def test_roundtrip_preserves_hash() -> None:
    config = make_config()
    again = Config.from_dict(config.to_dict()).validate()
    assert again == config
    assert again.hash() == config.hash()


def test_hash_is_independent_of_key_order() -> None:
    raw = json.loads(BASELINE.read_text())
    reordered = dict(reversed(list(raw.items())))
    assert Config.from_dict(raw).hash() == Config.from_dict(reordered).hash()


def test_hash_changes_with_seed() -> None:
    assert make_config(seed=1).hash() != make_config(seed=2).hash()


def test_unknown_key_rejected() -> None:
    raw = json.loads(BASELINE.read_text())
    raw["species"][0]["colour"] = "red"
    with pytest.raises(ConfigError, match="chiavi sconosciute"):
        Config.from_dict(raw)


def test_duplicate_species_names_rejected() -> None:
    with pytest.raises(ConfigError, match="duplicati"):
        make_config(
            species=[
                {"name": "A", "count": 1, "move_probability": 0.5, "energy": 1},
                {"name": "A", "count": 1, "move_probability": 0.5, "energy": 1},
            ]
        )


def test_too_many_particles_rejected() -> None:
    with pytest.raises(ConfigError, match="celle disponibili"):
        make_config(
            width=4,
            height=4,
            species=[{"name": "A", "count": 17, "move_probability": 0.5, "energy": 1}],
        )


def test_move_probability_range_enforced() -> None:
    with pytest.raises(ConfigError, match="move_probability"):
        make_config(
            species=[{"name": "A", "count": 1, "move_probability": 1.5, "energy": 1}]
        )


def test_boolean_is_not_an_integer() -> None:
    with pytest.raises(ConfigError, match="intero"):
        make_config(species=[{"name": "A", "count": True, "move_probability": 0.5, "energy": 1}])


def test_negative_seed_rejected() -> None:
    with pytest.raises(ConfigError, match="seed"):
        Config.from_dict(
            {
                "seed": -3,
                "grid": {"width": 8, "height": 8},
                "species": [{"name": "A", "count": 1, "move_probability": 0.5, "energy": 1}],
            }
        ).validate()


def test_missing_file(tmp_path) -> None:
    with pytest.raises(ConfigError, match="non trovata"):
        load_config(tmp_path / "assente.json")


def test_invalid_json(tmp_path) -> None:
    path = tmp_path / "rotto.json"
    path.write_text("{ non json", encoding="utf-8")
    with pytest.raises(ConfigError, match="JSON non valida"):
        load_config(path)
