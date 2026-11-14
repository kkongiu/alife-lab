# ALIFE — Laboratorio di vita artificiale

Universo computazionale minimo, deterministico e headless, nel quale osservare —
senza imporle — eventuali proprietà emergenti.

Stato: **M2 — chimica artificiale e legami reversibili**, dopo M1 (motore fisico
locale) approvato.

**M2 non contiene vita, né la cerca.** Non ci sono organismi, genomi, replicatori,
reti neurali, funzioni di fitness, sorgenti di energia. Ci sono particelle che si
spostano, legami reversibili con costo energetico, catalisi locale, con
invarianti verificabili e riproducibilità completa.

Documenti:

- [`SPEC.md`](SPEC.md) — specifica del modello (M1 + M2), sufficiente a una
  reimplementazione indipendente.
- [`reports/M1_baseline.md`](reports/M1_baseline.md) — performance e decisioni M1.
- [`reports/M2_chemistry.md`](reports/M2_chemistry.md) — risultati M2, catalisi,
  aggregati, decisioni, verdetti.
- [`reports/tests/index.md`](reports/tests/index.md) — risultati dei test, con un
  file per ogni caso e un'evidenza misurata per ogni requisito.

## Installazione

Richiede Python ≥ 3.12 (verificato su 3.14.9 con NumPy 2.5.4). Nessuna dipendenza
oltre NumPy; `pytest` solo per i test.

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

## Comandi

```bash
# M2: chimica, 128x128, 4 specie, 1400 particelle, 10 000 passi
.venv/bin/alife run --config configs/m2_baseline.json \
    --steps 10000 --out runs/m2_baseline

# variante con catalisi (S3 catalizza i legami S0-S1)
.venv/bin/alife run --config configs/m2_catalysis.json \
    --steps 5000 --out runs/m2_catalysis

# run con registro eventi: una riga per ogni formazione e rottura
.venv/bin/alife run --config configs/m2_quick.json \
    --steps 300 --out runs/m2_events --events

# ripresa esatta da checkpoint (stato, energia, legami, RNG)
.venv/bin/alife resume --checkpoint runs/m2_baseline/checkpoint.json --steps 5000

# ispezione di un checkpoint senza evolvere
.venv/bin/alife inspect --checkpoint runs/m2_baseline/checkpoint.json

# M1 (compatibile: schema 1, nessuna chimica)
.venv/bin/alife run --config configs/baseline.json --steps 10000 --out runs/baseline
```

Senza installazione: `PYTHONPATH=src .venv/bin/python -m alife …`.

Opzioni: `--seed` sovrascrive il seed (nuovo hash di configurazione),
`--metrics-every N`, `--events`.

### Artefatti di un run

| File | Contenuto |
|---|---|
| `manifest.json` | comando, seed, hash config, versioni, piattaforma, commit |
| `config.resolved.json` | configurazione effettivamente usata |
| `metrics.jsonl` | serie temporale: particelle, legami, aggregati, energia, hash |
| `summary.json` | riepilogo finale: passi/s, memoria, distribuzione aggregati, hash |
| `checkpoint.json` | stato completo riprendibile (particelle, energia, legami, RNG) |
| `events.jsonl` | solo con `--events`: formazioni e rotture, con passo, ID, energia, catalisi |

## Modello in breve

- Griglia `128 × 128`, confini periodici (o chiusi), una particella per cella,
  fino a 6 specie.
- Ogni particella ha **identificativo persistente** ed **energia** intera.
- Ogni specie ha `move_probability`, `energy` iniziale e `max_bonds`.
- Un passo: rottura dei legami → movimento delle particelle libere → risoluzione
  simultanea dei conflitti → formazione dei legami fra vicini.
- Legame = relazione locale reversibile fra particelle adiacenti, ammessa da una
  tabella di coppie, con costo `bond_cost` pagato da entrambe e immagazzinato nel
  legame; alla rottura l'energia torna alle particelle. Sistema chiuso: l'energia
  è conservata per costruzione.
- Le particelle legate sono immobili finché il legame non si rompe.
- La catalisi è un fattore moltiplicativo locale, spento nella baseline.
- Tutte le decisioni usano aritmetica intera sui bit grezzi di PCG64.

Dettagli, invarianti e formati: [`SPEC.md`](SPEC.md).

## Test

```bash
.venv/bin/python -m pytest
```

104 test: gli 8 obbligatori di M1, le regole della chimica M2 (formazione,
rottura, energia, `max_bonds`, coppie ammesse, catalisi, immobilità, aggregati,
migrazione dei checkpoint), più CLI e metriche.

### Risultati per ogni test

```bash
.venv/bin/python tools/test_report.py
```

Genera `reports/tests/`:

- `index.md` — indice con esito di tutti i casi;
- `cases/*.md` — **un file per ogni caso di test**;
- `evidence/M1-0N_*.md` e `evidence/M2-0N_*.md` — **un file per ogni requisito**,
  con le misure reali dello scenario;
- `results.json`, `junit.xml`, `pytest.log`.

## Benchmark

```bash
.venv/bin/python tools/benchmark.py --repeats 3
```

Misura passi/s e memoria su più densità (M1 e M2), verifica l'equivalenza fra run
continuo e run ripreso e scrive `reports/benchmark.json`.

## Struttura

```
alife/
├── pyproject.toml
├── SPEC.md
├── README.md
├── configs/
│   ├── baseline.json          # M1: nessuna chimica
│   ├── quick.json             # M1 veloce
│   ├── m2_baseline.json       # M2: legami, nessuna catalisi
│   ├── m2_catalysis.json      # M2 + catalisi S3 su S0-S1
│   └── m2_quick.json          # M2 veloce (test)
├── src/alife/
│   ├── config.py        # schema 1/2, validazione, hash canonico
│   ├── rng.py           # PCG64 + stato serializzabile
│   ├── particles.py     # particelle, energia, legami, griglia
│   ├── chemistry.py     # formazione, rottura, catalisi, aggregati
│   ├── dynamics.py      # proposta, conflitti, applicazione, passo
│   ├── world.py         # universo, invarianti, hash
│   ├── persistence.py   # checkpoint v2 + migrazione v1
│   ├── events.py        # events.jsonl
│   ├── metrics.py       # serie temporali, riepilogo, memoria
│   └── cli.py           # run / resume / inspect
├── tests/
├── tools/               # benchmark.py, test_report.py
└── runs/
```

## Limiti

Le particelle legate sono immobili: gli aggregati non hanno moto rigido. Non
esistono ancora flussi energetici (M3), nascita o morte di particelle,
ereditarietà. La comparsa di strutture persistenti non è un risultato di
replicazione: M4–M7 richiedono strumenti di osservazione e controlli dedicati.

## Nota scientifica

La comparsa spontanea di replicatori è un obiettivo sperimentale incerto, non un
risultato atteso. Il criterio di successo del progetto è avere una piattaforma
riproducibile capace di distinguere pattern casuali da autocatalisi, replicazione
ed ereditarietà — anche quando il risultato è negativo.
