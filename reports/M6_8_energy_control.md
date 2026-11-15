# M6.8 — La restituzione energetica non spiega la richiusura rapida degli anelli, nelle condizioni studiate

**Campagna:** 15 novembre 2026 · **Outcome preregistrato:** `no_large_allocation_effect_detected_descriptive`.

**Protocollo congelato PRIMA del runner e degli esiti:** [commit `aa8be77f`](https://github.com/kkongiu/alife-lab/commit/aa8be77fe4c833e21caabffcf59ca67f9790d326), `campaigns/m6_8_energy_control/protocol.json`.

**Evidenze riproducibili:** [CI completa + 40 mondi, run 43761017767 PASS](https://github.com/kkongiu/alife-lab/actions/runs/43761017767); [dati JSON completi di 79 fork × 3 rami](https://github.com/kkongiu/alife-lab/actions/runs/43761017767/artifacts/14179439151). Il branch aggiunge soltanto nuovi protocollo, codice sperimentale, test, workflow e report; nessuna modifica alle leggi fisiche o al ramo `master`.

## Domanda causale

Le precedenti campagne M6.6–M6.7 hanno mostrato una frequente riformazione del legame che chiude un anello dopo la sua apertura. Questa riformazione è compatibile con il tasso ordinario di formazione del legame (5% per candidato), ma l'apertura standard **restituisce agli estremi l'energia immagazzinata nel legame originale**. In quale misura il ritorno dell'energia, anziché il semplice stato chimicamente ammissibile dei due atomi adiacenti, contribuisce al fenomeno?

## Esperimento

**40** universi totalmente naturali su nuovi seed **9401–9420** × densità normale/arricchita, griglia toroidale 24×24, zero legami iniziali. Primi due insiemi materiali distinti che formano un anello di quattro particelle entro 600 tick: **39** casi densità normale e **40** arricchita, **79** fork totali, senza sostituzione dei mancanti.

Ciascuno stato iniziale è duplicato esattamente con stesso materiale, geometria, legami, energia totale e RNG, in tre bracci:

1. **`keep_intact`**: l'anello naturale non viene manipolato.
2. **`open_refund_endpoints`**: si rimuove il legame scelto fra gli ID minimi e si restituisce tutta l'energia immagazzinata nei due estremi (intervento M6.5).
3. **`open_sequester_in_S3`**: si rimuove **lo stesso identico legame**, ma l'energia viene accreditata a una particella **S3 chimicamente inerte (valenza massima 0)** massimamente lontana dai quattro atomi secondo la distanza Manhattan toroidale; gli atomi dell'ex-anello mantengono **la stessa energia che avevano prima dell'apertura**.

**I due rami aperti partono da identici posizioni, grado, legami, identità, specie, energia globale e RNG. Differisce solo la distribuzione dell'energia.** Questa è una manipolazione artificiale delle condizioni iniziali, non una modifica delle regole di M6 né una simulazione di un processo energetico naturale.

Nei 120 tick successivi vengono osservate la formazione nativa `BondEvent(kind=form)` della coppia originale entro 10 tick e la persistenza, a 120 tick, del componente isolato costituito esattamente dai quattro ID originali.

## Risultati preregistrati

| Densità | Braccio | Formazione del legame originale entro 10 tick | Quartetto materiale isolato al tick 120 | Tempo medio isolato / 120 tick |
|---|---|---:|---:|---:|
| Normale, n=39 | **Anello intatto** | n/a | **28/39 = 71,79%** | 102,36 |
| Normale, n=39 | **Aperto: energia agli estremi** | **14/39 = 35,90%** | **28/39 = 71,79%** | 91,03 |
| Normale, n=39 | **Aperto: energia su S3** | **13/39 = 33,33%** | **26/39 = 66,67%** | 87,97 |
| Arricchita, n=40 | **Anello intatto** | n/a | **30/40 = 75,00%** | 106,30 |
| Arricchita, n=40 | **Aperto: energia agli estremi** | **17/40 = 42,50%** | **24/40 = 60,00%** | 93,30 |
| Arricchita, n=40 | **Aperto: energia su S3** | **17/40 = 42,50%** | **26/40 = 65,00%** | 95,30 |

**Contrasto REFUND − S3 sulle due misure principali:**

- Densità normale: riformazione entro 10 tick **+2,57 punti percentuali**; isolamento a 120 tick **+5,12 pp**.
- Densità arricchita: riformazione entro 10 tick **0,00 pp**; isolamento a 120 tick **−5,00 pp**.

Il gate fissato prima dei risultati richiede, per segnalare un effetto energetico coerente, differenze ≥15 pp e dello **stesso segno in entrambe** le densità su almeno una misura. Se invece **tutti e quattro** i contrasti delle due misure sono ≤10 pp assoluti, l'esito descrittivo è **`no_large_allocation_effect_detected_descriptive`**. Questo secondo criterio è rispettato: **non emerge un grande effetto della destinazione dell'energia sulle due misure in queste condizioni**.

**Un dato meccanicistico particolarmente rilevante:** **38/39 (97,4%)** e **39/40 (97,5%)** degli anelli selezionati avevano **già entrambi** gli atomi interessati dall'apertura con energia individuale sufficiente a pagare il costo di formazione **anche senza restituzione**. Dunque il rilascio di energia non risolveva normalmente una limitazione energetica preesistente; è plausibile che la differenza fra gli interventi sia modesta proprio per questo motivo.

## Invarianti e qualità

- Suite pytest completa PASS; workflow GitHub Actions eseguito correttamente.
- Per ogni fork, verifica che le energie globali siano identiche nei tre rami e che RNG stato/impronta e draw count coincidano allo start.
- Fra i due rami aperti, verifica uguaglianza di IDs, specie, posizioni, grado e dizionario dei legami. La S3 neutralizza l'energia senza poter formare legami (valenza massima 0).
- Osservatori degli eventi chimici originari non toccano la fisica o il generatore casuale.
- Per il primo fork di ciascuna densità, replay di tutte le tre traiettorie senza osservatore: hash finali, impronta RNG, draw count, energia e dissipazione devono coincidere.
- Ogni fork (anche con nessuna riformazione o con perdita della struttura) è presente nel JSON, con le sequenze degli eventi riferiti ai quattro ID originali.
- I due anelli di uno stesso universo non sono unità pienamente indipendenti, la dimensione campionaria è limitata, nessun p-value o intervallo di confidenza causa-efficacia è rivendicato.

## Conclusione e prossima direzione

**M6.7 + M6.8**: la richiusura osservata è in linea con la normale cinetica di formazione del legame, e la quantità di energia distribuita agli estremi all'apertura **non sembra essere il fattore determinante quando gli atomi sono già energeticamente sufficienti**. L'ipotesi spettacolare di una speciale capacità di autoriparazione non è giustificata dai dati.

Il prossimo approfondimento interessante dovrebbe invece individuare **casi limite con atomi energeticamente insufficienti** o scegliere un nuovo fenomeno realmente emergente con una domanda falsificabile — per esempio frequenze e rischi di anelli che si aprono e vengono catturati da materia esterna, senza introdurre nuove leggi. Non modificare la soglia o riciclare i medesimi seed per trovare un effetto energetico positivo a posteriori.
