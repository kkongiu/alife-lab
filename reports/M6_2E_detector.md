# M6.2-E — Report: rilevatore v2 per copie progressive

Data: 2026-11-15 · Milestone: M6.2-E · Preregistrazione:
`campaigns/m6_2e/manifest.json` · Risultati: `campaigns/m6_2e/results.json`
· Rilevatore: `src/alife/replication_v2.py` (v1 invariato)

## 1. Sommario

| Voce | Esito |
|---|---|
| Rilevatore v2 | implementato, versionato e validato sui controlli M5 |
| v1 sui controlli M5 | positivo riconosciuto, negativi rifiutati |
| Ri-analisi M6 | 25/25 run, **hash del mondo identici a M6** |
| Candidate v1 | 0 |
| Candidate v2 | **1 051** (mediana 35–66 per run) |
| Candidate che raggiungono la firma | **1** |
| Copie persistenti | **1** |
| Catene di seconda generazione | **0** |
| Verdetto | **`no_evidence`** |

Il punto cieco del v1 esiste ed è stato misurato: il v1 non vedeva 1 051
candidate di prossimità. Il v2 le vede, ma una sola raggiunge la firma del
template e nessuna forma una discendenza. **Non c'era una replicazione nascosta
dietro il punto cieco.**

## 2. Perché un rilevatore v2

Il v1 richiede una struttura che **nasce già completa** (≥ 4 particelle) accanto
a una simile. In M6 il 99% delle nascite è dimerico (4 705–5 008 nascite di
dimensione 2 contro 12–14 di dimensione 3 e **zero** ≥ 4): le strutture crescono
per accrezione. Un replicatore che si assemblasse gradualmente sarebbe
invisibile — non perché non esista, ma perché il criterio non lo cerca.

Il v2 estende il criterio senza modificare il v1:

1. una nascita (di qualsiasi dimensione) entro 2 celle da un template con firma
   esatta di dimensione ≥ 4, nato prima;
2. la struttura raggiunge **la stessa firma del template** entro 150 passi,
   mentre il template è ancora attivo;
3. la copia persiste 10 passi dopo il raggiungimento;
4. la classificazione richiede ≥ 5 copie persistenti e una catena di seconda
   generazione, costruita solo con copie persistenti.

Parametri fissati in `campaigns/m6_2e/manifest.json` prima dell'esecuzione, con
hash delle sorgenti M6 e hash attesi dei 25 mondi.

## 3. Validazione sui controlli M5

Prima di applicare il v2 a M6, i criteri sono stati congelati e verificati sui
controlli già esistenti:

| Controllo | Candidate | Persistenti | Esito |
|---|---|---|---|
| positivo template-diretto | 9 | 9 (gen. 9) | `replication` |
| N1 immobile | 0 | 0 | `not_replication` |
| N2 aggregazione casuale | 4 | 0 | `not_replication` |
| N3 reazioni reversibili | 62 | 0 | `not_replication` |
| stress specie unica | 0 | 0 | `not_replication` |
| stress formazione massima | 1 | 0 | `not_replication` |

Il v2 produce candidate anche nei negativi (62 in N3), ma **nessuna raggiunge la
firma del template**: vengono scartate per morte, scomparsa del template o
scadenza della finestra. Il criterio non è stato allentato per ottenere un
positivo; è stato validato prima di guardare M6.

## 4. Ri-analisi dei 25 run M6

**Metodo.** I 25 mondi M6 sono stati rieseguiti con le stesse configurazioni e
seed. Per ogni run l'hash completo del mondo è stato confrontato con quello
registrato in `campaigns/m6/results.json`: **25/25 identici**. L'analisi riguarda
quindi gli stessi percorsi, non run nuovi. v1 e v2 sono stati applicati in
parallelo.

| Condizione | Run | v1 candidate | v2 candidate (mediana) | v2 raggiunte | v2 persistenti | Gen. max |
|---|---|---|---|---|---|---|
| `closed` | 5 | 0 | 66 | 0 | 0 | 0 |
| `unfed` | 5 | 0 | 35 | 1 | 1 | 1 |
| `fed-low` | 5 | 0 | 36 | 0 | 0 | 0 |
| `fed-mid` | 5 | 0 | 37 | 0 | 0 | 0 |
| `fed-high` | 5 | 0 | 37 | 0 | 0 | 0 |

