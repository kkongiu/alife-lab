# M6.2-E — P2: origine materiale e perturbazioni delle condizioni iniziali

**Data:** 15 novembre 2026 · **Stato:** audit completato, inferenza causale **INCONCLUSIVA**  
**Provenienza:** [issue #4](https://github.com/kkongiu/alife-lab/issues/4), [PR #7](https://github.com/kkongiu/alife-lab/pull/7), [PR #8](https://github.com/kkongiu/alife-lab/pull/8)  
**Esecuzione GitHub Actions:** [43729561383](https://github.com/kkongiu/alife-lab/actions/runs/43729561383)  
**Protocollo congelato prima del runner:** `campaigns/m6_2e/p2_initial_conditions_protocol.json`, commit `41b3b94`  
**Dati:** `campaigns/m6_2e/unfed_6101_ancestry.json` e
`campaigns/m6_2e/p2_initial_conditions_results.json` disponibili come
artefatti dell'esecuzione CI, non sovrascritti nei registri M6.

## 1. Ricostruzione materiale: storia preesistente alla presunta coppia

La ricostruzione osservazionale dei tick 0–771 considera **sei ID fissi**:
- futuri componenti del template 850: `143, 290, 388, 414`;
- futuro seme della candidata 872: `93, 245`.

Il primo **contatto di appartenenza alla stessa componente legata** fra almeno un
ID di ciascun gruppo compare al passo **2**, quindi molto prima della comparsa
dell'ID del template 850.

- Episodi con almeno una connessione fra i due gruppi: **2–166**, **259–263**,
  **307–770**.
- Prima appartenenza di **tutte e sei** le particelle allo stesso aggregato:
  **passo 381**.
- Ultimo intervallo continuo con tutte e sei nello stesso aggregato:
  **542–770**.
- A **771**, rottura del legame `93–414`: divisione e assegnazione degli ID
  strutturali 849 (dimero) e 850 (catena S0 di quattro particelle).
- A **786**, rottura `93–245`; a **792** il legame si riforma e appare il nuovo
  ID 872; a **800** e **835** ulteriori legami portano la candidata alla
  firma semplice `T:(S0:(S0:(S0:(S0:))))`.

Questo è **precursore materiale condiviso + scissione + riassemblaggio**.
Non costituisce una genealogia di copie causalmente mediate da un template.
Il rilevatore v2.1 ha riconosciuto una corrispondenza di firma persistente,
non un genitore causale. Non si può inferire che una copia fedele sia
*logicamente impossibile*, ma il caso osservato non la dimostra.

**Integrità:** la ricostruzione non consuma estrazioni RNG nel callback
osservazionale; il replay fino a 3000 riproduce l'hash M6 originale.

## 2. Protocollo delle perturbazioni, preregistrato prima dell'esecuzione

Dopo aver stabilito il primo incrocio materiale al tick 2, il protocollo
`alife-m6-2e-p2-ic-counterfactual-v1` ha fissato un intervento **al tick 0**,
dopo il collocamento iniziale e prima di ogni reazione. Non sono state
cambiate le leggi del simulatore, le probabilità, la chimica o l'RNG.

- Un braccio originale, senza interventi, con verifica dell'hash congelato M6.
- Un braccio con traslazione delle quattro particelle destinate al futuro
  template; due bracci di controllo con gruppi di quattro `S0` selezionati
  per distanze e densità locale iniziale.
- **16** vettori di spostamento predefiniti; una terna è ammissibile solo se
  tutti e tre i suoi gruppi raggiungono posizioni non occupate. Nessuna
  sostituzione delle traslazioni impossibili dopo la lettura dei risultati.
- Misura primaria: firma esatta nel componente del seme `93–245` **sia al
  passo 835 sia al 845**, senza particelle del futuro template.
- Misure secondarie: coincidenza degli ID della struttura osservata nel
  baseline, connessione del precursore, primo tick di divergenza
  dell'RNG e del componente del seme.

I risultati riguardano **un solo universo selezionato post-hoc**,
non campioni statisticamente indipendenti.

## 3. Risultati riproducibili

| Braccio | Terne valide | Firma al 835 | Firma al 845 | Firma in entrambi |
|---|---:|---:|---:|---:|
| Baseline originale, invariata | 1 | 1 | 1 | 1 |
| Spostamento futuri componenti template | 5 | 0 | 0 | 0 |
| Controllo S0 A | 5 | 0 | 0 | 0 |
| Controllo S0 B | 5 | 0 | 0 | 0 |

**5** terne complete su **16** tentativi (11 scartate per
incompatibilità di occupazione); raggiunta la soglia procedurale
preregistrata di almeno quattro terne.

In tutti gli interventi validi gli RNG hanno iniziato a divergere
prima del passo 835:

- braccio template: primi scostamenti ai passi **2, 3, 2, 4, 1**;
- controllo A: **passo 1** in tutti e cinque;
- controllo B: **passo 1** in tutti e cinque.

Gli esiti al passo 835 non sono quindi confronti con un identico
flusso casuale di reazioni. La perdita del matching anche nei
controlli indica una **sensibilità globale alle condizioni iniziali**,
non un effetto attribuibile in maniera specifica al template.

### Problema di validità rilevato in audit (non nascosto)

I gruppi selezionati automaticamente a tick 0 erano:
- sham A: **42, 100, 172, 417**;
- sham B: **454, 213, 40, 481**.

**Il controllo B contiene la particella 40**, presente nella struttura
finale della candidata originale `40, 93, 245, 477`. Di conseguenza
il controllo B **non è indipendente dall'oggetto misurato** e non
deve essere trattato come controllo negativo rigorosamente neutro.
Anche le particelle 42 e 481 partecipano a un evento locale osservato
al tick 814; ciò ne limita ulteriormente l'interpretazione come
*sham remoto*.

Questa criticità è stata identificata *dopo* l'esecuzione; non sono
stati ricalcolati o sostituiti i gruppi di controllo. La
preregistrazione v1 e i risultati grezzi restano disponibili per
riproducibilità e verifica degli errori metodologici.

## 4. Criteri di prova e decisione

- **GO tecnico:** workflow completato con successo; `pytest`, integrità
  delle repliche, conservazione di particelle/specie/energia e hash originale.
- **GO osservazionale sulla storia comune:** prime connessioni e
  scissione ricostruite, senza modificare gli universi archiviati.
- **NON GO causale:** tutte le condizioni iniziali perturbate
  perdono il match, anche gli sham; flusso RNG diverge precocemente;
  un gruppo di controllo contiene una particella della candidata.
- **Nessun GO a M7**, nessuna evidenza di fedeltà ereditaria
  o seconda generazione e nessuna motivazione sufficiente per chiamare
  `unfed-6101` un organismo.

**Verdetto: `inconclusive_for_causal_replication`.**

## 5. Prossime decisioni scientificamente ammissibili

1. Prima di qualsiasi nuova prova correttiva, fissare un
   **nuovo protocollo versionato** con esclusione esplicita di
   *tutte* le particelle della candidata finale dai gruppi sham;
   usare validità e controllo di occupazione preregistrati. Non
   ritoccare retroattivamente la versione v1.
2. Tuttavia, l'RNG sequenziale del motore crea divergenze già
   al tick 1–4 per un semplice spostamento iniziale. Ripetere
   cambiando solo gli sham produrrebbe ancora un **problema di
   identificazione causale**. Prima di altri run, motivare
   esattamente quali effetti misurare e quale confronto
   può distinguerli dal rumore accoppiato.
3. Strategia che non modifica le leggi: nuovi universi e seed
   **non selezionati in base ai risultati**, con interventi
   preregistrati e controllo statistico sulla frequenza di
   **meccanismi**, non sui singoli hash/percorsi. I controlli
   sintetici M5 restano separati.
4. Un RNG stabile per evento/coppia, anziché un flusso sequenziale
   globale, potrebbe rendere più interpretabili i controfattuali.
   **Ma altererebbe la dinamica del motore** e quindi richiede
   una proposta teorica separata, baseline nuova, golden hash
   invariati con modalità disabilitata e autorizzazione
   esplicita prima dell'implementazione.
5. Per il detector, progettare una **nuova versione analitica**
   che annoti la presenza di un precursore materiale comune
   e registri più possibili genitori invece di sceglierne
   uno arbitrariamente per vicinanza. Questo NON modifica v2
   o v2.1 e non prova da solo causalità.

Una serie di risultati negativi o inconclusivi va conservata:
non si cerca una copia positiva cambiando progressivamente le
regole o le soglie fino a ottenerne una.
