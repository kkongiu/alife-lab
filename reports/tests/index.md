# Risultati dei test

Generato: 2026-11-15T13:21:19+00:00 · Comando: `.venv/bin/python -m pytest -v`

**186 superati, 0 falliti, 186 casi in 22.42 s** (exit code 0).

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
| M5-01 | Controllo positivo riconosciuto (sensibilità) | **PASS** | [M5-01_positivo_riconosciuto.md](evidence/M5-01_positivo_riconosciuto.md) | 1/1 superati |
| M5-02 | Controlli negativi non classificati (falsi positivi) | **PASS** | [M5-02_negativi_rifiutati.md](evidence/M5-02_negativi_rifiutati.md) | 6/6 superati |
| M5-03 | Isolamento dei controlli dal mondo di scoperta | **PASS** | [M5-03_isolamento.md](evidence/M5-03_isolamento.md) | 1/1 superati |
| M5-04 | Controllo positivo riproducibile e versionato | **PASS** | [M5-04_controllo_riproducibile.md](evidence/M5-04_controllo_riproducibile.md) | 2/2 superati |
| M6-01 | Preregistrazione integra: seed, config, hash | **PASS** | [M6-01_preregistrazione.md](evidence/M6-01_preregistrazione.md) | 3/3 superati |
| M6-02 | Stato di tracker e rilevatore ripristinabile | **PASS** | [M6-02_analisi_ripristinabile.md](evidence/M6-02_analisi_ripristinabile.md) | 3/3 superati |
| M6-03 | Campagna completa, run nulli inclusi | **PASS** | [M6-03_campagna_completa.md](evidence/M6-03_campagna_completa.md) | 1/1 superati |
| M6.2-01 | Rilevatore v2: copie che si formano progressivamente | **PASS** | [M6.2-01_rilevatore_v2.md](evidence/M6.2-01_rilevatore_v2.md) | 3/3 superati |
| M6.2-02 | v2 validato sui controlli M5 | **PASS** | [M6.2-02_v2_controlli.md](evidence/M6.2-02_v2_controlli.md) | 3/3 superati |
| M6.2-03 | Ri-analisi dei 25 run M6 con v1 e v2 | **PASS** | [M6.2-03_rianalisi_m6.md](evidence/M6.2-03_rianalisi_m6.md) | 1/1 superati |
| M6.2-04 | Preregistrazione della ri-analisi v2 | **PASS** | [M6.2-04_preregistrazione_v2.md](evidence/M6.2-04_preregistrazione_v2.md) | 2/2 superati |

## Tutti i casi

