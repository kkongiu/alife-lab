# M6-03 — Campagna completa, run nulli inclusi

- Requisito: docx S6 — registrare anche i risultati nulli
- Esito: **PASS**
- Eseguito: 2026-11-15T13:21:15+00:00
- Test pytest associati: 1 (1 superati)

## Scenario

Risultati della campagna: tutti i run registrati, compresi quelli in cui non è stata osservata alcuna copia.

## Misure

| Voce | Valore |
|---|---|
| run registrati | 25 |
| run con zero copie persistenti | 25 |
| run classificati replication | 0 |
| condizioni | closed: 0/5 replication, 0 copie mediane; fed-high: 0/5 replication, 0 copie mediane; fed-low: 0/5 replication, 0 copie mediane; fed-mid: 0/5 replication, 0 copie mediane; unfed: 0/5 replication, 0 copie mediane |
| motore invariato dalla preregistrazione | True |
| verdetto | no_evidence |

## Verifiche

| Verifica | Esito |
|---|---|
| 25 run registrati | OK |
| tutte le cinque condizioni presenti | OK |
| i run nulli sono inclusi | OK |
| nessun run mancante | OK |
| verdetto definito | OK |

## Test pytest associati

- `tests/test_campaign.py::test_campaign_results_are_complete` → **PASSED** (0.0010 s)
