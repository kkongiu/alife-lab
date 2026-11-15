# M1-05 — Riproducibilità con identico seed

- Requisito: alife.md §7, punto 5
- Esito: **PASS**
- Eseguito: 2026-11-15T11:25:10+00:00
- Test pytest associati: 6 (6 superati)

## Scenario

Due universi con seed 1234 e uno con seed 1235, 120 passi ciascuno.

## Misure

| Voce | Valore |
|---|---|
| hash seed 1234 (run A) | cd9827e4acb14329f33f6a4c82512b66… |
| hash seed 1234 (run B) | cd9827e4acb14329f33f6a4c82512b66… |
| hash seed 1235 | b383b55a4bd0c00aebd9a8adeec1f6ad… |
| spostamenti run A / run B | 1380 / 1380 |
| fingerprint RNG uguale | True |

## Verifiche

| Verifica | Esito |
|---|---|
| stesso seed ⇒ stesso stato completo | OK |
| stesso seed ⇒ stesso hash | OK |
| stesso seed ⇒ stesso numero di mosse | OK |
| seed diverso ⇒ stato diverso | OK |

## Test pytest associati

- `tests/test_reproducibility.py::test_same_seed_same_result` → **PASSED** (0.0150 s)
- `tests/test_reproducibility.py::test_different_seed_different_result` → **PASSED** (0.0070 s)
- `tests/test_reproducibility.py::test_initial_placement_is_seed_deterministic` → **PASSED** (0.0010 s)
- `tests/test_reproducibility.py::test_repeated_advance_matches_single_call` → **PASSED** (0.0050 s)
- `tests/test_reproducibility.py::test_baseline_config_is_reproducible` → **PASSED** (0.2500 s)
- `tests/test_reproducibility.py::test_m1_run_reproduces_the_published_hash` → **PASSED** (4.5960 s)
