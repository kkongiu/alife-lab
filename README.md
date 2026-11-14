# ALIFE — Laboratorio di vita artificiale

Universo computazionale minimo, deterministico e headless, nel quale osservare —
senza imporle — eventuali proprietà emergenti.

Stato: **M3 — flussi energetici, dissipazione e costi**, dopo M1 (motore fisico)
e M2 (chimica e legami reversibili) approvati.

**M3 non contiene vita, né la cerca.** Non ci sono organismi, genomi, replicatori,
reti neurali, funzioni di fitness. Ci sono particelle che si spostano, legami
reversibili con costo energetico, sorgenti localizzate, dissipazione, catalisi
locale, con invarianti verificabili e riproducibilità completa.

Documenti:

- [`SPEC.md`](SPEC.md) — specifica del modello (M1–M3), sufficiente a una
  reimplementazione indipendente.
- [`reports/M1_baseline.md`](reports/M1_baseline.md) — performance e decisioni M1.
- [`reports/M2_chemistry.md`](reports/M2_chemistry.md) — legami, aggregati, catalisi.
- [`reports/M3_energy.md`](reports/M3_energy.md) — flussi, dissipazione, costi,
  confronto chiuso / alimentato / senza alimentazione.
- [`reports/tests/index.md`](reports/tests/index.md) — risultati dei test, con un
  file per ogni caso e un'evidenza misurata per ogni requisito.
- [`docs/M3_flussi_energetici.md`](docs/M3_flussi_energetici.md) — specifica
  tecnica dei flussi energetici (documento di progetto, ora implementato).

## Installazione

Richiede Python ≥ 3.12 (verificato su 3.14.9 con NumPy 2.5.4). Nessuna dipendenza
oltre NumPy; `pytest` solo per i test.

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

## Comandi

```bash
# M3: sistema aperto, 128x128, 9 sorgenti, dissipazione e costi, 10 000 passi
.venv/bin/alife run --config configs/m3_baseline.json \
    --steps 10000 --out runs/m3_baseline

# stesso mondo senza alimentazione: le strutture collassano
.venv/bin/alife run --config configs/m3_unfed.json \
    --steps 10000 --out runs/m3_unfed

# M2: chimica chiusa (nessun costo, nessun flusso)
.venv/bin/alife run --config configs/m2_baseline.json \
    --steps 10000 --out runs/m2_baseline

# M1: solo motore fisico
.venv/bin/alife run --config configs/baseline.json \
    --steps 10000 --out runs/baseline

# registro eventi (formazioni e rotture, con flag di catalisi)
.venv/bin/alife run --config configs/m2_quick.json \
    --steps 300 --out runs/m2_events --events

# ripresa esatta (stato, energia, legami, ledger, RNG)
.venv/bin/alife resume --checkpoint runs/m3_baseline/checkpoint.json --steps 5000

# ispezione senza evolvere
.venv/bin/alife inspect --checkpoint runs/m3_baseline/checkpoint.json
```

Senza installazione: `PYTHONPATH=src .venv/bin/python -m alife …`.

Opzioni: `--seed` sovrascrive il seed (nuovo hash di configurazione),
`--metrics-every N`, `--events`.

### Artefatti di un run

| File | Contenuto |
|---|---|
| `manifest.json` | comando, seed, hash config, versioni, piattaforma, commit |
| `config.resolved.json` | configurazione effettivamente usata |
| `metrics.jsonl` | serie temporale: particelle, legami, aggregati, energia, ledger, hash |
| `summary.json` | riepilogo finale: passi/s, memoria, distribuzione aggregati, identità energetica |
| `checkpoint.json` | stato completo: particelle, energia, legami, sorgenti, ledger, RNG |
| `events.jsonl` | solo con `--events`: formazioni e rotture, con passo, ID, energia, catalisi |

## Modello in breve

- Griglia `128 × 128`, confini periodici (o chiusi), una particella per cella,
  fino a 6 specie.
- Ogni particella ha **identificativo persistente** ed **energia** intera.
- Ogni specie ha `move_probability`, `energy` iniziale e `max_bonds`.
- Un passo (ordine fissato): **dissipazione → iniezione → rottura → movimento →
  risoluzione dei conflitti → formazione dei legami**.
