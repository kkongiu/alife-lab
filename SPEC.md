# SPEC — Modello computazionale (milestone M0, M1, M2, M3)

Versione: 3.0 (M3) · Data: 2026-11-15 · Riferimenti: `alife.md`, `Progetto_Vita_Artificiale_Roadmap_Milestone.docx`

Questa specifica descrive un universo deterministico, misurabile e — da M3 —
aperto: sorgenti, dissipazione e costi rendono il sistema lontano
dall'equilibrio. Deve essere sufficiente a reimplementare il motore senza
decisioni implicite. Ogni scelta non imposta dai documenti di progetto è marcata
come **decisione** ed è motivata.

---

## 1. Scopo e perimetro

Il sistema realizzato copre:

- **M1 — motore fisico locale**: particelle su griglia, movimento, conflitti,
  riproducibilità, checkpoint.
- **M2 — chimica artificiale**: legami reversibili fra particelle adiacenti, con
  costo energetico esplicito, soglie, decadimento e catalisi locale.
- **M3 — non-equilibrio**: sorgenti energetiche localizzate, dissipazione,
  costi di movimento e di reazione, con contabilità intera esatta.

Non esistono: organismi, genomi, DNA, replicatori, reti neurali, funzioni di
fitness, meccanismi di copia.

Da M3 l'energia **non** è costante: si conserva l'identità contabile
`E(t) = E(0) + iniettata − dissipata − non assorbita`. Le strutture che possono
comparire sono aggregati tenuti insieme da legami e alimentati da un flusso, non
organismi. Non c'è ancora ereditarietà, e nessun risultato di M3 autorizza a
parlarne.

---

## 2. Spazio, tempo, particelle

| Elemento | Definizione |
|---|---|
| Spazio | Griglia rettangolare `Lx × Ly`; baseline M1 e M2: `128 × 128 = 16 384` celle |
| Confini | `periodic` (toro, default) oppure `closed` (nessun attraversamento) |
| Occupazione | Al massimo **una** particella per cella |
| Tempo | Passi discreti |
| Particella | `(id, x, y, specie, energia)`; `id` persistente, mai riutilizzato |
| Specie | `move_probability ∈ [0,1]`, `energy ∈ ℕ`, `max_bonds ∈ [0,4]` |
| Legame | coppia non ordinata di particelle **adiacenti** con energia immagazzinata |
| Vicinato | von Neumann (4 celle ortogonali) |

Non esistono campi, forze a distanza o memoria delle particelle: l'unica
informazione disponibile è la propria specie e lo stato locale (occupazione,
specie ed energia dei vicini).

---

## 3. Rappresentazione dello stato

**Decisione.** Lo stato è composto da:

1. array paralleli `ids`, `xs`, `ys`, `species`, `energy`;
2. `degree[i]`: numero di legami della particella `i`;
3. `bonds`: dizionario `{(indice_a, indice_b): energia}` con `indice_a < indice_b`;
4. griglia piatta `grid`: cella → indice di particella, `-1` se vuota;
5. `step`, `moves_total`, contatori `bonds_formed_total`/`bonds_broken_total`,
   `next_id`;
6. stato completo del generatore casuale.

**Decisione: identificativi persistenti.** Gli ID sono assegnati in ordine
crescente alla creazione, salvati nel checkpoint, inclusi nell'hash completo e
**mai riutilizzati**. In M2 non esistono nascita né morte, quindi ID e indice
coincidono; il formato è però già quello necessario a M3, quando gli array
verranno compattati e gli indici non saranno più stabili. `next_id` è il primo
identificativo libero e un invariante verifica che ogni ID sia strettamente
minore.

**Decisione: due hash di stato.**

| Hash | Contenuto | Uso |
|---|---|---|
| `state_hash` | schema 1: posizioni e specie | confronto materiale, compatibilità con i risultati M1 |
| `state_hash_full` | schema 2/3: id, posizioni, specie, energia, legami; dallo schema 3 anche ledger, accumulatori e serbatoi | identità completa dello stato, verifica dei checkpoint |

Il mantenimento della definizione M1 permette di rieseguire una configurazione
M1 con il codice M2 e ottenere lo stesso hash pubblicato: la compatibilità è
verificata da un test (`test_v1_hash_is_unchanged`).

