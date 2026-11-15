# M6.4 — Anelli spontanei e collisioni delle firme cicliche

**15 novembre 2026 · Osservazione riprodotta, fisica M6 invariata**

- Protocollo preregistrato prima del runner: [commit `7c34fc0`](https://github.com/kkongiu/alife-lab/commit/7c34fc0b41f67b48a08ef60fdb480b15da039dd3).
- CI eseguita due volte sullo stesso commit: [43743176494 — PASS](https://github.com/kkongiu/alife-lab/actions/runs/43743176494), [43743208606 — PASS](https://github.com/kkongiu/alife-lab/actions/runs/43743208606).
- [Dati grezzi completi di tutti i 24 universi](https://github.com/kkongiu/alife-lab/actions/runs/43743176494/artifacts/14173072897), con episodi, materiali, firme, durata, hash e RNG.
- Nessuna modifica a `src/`, alle leggi, ai vecchi detector, ai risultati M6, o a `master`.

## Domanda

Senza assemblare artificialmente alcuna sonda, gli universi ALife formano **aggregati ciclici chiusi** e quanto persistono? Le firme cicliche del tracker storico, marcate `exact=false`, possono raggruppare strutture differenti in modo sistematico?

## Metodo

Sono partiti da **zero legami iniziali** 24 universi nuovi, con 12 seed (8601–8612) e due densità (200 e 264 particelle). Ognuno evolve per **600 passi**, con chimica, movimento, valenze, RNG ed energia originali M6.

Un anello è una componente connessa di almeno quattro particelle, con numero di legami uguale al numero di particelle e grado di ciascuna particella uguale a due. Non viene introdotta nessuna legge di autocostruzione, né un template.

L'osservatore estrae una **firma esatta della sequenza di specie su un ciclo semplice**, canonica rispetto a rotazioni e inversioni; il tracker esistente mantiene la propria firma approssimata `F:` e **non è stato modificato**.

Un **episodio** è una permanenza continua della *stessa struttura materiale, con gli stessi legami*, e termina anche in caso di rottura seguita da riformazione nello stesso tick. Si conservano gli episodi censurati alla fine del run. Per confronto descrittivo si misurano le catene lineari di quattro particelle; non sono assegnate casualmente al gruppo anelli/catene.

## Risultati

| Misura | Densità 200 (12 universi) | Densità 264 (12 universi) |
|---|---:|---:|
| Universi con almeno un anello | **12/12** | **12/12** |
| Episodi di anello, tutte le dimensioni | **129** | **161** |
| Episodi di anello da quattro particelle | **113** | **131** |
| Aggregati di anello con insieme materiale distinto (sommati per mondo) | **53** | **68** |
| Transizioni osservate catena-4 → anello-4 fra snapshot consecutivi | **108** | **122** |
| Anelli da quattro con episodio di almeno 50 tick | **70** | **79** |
| Durata media degli episodi anello-4 (inclusi censurati) | **106,478 tick** | **96,321 tick** |
| Durata media degli episodi catena-4 (inclusi censurati) | 54,285 tick | 47,174 tick |

**Totale:** 290 episodi di anello, di cui **244 quadrati di quattro particelle**; **149** episodi di quadrati durano almeno 50 tick. **Tutti e 24 gli universi** ne hanno prodotti naturalmente.

La maggiore longevità media descrittiva degli anelli rispetto alle catene **non dimostra che chiudere la catena causi l'aumento**: non sono gruppi sperimentalmente equiparati per età, composizione, energia o storia; inoltre le durate censurate non sono stime di sopravvivenza corrette.

## Scoperta tecnica: collisione reale della firma ciclica storica

I seguenti anelli di quattro particelle sono **non isomorfi come cicli con specie etichettate**, benché abbiano identica composizione 2×S0, 2×S1:

- **Sequenza adiacente:** `S0—S0—S1—S1—(S0)`
- **Sequenza alternata:** `S0—S1—S0—S1—(S0)`

L'attuale funzione `signature()` applica ai cicli un'impronta WL e, in questo caso concreto, restituisce **lo stesso hash `F:29e741479208d9ab2e2c0c346587c098136b265b3182e748582bf7572eef2f77`** per entrambi.

Il nuovo identificatore esatto `C:` distingue invece le due sequenze normalizzando tutte le rotazioni e le inversioni. I test riproducono la collisione su due anelli artificiali **solo a fini diagnostici**, e soprattutto l'osservazione trova **entrambe le varianti realmente emerse** nelle simulazioni naturali, in entrambe le densità.

Questo fornisce un esempio **concreto e riproducibile** di diversità delle strutture cicliche non interamente distinguibile dal tracker precedente. Non si tratta soltanto di una collisione teoricamente possibile.

**Cautela:** la firma WL precedente era già dichiarata `exact=false` dal progetto; non è corretto chiamarla un difetto nascosto o dire che ALife non misurava alcuna diversità. L'avanzamento è un **controesempio specifico, sperimentalmente osservato**, e un metodo esatto separato per gli anelli semplici.

## Limiti e controllo delle false conclusioni

1. **Chiusura di un ciclo ≠ replicazione.** Gli anelli compaiono e persistono, ma non è stata dimostrata la produzione causale di un secondo anello tramite quello precedente.
2. **Saturazione totale del nucleo.** In M6 le specie che compongono un anello di grado 2 hanno valenza massima 2. Un anello intatto non può aggiungere direttamente nuovi legami esterni: per accrescersi deve cambiare topologia o liberare uno slot.
3. **Episodio ≠ organismo.** Un episodio materiale può riformarsi ripetutamente; i dati non identificano metabolizzazione, ereditarietà o un ciclo di vita autonomo.
4. **Transizione da catena:** i 230 casi di catena-4 al tick precedente e anello-4 al successivo indicano una transizione osservabile, non necessariamente una singola reazione di chiusura priva di altri eventi nel tick.
5. **Durata delle catene vs anelli:** il confronto è osservazionale; censura e selezione condizionata impediscono deduzioni causali sulla stabilizzazione.
6. **Reproducibilità:** i due run di replay preregistrati hanno stesso hash finale, RNG, energia, dissipazione e contatori di legame con e senza observer. I 24/24 universi e la regressione `pytest` sono PASS.

## Decisione scientifica

**GO per un nuovo asse di osservabilità:** usare la firma ciclica `C:` esatta per i cicli semplici nei nuovi report e contare episodi materiali con rottura reale. **NON** cambiare retroattivamente la firma `F:` né i risultati già preregistrati; mantenere entrambe le metriche con versioni dichiarate.

**NO GO per l'ereditarietà/M7:** non chiamare gli anelli copie o organismi. Nessuna modifica alle leggi giustificata.

**Prossimo test causale consigliato:** con nuovo protocollo e seed indipendenti, misurare se un anello completamente saturo **protegge la propria sequenza rispetto a una catena comparabile** dopo condizioni controllate, distinguendo geometria, energia, numero di legami, specie, censura e RNG. Un altro possibile asse è verificare se i cicli costituiscono una riserva strutturale che rilascia monomeri durante rotture e ricombinazioni, senza assumere trasmissione informativa.
