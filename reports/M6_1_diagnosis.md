# M6.1 — Diagnosi della capacità evolutiva

Data: 2026-11-15 · Stato: milestone diagnostica · Nessuna legge del motore modificata
· Artefatti: `campaigns/diagnostics/m6_1/diagnostics.json`,
`tools/diagnose_m6_1.py`

## 0. Metodo e perimetro

L'audit esamina il codice effettivamente usato in M6 (`src/alife`, schema 3) e le
25 configurazioni preregistrate. Le misure diagnostiche usano **solo regole
esistenti**: censimento delle topologie dai checkpoint M6, una prova con
catalisi attiva (parametro già implementato, spento in M6), una prova di
autocatalisi di specie e una prova di auto-catalisi con una sola specie.

Nessun file di M0–M6 è stato modificato: configurazioni, seed, report e
risultati restano quelli pubblicati. Il motore non è stato toccato; gli
artefatti nuovi stanno in `campaigns/diagnostics/m6_1/`.

Avvertenza metodologica: **una limitazione del rilevatore non è una limitazione
delle leggi fisiche**. Il report le tiene separate in ogni sezione.

---

## 1. Stato effettivo della chimica

### 1.1 Regole in vigore (schema 3)

| Fase | Regola |
|---|---|
| Dissipazione | `num` quanti ogni `den` passi, sfasati per ID, su particelle e legami |
| Iniezione | 9 sorgenti puntiformi, accumulatore intero, serbatoio di capacità 30 |
| Rottura | probabilità per legame e per passo |
| Movimento | solo particelle con grado 0; 2 estrazioni RNG per particella |
| Formazione | coppia ammessa, adiacenza, `max_bonds`, energia sufficiente, estrazione |
| Catalisi | un vicino di specie catalizzatrice moltiplica la probabilità della coppia |
| Energia | `bond_cost` immagazzinato, attrito di formazione/rottura, ledger esatto |

Non esistono: cambio di specie, trasformazione di proprietà, legami orientati,
reazioni a più corpi, template, memoria strutturale.

### 1.2 Configurazioni M6

Chimica identica in tutte le condizioni: 4 specie, `max_bonds` 2/2/1/0, coppie
ammesse `S0-S0`, `S0-S1`, `S1-S1`, `S1-S2`, `formation_probability = 0.05`,
`break_probability = 0.002`, catalisi **vuota**. Cambiano solo sorgenti, costi e
decadimento (5 condizioni, 5 seed, 3 000 passi).

---

## 2. Matrice delle capacità e dei vincoli

| # | Punto | Possibile e implementato | Possibile ma disabilitato | Impossibile con le regole attuali | Non determinabile senza esperimenti |
|---|---|---|---|---|---|
| 1 | Mobilità molecolare | movimento delle particelle libere | — | movimento di particelle legate: nessuna fase lo prevede | effetto quantitativo di aggregati mobili su incontri ed energia |
| 2 | Valenze e topologie | catene e anelli pari; `max_bonds` 0–4 nel motore | ramificazioni (`max_bonds` 3–4) mai usate in M6 | cicli dispari (griglia bipartita); gradi oltre `max_bonds` | varietà topologica con valenze maggiori |
| 3 | Catalisi | regola generale `(specie, coppia, fattore)` | spenta in tutte le configurazioni M6 | catalisi che dipende dalla **forma** di una struttura | entità dell'effetto in altri regimi |
| 4 | Trasformazioni | — | — | cambio di specie o proprietà | — |
| 5 | Energia | sorgenti con serbatoio, decadimento, costi, ledger | tassi e posizioni alternativi | mantenere aggregati **mobili** (non esistono) | sostenibilità di strutture dinamiche |
| 6 | Informazione | composizione trasmessa per frammentazione (particelle condivise) | catalisi di specie che accelera motifs locali | trasmissione della **topologia**; memoria strutturale | — |
| 7 | Rilevamento | nascite complete (≥ 4 particelle) vicine a una struttura simile | — | copie che si formano per accrezione, con il rilevatore attuale | — |

### 2.1 Mobilità

Le particelle legate non propongono mosse (`_propose_moves` salta `degree > 0`) e
il test `test_bonded_particles_do_not_move` lo verifica. Conseguenze:

- due aggregati non possono incontrarsi: possono solo crescere per aggiunta di
  monomeri o rompersi;
- un aggregato non può raggiungere una sorgente: solo la particella che si trova
  già sulla cella della sorgente riceve energia;
