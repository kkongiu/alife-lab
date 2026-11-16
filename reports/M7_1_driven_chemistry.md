# M7.1 — Energia alimentata e catalisi: più attività, non ancora metabolismo

**Data:** 16 novembre 2026. **Stato:** protocollo preregistrato, quattro shard su quattro completati, suite completa PASS, 320/320 mondi, 16 replay fisici PASS.

- [Protocollo fissato prima del codice: commit `de1d7a8`](https://github.com/kkongiu/alife-lab/commit/de1d7a86fa01ba8e979ab2e394a29418c6da0bd2)
- [GitHub Actions riuscito #43870353832](https://github.com/kkongiu/alife-lab/actions/runs/43870353832)
- [Dataset JSON completo: 320 mondi e tutti i checkpoint/controlli, artifact #14227946072](https://github.com/kkongiu/alife-lab/actions/runs/43870353832/artifacts/14227946072)
- [PR di ricerca in bozza #29](https://github.com/kkongiu/alife-lab/pull/29)
- **Nessuna modifica alle leggi sorgente `src/alife` o al ramo `master`.** M7.1 non è una nuova implementazione di metabolismo: usa un **nuovo regime di configurazione** di flussi energetici, costo del movimento e catalisi già supportati e testati dal motore M3/M6.

## Obiettivo e definizioni falsificabili

**Domanda:** un sistema chimico aperto con movimento a costo energetico esplicito, sorgenti localizzate di energia e catalisi locale generica mantiene attività dinamica e formazione di legami più a lungo dello stesso sistema chiuso?

**Non è un test di vita, ereditarietà o autocopia**: non esistono genoma, morte/nascita di particelle né replicatore inserito. Le firme simili e gli anelli finali non dimostrano una genealogia causale.

### Design preregistrato

- **80 seed indipendenti nuovi** `18001–18080`. Ciascuno compare in **quattro bracci** (320 mondi appaiati): chiuso senza catalisi; alimentato senza catalisi; chiuso con catalisi; alimentato con catalisi. **600 tick** ciascuno; **192.000 tick-mondo**.
- **Tutti i bracci:** 264 particelle originali (S0=108, S1=108, S2=28, S3=20), reticolo periodico 24×24, stessi identici ID/posizioni/specie/energie iniziali e RNG dopo la generazione, **zero legami iniziali**. Movimento ora con costo `movement_cost=1`, non zero come in M6. Scissione e formazione dei legami restano governate dalla chimica originale.
- **Alimentazione:** 16 sorgenti fisse (coordinate cartesiane x,y in {2,8,14,20}), ciascuna produce 2 unità di energia per tick e ha un serbatoio di capacità 12; il surplus viene scartato, senza inventare materia o nuove molecole. **19.200 unità generate** in 600 tick per ciascun mondo alimentato.
- **Catalisi generica:** un S2 vicino a una coppia ammissibile S0–S1 moltiplica il tentativo locale di formazione del legame per **fattore 4**. Non riconosce sequenze, non copia informazione, non prescrive una struttura target.
- Campionamento a tick 0, 100, 200, 400, 500 e 600; primaria attività negli **ultimi 100 tick (501–600)** per ridurre il confondimento dell'energia iniziale.
- **Bilancio energetico testato:** `stored energy (particles + bonds + source buffers) + dissipated + unabsorbed = initial energy + injected`. Verificato ai checkpoint su tutti i 320 mondi.
- Quattro shard prefissati da 20 seed con protocollo identico, controlli di completezza e **16 replay senza osservatore** (un seed × quattro bracci in ciascuno shard), con hash completo finale, RNG, energia, dispersione e contatori identici.

### Soglie fissate prima di osservare risultati

1. Movimento alimentato: in assenza di catalisi, alimentazione deve produrre più movimenti nell'ultimo intervallo di 100 tick per **almeno 60 degli 80 seed appaiati**, e almeno 60 dei mondi alimentati devono compiere un movimento in quell'intervallo.
2. Chimica alimentata: senza catalisi, il numero di **nuovi legami nell'ultimo intervallo** deve essere maggiore nel sistema alimentato per **almeno 48 seed su 80**.
3. Catalisi: effetto descrittivo su attività iniziale e finale, non classificato come emergenza biologica.

## Esiti: entrambi gli endpoint preregistrati superati

| Braccio | Movimenti medi t501–600 | Nuovi legami medi t501–600 | Mondi con almeno un movimento t501–600 | Mondi con anello semplice nativo al tick 600 |
|---|---:|---:|---:|---:|
| Chiuso, no catalisi | 67,55 | 5,39 | 80/80 | 28/80 |
| Alimentato, no catalisi | **147,09** | **9,70** | 80/80 | 33/80 |
| Chiuso, catalisi | 67,80 | 6,79 | 80/80 | 28/80 |
| Alimentato, catalisi | 134,64 | **10,59** | 80/80 | **47/80** |

**Confronto appaiato alimentazione senza catalisi:**
- In **78/80** seed, più movimenti t501–600 con alimentazione (**soglia 60 superata**); nei restanti due meno movimenti.
- In **70/80** seed, più nuovi legami t501–600 con alimentazione (**soglia 48 superata**); sette peggio, tre pari.
- Differenza media appaiata: **+79,54 movimenti** e **+4,31 legami** per mondo negli ultimi 100 tick; le medie degli eventi approssimativamente raddoppiano rispetto al chiuso.
- La popolazione mobile non resta attiva in senso ampio: a t600, soltanto **7,3 particelle** di media sono contemporaneamente libere, mobili e con sufficiente energia per il movimento nell'alimentato senza catalisi (vs **3,5** nel chiuso).

### Il costo della catalisi: più legami, meno mobilità

La catalisi aggiunge, sui 100 tick iniziali, in media **13,95 legami** nel sistema chiuso e **10,19 legami** in quello alimentato rispetto al rispettivo controllo senza catalisi; i vantaggi compaiono rispettivamente in **77/80** e **70/80** seed. Quindi l'aggiunta di catalisi accelera realmente la formazione di legami nella fase iniziale del simulatore.

La mobilità iniziale però diminuisce di **124,21** movimenti medi nel sistema chiuso catalitico e **127,75** in quello alimentato catalitico, rispetto ai rispettivi controlli. Ciò è coerente con la legge del motore **che rende immobili le particelle legate**. Il compromesso fra aggregazione e moto appare come proprietà combinata del regime scelto, ma non costituisce metabolismo, catalisi auto-sostenuta o trasferimento di informazione.

Nel sistema alimentato catalitico, la media di nuovi legami negli ultimi 100 tick è **10,59** contro 9,70 nel relativo controllo; questa differenza non è universalmente positiva seed per seed (39 seed aumentano, 34 diminuiscono, 7 pari). Quindi **non** descriverla come una forte superiorità finale.

## Problema emergente importante: energia generata ≠ energia distribuita

Le sorgenti producono a ogni tick **32 unità**; in 600 tick, **19.200** per mondo alimentato. Parte dell'energia però **satura i piccoli serbatoi locali** e viene registrata in `unabsorbed`, non consegnata utilmente alle particelle.

| Grandezza media a t600 | Chiuso senza catalisi | Alimentato senza catalisi | Alimentato con catalisi |
|---|---:|---:|---:|
| Energia esterna generata | 0 | 19.200 | 19.200 |
| Energia scartata per overflow | 0 | **11.733,5** | **11.195,4** |
| Quota generata non assorbita | — | **61,1%** | **58,3%** |
| Energia ancora immagazzinata nel sistema | 694,2 | 7.545,9 | 8.213,5 |
| Particelle a energia zero | 160,3 / 264 | **138,5 / 264** | **131,5 / 264** |
| Particelle libere e abilitate energeticamente al movimento | 3,5 | 7,3 | 5,8 |

La dissipazione media del mondo alimentato senza catalisi è **2.876,6** contro 2.261,8 nel chiuso. Il bilancio torna, tenendo conto della grande energia scartata. **L'alimentazione aumenta l'attività** ma non crea automaticamente una rete di scambio efficiente: a fine esperimento, oltre **la metà delle particelle** alimentate rimane a energia zero. Questo è il risultato progettualmente più informativo di M7.1.

È anche prematuro parlare di **stato stazionario**. L'energia contabilizzata dei sistemi alimentati a t600 è molto maggiore che a t100, quindi i flussi possono accumularsi in alcune particelle o legami; non c'è dimostrazione di equilibrio dinamico stabile. M7.1 non distingue energia localizzata nelle particelle temporaneamente immobili da quella funzionalmente disponibile a una rete di reazioni. Va misurato separatamente.

### Nessuna prova di autoreplicazione

Al tick 600, contare un anello semplice non equivale a una copia o a un discendente. I 320 mondi non sono stati selezionati in funzione della comparsa di strutture longeve e l'osservatore finale conta anelli senza genealogia. Tra i quattro bracci esistono **0 anelli nativi di otto membri** osservati nel solo snapshot finale (non significa che non se ne siano formati in tick precedenti). È stato visto un solo precursore geometrico 3×3 a sette legami al tick 600, senza monomero mobile al centro; ciò non è un endpoint di vita.

## Interpretazione e prossimo esperimento

M7.1 dimostra che lo stesso motore può rappresentare un regime **con alimentazione esterna, costo energetico del movimento e chimica reversibile alimentata** che aumenta chiaramente mobilità e turnover chimico rispetto a un controllo chiuso. Mostra inoltre **un forte collo di bottiglia di assorbimento** e un compromesso con la formazione di legami.

La prossima domanda non dovrebbe essere genericamente “più energia = più vita”. In un futuro **M7.2** pre-registrato conviene confrontare **a identico budget energetico totale** sorgenti puntiformi, sorgenti distribuite e/o trasporto locale dell'energia tra vicini, usando controlli senza catalisi, tassi di overflow, accessibilità dell'energia alle particelle libere, turnover e registri di bilancio. Se si introduce una regola di trasporto, questa sarebbe una **nuova fisica separata**, non una modifica retroattiva del risultato M7.1.

La domanda sull'ereditarietà rimane distinta: occorre dimostrare che una configurazione materiale **aumenti causalmente** la produzione di configurazioni somiglianti, con controlli per coincidenze e causalità comune, senza creare replicatori già impiantati.
