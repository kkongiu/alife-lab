# M6.3-12 — Esposizione locale e coppie staticamente eleggibili

**Fonte comune:** [protocollo congelato prima dell'esecuzione](https://github.com/kkongiu/alife-lab/commit/417f27a0481f5a8fb5ee6463098716c3bbeafcc9), [run CI 43739195486 (PASS)](https://github.com/kkongiu/alife-lab/actions/runs/43739195486), [dati per tutti i 120 universi](https://github.com/kkongiu/alife-lab/actions/runs/43739195486/artifacts/14172125152).

**Unica campagna:** 12 seed nuovi (8201–8212), 2 densità × 5 sonde A/B/A_reverse/B_reverse/C, 450 passi. Le dieci analisi NON sono dieci campioni indipendenti. Nessuna legge M6 modificata.

L'osservatore misura le coppie nucleo–monomero libero adiacenti che rispettano specie ammesse, energia disponibile e valenza in un **snapshot successivo all'avanzamento**. Non è il numero reale di tentativi estratti dal RNG nella fase di formazione.

| Misura, somma sui 60 run | 200 particelle | 264 particelle |
|---|---:|---:|
| Tick di forma pura | ~2.704 | ~1.558 |
| Coppie eleggibili in forma pura | **757** | **715** |
| Coppie eleggibili per tick puro | ~**0,28** | ~**0,46** |
| Tick di nucleo cresciuto con tre legami originali presenti | ~13.397 | ~15.291 |
| Coppie eleggibili in quest'ultima fase | **391** | **351** |
| Coppie eleggibili per tick di nucleo cresciuto | ~**0,029** | ~**0,023** |

L'aumento di densità incrementa le potenziali occasioni **per tick puro**, ma comprime la fase pura e spesso satura gli slot disponibili. Non vi è evidenza di trasmissione di una sequenza in questi soli indicatori di esposizione.
