# M7.11 — Anelli nativi: richiusura spontanea frequente dopo una rottura, ma nessuna prova di feedback energetico o autoriparazione

**17 novembre 2026 — esperimento preregistrato 640/640 universi completato.** Tutti i 16 shard, suite integrale di regressione e fusione dei risultati sono **PASS**. **Criterio primario non raggiunto per insufficienza di coppie discordanti** (0 contro 4); **criterio secondario non raggiunto per quota favorevole insufficiente** (59 contro 36). La richiusura chimica del legame aperto è invece un fenomeno osservato molto frequentemente, non selezionato retrospettivamente.

## Provenienza e dati

- [Protocollo M7.11 congelato **prima** del codice e dei risultati: commit \`d41f3f8\`](https://github.com/kkongiu/alife-lab/commit/d41f3f84894ae2df929716511ba213f179472dce).
- [GitHub Actions finale #44171645566 — regressioni, 16 shard e 640/640 universi: **PASS**](https://github.com/kkongiu/alife-lab/actions/runs/44171645566).
- [Dataset completo grezzo: artifact #14368491326, inclusi tutti i seed assenti, i 626 anelli e le 2.504 evoluzioni sperimentali](https://github.com/kkongiu/alife-lab/actions/runs/44171645566/artifacts/14368491326).
- [PR #39 in bozza](https://github.com/kkongiu/alife-lab/pull/39); [runner \`tools/m7_11_ring_fault_tolerance.py\`](../tools/m7_11_ring_fault_tolerance.py); [protocollo \`campaigns/m7_11_ring_resilience/protocol.json\`](../campaigns/m7_11_ring_resilience/protocol.json).
- Il modello nativo M6 \`src/\`, i moduli precedenti M6/M7.3–M7.10 e \`master\` **non sono stati modificati**. Nessun merge automatico.

## Premessa: resistenza strutturale non significa riparazione biologica

I precedenti M7.5–M7.10 avevano studiato prevalentemente reti **arboree** al primo tick in cui superavano un criterio di vecchiaia parziale. I legami di un albero sono tutti *ponti*: la rimozione di uno solo divide immediatamente il grafo. Un anello, viceversa, possiede almeno un percorso alternativo fra ogni coppia di nodi: la rottura di un singolo lato lascia ancora connessi tutti i suoi membri.

Questa è una **proprietà matematica della connettività**, non un organismo. Per evitare un successo tautologico, M7.11 misura l'esito solo dopo altri **120 tick di fisica nativa**, compresa formazione e rottura probabilistica di altri legami.

Lo studio si pone due domande preregistrate, entrambe fisicamente verificabili:

1. **La conduzione di energia attraverso i legami superstiti di un anello aperto favorisce la riformazione nativa dell'esatto legame perduto prima che qualsiasi altro legame originale si rompa?**
2. **L'anello rimasto integro conserva più spesso, dopo 120 tick, tutti gli ID materiali iniziali in un'unica componente connessa rispetto allo stesso anello a cui è stato tagliato un lato?**

Il primo è un test di **meccanismo energetico** e una forma molto debole di recupero di un legame; il secondo è un test di **robustezza meccanica passiva**. Neanche un eventuale successo in uno dei due sarebbe prova di autoriparazione biologica.

## Campione e scelta naturale dell'anello

- **640 nuovi seed numerici 29001–29640**, 16 shard fissi da 40.
- Stessa fisica M7.3 originale con 264 particelle su griglia periodica 24×24, 16 sorgenti energetiche distribuite, chimica M6 reversibile, movimento con costo energetico, assenza di catalisi e **zero legami iniziali**.
- L'universo evolve fino a un massimo di 600 tick: ad ogni passo si applicano \`World.advance(1)\` originale e poi **esattamente un passaggio M7.3 originale di trasferimento lungo i legami**.
- Il vecchio osservatore M6.4 \`analyze_cycle\` riconosce solo componenti native massimali che siano **anelli semplici non ramificati**, di **4, 6 oppure 8** atomi e grado chimico 2 per ogni membro. La specie e la sequenza dell'anello vengono riconosciute senza introdurre una struttura.
- Ogni episodio conserva **esattamente gli stessi ID e gli stessi legami** in snapshot consecutivi, e la prima rottura nativa di uno qualunque di tali legami **azzera la continuità**, anche se il legame si riforma nello stesso tick.
- Dall'istante 120 si seleziona il **PRIMO** anello che abbia già almeno **20 snapshot continui** senza una rottura vera: tick più precoce, poi più piccolo insieme di ID in ordine lessicografico. Al massimo un anello per universo, senza scegliere retroattivamente quelli che sembrano recuperare meglio. Se nessun anello raggiunge il criterio, il mondo rimane nel dataset come negativo.

**Risultato sulla raggiungibilità dei cicli nativi in M7.3:**

| Voce | Mondi |
|---|---:|
| Universi esaminati | **640** |
| Universi con anello naturale e almeno 20 tick senza rottura prima di t600 | **626/640 = 97,81%** |
| Anelli osservati ma mai sufficientemente vecchi | 5 |
| Nessun anello semplice 4/6/8 osservato entro t600 | 9 |

Fra i 626 anelli selezionati, **557** hanno quattro atomi, **57** ne hanno sei e **12** ne hanno otto. Il tick medio della prima selezione è **141,08**; l'età continua media del ciclo in quel momento è **60,54 tick**, poiché il conteggio comincia prima del primo tick selezionabile (120).

Il tasso 626/640 riguarda **specificamente questo regime M7.3, questa densità e questo scanner**: non è una probabilità universale di generazione di una membrana o di vita.

## Quattro fork fisici e interfaccia con M6 originale

Al checkpoint dell'anello, quattro mondi sono **cloni completi** del medesimo universo nativo: stesse particelle, energie, posizioni, legami, buffer delle sorgenti, stato RNG e contatori energetici.

Il legame da tagliare è **sempre quello con la coppia di ID materiali lessicograficamente minima**, individuato prima di qualsiasi sviluppo successivo. L'intervento \`apertura\` rimuove quel solo legame; **tutta l'energia chimica già immagazzinata viene restituita** ai due atomi nello stesso ordine e con lo stesso arrotondamento del motore M6, senza dissipazione ulteriore né estrazioni RNG. Nessuna nuova particella, legame o sorgente compare. Il taglio genera una catena ancora connessa, come previsto dalla teoria dei grafi.

| Braccio | Stato al fork | Evoluzione successiva |
|---|---|---|
| **\`intact_normal\`** | Anello naturale completamente integro | M6 originale + passaggio M7.3 originale su tutti i legami |
| **\`intact_ring_conduction_suppressed\`** | **Stesso identico anello integro** | M6 originale; durante il passaggio energetico si saltano soltanto i legami originali dell'anello, mentre gli altri legami conducono secondo M7.3 |
| **\`opened_normal\`** | Un lato rimosso, energia chimica rimborsata | M6 originale + conduzione M7.3 originale su tutti i legami esistenti |
| **\`opened_surviving_ring_conduction_suppressed\`** | **Stesso identico anello aperto e rimborsato** | M6 originale; si salta la conduzione sui lati superstiti originari, ma se il lato tagliato viene ricreato può condurre |

Tutti e quattro i mondi conservano al fork **esattamente la stessa energia totale**, pur con distribuzioni fra le particelle e legami diverse nei mondi aperti rispetto a quelli integri. Entro ciascuna coppia \`integro/integro\` e \`aperto/aperto\`, **la prima evoluzione M6 e il relativo stato RNG sono identici PRIMA del successivo diverso passaggio energetico**, verificato automaticamente.

I percorsi casuali globali possono invece divergere nei tick successivi: l'apertura cambia il numero dei legami e quindi le estrazioni dei tentativi di rottura, mentre la conduzione modifica indirettamente la chimica successiva. Si tratta di interventi di regime e non di reazioni con sorteggi accoppiati per coppia come M7.8.

Le formazioni e rotture di legami sono rilevate tramite i veri \`BondEvent\` del motore M6, non dedotte soltanto dall'osservazione di un legame nella fotografia finale.

## I criteri PREREGISTRATI

**Primario — riformazione esatta prima di altre rotture.** Nei due bracci **APERTI**, deve verificarsi un vero evento chimico M6 \`FORM\` per **la stessa coppia originale tagliata**, il nuovo legame deve essere presente nel grafo dopo il passo, e non deve essere accaduto in alcun tick precedente o nello stesso tick un evento M6 \`BREAK\` su uno degli **altri** legami originali. Un legame che si spezza e si ricostituisce nello stesso tick conta comunque come rotto. Soglie: almeno **40 seed con anello**, almeno **25 confronti discordanti** fra \`opened_normal\` e \`opened_surviving_ring_conduction_suppressed\`, almeno **2/3** di tali discordanti favorevoli alla normale conduzione sui lati rimasti.

**Secondario — connettività dell'intero materiale a tick120.** Tutti gli ID dell'anello originale devono appartenere a **una stessa componente chimica connessa** dopo 120 tick; i percorsi possono coinvolgere anche particelle esterne. Soglie: almeno **40 seed idonei**, almeno **25 confronti discordanti**, almeno **2/3** favorevoli all'anello integro \`intact_normal\` rispetto alla sua copia inizialmente aperta \`opened_normal\`.

Queste soglie, i campioni, le dimensioni degli anelli e gli orizzonti temporali sono stati fissati **prima dei risultati**. Le altre metriche sono descrittive, non alternative post-hoc per dichiarare un successo.

## Risultati

| Misura per braccio sui 626 anelli | Integro normale | Integro, senza conduzione ring | Aperto normale | Aperto, senza conduzione sui lati rimasti |
|---|---:|---:|---:|---:|
| **Richiusura del legame tagliato prima di altre rotture** | n.a. | n.a. | **461** | **465** |
| Almeno una FORM sul target in qualsiasi momento del followup | 79* | 80* | **510** | **516** |
| **Tutti gli ID originali connessi a t120**, anche tramite esterni | **584** | 582 | 561 | 553 |
| Tutti gli ID originali connessi **soltanto mediante i propri legami** a t120 | **583** | 581 | 561 | 553 |
| **Tutti i legami originali dell'anello presenti** a t120 | **426** | 416 | 338 | 341 |
| Nessuna rottura M6 di un legame originale nei 120 tick | 208 | 208 | **236** | 234 |
| Trasferimenti medi di un quanto su legami originali dell'anello | 54,70 | **0** | 61,75 | 7,81 |

*Negli anelli inizialmente integri, una FORM sul target può verificarsi soltanto dopo una naturale rottura del medesimo legame; non equivale al recupero del lato tagliato sperimentalmente.*

### Endpoint primario: **NON RAGGIUNTO per insufficienza di discordanti**

Nei 626 confronti appaiati \`aperto normale\` vs \`aperto con conduzione sui lati superstiti soppressa\`:

| Esito | Seed |
|---|---:|
| Richiusura precoce soltanto con conduzione normale | **0** |
| Richiusura precoce soltanto senza conduzione superstite | **4** |
| Richiusura precoce in entrambi | **461** |
| Richiusura precoce in nessuno | **161** |
| **Discordanti** | **4** |

Il requisito preregistrato era **≥25 discordanti**, quindi il verdetto è \`not_met_insufficient_discordant_worlds\`. Non è corretto calcolare uno zero su quattro e spacciarlo per una conclusione generale che «la conduzione peggiora la richiusura»: i due bracci hanno risultati estremamente simili per questo endpoint e il confronto non raggiunge il minimo di informatività richiesto.

**La richiusura esiste comunque ed è osservata direttamente nella chimica nativa:** **461/626 = 73,64%** dei mondi aperti con conduzione normale producono una FORM dell'esatta coppia prima di qualunque altra rottura originale. Il semplice ricomparire del legame nello snapshot non sarebbe sufficiente a dimostrarlo; qui abbiamo gli eventi reali verificabili.

Fra i 461 casi positivi di richiusura precoce, il **tempo mediano al primo evento è 11 tick**, la media **16,44 tick**, circa il decimo percentile a **2 tick** e il novantesimo a **39 tick**. Il controllo con conduzione superstite soppressa presenta la stessa mediana di 11 tick. Il tempo è misurato dal **taglio sperimentale**, non dall'originaria formazione spontanea dell'anello.

Questa è una **reattività spontanea della chimica reversibile M6 dopo un danno controllato**, non una macchina di riconoscimento del danno o di riparazione regolata.

### Endpoint secondario: **NON RAGGIUNTO per quota favorevole insufficiente**

Confronto appaiato della coesione di tutti gli originali a tick120, anello integro vs inizialmente aperto:

| Esito | Seed |
|---|---:|
| Solo anello integro conserva la coesione | **59** |
| Solo anello aperto conserva la coesione | **36** |
| Entrambi conservano la coesione | **525** |
| Nessuno conserva la coesione | **6** |
| **Discordanti** | **95** |

Quindi **59/95 = 62,11%** dei confronti discordanti favoriscono l'anello integro, sotto la soglia **66,67%** congelata. Con 95 discordanti, per superare i due terzi sarebbero serviti **almeno 64** seed favorevoli, non 59. È un risultato vicino ma **formalmente negativo**, e il minimo di 25 discordanti è stato pienamente raggiunto.

Le percentuali assolute di coesione sono **584/626 = 93,29%** con anello integro e **561/626 = 89,62%** con anello aperto, differenza **+3,67 punti percentuali** in favore dell'integrità iniziale. È un segnale descrittivo di robustezza meccanica, ma non la conferma richiesta. Inoltre il taglio iniziale e il rimborso energetico cambiano la distribuzione locale dei quanti disponibili.

### Sensibilità DESCRITTIVA per dimensione dell'anello

| Dimensione nativa | Mondi | Richiusura precoce lato tagliato con conduzione normale | Coesione a t120 integro | Coesione a t120 aperto |
|---|---:|---:|---:|---:|
| 4 particelle | 557 | 411 | 523 | 503 |
| 6 particelle | 57 | 41 | 49 | 46 |
| 8 particelle | 12 | 9 | 12 | 12 |

Per le strutture di sei e otto particelle il numero di casi è piccolo; non sono campioni preregistrati separati e non autorizzano conclusioni comparative forti. La selezione stessa è fortemente dominata dai quadrati di quattro particelle.

## Verifiche computazionali e tracciamento delle anomalie

- Campione principale concluso al **100%**, **640 seed consecutivi**, **16 shard identici al protocollo** e SHA256 della preregistrazione e dei moduli storici M6.4/M7.3 per ciascun frammento.
- **626** sorgenti selezionate e **14** negative archiviate; **2.504** fork da 120 tick prodotti e verificati attraverso \`World.check()\` e ledger energetico completo ai cinque checkpoint prefissati più l'output finale.
- Identità iniziale completa dei due bracci integri e dei due bracci aperti; la rimozione di un solo legame conserva il totale energetico, la dissipazione pregressa e lo stato RNG. **La prima successiva evoluzione nativa M6 è esattamente identica** all'interno delle coppie.
- Il regime di conduzione M7.3 non modificato viene effettivamente chiamato in \`intact_normal\` e \`opened_normal\`; il regime sperimentale che sopprime uno specifico insieme di legami ne replica le regole di ordinamento, gradiente di snapshot e budget del donatore con il solo filtro definito.
- I dati \`results.json\` sono stati riletti fuori dal merge GitHub Actions: 640 seed, 626 ring e 14 null, numeri discordanti **0/4/461/161** e **59/36/525/6**, verificati dalle righe grezze; tempi di richiusura mediana 11 tick sui 461 eventi originali realmente osservati.
- Il primo tentativo di implementazione CI [#44171596108](https://github.com/kkongiu/alife-lab/actions/runs/44171596108) aveva rilevato una **asserzione booleana mal formulata** nel controllo della conduzione disabilitata: pretendeva erroneamente zero trasferimenti sui lati dell'anello anche in bracci in cui non erano stati disabilitati. L'asserzione è stata corretta con due controlli espliciti, uno per ciascun braccio con conduzione soppressa; **non** sono state modificate le regole fisiche, le soglie, la selezione o il protocollo. L'esecuzione conclusiva #44171645566 ha superato tutte le regressioni e tutte le simulazioni.
- Un programma separato di replay indipendente con osservatore eventi originale M6.4, fonte fisica originale M7.3 e grafo ricostruito indipendentemente viene documentato separatamente, senza poter modificare le conclusioni preregistrate.

## Conclusione

Un'organizzazione circolare di materiale, **realmente emersa**, può rimanere stabile decine di tick; dopo l'apertura artificiale di un lato, **la reazione chimica nativa frequentemente richiude quello stesso lato** prima che se ne rompa un altro.

Ma i controlli causali non identificano una capacità di auto-mantenimento: **togliere il trasporto energetico dai lati superstiti non riduce visibilmente la frequenza di richiusura nel campione**, e il vantaggio dell'anello integro sulla coesione a 120 tick non supera il criterio preregistrato.

Quello osservato è soprattutto il **recupero passivo permesso dalla geometria e dalla chimica reversibile**, non una riparazione regolata, un metabolismo, una membrana selettiva, un genoma o una forma di vita.

### Orientamento per M7.12

Un esperimento più informativo isolerebbe il **motore fisico della richiusura**: stessa geometria iniziale aperta, identico bilancio di energia e sorteggi per coppia, confrontando:

1. Riformazione spontanea esatta dei due estremi immediatamente vicini vs un controllo con identica formazione energetica ma endpoints separati geometricamente, esplicitando che spostare atomi modifica necessariamente anche le collisioni con altri vicini;
2. Mantenimento della coesione dopo **due rotture controllate** in strutture cicliche naturali (una rottura apre l'anello, la seconda spezza anche la catena) per verificare se si accumula o meno un vantaggio nel recuperare la topologia originale;
3. Una definizione più forte e non tautologica di autoriparazione: riconoscimento locale del danno o causalità del materiale originale nel favorire la **stessa reazione** rispetto a un sistema chimicamente ed energeticamente comparabile non organizzato.

Un controllo specifico sulla **frequenza e sull'ordine delle collisioni native**, oltre che sull'esito energetico, potrebbe spiegare perché la semplice conduzione dei legami superstiti non sembra determinante. Fino ad allora, nessun risultato M7.11 dimostra vita digitale.
