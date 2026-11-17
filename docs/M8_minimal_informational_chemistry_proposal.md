# M8 — Proposta di nuova fisica locale per trasmissione ereditaria dell'informazione

**Stato: proposta progettuale, NON implementata.** Il motore originale M6 e il mondo sperimentale M7.3 non devono essere riscritti. L'eventuale M8 deve partire con uno **schema fisico versionato distinto** e report comparabili ai controlli storici, senza attribuire retroattivamente nuove proprietà ai risultati M6–M7.

## Decisione del gate M7.14

Sospendere le campagne indiscriminate basate su numero di anelli, sopravvivenza e re-formazioni di legami. Un nuovo seed è utile soltanto se discrimina un'ipotesi sul **trasferimento causale di una proprietà da una struttura materiale ad un'altra**.

Nel modello corrente la sequenza di specie in un aggregato può costituire *una descrizione* dell'organizzazione, ma nessuna reazione legge **specificamente l'ordine della sequenza** come un template per organizzare materiale distinto. Le probabilità M6 dipendono da contatti locali, specie, energia, valenza e (eventualmente) catalisi della specie vicina. Ciò non esclude in senso matematico altre forme di trasmissione emergente, ma è un collo di bottiglia ingegneristico verificato.

## Due famiglie scientifiche possibili

**A. Reti autocatalitiche alimentate (RAF).** Reazioni collettivamente catalizzate, con substrati ricavabili da un insieme di risorse esterne (food set). È il percorso più vicino alla nozione di metabolismo pregenetico e permette organizzazioni non basate su un genoma. Un RAF è un *criterio strutturale* di una rete reattiva, non automaticamente una dimostrazione di persistenza, replicazione o vita. Si deve comunque provare la chiusura dinamica e la possibilità di propagazione/composizione ereditaria in gruppi distinti.

**B. Templating locale di polimeri informativi.** Monomeri di almeno due specie che possono concatenarsi senza essere programmaticamente obbligati a formare un "organismo"; un polimero già emerso può aumentare *localmente* la probabilità di assemblare un secondo polimero di specie corrispondenti. La reazione resta stocastica e consuma energia, monomeri e spazi. I due oggetti devono essere composti di ID materiali distinti, poi separarsi. Errori/mutazioni sono un risultato della chimica imperfetta, non l'esecuzione di una funzione \`copy()\`.

**Scelta operativa proposta per M8.0:** iniziare da **B**, perché permette un controllo causale diretto del contenuto informativo trasmesso. RAF/A rimane una possibile alternativa se B non supera il proprio gate. Non si ipotizza che la vita debba per definizione avere DNA o polimeri: è una scelta sperimentale con risultati interpretabili.

## Fisica candidata, dichiaratamente NUOVA

| Componente | Regola microscopica proposta | Perché necessaria |
|---|---|---|
| Monomeri 0/1 | Atomi materiali con specie A/B già presenti nella popolazione iniziale, posizioni su griglia, ID persistenti | Permette una sequenza identificabile senza memorizzare un genoma separato |
| Legame di backbone B | Reazione locale reversibile con massimo due legami backbone e costo energetico esplicito | Permette polimeri ordinati che possono nascere casualmente da materiale libero |
| Contatto templante H | Contatto locale, di tipo distinto dal backbone, fra due monomeri vicini su catene diverse; affinità per coppie di specie definite e budget/energia espliciti | Permette di leggere localmente la composizione dell'organizzazione preesistente, senza assegnare un nome o una "fitness" alla catena |
| Catalisi di attacco B | Se due nuovi monomeri adiacenti condividono una configurazione H coerente con due posizioni consecutive del template, la probabilità di B è moltiplicata per un fattore finito, mantenendo un tasso base non nullo | Questo è il solo nuovo canale informativo proposto; favorisce una copia, ma non la crea direttamente |
| Distacco | H può rompersi per cinetica/energia; B rimane soggetto ad altra cinetica reversibile | Permette strutture materialmente separate, una condizione osservabile per parlare di "figlie" |
| Ambiente | Quantità finita di monomeri, sorgenti di energia e dissipazione. Nessun aumento gratuito di materia o energia, né generazione automatica di una seconda catena | Tiene distinto consumo energetico e successo informativo |

**Attenzione:** la fisica M6 vincola a 2 i legami di alcuni atomi e immobilizza i legati. M8 deve quindi definire una seconda categoria di contatto H con una valenza specifica e gestire la geometria di catene affiancate. Non basta riutilizzare la saturazione di M6: un anello di valenza piena non avrebbe siti per interagire con il prodotto. Ogni cambiamento deve essere dichiarato in un nuovo schema, testato e versionato; i vecchi risultati devono restare replicabili.

## M8.0 — Prima scrivere test che possano fallire

