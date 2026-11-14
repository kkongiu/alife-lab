# M2-03 — Coppie ammesse, max_bonds e adiacenza

- Requisito: docx S2 — reazioni locali e generali
- Esito: **PASS**
- Eseguito: 2026-11-14T21:52:15+00:00
- Test pytest associati: 6 (6 superati)

## Scenario

Configurazione M2 quick, 300 passi: verifica delle regole locali sui legami formatisi.

## Misure

| Voce | Valore |
|---|---|
| grado massimo osservato per specie | S0=2, S1=2, S2=1, S3=0 |
| max_bonds per specie | S0=2, S1=2, S2=1, S3=0 |
| legami fra specie non ammesse | 0 |
| legami fra particelle non adiacenti | 0 |
| legami totali | 54 |

## Verifiche

| Verifica | Esito |
|---|---|
| ogni grado rispetta max_bonds | OK |
| nessuna coppia non ammessa | OK |
| tutti i legami sono locali | OK |

## Test pytest associati

- `tests/test_chemistry.py::test_no_bond_for_non_allowed_species` → **PASSED** (0.0010 s)
- `tests/test_chemistry.py::test_no_bond_when_species_cannot_bond` → **PASSED** (0.0010 s)
- `tests/test_chemistry.py::test_max_bonds_is_respected` → **PASSED** (0.0000 s)
- `tests/test_chemistry.py::test_chains_grow_to_max_bonds` → **PASSED** (0.0010 s)
- `tests/test_invariants.py::test_validate_detects_non_adjacent_bond` → **PASSED** (0.0020 s)
- `tests/test_invariants.py::test_validate_detects_bond_beyond_max_bonds` → **PASSED** (0.0020 s)
