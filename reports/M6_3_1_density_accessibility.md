# M6.3-1 — Densità, accessibilità e sopravvivenza delle sonde

**Data:** 15 novembre 2026 · **Stato:** 160/160 run completati, `pytest` superato, esito negativo/inconclusivo per trasmissione informativa.  
**Protocollo congelato prima del runner:** [commit `91d62e8`](https://github.com/kkongiu/alife-lab/commit/91d62e85b611a764f9ac34ea543025c38d071f23) (`campaigns/m6_3_1/protocol.json`).  
**Esecuzione riproducibile:** [GitHub Actions #43734750196](https://github.com/kkongiu/alife-lab/actions/runs/43734750196) — **success**.  
**Dati grezzi:** [artefatto `m6-3-1-all-runs`](https://github.com/kkongiu/alife-lab/actions/runs/43734750196/artifacts/14169857227), con `campaigns/m6_3_1/results.json`, tutti i 160 run inclusi quelli nulli, hash, contatori RNG, esposizione, eventi ed energia.

## 1. Domanda scientifica

M6.3-0 aveva prodotto circa 2–4 nuove catene A/B `strict near`
per braccio su 12 seed e 300 passi. Il problema poteva essere una
bassa disponibilità di contatti **oppure** un tempo troppo breve in cui
il presunto template rimane utilizzabile. L'esperimento M6.3-1
distingue questi fattori **senza modificare le leggi chimiche**.

Il test è **sintetico**: costruisce una sonda di 4 particelle
all'inizio, con energia correttamente contabilizzata. Nessun
replicatore è prodotto o inserito dal motore.

## 2. Protocollo

- Griglia periodica **24×24**.
- Densità **baseline**: 200 particelle (34,7% delle celle).
- Densità **enriched**: 264 particelle (45,8% delle celle).
- **16 seed nuovi** (8101–8116); **5 bracci bonded** A, B,
  A invertita, B invertita e terza variante C, per entrambe le
  densità: **2 × 16 × 5 = 160 mondi**.
- **450 passi** per mondo, senza modificare movimento,
  rottura/formazione, catalisi (off), RNG, energia, specie o valenze.
  Varia il *numero* delle particelle delle specie; le proporzioni
  sono simili ma **non esattamente identiche** fra densità.
- A: `S0–S1–S0–S1`; B: `S0–S0–S1–S1`;
  C: `S0–S1–S1–S0`.
  Tutte e cinque le sonde hanno **2 S0 + 2 S1, tre legami,
  stesse posizioni iniziali e stesso saldo energetico**.
  Le inversioni A/B sono controlli di orientamento.
- Per ogni seed/densità, lo sfondo ha le stesse posizioni e
  specie iniziali nei cinque bracci, con stato RNG identico
  dopo il posizionamento. Ciò **non implica** uguale RNG
  durante la chimica successiva.

L'osservatore conserva tutte le prime apparizioni di una
struttura con firma esatta A/B/C e **quattro ID distinti
dalla sonda**; gli eventi con precedente connessione materiale
ad essa sono marcati e **non contati** tra gli `strict`.
Una nuova firma conta come `near` quando almeno una
particella è entro 2 celle da uno dei quattro siti
del template originale.

**Misura decisiva:** conteggio `strict active near`, ossia la
prima comparsa di una nuova A o B `near` mentre il
componente della sonda è ancora formato **esattamente
dalle sue quattro particelle e tre legami, con la firma
originale**. Non si contano le comparizioni dopo
la perdita della struttura pura.

Vengono inoltre misurati:
- tick in cui la sonda è intatta, e tick della prima perdita;
- monomeri liberi S0/S1 in una cella adiacente ai siti della
  sonda per tick, divisi in periodi attivi/inattivi;
- eventi distanti, dopo perdita del template, e nel resto
  del mondo;
- reazioni di formazione, energia e impronte RNG.

Un'eventuale ricomparsa della forma pura conta nuovamente
come `active`; questa **non è** una prova di continuità
biologica.

## 3. Risultati primari

Nuove strutture di quattro particelle, `strict active near`;
i numeri riportano la **somma su 16 run per braccio**.

| Densità | Sonda | Nuove A | Nuove B | Tick attivi complessivi / 7.200 | Run attivi almeno 100 tick |
|---|---|---:|---:|---:|---:|
| baseline (200) | A | 2 | 0 | 639 | 3 |
| baseline (200) | B | 2 | 0 | 559 | 2 |
| baseline (200) | A invertita | 0 | 0 | 285 | 0 |
| baseline (200) | B invertita | 0 | 0 | 249 | 0 |
| baseline (200) | C | 2 | 1 | 1.002 | 3 |
| enriched (264) | A | 0 | 0 | 152 | 0 |
| enriched (264) | B | 0 | 0 | 131 | 0 |
| enriched (264) | A invertita | 0 | 0 | 101 | 0 |
| enriched (264) | B invertita | 0 | 0 | 122 | 0 |
| enriched (264) | C | 0 | 0 | 136 | 0 |

**Media del tempo con sonda intatta**, calcolata su
80 run per densità: **34,2 tick** alla densità baseline
contro **8,0 tick** alla densità enriched (su 450 disponibili).
La percentuale va letta come confronto **descrittivo,
non stima del tasso di rottura di legami**.

**Reazioni globali di formazione di legami**, somma per
tutti i 16 seed × 5 bracci: baseline **19.249**,
enriched **26.803** (**circa +39%**). Aumentano gli
eventi chimici mentre diminuisce il periodo in cui
un template puro è presente.

Altri risultati:
- Baseline `strict active near`: 7 eventi A/B
  nell'intero insieme dei cinque bracci; solo 4
  considerando i quattro bracci A/B senza C.
- Enriched `strict active near`: **0 A/B**
  su **80** run.
- Nessun braccio A/B enriched produce nemmeno un
  evento `strict active near`.
- Tutti i 4 bracci A/B enriched hanno **0/16 seed**
  con template intatto per almeno 100 tick.

## 4. Interpretazione: il collo di bottiglia riguarda l'esposizione di una sonda integra

M6.3-1 **non** ha superato il gate preregistrato,
che richiedeva almeno otto nuove A/B `strict active near`
per ciascuno dei quattro bracci A/B enriched e almeno
otto seed su sedici con la sonda intatta per 100 tick.
Neppure il gate di preferenza della variante è stato raggiunto.

**Risultato empirico robusto per questo regime:**
una densità maggiore provoca più reazioni di legame
ma **meno tempo con template esattamente intatto**.
Non aumenta la nostra capacità di osservare una
trasmissione specifica di variante prima della perdita
della struttura pura.

**Limite decisivo da chiarire prima di un'altra campagna:**
il criterio `active` richiede precisamente quattro
particelle senza altre incorporate. La sua perdita può
derivare da:
- **rottura** di uno dei legami iniziali;
- **accrescimento** con una quinta particella;
- **fusione** con un altro aggregato;
- più eventi successivi.

Questi meccanismi producono tutti `inactive` e il
rapporto attuale **non separa ancora** quanto contribuisce
ciascuno. Non possiamo concludere semplicemente che
i legami si rompono più in fretta all'aumentare
della densità. All'aumento delle reazioni può
corrispondere **maggiore accrescimento**.

**Importante:** esistono nuove A/B lontane dalle
sonde e dopo che le sonde non sono più pure: il
motore produce le forme, ma **non abbiamo verificato
una specificità ereditaria né una dipendenza causale**.
Un nuovo motivo vicino a una sonda intatta
non diventerebbe per questo un organismo.

Altre limitazioni: intervalli di esposizione brevi,
pochi eventi `strict active near`, posizione delle
specie differente fra A/B/C, flusso PCG64 globale
potenzialmente divergente, fixture sintetica e
assenza di discendenza multigenerazionale.

## 5. Prossimo gate scientifico: M6.3-2 osservazionale

**Prima di aumentare ulteriormente densità, durata
o introdurre nuovi meccanismi**, proporre un
audit *instrumentation-only* sulla causa effettiva
della prima perdita della forma pura:
- distinguere **rottura interna**, crescita da
  attacco di nuovi monomeri, fusione e combinazioni;
- misurare durata dei **tre legami originari**
  e persistenza del **nucleo materiale originale**,
  anche se aggregati aggiuntivi vi si legano;
- riportare contatti liberi per specie,
  opportunità di formazione e tempo con
  superfici ancora accessibili;
- conservare il confronto fra densità e
  i run negativi, senza reinterpretare i
  risultati precedenti;
- preregistrare metodi e decisioni prima
  dell'audit, con una nuova PR e nuovi output,
  lasciando la fisica di M6 completamente intatta.

**Verdetto:** `underpowered_or_no_detectable_specificity`.
Nessuna prova di copiatura causale, ereditarietà
o vita artificiale. **Nessuna autorizzazione
a modificare le leggi del simulatore o promuovere M7.**
