# M1 — Report: performance, decisioni, problemi aperti

Data: 2026-11-14 · Codice: `7521319` (M1) · Specifica: `SPEC.md`

## 1. Sommario

| Milestone | Esito | Evidenza |
|---|---|---|
| **M0** | **GO** | `SPEC.md` specifica stato, particelle, tempo, movimento, conflitti, RNG, energia, invarianti, formati e limiti. Un'implementazione indipendente non richiede decisioni implicite. |
| **M1** | **GO** | 61 test superati; determinismo verificato; checkpoint e ripresa equivalenti al run continuo; invarianti conservati su 10 000 passi; performance misurate, non dichiarate. |

Nessuna proprietà biologica è stata introdotta o osservata. M1 è un risultato
ingegneristico, non scientifico, e non autorizza conclusioni sull'ipotesi del
progetto.

## 2. Ambiente di misura

| Voce | Valore |
|---|---|
| CPU | 8 core x86_64 |
| RAM | 15 GiB |
| Sistema | Linux 7.3.3-1-cachyos (glibc 2.44) |
| Python | 3.14.9 (`venv` locale, `.venv/`) |
| NumPy | 2.5.4 |
| pytest | 9.2.0 |
| Motore | Python puro; NumPy usato solo per PCG64 |

Il contratto indicava Python 3.12; l'ambiente dispone di 3.14.9. La scelta
approvata è `requires-python >= 3.12` con registrazione della versione effettiva
in ogni manifest. La riproducibilità è documentata per "stesso ambiente
software" (livello A/B di `SPEC.md` §7), non come identità bit-a-bit fra macchine.

## 3. Metodo

- **Benchmark in-process** (`tools/benchmark.py`): 20 passi di riscaldamento non
  conteggiati, poi misura con `time.perf_counter`; una sola simulazione per
  processo per caso pesante, per non mescolare cache e GC fra configurazioni.
- **Misura end-to-end** via CLI sulla baseline, con I/O di metriche e checkpoint
  inclusi: è il numero che l'utente vede.
- Memoria: picco RSS del processo (`ru_maxrss`, convertito in byte) più il delta
  rispetto all'avvio del run, che isola la memoria attribuibile alla simulazione
  dall'interprete e da NumPy.
- Nessuna ottimizzazione è stata applicata: prima si misura, poi si decide.

## 4. Risultati

### 4.1 Baseline, 10 000 passi (CLI, I/O incluso)

| Metrica | Valore |
|---|---|
| Passi | 10 000 |
| Durata | 44.28 s |
| Passi/s | **225.8** |
| Particelle | 1 638 (occupazione 9.998%) |
| Spostamenti | 7 974 320 (797.4 per passo, 48.7% delle particelle) |
| Passi/s × particella | ~370 000 aggiornamenti/s |
| Energia | 17 668 quanti, invariata (in 0, out 0, delta 0) |
| Hash finale | `f8fca930c290ebc7a0cd3530bb036b4a17de46921ae930074b27544c84e385a0` |
| Seed / hash config | `20261114` / `f697f983…91c8` |
| Invarianti | ok |

**Tre esecuzioni indipendenti** (processi separati, orari diversi) hanno prodotto
lo stesso hash finale e lo stesso numero di spostamenti. Il determinismo è
verificato a livello di processo, non solo dentro la stessa sessione.

### 4.2 Scalabilità (mediana su 3 ripetizioni indipendenti)

| Caso | Particelle | Passi | Passi/s (mediana) | min–max | Tempo |
|---|---|---|---|---|---|
| quick 32×32 | 90 | 1 000 | 4 747.4 | 4 499.0–4 751.7 | 0.21 s |
| baseline 128×128, 6 specie | 1 638 | 500 | 219.1 | 216.6–224.5 | 2.28 s |
| densità 2.5% | 410 | 500 | 1 078.5 | 996.6–1 105.2 | 0.46 s |
| densità 25% | 4 096 | 200 | 62.4 | 55.0–64.6 | 3.21 s |
| densità 50% | 8 192 | 100 | 7.0 | 6.8–7.2 | 14.18 s |

L'intervallo min–max mostra la variabilità della macchina (±3–10%) ed è riportato
per non spacciare una singola misura come valore esatto.

**Il costo è superlineare nella densità.** Da 2.5% a 50% le particelle crescono
di 20 volte, il tempo per passo di ~147 volte. La causa è nella risoluzione dei
conflitti: a densità alta una frazione grande di proposte contende celle, il
numero di giri di risoluzione cresce e ogni giro riscansiona le mosse pendenti
(costo `O(P)` per giro). La configurazione baseline, al 10%, non è affetta in
modo significativo.

