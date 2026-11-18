# M8.0 — Prima fisica locale informativa: preflight del templating, non vita spontanea

**18 novembre 2026 — esperimento preregistrato COMPLETO.** Un nuovo motore sperimentale, isolato dal simulatore storico M6/M7, permette a **una catena artificiale preassemblata** di influenzare chimicamente il tipo di monomero catturato in una catena distinta. I risultati del controllo positivo su 32 seed superano **tutti e quattro i gate fissati in anticipo**, con un controllo negativo che rimescola l'identità informativa mantenendo le stesse opportunità di cattura. **Nessuna forma di vita è stata prodotta e nessuna catena iniziale è nata spontaneamente in questo esperimento.**

## Tracciabilità

- **Preregistrazione prima dell'implementazione della nuova legge e prima dei dati:** [commit b047b83](https://github.com/kkongiu/alife-lab/commit/b047b83159275248fc44a162bb8d62ece696a955).
- **CI completo PASS**, suite storica originale + nuova fisica + 32 × 6 esperimenti: [Actions #44255549853](https://github.com/kkongiu/alife-lab/actions/runs/44255549853).
- **Dati grezzi di tutte le 192 traiettorie**, eventi di cattura, nuove coppie chimiche B, sequenze e identificativi: [artifact #14405927400](https://github.com/kkongiu/alife-lab/actions/runs/44255549853/artifacts/14405927400).
- [PR #44 in bozza](https://github.com/kkongiu/alife-lab/pull/44), su **ramo indipendente direttamente da master**, senza merge.
- [Nuova fisica M8, separata: \`src/alife_m8/sandbox.py\`](../src/alife_m8/sandbox.py).
- [Runner \`tools/m8_0_preflight.py\`](../tools/m8_0_preflight.py); [protocollo congelato](../campaigns/m8_0/protocol.json); [test della fisica](../tests/test_m8_0_sandbox.py).
- [Decisione M7.14](https://github.com/kkongiu/alife-lab/pull/42) e [specifica M8 di partenza](https://github.com/kkongiu/alife-lab/blob/research/m7-14-mechanism-decision-gate/docs/M8_minimal_informational_chemistry_proposal.md).

Il primo tentativo di test automatici [#44255438060](https://github.com/kkongiu/alife-lab/actions/runs/44255438060) ha rilevato **esclusivamente** una incongruenza del test che confrontava il nome generico preregistrato della nuova fisica (\`M8.0-new-physics-not-M6\`) con la stringa esatta di versione della libreria (\`M8.0-local-B-H-sandbox-v1\`). La singola asserzione è stata corretta **senza modificare la legge, le soglie o il protocollo**; la suite e i dati conclusivi sono PASS.

## Perché M8 non è un proseguimento banale di M7

Nel motore originale M6/M7 i legami si formano in base a distanza, energia, valenza e specie; la chimica ha generato anelli spontanei ma nessuna discendenza informazionale dimostrata. M7.12 ha ricondotto la richiusura degli anelli a ripetuti tentativi di chimica ordinaria, e M7.13 non ha mostrato adattamento dopo un danno precedente.

Qui **introduciamo dichiaratamente una nuova legge fisica di templating**: un contatto chimico verticale H può preferire un monomero la cui specie corrisponde alla specie di un monomero già presente in una catena laterale. Il programma non contiene comandi come \`clone\`, \`make_offspring\`, \`copy_sequence\` o un generatore che scriva una catena figlia: crea soltanto **reazioni locali stocastiche** fra monomeri, legami e risorse. Ma il **principio di affinità fra specie** è stato programmato nel modello: non è un principio emergente scoperto.

## Nuova chimica locale dichiarata

Il mondo è volutamente piccolo e semplice: reticolo chiuso **10 × 5**, una particella per sito, due specie materiali 0/1, ID che non vengono riutilizzati, una riserva finita di monomeri per specie, risorsa energetica intera. Le particelle una volta catturate **non si muovono**; questa restrizione geometrica va risolta o motivata in una fisica autonoma successiva.

Due famiglie di contatto:
- **B (backbone)**: legami reversibili fra celle orizzontali adiacenti, valenza B massima 2. Nuova formazione con probabilità base **0,03**, oppure **0,90** se entrambi i candidati hanno contatti H verso due partner di una catena B già legata. Rottura spontanea per legame **0,0005/tick**.
- **H (contatto templante debole)**: contatti verticali temporanei, valenza H massima 2. Se un monomero adiacente appartiene ad una catena B, un sito vuoto può **catturare** un monomero da una delle riserve di specie con probabilità **0,55/tick**. La specie preferita della cattura corrisponde alla specie del vicino con probabilità **0,90**; la specie opposta viene scelta con probabilità **0,10**. Il nuovo contatto H conserva un quanto di energia e può dissociarsi con probabilità **0,035/tick**.

Nella condizione informativamente rimescolata, la **frequenza di cattura è esattamente la stessa (0,55)** e viene creato un contatto H che consuma la stessa energia. La specie preferita è tuttavia derivata da una pseudo-identità dipendente dalla coordinata e dal seed, **indipendente dalla vera specie del materiale vicino**. Questo è un controllo a opportunità energetiche/reattive confrontabili, non un controllo inattivo.

Tutte le lotterie usano valori pseudocasuali deterministici indicizzati da **seed, tick, sito e tipo di reazione**: cambiare un bit della sequenza parentale non riavvia né altera i sorteggi delle stesse celle e passi. Le reazioni non possono usare ID di genitore selezionati dal test. La "parentela" viene inferita da contatti fisici realmente creati e da ID materiali separati, non da una variabile di fitness.

### Risorse e costi

| Operazione | Costo energetico totale | Destinazione |
|---|---:|---|
| Adsorbimento senza template | 1 | 1 dissipato |
| Cattura H da un vicino con B | 2 | 1 dissipato + 1 immagazzinato in H |
| Formazione di B | 2 | 1 dissipato + 1 immagazzinato in B |
| Dissociazione di H | Rilascio 1 immagazzinato | 1 dissipato, nessuna nuova energia |
| Rottura di B | Rilascio 1 immagazzinato | 1 torna all'energia disponibile |

Il bilancio verificato **ad ogni passo di tutte le 192 traiettorie** è:

\[
N_{\mathrm{particelle}} + N_{\mathrm{monomeri\ nel\ bagno}}=N_{\mathrm{iniziale}}
\]

\[
E_{\mathrm{disponibile}} + E_B + E_H + E_{\mathrm{dissipata}}=E_{\mathrm{iniziale}}
\]

La fixture positiva comincia artificialmente con una catena B di quattro monomeri e quindi con tre quanti già immagazzinati nei legami; i costi sono contabilizzati nel valore iniziale e non compaiono dal nulla durante la simulazione.

## Campione esatto e controlli

**32 seed numerici prestabiliti 50001–50032**, con **sei regimi per seed** e **120 passi per regime**, quindi **192 universi fisici sperimentali** ma soltanto 32 unità appaiate per il confronto informativo. Ogni condizione positiva inizia con una **catena artificiale già montata** a y=1, x=3–6:

- Template originale: **0101**.
- Template modificato: **0111**, alterando **una sola** specie nel monomero di x=5, senza cambiare geometria, ID originali, energia o monomeri disponibili nel bagno.
- Due regimi informativi con entrambe le sequenze: **templated** e **shuffled_identity**.
- Due controlli ulteriori con catena originale: **no_template** e **unpowered**.

Per la causalità puntuale si osserva **in anticipo** il primo monomero realmente catturato nella cella x=5,y=2 in entrambi i mondi della coppia. Per la produzione completa si osserva la catena B dei quattro **ID nuovi e fisicamente distinti** nella fila y=2, x=3–6: i tre legami B devono essere presenti, nessuno dei quattro monomeri deve avere ancora un contatto H con la catena iniziale, e lo stesso materiale/ordine deve rimanere presente per **almeno 20 passi consecutivi**. Non vengono selezionati a posteriori i siti favorevoli o le strutture più simili.

## Quattro gate preregistrati: TUTTI PASS

| Gate | Soglia congelata | Risultato | Verdetto |
|---|---|---|---|
| Bilancio fisico e riproducibilità | 192/192 bilanci materia/energia validi; stessa identica ripetizione di un seed | **192/192**, replay identico | **PASS** |
| Edit puntuale del template, stessi sorteggi | ≥20/32 specie della prima cattura cambiate con lettura informativa, **0/32** col canale rimescolato | **32/32** vs **0/32** | **PASS** |
| Prodotto materiale B separato, 4 posizioni, sequenza esatta e persistenza ≥20 | ≥8/32 con template 0101, e almeno 5 più del controllo rimescolato | **18/32** vs **0/32** | **PASS** |
| Controlli senza canale/energia | 0 nuove particelle nel regime senza template (background 0) e nel regime non alimentato | **32/32** ciascuno | **PASS** |

I dataset mostrano **un numero comparabile di catture e legami B** nei regimi che leggono la sequenza e nei controlli con identità rimescolata. Il modello non supera i gate semplicemente perché il regime di controllo è "spento": il controllo rimescolato continua a catturare particelle e costruire legami, ma non copia preferenzialmente la specifica sequenza 0101.

### Interpretazione cauta dei 32/32

Questo risultato non ha la forza statistica apparentemente spettacolare di un fenomeno inatteso. La nuova legge sceglie fra **esattamente due specie**: con lo stesso numero casuale, invertire il bit preferito inverte necessariamente la scelta del bit catturato, anche nel caso minoritario del mismatch. Perciò, **quando la stessa cella cattura un monomero in entrambi i fork, il 32/32 è sostanzialmente atteso dalla logica programmata della legge**. Non è una scoperta di apprendimento spontaneo.

È comunque una prova operativa importante: la propagazione riguarda il **materiale catturato in un vero evento chimico locale**, non un'istruzione che assegna una sequenza a una figlia. Nel controllo indipendente dalla specie del template, la stessa alterazione del genitore produce **zero** variazioni al primo sito catturato.

Il risultato più impegnativo del preflight è la **formazione e liberazione di una catena B distinta per almeno 20 passi**: **18/32** nell'arm di affinità informativa e **0/32** con identità rimescolata, pur potendo entrambi assemblare polimeri in base alle stesse regole B/H. Anche questo è un risultato del nostro **sistema progettato**, non una forma di vita spontanea.

## Limitazioni e ostacolo esplicito a M8.1

**Il modello M8.0 non può ancora dare origine spontanea a un template a partire da un mondo vuoto.** Il protocollo di calibrazione ha fissato \`background_adsorption=0\` per isolare il canale H: senza una catena iniziale e senza catture spontanee, la griglia rimane vuota e non nascono legami B.

Questo è un **limite strutturale reale** della fisica corrente, non semplicemente un problema di scegliere più seed. Per M8.1 servirà **una legge di nucleazione/adsorbimento basale finita e non nulla**, oppure una popolazione iniziale di monomeri liberi con movimento e chimica spontanei, definita **in una nuova versione di fisica M8.1** prima della simulazione, senza riscrivere M8.0 dopo aver visto i risultati. Il background basale e il templating devono usare la stessa contabilità energetica e materiale; gli universi M8.1 dovranno partire **senza catene artificialmente assemblate**.

Altri limiti:
- La griglia è piccola, orientata e anisotropa; i legami strutturali sono orizzontali e i contatti informativi verticali; le particelle sono fisse dopo l'adsorbimento. È un modello di reazioni superficiali, non un fluido chimico realistico.
- L'osservatore positivo ha una fila e una sequenza **prestabilite** perché è una fixture di test. Non dimostra scoperta spontanea di forme o discendenza generazionale.
- La specie del monomero non può mutare dopo la sua cattura; il sistema produce errori di assemblaggio ma non abbiamo dimostrato varianti ereditarie attraverso tre generazioni.
- Lo pseudo-template rimescolato elimina intenzionalmente l'informazione parentale pur conservando la frequenza locale di cattura; i conti globali di energia e contatti sono verificati, ma ogni confronto resta un confronto fra **due leggi candidate**, non una misura dell'evoluzione naturale.
- I controlli senza template e senza energia hanno zero catture soprattutto perché il background è zero e/o non c'è energia disponibile: sono controlli necessari di integrità, non i più informativi sul meccanismo. Il confronto realmente discriminante è **templated vs shuffled**.
- Non c'è nascita spontanea di un organismo, nessun metabolismo indipendente, nessuna fitness con selezione darwiniana, nessun ecosistema né ereditarietà dimostrata su più generazioni.

## Cosa fare dopo: NON lanciare direttamente migliaia di semi M8.1

M8.0 autorizza, secondo i gate congelati, **la progettazione e la validazione di M8.1**. Non significa che si possa ripetere lo stesso motore con \`template_sequence=None\` e ottenere nuove strutture: con background zero ciò è impossibile.

M8.1 richiederà una fisica specificamente versionata che introduca la possibilità di **prima nucleazione senza template**, un benchmark positivo microscopico che non si affidi a un organismo precostruito, nuovi seed e controlli a tassi realizzati comparabili, un endpoint di origine spontanea indipendente dalla posizione, e un rilevatore di eventuali catene figlie per ID completamente diversi. Quando M8.1 funziona, **M8.2** potrà chiedere se un'alterazione informativa viene trasmessa oltre una generazione, e se questa differenza influenza causalmente la persistenza/produzione di una struttura.

**Conclusione:** la fisica M8.0 trasferisce *per progettazione* un'informazione di composizione con reazioni locali reali e costi finiti, e il preflight corrisponde ai controlli. **Non è emersa vita.** Adesso la domanda scientifica realmente nuova è se, con un meccanismo di nucleazione dichiarato e senza template preimpostati, possano comparire spontaneamente strutture che diano origine a materiale informativamente correlato.
