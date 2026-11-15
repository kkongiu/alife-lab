# M4-02 — Cicli come impronte, ambiguità dichiarata

- Requisito: docx S4 — incertezza dove una copia è ambigua
- Esito: **PASS**
- Eseguito: 2026-11-15T07:15:23+00:00
- Test pytest associati: 3 (3 superati)

## Scenario

Un anello a quattro particelle (ciclo) e due casi di firma condivisa: due anelli identici e due dimeri identici.

## Misure

| Voce | Valore |
|---|---|
| anello: firma esatta? | False |
| anello: prefisso firma | F:29e741479208d9ab2e2c0c |
| due anelli: firme distinte | 1 |
| due anelli: strutture ambigue | 2 |
| due dimeri: strutture ambigue | 0 |
| due dimeri: collisioni di firma | 1 |

## Verifiche

| Verifica | Esito |
|---|---|
| i cicli usano un'impronta, non una firma esatta | OK |
| due anelli identici sono ambigui | OK |
| due dimeri identici non sono ambigui | OK |
| i dimeri condividono una firma esatta | OK |

## Test pytest associati

- `tests/test_structures.py::test_cycles_are_fingerprints_not_exact` → **PASSED** (0.0010 s)
- `tests/test_structures.py::test_fuzzy_collision_is_reported_as_ambiguity` → **PASSED** (0.0010 s)
- `tests/test_structures.py::test_exact_signature_collision_is_not_ambiguity` → **PASSED** (0.0010 s)
