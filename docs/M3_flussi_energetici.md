# M3 — Flussi energetici, dissipazione e costi delle reazioni

Specifica tecnica (bozza di progetto, **non implementata**) · 2026-11-15

Obiettivo: aprire il sistema (sorgenti, pozzi, dissipazione, costi di movimento e
di reazione) mantenendo la proprietà che rende utili i risultati: **la stessa
configurazione e lo stesso seed producono la stessa storia, al bit, nello stesso
ambiente software**.

Il principio guida è che la riproducibilità non è "ottenere lo stesso numero
finale", ma **fissare in anticipo ogni decisione**: quante estrazioni casuali,
in quale ordine, su quale stato, con quale aritmetica. Tutto il resto segue.

---

## 1. Estensione contabile

Oggi `E(t) = Σ energia_particelle + Σ energia_legami` ed è costante. In M3 il
sistema è aperto, quindi l'energia **non** si conserva: si conserva l'**identità
contabile**

```
E_int(t) = E_int(0) + I(t) − D(t)
```

con

| Simbolo | Significato | Tipo |
|---|---|---|
| `E_int` | energia interna: particelle + legami | intero |
| `I` | energia iniettata cumulativa dalle sorgenti | intero ≥ 0, monotono |
| `D` | energia dissipata cumulativa (pozzi + costi non immagazzinati) | intero ≥ 0, monotono |

`I` e `D` sono **stato**, non statistiche: vanno salvati, hashati e verificati a
ogni passo. Un test di bilancio che ammetta tolleranza in virgola mobile è un
test che non verifica nulla.

Tre bucket distinti, per non confondere cause diverse:

1. `injected` — energia entrata dalle sorgenti;
2. `dissipated` — energia uscita per dissipazione e costi non immagazzinati;
3. `unabsorbed` — energia emessa da una sorgente che non ha trovato destinatario
   (va contata come dissipata, altrimenti la sorgente è una macchina che crea
   energia quando il bersaglio è occupato).

---

## 2. Regole energetiche

### 2.1 Sorgenti

Una sorgente è un punto localizzato con un tasso razionale e una capacità.

```json
{ "x": 64, "y": 64, "rate_num": 1, "rate_den": 4, "capacity": 50, "overflow": "discard" }
```

- Emissione con **accumulatore intero**, non con probabilità per passo:

  ```
  acc += rate_num
  quanti = acc // rate_den
  acc %= rate_den
  ```

  Zero drift, zero float, nessuna estrazione casuale. `acc` è stato e va
  serializzato.

- Destinazione **deterministica**: la particella nella cella della sorgente.
  Se la cella è vuota o la particella ha già raggiunto `capacity`, i quanti
  vanno in `unabsorbed` (contati come dissipati). Nessuna scelta casuale,
  nessuna ambiguità.
- Emissione solo ai passi previsti (`step % period == 0`), mai su tempo reale.

Alternative scartate: sorgenti "poissoniane" (numero variabile di estrazioni,
difficili da verificare) e sorgenti che scelgono una particella a caso nel
raggio (una decisione in più da ordinare e documentare, senza guadagno
scientifico in M3).

### 2.2 Dissipazione

- **Particelle**: `e -= (e * decay_num) // decay_den`, tutto intero.
- **Legami**: `bond_energy -= (bond_energy * bond_decay_num) // bond_decay_den`.
- Ogni quanto rimosso va in `D`. Mai ricalcolare l'energia per differenza:
  sottrarre e contabilizzare nello stesso punto del codice.

La dissipazione è ciò che rende il sistema lontano dall'equilibrio: se tutte le
sorgenti sono attive ma `D = 0`, il modello non è aperto, è solo gonfiato.

### 2.3 Costi

| Azione | Costo | Dove va |
|---|---|---|
| Movimento accettato | `movement_cost` dalla particella | `dissipated` |
| Formazione di un legame | `bond_cost` per particella, immagazzinato | nel legame |
| Formazione: quota di attrito | `formation_dissipation` per particella | `dissipated` |
| Rottura | `breaking_dissipation` sottratta all'energia restituita | `dissipated` |

