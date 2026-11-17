# M7.7 — Come la conduzione dei legami influenza la crescita degli aggregati nativi

**Data:** 17 novembre 2026. **Stato:** esperimento e suite completa **PASS**, 320 nuovi mondi nativi, 960 fork e otto shard completi. **Ipotesi primaria sull'aumento delle opportunità energetiche: NON raggiunta. Ipotesi secondaria sulla formazione di legami incidenti PRIMA della prima rottura originale: RAGGIUNTA.** Nessuna prova di metabolismo, riproduzione o vita.

## Provenienza e protocollo

- [Preregistrazione M7.7 prima del codice e dei dati: commit `a344595`](https://github.com/kkongiu/alife-lab/commit/a3445955b5adb288ebcdf224527aede63fb7bbfe).
- [GitHub Actions definitivo: regressioni complete, 8 shard, 320/320 sorgenti, merge — PASS #44109230919](https://github.com/kkongiu/alife-lab/actions/runs/44109230919).
- [Dati grezzi di tutti i 320 seed e 960 fork, incluso ogni passaggio energetico monitorato — artifact #14338864283](https://github.com/kkongiu/alife-lab/actions/runs/44109230919/artifacts/14338864283).
- [PR #35 in bozza](https://github.com/kkongiu/alife-lab/pull/35); [nuovo osservatore `tools/m7_7_cohort_mechanism.py`](../tools/m7_7_cohort_mechanism.py).
- **Leggi originali `src/`, `master`, protocolli e generatori M7.5/M7.6 invariati**. Il modello fisico di trasporto è quello originale M7.3.

## Domanda scientifica

Dopo M7.5 e M7.6, la conduzione energetica attraverso i legami nativi era associata a un aumento coerente di circa sette punti percentuali della crescita **dello stesso aggregato originale**. Ma non si era capito **perché**, e non si osservava stabilizzazione dei legami originari.

M7.7 distingue tre possibili passaggi causali:
1. **Opportunità geometriche/chimiche**: quanti vicini esterni possono, per specie e valenza, formare un legame con i materiali originali?
2. **Accessibilità energetica**: quanti di quei contatti dispongono in entrambi gli atomi dell'energia necessaria alla reazione?
3. **Reclutamento reale prima della rottura**: quando si forma effettivamente un nuovo legame originale–esterno, è avvenuto prima che un legame originale si spezzasse o soltanto dopo che l'aggregato era stato danneggiato?

Un semplice aumento della formazione di legami globali non dimostra nessuno di questi tre passaggi.

## Disegno immutato e nuovo campione

**320 seed nuovi** `25001–25320`, esclusi da M7.5 e M7.6, otto shard da 40. Viene utilizzato **direttamente** il selettore originale M7.5, senza cambiare criteri o codice:

- Universi originali M6/M7.3 con 264 particelle, 24×24 periodico, zero legami iniziali, 16 sorgenti energetiche distribuite, movimento con costo 1 e nessuna catalisi.
- Prima componente chimicamente connessa **5–16 atomi**, almeno quattro legami, almeno uno slot di legame libero, almeno **due legami originali con 20 tick consecutivi non rotti**; prima selezione possibile al tick120, massimo tick500.
- Tre copie complete del medesimo stato naturale: **senza trasferimento**, **solo lungo legami originali presenti in quel tick** e **attraverso tutti i contatti cardinali**. Ognuna evolve per 120 passi; sola modifica fra le condizioni è la regola di trasferimento energetico M7.3 già documentata.
- Al termine di ciascun passo, dopo il trasferimento, un osservatore senza RNG conta le opportunità di prossimo legame sugli **ID materiali originali**: contatti geometrici non già legati; fra questi, compatibilità di specie e valenza; fra questi, energia di entrambe le particelle ≥ `world.formation_cost`. Un confronto implementativo diretto contro `alife.chemistry._candidate_pairs` garantisce che sia misurata esattamente la fattibilità statica nativa **al netto dei legami già presenti**.
- Gli eventi **reali** di formazione `BondEvent(kind='form')` e rottura `BondEvent(kind='break')` vengono registrati separatamente. Un legame rotto e riformato nello stesso tick **ha subito una rottura**. Il reclutamento prima di una rottura si arresta al primo tick che contiene un evento di rottura originale, perché nel motore la rottura avviene prima della formazione.
- Si misura inoltre il flusso energetico passivo esterno→ID originali e ID originali→esterno distinguendolo dai trasferimenti interni, che **non** aumentano l'energia totale del gruppo. Prima di ciascun trasferimento si ricostruisce il registro previsto e lo si confronta con la routine M7.3 originale, e si verifica bilancio totale e RNG inalterati dal solo trasferimento.

### Importante distinzione temporale

La chimica di M6 forma i legami **prima** del trasferimento energetico post-step aggiunto per M7.3. Quindi un contatto energeticamente idoneo misurato al termine del tick `t` è una **opportunità statica prospettica**: se i vicini, le energie o le valenze cambiano nel tick `t+1` prima della reazione, quella opportunità non è necessariamente una coppia che riceve la lotteria chimica. **Non** va trattata come la probabilità di reazione osservata in quello stesso tick e **non** costituisce una misura causale diretta di mediazione.

## Criteri preregistrati

- **Primario: maggiore esposizione a interfacce energeticamente pronte.** Fra almeno 40 seed idonei e almeno 40 confronti non pari su `somma_{t=1}^{120} contatti energeticamente qualificati`, almeno **2/3 dei seed non pari** devono avere più opportunità nel braccio `bond_only` che nel braccio `no_transfer`. La somma è analizzata **a livello seed**, senza usare ogni contatto/tick come osservazione indipendente.
- **Secondario: reclutamento reale prima di qualsiasi rottura originale.** Fra almeno 25 seed discordanti sulla presenza di almeno un nuovo legame originale–esterno `form` prima di qualsiasi `break` su un legame originale, almeno **2/3** devono favorire `bond_only` contro `no_transfer`.
- La crescita coerente originale a tick120, secondo il criterio M7.5, viene registrata **descrittivamente** sul campione completamente nuovo, senza spostare le soglie degli altri due endpoint.
- Nessuna scelta post-hoc di nuovi seed, tempi o metriche alternative.

## Risultati: 320/320 sorgenti, tutte reti arboree

**320/320** mondi hanno fornito una fonte nativa idonea, tutte selezionate al **primo tick permesso, t120**. Dimensione media **6,9531 atomi**; tutte le 320 reti sono **alberi**, senza cicli. Abbiamo quindi osservato sottoreti con legami invecchiati, non dimostrato la maturità dell'intera componente e non studiato membrane circolari.

| Misura per mondo o sorgente, media sui 320 | Nessun trasferimento | Solo legami | Tutti i contatti |
|---|---:|---:|---:|
| Contatti geometrico-materiali non ancora legati, somma nel followup | 494,12 | 482,43 | 414,01 |
| Contatti con specie e valenza ammissibili, somma | 110,58 | 86,21 | 46,69 |
| **Contatti anche energeticamente abilitati, somma** | 7,45 | **9,02** | **24,64** |
| Contatti specie/valenza ammissibili ma bloccati dall'energia | 103,13 | **77,20** | **22,04** |
| Nuovi legami reali con un estremo nel materiale originale, media | 0,3813 | **0,5000** | 1,2000 |
| Nuovi legami originali–esterni PRIMA della prima rottura, media | 0,1063 | **0,2375** | 0,5969 |
| Universi con almeno un reclutamento originale–esterno PRIMA della prima rottura | **31/320** | **68/320** | **147/320** |
| Aggregato originale cresciuto coerentemente al tick120 | **19/320** | **41/320** | **102/320** |
| Tutti i legami originali mai rotti nei 120 tick | 88/320 | 86/320 | 97/320 |
| Nuovi legami globali nei 120 tick, media | 20,07 | 27,49 | 56,77 |

**Attenzione alle somme sui 120 tick:** contare lo stesso contatto in più tick misura *esposizione cumulativa*, non centinaia di contatti indipendenti. I rapporti globali `contatti energeticamente idonei / contatti con specie e valenza ammissibili` sono circa **6,7%** senza trasferimento, **10,5%** con sola conduzione e **52,8%** con tutti i contatti. Si tratta di rapporti descrittivi fra somme, **non probabilità sperimentali di formazione di un legame**.

### Ipotesi primaria — esposizione energetica: NON RAGGIUNTA

Delle **237** coppie di seed non pari sulla somma di contatti energeticamente possibili:

- **140** sono favorevoli alla conduzione sui legami;
- **97** favorevoli al controllo senza trasferimento;
- **83** coppie sono pari.

Il rapporto preregistrato è **140/237 = 59,07%**, sotto il **66,67%** richiesto. I minimi di potenza amministrativi (≥40 mondi e ≥40 non pari) sono ampiamente soddisfatti; in questo esperimento `not_met_or_underpowered` va letto come **criterio non raggiunto**, non campione insufficiente.

La media cresce da 7,453 a 9,016 opportunità statiche su 120 tick (+1,563), ma un aumento della media **non sostituisce** il criterio basato sulle coppie preregistrate. La conduzione riduce anche la quantità media di contatti geometricamente e valenzialmente qualificati, presumibilmente per differente aggregazione e mobilità, quindi il meccanismo non può essere ridotto a “la rete offre sempre più interfacce”.

### Ipotesi secondaria — reclutamento reale prima della rottura: RAGGIUNTA

Confronto appaiato della variabile booleana *almeno un nuovo legame originale–esterno prima di qualunque rottura originale*:

| Confronto `bond_only` vs `no_transfer` | Seed |
|---|---:|
| Reclutamento soltanto con conduzione | **47** |
| Reclutamento soltanto senza conduzione | **10** |
| Reclutamento in entrambi | 21 |
| Nessun reclutamento in entrambi | 242 |

**47/57 = 82,46%** dei seed discordanti favoriscono la conduzione, oltre i **2/3** preregistrati. La quota di mondi con reclutamento pre-rottura passa da **31/320** senza conduzione a **68/320** con conduzione, una differenza assoluta di **+11,56 punti percentuali**.

Contando *eventi reali* (non solo universi con almeno uno), sono **34 eventi** di formazione originale–esterno pre-rottura senza trasferimento e **76** con conduzione sui legami. Questo segnale è più specifico della crescita globale: mostra che l'interazione con l'esterno può aumentare mentre il reticolo originario non ha ancora perso un suo legame.

**Non è però dimostrata una mediazione microscopica univoca dell'energia**, perché il trasporto altera la dinamica dei passi successivi, inclusi numero/ordine di estrazioni RNG e contatti futuri. La formazione pre-rottura può quindi essere aumentata da percorsi dinamici indiretti, oltre che dalla disponibilità energetica diretta.

### La prova immediata a geometria congelata, prima di evolvere

Un controllo complementare applica **un solo passaggio energetico lungo i legami**, su due copie dello **stesso stato sorgente congelato al tick di fork**, senza alcun `World.advance` e senza consumare RNG o modificare legami/posizioni:

- In **13/320** mondi aumenta il numero di coppie originale–esterno energeticamente idonee; in **0/320** diminuisce; in **307/320** resta uguale.
- Si effettuano in media **91,23** trasferimenti energetici lungo legami per universo in quel singolo passaggio. **Il gruppo di ID originali non guadagna energia netta** in tale intervento, poiché la componente selezionata è massimale: non ha legami verso ID estranei al gruppo al fork.
- Il test sintetico mostra un caso reale (non spontaneamente selezionato) in cui un quanto passato lungo un legame interno cambia l'energia di un atomo del bordo da 1 a 2 e rende energicamente possibile un legame con una particella esterna senza modificare geometria, valenza, RNG o energia totale. Ciò verifica che il **meccanismo immediato può esistere** sotto la fisica configurata.

Questa semplice prova non dimostra che i 68 reclutamenti osservati in dinamica siano stati causati esclusivamente da tale passaggio energetico. **13/320** è anzi un vincolo quantitativo sull'effetto immediato al fork: la maggior parte delle differenze si sviluppa durante la traiettoria.

### Crescita materiale a tick120 — risultato descrittivo preregistrato

Senza trasferimento crescono **19/320** aggregati originali; con legami conduttori **41/320**; con tutti i contatti **102/320**.

Confronto appaiato bond-only/no-transfer: **33** seed favorevoli alla conduzione, **11** al controllo, **8** entrambi, **268** nessuno. **33/44 = 75,0%** dei discordanti favoriscono la conduzione, raggiungendo la soglia numerica originale M7.5. Questo era un indicatore **descrittivo** in M7.7, non può sostituire il fallimento del criterio primario sulle opportunità energetiche.

I tre campioni disgiunti M7.5, M7.6 e M7.7 (320 seed ciascuno) mostrano rispettivamente:

| Campagna | Crescita solo nel controllo | Crescita solo con conduzione | Discordanti favorevoli | Differenza assoluta |
|---|---:|---:|---:|---:|
| M7.5 | 18 | 41 | 41/59 = 69,5% | +23/320 = +7,19 pp |
| M7.6 | 22 | 43 | 43/65 = 66,2% | +21/320 = +6,56 pp |
| M7.7 | 11 | 33 | 33/44 = 75,0% | +22/320 = +6,88 pp |

Il saldo combinato **+66/960 = +6,875 punti percentuali** è descrittivamente molto stabile. **Non** rettifica il criterio M7.6 fallito, non è una prova di metabolismo e non equivale a una replica dell'identico endpoint *meccanicistico* M7.7.

## Controlli tecnici e incidente di validazione

**Ricalcolo separato del dataset ZIP originale:** esatti 320 seed `25001–25320`, 320 sorgenti selezionate e 8 primi fork ricontrollati dalla routine originale M7.5; verificati i **960 bilanci energetici finali**, la completezza di cinque checkpoint e 120 misure post-step di opportunità per ogni fork, l'identità della somma dei candidati per seed e i gruppi discordanti **47/10/21/242** e **33/11/8/268**. Tutto coerente con il merge CI.

Gli iniziali workflow M7.7 si sono arrestati durante l'implementazione dei controlli, **prima di produrre il dataset finale**, per due errori di validazione osservazionale (nessuna variazione delle regole o del protocollo):
1. Un test sintetico assumeva erroneamente che, con il trasporto su tutti i contatti, nessuna particella esterna potesse fornire energia a una della sorgente. Corretto il test; la fisica originale prevede tale trasferimento.
2. L'osservatore pretendeva che le coppie della funzione preliminare `_candidate_pairs` fossero tutte nuove; in realtà, la funzione originale può enumerare due particelle **già legate** se hanno ancora slot liberi: la formazione le scarta **dopo** il controllo probabilistico. Corretto l'osservatore affinché elimini esplicitamente le coppie già legate prima di confrontare l'insieme dei nuovi potenziali legami. Questo rispetta la definizione preregistrata di contatto *non ancora legato* e non modifica alcuna legge M6.

Un nuovo test di regressione copre espressamente il caso. La suite completa e gli otto shard finali sono **PASS** nel workflow definitivo. I primi workflow falliti sono conservati nella cronologia Actions e non sono risultati scientifici.

## Interpretazione e limiti

Il risultato M7.7 suggerisce una **direzione meccanicistica più specifica**: la conduzione lungo reti di legami già esistenti è associata a più **reclutamento chimico originale–esterno prima che i vecchi legami si rompano** e a una modesta maggior crescita coerente dello stesso materiale. Ma la misura cumulativa delle **opportunità energeticamente ammissibili** non è abbastanza uniformemente favorita nei seed per superare il criterio primario.

Questo suggerisce che la crescita potrebbe dipendere da **dove e quando** un atomo energeticamente pronto incontra un nuovo vicino, oppure dalla competizione con la saturazione della valenza e dal cambiamento della dinamica, più che dal semplice numero cumulativo di occasioni statiche. È **un'ipotesi di ricerca**, non una dimostrazione.

**Non dimostrato:** auto-mantenimento dei vecchi legami (il criterio è ancora negativo), riparazione, struttura circolare o membrana (tutte le sorgenti sono alberi), regolazione attiva dell'energia, informazione ereditaria, replicazione e vita artificiale.

### Proposta M7.8

Il passo scientifico più rigoroso ora è un test causale **a geometria invariata e con tentativi di legame controllati**. Bisognerebbe misurare, sullo stesso stato nativo naturale e senza cambiare posizioni/valenze o consumare RNG prima dell'intervento, se redistribuire un quanto lungo un legame aumenta effettivamente il **numero di nuove coppie reattive** al successivo istante di formazione. Un controllo parallelo con la **stessa distribuzione energetica complessiva ma energia riassegnata lungo coppie non legate** separerebbe i vantaggi del grafo dei legami dalla semplice levigatura dell'energia. Una seconda prova dovrebbe osservare formazione effettiva con una sorgente di numeri casuali **accoppiata per coppia/ID**, non mediante uno stream globale che diverge tra i mondi dopo il fork. Ciò richiede un banco meccanicistico sperimentale esterno, non alterazioni retroattive della chimica M6.

Fino a tali verifiche, abbiamo soltanto un **candidato concreto a feedback organizzativo**, non un organismo digitale.
