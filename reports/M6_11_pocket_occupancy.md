# M6.11 — Un primo confinamento geometrico NATIVO di una particella mobile (8 tick)

**Data:** 16 novembre 2026. **Stato:** esperimento preregistrato completato; GitHub Actions [PASS #43840364693](https://github.com/kkongiu/alife-lab/actions/runs/43840364693). **Decisione preregistrata:** `no_confirmed_trapping` (nessun mondo ha raggiunto la soglia dei 30 tick). L'osservazione positiva di 8 tick è documentata ma **non cambia** la decisione.

- [Protocollo fissato PRIMA del codice: commit `83b3356`](https://github.com/kkongiu/alife-lab/commit/83b3356748895a066b456b1fd9323e92470361c4)
- [Dati grezzi completi, inclusi tutti i casi nulli — artifact #14212966917](https://github.com/kkongiu/alife-lab/actions/runs/43840364693/artifacts/14212966917)
- Base: ramo M6.10, **leggi M6 immutate, nessun anello o monomero artificiale, `master` invariato**.

## Domanda

Un anello spontaneo di otto particelle che delimita esattamente una cella 3×3 può nascere mentre il suo centro contiene già una particella nativa mobile? L'assenza di occupanti in M6.10 è universale, oppure dipende dal campionamento? Com'è distribuita l'occupazione centrale dei gusci occupati con 0–5, 6, 7 o 8 legami nativi?

## Disegno sperimentale

100 seed nuovi `10001–10100`, due densità: baseline (200 particelle) ed enriched (264), **200 universi × 600 tick = 120.000 tick-mondo**; griglia periodica 24×24, zero legami iniziali, chimica originale M6, campionamento dei cerchi esatti a ogni tick. Ogni 20 tick sono campionati tutti i 576 possibili centri 3×3 (30 checkpoint per mondo), mantenendo solo quelli con tutti e otto i siti del perimetro occupati da particelle native. Si contano gli otto possibili legami lungo il bordo e si osserva lo stato della cella centrale. Un episodio termina all'effettiva rottura di un legame originale, anche se si riforma nello stesso tick.

**Unità indipendente:** universo/seed, non il singolo episodio e non i checkpoint ripetuti. Esempi e rapporti sui gusci sono descrittivi, non test causali.

## Risultati primari

| Misura | Baseline, 100 mondi | Enriched, 100 mondi | Totale |
|---|---:|---:|---:|
| Mondi con cavità native esatte | 3 | 4 | **7/200** |
| Episodi di anello | 12 | 5 | **17** |
| Insiemi materiali distinti con cavità | 3 | 4 | **7** |
| Episodi a centro vuoto alla nascita | 12 | 4 | **16** |
| Episodi con particella al centro alla nascita | 0 | **1** | **1** |
| Mondi con particella mobile intrappolata ≥30 tick | 0 | 0 | **0** |

I 17 episodi **non** sono 17 universi indipendenti: includono aperture e richiusure della stessa struttura.

### Caso positivo: `enriched-10093`

- **Tick 175:** gli otto siti dell'anello erano già occupati e **7/8 legami** perimetrali formati; la cella centrale era occupata da una particella nativa mobile libera.
- **Tick 176:** la chiusura naturale dell'ottavo legame ha prodotto un anello esatto; il residente è **ID 98**, grado 0, probabilità di movimento >0, centro **(12,10)**.
- **Tick 176–183 compresi:** bordo materiale geometricamente integro per **8 tick osservati** e residente inalterato nella casella centrale. Il criterio di 30 tick non è raggiunto.
- **Tick 184 (interruzione inferita dal conteggio degli episodi):** una rottura nativa di uno dei legami originari termina l'episodio, classificata `original_edge_broken`. Questo non dimostra che il residente si sia spostato immediatamente dopo la rottura.

Per evitare ambiguità: l'immobilità osservata è una conseguenza geometrica dell'occupazione delle quattro celle cardinali attorno al centro e della regola locale di movimento, non un comportamento attivo. Il sistema non possiede membrane biologiche, genomi, metabolismo o riproduzione.

### Controlli di occupazione ai checkpoint fissi

| Densità | Legami nativi perimetrali | Gusci osservati ai checkpoint | Centri vuoti | Monomeri mobili liberi al centro |
|---|---:|---:|---:|---:|
| Baseline | 0–5 | 1326 | 556 (41,9%) | 35 (2,6%) |
| Baseline | 6 | 330 | 240 (72,7%) | 14 (4,2%) |
| Baseline | 7 | 137 | 130 (94,9%) | 2 (1,5%) |
| Baseline | 8 | 35 | 35 (100%) | 0 |
| Enriched | 0–5 | 6509 | 2597 (39,9%) | 289 (4,4%) |
| Enriched | 6 | 1296 | 853 (65,8%) | 114 (8,8%) |
| Enriched | 7 | 292 | 205 (70,2%) | 68 (23,3%) |
| Enriched | 8 | 15 | 14 (93,3%) | 1 (6,7%) |

La tabella comprende gusci con tutti gli otto siti fisicamente occupati anche se la struttura non è un componente ciclico isolato: **otto legami perimetrali non equivalgono necessariamente a un anello indipendente esatto**. Centri classificati come non vuoti e non liberi possono contenere particelle legate ad altri elementi; per questo il campionamento dei gusci non misura direttamente la nascita di cavità esatte. I checkpoint ripetuti osservano spesso le stesse strutture: nessuna percentuale è una stima inferenziale indipendente per tick.

## Interpretazione

**Novità concreta:** M6.10 aveva osservato nove episodi di cavità tutte vuote. M6.11, usando **nuovi seed**, osserva almeno un caso in cui una particella nativa mobile è già presente mentre l'ultimo legame si forma spontaneamente e viene confinata per 8 tick. Pertanto i centri vuoti **non sono una necessità universale** del motore.

**Limite essenziale:** l'evento è unico in 200 mondi, e non soddisfa il criterio preregistrato di almeno 30 tick in due mondi. Non autorizza conclusioni sulla frequenza di compartimentazione stabile, né su causalità, auto-mantenimento, membrane, ereditarietà o vita.

**Meccanismo più semplice compatibile coi dati:** configurazione locale quasi chiusa (7/8 legami) attorno a un monomero, seguita da normale reazione di formazione dell'ultimo legame. Non è stata osservata crescita intenzionale di una parete attorno a un residente; le regole non hanno un obiettivo.

## Riproducibilità e qualità

- GitHub Actions **PASS**: suite completa di regressione, test su gusci sintetici e 200 universi.
- Due replay nativi senza osservatore (baseline/enriched seed 10001) producono stessi hash completi, RNG, energia, dissipazione, formazioni e rotture di legami.
- Il programma impedisce all'osservatore di consumare RNG e verifica l'identità del residente mentre il bordo originario permane.
- Dati grezzi di tutti i 200 mondi, inclusi casi zero, presenti nell'artefatto GitHub Actions.
- Sono possibili dipendenze tra episodi della stessa struttura e bias temporale dei checkpoint. Non sono stimati p-value da snapshot non indipendenti.

## Successivo test consigliato

**M6.12:** preregistrare una replica indipendente su nuovi seed e un controllo condizionale sulle strutture 7/8 già occupate. Confrontare la probabilità di chiusura dell'ottavo legame e la durata del confinamento in presenza/assenza di residente, abbinando tipo di specie, energia locale, geometria e tempo. Distinguere nascita della cavità da ri-formazione. Il confronto deve essere osservazionale o controfattuale esplicitamente etichettato; nessuna modifica alle leggi fisiche fino a decisione separata.
