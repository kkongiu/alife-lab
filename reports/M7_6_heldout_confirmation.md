# M7.6 — Replica indipendente di M7.5: vantaggio coerente nella direzione, ma soglia preregistrata NON raggiunta

**Data:** 17 novembre 2026. **Esito primario preregistrato:** `not_met_or_underpowered` (**soglia numerica non raggiunta, campione adeguato**). **Esito secondario:** `not_met_or_underpowered` (**soglia non raggiunta**).

**Conclusione scientifica:** il secondo campione mostra un vantaggio di crescita degli **stessi aggregati materiali** molto simile a M7.5, ma il criterio formalmente congelato di almeno 2/3 dei confronti discordanti favorevoli alla conduzione è mancato di **un solo seed discordante**. Non correggere retroattivamente la soglia, non riclassificare la replica come positiva.

## Tracciabilità completa

- [Protocollo M7.6 congelato prima del runner e dei nuovi risultati: commit `17571b4`](https://github.com/kkongiu/alife-lab/commit/17571b435dec4c42ba5e82e69ca4fd2b3512f500).
- [Protocollo M7.5 originale, congelato prima dell'esperimento precedente: commit `7bcbe0e`](https://github.com/kkongiu/alife-lab/commit/7bcbe0ec5f30657dc5f58d795d3fb3c428b9a463).
- [Workflow principale: suite regressioni PASS, 8 shard, 320/320 mondi, merge rigoroso — #44036962278](https://github.com/kkongiu/alife-lab/actions/runs/44036962278).
- [Dati grezzi completi 320 mondi/960 fork M7.6, inclusi tutti gli esiti negativi: artifact #14307926244](https://github.com/kkongiu/alife-lab/actions/runs/44036962278/artifacts/14307926244).
- [PR sperimentale #34, in bozza](https://github.com/kkongiu/alife-lab/pull/34).
- Script di replica: [`tools/m7_6_heldout_replication.py`](../tools/m7_6_heldout_replication.py).

**Integrità del codice precedente:** la simulazione fisica, il selettore di reti parzialmente mature, il tracciatore di eventi e il generatore dei tre fork vengono chiamati **direttamente dal modulo M7.5 originale**, senza copie alterate. Per valutare gli esiti si usa addirittura la funzione originale `M7.5.summarize()`: soltanto all'interno della copia temporanea destinata a quella funzione i numeri seed vengono mappati ai corrispondenti indici del vecchio intervallo, perché la funzione verificava rigidamente la sequenza 23001–23320. **I seed fisicamente simulati, gli stati RNG, le identità dei materiali e i file di output restano 24001–24320.** I protocolli e script M7.5 non vengono modificati. Gli hash dei file originali e del nuovo protocollo sono presenti in tutti gli shard.

## Disegno confermativo invariato

- **320 seed nuovi, non sovrapposti:** `24001–24320` (M7.5 era `23001–23320`). Un seed rappresenta un'unità sperimentale indipendente; i tre fork della stessa sorgente costituiscono una coppia/tripla controllata, non nuovi campioni.
- Ogni universo parte con **264 particelle native, zero legami**, reticolo 24×24 periodico, moto a costo energetico 1, 16 sorgenti distribuite, chimica M6 originale senza catalisi.
- Esame degli stati da tick1 a tick500; **dal tick120** si prende la **prima componente connessa massimale** di 5–16 particelle, con almeno quattro legami originali, valenza disponibile e almeno **due legami materiali originali con almeno 20 tick continui** senza eventi di rottura. Il più piccolo gruppo di ID al primo tick idoneo viene selezionato, senza conoscere gli esiti futuri.
- Tre copie identiche dello stato sorgente, per **120 tick**: nessun trasferimento, trasferimento lungo legami chimici nativi, trasferimento attraverso tutti i contatti cardinali.
- La **crescita coerente** a 120 tick richiede che **tutti gli ID originali** siano ancora in una stessa componente con almeno **un nuovo ID esterno**. La persistenza dei legami originali è distinta: nessun evento di rottura dei legami originari in 120 tick, anche se un legame successivamente si riforma.
- Le soglie preregistrate M7.5 sono **invariate**: almeno 40 sorgenti selezionate, almeno 25 confronti discordanti, e almeno **2/3 discordanti** favorevoli al trasporto sui legami rispetto all'assenza di trasporto, sia per crescita primaria sia separatamente per persistenza secondaria.
- Ogni sorgente viene osservata senza modificare la fisica. Stato del mondo e RNG identici ai tre fork, e prima rottura dei legami originali allo stesso tick1 per tutti i bracci.

## Esiti della nuova replica

**320/320** sorgenti hanno superato i criteri di selezione senza sostituzioni; tutte erano disponibili già al **tick120**, il primo tick ammesso, e **tutte le 320 strutture sono alberi, non cicli**. Dimensione media della struttura **7,0438 particelle**, media di **5,8781 legami** con almeno 20 tick consecutivi osservati. La selezione richiede due legami invecchiati, **non** garantisce che l'intera componente abbia vissuto con identica composizione e topologia per 20 tick.

| Esito a 120 tick, su 320 stati sorgente identici per braccio | Senza conduzione | Soltanto lungo legami | Tutti i contatti |
|---|---:|---:|---:|
| Crescita coerente dello stesso gruppo materiale | **28/320** | **49/320** | **106/320** |
| Crescita coerente almeno una volta in 120 tick | 44/320 | 80/320 | 169/320 |
| Nessuna rottura degli originali | **76/320** | **85/320** | 89/320 |
| Nuovi legami incidenti agli ID originali, media | 0,4031 | **0,5437** | 1,1031 |
| Nuovi legami incidenti PRIMA di qualsiasi rottura originale, media | 0,1125 | **0,2219** | 0,5094 |
| Nuovi legami GLOBALI nei 120 tick, media | 19,1062 | 27,2156 | **56,5625** |
| Energia trasferita internamente fra ID originali, eventi medi | 0 | **131,9594** | 230,5125 |
| Energia ricevuta per scambio passivo dall'esterno del gruppo, eventi medi | 0 | 4,7812 | **67,7219** |
| Energia ceduta per scambio passivo all'esterno, eventi medi | 0 | 5,1344 | 108,7062 |

I flussi contano passaggi di un quanto: lo stesso quanto può essere trasferito ripetutamente. **Trasferire energia fra due ID originali non accresce l'energia totale del gruppo.** Per il regime di sola conduzione sui legami, il saldo passivo medio al confine è leggermente **negativo** (−0,3531 eventi/quantità per sorgente), quindi il miglioramento di crescita **non dimostra un assorbimento netto di energia maggiore nel gruppo**. Le sorgenti esterne di energia, la formazione/rottura di legami e la dissipazione hanno altri contributi al bilancio.

### Verdetto formale A — Crescita stessa struttura: `not_met_or_underpowered`

| Confronto appaiato bond_only vs no_transfer, esito crescita a t120 | M7.5 | M7.6 |
|---|---:|---:|
| Crescita solo con conduzione | 41 | **43** |
| Crescita solo nel controllo | 18 | **22** |
| Crescita in entrambi | 10 | **6** |
| Nessuna crescita in entrambi | 251 | **249** |
| Quota favorevole conduzione fra discordanti | 41/59 = **69,49%** | 43/65 = **66,15%** |
| Criterio preregistrato ≥2/3 | **PASS** | **NON RAGGIUNTO** |
| Differenza assoluta fra i regimi | +23/320 = **7,19 punti %** | +21/320 = **6,56 punti %** |

Il campione M7.6 soddisfa ampiamente i minimi di selezione e discordanza (320 sorgenti e 65 discordanti). La soglia era 66,666…%, pari ad almeno **44/65** discordanti favorevoli: si osservano **43**. Pertanto il fallimento è **di soglia**, non di potenza minima: il nome tecnico restituito dal codice resta `not_met_or_underpowered`, ma va esplicitato che in questo caso la parte `underpowered` non è la causa.

La **direzione** e la **dimensione** del vantaggio di crescita sono sorprendentemente simili nei due campioni indipendenti. Questo non autorizza a trasformare M7.6 in una conferma formale del criterio preregistrato. Un esame esplorativo *diverso* (test binomiale simmetrico sui 65 discordanti rispetto al 50/50) restituisce **p a due code ≈ 0,0125**, ma **non** era la regola di successo preregistrata e non la sostituisce. È evidenza descrittiva utile sul segno, non una sanatoria del criterio fallito.

### Verdetto formale B — Sopravvivenza degli originali: `not_met_or_underpowered`

Nei 121 confronti discordanti:

- **65** favoriscono il gruppo con conduzione;
- **56** favoriscono il controllo;
- **20** conservano tutti i legami in entrambi;
- **179** non li conservano in nessuno.

Quota favorevole **65/121 = 53,72%**, sotto il 66,67% prefissato. Anche qui il numero di discordanti supera la soglia minima; il risultato non dimostra che la conduzione renda i legami originali più resistenti.

## Sguardo sui due esperimenti, senza cambiare l'esito confermativo

I due campioni `23001–23320` e `24001–24320` sono **disgiunti**, **320+320 = 640** universi con gli stessi trattamenti e gli stessi endpoint.

Aggregando **a titolo descrittivo** i 640 casi:

- Crescita nello stesso aggregato: **56/640** senza conduzione, **100/640** con conduzione, differenza **+44/640 = +6,875 punti percentuali**.
- Confronti discordanti: **84 favorevoli conduzione contro 40 favorevoli controllo**, pari a 84/124 = **67,74%** fra discordanti.
- Tutti i 640 sorgenti selezionati sono **alberi**, senza cicli.

Questa aggregazione è informativa sulla stabilità della direzione dell'effetto, ma è **post-hoc rispetto alla decisione confirmatoria M7.6**: non modifica il verdetto M7.6 non raggiunto, né dimostra riproduzione biologica.

## Audit, controlli e limiti

- GitHub Actions #44036962278: **pytest integrale PASS**, otto shard fissi PASS, aggregazione finale PASS, 320/320 semi nuovi; ogni shard contiene l'hash del protocollo M7.6 e del codice/protocollo M7.5 realmente eseguito.
- **Otto controlli di replay senza osservatore** (primo seed selezionato di ciascuno shard), oltre ai normali invarianti di hash, RNG, legami, energia e primo passo nel tracciatore originale.
- Rilettura separata del ZIP primario: verificati il campione 24001–24320, la completezza 320/320, i gruppi discordanti **43/22/6/249** per la crescita e **65/56/20/179** per la persistenza. Nessun seed vecchio M7.5 entra nel criterio primario.
- Il numero di semi e la decisione non sono stati adattati al risultato; la differenza di un solo seed rispetto alla soglia è **registrata come fallimento**, non come risultato positivo.

**Limiti scientifici:**
- La selezione ammette soltanto reti native arboree e tutte risultano pronte al primo tick ammesso; la durata dell'intera rete non è nota.
- La conduzione lungo legami è una nuova legge aggiunta intenzionalmente negli esperimenti M7, non un comportamento inventato o selezionato spontaneamente da una struttura.
- Dopo il fork i mondi possono usare flussi RNG globali diversi: abbiamo confronti causali del regime di conduzione, non la dimostrazione di un'unica micro-reazione biologica di auto-mantenimento.
- Il tasso elementare di rottura dei legami rimane costante; l'endpoint di persistenza fallisce in entrambe le campagne.
- Crescita coerente di un gruppo di ID **non equivale a discendenza, ereditarietà, replicazione, metabolismo o vita artificiale**.

## Indicazione per la ricerca successiva

È più produttivo comprendere **perché** la conduzione favorisce modestamente la crescita materiale ma **non** la persistenza dei legami, prima di incrementare ancora i seed senza cambiare domanda.

Un eventuale M7.7 dovrebbe preregistrare un audit meccanicistico di flussi energetici, contatti/forme e primo nuovo legame **sullo stesso materiale**, con controlli per topologia, composizione, opportunità di reclutamento e divergenza del RNG. Si può anche valutare una nuova conferma ancora identica per quantificare la robustezza, ma senza cambiare retroattivamente la soglia M7.6.

**Finora nessuna prova di organismo digitale o replicazione ereditaria.**
