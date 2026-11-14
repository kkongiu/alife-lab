# M2 — Report: chimica artificiale e legami reversibili

Data: 2026-11-15 · Milestone: M2 · Specifica: `SPEC.md` · Cronologia: `git log`

## 1. Sommario

| Milestone | Esito | Evidenza |
|---|---|---|
| **M0** | GO | `SPEC.md` v2: regole, invarianti, formati, limiti. |
| **M1** | GO (approvato) | 64 test, hash M1 riprodotto anche dal codice M2 (golden hash). |
| **M2** | **GO** | 104 test; 15 file di evidenza misurati; legami reversibili con bilancio energetico esatto; aggregati non banali e stabili su 10 000 passi; determinismo, ripresa e migrazione verificati. |

Il gate del docx per M2 — *l'ambiente produce una varietà non banale di strutture
mentre il motore resta misurabile e stabile* — è soddisfatto dai dati del §5, non
dall'aspetto di un'animazione. Non è stato osservato nulla che somigli a
replicazione o ereditarietà, e M2 non era progettata per questo.

## 2. Perimetro

Implementato:

- identificativi persistenti delle particelle, con `next_id` e inclusione
  nell'hash completo;
- energia intera **per particella**, oltre al deposito energetico nei legami;
- legami reversibili fra particelle adiacenti, con coppie ammesse, `max_bonds`
  per specie, soglia energetica e decadimento;
- catalisi locale come fattore moltiplicativo, spenta nella baseline;
- checkpoint schema 2 con migrazione automatica dei checkpoint M1;
- registro eventi opzionale (`--events`): ogni formazione e rottura, tracciabile;
- metriche di struttura: aggregati, dimensione massima e media, distribuzione.

Non implementato, per contratto: flussi energetici e non-equilibrio (M3),
rilevamento e tracciamento delle strutture (M4), controlli positivi (M5),
replicazione, ereditarietà, reti neurali, ricompense.

## 3. Prerequisiti di M2: come sono stati risolti

Il report M1 li aveva dichiarati bloccanti. Ecco le decisioni prese.

| Prerequisito | Decisione | Verifica |
|---|---|---|
| Identificativi persistenti | ID assegnati in ordine crescente, salvati nel checkpoint, mai riutilizzati; `next_id` = primo libero; ID e indice coincidono finché non esistono nascita/morte | `test_v1_checkpoint_is_migrated`, invariante I8 |
| Energia per particella | array `energy` intero; dotazione iniziale dalla specie; nessun float nel percorso caldo | I6, I9, `test_energy_with_bonds_is_conserved` |
| Costo dei legami | ogni particella paga `bond_cost`; il legame immagazzina `2·bond_cost`; alla rottura restituisce le due quote; il resto va all'ID minore | `test_bond_forms_between_adjacent_allowed_particles`, `test_breaking_returns_energy` |
| Formato checkpoint | schema 2; lo schema 1 è letto e migrato (`id = indice`, energia iniziale, nessun legame) | `test_v1_checkpoint_is_migrated` |
| Compatibilità dei risultati M1 | `state_hash` mantiene la definizione M1; il nuovo `state_hash_full` include identità, energia e legami | `test_v1_hash_is_unchanged`, `test_m1_run_reproduces_the_published_hash` |

Il golden hash è la verifica più forte: il run M1 al passo 1000 produce
`3f4a885a…d553af` sia con il codice M1 sia con il codice M2, quindi la semantica
del caso senza chimica non è cambiata.

## 4. Regole implementate

| Regola | Parametri | Nota |
|---|---|---|
| Formazione | coppia ammessa, adiacenza, slot liberi, `energia ≥ bond_cost`, estrazione | 1 estrazione per coppia candidata, ordine canonico |
| Rottura | `break_probability` per legame e per passo | 1 estrazione per legame esistente |
| Energia del legame | `2·bond_cost` immagazzinati, restituiti alla rottura | sistema chiuso, nessuna dissipazione |
| Immobilità | una particella con grado > 0 non propone mosse | limite dichiarato |
| Catalisi | fattore su una coppia, se una specie catalizzatrice è adiacente | spenta nella baseline |
| Aggregati | componenti connesse di dimensione ≥ 2 | misurate a posteriori, non riconosciute dal motore |

Ordine del passo: rottura → proposta di movimento → risoluzione → formazione.
La rottura prima del movimento rende mobile una particella nello stesso passo in
cui si libera; la formazione dopo il movimento permette a nuove adiacenze di
reagire subito.

## 5. Risultati sulla baseline (10 000 passi)

`configs/m2_baseline.json`: 128×128, 4 specie, 1400 particelle (8.5%), energia
iniziale 16 100 quanti.