---

## 4. Modello temporale e movimento

Un passo `t → t+1` ha quattro fasi, tutte sullo stesso stato di partenza tranne
dove indicato.

### 4.1 Rottura dei legami (decadimento)

Per ogni legame, in ordine canonico `(id_a, id_b)`, si consuma un uint64. Se
`raw < ⌊break_probability · 2⁶⁴⌋` il legame si rompe: l'energia immagazzinata
torna alle due particelle (§5.3).

### 4.2 Proposta di movimento

Per ogni particella in ordine crescente di indice si consumano **esattamente due**
uint64 (decisione e direzione), indipendentemente dal fatto che la particella sia
libera o legata:

```
roll      = raw()
direction = raw() & 3
se degree > 0:                       # particella legata: immobile
    resta ferma
altrimenti se roll >= ⌊p·2⁶⁴⌋:
    resta ferma
altrimenti propone la cella vicina in direzione `direction`
```

`⌊p·2⁶⁴⌋` è intero: nessun confronto in virgola mobile nel percorso caldo.
`raw & 3` è uniforme perché `2⁶⁴` è divisibile per 4.

**Decisione: le particelle legate non si muovono.** Un aggregato è quindi
immobile finché i legami non si rompono; il moto rigido di un aggregato
richiederebbe la proposta coordinata di tutte le sue particelle e una risoluzione
di collisione a livello di componente. È un limite dichiarato (§15), non una
svista: mantiene il passo semplice e verificabile.

**Confini:** `periodic` usa il modulo; `closed` annulla la mossa che uscirebbe
dalla griglia (nessun rimbalzo, nessuna direzione privilegiata).

### 4.3 Risoluzione dei conflitti

Proposte simultanee, priorità

```
priority(i, t) = splitmix64( (i+1)·0x9E3779B97F4A7C15  XOR  (t+1)·0xD6E8FEB86659FD93 )
```

calcolata senza RNG. Le mosse sono accettate in ordine di priorità decrescente;
una mossa è accettata se la cella bersaglio è vuota o sarà liberata da una mossa
già accettata, e se nessun'altra mossa accettata punta alla stessa cella. Le
rotazioni chiuse (scambi e cicli) sono rilevate e accettate come gruppo.
L'applicazione è simultanea: prima si svuotano tutte le celle di partenza, poi si
scrivono tutte le destinazioni.

Proprietà: destinazioni distinte, indipendenza dall'ordine di inserimento,
nessuna particella fuori griglia. L'algoritmo è invariato rispetto a M1: pseudo-
codice completo nella versione M1 di questo documento (cronologia git).

### 4.4 Formazione dei legami

Dopo il movimento, per ogni coppia di particelle adiacenti in ordine canonico
`(id_a, id_b)` si valuta un candidato se:

- la coppia di specie è in `allowed_pairs`;
- entrambe hanno `degree < max_bonds` della propria specie;
- entrambe hanno `energia ≥ bond_cost`;
- non esiste già un legame fra loro.

Ogni candidato consuma un uint64, anche se poi viene scartato per una formazione
precedente nello stesso passo. La soglia è `⌊p_formazione · fattore_catalitico · 2⁶⁴⌋`,
limitata a `2⁶⁴`. Se il candidato supera l'estrazione e le condizioni sono ancora
valide, il legame si forma.

---

## 5. Chimica artificiale

### 5.1 Cosa è un legame

Un legame è una relazione **locale e reversibile** fra due particelle adiacenti.
Non rappresenta un composto chimico specifico, non ha orientamento, non ha
proprietà oltre all'energia immagazzinata. Non esiste alcuna nozione di
"molecola" o "organismo" nel motore: gli aggregati sono solo componenti connesse
dei legami, misurate a posteriori (§5.5).

### 5.2 Formazione

Condizioni e soglia come in §4.4. Alla formazione ogni particella paga
`bond_cost + formation_dissipation`; il legame immagazzina `2 · bond_cost` e la
quota `2 · formation_dissipation` va in dissipazione. Con
`formation_dissipation = 0` (M2) il comportamento è identico a prima.

### 5.3 Rottura e restituzione dell'energia

Alla rottura il legame restituisce `bond_energy − breaking_dissipation`
(limitato a `bond_energy`):

