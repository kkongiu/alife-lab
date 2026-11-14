# M1-08 — Rilevamento di una violazione intenzionale delle invarianti

- Requisito: alife.md §7, punto 8
- Esito: **PASS**
- Eseguito: 2026-11-14T21:33:04+00:00
- Test pytest associati: 11 (11 superati)

## Scenario

Sei violazioni introdotte deliberatamente su stati validi; ogni caso deve produrre un errore esplicito.

## Misure

| Voce | Valore |
|---|---|
| doppia occupazione | stato non valido: - cella (14, 15) occupata da più particelle - cella (14, 15): la griglia indica 0, la particella 1 la rivendica - griglia con 20 celle occupate ma 19 posizioni valide |
| particella fuori griglia | stato non valido: - particella 0: posizione (-1, 15) fuori griglia - griglia con 20 celle occupate ma 19 posizioni valide |
| griglia desincronizzata | stato non valido: - griglia con 21 celle occupate ma 20 posizioni valide |
| particella mancante | stato non valido: - griglia con 20 celle occupate ma 19 posizioni valide - conteggi per specie {'A': 12, 'B': 7} diversi da {'A': 12, 'B': 8} - energia 71 diversa da 76 |
| specie inesistente | stato non valido: - particella 0: specie 7 inesistente - conteggi per specie {'A': 11, 'B': 8} diversi da {'A': 12, 'B': 8} |
| energia alterata | checkpoint: bilancio energetico non coerente |

## Verifiche

| Verifica | Esito |
|---|---|
| doppia occupazione: rilevata | OK |
| particella fuori griglia: rilevata | OK |
| griglia desincronizzata: rilevata | OK |
| particella mancante: rilevata | OK |
| specie inesistente: rilevata | OK |
| energia alterata: rilevata | OK |

## Test pytest associati

- `tests/test_invariants.py::test_validate_detects_duplicate_cell` → **PASSED** (0.0010 s)
- `tests/test_invariants.py::test_validate_detects_out_of_bounds_particle` → **PASSED** (0.0010 s)
- `tests/test_invariants.py::test_validate_detects_grid_desynchronisation` → **PASSED** (0.0010 s)
- `tests/test_invariants.py::test_validate_detects_missing_particle` → **PASSED** (0.0010 s)
- `tests/test_invariants.py::test_validate_detects_invalid_species_index` → **PASSED** (0.0010 s)
- `tests/test_checkpoint.py::test_detects_tampered_particle` → **PASSED** (0.0020 s)
- `tests/test_checkpoint.py::test_detects_tampered_config_hash` → **PASSED** (0.0020 s)
- `tests/test_checkpoint.py::test_detects_energy_imbalance` → **PASSED** (0.0020 s)
- `tests/test_checkpoint.py::test_detects_invalid_json` → **PASSED** (0.0010 s)
- `tests/test_checkpoint.py::test_detects_wrong_format` → **PASSED** (0.0010 s)
- `tests/test_checkpoint.py::test_detects_missing_rng_state` → **PASSED** (0.0010 s)
