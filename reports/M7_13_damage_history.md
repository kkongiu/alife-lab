# M7.13 — Prima lesione e seconda sfida: nessuna memoria strutturale adattiva positiva

**Data:** 17 novembre 2026. **Studio preregistrato completo:** 640/640 nuovi mondi, 16/16 shard e intera suite di regressioni **PASS**. Sono stati selezionati naturalmente **627** anelli di 4/6/8 atomi; ogni mondo ha prodotto tre storie fisiche di **240 passi** dopo il checkpoint originale. **ENTRAMBI gli endpoint confermativi NON RAGGIUNTI**: una prima vera lesione peggiora descrittivamente l'esito della seconda sfida rispetto sia al mondo non danneggiato sia a un placebo con la stessa riallocazione iniziale dell'energia, ma con il legame conservato.

## Provenienza e preregistrazione

- [Protocollo congelato PRIMA del runner M7.13 e prima dei dati M7.12: commit `bb4f5ad`](https://github.com/kkongiu/alife-lab/commit/bb4f5ad536d4bf23e09286cdd9eae74b42468aff).
- [Actions M7.13 #44177201548 — full pytest, 16 shard fissi, 640/640 mondi, merge: **PASS**](https://github.com/kkongiu/alife-lab/actions/runs/44177201548).
- [Dati integrali, 640 universi e 1.881 storie sperimentali: artifact #14368829871](https://github.com/kkongiu/alife-lab/actions/runs/44177201548/artifacts/14368829871).
- [Runner M7.13](../tools/m7_13_damage_history.py), [protocollo](../campaigns/m7_13_history/protocol.json) e [PR #41 in bozza](https://github.com/kkongiu/alife-lab/pull/41).
- Motore originale `src/alife`, M6, originali M7.3/M7.11 e `master` **immutati**; nessuna PR integrata.

## L'ipotesi

M7.11 ha mostrato che in molti anelli spontanei la chimica M6 ricrea un legame rimosso; M7.12 ha individuato la spiegazione osservativa più semplice: gli estremi restano adiacenti, spesso soddisfano le condizioni native di formazione e ciascuna candidatura affronta la normale soglia M6 del **5%**.

M7.13 domanda se l'esperienza di un primo danneggiamento comporti una **maggiore capacità futura** di recuperare un **secondo** danno rispetto allo stesso materiale rimasto indenne per lo stesso periodo. Per non scambiare l'energia liberata dalla prima rottura con l'esperienza topologica del danno, abbiamo un **terzo controllo a energia iniziale equivalente**: trasferiamo alle particelle l'intera energia del legame scelto senza eliminare il legame. È una manipolazione **non fisica ordinaria**, perché l'energia del legame viene fissata artificialmente a zero; il motore M6 rimane però invariato dopo il checkpoint e la stessa configurazione di energia-zero può esistere tramite decadimento.

## Selezione e tre interventi accoppiati

- **640 nuovi mondi seed `31001–31640`**, disgiunti da M7.11–12. Sono iniziati con zero legami, 264 particelle native, 16 sorgenti energetiche, chimica M6 reversibile e conduzione M7.3 originale.
- Si importa e chiama, **senza modificarlo**, il selettore M7.11 `scan_first_native_aged_ring`: primo ciclo massimale nativo a 4,6,8 nodi, stesso materiale e stessi legami per almeno 20 snapshot successivi, primo checkpoint eleggibile t≥120 e massimo t600.
- **627/640** mondi con anello idoneo (**558 quadrati, 58 esagoni e 11 cicli di otto**); tutti i 13 mondi senza anelli sono archiviati come null, senza sostituzione. **627** seed sono le unità indipendenti; tre regimi e 240 tick non generano migliaia di mondi indipendenti.
- Due coppie di ID originali vengono fissate **immediatamente**: il primo legame in ordine lessicografico per la prima perturbazione, e il **secondo legame in ordine lessicografico** come bersaglio distinto della seconda.
- Si clona il checkpoint nativo in **tre** microstati esattamente identici prima della prima manipolazione:

| Braccio | Prima manipolazione al checkpoint originale |
|---|---|
| **`first_lesion`** | Rimuove solo il primo legame originale e restituisce integralmente l'energia chimica immagazzinata ai suoi estremi senza ulteriore dissipazione né RNG |
| **`energy_only_first_sham`** | Conserva il primo legame e la sua valenza, ma ne porta artificialmente a zero l'energia di legame e la restituisce agli stessi estremi; la **distribuzione dell'energia tra particelle è IDENTICA** a `first_lesion` a t0 |
| **`no_first_lesion`** | Nessuna prima manipolazione; anello iniziale intatto, stessa energia totale e RNG, diversa energia di particella rispetto alle due condizioni precedenti |

Tutti e tre i bracci proseguono **120 passi fisici nativi M6** con conduzione energetica M7.3 originale. Nessun nuovo meccanismo di apprendimento, bonus di ricostituzione o riconoscimento del danno viene aggiunto. Tra due manipolazioni tutti i cambiamenti di legami, energia, geometria e RNG sono conseguenze delle leggi originali.

**Alla fine dei 120 passi**, il secondo target, già scelto prima, viene tagliato e integralmente rimborsato **se e solo se** esiste ancora in quel braccio. Se il target è già scomparso, il braccio **non viene scartato, non cerca un altro target e viene classificato come FALLIMENTO intention-to-treat**. Si prosegue comunque con altri **120 passi** di chimica e movimento M6 più conduzione originale M7.3.

La prima lesione **non deve necessariamente essersi richiusa** entro il secondo checkpoint: condizionare su una precedente guarigione selezionerebbe i sopravvissuti e introdurrebbe un bias. La permanenza del primo legame viene registrata soltanto come risultato descrittivo.

## Criteri preregistrati

**Primario:** tra almeno 40 mondi con anelli, almeno 25 confronti discordanti e almeno **2/3** dei discordanti devono favorire l'esperienza di una prima lesione vera rispetto al controllo senza prima lesione, sulla probabilità di **riformare realmente** il secondo specifico legame nella seconda finestra di 120 tick, *prima di qualunque vera rottura di altri legami originali nello stesso braccio*. Rotture e riformazioni nello stesso tick sono contate come rotture. Mancanza del secondo target al checkpoint intermedio = fallimento.

**Secondario:** esattamente lo stesso criterio di riformazione della seconda coppia, ma confronto `first_lesion` vs `energy_only_first_sham` con distribuzione iniziale di energia delle particelle identica. La stessa soglia >=2/3 e gli stessi minimi. Per entrambe le misure, un eventuale successo significherebbe un **effetto di regime della storia**, **non** memoria attiva o apprendimento senza ulteriori controlli.

La connettività finale di tutti gli ID, l'effettiva ricostituzione di ogni legame originale e il tempo al secondo recupero sono **descrittivi**: non possono essere sostituiti ai criteri registrati dopo la visione dei dati.

## Risultati completi sui 627 anelli

| Misura | Prima vera lesione | Nessuna prima lesione | Restituzione energetica senza prima lesione |
|---|---:|---:|---:|
| Secondo legame esistente e tagliato al checkpoint t120 | **566** | 577 | **583** |
| Secondo target già assente a t120, contato come insuccesso | 61 | 50 | **44** |
| **Riformazione del secondo target prima di ulteriori rotture originali** | **366** | 399 | **421** |
| Riformazione del secondo target e tutti gli ID originali connessi a t240 | **324** | 374 | **395** |
| Tutti gli ID originali ancora connessi a t240 | **440** | 505 | **516** |
| Esatto insieme di tutti gli originali legami dell'anello presente a t240 | **225** | 274 | **303** |
| Primo legame originale presente a t120 | **472** | 586 | **586** |
| Tempo medio al secondo recupero sui successi (tick dopo secondo taglio) | 16,75 | 16,32 | **15,99** |

### Criterio primario: NON RAGGIUNTO, campione sufficiente

| Risultato appaiato | Mondi |
|---|---:|
| Secondo recupero soltanto con storia di primo danno | **121** |
| Secondo recupero soltanto senza primo danno | **154** |
| Secondo recupero in entrambi | 245 |
| Nessun recupero in entrambi | 107 |
| **Confronti discordanti** | **275** |

La frazione favorevole all'esperienza è **121/275 = 44,00%**, molto al di sotto dei **2/3** richiesti. Sono rispettati i minimi preregistrati (627 source-world e 275 discordanti), quindi il verdetto è **`not_met_favorable_fraction`**, non carenza del campione.

### Criterio secondario: NON RAGGIUNTO, campione sufficiente

| Risultato appaiato | Mondi |
|---|---:|
| Secondo recupero soltanto con primo danno reale | **111** |
| Secondo recupero soltanto con sham energetico e legame mantenuto | **166** |
| Secondo recupero in entrambi | 255 |
| Nessun recupero in entrambi | 95 |
| **Confronti discordanti** | **277** |

La frazione favorevole al primo danno reale è **111/277 = 40,07%**, anch'essa ampiamente sotto i due terzi richiesti, con sample size valido. Verdetto **`not_met_favorable_fraction`**.

**Non invertiamo retroattivamente la direzione della domanda:** il maggior numero di recuperi nei controlli è un'evidenza **descrittiva** contraria all'ipotesi di adattamento positivo, non una nuova pretesa di successo confirmatorio preregistrato contro il danno.

## Che cosa significa e che cosa non significa

**Risultato concreto:** nello stesso regime fisico, dopo uguale durata temporale, un primo taglio non accresce la probabilità di recuperare la seconda coppia originale. Anzi, il materiale originale si conserva in media meglio nei due controlli senza una vera prima interruzione topologica. La disposizione energetica identica nel controllo `energy_only_first_sham` aiuta a separare una parte della redistribuzione iniziale dall'effetto della rimozione meccanica.

**Limiti essenziali:**

1. Il controllo che azzera l'energia immagazzinata in un legame senza romperlo è un'**ablazione artificiale**, non un evento spontaneo del mondo M6; dopo il checkpoint la fisica rimane originale.
2. Nonostante energie **delle particelle** identiche al t0 fra taglio e sham energetico, la topologia e la valenza differiscono, così come l'energia immagazzinata nel legame, la probabilità di rottura successiva e il consumo futuro dello stream RNG globale. La differenza non isola un singolo nesso causale microscopico.
3. Al tempo della seconda lesione le condizioni **non** sono state ricombinate per rendere identiche energie, geometria e numero dei legami; queste differenze **sono mediatori** della storia. Il risultato riguarda l'effetto complessivo dell'aver subito la prima perturbazione.
4. Il primo legame può essere assente al momento del secondo: un target mancante è fallimento come stabilito, ma questa classificazione misura la capacità composita di arrivare ancora danneggiabile al secondo checkpoint e richiudere poi il nuovo taglio; non è un confronto condizionale fra soli sopravvissuti.
5. Il secondo target prestabilito è il **secondo legame lessicografico originale**, non il legame più fragile, più energico o più vicino a una sorgente; la strategia elimina la selezione retrospettiva favorevole.
6. Un vero episodio di formazione `BondEvent(kind='form')` è **chimica reversibile**. Non dimostra un programma di riparazione, né metabolismo, apprendimento, memoria strutturale regolata, ereditarietà, autoriproduzione o una forma di vita artificiale.

## Integrità del workflow

- Protocollo M7.13 registrato in commit `bb4f5ad` **prima del risultato M7.12** e del runner; nessuna modifica delle soglie dopo osservazione dei risultati.
- Full suite `pytest` prima delle simulazioni: **PASS**. Sono stati eseguiti 16 shard fissi, senza nuovi seed in base agli esiti. Tutti i 640 mondi selezionati o null fusi con hash della preregistrazione e dei moduli M7.3/M7.11 originali invariati.
- La prima sorgente selezionata di ogni shard dispone di un replay completo del braccio nativo senza primo danno e successiva seconda lesione, riprodotto senza l'osservatore M7.13 e verificato tramite **hash finale completo e stato RNG**.
- La prima lesione e il controllo a energia azzerata mantengono **esattamente identici tutti i livelli energetici delle particelle**, così come l'energia totale, lo stato RNG e la dissipazione storica. Il legame è fisicamente diverso per costruzione.
- La seconda lesione conserva l'energia globale corrente di ciascun braccio; tutti i mondi continuano 120+120 passi originali. Verifiche energia/RNG e cinque+ checkpoint fissati: global t1,30,60,120,121,150,180,240 per ogni trattamento.
- Dati grezzi contengono tutte le 627×3 evoluzioni e i 13 null. Gli indicatori dei target mancanti al secondo checkpoint sono registrati esplicitamente e contati **FALSE**.

## Direzione di ricerca

M7.11 e M7.12 hanno reso verificabile una spiegazione semplice della richiusura: la geometria mantiene adiacenti estremi ancora ancorati, e la regola M6 prova ripetutamente a ricreare il legame con probabilità intorno al 5% ogni candidatura ammissibile.

M7.13 aggiunge un risultato negativo sull'ipotetico **rafforzamento tramite esperienza**: un primo danno non migliora il secondo recupero, nemmeno rispetto a un controllo con identica redistribuzione energetica iniziale ma nessuna rottura topologica.

Per un M7.14 davvero diverso, servirebbe uno studio mirato di una **variabile interna di memoria** causalmente misurabile e trasmissibile: ad esempio variazione strutturale che persista, regoli le probabilità future di ricostituzione e si riproduca in un nuovo gruppo, confrontata con una perturbazione placebo fisicamente equiparata. In assenza di tale meccanismo non si può chiamare `adattamento` il semplice ritorno stocastico ad un legame precedente.

**Conclusione:** la simulazione mostra chimica reversibile e reti di materia stabili; non ha ancora generato organismo digitale, metabolismo, eredità, replica o apprendimento emergente.


## Audit indipendente integrale dei 640 mondi e 1.881 fork — PASS

Dopo il congelamento del dataset M7.13, è stato eseguito un **secondo programma di verifica** con una propria implementazione di rimozione del legame, rimborso energetico, azzeramento della sola energia di legame, registrazione degli eventi chimici e ricostruzione degli indicatori. Questo programma **non importa il codice sperimentale M7.13 di intervento o valutazione**; continua a chiamare soltanto il simulatore fisico M6 e la conduzione M7.3 originari e il selettore di anelli M7.11 già verificato indipendentemente nella campagna precedente.

- [GitHub Actions #44178238047 — **PASS**](https://github.com/kkongiu/alife-lab/actions/runs/44178238047).
- [Dati di audit indipendente #14371365904](https://github.com/kkongiu/alife-lab/actions/runs/44178238047/artifacts/14371365904).
- [Script separato `tools/m7_13_independent_posthoc.py`](../tools/m7_13_independent_posthoc.py) e [test sintetico](../tests/test_m7_13_independent_posthoc.py).

Sedici shard di audit (i medesimi gruppi numerici prestabiliti) hanno ricostruito da seed tutti i **640** mondi, ritrovando esattamente i **627** primi anelli selezionati e tutti i **13** mondi negativi. Per ciascuno dei 627 positivi hanno rifatto le **tre storie complete di 240 tick**, ovvero **1.881/1.881 fork fisici originali**, con esito **PASS**.

Coincidono esattamente ogni checkpoint temporale di energia, posizioni, specie, connessioni, hash fisico, stato RNG/numero delle estrazioni, formazione e rottura native del primo e del secondo bersaglio, eleggibilità del secondo taglio, tutta l'energia dissipata e immagazzinata e gli endpoint intention-to-treat.

L'audit recupera in modo indipendente gli stessi risultati: **366** successi su **566** secondi tagli possibili nel primo danno, **421/583** nello sham energetico, **399/577** nel controllo non danneggiato, con i target già assenti conteggiati come fallimenti. I confronti binari preregistrati restano **121 contro 154** e **111 contro 166**, entrambi sotto il requisito prefissato dei due terzi.

**Non è una nuova replica statistica:** tutti i replay validano gli **stessi** seed e non aumentano la numerosità del campione. I due giudizi preregistrati restano **NON RAGGIUNTI**.