- i dati M6 lo riflettono: `closed` (senza costi) ha 284 strutture mediane,
  `fed-*` 150–156; l'energia iniettata cresce ma quella non assorbita cresce di
  più (15,7k → 84k passando da 1 a 4 quanti/passo).

### 2.2 Valenze e topologie

Censimento sui 25 checkpoint finali:

| Condizione | Strutture (mediana) | Dimensione max (mediana) | Componenti cicliche | Grado max |
|---|---|---|---|---|
| `closed` | 284 | 10 | 106 | 2 |
| `unfed` | 129 | 4 | 0 | 2 |
| `fed-low` | 156 | 4 | 3 | 2 |
| `fed-mid` | 150 | 6 | 0 | 2 |
| `fed-high` | 150 | 5 | 1 | 2 |

- **Grado massimo 2 in tutte le condizioni**: con `max_bonds ≤ 2` sono possibili
  solo catene e anelli. Nessuna ramificazione, nessun reticolo, nessuna
  struttura con giunzioni.
- La griglia è bipartita: **i cicli dispari sono geometricamente impossibili**.
  Gli anelli osservati sono pari (4, 6, …).
- Il motore supporta `max_bonds` fino a 4: le ramificazioni sono possibili ma
  mai state attivate. Non è un limite del codice, è una scelta di configurazione.
- Gli anelli compaiono soprattutto nel `closed` (106 componenti su 5 run), quasi
  assenti nelle condizioni con costi: la chiusura di un anello richiede che due
  estremi si incontrino e restino legati abbastanza a lungo.

### 2.3 Catalisi

La regola esiste ed è generale: una particella di specie `C` adiacente alla
coppia moltiplica la probabilità di formazione. Non dipende dalla forma della
struttura a cui appartiene `C`. In M6 è vuota in tutte le condizioni.

Prova diagnostica (fed-mid, 1 500 passi, fattore 1000 su `S0-S1`):

| | Strutture | Nascite | Dimensione max | Candidate |
|---|---|---|---|---|
| senza catalisi | 283 | 686 | 7 | 0 |
| con catalisi | 292 | 651 | 8 | 0 |

L'effetto è **+3% di strutture**, con meno nascite: la catalisi cambia la
cinetica locale, non produce copie. Coerente con il vincolo di slot e spazio già
osservato in M3.

### 2.4 Trasformazioni

Nessuna regola modifica la specie di una particella. I conteggi per specie sono
un invariante (`I2`). Sono quindi vietati: reazioni `A + B → C`, isomerizzazioni,
cambio di valenza, degradazione, modifiche ereditarie. Qualsiasi forma di
memoria genetica che richieda un cambiamento di stato chimico è fuori portata.

### 2.5 Energia

Il meccanismo è coerente e verifica l'identità a ogni passo. Il limite è
spaziale: le sorgenti sono 9 celle su 16 384 e solo la particella presente
assorbe. Gli aggregati sono immobili, quindi non si ricaricano.

| Condizione | Iniettata (mediana) | Dissipata (mediana) | Non assorbita (mediana) |
|---|---|---|---|
| `unfed` | 0 | 9 785 | 0 |
| `fed-low` | 27 000 | 10 072 | 15 677 |
| `fed-mid` | 54 000 | 10 182 | 38 680 |
| `fed-high` | 108 000 | 10 021 | 83 992 |

Il sistema è aperto e dissipativo, ma la frazione utile di energia **diminuisce**
con il tasso: il collo di bottiglia è l'accesso, non la disponibilità.

### 2.6 Informazione

Una configurazione può influenzare un'altra solo attraverso:

1. **occupazione dello spazio** (volume escluso): una struttura lineare offre
   una superficie lineare;
2. **specie dei vicini** (catalisi): una particella catalizzatrice accelera una
   coppia, indipendentemente da come è disposta;
3. **energia consumata**.

Nessuna regola legge la disposizione dei vicini. Quindi la **topologia** del
genitore non è un'informazione trasmissibile: al massimo la sua geometria
esclude celle. La composizione, invece, si conserva banalmente per
frammentazione (le particelle sono le stesse), ma non è una copia: non nasce una
struttura nuova con proprietà determinate dal genitore.

### 2.7 Rilevamento

Il rilevatore M5 richiede una **nascita** di una struttura completa (≥ 4
particelle) entro 2 celle da una struttura con la stessa firma, che persista 10
passi. Le nascite osservate in M6 sono quasi tutte dimeri:

