# M2-01 — Legami reversibili con costo energetico

- Requisito: docx S2 — legami reversibili, soglie energetiche
- Esito: **PASS**
- Eseguito: 2026-11-15T11:55:42+00:00
- Test pytest associati: 3 (3 superati)

## Scenario

Due particelle S0 adiacenti, formation_probability = 1 e break_probability = 1.

## Misure

| Voce | Valore |
|---|---|
| legami formati | 1 |
| energia delle particelle dopo la formazione | [8, 8] |
| energia immagazzinata nel legame | 4 |
| energia totale dopo la formazione | 20 |
| energia delle particelle dopo la rottura | [10, 10] |
| legami residui dopo la rottura | 0 |

## Verifiche

| Verifica | Esito |
|---|---|
| il legame si forma fra vicini ammessi | OK |
| il costo è pagato da entrambe le particelle | OK |
| l'energia non si perde | OK |
| la rottura restituisce l'energia | OK |
| dopo la rottura non restano legami | OK |

## Test pytest associati

- `tests/test_chemistry.py::test_bond_forms_between_adjacent_allowed_particles` → **PASSED** (0.0010 s)
- `tests/test_chemistry.py::test_breaking_returns_energy` → **PASSED** (0.0010 s)
- `tests/test_chemistry.py::test_no_bond_without_enough_energy` → **PASSED** (0.0010 s)
