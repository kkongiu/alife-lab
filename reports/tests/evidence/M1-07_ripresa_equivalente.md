# M1-07 — Equivalenza tra esecuzione continua e interrotta/ripresa

- Requisito: alife.md §7, punto 7
- Esito: **PASS**
- Eseguito: 2026-11-15T11:55:42+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Seed 107: run continuo di 60 passi contro run interrotto a 20 e ripreso per 40.

## Misure

| Voce | Valore |
|---|---|
| hash continuo | 2515213dac46178bfdfaf37092bd3c84… |
| hash ripreso | 2515213dac46178bfdfaf37092bd3c84… |
| mosse continue / riprese | 662 / 662 |
| fingerprint RNG uguale | True |
| passo finale | 60 |

## Verifiche

| Verifica | Esito |
|---|---|
| hash di stato identico | OK |
| numero di mosse identico | OK |
| stato RNG identico | OK |

## Test pytest associati

- `tests/test_checkpoint.py::test_resume_is_equivalent_to_continuous_run` → **PASSED** (0.0100 s)
- `tests/test_cli.py::test_resume_matches_continuous_run` → **PASSED** (0.5700 s)
