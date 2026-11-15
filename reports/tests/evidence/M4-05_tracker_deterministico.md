# M4-05 — Tracciamento deterministico e non invasivo

- Requisito: contratto M1 — riproducibilità; M4 — osservatore separato
- Esito: **PASS**
- Eseguito: 2026-11-15T13:21:09+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Due mondi identici, 100 passi, un tracker ciascuno; inoltre lo stato viene confrontato prima e dopo l'osservazione.

## Misure

| Voce | Valore |
|---|---|
| mondi identici | True |
| riepiloghi identici | True |
| stato invariato dopo l'osservazione | True |
| strutture attive | 2 |

## Verifiche

| Verifica | Esito |
|---|---|
| il tracker non altera il mondo | OK |
| due run identici producono lo stesso riepilogo | OK |
| il tracker osserva strutture | OK |

## Test pytest associati

- `tests/test_structures.py::test_tracking_does_not_change_the_world` → **PASSED** (0.0010 s)
- `tests/test_structures.py::test_tracker_is_deterministic` → **PASSED** (0.0010 s)
