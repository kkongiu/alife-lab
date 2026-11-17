# M7.14 — Reset scientifico: la precisione degli esperimenti non sostituisce un meccanismo di ereditarietà

**Data:** 17 novembre 2026. **Decisione:** **STOP** alle ulteriori campagne M7 su conteggio anelli, durata dei legami e trasporto energetico come sostituti della trasmissione informativa. **GO** alla **progettazione** di una nuova chimica M8 esplicitamente versionata, con controlli negativi sulla presenza del canale informativo e prova causale. Nessun nuovo organismo, nessuna nuova simulazione "di nascita" e nessuna fisica modificata in questo audit.

## Perché questo documento esiste

Fra M6.14 e M7.13 abbiamo imparato molte proprietà interessanti e *verificate* della chimica nativa: sorgenti energetiche, contatti di conduzione, legami e strutture spontanee, reattività, reclutamento materiale, persistenti anelli nativi, probabilità di richiusura e risposta a lesioni controllate. Tuttavia **la direzione scientifica ha perso concentrazione**: gli esperimenti sono diventati progressivamente più raffinati nel misurare aspetti passivi dello stesso motore senza fornire un **meccanismo falsificabile di trasferimento di informazione ereditaria**.

Due risultati recenti mostrano il problema:
- **M7.12:** 442 formazioni reali su 9.049 candidature della coppia originariamente tagliata (4,88%), coerenti con il 5% fisso della normale chimica M6; gli estremi restano adiacenti e ancorati in tutti i 17.993 tick a rischio. L'esperimento spiega la richiusura senza introdurre una funzione di riparazione. [Report M7.12](https://github.com/kkongiu/alife-lab/blob/exp/m7-12-native-reclosure-exposure/reports/M7_12_native_reclosure_mechanism.md).
- **M7.13:** il primo danno **non favorisce** il secondo recupero. Solo 121/275 discordanti favoriscono l'esperienza del danno rispetto al controllo intatto; solo 111/277 rispetto al placebo con energia riallocata ma primo legame preservato, contro una soglia preregistrata di due terzi. [Report M7.13](https://github.com/kkongiu/alife-lab/blob/exp/m7-13-first-lesion-history/reports/M7_13_damage_history.md).

