# ALIFE — M6.3: capacità fisiche per la trasmissione di informazione

**Stato:** proposta scientifica **solo progettuale**, non autorizzazione a implementare.  
**Data:** 15 novembre 2026 · **Origine:** [issue #4](https://github.com/kkongiu/alife-lab/issues/4) e [addendum scientifico proposto nella PR #5](https://github.com/kkongiu/alife-lab/pull/5).  
**Compatibilità:** questo file parte dal `master` M6.2-E; le PR #1–#8 sono revisioni **non assunte come già integrate**. La validazione dei nuovi osservatori e la revisione causale rimangono requisiti distinti.

> **Domanda:** sotto le regole locali attuali, può una variante di una struttura
> influenzare specificamente la variante costruita altrove, oltre alla semplice
> variazione del numero di incontri, della posizione e della composizione
> ambientale? Come riconoscere questo fenomeno senza inserirvi un replicatore
> precostituito?

**Non si modificheranno** `src/`, `configs/`, `tests/`, `campaigns/`,
`SPEC.md`, `replication_v2.py`, `replication_v21.py` né hash e risultati
storici in questa PR. Nessuna legge, seme, soglia o detector viene cambiato.

## 1. Fatti verificabili, inferenze e limiti del modello

Fonti implementative: [SPEC.md](../SPEC.md) §§2–9,
`src/alife/chemistry.py`, `src/alife/dynamics.py`,
`src/alife/structures.py`, [diagnosi M6.1](../reports/M6_1_diagnosis.md),
[ri-analisi M6.2-E](../reports/M6_2E_detector.md).

| Aspetto | Fatto nel motore | Implicazione da sottoporre a prova |
|---|---|---|
| Particelle | Specie fissa, posizione, energia intera e grado di legame; **nessuno stato chimico interno variabile** | La memoria di una variante risiede nella disposizione delle specie e dei legami, non in stati interni trasmissibili |
| Legami | Legami adiacenti, reversibili; in M6 la valenza massima è 2 per S0/S1, 1 per S2, 0 per S3 | Solo catene e anelli; nessuna ramificazione, ma **le catene possono avere sequenze di specie differenti** |
| Formazione legami | Coppia di specie, energia, slot di valenza, vicinato e possibile catalizzatore per **specie** | Non legge esplicitamente una firma di aggregato; la geometria può comunque variare **accessibilità e frequenza di contatto** |
| Movimento | Ogni particella legata è immobile; i componenti non traslano come interi | Diminuisce la possibilità di incontro/trasporto di un aggregato; non dimostra da sola l'impossibilità di trasmettere informazione |
| Catalisi | Il fattore dipende da una specie vicina, **non** da una sequenza o stato del legame | M6.2-B aumenta la frequenza dei legami, ma non documenta copia o ereditarietà |
| RNG | Flusso sequenziale PCG64, con numero di estrazioni dipendente dalle reazioni candidate | Interventi anche lontani possono alterare le estrazioni per passi successivi: gli esiti finali non isolano automaticamente una causa locale |
| Identità strutturale | Tracker fondato su particelle condivise; detector v2/v2.1 su prossimità e firme | Né continuità materiale né match geometrico equivalgono a una discendenza riproduttiva causale |

**Correzione epistemica importante.** Dalle regole non segue una dimostrazione
generale che ogni trasmissione strutturale sia *matematicamente impossibile*.
La forma del genitore non è una variabile esplicita nella probabilità di
reazione, ma la forma **modifica l'occupazione delle celle, l'accessibilità
delle superfici e la probabilità di incontri futuri**. Un processo di
templating geometrico indiretto non può essere escluso solo leggendo la
formula della catalisi. Serve distinguerlo dalla semplice ricorrenza.

**Evidenza empirica:** i 25 run M6 riletti con v2 producono 1.051 candidate,
un match persistente e zero catene di seconda generazione. Il tracciamento
P1/P2 (PR #6–#8) dimostra che il caso `unfed-6101` ha un precursore comune
materiale e che i controfattuali su condizioni iniziali alterano anche gli
sham. La PR #8 registra inoltre un controllo contaminato da un ID della
futura struttura figlia. Il verdetto resta **replicazione causale non provata**.

## 2. Che cosa conta come trasmissione di informazione

Per la milestone di **capacità** distinguere quattro livelli:

1. **Persistenza:** una struttura conserva la propria variante nel tempo.
2. **Dipendenza statistica:** la variante di una struttura di destinazione
   è predetta meglio conoscendo quella della struttura sorgente, dopo
   stratificazione per composizione, condizioni ambientali e geometria.
3. **Dipendenza causale locale:** un intervento sulla variante sorgente,
   definito e controllato *prima* del risultato, cambia in maniera
   specifica la distribuzione delle varianti di destinazione rispetto
   agli sham pertinenti; sono tracciati interventi, eventi chimici e
   divergenze casuali.
4. **Ereditarietà riproduttiva:** compaiono **più strutture figlie materialmente
   distinte**, con almeno due generazioni **causalmente sostenute**,
   e passaggio ripetibile di **almeno due varianti non banali**, inclusa
   la possibilità di varianti mutate.

Nessuno dei livelli 1–3 autorizza l'etichetta `organismo`.
**Definizione preliminare di variante:** firma *esatta* di albero
con sequenza di specie non omogenea, identità dei componenti tracciata,
confronto rispetto a frequenza di fondo e controlli shuffled.
Dove la firma è ambigua, classificare `ambiguous` e **non** contare
una copia come confermata.

Un possibile test di potere discriminante usa due **catene da quattro**
con identica composizione `2×S0 + 2×S1`, ma ordinamenti differenti:
`S0–S1–S0–S1` e `S0–S0–S1–S1`. Entrambe rispettano le coppie di
legame M6; non sono equivalenti per inversione e sono distinguibili
dalla firma esatta. Sono **sonde sintetiche assemblate per diagnosi**:
non replicatori introdotti nell'universo naturale.

La misura non è `#matching` isolata, ma per esempio la differenza
predefinita
`P(Y=variante A | template A) − P(Y=variante A | template B)`,
con occupazione, composizione, esposizione/contatti e condizioni locali
controllate. Riportare anche la matrice A/B delle frequenze assolute e
l'indipendenza condizionata sotto i controlli: un aumento globale delle
reazioni **non** è trasmissione di variante.

## 3. Fase M6.3-0 — Diagnostica senza cambiare la fisica (prima scelta)

**Scopo:** vedere quanto l'attuale chimica possa produrre un segnale
specifico della variante, evitando sia false impossibilità sia
l'invenzione di una copia per costruzione.

**Protocollo da preregistrare in una PR separata, *prima* di qualsiasi
esecuzione:**
- costruire due template A/B di uguale numero di particelle, composizione,
  energia, vincoli di legame e accessibilità geometrica per quanto possibile;
  se l'uguaglianza delle geometrie locali è impossibile, **documentare
  esplicitamente il confondimento** e non chiamare il test puramente informativo;
- fornire monomeri liberi di S0/S1 e risorse uguali, ma **non**
  introdurre un costruttore, enzima copiatore o una funzione `make_copy`;
- valutare con le **leggi M6 inalterate** nuove strutture prodotte altrove,
  escludendo aggregati che hanno condiviso particelle o un precursore con
  i template;
- bracci: template A, template B, senza template,
  sham con stessa occupazione/composizione ma ordine mescolato quando
  fisicamente realizzabile, e controllo di semplice aumento dei contatti;
- monitorare sequenza di eventi, energia, occupazione, distanze, RNG,
  popolazione delle varianti; non attribuire causalità a sola prossimità;
- campionare **seed indipendenti** fissati prima dell'esecuzione,
  dimensione campionaria motivata tramite analisi di sensibilità/potenza
  separata e una regola per i risultati `inconclusive`;
- conservare risultati nulli, gli hash congelati dei controlli e lo
  strumento analitico versionato.

**Falsificazione dell'ipotesi di templating osservabile:** nessuna
differenza di distribuzione A/B oltre alle bande fissate ex ante,
oppure vantaggio identico dopo controllo per superficie/numero di
contatti. Una differenza che nasce solo dal numero di collisioni
è effetto cinetico/geometrico, **non copia informativa accertata**.

**Gate:** se si vede un effetto specifico sotto le leggi attuali,
approfondire prima la causalità senza nuove leggi. Se non appare,
concludere `not observed at tested conditions`, **non**
`physically impossible for all configurations`.

## 4. Tre estensioni minime candidate — NON approvate

Nessuna è implementata in questa PR. Sono **alternative concorrenti**,
non tre cambiamenti simultanei. La scelta richiede un documento separato
con motivazione, protocollo, seed, parametri, costi e autorizzazione esplicita.

### A — Mobilità rigida di aggregati (M6.2-A)

**Ipotesi limitante:** l'immobilità dei cluster impedisce loro di
raggiungere substrati e altri aggregati a una velocità sufficiente,
riducendo occasioni di templating (anche solo geometrico).

**Regola ipotetica minima:** proporre di spostare un componente legato
come unità **rigida** di una cella, solo se tutte le celle di destinazione
sono accessibili; preservare adiacenza e legami, gestire bordi periodici,
competizione fra componenti e costo energetico con ledger chiuso.

**Confronto:** identici parametri chimici con mobilità
`off/on`; mobilità `off` deve riprodurre **bit per bit** gli hash M6.
Misurare incontri componente–monomero per tick, incontri fra componenti,
accesso alle sorgenti, assemblaggio e varianti A/B.

**Falsificatore:** incontri aumentati ma nessuna trasmissione di variante
specifica. In tal caso **A migliora la cinetica, non risolve l'ereditarietà**.
Necessaria verifica indipendente di collisioni, energia e numero di RNG.

**Rischio:** effetti massicci sul numero di collisioni e sul flusso RNG
globale; prova A/B difficile da identificare senza nuovi controlli.

### B — Catalisi dipendente dal contesto strutturale *locale*

**Ipotesi limitante:** un prodotto legato non influenza in maniera
specifica la reazione successiva in base a **come** è disposto,
mentre la sola specie catalizzatrice influenza la cinetica.

**Regola ipotetica minima:** arricchire la funzione di propensione con
un **predicato di vicinato** generico, locale e simmetrico, per esempio
presenza di un legame del catalizzatore e tipo dei suoi partner
immediati. Evitare di cercare la firma del template o una sequenza
globale nel motore; nessun riferimento a `replication`, `genome`,
`target signature`, né condizioni speciali dedicate ad A o B.

**Confronto:** usare varianti strutturali A/B uguali per composizione
e superficie esposta per quanto possibile; valutare la **specificità**
del prodotto, non soltanto quanti legami si formano. Controlli shuffled
dei motivi e catalisi per specie (schema M6.2-B) come baseline.

**Falsificatore:** più reazioni, ma `P(Y=A|T=A)` indistinguibile
da `P(Y=A|T=B)` dopo i controlli. Il predicato cambia la velocità
ma non porta una variante dall'una all'altra struttura.

**Rischio:** una regola troppo mirata può **codificare di nascosto
un replicatore**. Richiedere verifica che valga per molte specie,
motivi e configurazioni non scelte per produrre un risultato positivo.

### C — Stato interno reversibile di particella (tipo fisso)

**Ipotesi limitante:** senza alcuna variabile interna mutabile,
l'informazione trasmissibile è confinata a ordine di specie,
posizione e topologia; la sola catalisi di specie non può conservare
uno stato trasferibile di lungo periodo.

**Regola ipotetica minima:** aggiungere a ogni particella un piccolo
stato locale discreto (es. `q∈{0,1}`) che evolve con regole
di reazione **simmetriche e reversibili** dipendenti dal vicinato,
senza istruzioni esplicite `copia q del vicino` o riconoscimento
di genomi. Lo stato deve entrare in checkpoint, hash, test di
invarianti e rendicontazione energetica se la transizione ha costo.

**Confronto:** varianti differenziate per schema di `q` ma con
identica composizione e topologia; controlli con stati mescolati,
reazioni disattivate e periodi di rilassamento. Contare errori,
persistenza, trasmissione e generazioni causali (non soltanto
duplicazione di un bit isolato).

**Falsificatore:** stati che si propagano senza mantenere
un'associazione tra variante sorgente e struttura figlia,
oppure strutture la cui variante scompare prima del ciclo successivo.

**Rischio:** più gradi di libertà possono produrre pattern
persistenti senza capacità di riproduzione. Ereditare una singola
variabile non equivale a produrre una copia.

## 5. Confronto con lavori pubblicati: uso e limiti

| Riferimento | Capacità realmente studiata | Cosa ALIFE può utilizzare | Cosa **non** importare |
|---|---|---|---|
| [Hutton 2002, Squirm3](https://doi.org/10.1162/106454602321202417) | Molecole autoreplicanti da condizioni favorevoli di soup; atomi con **tipo fisso e stato mutabile**, reazioni locali e legami | Testare se uno stato e reazioni locali permettono più varianti trasmesse | Copiare direttamente la rete di regole che realizza la copia |
| [Hintze & Bohm 2026](https://doi.org/10.1038/s44260-026-00074-2) | Ricostruzione causale di replicatori anche **distribuiti** in un automa cellulare **deterministico** | Distinguere i veri archi causali dalle firme coincidenti; verificare più generazioni | Trattare le dipendenze di celle di un CA come se fossero automaticamente valide per il nostro RNG stocastico |
| [Kruszewski & Mikolov 2022](https://doi.org/10.1162/artl_a_00355) | Metabolismi autoriproduttivi in una chimica con reazioni computazionalmente espressive (riscrittura combinatoria) | Considerare reti di reazioni e processi ricorsivi, non solo copie di polimeri | Inserire Turing-complete rewriting come prerequisito o presunta equivalenza con ALIFE |
| [GARD / sintesi 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6073634/) | Trasmissione di **composizione** in aggregati con mutua catalisi, crescita e divisione | Valutare una nozione alternativa di ereditarietà e misure di stabilità composizionale | Chiamare ereditarietà la sola conservazione delle quantità di specie o il singolo split |

I risultati pubblicati dimostrano **possibilità in altri modelli**,
non predicono che ALIFE produrrà copie con poche modifiche.
Mantenere tre etichette separate: `observed here`, `demonstrated elsewhere`,
`hypothesized here`.

## 6. Matrice decisionale proposta

| Percorso | Capacità primaria testata | Rischio di hardcodare copiatura | Priorità |
|---|---|---|---|
| M6.3-0: variante A/B con regole attuali | Potere informativo già disponibile, causalità della geometria | **Nessun cambio di fisica** | **P0 — primo esperimento** |
| B: catalisi strutturale locale | Discriminazione tra varianti chimiche | Alto se il predicato è costruito ad hoc | **Prima opzione da progettare dopo P0**, non approvata |
| A: mobilità degli aggregati | Trasporto/incontri, non automaticamente ereditarietà | Basso per copiatura, alto per divergenza RNG | Seconda opzione se il collo di bottiglia è verificabilmente il trasporto |
| C: stato interno reversibile | Nuova memoria locale, possibile trasmissione | Medio-alto per eccesso di libertà | Terza opzione, maggiore complessità |
 
**Decisione raccomandata:** prima verificare con una sonda diagnostica
**non replicante** se l'attuale modello distingue e influenza varianti
A/B. Solo se il limite è dimostrato per il regime sperimentato
proporre *una* variazione minima e preregistrare il confronto a
singola variabile. L'ordine B–A–C è motivazione iniziale, non
decisione irrevocabile: può essere confutato dai dati M6.3-0.

## 7. Criteri di accettazione e tutela dei risultati storici

**Gate M6.3-0 (progetto → esperimento):**
1. protocollo con configurazioni, seed, n esperimenti, osservatori versionati,
   distribuzioni, invarianti, stop rule e gestione degli esiti nulli
   **committato prima dei primi run**;
2. varianti A/B con **stessa composizione** e verifica che le firme
   siano distinte; negativi di origine materiale comune/split e
   ricomposizione rimangono non-classificati come copie;
3. dati grezzi, hash del mondo, eventi, RNG ed esposizione locale
   conservati in artefatti CI; niente riscrittura di M6/M6.2-E;
4. effetti cinetici separati da dipendenza della variante;
5. nessuna proposta per M7 senza **almeno due generazioni, più discendenti
   causali e trasmissione di varianti** rispetto a controlli.

**Gate per cambiare le leggi:** richiesta esplicita e separata con
sintesi del dato che dimostra il limite, modifica atomica della regola,
costo computazionale, alternative scartate, protocolli
`off/on`, compatibilità del comportamento `off` *bit per bit*,
invarianti della materia/energia, determinismo e test di confutazione.
**Questa PR non soddisfa da sola tale autorizzazione.**

I test per questa PR sono limitati alla revisione redazionale e
alla verifica dei link e dei riferimenti: nessuna simulazione
scientifica o nuova batteria di test fisici è implicata.
