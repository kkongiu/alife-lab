# M6.3-9 — Rottura, riformazione e falsa persistenza

**Fonte comune:** [protocollo congelato prima dell'esecuzione](https://github.com/kkongiu/alife-lab/commit/417f27a0481f5a8fb5ee6463098716c3bbeafcc9), [run CI 43739195486 (PASS)](https://github.com/kkongiu/alife-lab/actions/runs/43739195486), [dati per tutti i 120 universi](https://github.com/kkongiu/alife-lab/actions/runs/43739195486/artifacts/14172125152).

**Unica campagna:** 12 seed nuovi (8201–8212), 2 densità × 5 sonde A/B/A_reverse/B_reverse/C, 450 passi. Le dieci analisi NON sono dieci campioni indipendenti. Nessuna legge M6 modificata.

Il recorder distingue l'evento di rottura dalla **riformazione di uno specifico legame originale dopo una rottura precedentemente registrata**. Una coppia può figurare di nuovo nello stesso componente senza avere mantenuto continuità ininterrotta.

| Densità | Eventi di rottura dei legami originali | Eventi di riformazione | Tick totali con tre legami presenti **dopo almeno una rottura** |
|---|---:|---:|---:|
| 200 particelle, 60 run | **153** | **82** | **7.464** |
| 264 particelle, 60 run | **146** | **95** | **7.466** |

I tick ripristinati sono una **somma di snapshot per mondo**, non una durata consecutiva né il tempo di una singola molecola. È scientificamente scorretto interpretare i circa 268–281 tick medi con tutti i legami presenti come un'intera vita ininterrotta. Il detector dovrà descrivere la continuità materiale e il ripristino separatamente.
