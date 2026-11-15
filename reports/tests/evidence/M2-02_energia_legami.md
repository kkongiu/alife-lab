# M2-02 — Conservazione dell'energia con i legami

- Requisito: docx S2 / vincolo di bilancio energetico
- Esito: **PASS**
- Eseguito: 2026-11-15T11:55:42+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Configurazione M2 quick (32×32, 4 specie), 200 passi con legami attivi.

## Misure

| Voce | Valore |
|---|---|
| energia iniziale attesa | 1160 |
| energia nelle particelle | 964 |
| energia nei legami | 196 |
| energia totale | 1160 |
| delta | 0 |
| legami al passo 200 | 49 |

## Verifiche

| Verifica | Esito |
|---|---|
| energia totale = energia iniziale | OK |
| particelle + legami = totale | OK |
| esistono legami | OK |
| nessuna violazione di invariante | OK |

## Test pytest associati

- `tests/test_invariants.py::test_energy_with_bonds_is_conserved` → **PASSED** (0.0790 s)
- `tests/test_chemistry.py::test_m2_baseline_produces_structures_and_conserves_energy` → **PASSED** (2.2550 s)
