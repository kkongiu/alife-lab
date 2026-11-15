# M6-01 — Preregistrazione integra: seed, config, hash

- Requisito: docx S6 — seed e griglie fissati prima dei run
- Esito: **PASS**
- Eseguito: 2026-11-15T13:21:15+00:00
- Test pytest associati: 3 (3 superati)

## Scenario

Manifest preregistrato: condizioni, seed, passi, configurazioni e hash fissati prima dei run.

## Misure

| Voce | Valore |
|---|---|
| versionato il | 2026-11-15T11:38:33+00:00 |
| condizioni | closed, unfed, fed-low, fed-mid, fed-high |
| seed | 6101, 6102, 6103, 6104, 6105 |
| passi per run | 3000 |
| run dichiarati | 25 |
| hash di configurazione distinti | 25 |
| criterio | almeno 3 seed su 5 classificati 'replication' e mediana delle copie persistenti >= 5 |

## Verifiche

| Verifica | Esito |
|---|---|
| 25 run dichiarati | OK |
| 5 condizioni × 5 seed | OK |
| ogni configurazione corrisponde al suo hash | OK |
| gli hash sono distinti | OK |
| la regola di decisione è registrata | OK |

## Test pytest associati

- `tests/test_campaign.py::test_manifest_is_preregistered` → **PASSED** (0.0000 s)
- `tests/test_campaign.py::test_manifest_configs_match_their_hashes` → **PASSED** (0.0080 s)
- `tests/test_campaign.py::test_manifest_records_the_decision_rule` → **PASSED** (0.0000 s)
