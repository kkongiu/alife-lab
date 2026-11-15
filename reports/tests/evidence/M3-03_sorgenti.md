# M3-03 — Sorgenti con accumulatore e capacità

- Requisito: docx S3 — ingresso energetico localizzato
- Esito: **PASS**
- Eseguito: 2026-11-15T11:25:11+00:00
- Test pytest associati: 3 (3 superati)

## Scenario

Sorgente con tasso 1/4 e particella presente per 1000 passi (atteso 250 quanti assorbiti) e serbatoio con capacità 10 su cella vuota per 20 passi (atteso 10 immagazzinati, 10 traboccati).

## Misure

| Voce | Valore |
|---|---|
| iniettati a tasso 1/4 in 1000 passi | 250 |
| assorbiti | 250 |
| serbatoio finale | [0] |
| iniettati con capacità 10 in 20 passi | 20 |
| immagazzinati nel serbatoio | [10] |
| traboccati | 10 |

## Verifiche

| Verifica | Esito |
|---|---|
| nessun drift: 250 quanti | OK |
| tutto assorbito dalla particella | OK |
| serbatoio vuoto quando la particella è presente | OK |
| capacità del serbatoio rispettata | OK |
| trabocco contabilizzato | OK |

## Test pytest associati

- `tests/test_energy.py::test_source_accumulator_is_exact` → **PASSED** (0.0040 s)
- `tests/test_energy.py::test_source_capacity_and_unabsorbed` → **PASSED** (0.0010 s)
- `tests/test_energy.py::test_source_on_empty_cell_is_unabsorbed` → **PASSED** (0.0010 s)
