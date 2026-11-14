# Risultati dei test

Generato: 2026-11-14T21:52:16+00:00 · Comando: `.venv/bin/python -m pytest -v`

**104 superati, 0 falliti, 104 casi in 12.78 s** (exit code 0).

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
| M1-08 | Rilevamento di una violazione intenzionale delle invarianti | **PASS** | [M1-08_violazioni_intenzionali.md](evidence/M1-08_violazioni_intenzionali.md) | 11/11 superati |
| M2-01 | Legami reversibili con costo energetico | **PASS** | [M2-01_legami_reversibili.md](evidence/M2-01_legami_reversibili.md) | 3/3 superati |
| M2-02 | Conservazione dell'energia con i legami | **PASS** | [M2-02_energia_legami.md](evidence/M2-02_energia_legami.md) | 2/2 superati |
| M2-03 | Coppie ammesse, max_bonds e adiacenza | **PASS** | [M2-03_regole_locali.md](evidence/M2-03_regole_locali.md) | 6/6 superati |
| M2-04 | Catalisi locale per differenza | **PASS** | [M2-04_catalisi.md](evidence/M2-04_catalisi.md) | 2/2 superati |
| M2-05 | Aggregati: distribuzione delle dimensioni | **PASS** | [M2-05_aggregati.md](evidence/M2-05_aggregati.md) | 2/2 superati |
| M2-06 | Determinismo e ripresa con la chimica | **PASS** | [M2-06_determinismo_chimica.md](evidence/M2-06_determinismo_chimica.md) | 3/3 superati |
| M2-07 | Migrazione dei checkpoint M1 | **PASS** | [M2-07_migrazione_checkpoint.md](evidence/M2-07_migrazione_checkpoint.md) | 2/2 superati |

## Tutti i casi

