# M7.9 — L'allocazione dell'energia prodotta dai legami non supera il controllo a identica energia, ma posizione rimescolata

**Data:** 17 novembre 2026. **Risultato scientifico:** entrambi i criteri preregistrati di **superiorità della collocazione energetica originale** sono **NON RAGGIUNTI**, con campione e numero di confronti informativi sufficienti. I quattro controlli che riassegnano artificialmente gli **stessi** valori di energia a particelle diverse dell'aggregato presentano, in media, **più contatti energeticamente possibili e più nuovi legami con l'esterno**. Questo limita l'ipotesi che la rete chimica naturale collochi spontaneamente l'energia in modo funzionalmente privilegiato.

## Tracciabilità

- [Preregistrazione M7.9, commit `db9ca74`, prima di implementazione e risultati](https://github.com/kkongiu/alife-lab/commit/db9ca741238c3308bfb676572bb0d5d5cca0eaf4).
- [GitHub Actions #44121359723: intera suite di regressione + 16 shard + 640/640 universi + merge: PASS](https://github.com/kkongiu/alife-lab/actions/runs/44121359723).
- [Artefatto integrale di tutti i 640 stati sorgente, sei condizioni e 32 reazioni accoppiate per condizione: #14344284768](https://github.com/kkongiu/alife-lab/actions/runs/44121359723/artifacts/14344284768).
- [Codice M7.9](../tools/m7_9_energy_placement.py) e [PR #37 in bozza](https://github.com/kkongiu/alife-lab/pull/37).
- Il motore nativo M6 `src/`, la conduzione M7.3, il selettore M7.5, i rilevatori M7.7/M7.8 e `master` sono rimasti invariati. Nessuna PR è stata integrata.

## Problema affrontato: l'energia non basta

M7.8 ha stabilito in un esperimento di chimica isolata e geometria congelata che **un solo trasferimento energetico attraverso legami esistenti** può attivare una nuova coppia originale–esterno e causarne la formazione, confrontando le stesse estrazioni casuali per coppia. Ma il percorso di diffusione attraverso contatti **non legati** era mediamente ancora più efficace.

La domanda M7.9 non è quindi se la conduzione aumenti la reattività, bensì: **la distribuzione particolare di energia dopo la conduzione in una struttura naturale è più favorevole alle reazioni di confine di altre collocazioni che conservano esattamente la stessa energia?**

Un vantaggio rispetto al controllo senza trasferimento sarebbe insufficiente. Occorre un vantaggio rispetto a un placebo che possiede **identico budget energetico e identica distribuzione statistica dei livelli di energia**, ma non ne conserva l'assegnazione ai singoli ID materiali.

## Disegno preregistrato

- **640 nuovi seed disgiunti** `27001–27640`, raggruppati in **16 shard fissi di 40**, tutti inclusi. `640/640` hanno prodotto una sorgente naturalmente idonea. Nessun seed escluso o sostituito.
- Ogni universo fisico originale è quello M7.3/M7.5: **264 particelle native**, reticolo periodico 24×24, zero legami all'inizio, 16 sorgenti energetiche esterne, chimica reversibile M6 invariata, nessuna catalisi e nessun organismo preinserito.
- Il selettore M7.5 originale, senza modifiche, sceglie la prima componente massimale di **5–16 particelle** con almeno 4 legami nativi, valenza residua e almeno **due legami presenti ininterrottamente da 20 tick**, dal primo istante ammissibile tick120 (fino al massimo tick500). Tutte le strutture del campione M7.9 risultano selezionate **già al tick120**.
- Tutte le **640 strutture** sono **alberi**, non anelli o membrane. Richiedere due legami invecchiati **non prova** che l'intero componente abbia mantenuto la stessa configurazione per 20 tick.
- Dopo la selezione, si congela lo stato: **nessun `World.advance`, movimento, rottura, nuova iniezione energetica, movimento di particelle o cambiamento di legami** fino all'intervento.

### Sei condizioni, ma soltanto un seed indipendente

| Condizione | Cosa cambia |
|---|---|
| `sham` | Nessun trasferimento energetico: stato nativo originale |
| `bond_only` | **Un solo passaggio** di trasferimento M7.3 originale lungo gli attuali legami nativi |
| `root_scramble_0` | Stesso passaggio M7.3, poi riassegnazione artificiale di tutti i valori energetici ai membri originari della struttura mediante permutazione SHA256 fissa 0 |
| `root_scramble_1` | Come sopra, permutazione SHA256 fissa 1 |
| `root_scramble_2` | Come sopra, permutazione SHA256 fissa 2 |
| `root_scramble_3` | Come sopra, permutazione SHA256 fissa 3 |

La permutazione è fissata prima dei dati: ordina gli **ID originari** secondo SHA256 del testo ASCII `alife-m7-9|seed|rank|material_id`; i valori energetici del componente dopo il trasferimento originale, ordinati secondo ID crescente, vengono assegnati nell'ordine permutato.

Nei cinque regimi che hanno avuto la conduzione, prima della chimica:

- **identico numero di trasferimenti M7.3** rispetto alla condizione `bond_only`, media **90,328125** eventi energetici per mondo;
- **identica somma e identico multinsieme dei valori di energia** delle stesse particelle originarie;
- **tutta l'energia delle particelle esterne alla struttura originaria assolutamente invariata**, identici ID/posizioni/specie/legami/valenze, bilancio energetico totale e stato RNG;
- cambia **soltanto quale ID materiale originale possiede quale valore energetico**.

La riassegnazione non è vincolata a un percorso localmente trasportabile tramite i legami. È un'**ablazione spaziale non fisica**, usata per testare il valore della collocazione naturale, non per proporre un nuovo meccanismo naturale di trasporto.

### Lotterie chimiche controllate

A ciascuna delle sei condizioni seguono **32 sweep distinti e accoppiati di sola formazione di legami**, con il codice chimico isolato M7.8 già verificato rispetto a M6. Per ogni coppia materiale non ordinata e per ciascun salt fissato `0..31` è usata la **stessa estrazione a 64 bit SHA256** indipendentemente dall'intervento energetico. Specie, geometria, iteratore nativo dei candidati, soglia di reazione, verifiche successive di valenza/energia e costi chimici sono quelli originali M6.

In totale sono stati eseguiti **640 × 6 × 32 = 122.880 sweep controfattuali di formazione**. Le 32 lotterie e le quattro permutazioni condividono lo stesso mondo: **non sono 122.880 campioni indipendenti**. L'unità statistica resta il seed mondo, 640 in totale.

Le reazioni producono **nuovi legami fra almeno una particella dell'aggregato originario e una esterna**, non organismi o discendenti.

## Criteri preregistrati

**Primario — collocazione originaria e reattività energetica statica.** Richiedere almeno 40 sorgenti e almeno **25 confronti informativi** sul segno della differenza `4 × coppie_originali_energeticamente_idonee − somma(coppie_idonee_nelle_quattro_permutazioni)`, a parità esatta di multinsieme energetico; **≥2/3** di tali confronti devono favorire la collocazione originale.

**Secondario — reazioni reali della medesima struttura.** Almeno 40 sorgenti e **20 confronti informativi** sulla differenza `4 × totale_32_reazioni_esterne_originali − somma(totale_32_reazioni_esterne_nelle_quattro_permutazioni)`; **≥2/3** favorevoli alla collocazione originale.

I confronti contro `sham` sono **solo descrittivi**, non possono sostituire i criteri originali; nessuna scelta della permutazione migliore a posteriori.

## Risultati: nessun vantaggio della collocazione nativa rispetto al rimescolamento

| Misura per mondo | `sham` | `bond_only` | Media delle quattro permutazioni |
|---|---:|---:|---:|
| Coppie originali–esterne staticamente energeticamente idonee | **0,101562** | 0,164062 | **0,210156** |
| Nuovi legami originali–esterni sommati sui 32 tentativi accoppiati | **0,189062** | 0,265625 | **0,343359** |
| Media di nuovi legami per **un** sweep controfattuale | 0,005908 | 0,008301 | **0,010730** |

Anche le quattro permutazioni individuali mostrano mediamente più reazioni della collocazione originale:

| Permutazione post-conduzione | Contatti idonei, media | Nuovi legami originali–esterni nei 32 sweep, media |
|---|---:|---:|
| `root_scramble_0` | 0,200000 | 0,335938 |
| `root_scramble_1` | 0,212500 | 0,351562 |
| `root_scramble_2` | 0,217188 | 0,346875 |
| `root_scramble_3` | 0,210938 | 0,339062 |

La conduzione sui legami originale supera il controllo `sham` anche in questo campione, ma **non** i quattro rimescolamenti artificiali alla stessa energia per struttura.

### Endpoint primario: NON RAGGIUNTO, campione sufficiente

| Confronti appaiati per seed sull'interfaccia energetica | Numero |
|---|---:|
| Migliore collocazione originale `bond_only` | **28** |
| Migliore media delle collocazioni rimescolate | **58** |
| Pari | 554 |
| **Discordanti** | **86** |

Quindi soltanto **28/86 = 32,56%** favoriscono la collocazione originale, molto sotto la soglia preregistrata **66,67%**. Sono soddisfatti i minimi 40 sorgenti e 25 discordanti. Il giudizio algoritmico è esattamente `not_met_favorable_fraction`, non un'indeterminatezza per insufficiente campione.

### Endpoint secondario: NON RAGGIUNTO, campione sufficiente

| Confronti appaiati per seed sulla formazione effettiva | Numero |
|---|---:|
| Più nuovi legami con la collocazione originale | **25** |
| Più nuovi legami con il valore medio delle permutazioni | **48** |
| Pari | 567 |
| **Discordanti** | **73** |

La quota favorevole originale è **25/73 = 34,25%**, anch'essa distante dal **66,67%** prefissato. I minimi 40 sorgenti e 20 discordanti sono raggiunti. Esito formale: `not_met_favorable_fraction`.

**Il rimescolamento prevale in numero di seed e media**, ma il protocollo non prevedeva una soglia confirmatoria per dichiararne la superiorità. Pertanto è corretto riportarlo come un andamento descrittivo robusto in questo campione, non ribaltare a posteriori l'ipotesi per dichiarare una nuova conferma statistica.

## Controlli aggiuntivi sul dataset grezzo

Ho scaricato e riletto separatamente il file originale `results.json` proveniente da GitHub Actions:

- Esatti **640** seed consecutivi `27001–27640`, **640/640 selezionati** senza esclusioni, e **16** prime sorgenti di shard conservate per controllo.
- **Tutti** selezionati al tick120; struttura di dimensione 5–16 e **tutte le topologie arboree**.
- Reiterati indipendentemente i segni dei confronti per seed direttamente sulle sei condizioni, ricostruendo **28/58/554** sul criterio primario e **25/48/567** sul secondario; corrispondono esattamente alla fusione CI.
- Ricontati i totali di legami effettivi nelle 32 lotterie su 640 seed: **121** in `sham`, **170** con `bond_only`, contro **215, 225, 222 e 217** nelle quattro permutazioni, rispettivamente.
- Tutti gli interventi mantengono le energie esterne agli ID originali identiche, la somma del gruppo e il multinsieme energetico, gli ID, le posizioni e i legami: questi vincoli sono asseriti automaticamente in ogni mondo e salvati nel dataset.
- Ogni sweep originale M7.8 (usato senza modifiche) verifica ledger e stato RNG inalterato. La suite completa di regressione è **PASS**; i 16 shard di 40 universi e la fusione conclusiva sono **PASS**.

La verifica fisica post-hoc ricostruttiva con la funzione chimica M6 originale è documentata separatamente dopo la conclusione: non può cambiare il risultato preregistrato.

## Significato e limiti

**Cosa sappiamo:**

1. La conduzione passiva lungo legami chimici preesistenti può aumentare la reattività verso particelle esterne rispetto al mancato trasferimento (M7.8; conferma descrittiva M7.9).
2. Questo aumento non implica che il **posizionamento esatto** dell'energia dopo la conduzione, sulla stessa struttura materiale, sia superiore a collocazioni alternative con **identica quantità e distribuzione globale dei valori energetici per aggregato**.
3. Le quattro collocazioni controfattuali rimescolate presentano più occasioni e reazioni in media, nonostante non ricevano alcuna energia aggiuntiva né modifiche di geometria o legami.

**Cosa non dimostra:**

- Che il rimescolamento sia fisicamente realizzabile tramite i vincoli del simulatore; può scambiare valori tra particelle che non sono adiacenti. Non è un controllo fisico di trasporto equivalente per percorso o costo, soltanto per il budget e la distribuzione finale dei valori energetici nell'aggregato.
- Che la conduzione nativa sia «inefficiente» per *tutte* le funzioni: misuriamo esclusivamente legami originali–esterni immediati, non resistenza a perturbazioni, diffusione di segnali, conservazione dei legami, riparazione o generazione di prole.
- Che l'aggregato selezioni o regoli attivamente la propria conduzione: è una legge fisica preimpostata dall'esperimentatore.
- Che una struttura ramificata equivalga a una membrana, un metabolismo, un genoma o un organismo. **Nessuna evidenza di vita digitale.**

## M7.10: domanda successiva più produttiva

Continuare a variare il numero di mondi o a rimescolare energia senza un'ipotesi locale rischia di produrre altri segnali generici. Per studiare **funzionalità emergente** occorre misurare qualcosa che non sia solamente un nuovo legame più facile, ad esempio:

- Il destino nel tempo di un aggregato dopo aver acquisito una particella: **il nuovo materiale rimane stabilmente integrato** e contribuisce a nuove reazioni?
- Un possibile **feedback energetico positivo**: il nuovo legame crea un percorso che aumenta la capacità locale di importare, conservare e ridistribuire energia in passi successivi, rispetto allo stesso materiale impedito a formare quel solo nuovo legame?
- Un controllo causale con **legame neoformato presente vs assente** in uno stato sorgente altrimenti identico, bilanciando esplicitamente l'energia chimica pagata e conservata nel legame, senza alterare la fisica successiva.

Questa sarebbe una prova di **funzionalità strutturale del legame acquisito**, più vicina al concetto di auto-organizzazione, benché ancora distinta da ereditarietà, replicazione e vita.


## Audit fisico indipendente post-hoc — PASS

Dopo aver congelato il dataset dei 640 seed, un secondo programma di verifica ha **ricalcolato da zero tutti gli stati sorgente nativi** ed effettuato **quattro riassegnazioni energetiche per ognuno**, implementando autonomamente la permutazione SHA256 senza utilizzare la funzione originale M7.9. L'audit è dunque un controllo di correttezza della trasformazione energetica, non una nuova raccolta di dati.

- [GitHub Actions #44121975730, PASS](https://github.com/kkongiu/alife-lab/actions/runs/44121975730).
- [Dataset post-hoc dell'audit #14346281499](https://github.com/kkongiu/alife-lab/actions/runs/44121975730/artifacts/14346281499).
- [Script `tools/m7_9_original_M6_oracle_audit.py`](../tools/m7_9_original_M6_oracle_audit.py).
- [Test indipendente `tests/test_m7_9_original_M6_oracle_audit.py`](../tests/test_m7_9_original_M6_oracle_audit.py).

Risultati del controllo:

1. **640/640** mondi fisici originali ricostruiti da seed e selettore M7.5 invariato, con hash materiale completo e stato RNG identici al dato pubblicato.
2. **2.560/2.560** collocazioni energetiche alternative ricostruite separatamente, con uguaglianza esatta degli hash, del multinsieme energetico e della somma di energia del gruppo originale, senza toccare le particelle esterne.
3. Identificati **87 seed informativi** con un confronto non pari in almeno uno dei due criteri preregistrati. Aggiunti i primi seed di ciascuno dei 16 shard come controlli predefiniti; in totale **100 seed distinti** per l'audit chimico.
4. Su questi 100 seed, ripetuti **100 × 6 condizioni × 32 lotterie = 19.200 sweep**, richiamando direttamente `alife.chemistry.form_bonds` M6 originale con un estrattore `raw()` per coppia iniettato temporaneamente (non la funzione sperimentale M7.8). Tutti i **19.200/19.200** sweep coincidono su identità dei nuovi legami, lotterie consumate, energia chimica, dissipazione, stato RNG e hash completi.

L'audit comprende quindi **tutti i mondi e tutti i rimescolamenti**, mentre le reazioni con l'implementazione M6 originale sono verificate **sui casi informativi e sulle sentinelle**, non sui 640×6×32 sweep. Non introduce campioni statisticamente indipendenti e non cambia i due esiti preregistrati **NON RAGGIUNTI**.
