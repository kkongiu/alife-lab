# M1-06 — Integrità del salvataggio e caricamento

- Requisito: alife.md §7, punto 6
- Esito: **PASS**
- Eseguito: 2026-11-15T13:21:08+00:00
- Test pytest associati: 4 (4 superati)

## Scenario

Universo 16×16, seed 106, 17 passi: salvataggio, ricaricamento e corruzione intenzionale di una specie.

## Misure

| Voce | Valore |
|---|---|
| dimensione checkpoint | 1564 byte |
| passo ricaricato | 17 |
| hash originale = hash ricaricato | True |
| RNG originale = RNG ricaricato | True |
| errore sul file corrotto | checkpoint: hash dello stato non coerente (file corrotto) |

## Verifiche

| Verifica | Esito |
|---|---|
| stato identico dopo il caricamento | OK |
| configurazione identica | OK |
| file corrotto rifiutato | OK |

## Test pytest associati

- `tests/test_checkpoint.py::test_roundtrip_preserves_state` → **PASSED** (0.0030 s)
- `tests/test_checkpoint.py::test_repeated_save_load_cycles_are_stable` → **PASSED** (0.0050 s)
- `tests/test_checkpoint.py::test_checkpoint_does_not_mutate_world` → **PASSED** (0.0020 s)
- `tests/test_checkpoint.py::test_no_temporary_file_left_behind` → **PASSED** (0.0010 s)
