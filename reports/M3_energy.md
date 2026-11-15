# M3 — Report: flussi energetici, dissipazione e costi

Data: 2026-11-15 · Milestone: M3 · Specifica: `SPEC.md` (v3) · Cronologia: `git log`

## 1. Sommario

| Milestone | Esito | Evidenza |
|---|---|---|
| M1 | GO (approvato) | golden hash riprodotto dal codice M3 |
| M2 | GO (approvato) | golden hash completo riprodotto dal codice M3 |
| **M3** | **GO** | 139 test; 23 requisiti con evidenza misurata; identità energetica esatta su 10 000 passi; strutture persistenti con alimentazione, collasso senza; determinismo, ripresa e migrazione verificati |

Il gate del docx S3 — *ogni trasformazione ha un costo o un trasferimento
coerente e i controlli si comportano in modo plausibile* — è soddisfatto dai
numeri del §4: non dalla presenza di strutture, ma dalla loro risposta al flusso.

## 2. Perimetro

Implementato: sorgenti localizzate con serbatoio e accumulatore interi,
dissipazione di particelle e legami, costo di movimento, costi di formazione e
rottura, ledger (`injected`, `dissipated`, `unabsorbed`), schema di
configurazione e checkpoint 3, migrazione da 1 e 2, metriche e invarianti nuovi.

Non implementato, per contratto: rilevamento delle strutture (M4), controlli
positivi (M5), replicazione, ereditarietà, morte e nascita delle particelle,
parallelismo.

## 3. Regole effettive

