# M3-01 — Identità energetica in sistema aperto

- Requisito: docx S3 — bilanci aggregati
- Esito: **PASS**
- Eseguito: 2026-11-15T11:55:42+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Configurazione M3 quick (32×32) con sorgenti, dissipazione, costi di movimento e di reazione, 100 passi.

## Misure

| Voce | Valore |
|---|---|
| energia interna | 389 |
| energia iniziale | 1160 |
| iniettata | 400 |
| dissipata | 895 |
| non assorbita | 276 |
| identità: E − (E0 + in − out) | 0 |

## Verifiche

| Verifica | Esito |
|---|---|
| identità energetica esatta | OK |
| esiste un flusso entrante | OK |
| esiste dissipazione | OK |
| nessuna energia negativa | OK |
| nessuna violazione di invariante | OK |

## Test pytest associati

- `tests/test_energy.py::test_open_run_keeps_identity` → **PASSED** (0.0410 s)
- `tests/test_energy.py::test_closed_system_keeps_identity` → **PASSED** (0.0070 s)
