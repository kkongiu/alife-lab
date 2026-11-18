# M8.1a — Audit post-hoc delle 192 traiettorie originali

**18 novembre 2026. Audit di sola lettura completato, verifica GitHub Actions PASS.**

Fonti immutabili:
- [Campagna primaria M8.1a, Actions #44412124197](https://github.com/kkongiu/alife-lab/actions/runs/44412124197)
- [Artefatto primario contenente tutte le 192 traiettorie, #14476369876](https://github.com/kkongiu/alife-lab/actions/runs/44412124197/artifacts/14476369876)
- [Audit di soli eventi, Actions #44417148495](https://github.com/kkongiu/alife-lab/actions/runs/44417148495)
- [Dati aggregati e analisi per seed dell'audit #14478304922](https://github.com/kkongiu/alife-lab/actions/runs/44417148495/artifacts/14478304922)
- [Protocollo M8.1a congelato prima di codice e dati](https://github.com/kkongiu/alife-lab/commit/05a574dedff2680fe367ac90b1d5cb1c0d81f497)

## Risultato principale: blocco geometrico strutturale, non semplice sfortuna

In tutti i 30 mondi del braccio `templated` nei quali si forma la prima
catena B nativa di quattro monomeri originariamente non legati, **zero**
hanno una fila adiacente con quattro siti tutti liberi nell'istante in cui
quella prima catena viene riconosciuta.

Il protocollo primario richiedeva precisamente quattro **nuovi monomeri
adsorbiti DOPO la nascita del genitore**, ciascuno nel sito lateralmente
allineato e proveniente dalla cattura H della prima catena. Poiché nella
fisica M8.0 **le particelle adsorbite non si muovono né sono rimosse**,
una fila adiacente già occupata in almeno uno dei quattro siti alla nascita
della prima catena **non può soddisfare quel criterio in futuro**.

Pertanto, nel campione congelato, **il criterio primario di figlia era
irrealizzabile per tutti i 30 mondi con prima catena nativa**, a prescindere
dalla capacità cinetica dei legami H/B di trasmettere informazione.

Questa è una conclusione *logico-geometrica* all'interno delle leggi
dichiarate di M8.0, **non** una prova generale contro la copiatura spontanea,
né una nuova dimostrazione di ereditarietà. Manteniamo il NO_GO
preregistrato; non lo reinterpretamo come successo.

## Dati diagnostici per braccio

| Misura | Templating | Identità rimescolata | Senza templating |
|---|---:|---:|---:|
| Mondi con prima catena B nativa | **30/64** | **30/64** | **29/64** |
| Tick mediano di comparsa della prima catena | **37** | 37 | 35 |
| Siti occupati mediani alla nascita (su 50) | **35** | 35 | **20** |
| Prime catene con un'intera fila laterale di 4 siti liberi | **0/30** | **0/30** | 5/29 |
| Prime catene con *tutte* le file laterali completamente occupate | **19/30** | 19/30 | 0/29 |
| Prime catene con almeno una cella laterale libera | **11/30** | 11/30 | 29/29 |
| Mondi con almeno una cattura H reale dalla prima catena dopo la nascita | **11/30** | 11/30 | 0/29 |
| Mondi con almeno quattro catture H dalla prima catena | **0/30** | **0/30** | 0/29 |
| Catture H reali dalla prima catena (totale) | **16** | **16** | 0 |
| Possibili celle-tick pre-passo in cui la prima catena poteva essere selezionata come sorgente H | **33** | **33** | 17.659 |
| Contatti H della prima catena effettivamente rilasciati | **16** | **16** | 0 |
| Durata mediana, in tick, dei 16 contatti H rilasciati | **19** | 19 | — |

**Unità e denominatori:** 64 seed numerici per braccio; 30/29 mondi
con prima catena ove si analizza geometria/tempo della prima catena.
Le 33 *celle-tick* sono opportunità di esposizione rilevate allo
stato pre-passo, non osservazioni statistiche indipendenti e non la
misura dell'effettivo numero di sorteggi dopo la fase di rottura H/B.
Le 17.659 celle-tick del braccio `no_template` sono un indicatore
geometrico controfattuale: in tale braccio il canale H di copiatura
è disabilitato, quindi NON sono probabilità di cattura reale.
Il conteggio di 16 catture riguarda soltanto la prima catena selezionata;
le 1.647 catture globali del braccio informativo includono tutte le catene.

**Interpretazione dell'affollamento.** Il braccio con templating riempie
rapidamente il reticolo fisso tramite adsorbimenti di altre catene
anche *prima* che il primo polimero qualificante B4 nasca, portando la
mediana di occupazione a 35/50. Nel braccio senza templating, con
`P_BACKGROUND=0`, rimangono 20/50 siti occupati, e cinque prime
catene hanno effettivamente quattro posizioni laterali tutte libere,
ma la cattura H è intenzionalmente disabilitata.

La causa materiale immediata del fallimento del criterio rigidamente
preregistrato è **l'assenza di quattro siti laterali utilizzabili dopo
la nascita della prima catena**. Né l'audit né gli eventi possono
stabilire se una diversa fisica di mobilità, scambio o desorbimento
genererebbe copiatura persistente. Nemmeno eliminare retroattivamente
il requisito `captured AFTER source birth` sarebbe una verifica valida
della campagna primaria.

## Verifiche tecniche indipendenti dal motore

`tools/m8_1a_trace_audit.py` ricostruisce ogni stato dalla
popolazione iniziale e dai soli `adsorb`, `B_form`, `B_break`
e `H_release` dell'artefatto primario, senza chiamare
`WorldM8`, `step`, RNG o importare la fisica M8.

- **192/192** traiettorie originali ricostruite senza errori.
- **192/192** prime catene riidentificate esattamente come nel
  rilevatore primario (seed, tick, riga, colonna, ID e sequenza).
- Numero di catture, legami B/H e conti finali materia/energia
  corrispondenti agli originali, con bilancio contabile ricontrollato
  dopo ciascun evento.
- **Zero** nuovi seed, nessuna legge fisica o soglia scientifica
  cambiata, nessuna nuova simulazione.

## Conclusione e prossimo esperimento proposto

1. **M8.1a resta NO_GO per la copia informativa**, mentre la
   nucleazione spontanea di polimeri non legati resta confermata.
2. Il criterio adottato è risultato **strutturalmente irrealizzabile**
   negli specifici mondi che avevano superato la prima selezione,
   per effetto dell'occupazione irreversibile delle celle.
3. Per **M8.1b** raccomandiamo un nuovo protocollo *prima dei dati*
   che isoli una singola nuova ipotesi fisica: un movimento locale
   non teleologico di monomeri liberi e/o uno scambio/desorbimento
   con contabilità di energia e materia; controlli di esatta
   opportunità locale, mantenendo come criterio distinto
   la copiatura da un genitore apparso spontaneamente.
4. Conservare M8.0 e tutti gli esiti M8.1a inalterati. Separare
   preflight tecnico, origine spontanea, copiatura causale e
   trasmissione informativa multigenerazionale.

**Questo documento descrive un audit POST-HOC e NON è un nuovo
protocollo preregistrato, né una dimostrazione di vita artificiale.**
