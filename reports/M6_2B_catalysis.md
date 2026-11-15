# M6.2-B — Effetto della catalisi locale (campagna preregistrata)

**Data:** 2026-11-15 · **Universi:** 15 (5 seed × 3 condizioni × 3.000 passi) · **Motore:** schema 3, invariato · **Protocollo:** `campaigns/m6_2b/protocol.json` (preregistrato nel commit `a00028c`).

## Metodo

Usati i cinque universi `fed-mid` di M6 con seed 6101–6105. L'unica variazione consiste nell'aggiunta di una regola catalitica già supportata dal motore: fattore moltiplicativo 5 sulla formazione del legame S0-S1. Bracci: **off** (nessuna catalisi); **external_S3** (catalizzatore S3, non legante); **incorporated_S0** (catalizzatore S0, che può appartenere al legame prodotto). Ogni braccio parte da uno stato iniziale nuovo e deterministico. I criteri sono stati fissati *prima* delle simulazioni.

Misura primaria: **numero cumulativo di eventi di formazione di legami S0-S1** in 3.000 passi, non numero finale di legami. Criterio preregistrato per ciascun trattamento: delta mediano positivo e almeno 4 seed su 5 con incremento rispetto a off.

## Risultati principali

| Condizione | Mediana formazioni S0-S1 | Delta mediano appaiato | Seed con incremento | Esito cinetico |
|---|---:|---:|---:|---|
| off | 799 | 0 | — | riferimento |
| external_S3 | 889 | +76 | 5/5 | **positivo** |
| incorporated_S0 | 1.015 | +240 | 5/5 | **positivo** |

Incrementi indicativi sul valore mediano di controllo: **+9,5%** (S3), **+30,0%** (S0); il confronto principale resta il *delta appaiato* preregistrato.

| Seed | Off | S3 esterno | S0 nel prodotto | Δ S3 | Δ S0 |
|---|---:|---:|---:|---:|---:|
| 6101 | 760 | 889 | 1.015 | +129 | +255 |
| 6102 | 794 | 923 | 1.010 | +129 | +216 |
| 6103 | 810 | 862 | 971 | +52 | +161 |
| 6104 | 799 | 838 | 1.051 | +39 | +252 |
| 6105 | 814 | 890 | 1.054 | +76 | +240 |

Eventi esplicitamente catalizzati: **928** per S3, **3.390** per S0 (totali su 5 seed). Il rilevatore v2.1 ha rilevato **un evento di corrispondenza di firma in S3, ma zero copie persistenti in tutti i 15 run**. Nessuna discendenza; nessuna prova di replicazione.

## Integrità sperimentale

- 15/15 universi completati su cinque runner GitHub Actions indipendenti.
- Il braccio *off* riproduce esattamente **5/5 hash del mondo M6**, verificati dal processo prima dell'aggregazione.
- Invarianti e contabilità energetica verificati al termine di ogni run, senza modifiche alle leggi del motore.
- I run individuali, i risultati JSON aggregati e il report originale sono archiviati come artefatti nel [run GitHub Actions](https://github.com/kkongiu/alife-lab/actions/runs/43721178967); [risultati aggregati](https://github.com/kkongiu/alife-lab/actions/runs/43721178967/artifacts/14164148129).
- Codice sorgente e protocollo permettono di ripetere l'intera campagna.

## Interpretazione e limiti

**M6.2-B: GO limitato alla verifica dell'effetto cinetico della catalisi.** La catalisi locale cambia le frequenze di formazione dei legami in entrambi i trattamenti, secondo il criterio fissato. **Non** è dimostrata autocatalisi di strutture né amplificazione dei catalizzatori: la specie S0 è conservata, e S3 rimane esterna al prodotto. Non è stato eseguito un controllo spaziale shuffled: esigerlo richiederebbe una nuova fase preregistrata. Lo stesso seed allinea le condizioni iniziali, ma le traiettorie successive non restano identiche una volta cambiate le probabilità di reazione. Il successo cinetico non dimostra replicazione, ereditarietà o evoluzione darwiniana.

**Prossima decisione:** discutere il movimento degli aggregati (M6.2-A) e un controllo di templating causale, *prima* di modificare le leggi fisiche o avviare M7.
