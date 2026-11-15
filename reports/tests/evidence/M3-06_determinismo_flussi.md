# M3-06 — Determinismo con flussi e budget RNG

- Requisito: docx S3 / contratto M1 (riproducibilità)
- Esito: **PASS**
- Eseguito: 2026-11-15T07:04:42+00:00
- Test pytest associati: 3 (3 superati)

## Scenario

Due run indipendenti con sorgenti, dissipazione e costi, stesso seed, 60 passi.

## Misure

| Voce | Valore |
|---|---|
| state_hash_full A | 0069813f8d85667518f8a065ae420993… |
| state_hash_full B | 0069813f8d85667518f8a065ae420993… |
| iniettata A / B | 240 / 240 |
| dissipata A / B | 822 / 822 |
| estrazioni A / B | 14187 / 14187 |

## Verifiche

| Verifica | Esito |
|---|---|
| hash completo identico | OK |
| ledger identico | OK |
| estrazioni identiche | OK |

## Test pytest associati

- `tests/test_energy.py::test_open_run_is_deterministic` → **PASSED** (0.0630 s)
- `tests/test_energy.py::test_rng_budget_with_flows_disabled` → **PASSED** (0.0010 s)
- `tests/test_energy.py::test_priority_uses_identity` → **PASSED** (0.0000 s)
