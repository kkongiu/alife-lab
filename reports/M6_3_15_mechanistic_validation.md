# M6.3-15 — Integrità e identifiabilità del confronto A/B

**Fonte comune:** [protocollo congelato prima dell'esecuzione](https://github.com/kkongiu/alife-lab/commit/417f27a0481f5a8fb5ee6463098716c3bbeafcc9), [run CI 43739195486 (PASS)](https://github.com/kkongiu/alife-lab/actions/runs/43739195486), [dati per tutti i 120 universi](https://github.com/kkongiu/alife-lab/actions/runs/43739195486/artifacts/14172125152).

**Unica campagna:** 12 seed nuovi (8201–8212), 2 densità × 5 sonde A/B/A_reverse/B_reverse/C, 450 passi. Le dieci analisi NON sono dieci campioni indipendenti. Nessuna legge M6 modificata.

L'intera suite `pytest`, il replay dei 120 mondi e il controllo fisico finale sono riusciti. I mondi `baseline/8201/A` e `enriched/8201/A` sono stati ricostruiti **indipendentemente** e osservati con lo strumento M6.3-1: stessi hash finali, RNG, energia e contatori di reazioni; nessuna mutazione delle traiettorie da parte del nuovo observer.

**Audit delle leggi e test aggiunto dopo i risultati (esplorativo, non parte del gate congelato):** A `S0–S1–S0–S1` e B `S0–S0–S1–S1` presentano **lo stesso terminale S0 a sinistra e S1 a destra**. Le due particelle interne sono già al loro massimo di due legami, dunque non possono formare ulteriori legami finché non si libera una valenza. Anche A_reverse e B_reverse condividono i rispettivi estremi. Il test confronta direttamente l'elenco iniziale delle coppie candidate del motore.

**Conseguenza metodologica:** il confronto A/B, quando il nucleo è intatto, mette in gioco *sequenze interne diverse ma terminazioni reattive identiche*. È dunque poco sensibile a un'ipotetica copia della sequenza interna nel modello attuale, che non legge una firma globale per decidere una reazione. Questo limita fortemente l'interpretabilità di un risultato nullo A/B. Non prova che ogni forma di templating sia impossibile.
