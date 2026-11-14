# Risultati dei test

Generato: 2026-11-14T21:33:04+00:00 · Comando: `.venv/bin/python -m pytest -v`

**64 superati, 0 falliti, 64 casi in 3.49 s** (exit code 0).

## Test obbligatori del contratto

| ID | Requisito | Esito | File | Test pytest |
|---|---|---|---|---|
| M1-01 | Conservazione del numero di particelle | **PASS** | [M1-01_conservazione_particelle.md](evidence/M1-01_conservazione_particelle.md) | 1/1 superati |
| M1-02 | Conservazione della quantità per specie | **PASS** | [M1-02_conservazione_specie.md](evidence/M1-02_conservazione_specie.md) | 1/1 superati |
| M1-03 | Assenza di occupazione multipla | **PASS** | [M1-03_occupazione_unica.md](evidence/M1-03_occupazione_unica.md) | 1/1 superati |
| M1-04 | Rispetto dei confini configurati | **PASS** | [M1-04_confini.md](evidence/M1-04_confini.md) | 2/2 superati |
| M1-05 | Riproducibilità con identico seed | **PASS** | [M1-05_riproducibilita.md](evidence/M1-05_riproducibilita.md) | 5/5 superati |
| M1-06 | Integrità del salvataggio e caricamento | **PASS** | [M1-06_checkpoint.md](evidence/M1-06_checkpoint.md) | 4/4 superati |
| M1-07 | Equivalenza tra esecuzione continua e interrotta/ripresa | **PASS** | [M1-07_ripresa_equivalente.md](evidence/M1-07_ripresa_equivalente.md) | 2/2 superati |
| M1-08 | Rilevamento di una violazione intenzionale delle invarianti | **PASS** | [M1-08_violazioni_intenzionali.md](evidence/M1-08_violazioni_intenzionali.md) | 11/11 superati |

## Tutti i casi

