# M7.5 — Aggregati nativi con legami persistenti: prima crescita coerente preferenziale, NON auto-mantenimento

**Data:** 16 novembre 2026. **Stato:** campagna preregistrata completa, 320/320 mondi sorgente e 960 fork, tutti gli shard e test **PASS**. **Endpoint primario preregistrato di crescita coerente: PASS. Endpoint secondario di sopravvivenza dei legami originali: NON RAGGIUNTO.**

## Tracciabilità

- [Protocollo congelato PRIMA della scrittura del runner e prima dei risultati: commit `7bcbe0e`](https://github.com/kkongiu/alife-lab/commit/7bcbe0ec5f30657dc5f58d795d3fb3c428b9a463).
- [GitHub Actions: regressioni complete, 8 shard, aggregazione e completezza 320/320 — PASS #43963759908](https://github.com/kkongiu/alife-lab/actions/runs/43963759908).
- [Artefatto originale, tutti i 320 mondi, 960 fork, inclusi i risultati negativi: #14275033943](https://github.com/kkongiu/alife-lab/actions/runs/43963759908/artifacts/14275033943).
- [PR #33 in bozza](https://github.com/kkongiu/alife-lab/pull/33); [codice `tools/m7_5_mature_feedback.py`](../tools/m7_5_mature_feedback.py).
- Nessuna modifica alle leggi `src/`, agli studi M6–M7.4 o a `master`.

## Perché cambiare la selezione rispetto a M7.4

M7.4 selezionava la prima struttura nativa con 3–10 atomi e almeno due legami. **148/160** risultati erano catene da tre particelle, nate intorno al tick2: avevamo controllato strutture troppo piccole e giovani per valutare una topologia energetica estesa.

M7.5 preregistra, per nuovi seed non sovrapposti a quelli degli esperimenti precedenti, criteri di origine non dipendenti dagli esiti futuri:

1. Universo originale con 264 particelle native, 24×24 periodico, movimento con costo 1, 16 sorgenti esterne distribuite, legami reversibili M6, nessun legame inserito artificialmente, nessuna catalisi o replicatore.
2. Esaminare i tick 1–500 dello stato **senza trasferimento**. Dall'istante 120, prendere la **prima** componente massimale di 5–16 atomi e almeno 4 legami nativi, con almeno un membro che abbia ancora capacità di formare un legame.
3. Richiedere almeno **due legami materiali originali con un'età verificata di almeno 20 snapshot consecutivi**, azzerando l'età se il legame si spezza anche nel caso di ricostituzione nello stesso tick.
4. Se più candidati compaiono allo stesso tick, scegliere quello con la tupla di ID materiali numericamente minore. Un solo aggregato per seed, senza scegliere in funzione del successivo successo.
5. Eseguire il fork dello **stesso identico mondo** in tre bracci (senza conduzione, conduzione lungo i legami nativi, conduzione su ogni contatto cardinale) per **120 tick**. Il trasferimento è una regola sperimentale già definita in M7.3, non un metabolismo spontaneamente inventato dall'aggregato.

**La definizione di età riguarda almeno due legami originali**, non la permanenza dell'intero componente nella stessa configurazione per 20 tick. Questo limite fa parte del protocollo e non deve essere nascosto.

### Endpoint registrati prima dei nuovi dati

**Primario — crescita coerente:** a 120 tick, tutti gli ID materiali originali devono appartenere a **un'unica componente connessa contenente almeno un nuovo ID**. Sul confronto appaiato `bond_only` vs `no_transfer`, con almeno 40 seed selezionati e 25 coppie discordanti, almeno **2/3 delle discordanti** devono favorire la conduzione.

**Secondario — persistenza:** nessuno dei legami materiali originali deve aver subito un reale evento di rottura nei 120 tick, anche se in seguito riformato. Stessa soglia minima di campione e quota favorevole.

Eventi di nuovi legami che coinvolgono gli ID sorgente, crescita a qualsiasi tempo, trasferimento energetico interno/al confine e formazione globale di legami sono misurati **separatamente**; non sostituiscono l'endpoint primario dopo l'osservazione.

## Campione realmente osservato e suo limite

- **320/320 universi selezionati**, zero risultati esclusi.
- Tutte le strutture erano già ammissibili **al tick120**, cioè il primo tick permesso dal protocollo: la distribuzione dei tempi di selezione è quindi troncata dalla soglia inferiore, non dimostra un'età del componente di 120 tick.
- Dimensione media del componente: **7,1844 atomi**; media di **6,0031 legami con almeno 20 tick osservati**.
- **247/320** strutture di 5–8 atomi, **73/320** di 9–16.
- **Tutti i 320 aggregati selezionati sono alberi chimici**, con zero cicli. Il campione non permette di confrontare reti cicliche con catene o alberi; la selezione deterministica del primo candidato lessicografico può favorire le strutture più comuni. Un confronto con anelli va progettato su seed nuovi, non ricavato da questi.

## Esito M7.5

| Esito su 320 fork del medesimo aggregato | Nessuna conduzione | Conduzione solo sui legami | Diffusione su tutti i contatti |
|---|---:|---:|---:|
| Crescita coerente al tick120 | **28** | **51** | **111** |
| Crescita coerente in almeno un tick | 49 | 74 | 174 |
| Nessun legame originale mai rotto | **89** | 86 | 83 |
| Nuovi legami incidenti al materiale originale, media | 0,4000 | 0,5312 | **1,2250** |
| Nuovi legami incidenti PRIMA di una rottura originale, media | 0,1094 | 0,2125 | **0,5813** |
| Nuovi legami globali nei 120 tick, media | 20,0188 | 27,5938 | **57,0031** |
| Trasferimenti energetici su legami originali, media | 0 | **131,975** | 216,5531 |
| Energia trasferita passivamente dall'esterno agli ID originali, media | 0 | 4,6813 | 83,7719 |
| Energia trasferita passivamente dagli ID originali verso l'esterno, media | 0 | 3,8875 | 125,5594 |

Il trasferimento **interno** non aggiunge energia complessiva all'insieme di atomi originali. Gli ultimi due dati misurano esclusivamente il **passaggio passivo attraverso il confine** dell'insieme di ID, senza confonderlo con iniezione diretta delle sorgenti, formazione/rottura dei legami e dissipazione. L'energia può transitare più volte e il conteggio riguarda **eventi di cessione di un quanto**, non energia nuova creata.

### Verdetto A — Crescita dello stesso aggregato: `passed`

Nel confronto appaiato `bond_only` vs `no_transfer`:

| Esito della coppia di fork | Seed |
|---|---:|
| Crescita soltanto con conduzione | **41** |
| Crescita soltanto senza conduzione | **18** |
| Crescita in entrambi | 10 |
| Crescita in nessuno | 251 |

**41/59 = 69,49%** dei casi discordanti favoriscono la conduzione, oltre il limite preregistrato di **66,67%**. Le 59 coppie discordanti superano la numerosità minima di 25 e i 320 seed superano il minimo di 40.

La differenza assoluta di crescita al tick120 è **51/320 − 28/320 = +7,19 punti percentuali**. Questo è il primo endpoint del progetto che raggiunge una soglia fissata prima dei dati riguardante la **crescita connessa della stessa coorte materiale naturale** anziché i soli nuovi legami globali.

La soglia è però superata con un margine relativamente piccolo (**41 successi favorevoli contro una soglia intera minima di 40 su 59 discordanti**). **Va replicato su seed nuovi con protocollo invariato**, non proclamato prova di auto-organizzazione biologica.

### Verdetto B — Sopravvivenza dei legami originali: `not_met_or_underpowered`

Nel confronto sulla mancata rottura di qualsiasi legame originario:

- **60** seed favorevoli alla conduzione;
- **63** favorevoli al controllo;
- **26** dove entrambi conservano i legami;
- **171** dove entrambi registrano una rottura.

Quindi **60/123 = 48,78%** delle discordanti favoriscono la conduzione, ben lontano dalla soglia dei due terzi. Con 123 casi discordanti non è un problema di mancato raggiungimento del limite minimo del campione, ma di **criterio non soddisfatto**.

Alcune strutture crescono anche dopo aver perso e eventualmente ricostituito uno o più legami originali. L'audit esplorativo del file grezzo mostra che, tra le crescite a tick120, **14/28** nel controllo e **22/51** nella conduzione mantengono tutti i legami originali senza rottura per i 120 tick. Il requisito combinato *crescita e sopravvivenza* è **post-hoc descrittivo**, non un nuovo criterio di successo.

### Controllo di dimensione (esplorativo, non confermativo)

- **5–8 particelle**: 33 confronti discordanti favorevoli ai legami contro 15 favorevoli al controllo (48 discordanti).
- **9–16 particelle**: 8 contro 3 (11 discordanti).

Entrambi i gruppi hanno il medesimo segno descrittivo, ma nel secondo ci sono soltanto 11 discordanti. Non è lecito sostenere un vantaggio confermato dipendente dalla dimensione o utilizzare sottogruppi per selezionare nuovi criteri a posteriori.

## Qualità del risultato

- GitHub Actions: tutti i test PASS, otto shard prefissati da 40 seed ciascuno, esatti 320/320 seed con stesso SHA del protocollo e nessun risultato nullo escluso.
- **Otto sham replay** del primo stato selezionato di ogni shard riproducono il braccio senza conduzione senza osservatore dei legami, con hash materiale, RNG e energia identici.
- Lo script del nuovo esperimento verifica ad ogni fork che i tre mondi partano con identici **hash del mondo completo, stato RNG, energie e legami**; i primi eventi di rottura originale devono coincidere tra tutti i bracci.
- **Verifica indipendente del file ZIP GitHub originale**: ricontati 320 seed, 960 risultati di fork, gli esatti 41/18/10/251 per la crescita e 60/63/26/171 per la persistenza; controllate età di tutti i legami selezionati, le condizioni di valenza, i cinque checkpoint di ogni fork, il bilancio degli scambi passivi e l'identità dei primi eventi di rottura. Tutti i controlli effettuati concordano con i risultati della CI.

## Interpretazione

In una simulazione con conduzione energetica **deliberatamente abilitata** sui legami chimici, gli aggregati che spontaneamente possiedono più legami persistenti hanno maggior probabilità di risultare **cresciuti coerentemente** dopo 120 tick rispetto a copie equivalenti prive della conduzione. Questo è un **effetto del regime fisico sul comportamento della stessa coorte**, confermato dall'endpoint preregistrato.

**Non dimostra:**
- Mantenimento attivo dei vecchi legami: il secondo endpoint è fallito.
- Che l'energia attraversi la rete per uno scopo interno o sia usata selettivamente: il trasporto è generico e predefinito.
- Una struttura ciclica, una membrana o una protocellula: **tutte le sorgenti sono alberi, non anelli**.
- Metabolismo, ereditarietà, riproduzione o un organismo vivente: la crescita di una componente con ID originali persistenti non equivale alla generazione di un discendente.

È inoltre impossibile attribuire direttamente ogni differenza a un singolo evento fisico locale quando le traiettorie future consumano flussi RNG globali differenti. Il confronto resta causale per **il regime di conduzione inserito nel simulatore**, non per un meccanismo biologico isolato.

## Direzione M7.6 più rigorosa

La prossima prova scientifica dovrebbe essere una **replica confermativa con nuovi seed** della crescita delle reti arboree con almeno due legami invecchiati, **stesso identico criterio M7.5**, stesso numero di tick e stessi endpoint. In parallelo, ma come studio distinto e preregistrato, servirebbe un **campione di anelli nativi** e controlli per composizione/valenza/topologia, evitando di assumere che reti e cicli si comportino allo stesso modo.

Il passaggio successivo non consiste nello scegliere un organismo digitale e inserirlo nel mondo, ma nel verificare se il modesto vantaggio di crescita sia stabile, poi se esista una fonte di informazione trasmissibile a un secondo aggregato.
