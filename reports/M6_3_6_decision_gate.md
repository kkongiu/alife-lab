# M6.3-6 — Decisione scientifica dopo cinque step

**Step 5/5 — consolidamento e decisione, NON nuova simulazione indipendente.**

## Integrità dell'evidenza

Gli step **M6.3-2, -3, -4, -5 e -6** sono cinque analisi/prodotti dello **stesso campione M6.3-1 di 160 universi**. Non rappresentano 800 run indipendenti o cinque test causali separati.

- [Protocollo congelato **prima dell'analizzatore**](https://github.com/kkongiu/alife-lab/commit/43613a0818edab180a60cd70ab3cdfe7f1e43a51).
- [CI riuscita con intera suite `pytest` e 160 replay](https://github.com/kkongiu/alife-lab/actions/runs/43737009689).
- [Dati JSON di ogni caso, inclusi zeri, right-censoring, RNG, hash, energia ed eventi](https://github.com/kkongiu/alife-lab/actions/runs/43737009689/artifacts/14170732108).
- Su due controlli fissati **prima** dell'audit (`baseline/8101/A`, `enriched/8101/A`), il nuovo osservatore e quello M6.3-1 hanno prodotto gli stessi **hash, RNG, contatori di formazione e rottura, energia e tick di forma pura**.
- Il branch non modifica `src/`, le regole del movimento, valenze, catalisi, dinamica energetica o `master`.

## Decisioni dopo i cinque step

| Problema | Evidenza | Decisione |
|---|---|---|
| Che cosa causa la prima perdita? | **67/80** baseline e **80/80** enriched si estendono per attacco di materiale, senza perdita netta dei legami originali | Non trattare `not pure` come `destroyed` |
| Il nucleo è fragile ad alta densità? | Media dei tick con tutti i legami originali presenti: **252** baseline, **333** enriched; attenzione alle possibili riformazioni | Misurare *persistenza di nucleo* e *purezza* separatamente |
| Le risorse mancano? | In condizione enriched ci sono più coppie eleggibili **per tick puro**, ma la fase pura dura poco; dopo crescita, poche coppie eleggibili | Priorità a accessibilità/valenza e tempo effettivo di contatto, non solo densità |
| La crescita genera copiatura A/B? | La forma B compare vicino a sorgenti A, B e C; nessun vantaggio coerente della variante sorgente | **Nessuna ereditarietà osservata** |
| Dobbiamo cambiare le leggi? | I test non identificano ancora una limitazione fisica unica che giustifichi una regola nuova | **NO: nessuna modifica alla fisica** senza proposta e autorizzazione |

## Prossimo esperimento consigliato, non eseguito qui

**M6.3-7: osservazione degli estremi reattivi e del destino dei nuclei cresciuti**, con nuovo protocollo e seed indipendenti **prima** dei risultati. Misurare:
1. durata continua dei legami originali (non soltanto presenza in snapshot), ricomparsa e sostituzione di legami;
2. valenza ancora disponibile e superfici adiacenti ai diversi motivi, separando accessibilità da pura abbondanza di monomeri;
3. se la crescita rende il nucleo un centro di reclutamento *aspecifico* o mostra una preferenza ripetibile per sequenze/varianti, con controlli isoenergetici e correzione per la cinetica.

Solo dopo questi dati sarà sensato valutare separatamente:
- una proposta **B** di catalisi strutturale locale, oppure
- una proposta **A** di mobilità rigida degli aggregati.

Entrambe cambierebbero le leggi e **richiedono un razionale teorico distinto e approvazione esplicita**. Non introdurre un `copy` hardcoded, non cambiare soglie retroattivamente, non chiamare l'evento `unfed-6101` organismo o autoreplicatore.

**Verdetto generale:** `physical-growth-bottleneck-identified; causal-information-transfer-not-demonstrated`. L'audit è un **GO strumentale**, non un GO biologico/M7.
