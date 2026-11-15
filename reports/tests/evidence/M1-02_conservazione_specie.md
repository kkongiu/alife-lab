# M1-02 — Conservazione della quantità per specie

- Requisito: alife.md §7, punto 2
- Esito: **PASS**
- Eseguito: 2026-11-15T11:11:41+00:00
- Test pytest associati: 1 (1 superati)

## Scenario

Configurazione 16×16, specie A=12 B=8, seed 102, 150 passi.

## Misure

| Voce | Valore |
|---|---|
| specie A: iniziale → finale | 12 → 12 |
| specie B: iniziale → finale | 8 → 8 |
| conteggi finali | {"A": 12, "B": 8} |

## Verifiche

| Verifica | Esito |
|---|---|
| specie A conservata | OK |
| specie B conservata | OK |
| conteggi finali = configurazione | OK |

## Test pytest associati

- `tests/test_invariants.py::test_species_quantities_conserved` → **PASSED** (0.0080 s)
