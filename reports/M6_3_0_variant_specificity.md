# M6.3-0 — Schermatura preregistrata di specificità informativa A/B

**Data:** 15 novembre 2026 · **Stato:** 72/72 run completati, test superati, **nessun segnale sufficiente** nel regime selezionato.  
**Protocollo congelato:** [`de5e7fb`](https://github.com/kkongiu/alife-lab/commit/de5e7fbb82bc3049fcdc6bdf3fd34f2e37f6cf92), `campaigns/m6_3_0/protocol.json`, committato prima della creazione del runner.  
**GitHub Actions:** [run 43733627441](https://github.com/kkongiu/alife-lab/actions/runs/43733627441) — **success**, `pytest` e runner completi.  
**Evidenze integrali:** [artefatto `m6-3-0-variant-specificity-data`](https://github.com/kkongiu/alife-lab/actions/runs/43733627441/artifacts/14169451487) (`campaigns/m6_3_0/results.json`, comprendente gli zeri, hash, eventi e seed).

## 1. Ipotesi e modello fisico

Il test ricerca la possibilità che la disposizione delle specie
nel template **A** (`S0–S1–S0–S1`) o **B**
(`S0–S0–S1–S1`) cambi la proporzione delle **nuove**
strutture con firma A o B nel proprio vicinato, e non soltanto
la quantità totale di reazioni.

- **Le leggi M6 non sono state modificate**: probabilità di movimento,
  formazione/rottura, valenze, catalisi disattivata, costo energetico,
  decadimento, configurazione del RNG e regole di legame provengono
  da `campaigns/m6/configs/unfed-6101.json`.
- Questo è un **nuovo regime di screening**, non la replica del mondo M6:
  griglia periodica **24×24**, **200 particelle**
  (80 S0, 80 S1, 24 S2, 16 S3), **300 passi**, **12 seed indipendenti**
  (7101–7112), **sei bracci** per seed = **72 universi**.
- Template sintetici formati da quattro particelle già collegate
  alla partenza; stessa composizione e stessa geometria delle
  quattro posizioni ma **ordine delle specie differente**.
  La composizione dell'ambiente, le posizioni iniziali delle
  altre particelle e lo stato RNG dopo il piazzamento
  sono identici fra bracci con lo stesso seed.
- Bracci: A, B, A invertita, B invertita, A con nessun legame
  iniziale, B con nessun legame iniziale.
  Le catene invertite conservano la stessa firma canonica
  (invarianza per inversione), confermata dai test.
- I legami delle sonde sono inseriti come **condizione iniziale
  controllata** con energia immagazzinata e dissipazione contabilizzate,
  quindi l'invariante energetico è soddisfatto.

L'assemblaggio iniziale delle sonde **è deliberato**: non
pretendiamo che A/B siano emersi spontaneamente, né
introduciamo una regola che costruisca figli.

## 2. Definizione operativa di misura

Si conta una sola volta, alla prima apparizione, ciascuna
coppia `(firma esatta A/B, insieme dei quattro ID)`.
È richiesta una struttura **materialmente distinta** dai
quattro ID del template. Gli eventi sono segnati come
`previously_material_shared` se le loro particelle
hanno mai appartenuto, fino a quell'istante, a un componente
legato contenente una delle particelle del template.

La misura **strict near** esclude tali eventi e richiede
almeno una particella della struttura entro distanza toroidale
Manhattan **≤2** da uno dei quattro siti iniziali della sonda.
Questa condizione non prova causalità; misura solo comparsa
in un'area prefissata con controllo minimo della storia materiale.

I conteggi globali (occorrenti in qualsiasi cella) e
l'opportunità di incontro di monomeri liberi vengono raccolti
separatamente, per rilevare aumenti cinetici non specifici.

## 3. Risultati osservati

| Braccio | Strict near A | Strict near B | A ovunque | B ovunque | Formazioni di legami in 12 run |
|---|---:|---:|---:|---:|---:|
| A | **2** | 1 | 45 | 35 | 2.446 |
| B | **2** | 1 | 45 | 36 | 2.445 |
| A invertita | **3** | 1 | 39 | 36 | 2.397 |
| B invertita | **3** | 1 | 35 | 36 | 2.421 |
| A senza legami | 2 | 2 | 29 | 37 | 2.518 |
| B senza legami | 2 | 1 | 39 | 33 | 2.481 |

**Non appare un vantaggio specifico della variante del template:**
i bracci A/B hanno gli stessi conteggi strict near (2 A, 1 B)
e le inversioni danno ugualmente 3 A, 1 B in entrambi
i bracci. Con questi numeri molto piccoli non è possibile
stimare con precisione una differenza di probabilità.

Il criterio di follow-up fissato prima di eseguire i run
richiedeva **almeno cinque eventi strict near per ogni braccio
bonded** e preferenza della variante corretta in almeno 8
dei 12 seed per ciascuno dei quattro bracci legati.

**Gate fallito**:
- minimo cinque: **non soddisfatto** in nessuno dei quattro bracci;
- seed con preferenza della variante del template:
  A **2/12**, B **1/12**, A invertita **3/12**, B invertita **1/12**.

Il totale di occorrenze nel resto della griglia è
non nullo, quindi il motore **produce** occasionalmente
entrambi i motivi come aggregati; manca il segnale locale
specificamente correlato alla variante della sonda
richiesto da questo test.

## 4. Interpretazione scientifica

**Evidenza tecnica:** la simulazione e l'osservazione sono
deterministiche nello stesso ambiente; l'esperimento ripete
una prova e ne confronta l'output esatto; i test controllano
firme differenti, composizione identica, reverse invariance,
stessa disposizione ambientale e ledger energetico.
La CI è conclusa correttamente e ha archiviato ogni run,
inclusi gli esiti nulli.

**Verdetto osservativo:**
`no_sufficient_variant_specificity_signal_at_tested_regime`.

**Non è la prova** che il motore non possa realizzare
templating geometrico in tutte le condizioni possibili:
- regimi di densità, durata, disponibilità energetica e
  composizione differenti potrebbero produrre esiti diversi;
- le sonde sono **inizialmente costruite**, non nate
  dall'evoluzione spontanea;
- A e B occupano le stesse celle ma distribuiscono
  diversamente S0/S1 in esse, variando incontri e
  accessibilità locale (confondimento non eliminato);
- i controlli senza legami hanno diversa energia iniziale
  immagazzinata/dissipata (confronto non isoenergetico);
- il flusso RNG globale può divergere dopo differenze nelle
  reazioni candidate;
- sono misurate nuove strutture riconoscibili, non
  generazioni causali successive né fedeltà ereditaria.

**Non autorizza M7 né alcuna introduzione di replicatori,
nuove reazioni, catalisi strutturale o stati interni.**

## 5. Prossima decisione

Non modificare le leggi sulla base di questo screening
**negativo ma poco potente**. La scelta più utile è
una nuova campagna analitica con **protocollo v2 distinto**,
senza ritoccare `protocol.json` v1, che migliori
l'identificabilità del segnale e l'accessibilità dei
substrati alla sonda.

Per esempio, studiare prima (con sola osservabilità)
quanto tempo il template resta accessibile e quanti
incontri utili riceve; poi preregistrare, con controlli
espliciti per geometria e densità, una configurazione
in cui il test sulla preferenza A/B abbia un numero
ragionevole di eventi. L'aumento di densità o durata
è **configurazione sperimentale**, non un cambio di legge,
ma deve essere giustificato e fissato prima di guardare
i risultati della nuova campagna.

Se anche in tale regime non apparisse nessun effetto
specifico, preparare una richiesta separata per
confrontare **A: mobilità rigida** e **B: catalisi
locale dipendente dal contesto**, senza implementarne
nessuna finché non venga approvata.
