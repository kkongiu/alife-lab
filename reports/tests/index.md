# Risultati dei test

Generato: 2026-11-15T07:15:23+00:00 · Comando: `.venv/bin/python -m pytest -v`

**156 superati, 0 falliti, 156 casi in 11.18 s** (exit code 0).

## Test obbligatori del contratto

| ID | Requisito | Esito | File | Test pytest |
|---|---|---|---|---|
| M1-01 | Conservazione del numero di particelle | **PASS** | [M1-01_conservazione_particelle.md](evidence/M1-01_conservazione_particelle.md) | 1/1 superati |
| M1-02 | Conservazione della quantità per specie | **PASS** | [M1-02_conservazione_specie.md](evidence/M1-02_conservazione_specie.md) | 1/1 superati |
| M1-03 | Assenza di occupazione multipla | **PASS** | [M1-03_occupazione_unica.md](evidence/M1-03_occupazione_unica.md) | 1/1 superati |
| M1-04 | Rispetto dei confini configurati | **PASS** | [M1-04_confini.md](evidence/M1-04_confini.md) | 2/2 superati |
| M1-05 | Riproducibilità con identico seed | **PASS** | [M1-05_riproducibilita.md](evidence/M1-05_riproducibilita.md) | 6/6 superati |
| M1-06 | Integrità del salvataggio e caricamento | **PASS** | [M1-06_checkpoint.md](evidence/M1-06_checkpoint.md) | 4/4 superati |
| M1-07 | Equivalenza tra esecuzione continua e interrotta/ripresa | **PASS** | [M1-07_ripresa_equivalente.md](evidence/M1-07_ripresa_equivalente.md) | 2/2 superati |
| M1-08 | Rilevamento di una violazione intenzionale delle invarianti | **PASS** | [M1-08_violazioni_intenzionali.md](evidence/M1-08_violazioni_intenzionali.md) | 12/12 superati |
| M2-01 | Legami reversibili con costo energetico | **PASS** | [M2-01_legami_reversibili.md](evidence/M2-01_legami_reversibili.md) | 3/3 superati |
| M2-02 | Conservazione dell'energia con i legami | **PASS** | [M2-02_energia_legami.md](evidence/M2-02_energia_legami.md) | 2/2 superati |
| M2-03 | Coppie ammesse, max_bonds e adiacenza | **PASS** | [M2-03_regole_locali.md](evidence/M2-03_regole_locali.md) | 6/6 superati |
| M2-04 | Catalisi locale per differenza | **PASS** | [M2-04_catalisi.md](evidence/M2-04_catalisi.md) | 2/2 superati |
| M2-05 | Aggregati: distribuzione delle dimensioni | **PASS** | [M2-05_aggregati.md](evidence/M2-05_aggregati.md) | 2/2 superati |
| M2-06 | Determinismo e ripresa con la chimica | **PASS** | [M2-06_determinismo_chimica.md](evidence/M2-06_determinismo_chimica.md) | 3/3 superati |
| M2-07 | Migrazione dei checkpoint M1 | **PASS** | [M2-07_migrazione_checkpoint.md](evidence/M2-07_migrazione_checkpoint.md) | 2/2 superati |
| M3-01 | Identità energetica in sistema aperto | **PASS** | [M3-01_identita_energetica.md](evidence/M3-01_identita_energetica.md) | 2/2 superati |
| M3-02 | Dissipazione esatta di particelle e legami | **PASS** | [M3-02_dissipazione.md](evidence/M3-02_dissipazione.md) | 3/3 superati |
| M3-03 | Sorgenti con accumulatore e capacità | **PASS** | [M3-03_sorgenti.md](evidence/M3-03_sorgenti.md) | 3/3 superati |
| M3-04 | Costo di movimento pagato solo se accettato | **PASS** | [M3-04_costo_movimento.md](evidence/M3-04_costo_movimento.md) | 2/2 superati |
| M3-05 | Costi di formazione e rottura | **PASS** | [M3-05_costi_reazione.md](evidence/M3-05_costi_reazione.md) | 2/2 superati |
| M3-06 | Determinismo con flussi e budget RNG | **PASS** | [M3-06_determinismo_flussi.md](evidence/M3-06_determinismo_flussi.md) | 3/3 superati |
| M3-07 | Checkpoint con ledger e accumulatori | **PASS** | [M3-07_checkpoint_flussi.md](evidence/M3-07_checkpoint_flussi.md) | 3/3 superati |
| M3-08 | Core senza sorgenti di non determinismo | **PASS** | [M3-08_core_deterministico.md](evidence/M3-08_core_deterministico.md) | 1/1 superati |
| M4-01 | Firme canoniche esatte per strutture ad albero | **PASS** | [M4-01_firme_esatte.md](evidence/M4-01_firme_esatte.md) | 3/3 superati |
| M4-02 | Cicli come impronte, ambiguità dichiarata | **PASS** | [M4-02_ambiguita.md](evidence/M4-02_ambiguita.md) | 3/3 superati |
| M4-03 | Eventi: nascita, crescita, scissione, fusione, morte | **PASS** | [M4-03_eventi_tracciati.md](evidence/M4-03_eventi_tracciati.md) | 5/5 superati |
| M4-04 | Persistenza: distribuzione delle vite | **PASS** | [M4-04_persistenza.md](evidence/M4-04_persistenza.md) | 2/2 superati |
| M4-05 | Tracciamento deterministico e non invasivo | **PASS** | [M4-05_tracker_deterministico.md](evidence/M4-05_tracker_deterministico.md) | 2/2 superati |
| M4-06 | Tracciamento end-to-end e file di eventi | **PASS** | [M4-06_tracking_end_to_end.md](evidence/M4-06_tracking_end_to_end.md) | 2/2 superati |

## Tutti i casi

