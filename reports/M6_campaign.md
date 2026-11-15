# M6 — Report: campagna esplorativa multi-universo

Data: 2026-11-15 · Campagna: `m6` · Preregistrazione: `campaigns/m6/manifest.json`
· Esecutore: `tools/run_campaign.py` · Risultati: `campaigns/m6/results.json`

## 1. Sommario

| Voce | Esito |
|---|---|
| Campagna | **GO** — 25 run su 25, protocollo preregistrato rispettato, nessun run omesso |
| Passaggio a S7 | **REVISE** — nessun candidato replicante; risultato negativo documentato |
| Controlli | `closed` e `unfed` non classificati: il criterio regge |
| Copie rilevate | 0 su 25 run |

La priorità dichiarata era produrre esperimenti riproducibili, non un risultato
positivo. Il risultato è negativo e riproducibile.

## 2. Preregistrazione

Prima di eseguire qualsiasi run, `tools/preregister_m6.py` ha scritto:

- 5 condizioni, 5 seed (`6101…6105`), 3 000 passi, 25 run;
- una configurazione completa per run, con hash SHA-256;
- i parametri del rilevatore e la lista delle metriche;
- la regola di decisione e il controllo sui negativi;
- versione del codice e commit al momento della registrazione.

L'esecutore verifica ogni configurazione contro l'hash del manifest e rifiuta le
differenze. Nessuna configurazione è stata modificata dopo la registrazione.

**Deviazione dichiarata.** Il manifest registra il commit `96bb8dc`; i run sono
partiti da `aac9562`, perché tra registrazione ed esecuzione è stato aggiunto il
livello di persistenza dell'analisi (`analysis.py`, serializzazione di tracker e
rilevatore, CLI). Nessun modulo della simulazione è cambiato: il controllo
automatico lo conferma (`simulation_unchanged: true`, `analysis_changed: true`).
La verifica è stata ripetuta in un worktree al commit preregistrato, sulle stesse
configurazioni e senza tracking:

| Run | Hash del mondo al commit registrato | Uguale al run della campagna |
|---|---|---|
| `closed-6101` | `feb49be3…` | sì |
| `unfed-6101` | `34dc7c81…` | sì |
| `fed-mid-6101` | `07fe1ad2…` | sì |

Dettaglio in `campaigns/m6/deviations.json`.

## 3. Design sperimentale

Stessa chimica in tutte le condizioni; cambiano solo sorgenti, costi e
decadimento.

| Condizione | Sorgenti | Costi e decadimento | Energia |
|---|---|---|---|
| `closed` | no | no | conservata |
| `unfed` | no | sì | decrescente |
| `fed-low` | 9 × 1 quanto/passo | sì | flusso basso |
| `fed-mid` | 9 × 2 quanti/passo | sì | flusso medio |
| `fed-high` | 9 × 4 quanti/passo | sì | flusso alto |

Il confronto è a tre punti: `closed` vs `unfed` isola i costi; `unfed` vs
`fed-*` isola il flusso. La differenza fra `closed` e `fed` non è attribuibile a
una sola variabile: nel report non viene attribuita.

## 4. Stato di analisi ripristinabile

Tracker e rilevatore hanno uno stato che influisce sui risultati. Ora è salvato
in `analysis.json` accanto al checkpoint e ripristinato dalla ripresa:

- strutture attive, contatori, vite concluse, firme viste;
- candidati, verifiche di persistenza pendenti, generazioni;
- passo di riferimento, per rifiutare un ripristino incoerente.

La ripresa con analisi riproduce esattamente il run continuo: stesso hash del
mondo, stesso riepilogo del tracker, stesso riepilogo del rilevatore
(`tests/test_analysis.py`). È la condizione tecnica perché una campagna possa
fermarsi e riprendere senza inventare eventi.

## 5. Risultati

| Condizione | Run | `replication` | Copie persistenti (mediana) | Gen. max | Strutture (mediana) | Vita media (mediana) | Passi ambigui (mediana) |
|---|---|---|---|---|---|---|---|
| `closed` | 5 | 0 | 0 | 0 | **284** | 271,2 | 2 849 |
| `unfed` | 5 | 0 | 0 | 0 | 129 | 429,9 | 948 |
| `fed-low` | 5 | 0 | 0 | 0 | 156 | 427,3 | 1 301 |
| `fed-mid` | 5 | 0 | 0 | 0 | 150 | 425,3 | 1 286 |
| `fed-high` | 5 | 0 | 0 | 0 | 150 | 425,3 | 1 144 |

Nessun run ha prodotto una copia candidata: 0 su 25, in tutte le condizioni.

Energia: identità esatta in ogni run (`identity_delta = 0`). Le condizioni
alimentate accumulano energia non assorbita crescente con il tasso:

