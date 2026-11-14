# ALIFE — Laboratorio di vita artificiale

Universo computazionale minimo, deterministico e headless, nel quale osservare —
senza imporle — eventuali proprietà emergenti. Questo repository contiene la
milestone **M1**: il motore fisico locale e la sua infrastruttura di
riproducibilità.

**M1 non contiene vita, né la cerca.** Non ci sono organismi, genomi,
replicatori, reti neurali, funzioni di fitness, sorgenti di energia o reazioni.
Ci sono particelle che si spostano su una griglia, con invarianti verificabili e
riproducibilità completa.

Documenti:

- [`SPEC.md`](SPEC.md) — specifica del modello, sufficiente a una
  reimplementazione indipendente.
- [`reports/M1_baseline.md`](reports/M1_baseline.md) — performance misurate,
  decisioni progettuali, problemi aperti.
- `alife.md`, `Progetto_Vita_Artificiale_Roadmap_Milestone.docx` — contratto di
  progetto e roadmap.

## Installazione

Richiede Python ≥ 3.12 (verificato su 3.14.9 con NumPy 2.5.4). Nessuna dipendenza
oltre NumPy; `pytest` solo per i test.

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

## Comandi

```bash
# run baseline: 128x128, 6 specie, 1638 particelle, 10 000 passi
.venv/bin/alife run --config configs/baseline.json \
    --steps 10000 --out runs/baseline

# ripresa esatta da checkpoint (stato + generatore casuale)
.venv/bin/alife resume --checkpoint runs/baseline/checkpoint.json \
    --steps 5000

# ispezione di un checkpoint senza evolvere
.venv/bin/alife inspect --checkpoint runs/baseline/checkpoint.json

# run rapido di prova (32x32, 90 particelle)
.venv/bin/alife run --config configs/quick.json --steps 100 --out runs/quick
```

Equivalente senza installazione:

```bash
PYTHONPATH=src .venv/bin/python -m alife run --config configs/quick.json \
    --steps 100 --out runs/quick
```

Opzioni: `--seed` sovrascrive il seed della configurazione (produce un nuovo hash
di configurazione), `--metrics-every N` regola la frequenza dei record.

### Artefatti di un run

| File | Contenuto |
|---|---|
| `manifest.json` | comando, seed, hash config, versioni, piattaforma, commit git |
| `config.resolved.json` | configurazione effettivamente usata |
| `metrics.jsonl` | serie temporale: conteggi, spostamenti, occupazione, energia, hash |
| `summary.json` | riepilogo finale: passi/s, memoria di picco, hash finale, invarianti |
| `checkpoint.json` | stato completo riprendibile (particelle + RNG + passo) |

## Modello in breve

- Griglia `128 × 128`, confini periodici (o chiusi), massimo una particella per
  cella, fino a 6 specie.
- Ogni specie ha solo `move_probability` ed `energy` (quanti interi).
- Un passo: ogni particella propone una mossa (2 estrazioni RNG), poi le mosse
  sono risolte **simultaneamente** con priorità deterministica, gestendo
  contese, scambi e catene. Nessuna dipendenza dall'ordine di scansione.
- L'energia è conservata per costruzione: nessuna sorgente, nessun pozzo, nessun
  costo di movimento in M1.
- Tutte le decisioni usano aritmetica intera sui bit grezzi di PCG64: nessun
  calcolo in virgola mobile nel percorso caldo.

Dettagli, invarianti e formato dei file: [`SPEC.md`](SPEC.md).

## Test

```bash
.venv/bin/python -m pytest
```

La suite copre gli 8 test obbligatori del contratto M1: conservazione di materia e
specie, occupazione unica, confini, riproducibilità, integrità dei checkpoint,
equivalenza fra run continuo e ripreso, rilevamento di violazioni intenzionali.
Aggiunge test sulla risoluzione dei conflitti, sul consumo esatto del generatore,
sulla validazione della configurazione, sulla CLI e sulle metriche.

### Risultati per ogni test

```bash
.venv/bin/python tools/test_report.py
```

Genera `reports/tests/`:

- `index.md` — indice con esito di tutti i casi;
- `cases/*.md` — **un file per ogni caso di test** (nodo, esito, durata,
  requisito, comando di rerun, output o errore);
- `evidence/M1-0N_*.md` — **un file per ogni test obbligatorio**, con le misure
  reali dello scenario (conteggi, hash, delta, messaggi d'errore);
- `results.json`, `junit.xml`, `pytest.log`.

## Benchmark

```bash
.venv/bin/python tools/benchmark.py --steps 1000
```

Misura passi/s e memoria su più densità, verifica l'equivalenza fra run continuo e
run ripreso alla scala della baseline e scrive `reports/benchmark.json`. I
risultati misurati sono in [`reports/M1_baseline.md`](reports/M1_baseline.md).

## Struttura

```
alife/
├── pyproject.toml
├── SPEC.md
├── README.md
├── configs/
│   ├── baseline.json
│   └── quick.json
├── src/alife/
│   ├── config.py        # parsing, validazione, hash canonico
│   ├── rng.py           # PCG64 + stato serializzabile
│   ├── particles.py     # stato delle particelle e occupazione
│   ├── dynamics.py      # proposta, conflitti, applicazione
│   ├── world.py         # universo, invarianti, hash
│   ├── persistence.py   # checkpoint atomici e verificati
│   ├── metrics.py       # serie temporali, riepilogo, memoria
│   └── cli.py           # run / resume / inspect
├── tests/
└── runs/
```

Il core non dipende dalla visualizzazione, che non esiste in M1 e sarà un
componente separato.

## Limiti

Il motore non può produrre strutture persistenti: senza interazioni attrattive è
una nuvola diffusa. È voluto. Le milestone successive introducono chimica (M2),
non-equilibrio (M3), osservabilità (M4), controlli (M5). Non è previsto procedere
oltre M1 senza approvazione esplicita.

## Nota scientifica

La comparsa spontanea di replicatori è un obiettivo sperimentale incerto, non un
risultato atteso. Il criterio di successo del progetto è avere una piattaforma
riproducibile capace di distinguere pattern casuali da autocatalisi, replicazione
ed ereditarietà — anche quando il risultato è negativo.
