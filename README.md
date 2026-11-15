# ALIFE — Laboratorio di vita artificiale

Universo computazionale minimo, deterministico e headless, nel quale osservare —
senza imporle — eventuali proprietà emergenti.

Stato: **M6 — campagna esplorativa multi-universo** (in attesa di approvazione),
dopo M1–M5 approvati. Preregistrazione, cinque condizioni, stato di analisi
ripristinabile e registrazione di tutti i run, compresi quelli nulli.

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
- [`reports/M4_observability.md`](reports/M4_observability.md) — firme,
  tracciamento, persistenza, ambiguità.
- [`reports/M5_controls.md`](reports/M5_controls.md) — controllo positivo,
  negativi, sensibilità e falsi positivi.
- [`reports/M6_campaign.md`](reports/M6_campaign.md) — campagna preregistrata,
  confronto fra condizioni, risultati anche nulli.
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

# osservabilità: strutture, firme canoniche, eventi e persistenza
.venv/bin/alife run --config configs/m3_baseline.json \
    --steps 10000 --out runs/m4_tracked --track --events

# ripresa esatta (stato, energia, legami, ledger, RNG)
.venv/bin/alife resume --checkpoint runs/m3_baseline/checkpoint.json --steps 5000

# ispezione senza evolvere
.venv/bin/alife inspect --checkpoint runs/m3_baseline/checkpoint.json

# controlli M5: positivo noto, negativi e rilevatore preregistrato
.venv/bin/python tools/run_controls.py

# campagna M6: preregistrazione (una volta) e esecuzione dei run mancanti
.venv/bin/python tools/preregister_m6.py
.venv/bin/python tools/run_campaign.py
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
| `analysis.json` | solo con `--track`: stato di tracker e rilevatore, ripristinabile |
| `events.jsonl` | solo con `--events`: formazioni e rotture, con passo, ID, energia, catalisi |
| `structures.jsonl` | solo con `--track`: un record per passo sulle strutture |
| `lineage.jsonl` | solo con `--track`: un record per evento (nascita, crescita, scissione, fusione, morte) |

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
- **Osservabilità separata** (`--track`): ogni componente connessa riceve una
  firma canonica — esatta per gli alberi, impronta dichiarata per i cicli — e
  viene tracciata per identità, con eventi di nascita, crescita, scissione,
  fusione, morte e metriche di persistenza.
- **Controlli isolati** (`alife.controls`): un copiatore template-diretto, tre
  negativi e due casi di stress, usati per calibrare un rilevatore con criteri
  preregistrati. Il motore non li importa.

Dettagli, invarianti e formati: [`SPEC.md`](SPEC.md).

## Test

```bash
.venv/bin/python -m pytest
```

176 test: gli 8 obbligatori di M1, le regole della chimica M2, i flussi M3
(identità energetica, dissipazione, sorgenti, costi, determinismo, migrazione),
l'osservabilità M4 (firme, ambiguità, eventi, persistenza), i controlli M5
(isolamento, positivo, negativi, riproducibilità), la campagna M6
(preregistrazione, stato di analisi ripristinabile, copertura dei run), più CLI
e metriche.

### Risultati per ogni test

```bash
.venv/bin/python tools/test_report.py
```

Genera `reports/tests/`:

- `index.md` — indice con esito di tutti i casi;
- `cases/*.md` — **un file per ogni caso di test**;
- `evidence/M1-0N_*.md` … `M5-0N_*.md` — **un file per ogni requisito**, con
  le misure reali dello scenario;
- `results.json`, `junit.xml`, `pytest.log`.

## Benchmark

```bash
.venv/bin/python tools/benchmark.py --repeats 3
```

Misura passi/s e memoria su M1, M2, M3, M4 e più densità, verifica l'equivalenza
fra run continuo e run ripreso (anche con legami e ledger) e scrive
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
│   ├── structures.py    # componenti, firme canoniche, tracciamento
│   ├── replication.py   # rilevatore di copie con criteri preregistrati
│   ├── analysis.py      # tracker + rilevatore, stato ripristinabile
│   ├── controls/        # fixture isolate: positivo, negativi, stress
│   ├── persistence.py   # checkpoint v3 + migrazione v1/v2
│   ├── events.py        # events.jsonl
│   ├── metrics.py       # serie temporali, riepilogo, memoria
│   └── cli.py           # run / resume / inspect
├── tests/
├── tools/               # benchmark, test_report, run_controls, campagne
├── campaigns/m6/        # preregistrazione, configurazioni, risultati
└── runs/
```

## Limiti

Le particelle legate sono immobili: gli aggregati non hanno moto rigido e non
possono raggiungere le sorgenti. Le sorgenti sono puntiformi: metà dell'energia
iniettata trabocca senza essere raccolta. Non esistono ancora nascita o morte di
particelle né ereditarietà. Il tracciamento usa l'identità delle particelle: le
linee dopo scissione o fusione seguono una regola di attribuzione, non una
discendenza biologica. Il controllo positivo di M5 è un copiatore programmato e
isolato: calibra il rilevatore, non dimostra replicazione spontanea. La campagna
M6 usa cinque seed per condizione: è un primo confronto, non uno studio con
potenza statistica. I numeri di `reports/` sono misure, non promesse.

## Nota scientifica

La comparsa spontanea di replicatori è un obiettivo sperimentale incerto, non un
risultato atteso. Il criterio di successo del progetto è avere una piattaforma
riproducibile capace di distinguere pattern casuali da autocatalisi, replicazione
ed ereditarietà — anche quando il risultato è negativo.