```
restituito = bond_energy − min(breaking_dissipation, bond_energy)
quota_minore = restituito // 2
quota_maggiore = restituito - quota_minore
la particella con ID minore riceve quota_maggiore
```

La regola del resto è deterministica e documentata perché il restituito può
essere dispari.

### 5.4 Catalisi

Una regola di catalisi è una terna `(specie_catalizzatrice, coppia, fattore)`.
Se una particella della specie catalizzatrice è **adiacente** a una delle due
particelle della coppia (e non è uno dei due estremi), la probabilità di
formazione è moltiplicata per `fattore`, con saturazione a 1. Con più
catalizzatori adiacenti si usa il fattore massimo.

La catalisi:

- non riconosce sequenze, strutture o organismi: dipende solo da specie locali;
- non crea energia: `fattore` moltiplicativo a probabilità base 0 resta 0;
- è disattivata nella configurazione baseline (`catalysis: []`) e attiva in
  `configs/m2_catalysis.json`, così l'effetto è misurabile per differenza.

### 5.5 Aggregati

Un aggregato è una componente connessa di particelle unite da legami, di
dimensione ≥ 2. Le metriche riportano: numero di legami, energia nei legami,
particelle legate, particelle libere, numero di aggregati, dimensione massima,
dimensione media e distribuzione delle dimensioni.

Nessuna di queste misure è un obiettivo del modello: sono descrizioni.

---

## 6. Energia

**Decisione: energia intera, per particella, più un deposito nei legami, più un
ledger dei flussi.**

- Ogni specie ha `energy ∈ ℕ` quanti come dotazione iniziale di ogni particella.
- Energia interna: `E_int(t) = Σ energia_particelle + Σ energia_legami + Σ serbatoi`.
  I serbatoi delle sorgenti sono energia interna: è stata iniettata e non è
  ancora stata assorbita.
- Identità contabile, verificata con interi esatti:

```
E_int(t) = E_int(0) + injected(t) − dissipated(t) − unabsorbed(t)
```

| Voce | Significato |
|---|---|
| `injected` | energia emessa dalle sorgenti (lordo) |
| `dissipated` | dissipazione, costi di movimento e quote di attrito delle reazioni |
| `unabsorbed` | energia emessa da una sorgente e non consegnata (cella vuota o capacità piena) |

`unabsorbed` è contata come perdita: una sorgente che non trova destinatario non
crea energia.

### 6.1 Ordine delle fasi energetiche

Fissato e non negoziabile:

```
dissipazione → iniezione → rottura → movimento → risoluzione → formazione
```

- **Dissipazione**: `num` quanti ogni `den` passi, sfasati per identificativo:
  una particella perde 1 quanto nei passi in cui `(step + id) mod den < num`, un
  legame quando `(step + id_a + id_b) mod den < num`. Ogni quanto rimosso va in
  `dissipated`. Il tasso è **assoluto** (un quanto per evento), non proporzionale:
  un tasso proporzionale intero `(E·num)//den` si annulla per arrotondamento alle
  energie tipiche del modello (10–30 quanti) e la dissipazione diventa inerte.
- **Iniezione**: per ogni sorgente, in ordine canonico `(y, x)`,
  `acc += rate_num; quanti, acc = divmod(acc, rate_den)`. I quanti entrano in un
  **serbatoio locale** di capacità `capacity`; se il serbatoio trabocca, l'eccesso
  va in `unabsorbed`. La particella presente sulla cella assorbe l'intero
  serbatoio. Nessuna estrazione casuale, nessun drift.
- **Costo di movimento**: pagato solo dalle mosse accettate, dalla particella che
  si sposta; va in `dissipated`.
- **Costi di reazione**: come in §5.2–5.3.

Se `particle_decay.num = 0`, `bond_decay.num = 0`, `movement_cost = 0`,
`formation_dissipation = 0`, `breaking_dissipation = 0` e non ci sono sorgenti,
il modello è chiuso e identico a M2.

**Decisione: nessun riscalamento e nessun clamp.** I valori non vengono
rinormalizzati per evitare overflow o per "stabilizzare" la dinamica: alterano il
bilancio e rendono incomparabili i run. Gli interi Python non hanno overflow; nel
file i valori restano leggibili.

