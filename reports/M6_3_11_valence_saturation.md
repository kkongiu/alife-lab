# M6.3-11 — Valenza e disponibilità reattiva del nucleo

**Fonte comune:** [protocollo congelato prima dell'esecuzione](https://github.com/kkongiu/alife-lab/commit/417f27a0481f5a8fb5ee6463098716c3bbeafcc9), [run CI 43739195486 (PASS)](https://github.com/kkongiu/alife-lab/actions/runs/43739195486), [dati per tutti i 120 universi](https://github.com/kkongiu/alife-lab/actions/runs/43739195486/artifacts/14172125152).

**Unica campagna:** 12 seed nuovi (8201–8212), 2 densità × 5 sonde A/B/A_reverse/B_reverse/C, 450 passi. Le dieci analisi NON sono dieci campioni indipendenti. Nessuna legge M6 modificata.

Per ogni tick **con nucleo cresciuto ma tutti e tre i legami originari presenti**, contiamo gli slot di valenza liberi delle quattro particelle del nucleo e gli slot energeticamente qualificati. Una sonda può avere tanti monomeri attorno ma non riuscire a incorporarne altri se le sue valenze sono sature.

| Densità | Tick post-crescita senza slot fonte energeticamente utilizzabili, quota ponderata per durata |
|---|---:|
| 200 particelle | **circa 50,7%** |
| 264 particelle | **circa 80,3%** |

Il secondo valore supera di poco il gate descrittivo dell'**80%** preregistrato: nel regime enriched c'è un **collo di bottiglia di valenza/accessibilità sul nucleo originale**. Non significa che l'intero aggregato sia saturo: le particelle esterne possono ancora avere slot liberi. L'osservazione è post-step e la soglia non prova una legge generale sull'ereditarietà. Non modifichiamo `max_bonds`.
