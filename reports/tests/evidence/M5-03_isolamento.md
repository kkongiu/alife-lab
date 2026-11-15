# M5-03 — Isolamento dei controlli dal mondo di scoperta

- Requisito: alife.md §2 — controlli completamente isolati
- Esito: **PASS**
- Eseguito: 2026-11-15T11:25:17+00:00
- Test pytest associati: 1 (1 superati)

## Scenario

Isolamento: i moduli del motore non devono importare né citare il pacchetto dei controlli.

## Misure

| Voce | Valore |
|---|---|
| moduli del motore | __main__.py, chemistry.py, cli.py, config.py, dynamics.py, events.py, metrics.py, particles.py, persistence.py, replication.py, rng.py, structures.py, world.py |
| moduli con riferimenti ai controlli | nessuno |
| fixture | m5-fixtures-1 |

## Verifiche

| Verifica | Esito |
|---|---|
| nessun riferimento ai controlli | OK |
| il motore è coperto dalla scansione | OK |

## Test pytest associati

- `tests/test_controls.py::test_engine_does_not_import_controls` → **PASSED** (0.0010 s)
