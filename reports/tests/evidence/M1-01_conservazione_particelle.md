# M1-01 — Conservazione del numero di particelle

- Requisito: alife.md §7, punto 1
- Esito: **PASS**
- Eseguito: 2026-11-15T11:55:42+00:00
- Test pytest associati: 1 (1 superati)

## Scenario

Configurazione 16×16, specie A=12 B=8, seed 101, 150 passi.

## Misure

| Voce | Valore |
|---|---|
| particelle iniziali | 20 |
| particelle finali | 20 |
| delta | 0 |
| hash iniziale | a57513f60b96804fcab84c68dc4f2e47… |
| hash finale | 3ad08713b25a3f2e30b2d780a97af531… |
| violazioni rilevate | 0 |

## Verifiche

| Verifica | Esito |
|---|---|
| numero di particelle invariato | OK |
| nessuna violazione di invariante | OK |
| lo stato è cambiato (la simulazione ha evoluto) | OK |

## Test pytest associati

- `tests/test_invariants.py::test_particle_count_conserved` → **PASSED** (0.0090 s)