| # | Caso | Stato | Durata (s) | File |
|---|---|---|---|---|
| 1 | `tests/test_checkpoint.py::test_checkpoint_does_not_mutate_world` | PASSED | 0.0020 | [01_test_checkpoint__test_checkpoint_does_not_mutate_world.md](cases/01_test_checkpoint__test_checkpoint_does_not_mutate_world.md) |
| 2 | `tests/test_checkpoint.py::test_detects_energy_imbalance` | PASSED | 0.0020 | [02_test_checkpoint__test_detects_energy_imbalance.md](cases/02_test_checkpoint__test_detects_energy_imbalance.md) |
| 3 | `tests/test_checkpoint.py::test_detects_invalid_json` | PASSED | 0.0010 | [03_test_checkpoint__test_detects_invalid_json.md](cases/03_test_checkpoint__test_detects_invalid_json.md) |
| 4 | `tests/test_checkpoint.py::test_detects_missing_rng_state` | PASSED | 0.0020 | [04_test_checkpoint__test_detects_missing_rng_state.md](cases/04_test_checkpoint__test_detects_missing_rng_state.md) |
| 5 | `tests/test_checkpoint.py::test_detects_tampered_bond_energy` | PASSED | 0.0160 | [05_test_checkpoint__test_detects_tampered_bond_energy.md](cases/05_test_checkpoint__test_detects_tampered_bond_energy.md) |
| 6 | `tests/test_checkpoint.py::test_detects_tampered_config_hash` | PASSED | 0.0020 | [06_test_checkpoint__test_detects_tampered_config_hash.md](cases/06_test_checkpoint__test_detects_tampered_config_hash.md) |
| 7 | `tests/test_checkpoint.py::test_detects_tampered_identity` | PASSED | 0.0030 | [07_test_checkpoint__test_detects_tampered_identity.md](cases/07_test_checkpoint__test_detects_tampered_identity.md) |
| 8 | `tests/test_checkpoint.py::test_detects_tampered_ledger` | PASSED | 0.0070 | [08_test_checkpoint__test_detects_tampered_ledger.md](cases/08_test_checkpoint__test_detects_tampered_ledger.md) |
| 9 | `tests/test_checkpoint.py::test_detects_tampered_particle` | PASSED | 0.0030 | [09_test_checkpoint__test_detects_tampered_particle.md](cases/09_test_checkpoint__test_detects_tampered_particle.md) |
| 10 | `tests/test_checkpoint.py::test_detects_tampered_particle_energy` | PASSED | 0.0150 | [10_test_checkpoint__test_detects_tampered_particle_energy.md](cases/10_test_checkpoint__test_detects_tampered_particle_energy.md) |
| 11 | `tests/test_checkpoint.py::test_detects_wrong_format` | PASSED | 0.0010 | [11_test_checkpoint__test_detects_wrong_format.md](cases/11_test_checkpoint__test_detects_wrong_format.md) |
| 12 | `tests/test_checkpoint.py::test_detects_wrong_source_accumulators` | PASSED | 0.0030 | [12_test_checkpoint__test_detects_wrong_source_accumulators.md](cases/12_test_checkpoint__test_detects_wrong_source_accumulators.md) |
| 13 | `tests/test_checkpoint.py::test_missing_file` | PASSED | 0.0010 | [13_test_checkpoint__test_missing_file.md](cases/13_test_checkpoint__test_missing_file.md) |
| 14 | `tests/test_checkpoint.py::test_no_temporary_file_left_behind` | PASSED | 0.0010 | [14_test_checkpoint__test_no_temporary_file_left_behind.md](cases/14_test_checkpoint__test_no_temporary_file_left_behind.md) |
| 15 | `tests/test_checkpoint.py::test_repeated_save_load_cycles_are_stable` | PASSED | 0.0060 | [15_test_checkpoint__test_repeated_save_load_cycles_are_stable.md](cases/15_test_checkpoint__test_repeated_save_load_cycles_are_stable.md) |
| 16 | `tests/test_checkpoint.py::test_resume_is_equivalent_to_continuous_run` | PASSED | 0.0110 | [16_test_checkpoint__test_resume_is_equivalent_to_continuous_run.md](cases/16_test_checkpoint__test_resume_is_equivalent_to_continuous_run.md) |
| 17 | `tests/test_checkpoint.py::test_roundtrip_preserves_state` | PASSED | 0.0180 | [17_test_checkpoint__test_roundtrip_preserves_state.md](cases/17_test_checkpoint__test_roundtrip_preserves_state.md) |
| 18 | `tests/test_checkpoint.py::test_v1_checkpoint_is_migrated` | PASSED | 0.0020 | [18_test_checkpoint__test_v1_checkpoint_is_migrated.md](cases/18_test_checkpoint__test_v1_checkpoint_is_migrated.md) |
| 19 | `tests/test_checkpoint.py::test_v1_checkpoint_with_bonds_is_rejected` | PASSED | 0.0020 | [19_test_checkpoint__test_v1_checkpoint_with_bonds_is_rejected.md](cases/19_test_checkpoint__test_v1_checkpoint_with_bonds_is_rejected.md) |
| 20 | `tests/test_checkpoint.py::test_v2_checkpoint_is_migrated_to_v3` | PASSED | 0.0120 | [20_test_checkpoint__test_v2_checkpoint_is_migrated_to_v3.md](cases/20_test_checkpoint__test_v2_checkpoint_is_migrated_to_v3.md) |
| 21 | `tests/test_checkpoint.py::test_v2_resume_is_equivalent_to_continuous_run` | PASSED | 0.0810 | [21_test_checkpoint__test_v2_resume_is_equivalent_to_continuous_run.md](cases/21_test_checkpoint__test_v2_resume_is_equivalent_to_continuous_run.md) |
| 22 | `tests/test_checkpoint.py::test_v2_roundtrip_preserves_bonds_and_energy` | PASSED | 0.0270 | [22_test_checkpoint__test_v2_roundtrip_preserves_bonds_and_energy.md](cases/22_test_checkpoint__test_v2_roundtrip_preserves_bonds_and_energy.md) |
| 23 | `tests/test_checkpoint.py::test_v3_resume_is_equivalent_with_flows` | PASSED | 0.0550 | [23_test_checkpoint__test_v3_resume_is_equivalent_with_flows.md](cases/23_test_checkpoint__test_v3_resume_is_equivalent_with_flows.md) |
| 24 | `tests/test_checkpoint.py::test_v3_roundtrip_preserves_ledger` | PASSED | 0.0160 | [24_test_checkpoint__test_v3_roundtrip_preserves_ledger.md](cases/24_test_checkpoint__test_v3_roundtrip_preserves_ledger.md) |
| 25 | `tests/test_chemistry.py::test_aggregate_statistics` | PASSED | 0.0000 | [25_test_chemistry__test_aggregate_statistics.md](cases/25_test_chemistry__test_aggregate_statistics.md) |
| 26 | `tests/test_chemistry.py::test_bond_forms_between_adjacent_allowed_particles` | PASSED | 0.0010 | [26_test_chemistry__test_bond_forms_between_adjacent_allowed_particles.md](cases/26_test_chemistry__test_bond_forms_between_adjacent_allowed_particles.md) |
| 27 | `tests/test_chemistry.py::test_bonded_particles_do_not_move` | PASSED | 0.0010 | [27_test_chemistry__test_bonded_particles_do_not_move.md](cases/27_test_chemistry__test_bonded_particles_do_not_move.md) |
| 28 | `tests/test_chemistry.py::test_breaking_returns_energy` | PASSED | 0.0010 | [28_test_chemistry__test_breaking_returns_energy.md](cases/28_test_chemistry__test_breaking_returns_energy.md) |
| 29 | `tests/test_chemistry.py::test_catalysis_config_changes_chemistry` | PASSED | 0.2010 | [29_test_chemistry__test_catalysis_config_changes_chemistry.md](cases/29_test_chemistry__test_catalysis_config_changes_chemistry.md) |
| 30 | `tests/test_chemistry.py::test_catalysis_multiplies_only_when_adjacent` | PASSED | 0.0010 | [30_test_chemistry__test_catalysis_multiplies_only_when_adjacent.md](cases/30_test_chemistry__test_catalysis_multiplies_only_when_adjacent.md) |
| 31 | `tests/test_chemistry.py::test_chains_grow_to_max_bonds` | PASSED | 0.0000 | [31_test_chemistry__test_chains_grow_to_max_bonds.md](cases/31_test_chemistry__test_chains_grow_to_max_bonds.md) |
| 32 | `tests/test_chemistry.py::test_m2_baseline_produces_structures_and_conserves_energy` | PASSED | 1.8090 | [32_test_chemistry__test_m2_baseline_produces_structures_and_conserves_energy.md](cases/32_test_chemistry__test_m2_baseline_produces_structures_and_conserves_energy.md) |
| 33 | `tests/test_chemistry.py::test_m2_quick_is_deterministic` | PASSED | 0.1080 | [33_test_chemistry__test_m2_quick_is_deterministic.md](cases/33_test_chemistry__test_m2_quick_is_deterministic.md) |
| 34 | `tests/test_chemistry.py::test_max_bonds_is_respected` | PASSED | 0.0000 | [34_test_chemistry__test_max_bonds_is_respected.md](cases/34_test_chemistry__test_max_bonds_is_respected.md) |
| 35 | `tests/test_chemistry.py::test_no_bond_for_non_allowed_species` | PASSED | 0.0010 | [35_test_chemistry__test_no_bond_for_non_allowed_species.md](cases/35_test_chemistry__test_no_bond_for_non_allowed_species.md) |
| 36 | `tests/test_chemistry.py::test_no_bond_when_species_cannot_bond` | PASSED | 0.0000 | [36_test_chemistry__test_no_bond_when_species_cannot_bond.md](cases/36_test_chemistry__test_no_bond_when_species_cannot_bond.md) |
| 37 | `tests/test_chemistry.py::test_no_bond_without_enough_energy` | PASSED | 0.0000 | [37_test_chemistry__test_no_bond_without_enough_energy.md](cases/37_test_chemistry__test_no_bond_without_enough_energy.md) |
| 38 | `tests/test_cli.py::test_inspect_reads_checkpoint` | PASSED | 0.4860 | [38_test_cli__test_inspect_reads_checkpoint.md](cases/38_test_cli__test_inspect_reads_checkpoint.md) |
| 39 | `tests/test_cli.py::test_invalid_config_reports_error` | PASSED | 0.2630 | [39_test_cli__test_invalid_config_reports_error.md](cases/39_test_cli__test_invalid_config_reports_error.md) |
| 40 | `tests/test_cli.py::test_m2_resume_matches_continuous_run` | PASSED | 0.6260 | [40_test_cli__test_m2_resume_matches_continuous_run.md](cases/40_test_cli__test_m2_resume_matches_continuous_run.md) |
| 41 | `tests/test_cli.py::test_negative_steps_rejected` | PASSED | 0.2830 | [41_test_cli__test_negative_steps_rejected.md](cases/41_test_cli__test_negative_steps_rejected.md) |
| 42 | `tests/test_cli.py::test_resume_matches_continuous_run` | PASSED | 0.5010 | [42_test_cli__test_resume_matches_continuous_run.md](cases/42_test_cli__test_resume_matches_continuous_run.md) |
| 43 | `tests/test_cli.py::test_run_m2_writes_events_and_checkpoint` | PASSED | 0.3600 | [43_test_cli__test_run_m2_writes_events_and_checkpoint.md](cases/43_test_cli__test_run_m2_writes_events_and_checkpoint.md) |
| 44 | `tests/test_cli.py::test_run_produces_artifacts` | PASSED | 0.2340 | [44_test_cli__test_run_produces_artifacts.md](cases/44_test_cli__test_run_produces_artifacts.md) |
| 45 | `tests/test_cli.py::test_run_with_tracking` | PASSED | 0.2590 | [45_test_cli__test_run_with_tracking.md](cases/45_test_cli__test_run_with_tracking.md) |
| 46 | `tests/test_cli.py::test_seed_override` | PASSED | 0.2390 | [46_test_cli__test_seed_override.md](cases/46_test_cli__test_seed_override.md) |
| 47 | `tests/test_cli.py::test_version[command0]` | PASSED | 0.2710 | [47_test_cli__test_version[command0].md](cases/47_test_cli__test_version[command0].md) |
| 48 | `tests/test_config.py::test_baseline_config_is_valid` | PASSED | 0.0000 | [48_test_config__test_baseline_config_is_valid.md](cases/48_test_config__test_baseline_config_is_valid.md) |
| 49 | `tests/test_config.py::test_boolean_is_not_an_integer` | PASSED | 0.0010 | [49_test_config__test_boolean_is_not_an_integer.md](cases/49_test_config__test_boolean_is_not_an_integer.md) |
| 50 | `tests/test_config.py::test_catalysis_factor_below_one_rejected` | PASSED | 0.0010 | [50_test_config__test_catalysis_factor_below_one_rejected.md](cases/50_test_config__test_catalysis_factor_below_one_rejected.md) |
| 51 | `tests/test_config.py::test_catalysis_on_non_allowed_pair_rejected` | PASSED | 0.0010 | [51_test_config__test_catalysis_on_non_allowed_pair_rejected.md](cases/51_test_config__test_catalysis_on_non_allowed_pair_rejected.md) |
| 52 | `tests/test_config.py::test_chemistry_requires_usable_pair` | PASSED | 0.0010 | [52_test_config__test_chemistry_requires_usable_pair.md](cases/52_test_config__test_chemistry_requires_usable_pair.md) |
| 53 | `tests/test_config.py::test_dissipation_requires_chemistry` | PASSED | 0.0010 | [53_test_config__test_dissipation_requires_chemistry.md](cases/53_test_config__test_dissipation_requires_chemistry.md) |
| 54 | `tests/test_config.py::test_duplicate_source_rejected` | PASSED | 0.0010 | [54_test_config__test_duplicate_source_rejected.md](cases/54_test_config__test_duplicate_source_rejected.md) |
| 55 | `tests/test_config.py::test_duplicate_species_names_rejected` | PASSED | 0.0000 | [55_test_config__test_duplicate_species_names_rejected.md](cases/55_test_config__test_duplicate_species_names_rejected.md) |
| 56 | `tests/test_config.py::test_energy_block_rejected_before_schema3` | PASSED | 0.0010 | [56_test_config__test_energy_block_rejected_before_schema3.md](cases/56_test_config__test_energy_block_rejected_before_schema3.md) |
| 57 | `tests/test_config.py::test_hash_changes_with_seed` | PASSED | 0.0000 | [57_test_config__test_hash_changes_with_seed.md](cases/57_test_config__test_hash_changes_with_seed.md) |
| 58 | `tests/test_config.py::test_hash_is_independent_of_key_order` | PASSED | 0.0010 | [58_test_config__test_hash_is_independent_of_key_order.md](cases/58_test_config__test_hash_is_independent_of_key_order.md) |
| 59 | `tests/test_config.py::test_invalid_decay_denominator_rejected` | PASSED | 0.0010 | [59_test_config__test_invalid_decay_denominator_rejected.md](cases/59_test_config__test_invalid_decay_denominator_rejected.md) |
| 60 | `tests/test_config.py::test_invalid_json` | PASSED | 0.0010 | [60_test_config__test_invalid_json.md](cases/60_test_config__test_invalid_json.md) |
| 61 | `tests/test_config.py::test_invalid_overflow_rejected` | PASSED | 0.0010 | [61_test_config__test_invalid_overflow_rejected.md](cases/61_test_config__test_invalid_overflow_rejected.md) |
| 62 | `tests/test_config.py::test_m1_and_m2_configs_differ_in_hash` | PASSED | 0.0010 | [62_test_config__test_m1_and_m2_configs_differ_in_hash.md](cases/62_test_config__test_m1_and_m2_configs_differ_in_hash.md) |
| 63 | `tests/test_config.py::test_max_bonds_is_validated` | PASSED | 0.0000 | [63_test_config__test_max_bonds_is_validated.md](cases/63_test_config__test_max_bonds_is_validated.md) |
| 64 | `tests/test_config.py::test_missing_file` | PASSED | 0.0010 | [64_test_config__test_missing_file.md](cases/64_test_config__test_missing_file.md) |
| 65 | `tests/test_config.py::test_move_probability_range_enforced` | PASSED | 0.0010 | [65_test_config__test_move_probability_range_enforced.md](cases/65_test_config__test_move_probability_range_enforced.md) |
| 66 | `tests/test_config.py::test_negative_energy_cost_rejected` | PASSED | 0.0010 | [66_test_config__test_negative_energy_cost_rejected.md](cases/66_test_config__test_negative_energy_cost_rejected.md) |
| 67 | `tests/test_config.py::test_negative_seed_rejected` | PASSED | 0.0000 | [67_test_config__test_negative_seed_rejected.md](cases/67_test_config__test_negative_seed_rejected.md) |
| 68 | `tests/test_config.py::test_roundtrip_preserves_hash` | PASSED | 0.0000 | [68_test_config__test_roundtrip_preserves_hash.md](cases/68_test_config__test_roundtrip_preserves_hash.md) |
| 69 | `tests/test_config.py::test_schema3_roundtrip_preserves_hash` | PASSED | 0.0010 | [69_test_config__test_schema3_roundtrip_preserves_hash.md](cases/69_test_config__test_schema3_roundtrip_preserves_hash.md) |
| 70 | `tests/test_config.py::test_schema3_sources_order_is_canonical` | PASSED | 0.0010 | [70_test_config__test_schema3_sources_order_is_canonical.md](cases/70_test_config__test_schema3_sources_order_is_canonical.md) |
| 71 | `tests/test_config.py::test_source_out_of_grid_rejected` | PASSED | 0.0010 | [71_test_config__test_source_out_of_grid_rejected.md](cases/71_test_config__test_source_out_of_grid_rejected.md) |
| 72 | `tests/test_config.py::test_too_many_particles_rejected` | PASSED | 0.0000 | [72_test_config__test_too_many_particles_rejected.md](cases/72_test_config__test_too_many_particles_rejected.md) |
| 73 | `tests/test_config.py::test_unknown_key_rejected` | PASSED | 0.0000 | [73_test_config__test_unknown_key_rejected.md](cases/73_test_config__test_unknown_key_rejected.md) |
| 74 | `tests/test_config.py::test_unknown_species_in_pairs_rejected` | PASSED | 0.0010 | [74_test_config__test_unknown_species_in_pairs_rejected.md](cases/74_test_config__test_unknown_species_in_pairs_rejected.md) |
| 75 | `tests/test_config.py::test_v1_hash_is_unchanged` | PASSED | 0.0010 | [75_test_config__test_v1_hash_is_unchanged.md](cases/75_test_config__test_v1_hash_is_unchanged.md) |
| 76 | `tests/test_config.py::test_v1_rejects_chemistry_block` | PASSED | 0.0010 | [76_test_config__test_v1_rejects_chemistry_block.md](cases/76_test_config__test_v1_rejects_chemistry_block.md) |
| 77 | `tests/test_config.py::test_v2_hash_ignores_pair_order_and_duplicates` | PASSED | 0.0010 | [77_test_config__test_v2_hash_ignores_pair_order_and_duplicates.md](cases/77_test_config__test_v2_hash_ignores_pair_order_and_duplicates.md) |
| 78 | `tests/test_config.py::test_v2_roundtrip_preserves_hash` | PASSED | 0.0010 | [78_test_config__test_v2_roundtrip_preserves_hash.md](cases/78_test_config__test_v2_roundtrip_preserves_hash.md) |
| 79 | `tests/test_dynamics.py::test_blocked_chain_leaves_head_stuck` | PASSED | 0.0000 | [79_test_dynamics__test_blocked_chain_leaves_head_stuck.md](cases/79_test_dynamics__test_blocked_chain_leaves_head_stuck.md) |
| 80 | `tests/test_dynamics.py::test_chain_towards_empty_cell_moves_entirely` | PASSED | 0.0000 | [80_test_dynamics__test_chain_towards_empty_cell_moves_entirely.md](cases/80_test_dynamics__test_chain_towards_empty_cell_moves_entirely.md) |
| 81 | `tests/test_dynamics.py::test_closed_boundary_keeps_particles_inside` | PASSED | 0.0050 | [81_test_dynamics__test_closed_boundary_keeps_particles_inside.md](cases/81_test_dynamics__test_closed_boundary_keeps_particles_inside.md) |
| 82 | `tests/test_dynamics.py::test_contention_produces_single_winner` | PASSED | 0.0000 | [82_test_dynamics__test_contention_produces_single_winner.md](cases/82_test_dynamics__test_contention_produces_single_winner.md) |
| 83 | `tests/test_dynamics.py::test_direction_set_is_von_neumann` | PASSED | 0.0000 | [83_test_dynamics__test_direction_set_is_von_neumann.md](cases/83_test_dynamics__test_direction_set_is_von_neumann.md) |
| 84 | `tests/test_dynamics.py::test_free_move_accepted` | PASSED | 0.0000 | [84_test_dynamics__test_free_move_accepted.md](cases/84_test_dynamics__test_free_move_accepted.md) |
| 85 | `tests/test_dynamics.py::test_immobile_species_never_moves` | PASSED | 0.0010 | [85_test_dynamics__test_immobile_species_never_moves.md](cases/85_test_dynamics__test_immobile_species_never_moves.md) |
| 86 | `tests/test_dynamics.py::test_resolution_is_insertion_order_independent` | PASSED | 0.0010 | [86_test_dynamics__test_resolution_is_insertion_order_independent.md](cases/86_test_dynamics__test_resolution_is_insertion_order_independent.md) |
| 87 | `tests/test_dynamics.py::test_rng_stream_is_two_draws_per_particle_per_step` | PASSED | 0.0010 | [87_test_dynamics__test_rng_stream_is_two_draws_per_particle_per_step.md](cases/87_test_dynamics__test_rng_stream_is_two_draws_per_particle_per_step.md) |
| 88 | `tests/test_dynamics.py::test_single_particle_moves_exactly_one_cell` | PASSED | 0.0010 | [88_test_dynamics__test_single_particle_moves_exactly_one_cell.md](cases/88_test_dynamics__test_single_particle_moves_exactly_one_cell.md) |
| 89 | `tests/test_dynamics.py::test_swap_is_resolved_as_rotation` | PASSED | 0.0000 | [89_test_dynamics__test_swap_is_resolved_as_rotation.md](cases/89_test_dynamics__test_swap_is_resolved_as_rotation.md) |
| 90 | `tests/test_dynamics.py::test_three_particle_cycle` | PASSED | 0.0000 | [90_test_dynamics__test_three_particle_cycle.md](cases/90_test_dynamics__test_three_particle_cycle.md) |
| 91 | `tests/test_energy.py::test_bond_decay_is_exact` | PASSED | 0.0010 | [91_test_energy__test_bond_decay_is_exact.md](cases/91_test_energy__test_bond_decay_is_exact.md) |
| 92 | `tests/test_energy.py::test_breaking_dissipation` | PASSED | 0.0010 | [92_test_energy__test_breaking_dissipation.md](cases/92_test_energy__test_breaking_dissipation.md) |
| 93 | `tests/test_energy.py::test_closed_system_keeps_identity` | PASSED | 0.0080 | [93_test_energy__test_closed_system_keeps_identity.md](cases/93_test_energy__test_closed_system_keeps_identity.md) |
| 94 | `tests/test_energy.py::test_core_modules_do_not_import_nondeterministic_sources` | PASSED | 0.0010 | [94_test_energy__test_core_modules_do_not_import_nondeterministic_sources.md](cases/94_test_energy__test_core_modules_do_not_import_nondeterministic_sources.md) |
| 95 | `tests/test_energy.py::test_formation_dissipation` | PASSED | 0.0010 | [95_test_energy__test_formation_dissipation.md](cases/95_test_energy__test_formation_dissipation.md) |
| 96 | `tests/test_energy.py::test_golden_hash_m2_is_preserved` | PASSED | 0.0610 | [96_test_energy__test_golden_hash_m2_is_preserved.md](cases/96_test_energy__test_golden_hash_m2_is_preserved.md) |
| 97 | `tests/test_energy.py::test_ledger_tampering_is_detected` | PASSED | 0.0070 | [97_test_energy__test_ledger_tampering_is_detected.md](cases/97_test_energy__test_ledger_tampering_is_detected.md) |
| 98 | `tests/test_energy.py::test_movement_cost_blocks_when_insufficient` | PASSED | 0.0010 | [98_test_energy__test_movement_cost_blocks_when_insufficient.md](cases/98_test_energy__test_movement_cost_blocks_when_insufficient.md) |
| 99 | `tests/test_energy.py::test_movement_cost_charged_per_move` | PASSED | 0.0010 | [99_test_energy__test_movement_cost_charged_per_move.md](cases/99_test_energy__test_movement_cost_charged_per_move.md) |
| 100 | `tests/test_energy.py::test_open_run_is_deterministic` | PASSED | 0.0750 | [100_test_energy__test_open_run_is_deterministic.md](cases/100_test_energy__test_open_run_is_deterministic.md) |
| 101 | `tests/test_energy.py::test_open_run_keeps_identity` | PASSED | 0.0480 | [101_test_energy__test_open_run_keeps_identity.md](cases/101_test_energy__test_open_run_keeps_identity.md) |
| 102 | `tests/test_energy.py::test_particle_decay_is_exact` | PASSED | 0.0010 | [102_test_energy__test_particle_decay_is_exact.md](cases/102_test_energy__test_particle_decay_is_exact.md) |
| 103 | `tests/test_energy.py::test_particle_decay_uses_identity_not_index` | PASSED | 0.0010 | [103_test_energy__test_particle_decay_uses_identity_not_index.md](cases/103_test_energy__test_particle_decay_uses_identity_not_index.md) |
| 104 | `tests/test_energy.py::test_priority_uses_identity` | PASSED | 0.0010 | [104_test_energy__test_priority_uses_identity.md](cases/104_test_energy__test_priority_uses_identity.md) |
| 105 | `tests/test_energy.py::test_rng_budget_with_flows_disabled` | PASSED | 0.0010 | [105_test_energy__test_rng_budget_with_flows_disabled.md](cases/105_test_energy__test_rng_budget_with_flows_disabled.md) |
| 106 | `tests/test_energy.py::test_source_accumulator_is_exact` | PASSED | 0.0050 | [106_test_energy__test_source_accumulator_is_exact.md](cases/106_test_energy__test_source_accumulator_is_exact.md) |
| 107 | `tests/test_energy.py::test_source_accumulator_out_of_range_is_detected` | PASSED | 0.0010 | [107_test_energy__test_source_accumulator_out_of_range_is_detected.md](cases/107_test_energy__test_source_accumulator_out_of_range_is_detected.md) |
| 108 | `tests/test_energy.py::test_source_buffer_is_delivered_to_a_visiting_particle` | PASSED | 0.0010 | [108_test_energy__test_source_buffer_is_delivered_to_a_visiting_particle.md](cases/108_test_energy__test_source_buffer_is_delivered_to_a_visiting_particle.md) |
| 109 | `tests/test_energy.py::test_source_capacity_and_unabsorbed` | PASSED | 0.0010 | [109_test_energy__test_source_capacity_and_unabsorbed.md](cases/109_test_energy__test_source_capacity_and_unabsorbed.md) |
| 110 | `tests/test_energy.py::test_source_on_empty_cell_is_unabsorbed` | PASSED | 0.0010 | [110_test_energy__test_source_on_empty_cell_is_unabsorbed.md](cases/110_test_energy__test_source_on_empty_cell_is_unabsorbed.md) |
| 111 | `tests/test_energy.py::test_validate_detects_unsorted_identifiers` | PASSED | 0.0010 | [111_test_energy__test_validate_detects_unsorted_identifiers.md](cases/111_test_energy__test_validate_detects_unsorted_identifiers.md) |
| 112 | `tests/test_invariants.py::test_energy_is_conserved` | PASSED | 0.0090 | [112_test_invariants__test_energy_is_conserved.md](cases/112_test_invariants__test_energy_is_conserved.md) |
| 113 | `tests/test_invariants.py::test_energy_with_bonds_is_conserved` | PASSED | 0.0620 | [113_test_invariants__test_energy_with_bonds_is_conserved.md](cases/113_test_invariants__test_energy_with_bonds_is_conserved.md) |
| 114 | `tests/test_invariants.py::test_no_multiple_occupancy` | PASSED | 0.0060 | [114_test_invariants__test_no_multiple_occupancy.md](cases/114_test_invariants__test_no_multiple_occupancy.md) |
| 115 | `tests/test_invariants.py::test_particle_count_conserved` | PASSED | 0.0070 | [115_test_invariants__test_particle_count_conserved.md](cases/115_test_invariants__test_particle_count_conserved.md) |
| 116 | `tests/test_invariants.py::test_periodic_boundaries` | PASSED | 0.0090 | [116_test_invariants__test_periodic_boundaries.md](cases/116_test_invariants__test_periodic_boundaries.md) |
| 117 | `tests/test_invariants.py::test_species_quantities_conserved` | PASSED | 0.0060 | [117_test_invariants__test_species_quantities_conserved.md](cases/117_test_invariants__test_species_quantities_conserved.md) |
| 118 | `tests/test_invariants.py::test_state_hash_is_stable_and_sensitive` | PASSED | 0.0010 | [118_test_invariants__test_state_hash_is_stable_and_sensitive.md](cases/118_test_invariants__test_state_hash_is_stable_and_sensitive.md) |
| 119 | `tests/test_invariants.py::test_store_rejects_double_placement` | PASSED | 0.0000 | [119_test_invariants__test_store_rejects_double_placement.md](cases/119_test_invariants__test_store_rejects_double_placement.md) |
| 120 | `tests/test_invariants.py::test_store_rejects_duplicate_identifiers` | PASSED | 0.0000 | [120_test_invariants__test_store_rejects_duplicate_identifiers.md](cases/120_test_invariants__test_store_rejects_duplicate_identifiers.md) |
| 121 | `tests/test_invariants.py::test_store_rejects_out_of_grid_particle` | PASSED | 0.0000 | [121_test_invariants__test_store_rejects_out_of_grid_particle.md](cases/121_test_invariants__test_store_rejects_out_of_grid_particle.md) |
| 122 | `tests/test_invariants.py::test_validate_detects_bond_beyond_max_bonds` | PASSED | 0.0010 | [122_test_invariants__test_validate_detects_bond_beyond_max_bonds.md](cases/122_test_invariants__test_validate_detects_bond_beyond_max_bonds.md) |
| 123 | `tests/test_invariants.py::test_validate_detects_bonds_without_chemistry` | PASSED | 0.0010 | [123_test_invariants__test_validate_detects_bonds_without_chemistry.md](cases/123_test_invariants__test_validate_detects_bonds_without_chemistry.md) |
| 124 | `tests/test_invariants.py::test_validate_detects_degree_mismatch` | PASSED | 0.0010 | [124_test_invariants__test_validate_detects_degree_mismatch.md](cases/124_test_invariants__test_validate_detects_degree_mismatch.md) |
| 125 | `tests/test_invariants.py::test_validate_detects_duplicate_cell` | PASSED | 0.0010 | [125_test_invariants__test_validate_detects_duplicate_cell.md](cases/125_test_invariants__test_validate_detects_duplicate_cell.md) |
| 126 | `tests/test_invariants.py::test_validate_detects_grid_desynchronisation` | PASSED | 0.0000 | [126_test_invariants__test_validate_detects_grid_desynchronisation.md](cases/126_test_invariants__test_validate_detects_grid_desynchronisation.md) |
| 127 | `tests/test_invariants.py::test_validate_detects_identity_above_next_id` | PASSED | 0.0010 | [127_test_invariants__test_validate_detects_identity_above_next_id.md](cases/127_test_invariants__test_validate_detects_identity_above_next_id.md) |
| 128 | `tests/test_invariants.py::test_validate_detects_invalid_species_index` | PASSED | 0.0000 | [128_test_invariants__test_validate_detects_invalid_species_index.md](cases/128_test_invariants__test_validate_detects_invalid_species_index.md) |
| 129 | `tests/test_invariants.py::test_validate_detects_missing_particle` | PASSED | 0.0000 | [129_test_invariants__test_validate_detects_missing_particle.md](cases/129_test_invariants__test_validate_detects_missing_particle.md) |
| 130 | `tests/test_invariants.py::test_validate_detects_non_adjacent_bond` | PASSED | 0.0010 | [130_test_invariants__test_validate_detects_non_adjacent_bond.md](cases/130_test_invariants__test_validate_detects_non_adjacent_bond.md) |
| 131 | `tests/test_invariants.py::test_validate_detects_out_of_bounds_particle` | PASSED | 0.0010 | [131_test_invariants__test_validate_detects_out_of_bounds_particle.md](cases/131_test_invariants__test_validate_detects_out_of_bounds_particle.md) |
| 132 | `tests/test_metrics.py::test_peak_memory_is_plausible` | PASSED | 0.0000 | [132_test_metrics__test_peak_memory_is_plausible.md](cases/132_test_metrics__test_peak_memory_is_plausible.md) |
| 133 | `tests/test_metrics.py::test_runtime_versions_are_recorded` | PASSED | 0.0010 | [133_test_metrics__test_runtime_versions_are_recorded.md](cases/133_test_metrics__test_runtime_versions_are_recorded.md) |
| 134 | `tests/test_metrics.py::test_summary_contains_required_fields` | PASSED | 0.0020 | [134_test_metrics__test_summary_contains_required_fields.md](cases/134_test_metrics__test_summary_contains_required_fields.md) |
| 135 | `tests/test_reproducibility.py::test_baseline_config_is_reproducible` | PASSED | 0.1950 | [135_test_reproducibility__test_baseline_config_is_reproducible.md](cases/135_test_reproducibility__test_baseline_config_is_reproducible.md) |
| 136 | `tests/test_reproducibility.py::test_different_seed_different_result` | PASSED | 0.0050 | [136_test_reproducibility__test_different_seed_different_result.md](cases/136_test_reproducibility__test_different_seed_different_result.md) |
| 137 | `tests/test_reproducibility.py::test_initial_placement_is_seed_deterministic` | PASSED | 0.0010 | [137_test_reproducibility__test_initial_placement_is_seed_deterministic.md](cases/137_test_reproducibility__test_initial_placement_is_seed_deterministic.md) |
| 138 | `tests/test_reproducibility.py::test_m1_run_reproduces_the_published_hash` | PASSED | 3.9660 | [138_test_reproducibility__test_m1_run_reproduces_the_published_hash.md](cases/138_test_reproducibility__test_m1_run_reproduces_the_published_hash.md) |
| 139 | `tests/test_reproducibility.py::test_repeated_advance_matches_single_call` | PASSED | 0.0030 | [139_test_reproducibility__test_repeated_advance_matches_single_call.md](cases/139_test_reproducibility__test_repeated_advance_matches_single_call.md) |
| 140 | `tests/test_reproducibility.py::test_same_seed_same_result` | PASSED | 0.0120 | [140_test_reproducibility__test_same_seed_same_result.md](cases/140_test_reproducibility__test_same_seed_same_result.md) |
| 141 | `tests/test_structures.py::test_birth_and_death` | PASSED | 0.0010 | [141_test_structures__test_birth_and_death.md](cases/141_test_structures__test_birth_and_death.md) |
| 142 | `tests/test_structures.py::test_chain_signature_distinguishes_composition` | PASSED | 0.0010 | [142_test_structures__test_chain_signature_distinguishes_composition.md](cases/142_test_structures__test_chain_signature_distinguishes_composition.md) |
| 143 | `tests/test_structures.py::test_chain_signature_is_invariant_under_relabeling` | PASSED | 0.0010 | [143_test_structures__test_chain_signature_is_invariant_under_relabeling.md](cases/143_test_structures__test_chain_signature_is_invariant_under_relabeling.md) |
| 144 | `tests/test_structures.py::test_cycles_are_fingerprints_not_exact` | PASSED | 0.0010 | [144_test_structures__test_cycles_are_fingerprints_not_exact.md](cases/144_test_structures__test_cycles_are_fingerprints_not_exact.md) |
| 145 | `tests/test_structures.py::test_exact_signature_collision_is_not_ambiguity` | PASSED | 0.0010 | [145_test_structures__test_exact_signature_collision_is_not_ambiguity.md](cases/145_test_structures__test_exact_signature_collision_is_not_ambiguity.md) |
| 146 | `tests/test_structures.py::test_fuzzy_collision_is_reported_as_ambiguity` | PASSED | 0.0010 | [146_test_structures__test_fuzzy_collision_is_reported_as_ambiguity.md](cases/146_test_structures__test_fuzzy_collision_is_reported_as_ambiguity.md) |
| 147 | `tests/test_structures.py::test_growth_and_shrink_keep_identity` | PASSED | 0.0010 | [147_test_structures__test_growth_and_shrink_keep_identity.md](cases/147_test_structures__test_growth_and_shrink_keep_identity.md) |
| 148 | `tests/test_structures.py::test_lifetime_counts_steps_alive` | PASSED | 0.0010 | [148_test_structures__test_lifetime_counts_steps_alive.md](cases/148_test_structures__test_lifetime_counts_steps_alive.md) |
| 149 | `tests/test_structures.py::test_merge_creates_one_structure` | PASSED | 0.0010 | [149_test_structures__test_merge_creates_one_structure.md](cases/149_test_structures__test_merge_creates_one_structure.md) |
| 150 | `tests/test_structures.py::test_signature_is_a_signature_instance` | PASSED | 0.0010 | [150_test_structures__test_signature_is_a_signature_instance.md](cases/150_test_structures__test_signature_is_a_signature_instance.md) |
| 151 | `tests/test_structures.py::test_split_creates_two_structures` | PASSED | 0.0010 | [151_test_structures__test_split_creates_two_structures.md](cases/151_test_structures__test_split_creates_two_structures.md) |
| 152 | `tests/test_structures.py::test_tracker_is_deterministic` | PASSED | 0.0010 | [152_test_structures__test_tracker_is_deterministic.md](cases/152_test_structures__test_tracker_is_deterministic.md) |
| 153 | `tests/test_structures.py::test_tracker_writes_jsonl_files` | PASSED | 0.0020 | [153_test_structures__test_tracker_writes_jsonl_files.md](cases/153_test_structures__test_tracker_writes_jsonl_files.md) |
| 154 | `tests/test_structures.py::test_tracking_does_not_change_the_world` | PASSED | 0.0010 | [154_test_structures__test_tracking_does_not_change_the_world.md](cases/154_test_structures__test_tracking_does_not_change_the_world.md) |
| 155 | `tests/test_structures.py::test_transform_same_size_new_topology` | PASSED | 0.0010 | [155_test_structures__test_transform_same_size_new_topology.md](cases/155_test_structures__test_transform_same_size_new_topology.md) |
| 156 | `tests/test_structures.py::test_tree_signature_distinguishes_shape` | PASSED | 0.0010 | [156_test_structures__test_tree_signature_distinguishes_shape.md](cases/156_test_structures__test_tree_signature_distinguishes_shape.md) |

## File

- `junit.xml` — risultato macchina-leggibile (JUnit XML)
- `pytest.log` — log completo di pytest
- `results.json` — tutti i casi e le evidenze in forma strutturata
- `cases/` — un file per ogni caso di test
- `evidence/` — un file per ogni test obbligatorio, con misure reali
