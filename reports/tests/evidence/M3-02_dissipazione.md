# M3-02 — Dissipazione esatta di particelle e legami

- Requisito: docx S3 — dissipazione
- Esito: **PASS**
- Eseguito: 2026-11-15T11:25:11+00:00
- Test pytest associati: 3 (3 superati)

## Scenario

Decadimento sfasato: 1 quanto ogni 3 passi per una particella con 100 quanti; 1 quanto per passo su un legame con 100.

## Misure

| Voce | Valore |
|---|---|
| energia della particella dopo 9 passi | 97 |
| dissipato dalla particella | 3 |
| energia del legame dopo 3 passi | 97 |
| dissipato dal legame | 3 |

## Verifiche

| Verifica | Esito |
|---|---|
| particella: 3 quanti in 9 passi | OK |
| legame: 3 quanti in 3 passi | OK |

## Test pytest associati

- `tests/test_energy.py::test_particle_decay_is_exact` → **PASSED** (0.0010 s)
- `tests/test_energy.py::test_bond_decay_is_exact` → **PASSED** (0.0010 s)
- `tests/test_energy.py::test_particle_decay_uses_identity_not_index` → **PASSED** (0.0010 s)
