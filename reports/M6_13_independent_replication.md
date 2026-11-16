# M6.13 — Replica del confinamento geometrico nativo in 3 seed nuovi (con sensibilità sfavorevole alla prima formazione)

**Data:** 16 novembre 2026. **Stato:** protocollo preregistrato ed eseguito, **CI PASS**. Il criterio principale di replicazione a **due seed distinti** è soddisfatto, ma la verifica restrittiva sulla **prima comparsa dell'insieme materiale** trova un solo seed con durata ≥30 tick: la conclusione è quindi **replicazione del confinamento dopo possibili ricostituzioni, non conferma di formazione iniziale indipendente di strutture longeve**.

- [Protocollo congelato **PRIMA** del codice: commit `f176d0f`](https://github.com/kkongiu/alife-lab/commit/f176d0faf8e7366557c3f46f1cdf7285ea1c2667).
- [GitHub Actions — 4 shard + verifica dell'aggregazione, PASS #43851629351](https://github.com/kkongiu/alife-lab/actions/runs/43851629351).
- [Dati completi 800 mondi, compresi gli zeri, artefatto #14218570849](https://github.com/kkongiu/alife-lab/actions/runs/43851629351/artifacts/14218570849).
- Codice dell'osservatore M6.12 invariato; motore M6, leggi energetiche, `src/` e `master` **immutati**. Le scoperte di M6.11 e M6.12 NON partecipano al conteggio M6.13.

## Protocollo e definizione

**400 seed nuovi (12001–12400)** × **due densità** (baseline 200 particelle; enriched 264) = **800 universi**, ciascuno osservato per **600 tick** su reticolo toroidale 24×24, senza legami iniziali né template artificiali. Quattro shard con 200 universi ciascuno; l'aggregatore controlla copertura 800/800, assenza di duplicati, hash del protocollo identici e ricalcola il verdetto solo dopo tutti i risultati.

La definizione di barriera è la stessa di M6.12: otto particelle **native** occupano l'intero perimetro 3×3, collegate da **sette legami nativi originali** che non si interrompono durante l'episodio; al centro c'è una particella **nativa, libera, mobile** il cui ID resta invariato. Le particelle che costituiscono il bordo sono immobili finché legate. L'ottavo legame può formarsi o rompersi, ma **non è il requisito per il confinamento geometrico**. Un evento di rottura anche transitorio di uno dei sette legami originari termina l'episodio.

**Criterio principale, fissato a priori:** almeno **due numeri di seed nuovi e distinti**, indipendentemente dalla densità, in cui una particella mobile è confinata per almeno **30 tick consecutivi** in un episodio. Un seed usato in entrambi i regimi di densità viene contato **al massimo una volta**. Episodi ripetuti dello stesso mondo e della stessa struttura non diventano nuove repliche. I casi censurati al termine del run si contano solo per la persistenza già osservata, senza inferire il seguito.

## Risultati verificati

| Indicatore | Baseline (400 mondi) | Enriched (400 mondi) |
|---|---:|---:|
| Episodi di precursore nativo 7/8, inclusi ripetuti | 42 | 110 |
| Prime apparizioni di insiemi materiali (episodi) | 21 | 45 |
| Episodi con centro occupato da particella mobile | **0** | **17** |
| Episodi mobili con durata ≥30 tick | **0** | **6** |
| Episodi mobili con durata ≥100 tick | 0 | **2** |
| Episodi mobili con durata ≥250 tick | 0 | **0** |
| Mondi con confinamento ≥30 tick | 0 | **3** |
| Mondi con confinamento ≥100 tick | 0 | **2** |
| Episodi ≥30 tick censurati a fine simulazione | 0 | **0** |

Gli episodi con centro occupato rappresentano più volte gli stessi insiemi materiali. Nessun mondo baseline ha soddisfatto ≥30 tick; i tre mondi positivi sono tutti enriched.

### Tre nuovi seed indipendenti positivi

| Nuovo seed | Centro | Residente mobile | Massima durata di un episodio continuo | Ottavo legame in quell'episodio | Prima apparizione del materiale? |
|---|---|---:|---:|---:|---|
| `12199` | (22,8) | ID 260 | **51 tick** (dal 217 al 267) | tick 220 | **Sì** |
| `12229` | (1,8) | ID 254 | **105 tick** (dal 24 al 128) | tick 74 | **No**; episodio iniziale di 5 tick |
| `12321` | (14,11) | ID 253 | **160 tick** (dal 344 al 503) | tick 362 | **No**; episodio iniziale di 18 tick |

A t=268, 129 e 504 rispettivamente, un evento di rottura di un legame originale segna la fine dei tre episodi lunghi. Il fatto che si formino nuovamente alcuni legami è compatibile con la chimica reversibile prevista dal modello; **non** dimostra una riparazione biologica o intenzionale.

Per gli altri casi mobili ma brevi, vengono registrate tutte le durate e i casi nulli nell'artefatto originale; non sono esclusi dai denominatori.

## Decisione preregistrata, in due letture

**Lettura principale:** `replicated_30tick_native_geometric_confinement_only` — **3 seed distinti** con almeno 30 tick osservati, contro il requisito di 2. Quindi è ripetibile la comparsa *almeno una volta nel mondo* di un episodio abbastanza persistente con materiale nativo e residente nativo.

**Sensibilità restrittiva, preregistrata:** contando soltanto la **prima osservazione** del medesimo insieme materiale per ogni mondo, **solo il seed 12199** ha una barriera lunga almeno 30 tick già nel suo primo episodio. La prova **non** soddisfa la stessa soglia di due seed nella lettura restrittiva. Questo è un limite fondamentale all'interpretazione della formazione spontanea iniziale: in `12229` e `12321` gli episodi più lunghi seguono un primo episodio breve dello stesso materiale.

### Stima di frequenza descrittiva

Con unità conservativa di 400 seed numerici distinti, **3/400 = 0,75%**, intervallo Wilson descrittivo al 95% **0,26%–2,18%**. Nel regime enriched sono ancora **3/400 = 0,75%**; nel baseline **0/400**, limite superiore Wilson ≈ **0,95%**. Gli intervalli non misurano probabilità di vita o autoreplicazione e non dimostrano una differenza causale fra densità. L'esperimento non è progettato per stabilire una legge universale sulle frequenze di confinamento.

## Integrità

- **CI completamente verde**: test originali e nuovi, quattro shard e aggregazione dei 800/800 mondi.
- **Cinque replay senza osservatore:** baseline/12001, enriched/12001 e i tre mondi positivi enriched/12199, enriched/12229, enriched/12321. Per ciascuno, coincidono hash completo finale, stato/numero estrazioni RNG, energia, dissipazione e contatori di legami.
- Tutti i risultati (inclusi universi senza anelli), episodi materiali, durate, chiusure ottavo legame e marcatori di censura sono conservati nel dataset. **Nessun p-value derivato da tick o episodi correlati**.
- Gli stessi 400 numeri di seed sono usati per due densità: ciò è gestito contando il **numero di seed unici**, non 800 prove statisticamente del tutto indipendenti.


### Audit fisico indipendente, successivo ai risultati (post-hoc)

Il codice [`tools/m6_13_physical_crosscheck.py`](../tools/m6_13_physical_crosscheck.py) **non** chiama il rilevatore M6.12 né la logica di classificazione degli episodi M6.13. Esegue da zero i tre universi positivi, controlla **a ogni singolo tick** tutte le sette connessioni materiali originali, la geometria del bordo, l'ID e il grado del residente, l'istante di formazione dell'ottavo legame e l'esatto evento di rottura che termina l'intervallo. Ripete ciascun mondo senza osservatore e verifica identità di hash completo, RNG, energia e contatori fisici.

Il controllo aggiuntivo è **PASS**: [GitHub Actions #43852751508](https://github.com/kkongiu/alife-lab/actions/runs/43852751508), [artefatto #14219805388](https://github.com/kkongiu/alife-lab/actions/runs/43852751508/artifacts/14219805388). Conferma:

| Seed | Tick iniziale | Ultimo tick integro | Prima rottura originale | Legame rotto | Tick ottavo legame |
|---|---:|---:|---:|---|---:|
| `12199` | 217 | 267 | 268 | 9–56 | 220 |
| `12229` | 24 | 128 | 129 | 29–39 | 74 |
| `12321` | 344 | 503 | 504 | 8–133 | 362 |

Questa verifica è **post-hoc**, non una nuova replica statistica né una modifica delle soglie preregistrate. Conferma l'implementazione dell'osservazione su tre traiettorie note, non la validità biologica del modello.

## Significato scientifico

Abbiamo **un fenomeno fisico simulato ripetibile** di confinamento passivo per decine o centinaia di passi, in un sistema con legami reversibili locali e regole deterministiche condizionate al seed. Il modello però non implementa riproduzione di particelle, metabolismo, selettività di una membrana, capacità di crescita organizzata o ereditarietà. Il risultato è una premessa per investigare forme primitive di compartimentazione *geometrica*, non evidenza di vita artificiale.

**Proposta M6.14:** preregistrare una verifica di **formazione iniziale** su nuovi seed (criterio esclusivo: primo episodio per insieme materiale, ≥30 tick in almeno due seed) e, in uno studio distinto, confrontare ricostituzione e durata di una barriera dopo rotture naturali rispetto a controlli con la stessa composizione e geometria. Separare rigorosamente prova di ricorrenza da prova di auto-mantenimento. Nessuna variazione delle leggi senza un protocollo separato.
