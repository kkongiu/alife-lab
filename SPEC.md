# SPEC — Modello computazionale (milestone M0/M1)

Versione: 1.0 (M1) · Data: 2026-11-14 · Riferimenti: `alife.md`, `Progetto_Vita_Artificiale_Roadmap_Milestone.docx`

Questa specifica descrive un universo chiuso, deterministico e osservabile. Deve
essere sufficiente a reimplementare il motore senza decisioni implicite. Ogni
scelta non imposta dai documenti di progetto è marcata come **decisione** ed è
motivata.

---

## 1. Scopo e perimetro

Il sistema realizzato è il motore fisico locale della milestone M1: particelle che
si spostano su una griglia discreta, senza reazioni, catalisi, legami,
replicazione, ereditarietà o ricompense.

Non esistono nel modello: organismi, genomi, DNA, replicatori, reti neurali,
funzioni di fitness, sorgenti o pozzi di energia, meccanismi di copia.

L'universo è **chiuso**: materia ed energia sono costanti. Non ci sono fenomeni
biologici da osservare in M1, e il motore non è progettato per produrne. Il valore
di M1 è ingegneristico: rendere possibili, e verificabili, le milestone
successive.

---

## 2. Spazio, tempo, particelle

| Elemento | Definizione |
|---|---|
| Spazio | Griglia rettangolare `Lx × Ly` di celle discrete; baseline `128 × 128 = 16 384` celle |
| Confini | `periodic` (toro, default) oppure `closed` (nessun attraversamento) |
| Occupazione | Al massimo **una** particella per cella |
| Tempo | Passi discreti; un passo = una proposta di movimento per particella + una risoluzione |
| Particella | Tupla `(x, y, specie)`; nessun altro attributo in M1 |
| Specie | Etichetta con due proprietà locali: `move_probability ∈ [0,1]`, `energy ∈ ℕ` |
| Vicinato | von Neumann (4 celle ortogonali), configurabile nella forma ma una sola opzione in M1 |

Non esistono campi, forze a distanza, ordine globale o memoria delle particelle:
l'unica informazione disponibile a una particella è la propria specie e
l'occupazione locale al momento della risoluzione.

---

## 3. Rappresentazione dello stato

**Decisione.** Lo stato è composto da:

1. tre array paralleli di lunghezza `N`: `xs[i]`, `ys[i]`, `species[i]`;
2. una griglia piatta `grid` di `Lx·Ly` interi: `grid[y·Lx + x] = i` se la cella è
   occupata dalla particella `i`, `-1` se è vuota;
3. il contatore `step`;
4. il contatore cumulativo `moves_total`;
5. lo stato completo del generatore casuale.

**Decisione: l'indice `i` è l'identificatore stabile della particella.** In M1 non
esistono nascita, morte né riordinamento degli array, quindi l'ordine è canonico e
`i` identifica una particella per tutta la vita del run. Conseguenze:

- nessun array di ID separato (meno stato da serializzare e da corrompere);
- il checkpoint conserva l'ordine, quindi l'identità è preservata fra run;
- **in M2**, quando nasceranno e moriranno particelle, questa semplificazione
  dovrà essere sostituita da ID espliciti e persistenti (vedi §14).

La griglia è ridondante rispetto agli array di posizione: è una cache per
l'occupazione O(1). La coerenza fra le due rappresentazioni è un invariante
verificato (§8, I5).

**Decisione.** Gli array sono liste Python, non array NumPy: il passo è dominato
da accessi scalari e da un ordinamento, dove NumPy non porta vantaggio e
introdurrebbe conversioni. NumPy è usato solo per PCG64. La scelta è rivalutabile
solo dopo profilazione (M9).

---

## 4. Modello temporale e movimento

Un passo `t → t+1` ha quattro fasi, tutte sullo stesso stato di partenza.

### 4.1 Proposta

Per ogni particella in ordine crescente di indice si consumano **esattamente due**
uint64 dal generatore:

