# M6.7 — Il ritorno degli anelli è compatibile con il semplice legame locale al 5%

**Status scientifico:** campagna completata con risultato descrittivo **`consistent_with_simple_contact_reference_descriptive`**; non equivale ad accettare matematicamente un'ipotesi nulla né prova che le simulazioni non possano avere dinamiche complesse.

**Protocollo fissato prima del codice e degli esiti:** [commit `c6fc5f92`](https://github.com/kkongiu/alife-lab/commit/c6fc5f92bd9b35401f945028f6217b3c01a7fff0), `campaigns/m6_7_reclosure_null/protocol.json`.

**GitHub Actions:** [run #43760411559 — PASS](https://github.com/kkongiu/alife-lab/actions/runs/43760411559), suite pytest integrale più 40 universi naturali e 156 fork di apertura. **Dati grezzi integrali:** [artifact 14179199657](https://github.com/kkongiu/alife-lab/actions/runs/43760411559/artifacts/14179199657).

## Domanda falsificabile

M6.6 aveva osservato che **31/76 (40,8%)** degli anelli perturbati richiudevano un legame entro 10 tick. In M6 la formazione di un legame chimicamente consentito e fra vicini ha probabilità `p = 0.05` per candidato e tick, salvo disponibilità energetica, catalisi e conflitti.

Il riferimento analitico più semplice per *una coppia che riceva esattamente un tentativo valido e indipendente ogni tick* è

`P(almeno una formazione in 10 tick) = 1 - (1 - 0.05)^10 = 0.401263060761621`.

**Importante:** questo è un confronto **naïf**, non la probabilità rigorosa di riformazione in un universo affollato. Le condizioni di ammissibilità possono cambiare dopo rotture, movimento, reazioni concorrenti o differenze nell'ordine delle proposte.

## Nuova campagna prospettica

Nuovi seed **9201–9220**, non utilizzati nelle campagne precedenti, × densità 200/264: **40** mondi inizialmente senza legami. I primi due anelli naturali con quattro ID materiali distinti entro 600 tick sono selezionati senza ottimizzazioni successive: **40** anelli nella densità normale e **38** in quella arricchita, **78** in totale. Ogni anello è clonato due volte, aprendo il legame con ID minimo o quello opposto, conservando l'energia del mondo mediante redistribuzione della quota immagazzinata nel legame. Le leggi fisiche e il generatore RNG non cambiano.

Ogni fork è osservato per 10 tick. La misura **primaria** è la comparsa di un evento chimico nativo `BondEvent(kind=form)` relativo alla **coppia originale aperta**, non una somiglianza della struttura. Separatamente viene controllata la ricomparsa di un anello esattamente dei quattro ID originali.

## Risultati: 156 traiettorie di apertura

| Densità | Apertura | Nuova formazione del legame entro 10 tick | Scostamento dalla reference 40,126% | Disponibilità del candidato pre-tick prima del primo evento |
|---|---|---:|---:|---:|
| 200 | Legame ID minimo | **13/40 = 32,5%** | −7,63 pp | **299/350 = 85,43%** |
| 200 | Legame opposto | **15/40 = 37,5%** | −2,63 pp | **275/327 = 84,10%** |
| 264 | Legame ID minimo | **14/38 = 36,84%** | −3,28 pp | **242/300 = 80,67%** |
| 264 | Legame opposto | **16/38 = 42,11%** | +1,98 pp | **238/284 = 83,80%** |

In **tutti e quattro** gli strati, il tasso osservato differisce dal benchmark `0,401263` per meno del margine **±10 punti percentuali** fissato nel protocollo. Ogni strato possiede ≥20 osservazioni, quindi supera il requisito di numerosità **descrittivo**.

Per questa campagna: **58/156 = 37,18%** fork hanno formato il legame originale entro 10 tick. Contemporaneamente, esattamente **58/156** sono stati osservati come anelli di quattro ID originali entro lo stesso orizzonte: in tutti gli strati `target_event_but_no_ring_snapshot=0` e `ring_snapshot_but_no_target_event=0`. Questo descrive **chiusura di un legame ordinario** e non produzione di un nuovo organismo.

L'osservatore ha anche misurato che, prima della prima riformazione o della fine dei 10 tick, la coppia era un candidato chimico statico visibile nel **solo 80,7%–85,4%** delle fotografie pre-passo. Il contatto sempre disponibile presupposto dal semplice benchmark quindi **non è completamente soddisfatto**. Inoltre le condizioni vengono rilevate prima di dissipazione, rottura e movimento, non precisamente all'istante di proposta chimica; il confronto non è un test di hazard esatto.

## Decisione e implicazioni

**Gate di M6.7: PASS, esclusivamente in senso descrittivo.**

L'affascinante fenomeno della richiusura rapida degli anelli si spiega plausibilmente con **la regola ordinaria di formazione dei legami fra due estremi adiacenti**. È un'informazione nuova perché ridimensiona l'ipotesi esplorativa di un possibile meccanismo speciale di autoriparazione. Non dimostra nulla di biologico, non implica un genoma né un metabolismo, e non è un test significativo dell'assenza di qualunque altra dinamica emergente.

### Qualità dei dati

- Tutte le 40 condizioni naturali, 78 anelli selezionati e 156 fork sono inclusi, inclusi casi senza riformazione.
- Suite pytest completa e simulazione CI passate.
- Le due orientazioni di apertura partono da identiche fotografie, con energia conservata e RNG iniziale coincidente.
- L'osservatore registra eventi originali e controlla candidati senza consumare RNG.
- Per il primo fork del primo seed in ciascuna densità, la traiettoria di 10 tick senza osservatore produce **identici hash, RNG, energia e contatori di legame**.
- I due anelli dello stesso universo non costituiscono due repliche indipendenti. Nessun p-value e nessuna inferenza di potenza.
- Nessuna modifica a `src/`, schema fisico, `master` o dati storici.

### Prossima domanda

Il passo successivo più informativo è **separare causalmente il ruolo della liberazione delle valenze da quello dell'energia restituita agli estremi**: creare fork che aprano lo stesso legame senza far cambiare l'energia dei quattro atomi (trasferendola a una particella S3 non reattiva lontana), confrontati con l'apertura classica che la restituisce agli estremi. Questo è un altro intervento sulle condizioni iniziali, NON una modifica della fisica: preregistrare e verificare sempre gli invarianti.
