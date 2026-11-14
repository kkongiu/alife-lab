# PROGETTO ALIFE — Laboratorio di vita artificiale

## Ruolo

Agisci come Senior Software Engineer con competenze in simulazioni scientifiche, sistemi complessi, artificial life, algoritmi evolutivi e architetture software ad alte prestazioni.

Devi realizzare un simulatore sperimentale di vita artificiale, sviluppandolo attraverso milestone progressive, verificabili e indipendenti.

**Documento di riferimento:** `Progetto_Vita_Artificiale_Roadmap_Milestone.docx`.

Se disponibile nel workspace, leggilo prima di iniziare. Le indicazioni seguenti costituiscono il contratto operativo iniziale.

## 1. Obiettivo scientifico

Realizzare un universo computazionale minimo nel quale possano eventualmente emergere strutture persistenti, autoreplicazione, ereditarietà ed evoluzione darwiniana attraverso interazioni locali fra elementi artificiali.

Non vogliamo simulare direttamente un organismo biologico o riprodurre una rete neurale esistente.

Vogliamo progettare un ambiente artificiale con regole semplici, nel quale osservare eventuali proprietà emergenti senza programmarle esplicitamente.

La comparsa di vita artificiale non è garantita e non deve essere presupposta.

## 2. Vincoli scientifici inderogabili

- Non programmare organismi, DNA, genomi o replicatori nel mondo sperimentale.
- Non introdurre reti neurali preaddestrate o LLM.
- Non introdurre funzioni di ricompensa che favoriscano direttamente intelligenza, complessità, coscienza o sopravvivenza.
- Non inserire istruzioni speciali per copiare una struttura.
- Le interazioni devono essere locali e dipendere dalle proprietà degli elementi.
- Materia ed energia devono seguire regole esplicite e verificabili.
- Le simulazioni devono essere riproducibili mediante seed.
- Ogni risultato deve essere distinguibile da un artefatto numerico o implementativo.
- I controlli positivi con replicatori noti, quando saranno introdotti in M5, devono rimanere completamente isolati dall'universo sperimentale.

Non modificare arbitrariamente le regole per ottenere comportamenti apparentemente biologici.

## 3. Architettura software

Target iniziale: macOS Apple Silicon M4, con compatibilità Linux.

Stack preferito:

- Python 3.12
- NumPy per rappresentazione e operazioni numeriche
- pytest per test automatici
- JSON per configurazione degli esperimenti
- CSV/JSON per output e metriche
- matplotlib per analisi successive
- Numba o C++ soltanto dopo profiling e approvazione

Architettura modulare proposta:

```text
alife/
├── pyproject.toml
├── README.md
├── SPEC.md
├── configs/
│   └── baseline.json
├── src/
│   └── alife/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── world.py
│       ├── particles.py
│       ├── dynamics.py
│       ├── rng.py
│       ├── persistence.py
│       └── metrics.py
├── tests/
│   ├── test_dynamics.py
│   ├── test_invariants.py
│   ├── test_reproducibility.py
│   └── test_checkpoint.py
└── runs/
```

La struttura può essere adattata se esiste una motivazione tecnica, purché la separazione delle responsabilità rimanga chiara.

Il motore deve essere utilizzabile senza interfaccia grafica.

La visualizzazione, quando introdotta, sarà un componente separato.

## 4. Modello computazionale iniziale

Definire un universo bidimensionale discreto.

Configurazione baseline:

- Griglia 128 × 128.
- Condizioni al contorno periodiche, configurabili.
- Celle vuote e particelle con tipologie differenti.
- Fino a sei specie iniziali configurabili.
- Occupazione massima di una particella per cella nel primo prototipo.
- Movimento locale verso celle adiacenti.
- Aggiornamenti deterministici dato uno stato iniziale e un seed.
- Evoluzione in passi temporali discreti.

In M1 non devono ancora essere presenti reazioni chimiche, catalisi o replicazione.

Utilizza uno schema di aggiornamento che gestisca esplicitamente i conflitti di movimento ed eviti dipendenze accidentali dall'ordine di scansione della griglia.

Le scelte relative a movimento, vicinato, aggiornamento e trattamento dell'energia devono essere documentate in `SPEC.md`.

## 5. Roadmap generale

| Fase | Obiettivo |
|---|---|
| M0 | Specifiche scientifiche e protocollo |
| M1 | Motore fisico locale riproducibile |
| M2 | Chimica artificiale e legami reversibili |
| M3 | Flussi energetici e non-equilibrio |
| M4 | Rilevamento di strutture persistenti |
| M5 | Validazione attraverso controlli |
| M6 | Campagne evolutive multi-seed |
| M7 | Verifica di replicazione ed ereditarietà |
| M8 | Studio dell'individualità funzionale |
| M9 | Ottimizzazione e simulazioni estese |

**Non implementare l'intera roadmap.**

Procedi progressivamente e attendi l'approvazione prima di passare alla milestone successiva.

## 6. ATTIVITÀ DA ESEGUIRE ORA — M0 e M1