Regola: **si paga solo ciò che accade**. Una mossa rifiutata dalla risoluzione
dei conflitti non costa; una mossa accettata sì. La proposta resta soggetta a
`energia ≥ movement_cost`, verificata prima di proporre, così il costo non
cambia la statistica dei conflitti.

La catalisi resta **solo cinetica** (fattore sulla probabilità), senza ruolo
energetico: mescolare i due piani renderebbe impossibile attribuire un effetto.

---

## 3. Le dieci regole di riproducibilità

Da trattare come requisiti di accettazione, non come consigli.

**R1 — Interi ovunque.** Ogni quantità energetica è intera. Le probabilità sono
float solo in configurazione e vengono convertite una volta in soglie intere
`⌊p·2⁶⁴⌋`. Nessun confronto in virgola mobile nel percorso caldo.

**R2 — Budget di estrazioni esplicito e costante rispetto allo schema.** Ogni
fase dichiara quante estrazioni consuma e in quale ordine:

```
estrazioni(passo) = 2·N + |legami| + |coppie candidate| + |eventi stocastici|
```

con `N` particelle. Gli accumulatori interi (sorgenti, dissipazione
deterministica) **non** consumano estrazioni. Il valore teorico è confrontato in
un test con il contatore reale (`draws_consumed`, attivo solo in debug).

**R3 — Ordine canonico per ID, non per indice.** Finché non esiste la morte,
indice e ID coincidono. Appena M3 compatta gli array, l'indice non è più
canonico: **tutte** le iterazioni con effetti casuali o contabili vanno ordinate
per ID. Un `for index in range(len(store))` dopo una compattazione è un bug di
riproducibilità, non di stile.

**R4 — Mai iterare su `dict`/`set` senza ordinare.** Vale per legami, sorgenti,
eventi. L'ordine di inserimento non è un contratto; `PYTHONHASHSEED` non deve
poter influenzare nulla.

**R5 — Nessuna sorgente di non determinismo.** Niente `time`, `datetime`,
`random`, `secrets`, `os.urandom`, variabili d'ambiente o affinità di CPU nel
core. Un test statico verifica che i moduli del core non importino queste
librerie (le eccezioni sono `metrics` e `events`, che non influenzano lo stato).

**R6 — Ordine delle fasi fissato**, e un cambio di ordine è un cambio di
schema, non un refactoring:

```
dissipazione → iniezione → rottura → movimento → risoluzione → formazione
```

La dissipazione prima dell'iniezione evita che l'energia appena immessa venga
tassata nello stesso passo; è una scelta arbitraria ma **fissata**.

**R7 — Nessun riscalamento, nessun clamp silenzioso.** Mai rinormalizzare
l'energia per evitare overflow o per "stabilizzare" la dinamica: altera il
bilancio e rende incomparabili i run. I valori sono limitati dalla fisica del
modello (energia iniziale + iniezione); un superamento è un errore da segnalare.
In Python gli interi sono a precisione arbitraria; il file resta leggibile.

**R8 — L'hash copre tutto ciò che conta.** `state_hash_full` include, oltre a
identità, posizioni, specie, energia e legami: `injected`, `dissipated`,
`unabsorbed`, gli accumulatori delle sorgenti e `next_id`. Due stati con la
stessa disposizione di particelle ma storia energetica diversa devono avere hash
diversi.

**R9 — Migrazione senza cambiare il passato.** Gli schemi 1 e 2 restano
leggibili. Una configurazione M2 caricata dal codice M3, con il blocco `energy`
assente o a costo zero, deve evolvere **esattamente** come prima: lo verificano
i golden hash M1 (`3f4a885a…`) e M2 (`a38a6acf…`).

**R10 — Il checkpoint è sufficiente.** Chi riprende non deve ricostruire nulla:
RNG, passo, ledger, accumulatori, contatori e `next_id` sono nel file; il
caricamento ricalcola gli hash e verifica il bilancio.

