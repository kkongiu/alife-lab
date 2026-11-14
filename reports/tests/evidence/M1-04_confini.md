# M1-04 — Rispetto dei confini configurati

- Requisito: alife.md §7, punto 4
- Esito: **PASS**
- Eseguito: 2026-11-14T21:33:04+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Periodico: 20×20, seed 104, 200 passi. Chiuso: 10×10, seed 104, 50 passi.

## Misure

| Voce | Valore |
|---|---|
| periodico: intervallo x / y | 0..19 / 0..18 |
| periodico: particelle fuori griglia | 0 |
| chiuso: intervallo x / y | 0..9 / 1..8 |
| chiuso: particelle fuori griglia | 0 |

## Verifiche

| Verifica | Esito |
|---|---|
| confini periodici rispettati | OK |
| confini chiusi rispettati | OK |
| nessuna violazione (periodico) | OK |
| nessuna violazione (chiuso) | OK |

## Test pytest associati

- `tests/test_invariants.py::test_periodic_boundaries` → **PASSED** (0.0140 s)
- `tests/test_dynamics.py::test_closed_boundary_keeps_particles_inside` → **PASSED** (0.0050 s)