Gli esperimenti iniziali NON devono cercare una "vita" dichiarata dal numero di repliche. Prima occorre verificare:

1. **Contabilità:** il consumo di materiale e quanti energetici è esplicito per B/H, dissociazione e prodotti; fonte e scarti sono separati; nessun atomo compare senza risorsa.
2. **Controllo positivo artificiale, esplicitamente artificiale:** una breve catena-template costruita in laboratorio produce, eventualmente, una seconda catena con la nuova legge e può separarsene. Il risultato verifica una capacità implementativa: **NON** è vita emersa.
3. **Controlli negativi allo stesso budget:** identica configurazione ma H disabilitato; H attivo con identità di corrispondenza del template rimescolata; tasso globale di B allineato ma senza riconoscimento del template; energia assente. Confrontare anche il numero dei contatti veri, non soltanto il numero di prodotti.
4. **Controllo causale della sequenza:** modificare una sola specie nel template mediante intervento controllato; conservare il resto della geometria, le risorse, le lotterie per coppia e — quando fattibile — i conteggi totali delle specie. Il cambiamento deve propagarsi preferenzialmente alla posizione corrispondente della **figlia**, e scomparire con canale H neutralizzato.
5. **Niente \`clone_structure()\`:** il codice non può scrivere una seconda sequenza nel grafo; deve soltanto proporre reazioni locali B/H.
6. **Rilevatore esterno:** usare lineage audit con ID materiali disgiunti, provenienza temporale, almeno 20 tick di persistenza della figlia e struttura fisicamente separata dal template. Un duplicato visuale non vale.

Se questi controlli non riescono, **STOP**: correggere l'ipotesi/rulebook, non lanciare migliaia di seed.

## M8.1 — Origine spontanea e generalizzazione

Solo dopo il gate M8.0, eseguire nuovi mondi **senza catene/template/organismi precostruiti**: soltanto monomeri, sorgenti, spazi e leggi locali identiche. La prima catena candidata deve derivare da incontri/reazioni spontanee e non da una fixture sintetica.

Predefinire prima dei risultati:
- durata, densità, distribuzione delle specie, quantità di energia e monomeri, seed completi e negativi;
- identificazione non retrospettiva del primo template, marcatura dei materiali e tempo di formazione;
- discendenza materiale disgiunta e separazione fisica dai precedenti;
- **almeno tre generazioni informative successive** e una misura di fedeltà, mutazioni e stabilità dei polimeri;
- controllo di parent-edit abbinato alla stessa disponibilità di monomeri/energia e alla stessa lotteria chimica;
- controlli negativi rate-matched e per identità rimescolata;
- soglie confermative preregistrate con minimo numero di seed e di confronti discordanti.

Un successo del templating aumenterebbe la plausibilità di una trasmissione informativa, **non** dimostrerebbe automaticamente metabolismo autonomo o selezione naturale. L'evoluzione darwiniana richiede anche variazione ereditaria con conseguenze riproducibili sulla produzione/persistenza delle discendenze.

## M8.2 — Ereditarietà, variazione e selezione

Soltanto dopo una vera discendenza causale, introdurre il test che conta:
- varianti informazionali che nascono **per imperfezione delle reazioni**, non per una procedura che le genera intenzionalmente;
- almeno due generazioni successive in cui la variante è trasmessa al materiale disgiunto, con controlli di ambiente;
- una differenza di successo associata causalmente alla variante, che scompare con perturbazione parentale abbinata;
- capacità di usare energia/materiale per sostenerne il ciclo, non semplicemente somigliare ad una sequenza.

## Regola di governo della ricerca

Per ogni milestone:
**ipotesi scientifica → legge fisica dichiarata → controllo positivo e negativi → misura di causalità → registrazione campioni e soglie → simulazione → audit indipendente → conclusione anche negativa.**

Sospendere le ulteriori campagne M7 che aggiungono solo ring count, durata di legami o energia media. Non modificare mai la fisica storica per riscrivere gli esiti precedenti.

## Letteratura di riferimento

- Hordijk et al., *Self-generating autocatalytic networks: structural results, algorithms and their relevance to early biochemistry* (2024), https://pmc.ncbi.nlm.nih.gov/articles/PMC11286130/
- *Template-Based Catalysis and the Emergence of Collectively Autocatalytic Systems* (2026), https://pmc.ncbi.nlm.nih.gov/articles/PMC12939731/
- Artificial Life, *Introduction to Digital Evolution*, https://alife.org/encyclopedia/digital-evolution/introduction-to-digital-evolution/
- Artificial Life, *Avida Digital Evolution Platform*, https://alife.org/encyclopedia/digital-evolution/avida/

La letteratura è usata come ispirazione metodologica, **non** come dimostrazione che le nuove regole producano automaticamente la vita.