| Condizione | Nascite di dimensione 2 | 3 | ≥ 4 |
|---|---|---|---|
| `closed` | 4 705 | 14 | 0 |
| `unfed` | 4 853 | 12 | 0 |
| `fed-low` | 4 956 | 14 | 0 |
| `fed-mid` | 4 917 | 13 | 0 |
| `fed-high` | 5 008 | 13 | 0 |

**Zero nascite ≥ 4 in 25 run.** Lo zero del rilevatore è quindi atteso per
costruzione: nell'universo attuale una struttura nasce dimerica e cresce per
accrezione. Un replicatore che si assemblasse gradualmente sarebbe invisibile a
questo criterio. Questa è una limitazione del **rilevatore**, non una prova che
la replicazione non avvenga.

---

## 3. La replicazione è possibile con le regole attuali?

### 3.1 Argomento

Per replicare una struttura A in una struttura A′ distinta, qualche regola deve
far dipendere la probabilità di formare A′ dalla **configurazione** di A. Le
regole attuali fanno dipendere la probabilità di un legame solo da:

- specie della coppia,
- adiacenza,
- `max_bonds` e energia,
- specie di un eventuale catalizzatore adiacente.

Nessun termine contiene la disposizione di A. Di conseguenza:

- **Impossibile dimostrata**: la trasmissione fedele di una topologia. Due
  strutture con la stessa composizione ma topologia diversa non possono
  influenzare una figlia in modo diverso, se non per il volume occupato.
- **Possibile ma non implementata**: un templating geometrico, in cui la
  superficie di A biasima *dove* si formano i legami. Produrrebbe al più una
  figlia con forma simile per vincolo spaziale, non con lunghezza o ramificazioni
  determinate da A.
- **Possibile e dimostrata**: l'autocatalisi di **specie**. Nella prova A-B con
  catalizzatore A (fattore 1000), i legami passano da 53 a 135 in 2 000 passi:
  il prodotto contiene la specie che catalizza, quindi la velocità cresce con il
  prodotto. È autocatalisi chimica, non replicazione strutturale.
- **Assenza di evidenza**: nessuna copia candidata in M6. Coerente con
  l'impossibilità dimostrata, ma anche con il fatto che il rilevatore non
  vedrebbe copie per accrezione.

### 3.2 Caso minimo sperimentale

Il caso più vicino consentito dalle regole è la **produzione autocatalitica di
legami**:

1. specie A e B, coppia ammessa A-B, catalisi di A sulla coppia;
2. il prodotto A-B contiene A, che continua a catalizzare;
3. la velocità di formazione cresce con il prodotto (misurato: 53 → 135).

Non soddisfa i criteri di replicazione:

- non produce una struttura nuova con la stessa topologia del "genitore";
- non c'è un genitore strutturale: A è una specie, non una configurazione;
- la crescita satura per esaurimento dei substrati e dello spazio.

Una prova con una sola specie auto-catalitica (A catalizza A-A, formazione 0.01)
ha prodotto 2 nascite di dimensione 4 su 2 000 passi, ma **0 candidate**: le
nascite complete non erano vicine a strutture con la stessa firma. È il tipo di
evento raro che una campagna futura deve sorvegliare come possibile falso
positivo.

### 3.3 Conclusione della fase 2

| Affermazione | Stato |
|---|---|
| Replicazione strutturale con le leggi attuali | **impossibile** (nessuna regola legge la topologia) |
| Templating geometrico debole | possibile in linea di principio, non implementato, non fedele |
| Autocatalisi di specie | possibile e dimostrata con catalisi attiva |
| Copie candidate in M6 | assenti; il rilevatore non vedrebbe copie per accrezione |
| Ereditarietà | impossibile senza trasformazioni o memoria strutturale |
| Evoluzione darwiniana | impossibile: mancano variazione ereditabile e successo differenziale |

Il limite non è (solo) nel rilevatore: **mancano le leggi che potrebbero
trasmettere informazione strutturale**. Il rilevatore è cieco a un'unica classe
di meccanismi (accrezione), ma anche correggendolo non troverebbe nulla, perché
la fisica non consente la copia.

---

## 4. Esperimenti diagnostici eseguiti

Tutti senza modificare il motore; configurazioni e hash in
`campaigns/diagnostics/m6_1/diagnostics.json`.

