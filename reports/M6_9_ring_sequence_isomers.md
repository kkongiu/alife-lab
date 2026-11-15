# M6.9 — Causalità della sequenza negli isomeri ciclici S0/S1

**Stato:** completato. **Esito preregistrato:** `no_large_sequence_effect_detected_descriptive`; **non** è una dimostrazione matematica dell'assenza di qualsiasi selezione o informazione.

**Protocollo congelato PRIMA dell'implementazione:** [commit `36e9f052`](https://github.com/kkongiu/alife-lab/commit/36e9f05214f86f4f5788beaae5e28cb8af76cfa6), `campaigns/m6_9_isomers/protocol.json`.

**Risultati verificabili:** [GitHub Actions 43762564125 — PASS](https://github.com/kkongiu/alife-lab/actions/runs/43762564125), suite pytest e 100 mondi × fino a 600 tick; [dati JSON di ogni fork e dei mondi senza anelli selezionati](https://github.com/kkongiu/alife-lab/actions/runs/43762564125/artifacts/14181256525).

## Domanda

I due cicli di quattro atomi con due specie `S0` e due `S1` ma sequenze diverse

- **adiacente:** `S0—S0—S1—S1—S0`
- **alternata:** `S0—S1—S0—S1—S0`

sono esattamente distinguibili dal detector ciclico v2, pur condividendo la medesima composizione 2+2. La diversità della sequenza produce un vantaggio dinamico misurabile, oppure è soltanto un'informazione geometrico-composizionale che il sistema non sfrutta in modo efficiente?

## Disegno pre-registrato

50 nuovi seed 9601–9650 × 2 densità = **100 universi naturali inizialmente senza legami**. In ogni mondo selezioniamo **i primi due insiemi materiali distinti** che costituiscono spontaneamente anelli con precisamente 2 S0 e 2 S1 entro i primi 600 tick, senza rimpiazzo dei mondi privi del caso richiesto.

Abbiamo raccolto **132 anelli**: **59** a densità normale (200 particelle), **73** arricchita (264 particelle).

Per ognuno, due cloni dell'identico mondo naturale mantengono tutte le **identità, posizioni, energie individuali, legami, energia globale, RNG iniziale e ambiente**. L'unica manipolazione è una permutazione di due etichette di specie all'interno dell'anello, ottenendo rispettivamente i due isomeri; la disposizione che coincide con il motivo naturale resta identica all'originale. Non vengono introdotti cambiamenti alla fisica e agli ID materiali.

Entrambe le traiettorie evolvono con la M6 originale per 180 tick. Si registra ogni vero evento di legame originale, la sopravvivenza dell'anello e l'isolamento materiale delle quattro particelle.

**Controllo causale forte:** prima della PRIMA rottura spontanea di uno dei quattro legami originari, la chiusura totale e la valenza satura delle particelle dell'anello implicano immobilità e indisponibilità di legami esterni. L'intero stato fisico — eccetto le etichette S0/S1 del ring — **deve** restare uguale, inclusi la sequenza di coordinate di tutte le particelle, energia, legami, RNG e contatori. La prima rottura deve avvenire allo stesso tick nei due cloni. Questo è controllato tick per tick, con fallimento immediato in caso di difformità.

## Risultati

| Misura | Densità normale | Densità maggiore |
|---|---:|---:|
| Anelli naturali 2S0/2S1 selezionati | **59** | **73** |
| Coppie con almeno una rottura del legame originario entro 180 tick | **43** | **54** |
| Coppie senza rottura originale entro 180 tick, censurate | 16 | 19 |
| **Prima rottura perfettamente sincronizzata, o nessuna rottura in entrambi** | **59/59** | **73/73** |
| Anelli adiacenti ancora ciclici al tick 180, fra coppie con rottura | **18/43 (41,86%)** | **20/54 (37,04%)** |
| Anelli alternati ancora ciclici al tick 180, fra coppie con rottura | **18/43 (41,86%)** | **20/54 (37,04%)** |
| Quartetto originario isolato al tick 180, isomero adiacente | 29/43 (67,44%) | 29/54 (53,70%) |
| Quartetto originario isolato al tick 180, isomero alternato | 30/43 (69,77%) | 28/54 (51,85%) |
| Differenza di isolamento adiacente − alternato | **−2,33 pp** | **+1,85 pp** |
| Durata media come anello dal primo break, fra coppie con break, adiacente | 0,3868 frazione dei tick | 0,3780 |
| Durata media come anello dal primo break, fra coppie con break, alternato | 0,3911 | 0,3758 |

La sopravvivenza ciclica al tick 180 è **numericamente identica** nei due isomeri in entrambe le densità, malgrado l'osservazione tick per tick registri qualche discordanza di singoli fork (1 coppia a favore dell'adiacente e 1 a favore dell'alternato, alla densità normale). I confronti sull'isolamento materiale hanno differenze minime e di segno opposto.

La diversa velocità dei monomeri S0 e S1 può diventare rilevante soltanto dopo liberazione di particelle non legate; inoltre S1 può legarsi a S2 mentre S0 no. Quindi la conclusione **non** è che la sequenza delle specie sia matematicamente irrilevante, ma che non emerge un **grande vantaggio coerente** nel presente esperimento.

**Decisione congelata**: almeno 25 coppie selezionate e 20 coppie con rottura per densità; cercare differenze di almeno 15 punti percentuali dello stesso segno in entrambe le densità su sopravvivenza dell'anello o isolamento originario, oppure dichiarare `no_large_sequence_effect_detected_descriptive` quando tutte e quattro le differenze assolute sono ≤10 punti percentuali. **Questa seconda condizione è soddisfatta.** Non usiamo p-value per fork correlati.

## Integrità e limiti

- Tutti i 100 mondi sono inclusi, anche se non forniscono due anelli validi. Tutti i 132 fork, incluso l'esito nullo e le coppie censurate, sono nel JSON; 97 hanno avuto rottura originaria.
- I test sintetici comprendono il caso con nessuna rottura (`p_break=0`), una rottura immediata (`p_break=1`) e la verifica di equivalenza delle traiettorie senza osservatore.
- I due isomeri hanno esattamente la medesima composizione e differiscono per l'ordine dei due atomi S0/S1, non per quantità totale, valenze iniziali, energia globale o geometria.
- La permutazione di etichette di specie è una **perturbazione artificiale delle condizioni iniziali**. Due anelli nello stesso mondo non sono due universi indipendenti. Un lieve effetto può essere non identificabile per dimensione del campione.
- **Nessuna evidenza di ereditarietà, selezione evolutiva o vita** deriva da questa prova. Una firma canonica esatta identifica la diversità della sequenza, non un codice biologico capace di perpetuarsi.
- Nessun cambio in `src/`, nelle leggi fisiche, negli altri risultati o in `master`; PR rimane draft.

## Prossima direzione

Per evitare di ripetere varianti senza segnale di un semplice anello 4, la nuova osservazione dovrebbe salire di scala: **anelli più grandi possono racchiudere regioni della griglia e intrappolare particelle libere?** È un fenomeno geometricamente falsificabile e potenzialmente simile a una compartimentazione, ma non va confuso con una membrana biologica.
