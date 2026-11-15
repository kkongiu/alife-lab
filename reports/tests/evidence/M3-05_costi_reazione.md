# M3-05 — Costi di formazione e rottura

- Requisito: docx S3 — costi delle reazioni
- Esito: **PASS**
- Eseguito: 2026-11-15T11:55:42+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Formazione con costo 2 e attrito 1; rottura con attrito 1 su un legame da 4.

## Misure

| Voce | Valore |
|---|---|
| energia delle particelle dopo la formazione | [7, 7] |
| energia nel legame | 4 |
| dissipato dalla formazione | 2 |
| energia restituita alla rottura | [10, 9] |
| dissipato dalla rottura | 1 |

## Verifiche

| Verifica | Esito |
|---|---|
| attrito di formazione = 2 | OK |
| energia immagazzinata = 2×bond_cost | OK |
| attrito di rottura = 1 | OK |
| restituito 3 su 4 | OK |

## Test pytest associati

- `tests/test_energy.py::test_formation_dissipation` → **PASSED** (0.0010 s)
- `tests/test_energy.py::test_breaking_dissipation` → **PASSED** (0.0010 s)
