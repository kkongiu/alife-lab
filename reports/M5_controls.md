# M5 — Report: controlli positivi e negativi

Data: 2026-11-15 · Milestone: M5 · Specifica: `SPEC.md` §18 · Fixture: `m5-fixtures-1`

## 1. Sommario

| Milestone | Esito | Evidenza |
|---|---|---|
| M1–M4 | GO (approvati) | invariati; il motore non conosce i controlli |
| **M5** | **GO** | 166 test; 33 requisiti con evidenza; positivo riconosciuto 9/9; cinque condizioni negative con 0 falsi positivi |

Il gate del docx S5 — *il benchmark positivo è riconosciuto e i negativi non
vengono classificati come replicazione* — è soddisfatto: 9 copie persistenti su 9
nel controllo positivo, 0 copie candidate in tutte le condizioni negative.

## 2. Cosa dimostra e cosa non dimostra

**Dimostra** che il motore sa rappresentare, tracciare e far riconoscere a un
rilevatore preregistrato un sistema di copiatura noto, e che lo stesso rilevatore
non scatta su aggregazione casuale, reazioni reversibili, immobilità o firme
molto ripetute.

**Non dimostra** che nell'universo di scoperta avvenga qualcosa di simile. Il
copiatore del controllo positivo è programmato, vive fuori dal motore ed è usato
solo per calibrare il rilevatore. Nessun risultato di M5 autorizza a parlare di
replicazione spontanea.

## 3. Isolamento

- Il pacchetto `alife.controls` contiene l'unico replicatore codificato del
  progetto.
- Nessun modulo di `src/alife/*.py` cita `controls`: un test statico lo verifica
  a ogni esecuzione della suite.
- Le fixture sono costruite da codice con posizioni fisse e una versione
  dichiarata (`m5-fixtures-1`); non leggono configurazioni del mondo di scoperta
  e non ne modificano i parametri.
- Il motore non ha alcuna modalità "controllo": il copiatore è un driver esterno
  che usa `add_bond` e il tracciamento.

## 4. Controllo positivo

Template `A-B-B-A` e nove siti di monomeri con la stessa sequenza. A ogni passo
il copiatore assembla la catena nel sito a destra di un template; la copia
diventa template al passo successivo.

| Passo | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| Copie | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| Generazione massima | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |

Ogni copia è una struttura nuova (nessuna particella condivisa), a distanza 1 dal
genitore, con firma esatta identica. Al passo 9 il combustibile è esaurito: il
sistema si ferma, non cresce più. La discendenza è verificabile nel registro
(`reports/tests/evidence/M5-01_*`).

## 5. Controlli negativi

| Fixture | Passi | Strutture finali | Nascite | Copie candidate | Classificazione |
|---|---|---|---|---|---|
| N1 immobile | 100 | 0 | 0 | 0 | `not_replication` |
| N2 aggregazione casuale (4 specie) | 1 000 | 112 | 151 | 0 | `not_replication` |
| N3 reazioni reversibili | 1 000 | 87 | 1 681 | 0 | `not_replication` |
| stress: una sola specie | 1 000 | 62 | 87 | 0 | `not_replication` |
| stress: formazione massima | 1 000 | 63 | 77 | 0 | `not_replication` |

## 6. Perché i negativi non producono copie

Il criterio richiede una **nascita** di una struttura completa (≥ 4 particelle)
accanto a una struttura con la stessa firma. Nei negativi le strutture non
nascono complete: partono da dimeri e crescono per accrezione, un legame alla
volta. Le nascite di dimensione ≥ 4 sono rare e, quando avvengono, non hanno una
struttura simile a distanza ≤ 2. Il positivo è l'unico caso in cui una struttura
completa compare accanto a un template.

È un risultato, non un dettaglio: il criterio riconosce l'**assemblaggio
template-diretto**, non la replicazione in generale. Un replicatore che crescesse
per accrezione non verrebbe classificato come copia; servirebbero criteri di
discendenza, materia di M6–M7.

## 7. Criterio preregistrato