| Metrica | Valore |
|---|---|
| Durata | 33.48 s |
| Passi/s | **298.6** |
| Spostamenti | 2 150 711 (215 per passo) |
| Legami finali | 686 |
| Particelle legate / libere | 942 / 458 |
| Aggregati (dim. ≥ 2) | 284 |
| Dimensione massima / media | 14 / 3.32 |
| Formazioni / rotture cumulate | 13 746 / 13 060 |
| Energia | 16 100 = 13 356 (particelle) + 2 744 (legami), delta 0 |
| `state_hash` / `state_hash_full` | `6a9866f1…` / `a38a6acf…` |
| Memoria (picco / simulazione) | 42.9 MiB / 6.2 MiB |

### 5.1 Distribuzione degli aggregati (passo 10 000)

| Dimensione | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|
| Numero | 99 | 77 | 70 | 22 | 7 | 2 | 3 | 1 | 2 | 1 |

La distribuzione è monotona decrescente con una coda lunga: il tipo di forma che
ci si aspetta da aggregazione con rottura, non da un aggregato unico che
ingloba tutto. Non è una prova di autocatalisi: senza un controllo negativo
(M5) non si può escludere che sia semplice aggregazione cinetica.

### 5.2 Stato stazionario

| Passo | 2 000 | 4 000 | 6 000 | 8 000 | 10 000 |
|---|---|---|---|---|---|
| Legami | 661 | 665 | 676 | 694 | 686 |
| Aggregati | 282 | 277 | 283 | 267 | 284 |
| Massimo | 13 | 9 | 11 | 16 | 14 |

Il sistema raggiunge un regime stazionario entro ~2 000 passi: formazione e
rottura si bilanciano (13 746 vs 13 060). Non c'è crescita illimitata né
collasso. È la condizione di stabilità richiesta dal gate, misurata e non
impressionistica.

## 6. Catalisi: un risultato negativo onesto

Nella baseline la catalisi (fattore 8 su S0-S1) cambia le formazioni cumulate al
passo 5 000 solo dello **0,6%** (7 071 contro 7 030) e lascia invariata la
struttura macroscopica (648 contro 679 legami).

**Perché.** Con `formation_probability = 0.05` e `max_bonds` basso, la chimica è
limitata dalla **disponibilità di slot e di coppie adiacenti**, non dalla
probabilità di reazione. Moltiplicare una probabilità che non è il collo di
bottiglia non cambia nulla di misurabile. È un risultato negativo pulito e va
registrato come tale: la catalisi non è un effetto forte in questo regime.

Per mostrare che il meccanismo funziona, è stato usato un regime limitato dalla
probabilità (base `1e-9`, fattore `1e9`), a parità di seed e di configurazione:

| | Formazioni | Legami finali |
|---|---|---|
| senza catalisi | 0 | 0 |
| con catalisi | 44 | 13 |

Il meccanismo è quindi corretto e isolato; il suo effetto macroscopico dipende
dal regime. Nessuna delle due misure è presentata come scoperta.

## 7. Eventi tracciati

Con `--events` ogni formazione e rottura è registrata con passo, ID, energia e
flag di catalisi. Run di prova (`configs/m2_catalysis.json`, 300 passi, 1400
particelle): **956 eventi**, 752 formazioni e 204 rotture, di cui **57
formazioni catalizzate**. Esempi:

```json
{"kind": "form", "step": 0,  "id_a": 16,  "id_b": 37,  "energy": 4, "catalyzed": false}
{"kind": "form", "step": 2,  "id_a": 274, "id_b": 687, "energy": 4, "catalyzed": true}
```

Il registro permette di ricostruire la storia di un aggregato senza guardare la
griglia: è il materiale grezzo che M4 userà per il tracciamento delle strutture.

## 8. Compatibilità e migrazione

- Configurazione schema 1 invariata: hash `f697f983…91c8` come in M1.
- Checkpoint M1 (schema 1) caricato dal codice M2: ID contigui, energia iniziale
  della specie, nessun legame, `state_hash` identico.
- `runs/baseline/checkpoint.json` (M1, passo 10 000) si carica e ispeziona
  correttamente con il codice M2.

## 9. Performance

Misura end-to-end (CLI, I/O incluso) della baseline M2: 33.48 s per 10 000 passi,
298.6 passi/s, 42.9 MiB di picco, 6.2 MiB attribuibili alla simulazione.

Rispetto a M1 (225.8 passi/s sulla baseline fisica) il motore è più veloce perché
le particelle legate non si muovono: a parità di passi ci sono meno proposte da
risolvere. Il costo della chimica (scansione dei vicini, estrazioni per legame e
per candidato) è inferiore al risparmio di movimento in questa configurazione.

### 9.1 Benchmark a ripetizioni (3 run indipendenti, mediana)

