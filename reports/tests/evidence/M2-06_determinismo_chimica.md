# M2-06 — Determinismo e ripresa con la chimica

- Requisito: docx S2 / contratto M1 (riproducibilità)
- Esito: **PASS**
- Eseguito: 2026-11-14T21:52:16+00:00
- Test pytest associati: 3 (3 superati)

## Scenario

Due run indipendenti con lo stesso seed e 100 passi di chimica.

## Misure

| Voce | Valore |
|---|---|
| state_hash_full run A | 332cc543ebc16d53eb8ae7c601295ed0… |
| state_hash_full run B | 332cc543ebc16d53eb8ae7c601295ed0… |
| legami A / B | 47 / 47 |
| formazioni A / B | 74 / 74 |
| rotture A / B | 27 / 27 |

## Verifiche

| Verifica | Esito |
|---|---|
| hash completo identico | OK |
| legami identici | OK |
| stato RNG identico | OK |

## Test pytest associati

- `tests/test_chemistry.py::test_m2_quick_is_deterministic` → **PASSED** (0.1160 s)
- `tests/test_checkpoint.py::test_v2_resume_is_equivalent_to_continuous_run` → **PASSED** (0.0650 s)
- `tests/test_checkpoint.py::test_v2_roundtrip_preserves_bonds_and_energy` → **PASSED** (0.0260 s)