| Prova | Configurazione | Passi | Risultato |
|---|---|---|---|
| Censimento topologie | 25 checkpoint M6 | — | grado max 2; cicli solo pari; 0 nascite ≥ 4 |
| Catalisi attiva | fed-mid + `S3` catalizza `S0-S1` (fattore 1000) | 1 500 | +3% strutture, 0 candidate |
| Autocatalisi A-B | catalizzatore A, fattore 1000, formazione 0.002 | 2 000 | legami 53 → 135 |
| Auto-catalisi A-A | una specie, catalisi A su A-A, formazione 0.01 | 2 000 | 2 nascite di dimensione 4, 0 candidate |

---

## 5. Proposte di modifica

Valutate separatamente. Priorità e dipendenze alla fine della sezione.

### A. Movimento coordinato degli aggregati

| Voce | Contenuto |
|---|---|
| **Software** | nuova fase di movimento per componenti: proposta di traslazione rigida per l'intero aggregato, risoluzione dei conflitti a livello di componente, 1–2 estrazioni per componente in ordine di ID minimo, flag di configurazione `aggregate_motion` (schema 4 se cambia il flusso RNG) |
| **Motivazione** | oggi le strutture non possono incontrarsi né raggiungere le sorgenti; è il vincolo più forte emerso in M3 e M6 |
| **Effetti attesi** | più incontri, più fusioni/scissioni, accesso all'energia; **non** replicazione |
| **Artefatti** | aggregati rigidi che "spazzano" il reticolo; jamming; fusione per collisione non mediata dalla chimica; statistica dei conflitti diversa |
| **Costo** | O(componenti × dimensione) proposte; risoluzione più complessa; attesa 2–3× |
| **Test** | invarianti di occupazione e legami, identità energetica, determinismo (budget RNG per componente), golden hash M1–M6 invariati con flag off, ripresa equivalente |
| **Confronto M6** | stessa matrice 5×5×3 000 passi con flag on/off; delta su strutture, vite, fusioni, energia assorbita |

### B. Catalisi locale generale attiva

| Voce | Contenuto |
|---|---|
| **Software** | nessuna modifica al motore: solo configurazione. Versionare la regola scelta (specie, coppia, fattore) e l'hash |
| **Motivazione** | è l'unico meccanismo di feedback già presente; l'autocatalisi di specie è dimostrata |
| **Effetti attesi** | cinetica locale più rapida, possibili motifs autocatalitici; nessuna garanzia di copia |
| **Artefatti** | la specie catalizzatrice è anche abbondante: l'effetto può ridursi a un boost di densità; possibili falsi positivi del rilevatore su assemblaggi a raffica |
| **Costo** | trascurabile (implementata) |
| **Test** | identità energetica, determinismo, catena catalisi on/off/shuffled, M5 positivo e negativi ancora validi |
| **Confronto M6** | fed-mid con catalisi spenta/attiva, stessi seed; delta su strutture, nascite per dimensione, candidate |

### C. Ampliamento delle valenze e delle topologie

| Voce | Contenuto |
|---|---|
| **Software** | solo configurazione (`max_bonds` 3–4, nuove coppie). Attenzione: il tracciamento firma gli alberi in O(n²); con aggregati grandi serve un limite o una cache |
| **Motivazione** | con grado ≤ 2 sono possibili solo catene e anelli; senza ramificazioni non esistono reticoli né strutture compartimentate |
| **Effetti attesi** | aggregati più grandi e ramificati, possibile percolazione; **non** informazione |
| **Artefatti** | gelificazione rapida, immobilismo totale, firme fuzzy per i cicli, ambiguità in aumento |
| **Costo** | più legami e componenti più grandi; firme e tracking più costosi |
| **Test** | invarianti, energia, determinismo; esattezza delle firme ad albero; golden hash invariati con `max_bonds` invariato |
| **Confronto M6** | `max_bonds` 2 vs 3 vs 4, stessi seed; delta su dimensione, cicli, ambiguità |

### D. Trasformazione delle specie

| Voce | Contenuto |
|---|---|
| **Software** | tabella di reazioni locali (coppie/triple) con costo energetico e reversibilità; schema 4; invarianti nuovi (particelle conservate, specie no); checkpoint e metriche aggiornati; eventi di reazione |
| **Motivazione** | senza trasformazioni non esiste variazione ereditaria: la composizione iniziale è tutto ciò che c'è |
| **Effetti attesi** | cicli catalitici, motifs convertibili, possibile memoria chimica; nessuna garanzia |
| **Artefatti** | violazione degli invarianti attuali (I2); rischio di creare energia se i costi non sono esatti; rischio di regole che codificano strutture specifiche |
| **Costo** | scansione locale per passo, più eventi, migrazione dello schema |
| **Test** | conservazione delle particelle, identità energetica, determinismo, chiusura dei cicli di reazione, nessuna creazione oltre le regole |
| **Confronto M6** | matrice M6 più insiemi di reazioni; distribuzioni di specie, cicli, persistenza |

