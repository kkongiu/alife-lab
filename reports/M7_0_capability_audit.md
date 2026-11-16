# M7.0 — Capacità e limiti intrinseci della fisica A-Life M6

**Data:** 16 novembre 2026. **Stato:** audit deterministico completato con **test e GitHub Actions PASS**. Questo documento non è un esperimento di nascita della vita, ma un controllo del **perimetro di possibilità delle regole correnti**.

- [Protocollo fissato prima dell'implementazione: commit `8c73b43`](https://github.com/kkongiu/alife-lab/commit/8c73b434c2f691772ed8614d58888f78a08b6dc9)
- [GitHub Actions PASS: regressioni complete + audit M7.0 #43867854027](https://github.com/kkongiu/alife-lab/actions/runs/43867854027)
- [JSON grezzo e verificabile dell'audit #14226686722](https://github.com/kkongiu/alife-lab/actions/runs/43867854027/artifacts/14226686722)
- [Script eseguibile `tools/m7_0_capability_audit.py`](../tools/m7_0_capability_audit.py)
- M6 fisica originale, `src/` e `master` **mai modificati**.

## Verifiche dirette sulle regole

| Proprietà del modello attuale | Osservazione audit | Implicazione |
|---|---|---|
| Particelle nate / morte | **Nessuna** procedura attiva di nascita o morte durante `World.advance`; un universo arricchito è passato per 120 tick da **264 a 264 particelle**, stessi ID | Un atomo non produce nuovi atomi; la sola copia possibile sarebbe una riconfigurazione materiale usando atomi già esistenti |
| Nascita di informazione ereditaria | **Nessun** genoma/codice informativo con regole di trasmissione esplicite nella configurazione M6 | Non c'è un meccanismo implementato di copiatura dell'informazione genetica; non si può *escludere logicamente* che geometria o composizione influenzino la produzione di pattern simili |
| Catalisi | **0** regole `catalysis` nella configurazione `unfed-6101` | Non ci sono moltiplicatori catalitici nativi in questo scenario, anche se il motore generale prevede un meccanismo di catalisi configurabile |
| Sorgenti energetiche | **0** sorgenti | Sistema simulato senza alimentazione esterna; energia contabilizzata non cresce |
| Energia totale M6 arricchito | **2956 → 2502** in 120 tick, sempre non crescente, per il seed audit 17001 | In assenza di alimentazione, l'energia chimica disponibile si degrada; non si può dedurre un metabolismo autoalimentato |
| Costo energetico del movimento | **0** | L'agitazione casuale del simulatore è in parte un processo esterno alla contabilità energetica |
| Valenza massima | **S0=2, S1=2, S2=1, S3=0** | Un ciclo chiuso di atomi S0/S1 di grado due ha tutti i siti di legame saturi |
| Controllo di saturazione | Anello sintetico S0 di otto membri, **zero** ulteriori slot e **zero** coppie ammissibili alla nuova formazione prima della rottura | Un anello saturo non può reclutare direttamente altri atomi con legami aggiuntivi senza prima rompersi |

### Il test più sorprendente: movimento senza energia

Il test ha creato un universo di controllo con **una sola particella S3 nativa**, una sola modifica alla **condizione iniziale** (`energia iniziale = 0`), mantenendo invariata la probabilità di movimento originale della specie (0,6), l'assenza di alimentazione e le altre leggi M6.

In **128 tick**, la particella ha compiuto **79 movimenti**, pur avendo **energia pari a zero all'inizio e alla fine**. Il movimento resta permesso perché il costo previsto da M6 è zero. Il risultato è una prova concreta di ciò che significa il codice: `movement_cost = 0` e `move_probability > 0` non dipendono dall'energia finché il costo del movimento è soddisfatto.

Questo non è necessariamente un *bug software*; potrebbe essere una scelta deliberata per rappresentare un bagno termico esterno o un movimento browniano idealizzato. Tuttavia, **se vogliamo studiare vita e metabolismo come conseguenze del bilancio energetico**, il movimento a costo zero richiede un'interpretazione fisica esplicita: nel sistema corrente può persistere moto stocastico senza energia chimica contabilizzata.

### Nessuna formazione di nuove particelle: ciò esclude la replicazione?

**No, non in senso assoluto.** È utile distinguere:
- *Replicazione degli atomi*: esclusa nell'evoluzione M6 corrente perché la popolazione resta fissa.
- *Replicazione di un'organizzazione o pattern*: non esclusa dalla popolazione fissa, perché particelle preesistenti potrebbero riorganizzarsi in copie di strutture materiali.
- *Riproduzione con ereditarietà e variazione*: non osservata né implementata come regola nella configurazione originale. Richiede una dimostrazione causale di trasferimento di una proprietà da una struttura all'altra, non solo collisioni fra firme simili.
- *Metabolismo fisicamente sostenuto*: non dimostrato. Senza sorgenti e con dissipazione, l'energia chimica totale è decrescente nell'esperimento; il movimento casuale senza costo non è una fonte energetica per reazioni chimiche.

### Perché questo cambia il percorso del progetto

M6.10–M6.14 hanno stabilito che un reticolo chimico semplice genera **strutture native spontanee e persistenti**. M6.15 testa il feedback locale tra residente e parete ed è coerente con l'assenza di un robusto effetto stabilizzante. Queste osservazioni **non** si trasformano automaticamente in organismi semplicemente aumentando i seed.

Per puntare all'emergere di organismi digitali senza predisporre in anticipo la forma dei replicatori, una futura fase **M7** potrebbe configurare un nuovo mondo (non alterare retroattivamente M6) che introduca almeno:
1. **Energia disponibile e consumabile** legata a reazioni e/o lavoro, separando esplicitamente l'agitazione termica dal metabolismo.
2. **Un ciclo chimico aperto** con risorse e scarti, capace di mantenere stati non all'equilibrio. Le risorse non devono coincidere con un replicatore artificiale già costruito.
3. **Possibili percorsi di catalisi o templating** che possano trasmettere informazione di configurazione senza definire a priori il genoma desiderato.
4. **Controlli negativi di informazione**: rompere il possibile trasferimento causale e verificare se le analogie fra prodotti scompaiono, usando seed nuovi e campioni preregistrati.

Queste sono proposte progettuali; **non sono nuove conclusioni sperimentali**. Qualunque modifica delle leggi dovrebbe essere dichiarata, versionata e tenuta su un ramo distinto rispetto agli studi M6.

## Conclusione

Il sistema M6 sembra già sufficiente a generare **complessità geometrica**, ma non abbiamo evidenze di un meccanismo di **replicazione informativa o auto-mantenimento energetico**. L'audit verifica concretamente popolazione fissa, assenza di catalisi e fonti energetiche nella configurazione, saturazione valenziale degli anelli e movimento possibile anche con energia zero.

Il passo scientificamente interessante non è produrre ancora più anelli: è cercare una connessione **causale fra organizzazione, flusso energetico e trasmissione di informazione**.
