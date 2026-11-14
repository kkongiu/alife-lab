"""Validazione e hashing canonico della configurazione."""

from __future__ import annotations

import json

import pytest

from alife.config import Config, ConfigError, load_config
from support import BASELINE, M2_BASELINE, M2_QUICK, M3_QUICK, make_config


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


# --- schema 2: chimica ------------------------------------------------------


def test_v1_hash_is_unchanged() -> None:
    # valore pubblicato nella milestone M1: la compatibilità del formato è un
    # requisito, non un dettaglio
    assert load_config(BASELINE).hash() == (
        "f697f983214246b4b7a96560a8e7de5d33c57e354e14899d6929e6a5226391c8"
    )


def test_v2_roundtrip_preserves_hash() -> None:
    config = load_config(M2_QUICK)
    assert config.schema_version == 2
    again = Config.from_dict(config.to_dict()).validate()
    assert again == config
    assert again.hash() == config.hash()


def test_v2_hash_ignores_pair_order_and_duplicates() -> None:
    base = json.loads(M2_QUICK.read_text())
    reordered = json.loads(M2_QUICK.read_text())
    reordered["chemistry"]["allowed_pairs"] = [
        ["S1", "S0"],
        ["S0", "S0"],
        ["S1", "S2"],
        ["S1", "S1"],
        ["S0", "S0"],
    ]
    assert Config.from_dict(base).hash() == Config.from_dict(reordered).hash()


def test_v1_rejects_chemistry_block() -> None:
    raw = json.loads(BASELINE.read_text())
    raw["chemistry"] = {"enabled": False}
    with pytest.raises(ConfigError, match="schema 1"):
        Config.from_dict(raw)


def test_chemistry_requires_usable_pair() -> None:
    raw = json.loads(M2_QUICK.read_text())
    raw["species"] = [
        {"name": name, "count": 1, "move_probability": 0.5, "energy": 5, "max_bonds": 0}
        for name in ("S0", "S1", "S2", "S3")
    ]
    with pytest.raises(ConfigError, match="max_bonds"):
        Config.from_dict(raw).validate()


def test_unknown_species_in_pairs_rejected() -> None:
    raw = json.loads(M2_QUICK.read_text())
    raw["chemistry"]["allowed_pairs"] = [["S0", "S9"]]
    with pytest.raises(ConfigError, match="coppia non valida"):
        Config.from_dict(raw).validate()


def test_catalysis_on_non_allowed_pair_rejected() -> None:
    raw = json.loads(M2_QUICK.read_text())
    raw["chemistry"]["catalysis"] = [
        {"catalyst": "S3", "pair": ["S0", "S2"], "factor": 2.0}
    ]
    with pytest.raises(ConfigError, match="non è fra quelle ammesse"):
        Config.from_dict(raw).validate()


def test_catalysis_factor_below_one_rejected() -> None:
    raw = json.loads(M2_QUICK.read_text())
    raw["chemistry"]["catalysis"] = [
        {"catalyst": "S3", "pair": ["S0", "S1"], "factor": 0.5}
    ]
    with pytest.raises(ConfigError, match="factor"):
        Config.from_dict(raw).validate()


def test_max_bonds_is_validated() -> None:
    raw = json.loads(M2_QUICK.read_text())
    raw["species"][0]["max_bonds"] = 99
    with pytest.raises(ConfigError, match="max_bonds"):
        Config.from_dict(raw).validate()


def test_m1_and_m2_configs_differ_in_hash() -> None:
    assert load_config(BASELINE).hash() != load_config(M2_BASELINE).hash()


# --- schema 3: flussi energetici -------------------------------------------


def test_schema3_roundtrip_preserves_hash() -> None:
    config = load_config(M3_QUICK)
    assert config.schema_version == 3
    again = Config.from_dict(config.to_dict()).validate()
    assert again == config
    assert again.hash() == config.hash()


def test_schema3_sources_order_is_canonical() -> None:
    base = json.loads(M3_QUICK.read_text())
    reordered = json.loads(M3_QUICK.read_text())
    reordered["energy"]["sources"] = list(reversed(reordered["energy"]["sources"]))
    assert Config.from_dict(base).hash() == Config.from_dict(reordered).hash()


def test_energy_block_rejected_before_schema3() -> None:
    raw = json.loads(M2_QUICK.read_text())
    raw["energy"] = {}
    with pytest.raises(ConfigError, match="schema 2"):
        Config.from_dict(raw)


def test_invalid_decay_denominator_rejected() -> None:
    raw = json.loads(M3_QUICK.read_text())
    raw["energy"]["particle_decay"] = {"num": 1, "den": 0}
    with pytest.raises(ConfigError, match="den"):
        Config.from_dict(raw).validate()


def test_negative_energy_cost_rejected() -> None:
    raw = json.loads(M3_QUICK.read_text())
    raw["energy"]["movement_cost"] = -1
    with pytest.raises(ConfigError, match="movement_cost"):
        Config.from_dict(raw).validate()


def test_duplicate_source_rejected() -> None:
    raw = json.loads(M3_QUICK.read_text())
    raw["energy"]["sources"].append(dict(raw["energy"]["sources"][0]))
    with pytest.raises(ConfigError, match="duplicata"):
        Config.from_dict(raw).validate()


def test_source_out_of_grid_rejected() -> None:
    raw = json.loads(M3_QUICK.read_text())
    raw["energy"]["sources"][0]["x"] = 10_000
    with pytest.raises(ConfigError, match="fuori griglia"):
        Config.from_dict(raw).validate()


def test_dissipation_requires_chemistry() -> None:
    raw = json.loads(M3_QUICK.read_text())
    raw["chemistry"]["enabled"] = False
    with pytest.raises(ConfigError, match="chemistry"):
        Config.from_dict(raw).validate()


def test_invalid_overflow_rejected() -> None:
    raw = json.loads(M3_QUICK.read_text())
    raw["energy"]["sources"][0]["overflow"] = "accumulate"
    with pytest.raises(ConfigError, match="overflow"):
        Config.from_dict(raw).validate()