---

## 7. Generatore casuale

| Aspetto | Scelta |
|---|---|
| Algoritmo | PCG64 (NumPy) |
| Interfaccia | **solo** `random_raw()` → uint64 |
| Semina | `seed` intero non negativo, obbligatorio |
| Collocazione | 1 estrazione per particella |
| Movimento | 2 estrazioni per particella per passo, sempre |
| Chimica | 1 estrazione per legame esistente + 1 per coppia candidata, per passo |

Il flusso consumato dipende quindi dallo stato (numero di legami e di candidati),
ma è deterministico e riproducibile. Non ci sono estrazioni "nascoste": ogni
decisione casuale corrisponde a un'unità del flusso.

Tutte le soglie sono intere, calcolate una volta all'avvio: nel percorso caldo
non c'è aritmetica in virgola mobile.

---

## 8. Determinismo e riproducibilità

| Livello | Garanzia | Verifica |
|---|---|---|
| A. Ripetizione | stesso codice, config e seed ⇒ stesso risultato | test di riproducibilità, incluso `state_hash_full` |
| B. Ripresa | run continuo ≡ run interrotto e ripreso | test su checkpoint M1 e M2 |
| C. Portabilità | **non** garantita fra versioni o macchine | mitigata da interi, `random_raw`, versioni registrate |

Un risultato è citabile solo con: `state_hash_full`, hash della configurazione,
seed, versione del codice. Per i confronti fra configurazioni si usa l'hash della
configurazione.

---

## 9. Invarianti

| ID | Invariante | Verifica |
|---|---|---|
| I1 | Numero di particelle costante | conteggio |
| I2 | Quantità per specie costante | confronto con configurazione |
| I3 | Nessuna cella con più di una particella | griglia e posizioni |
| I4 | Ogni particella dentro la griglia | limiti |
| I5 | `grid` coerente con le posizioni | controllo incrociato |
| I6 | Identità energetica `E_int = E_0 + injected − dissipated − unabsorbed` | confronto intero |
| I7 | Flusso RNG tracciabile | test sul caso senza chimica: `N + 2·N·t` |
| I8 | ID unici, non negativi, `< next_id` | controllo |
| I9 | Energia di ogni particella ≥ 0 | controllo |
| I10 | Ogni legame unisce particelle adiacenti | distanza di Manhattan (toroidale se periodico) |
| I11 | Grado di ogni particella = legami registrati e ≤ `max_bonds` | conteggio incrociato |
| I12 | Nessun legame se la chimica è disabilitata | controllo |
| I13 | `injected`, `dissipated`, `unabsorbed` ≥ 0 | controllo |
| I14 | Un accumulatore di sorgente sta in `[0, rate_den)` | controllo |
| I15 | Un serbatoio di sorgente sta in `[0, capacity]` | controllo |
| I16 | Una sorgente esiste per ogni accumulatore e per ogni serbatoio | conteggio |

`World.validate()` restituisce l'elenco dei problemi; `World.check()` solleva
`InvariantError`. Esecuzione: alla creazione, a fine run, al caricamento di un
checkpoint e nei test.

---

## 10. Configurazione

Formato JSON. Schema 1 = M1, schema 2 = M2, schema 3 = M3 (flussi energetici).
Le chiavi sconosciute sono rifiutate e ogni schema rifiuta i blocchi introdotti
dai successivi.

```json
{
  "schema_version": 3,
  "seed": 20261115,
  "grid": { "width": 128, "height": 128, "boundary": "periodic" },
  "neighborhood": "von_neumann",
  "placement": "random_uniform",
  "species": [
    { "name": "S0", "count": 500, "move_probability": 0.5, "energy": 12, "max_bonds": 2 },
    { "name": "S1", "count": 400, "move_probability": 0.4, "energy": 10, "max_bonds": 2 },
    { "name": "S2", "count": 300, "move_probability": 0.3, "energy": 15, "max_bonds": 1 },
    { "name": "S3", "count": 200, "move_probability": 0.6, "energy": 8,  "max_bonds": 0 }
  ],
  "chemistry": {
    "enabled": true,
    "bond_cost": 2,
    "formation_probability": 0.05,
    "break_probability": 0.002,
    "allowed_pairs": [["S0","S0"], ["S0","S1"], ["S1","S1"], ["S1","S2"]],
    "catalysis": []
  },
  "energy": {
    "movement_cost": 0,
    "formation_dissipation": 1,
    "breaking_dissipation": 1,
    "particle_decay": { "num": 1, "den": 2000 },
    "bond_decay": { "num": 1, "den": 2000 },
    "sources": [
      { "x": 32, "y": 32, "rate_num": 2, "rate_den": 1, "capacity": 30 },
      { "x": 96, "y": 96, "rate_num": 2, "rate_den": 1, "capacity": 30 }
    ]
  },
  "metrics": { "every": 100 }
}
```