| Parametro | Valore | Perché |
|---|---|---|
| `radius` | 2 | una copia locale deve stare accanto al genitore |
| `persist_steps` | 10 | una comparsa effimera non è una copia |
| `min_size` | 4 | sotto questa soglia l'associazione casuale è indistinguibile |
| `min_copies` | 5 | evita di classificare un singolo evento |
| `min_generation` | 2 | richiede una catena persistente, non solo una copia del template |
| genitore precedente | `born_step < step` | due strutture nate insieme non possono essere genitore e figlia |
| generazioni | solo copie persistenti | una seconda generazione transitoria non conta |

I parametri sono fissati nel codice prima dei run e riportati in
`reports/controls.json` insieme ai risultati. Cambiarli richiede una nuova
versione delle fixture e una nuova misura: non sono stati scelti dopo aver visto
i numeri.

## 8. Sensibilità e falsi positivi

| Metrica | Valore |
|---|---|
| Copie assemblate dalla fixture | 9 |
| Copie rilevate | 9 (100%) |
| Copie persistenti | 9 |
| Condizioni negative | 5 |
| Falsi positivi | 0 |
| Generazioni rilevate | 9 |

## 9. Riproducibilità

Due esecuzioni indipendenti del positivo producono lo stesso hash completo e lo
stesso riepilogo del rilevatore. Il controllo non usa il RNG del mondo: è
deterministico per costruzione. Il run del motore resta riproducibile come in
M1–M4.

## 10. Limiti

1. **Il copiatore è programmato.** Serve a calibrare il rilevatore, non a
   suggerire che la copiatura emerga.
2. **Il criterio richiede assemblaggio simultaneo.** Replicatori per accrezione
   non vengono riconosciuti.
3. **Nessuna ereditarietà.** Le copie sono identiche; le variazioni e la
   selezione sono oggetto di M7.
4. **Una sola forma di copia.** Il controllo copia un solo tipo di struttura.
5. **Soglia `min_size`.** Con strutture più piccole i falsi positivi
   aumenterebbero; il valore è dichiarato, non nascosto.

## 11. Verdetti

**M5: GO.** Il positivo è riconosciuto con sensibilità piena, i negativi non sono
classificati come replicazione, il rilevatore è isolato e riproducibile. Il
risultato più utile è un limite esplicito: il criterio misura l'assemblaggio
template-diretto, non la replicazione in generale.

**M6 non è stata iniziata.** Campagne multi-seed e preregistrazione richiedono
approvazione esplicita.

---

## 12. Correzioni successive alla consegna

Due criticità del rilevatore, entrambe corrette prima di M6.

**1. Le generazioni contavano anche le copie non persistenti.** `max_generation`
era calcolato su tutti i candidati, mentre `min_copies` veniva verificato solo
sui persistenti: una seconda generazione transitoria poteva bastare per la
classificazione. Ora la generazione di una copia è la lunghezza della catena di
**copie persistenti** che la separa dalla struttura originale; se un antenato non
è persistente la catena vale 0 e non contribuisce. Il valore diagnostico su tutti
i candidati resta disponibile come `max_generation_all`, ma non decide.

**2. Il genitore poteva essere nato nello stesso passo.** Il rilevatore cercava
una struttura con la stessa firma fra quelle attive, incluse quelle nate nel
passo corrente: due strutture identiche comparse insieme potevano essere
considerate genitore e figlia. Ora serve `born_step < step`.

Test aggiunti (falliscono sul codice precedente):

- `test_simultaneous_identical_structures_are_not_copies`: due strutture
  identiche nate insieme, adiacenti, non producono alcuna copia candidata;
- `test_transient_second_generation_does_not_classify`: una catena
  template → copia effimera → copia persistente non basta, anche se la
  generazione grezza è 2.

**Impatto sulle misure: nessuno** sui controlli attuali. Il positivo resta 9/9
copie persistenti, generazione 9; i cinque negativi restano a 0 candidate. La
correzione elimina due modi di ottenere un falso positivo che le fixture presenti
non attivavano, ma che una campagna M6 avrebbe potuto incontrare.