### M0 — Specifiche scientifiche

Prima di implementare il motore:

1. Esamina il workspace esistente.
2. Definisci le caratteristiche dello stato dell'universo.
3. Specifica la rappresentazione delle particelle.
4. Definisci il modello temporale e le regole di movimento.
5. Documenta il funzionamento del generatore casuale.
6. Definisci le invarianti fisiche e computazionali.
7. Definisci il trattamento dell'energia nel prototipo chiuso, senza introdurre ancora sorgenti e pozzi.
8. Stabilisci il formato dei file di configurazione e checkpoint.
9. Documenta le limitazioni del modello.

Produci `SPEC.md` con una specifica sufficientemente dettagliata da consentire un'implementazione indipendente.

Se emergono contraddizioni nelle specifiche, segnalale prima di procedere.

### M1 — Implementazione del motore

Realizza il primo motore headless.

Funzioni obbligatorie:

**A. Inizializzazione**

Creazione dell'universo a partire da un file JSON, con posizionamento iniziale riproducibile delle particelle.

**B. Evoluzione**

Avanzamento della simulazione per N passi mediante interazioni locali, senza reazioni o replicazione.

**C. Stato**

Rappresentazione efficiente dello stato, dell'occupazione, delle specie e delle eventuali proprietà energetiche.

**D. Riproducibilità**

Il medesimo stato iniziale, seed e configurazione devono produrre gli stessi risultati nello stesso ambiente software.

**E. Persistenza**

Salvataggio e caricamento degli stati, compreso lo stato del generatore casuale, così da poter riprendere una simulazione senza alterarne l'evoluzione.

**F. Metriche**

Registrazione almeno di:

- Passi eseguiti.
- Numero di particelle per specie.
- Numero di spostamenti.
- Occupazione della griglia.
- Bilancio energetico definito dalla specifica.
- Tempo di esecuzione.
- Memoria utilizzata.
- Hash dello stato finale.
- Seed e versione della configurazione.

**G. CLI**

Prevedi comandi equivalenti a:

```bash
alife run --config configs/baseline.json \
  --steps 10000 --out runs/baseline

alife resume --checkpoint runs/baseline/checkpoint.json \
  --steps 5000
```

Puoi adottare un formato di checkpoint diverso se necessario per rappresentare correttamente stato e RNG; documenta il comando effettivo.

## 7. Test obbligatori

Utilizza pytest.

Verifica almeno:

1. Conservazione del numero di particelle in assenza di regole di creazione e distruzione.
2. Conservazione della quantità di ciascuna specie.
3. Assenza di occupazione multipla delle celle.
4. Rispetto dei confini configurati.
5. Riproducibilità con identico seed.
6. Integrità del salvataggio e caricamento.
7. Equivalenza tra esecuzione continua ed esecuzione interrotta e ripresa.
8. Rilevamento di una violazione intenzionale delle invarianti.

Non limitarti a scrivere i test: eseguili e riportane i risultati reali.

## 8. Performance

Il prototipo deve funzionare su un normale computer personale.

Non ottimizzare prematuramente.

Registra:

- Passi al secondo.
- Tempo totale.
- Picco della memoria.
- Numero di particelle simulate.

Esegui almeno un benchmark con la configurazione baseline.

Non dichiarare un livello di performance senza averlo misurato.

## 9. Regole di sviluppo

Lavora autonomamente sulle attività autorizzate.

- Preferisci codice semplice, leggibile, tipizzato dove utile e testabile.
- Non introdurre framework complessi se non necessari.
- Mantieni il core indipendente dalla visualizzazione.
- Evita dipendenze superflue.
- Non effettuare modifiche a file esterni al progetto.
- Non pubblicare repository o dati su servizi esterni.
- Non proseguire verso M2 senza esplicita approvazione.
- Non presentare come sperimentali risultati inventati.
- Se un comando non può essere eseguito, dichiaralo e non fingere che sia stato verificato.
- Documenta assunzioni, decisioni tecniche e limitazioni.

Se una decisione tecnica minore non è specificata, scegli una soluzione ragionevole e documentala, senza interrompere continuamente il lavoro.

## 10. Consegna finale

Al termine di M1 produci:

1. Repository eseguibile.
2. `SPEC.md` completo.
3. `README.md` con installazione e comandi.
4. File di configurazione baseline.
5. Suite di test.
6. Esempio reale di simulazione.
7. Report delle performance misurate.
8. Resoconto delle scelte progettuali.
9. Elenco dei problemi ancora aperti.

Concludi con un report sintetico:

**M0:** GO / REVISE / STOP

**M1:** GO / REVISE / STOP

Per ogni decisione indica le evidenze che la giustificano e gli eventuali test non superati.

### Istruzione finale

**Inizia ora.**

Analizza il workspace, definisci M0, implementa M1, esegui i test e produci il report finale.

Fermati dopo M1, anche se tutti i test sono superati.

Non implementare ancora chimica, reti neurali, organismi, replicazione, ereditarietà o visualizzazione grafica.