- Legame = relazione locale reversibile fra adiacenti, con `bond_cost`
  immagazzinato e un attrito di formazione; alla rottura l'energia torna alle
  particelle meno l'attrito.
- Sorgenti localizzate con serbatoio e accumulatore interi: `rate_num/rate_den`
  quanti per passo, nessuna estrazione casuale; la particella presente assorbe il
  serbatoio, il trabocco è `unabsorbed`.
- Dissipazione a tasso assoluto sfasato (`num` quanti ogni `den` passi per ID).
- Sistema aperto: l'energia **non** si conserva; si conserva l'identità
  `E = E₀ + injected − dissipated − unabsorbed`, verificata con interi esatti.
- Tutte le decisioni casuali usano aritmetica intera sui bit grezzi di PCG64.

Dettagli, invarianti e formati: [`SPEC.md`](SPEC.md).

## Test

```bash
.venv/bin/python -m pytest
```

136 test: gli 8 obbligatori di M1, le regole della chimica M2, i flussi M3
(identità energetica, dissipazione, sorgenti, costi, determinismo, migrazione),
più CLI e metriche.

### Risultati per ogni test

```bash
.venv/bin/python tools/test_report.py
```

Genera `reports/tests/`:

- `index.md` — indice con esito di tutti i casi;
- `cases/*.md` — **un file per ogni caso di test**;
- `evidence/M1-0N_*.md`, `M2-0N_*.md`, `M3-0N_*.md` — **un file per ogni
  requisito**, con le misure reali dello scenario;
- `results.json`, `junit.xml`, `pytest.log`.

## Benchmark

```bash
.venv/bin/python tools/benchmark.py --repeats 3
```

Misura passi/s e memoria su M1, M2, M3 e più densità, verifica l'equivalenza fra
run continuo e run ripreso (anche con legami e ledger) e scrive
`reports/benchmark.json`.

## Struttura

```
alife/
├── pyproject.toml
├── SPEC.md
├── README.md
├── docs/
│   └── M3_flussi_energetici.md
├── configs/
│   ├── baseline.json          # M1: nessuna chimica
│   ├── quick.json             # M1 veloce
│   ├── m2_baseline.json       # M2: legami, nessuna catalisi
│   ├── m2_catalysis.json      # M2 + catalisi S3 su S0-S1
│   ├── m2_quick.json          # M2 veloce (test)
│   ├── m3_baseline.json       # M3: sorgenti + dissipazione + costi
│   ├── m3_unfed.json          # M3 senza sorgenti
│   └── m3_quick.json          # M3 veloce (test)
├── src/alife/
│   ├── config.py        # schemi 1/2/3, validazione, hash canonico
│   ├── rng.py           # PCG64 + stato serializzabile + contatore estrazioni
│   ├── particles.py     # particelle, energia, legami, griglia
│   ├── chemistry.py     # formazione, rottura, catalisi, aggregati
│   ├── dynamics.py      # proposta, conflitti, applicazione, passo
│   ├── world.py         # universo, flussi, ledger, invarianti, hash
│   ├── persistence.py   # checkpoint v3 + migrazione v1/v2
│   ├── events.py        # events.jsonl
│   ├── metrics.py       # serie temporali, riepilogo, memoria
│   └── cli.py           # run / resume / inspect
├── tests/
├── tools/               # benchmark.py, test_report.py
└── runs/
```

## Limiti

Le particelle legate sono immobili: gli aggregati non hanno moto rigido e non
possono raggiungere le sorgenti. Le sorgenti sono puntiformi: metà dell'energia
iniettata trabocca senza essere raccolta. Non esistono ancora nascita o morte di
particelle, rilevamento delle strutture, ereditarietà. I numeri di `reports/`
sono misure, non promesse.

## Nota scientifica

La comparsa spontanea di replicatori è un obiettivo sperimentale incerto, non un
risultato atteso. Il criterio di successo del progetto è avere una piattaforma
riproducibile capace di distinguere pattern casuali da autocatalisi, replicazione
ed ereditarietà — anche quando il risultato è negativo.