**Perché le candidate non diventano copie.** Su 1 051 candidate:

| Esito | Numero |
|---|---|
| muore prima di raggiungere la firma | 318 |
| il template scompare prima | 284 |
| la finestra di 150 passi scade | 438 |
| ancora in attesa alla fine del run | 10 |
| raggiunge la firma (di cui persistenti) | 1 (1) |

La struttura nasce vicino a un template, ma nella grande maggioranza dei casi
non arriva alla sua forma: le dinamiche di accrezione e rottura la disfano prima.

**L'unica candidata** è in `unfed-6101`: una copia progressiva che raggiunge la
firma del template e persiste 10 passi, generazione 1. Non ha discendenti e non
è accompagnata da altre copie persistenti: è un candidato da esaminare, non un
risultato.

## 5. Osservazioni e ipotesi

**Osservazioni** (misure):

1. il v1 non vede alcuna candidate; il v2 ne vede 1 051, con lo stesso criterio
   di persistenza e la stessa soglia di classificazione;
2. 1 040 candidate su 1 051 sono scartate esplicitamente prima di raggiungere la
   firma, e 10 sono ancora in attesa alla fine del run;
3. una sola raggiunge la firma; nessuna catena di seconda generazione;
4. tutte le condizioni, controlli compresi, restano `not_replication`;
5. il verdetto preregistrato è `no_evidence`.

**Ipotesi** (non dimostrate):

- la forma delle strutture in M6 è troppo labile perché una copia progressiva
  possa conservarla: le vite medie (271–445 passi) sono confrontabili con la
  finestra di 150 passi, ma la crescita è interrotta da rotture e morti;
- il template scompare spesso prima che la copia maturi (284 casi): in un
  universo senza mobilità degli aggregati, il template non può "attendere" né
  proteggere la copia;
- la prossimità non è causalità: il v2 misura che una struttura cresce vicino a
  un template, non che il template l'abbia guidata. Servirebbe un controllo con
  template rimosso o spostato per distinguere le due cose.

## 6. Limiti

1. **Prossimità ≠ causalità.** Il criterio è necessario, non sufficiente.
2. **Finestra di 150 passi.** Copie più lente sarebbero invisibili; il valore è
   preregistrato, non ottimizzato sui risultati.
3. **Firma esatta.** I cicli restano impronte e non sono ammessi come target;
   una copia ciclica non sarebbe riconosciuta con la stessa certezza.
4. **Nessuna nuova legge.** Il v2 è un livello di analisi: non cambia ciò che
   l'universo può fare, solo ciò che sappiamo osservare.
5. **Un solo candidato** non è una popolazione: non si può stimare una
   distribuzione, né una frequenza.

## 7. Test e riproducibilità

- 7 test dedicati al v2: versione, controlli M5, assemblaggio progressivo,
  soglia di due generazioni, nascite simultanee, determinismo.
- 3 test sulla ri-analisi: preregistrazione, riferimenti a M6, completezza e
  corrispondenza degli hash.
- La ri-analisi è rieseguibile con
  `tools/reanalyze_m6_2e.py --force`; i risultati sono deterministici.
- Suite completa: **186 test**.

## 8. Verdetti

**M6.2-E: GO.** Il punto cieco è stato misurato e chiuso senza modificare il
v1; il v2 conserva la validazione sui controlli e non altera la classificazione
di M6. La ri-analisi è sugli stessi percorsi (hash identici) e registra tutte le
candidate, comprese quelle scartate.

**Passaggio a S7: REVISE (invariato).** Il v2 trova 1 051 candidate di
prossimità ma una sola copia persistente e nessuna catena: non c'è evidenza di
replicazione progressiva in M6. Il prossimo passo utile non è un rilevatore
ancora più permissivo, ma una modifica delle leggi che renda **possibile** una
copia: catalisi attiva (M6.2-B) e movimento degli aggregati (M6.2-A), nell'ordine
proposto dalla diagnosi M6.1.