Va riconosciuto un errore di **priorità della ricerca**: un primo audit **M7.0 aveva già individuato la mancanza di regole esplicite di copiatura, di genomi e di nascita/morte delle particelle**, e suggerito un ciclo di risorse, reazioni e possibili processi di templating. Ciò avrebbe dovuto restringere prima lo spazio degli esperimenti. [Rapporto M7.0](https://github.com/kkongiu/alife-lab/blob/analysis/m7-0-physical-capability-audit/reports/M7_0_capability_audit.md) (nella serie originale delle PR; eventuali percorsi storici differiscono fra i rami).

Non è corretto dire che gli esperimenti siano stati "inutili": hanno stabilito falsificazioni precise ed escluso interpretazioni suggestive ma errate. Non è però corretto proseguire per inerzia.

## Scelta ingegneristica: ramo separato da master

L'intera serie M7 rimane una sequenza di **PR sperimentali in bozza, non integrate**, dove molti rami dipendono dal ramo immediatamente precedente. Continuare ad aggiungere prove su questa stessa catena aumenta la difficoltà di orientarsi.

**M7.14 nasce quindi direttamente da \`master\`**, come rapporto/strumento di decisione indipendente e non come un'altra PR sovrapposta alle precedenti. Nessuna legge originale viene modificata; \`master\` rimane intatto. La scelta del ramo non cancella o discredita gli studi storici, che restano citati e recuperabili.

- [Preregistrazione M7.14, commit \`8c8f8f9\`, prima dello script](https://github.com/kkongiu/alife-lab/commit/8c8f8f92e2f5ff9fec1d4a92437328c84eb7b704).
- [Codice audit eseguibile](../tools/m7_14_decision_gate.py).
- [Test sulle false discendenze e sul modello fisico originale](../tests/test_m7_14_decision_gate.py).
- [Protocollo machine-readable](../campaigns/m7_14_decision/protocol.json).
- [Proposta di nuova chimica informativa M8](../docs/M8_minimal_informational_chemistry_proposal.md).

## Audit computazionale M7.14

L'esecuzione controlla **direttamente i file nativi originali** \`config.py\`, \`particles.py\`, \`chemistry.py\`, \`dynamics.py\`, \`world.py\`, registrandone l'hash SHA256 e verificando tramite AST alcune funzioni chiave. Confronta in un test dinamico i campi del materiale e delle specie su **12 seed deterministici 41001–41012**, con **40 passi nativi ciascuno** della configurazione M2 quick originale. Non si tratta di nuovi campioni a sostegno o contro la nascita di organismi; sono **test di implementazione**.

| Proprietà | Stato verificato | Significato |
|---|---|---|
| Identità e tipo delle particelle | **Invariati** in 12/12 mondi per 40 passi | Attualmente non viene creato materiale e non cambia la specie di un monomero durante \`World.advance\` |
| Rete di legami | **549 nuove formazioni complessive** nei 12 universi | Il mondo genera davvero nuova organizzazione geometrica mediante M6 |
| Campo informativo ereditabile esplicito | **Assente** negli attributi originali del \`ParticleStore\` e delle specie | Non esiste una sequenza informativa persistente programmata come campo separato |
| Reazione che legga una sequenza di un template | **Assente come regola esplicita** nella chimica nativa | Il tasso di formazione dipende localmente da specie, valenza, energia, adiacenza e dalla specie di eventuali catalizzatori, non da un riconoscimento di sequenze |
| Ereditarietà di pattern materialmente disgiunti | **Non osservata in questo audit** | Questo controllo non dimostra una legge di trasmissione ereditaria |
| Capacità di produrre pattern materiali simili senza nascita di particelle | **Non esclusa logicamente** | Materia a popolazione costante può riorganizzarsi in strutture simili o persino in copie causali; servirebbe dimostrarle, non negarle per definizione |

**Precisione necessaria:** il legame chimico può influenzare l'energia, la valenza e la mobilità locale, così da generare indirettamente correlazioni strutturali. La mancanza di una regola di templating **esplicita** non è un teorema di impossibilità di qualunque informazione emergente, e l'audit dinamico non tenta di dimostrare una tale impossibilità.

### Il nuovo rilevatore: testarlo prima di usarlo

Un rilevatore di discendenza degno del nome non deve confondere:
- due anelli della stessa forma, semplicemente esistenti nello stesso mondo;
- un aggregato che si divide e riusa gli stessi ID, scambiato per nuovo discendente;
- una prima reazione senza prole di seconda e terza generazione;
- un programma che chiama direttamente una funzione \`clone\`, presentato come nascita spontanea;
- una sequenza del genitore cambiata che non provoca alcuna differenza nella sequenza del prodotto.

M7.14 implementa una **validazione strutturale del registro di discendenza**, richiedendo ID materiali disgiunti, ordine temporale e almeno tre archi generazionali. Implementa anche un test su eventi **di esempio** con una singola modifica di bit del genitore e controllo di stessa energia, stessi substrati e stessa lotteria.

| Fixture sintetica del rilevatore | Verdetto |
|---|---|
| Tre generazioni vere nel registro, con discendenza esplicita e materia distinta | **Accettato come fixture positiva**, mai come vita |
| Strutture uguali senza genitore materialmente identificato | Correttamente rifiutate |
| Figlia che condivide gli ID materiali del genitore | Correttamente rifiutata |
| Una sola generazione e poi nessuna prole successiva | Correttamente rifiutata |
| \`explicit_clone_instruction\` che produce materialmente una copia | Correttamente rifiutata |
| Modifica del genitore che causa la stessa modifica della figlia in dati controllati | Accettato **solo come fixture positiva dichiarata** |
| Genitore mutato, figlia invariata | Correttamente rifiutato |

Tutti questi controlli usano **registrazioni artificialmente costruite**, non universi che abbiano prodotto spontaneamente una discendenza. Lo script marca esplicitamente \`physical_provenance_externally_audited = false\` nei risultati della funzione di validazione: un JSON auto-dichiarato non basta per dimostrare che un intervento causale è davvero avvenuto. Una futura prova richiederà log fisici indipendenti e confronti controfattuali reali.

## La decisione finale: cambiare cosa intendiamo per progresso

**STOP — serie M7.** Ulteriori seed, durate, trasporti energetici, legami e lesioni *senza una nuova ipotesi su una variabile informativa causale* non sono prioritari. Gli audit già completati M7.0–13 restano parte del patrimonio scientifico, con risultati anche negativi.

**GO — solo alla progettazione di M8.** La nuova domanda è:

> Una struttura materiale nata spontaneamente può modificare causalmente la sequenza o composizione di una **seconda struttura costruita con materiale diverso**, conservando quella differenza lungo più generazioni, grazie a leggi di reazione locali, consumo energetico e risorse finiti?

Due possibili ipotesi:
1. **Rete autocatalitica collettiva (RAF)**, sostenuta da risorse ambientali: può fornire organizzazione chimica e circolarità energetica anche senza genoma codificato; una rete RAF non è automaticamente un organismo.
2. **Templating locale** fra catene di monomeri eterogenei: la presenza di una sequenza materiale aumenta, senza imporre un risultato, la probabilità di ottenere una seconda catena di composizione corrispondente, che poi si separa.

**Preferenza iniziale: templating.** È possibile trasformare la questione in una prova relativamente precisa: cambiare una sola posizione del template e controllare se cambia la posizione corrispondente del prodotto, a parità di energie, risorse e sorteggi, mentre uno shuffle informativo allo stesso budget annulla l'effetto. La fisica **deve essere introdotta come nuova legge**, non spacciata per proprietà emergente del motore storico.

### Condizioni minime di accettazione prima di nuovi mondi

- Una legge di reazione **locale e stocastica**, non una routine che costruisca la "figlia" chiamando una funzione di clonazione.
- Nessun organismo o catena di partenza **preinseriti** nella campagna dichiarata spontanea; una fixture con template già costruito è ammessa soltanto come *controllo positivo artificiale*.
- Conservazione della materia ed energia, substrati finiti, dissipazione esplicita, distacco fisico parent–child.
- **Controlli negativi a risorse e velocità di reazione comparabili**: senza template, identità templante rimescolata, controllo non energeticamente alimentato.
- Trasmissione causale di almeno una differenza informativa del materiale originale, con ID della prole disgiunti e sorteggi chimici accoppiati.
- Fino a **tre generazioni informative successive** con variazioni/errore misurati prima di parlare di ereditarietà. Tre generazioni da sole non dimostrano evoluzione darwiniana.
- Seed e soglie preregistrati **solo quando la legge e i controlli microfisici saranno implementati e verificati**. Se i controlli negativi generano presunta ereditarietà, stop e correzione del rilevatore; se il meccanismo non produce il controllo positivo, stop e revisione esplicita della legge.

Il documento [M8 — Proposta di nuova fisica informativa](../docs/M8_minimal_informational_chemistry_proposal.md) contiene la suddivisione in M8.0 (leggi e prove microscopiche), M8.1 (origine spontanea senza template predefiniti) e M8.2 (ereditarietà, variazione e selezione), con controlli e condizioni di arresto.

## Limiti filosofici e scientifici

La letteratura sui **RAF sets** distingue chiusura autocatalitica e risorse ambientali; gli ecosistemi di **evoluzione digitale**, come Avida, illustrano che il passaggio informativo alla prole è una proprietà codificata nel sistema fisico/computazionale, ma un sistema Avida possiede già il linguaggio di istruzioni necessario alla copiatura. Non avrebbe senso dire che un nostro organismo "nasce spontaneamente" se pre-programmassimo esattamente il suo meccanismo completo di duplicazione.

Nel nuovo M8 dovremo programmare **le leggi possibili**, non il risultato individuale né la sequenza che deve apparire. Se otteniamo soltanto la riproduzione di un template sintetico noto, avremo un controllo positivo di implementazione, non vita. Se un insieme materiale emerge spontaneamente e trasmette una variazione con discendenza indipendente e fitness differenziale, quello sarebbe molto più interessante, ma ancora da verificare con criteri rigorosi.

Riferimenti:
- [Self-generating autocatalytic networks: structural results, algorithms and their relevance to early biochemistry (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11286130/)
- [Template-Based Catalysis and the Emergence of Collectively Autocatalytic Systems (2026)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12939731/)
- [Artificial Life — Introduction to Digital Evolution](https://alife.org/encyclopedia/digital-evolution/introduction-to-digital-evolution/)
- [Artificial Life — Avida](https://alife.org/encyclopedia/digital-evolution/avida/)

**Conclusione in una riga:** *Abbiamo verificato che il motore sa organizzare materia e distribuire energia. Non abbiamo trovato una trasmissione causale ereditaria. M7.14 arresta le esplorazioni che non misurano questo divario; il prossimo lavoro sensato è progettare una legge locale capace di essere messa alla prova.*