```
roll      = raw()          # prima estrazione
direction = raw() & 3      # seconda estrazione, sempre effettuata
if roll >= threshold[specie]: la particella resta ferma
else: propone la cella vicina in direzione `direction`
```

`threshold = ⌊p · 2⁶⁴⌋` è calcolata come intero, così il confronto è esatto e non
dipende da aritmetica in virgola mobile.

**Decisione.** La direzione viene estratta anche quando la particella non si
muove. Il flusso RNG consumato per passo è quindi esattamente `2N`, indipendente
dalle scelte: questa proprietà è verificata da un test e rende banale il controllo
di allineamento del generatore.

**Decisione.** Le direzioni sono indicizzate nell'ordine
`(0,-1), (1,0), (0,1), (-1,0)` = nord, est, sud, ovest; `raw & 3` è uniforme
perché `2⁶⁴` è divisibile per 4, quindi **nessun bias direzionale**.

**Confini:**

- `periodic`: la destinazione è `((x+dx) mod Lx, (y+dy) mod Ly)`;
- `closed`: se la destinazione esce dalla griglia la mossa viene annullata (la
  particella resta ferma). Non c'è rimbalzo né riflessione: la scelta è la più
  semplice e non introduce una direzione privilegiata.

**Decisione.** Il campionamento con rifiuto sui bordi non altera il flusso RNG
(le estrazioni avvengono comunque), quindi non introduce dipendenze nascoste.

### 4.2 Risoluzione dei conflitti

Le proposte sono simultanee; la risoluzione è esplicita e indipendente
dall'ordine di scansione della griglia.

**Priorità.** Ogni particella che propone una mossa riceve una priorità intera

```
h = (i+1) · 0x9E3779B97F4A7C15  XOR  (t+1) · 0xD6E8FEB86659FD93   (mod 2⁶⁴)
priority(i, t) = splitmix64(h)
```

dove `splitmix64` è il finalizzatore a 64 bit standard. La priorità:

- non consuma RNG;
- dipende solo da `(indice, passo)`, quindi è riproducibile e non dipende
  dall'ordine di scansione;
- non è correlata con la posizione né con la specie (l'indice iniziale è assegnato
  in ordine di collocazione casuale, e comunque l'hash elimina ogni struttura
  residua);
- è ricalcolata a ogni passo: una particella non ha una "forza" persistente.

**Algoritmo.**

```
accettate := {}
riservate := {}                       # celle già assegnate
pendenti  := tutte le proposte, ordinate per priorità decrescente (pareggio: indice)

ripeti:
    progresso := falso
    per ogni mossa m in pendenti (in ordine di priorità):
        se destinazione(m) ∈ riservate: continua
        occupante := grid[destinazione(m)]
        se occupante = -1 oppure occupante ∈ accettate:
            accetta m; progresso := vero
    se progresso: aggiorna pendenti e ripeti

    ciclo := cerca_ciclo(pendenti)     # rotazione chiusa A→B→…→A
    se ciclo esiste: accetta tutte le mosse del ciclo
    altrimenti: esci
```

`cerca_ciclo` segue la catena "occupante della cella bersaglio" fra le mosse
pendenti; se torna su un nodo già visitato, il tratto ripetuto è una rotazione
chiusa e viene accettato come gruppo (scambio a due, ciclo a tre, ecc.).

**Proprietà garantite** (verificate dai test in `tests/test_dynamics.py` e
`tests/test_invariants.py`):

- **P1** le destinazioni accettate sono tutte distinte (nessuna collisione);
- **P2** una mossa verso una cella vuota è sempre accettata;
- **P3** una catena che termina in una cella vuota viene accettata per intero;
- **P4** uno scambio o un ciclo chiuso viene accettato per intero;
- **P5** una catena bloccata da una particella ferma non muove nessuno dei suoi
  elementi;