| # | Caso | Stato | Durata (s) | File |
|---|---|---|---|---|
| 1 | `tests/test_analysis.py::test_invalid_format_is_rejected` | PASSED | 0.0010 | [01_test_analysis__test_invalid_format_is_rejected.md](cases/01_test_analysis__test_invalid_format_is_rejected.md) |
| 2 | `tests/test_analysis.py::test_missing_file_is_rejected` | PASSED | 0.0010 | [02_test_analysis__test_missing_file_is_rejected.md](cases/02_test_analysis__test_missing_file_is_rejected.md) |
| 3 | `tests/test_analysis.py::test_restore_requires_matching_step` | PASSED | 0.0090 | [03_test_analysis__test_restore_requires_matching_step.md](cases/03_test_analysis__test_restore_requires_matching_step.md) |
| 4 | `tests/test_analysis.py::test_resume_matches_continuous_run` | PASSED | 0.0920 | [04_test_analysis__test_resume_matches_continuous_run.md](cases/04_test_analysis__test_resume_matches_continuous_run.md) |
| 5 | `tests/test_analysis.py::test_roundtrip_preserves_state` | PASSED | 0.0430 | [05_test_analysis__test_roundtrip_preserves_state.md](cases/05_test_analysis__test_roundtrip_preserves_state.md) |
| 6 | `tests/test_campaign.py::test_campaign_results_are_complete` | PASSED | 0.0010 | [06_test_campaign__test_campaign_results_are_complete.md](cases/06_test_campaign__test_campaign_results_are_complete.md) |
| 7 | `tests/test_campaign.py::test_manifest_configs_match_their_hashes` | PASSED | 0.0080 | [07_test_campaign__test_manifest_configs_match_their_hashes.md](cases/07_test_campaign__test_manifest_configs_match_their_hashes.md) |
| 8 | `tests/test_campaign.py::test_manifest_is_preregistered` | PASSED | 0.0000 | [08_test_campaign__test_manifest_is_preregistered.md](cases/08_test_campaign__test_manifest_is_preregistered.md) |
| 9 | `tests/test_campaign.py::test_manifest_records_the_decision_rule` | PASSED | 0.0000 | [09_test_campaign__test_manifest_records_the_decision_rule.md](cases/09_test_campaign__test_manifest_records_the_decision_rule.md) |
| 10 | `tests/test_checkpoint.py::test_checkpoint_does_not_mutate_world` | PASSED | 0.0020 | [10_test_checkpoint__test_checkpoint_does_not_mutate_world.md](cases/10_test_checkpoint__test_checkpoint_does_not_mutate_world.md) |
| 11 | `tests/test_checkpoint.py::test_detects_energy_imbalance` | PASSED | 0.0020 | [11_test_checkpoint__test_detects_energy_imbalance.md](cases/11_test_checkpoint__test_detects_energy_imbalance.md) |
| 12 | `tests/test_checkpoint.py::test_detects_invalid_json` | PASSED | 0.0010 | [12_test_checkpoint__test_detects_invalid_json.md](cases/12_test_checkpoint__test_detects_invalid_json.md) |
| 13 | `tests/test_checkpoint.py::test_detects_missing_rng_state` | PASSED | 0.0010 | [13_test_checkpoint__test_detects_missing_rng_state.md](cases/13_test_checkpoint__test_detects_missing_rng_state.md) |
| 14 | `tests/test_checkpoint.py::test_detects_tampered_bond_energy` | PASSED | 0.0140 | [14_test_checkpoint__test_detects_tampered_bond_energy.md](cases/14_test_checkpoint__test_detects_tampered_bond_energy.md) |
| 15 | `tests/test_checkpoint.py::test_detects_tampered_config_hash` | PASSED | 0.0010 | [15_test_checkpoint__test_detects_tampered_config_hash.md](cases/15_test_checkpoint__test_detects_tampered_config_hash.md) |
| 16 | `tests/test_checkpoint.py::test_detects_tampered_identity` | PASSED | 0.0030 | [16_test_checkpoint__test_detects_tampered_identity.md](cases/16_test_checkpoint__test_detects_tampered_identity.md) |
| 17 | `tests/test_checkpoint.py::test_detects_tampered_ledger` | PASSED | 0.0060 | [17_test_checkpoint__test_detects_tampered_ledger.md](cases/17_test_checkpoint__test_detects_tampered_ledger.md) |
| 18 | `tests/test_checkpoint.py::test_detects_tampered_particle` | PASSED | 0.0020 | [18_test_checkpoint__test_detects_tampered_particle.md](cases/18_test_checkpoint__test_detects_tampered_particle.md) |
| 19 | `tests/test_checkpoint.py::test_detects_tampered_particle_energy` | PASSED | 0.0130 | [19_test_checkpoint__test_detects_tampered_particle_energy.md](cases/19_test_checkpoint__test_detects_tampered_particle_energy.md) |
| 20 | `tests/test_checkpoint.py::test_detects_wrong_format` | PASSED | 0.0010 | [20_test_checkpoint__test_detects_wrong_format.md](cases/20_test_checkpoint__test_detects_wrong_format.md) |
| 21 | `tests/test_checkpoint.py::test_detects_wrong_source_accumulators` | PASSED | 0.0030 | [21_test_checkpoint__test_detects_wrong_source_accumulators.md](cases/21_test_checkpoint__test_detects_wrong_source_accumulators.md) |
| 22 | `tests/test_checkpoint.py::test_missing_file` | PASSED | 0.0010 | [22_test_checkpoint__test_missing_file.md](cases/22_test_checkpoint__test_missing_file.md) |
| 23 | `tests/test_checkpoint.py::test_no_temporary_file_left_behind` | PASSED | 0.0010 | [23_test_checkpoint__test_no_temporary_file_left_behind.md](cases/23_test_checkpoint__test_no_temporary_file_left_behind.md) |
| 24 | `tests/test_checkpoint.py::test_repeated_save_load_cycles_are_stable` | PASSED | 0.0050 | [24_test_checkpoint__test_repeated_save_load_cycles_are_stable.md](cases/24_test_checkpoint__test_repeated_save_load_cycles_are_stable.md) |
| 25 | `tests/test_checkpoint.py::test_resume_is_equivalent_to_continuous_run` | PASSED | 0.0080 | [25_test_checkpoint__test_resume_is_equivalent_to_continuous_run.md](cases/25_test_checkpoint__test_resume_is_equivalent_to_continuous_run.md) |
| 26 | `tests/test_checkpoint.py::test_roundtrip_preserves_state` | PASSED | 0.0030 | [26_test_checkpoint__test_roundtrip_preserves_state.md](cases/26_test_checkpoint__test_roundtrip_preserves_state.md) |
| 27 | `tests/test_checkpoint.py::test_v1_checkpoint_is_migrated` | PASSED | 0.0020 | [27_test_checkpoint__test_v1_checkpoint_is_migrated.md](cases/27_test_checkpoint__test_v1_checkpoint_is_migrated.md) |
| 28 | `tests/test_checkpoint.py::test_v1_checkpoint_with_bonds_is_rejected` | PASSED | 0.0010 | [28_test_checkpoint__test_v1_checkpoint_with_bonds_is_rejected.md](cases/28_test_checkpoint__test_v1_checkpoint_with_bonds_is_rejected.md) |
| 29 | `tests/test_checkpoint.py::test_v2_checkpoint_is_migrated_to_v3` | PASSED | 0.0110 | [29_test_checkpoint__test_v2_checkpoint_is_migrated_to_v3.md](cases/29_test_checkpoint__test_v2_checkpoint_is_migrated_to_v3.md) |
| 30 | `tests/test_checkpoint.py::test_v2_resume_is_equivalent_to_continuous_run` | PASSED | 0.0620 | [30_test_checkpoint__test_v2_resume_is_equivalent_to_continuous_run.md](cases/30_test_checkpoint__test_v2_resume_is_equivalent_to_continuous_run.md) |
| 31 | `tests/test_checkpoint.py::test_v2_roundtrip_preserves_bonds_and_energy` | PASSED | 0.0230 | [31_test_checkpoint__test_v2_roundtrip_preserves_bonds_and_energy.md](cases/31_test_checkpoint__test_v2_roundtrip_preserves_bonds_and_energy.md) |
| 32 | `tests/test_checkpoint.py::test_v3_resume_is_equivalent_with_flows` | PASSED | 0.0490 | [32_test_checkpoint__test_v3_resume_is_equivalent_with_flows.md](cases/32_test_checkpoint__test_v3_resume_is_equivalent_with_flows.md) |
| 33 | `tests/test_checkpoint.py::test_v3_roundtrip_preserves_ledger` | PASSED | 0.0130 | [33_test_checkpoint__test_v3_roundtrip_preserves_ledger.md](cases/33_test_checkpoint__test_v3_roundtrip_preserves_ledger.md) |
| 34 | `tests/test_chemistry.py::test_aggregate_statistics` | PASSED | 0.0000 | [34_test_chemistry__test_aggregate_statistics.md](cases/34_test_chemistry__test_aggregate_statistics.md) |
| 35 | `tests/test_chemistry.py::test_bond_forms_between_adjacent_allowed_particles` | PASSED | 0.0010 | [35_test_chemistry__test_bond_forms_between_adjacent_allowed_particles.md](cases/35_test_chemistry__test_bond_forms_between_adjacent_allowed_particles.md) |
| 36 | `tests/test_chemistry.py::test_bonded_particles_do_not_move` | PASSED | 0.0010 | [36_test_chemistry__test_bonded_particles_do_not_move.md](cases/36_test_chemistry__test_bonded_particles_do_not_move.md) |
| 37 | `tests/test_chemistry.py::test_breaking_returns_energy` | PASSED | 0.0000 | [37_test_chemistry__test_breaking_returns_energy.md](cases/37_test_chemistry__test_breaking_returns_energy.md) |
| 38 | `tests/test_chemistry.py::test_catalysis_config_changes_chemistry` | PASSED | 0.1880 | [38_test_chemistry__test_catalysis_config_changes_chemistry.md](cases/38_test_chemistry__test_catalysis_config_changes_chemistry.md) |
| 39 | `tests/test_chemistry.py::test_catalysis_multiplies_only_when_adjacent` | PASSED | 0.0010 | [39_test_chemistry__test_catalysis_multiplies_only_when_adjacent.md](cases/39_test_chemistry__test_catalysis_multiplies_only_when_adjacent.md) |
| 40 | `tests/test_chemistry.py::test_chains_grow_to_max_bonds` | PASSED | 0.0000 | [40_test_chemistry__test_chains_grow_to_max_bonds.md](cases/40_test_chemistry__test_chains_grow_to_max_bonds.md) |
| 41 | `tests/test_chemistry.py::test_m2_baseline_produces_structures_and_conserves_energy` | PASSED | 1.7620 | [41_test_chemistry__test_m2_baseline_produces_structures_and_conserves_energy.md](cases/41_test_chemistry__test_m2_baseline_produces_structures_and_conserves_energy.md) |
| 42 | `tests/test_chemistry.py::test_m2_quick_is_deterministic` | PASSED | 0.0950 | [42_test_chemistry__test_m2_quick_is_deterministic.md](cases/42_test_chemistry__test_m2_quick_is_deterministic.md) |
| 43 | `tests/test_chemistry.py::test_max_bonds_is_respected` | PASSED | 0.0000 | [43_test_chemistry__test_max_bonds_is_respected.md](cases/43_test_chemistry__test_max_bonds_is_respected.md) |
| 44 | `tests/test_chemistry.py::test_no_bond_for_non_allowed_species` | PASSED | 0.0000 | [44_test_chemistry__test_no_bond_for_non_allowed_species.md](cases/44_test_chemistry__test_no_bond_for_non_allowed_species.md) |
| 45 | `tests/test_chemistry.py::test_no_bond_when_species_cannot_bond` | PASSED | 0.0000 | [45_test_chemistry__test_no_bond_when_species_cannot_bond.md](cases/45_test_chemistry__test_no_bond_when_species_cannot_bond.md) |
| 46 | `tests/test_chemistry.py::test_no_bond_without_enough_energy` | PASSED | 0.0000 | [46_test_chemistry__test_no_bond_without_enough_energy.md](cases/46_test_chemistry__test_no_bond_without_enough_energy.md) |
| 47 | `tests/test_cli.py::test_inspect_reads_checkpoint` | PASSED | 0.5490 | [47_test_cli__test_inspect_reads_checkpoint.md](cases/47_test_cli__test_inspect_reads_checkpoint.md) |
| 48 | `tests/test_cli.py::test_invalid_config_reports_error` | PASSED | 0.2170 | [48_test_cli__test_invalid_config_reports_error.md](cases/48_test_cli__test_invalid_config_reports_error.md) |
| 49 | `tests/test_cli.py::test_m2_resume_matches_continuous_run` | PASSED | 0.5420 | [49_test_cli__test_m2_resume_matches_continuous_run.md](cases/49_test_cli__test_m2_resume_matches_continuous_run.md) |
| 50 | `tests/test_cli.py::test_negative_steps_rejected` | PASSED | 0.2790 | [50_test_cli__test_negative_steps_rejected.md](cases/50_test_cli__test_negative_steps_rejected.md) |
| 51 | `tests/test_cli.py::test_resume_matches_continuous_run` | PASSED | 0.5600 | [51_test_cli__test_resume_matches_continuous_run.md](cases/51_test_cli__test_resume_matches_continuous_run.md) |
| 52 | `tests/test_cli.py::test_resume_restores_analysis_state` | PASSED | 0.5480 | [52_test_cli__test_resume_restores_analysis_state.md](cases/52_test_cli__test_resume_restores_analysis_state.md) |
| 53 | `tests/test_cli.py::test_run_m2_writes_events_and_checkpoint` | PASSED | 0.3440 | [53_test_cli__test_run_m2_writes_events_and_checkpoint.md](cases/53_test_cli__test_run_m2_writes_events_and_checkpoint.md) |
| 54 | `tests/test_cli.py::test_run_produces_artifacts` | PASSED | 0.2440 | [54_test_cli__test_run_produces_artifacts.md](cases/54_test_cli__test_run_produces_artifacts.md) |
| 55 | `tests/test_cli.py::test_run_with_tracking` | PASSED | 0.2720 | [55_test_cli__test_run_with_tracking.md](cases/55_test_cli__test_run_with_tracking.md) |
| 56 | `tests/test_cli.py::test_seed_override` | PASSED | 0.2390 | [56_test_cli__test_seed_override.md](cases/56_test_cli__test_seed_override.md) |
| 57 | `tests/test_cli.py::test_version[command0]` | PASSED | 0.2380 | [57_test_cli__test_version[command0].md](cases/57_test_cli__test_version[command0].md) |
| 58 | `tests/test_config.py::test_baseline_config_is_valid` | PASSED | 0.0010 | [58_test_config__test_baseline_config_is_valid.md](cases/58_test_config__test_baseline_config_is_valid.md) |
| 59 | `tests/test_config.py::test_boolean_is_not_an_integer` | PASSED | 0.0000 | [59_test_config__test_boolean_is_not_an_integer.md](cases/59_test_config__test_boolean_is_not_an_integer.md) |
| 60 | `tests/test_config.py::test_catalysis_factor_below_one_rejected` | PASSED | 0.0010 | [60_test_config__test_catalysis_factor_below_one_rejected.md](cases/60_test_config__test_catalysis_factor_below_one_rejected.md) |
| 61 | `tests/test_config.py::test_catalysis_on_non_allowed_pair_rejected` | PASSED | 0.0010 | [61_test_config__test_catalysis_on_non_allowed_pair_rejected.md](cases/61_test_config__test_catalysis_on_non_allowed_pair_rejected.md) |
| 62 | `tests/test_config.py::test_chemistry_requires_usable_pair` | PASSED | 0.0000 | [62_test_config__test_chemistry_requires_usable_pair.md](cases/62_test_config__test_chemistry_requires_usable_pair.md) |
| 63 | `tests/test_config.py::test_dissipation_requires_chemistry` | PASSED | 0.0000 | [63_test_config__test_dissipation_requires_chemistry.md](cases/63_test_config__test_dissipation_requires_chemistry.md) |
| 64 | `tests/test_config.py::test_duplicate_source_rejected` | PASSED | 0.0000 | [64_test_config__test_duplicate_source_rejected.md](cases/64_test_config__test_duplicate_source_rejected.md) |
| 65 | `tests/test_config.py::test_duplicate_species_names_rejected` | PASSED | 0.0000 | [65_test_config__test_duplicate_species_names_rejected.md](cases/65_test_config__test_duplicate_species_names_rejected.md) |
| 66 | `tests/test_config.py::test_energy_block_rejected_before_schema3` | PASSED | 0.0000 | [66_test_config__test_energy_block_rejected_before_schema3.md](cases/66_test_config__test_energy_block_rejected_before_schema3.md) |
| 67 | `tests/test_config.py::test_hash_changes_with_seed` | PASSED | 0.0000 | [67_test_config__test_hash_changes_with_seed.md](cases/67_test_config__test_hash_changes_with_seed.md) |
| 68 | `tests/test_config.py::test_hash_is_independent_of_key_order` | PASSED | 0.0010 | [68_test_config__test_hash_is_independent_of_key_order.md](cases/68_test_config__test_hash_is_independent_of_key_order.md) |
| 69 | `tests/test_config.py::test_invalid_decay_denominator_rejected` | PASSED | 0.0000 | [69_test_config__test_invalid_decay_denominator_rejected.md](cases/69_test_config__test_invalid_decay_denominator_rejected.md) |
| 70 | `tests/test_config.py::test_invalid_json` | PASSED | 0.0010 | [70_test_config__test_invalid_json.md](cases/70_test_config__test_invalid_json.md) |
| 71 | `tests/test_config.py::test_invalid_overflow_rejected` | PASSED | 0.0000 | [71_test_config__test_invalid_overflow_rejected.md](cases/71_test_config__test_invalid_overflow_rejected.md) |
| 72 | `tests/test_config.py::test_m1_and_m2_configs_differ_in_hash` | PASSED | 0.0010 | [72_test_config__test_m1_and_m2_configs_differ_in_hash.md](cases/72_test_config__test_m1_and_m2_configs_differ_in_hash.md) |
| 73 | `tests/test_config.py::test_max_bonds_is_validated` | PASSED | 0.0010 | [73_test_config__test_max_bonds_is_validated.md](cases/73_test_config__test_max_bonds_is_validated.md) |
| 74 | `tests/test_config.py::test_missing_file` | PASSED | 0.0010 | [74_test_config__test_missing_file.md](cases/74_test_config__test_missing_file.md) |
| 75 | `tests/test_config.py::test_move_probability_range_enforced` | PASSED | 0.0000 | [75_test_config__test_move_probability_range_enforced.md](cases/75_test_config__test_move_probability_range_enforced.md) |
| 76 | `tests/test_config.py::test_negative_energy_cost_rejected` | PASSED | 0.0000 | [76_test_config__test_negative_energy_cost_rejected.md](cases/76_test_config__test_negative_energy_cost_rejected.md) |
| 77 | `tests/test_config.py::test_negative_seed_rejected` | PASSED | 0.0000 | [77_test_config__test_negative_seed_rejected.md](cases/77_test_config__test_negative_seed_rejected.md) |
| 78 | `tests/test_config.py::test_roundtrip_preserves_hash` | PASSED | 0.0000 | [78_test_config__test_roundtrip_preserves_hash.md](cases/78_test_config__test_roundtrip_preserves_hash.md) |
| 79 | `tests/test_config.py::test_schema3_roundtrip_preserves_hash` | PASSED | 0.0010 | [79_test_config__test_schema3_roundtrip_preserves_hash.md](cases/79_test_config__test_schema3_roundtrip_preserves_hash.md) |
| 80 | `tests/test_config.py::test_schema3_sources_order_is_canonical` | PASSED | 0.0010 | [80_test_config__test_schema3_sources_order_is_canonical.md](cases/80_test_config__test_schema3_sources_order_is_canonical.md) |
| 81 | `tests/test_config.py::test_source_out_of_grid_rejected` | PASSED | 0.0000 | [81_test_config__test_source_out_of_grid_rejected.md](cases/81_test_config__test_source_out_of_grid_rejected.md) |
| 82 | `tests/test_config.py::test_too_many_particles_rejected` | PASSED | 0.0000 | [82_test_config__test_too_many_particles_rejected.md](cases/82_test_config__test_too_many_particles_rejected.md) |
| 83 | `tests/test_config.py::test_unknown_key_rejected` | PASSED | 0.0000 | [83_test_config__test_unknown_key_rejected.md](cases/83_test_config__test_unknown_key_rejected.md) |
| 84 | `tests/test_config.py::test_unknown_species_in_pairs_rejected` | PASSED | 0.0000 | [84_test_config__test_unknown_species_in_pairs_rejected.md](cases/84_test_config__test_unknown_species_in_pairs_rejected.md) |
| 85 | `tests/test_config.py::test_v1_hash_is_unchanged` | PASSED | 0.0000 | [85_test_config__test_v1_hash_is_unchanged.md](cases/85_test_config__test_v1_hash_is_unchanged.md) |
| 86 | `tests/test_config.py::test_v1_rejects_chemistry_block` | PASSED | 0.0000 | [86_test_config__test_v1_rejects_chemistry_block.md](cases/86_test_config__test_v1_rejects_chemistry_block.md) |
| 87 | `tests/test_config.py::test_v2_hash_ignores_pair_order_and_duplicates` | PASSED | 0.0010 | [87_test_config__test_v2_hash_ignores_pair_order_and_duplicates.md](cases/87_test_config__test_v2_hash_ignores_pair_order_and_duplicates.md) |
| 88 | `tests/test_config.py::test_v2_roundtrip_preserves_hash` | PASSED | 0.0010 | [88_test_config__test_v2_roundtrip_preserves_hash.md](cases/88_test_config__test_v2_roundtrip_preserves_hash.md) |
| 89 | `tests/test_controls.py::test_engine_does_not_import_controls` | PASSED | 0.0010 | [89_test_controls__test_engine_does_not_import_controls.md](cases/89_test_controls__test_engine_does_not_import_controls.md) |
| 90 | `tests/test_controls.py::test_fixture_version_is_declared` | PASSED | 0.0000 | [90_test_controls__test_fixture_version_is_declared.md](cases/90_test_controls__test_fixture_version_is_declared.md) |
| 91 | `tests/test_controls.py::test_negative_immobile_is_not_replication` | PASSED | 0.0120 | [91_test_controls__test_negative_immobile_is_not_replication.md](cases/91_test_controls__test_negative_immobile_is_not_replication.md) |
| 92 | `tests/test_controls.py::test_negative_random_aggregation_is_not_replication` | PASSED | 2.4390 | [92_test_controls__test_negative_random_aggregation_is_not_replication.md](cases/92_test_controls__test_negative_random_aggregation_is_not_replication.md) |
| 93 | `tests/test_controls.py::test_negative_reversible_is_not_replication` | PASSED | 1.7850 | [93_test_controls__test_negative_reversible_is_not_replication.md](cases/93_test_controls__test_negative_reversible_is_not_replication.md) |
| 94 | `tests/test_controls.py::test_negative_stress_cases_are_not_replication` | PASSED | 1.8380 | [94_test_controls__test_negative_stress_cases_are_not_replication.md](cases/94_test_controls__test_negative_stress_cases_are_not_replication.md) |
| 95 | `tests/test_controls.py::test_positive_control_is_detected` | PASSED | 0.0300 | [95_test_controls__test_positive_control_is_detected.md](cases/95_test_controls__test_positive_control_is_detected.md) |
| 96 | `tests/test_controls.py::test_positive_control_is_reproducible` | PASSED | 0.0650 | [96_test_controls__test_positive_control_is_reproducible.md](cases/96_test_controls__test_positive_control_is_reproducible.md) |
| 97 | `tests/test_controls.py::test_simultaneous_identical_structures_are_not_copies` | PASSED | 0.0010 | [97_test_controls__test_simultaneous_identical_structures_are_not_copies.md](cases/97_test_controls__test_simultaneous_identical_structures_are_not_copies.md) |
| 98 | `tests/test_controls.py::test_transient_second_generation_does_not_classify` | PASSED | 0.0010 | [98_test_controls__test_transient_second_generation_does_not_classify.md](cases/98_test_controls__test_transient_second_generation_does_not_classify.md) |
| 99 | `tests/test_dynamics.py::test_blocked_chain_leaves_head_stuck` | PASSED | 0.0000 | [99_test_dynamics__test_blocked_chain_leaves_head_stuck.md](cases/99_test_dynamics__test_blocked_chain_leaves_head_stuck.md) |
| 100 | `tests/test_dynamics.py::test_chain_towards_empty_cell_moves_entirely` | PASSED | 0.0000 | [100_test_dynamics__test_chain_towards_empty_cell_moves_entirely.md](cases/100_test_dynamics__test_chain_towards_empty_cell_moves_entirely.md) |
| 101 | `tests/test_dynamics.py::test_closed_boundary_keeps_particles_inside` | PASSED | 0.0040 | [101_test_dynamics__test_closed_boundary_keeps_particles_inside.md](cases/101_test_dynamics__test_closed_boundary_keeps_particles_inside.md) |
| 102 | `tests/test_dynamics.py::test_contention_produces_single_winner` | PASSED | 0.0000 | [102_test_dynamics__test_contention_produces_single_winner.md](cases/102_test_dynamics__test_contention_produces_single_winner.md) |
| 103 | `tests/test_dynamics.py::test_direction_set_is_von_neumann` | PASSED | 0.0000 | [103_test_dynamics__test_direction_set_is_von_neumann.md](cases/103_test_dynamics__test_direction_set_is_von_neumann.md) |
| 104 | `tests/test_dynamics.py::test_free_move_accepted` | PASSED | 0.0000 | [104_test_dynamics__test_free_move_accepted.md](cases/104_test_dynamics__test_free_move_accepted.md) |
| 105 | `tests/test_dynamics.py::test_immobile_species_never_moves` | PASSED | 0.0010 | [105_test_dynamics__test_immobile_species_never_moves.md](cases/105_test_dynamics__test_immobile_species_never_moves.md) |
| 106 | `tests/test_dynamics.py::test_resolution_is_insertion_order_independent` | PASSED | 0.0000 | [106_test_dynamics__test_resolution_is_insertion_order_independent.md](cases/106_test_dynamics__test_resolution_is_insertion_order_independent.md) |
| 107 | `tests/test_dynamics.py::test_rng_stream_is_two_draws_per_particle_per_step` | PASSED | 0.0010 | [107_test_dynamics__test_rng_stream_is_two_draws_per_particle_per_step.md](cases/107_test_dynamics__test_rng_stream_is_two_draws_per_particle_per_step.md) |
| 108 | `tests/test_dynamics.py::test_single_particle_moves_exactly_one_cell` | PASSED | 0.0010 | [108_test_dynamics__test_single_particle_moves_exactly_one_cell.md](cases/108_test_dynamics__test_single_particle_moves_exactly_one_cell.md) |
| 109 | `tests/test_dynamics.py::test_swap_is_resolved_as_rotation` | PASSED | 0.0000 | [109_test_dynamics__test_swap_is_resolved_as_rotation.md](cases/109_test_dynamics__test_swap_is_resolved_as_rotation.md) |
| 110 | `tests/test_dynamics.py::test_three_particle_cycle` | PASSED | 0.0000 | [110_test_dynamics__test_three_particle_cycle.md](cases/110_test_dynamics__test_three_particle_cycle.md) |
| 111 | `tests/test_energy.py::test_bond_decay_is_exact` | PASSED | 0.0000 | [111_test_energy__test_bond_decay_is_exact.md](cases/111_test_energy__test_bond_decay_is_exact.md) |
| 112 | `tests/test_energy.py::test_breaking_dissipation` | PASSED | 0.0000 | [112_test_energy__test_breaking_dissipation.md](cases/112_test_energy__test_breaking_dissipation.md) |
| 113 | `tests/test_energy.py::test_closed_system_keeps_identity` | PASSED | 0.0060 | [113_test_energy__test_closed_system_keeps_identity.md](cases/113_test_energy__test_closed_system_keeps_identity.md) |
| 114 | `tests/test_energy.py::test_core_modules_do_not_import_nondeterministic_sources` | PASSED | 0.0010 | [114_test_energy__test_core_modules_do_not_import_nondeterministic_sources.md](cases/114_test_energy__test_core_modules_do_not_import_nondeterministic_sources.md) |
| 115 | `tests/test_energy.py::test_formation_dissipation` | PASSED | 0.0000 | [115_test_energy__test_formation_dissipation.md](cases/115_test_energy__test_formation_dissipation.md) |
| 116 | `tests/test_energy.py::test_golden_hash_m2_is_preserved` | PASSED | 0.0530 | [116_test_energy__test_golden_hash_m2_is_preserved.md](cases/116_test_energy__test_golden_hash_m2_is_preserved.md) |
| 117 | `tests/test_energy.py::test_ledger_tampering_is_detected` | PASSED | 0.0070 | [117_test_energy__test_ledger_tampering_is_detected.md](cases/117_test_energy__test_ledger_tampering_is_detected.md) |
| 118 | `tests/test_energy.py::test_movement_cost_blocks_when_insufficient` | PASSED | 0.0000 | [118_test_energy__test_movement_cost_blocks_when_insufficient.md](cases/118_test_energy__test_movement_cost_blocks_when_insufficient.md) |
| 119 | `tests/test_energy.py::test_movement_cost_charged_per_move` | PASSED | 0.0010 | [119_test_energy__test_movement_cost_charged_per_move.md](cases/119_test_energy__test_movement_cost_charged_per_move.md) |
| 120 | `tests/test_energy.py::test_open_run_is_deterministic` | PASSED | 0.0860 | [120_test_energy__test_open_run_is_deterministic.md](cases/120_test_energy__test_open_run_is_deterministic.md) |
| 121 | `tests/test_energy.py::test_open_run_keeps_identity` | PASSED | 0.0490 | [121_test_energy__test_open_run_keeps_identity.md](cases/121_test_energy__test_open_run_keeps_identity.md) |
| 122 | `tests/test_energy.py::test_particle_decay_is_exact` | PASSED | 0.0000 | [122_test_energy__test_particle_decay_is_exact.md](cases/122_test_energy__test_particle_decay_is_exact.md) |
| 123 | `tests/test_energy.py::test_particle_decay_uses_identity_not_index` | PASSED | 0.0000 | [123_test_energy__test_particle_decay_uses_identity_not_index.md](cases/123_test_energy__test_particle_decay_uses_identity_not_index.md) |
| 124 | `tests/test_energy.py::test_priority_uses_identity` | PASSED | 0.0000 | [124_test_energy__test_priority_uses_identity.md](cases/124_test_energy__test_priority_uses_identity.md) |
| 125 | `tests/test_energy.py::test_rng_budget_with_flows_disabled` | PASSED | 0.0010 | [125_test_energy__test_rng_budget_with_flows_disabled.md](cases/125_test_energy__test_rng_budget_with_flows_disabled.md) |
| 126 | `tests/test_energy.py::test_source_accumulator_is_exact` | PASSED | 0.0030 | [126_test_energy__test_source_accumulator_is_exact.md](cases/126_test_energy__test_source_accumulator_is_exact.md) |
| 127 | `tests/test_energy.py::test_source_accumulator_out_of_range_is_detected` | PASSED | 0.0010 | [127_test_energy__test_source_accumulator_out_of_range_is_detected.md](cases/127_test_energy__test_source_accumulator_out_of_range_is_detected.md) |
| 128 | `tests/test_energy.py::test_source_buffer_is_delivered_to_a_visiting_particle` | PASSED | 0.0000 | [128_test_energy__test_source_buffer_is_delivered_to_a_visiting_particle.md](cases/128_test_energy__test_source_buffer_is_delivered_to_a_visiting_particle.md) |
| 129 | `tests/test_energy.py::test_source_capacity_and_unabsorbed` | PASSED | 0.0010 | [129_test_energy__test_source_capacity_and_unabsorbed.md](cases/129_test_energy__test_source_capacity_and_unabsorbed.md) |
| 130 | `tests/test_energy.py::test_source_on_empty_cell_is_unabsorbed` | PASSED | 0.0000 | [130_test_energy__test_source_on_empty_cell_is_unabsorbed.md](cases/130_test_energy__test_source_on_empty_cell_is_unabsorbed.md) |
| 131 | `tests/test_energy.py::test_validate_detects_unsorted_identifiers` | PASSED | 0.0010 | [131_test_energy__test_validate_detects_unsorted_identifiers.md](cases/131_test_energy__test_validate_detects_unsorted_identifiers.md) |
| 132 | `tests/test_invariants.py::test_energy_is_conserved` | PASSED | 0.0110 | [132_test_invariants__test_energy_is_conserved.md](cases/132_test_invariants__test_energy_is_conserved.md) |
| 133 | `tests/test_invariants.py::test_energy_with_bonds_is_conserved` | PASSED | 0.0700 | [133_test_invariants__test_energy_with_bonds_is_conserved.md](cases/133_test_invariants__test_energy_with_bonds_is_conserved.md) |
| 134 | `tests/test_invariants.py::test_no_multiple_occupancy` | PASSED | 0.0080 | [134_test_invariants__test_no_multiple_occupancy.md](cases/134_test_invariants__test_no_multiple_occupancy.md) |
| 135 | `tests/test_invariants.py::test_particle_count_conserved` | PASSED | 0.0080 | [135_test_invariants__test_particle_count_conserved.md](cases/135_test_invariants__test_particle_count_conserved.md) |
| 136 | `tests/test_invariants.py::test_periodic_boundaries` | PASSED | 0.0110 | [136_test_invariants__test_periodic_boundaries.md](cases/136_test_invariants__test_periodic_boundaries.md) |
| 137 | `tests/test_invariants.py::test_species_quantities_conserved` | PASSED | 0.0080 | [137_test_invariants__test_species_quantities_conserved.md](cases/137_test_invariants__test_species_quantities_conserved.md) |
| 138 | `tests/test_invariants.py::test_state_hash_is_stable_and_sensitive` | PASSED | 0.0010 | [138_test_invariants__test_state_hash_is_stable_and_sensitive.md](cases/138_test_invariants__test_state_hash_is_stable_and_sensitive.md) |
| 139 | `tests/test_invariants.py::test_store_rejects_double_placement` | PASSED | 0.0000 | [139_test_invariants__test_store_rejects_double_placement.md](cases/139_test_invariants__test_store_rejects_double_placement.md) |
| 140 | `tests/test_invariants.py::test_store_rejects_duplicate_identifiers` | PASSED | 0.0000 | [140_test_invariants__test_store_rejects_duplicate_identifiers.md](cases/140_test_invariants__test_store_rejects_duplicate_identifiers.md) |
| 141 | `tests/test_invariants.py::test_store_rejects_out_of_grid_particle` | PASSED | 0.0000 | [141_test_invariants__test_store_rejects_out_of_grid_particle.md](cases/141_test_invariants__test_store_rejects_out_of_grid_particle.md) |
| 142 | `tests/test_invariants.py::test_validate_detects_bond_beyond_max_bonds` | PASSED | 0.0010 | [142_test_invariants__test_validate_detects_bond_beyond_max_bonds.md](cases/142_test_invariants__test_validate_detects_bond_beyond_max_bonds.md) |
| 143 | `tests/test_invariants.py::test_validate_detects_bonds_without_chemistry` | PASSED | 0.0010 | [143_test_invariants__test_validate_detects_bonds_without_chemistry.md](cases/143_test_invariants__test_validate_detects_bonds_without_chemistry.md) |
| 144 | `tests/test_invariants.py::test_validate_detects_degree_mismatch` | PASSED | 0.0010 | [144_test_invariants__test_validate_detects_degree_mismatch.md](cases/144_test_invariants__test_validate_detects_degree_mismatch.md) |
| 145 | `tests/test_invariants.py::test_validate_detects_duplicate_cell` | PASSED | 0.0010 | [145_test_invariants__test_validate_detects_duplicate_cell.md](cases/145_test_invariants__test_validate_detects_duplicate_cell.md) |
| 146 | `tests/test_invariants.py::test_validate_detects_grid_desynchronisation` | PASSED | 0.0010 | [146_test_invariants__test_validate_detects_grid_desynchronisation.md](cases/146_test_invariants__test_validate_detects_grid_desynchronisation.md) |
| 147 | `tests/test_invariants.py::test_validate_detects_identity_above_next_id` | PASSED | 0.0010 | [147_test_invariants__test_validate_detects_identity_above_next_id.md](cases/147_test_invariants__test_validate_detects_identity_above_next_id.md) |
| 148 | `tests/test_invariants.py::test_validate_detects_invalid_species_index` | PASSED | 0.0010 | [148_test_invariants__test_validate_detects_invalid_species_index.md](cases/148_test_invariants__test_validate_detects_invalid_species_index.md) |
| 149 | `tests/test_invariants.py::test_validate_detects_missing_particle` | PASSED | 0.0010 | [149_test_invariants__test_validate_detects_missing_particle.md](cases/149_test_invariants__test_validate_detects_missing_particle.md) |
| 150 | `tests/test_invariants.py::test_validate_detects_non_adjacent_bond` | PASSED | 0.0020 | [150_test_invariants__test_validate_detects_non_adjacent_bond.md](cases/150_test_invariants__test_validate_detects_non_adjacent_bond.md) |
| 151 | `tests/test_invariants.py::test_validate_detects_out_of_bounds_particle` | PASSED | 0.0010 | [151_test_invariants__test_validate_detects_out_of_bounds_particle.md](cases/151_test_invariants__test_validate_detects_out_of_bounds_particle.md) |
| 152 | `tests/test_m6_2e.py::test_manifest_freezes_v2_criteria` | PASSED | 0.0000 | [152_test_m6_2e__test_manifest_freezes_v2_criteria.md](cases/152_test_m6_2e__test_manifest_freezes_v2_criteria.md) |
| 153 | `tests/test_m6_2e.py::test_manifest_references_identical_m6_runs` | PASSED | 0.0080 | [153_test_m6_2e__test_manifest_references_identical_m6_runs.md](cases/153_test_m6_2e__test_manifest_references_identical_m6_runs.md) |
| 154 | `tests/test_m6_2e.py::test_reanalysis_is_complete_and_matches_m6_worlds` | PASSED | 0.0010 | [154_test_m6_2e__test_reanalysis_is_complete_and_matches_m6_worlds.md](cases/154_test_m6_2e__test_reanalysis_is_complete_and_matches_m6_worlds.md) |
| 155 | `tests/test_metrics.py::test_peak_memory_is_plausible` | PASSED | 0.0000 | [155_test_metrics__test_peak_memory_is_plausible.md](cases/155_test_metrics__test_peak_memory_is_plausible.md) |
| 156 | `tests/test_metrics.py::test_runtime_versions_are_recorded` | PASSED | 0.0010 | [156_test_metrics__test_runtime_versions_are_recorded.md](cases/156_test_metrics__test_runtime_versions_are_recorded.md) |
| 157 | `tests/test_metrics.py::test_summary_contains_required_fields` | PASSED | 0.0020 | [157_test_metrics__test_summary_contains_required_fields.md](cases/157_test_metrics__test_summary_contains_required_fields.md) |
| 158 | `tests/test_replication_v2.py::test_default_threshold_requires_two_generations` | PASSED | 0.0020 | [158_test_replication_v2__test_default_threshold_requires_two_generations.md](cases/158_test_replication_v2__test_default_threshold_requires_two_generations.md) |
| 159 | `tests/test_replication_v2.py::test_detector_is_deterministic` | PASSED | 0.0790 | [159_test_replication_v2__test_detector_is_deterministic.md](cases/159_test_replication_v2__test_detector_is_deterministic.md) |
| 160 | `tests/test_replication_v2.py::test_detector_version_is_declared` | PASSED | 0.0000 | [160_test_replication_v2__test_detector_version_is_declared.md](cases/160_test_replication_v2__test_detector_version_is_declared.md) |
| 161 | `tests/test_replication_v2.py::test_negative_controls_are_not_replication` | PASSED | 4.4010 | [161_test_replication_v2__test_negative_controls_are_not_replication.md](cases/161_test_replication_v2__test_negative_controls_are_not_replication.md) |
| 162 | `tests/test_replication_v2.py::test_positive_control_is_detected` | PASSED | 0.0330 | [162_test_replication_v2__test_positive_control_is_detected.md](cases/162_test_replication_v2__test_positive_control_is_detected.md) |
| 163 | `tests/test_replication_v2.py::test_progressive_assembly_is_detected` | PASSED | 0.0020 | [163_test_replication_v2__test_progressive_assembly_is_detected.md](cases/163_test_replication_v2__test_progressive_assembly_is_detected.md) |
| 164 | `tests/test_replication_v2.py::test_simultaneous_identical_structures_are_not_copies` | PASSED | 0.0010 | [164_test_replication_v2__test_simultaneous_identical_structures_are_not_copies.md](cases/164_test_replication_v2__test_simultaneous_identical_structures_are_not_copies.md) |
| 165 | `tests/test_reproducibility.py::test_baseline_config_is_reproducible` | PASSED | 0.1970 | [165_test_reproducibility__test_baseline_config_is_reproducible.md](cases/165_test_reproducibility__test_baseline_config_is_reproducible.md) |
| 166 | `tests/test_reproducibility.py::test_different_seed_different_result` | PASSED | 0.0050 | [166_test_reproducibility__test_different_seed_different_result.md](cases/166_test_reproducibility__test_different_seed_different_result.md) |
| 167 | `tests/test_reproducibility.py::test_initial_placement_is_seed_deterministic` | PASSED | 0.0010 | [167_test_reproducibility__test_initial_placement_is_seed_deterministic.md](cases/167_test_reproducibility__test_initial_placement_is_seed_deterministic.md) |
| 168 | `tests/test_reproducibility.py::test_m1_run_reproduces_the_published_hash` | PASSED | 3.9920 | [168_test_reproducibility__test_m1_run_reproduces_the_published_hash.md](cases/168_test_reproducibility__test_m1_run_reproduces_the_published_hash.md) |
| 169 | `tests/test_reproducibility.py::test_repeated_advance_matches_single_call` | PASSED | 0.0040 | [169_test_reproducibility__test_repeated_advance_matches_single_call.md](cases/169_test_reproducibility__test_repeated_advance_matches_single_call.md) |
| 170 | `tests/test_reproducibility.py::test_same_seed_same_result` | PASSED | 0.0180 | [170_test_reproducibility__test_same_seed_same_result.md](cases/170_test_reproducibility__test_same_seed_same_result.md) |
| 171 | `tests/test_structures.py::test_birth_and_death` | PASSED | 0.0010 | [171_test_structures__test_birth_and_death.md](cases/171_test_structures__test_birth_and_death.md) |
| 172 | `tests/test_structures.py::test_chain_signature_distinguishes_composition` | PASSED | 0.0010 | [172_test_structures__test_chain_signature_distinguishes_composition.md](cases/172_test_structures__test_chain_signature_distinguishes_composition.md) |
| 173 | `tests/test_structures.py::test_chain_signature_is_invariant_under_relabeling` | PASSED | 0.0010 | [173_test_structures__test_chain_signature_is_invariant_under_relabeling.md](cases/173_test_structures__test_chain_signature_is_invariant_under_relabeling.md) |
| 174 | `tests/test_structures.py::test_cycles_are_fingerprints_not_exact` | PASSED | 0.0010 | [174_test_structures__test_cycles_are_fingerprints_not_exact.md](cases/174_test_structures__test_cycles_are_fingerprints_not_exact.md) |
| 175 | `tests/test_structures.py::test_exact_signature_collision_is_not_ambiguity` | PASSED | 0.0010 | [175_test_structures__test_exact_signature_collision_is_not_ambiguity.md](cases/175_test_structures__test_exact_signature_collision_is_not_ambiguity.md) |
| 176 | `tests/test_structures.py::test_fuzzy_collision_is_reported_as_ambiguity` | PASSED | 0.0010 | [176_test_structures__test_fuzzy_collision_is_reported_as_ambiguity.md](cases/176_test_structures__test_fuzzy_collision_is_reported_as_ambiguity.md) |
| 177 | `tests/test_structures.py::test_growth_and_shrink_keep_identity` | PASSED | 0.0010 | [177_test_structures__test_growth_and_shrink_keep_identity.md](cases/177_test_structures__test_growth_and_shrink_keep_identity.md) |
| 178 | `tests/test_structures.py::test_lifetime_counts_steps_alive` | PASSED | 0.0010 | [178_test_structures__test_lifetime_counts_steps_alive.md](cases/178_test_structures__test_lifetime_counts_steps_alive.md) |
| 179 | `tests/test_structures.py::test_merge_creates_one_structure` | PASSED | 0.0010 | [179_test_structures__test_merge_creates_one_structure.md](cases/179_test_structures__test_merge_creates_one_structure.md) |
| 180 | `tests/test_structures.py::test_signature_is_a_signature_instance` | PASSED | 0.0000 | [180_test_structures__test_signature_is_a_signature_instance.md](cases/180_test_structures__test_signature_is_a_signature_instance.md) |
| 181 | `tests/test_structures.py::test_split_creates_two_structures` | PASSED | 0.0010 | [181_test_structures__test_split_creates_two_structures.md](cases/181_test_structures__test_split_creates_two_structures.md) |
| 182 | `tests/test_structures.py::test_tracker_is_deterministic` | PASSED | 0.0010 | [182_test_structures__test_tracker_is_deterministic.md](cases/182_test_structures__test_tracker_is_deterministic.md) |
| 183 | `tests/test_structures.py::test_tracker_writes_jsonl_files` | PASSED | 0.0010 | [183_test_structures__test_tracker_writes_jsonl_files.md](cases/183_test_structures__test_tracker_writes_jsonl_files.md) |
| 184 | `tests/test_structures.py::test_tracking_does_not_change_the_world` | PASSED | 0.0010 | [184_test_structures__test_tracking_does_not_change_the_world.md](cases/184_test_structures__test_tracking_does_not_change_the_world.md) |
| 185 | `tests/test_structures.py::test_transform_same_size_new_topology` | PASSED | 0.0010 | [185_test_structures__test_transform_same_size_new_topology.md](cases/185_test_structures__test_transform_same_size_new_topology.md) |
| 186 | `tests/test_structures.py::test_tree_signature_distinguishes_shape` | PASSED | 0.0010 | [186_test_structures__test_tree_signature_distinguishes_shape.md](cases/186_test_structures__test_tree_signature_distinguishes_shape.md) |

## File

- `junit.xml` — risultato macchina-leggibile (JUnit XML)
- `pytest.log` — log completo di pytest
- `results.json` — tutti i casi e le evidenze in forma strutturata
- `cases/` — un file per ogni caso di test
- `evidence/` — un file per ogni test obbligatorio, con misure reali
