# M4-06 — Tracciamento end-to-end e file di eventi

- Requisito: docx S4 — log eventi accessibile
- Esito: **PASS**
- Eseguito: 2026-11-15T11:55:43+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Configurazione M3 quick tracciata per 300 passi: strutture, eventi, persistenza e ambiguità.

## Misure

| Voce | Valore |
|---|---|
| strutture attive | 5 |
| componenti nel mondo | 5 |
| nascite / morti | 23 / 20 |
| fusioni / scissioni | 2 / 8 |
| firme distinte | 14 |
| osservazioni esatte / impronte | 3832 / 47 |
| vita media | 117.545 |

## Verifiche

| Verifica | Esito |
|---|---|
| il conteggio coincide con le componenti | OK |
| sono stati osservati eventi | OK |
| la vita media è positiva | OK |

## Test pytest associati

- `tests/test_structures.py::test_tracker_writes_jsonl_files` → **PASSED** (0.0020 s)
- `tests/test_cli.py::test_run_with_tracking` → **PASSED** (0.3030 s)