| # | Caso | Stato | Durata (s) | File |
|---|---|---|---|---|
| 1 | `tests/test_checkpoint.py::test_checkpoint_does_not_mutate_world` | PASSED | 0.0030 | [01_test_checkpoint__test_checkpoint_does_not_mutate_world.md](cases/01_test_checkpoint__test_checkpoint_does_not_mutate_world.md) |
| 2 | `tests/test_checkpoint.py::test_detects_energy_imbalance` | PASSED | 0.0020 | [02_test_checkpoint__test_detects_energy_imbalance.md](cases/02_test_checkpoint__test_detects_energy_imbalance.md) |
| 3 | `tests/test_checkpoint.py::test_detects_invalid_json` | PASSED | 0.0010 | [03_test_checkpoint__test_detects_invalid_json.md](cases/03_test_checkpoint__test_detects_invalid_json.md) |
| 4 | `tests/test_checkpoint.py::test_detects_missing_rng_state` | PASSED | 0.0020 | [04_test_checkpoint__test_detects_missing_rng_state.md](cases/04_test_checkpoint__test_detects_missing_rng_state.md) |
| 5 | `tests/test_checkpoint.py::test_detects_tampered_bond_energy` | PASSED | 0.0140 | [05_test_checkpoint__test_detects_tampered_bond_energy.md](cases/05_test_checkpoint__test_detects_tampered_bond_energy.md) |
| 6 | `tests/test_checkpoint.py::test_detects_tampered_config_hash` | PASSED | 0.0020 | [06_test_checkpoint__test_detects_tampered_config_hash.md](cases/06_test_checkpoint__test_detects_tampered_config_hash.md) |
| 7 | `tests/test_checkpoint.py::test_detects_tampered_identity` | PASSED | 0.0030 | [07_test_checkpoint__test_detects_tampered_identity.md](cases/07_test_checkpoint__test_detects_tampered_identity.md) |
| 8 | `tests/test_checkpoint.py::test_detects_tampered_particle` | PASSED | 0.0030 | [08_test_checkpoint__test_detects_tampered_particle.md](cases/08_test_checkpoint__test_detects_tampered_particle.md) |
| 9 | `tests/test_checkpoint.py::test_detects_tampered_particle_energy` | PASSED | 0.0140 | [09_test_checkpoint__test_detects_tampered_particle_energy.md](cases/09_test_checkpoint__test_detects_tampered_particle_energy.md) |
| 10 | `tests/test_checkpoint.py::test_detects_wrong_format` | PASSED | 0.0010 | [10_test_checkpoint__test_detects_wrong_format.md](cases/10_test_checkpoint__test_detects_wrong_format.md) |
| 11 | `tests/test_checkpoint.py::test_missing_file` | PASSED | 0.0010 | [11_test_checkpoint__test_missing_file.md](cases/11_test_checkpoint__test_missing_file.md) |
| 12 | `tests/test_checkpoint.py::test_no_temporary_file_left_behind` | PASSED | 0.0010 | [12_test_checkpoint__test_no_temporary_file_left_behind.md](cases/12_test_checkpoint__test_no_temporary_file_left_behind.md) |
| 13 | `tests/test_checkpoint.py::test_repeated_save_load_cycles_are_stable` | PASSED | 0.0070 | [13_test_checkpoint__test_repeated_save_load_cycles_are_stable.md](cases/13_test_checkpoint__test_repeated_save_load_cycles_are_stable.md) |
| 14 | `tests/test_checkpoint.py::test_resume_is_equivalent_to_continuous_run` | PASSED | 0.0130 | [14_test_checkpoint__test_resume_is_equivalent_to_continuous_run.md](cases/14_test_checkpoint__test_resume_is_equivalent_to_continuous_run.md) |
| 15 | `tests/test_checkpoint.py::test_roundtrip_preserves_state` | PASSED | 0.0210 | [15_test_checkpoint__test_roundtrip_preserves_state.md](cases/15_test_checkpoint__test_roundtrip_preserves_state.md) |
| 16 | `tests/test_checkpoint.py::test_v1_checkpoint_is_migrated` | PASSED | 0.0020 | [16_test_checkpoint__test_v1_checkpoint_is_migrated.md](cases/16_test_checkpoint__test_v1_checkpoint_is_migrated.md) |
| 17 | `tests/test_checkpoint.py::test_v1_checkpoint_with_bonds_is_rejected` | PASSED | 0.0020 | [17_test_checkpoint__test_v1_checkpoint_with_bonds_is_rejected.md](cases/17_test_checkpoint__test_v1_checkpoint_with_bonds_is_rejected.md) |
| 18 | `tests/test_checkpoint.py::test_v2_resume_is_equivalent_to_continuous_run` | PASSED | 0.0650 | [18_test_checkpoint__test_v2_resume_is_equivalent_to_continuous_run.md](cases/18_test_checkpoint__test_v2_resume_is_equivalent_to_continuous_run.md) |
| 19 | `tests/test_checkpoint.py::test_v2_roundtrip_preserves_bonds_and_energy` | PASSED | 0.0260 | [19_test_checkpoint__test_v2_roundtrip_preserves_bonds_and_energy.md](cases/19_test_checkpoint__test_v2_roundtrip_preserves_bonds_and_energy.md) |
| 20 | `tests/test_chemistry.py::test_aggregate_statistics` | PASSED | 0.0000 | [20_test_chemistry__test_aggregate_statistics.md](cases/20_test_chemistry__test_aggregate_statistics.md) |
| 21 | `tests/test_chemistry.py::test_bond_forms_between_adjacent_allowed_particles` | PASSED | 0.0010 | [21_test_chemistry__test_bond_forms_between_adjacent_allowed_particles.md](cases/21_test_chemistry__test_bond_forms_between_adjacent_allowed_particles.md) |
| 22 | `tests/test_chemistry.py::test_bonded_particles_do_not_move` | PASSED | 0.0010 | [22_test_chemistry__test_bonded_particles_do_not_move.md](cases/22_test_chemistry__test_bonded_particles_do_not_move.md) |
| 23 | `tests/test_chemistry.py::test_breaking_returns_energy` | PASSED | 0.0010 | [23_test_chemistry__test_breaking_returns_energy.md](cases/23_test_chemistry__test_breaking_returns_energy.md) |
| 24 | `tests/test_chemistry.py::test_catalysis_config_changes_chemistry` | PASSED | 0.2090 | [24_test_chemistry__test_catalysis_config_changes_chemistry.md](cases/24_test_chemistry__test_catalysis_config_changes_chemistry.md) |
| 25 | `tests/test_chemistry.py::test_catalysis_multiplies_only_when_adjacent` | PASSED | 0.0010 | [25_test_chemistry__test_catalysis_multiplies_only_when_adjacent.md](cases/25_test_chemistry__test_catalysis_multiplies_only_when_adjacent.md) |
| 26 | `tests/test_chemistry.py::test_chains_grow_to_max_bonds` | PASSED | 0.0010 | [26_test_chemistry__test_chains_grow_to_max_bonds.md](cases/26_test_chemistry__test_chains_grow_to_max_bonds.md) |
| 27 | `tests/test_chemistry.py::test_m2_baseline_produces_structures_and_conserves_energy` | PASSED | 2.0520 | [27_test_chemistry__test_m2_baseline_produces_structures_and_conserves_energy.md](cases/27_test_chemistry__test_m2_baseline_produces_structures_and_conserves_energy.md) |
| 28 | `tests/test_chemistry.py::test_m2_quick_is_deterministic` | PASSED | 0.1160 | [28_test_chemistry__test_m2_quick_is_deterministic.md](cases/28_test_chemistry__test_m2_quick_is_deterministic.md) |
| 29 | `tests/test_chemistry.py::test_max_bonds_is_respected` | PASSED | 0.0000 | [29_test_chemistry__test_max_bonds_is_respected.md](cases/29_test_chemistry__test_max_bonds_is_respected.md) |
| 30 | `tests/test_chemistry.py::test_no_bond_for_non_allowed_species` | PASSED | 0.0010 | [30_test_chemistry__test_no_bond_for_non_allowed_species.md](cases/30_test_chemistry__test_no_bond_for_non_allowed_species.md) |
| 31 | `tests/test_chemistry.py::test_no_bond_when_species_cannot_bond` | PASSED | 0.0010 | [31_test_chemistry__test_no_bond_when_species_cannot_bond.md](cases/31_test_chemistry__test_no_bond_when_species_cannot_bond.md) |
| 32 | `tests/test_chemistry.py::test_no_bond_without_enough_energy` | PASSED | 0.0000 | [32_test_chemistry__test_no_bond_without_enough_energy.md](cases/32_test_chemistry__test_no_bond_without_enough_energy.md) |
| 33 | `tests/test_cli.py::test_inspect_reads_checkpoint` | PASSED | 0.8560 | [33_test_cli__test_inspect_reads_checkpoint.md](cases/33_test_cli__test_inspect_reads_checkpoint.md) |
| 34 | `tests/test_cli.py::test_invalid_config_reports_error` | PASSED | 0.3010 | [34_test_cli__test_invalid_config_reports_error.md](cases/34_test_cli__test_invalid_config_reports_error.md) |
| 35 | `tests/test_cli.py::test_m2_resume_matches_continuous_run` | PASSED | 0.6640 | [35_test_cli__test_m2_resume_matches_continuous_run.md](cases/35_test_cli__test_m2_resume_matches_continuous_run.md) |
| 36 | `tests/test_cli.py::test_negative_steps_rejected` | PASSED | 0.3590 | [36_test_cli__test_negative_steps_rejected.md](cases/36_test_cli__test_negative_steps_rejected.md) |
| 37 | `tests/test_cli.py::test_resume_matches_continuous_run` | PASSED | 0.6060 | [37_test_cli__test_resume_matches_continuous_run.md](cases/37_test_cli__test_resume_matches_continuous_run.md) |
| 38 | `tests/test_cli.py::test_run_m2_writes_events_and_checkpoint` | PASSED | 0.3050 | [38_test_cli__test_run_m2_writes_events_and_checkpoint.md](cases/38_test_cli__test_run_m2_writes_events_and_checkpoint.md) |
| 39 | `tests/test_cli.py::test_run_produces_artifacts` | PASSED | 0.2880 | [39_test_cli__test_run_produces_artifacts.md](cases/39_test_cli__test_run_produces_artifacts.md) |
| 40 | `tests/test_cli.py::test_seed_override` | PASSED | 0.3310 | [40_test_cli__test_seed_override.md](cases/40_test_cli__test_seed_override.md) |
| 41 | `tests/test_cli.py::test_version[command0]` | PASSED | 0.3100 | [41_test_cli__test_version[command0].md](cases/41_test_cli__test_version[command0].md) |
| 42 | `tests/test_config.py::test_baseline_config_is_valid` | PASSED | 0.0010 | [42_test_config__test_baseline_config_is_valid.md](cases/42_test_config__test_baseline_config_is_valid.md) |
| 43 | `tests/test_config.py::test_boolean_is_not_an_integer` | PASSED | 0.0000 | [43_test_config__test_boolean_is_not_an_integer.md](cases/43_test_config__test_boolean_is_not_an_integer.md) |
| 44 | `tests/test_config.py::test_catalysis_factor_below_one_rejected` | PASSED | 0.0030 | [44_test_config__test_catalysis_factor_below_one_rejected.md](cases/44_test_config__test_catalysis_factor_below_one_rejected.md) |
| 45 | `tests/test_config.py::test_catalysis_on_non_allowed_pair_rejected` | PASSED | 0.0010 | [45_test_config__test_catalysis_on_non_allowed_pair_rejected.md](cases/45_test_config__test_catalysis_on_non_allowed_pair_rejected.md) |
| 46 | `tests/test_config.py::test_chemistry_requires_usable_pair` | PASSED | 0.0010 | [46_test_config__test_chemistry_requires_usable_pair.md](cases/46_test_config__test_chemistry_requires_usable_pair.md) |
| 47 | `tests/test_config.py::test_duplicate_species_names_rejected` | PASSED | 0.0000 | [47_test_config__test_duplicate_species_names_rejected.md](cases/47_test_config__test_duplicate_species_names_rejected.md) |
| 48 | `tests/test_config.py::test_hash_changes_with_seed` | PASSED | 0.0000 | [48_test_config__test_hash_changes_with_seed.md](cases/48_test_config__test_hash_changes_with_seed.md) |
| 49 | `tests/test_config.py::test_hash_is_independent_of_key_order` | PASSED | 0.0010 | [49_test_config__test_hash_is_independent_of_key_order.md](cases/49_test_config__test_hash_is_independent_of_key_order.md) |
| 50 | `tests/test_config.py::test_invalid_json` | PASSED | 0.0010 | [50_test_config__test_invalid_json.md](cases/50_test_config__test_invalid_json.md) |
| 51 | `tests/test_config.py::test_m1_and_m2_configs_differ_in_hash` | PASSED | 0.0010 | [51_test_config__test_m1_and_m2_configs_differ_in_hash.md](cases/51_test_config__test_m1_and_m2_configs_differ_in_hash.md) |
| 52 | `tests/test_config.py::test_max_bonds_is_validated` | PASSED | 0.0000 | [52_test_config__test_max_bonds_is_validated.md](cases/52_test_config__test_max_bonds_is_validated.md) |
| 53 | `tests/test_config.py::test_missing_file` | PASSED | 0.0010 | [53_test_config__test_missing_file.md](cases/53_test_config__test_missing_file.md) |
| 54 | `tests/test_config.py::test_move_probability_range_enforced` | PASSED | 0.0000 | [54_test_config__test_move_probability_range_enforced.md](cases/54_test_config__test_move_probability_range_enforced.md) |
| 55 | `tests/test_config.py::test_negative_seed_rejected` | PASSED | 0.0000 | [55_test_config__test_negative_seed_rejected.md](cases/55_test_config__test_negative_seed_rejected.md) |
| 56 | `tests/test_config.py::test_roundtrip_preserves_hash` | PASSED | 0.0010 | [56_test_config__test_roundtrip_preserves_hash.md](cases/56_test_config__test_roundtrip_preserves_hash.md) |
| 57 | `tests/test_config.py::test_too_many_particles_rejected` | PASSED | 0.0000 | [57_test_config__test_too_many_particles_rejected.md](cases/57_test_config__test_too_many_particles_rejected.md) |
| 58 | `tests/test_config.py::test_unknown_key_rejected` | PASSED | 0.0000 | [58_test_config__test_unknown_key_rejected.md](cases/58_test_config__test_unknown_key_rejected.md) |
| 59 | `tests/test_config.py::test_unknown_species_in_pairs_rejected` | PASSED | 0.0010 | [59_test_config__test_unknown_species_in_pairs_rejected.md](cases/59_test_config__test_unknown_species_in_pairs_rejected.md) |
| 60 | `tests/test_config.py::test_v1_hash_is_unchanged` | PASSED | 0.0010 | [60_test_config__test_v1_hash_is_unchanged.md](cases/60_test_config__test_v1_hash_is_unchanged.md) |
| 61 | `tests/test_config.py::test_v1_rejects_chemistry_block` | PASSED | 0.0000 | [61_test_config__test_v1_rejects_chemistry_block.md](cases/61_test_config__test_v1_rejects_chemistry_block.md) |
| 62 | `tests/test_config.py::test_v2_hash_ignores_pair_order_and_duplicates` | PASSED | 0.0010 | [62_test_config__test_v2_hash_ignores_pair_order_and_duplicates.md](cases/62_test_config__test_v2_hash_ignores_pair_order_and_duplicates.md) |
| 63 | `tests/test_config.py::test_v2_roundtrip_preserves_hash` | PASSED | 0.0010 | [63_test_config__test_v2_roundtrip_preserves_hash.md](cases/63_test_config__test_v2_roundtrip_preserves_hash.md) |
| 64 | `tests/test_dynamics.py::test_blocked_chain_leaves_head_stuck` | PASSED | 0.0000 | [64_test_dynamics__test_blocked_chain_leaves_head_stuck.md](cases/64_test_dynamics__test_blocked_chain_leaves_head_stuck.md) |
| 65 | `tests/test_dynamics.py::test_chain_towards_empty_cell_moves_entirely` | PASSED | 0.0000 | [65_test_dynamics__test_chain_towards_empty_cell_moves_entirely.md](cases/65_test_dynamics__test_chain_towards_empty_cell_moves_entirely.md) |
| 66 | `tests/test_dynamics.py::test_closed_boundary_keeps_particles_inside` | PASSED | 0.0040 | [66_test_dynamics__test_closed_boundary_keeps_particles_inside.md](cases/66_test_dynamics__test_closed_boundary_keeps_particles_inside.md) |
| 67 | `tests/test_dynamics.py::test_contention_produces_single_winner` | PASSED | 0.0000 | [67_test_dynamics__test_contention_produces_single_winner.md](cases/67_test_dynamics__test_contention_produces_single_winner.md) |
| 68 | `tests/test_dynamics.py::test_direction_set_is_von_neumann` | PASSED | 0.0000 | [68_test_dynamics__test_direction_set_is_von_neumann.md](cases/68_test_dynamics__test_direction_set_is_von_neumann.md) |
| 69 | `tests/test_dynamics.py::test_free_move_accepted` | PASSED | 0.0000 | [69_test_dynamics__test_free_move_accepted.md](cases/69_test_dynamics__test_free_move_accepted.md) |
| 70 | `tests/test_dynamics.py::test_immobile_species_never_moves` | PASSED | 0.0010 | [70_test_dynamics__test_immobile_species_never_moves.md](cases/70_test_dynamics__test_immobile_species_never_moves.md) |
| 71 | `tests/test_dynamics.py::test_resolution_is_insertion_order_independent` | PASSED | 0.0000 | [71_test_dynamics__test_resolution_is_insertion_order_independent.md](cases/71_test_dynamics__test_resolution_is_insertion_order_independent.md) |
| 72 | `tests/test_dynamics.py::test_rng_stream_is_two_draws_per_particle_per_step` | PASSED | 0.0010 | [72_test_dynamics__test_rng_stream_is_two_draws_per_particle_per_step.md](cases/72_test_dynamics__test_rng_stream_is_two_draws_per_particle_per_step.md) |
| 73 | `tests/test_dynamics.py::test_single_particle_moves_exactly_one_cell` | PASSED | 0.0010 | [73_test_dynamics__test_single_particle_moves_exactly_one_cell.md](cases/73_test_dynamics__test_single_particle_moves_exactly_one_cell.md) |
| 74 | `tests/test_dynamics.py::test_swap_is_resolved_as_rotation` | PASSED | 0.0000 | [74_test_dynamics__test_swap_is_resolved_as_rotation.md](cases/74_test_dynamics__test_swap_is_resolved_as_rotation.md) |
| 75 | `tests/test_dynamics.py::test_three_particle_cycle` | PASSED | 0.0000 | [75_test_dynamics__test_three_particle_cycle.md](cases/75_test_dynamics__test_three_particle_cycle.md) |
| 76 | `tests/test_invariants.py::test_energy_is_conserved` | PASSED | 0.0120 | [76_test_invariants__test_energy_is_conserved.md](cases/76_test_invariants__test_energy_is_conserved.md) |
| 77 | `tests/test_invariants.py::test_energy_with_bonds_is_conserved` | PASSED | 0.1090 | [77_test_invariants__test_energy_with_bonds_is_conserved.md](cases/77_test_invariants__test_energy_with_bonds_is_conserved.md) |
| 78 | `tests/test_invariants.py::test_no_multiple_occupancy` | PASSED | 0.0120 | [78_test_invariants__test_no_multiple_occupancy.md](cases/78_test_invariants__test_no_multiple_occupancy.md) |
| 79 | `tests/test_invariants.py::test_particle_count_conserved` | PASSED | 0.0080 | [79_test_invariants__test_particle_count_conserved.md](cases/79_test_invariants__test_particle_count_conserved.md) |
| 80 | `tests/test_invariants.py::test_periodic_boundaries` | PASSED | 0.0130 | [80_test_invariants__test_periodic_boundaries.md](cases/80_test_invariants__test_periodic_boundaries.md) |
| 81 | `tests/test_invariants.py::test_species_quantities_conserved` | PASSED | 0.0090 | [81_test_invariants__test_species_quantities_conserved.md](cases/81_test_invariants__test_species_quantities_conserved.md) |
| 82 | `tests/test_invariants.py::test_state_hash_is_stable_and_sensitive` | PASSED | 0.0010 | [82_test_invariants__test_state_hash_is_stable_and_sensitive.md](cases/82_test_invariants__test_state_hash_is_stable_and_sensitive.md) |
| 83 | `tests/test_invariants.py::test_store_rejects_double_placement` | PASSED | 0.0000 | [83_test_invariants__test_store_rejects_double_placement.md](cases/83_test_invariants__test_store_rejects_double_placement.md) |
| 84 | `tests/test_invariants.py::test_store_rejects_duplicate_identifiers` | PASSED | 0.0010 | [84_test_invariants__test_store_rejects_duplicate_identifiers.md](cases/84_test_invariants__test_store_rejects_duplicate_identifiers.md) |
| 85 | `tests/test_invariants.py::test_store_rejects_out_of_grid_particle` | PASSED | 0.0010 | [85_test_invariants__test_store_rejects_out_of_grid_particle.md](cases/85_test_invariants__test_store_rejects_out_of_grid_particle.md) |
| 86 | `tests/test_invariants.py::test_validate_detects_bond_beyond_max_bonds` | PASSED | 0.0020 | [86_test_invariants__test_validate_detects_bond_beyond_max_bonds.md](cases/86_test_invariants__test_validate_detects_bond_beyond_max_bonds.md) |
| 87 | `tests/test_invariants.py::test_validate_detects_bonds_without_chemistry` | PASSED | 0.0010 | [87_test_invariants__test_validate_detects_bonds_without_chemistry.md](cases/87_test_invariants__test_validate_detects_bonds_without_chemistry.md) |
| 88 | `tests/test_invariants.py::test_validate_detects_degree_mismatch` | PASSED | 0.0020 | [88_test_invariants__test_validate_detects_degree_mismatch.md](cases/88_test_invariants__test_validate_detects_degree_mismatch.md) |
| 89 | `tests/test_invariants.py::test_validate_detects_duplicate_cell` | PASSED | 0.0010 | [89_test_invariants__test_validate_detects_duplicate_cell.md](cases/89_test_invariants__test_validate_detects_duplicate_cell.md) |
| 90 | `tests/test_invariants.py::test_validate_detects_grid_desynchronisation` | PASSED | 0.0010 | [90_test_invariants__test_validate_detects_grid_desynchronisation.md](cases/90_test_invariants__test_validate_detects_grid_desynchronisation.md) |
| 91 | `tests/test_invariants.py::test_validate_detects_identity_above_next_id` | PASSED | 0.0020 | [91_test_invariants__test_validate_detects_identity_above_next_id.md](cases/91_test_invariants__test_validate_detects_identity_above_next_id.md) |
| 92 | `tests/test_invariants.py::test_validate_detects_invalid_species_index` | PASSED | 0.0010 | [92_test_invariants__test_validate_detects_invalid_species_index.md](cases/92_test_invariants__test_validate_detects_invalid_species_index.md) |
| 93 | `tests/test_invariants.py::test_validate_detects_missing_particle` | PASSED | 0.0010 | [93_test_invariants__test_validate_detects_missing_particle.md](cases/93_test_invariants__test_validate_detects_missing_particle.md) |
| 94 | `tests/test_invariants.py::test_validate_detects_non_adjacent_bond` | PASSED | 0.0020 | [94_test_invariants__test_validate_detects_non_adjacent_bond.md](cases/94_test_invariants__test_validate_detects_non_adjacent_bond.md) |
| 95 | `tests/test_invariants.py::test_validate_detects_out_of_bounds_particle` | PASSED | 0.0010 | [95_test_invariants__test_validate_detects_out_of_bounds_particle.md](cases/95_test_invariants__test_validate_detects_out_of_bounds_particle.md) |
| 96 | `tests/test_metrics.py::test_peak_memory_is_plausible` | PASSED | 0.0000 | [96_test_metrics__test_peak_memory_is_plausible.md](cases/96_test_metrics__test_peak_memory_is_plausible.md) |
| 97 | `tests/test_metrics.py::test_runtime_versions_are_recorded` | PASSED | 0.0020 | [97_test_metrics__test_runtime_versions_are_recorded.md](cases/97_test_metrics__test_runtime_versions_are_recorded.md) |
| 98 | `tests/test_metrics.py::test_summary_contains_required_fields` | PASSED | 0.0030 | [98_test_metrics__test_summary_contains_required_fields.md](cases/98_test_metrics__test_summary_contains_required_fields.md) |
| 99 | `tests/test_reproducibility.py::test_baseline_config_is_reproducible` | PASSED | 0.2720 | [99_test_reproducibility__test_baseline_config_is_reproducible.md](cases/99_test_reproducibility__test_baseline_config_is_reproducible.md) |
| 100 | `tests/test_reproducibility.py::test_different_seed_different_result` | PASSED | 0.0100 | [100_test_reproducibility__test_different_seed_different_result.md](cases/100_test_reproducibility__test_different_seed_different_result.md) |
| 101 | `tests/test_reproducibility.py::test_initial_placement_is_seed_deterministic` | PASSED | 0.0010 | [101_test_reproducibility__test_initial_placement_is_seed_deterministic.md](cases/101_test_reproducibility__test_initial_placement_is_seed_deterministic.md) |
| 102 | `tests/test_reproducibility.py::test_m1_run_reproduces_the_published_hash` | PASSED | 4.9320 | [102_test_reproducibility__test_m1_run_reproduces_the_published_hash.md](cases/102_test_reproducibility__test_m1_run_reproduces_the_published_hash.md) |
| 103 | `tests/test_reproducibility.py::test_repeated_advance_matches_single_call` | PASSED | 0.0050 | [103_test_reproducibility__test_repeated_advance_matches_single_call.md](cases/103_test_reproducibility__test_repeated_advance_matches_single_call.md) |
| 104 | `tests/test_reproducibility.py::test_same_seed_same_result` | PASSED | 0.0150 | [104_test_reproducibility__test_same_seed_same_result.md](cases/104_test_reproducibility__test_same_seed_same_result.md) |

## File

- `junit.xml` — risultato macchina-leggibile (JUnit XML)
- `pytest.log` — log completo di pytest
- `results.json` — tutti i casi e le evidenze in forma strutturata
- `cases/` — un file per ogni caso di test
- `evidence/` — un file per ogni test obbligatorio, con misure reali
