# M6.2-E — Audit controfattuale esplorativo di `unfed-6101`

Data: 2026-11-15 · PR: #3 · Stato: **verificato su GitHub Actions**  
Script: `tools/counterfactual_unfed6101.py` · Evidenza JSON: artefatto
`m6-2e-unfed-6101-counterfactual` della run
[43722026211](https://github.com/kkongiu/alife-lab/actions/runs/43722026211).

## Domanda e perimetro

L'unico candidato persistente osservato in M6.2-E dimostra una copia causalmente
indotta dal presunto template oppure può nascere senza la presenza di quel template
nella posizione originale?

**L'evento è stato selezionato *dopo* aver osservato i risultati.** Le prove sono
esplorative e non preregistrate; non forniscono una frequenza di replicazione
né una stima di significatività.

Non sono state modificate le leggi dell'universo, M6, M6.2-E, le relative firme
o il rilevatore v2 preregistrato. Il replay è verificato contro una clonazione
completa di particelle, legami, energia e stato RNG. Le perturbazioni sono
traslazioni esterne al motore, applicate solo a cloni del mondo.

## Evento originale verificato

| Misura | Valore |
|---|---|
| Universo | `unfed-6101` |
| Intervento prima della nascita | passo 791 |
| Nascita della candidata | passo 792 |
| Prima firma identica | passo 835 |
| Persistenza controllata | passo 845 |
| Template | struttura 850, particelle 143, 290, 388, 414 |
| Figlia | struttura 872, dimero iniziale 93, 245 |
| Componenti della figlia al matching | 40, 93, 245, 477 |
| Firma | `T:(S0:(S0:(S0:(S0:))))` |
| Controllo remoto omologo | struttura 305 |
| Replay baseline | hash completo e RNG coincidono |

Le due strutture al matching non condividono particelle. La candidata è
una catena omogenea di quattro `S0`: la firma, per quanto esatta come
isomorfismo, **non codifica una sequenza chimica diversificata**.

Nel registro `runs/m6/unfed/seed-6101/lineage.jsonl`, prima del passo 792,
**20 identificativi distinti** hanno già avuto quella stessa firma almeno una
volta (26 eventi). Queste ricorrenze non sono necessariamente indipendenti
e non equivalgono a 20 nascite autonome, ma dimostrano che la forma non è rara
nel senso di essere apparsa una sola volta.

## Metodo di perturbazione

Partendo dallo stato verificato al passo 791:

1. **Baseline:** nessun cambiamento, il mondo prosegue fino al passo 845;
   il risultato riprodotto deve essere identico a quello senza clonazione.
2. **Spostamento del template:** le particelle del componente 850 sono
   traslate rigidamente verso posizioni lontane e libere; ogni particella,
   specie, legame, energia e lo stato RNG sono conservati.
3. **Controllo remoto:** si applicano traslazioni prefissate analoghe a una
   struttura con *la stessa firma*, ma lontana dalla candidata (ID 305).
4. Si controlla se le due particelle fondatrici della candidata (93, 245)
   appartengano ancora a un componente con la firma originale ai passi 835 e
   845; si verifica nuovamente l'identità energetica.

Le traslazioni sono enumerate nel codice prima dell'esecuzione e quelle che
colliderebbero con altre particelle sono escluse, non sostituite scegliendo i
risultati favorevoli. I numeri di tentativi riusciti sono quindi diversi.

## Risultati

| Braccio | Spostamenti validi | Firma al passo 835 | Firma al passo 845 |
|---|---:|---:|---:|
| Baseline intatta | 1 | 1 | 1 |
| Template spostato | 3 | 2 | 2 |
| Controllo remoto spostato | 4 | 4 | 2 |

La baseline conserva esattamente traiettoria e RNG originali. **In due
perturbazioni valide, il componente figlio raggiunge ancora la firma anche
senza il presunto template nella posizione iniziale.** La candidata è quindi
compatibile con un assemblaggio che non richiede quella specifica vicinanza
durante l'intera fase di formazione.

Il fatto che anche il controllo remoto possa influire sull'esito di persistenza
indica che le perturbazioni possono deviare il percorso globale; la nostra
simulazione usa un RNG sequenziale e le nuove collisioni/coppie reattive possono
cambiare la quantità di estrazioni future.

## Interpretazione e limiti

- Non abbiamo evidenza che il template abbia *guidato* l'assemblaggio. La
  ricorrenza pregressa della stessa firma ne indebolisce ulteriormente
  l'interpretazione come copia informativa.
- **Non è una dimostrazione di indipendenza causale assoluta.** Gli interventi
  sono pochi, il caso è selezionato *post hoc* e gli spostamenti possono avere
  effetti globali indiretti.
- Non equivale a un controfattuale fisico spontaneo: trasportare a distanza
  un aggregato legato non è permesso dalle leggi M6.
- Una differenza tra un braccio e l'altro dimostrerebbe sensibilità
  alla perturbazione, **non automaticamente replicazione**.
- La coincidenza della firma di un semplice omopolimero non misura
  fedeltà ereditaria né evoluzione darwiniana.

## Verdetto

**Audit tecnico: GO** — workflow completato, test `pytest` superati,
replica baseline e verifica di invarianti riuscite. Le evidenze JSON sono
archiviate nell'esecuzione GitHub Actions indicata sopra.

**Replicazione causale: NON DIMOSTRATA.** L'evento non è una ragione sufficiente
per procedere a M7. Trattare il matching come *ricorrenza strutturale*
e non come discendenza riproduttiva, fino a nuovi esperimenti indipendenti.

Prossimo livello scientificamente utile: osservare **informazione variabile
trasmessa** (sequenze o topologie non banali), con controlli causali e
un disegno preregistrato *prima* di guardare nuovi risultati. Le modifiche
alla chimica rimangono una decisione separata.