Vincoli aggiuntivi di schema 2:

- `1 ≤ specie ≤ 6` (limite del contratto M1), nomi univoci;
- `max_bonds ∈ [0,4]`;
- `allowed_pairs` normalizzate (coppia ordinata, lista ordinata, senza duplicati):
  l'hash non dipende dall'ordine o da ripetizioni;
- con `enabled: true` serve almeno una coppia fra specie con `max_bonds > 0`;
- ogni coppia e ogni catalizzatore devono riferirsi a specie esistenti;
- `factor ≥ 1`;
- lo schema 1 rifiuta `chemistry` e `max_bonds`; lo schema 2 rifiuta `energy`.

Vincoli aggiuntivi di schema 3:

- `movement_cost`, `formation_dissipation`, `breaking_dissipation` interi ≥ 0;
- `particle_decay.den`, `bond_decay.den` ≥ 1, `num` ≥ 0;
- sorgenti dentro la griglia, su celle distinte, con `rate_den ≥ 1`,
  `capacity ≥ 0` (capacità del serbatoio locale) e `overflow = "discard"`;
- le sorgenti sono normalizzate in ordine `(y, x)`: l'hash e gli accumulatori
  non dipendono dall'ordine di scrittura;
- `formation_dissipation` o `breaking_dissipation` richiedono `chemistry.enabled`.

**Hash canonico.** `sha256(JSON compatto con chiavi ordinate)` dell'oggetto
risolto. Il valore per `configs/baseline.json` (schema 1) è invariato rispetto a
M1: `f697f983…91c8`. Le configurazioni schema 2 mantengono hash e semantica.

Baseline M3 (`configs/m3_baseline.json`): 4 specie, 1400 particelle (8.5%),
energia iniziale 16 100 quanti, 4 sorgenti da 2 quanti/passo, decadimento
`1/2000` su particelle e legami, dissipazione delle reazioni 1.

---

## 11. Checkpoint

Formato JSON, scrittura atomica. Schema 3:

```json
{
  "format": "alife-checkpoint",
  "schema_version": 3,
  "config": { ... },
  "config_hash": "...",
  "step": 10000,
  "moves_total": 0,
  "next_id": 1400,
  "rng": { ... },
  "rng_draws": 0,
  "particles": [[id, x, y, specie, energia], ...],
  "bonds": [[id_a, id_b, energia], ...],
  "ledger": { "injected": 0, "dissipated": 0, "unabsorbed": 0 },
  "source_acc": [0],
  "source_store": [0],
  "counts": { ... },
  "energy_total": 16100,
  "energy_particles": 0,
  "energy_bonds": 0,
  "bonds_formed_total": 0,
  "bonds_broken_total": 0,
  "state_hash": "...",
  "state_hash_full": "..."
}
```

**Verifiche in lettura:** formato e schema (1, 2 o 3); configurazione valida e
hash coerente; stato RNG; particelle e legami ben formati; `state_hash`; per gli
schemi 2 e 3 anche `state_hash_full`; ledger non negativo; accumulatori e
serbatoi coerenti con le sorgenti; identità energetica; invarianti I1–I16.

**Migrazione.** Schema 1: `id = indice`, energia iniziale della specie, nessun
legame, `next_id = N`, `state_hash` verificato con la definizione M1. Schema 2:
stessi campi fisici, ledger azzerato e accumulatori a zero. In entrambi i casi il
mondo migrato è subito salvabile come schema 3 e conserva il proprio hash.

---

## 12. Metriche e artefatti

