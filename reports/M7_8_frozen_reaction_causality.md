# M7.8 — Causalità a geometria congelata: l'energia trasferita può abilitare nuovi legami, ma il grafo chimico non è un canale privilegiato

**Data:** 17 novembre 2026. **Stato:** 640/640 sorgenti naturali e 16/16 shard completi, regressioni **PASS**. **Criterio primario (attivazione energetica) RAGGIUNTO**; **criterio secondario (formazione chimica effettiva con RNG accoppiato) RAGGIUNTO**. **Nessuna superiorità specifica della conduzione sui legami rispetto ai contatti non legati**; i controlli alternativi, pur con budget di trasferimenti spesso limitato, producono più reazioni.

## Tracciabilità

- [Protocollo congelato **prima** di scrivere l'implementazione e di osservare i nuovi dati: commit `20cf62f`](https://github.com/kkongiu/alife-lab/commit/20cf62f2a23855a67aa834da7241291fd0bde4cc).
- [GitHub Actions ufficiale — intera suite di test, 16 shard e fusione 640/640 PASS #44115455468](https://github.com/kkongiu/alife-lab/actions/runs/44115455468).
- [Dati grezzi integrali di 640 mondi × 4 interventi × 32 tentativi accoppiati: artifact #14343815285](https://github.com/kkongiu/alife-lab/actions/runs/44115455468/artifacts/14343815285).
- [Codice `tools/m7_8_frozen_reactions.py`](../tools/m7_8_frozen_reactions.py); [PR #36, DRAFT](https://github.com/kkongiu/alife-lab/pull/36).
- Nessuna modifica a `master`, `src/`, alla chimica M6 o ai moduli/protocolli M7.3–M7.7.

## Perché M7.8 è diverso da M7.7

M7.7 aveva verificato che la formazione di legami tra il materiale originale e le particelle esterne, **prima** di una rottura dei legami originari, fosse più comune nei mondi con conduzione sui legami. Ma i mondi evolvono con movimento, cambiamenti di topologia, energia diversa e consumo divergente di uno stream casuale globale: quella osservazione **non** isola la causa di una reazione.

M7.8 congela un mondo nativo dopo che si è formato spontaneamente un aggregato parzialmente maturo. **Non avanza il tempo nemmeno di un tick**, **non** muove atomi, non rompe legami, non inietta energia, non esegue dissipazione e non cambia specie o valenza. Confronta copie identiche del mondo che differiscono **esclusivamente nell'assegnazione di energia fra gli atomi**.

Dopo un solo eventuale trasferimento energetico, ripete una **formazione chimica isolata**, usando le stesse condizioni statiche originali M6 e gli stessi valori pseudocasuali per la **stessa coppia di ID materiali** in tutte le condizioni. Così una variazione di formazione non può derivare da movimenti successivi o dall'ordine diverso delle estrazioni casuali globali. Rimane però possibile la competizione di energia/valenza fra più coppie nel medesimo sweep: non bisogna attribuire ogni differenza a una sola coppia isolata.

## Protocollo preregistrato e quattro condizioni

**Campione:** 640 nuovi seed numerici `26001–26640`, disgiunti dai campioni M7.5, M7.6 e M7.7; 16 shard di 40 universi nativi ciascuno. **640/640** hanno selezionato un aggregato, nessuna esclusione. L'unità statistica resta il **seed nativo**, non la coppia né il singolo tentativo casuale.

Per la selezione si richiama **direttamente il codice M7.5 non modificato**: prima componente chimica naturale massimale di 5–16 particelle, almeno 4 legami, valenza residua e almeno 2 legami con età continua ≥20 tick, dal tick120 al massimo tick500. Un solo aggregato per seed, senza esaminare gli esiti successivi.

Lo stato originale contiene 264 particelle native su reticolo 24×24 periodico, 16 sorgenti energetiche distribuite, costo di movimento 1, nessuna catalisi, zero legami iniziali; nessuna particella, legame o struttura artificiale viene inserita.

| Regime | Trasferimento a geometria congelata |
|---|---|
| **`sham`** | Nessun trasferimento. |
| **`bond_only`** | Un passaggio energetico M7.3 originale su legami chimici già formati naturalmente. Un quanto da particella più ricca a più povera se differenza ≥2. |
| **`all_contacts`** | Identico passaggio M7.3 originale, ma attraverso tutti i contatti cardinali, anche non legati. Controllo generico positivo, **non** a budget uguale. |
| **`unbonded_budget_matched`** | Solo contatti cardinali **non legati**, in ordine canonico per ID persistente, donatore-budgeted. Al massimo lo **stesso numero** di trasferimenti accettati da `bond_only` su quel mondo. Se non ci sono sufficienti contatti non legati con gradiente, il deficit viene registrato: il confronto non è necessariamente pareggiato e non replica la stessa localizzazione dell'energia. |

Nei quattro regimi sono identiche posizioni, specie, valenze, legami prima della reazione, bilancio energetico complessivo e stato RNG. Cambia solo la distribuzione dell'energia delle particelle.

### Le 32 lotterie chimiche accoppiate

Per ciascuna condizione e ciascun seed si effettuano **32 versioni distinte** di un unico sweep di formazione chimica isolata, `salt=0..31`. La chiave di estrazione 64 bit per la coppia `(id_a,id_b)` è:

`SHA256("alife-m7-8|{seed}|{salt}|{min_id}|{max_id}")[:8]`, interpretata come intero unsigned big endian.

Per la **stessa coppia materiale** e la **stessa salt**, il numero casuale è **identico** nei quattro regimi anche se l'energia ha reso alcune coppie ammissibili e altre no. La distribuzione delle 32 salt è fissata prima del campione; sono 32 tentativi condizionati allo **stesso mondo**, non 32 universi indipendenti.

Lo sweep usa l'**iteratore nativo di candidati `_candidate_pairs`**, stessa soglia originale di formazione, verifiche successive di valenza, energia e legami già esistenti, stessa spesa di energia, energia immagazzinata nel nuovo legame e dissipazione. La sola modifica della funzione sperimentale rispetto alla chimica M6 `form_bonds` è la sorgente delle estrazioni: **una chiave per coppia** in luogo dello stream RNG globale. La funzione non richiama `World.advance`: **è un controfattuale di reazione isolata, non un normale tick nativo**.

## Criteri congelati prima dei dati

**Primario — attivazione diretta di opportunità.** Almeno 40 sorgenti selezionate, almeno 20 coppie non pari sul numero di *nuovi contatti originale–esterno energeticamente qualificati* dopo un solo passaggio `bond_only` rispetto a `sham`; almeno **15 universi con incremento stretto** e **≥4/5** dei confronti discordanti favorevoli a `bond_only`. Tutte le condizioni congiunte.

**Secondario — formazione chimica effettiva accoppiata.** Almeno **15 seed** non pari nel numero totale di nuovi legami originale–esterno sulle 32 lotterie accoppiate; almeno **2/3** dei seed discordanti favorevoli a `bond_only` rispetto a `sham`. Il totale sulle 32 lotterie è una stima interna a ciascun seed, non 32 osservazioni indipendenti.

Le comparazioni con le altre forme di diffusione sono **predefinite ma descrittive**, senza una nuova soglia confirmatoria di superiorità strutturale.

## Risultati definitivi: entrambi i criteri PASS, ma effetto raro in un singolo stato

| Misura dopo un solo passaggio / sweep | Sham | Solo legami | Tutti i contatti | Solo non legati, budget limitato |
|---|---:|---:|---:|---:|
| Trasferimenti di un quanto per sorgente, media | 0 | **90,588** | 183,173 | 87,284 |
| Coppie originale–esterno energeticamente qualificate dopo il passaggio, media | 0,10781 | **0,14063** | 0,25156 | 0,22188 |
| Nuovi legami originale–esterno **sommati su 32 lotterie per seed**, media | 0,17813 | **0,24688** | 0,44375 | 0,37188 |
| Nuovi legami originale–esterno **per una singola lotteria isolata**, media | 0,00557 | **0,00771** | 0,01387 | 0,01162 |
| Seed con almeno una reazione originale–esterno in una delle 32 lotterie | 52/640 | **71/640** | 122/640 | 112/640 |

Le **32 lotterie** hanno distribuzioni casuali per coppia comuni fra i regimi, ma non sono 20.480 mondi naturali indipendenti. La somma di legami originali–esterni attraverso le 32 lotterie sull'intero campione è **114** nel controllo, **158** con conduzione sui legami, **284** per tutti i contatti e **238** sul canale non legato a budget limitato. I numeri sono conteggi di tentativi isolati, **non** 114 o 158 nuovi organismi.

### Endpoint primario: attivazione energetica — **RAGGIUNTO**

I **640 seed** presentano:

- **26** con incremento netto del numero di coppie originali–esterne energeticamente idonee dopo `bond_only`.
- **6** con decremento netto.
- **608** senza differenza netta.

Quindi **26/32 = 81,25%** dei confronti discordanti favoriscono la conduzione: supera la soglia **80%** preregistrata; i 26 positivi superano il minimo di 15. Differenza media appaiata **+0,032813 nuove coppie energeticamente idonee per seed**.

La soglia è superata di un margine limitato: con 32 discordanti servivano **almeno 26** positivi. Il risultato mostra che, in alcune configurazioni naturali, un solo passaggio energetico lungo legami spontanei **può** abilitare direttamente una nuova reazione in geometria invariata. Nel **95%** circa dei mondi il numero netto di opportunità è invariato.

L'effetto non è matematicamente garantito monotono: sei mondi **perdono** almeno una opportunità netta, perché la redistribuzione può togliere a una particella l'energia minima necessaria.

### Endpoint secondario: legami realmente formati con draw di coppia identici — **RAGGIUNTO**

Sulla formazione di legami originale–esterno nelle 32 lotterie, per ogni seed:

- **25** mondi mostrano più nuovi legami in `bond_only` che in `sham`.
- **5** mondi mostrano più nuovi legami nel controllo.
- **610** mondi presentano lo stesso conteggio nei due regimi.

**25/30 = 83,33%** dei confronti discordanti favoriscono `bond_only`, oltre i **2/3** preregistrati, con almeno 15 discordanti.

L'effetto complessivo è **+44 legami** attraverso i 640×32 tentativi accoppiati, pari a **+0,06875 legami per seed in 32 tentativi**, ovvero **+0,002148 legami per singolo sweep per mondo**.

I dati dimostrano che, in questo **controfattuale di formazione isolata**, il trasferimento di energia lungo i legami cambia effettivamente il risultato chimico *senza movimento, senza cambiamento del grafo iniziale e senza divergenza della lotteria per coppia*. **Non** dimostra che ogni differenza di formazione sia mediata da uno specifico singolo quanto, né predice la probabilità di crescita dopo 120 normali tick.

### Controllo cruciale: nessuna superiorità specifica del canale legato

Con **`unbonded_budget_matched`** limitato a un numero massimo di trasferimenti uguale al `bond_only`:

- Su 640 mondi, il controllo non legato produce più legami originale–esterno sulle 32 lotterie in **51**, la conduzione sui legami in **10**, con **579** pareggi.
- Numero medio di trasferimenti accettati: **87,28 non legati** contro **90,59 legati**.
- Si ottiene l'esatto stesso numero di trasferimenti in **370/640** mondi; negli altri **270/640** il canale non legato resta **sotto** il budget richiesto, con shortfall medio di **3,303** passaggi.
- Ciononostante, i nuovi legami originale–esterno sono mediamente **0,37188 per 32 lotterie** sui canali non legati, contro **0,24688** sui legami.

Questo è il dato qualitativamente più importante per l'interpretazione: **il semplice fatto di trasportare energia attraverso un grafo di legami non emerge come strategia ottimale di reclutamento**, quando un trasferimento passivo alternativo attraverso contatti non legati può rendere disponibili quanti alle coppie che ancora possono unirsi.

Il confronto a budget è parziale: il numero massimo di passaggi non garantisce la stessa energia ai medesimi atomi e non crea un controllo strutturalmente isomorfo. Non è stato preregistrato un criterio di superiorità per questa quarta condizione: la sua osservazione costituisce **evidenza descrittiva contro una pretesa di specificità**, non una nuova ipotesi confirmatoria.

## Integrità fisica e verifiche

- I mondi iniziali sono **nativi** e partono tutti da zero legami; dopo la selezione lo stato materiale completo dei quattro fork è identico prima di intervenire.
- L'intervento energetico conserva esattamente il totale di energia delle particelle, non cambia posizione, specie, grafo dei legami, identificativi o RNG. Poiché la sorgente selezionata è una componente massimale legata, `bond_only` trasferisce energia soltanto fra gli stessi ID originali al momento del fork e **non aumenta la loro energia totale**.
- La chimica isolata conserva il bilancio completo secondo le regole originali M6 di spesa energetica, energia immagazzinata nei legami e dissipazione; tutte le combinazioni osservate sono verificate con `world.check()`.
- Il campione comprende **640 mondi originali e 16 shard senza esclusioni**. Ogni shard conserva il SHA256 del protocollo preregistrato e del selettore storico M7.5 invariato. La prima sorgente di ogni shard viene rigenerata da zero con hash e RNG identici, quindi verificata anche dopo uno sweep sperimentale.
- Un test sintetico riproduce esattamente con **`alife.chemistry.form_bonds` originale** la formazione (energie, legami, energia dissipata) ottenuta con il nuovo codice sperimentale per un'unica coppia accettata. L'estensione del test oracle su casi naturali informativi viene documentata separatamente quando disponibile.
- Il primo workflow di sviluppo aveva un'aspettativa errata sul controllo non legato in un caso sintetico (tra due particelle c'era realmente un gradiente energetico sufficiente). È stato **corretto soltanto il test**, senza alcuna modifica alla fisica o alle soglie. La suite definitiva e tutti gli shard del workflow #44115455468 sono **PASS**.
- Un **ricalcolo indipendente del ZIP originale** conferma esattamente il numero dei seed, dei 16 shard e delle 32 lotterie per regime, l'invarianza dello stato iniziale e i conteggi dei criteri principali e dei controlli; i valori del report derivano dal dataset primario congelato.

## Limiti — ciò che NON abbiamo scoperto

1. Il test è un **controfattuale sperimentale isolato** con la chimica originale M6 ma un sorteggio casuale per coppia **introdotto apposta**: non è il naturale funzionamento completo dell'universo M6–M7.3.
2. La modifica energetica agisce su tutti i contatti possibili lungo i legami del mondo, non unicamente sul reticolo originale selezionato; tuttavia, in quanto componente massimale, i legami che coinvolgono i materiali della sorgente selezionata sono interni. Gli effetti su competizione locale di valenza/energia sono possibili.
3. Tutti gli aggregati selezionati hanno **topologia arborea** (640 alberi, zero cicli), dimensioni 5–16, non membrane o sistemi chiusi. Due legami anziani non implicano che il componente intero sia vissuto 20 tick con la stessa configurazione.
4. La conduzione sui legami non viene **attivata o regolata dall'aggregato stesso**; è una regola fisica programmata dall'esperimentatore. Non è comportamento metabolico emergente.
5. Un legame originale–esterno è acquisizione di materia, non una **discendenza indipendente**. Non abbiamo osservato un programma informativo copiato, una riproduzione, un confine autoregolato o una macchina di auto-mantenimento. **Non è nata vita artificiale.**

## Passo M7.9 proposto

M7.8 ha separato con successo la **causalità locale della redistribuzione energetica** dai moti e dallo stream RNG globale; tuttavia i contatti non legati sembrano più efficienti per il reclutamento istantaneo.

Per M7.9 sarebbe più utile progettare un meccanismo di **allocazione energetica localmente selettiva e causalmente dipendente dalla struttura**, confrontando budget **esattamente equiparati e destinazioni comparabili**, anziché aggiungere genericamente altre forme di diffusione. Occorre però distinguere rigorosamente le nuove regole programmate dall'esperimentatore dalle proprietà emergenti, e prima di parlare di organismi misurare davvero il mantenimento del materiale originale, la riparazione e la produzione di un discendente con informazione trasmessa.

**Esito scientifico:** una rete chimica spontanea può essere il percorso fisico lungo cui un quanto si redistribuisce, cambiando la reattività di un contatto esterno in modo causalmente verificato. **Non** emerge una prova che tale percorso sia specificamente favorito rispetto a qualsiasi altro sistema di diffusione passiva.


## Audit indipendente post-hoc usando il motore chimico M6 ORIGINAL — PASS

Dopo la chiusura del dataset primario, ho eseguito un audit che **non** richiama la funzione sperimentale M7.8 di formazione dei legami, ma la routine originale **`alife.chemistry.form_bonds`** con una sorgente `raw()` accoppiata per coppia e un wrapper temporaneo sull'iteratore dei candidati. Il wrapping è ripristinato subito dopo ciascuno sweep; il motore originale `src/` non viene modificato e nessun evento aggiunge seed ai criteri scientifici.

- [GitHub Actions #44116475310 — verifica PASS](https://github.com/kkongiu/alife-lab/actions/runs/44116475310).
- [Artifact completo dell'audit post-hoc #14341984655](https://github.com/kkongiu/alife-lab/actions/runs/44116475310/artifacts/14341984655).
- [Script indipendente `tools/m7_8_posthoc_native_oracle.py`](../tools/m7_8_posthoc_native_oracle.py).
- [Test sintetico di equivalenza con `form_bonds` originale](../tests/test_m7_8_posthoc_native_oracle.py).

Il programma rigenera da zero **tutti e 640 gli stati sorgente naturali**, verificandone hash completi, IDs, legami, stato RNG e conteggio delle estrazioni. Poi identifica, nel dataset già congelato, tutti i seed con un **confronto discordante** nel numero di opportunità energetiche o di formazioni originali–esterne fra conduzione e controllo, più il primo seed selezionato in ognuno dei 16 shard. Per questi **46 seed**, ripete **tutte le quattro condizioni e tutte le 32 lotterie accoppiate**, cioè **5.888 sweep di formazione con il codice M6 originale**.

**5.888/5.888 PASS:** totale di coppie candidate, identità e ordine dei nuovi legami, reazioni originali–esterne, hash completo dopo lo sweep, energia, dissipazione e stato casuale coincidono con le osservazioni M7.8. Gli altri 594 seed hanno comunque stato sorgente ricostruito e risultati originari conservati; l'audit fisico degli sweep M6 è concentrato sui casi che determinano le decisioni e sulle sentinelle preregistrate dei 16 shard.

Si tratta di una **verifica post-hoc di correttezza sul medesimo campione**, non di una nuova replica con 46 o 640 universi indipendenti supplementari. **Il criterio primario resta 26/32 e quello secondario resta 25/30**, senza modifiche.
