# M2-05 — Aggregati: distribuzione delle dimensioni

- Requisito: docx S2 — evidenze sulla varietà di strutture
- Esito: **PASS**
- Eseguito: 2026-11-15T11:11:42+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Configurazione M2 quick, 500 passi: aggregati come componenti connesse dei legami.

## Misure

| Voce | Valore |
|---|---|
| legami | 56 |
| particelle legate | 72 |
| particelle libere | 28 |
| aggregati | 21 |
| dimensione massima | 6 |
| dimensione media | 3.4286 |
| distribuzione (dimensione×numero) | 2×7, 3×3, 4×8, 5×1, 6×2 |

## Verifiche

| Verifica | Esito |
|---|---|
| esistono aggregati | OK |
| la distribuzione è non banale | OK |
| nessuna violazione di invariante | OK |

## Test pytest associati

- `tests/test_chemistry.py::test_aggregate_statistics` → **PASSED** (0.0000 s)
- `tests/test_chemistry.py::test_m2_baseline_produces_structures_and_conserves_energy` → **PASSED** (1.8120 s)