| Caso | Particelle | Passi | Passi/s | min–max | MB sim |
|---|---|---|---|---|---|
| quick 32×32 (M1) | 90 | 1 000 | 5 876.8 | 5 493.8–6 306.6 | 3.5 |
| baseline 128×128 (M1) | 1 638 | 500 | 211.2 | 199.4–240.0 | 4.9 |
| **M2 chimica 128×128** | 1 400 | 300 | **255.3** | 245.5–271.3 | 4.9 |
| densità 2.5% | 410 | 500 | 1 096.9 | 1 092.3–1 103.4 | 4.9 |
| densità 25% | 4 096 | 200 | 64.5 | 61.8–64.6 | 5.6 |
| densità 50% | 8 192 | 100 | 6.8 | 6.6–7.4 | 7.5 |

### 9.2 Equivalenza continuo ↔ ripreso

| Configurazione | Passi | Checkpoint | Hash | RNG | Mosse | Legami |
|---|---|---|---|---|---|---|
| baseline M1 | 2 000 | 37 972 B | uguale | uguale | uguali | n/d |
| m2_quick | 400 | 4 107 B | uguale | uguale | uguali | uguali |

Il checkpoint M1 è ora serializzato in schema 2, quindi è più grande di quello
prodotto da M1 (22.9 KB): contiene anche identità, energia e legami.

I dati grezzi sono in `reports/benchmark.json`, generato da
`tools/benchmark.py --repeats 3`.

## 10. Test

```
104 passed in 12.9 s
```

15 requisiti hanno un file di evidenza con misure reali
(`reports/tests/evidence/`): 8 obbligatori M1 e 7 di M2 (legami, energia,
regole locali, catalisi, aggregati, determinismo, migrazione). Ogni caso ha il
proprio file in `reports/tests/cases/`; indice in `reports/tests/index.md`.

Le verifiche che contano di più:

- bilancio energetico esatto su 10 000 passi con ~700 legami;
- ripresa continua ≡ interrotta con legami ed energia (hash completo, RNG e
  insieme dei legami identici);
- corruzione di un legame, dell'energia di una particella o di un ID rilevata;
- golden hash M1 riprodotto dal codice M2.

## 11. Decisioni progettuali

| # | Decisione | Motivazione |
|---|---|---|
| D12 | ID persistenti già in M2, con `next_id` | evita una migrazione traumatica in M3; il costo ora è minimo |
| D13 | Energia per particella + deposito nei legami | rende il costo dei legami reale e conservativo; prepara M3 |
| D14 | Particelle legate immobili | elimina la dinamica di corpo rigido, che richiederebbe risoluzione a livello di componente |
| D15 | Ordine: rottura → movimento → formazione | una particella liberata si muove subito; le nuove adiacenze reagiscono subito |
| D16 | Catalisi moltiplicativa, spenta di default | misurabile per differenza; non contamina la baseline |
| D17 | Due hash (materiale e completo) | conserva la confrontabilità con M1 e verifica l'intero stato |
| D18 | Migrazione automatica dello schema 1 | i risultati M1 restano riproducibili e ispezionabili |
| D19 | Eventi opt-in | nessun costo né file enorme nei run lunghi; disponibili quando servono |

## 12. Limiti e problemi aperti

1. **Nessun moto rigido degli aggregati** (§15 SPEC). Un aggregato è immobile
   finché non si rompe un legame: questo favorisce la persistenza e limita la
   riorganizzazione. Da valutare in M4, quando la persistenza andrà misurata.
2. **Chimica limitata dagli slot**, non dalle probabilità (§6). Le conclusioni
   sulla catalisi valgono per il regime testato, non in generale.
3. **Costo dei legami costante** e uguale per tutte le coppie; nessuna
   specificità energetica per specie.
4. **Nessuna sorgente o pozzo**: le strutture non sono mantenute da un flusso.
   M3 dovrà introdurre ingresso, dissipazione e scarsità, mantenendo il bilancio.
5. **Nessun decadimento delle particelle**: la materia resta costante; nascita e
   morte richiedono una politica di rilascio degli ID.
6. **Costo superlineare in densità** (ereditato da M1): non tocca la baseline.
7. **Blocking**: la formazione valuta solo coppie adiacenti al momento; non
   esiste orientamento né valenza direzionale.
8. **Riproducibilità cross-version** ancora non garantita, ma il golden hash M1
   la rende verificabile per il caso senza chimica.

## 13. Verdetti

**M2: GO.** Le regole sono locali, esplicite, testate e conservano materia ed
energia; le strutture sono misurate, stabili e non banalmente degeneri; il
motore resta misurabile e riproducibile. La catalisi è implementata e verificata,
ma il suo effetto è debole nel regime della baseline: questo è documentato come
risultato, non nascosto.

**M3 non è stata iniziata.** Flussi energetici, dissipazione, sorgenti e pozzi
richiedono approvazione esplicita.
