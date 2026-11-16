# M6.14 — Replica indipendente della *prima* compartimentazione geometrica: 16/1600, con verifica post-hoc più severa 15/1600

**Data:** 16 novembre 2026. **Stato:** campagna completa, CI verde, verifica fisica indipendente di **tutti e sedici i casi primari** verde. **Decisione preregistrata:** `replicated_first_genesis_native_geometric_confinement_only`. Significa **primo confinamento geometrico nativo replicato** nelle condizioni del simulatore, **non** formazione di cellule vive o autoreplicanti.

## Tracciabilità

- [Protocollo M6.14 congelato prima di implementazione e risultato: commit `995bdbb`](https://github.com/kkongiu/alife-lab/commit/995bdbb988b54c2fa319c56ae32b54297151d15d).
- [GitHub Actions PASS — otto shard, 1600/1600 mondi, regressioni, verifica finale #43855208596](https://github.com/kkongiu/alife-lab/actions/runs/43855208596).
- [Dataset completo con tutti gli esiti negativi, identificativi originali, eventi e replay: artifact #14219473866](https://github.com/kkongiu/alife-lab/actions/runs/43855208596/artifacts/14219473866).
- [Verifica fisica indipendente e post-hoc PASS #43856432601](https://github.com/kkongiu/alife-lab/actions/runs/43856432601) e [relativo artifact #14220403811](https://github.com/kkongiu/alife-lab/actions/runs/43856432601/artifacts/14220403811).
- [Pull Request in bozza #26](https://github.com/kkongiu/alife-lab/pull/26). `master` e `src/alife/` invariati.

## Perché è diverso da M6.13

M6.13 aveva raggiunto il criterio largo di 30 tick in tre seed, ma la sensibilità restrittiva che ammetteva soltanto il **primo episodio** del medesimo gruppo di atomi ne confermava uno solo. M6.14 sposta **prima di vedere nuovi dati** quel criterio restrittivo nell'endpoint principale e aggiunge un'altra esclusione: se l'insieme di otto ID era già comparso in precedenza come **anello nativo di otto legami**, una successiva apertura a sette legami **non è una nuova prima formazione**.

Pertanto `first_genesis` significa **prima osservazione di questi stessi otto atomi in una configurazione geometrica di perimetro 3×3 con sette oppure otto legami**. Non significa prima interazione chimica in assoluto tra quegli atomi, né prova di costruzione orientata a intrappolare un residente.

## Esperimento preregistrato

- **1.600 seed nuovi**, numeri 13001–14600, **densità enriched soltanto**, 264 particelle in una griglia periodica 24×24; 600 tick per mondo, **960.000 tick-mondo**. La densità era stata selezionata *prima* del nuovo campione perché era l'unica con risultati positivi negli studi precedenti. Non è lecito extrapolare questi tassi al regime baseline o ad altre densità.
- Condizioni native M6 originali, tutti i mondi partono con **zero legami**, nessun anello/monomero aggiunto, nessuna regola fisica modificata.
- Fonte originale: `tools.m6_4_cycles.create_natural`. Osservatore passivo: esattamente otto ID materiali collocati nei siti del perimetro 3×3, legati da **sette** connessioni originali lungo il bordo; una particella centrale nativa deve essere **inizialmente libera (grado zero) e mobile**.
- La durata riguarda il mantenimento delle sette connessioni originali e dell'identità del residente, non necessariamente lo stato chimico libero del residente in tutti i tick (questa distinzione è verificata separatamente nell'audit post-hoc). Una rottura di un legame originario interrompe l'episodio anche se il legame si riforma durante lo stesso passo.
- **Criterio principale congelato:** almeno **due nuovi seed distinti** con prima formazione di quel materiale in configurazione a sette legami e un residente centrale nativo, stabili per ≥30 tick osservati.
- Otto shard predefiniti da 200 mondi; l'aggregatore verifica tutti i 1600 seed, hash identico del protocollo, nessun duplicato, replay senza osservatore per ogni universo con qualsiasi evento mobile ≥30 e per il seed fisso 13001.

## Esiti principali

| Misura | Risultato |
|---|---:|
| Universi completati | **1.600 / 1.600** |
| Episodi di strutture native a 7 legami | **375** |
| Prime configurazioni a 7 legami di nuovi insiemi materiali | 161 |
| Episodi di riapparizione di materiale già osservato | 214 |
| Episodi con residente inizialmente mobile e libero | 53 |
| Episodi iniziali con residente libero e mobile | 25 |
| **Seed con prima formazione ≥30 tick** | **16** |
| Seed con almeno un episodio qualsiasi ≥30 tick | 22 |
| Seed con confinamento ≥30 soltanto dopo ricomparse | 6 |
| Episodi mobili ≥30 tick, incluse ripetizioni | 35 |
| Prima formazione ≥100 tick | 3 seed |
| Prima formazione ≥250 tick | 0 seed |

**Risultato preregistrato: 16 seed distinti**, contro il requisito minimo di 2. Il tasso descrittivo è **16/1600 = 1,00%**, intervallo di Wilson al 95% **0,62–1,62%**. Per almeno un episodio mobile lungo, incluse ricomparse, la frequenza è **22/1600 = 1,375%** (IC descrittivo 0,91–2,07%). I singoli tick o episodi della stessa configurazione non sono unità indipendenti; questi intervalli sono calcolati a livello di **seed**.

I 16 seed primari sono: **13082, 13303, 13364, 13507, 13622, 13728, 13773, 13970, 13972, 14191, 14339, 14404, 14421, 14448, 14463, 14527**.

### I casi iniziali più duraturi

| Seed | Centro | ID residente | Passi continui | Ottavo legame osservato? | Esito |
|---|---|---:|---:|---|---|
| **13972** | (16,1) | 250 | **241** | **No** | Interruzione di un legame originale |
| **14527** | (10,11) | 252 | **144** | No | Interruzione |
| **14191** | (16,4) | 226 | **143** | Sì, tick 264 | Interruzione |
| **14463** | (0,8) | 248 | 94 | No | Interruzione |
| **13507** | (6,20) | 250 | 90 | No | Interruzione |

La barriera più longeva, **241 tick**, si osserva **senza mai formare l'ottavo legame**. Questo è coerente con un principio geometrico: il confinamento dipende da un bordo di particelle occupanti i quattro vicini cardinali del centro, non da una topologia a ciclo completo.

## Audit post-hoc indipendente: distinzione importante tra confinamento e cattura chimica

Il primo audit indipendente ha segnalato che nel seed **13303** il residente inizialmente libero **diventa legato** durante l'episodio. Questo **non falsifica** l'endpoint primario congelato, che richiedeva grado zero alla prima osservazione, identità stabile del residente e sette legami originali continui, **non** grado zero del residente a ogni tick. Cambia però l'interpretazione fisica, perché il residente può passare da confinamento geometrico a cattura chimica.

Per evitare ambiguità, il nuovo audit `tools/m6_14_independent_physical_audit.py` ha rifatto **tutti e 16 i seed** senza chiamare `precursor_candidates`, `observed_cycles` o il classificatore originale M6.14. Ricostruisce da zero la geometria a sette/otto legami di quegli specifici ID in tutti i tick precedenti, accerta **assenza di analoghe configurazioni precedenti**, controlla ogni legame originario, la posizione dei materiali, l'identità del residente, l'eventuale grado del residente a ogni tick e la rottura esatta che conclude il periodo; per ogni seed ripete poi il mondo senza osservatore e confronta hash completo, RNG, energia e contatori fisici.

**Tutti 16/16 verificati: PASS** nell'[esecuzione #43856432601](https://github.com/kkongiu/alife-lab/actions/runs/43856432601). Introducendo **post-hoc** il criterio supplementare di *residente ininterrottamente di grado zero per almeno i primi 30 tick*, rimangono **15/1600 seed** (0,94%, Wilson descrittivo 95% circa 0,57–1,54%). Il seed 13303 è quello escluso dall'endpoint più severo. Anche **15 seed distinti** sono ampiamente oltre il minimo di due, ma il criterio 'sempre libero per 30 tick' è **una verifica di robustezza successiva**, non l'endpoint preregistrato.

**Attenzione:** perfino un residente che rimane chimicamente non legato per 30 tick non dimostra il funzionamento di una membrana biologica: i movimenti sono bloccati dalla regola di occupazione del reticolo. La barriera non è un oggetto biologico auto-assemblato per uno scopo e non può crescere, replicarsi o mantenere attivamente un metabolismo in questo modello.

## Quale passo successivo sarebbe scientificamente utile?

L'evidenza a questo punto è solida per **esistenza e ripetibilità del confinamento geometrico nativo al primo evento osservato**, con nuovi seed e verifiche fisiche indipendenti. Ulteriori campagne di conteggio alle stesse condizioni hanno rendimento informativo decrescente.

Un esperimento **M6.15** dovrebbe introdurre, in un protocollo separato e dichiarato come controfattuale, una domanda realmente causale: a parità di posizione, specie, energia e sette connessioni materiali, **la presenza di un monomero nel centro modifica il tasso di rottura dei legami originali o la durata del bordo?** Separare la componente già predetta dalla chimica locale dall'eventuale effetto dell'occupazione centrale. Il confronto richiede controlli abbinati su stati nativi e attenzione alla dipendenza dei flussi RNG se si modificano le condizioni iniziali. Senza prova di un meccanismo causale o di ereditarietà, **non** bisogna usare termini come 'vita', 'organismo', 'protocellula' in senso affermativo.
