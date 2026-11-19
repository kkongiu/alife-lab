# M8.1b — Audit retrospettivo del blocco geometrico B/H (256 mondi)

**19 novembre 2026 — audit di sola lettura COMPLETATO, GitHub Actions PASS. Nessuna nuova simulazione.**

## Riproducibilità e dati originali

- [Run scientifico originale M8.1b #44491013828 — 256 mondi, regressioni PASS, gate corridoi e figli NO_GO](https://github.com/kkongiu/alife-lab/actions/runs/44491013828).
- [Artefatto originale delle 256 traiettorie #14512363685](https://github.com/kkongiu/alife-lab/actions/runs/44491013828/artifacts/14512363685).
- [Run diagnostico indipendente su eventi archiviati #44574529716 — PASS](https://github.com/kkongiu/alife-lab/actions/runs/44574529716).
- [Artefatto diagnostico completo, 256 voci per seed e report automatico #14556081363](https://github.com/kkongiu/alife-lab/actions/runs/44574529716/artifacts/14556081363).
- [Script di ricostruzione da eventi senza import del simulatore](https://github.com/kkongiu/alife-lab/blob/analysis/m8-1b-archived-spatial-bottleneck/tools/m8_1b_frozen_trace_audit.py).

Il diagnostico rilegge per **tutti i 64 seed × 4 bracci** soltanto le condizioni iniziali e gli eventi originali `hop`, `adsorb`, `B_form`, `B_break`, `H_release`: aggiorna posizioni, ID, B/H, bagno, energia, dissipazione; verifica i bilanci di materia/energia **dopo ogni evento**, le condizioni fisiche di ogni hop, la prima catena e la disponibilità del corridoio rispetto al rilevatore originale. **256/256 ricostruzioni PASS.** Nessun nuovo random, nessun `WorldM8.step`, nessuna legge modificata. Il verdetto M8.1b resta **NO_GO**.

## Risultati diagnostici principali

| Misura | Statico templating | Mobile templating | Mobile shuffled | Mobile senza templating |
|---|---:|---:|---:|---:|
| Mondi con prima catena B4 nativa | 29/64 | **42/64** | 42/64 | 61/64 |
| Tick mediano di prima catena | 26 | **43,5** | 43,5 | 58 |
| Occupazione mediana alla prima catena (su 50 celle) | 34 | **39** | 39 | 20 |
| Energia libera mediana alla prima catena (su 500) | 442 | **343,5** | 343,5 | 389 |
| Migliore fila laterale: mediana celle libere alla prima catena (su 4) | 1 | **0** | 0 | 3 |
| Mondi in cui la prima catena ha almeno un blocco B laterale alla nascita | 28/29 | **39/42** | 39/42 | 24/61 |
| Mondi che vedono almeno 3 celle libere nella medesima fila durante la vita della prima catena | 0/29 | **1/42** | 1/42 | 50/61 |
| Mondi che vedono 4 celle laterali libere contemporaneamente con genitore integro | **0/29** | **0/42** | 0/42 | 42/61 |
| Mondi con almeno una cattura H dalla prima catena | 16/29 | **13/42** | 13/42 | 0/61 |
| Catture H dalla prima catena, eventi complessivi | 20 | **29** | 29 | 0 |

### La natura dei blocchi di superficie

Frazioni di **celle-tick nella/e fila/e adiacente/i al primo genitore mentre è ancora integro**, non frazioni di mondi indipendenti:

| Stato della cella laterale | Mobile con templating | Mobile senza templating |
|---|---:|---:|
| Occupata da monomero che presenta ≥1 legame B | **97,517%** | 23,131% |
| Occupata da monomero legato soltanto con H | 0,543% | 0% |
| Occupata da monomero isolato (senza B/H) | 1,876% | 9,940% |
| Libera | **0,064%** | **66,929%** |

I 42 mondi con prima catena B4 del braccio mobile con templating raggiungono, durante la vita del primo genitore, al massimo questo numero di siti vuoti nella **stessa** fila laterale:

| Massimo simultaneo osservato | Numero di mondi |
|---|---:|
| 0 celle libere | **32/42** |
| 1 cella libera | 7/42 |
| 2 celle libere | 2/42 |
| 3 celle libere | 1/42 |
| 4 celle libere | **0/42** |

I genitori non scompaiono immediatamente: durata media con il quartetto originario ancora in posizione e tre legami B integri circa **184,19 tick** nei mondi che lo formano. Dunque nel campione il mancato corridoio non è principalmente spiegato da genitori troppo effimeri.

### Diagnosi tecnica

- La **sola mobilità di monomeri senza B né H** non può spostare le particelle che costituiscono il **97,5% delle occupazioni laterali** nel braccio attivo, poiché hanno almeno un legame B. La frazione può includere la stessa particella misurata ripetutamente in tick successivi e non è una frequenza di monomeri indipendenti.
- Il primo genitore attivo nasce con **39/50** celle occupate in mediana, benché disponga ancora di **343,5/500** unità di energia libera in mediana; tutti i 42 mondi con un primo genitore attivo hanno almeno 2 unità disponibili a quell'istante. Quindi un **deficit energetico immediato alla nascita** non basta a spiegare il blocco.
- Nel controllo senza templating la densità resta 20/50, perché il modello M8.0 ha `P_BACKGROUND=0`: esso è quindi un **controllo meccanico/geometrico**, non un controllo a identiche opportunità di adsorbimento. La grande differenza 0/42 vs 42/61 nei corridoi non isola l'effetto di una singola interazione B o H.
- Il canalizzare il problema verso i legami B è una **spiegazione geometrico-meccanica direttamente supportata dalle posizioni e dai legami registrati**. Non è ancora una dimostrazione causale che un preciso tasso di desorbimento, scambio o rottura B produrrebbe figli informativi.
- Le 28 opportunità potenziali di cattura dalla prima catena con energia nel braccio attivo sono **celle-tick a fine passo**, mentre le 29 catture sono eventi durante i passi fisici; i due numeri non sono denominatori numericamente confrontabili perché tra una fotografia e il passo successivo operano rotture, hop e nuovi legami.

## Implicazioni per una futura M8.1c (NON eseguita)

Il prossimo esperimento dovrebbe isolare **una sola nuova legge fisica di turnover delle superfici** che renda nuovamente disponibili le celle occupate, esplicitando:

1. Quali stati materiali possono lasciare un sito (monomero legato B, legato H, isolato), come vengono trattati tutti i legami B/H e se il materiale torna al bagno o si sposta localmente; una sola trasformazione elementare descritta per intero.
2. Bilanci esatti: **nessuna perdita o creazione materiale, energia limitata**, conto dell'energia immagazzinata nei B/H, dissipazione di ogni rilascio e probabilità non teleologica indipendente da identità di parentela.
3. Nuovi seed, preregistrazione e controlli causali diversi dalla chimica immobile. Verificare **se nasce spazio mentre il genitore è vivo**, e separatamente se si formano figli con provenienza H verificata e 20 tick di persistenza.
4. Arresto scientifico preregistrato in caso di assenza del corridoio o del prodotto; nessuna riscrittura retroattiva degli esperimenti 8.0, 8.1a, 8.1b.

**Non è stata dimostrata vita, ereditarietà multigenerazionale o replicazione spontanea.** Questo report è un'analisi meccanica post-hoc su dati preesistenti e non una nuova prova confermativa.