| Elemento | Regola |
|---|---|
| Dissipazione | `num` quanti ogni `den` passi, sfasati per ID: `(step + id) mod den < num`; legami con chiave `(step + id_a + id_b)` |
| Sorgente | accumulatore `acc += rate_num`, emissione `acc // rate_den`; serbatoio locale di capacità `capacity`; trabocco in `unabsorbed` |
| Raccolta | la particella sulla cella assorbe l'intero serbatoio; nessuna scelta casuale |
| Movimento | `movement_cost` pagato solo dalle mosse accettate |
| Formazione | `bond_cost` immagazzinato + `formation_dissipation` dissipata per particella |
| Rottura | `breaking_dissipation` sottratta al restituito (limitata all'energia del legame) |
| Ordine | dissipazione → iniezione → rottura → movimento → risoluzione → formazione |

Una deviazione rispetto alla bozza iniziale è stata necessaria ed è documentata:
il decadimento proporzionale intero `(E·num)//den` si annulla per arrotondamento
alle energie tipiche (10–30 quanti) e rendeva la dissipazione inerte. Il tasso
assoluto sfasato è esatto, non richiede stato aggiuntivo e non consuma estrazioni.

## 4. Le tre condizioni

Tutte con 128×128, 4 specie, 1400 particelle, 10 000 passi.

| Condizione | Energia finale | Legami | Aggregati | Max | Formazioni / rotture |
|---|---|---|---|---|---|
| **Chiuso** (M2: nessun costo, nessun flusso) | 16 100 costante | 686 | 284 | 14 | 13 746 / 13 060 |
| **Alimentato** (9 sorgenti, dissipazione, costi) | 84 272 | **116** | 65 | 6 | 4 176 / 4 060 |
| **Senza alimentazione** (solo dissipazione e costi) | 2 471 | **0** | 0 | 0 | 2 633 / 2 633 |

### 4.1 Traiettorie

| Passo | 2 000 | 4 000 | 6 000 | 8 000 | 10 000 |
|---|---|---|---|---|---|
| Alimentato: legami | 330 | 99 | 101 | 119 | 116 |
| Alimentato: energia | 17 797 | 29 780 | 47 396 | 64 369 | 84 272 |
| Senza alimentazione: legami | 326 | 63 | 5 | 1 | 0 |
| Senza alimentazione: energia | 7 894 | 4 988 | 3 734 | 3 016 | 2 471 |

La differenza è qualitativa: **con il flusso il sistema mantiene una popolazione
persistente di legami** (90–130 dal passo 4 000 in poi), **senza il flusso
collassa a zero** entro il passo 8 000. Non è una differenza di parametri: è la
stessa configurazione con `sources: []`.

## 5. Interpretazione: il flusso non ripristina M2

Il risultato più importante è negativo e va detto chiaramente.

1. **Le strutture alimentate sono meno numerose di quelle chiuse** (116 contro
   686). In M2 un legame non costa nulla: si forma pagando `bond_cost` e alla
   rottura l'energia torna. In M3 ogni ciclo di legame perde
   `2·formation_dissipation + breaking_dissipation` quanti. I costi riducono
   l'occupazione di legami di un fattore ~6.
2. **La sorgente è un collo di bottiglia spaziale.** Le particelle legate sono
   immobili e non possono visitare le sorgenti: si legano, esauriscono l'energia
   e muoiono come struttura. Solo le particelle libere si ricaricano, e lo fanno
   in pochi punti. È il limite già dichiarato in M2 (nessun moto rigido) che
   diventa, in M3, il fattore limitante.
3. **Metà dell'energia iniettata è sprecata**: 92 998 quanti su 180 000 finiscono
   in `unabsorbed` perché il serbatoio trabocca prima che una particella passi.
   Il sistema è aperto, ma inefficiente.
4. **L'energia si accumula** (da 16 100 a 84 272) invece di stabilizzarsi: i
   serbatoi traboccano e le particelle fortunate diventano molto ricche. Non è
   un equilibrio termodinamico: è una disuguaglianza di accesso.

Nessuna di queste osservazioni è presentata come proprietà emergente. Sono
proprietà del modello, misurate, e indicano dove intervenire in M4: moto degli
aggregati, distribuzione delle sorgenti, oppure costi più bassi. Non è corretto
"aggiustare" i parametri per far comparire più strutture.

## 6. Verifiche

| Verifica | Esito |
|---|---|
| Identità `E = E₀ + I − D − U` a ogni passo | esatta (`identity_delta = 0`) su tutte le condizioni |
| Sorgente `1/4` per 1 000 passi | 250 quanti, nessun drift dell'accumulatore |
| Serbatoio | capacità rispettata, trabocco contabilizzato |
| Costo di movimento | 10 mosse ⇒ 10 quanti, solo sulle mosse accettate |
| Costi di reazione | attrito di formazione 2 per legame, di rottura 1 |
| Decadimento | 1 quanto ogni 3 passi ⇒ 3 quanti in 9 passi |
| Determinismo | due run con lo stesso seed: hash completo, ledger ed estrazioni identici |
| Budget RNG | invariato (`N + 2·N·t` senza chimica); nessuna estrazione nelle sorgenti |
| Checkpoint | ledger, accumulatori, serbatoi e contatore RNG sopravvivono al roundtrip |
| Migrazione | schema 1 e 2 leggibili; golden hash M1 e M2 riprodotti |
| Core | nessun import di `time`, `random`, `secrets`, `os.urandom` |

## 7. Performance

| Condizione | Durata | Passi/s | Memoria (picco / simulazione) |
|---|---|---|---|
| Alimentato | 46.19 s | 216.5 | 43.0 MiB / 6.1 MiB |
| Senza alimentazione | 48.29 s | 207.1 | 43.0 MiB / 6.1 MiB |

Il costo dei flussi è marginale: due confronti interi per particella e per legame
a ogni passo, più la scansione delle sorgenti. La variabilità della macchina
(±10%) è maggiore della differenza fra le due condizioni.

### 7.1 Benchmark a ripetizioni (3 run, mediana)

| Caso | Particelle | Passi | Passi/s | min–max |
|---|---|---|---|---|
| quick 32×32 (M1) | 90 | 1 000 | 4 328.4 | 3 624.8–4 443.1 |
| baseline 128×128 (M1) | 1 638 | 500 | 189.9 | 185.1–196.1 |
| M2 chimica 128×128 | 1 400 | 300 | 213.2 | 212.1–223.5 |
| **M3 flussi 128×128** | 1 400 | 300 | **188.4** | 187.5–203.5 |
| densità 2.5% | 410 | 500 | 875.6 | 858.0–892.9 |
| densità 25% | 4 096 | 200 | 53.3 | 53.2–57.5 |
| densità 50% | 8 192 | 100 | 6.5 | 6.5–6.8 |

M3 costa circa il 12% più di M2 nella stessa configurazione: dissipazione,
sorgenti e contabilità del ledger.

### 7.2 Equivalenza continuo ↔ ripreso

| Configurazione | Passi | Checkpoint | Hash | RNG | Mosse | Legami |
|---|---|---|---|---|---|---|
| M1 | 2 000 | 38 093 B | uguale | uguale | uguali | n/d |
| M2 | 400 | 4 226 B | uguale | uguale | uguali | uguali |
| M3 | 400 | 4 104 B | uguale | uguale | uguali | uguali |

I dati grezzi sono in `reports/benchmark.json` (`tools/benchmark.py --repeats 3`).

## 8. Test

```
139 passed in 11.7 s
```

23 requisiti hanno un file di evidenza con misure reali
(`reports/tests/evidence/`): 8 obbligatori M1, 7 M2, 8 M3. Ogni caso ha il
proprio file in `reports/tests/cases/`; indice in `reports/tests/index.md`.

## 9. Decisioni progettuali

| # | Decisione | Motivazione |
|---|---|---|
| D20 | Decadimento a tasso assoluto sfasato, non proporzionale | un tasso proporzionale intero si annulla alle energie del modello |
| D21 | Serbatoio locale per sorgente | un'emissione puntuale senza buffer è quasi tutta sprecata; il buffer è energia interna |
| D22 | Assorbimento immediato dell'intero serbatoio | nessuna scelta casuale, nessun parametro aggiuntivo |
| D23 | Ledger come stato, hashato | rende verificabile un sistema aperto; un ledger fuori hash è una statistica, non uno stato |
| D24 | Ordine dissipazione → iniezione → … | fissato: evita che l'energia appena immessa sia tassata nello stesso passo |
| D25 | Errori, non clamp | nessun riscalamento silenzioso: un valore fuori regola è un difetto |
| D26 | Costi solo sulle azioni accettate | il costo non altera la statistica dei conflitti |

## 10. Limiti e problemi aperti

1. **Le particelle legate restano immobili**: non possono ricaricarsi. È il
   limite che in M3 diventa dominante (§5.2). M4 dovrà decidere se e come gli
   aggregati si muovono.
2. **Sorgenti puntiformi**: l'accesso all'energia dipende dalla posizione. Una
   distribuzione più fine o un gradiente cambierebbero i risultati; sono
   esperimenti, non correzioni.
3. **Metà dell'input è sprecato**: capacità e frequenza dei passaggi sono da
   esplorare in una campagna parametrica, non da ottimizzare a occhio.
4. **L'energia si accumula**: manca un pozzo proporzionale all'energia (o un
   costo che cresca con essa). Il decadimento attuale è a tasso costante.
5. **Nessun decadimento delle particelle**: la materia resta costante.
6. **Nessun parallelismo** e riproducibilità cross-version non garantita.
7. **Il costo superlineare in densità** resta quello di M1.

## 11. Verdetti

**M3: GO — approvato il 2026-11-15.** Ogni trasformazione ha un costo o un
trasferimento coerente e il bilancio è verificabile con interi esatti; i controlli
(chiuso, alimentato, senza alimentazione) si comportano in modo plausibile e
distinguibile. Il risultato principale è negativo: il flusso mantiene strutture,
ma non ne produce di più che il sistema chiuso, e metà dell'energia è sprecata.
Questo è un risultato, non un difetto da nascondere.

**M4 non è stata iniziata.** Rilevamento e tracciamento delle strutture
richiedono approvazione esplicita.

---

## 12. Correzioni successive alla consegna

**Decadimento e priorità usavano l'indice invece dell'identificativo.** La
specifica richiede lo sfasamento sull'ID persistente:
`(step + id) mod den < num`, mentre il codice usava `(step + index)`. Lo stesso
problema era nella priorità dei conflitti, calcolata sull'indice.

Corretto:

- `World.dissipate()` usa `store.ids[index]`;
- `resolve_moves(..., identity=store.ids)` calcola la priorità sull'ID, con
  spareggio per ID;
- aggiunto l'invariante I17: gli array sono mantenuti in ordine crescente di ID,
  così l'ordine di iterazione resta canonico dopo una compattazione;
- tre test nuovi: decadimento con ID sparsi (`id=3`, nessun decadimento al passo
  0), priorità che segue l'identità anche quando l'ordine degli indici è diverso,
  identificativi fuori ordine rilevati da `validate()`.

**Impatto sui risultati: nessuno**, perché oggi ID e indice coincidono. Verificato
confrontando gli hash del run alimentato al passo 1 000:
`85610acb…d4918` (materiale) e `92357dc8…e868f` (completo) sono identici a quelli
registrati in `runs/m3_baseline/metrics.jsonl` prima della correzione. I golden
hash di M1 e M2 restano invariati.
