# M1-03 — Assenza di occupazione multipla

- Requisito: alife.md §7, punto 3
- Esito: **PASS**
- Eseguito: 2026-11-15T13:21:08+00:00
- Test pytest associati: 1 (1 superati)

## Scenario

Configurazione 16×16, 20 particelle, seed 103, 150 passi.

## Misure

| Voce | Valore |
|---|---|
| particelle | 20 |
| celle distinte occupate | 20 |
| celle occupate secondo la griglia | 20 |
| celle con più di un occupante | 0 |

## Verifiche

| Verifica | Esito |
|---|---|
| posizioni tutte distinte | OK |
| griglia coerente con le posizioni | OK |
| celle occupate = particelle | OK |

## Test pytest associati

- `tests/test_invariants.py::test_no_multiple_occupancy` → **PASSED** (0.0080 s)