| File | Contenuto |
|---|---|
| `manifest.json` | comando, seed, hash config, versioni, piattaforma, commit |
| `config.resolved.json` | configurazione usata |
| `metrics.jsonl` | serie temporale (ogni `metrics.every` passi) |
| `summary.json` | riepilogo finale |
| `checkpoint.json` | stato completo riprendibile |
| `events.jsonl` | **solo con `--events`**: ogni formazione e rottura, con passo, ID, energia, catalisi |

Serie temporale e riepilogo includono: passi, tempo, passi/s, spostamenti,
particelle per specie, occupazione, energia interna/particelle/legami/serbatoi,
energia iniettata/dissipata/non assorbita, `identity_delta`, legami, particelle
legate, aggregati, dimensione massima, formazioni e rotture cumulate,
`state_hash`, `state_hash_full`, seed, hash della configurazione, picco di
memoria e versioni.

Memoria: `VmHWM` su Linux (picco dell'address space, azzerato all'exec),
`ru_maxrss` su macOS; il riepilogo registra anche il delta rispetto al
caricamento del modulo. Motivo: `ru_maxrss` può ereditare il picco del processo
genitore e produrre valori non riproducibili.

---

## 13. Come si riconosce un artefatto

Regole già attive:

- un risultato vale solo con hash completo, seed e hash della configurazione;
- i run sono confrontabili solo a parità di hash di configurazione;
- una struttura osservata una volta è un candidato, non una scoperta;
- la catalisi si valuta *per differenza* rispetto alla stessa configurazione
  senza catalisi, a parità di seed;
- la distribuzione delle dimensioni degli aggregati va confrontata con quella
  attesa per aggregazione casuale: un aggregato grande non è una scoperta;
- un bilancio energetico si verifica con l'identità intera
  `E_int = E_0 + injected − dissipated − unabsorbed`, mai con una tolleranza:
  `identity_delta ≠ 0` è un difetto, non un fenomeno.

---

## 14. Test

Obbligatori M1 (invariati): conservazione di particelle e specie, occupazione
unica, confini, riproducibilità, integrità dei checkpoint, equivalenza
continuo/ripreso, rilevamento di violazioni intenzionali. Mappatura e file di
risultato: `reports/tests/index.md`.

Test M2 aggiunti:

| Regola | Test |
|---|---|
| Formazione fra vicini ammessi | `test_bond_forms_between_adjacent_allowed_particles` |
| Coppia di specie non ammessa | `test_no_bond_for_non_allowed_species` |
| Specie con `max_bonds = 0` | `test_no_bond_when_species_cannot_bond` |
| Limite `max_bonds` | `test_max_bonds_is_respected`, `test_chains_grow_to_max_bonds` |
| Energia insufficiente | `test_no_bond_without_enough_energy` |
| Restituzione dell'energia | `test_breaking_returns_energy` |
| Immobilità delle particelle legate | `test_bonded_particles_do_not_move` |
| Catalisi locale | `test_catalysis_multiplies_only_when_adjacent` |
| Statistiche degli aggregati | `test_aggregate_statistics` |
| Conservazione dell'energia con legami | `test_energy_with_bonds_is_conserved` |
| Determinismo con chimica | `test_m2_quick_is_deterministic` |
| Golden hash M1 riprodotto dal codice M2 | `test_m1_run_reproduces_the_published_hash` |
| Roundtrip, ripresa e corruzione | `test_v2_*`, `test_detects_tampered_*` |
| Migrazione schema 1 → 2 | `test_v1_checkpoint_is_migrated` |
| Legami non adiacenti, gradi, limiti | `test_validate_detects_*` |

Test M3 aggiunti:

