# M6.12 — Una barriera naturale persistente per 282 tick: protocellula NO, confinamento geometrico SÌ

**Data:** 16 novembre 2026. **Esperimento preregistrato completo:** [protocollo congelato prima del runner, commit `a64f518`](https://github.com/kkongiu/alife-lab/commit/a64f51811aee4b89732e3179b9f18e128222365e) · [GitHub Actions originale, PASS #43842973287](https://github.com/kkongiu/alife-lab/actions/runs/43842973287) · [dati grezzi completi: 300 mondi, artifact #14214645568](https://github.com/kkongiu/alife-lab/actions/runs/43842973287/artifacts/14214645568).

**Verdetto preregistrato: `single_unreplicated_30tick_confinement` e `closure_comparison_underpowered=true`.** Nessuna prova di autoreplicazione, metabolismo, ereditarietà, protezione attiva o vita.

## Domanda e correzione concettuale

In M6.11 la particella ID98 era presente quando la struttura aveva già sette degli otto legami: nel reticolo, se tutti gli otto siti del bordo di una griglia 3×3 sono occupati da atomi collegati e immobili, i quattro movimenti cardinali dal centro sono già impediti. **La nascita dell'ottavo legame è un evento topologico distinto dall'inizio del confinamento fisico.** M6.12 misura entrambi: durata della barriera nativa a sette legami originali e probabilità di aggiungere l'ottavo legame, confrontando strutture con centro vuoto e con particella mobile.

## Disegno fisso e falsificabilità

- **300 configurazioni native**: 150 seed nuovi, dal 11001 al 11150, due densità (200 particelle baseline; 264 enriched); 600 tick per mondo, 180.000 tick-mondo.
- Universo M6: griglia periodica 24×24, zero legami iniziali, senza modifiche alla chimica, alle particelle, a `src/`, a `master` e agli esperimenti storici.
- Precursore valido: **esattamente otto particelle** nei siti del perimetro 3×3, collegate fra loro da **esattamente sette legami nativi** consecutivi, un solo legame mancante, due estremi di grado 1 e sei membri di grado 2; niente legami esterni nel componente. Un semplice guscio di otto siti occupati non basta.
- `empty`: centro vuoto; `free_mobile`: monomero nativo grado 0 con probabilità di movimento non nulla; `other_occupied`: altri occupanti.
- Episodio di barriera: **stesse sette connessioni originali**, stessi otto ID materiali, stessi siti. Si conclude alla prima rottura reale di uno dei sette legami originali, anche se viene ricostituito nello stesso tick; l'ottavo legame può comparire o rompersi senza interrompere la barriera di partenza.
- Rischio di chiusura: dal tick `t` con sette legami a `t+1` con l'ottavo, solo se gli originali non si rompono e la configurazione rimane in posizione. Si riportano esposizioni chimicamente ammissibili, separate per densità, specie della coppia terminale e occupazione del centro. I tick ripetuti **non sono campioni indipendenti**.
- Due mondi fissi sono riprodotti senza osservatore per verificare hash completo, RNG/draws, energia, dissipazione e contatori; tutti i 300 mondi e i casi nulli sono conservati nell'artefatto.

**Nota:** i due regimi usano gli stessi 150 numeri di seed con condizioni iniziali diverse; sono mondi distinti ma non necessariamente campioni statisticamente indipendenti tra densità.

## Esiti: tutti i 300 universi

| Misura | Baseline 150 | Enriched 150 | Totale |
|---|---:|---:|---:|
| Episodi validi di precursore 7/8 | 12 | 18 | **30** |
| Insiemi materiali distinti | 6 | 12 | **18** |
| Episodi con centro vuoto alla scoperta | 11 | 17 | **28** |
| Episodi con monomero nativo mobile al centro | 1 | 1 | **2** |
| Chiusure 7→8 con sette legami originali continui | 3 | 2 | **5** |
| Mondi con barriere che confinano un monomero mobile per ≥30 tick | 0 | **1** | **1** |
| Mondi con precursore mobile-centro *ammissibile chimicamente* | 0 | 1 | **1** |

L'unico mondo positivo da almeno trenta tick è dettagliato qui sotto. La condizione preregistrata per parlare di fenomeno ripetuto richiedeva **almeno due mondi**, non raggiunta.

### Evento positivo `enriched-11110`: barriera naturale durata 282 tick

Il nuovo dato documentato nel JSON originale è:

| Proprietà | Valore |
|---|---|
| Mondo, seed | `enriched / 11110` |
| Nascita del precursore | tick **225** |
| Posizione del centro | **(20, 6)** |
| Residente mobile libero | **ID 244** |
| Materiali del bordo | ID 20, 31, 55, 57, 90, 100, 117, 149 |
| Numero di legami originali del precursore | **7** |
| Prima formazione dell'ottavo legame | tick **231** |
| Barriera originale integra | **282 tick**, dal tick 225 al tick 506 inclusi |
| Termine dell'episodio | rottura originale rilevata al tick **507** |
| Esposizioni per completamento dell'ottavo legame | 6 tick ammissibili, 1 prima chiusura |
| Censura temporale | **No**: rottura osservata prima del termine del mondo |

**Attenzione:** **282 tick è la continuità delle sette connessioni originali e della barriera materiale**, non necessariamente una durata ininterrotta di tutti gli otto legami. L'ottavo si forma inizialmente al tick 231, ma può rompersi e riformarsi successivamente, senza invalidare la barriera originale.

La particella ID244 non ha una funzione di controllo della struttura: il movimento cardinalmente impedito è una conseguenza passiva del modello. Il risultato è interessante per una ricerca sulla **compartimentazione geometrica primitiva**, non è una cellula.

### Controllo positivo secondario: `baseline-11102`

Un secondo precursore naturale con residente mobile libero si trova nel mondo `baseline-11102`, centro (1,11), residente **ID184**. Il bordo a sette legami rimane integro per **9 tick**, senza chiudere l'ottava connessione. La coppia terminale è `S1–S2`, non chimicamente ammissibile nelle condizioni misurate: il mancato ottavo legame **non** deve essere attribuito alla presenza della particella centrale.

### Probabilità di chiusura: controllo insufficiente

Tra i precursori ammissibili, il registro dà:

| Configurazione | Tick-esposizione ammissibili | Prime chiusure 7→8 |
|---|---:|---:|
| Baseline, centro vuoto (coppie ammissibili) | **112** | **3** |
| Enriched, centro vuoto (coppie ammissibili) | **79** | **1** |
| Enriched, centro mobile libero (S0–S1) | **6** | **1** |
| Baseline, centro mobile libero | **0** | **0** |

L'unico positivo ammissibile con centro occupato appartiene **a un solo mondo, un solo oggetto e un solo episodio**, con esposizioni ripetute nel tempo. Non è legittimo inferire che il centro occupato favorisca la chiusura confrontando 1/6 con 1/79 o 3/112. Per una comparazione utilizzabile servono più mondi indipendenti per strato, un campionamento predefinito degli stati di ingresso e controlli sui materiali terminali e sul tempo.

## Riproducibilità e limiti

L'esecuzione GitHub Actions originale ha superato regressioni e 300/300 mondi; i due replay fissi senza osservatore coincidono in hash/RNG/energia/legami. Una **verifica post-hoc separata** del caso `enriched-11110` è stata aggiunta successivamente in un test e **superata** in [GitHub Actions #43843649892](https://github.com/kkongiu/alife-lab/actions/runs/43843649892): ripete il seed 11110 con observer e senza observer, richiede il medesimo episodio di 282 tick e verifica gli hash completi, RNG, energia e contatori finali. Anche l'intera campagna dei 300 mondi è stata ripetuta con esito PASS. Questo controllo **non** modifica la preregistrazione, né la regola di decisione.

Questo esperimento non mette alla prova membrane selettive, scambio energetico organizzato, produzione di nuove molecole, ereditarietà o riproduzione di compartimenti. La barriera può essere spiegata interamente dall'immobilità degli aggregati legati e da probabilità locali di rottura/riformazione dei legami. Mancano replicazioni indipendenti di lunga durata.

## Decisione e passo successivo proposto

**Accettare come osservazione fisica di lunga durata, ricontrollata post-hoc** la barriera passiva `enriched-11110`. **Non accettare** una differenza causale di chiusura per presenza di residente: è fortemente sottocampionata.

Priorità successiva **M6.13**: preregistrare campione esplicitamente dimensionato per aumentare il numero di precursori con centro occupato *senza introdurre nuove leggi o template*, registrare la durata indipendentemente dal completamento dell'ottavo legame e verificare se esiste almeno una seconda replica di lunga durata su nuovi seed. Solo dopo, separare l'effetto puramente geometrico dal contributo del ciclo di legami con esperimenti controfattuali.
