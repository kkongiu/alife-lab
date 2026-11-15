# M2-04 — Catalisi locale per differenza

- Requisito: docx S2 — catalisi basata su proprietà locali
- Esito: **PASS**
- Eseguito: 2026-11-15T11:55:42+00:00
- Test pytest associati: 2 (2 superati)

## Scenario

Stessa configurazione e stesso seed; probabilità base 1e-9, fattore catalitico 1e9 su S0-S1: senza catalisi non si forma nulla, con la catalisi la coppia si forma.

## Misure

| Voce | Valore |
|---|---|
| formazioni senza catalisi | 0 |
| formazioni con catalisi | 44 |
| legami finali senza catalisi | 0 |
| legami finali con catalisi | 13 |
| configurazioni identiche tranne la catalisi | True |

## Verifiche

| Verifica | Esito |
|---|---|
| senza catalisi non si formano legami | OK |
| con la catalisi si formano legami | OK |
| l'energia resta conservata con la catalisi | OK |

## Test pytest associati

- `tests/test_chemistry.py::test_catalysis_multiplies_only_when_adjacent` → **PASSED** (0.0010 s)
- `tests/test_chemistry.py::test_catalysis_config_changes_chemistry` → **PASSED** (0.2310 s)