### 4.3 Dove va il tempo (profilazione, 200 passi baseline)

| Fase | Quota del tempo |
|---|---|
| Proposta di movimento (incluse 2 estrazioni RNG per particella) | ~46% |
| Risoluzione dei conflitti (di cui ~31% ordinamento delle priorità) | ~47% |
| Applicazione delle mosse | ~7% |

Dettagli: 655 200 chiamate a `random_raw` (0.44 s su 1.65 s, ~27% del totale per
sola overhead di chiamata Python) e 171 446 calcoli di priorità. La profilazione
aggiunge circa il 15–20% di overhead: le quote sono indicative, non assolute.

I conflitti producono in media ~6.5 rotazioni chiuse per passo al 10% di densità:
è il motivo per cui la risoluzione costa quanto la proposta.

### 4.4 Memoria

| Voce | Valore |
|---|---|
| Picco RSS del processo | **42.4 MiB** |
| Baseline al caricamento (interprete + NumPy) | 36.8 MiB |
| Memoria della simulazione | **5.7 MiB** |

Nota metodologica: una prima serie di misure ha registrato picchi di 526–591 MiB,
non riproducibili e non attribuibili al processo (RSS reale 44 MiB). La causa era
`ru_maxrss`, che in questo ambiente eredita il picco del processo genitore. Il
motore ora legge `VmHWM` da `/proc/self/status` (picco dell'address space
corrente) e registra anche il delta rispetto al caricamento del modulo. È
esattamente il tipo di artefatto numerico che il progetto richiede di
distinguere, e il test M1-01/M1-06 lo documenta nei file di evidenza.

### 4.5 Equivalenza continuo ↔ ripreso a scala (2 000 passi baseline)

```
hash continui uguali: True
stato RNG uguale:     True
mosse totali uguali:  True
checkpoint:           22 989 byte
```

La ripresa da checkpoint non altera né lo stato delle particelle né la posizione
nel flusso casuale.

## 5. Test

```
64 passed in 3.49s
```

