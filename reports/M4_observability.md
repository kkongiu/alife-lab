# M4 — Report: osservabilità, firme canoniche e persistenza

Data: 2026-11-15 · Milestone: M4 · Specifica: `SPEC.md` §17 · Cronologia: `git log`

## 1. Sommario

| Milestone | Esito | Evidenza |
|---|---|---|
| M1–M3 | GO (approvati) | golden hash e ripresa verificati anche con il livello di osservabilità |
| **M4** | **GO** | 156 test; 29 requisiti con evidenza misurata; firme esatte per gli alberi; ambiguità dichiarata per i cicli; 10 000 passi tracciati senza alterare il mondo |

Il gate del docx S4 — *riconosce esempi sintetici noti e segnala l'incertezza dove
una copia è ambigua* — è soddisfatto in entrambe le parti: le fixture sintetiche
sono riconosciute con firme esatte, e l'ambiguità è contata, non nascosta.

## 2. Perimetro

Implementato: componenti connesse, firma canonica (esatta per alberi, impronta per
cicli), tracciamento per identità con sette tipi di evento, metriche di
persistenza, ambiguità dichiarata, file `structures.jsonl` e `lineage.jsonl`,
integrazione CLI `--track`.

Non implementato, per contratto: controlli positivi e negativi (M5), campagna
multi-seed (M6), replicazione, ereditarietà. Nessun visualizzatore: scelta
esplicita per non accoppiare motore e interfaccia.

**Cosa M4 non fa.** Non dichiara che due strutture sono la stessa cosa perché
condividono una firma. Il tracciamento usa l'identità delle particelle; la firma
serve a descrivere e confrontare. Una struttura che nasce indipendentemente con
una firma già vista è una **ricorrenza di forma**, non una discendenza.

## 3. Firme: garanzie e limiti

| Caso | Firma | Garanzia |
|---|---|---|
| Albero (`legami = particelle − 1`) | `T:…` codice AHU su tutte le radici | uguale **se e solo se** isomorfe |
| Grafo con cicli | `F:…` impronta Weisfeiler-Lehman | invariante, **non completa** |

La firma non usa identificativi, posizioni o orientamenti; include composizione
per specie, dimensione e topologia. Non esiste alcuna nozione di genoma o
sequenza.

Ambiguità operativa: due strutture con la stessa chiave `T:` sono lo stesso tipo
(nessuna incertezza); due con la stessa chiave `F:` non sono dimostrabilmente
uguali e vengono contate come ambigue.

## 4. Run tracciato (10 000 passi, baseline M3 alimentata)

| Metrica | Valore |
|---|---|
| Strutture attive al passo 10 000 | 65 |
| Linee (identità) create | 2 323 |
| Nascite / morti | 1 472 / 1 494 |
| Crescite / riduzioni | 2 042 / 1 825 |
| Scissioni / fusioni | 934 / 382 |
| Trasformazioni | 290 |
| Persistenze (struttura × passo) | 1 224 698 |
| Osservazioni esatte / impronte | 1 213 890 / 17 753 (1,4% impronte) |
| Firme distinte | 131 |
| Passi con ambiguità | 3 208 (32%) |
| Strutture ambigue osservate | 11 216 |
| Dimensione massima corrente | 6 |

Esempi reali dal registro:

```json
{"kind": "birth",  "step": 1,   "structure": 0,  "size": 2, "signature": "T:(S0:(S0:))"}
{"kind": "growth", "step": 7,   "structure": 0,  "size": 3, "signature": "T:(S0:(S0:(S0:)))"}
{"kind": "merge",  "step": 15,  "structure": 68, "parents": [40, 51], "size": 4}
{"kind": "split",  "step": 95,  "structure": 259, "parents": [0], "size": 2}
{"kind": "transform", "step": 115, "structure": 99, "size": 4, "exact": false}
```

L'ultimo è il caso interessante: una struttura resta 1:1 ma cambia topologia
(da albero a ciclo). La firma passa da esatta a impronta e il tracker lo registra
come trasformazione, non come nuova struttura.

## 5. Persistenza

2 723 identità concluse, vita media **441,8 passi**, massima **5 968**.

| Vita (passi) | ≤1 | ≤2 | ≤5 | ≤10 | ≤20 | ≤50 | ≤100 | ≤200 | ≤500 | ≤1 000 | ≤2 000 | ≤5 000 | ≤10 000 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Strutture | 55 | 49 | 101 | 187 | 212 | 310 | 220 | 289 | 496 | 421 | 299 | 83 | 1 |

La coda lunga è coerente con la probabilità di rottura (`0,002` per passo): la
vita media attesa di un legame è ~500 passi e le strutture piccole durano quanto
il loro legame più debole. Non c'è nulla di emergente in questo: è la statistica
del decadimento.