| Condizione | Iniettata (mediana) | Dissipata (mediana) | Non assorbita (mediana) |
|---|---|---|---|
| `unfed` | 0 | 9 785 | 0 |
| `fed-low` | 27 000 | 10 072 | 15 677 |
| `fed-mid` | 54 000 | 10 182 | 38 680 |
| `fed-high` | 108 000 | 10 021 | 83 992 |

## 6. Osservazioni

Solo misure, senza spiegazioni.

1. **Zero copie candidate** in 25 run, con il criterio preregistrato
   (assemblaggio simultaneo ≥ 4 particelle, entro 2 celle, persistenza ≥ 10
   passi, catena persistente).
2. **Strutture**: 284 mediane nel chiuso, 122–160 nelle condizioni aperte.
3. **Nascite** simili in tutte le condizioni (885–1 088); le strutture attive sono
   però più numerose nel chiuso (284) che nelle aperte (122–160).
4. **Vita media** delle strutture: 271 passi nel chiuso, 420–445 nelle aperte.
5. **Ambiguità** (collisioni di impronta): 2 849 passi mediani nel chiuso,
   948–1 301 nelle aperte.
6. **Saturazione**: quadruplicare il tasso delle sorgenti (1 → 4) non aumenta le
   strutture (156 → 150 → 150) e quadruplica l'energia non assorbita.
7. **Identità energetica** esatta in tutte le condizioni.

## 7. Ipotesi

Spiegazioni possibili, **non dimostrate** da questa campagna.

- **La soglia del rilevatore.** Lo zero può riflettere il fatto che il criterio
  richiede l'assemblaggio simultaneo di una struttura completa accanto a una
  simile. Un replicatore per accrezione non verrebbe visto, come già dichiarato
  in M5. Lo zero non è la prova che nell'universo non avvenga nulla.
- **Il costo dei legami.** Il chiuso ha più strutture (284 contro 150) e costi
  nulli. È compatibile con l'idea che nel chiuso ogni legame sia "gratis", non
  con una maggiore tendenza alla vita.
- **L'accesso alle sorgenti.** La saturazione con il tasso suggerisce che il
  collo di bottiglia sia spaziale (le particelle legate non raggiungono le
  sorgenti), coerente con il limite dichiarato in M3. Non è una spiegazione
  esclusiva: la stessa curva sarebbe compatibile con altri vincoli.
- **Le vite più lunghe nelle condizioni aperte** potrebbero dipendere dal
  rapporto fra formazione e rottura, non da una regolazione interna.

Nessuna di queste ipotesi è un risultato. Per discriminarle servono esperimenti
dedicati (M7 e oltre), non run più lunghi con gli stessi parametri.

## 8. Decisione preregistrata

| Regola | Esito |
|---|---|
| Condizione candidata: ≥ 3/5 seed `replication` e mediana copie persistenti ≥ 5 | nessuna condizione |
| Controllo: `closed`/`unfed` non devono essere `replication` | rispettato |
| Verdetto | **`no_evidence`** |

Come previsto dal protocollo del docx: nessun candidato → risultato negativo
pubblicato, nessun passaggio a S7. Un run più lungo non è la risposta; prima
vanno riviste ipotesi e spazio dei parametri.

## 9. Riproducibilità

```bash
.venv/bin/python tools/preregister_m6.py   # rifiuta se il manifest esiste
.venv/bin/python tools/run_campaign.py     # salta i run già completati
.venv/bin/python tools/run_campaign.py --force  # riesegue tutto
```

- Ogni configurazione è verificata contro l'hash del manifest.
- `results.json` contiene tutti i 25 run, inclusi quelli nulli.
- I run sono deterministici: stesso seed e configurazione ⇒ stesso
  `state_hash_full`.
- Il codice della simulazione è identico a quello preregistrato (verifica
  automatica più worktree su tre seed).

## 10. Limiti

1. **Cinque seed per condizione**: descrittivo, non inferenziale. Le mediane non
   hanno intervalli di confidenza.
2. **Una sola famiglia di parametri**: varia solo il tasso delle sorgenti; la
   chimica è fissa.
3. **3 000 passi**: le vite oltre i 3 000 passi non sono osservabili.
4. **Il rilevatore misura l'assemblaggio template-diretto**, non la replicazione
   in generale (limite di M5, invariato).
5. **Confondimento parziale**: `closed` vs `fed` cambia sia i costi sia il flusso;
   solo `unfed` vs `fed` isola il flusso.
6. **La deviazione di codice** è dichiarata e verificata, ma resta una deviazione.

## 11. Verdetti

**M6: GO.** La campagna è stata eseguita come preregistrata, con stato di
analisi ripristinabile, tutti i run registrati e nessun risultato omesso. Il
protocollo è riproducibile.

**Passaggio a S7: REVISE.** Nessun candidato replicante. Il risultato negativo è
il risultato: le condizioni testate non producono copie persistenti secondo il
criterio preregistrato. Prima di S7 vanno riviste le ipotesi e lo spazio dei
parametri — non semplicemente aumentata la durata dei run.
