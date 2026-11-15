# M3-07 — Checkpoint con ledger e accumulatori

- Requisito: docx S3 — riproducibilità dei run aperti
- Esito: **PASS**
- Eseguito: 2026-11-15T11:25:11+00:00
- Test pytest associati: 3 (3 superati)

## Scenario

Salvataggio e ricaricamento di un mondo aperto: ledger, accumulatori e sorgenti devono sopravvivere identici.

## Misure

| Voce | Valore |
|---|---|
| passo | 30 |
| iniettata | 120 |
| dissipata | 670 |
| non assorbita | 34 |
| accumulatori | [0, 0] |
| estrazioni RNG | 7135 |
| dimensione checkpoint | 4319 byte |

## Verifiche

| Verifica | Esito |
|---|---|
| stato identico | OK |
| hash completo identico | OK |
| ledger identico | OK |
| accumulatori identici | OK |

## Test pytest associati

- `tests/test_checkpoint.py::test_v3_roundtrip_preserves_ledger` → **PASSED** (0.0120 s)
- `tests/test_checkpoint.py::test_v3_resume_is_equivalent_with_flows` → **PASSED** (0.0460 s)
- `tests/test_checkpoint.py::test_v2_checkpoint_is_migrated_to_v3` → **PASSED** (0.0100 s)
