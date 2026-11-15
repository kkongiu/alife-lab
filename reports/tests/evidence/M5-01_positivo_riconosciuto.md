# M5-01 — Controllo positivo riconosciuto (sensibilità)

- Requisito: docx S5 — il benchmark positivo è riconosciuto
- Esito: **PASS**
- Eseguito: 2026-11-15T11:11:42+00:00
- Test pytest associati: 1 (1 superati)

## Scenario

Controllo positivo: template A-B-B-A con nove siti di monomeri; a ogni passo il copiatore assembla una catena nel sito a destra di un template.

## Misure

| Voce | Valore |
|---|---|
| versione fixture | m5-fixtures-1 |
| strutture finali | 10 |
| copie assemblate dalla fixture | 9 |
| copie candidate dal rilevatore | 9 |
| copie persistenti | 9 |
| generazione massima | 9 |
| classificazione | replication |

## Verifiche

| Verifica | Esito |
|---|---|
| nove copie assemblate | OK |
| nove copie rilevate | OK |
| tutte persistenti | OK |
| almeno due generazioni | OK |
| classificato come replicazione | OK |

## Test pytest associati

- `tests/test_controls.py::test_positive_control_is_detected` → **PASSED** (0.0360 s)
