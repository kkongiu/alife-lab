# M5-04 — Controllo positivo riproducibile e versionato

- Requisito: docx S5 — fixture versionate
- Esito: **PASS**
- Eseguito: 2026-11-15T13:21:15+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Due esecuzioni indipendenti del controllo positivo con le stesse posizioni e lo stesso seed.

## Misure

| Voce | Valore |
|---|---|
| hash completo A | 7911dd2099ba92e7de87ef3246186959… |
| hash completo B | 7911dd2099ba92e7de87ef3246186959… |
| riepiloghi identici | True |
| copie A / B | 9 / 9 |

## Verifiche

| Verifica | Esito |
|---|---|
| hash completo identico | OK |
| stesso esito del rilevatore | OK |

## Test pytest associati

- `tests/test_controls.py::test_positive_control_is_reproducible` → **PASSED** (0.0650 s)
- `tests/test_controls.py::test_fixture_version_is_declared` → **PASSED** (0.0000 s)
