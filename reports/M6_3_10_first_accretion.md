# M6.3-10 — Primo accrescimento e tipo di substrato incorporato

**Fonte comune:** [protocollo congelato prima dell'esecuzione](https://github.com/kkongiu/alife-lab/commit/417f27a0481f5a8fb5ee6463098716c3bbeafcc9), [run CI 43739195486 (PASS)](https://github.com/kkongiu/alife-lab/actions/runs/43739195486), [dati per tutti i 120 universi](https://github.com/kkongiu/alife-lab/actions/runs/43739195486/artifacts/14172125152).

**Unica campagna:** 12 seed nuovi (8201–8212), 2 densità × 5 sonde A/B/A_reverse/B_reverse/C, 450 passi. Le dieci analisi NON sono dieci campioni indipendenti. Nessuna legge M6 modificata.

La prima perdita del quartetto isolato è classificata tramite il grafo fisico: attacco di estranei con i tre legami originari ancora presenti, oppure rottura dei legami senza tale attacco. Nel nuovo campione non sono emersi eventi iniziali `mixed` o casi censurati rispetto alla purezza.

| Prima causa netta della perdita | 200 particelle | 264 particelle |
|---|---:|---:|
| **Attacco con legami iniziali presenti** | **44/60** | **58/60** |
| Rottura di legame senza attacco | 16/60 | 2/60 |

Durante l'intera evoluzione sono stati registrati **114/137** nuovi legami diretti fra sorgente e particelle che risultavano libere nel tick precedente, rispettivamente a bassa/alta densità, e **140/168** verso particelle già legate nel tick precedente. Questi sono **eventi**, non particelle uniche o run; una particella poteva cambiare stato durante lo stesso avanzamento. Crescita della sonda non equivale alla generazione di un organismo figlio.
