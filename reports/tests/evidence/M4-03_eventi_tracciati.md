# M4-03 — Eventi: nascita, crescita, scissione, fusione, morte

- Requisito: docx S4 — registrare nascita, trasformazione, scissione, scomparsa
- Esito: **PASS**
- Eseguito: 2026-11-15T13:21:09+00:00
- Test pytest associati: 5 (5 superati)

## Scenario

Sei particelle in linea: due dimeri, fusione, crescita, scissione, riduzione, due morti.

## Misure

| Voce | Valore |
|---|---|
| nascite | 2 |
| fusioni | 1 |
| crescite | 1 |
| scissioni | 2 |
| riduzioni | 1 |
| morti | 2 |
| persistenze | 2 |

## Verifiche

| Verifica | Esito |
|---|---|
| due nascite iniziali | OK |
| una fusione | OK |
| una crescita | OK |
| due scissioni | OK |
| una riduzione | OK |
| due morti | OK |

## Test pytest associati

- `tests/test_structures.py::test_birth_and_death` → **PASSED** (0.0010 s)
- `tests/test_structures.py::test_growth_and_shrink_keep_identity` → **PASSED** (0.0010 s)
- `tests/test_structures.py::test_split_creates_two_structures` → **PASSED** (0.0010 s)
- `tests/test_structures.py::test_merge_creates_one_structure` → **PASSED** (0.0010 s)
- `tests/test_structures.py::test_transform_same_size_new_topology` → **PASSED** (0.0010 s)