---

## 4. Formato: configurazione e checkpoint

### 4.1 Configurazione (schema 3)

Blocco nuovo, opzionale; se assente, comportamento M2 identico.

```json
"energy": {
  "movement_cost": 0,
  "formation_dissipation": 0,
  "breaking_dissipation": 0,
  "particle_decay": { "num": 0, "den": 1 },
  "bond_decay":    { "num": 0, "den": 1 },
  "sources": [
    { "x": 64, "y": 64, "rate_num": 1, "rate_den": 4,
      "capacity": 50, "overflow": "discard" }
  ]
}
```

Validazione: denominatori > 0, costi ≥ 0, sorgenti dentro la griglia e su celle
distinte, `capacity ≥ 0`, `overflow ∈ {discard}`. L'hash canonico include il
blocco; le configurazioni schema 1 e 2 mantengono hash e semantica.

### 4.2 Checkpoint (schema 3)

Campi aggiunti a quelli dello schema 2:

```json
"ledger": { "injected": 0, "dissipated": 0, "unabsorbed": 0 },
"sources": [ { "acc": 0 } ],
"draws_consumed": 0
```

`acc` per sorgente, nell'ordine canonico della configurazione (che è ordinato e
hashata: nessuna ambiguità).

---

## 5. Test di accettazione

| ID | Verifica |
|---|---|
| E1 | `E_int(t) = E_int(0) + I(t) − D(t)` esatto a ogni passo, su run con sorgenti, dissipazione e costi |
| E2 | Con sorgenti a tasso `1/4` per 10 000 passi: `I = 2500`, nessun drift dell'accumulatore |
| E3 | Costo di movimento: mossa accettata ⇒ energia scalata e `D` aumentato; mossa rifiutata ⇒ nessun costo |
| E4 | Costi di formazione/rottura: `D` aumenta esattamente della quota di attrito |
| E5 | Golden hash M1 e M2 riprodotti con il codice M3 e blocco `energy` disattivato |
| E6 | Ripresa continua ≡ interrotta con ledger e accumulatori |
| E7 | Corruzione di `injected`/`dissipated`/accumulatore rilevata dal caricamento |
| E8 | Budget di estrazioni: contatore reale = formula attesa, per 1 000 passi |
| E9 | Test statico: il core non importa `time`, `random`, `secrets`, `os.urandom` |
| E10 | Due esecuzioni con la stessa config e seed: `state_hash_full` e ledger identici |

---

## 6. Cosa resta fuori (e perché)

- **Temperatura e termostati** che riscalano l'energia: rompono il ledger.
- **Dissipazione proporzionale a numeri reali** o a costanti fisiche non intere.
- **Sorgenti che scelgono casualmente il destinatario**: aggiungono una
  decisione da ordinare senza un guadagno scientifico misurabile.
- **Parallelismo**: con un solo flusso RNG sequenziale è impossibile. Se M9 lo
  richiederà, servirà un RNG counter-based con chiave `(passo, id)` e un test di
  equivalenza seriale/parallelo. Non è un dettaglio implementativo: è un cambio
  di modello di casualità.
- **Morte e nascita delle particelle**: richiedono una politica di rilascio
  degli ID e la compattazione degli array (vedi R3). Rinviate a M3-bis o M4.

---

## 7. Ordine di implementazione consigliato

1. `energy` block in configurazione + validazione + hash (schema 3, retrocompatibile).
2. Ledger nello stato, nell'hash completo e nel checkpoint; test E1, E5, E10.
3. Dissipazione intera di particelle e legami; test E1, E4.
4. Costo di movimento; test E3.
5. Sorgenti con accumulatore; test E2, E7.
6. Contatore delle estrazioni in debug; test E8, E9.
7. Run di confronto chiuso / aperto / senza alimentazione (il gate del docx S3).

Nessun punto richiede di cambiare le regole di M2: si aggiungono termini, non si
riscrive la dinamica. Questa è la condizione perché i risultati M2 restino
confrontabili.
