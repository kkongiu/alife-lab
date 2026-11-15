# ALIFE — Piano scientifico aggiornato: causalità prima delle nuove leggi

**Stato:** proposta di integrazione della roadmap M0–M7 · **Data:** 15 novembre 2026
**Origine:** [issue #4](https://github.com/kkongiu/alife-lab/issues/4) ·
**Politica:** questo documento non modifica il simulatore, le sue configurazioni storiche, i rilevatori preregistrati o i criteri di M6.

Questo è un **addendum di ricerca** alla roadmap originaria
[`Progetto_Vita_Artificiale_Roadmap_Milestone.docx`](../Progetto_Vita_Artificiale_Roadmap_Milestone.docx),
non un cambiamento retroattivo della specifica delle milestone approvate.
Un test di infrastruttura superato non è prova di vita o di replicazione.

## 1. Evidenza accertata e attività già disponibili

| Evidenza / funzione | Stato verificabile | Interpretazione |
|---|---|---|
| M6: cinque condizioni × cinque seed, 3.000 passi | 25 run; zero classificazioni di replicazione | Nessuna evidenza di replicazione nei mondi originari |
| M6.2-E / `v2` | 1.051 nascite candidate di prossimità; una raggiunge la firma e persiste in `unfed-6101`; nessuna seconda generazione | **Match osservato**, non prova di parentela |
| Rilevatore `v2.1`, [PR #1](https://github.com/kkongiu/alife-lab/pull/1) | Test di regressione sul limite della finestra e sulla permanenza **continua** della firma; versione `v2` originale preservata | Correzione analitica; non ricalibrare retroattivamente i risultati `v2` |
| M6.2-B, [PR #2](https://github.com/kkongiu/alife-lab/pull/2) | 15 run, catalisi S3/S0: aumento delle formazioni S0–S1 in tutti i cinque seed; nessuna copia persistente | **Effetto cinetico**, non autocatalisi evolutiva né ereditarietà |
| `unfed-6101`, [PR #3](https://github.com/kkongiu/alife-lab/pull/3) | Replay dal passo 791, identità completa baseline; spostamento del template (2/3 match persistenti), sham remoto (2/4) | **Esplorazione post-hoc**, non stima causale definitiva |
| `master` al momento della stesura | Ultimo commit `ff135528`, M6.2-E | Le PR #1–#3 sono **bozze**, non sono integrate in `master` |

Il template dell'unico match è la struttura **850** (particelle
143, 290, 388, 414). La candidata è la struttura **872**, nata al passo
**792** dal dimero **93–245**, con prima firma uguale al passo **835**
e controllo di persistenza al passo **845**. La firma è
`T:(S0:(S0:(S0:(S0:))))`: **catena omogenea di quattro S0**.
Non ci sono particelle condivise con il template. Il rapporto PR #3 conta
**20 ID strutturali distinti** che avevano già assunto quella firma prima
del passo 792 (26 eventi, non necessariamente indipendenti).
La firma è esatta rispetto all'isomorfismo del grafo, ma ha **scarsa
specificità informativa** perché non descrive una sequenza chimica diversificata.

## 2. Principio di inferenza

Conservare quattro livelli di evidenza distinti, mai intercambiabili:

1. **Ricorrenza:** due strutture hanno la stessa firma o composizione.
2. **Associazione:** la firma compare vicino a una struttura precedente.
3. **Influenza causale candidata:** un intervento predefinito sul presunto
   genitore modifica un esito misurabile più dei controlli comparabili,
   senza spiegazioni alternative dominanti.
4. **Replicazione ereditaria:** discendenza causale verificabile, più copie
   indipendenti, **almeno due generazioni** e trasmissione di una
   *variante informativa* (non una firma omogenea comune).
   
Non chiamare mai “organismo” un evento del livello 1–3. Un esperimento
negativo è un risultato: dev'essere archiviato, non escluso.

## 3. Ordine delle prossime milestone

### P0 — Congelare e qualificare gli osservatori (prima di ogni nuova fisica)

**Obiettivo:** rendere ogni risultato riconducibile a una versione del
rilevatore senza modificarne il passato.

- Mantenere `replication_v2.py` originale **immutato** con le sue soglie e i
  suoi manifest; utilizzare `replication_v21.py` come *nuova* versione con
  criteri di persistenza espliciti.
- Validare `v2.1` sui controlli positivi/negativi M5, su matching al limite
  di 150 passi e fuori limite, e su variazione di firma con ID ancora attivo.
- Aggiungere fixture separate per **split, merge, ri-accrescimento, interruzione
  e ripristino della firma, nascite simultanee**, e alternative di template
  a pari distanza. Riportare ambiguità e falsi positivi, non occultarli.
- Registrare per ogni candidato: versione, chiave della firma, passi di nascita
  e corrispondenza, motivo di scarto, cronologia di firma e identità particellare.
- **Gate:** tutti i controlli passano su GitHub Actions e la ri-analisi
  deterministica preserva gli hash M6 originali; `v2` e `v2.1` non vengono
  mescolati nelle medesime statistiche senza etichetta.

**Stato:** una parte è già implementata e verificata in PR #1; i nuovi
controlli split/merge e ripristino transitorio restano **da completare**.

### P1 — Ricostruzione degli eventi di `unfed-6101` (priorità assoluta)

**Solo strumentazione; nessun cambiamento alle leggi.**

- Replay del mondo originale con seed/config già registrati, verificando hash
  completo, stato RNG e contabilità energetica finale.
- Tracciare a livello di **particelle e legami** i passi **770–846**
  (inclusi il periodo precedente alla comparsa della struttura 850,
  la nascita 872 e i dieci passi successivi al match): ID, specie,
  posizioni, componenti, firme, formazioni/rotture, vicinanze, energia,
  numero di estrazioni RNG e variazioni locali.
- Produrre `JSON` macchina-leggibile e tabella cronologica leggibile,
  identificando esattamente quando l'assemblaggio della candidata è
  stato eventualmente influenzato da vicini del template.
- Registrare anche la **frequenza di fondo** della stessa firma prima
  dell'evento, distinguendo occorrenze, ID e nascite indipendenti.
- **Gate:** stessa identica traiettoria del mondo originale con observer;
  è possibile ricostruire gli eventi che portano da 93–245 a 40–93–245–477.
  Qualsiasi osservazione che consuma RNG o modifica il mondo fallisce il gate.

**Stato:** PR #1 contiene una prima timeline di firma e replay; PR #3
contiene un controfattuale esplorativo. Una vera timeline completa delle
reazioni e dei fattori di incontro locali resta da realizzare.

### P2 — Verifica causale controllata (non aggiungere un replicatore)

**Ipotesi falsificabile:** la presenza o la struttura del template 850
fornisce un contributo specifico alla formazione della firma della figlia
872, oltre a un effetto puramente spaziale e oltre alle perturbazioni casuali
del resto del mondo.

- Conservare il risultato della [PR #3](https://github.com/kkongiu/alife-lab/pull/3)
  come **esplorativo post-hoc**, non usare i suoi 3/4 tentativi come
  campione indipendente o evidenza statistica.
- **Prima di nuovi interventi:** versionare manifest di preregistrazione con
  ipotesi, tempi, lista completa degli interventi, *criteri di validità
  fissati prima degli esiti*, controlli e regola decisionale. Non scegliere
  gli spostamenti in base alla sopravvivenza della candidata.
- Confrontare baseline, intervento sul template e **sham omologhi remoti**.
  Controllare per distanza, occupazione, specie/composizione, numero di
  particelle e energia; dichiarare gli interventi non fisici.
- Misurare la divergenza delle estrazioni RNG e il **primo evento divergente**.
  L'RNG sequenziale può deviare globalmente dopo cambiamenti nel numero di
  incontri: non si può interpretare una differenza finale come effetto diretto
  della sola struttura rimossa.
- Analizzare gli **esiti locali prima della prima divergenza non locale**
  e la sensibilità ai controlli. Non presumere che stessa seed significhi
  rumore casuale identico dopo una perturbazione.
- Usare esperimenti sintetici con una **vera dipendenza nota** e controlli
  senza dipendenza per verificare la sensibilità e la specificità del metodo
  causale (separati dalla fisica naturale M6).
- Per evitare `p`-value ingiustificati sul singolo caso selezionato post-hoc,
  richiedere in futuro una **campagna nuova con seed e criteri congelati prima
  dell'osservazione**. Nessuna stima di frequenza causale da `unfed-6101`.
- **Gate:** una serie di interventi valida, bilanciata e ripetibile con
  risultato nullo o positivo *esplicitamente limitato*; se l'RNG non è
  accoppiabile e le alternative non sono escluse, verdetto **inconclusivo**,
  non “causale”.

**Importante:** cambiare la generazione globale dei numeri casuali per creare
un flusso *counter-based* sarebbe un **cambiamento della dinamica** e richiede
approvazione separata. Prima preferire tracing, misure di divergenza e
controlli a monte senza toccare il motore.

### P3 — Tracciamento genealogico causale, non solo geometrico

- Distinguere nel modello dati le relazioni del `Tracker` (continuità per
  particelle condivise, split/merge) dalle **dipendenze causali** tra
  aggregati distinti; il `Tracker` attuale **non** dimostra “padre → figlia”.
- Definire un grafo di **eventi locali** (formazione/rottura, vicinanza,
  contributo necessario al verificarsi di una reazione) che possa attribuire
  influenze e renderne esplicita l'incertezza. Usare i test controfattuali
  per verificare gli archi, non dedurli dalle sole firme.
- Richiedere più figlie **distinte, non ottenute per semplice frammentazione**,
  almeno due generazioni causali e varianti di forma/composizione trasmesse.
- Calcolare una misura descrittiva di **novità/specificità della firma**
  condizionata alla frequenza di fondo. La sola firma S0–S0–S0–S0
  non fornisce un test convincente di ereditarietà.
- Solo **in seconda battuta**, se i processi causali lo giustificano,
  sperimentare rilevamento di “individui distribuiti” composti da cluster
  disconnessi. Non importare direttamente un detector di automi cellulari
  in una chimica con particelle conservate, legami e RNG.
- **Gate:** lignaggi causali controllabili su positivi/negativi, distinti
  dai lignaggi di continuità fisica. Non procedere a M7 per un solo match.

### P4 — Confronto fisico con sistemi pubblicati

| Dimensione | ALIFE attuale | Squirm3 (Hutton, 2002) | Lezione verificabile |
|---|---|---|---|
| Rappresentazione | Particelle con specie fissa, legami e energia intera | Atomi con **tipo e stato**; sequenze di basi in molecole | La capacità di variare **stato** non richiede necessariamente cambiare tipo |
| Reazioni | Formazione/rottura probabilistica di legami; catalisi moltiplica la probabilità di una coppia per una specie vicina | Serie di reazioni locali dipendenti anche dallo stato degli atomi, capace di propagare una sequenza | La catalisi generica di ALIFE non legge la struttura come *template* |
| Movimento | Particelle libere mobili; aggregati legati **immobili** | Movimento locale degli atomi con vincoli di prossimità dei legami | Mobilità degli aggregati è ipotesi fisica da testare, non una garanzia di copie |
| Energia / risorse | Ledger M3 esplicito e sorgenti/dissipazione | Risorse molecolari consumabili, eventi di perturbazione dello stato per innescare replicatori da soup | Modelli energetici differenti; non assumere equivalenza termodinamica |
| Ereditarietà | Nessun trasferimento di sequenza provato | Copia di catene di tipi; mutazioni e selezione semplice | Una vera variante trasmessa è più informativa di una ricorrenza omopolimerica |

**Precisazione cruciale:** nel modello Squirm3 la comparsa da una miscela inizialmente
inerte richiede perturbazioni casuali dello **stato** degli atomi
(“cosmic rays”). Non copiare le regole R1–R8 né imporre nel motore ALIFE
una reazione `make_copy`; Squirm3 offre un **confronto di capacità
meccanicistiche**, non il risultato che ALIFE debba produrre.

Altri filoni, in ordine di pertinenza:
- **Hintze & Bohm (2026):** *causal ancestry graph* per replicazione
  multigenerazionale e distribuita in automi cellulari. Adattare **la domanda
  causale**, non presumere l'identità della dinamica.
- **Kruszewski & Mikolov (2022):** reti di reazioni e metabolismi ricorsivi,
  filone alternativo se la copiatura di strutture resta poco espressiva.
- **GARD:** ereditarietà **composizionale**; eventuale filone successivo,
  distinguendolo dalla fedeltà di sequenza.
- **Stepney (2025):** quadro delle origini della vita artificiale virtuale,
  utile per non confondere comparsa di strutture con autonomia.
- **Avida / Lenski et al. (2003):** benchmark di **evoluzione dopo** che
  la replicazione è disponibile, non prova che la replicazione sia emersa
  spontaneamente in ALIFE.

### Bibliografia primaria / di sintesi

- Hintze & Bohm (2026), [npj Complexity](https://doi.org/10.1038/s44260-026-00074-2).
- Hutton (2002), [Squirm3, Artificial Life 8(4)](https://doi.org/10.1162/106454602321202417),
  [testo consultabile](https://faculty.cc.gatech.edu/~turk/bio_sim/articles/hutton_rep_molecules.pdf).
- Kruszewski & Mikolov (2022),
  [Artificial Life](https://doi.org/10.1162/artl_a_00355).
- GARD: [sintesi su PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6073634/).
- Stepney (2025), [Philosophical Transactions B](https://doi.org/10.1098/rstb.2024.0298).
- Lenski et al. (2003), [Nature / Avida](https://doi.org/10.1038/nature01568).

### P5 — Solo dopo la causalità: eventuali modifiche alle leggi (decisione separata)

**M6.2-A, mobilità degli aggregati, non è autorizzata da questo addendum.**
La sua motivazione possibile è concreta: con aggregati immobili, la
mobilità relativa tra template e risorse può essere insufficiente.
Ma serve prima valutare se un'ipotesi d'interazione informativa è
realizzabile nel modello, distinguendo *impossibile* da *non osservato*.

Proporre in una PR **solo di progettazione**, prima di implementare:
1. descrizione delle regole locali minime (spostamento rigido di componenti,
   conflitti, adiacenza dei legami e bordo periodico; energia di movimento);
2. conservazione di particelle, specie e ledger energetico, invarianti
   topologici, determinismo, budget RNG, checkpoint/replay;
3. modalità disabilitata equivalente **bit per bit** al baseline M6;
4. confronto a singola variabile, con seed e soglie preregistrati;
5. confutazioni e criteri di arresto; costo computazionale stimato;
6. esplicita autorizzazione a cambiare fisica, separata dal merge di
   documentazione/strumenti di analisi.

Possibili evoluzioni successive (mai simultanee nel primo esperimento):
catalisi sensibile alla struttura, stati interni chimici, diverse valenze,
trasformazioni di specie. Nessuna è necessaria *per definizione*; ogni proposta
deve specificare quale capacità minima mancava e come falsificare la tesi.

## 4. Regole per il passaggio a M7

**Non passare a M7** sulla base di:
- un singolo `signature match`, nemmeno persistente;
- un incremento della frequenza di legami o di energia disponibile;
- una catena di parentela del tracker fondata su contatto o condivisione
  di particelle senza test causale;
- sole differenze di un replay spostando materia con flusso RNG divergente.

Una eventuale campagna candidata M7 deve preregistrare:
- definizione esatta di copia informativa e controllo del tasso di ricorrenza;
- più copie indipendenti da almeno un genitore, non semplici split;
- discendenza causalmente sostenuta per almeno due generazioni;
- trasmissione verificabile di almeno due varianti non banali di forma,
  composizione o sequenza;
- controlli positivi e negativi e universi **indipendenti**;
- ripetibilità su seed distinti e criteri di decisione fissati in anticipo.

Il numero di seed, la soglia statistica, i casi inconclusivi e la
procedura di gestione delle ambiguità vanno fissati **prima** della
campagna, non scegliendoli sui dati.

## 5. Sequenza operativa consigliata

**Prima:** integrare e verificare gli strumenti di osservazione in PR #1;
tenere l'audit post-hoc della PR #3 come riferimento, senza trasformarlo in
prova generale.

**Poi:** completare P1 (tracciamento eventi di `unfed-6101`) e P2 (nuovi
controfattuali preregistrati e controlli sham bilanciati). Una volta chiusi,
progettare il grafo causale P3.

**Infine:** usare P4 per giustificare o rifiutare una proposta isolata M6.2-A.
Non modificare le leggi senza discussione e decisione documentata.

### Regole di repository

- Preservare hash, manifest e report M0–M6.2-E originali.
- Una PR per cambiamento di detector/osservatore, una PR separata
  per nuove leggi; non mescolare le due classi.
- Ogni esperimento conserva protocolli, seed, codice, versioni,
  risultati grezzi, controlli e verdict nulli.
- GitHub Actions è **strumento di esecuzione**, non validazione della
  causalità per il solo fatto di restituire un esito verde.
