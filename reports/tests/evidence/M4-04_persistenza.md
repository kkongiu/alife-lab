# M4-04 — Persistenza: distribuzione delle vite

- Requisito: docx S4 — metriche di persistenza
- Esito: **PASS**
- Eseguito: 2026-11-15T11:25:11+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Stesse sei particelle: ogni identità che termina contribuisce alla distribuzione delle vite, incluse quelle interrotte da fusione o scissione.

## Misure

| Voce | Valore |
|---|---|
| strutture concluse | 5 |
| vita media | 1.8 |
| vita massima | 3 |
| istogramma | {"1": 2, "2": 2, "5": 1} |

## Verifiche

| Verifica | Esito |
|---|---|
| cinque identità concluse | OK |
| vita media 1.8 | OK |
| vita massima 3 | OK |

## Test pytest associati

- `tests/test_structures.py::test_lifetime_counts_steps_alive` → **PASSED** (0.0010 s)
- `tests/test_structures.py::test_birth_and_death` → **PASSED** (0.0010 s)