- **P6** il risultato non dipende dall'ordine di inserimento delle proposte;
- **P7** nessuna particella può finire fuori griglia o su una cella occupata.

**Complessità.** `O(N log N)` per l'ordinamento delle priorità, `O(N)` per ogni
giro di risoluzione; il numero di giri è piccolo (nella pratica 1–3) e comunque
limitato da `N`.

### 4.3 Applicazione

L'applicazione è simultanea. Prima si svuotano **tutte** le celle di partenza,
poi si scrivono tutte le destinazioni. Senza questo ordine uno scambio
sovrascriverebbe una particella. Prima della scrittura si verifica che la cella
destinazione sia vuota: una collisione è un errore di programmazione, non una
condizione tollerata.

### 4.4 Perché non un aggiornamento sequenziale

Un aggiornamento "particella per particella" introdurrebbe una dipendenza
dall'ordine di scansione (chi si muove prima vede un mondo diverso) e un bias
sistematico nella direzione del flusso. Lo schema a proposta + risoluzione rende
la simultaneità esplicita e la verifica possibile.

---

## 5. Energia nel prototipo chiuso

**Decisione: l'energia è una quantità intera, in "quanti", non un float.**

- Ogni specie ha `energy ∈ ℕ` quanti per particella.
- L'energia totale è `E(t) = Σ_particles energy(specie(i))`.
- In M1 **il movimento non ha costo**: non esistono sorgenti, pozzi,
  dissipazione, soglie o decadimento.
- Conseguenza: `E(t) = E(0)` **per costruzione**, non per aggiustamento
  numerico. Non c'è drift in virgola mobile da mascherare.

Il campo `energy` esiste già in configurazione perché è il punto di innesto di
M3: costi di movimento, dissipazione e flussi entranti si aggiungeranno come
termini espliciti, mantenendo il bilancio verificabile come
`E(t+1) = E(t) + in − out − dissipato`.

Il bilancio registrato nelle metriche è quindi `in = out = 0`, `delta = 0`.
Un valore `delta ≠ 0` è un errore, non un fenomeno.

---

## 6. Generatore casuale

| Aspetto | Scelta |
|---|---|
| Algoritmo | PCG64 (NumPy `Generator`/`BitGenerator`) |
| Interfaccia usata | **solo** `random_raw()` → uint64 |
| Motivo | il flusso di bit di PCG64 è stabile fra versioni; i metodi di distribuzione (`random`, `integers`) possono cambiare implementazione |
| Semina | `seed` intero non negativo, obbligatorio in configurazione |
| Consumo iniziale | esattamente 1 estrazione per particella collocata |
| Consumo per passo | esattamente 2 estrazioni per particella |
| Serializzazione | `bit_generator`, `state.state`, `state.inc`, `has_uint32`, `uinteger` in JSON |

**Collocazione iniziale.** Le celle libere sono tenute in una lista; per ogni
particella si estrae `k = raw() mod |free|`, si assegna la cella `free[k]` e si
rimuove con swap-pop. È un campionamento uniforme senza sostituzione, con
**una sola estrazione per particella** e senza rifiuti.

**Uso dell'aritmetica intera.** Tutte le decisioni sono confronti o maschere su
uint64: non c'è alcun calcolo in virgola mobile nel percorso caldo. I soli float
della configurazione (`move_probability`) sono convertiti una volta in soglie
intere all'avvio.

---

## 7. Determinismo e riproducibilità

Si distinguono tre livelli, con garanzie diverse:

| Livello | Garanzia | Come si verifica |
|---|---|---|
| A. Ripetizione | stesso codice, stessa config, stesso seed ⇒ stesso risultato | `test_reproducibility.py` |
| B. Ripresa | run continuo ≡ run interrotto e ripreso dal checkpoint | `test_checkpoint.py`, `test_cli.py` |
| C. Portabilità | identità **non** garantita fra versioni di Python/NumPy o architetture diverse | mitigata da: solo aritmetica intera nel percorso caldo, `random_raw`, versioni registrate nel manifest |

