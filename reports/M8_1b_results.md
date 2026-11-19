# M8.1b — Diffusione locale di monomeri isolati: esperimento completo

**19 novembre 2026 — campagna fisica completata, suite di test PASS, due gate scientifici NO_GO.**

## Provenienza verificabile

- [Protocollo preregistrato prima di qualunque nuova legge o dato, commit 8e5981e](https://github.com/kkongiu/alife-lab/commit/8e5981edc201784c83bb82dc626e069e7e272b52).
- [Chiarimento preregistrato del corridoio con genitore ancora integro, commit 9f06297](https://github.com/kkongiu/alife-lab/commit/9f062977f25e06b73e35b483a017aeeb07f1a487).
- [GitHub Actions #44491013828 — PASS regressioni storiche e 256 mondi reali](https://github.com/kkongiu/alife-lab/actions/runs/44491013828).
- [Dati grezzi di 256 traiettorie, incluse tutte le condizioni nulle, artifact #14512363685](https://github.com/kkongiu/alife-lab/actions/runs/44491013828/artifacts/14512363685).
- [Pull request in bozza #48](https://github.com/kkongiu/alife-lab/pull/48), non unita a master.

La fisica originale in `src/alife_m8/sandbox.py` rimane **immutata**.
M8.1b aggiunge una **singola legge esplicita** in `src/alife_m8/hopping_v1.py`: i monomeri privi di qualsiasi legame B o H possono tentare un passo verso una delle quattro celle adiacenti con probabilità 0,25 per tick. Un passo riesce soltanto se la destinazione è libera e interna al reticolo e consuma esattamente **1 unità di energia**. ID, specie e materia sono preservati. I monomeri con legami rimangono immobili; nessun desorbimento o nuova regola di copiatura.

## Campione e condizioni fissati prima dei risultati

- **64 nuovi seed** 620001–620064, indipendenti per condizione appaiata.
- **4 condizioni per seed × 240 tick = 256 mondi fisici.**
- Partenza con **20 monomeri non legati** di due specie, 10+10, senza B/H o template artificiali, sempre con stessi siti/ID/specie nei quattro bracci.
- `static_templated`: identica fisica M8.0.
- `hop_templated`: mobilità di monomeri isolati e templating di M8.0.
- `hop_shuffled`: medesima mobilità e chimica, ma identità del template rimescolata.
- `hop_no_template`: mobilità senza cattura di materiale tramite templating.

Il criterio di spazio libero viene contato **soltanto con il genitore originario di quattro monomeri ancora presente e con tutti e tre i legami B intatti**, anche se una fila vuota compare successivamente alla sua nascita. Per una figlia materiale persistente si mantiene la soglia originaria M8.1a: quattro nuovi ID materialmente separati da un primo genitore nato spontaneamente, quattro catture H native da quel genitore dopo la sua nascita, tre B native, distacco H, componente B esattamente di quattro ID e persistenza ≥20 tick; per figlia informativa anche sequenza identica.

## Risultati sui 64 mondi per braccio

| Misura | Statico con templating | Mobile con templating | Mobile identità rimescolata | Mobile senza templating |
|---|---:|---:|---:|---:|
| Mondi con prima catena B4 spontanea | **29** | **42** | **42** | **61** |
| Mondi con fila di quattro celle laterali libere **alla nascita** | 0 | 0 | 0 | 15 |
| Mondi con fila laterale libera almeno una volta con genitore vivo | **0** | **0** | **0** | **42** |
| Catture H provenienti dalla prima catena (eventi) | 20 | **29** | 29 | 0 |
| Mondi con figlia materiale persistente | 0 | 0 | 0 | 0 |
| Mondi con figlia informativa persistente | 0 | 0 | 0 | 0 |
| Passi locali realizzati (eventi) | 0 | **5.054** | 5.054 | **12.670** |
| Adsorbimenti complessivi da tutte le strutture | 1.616 | **1.905** | 1.905 | 0 |
| Formazioni B complessive | 2.568 | **3.093** | 3.093 | 869 |

**Il numero 5.054 riguarda gli eventi di spostamento complessivi nei 64 mondi**, non mondi indipendenti né un numero di progenie. Identici conteggi globali in templated/shuffled NON dimostrano copiatura informativa.

## Verdetti preregistrati

1. **Integrità fisica: PASS**. 256/256 mondi hanno completato i controlli di conservazione esatta per tutti i 240 tick. Test di regressione originali e nuovi PASS. Il braccio statico è stato confrontato anche contro il precedente runner M8.1a sul medesimo seed.
2. **Effetto geometrico della sola mobilità: NO_GO**. La soglia congelata richiedeva almeno 8/64 mondi mobili con un corridoio libero e almeno 5 più del controllo statico. Risultato: **0/64 mobili contro 0/64 statici**.
3. **Figlie informative persistenti: NO_GO**. La soglia congelata richiedeva almeno 3/64 nel braccio mobile attivo e 3 in più di quello rimescolato. Risultato: **0 contro 0**.

## Interpretazione con limite causale

La mobilità dei singoli monomeri non legati aumenta nel campione la quota di mondi in cui compare un primo polimero (29/64 statici → 42/64 mobili), ma **non genera nessuno spazio laterale sufficientemente libero** durante la vita di quel primo polimero nelle condizioni con templating. Non è quindi stata dimostrata alcuna copiatura spontanea, nonostante movimenti reali con costi fisici e maggiori catture complessive.

Il contrasto più utile è il controllo `hop_no_template`: **42/61** mondi che formano una prima catena presentano un corridoio completo libero mentre questa è viva. Dunque la legge di movimento può, nel modello, rendere disponibili siti; non basta però quando l'attività di templating e la chimica locale occupano e connettono altri monomeri sulla superficie. **Non possiamo ancora quantificare quanto ostacolo sia dovuto specificamente ai legami B, ai contatti H o al tempo/energia esauriti**: serve un audit diagnostico mirato prima di introdurre nuove leggi.

Questi dati suggeriscono una nuova ipotesi distinta (non testata in M8.1b): **turnover/reversibilità della popolazione superficiale**, con desorbimento/movimento di specie attualmente bloccate, conservazione esatta di materia ed energia, controllo indipendente delle opportunità, ma soltanto dopo preregistrazione di M8.1c.

**STOP della campagna M8.1b:** nessun allungamento retroattivo, modifica a P_HOP, nuovi seed selezionati o cambiamento delle condizioni per ribaltare un NO_GO. La PR resta in bozza e il ramo principale rimane intatto. Né i polimeri spontanei, né il passaggio energetico, né l'eventuale figlia di una singola generazione costituiscono da soli vita artificiale o ereditarietà darwiniana.
