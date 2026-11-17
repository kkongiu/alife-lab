# M7.10 — Il primo legame spontaneo trattiene materia, ma non abilita un ulteriore reclutamento selettivo verificabile

**Data:** 17 novembre 2026. **Stato:** campagna preregistrata completa **640/640** nuovi mondi naturali; **122** checkpoint di primo reclutamento prima della prima rottura dei legami originali; **366** fork di 120 tick; suite completa e sedici shard **PASS**. **Nessuno dei due criteri confermativi raggiunto**: criterio primario sotto la soglia minima di confronti discordanti (**0**), criterio secondario con **12/33** discordanti favorevoli al mantenimento del legame (richiesto **≥2/3**). Non è dimostrato un feedback funzionale di auto-espansione o auto-mantenimento.

## Fonti verificabili e cronologia

- [Protocollo bloccato prima di scrivere l'esperimento o osservarne i risultati: commit `20050f7`](https://github.com/kkongiu/alife-lab/commit/20050f7f75617eded66f8fead1efaaa0dfd0e559).
- [Esecuzione principale, regressioni e 16 shard **PASS**: GitHub Actions #44165823040](https://github.com/kkongiu/alife-lab/actions/runs/44165823040).
- [Dati grezzi di tutti i 640 seed, positivi e negativi, inclusi tutti i 366 fork e i relativi checkpoint: artifact #14364493654](https://github.com/kkongiu/alife-lab/actions/runs/44165823040/artifacts/14364493654).
- [PR #38 sperimentale in bozza](https://github.com/kkongiu/alife-lab/pull/38), su ramo `exp/m7-10-recruited-bond-function`; [runner principale `tools/m7_10_recruited_link_function.py`](../tools/m7_10_recruited_link_function.py).
- **`master`, `src/`, protocolli e programmi di M6–M7.9 invariati. Nessuna PR integrata.**
- Il primissimo workflow di sviluppo #44165649156 aveva fallito soltanto per un mondo sintetico di test con energia totale configurata 24 ma dati per 32; la fixture è stata corretta (energia della prima particella 8 anziché 16) **senza cambiare la fisica o il protocollo**; la suite finale e i sedici shard sono PASS.

## Perché M7.10

M7.8 ha verificato un effetto causale reale e limitato della redistribuzione energetica sulla *singola formazione* di un nuovo legame: la stessa geometria, gli stessi legami e la stessa estrazione casuale per coppia potevano dare esiti differenti. M7.9 ha mostrato che il modo particolare in cui la conduzione nativa distribuisce energia **non supera** assegnazioni artificiali a parità di identico multinsieme energetico dell'aggregato.

La domanda qui è quindi qualitativamente diversa: **una particella che entra in un aggregato tramite un vero nuovo legame chimico produce una capacità funzionale successiva di attrarre altra materia?** E, se sì, questo dipende dall'energia che circola lungo **proprio quel nuovo legame**, o dall'aver aggiunto una connessione strutturale?

Mantenere la prima particella già acquisita non è di per sé una risposta: sarebbe una proprietà quasi tautologica del collegamento presente rispetto al controllo privo del collegamento. L'endpoint è pertanto un **secondo reclutamento distinto**, mai la mera presenza del primo legame.

## Campione originale, interamente spontaneo

- **640 nuovi semi numerici `28001–28640`**, un mondo originario per seed, non sovrapposti alle campagne precedenti. **16 shard fissi da 40**; tutti gli insuccessi selettivi conservati.
- Dall'universo originale M7.3 (264 particelle native, zero legami iniziali, reticolo periodico 24×24, 16 sorgenti energetiche distribuite, movimento con costo 1 e nessuna catalisi) è scelto **esattamente con il modulo M7.5 invariato** il primo componente chimico naturale con 5–16 ID materiali, almeno 4 legami nativi e almeno due legami presenti da 20 tick continui, con valenza residua; prima possibilità al tick120, massimo tick500. L'aggregato originale non viene inserito.
- Successivamente lo stesso mondo avanza con chimica M6 e conduzione M7.3 lungo i legami, al massimo per **120 tick**. Un osservatore registra la **prima** formazione spontanea di un legame tra un ID del materiale originale e un ID esterno. Se un qualsiasi legame ORIGINALE si spezza prima o nello stesso tick della formazione, il seed è **escluso permanentemente**. Non si cerca un'altra opportunità più favorevole.
- L'evento di formazione è realmente prodotto dal motore originale M6; il legame è presente nel grafo fisico al checkpoint di fork. Se più eventi idonei avvengono nello stesso tick, si sceglie la coppia di ID lessicograficamente minore. Nessuna selezione basata sugli esiti futuri.

**Esito della selezione:** **122/640** mondi (19,06%) raggiungono il primo reclutamento prima di qualunque rottura originaria, in media **28,22 tick** dopo la selezione iniziale. Gli altri **518** restano nel dataset:

- **397** mondi: almeno un legame originale si rompe prima di una formazione esterna idonea; nessun successivo evento viene selezionato.
- **121** mondi: nessuna formazione idonea entro il periodo di osservazione senza una precedente rottura originaria.

Tutti i **122** aggregati al momento del primo reclutamento derivano da **reti arboree**, non da anelli o membrane. Il gruppo di 122 è un campione **condizionato** ad aver già realizzato un reclutamento pre-rottura, non una popolazione indistinta di tutti gli universi.

## Tre fork identici alla partenza, tre interventi

Dallo **stesso istante poststep** vengono clonate le posizioni, specie, identificativi, legami originali, energie di particelle e legami, buffer delle sorgenti, stato RNG, contatori chimici e fisici.

| Braccio | Intervento causale |
|---|---|
| **`native_intact`** | Conserva il nuovo legame chimico e usa, per i successivi 120 tick, la conduzione energetica originale M7.3 lungo tutti i legami presenti; chimica e movimento M6 immutati |
| **`bond_intact_conduction_ablated`** | Conserva il nuovo legame **fisicamente intatto** (stesso costo energetico già pagato, stesse energie, valenze e posizioni, RNG e chimica), ma durante la conduzione poststep sopprime esclusivamente i trasferimenti lungo **quella precisa coppia materiale di ID**, anche se il legame successivamente si riforma; tutti gli altri legami conducono secondo M7.3 |
| **`recruited_edge_excised_refunded`** | Rimuove il solo nuovo legame e restituisce **tutta** l'energia in esso immagazzinata ai due estremi, con la stessa divisione intera nativa secondo l'ID; **nessuna dissipazione aggiuntiva**, né nuovo sorteggio RNG. La dissipazione già pagata alla formazione originale rimane pagata in tutti i bracci. La coppia può riformare un legame spontaneamente in seguito. |

**Vincolo energetico:** subito dopo l'ablazione, i mondi hanno **identica energia totale conservata**. I due bracci col legame fisico iniziano perfettamente identici e hanno il medesimo stato fisico/RNG **anche dopo il primo passo nativo, prima del diverso trasferimento poststep**. Il braccio con legame rimosso conserva il bilancio totale ma differisce in energia disponibile alle particelle, valenza, legami e in seguito nel consumo dello stream RNG globale. Pertanto non isola una sola collisione chimica nel senso dell'esperimento M7.8.

### Endpoint congelati prima dei dati

**Primario:** nei successivi 120 passi, almeno un evento nativo `FORM` lega un membro del **gruppo iniziale esteso** (tutti gli ID originali più la prima particella reclutata) a un **SECONDO ID esterno distinto**, e lo fa **PRIMA di qualsiasi rottura reale dei legami originali della sorgente** nel proprio braccio (una rottura seguita da ricostituzione nello stesso tick è comunque rottura). La ri-formazione del **primo** legame fra i medesimi due ID non conta come secondo reclutamento. Confronto `native_intact` vs `bond_intact_conduction_ablated`; richiede **≥40 seed selezionati**, **≥25 confronti discordanti** e **≥2/3** di questi favorevoli al braccio originale.

**Secondario:** **stesso identico endpoint** ma confronto `native_intact` vs `recruited_edge_excised_refunded`, con i **medesimi** minimi e la stessa quota favorevole.

**Caveat semantico preregistrato:** un evento di formazione che coinvolge il **primo reclutato** può essere contato nel criterio sopra anche se quest'ultimo si è nel frattempo separato dalla sorgente; quindi è monitorata **anche** una versione più rigorosa dell'endpoint, che chiede che il nuovo secondo ID sia nella componente ancora connessa di *tutti* gli ID originali. Questa misura è **descrittiva**, non sostituisce il criterio congelato.

La mera sopravvivenza del primo legame, le dimensioni della componente finale e la conservazione degli edge originali sono **esiti descrittivi**, non vie alternative per dichiarare successo dopo i dati.

## Risultati completi

| Misura su 122 fork per braccio | Nuovo legame mantenuto | Nuovo legame mantenuto, conduzione proibita | Legame rimosso + energia restituita |
|---|---:|---:|---:|
| **Almeno un secondo esterno reclutato PRIMA della prima rottura originale** | **25** | **25** | **34** |
| Secondo esterno reclutato e coerente con tutti gli ID originari PRIMA della rottura | **24** | **24** | **24** |
| Nessuno dei legami originali si rompe entro 120 tick | 30 | **32** | **36** |
| Primo ID esterno reclutato **ancora nella componente originaria** a tick120 | **74** | **74** | 51 |
| Qualsiasi ulteriore ID esterno nella componente originaria a tick120 | **53** | 52 | 52 |
| Numero medio di trasferimenti di un quanto lungo il primo legame selezionato | **33,7377** | **0** | 19,7787 |
| Saldo passivo medio di trasferimenti energetici al confine degli ID originali | **+12,5246** | +1,3607 | +7,3525 |
| Dimensione media componente finale che contiene tutti gli ID originali, se esiste | 9,6282 | 9,5823 | 8,8421 |

**Attenzione:** il braccio col legame rimosso permette la sua ricostituzione naturale. I trasferimenti energetici medi **19,78** lungo quella coppia sono possibili solo **dopo** che un legame si è riformato: non sono energia condotta attraverso una connessione assente. Gli scambi sono **eventi di un quanto**, potenzialmente ripetuti; non sono nuovi quanti generati e non implicano consumo metabolico.

### Verdetto preregistrato primario: nessun confronto discordante, criterio NON raggiunto

Fra `native_intact` e `bond_intact_conduction_ablated`:

- **25** seed ottengono un secondo reclutamento in **entrambi** i bracci;
- **97** non lo ottengono in **nessuno**;
- **0** seed mostrano un secondo reclutamento soltanto con conduzione;
- **0** lo mostrano soltanto senza conduzione su quel link.

Risultato **`not_met_insufficient_discordant_source_worlds`** (0 contro minimo 25), non un test superato. Non è lecito concludere che i regimi siano in generale equivalenti: i due percorsi energetici differiscono molto, ma **non** su questo specifico endpoint per i 122 mondi e il follow-up prescritto. I regimi mostrano differenze in altre misure (saldo energetico, integrità di alcuni legami originali e dimensione del gruppo), ma non sono prove del successo predefinito.

### Verdetto preregistrato secondario: criterio NON raggiunto

Confronto `native_intact` vs `recruited_edge_excised_refunded`:

| Confronti appaiati sul SECONDO reclutamento pre-rottura | Seed |
|---|---:|
| Secondo reclutamento solo mantenendo il primo legame | **12** |
| Secondo reclutamento solo rimuovendo il primo legame | **21** |
| Secondo reclutamento in entrambi | **13** |
| Nessun secondo reclutamento in entrambi | **76** |

**12/33 = 36,36%** dei seed discordanti favoriscono il mantenimento del legame, ben sotto la soglia **66,67%**. Il campione è sufficiente secondo le soglie preregistrate (**122 seed selezionati, 33 discordanti**), perciò il verdetto è **`not_met_favorable_fraction`**, non mancanza di dati. Non invertiamo la direzione della domanda dopo i dati per presentare la rimozione come una nuova ipotesi confermata.

### Il dato descrittivo più intuitivo: materia trattenuta non equivale a vantaggio di crescita

Il primo ID reclutato è ancora chimicamente connesso al gruppo originale dopo 120 tick in **74/122** mondi con il nuovo link presente, contro **51/122** mondi quando il link viene inizialmente rimosso con restituzione dell'energia del legame.

Confronto appaiato, **non preregistrato come criterio di successo**: 43 seed mantengono il primo reclutato soltanto nel mondo con legame originale, 20 soltanto nel mondo con legame rimosso, 31 lo mantengono in entrambi, 28 in nessuno. Una maggiore permanenza della particella *già legata* è una conseguenza plausibile e in parte aspettabile della presenza fisica del legame. **Non** dimostra auto-mantenimento, dato che la struttura originale non mostra un vantaggio nei nuovi reclutamenti pre-rottura né nella conservazione dei propri legami.

Il confronto più rigoroso del **secondo reclutamento ancora connesso a tutti gli ID originali al momento della sua formazione** è **24/122 in tutti e tre i bracci**. Il confronto appaiato mantenuto vs rimosso presenta **12 seed favorevoli e 12 contrari**, 12 positivi in entrambi e 86 in nessuno: nessun segnale netto di nuova crescita strutturale di secondo livello. Anche questa è analisi **descrittiva**, non un cambio retroattivo dei criteri.

## Integrità e limiti

- Il primo legame è un **vero evento `BondEvent(kind='form')`** prodotto dal modello nativo: nessun nuovo elemento o legame è introdotto per ottenere un risultato favorevole.
- Sono mantenuti i **640/640 seed**, inclusi 397 interrotti alla prima rottura originale e 121 senza un primo nuovo link nel termine previsto. Le tre copie di ciascuna delle 122 sorgenti iniziano con full hash e RNG identici prima degli interventi.
- **La soppressione della sola conduzione sul link mantiene il legame fisicamente presente**. Lo script implementa la medesima sequenza originale M7.3 di proposte energetiche basate su snapshot e budget del donatore, saltando soltanto la coppia selezionata; quando non viene soppressa usa direttamente la funzione M7.3 originale, confrontandola contro l'implementazione previsionale indipendente.
- Tutte le energie spostate dalla rimozione sono **restituzioni di energia già immagazzinata nel legame**, non un'iniezione; la dissipazione storica di formazione resta contabilizzata e nessun sorteggio viene consumato dall'operazione.
- Nel primo tick successivo, le copie col link presente hanno **identico hash materiale e RNG prima del trasporto**, verificato automaticamente. Il braccio col legame rimosso non è tenuto a utilizzare le stesse estrazioni, poiché la chimica nativa consuma RNG anche per i legami presenti.
- **366/366** fork terminati con controllo di ledger energetico e invarianti per tutti e cinque i checkpoint preregistrati (1,10,30,60,120), oltre agli hash finali, contatori dei legami ed eventi di rottura/formazione.
- L'audit fisico indipendente verrà documentato separatamente dopo il suo completamento; anche quando supera i controlli, verifica il medesimo campione e **non** aggiunge nuovi universi.

### Limiti concettuali

1. L'esperimento contiene selezione condizionale: studia **soltanto** gli aggregati che realizzano una prima formazione esterna prima della prima rottura originaria. Non misura la probabilità di nascita di un organismo nel campione intero.
2. La condizione con rimozione cambia topologia, valenza, disponibilità di energia nelle due particelle e **consumo futuro dello stream RNG globale**: i confronti misurano l'effetto complessivo dell'intervento, non quello della sola conduzione o di un singolo bit d'informazione.
3. Nella condizione che mantiene il primo legame ma ne sopprime la conduzione, la fisica nativa prima del trasporto nel primo tick è identica, ma i successivi percorsi di movimento/reazione possono divergere indirettamente per l'energia e l'RNG.
4. Il legame originale può romper-si e riformarsi; una formazione post-rottura non dimostra riparazione mirata, bensì chimica reversibile.
5. La mera aggiunta di atomi non genera discendenti, informazioni ereditarie o una struttura capace di conservare attivamente i propri legami. **Non è un organismo digitale, metabolismo, ereditarietà o autoreplicazione.**

## Proposta di M7.11

Il prossimo esperimento dovrebbe abbandonare la pretesa che **un singolo link passivo** basti a produrre un feedback auto-rinforzante, e passare a **reti native cicliche o topologie con almeno due vie indipendenti**, se sono selezionabili senza inserirle artificialmente. Lo studio dovrebbe richiedere un endpoint di **recupero reale dopo una perturbazione fisica controllata**: ricostituzione di uno specifico materiale dopo rottura, distinguendo la chimica casuale da un vantaggio causale della ridondanza topologica. Un controllo con identico numero di legami, composizione e budget energetico permette di separare gli effetti della topologia dal semplice numero di contatti.

Una alternativa preliminare, prima di molti nuovi universi, sarebbe un **audit formale di raggiungibilità** della fisica M6 (quali strutture cicliche e rami di feedback sono effettivamente generabili nelle densità osservate), per non preregistrare campioni che il modello può difficilmente raggiungere.

**Conclusione:** il primo legame naturale ha una funzione meccanica plausibile di **ritenzione del primo materiale**; non abbiamo però evidenza che quel legame o la sua capacità di condurre energia **causi un secondo reclutamento più frequente** o un fenomeno di auto-mantenimento.