Il livello C è dichiarato esplicitamente: `alife.md` richiede la ripetibilità
"nello stesso ambiente software", non l'identità bit-a-bit fra macchine. Ogni run
registra versione di Python, versione di NumPy, piattaforma, hash della
configurazione e commit git (se disponibile).

---

## 8. Invarianti

| ID | Invariante | Verifica |
|---|---|---|
| I1 | Il numero di particelle è costante | conteggio su array e griglia |
| I2 | Il numero di particelle per specie è costante | confronto con la configurazione |
| I3 | Nessuna cella contiene più di una particella | `grid` e celle rivendicate |
| I4 | Ogni particella è dentro `[0,Lx) × [0,Ly)` | controllo sui limiti |
| I5 | `grid` è coerente con gli array di posizione in entrambe le direzioni | controllo incrociato |
| I6 | `E(t) = E(0)` | confronto intero |
| I7 | Il flusso RNG consumato è `N + 2·N·t` | confronto con un generatore di riferimento |

`World.validate()` restituisce l'elenco dei problemi (vuoto = stato integro);
`World.check()` solleva `InvariantError` con il dettaglio. Il controllo viene
eseguito alla creazione, al termine di ogni run, dopo il caricamento di un
checkpoint e nei test; **non** a ogni passo (costo `O(N·celle)`), ma può essere
attivato in debug.

---

## 9. Configurazione

Formato: JSON, un oggetto per esperimento. Tutte le chiavi sono obbligatorie
tranne quelle con default. Chiavi sconosciute sono **rifiutate** (un refuso non
deve passare silenziosamente).

```json
{
  "schema_version": 1,
  "seed": 20261114,
  "grid": { "width": 128, "height": 128, "boundary": "periodic" },
  "neighborhood": "von_neumann",
  "placement": "random_uniform",
  "species": [
    { "name": "S0", "count": 400, "move_probability": 0.60, "energy": 10 }
  ],
  "metrics": { "every": 100 }
}
```

Vincoli di validazione:

- `seed ≥ 0` intero;
- `width, height ≥ 2`;
- `boundary ∈ {periodic, closed}`;
- `1 ≤ numero di specie ≤ 6`, nomi univoci e non vuoti;
- `count ≥ 0`, `Σ count ≤ Lx·Ly`;
- `0 ≤ move_probability ≤ 1`, finito;
- `energy ≥ 0` intero;
- `metrics.every ≥ 1`;
- i booleani non sono accettati come interi.

**Hash canonico.** `sha256(JSON compatto con chiavi ordinate)` dell'oggetto
risolto. Identifica l'esperimento in manifest, metriche e checkpoint. Lo stesso
insieme di parametri produce lo stesso hash indipendentemente dall'ordine delle
chiavi o dalla formattazione del file.

Baseline (`configs/baseline.json`): 128×128, 6 specie, 1638 particelle (10.0% di
occupazione), energia iniziale 17 668 quanti.

---

## 10. Checkpoint

Formato: JSON singolo, scrittura **atomica** (file temporaneo + `os.replace`,
`fsync` prima della sostituzione). Un'interruzione non lascia checkpoint parziali.

```json
{
  "format": "alife-checkpoint",
  "schema_version": 1,
  "created_utc": "...",
  "config": { ... },
  "config_hash": "...",
  "step": 10000,
  "moves_total": 7231450,
  "rng": { "bit_generator": "PCG64", "state": { ... }, "has_uint32": 0, "uinteger": 0 },
  "particles": [[x, y, specie_index], ...],
  "counts": { "S0": 400, ... },
  "energy_total": 17668,
  "state_hash": "..."
}
```

**Verifiche in lettura** (ognuna produce `CheckpointError` con messaggio distinto):

