# M6.6 — Replica a seed indipendenti dell'apertura controllata di anelli spontanei

**Data:** 15 novembre 2026 · **Tipo:** replica preregistrata del contrasto M6.5, nessuna nuova legge fisica.
**Protocollo congelato prima del runner:** [commit `0019d1e4`](https://github.com/kkongiu/alife-lab/commit/0019d1e4e024b3689a481bdbe8e37ddc938327fd).
**Esecuzione:** [GitHub Actions #43758589913 — PASS](https://github.com/kkongiu/alife-lab/actions/runs/43758589913), suite pytest e 40 mondi completati.
**Dati per tutti i casi, inclusi gli zeri:** [JSON di 76 fork](https://github.com/kkongiu/alife-lab/actions/runs/43758589913/artifacts/14178623526).

## Campionamento indipendente

20 nuovi seed 9001–9020 × 2 densità, mondi ALife con **zero legami iniziali**. In ciascun universo si selezionano i primi **due** anelli naturali con materiale distinto entro 600 tick: 36 fork baseline e 40 enriched, **76** in totale (4 casi non trovati entro la finestra preregistrata).

Ciascun fork genera tre evoluzioni di 120 tick dalla stessa identica configurazione: (1) anello lasciato intatto, (2) apertura di un legame e ridistribuzione della sua energia immagazzinata, (3) apertura del legame opposto. Le regole fisiche M6 restano identiche in tutte e tre le condizioni.

La prima misura è la **conservazione a 120 tick di una componente isolata con esattamente i quattro atomi originali**, anche se la loro forma non è più ciclica.

## Replica del criterio M6.5

| Densità | Anello intatto | Apertura legame minimo | Apertura legame opposto | Vantaggio intatto vs minimo |
|---|---:|---:|---:|---:|
| 200 particelle (36 fork) | **32/36 (88,9%)** | 26/36 (72,2%) | 26/36 (72,2%) | **+16,7 pp** |
| 264 particelle (40 fork) | **32/40 (80,0%)** | 21/40 (52,5%) | 25/40 (62,5%) | **+27,5 pp** |

**Risultato del gate preregistrato identico a M6.5: FAIL / `not_confirmed_under_original_gate`.**
Serviva differenza keep–open_lowest **≥20 punti percentuali in entrambe le densità** e stesso segno positivo per keep–open_opposite. Il vantaggio ha lo stesso segno in entrambi i regimi ma baseline è **+16,7 pp**, sotto soglia. Non abbassiamo la soglia e **non** combiniamo retroattivamente M6.5 e M6.6 per fabbricare una conferma.

I due anelli potenzialmente selezionati dallo stesso universo hanno un background e una storia condivisa: non sono 76 mondi causalmente indipendenti.

## Esito secondario preregistrato: richiusura spontanea dopo apertura

Un fenomeno misurabile è la **ricomparsa dell'anello originale di quattro particelle dopo che abbiamo rimosso un legame**.

| Apertura | 200 particelle | 264 particelle | Totale |
|---|---:|---:|---:|
| Legame minimo: anello riformato almeno una volta entro 120 tick | 31/36 | 26/40 | **57/76 (75,0%)** |
| Legame opposto: anello riformato almeno una volta entro 120 tick | 27/36 | 27/40 | **54/76 (71,1%)** |
| Legame minimo: riformazione entro 10 tick | 19/36 | 12/40 | **31/76 (40,8%)** |
| Legame opposto: riformazione entro 10 tick | 13/36 | 18/40 | **31/76 (40,8%)** |

Le medie del primo tick di riformazione **condizionate alla riformazione osservata** sono 13,23 / 18,04 tick per l'apertura del legame minimo (baseline/enriched) e 19,41 / 9,33 tick per l'apertura opposta.

**Interpretazione:** anelli artificialmente aperti in mondi nati spontaneamente **tendono spesso a richiudersi**, anche in meno di dieci tick. È una resilienza dinamica locale osservata ripetutamente con nuovi seed. Tuttavia non indica una risposta biologica: gli estremi dell'ex-anello quadrato restano vicini, un legame fra essi è chimicamente consentito e l'apertura libera slot di valenza e redistribuisce energia. Un test causale ulteriore dovrebbe separare questi fattori e includere un controllo di semplice riassociazione di due vicini, non etichettare il fenomeno `self-healing` genetico.

## Controlli ed evidenza

- Tutti i 40 mondi, 76 fork e tre condizioni per fork hanno prodotto risultati validi.
- Suite di regressione completa PASS.
- Il runner richiama **esattamente** `sample_density`, `paired_experiment` e `summary` originali di M6.5, modificando **solo la lista preregistrata dei seed**.
- Il test impone un confronto totale del protocollo M6.5 con quello della replica (eccetto i seed), impedendo cambiamenti nascosti alla regola, durata o gate.
- Ogni apertura modifica lo stato fisico ma conserva l'energia totale e il RNG iniziale; le traiettorie possono divergere dopo il fork.
- Nessuna modifica a `src/`, fisica, `master` o dati storici.

## Decisione

**Non confermato** il criterio quantitativo originario di protezione ad entrambe le densità. **Risultato secondario interessante:** frequente **richiusura spontanea** dello stesso anello dopo l'apertura, confermata su seed nuovi; osservabile ma ancora spiegabile con la geometria e le leggi di legame esistenti.

**Prossima priorità scientifica proposta:** esperimento con apertura e perturbazione geometrica/energetica controllata per distinguere riassociazione locale ordinaria da persistente conservazione strutturale. Nessuna modifica a M6 o promozione a M7 senza nuovo protocollo e autorizzazione.
