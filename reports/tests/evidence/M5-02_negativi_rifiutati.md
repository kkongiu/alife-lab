# M5-02 — Controlli negativi non classificati (falsi positivi)

- Requisito: docx S5 — i negativi non sono replicazione
- Esito: **PASS**
- Eseguito: 2026-11-15T11:11:49+00:00
- Test pytest associati: 4 (4 superati)

## Scenario

Cinque condizioni senza copiatura: immobilità, aggregazione casuale, reazioni reversibili e due casi di stress con firme molto ripetute.

## Misure

| Voce | Valore |
|---|---|
| N1 immobile | 0 strutture, 0 candidate, not_replication |
| N2 aggregazione casuale | 116 strutture, 0 candidate, not_replication |
| N3 reazioni reversibili | 84 strutture, 0 candidate, not_replication |
| stress specie unica | 64 strutture, 0 candidate, not_replication |
| stress formazione massima | 67 strutture, 0 candidate, not_replication |

## Verifiche

| Verifica | Esito |
|---|---|
| N1 immobile: non replicazione e nessuna candidata | OK |
| N2 aggregazione casuale: non replicazione e nessuna candidata | OK |
| N3 reazioni reversibili: non replicazione e nessuna candidata | OK |
| stress specie unica: non replicazione e nessuna candidata | OK |
| stress formazione massima: non replicazione e nessuna candidata | OK |

## Test pytest associati

- `tests/test_controls.py::test_negative_immobile_is_not_replication` → **PASSED** (0.0300 s)
- `tests/test_controls.py::test_negative_random_aggregation_is_not_replication` → **PASSED** (2.9880 s)
- `tests/test_controls.py::test_negative_reversible_is_not_replication` → **PASSED** (1.8210 s)
- `tests/test_controls.py::test_negative_stress_cases_are_not_replication` → **PASSED** (1.7590 s)