1. formato e `schema_version`;
2. configurazione ricostruibile e valida;
3. `config_hash` ricalcolato = quello salvato;
4. stato RNG completo e caricabile;
5. particelle ben formate, dentro griglia, senza doppie occupazioni;
6. `state_hash` ricalcolato = quello salvato (rileva ogni alterazione delle
   particelle);
7. `energy_total` coerente con le particelle;
8. invarianti I1–I6 sul mondo ricostruito.

**Definizione di `state_hash`.** `sha256` della serializzazione canonica di
`{schema, width, height, boundary, specie (nomi), particelle (x,y,specie) in
ordine di indice}`. Non include `step` né lo stato RNG: due stati con le stesse
particelle hanno lo stesso hash anche a passi diversi, il che rende confrontabile
"run continuo" e "run ripreso". Configurazione e RNG hanno hash/fingerprint
separati.

Il comando di ripresa è `alife resume --checkpoint <file> --steps <n>`.

---

## 11. Metriche e artefatti

Ogni run produce una directory con:

| File | Contenuto |
|---|---|
| `manifest.json` | comando, argv, seed, hash config, versioni, piattaforma, commit git, timestamp |
| `config.resolved.json` | configurazione effettivamente usata (dopo eventuale override del seed) |
| `metrics.jsonl` | un record ogni `metrics.every` passi |
| `summary.json` | riepilogo finale conforme ai campi obbligatori di M1 |
| `checkpoint.json` | stato finale completo, riprendibile |

Campi registrati: passo, tempo, passi/s, spostamenti (totali e per intervallo),
particelle per specie, occupazione, energia totale/in/out/delta, hash dello stato,
seed, hash e versione della configurazione, picco di memoria RSS, versione di
Python e NumPy.

**Memoria.** Picco RSS del processo: su Linux `VmHWM` da `/proc/self/status`, cioè
il picco dell'address space corrente, azzerato all'`exec`; su macOS `ru_maxrss`,
espresso in byte. `ru_maxrss` non è usato su Linux perché può ereditare il picco
del processo genitore: in questo ambiente sono state osservate letture di 590 MiB
con RSS reale di 44 MiB.

Il picco assoluto dipende dall'ambiente (interprete, NumPy) e non è una misura
stabile della simulazione. Per questo `summary.json` registra tre valori:

| Campo | Significato |
|---|---|
| `peak_memory_bytes` | picco RSS dell'intero processo |
| `baseline_memory_bytes` | picco al caricamento del modulo, con interprete e NumPy già importati |
| `simulation_memory_bytes` | `peak − baseline`: memoria aggiuntiva della simulazione |

Il valore da citare nei report è `simulation_memory_bytes`. Un `peak` anomalo con
`simulation_memory_bytes` vicino a zero indica un artefatto dell'ambiente, non un
consumo del motore.

---

## 12. Come si riconosce un artefatto numerico

Regole applicate già in M1, per non doverle improvvisare in M4–M7:

- un risultato vale solo se accompagnato da hash dello stato, seed e hash della
  configurazione;
- i run sono confrontabili solo a parità di hash di configurazione;
- un pattern osservato una volta è un candidato, non un risultato;
- i controlli negativi (§15) sono definiti prima dei run esplorativi;
- nessun parametro viene modificato *dopo* aver visto un risultato senza
  registrare la modifica come nuova configurazione (nuovo hash).

---

## 13. Test obbligatori: mappatura

| Richiesta `alife.md` §7 | Test |
|---|---|
| 1. Conservazione del numero di particelle | `test_invariants.py::test_particle_count_conserved` |
| 2. Conservazione per specie | `test_invariants.py::test_species_quantities_conserved` |
| 3. Nessuna occupazione multipla | `test_invariants.py::test_no_multiple_occupancy` |
| 4. Rispetto dei confini | `test_invariants.py::test_periodic_boundaries`, `test_dynamics.py::test_closed_boundary_keeps_particles_inside` |
| 5. Riproducibilità con lo stesso seed | `test_reproducibility.py` (5 test) |
| 6. Integrità salvataggio/caricamento | `test_checkpoint.py::test_roundtrip_preserves_state` e i test di corruzione |
| 7. Equivalenza continuo ↔ ripreso | `test_checkpoint.py::test_resume_is_equivalent_to_continuous_run`, `test_cli.py::test_resume_matches_continuous_run` |
| 8. Rilevamento di violazioni intenzionali | `test_invariants.py::test_validate_detects_*` (5 casi), `test_checkpoint.py::test_detects_*` (5 casi) |