### E. Rilevamento di copie progressive

| Voce | Contenuto |
|---|---|
| **Software** | rilevatore v2 versionato: candidato = nuovo aggregato che **cresce** vicino a un template e ne acquisisce la firma entro N passi, senza particelle condivise; metriche di similarità e incertezza |
| **Motivazione** | in M6 il 99% delle nascite è dimerico: un replicatore per accrezione sarebbe invisibile |
| **Effetti attesi** | più candidate, inclusi falsi positivi da crescita ordinaria |
| **Artefatti** | rischio di chiamare copia ogni crescita; dipendenza da soglie; ambiguità delle firme fuzzy |
| **Costo** | matching per passo e confronto di firme; analisi-only, nessun costo sul motore |
| **Test** | M5 positivo riconosciuto e negativi rifiutati; fixture di assemblaggio progressivo; determinismo; ri-analisi dei run M6 esistenti senza rieseguirli |
| **Confronto M6** | stessa analisi sui 25 run salvati, con rilevatore v1 e v2 affiancati |

### Priorità e dipendenze

| Ordine | Proposta | Dipende da | Motivo |
|---|---|---|---|
| 1 | **E** rilevatore v2 | — | elimina un punto cieco noto; si applica ai run M6 già salvati senza rieseguire |
| 2 | **B** catalisi attiva | E (per interpretare) | costo quasi nullo, testa il feedback già presente |
| 3 | **A** movimento aggregati | B, E | il vincolo più forte; richiede nuove collisioni |
| 4 | **C** valenze 3–4 | A, B | più significativo quando gli aggregati possono incontrarsi |
| 5 | **D** trasformazioni | A–C | cambia gli invarianti; da ultimo, con schema 4 |

Nessuna proposta è giustificata dall'obiettivo di "aumentare gli aggregati". La
metrica è la capacità di sostenere trasformazioni informative causalmente
significative.

---

## 6. Protocollo di validazione della nuova versione

### 6.1 Principi

- una modifica per volta, con manifest preregistrato e hash delle configurazioni;
- stessi seed della campagna M6 (`6101–6105`) per il confronto appaiato;
- stessi 3 000 passi; stessi rilevatori e metriche, salvo la versione esplicita;
- nessuna metrica ridefinita in silenzio: ogni nuova metrica ha una versione.

### 6.2 Livelli di evidenza (non cumulativi)

| Livello | Definizione operativa | Evidenza minima | Non implica |
|---|---|---|---|
| **L1 Aggregazione** | strutture connesse presenti | ≥ 1 struttura persistente per run, distribuzione misurata | persistenza |
| **L2 Persistenza** | strutture che sopravvivono | vita mediana ≥ 100 passi e coda > 500 in ≥ 3/5 seed | autocatalisi |
| **L3 Autocatalisi** | la formazione del prodotto cresce con il prodotto | tasso di formazione in funzione del prodotto, con controllo shuffled e Δ significativo | replicazione |
| **L4 Replicazione** | copie persistenti senza particelle condivise, vicine a un template | rilevatore v2 positivo in ≥ 3/5 seed e in run indipendenti | ereditarietà |
| **L5 Ereditarietà** | le copie conservano una firma misurabile con variazione | fedeltà > controllo, variazione tra generazioni | evoluzione |
| **L6 Evoluzione** | successo riproduttivo differenziale correlato a un tratto ereditabile | esperimento di selezione con ambiente cambiato, replicato | coscienza o "vita" |

Nessun livello si deduce dal precedente: L2 non prova L3, L4 non prova L5, L5 non
prova L6.

### 6.3 Campagne previste (una alla volta)

| Campagna | Modifica | Controlli | Criterio di GO |
|---|---|---|---|
| `m6.2-E` | rilevatore v2, ri-analisi dei 25 run M6 | v1 affiancato; M5 positivo/negativi | v2 riconosce il positivo M5 e non altera la classificazione dei negativi; sui run M6 riporta candidate solo se soddisfano il criterio |
| `m6.2-B` | catalisi attiva (una coppia, un fattore) | off, shuffled, fattore basso | L3 raggiunto; L4 solo con copie persistenti |
| `m6.2-A` | movimento aggregati | flag off; M6 invariato | L1–L2 invariati o migliorati, nessuna violazione; eventuali L3/L4 misurati |
| `m6.2-C` | `max_bonds` 3 | `max_bonds` 2 | strutture ramificate misurate; nessun crollo di stabilità |
| `m6.2-D` | trasformazioni (schema 4) | nessuna trasformazione | conservazione delle particelle, energia, determinismo; nuovi livelli misurati |

