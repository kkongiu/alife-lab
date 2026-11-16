# M7.4 — La conduzione energetica favorisce i legami nel mondo, ma non la crescita della stessa struttura

**Data:** 16 novembre 2026. **Stato:** esperimento preregistrato terminato, regressioni e quattro shard **PASS**. **Entrambi gli endpoint di feedback strutturale non raggiunti**. Lo studio è particolarmente utile perché evita di confondere il maggior numero di legami nel mondo con l'auto-mantenimento di un oggetto materiale specifico.

## Tracciabilità

- [Protocollo fissato PRIMA dell'implementazione e di qualsiasi risultato: commit `2181472`](https://github.com/kkongiu/alife-lab/commit/21814727cca8f47693b63201349af7910c1ee03c).
- [GitHub Actions PASS: tutti i test, 160/160 mondi sorgente, tre fork per sorgente, quattro shard + merge #43919895815](https://github.com/kkongiu/alife-lab/actions/runs/43919895815).
- [Dataset integrale di tutti i fork e i risultati nulli: artifact #14254146168](https://github.com/kkongiu/alife-lab/actions/runs/43919895815/artifacts/14254146168).
- [Codice riproducibile `tools/m7_4_material_feedback.py`](../tools/m7_4_material_feedback.py).
- [PR #32 in bozza](https://github.com/kkongiu/alife-lab/pull/32); `master` e `src/` immutati.

## Domanda e motivazione

In M7.3, rendere i legami conduttori di energia aumentava il numero di **nuovi legami globali** negli ultimi 100 tick. Non sapevamo se quei nuovi legami coinvolgessero effettivamente l'aggregato che trasportava energia.

M7.4 fissa un identificatore materiale e confronta **copie dello stesso stato fisico nativo**. La domanda è: *una struttura che conduce energia attraverso i propri legami ha maggiore probabilità di crescere coerentemente o conservare i propri legami originali, rispetto allo stesso aggregato nello stesso mondo senza conduzione supplementare?*

**Non si testano né vita artificiale né organismi**. La fisica di rottura M6 rimane a probabilità costante; qualsiasi vantaggio a lungo termine può riflettere sequenze chimiche diverse e desincronizzazione successiva del RNG.

## Protocollo preregistrato

- **160 nuovi seed `22001–22160`**; l'universo originale di ciascuno inizia con 264 particelle native, zero legami, sorgenti disperse originali M7.3, movimento con costo 1, senza catalisi; nessuna struttura o replicatore inserito artificialmente.
- Cercare **la prima componente connessa naturale di 3–10 particelle, almeno due legami originali e almeno una valenza disponibile**, nei primi 250 tick; selezionare la componente con identificativi materiali ordinati lessicograficamente minori al primo tick disponibile. **Al massimo una sorgente per seed**, nessuna selezione sugli esiti futuri.
- Clonare lo stato completo (posizioni, specie, tutte le energie, legami, contatori, serbatoi e stato RNG) nei regimi: **nessun trasferimento, solo legami, tutti i contatti cardinali**. Evolvere per **120 tick** in seguito.
- Gli ID del materiale iniziale sono persistenti. Un **nuovo legame incidente** è una FORMAZIONE chimica con esattamente uno degli estremi negli ID originali e l'altro esterno. Non va confuso con qualsiasi nuovo legame nel mondo.
- **Crescita coerente dello stesso materiale:** al checkpoint il componente chimico che contiene **tutti gli ID originali** deve includere almeno una particella nuova. Se gli ID originali sono frammentati, anche se qualche frammento acquista particelle, la crescita coerente **non** viene conteggiata.
- **Persistenza:** nessun evento di rottura di qualunque legame originale, anche se quel legame viene ricostituito nello stesso tick. Le ricostituzioni si riportano separatamente; non costituiscono auto-riparazione attiva.
- Scambio energetico: dopo ogni passo M6 si trasferiscono quanti solo attraverso il tipo di collegamento permesso per il braccio, conservando energia e RNG; si misurano i passaggi lungo **gli stessi legami originali**, i passaggi interni fra membri originali e gli scambi attraverso il confine del materiale originario.
- **Controllo falsificabile:** i legami originali che si rompono nel primo tick dopo il fork devono coincidere nei tre bracci. Il trasporto non è ancora avvenuto e la probabilità di rottura nativa è indipendente dall'energia.
- Un clone senza alcun trasporto viene anche replicato separatamente nel primo seed selezionato di ognuno dei quattro shard.

### Soglie preregistrate

**Crescita coerente:** almeno **30 sorgenti selezionate** e almeno **20 coppie discordanti**; fra le coppie discordanti sul risultato a 120 tick, il regime solo-legami deve vincere in almeno **due terzi** dei casi contro nessun trasferimento.

**Persistenza dei legami originali:** medesimo minimo di 20 coppie discordanti e quota favorevole solo-legami di almeno due terzi.

Se non raggiunti, l'esito resta `not_met_or_underpowered` nello schema della preregistrazione; con un campione sufficiente, ciò significa specificamente **soglia non raggiunta**, non mancanza delle 20 coppie richieste.

## Risultati completi

**160/160 mondi sorgente** selezionati, zero esclusioni; tutti i risultati negativi conservati nel dataset.

| Misura su 160 fork per braccio | Nessun trasferimento | Conduzione solo sui legami | Tutti i contatti |
|---|---:|---:|---:|
| Aggregato originale cresciuto coerentemente al tick120 | **127** | 126 | 120 |
| Aggregato cresciuto coerentemente almeno una volta durante i 120 tick | 147 | 143 | 150 |
| Nessun evento di rottura dei legami originali per tutti i 120 tick | 105 | **114** | 103 |
| Almeno un nuovo legame di confine con un ID originale | 153 | 149 | 154 |
| Nuovi legami di confine con ID originali, totale | **292** | **292** | 333 |
| Nuovi legami di confine con ID originali, media per sorgente | **1,825** | **1,825** | 2,081 |
| Nuovi legami nell'intero mondo, media per sorgente nei 120 tick | 147,325 | 153,119 | **185,775** |
| Passaggi energetici medi attraverso i **legami materiali originali** | 0 | **34,11** | 62,58 |
| Passaggi medi verso la sorgente da materiali esterni | 0 | 14,46 | **68,46** |
| Durata media della crescita coerente, in tick | 88,84 | 90,75 | 87,74 |
| Ricostituzione osservata di tutti i legami originali dopo almeno una rottura, numero di mondi | 26 | 24 | 23 |

**Avvertenza:** il numero di passaggi energetici conta trasmissioni di un quanto, anche ripetute; non significa energia nuova. Il flusso lungo legami *interni* allo stesso materiale non aumenta la sua energia totale: per quello contano trasferimenti al confine, in entrata e in uscita, non solo eventi interni.

### Confronti appaiati indipendenti

| Endpoint confronto solo-legami vs nessun trasferimento | Favorevoli solo-legami | Favorevoli controllo | Entrambi positivi | Entrambi negativi |
|---|---:|---:|---:|---:|
| Crescita coerente del medesimo aggregato a tick120 | **25** | **26** | 101 | 8 |
| Nessuna rottura di tutti i legami originali entro tick120 | **36** | **27** | 78 | 19 |

- **Crescita:** 51 coppie discordanti, quota favorevole alla conduzione **25/51 = 49,0%**, contro il minimo preregistrato **66,7%** → **criterio NON raggiunto**.
- **Persistenza:** 63 coppie discordanti, quota favorevole alla conduzione **36/63 = 57,1%**, ancora sotto il requisito **66,7%** → **criterio NON raggiunto**.
- Entrambi i confronti hanno superato i limiti quantitativi preregistrati (**160 sorgenti, almeno 20 discordanti**). Non possiamo liquidarli come semplicemente sottocampionati rispetto a quelle soglie, né dichiarare un vantaggio causale significativo: questo specifico criterio non è stato raggiunto.
- Anche contando ogni formazione chimica con un'estremità nelle particelle originali, senza chiedere crescita coerente, **il numero complessivo di nuovi legami incidenti non aumenta affatto** fra controllo e trasporto sui legami: 292 eventi in entrambi i regimi. Il totale di nuovi legami *in tutto il mondo* aumenta invece di 927 eventi (da 23.572 a 24.499 su 160 universi). Ciò supporta la distinzione fra attività globale e crescita localizzata.

### Osservazione metodologica importante: le sorgenti erano piccole e giovani

Il criterio di selezione è stato fissato prima dei dati. Nel campione reale, però, l'aggregato selezionato compare **quasi subito**:

- **148/160** sorgenti hanno **3 atomi e 2 legami**; dieci ne hanno 4 e due ne hanno 5.
- Tick di selezione: **minimo 1, mediana 2, massimo 4**.
- Tutte le sorgenti sono quindi piccoli aggregati giovanissimi e le loro energie sono quelle di un sistema ancora molto vicino alla condizione iniziale.

Il risultato negativo è valido per **questo preciso esperimento** e la classe di oggetti selezionati, ma non esclude che reti più antiche o più estese abbiano proprietà differenti. Sarebbe necessario un nuovo protocollo preregistrato che selezioni strutture più mature *prima* di fissare gli endpoint; modificare adesso la selezione dei 160 seed sarebbe scorretto.

## Riproducibilità e indipendenza dei risultati

GitHub Actions ha completato la suite completa dei test, quattro gruppi preregistrati da 40 sorgenti e il merge finale. L'aggregazione verifica l'hash del protocollo, l'identità di tutti i 160 seed e il loro ordinamento. Un replay completamente indipendente senza trasporto è passato per la prima struttura selezionata in ciascuno dei quattro shard (seed 22001, 22041, 22081, 22121).

**Verifica ulteriore del file ZIP originale dopo la CI:** riletto `results.json`, controllati 160 seed esatti, tutti gli endpoint energetici finali, i quattro record di replay; ricontati indipendentemente dai singoli fork i numeri della tabella (127/126/120 crescita, 105/114/103 persistenza, 292/292/333 legami incidenti) e i confronti discordanti (25–26; 36–27). Concordano con il sommario originale.

Il test sintetico riproduce il regime di trasporto M7.3 dal medesimo stato nativo (energia e hash finali identici), verificando contemporaneamente la classificazione dei passaggi sugli ID originali, l'assenza di energia creata e la mancata estrazione di RNG dal trasporto. I tre fork iniziano identici; dopo i primi passaggi, i processi possono divergere anche nel consumo globale di RNG. **Non** abbiamo separato ogni contributo a livello di singola reazione né dimostrato un trasferimento mirato di informazioni.

## Interpretazione: non ancora auto-mantenimento

**M7.3:** trasferire energia via legami fa nascere più legami *in totale*.

**M7.4:** gli aggregati che già possedevano legami all'inizio del fork **non** ottengono una crescita coerente preferenziale né un vantaggio di persistenza sufficiente a superare i criteri dichiarati. Dunque l'aumento globale delle reazioni **non equivale** all'auto-crescita di una stessa struttura.

La probabilità elementare di rottura dei legami rimane costante e indipendente dall'energia. La ricostituzione di vecchi legami è prevista dalla chimica reversibile e **non** dimostra un dispositivo biologico di auto-riparazione. Nessun risultato supporta cellule digitali, metabolismo autoregolato, geni, ereditarietà, discendenza o autoreplicazione.

## Prossima domanda con maggiore valore informativo

**M7.5** non dovrebbe limitarsi a ripetere M7.4 per altri milioni di universi. Serve confrontare in un campione nuovo e preregistrato **aggregati più maturi** (dimensione, architettura e valenze) e, ancora meglio, separare sperimentalmente:
1. Energia che entra attraverso il confine dell'aggregato contro quella semplicemente redistribuita all'interno;
2. L'eventuale formazione di nuovi legami *fra il materiale sorgente e quello esterno*, prima che la sorgente si frammenti;
3. La persistenza dei **legami originali** rispetto alla crescita generica del componente;
4. Un controllo di topologia equivalente per dimensione/composizione/grado, per non attribuire a "organizzazione" ciò che dipende solo da un numero maggiore di contatti o legami.

Finché non osserviamo un feedback locale vantaggioso sullo **stesso aggregato** e poi un trasferimento causale di informazione ad aggregati nuovi, A-Life resta un esperimento di auto-organizzazione chimico-geometrica, **non** un organismo digitale.