Copertura degli 8 test obbligatori: vedi `SPEC.md` §13. In aggiunta: 7 casi di
risoluzione dei conflitti (mossa libera, contesa, scambio, catena, ciclo a tre,
catena bloccata, indipendenza dall'ordine), consumo esatto del flusso RNG,
validazione della configurazione, 6 casi di corruzione dei checkpoint, test
end-to-end della CLI, metriche.

Il test 8 richiede che una violazione intenzionale venga **rilevata**: sono
verificati doppia occupazione, particella fuori griglia, griglia desincronizzata,
particella mancante, specie inesistente, particelle corrotte, hash alterato,
energia alterata, stato RNG mancante.

### File di risultati, uno per test

`tools/test_report.py` esegue la suite, legge il JUnit XML e produce:

| Percorso | Contenuto |
|---|---|
| `reports/tests/index.md` | indice con esito dei test obbligatori e di tutti i casi |
| `reports/tests/cases/*.md` | **un file per ciascuno dei 64 casi**: nodo pytest, esito, durata, requisito associato, comando di rerun, output o dettaglio dell'errore |
| `reports/tests/evidence/M1-0N_*.md` | **un file per ciascuno degli 8 test obbligatori**, con le misure reali dello scenario (conteggi, hash, delta, messaggi di errore), non solo l'esito |
| `reports/tests/results.json` | tutti i casi e le evidenze in forma strutturata |
| `reports/tests/junit.xml` | risultato macchina-leggibile |
| `reports/tests/pytest.log` | log completo dell'esecuzione |

Rigenerabile con `.venv/bin/python tools/test_report.py`; il comando esce con
codice diverso da zero se un test o un'evidenza non è PASS.

## 6. Decisioni progettuali

| # | Decisione | Motivazione |
|---|---|---|
| D1 | Proposta simultanea + risoluzione con priorità hash `(indice, passo)` | elimina la dipendenza dall'ordine di scansione e il bias direzionale; nessun consumo RNG |
| D2 | Due estrazioni RNG per particella per passo, sempre | flusso RNG esattamente `2N` per passo: verificabile con un test, nessuna dipendenza nascosta dal tasso di mobilità |
| D3 | Solo `random_raw()` di PCG64 | stabile fra versioni, a differenza dei metodi di distribuzione |
| D4 | Soglie di probabilità intere (`⌊p·2⁶⁴⌋`) | nessun confronto in virgola mobile nel percorso caldo |
| D5 | Energia intera e passiva, movimento gratuito | bilancio esatto per costruzione; nessun drift da mascherare; innesto pulito per M3 |
| D6 | Indice dell'array = ID della particella | meno stato, checkpoint più piccolo; documentato come limite da rimuovere in M2 |
| D7 | Liste Python, non array NumPy, nel percorso caldo | il passo è dominato da accessi scalari e ordinamenti: NumPy non aiuta e aggiunge conversioni |
| D8 | Checkpoint JSON con scrittura atomica e 8 verifiche in lettura | semplicità ispezionabile; un file corrotto non può passare inosservato |
| D9 | Hash dello stato senza `step` e senza RNG | rende confrontabili run continuo e run ripreso |
| D10 | Chiavi di configurazione sconosciute = errore | un refuso non deve cambiare silenziosamente l'esperimento |
| D11 | Nessuna ottimizzazione applicata | richiesto dal contratto: prima la misura, poi — se serve — il profiling e l'approvazione |

## 7. Problemi aperti

1. **Costo superlineare in densità** (§4.2). Non affligge la baseline, ma M2–M3
   potrebbero lavorare ad alta densità. Candidati: risoluzione a coda di
   dipendenze invece di giri di riscansione, oppure componenti connesse del
   grafo delle proposte. Da valutare solo dopo un caso d'uso reale.
2. **Identità = indice dell'array**: da sostituire con ID persistenti quando
   esisteranno nascita e morte (M2), con migrazione dello schema di checkpoint.
3. **Energia derivata, non memorizzata per particella**: sufficiente in M1,
   insufficiente appena i costi di movimento differiscono (M3).
4. **Ottimizzazione RNG**: l'overhead di chiamata pesa ~27%; richiede di esporre
   il bit generator o di memorizzare i raw a blocchi. Rimandato a M9.
5. **`ru_maxrss`**: il picco assoluto dipende dall'ambiente; il delta è la metrica
   affidabile. Da mantenere in tutti i report futuri.
6. **Riproducibilità cross-version** non garantita: accettata e documentata. Se
   M6 richiederà confronti fra macchine, servirà un riferimento numerico fisso
   (golden hash per configurazione).
7. **Nessun visualizzatore**: escluso da M1 per contratto; il core è già
   indipendente dalla UI.

## 8. Riproduzione

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/python tools/test_report.py
.venv/bin/alife run --config configs/baseline.json --steps 10000 --out runs/baseline
.venv/bin/alife resume --checkpoint runs/baseline/checkpoint.json --steps 5000
.venv/bin/python tools/benchmark.py --repeats 3
```

I numeri di questo report provengono da queste stesse esecuzioni; i dati grezzi
sono in `runs/baseline/`, `reports/benchmark.json` e `reports/tests/`.

## 9. Divergenze fra i documenti di progetto

Nessuna contraddizione bloccante. Tre divergenze, risolte a favore di `alife.md`
(contratto operativo) e documentate:

| Punto | `alife.md` | Docx | Risoluzione |
|---|---|---|---|
| Stack | Python 3.12, JSON, niente Numba senza profiling | YAML/JSON, CSV/SQLite, Numba "se necessario" | 3.12+ (3.14.9 effettivo, registrato), JSON, nessuna accelerazione |
| M1 | nessun legame; legami in M2 | "aggiornamento di particelle/legami" in M1 | nessun legame in M1 |
| M0 | specifica e invarianti | anche tre esperimenti negativi e tabella delle reazioni | tabella vuota in M1 e tre controlli negativi definiti ma non implementati (`SPEC.md` §15) |

Resta una tensione metodologica, non un errore: il docx chiede "tre esperimenti
negativi" già in M0, ma eseguirli richiede un motore con reazioni (M2). Sono
quindi *definiti* ora e *eseguibili* dopo M2, nell'ordine giusto.

## 10. Verdetti

**M0: GO.** La specifica è implementabile da terzi; le decisioni non fissate dai
documenti di progetto sono esplicite e motivate.

**M1: GO.** Le condizioni poste dal docx sono soddisfatte: nessuna creazione o
perdita di materia fuori regola, nessuna discrepanza fra run equivalenti,
prestazioni misurate e riproducibili. Restano i limiti dichiarati al §7, nessuno
dei quali blocca M2.

**Fermarsi qui.** M2 (chimica, legami reversibili) non è stata iniziata e richiede
approvazione esplicita.
