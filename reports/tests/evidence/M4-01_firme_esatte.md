# M4-01 — Firme canoniche esatte per strutture ad albero

- Requisito: docx S4 — firme canoniche delle strutture
- Esito: **PASS**
- Eseguito: 2026-11-15T07:15:23+00:00
- Test pytest associati: 3 (3 superati)

## Scenario

Quattro strutture note: catena S0-S0-S1, la stessa catena con particelle etichettate al contrario, catena S0-S1-S1, stella S1 con tre foglie S0.

## Misure

| Voce | Valore |
|---|---|
| catena: composizione / legami | (('S0', 2), ('S1', 1)) / 2 |
| catena: firma | T:(S0:(S0:(S1:)))… |
| stessa catena rietichettata: firma | T:(S0:(S0:(S1:)))… |
| catena S0-S1-S1: firma | T:(S0:(S1:(S1:)))… |
| stella: firma | T:(S0:(S1:(S0:),(S0:)))… |
| firme esatte | True, True |

## Verifiche

| Verifica | Esito |
|---|---|
| la rietichettatura non cambia la firma | OK |
| composizione diversa ⇒ firma diversa | OK |
| forma diversa ⇒ firma diversa | OK |
| le firme degli alberi sono esatte | OK |

## Test pytest associati

- `tests/test_structures.py::test_chain_signature_is_invariant_under_relabeling` → **PASSED** (0.0010 s)
- `tests/test_structures.py::test_chain_signature_distinguishes_composition` → **PASSED** (0.0010 s)
- `tests/test_structures.py::test_tree_signature_distinguishes_shape` → **PASSED** (0.0010 s)
