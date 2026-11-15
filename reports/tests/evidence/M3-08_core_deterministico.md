# M3-08 — Core senza sorgenti di non determinismo

- Requisito: specifica M3 — regole R1–R10
- Esito: **PASS**
- Eseguito: 2026-11-15T07:04:42+00:00
- Test pytest associati: 1 (1 superati)

## Scenario

Scansione statica dei moduli del core: nessuna sorgente di non determinismo che possa alterare lo stato.

## Misure

| Voce | Valore |
|---|---|
| moduli scansionati | 8 |
| moduli esclusi (solo metadati) | cli.py, events.py, metrics.py, persistence.py |
| occorrenze vietate | nessuna |

## Verifiche

| Verifica | Esito |
|---|---|
| nessun import vietato | OK |
| core coperto dalla scansione | OK |

## Test pytest associati

- `tests/test_energy.py::test_core_modules_do_not_import_nondeterministic_sources` → **PASSED** (0.0010 s)