## 6. Ambiguità misurata

- 131 firme distinte su 2 323 linee: le forme si ripetono molto più delle
  identità. È il dato che M5 dovrà distinguere da una vera copia.
- Il 32% dei passi contiene almeno una collisione di impronta; in quei passi la
  firma non basta a dire "stessa struttura". Il tracker non decide: conta.
- Le strutture ambigue osservate sono 11 216 su ~1,23 milioni di osservazioni
  (0,9%), tutte su cicli.

## 7. Fixture sintetiche (gate)

| Struttura | Atteso | Esito |
|---|---|---|
| Catena `S0-S0-S1` vs stessa catena rietichettata | stessa firma | ✅ |
| Catena `S0-S0-S1` vs `S0-S1-S1` | firme diverse | ✅ |
| Catena `S0-S1-S0-S0` vs stella `S1(S0)₃` | stessa composizione, firme diverse | ✅ |
| Anello a 4 | impronta, non firma esatta | ✅ |
| Due anelli identici | ambiguità dichiarata | ✅ |
| Due dimeri identici | stessa firma esatta, nessuna ambiguità | ✅ |

Ogni riga corrisponde a un test con asserzione esplicita
(`tests/test_structures.py`); le evidenze sono in `reports/tests/evidence/M4-*`.

## 8. L'osservatore non altera il mondo

Il run tracciato produce **lo stesso hash completo** del run non tracciato già in
`runs/m3_baseline`:

```
3e6aae8ee88f5b5ac775faccec043886a5214d16f5a33ebf125217632a39dcd8
```

Il tracker non consuma RNG e non modifica lo stato. Il costo è però reale e va
riportato con il contesto della misura:

| Misura | Senza tracking | Con tracking | Variazione |
|---|---|---|---|
| Run end-to-end, 10 000 passi | 216,5 passi/s | 119,1 passi/s | −45% |
| Benchmark in-process, 300 passi (mediana di 3) | 256,4 passi/s | 96,0 passi/s | −63% |

La differenza fra le due righe è il contesto: il run end-to-end include startup e
I/O e si misura su 10 000 passi; il benchmark misura 300 passi con il mondo già
maturo, dove ci sono più strutture da firmare per passo. Componenti e firme sono
il collo di bottiglia; dati grezzi in `reports/benchmark.json` (caso
`m4 tracking`).

## 9. Test

156 test; 29 requisiti con un file di evidenza misurato (8 M1, 7 M2, 8 M3, 6 M4).
Ogni caso ha il proprio file in `reports/tests/cases/`; indice in
`reports/tests/index.md`.

## 10. Decisioni progettuali

| # | Decisione | Motivazione |
|---|---|---|
| D27 | Firma esatta solo per alberi, impronta dichiarata per i cicli | un test di isomorfismo esatto su grafi arbitrari è costoso; l'ambiguità è preferibile a una falsa certezza |
| D28 | Tracciamento per identità, non per firma | evita di chiamare "discendenza" una somiglianza strutturale |
| D29 | Ambiguità = collisione di impronta, non di firma esatta | per gli alberi l'uguaglianza è una prova; per i cicli no |
| D30 | Eventi di struttura separati dal registro dei legami | due livelli di descrizione: materia e forma |
| D31 | Tracker non serializzato | è analisi, non stato; la ripresa riparte dal mondo |
| D32 | Ereditarietà di linea nelle scissioni al figlio più grande | regola deterministica e dichiarata, non una tesi biologica |

## 11. Limiti e problemi aperti

1. **Solo alberi esatti.** I cicli usano un'impronta; collisioni possibili.
2. **Nessuna sequenza.** Non c'è nulla da allineare: la similarità è strutturale.
3. **Linee dopo split/merge** seguono una regola di attribuzione, non una
   discendenza verificata.
4. **Costo dell'osservazione** −45% (end-to-end) / −63% (benchmark a passi
   maturi); accettabile per l'analisi, da ottimizzare se M6 richiederà campagne
   lunghe.
5. **Tracker non ripristinabile**: una ripresa con `--track` ricomincia il
   tracciamento.
6. **Nessun visualizzatore**: scelta esplicita, componente separata.

## 12. Verdetti

**M4: GO.** Le firme sono corrette e verificate su fixture note; l'ambiguità è
misurata e dichiarata; il tracciamento non perturba la simulazione e produce un
registro completo di nascite, crescite, scissioni, fusioni, trasformazioni e
morti. Il risultato utile per M5 è un numero: **2 323 linee per 131 firme**, cioè
molte più identità che forme — il punto di partenza per distinguere una
ricorrenza da una copia.

**M5 non è stata iniziata.** Controlli positivi e negativi richiedono
approvazione esplicita.
