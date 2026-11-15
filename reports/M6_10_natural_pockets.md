# M6.10 — Anelli spontanei di otto particelle creano cavità geometriche VUOTE

**Stato:** campagna completata con test e replay verificati; **esito preregistrato: `geometric_pocket_without_long_lived_trapping`**. Non c'è prova di intrappolamento naturale di particelle, cellule o membrane biologiche.

**Protocollo congelato PRIMA dell'implementazione:** [commit `9425d971`](https://github.com/kkongiu/alife-lab/commit/9425d97119934e51b3ee4dc8b8155224af903dae), `campaigns/m6_10_pockets/protocol.json`.

**Esecuzione verificata:** [GitHub Actions #43763636346 — PASS](https://github.com/kkongiu/alife-lab/actions/runs/43763636346), suite completa pytest e 100 universi nativi. **Dati grezzi per ogni universo, episodio e caso zero:** [artifact #14181297982](https://github.com/kkongiu/alife-lab/actions/runs/43763636346/artifacts/14181297982).

## Domanda e definizione

In una griglia quadrata 24×24 periodica con movimento di von Neumann, un anello chiuso di **otto particelle** che occupino gli **otto siti del perimetro di un blocco 3×3** racchiude un'unica casella centrale. Se una particella libera è già al centro, i suoi quattro spostamenti cardinali sono impediti dalle particelle dell'anello, finché esse restano fisicamente nei siti circostanti.

L'esperimento non costruisce artificialmente alcun anello: osserva l'eventuale comparsa naturale del bordo geometrico e registra se una particella nativa è effettivamente intrappolata.

**Concretamente, per essere classificato come cavità:** un'unica componente connessa di otto ID materiali, otto legami nativi, grado=2 per ciascun membro, posizioni che corrispondono precisamente agli otto siti attorno a un centro di un quadrato 3×3, considerando le coordinate mod 24 per attraversamenti del bordo toroidale. Non basta una generica firma ciclica di otto particelle: gli anelli allungati non racchiudono necessariamente alcuna casella.

## Metodo e campionamento

50 seed nuovi **9801–9850** × due densità (200 e 264 particelle) = **100 mondi**, inizialmente senza alcun legame, seguiti per 600 tick con la chimica originale M6. Nessun template artificiale, catalizzatore supplementare o nuova legge.

I candidati sono osservati dopo **ogni** tick. Gli episodi di un determinato anello si interrompono al primo **vero evento di rottura** di uno dei suoi otto legami originari, anche se la stessa connessione viene ristabilita entro il medesimo tick; oppure quando la struttura geometrica scompare o cambia. Gli episodi ancora attivi al tick 600 sono dichiarati **censurati a destra** e non usati per inferire durate complete.

Nel momento di comparsa si rileva il contenuto della cella centrale: ID, specie, grado e probabilità di movimento dell'eventuale residente. Se, mentre il bordo materiale rimane integro, l'ID residente cambiasse posizione, il software segnala un errore di invariante.

## Risultati

| Misura | 200 particelle (50 mondi) | 264 particelle (50 mondi) |
|---|---:|---:|
| **Mondi con almeno un anello esatto a perimetro 3×3** | **1** | **3** |
| Episodi materiali continui di tali cavità | **1** | **8** |
| Episodi con una particella libera già presente al centro | **0** | **0** |
| Episodi con un residente naturale intrappolato per almeno 30 tick | **0** | **0** |
| Episodio di cavità più lungo osservato | 11 tick, censurato | **249 tick**, terminato da rottura |
| Insiemi materiali distinti di cicli di dimensione 8, anche non quadrati | 5 | 17 |
| Di questi, con geometria allungata / non perimetro 3×3 | 4 | 14 |
| Insiemi materiali distinti di cicli con almeno 10 particelle | **3** | **7** |

**Totale: 4/100 universi hanno costruito spontaneamente cavità geometriche di una cella**, per **9 episodi osservativi**. Episodi multipli possono essere **riformazioni dello stesso anello materiale nello stesso universo** e non nove cavità indipendenti. Non erano presenti occupanti nella casella centrale all'inizio di alcuno dei nove episodi.

Sono comparsi anche altri anelli più grandi, per i quali non si inferisce alcun centro interno: i conteggi di **osservazioni per tick**, non di oggetti indipendenti, includono, ad esempio, cicli a 10, 12 e perfino **14** particelle. Per gli anelli con almeno dieci membri il numero di **insiemi materiali distinti** è 10 sui 100 universi. Questo costituisce diversità topologica naturale, non autoriproduzione.

### Due esempi concreti di cavità vuote

- **Densità maggiore, cavità centrata in (2,0):** anello di otto particelle con esattamente la sequenza canonica di specie `S0,S0,S1,S1,S0,S1,S1,S1`; osservato per **206 tick** fino al confine temporale del run (censurato), con la casella centrale vuota.
- **Densità maggiore, cavità centrata in (19,21):** struttura materiale di otto particelle, episodio durato **249 tick osservati** prima di una rottura reale di legame, ancora con centro vuoto.

Le coordinate sono nella griglia periodica del mondo associato; non consentono di localizzare la fonte senza seed/ID nel dataset, entrambi presenti nel file JSON.

## Valutazione preregistrata

L'ipotesi più forte richiedeva **almeno due mondi indipendenti** contenenti un anello con residente nativo di grado zero, probabilità di movimento >0 e confinamento **≥30 tick**. Il criterio **non è soddisfatto**: zero residenti naturali osservati, qualunque sia la durata della cavità.

Invece la condizione debole **`geometric_pocket_without_long_lived_trapping`** è soddisfatta: il sistema sa assemblare spontaneamente almeno alcuni bordi topologicamente chiusi, di otto atomi, che geometricamente **possono** ostacolare movimenti verso il loro interno, ma nelle condizioni testate risultano **vuoti**.

### Limiti scientifici essenziali

1. **Un anello geometrico non è una membrana biologica.** È un bordo di siti occupati e collegati, senza metabolismo, selettività molecolare attiva, crescita di compartimento o capacità di autocopia.
2. **Cavità vuota ≠ intrappolamento osservato.** Il modello di movimento impedirebbe a un monomero libero interno di attraversare gli otto siti bloccanti finché il bordo rimane fisicamente integro, e i test sintetici verificano la proprietà; ma non abbiamo osservato alcun caso naturale con residente.
3. **Non sappiamo perché il centro sia vuoto.** Può derivare da statistiche di densità locale, selezione geometrica nella costruzione dell'anello, piccola numerosità dei mondi che producono queste geometrie o semplice caso; non abbiamo eseguito un controllo causale a questo proposito.
4. **Nessun confronto fra permanenze come se fossero misure indipendenti:** i nove episodi possono ripetere la stessa cavità materiale e sono misurati entro una finestra temporale limitata, con censura.
5. **La dinamica è identica alla M6 originaria:** nessuna fisica nuova, nessuna particella inserita, nessuna modifica a `src/`, `master` o agli esperimenti precedenti.

## Invarianti e riproducibilità

La suite pytest verifica anelli sintetici 3×3 in geometria normale e attraverso i bordi periodici, un negativo con anello allungato di otto atomi che **non** racchiude la casella, permanenza di un residente sintetico non legato per 40 tick mentre il bordo permane, e il gate dei due mondi distinti. In CI tutto **PASS**.

I due mondi preregistrati `baseline/9801` e `enriched/9801` sono stati riavviati **senza osservatore**: hash completo finale, fingerprint/draws RNG, energia, dissipazione e contatori di legami esattamente identici alla traiettoria osservata.

## Prossima ricerca

L'interrogativo verificabile successivo è **se le cavità spontanee tendano a formarsi dove il centro è già vuoto**, rispetto a blocchi 3×3 di pari densità e tempi di controllo, senza decidere a posteriori i seed. Oppure si può studiare se i cicli con ≥10 particelle formano geometrie capaci di racchiudere più di un sito, usando un rilevatore di regioni interne topologicamente corretto sul toro. Ogni risultato positivo richiederebbe un nuovo protocollo congelato, nuove osservazioni e replica indipendente.
