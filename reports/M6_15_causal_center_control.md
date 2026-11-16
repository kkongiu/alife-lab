# M6.15 — Una particella interna non mostra una protezione causale robusta del bordo

**Data:** 16 novembre 2026. **Stato:** tutti i test e le 1000 simulazioni del campione preregistrato completati con successo. L'interpretazione deve distinguere il controllo causale **immediato** dalle differenze **di traiettoria** a lunga distanza.

## Riproducibilità e pre-registrazione

- [Protocollo congelato prima della scrittura del runner e di qualsiasi risultato: `0e2211e`](https://github.com/kkongiu/alife-lab/commit/0e2211e3598ab76655278f64f94758e3dddf3bed); [chiarimento regola donor/destinazione remota `2eaff13`](https://github.com/kkongiu/alife-lab/commit/2eaff1387a7e23a2e8940571aeef057281402c76), anch'esso prima del runner.
- [GitHub Actions riuscito #43866867213](https://github.com/kkongiu/alife-lab/actions/runs/43866867213): regressioni complete, 5 shard, verifica 1000/1000 mondi e hash del protocollo. Il primo avvio aveva una semplice discordanza nel nome di un parametro nel test; risolta prima dei risultati.
- [Dati grezzi comprensivi di tutti gli universi non selezionati: artifact #14225872646](https://github.com/kkongiu/alife-lab/actions/runs/43866867213/artifacts/14225872646).
- [PR sperimentale #27](https://github.com/kkongiu/alife-lab/pull/27). `master` e `src/` invariati, nessuna modifica alle regole energetiche e chimiche native.

## La domanda

L'affermazione "una particella interna protegge la parete" è **una possibile relazione causale**, non ricavabile dal semplice fatto che un residente rimanga immobile dentro una struttura per 241 passi.

In M6 la funzione `break_bonds` esamina tutti i legami in ordine canonico **all'inizio del passo**, prima di movimento e formazione chimica; il tasso di rottura è lo stesso valore `break_probability=0.002` per tutti i legami. Se si parte dallo **stesso grafo di legami** e dallo **stesso RNG**, il solo spostamento di una particella **non legata** non può modificare direttamente quali legami originali si rompono nel **primo passo**. Questo è verificabile senza ipotesi biologiche.

## Metodo controfattuale

- **1.000 seed nuovi** enriched `15001–16000`, a densità M6.4 (264 particelle, reticolo toroidale 24×24, zero legami iniziali). Ogni universo viene osservato fino a 600 tick per individuare la **prima struttura nativa ammissibile** con 8 atomi e 7 legami lungo il bordo 3×3. **Una sola coppia di interventi per universo**.
- Copie identiche dello stato originale. In un braccio il centro è **vuoto**; nell'altro contiene una particella nativa libera e mobile. Se nel mondo reale il centro è vuoto, si trasferisce nel centro un donatore remoto, isolato dai quattro vicini. Se già occupato, il residente viene trasferito in una cella remota libera, isolata dai quattro vicini. Scelta deterministica senza guardare l'esito futuro.
- Lo spostamento cambia **solo la posizione** di un atomo, mantenendo esattamente invariati gli ID, la specie, il numero di particelle, gli otto materiali del bordo, le sette connessioni originali, l'energia di ogni particella, il totale energetico, il numero di estrazioni e lo stato RNG. Il braccio naturale non subisce alcun intervento. La prima coppia realmente selezionata in ciascuno shard è oggetto di un replay indipendente di controllo.
- Si eseguono **120 passi** su entrambi i bracci. L'endpoint è il **primo evento di rottura di uno dei sette legami originali**, anche se in seguito lo stesso legame si riforma. La permanenza dei sette legami è valutata ai tempi prestabiliti 10, 30, 60 e 120 passi. Si registra anche la prima formazione dell'ottavo legame, soltanto finché gli originali sono integri.
- Scopo: valutare l'effetto complessivo dell'**intervento di posizione**; non è possibile isolare completamente il contributo "solo locale" della particella al centro, perché la sua posizione remota cambia anch'essa e la sequenza di estrazioni globali può desincronizzarsi.

## Risultati

**1.000/1.000 universi completati**, **102 coppie controfattuali ammissibili**. Gli altri **898 mondi** non hanno prodotto una struttura a sette legami nelle condizioni di selezione; non sono stati scartati dai risultati.

| Fenomeno | Risultato |
|---|---:|
| Coppie create | **102** |
| Sorgenti naturali inizialmente con centro vuoto | 86 |
| Sorgenti naturali inizialmente con centro occupato | 16 |
| Identità della rottura originale al **primo passo** | **102/102, PASS** |
| Differenza nello stato RNG già al primo passo | 42/102 |
| Differenza dello stato RNG entro 120 passi | 90/102 |

### Persistenza dei sette legami originali

| Orizzonte | Centro occupato | Centro vuoto | Differenza occupato − vuoto | Coppie discordanti favorevoli occupato / favorevoli vuoto |
|---|---:|---:|---:|---:|
| 10 passi | 91/102 | 89/102 | +2,0 punti % | 6 / 4 |
| 30 passi | 73/102 | 71/102 | +2,0 punti % | 16 / 14 |
| 60 passi | 46/102 | 45/102 | +1,0 punti % | 16 / 15 |
| 120 passi | 21/102 | 18/102 | +2,9 punti % | 13 / 10 |

Le differenze sono modeste, non monotone e non identificano una protezione o autoregolazione. In particolare, **23/102** coppie sono discordanti al tempo 120, ma soltanto **3** in più favoriscono il braccio occupato. Non si è effettuata una selezione post-hoc di orizzonti, densità, specie o seed.

### Sottogruppi preregistrati

I **86 mondi originariamente vuoti** producono a 120 passi 18 bracci occupati integri contro 15 vuoti (differenza +3/86). Nei **16 mondi originariamente occupati** il confronto è **3 vs 3**, differenza nulla. Questi sottogruppi descrivono origini diverse dell'intervento: il campione di 16 è troppo piccolo per affermare equivalenza statistica.

## Un avvertimento sul flusso dei numeri casuali

La condizione iniziale usa lo stesso PCG64, ma M6 campiona in ordine sequenziale il tentativo di rottura dei legami, il movimento di tutte le particelle e poi i candidati alla formazione di nuovi legami. Un diverso centro occupato introduce opportunità di movimento e legame differenti; la lista di candidati alla formazione può cambiare e **consumare un diverso numero di estrazioni RNG**. Quando ciò avviene, il successivo controllo di rottura di un medesimo legame può ricevere **un numero casuale diverso**. Questo è **un percorso causale computazionale reale dell'intervento su questa implementazione**, ma non equivale a un meccanismo biologico o a una modifica chimica diretta della resistenza dei sette legami.

**Conclusione primaria:** la previsione meccanicistica di **nessun effetto diretto sul primo passo** è confermata in tutti i 102 confronti; il confronto a lungo termine non offre un segnale robusto che la presenza del residente stabilizzi il bordo.

## Implicazioni per A-Life

Il risultato riduce l'interesse a fare milioni di repliche del medesimo meccanismo geometrico: sappiamo già che le barriere spontanee esistono e possono durare. Qui non abbiamo trovato un circuito di feedback fra residente e parete. **Un contenitore non diventa un organismo perché conserva materia al proprio interno.**

Per cercare un vero comportamento emergente occorre individuare un meccanismo di **informazione funzionale**: una configurazione materiale che modifica riproducibilmente la probabilità di produrre un'altra configurazione della stessa famiglia o che contribuisce a ripristinare la propria struttura oltre il tasso di ricomposizione previsto dalla sola chimica locale.

Il percorso consigliato è un audit indipendente delle capacità delle leggi M6 (nascita, catalisi, bilancio energetico, possibilità di ereditarietà), seguito da un esperimento M7 su **nuove regole esplicitamente dichiarate** e basato su controlli senza replicatori impiantati. Questo non deve modificare retroattivamente M6.
