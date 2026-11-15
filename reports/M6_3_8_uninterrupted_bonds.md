# M6.3-8 — Prima rottura **effettiva** di un legame originale

**Fonte comune:** [protocollo congelato prima dell'esecuzione](https://github.com/kkongiu/alife-lab/commit/417f27a0481f5a8fb5ee6463098716c3bbeafcc9), [run CI 43739195486 (PASS)](https://github.com/kkongiu/alife-lab/actions/runs/43739195486), [dati per tutti i 120 universi](https://github.com/kkongiu/alife-lab/actions/runs/43739195486/artifacts/14172125152).

**Unica campagna:** 12 seed nuovi (8201–8212), 2 densità × 5 sonde A/B/A_reverse/B_reverse/C, 450 passi. Le dieci analisi NON sono dieci campioni indipendenti. Nessuna legge M6 modificata.

Si registra il primo evento `BondEvent(kind=break)` che tocca uno dei tre legami `0–1`, `1–2`, `2–3`, traducendo il passo pre-transizione nel tick di osservazione. Non si usa la prima fotografia in cui un legame è assente: potrebbe essersi rotto e riformato nello stesso tick.

| Densità | Run con prima rottura osservata | Run censurati a 450 tick | Tick medio prima rottura, solo osservati |
|---|---:|---:|---:|
| 200 particelle | **60/60** | 0 | **144,83** |
| 264 particelle | **57/60** | 3 | **141,84** |

Questi sono valori descrittivi, non hazard stimati con censura corretta. Il tick medio di rottura differisce relativamente poco, mentre la durata media della *forma pura* scende da **45,07** a **25,97** tick. La purezza è quindi una misura diversa dalla sopravvivenza del legame. Il confronto non autorizza un'inferenza causale sulla densità, che cambia anche lievemente composizione.
