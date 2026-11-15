# M6.3-7 — Protocolli e condizioni iniziali

**Fonte comune:** [protocollo congelato prima dell'esecuzione](https://github.com/kkongiu/alife-lab/commit/417f27a0481f5a8fb5ee6463098716c3bbeafcc9), [run CI 43739195486 (PASS)](https://github.com/kkongiu/alife-lab/actions/runs/43739195486), [dati per tutti i 120 universi](https://github.com/kkongiu/alife-lab/actions/runs/43739195486/artifacts/14172125152).

**Unica campagna:** 12 seed nuovi (8201–8212), 2 densità × 5 sonde A/B/A_reverse/B_reverse/C, 450 passi. Le dieci analisi NON sono dieci campioni indipendenti. Nessuna legge M6 modificata.

Il protocollo definisce **120 universi sintetici con condizioni iniziali controllate**; ogni sonda contiene quattro particelle S0/S1 e tre legami, con identico conto energetico. I background e lo stato RNG dopo il posizionamento sono identici fra i cinque bracci di uno stesso seed/densità. Le due densità (200 e 264 particelle su 24×24) non hanno proporzioni delle specie perfettamente identiche, confondimento dichiarato.

Le sonde sono state *assemblate deliberatamente* a tick 0; non sono emerse né si sono riprodotte spontaneamente. I run sono nuovi rispetto ai seed della campagna M6.3-1, ma seguono una domanda decisa dopo aver visto i risultati precedenti. **GO strumentale**: verifiche iniziali, vincoli invariati, congelamento preventivo, salvataggio degli zeri. Non è un GO biologico.
