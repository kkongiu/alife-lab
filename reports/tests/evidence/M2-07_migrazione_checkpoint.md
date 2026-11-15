# M2-07 — Migrazione dei checkpoint M1

- Requisito: prerequisito M2 — identificativi persistenti
- Esito: **PASS**
- Eseguito: 2026-11-15T11:25:11+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Checkpoint schema 1 (M1) costruito da un mondo M1 e ricaricato con il codice M2.

## Misure

| Voce | Valore |
|---|---|
| identificativi assegnati | 0..19 |
| energia per particella | [3, 5] |
| legami | 0 |
| state_hash M1 preservato | True |
| next_id | 20 |

## Verifiche

| Verifica | Esito |
|---|---|
| identificativi contigui | OK |
| energia iniziale della specie | OK |
| nessun legame importato | OK |
| hash materiale identico | OK |
| stato valido | OK |

## Test pytest associati

- `tests/test_checkpoint.py::test_v1_checkpoint_is_migrated` → **PASSED** (0.0020 s)
- `tests/test_config.py::test_v1_hash_is_unchanged` → **PASSED** (0.0000 s)