| # | Caso | Stato | Durata (s) | File |
|---|---|---|---|---|
| 1 | `tests/test_checkpoint.py::test_checkpoint_does_not_mutate_world` | PASSED | 0.0020 | [01_test_checkpoint__test_checkpoint_does_not_mutate_world.md](cases/01_test_checkpoint__test_checkpoint_does_not_mutate_world.md) |
| 2 | `tests/test_checkpoint.py::test_detects_energy_imbalance` | PASSED | 0.0020 | [02_test_checkpoint__test_detects_energy_imbalance.md](cases/02_test_checkpoint__test_detects_energy_imbalance.md) |
| 3 | `tests/test_checkpoint.py::test_detects_invalid_json` | PASSED | 0.0010 | [03_test_checkpoint__test_detects_invalid_json.md](cases/03_test_checkpoint__test_detects_invalid_json.md) |
| 4 | `tests/test_checkpoint.py::test_detects_missing_rng_state` | PASSED | 0.0010 | [04_test_checkpoint__test_detects_missing_rng_state.md](cases/04_test_checkpoint__test_detects_missing_rng_state.md) |
| 5 | `tests/test_checkpoint.py::test_detects_tampered_config_hash` | PASSED | 0.0020 | [05_test_checkpoint__test_detects_tampered_config_hash.md](cases/05_test_checkpoint__test_detects_tampered_config_hash.md) |
| 6 | `tests/test_checkpoint.py::test_detects_tampered_particle` | PASSED | 0.0020 | [06_test_checkpoint__test_detects_tampered_particle.md](cases/06_test_checkpoint__test_detects_tampered_particle.md) |
| 7 | `tests/test_checkpoint.py::test_detects_wrong_format` | PASSED | 0.0010 | [07_test_checkpoint__test_detects_wrong_format.md](cases/07_test_checkpoint__test_detects_wrong_format.md) |
| 8 | `tests/test_checkpoint.py::test_missing_file` | PASSED | 0.0010 | [08_test_checkpoint__test_missing_file.md](cases/08_test_checkpoint__test_missing_file.md) |
| 9 | `tests/test_checkpoint.py::test_no_temporary_file_left_behind` | PASSED | 0.0010 | [09_test_checkpoint__test_no_temporary_file_left_behind.md](cases/09_test_checkpoint__test_no_temporary_file_left_behind.md) |
| 10 | `tests/test_checkpoint.py::test_repeated_save_load_cycles_are_stable` | PASSED | 0.0050 | [10_test_checkpoint__test_repeated_save_load_cycles_are_stable.md](cases/10_test_checkpoint__test_repeated_save_load_cycles_are_stable.md) |
| 11 | `tests/test_checkpoint.py::test_resume_is_equivalent_to_continuous_run` | PASSED | 0.0090 | [11_test_checkpoint__test_resume_is_equivalent_to_continuous_run.md](cases/11_test_checkpoint__test_resume_is_equivalent_to_continuous_run.md) |
| 12 | `tests/test_checkpoint.py::test_roundtrip_preserves_state` | PASSED | 0.0260 | [12_test_checkpoint__test_roundtrip_preserves_state.md](cases/12_test_checkpoint__test_roundtrip_preserves_state.md) |
| 13 | `tests/test_cli.py::test_inspect_reads_checkpoint` | PASSED | 0.5520 | [13_test_cli__test_inspect_reads_checkpoint.md](cases/13_test_cli__test_inspect_reads_checkpoint.md) |
| 14 | `tests/test_cli.py::test_invalid_config_reports_error` | PASSED | 0.2740 | [14_test_cli__test_invalid_config_reports_error.md](cases/14_test_cli__test_invalid_config_reports_error.md) |
| 15 | `tests/test_cli.py::test_negative_steps_rejected` | PASSED | 0.2410 | [15_test_cli__test_negative_steps_rejected.md](cases/15_test_cli__test_negative_steps_rejected.md) |
| 16 | `tests/test_cli.py::test_resume_matches_continuous_run` | PASSED | 0.5970 | [16_test_cli__test_resume_matches_continuous_run.md](cases/16_test_cli__test_resume_matches_continuous_run.md) |
| 17 | `tests/test_cli.py::test_run_produces_artifacts` | PASSED | 0.2840 | [17_test_cli__test_run_produces_artifacts.md](cases/17_test_cli__test_run_produces_artifacts.md) |
| 18 | `tests/test_cli.py::test_seed_override` | PASSED | 0.2760 | [18_test_cli__test_seed_override.md](cases/18_test_cli__test_seed_override.md) |
| 19 | `tests/test_cli.py::test_version[command0]` | PASSED | 0.2450 | [19_test_cli__test_version[command0].md](cases/19_test_cli__test_version[command0].md) |
| 20 | `tests/test_config.py::test_baseline_config_is_valid` | PASSED | 0.0010 | [20_test_config__test_baseline_config_is_valid.md](cases/20_test_config__test_baseline_config_is_valid.md) |
| 21 | `tests/test_config.py::test_boolean_is_not_an_integer` | PASSED | 0.0010 | [21_test_config__test_boolean_is_not_an_integer.md](cases/21_test_config__test_boolean_is_not_an_integer.md) |
| 22 | `tests/test_config.py::test_duplicate_species_names_rejected` | PASSED | 0.0010 | [22_test_config__test_duplicate_species_names_rejected.md](cases/22_test_config__test_duplicate_species_names_rejected.md) |
| 23 | `tests/test_config.py::test_hash_changes_with_seed` | PASSED | 0.0010 | [23_test_config__test_hash_changes_with_seed.md](cases/23_test_config__test_hash_changes_with_seed.md) |
| 24 | `tests/test_config.py::test_hash_is_independent_of_key_order` | PASSED | 0.0010 | [24_test_config__test_hash_is_independent_of_key_order.md](cases/24_test_config__test_hash_is_independent_of_key_order.md) |
| 25 | `tests/test_config.py::test_invalid_json` | PASSED | 0.0010 | [25_test_config__test_invalid_json.md](cases/25_test_config__test_invalid_json.md) |
| 26 | `tests/test_config.py::test_missing_file` | PASSED | 0.0010 | [26_test_config__test_missing_file.md](cases/26_test_config__test_missing_file.md) |
| 27 | `tests/test_config.py::test_move_probability_range_enforced` | PASSED | 0.0010 | [27_test_config__test_move_probability_range_enforced.md](cases/27_test_config__test_move_probability_range_enforced.md) |
| 28 | `tests/test_config.py::test_negative_seed_rejected` | PASSED | 0.0010 | [28_test_config__test_negative_seed_rejected.md](cases/28_test_config__test_negative_seed_rejected.md) |
| 29 | `tests/test_config.py::test_roundtrip_preserves_hash` | PASSED | 0.0010 | [29_test_config__test_roundtrip_preserves_hash.md](cases/29_test_config__test_roundtrip_preserves_hash.md) |
| 30 | `tests/test_config.py::test_too_many_particles_rejected` | PASSED | 0.0010 | [30_test_config__test_too_many_particles_rejected.md](cases/30_test_config__test_too_many_particles_rejected.md) |
| 31 | `tests/test_config.py::test_unknown_key_rejected` | PASSED | 0.0010 | [31_test_config__test_unknown_key_rejected.md](cases/31_test_config__test_unknown_key_rejected.md) |
| 32 | `tests/test_dynamics.py::test_blocked_chain_leaves_head_stuck` | PASSED | 0.0000 | [32_test_dynamics__test_blocked_chain_leaves_head_stuck.md](cases/32_test_dynamics__test_blocked_chain_leaves_head_stuck.md) |
| 33 | `tests/test_dynamics.py::test_chain_towards_empty_cell_moves_entirely` | PASSED | 0.0000 | [33_test_dynamics__test_chain_towards_empty_cell_moves_entirely.md](cases/33_test_dynamics__test_chain_towards_empty_cell_moves_entirely.md) |
| 34 | `tests/test_dynamics.py::test_closed_boundary_keeps_particles_inside` | PASSED | 0.0050 | [34_test_dynamics__test_closed_boundary_keeps_particles_inside.md](cases/34_test_dynamics__test_closed_boundary_keeps_particles_inside.md) |
| 35 | `tests/test_dynamics.py::test_contention_produces_single_winner` | PASSED | 0.0000 | [35_test_dynamics__test_contention_produces_single_winner.md](cases/35_test_dynamics__test_contention_produces_single_winner.md) |
| 36 | `tests/test_dynamics.py::test_direction_set_is_von_neumann` | PASSED | 0.0000 | [36_test_dynamics__test_direction_set_is_von_neumann.md](cases/36_test_dynamics__test_direction_set_is_von_neumann.md) |
| 37 | `tests/test_dynamics.py::test_free_move_accepted` | PASSED | 0.0000 | [37_test_dynamics__test_free_move_accepted.md](cases/37_test_dynamics__test_free_move_accepted.md) |
| 38 | `tests/test_dynamics.py::test_immobile_species_never_moves` | PASSED | 0.0010 | [38_test_dynamics__test_immobile_species_never_moves.md](cases/38_test_dynamics__test_immobile_species_never_moves.md) |
| 39 | `tests/test_dynamics.py::test_resolution_is_insertion_order_independent` | PASSED | 0.0000 | [39_test_dynamics__test_resolution_is_insertion_order_independent.md](cases/39_test_dynamics__test_resolution_is_insertion_order_independent.md) |
| 40 | `tests/test_dynamics.py::test_rng_stream_is_two_draws_per_particle_per_step` | PASSED | 0.0010 | [40_test_dynamics__test_rng_stream_is_two_draws_per_particle_per_step.md](cases/40_test_dynamics__test_rng_stream_is_two_draws_per_particle_per_step.md) |
| 41 | `tests/test_dynamics.py::test_single_particle_moves_exactly_one_cell` | PASSED | 0.0010 | [41_test_dynamics__test_single_particle_moves_exactly_one_cell.md](cases/41_test_dynamics__test_single_particle_moves_exactly_one_cell.md) |
| 42 | `tests/test_dynamics.py::test_swap_is_resolved_as_rotation` | PASSED | 0.0000 | [42_test_dynamics__test_swap_is_resolved_as_rotation.md](cases/42_test_dynamics__test_swap_is_resolved_as_rotation.md) |
| 43 | `tests/test_dynamics.py::test_three_particle_cycle` | PASSED | 0.0000 | [43_test_dynamics__test_three_particle_cycle.md](cases/43_test_dynamics__test_three_particle_cycle.md) |
| 44 | `tests/test_invariants.py::test_energy_is_conserved` | PASSED | 0.0130 | [44_test_invariants__test_energy_is_conserved.md](cases/44_test_invariants__test_energy_is_conserved.md) |
| 45 | `tests/test_invariants.py::test_no_multiple_occupancy` | PASSED | 0.0100 | [45_test_invariants__test_no_multiple_occupancy.md](cases/45_test_invariants__test_no_multiple_occupancy.md) |
| 46 | `tests/test_invariants.py::test_particle_count_conserved` | PASSED | 0.0100 | [46_test_invariants__test_particle_count_conserved.md](cases/46_test_invariants__test_particle_count_conserved.md) |
| 47 | `tests/test_invariants.py::test_periodic_boundaries` | PASSED | 0.0140 | [47_test_invariants__test_periodic_boundaries.md](cases/47_test_invariants__test_periodic_boundaries.md) |
| 48 | `tests/test_invariants.py::test_species_quantities_conserved` | PASSED | 0.0100 | [48_test_invariants__test_species_quantities_conserved.md](cases/48_test_invariants__test_species_quantities_conserved.md) |
| 49 | `tests/test_invariants.py::test_state_hash_is_stable_and_sensitive` | PASSED | 0.0010 | [49_test_invariants__test_state_hash_is_stable_and_sensitive.md](cases/49_test_invariants__test_state_hash_is_stable_and_sensitive.md) |
| 50 | `tests/test_invariants.py::test_store_rejects_double_placement` | PASSED | 0.0010 | [50_test_invariants__test_store_rejects_double_placement.md](cases/50_test_invariants__test_store_rejects_double_placement.md) |
| 51 | `tests/test_invariants.py::test_store_rejects_out_of_grid_particle` | PASSED | 0.0000 | [51_test_invariants__test_store_rejects_out_of_grid_particle.md](cases/51_test_invariants__test_store_rejects_out_of_grid_particle.md) |
| 52 | `tests/test_invariants.py::test_validate_detects_duplicate_cell` | PASSED | 0.0010 | [52_test_invariants__test_validate_detects_duplicate_cell.md](cases/52_test_invariants__test_validate_detects_duplicate_cell.md) |
| 53 | `tests/test_invariants.py::test_validate_detects_grid_desynchronisation` | PASSED | 0.0010 | [53_test_invariants__test_validate_detects_grid_desynchronisation.md](cases/53_test_invariants__test_validate_detects_grid_desynchronisation.md) |
| 54 | `tests/test_invariants.py::test_validate_detects_invalid_species_index` | PASSED | 0.0010 | [54_test_invariants__test_validate_detects_invalid_species_index.md](cases/54_test_invariants__test_validate_detects_invalid_species_index.md) |
| 55 | `tests/test_invariants.py::test_validate_detects_missing_particle` | PASSED | 0.0010 | [55_test_invariants__test_validate_detects_missing_particle.md](cases/55_test_invariants__test_validate_detects_missing_particle.md) |
| 56 | `tests/test_invariants.py::test_validate_detects_out_of_bounds_particle` | PASSED | 0.0010 | [56_test_invariants__test_validate_detects_out_of_bounds_particle.md](cases/56_test_invariants__test_validate_detects_out_of_bounds_particle.md) |
| 57 | `tests/test_metrics.py::test_peak_memory_is_plausible` | PASSED | 0.0000 | [57_test_metrics__test_peak_memory_is_plausible.md](cases/57_test_metrics__test_peak_memory_is_plausible.md) |
| 58 | `tests/test_metrics.py::test_runtime_versions_are_recorded` | PASSED | 0.0020 | [58_test_metrics__test_runtime_versions_are_recorded.md](cases/58_test_metrics__test_runtime_versions_are_recorded.md) |
| 59 | `tests/test_metrics.py::test_summary_contains_required_fields` | PASSED | 0.0030 | [59_test_metrics__test_summary_contains_required_fields.md](cases/59_test_metrics__test_summary_contains_required_fields.md) |
| 60 | `tests/test_reproducibility.py::test_baseline_config_is_reproducible` | PASSED | 0.2800 | [60_test_reproducibility__test_baseline_config_is_reproducible.md](cases/60_test_reproducibility__test_baseline_config_is_reproducible.md) |
| 61 | `tests/test_reproducibility.py::test_different_seed_different_result` | PASSED | 0.0050 | [61_test_reproducibility__test_different_seed_different_result.md](cases/61_test_reproducibility__test_different_seed_different_result.md) |
| 62 | `tests/test_reproducibility.py::test_initial_placement_is_seed_deterministic` | PASSED | 0.0010 | [62_test_reproducibility__test_initial_placement_is_seed_deterministic.md](cases/62_test_reproducibility__test_initial_placement_is_seed_deterministic.md) |
| 63 | `tests/test_reproducibility.py::test_repeated_advance_matches_single_call` | PASSED | 0.0040 | [63_test_reproducibility__test_repeated_advance_matches_single_call.md](cases/63_test_reproducibility__test_repeated_advance_matches_single_call.md) |
| 64 | `tests/test_reproducibility.py::test_same_seed_same_result` | PASSED | 0.0150 | [64_test_reproducibility__test_same_seed_same_result.md](cases/64_test_reproducibility__test_same_seed_same_result.md) |

## File

- `junit.xml` — risultato macchina-leggibile (JUnit XML)
- `pytest.log` — log completo di pytest
- `results.json` — tutti i casi e le evidenze in forma strutturata
- `cases/` — un file per ogni caso di test
- `evidence/` — un file per ogni test obbligatorio, con misure reali
