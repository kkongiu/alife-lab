# M6-02 — Stato di tracker e rilevatore ripristinabile

- Requisito: M6 — salvare e ripristinare anche l'analisi
- Esito: **PASS**
- Eseguito: 2026-11-15T13:21:15+00:00
- Test pytest associati: 3 (3 superati)

## Scenario

Salvataggio e ripristino di tracker e rilevatore: run continuo di 40 passi contro run interrotto a 20 e ripreso.

## Misure

| Voce | Valore |
|---|---|
| passo salvato | 20 |
| hash completo continuo | ffe1266ff45810f0d82847995c16394a… |
| hash completo ripreso | ffe1266ff45810f0d82847995c16394a… |
| strutture attive | 20 |
| riepiloghi strutture identici | True |
| riepiloghi rilevatore identici | True |

## Verifiche

| Verifica | Esito |
|---|---|
| mondo identico | OK |
| tracker identico | OK |
| rilevatore identico | OK |

## Test pytest associati

- `tests/test_analysis.py::test_roundtrip_preserves_state` → **PASSED** (0.0430 s)
- `tests/test_analysis.py::test_resume_matches_continuous_run` → **PASSED** (0.0920 s)
- `tests/test_analysis.py::test_restore_requires_matching_step` → **PASSED** (0.0090 s)
