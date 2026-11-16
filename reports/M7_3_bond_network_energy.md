# M7.3 — Reti di legami come conduttori energetici: più chimica, non più mobilità

**Data:** 16 novembre 2026. **Stato:** campagna preregistrata completata, 300/300 mondi e regressioni **PASS**; entrambi i criteri preregistrati **raggiunti**. La dimostrazione riguarda il nuovo *regime di conduzione* inserito nel simulatore, non la comparsa spontanea di metabolismo o vita.

## Tracciabilità e dati

- [Protocollo congelato PRIMA della scrittura del codice: commit `b4697d7`](https://github.com/kkongiu/alife-lab/commit/b4697d7cde9eba447bcbb8424187e0f1030120e7).
- [GitHub Actions PASS, 4 shard + test integrali + aggregazione #43895731606](https://github.com/kkongiu/alife-lab/actions/runs/43895731606).
- [Dataset di tutti i 300 mondi, inclusi risultati nulli: artifact #14239091789](https://github.com/kkongiu/alife-lab/actions/runs/43895731606/artifacts/14239091789).
- [Implementazione sperimentale `tools/m7_3_bond_energy.py`](../tools/m7_3_bond_energy.py).
- [PR #31 in bozza](https://github.com/kkongiu/alife-lab/pull/31). `master`, `src/` e le leggi originali M6/M7.1/M7.2 rimangono immutati.

## Domanda

M7.2 ha mostrato che una nuova regola di diffusione lungo qualsiasi contatto favorisce fortemente l'attività. Ma l'energia veniva trasportata senza che gli atomi dovessero prima organizzarsi. Se **soltanto i legami chimici nativi** possono condurre energia, l'aggregazione cambia la successiva disponibilità di energia e il comportamento chimico? La risposta non coincide con la comparsa di un organismo: è un test della **funzione energetica di una topologia costruita spontaneamente**.

## Protocollo già fissato

- **100 nuovi seed indipendenti** `20001–20100`, ognuno ripetuto in tre regimi strettamente appaiati: **300 mondi, 600 tick ciascuno, 180.000 tick-mondo**.
- Condizioni comuni: reticolo periodico 24×24, 264 particelle originali con stesse posizioni, specie, energie e RNG iniziale per seed; zero legami iniziali; costo energetico del movimento pari a 1; stessa chimica M6 senza catalisi; sorgenti distribuite identiche a M7.2, **16 × 2 × 600 = 19.200 unità esterne generate per mondo**.
- **Controllo nullo**: nessun trasferimento supplementare.
- **Conduzione sui legami**: soltanto le coppie collegate **in quel tick da un legame chimico originale** possono scambiare energia. Dopo ogni passo M6, le energie vengono lette da uno snapshot, le connessioni ordinate per ID persistenti e, quando la differenza è almeno due unità, è proposta una cessione di un quanto dalla più ricca alla meno ricca; le cessioni si applicano simultaneamente nel limite del budget del donatore.
- **Conduzione sui contatti**: identico principio, ma ammesse tutte le coppie cardinalmente vicine, legate **o non legate** (meccanismo M7.2 originale). Il nuovo modulo è separato dal motore.
- Il passaggio energetico non crea energia, non consuma RNG, non sposta particelle, non modifica direttamente le specie, i legami o il tasso di rottura originale. L'energia scambiata ha costo nullo come idealizzazione del trasporto passivo.
- Misure preregistrate: attività, formazione/rottura di nuovi legami negli ultimi **100 tick (501–600)**; particelle a energia zero, energia contenuta in particelle legate e libere, disuguaglianza energetica Gini, mobilità energeticamente ammissibile, overflow e numero di anelli semplici al tick600. Le 100 unità sperimentali indipendenti sono i **seed**, non i 300 mondi o i singoli contatti.

### Criteri principali preregistrati

**A — Vantaggio chimico della rete di legami.** Almeno 70/100 mondi devono registrare almeno uno scambio lungo legami nativi nel regime `bond_only`, **e** almeno 60/100 devono produrre più nuovi legami nell'ultimo intervallo rispetto al controllo nullo.

**B — Vantaggio dei contatti generici.** Almeno 75/100 seed devono avere più movimenti nell'ultimo intervallo sotto trasferimento fra tutti i contatti rispetto a soli legami, **e** almeno 70/100 devono avere meno particelle a energia zero al passo600.

Le due condizioni di ogni criterio sono congiunte: nessuna soglia è stata modificata dopo aver visto i dati.

## Risultati: due criteri PASS, con compromesso evidente

| Media su 100 mondi per braccio | Nessun trasferimento | Soltanto legami nativi | Tutti i contatti |
|---|---:|---:|---:|
| Movimenti accettati, tick501–600 | **143,50** | 136,85 | **758,08** |
| Nuovi legami, tick501–600 | 8,66 | **17,59** | **35,93** |
| Particelle con energia 0, tick600 | 139,86 | **110,89** | **26,62** |
| Particelle libere, mobili, con energia sufficiente, tick600 | 7,04 | 6,16 | **24,47** |
| Energia media in particelle *legate*, tick600 | 6.571,37 | **6.616,92** | 4.761,86 |
| Energia media in particelle *libere*, tick600 | 720,15 | **496,04** | 335,85 |
| Disuguaglianza Gini delle energie per particella, tick600 | 0,9510 | 0,8537 | **0,5255** |
| Energia media scartata per overflow, su 19.200 generate | 11.477,12 | 11.507,56 | **9.720,18** |
| Trasferimenti energetici totali durante 600 tick | 0 | **11.119** | **49.329** |
| Mondi con almeno un anello nativo semplice al tick600 | 54/100 | **77/100** | **93/100** |

Il numero di trasferimenti conta i **passaggi di un quanto** e non l'energia nuova immessa dall'esterno. Lo stesso quanto può transitare più volte; la sorgente energetica rimane uguale in tutti i regimi.

### Verdetto A — Reti native e attività chimica: `passed`

- **100/100** mondi mostrano almeno un trasferimento lungo un legame chimico nato spontaneamente (soglia 70 superata).
- **96/100** seed appaiati formano più nuovi legami nei tick501–600 con trasporto sui legami rispetto a nessun trasferimento (soglia 60 superata); due diminuiscono e due pareggiano.
- Aumento medio appaiato **+8,93 nuovi legami** nell'intervallo; da 8,66 a 17,59 legami per 100 tick, **circa 2,03 volte**.
- **La mobilità non aumenta**: 136,85 contro 143,50 movimenti, differenza media **−6,65**. Il braccio dei legami vince nel confronto sul movimento solo in **46/100** seed (53 peggiorano e uno pareggia).
- Si riduce di circa **29** il numero di particelle a energia zero, ma la disponibilità energetica delle particelle **libere e in grado di muoversi** scende da 7,04 a 6,16.

La conclusione corretta è che **abilitare conduzione sulle connessioni chimiche nativamente formate modifica in modo riproducibile la chimica e aumenta il turnover di formazione dei legami**, senza generare un corrispondente miglioramento della mobilità. Gli atomi legati sono immobili nella fisica di base: il trasporto può servire l'aggregazione più del movimento. La differenza può dipendere da diversi percorsi dinamici e da flussi RNG successivamente non sincronizzati; non è stata isolata una causa microscopica unica per ogni nuovo legame.

### Verdetto B — Contatti liberi rispetto ai soli legami: `passed`

- **100/100** seed presentano più movimenti tardivi con i contatti generici rispetto alla rete legata (soglia 75 superata), differenza media **+621,23** movimenti.
- **100/100** hanno meno particelle a energia zero al tick600 (soglia 70 superata), differenza media **−84,27** particelle.
- **97/100** formano anche più nuovi legami nel regime di contatto generico; tre meno.
- L'energia per particella è distribuita in modo molto meno diseguale (Gini ~0,526 contro ~0,854). Le particelle libere ed energeticamente mobili sono in media **24,47** contro **6,16**.

### Dato aggiuntivo: i legami trasportano energia anche nel regime generale

Su circa **49.329 passaggi** medi per mondo nel regime `all_contacts`, **26.310** avvengono attraverso **coppie che in quel tick erano legate chimicamente**, e **23.019** attraverso contatti non legati. Tuttavia questi valori si riferiscono a reti generate da traiettorie **diverse** rispetto al regime `bond_only`: non è corretto confrontare 26.310 con 11.119 come se fossero la capacità delle stesse strutture sotto identiche condizioni dinamiche.

## Integrità e audit indipendente del dataset

- **GitHub Actions completamente verde**: suite integrale dei test, quattro shard fissi da 25 seed × 3 regimi, aggregazione e verifica 300/300 mondi.
- **12 replay da seed**, un seed × tre regimi in ciascuno dei quattro shard, con stesso hash materiale completo, stato RNG e numero estrazioni, bilancio energetico, formazione/rottura di legami, movimenti e conteggi dei trasferimenti.
- **1.800 checkpoint energetici** (6 per ciascuno dei 300 mondi): in tutti si verifica l'equazione `stored + dissipated + unabsorbed = initial + injected`.
- Test sintetici con tre particelle, una coppia legata e un'altra coppia adiacente non legata: sul grafo di un legame il trasferimento coinvolge **soltanto la prima coppia**; sui contatti coinvolge **entrambe**. Il modulo restituisce le stesse energie e lo stesso stato finale del trasporto originale M7.2 nel caso `all_contacts`.
- **Lettura separata del file ZIP originale:** nuovo conteggio di tutti i seed e delle metriche 96/100, 100/100, 100/100 e 100/100; controllo di tutti i 1.800 bilanci energetici, 300 mondi completi e 12 record di replay. Tutto coerente.

## Cosa abbiamo e cosa ci manca

**Risultato concreto:** una topologia energetica che nasce dalle regole di chimica (un insieme di legami), quando viene esplicitamente abilitata alla conduzione, può favorire ulteriore attività di formazione dei legami nel sistema. È un **possibile ingrediente** di un feedback fra organizzazione ed energia.

**Non dimostrato:** che uno specifico aggregato usi quell'energia per mantenere **se stesso**, che i legami riparati appartengano al medesimo materiale, che la rete cresca o costruisca un discendente, che una proprietà sia ereditata o che esista una membrana metabolica. Il tasso di rottura dei legami rimane costante e indipendente da energia e struttura: il regime non introduce una protezione diretta dei legami originali.

### Proposta M7.4

M7.4 dovrebbe seguire **identificativi materiali e genealogia dei singoli aggregati**, non soltanto contare nuovi legami in tutto il mondo:

1. Registrare per ogni aggregato nativo la nascita, i legami originali, le rotture, la ricostituzione, l'acquisizione di particelle e l'energia ricevuta dagli aggregati tramite legami;
2. Separare il mantenimento dello *stesso* aggregato dalla formazione casuale di *altri* legami altrove;
3. Usare fork appaiati di stati **spontanei** e controlli sui legami/materiali, con identico stato iniziale e RNG, per verificare una relazione causale fra conduzione della rete e persistenza/crescita dello **stesso** materiale;
4. Richiedere una discendenza osservabile e causalmente testabile prima di discutere di riproduzione; evitare firme simili non genealogiche.

Questo è il passo necessario per passare dalla semplice correlazione **rete energetica → più legami globali** a una prova di **feedback strutturale locale**.