Test aggiuntivi rispetto al minimo: risoluzione dei conflitti (7 casi), flusso
RNG, validazione della configurazione, CLI end-to-end.

---

## 14. Limiti dichiarati e decisioni aperte

Limiti del modello M1:

1. **Nessuna struttura emergente possibile.** Senza interazioni attrattive o
   reazioni, il sistema è una nuvola diffusa: qualunque struttura osservata
   sarebbe un artefatto statistico di densità. Questo è voluto.
2. **Energia passiva.** Non può produrre non-equilibrio: è un contatore
   conservato, non un vincolo dinamico.
3. **Una particella per cella.** Esclude collisioni e densità locali; sarà
   rivisto se M2 richiederà più occupanti.
4. **Identità = indice dell'array.** Non regge nascita/morte: in M2 servono ID
   persistenti, e il checkpoint dovrà migrare allo schema successivo.
5. **Dimensione fissa della griglia.** Nessun dominio che cresce o si adatta.
6. **Nessun legame.** I legami sono materia di M2 e non esistono nel modello.
7. **Prestazioni da Python puro.** Misurate, non ottimizzate: vedi
   `reports/M1_baseline.md`. La profilazione indica che ~27% del tempo è
   overhead di chiamata per estrazione RNG e ~30% ordinamento delle priorità:
   entrambi sono candidati per M9, non per M1.
8. **Riproducibilità cross-version non garantita** (§7, livello C).

Decisioni rinviate, da prendere prima di M2:

- ID persistenti delle particelle e politica di riuso;
- schema di checkpoint v2 (retrocompatibilità o migrazione);
- se l'energia diventa un campo per particella (necessario per costi e
  dissipazione differenziati) e come mantenerla intera;
- rappresentazione dei legami e loro ordine canonico per la serializzazione.

---

## 15. Reazioni consentite e controlli negativi (definiti, non implementati)

In M1 la tabella delle reazioni consentite è **vuota**. Nessuna trasformazione di
specie, nessun legame, nessuna catalisi. Questa sezione esiste perché M0 richiede
che i controlli negativi siano definiti *prima* di cercare fenomeni.

Controlli negativi previsti per M2–M5 (non ancora implementati):

| ID | Controllo | Cosa deve succedere | Cosa dimostra |
|---|---|---|---|
| N1 | Particelle immobili senza reazioni | Nessuna struttura, nessuna persistenza | Il rilevatore non inventa aggregati |
| N2 | Aggregazione casuale a densità controllata | Il rilevatore misura la distribuzione attesa per caso | Le soglie di persistenza sono calibrate |
| N3 | Reazioni reversibili senza ereditarietà | Copie apparenti ma nessuna linea di discendenza stabile | Distingue copia da ereditarietà |

Controllo positivo previsto per M5: fixture **isolata** con un replicatore noto,
in un modulo separato con configurazione separata, mai raggiungibile
dall'universo di scoperta. In M1 non esiste alcun codice di replicazione.

---

## 16. Glossario minimo

- **Passo**: una proposta di movimento per particella più una risoluzione.
- **Mossa accettata**: particella che cambia cella in un passo.
- **Occupazione**: particelle / celle.
- **Quanto di energia**: unità intera di energia; nessuna unità fisica è
  attribuita.
- **Hash dello stato**: identificatore delle sole particelle; **hash della
  configurazione**: identificatore dei parametri; **fingerprint RNG**:
  identificatore della posizione nel flusso casuale.
