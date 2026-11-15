# M6.3-16 — Decisione dopo dieci step autonomi

**Fonte comune:** [protocollo congelato prima dell'esecuzione](https://github.com/kkongiu/alife-lab/commit/417f27a0481f5a8fb5ee6463098716c3bbeafcc9), [run CI 43739195486 (PASS)](https://github.com/kkongiu/alife-lab/actions/runs/43739195486), [dati per tutti i 120 universi](https://github.com/kkongiu/alife-lab/actions/runs/43739195486/artifacts/14172125152).

**Unica campagna:** 12 seed nuovi (8201–8212), 2 densità × 5 sonde A/B/A_reverse/B_reverse/C, 450 passi. Le dieci analisi NON sono dieci campioni indipendenti. Nessuna legge M6 modificata.

I dieci step M6.3-7→16 sono **dieci valutazioni di una sola nuova campagna preregistrata di 120 mondi**, non dieci esperimenti indipendenti. Il protocollo è stato congelato nel commit [417f27a](https://github.com/kkongiu/alife-lab/commit/417f27a0481f5a8fb5ee6463098716c3bbeafcc9); la CI e le repliche sono PASS.

## Esiti decisivi

1. **Crescita prima della distruzione:** la prima perdita di purezza per attacco materiale si verifica in **44/60** mondi baseline e **58/60** enriched. La purezza media è **45,1/26,0** tick, mentre i tre legami originali sono presenti in media per **268,4/280,8** tick.
2. **Legami ricostituiti:** eventi di rottura **153/146**, di riformazione **82/95**. La durata continua non può essere letta dalla semplice presenza a ogni fotografia. Il primo evento di rottura è osservato in 60/60 e 57/60 casi; tre sono censurati.
3. **Valenza come collo di bottiglia locale:** circa **50,7%/80,3%** dei tick di nucleo cresciuto ha zero slot energeticamente disponibili sulle quattro particelle originarie. Il gate dell'80% è raggiunto nella condizione più densa **per questa sonda**.
4. **Nessuna specificità ereditaria:** nuove strutture indipendenti vicine al nucleo cresciuto A/B = **10/9** baseline e **20/7** enriched, senza preferenza coerente per il motivo della sorgente; il gate preventivo non è superato.
5. **Difetto di identificabilità A/B:** le due catene differiscono nella disposizione delle specie **interne già sature**, ma hanno gli stessi **due estremi reattivi**. Il risultato nullo non testa in modo efficace una trasmissione della sequenza interna; questo controllo strutturale è stato rilevato *post hoc* e va dichiarato.

## Decisione e prossimo esperimento (non eseguito)

**GO di qualità strumentale; NO GO a M7, NO a modifiche immediate della fisica.** C'è crescita, conservazione materiale intermittente e saturazione della valenza del nucleo, **non** copia causale o trasmissione ereditaria dimostrata.

Un prossimo protocollo dovrebbe prima definire coppie di motivi con differenze **fisicamente visibili agli estremi** e controlli di composizione/energia/forma equivalenti, per stabilire se i soli effetti locali producono una preferenza *chimica*, non già una copia. Andrebbe misurata la presenza di nuovi motivi con nuova origine materiale, mantenendo separate dipendenza di superficie, divergenza RNG e trasmissione di una proprietà interna. Non basterà cambiare `max_bonds`: quella sarebbe una **nuova legge/configurazione** che richiede motivazione e autorizzazione specifica.

Le PR rimangono in bozza, il ramo `master` e le leggi M6 rimangono invariati. Nessun evento viene chiamato organismo digitale.
