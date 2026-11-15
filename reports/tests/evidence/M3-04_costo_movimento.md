# M3-04 — Costo di movimento pagato solo se accettato

- Requisito: docx S3 — ogni trasformazione ha un costo
- Esito: **PASS**
- Eseguito: 2026-11-15T11:11:42+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Costo 1 con energia 10 per 10 passi; costo 2 con energia 1 per 10 passi.

## Misure

| Voce | Valore |
|---|---|
| mosse pagate | 10 |
| energia residua | 0 |
| dissipato per movimento | 10 |
| mosse con energia insufficiente | 0 |
| energia del mondo bloccato | 1 |

## Verifiche

| Verifica | Esito |
|---|---|
| una mossa = un quanto | OK |
| energia esaurita esattamente | OK |
| nessuna mossa senza energia | OK |
| energia intatta nel mondo bloccato | OK |

## Test pytest associati

- `tests/test_energy.py::test_movement_cost_charged_per_move` → **PASSED** (0.0010 s)
- `tests/test_energy.py::test_movement_cost_blocks_when_insufficient` → **PASSED** (0.0000 s)
