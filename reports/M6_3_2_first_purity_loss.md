# M6.3-2 — Prima perdita della forma originale

**Step 1/5 — diagnostica causale locale degli eventi fisici (non della replicazione).**
Protocollo congelato [43613a0](https://github.com/kkongiu/alife-lab/commit/43613a0818edab180a60cd70ab3cdfe7f1e43a51), riprodotto con la CI [43737009689](https://github.com/kkongiu/alife-lab/actions/runs/43737009689) e [JSON integrale](https://github.com/kkongiu/alife-lab/actions/runs/43737009689/artifacts/14170732108).

**Campione:** esattamente gli **160 universi storici M6.3-1** (due densità, 16 seed, cinque sonde; 450 tick). Studio osservazionale *post hoc*: gli eventi erano già generati dalle leggi originali.

La forma **pura** richiede le quattro particelle sorgente isolate, con i tre legami originari e firma esatta. Il primo momento in cui smette di essere pura è classificato dal cambiamento **netto** del grafo e dagli eventi `BondEvent` prodotti dalla chimica, non da differenze di hash.

| Prima perdita | Baseline, 200 particelle (80 run) | Enriched, 264 particelle (80 run) |
|---|---:|---:|
| Nuovo materiale si attacca, legami originari presenti | **67** | **80** |
| Almeno un legame originario assente, nessun attacco | 11 | 0 |
| Rottura e attacco nello stesso esito osservato | 1 | 0 |
| Nessuna perdita entro 450 tick (censura) | 1 | 0 |
| Primo tick di perdita, media sui run osservabili | 18,94 | 8,08 |

Fra gli eventi di formazione registrati al primo tick di perdita, **60** baseline e **70** enriched coinvolgono un vicino che era libero *nel tick precedente*, mentre **8** e **15** coinvolgono un vicino già legato nel tick precedente. Questi sono **conteggi di eventi**, non di run: possono essercene più di uno nel medesimo tick. Un monomero libero nel tick precedente potrebbe aver formato altri legami prima dell'attacco, nello stesso avanzamento.

**Conclusione:** l'elevata densità accelera la perdita dell'**isolamento** della sonda soprattutto tramite **accrescimento e incorporazione**, non tramite rottura immediata della catena. La legge di rottura non è stata modificata. La classificazione non dimostra in alcun modo un effetto di copia informativa.

**Integrità:** osservazione non invasiva, `pytest` superato; nessun cambiamento a `src/`, RNG o mondo M6. Vedi [M6.3-3](M6_3_3_core_retention.md) per la sopravvivenza effettiva del nucleo.