| Regola | Test |
|---|---|
| Identità energetica in sistema chiuso | `test_closed_system_keeps_identity` |
| Decadimento esatto di particelle e legami | `test_particle_decay_is_exact`, `test_bond_decay_is_exact` |
| Accumulatore delle sorgenti senza drift | `test_source_accumulator_is_exact` |
| Capacità e energia non assorbita | `test_source_capacity_and_unabsorbed`, `test_source_on_empty_cell_is_unabsorbed` |
| Costo di movimento solo su mosse accettate | `test_movement_cost_charged_per_move` |
| Movimento bloccato da energia insufficiente | `test_movement_cost_blocks_when_insufficient` |
| Attrito di formazione e rottura | `test_formation_dissipation`, `test_breaking_dissipation` |
| Identità su run aperto | `test_open_run_keeps_identity` |
| Determinismo con flussi | `test_open_run_is_deterministic` |
| Budget di estrazioni invariato | `test_rng_budget_with_flows_disabled` |
| Golden hash M2 preservato | `test_golden_hash_m2_is_preserved` |
| Accumulatore fuori intervallo, ledger alterato | `test_source_accumulator_out_of_range_is_detected`, `test_ledger_tampering_is_detected` |
| Core senza sorgenti di non determinismo | `test_core_modules_do_not_import_nondeterministic_sources` |
| Roundtrip e ripresa con ledger | `test_v3_roundtrip_preserves_ledger`, `test_v3_resume_is_equivalent_with_flows` |
| Migrazione schema 2 → 3 | `test_v2_checkpoint_is_migrated_to_v3` |

---

## 15. Limiti dichiarati e decisioni aperte

1. **Particelle legate immobili.** Nessun moto rigido degli aggregati; un
   aggregato è statico finché non si rompe un legame. Conseguenza voluta:
   strutture persistenti e misurabili, senza dinamica di corpo rigido.
2. **Nessuna catalisi di rottura.** La catalisi agisce solo sulla formazione.
3. **Un legame per coppia, senza orientamento.** Non esistono valenze, ordini di
   legame o angoli.
4. **Nessun decadimento delle particelle.** La materia è costante; la morte di
   particelle richiede una politica di rilascio degli ID.
5. **Sorgenti puntiformi e deterministiche.** Una sola particella per cella
   riceve l'energia; non esistono gradienti, diffusione o campi.
6. **Nessun termostato.** Non si riscalala l'energia per stabilizzare la
   dinamica: romperebbe il ledger.
7. **Nessuna nozione di "molecola".** Gli aggregati sono componenti connesse,
   misurate; il motore non le riconosce.
8. **Costo superlineare in densità** per la risoluzione dei conflitti (§4.3).
9. **Riproducibilità cross-version non garantita** (§8, livello C).
10. **Nessun parallelismo.** Il flusso RNG sequenziale lo esclude; M9 richiederà
    un RNG counter-based con chiave `(passo, id)` e un test di equivalenza.

Decisioni rinviate a M4: rilevamento e tracciamento delle strutture, eventi di
nascita/scissione, politiche di creazione e morte delle particelle con rilascio
degli ID, catalisi della rottura, gradienti di energia.

---

## 16. Reazioni consentite e controlli negativi

In M3 la "tabella delle reazioni" è:

| Regola | Condizione | Effetto | Costo |
|---|---|---|---|
| Formazione | coppia ammessa, adiacenza, slot liberi, energia sufficiente, estrazione | nasce un legame | `bond_cost` immagazzinato + `formation_dissipation` dissipata |
| Rottura | estrazione | il legame scompare | `breaking_dissipation` sottratta al restituito |
| Movimento | estrazione, energia sufficiente | la particella cambia cella | `movement_cost` dissipato, solo se accettata |
| Iniezione | accumulatore della sorgente | energia a una particella | nessuna, è il flusso entrante |
| Dissipazione | decadimento intero per passo | energia rimossa | va in `dissipated` |

Nessuna trasformazione di specie. Controlli negativi definiti in M0 (N1
particelle immobili senza reazioni, N2 aggregazione casuale a densità
controllata, N3 reazioni reversibili senza ereditarietà) e il controllo positivo
isolato per M5.

---

## 17. Glossario

- **Passo**: dissipazione, iniezione, rottura, movimento, risoluzione, formazione.
- **Legame**: relazione locale reversibile con energia immagazzinata.
- **Aggregato**: componente connessa di particelle legate, dimensione ≥ 2.
- **Particella libera**: particella con grado 0.
- **Ledger**: `injected`, `dissipated`, `unabsorbed`; rende verificabile il
  bilancio di un sistema aperto.
- **Accumulatore**: resto intero di una sorgente, stato persistente.
- **`state_hash`**: hash materiale (posizioni e specie).
- **`state_hash_full`**: hash completo (identità, energia, legami, flussi).
- **Quanto**: unità intera di energia; nessuna unità fisica è attribuita.