Durata: 3 000 passi per confronto diretto con M6; eventuale estensione solo dopo
un risultato positivo a 3 000, con nuovo manifest.

### 6.4 Criteri di verifica e confronto

- **Appaiato**: stessi seed, stessa durata, stesse metriche; delta e intervallo.
- **Controllo negativo obbligatorio** per ogni campagna: la versione precedente
  con lo stesso seed.
- **Nessuna conclusione da un solo seed**; riportare anche i run nulli.
- **Confronto con M6** tramite `campaigns/m6/results.json` e, per E, ri-analisi
  dei run salvati senza rieseguire la simulazione.

---

## 7. Rischi scientifici e computazionali

### Scientifici

1. **Falsi positivi per assemblaggio a raffica**: la prova A-A ha prodotto
   nascite di dimensione 4; con catalisi forte il rilevatore potrebbe scattare su
   eventi non ereditari. Servono controlli shuffled e la versione v2 con
   discendenza.
2. **Confondimento densità/catalisi**: una specie catalizzatrice abbondante
   aumenta la densità locale; l'effetto va separato con catalizzatori inerti.
3. **Vincolo di configurazione scambiato per vincolo fisico**: `max_bonds` 2 in
   M6 non significa che il motore non possa ramificare.
4. **Metriche che cambiano significato** (es. "struttura" con valenze maggiori):
   ogni modifica va versionata, non ridefinita.
5. **Pressione al risultato**: la diagnosi mostra che la fisica attuale non può
   replicare; aggiungere leggi finché compare una copia è il rischio principale.
   Il protocollo preregistrato è la difesa.

### Computazionali

1. **Tracking**: già −45% di passi/s end-to-end in M4; aggregati più grandi
   peggiorano firme e union-find.
2. **Firme**: il codice AHU è O(n²) per struttura; con reticoli grandi serve un
   limite o una cache. Le firme fuzzy restano ambigue.
3. **Movimento di aggregati**: collisioni a livello di componente e nuovi
   conflitti; rischio di esplosione combinatoria.
4. **Trasformazioni**: nuovo schema di checkpoint (4), migrazione, più eventi e
   più spazio su disco.
5. **Campagne**: 25 run × 3 000 passi ≈ 15 minuti per variante; con tracking e
   valenze maggiori può raddoppiare.

---

## 8. Raccomandazione finale

**REVISE.**

Motivazione, in ordine di evidenza:

1. **Impossibilità dimostrata**: con le leggi attuali nessuna regola legge la
   topologia di una struttura; la trasmissione fedele di una configurazione è
   esclusa per costruzione, non per mancanza di osservazioni.
2. **Limite del rilevatore distinto**: lo zero di M6 è atteso anche perché il 99%
   delle nascite è dimerico; il rilevatore non vede l'accrezione. Questo va
   corretto (E) prima di interpretare qualsiasi campagna futura.
3. **Leve disponibili, in ordine**: rilevatore v2 (analisi, nessun rischio
   fisico) → catalisi attiva (configurazione) → movimento degli aggregati (il
   vincolo più forte) → valenze → trasformazioni.
4. **Nessun GO a M7**: non ci sono le condizioni per la replicazione; procedere
   ora significherebbe cercare un risultato con strumenti che non possono
   trovarlo.
5. **Nessuno STOP**: la piattaforma è solida, deterministica e misurabile; la
   diagnosi indica modifiche concrete e verificabili.

Prossimo passo proposto: **M6.2-E** (rilevatore v2, ri-analisi dei run M6 senza
modificare la simulazione), poi **M6.2-B** (catalisi attiva). Entrambi non
toccano le leggi del motore e possono essere preregistrati subito. Il movimento
degli aggregati (A) è la prima modifica alle leggi e richiede approvazione
esplicita.

---

### Appendice — Come riprodurre la diagnosi

```bash
.venv/bin/python tools/diagnose_m6_1.py
```

Genera `campaigns/diagnostics/m6_1/diagnostics.json` leggendo i 25 checkpoint M6,
i registri di lineage e quattro prove isolate. Non modifica configurazioni,
seed o risultati di M0–M6 e non altera il motore.
