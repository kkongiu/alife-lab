# M7.2 — Distribuzione delle sorgenti ed energia trasmessa per contatto: esperimento fattoriale concluso

**Data:** 16 novembre 2026. **Esito:** test, quattro shard e aggregazione di **320/320 universi PASS**. **Criterio preregistrato sulla diffusione: raggiunto.** **Criterio preregistrato sulla sola geometria delle sorgenti: non raggiunto.**

## Fonti verificabili

- [Protocollo congelato PRIMA del runner: commit 20b145f](https://github.com/kkongiu/alife-lab/commit/20b145f77a244c9257edf3198e8e0ee0c4958b80).
- [GitHub Actions, suite completa e quattro shard + merge: PASS #43885576094](https://github.com/kkongiu/alife-lab/actions/runs/43885576094).
- [Dati grezzi di tutti i 320 mondi e relativi checkpoint, inclusi controlli negativi: artifact #14235120877](https://github.com/kkongiu/alife-lab/actions/runs/43885576094/artifacts/14235120877).
- [PR #30, bozza](https://github.com/kkongiu/alife-lab/pull/30).
- Script eseguibile: [tools/m7_2_energy_distribution.py](../tools/m7_2_energy_distribution.py).
- **Leggi originali M6/M7.1, \`src/\` e \`master\` immutati.** Il nuovo scambio locale è implementato solo nel modulo sperimentale ed eseguito **dopo** ogni passo originale, non è una nuova funzione retroattiva di M6.

## Domanda e ipotesi

M7.1 aveva riscontrato attività energetica sostenuta in mondi alimentati, ma elevata energia di overflow e moltissime particelle senza energia. In M7.2 manteniamo **esattamente uguale l'energia totale generata** e distinguiamo:

1. L'effetto **spaziale** di 16 sorgenti distribuite o concentrate;
2. L'effetto dell'aggiunta di una **regola di trasferimento energetico passivo**, consentito soltanto fra particelle su celle cardinalmente adiacenti.

Il trasferimento è una **nuova scelta di fisica esplicitamente dichiarata**, non una scoperta emergente: ciò che testiamo è come reagisce la chimica sottostante a quella regola. Non studiamo né introduciamo organismi, geni, copie o protocellule.

## Protocollo fissato prima dei dati

**80 nuovi seed indipendenti** \`19001–19080\`, quattro bracci ciascuno, **320 mondi × 600 tick = 192.000 tick-mondo**. Reticolo periodico 24×24; stesse 264 particelle M6 (S0=108, S1=108, S2=28, S3=20), identici ID, posizioni, energie e stato RNG iniziali per i quattro bracci dello stesso seed. Zero legami iniziali, **costo movimento 1**, chimica M6 nativa senza catalisi.

| Braccio | Sorgenti | Trasferimento fra particelle |
|---|---|---|
| \`dispersed_no_transfer\` | distribuite, x/y ∈ {2,8,14,20} | disattivato |
| \`clustered_no_transfer\` | concentrate, x/y ∈ {10,11,12,13} | disattivato |
| \`dispersed_contact_transfer\` | distribuite | attivato |
| \`clustered_contact_transfer\` | concentrate | attivato |

Ogni mondo ha **16 sorgenti × 2 unità/tick × 600 tick = 19.200 unità generate**, capacità per sorgente 12, eccedenza espulsa come \`unabsorbed\`. Le condizioni con sorgenti distribuite e trasferimento **disattivato** utilizzano esattamente la stessa configurazione di \`driven_no_catalysis\` di M7.1 (ma seed nuovi).

### Regola locale di scambio

Alla **fine** di ogni passo standard, si considerano coppie non ordinate di particelle **a contatto cardinale** sul toro. Le coppie vengono ordinate per ID materiale persistente; sono ammesse particelle libere o legate, di qualsiasi specie. Su uno snapshot delle energie, se due vicine differiscono di almeno due unità, si propone il passaggio di **un quanto** da quella più ricca a quella più povera. Ogni proposta può essere accettata solo se il budget residuo del donatore consente la cessione; gli incrementi/decrementi sono applicati simultaneamente, senza ricalcolare i gradienti nella stessa scansione.

Il trasferimento **non consuma RNG** e conserva esattamente la somma delle energie delle particelle, senza modificare ID, specie, legami, posizioni o serbatoi. Ha **costo energetico zero**: è una **diffusione passiva idealizzata**, non pompaggio selettivo, termodinamica completa, metabolismo o trasporto attivo.

**Criterio primario delle sole sorgenti:** senza trasferimento, il regime distribuito deve produrre meno overflow in almeno **60/80** seed appaiati **e** più movimenti nell'ultimo intervallo (tick 501–600) in almeno **48/80**.

**Criterio primario del trasporto:** con sorgenti distribuite, il trasporto deve ridurre il numero di particelle a energia zero al tick600 in almeno **50/80** seed appaiati **e** aumentare i movimenti negli ultimi 100 tick in almeno **48/80**.

Ogni condizione deve essere valutata integralmente, senza cambiare soglie o selezionare altri indicatori dopo i risultati.

## Risultati: trasferimento locale molto efficace, sola distribuzione delle sorgenti ambigua

| Misura, media su 80 mondi per braccio | Distribuite senza trasferimento | Concentrate senza trasferimento | Distribuite con trasferimento | Concentrate con trasferimento |
|---|---:|---:|---:|---:|
| Movimenti, tick 501–600 | **141,1** | 113,5 | **745,3** | 278,2 |
| Nuovi legami, tick 501–600 | 9,65 | 7,19 | **36,35** | 15,28 |
| Particelle a energia zero, tick 600 | 139,55 | 150,69 | **27,53** | 119,28 |
| Monomeri mobili con energia sufficiente, tick600 | 6,38 | 5,04 | **24,13** | 10,40 |
| Energia scartata per overflow, su 19.200 | 11.471 | **9.744** | 9.656 | **9.193** |
| Quota generata **non scartata** | 40,3% | **49,2%** | 49,7% | **52,1%** |
| Gini descrittivo energia per particella, tick600 | 0,951 | 0,957 | **0,523** | 0,913 |
| Universi con almeno un anello nativo semplice al tick600 | 38/80 | 34/80 | **76/80** | 56/80 |
| Numero medio totale di trasferimenti nel mondo, 600 tick | 0 | 0 | **49.249** | 23.981 |

**Precisazione contabile:** la *quota generata non scartata* è \`1 − unabsorbed/injected\`. Include energia trasferita alle particelle e poi eventualmente dissipata **e** l'energia ancora contenuta nei serbatoi. **Non equivale rigorosamente alla quota assorbita dalle particelle.** L'energia media ancora nei serbatoi a tick600 è rispettivamente 127,1; 106,8; 96,6 e 102,2, nell'ordine della tabella.

### Verdetto A — Geometria delle sorgenti senza scambio: \`not_met\`

Senza trasferimento, la condizione distribuita ottiene più movimenti tardivi in **58/80** seed (soglia 48 raggiunta), ma **meno overflow soltanto in 26/80** seed (soglia 60 non raggiunta); in **54/80** seed il regime distribuito scarta addirittura più energia di quello concentrato.

Rispetto alle sorgenti concentrate senza trasporto, distribuire le sorgenti abbassa mediamente di 11,14 il numero di particelle a energia zero e aumenta mediamente di 27,61 i movimenti finali, **ma peggiora di 1.727 unità l'overflow**. Quindi la sola distribuzione spaziale non soddisfa la doppia condizione preregistrata: **più attività non significa necessariamente meno spreco**.

### Verdetto B — Trasferimento passivo su sorgenti distribuite: \`passed\`

A parità di disposizione delle sorgenti, introducendo la diffusione locale:

- **80/80** mondi hanno **meno particelle a energia zero** al tick600 (soglia 50 superata);
- **80/80** mondi hanno **più movimenti** negli ultimi 100 tick (soglia 48 superata);
- **80/80** mondi producono anche **più nuovi legami** negli ultimi 100 tick, misura secondaria.
- Aumento medio appaiato: **+604,16 movimenti** e **+26,7 legami** nell'ultimo intervallo, rispetto al controllo senza trasferimento; quasi **5,28×** i movimenti e **3,77×** i nuovi legami.
- Diminuzione media appaiata: **−112,03 particelle a energia zero** al tick600.
- Riduzione descrittiva della disuguaglianza Gini da ~**0,951 a ~0,523** al tick600, un effetto presente in 80/80 seed.
- Miglioramento nell'overflow: **−1.815,5 unità** per mondo in media, in 65/80 seed.

Questi risultati sono riproducibili e non si devono presentare come effetti emergenti di una membrana: è un **trasporto passivo programmato**. La sua applicazione modifica energia disponibile, moto, contatti e il successivo consumo del RNG globale nei diversi bracci. L'effetto osservato è quello del **regime fisico completo**, non un'identica traiettoria con differenza locale mantenuta infinitamente.

### Interazione rilevante — Geometria × diffusione

**Con trasferimento attivo**, le sorgenti distribuite producono una differenza media di **+467,13 movimenti tardivi** e **+21,08 nuovi legami** rispetto alle concentrate con trasferimento. Hanno inoltre **−91,75 particelle a energia zero** e una forte riduzione del Gini (0,523 vs 0,913). Le sorgenti concentrate conservano un lieve vantaggio nella quota energetica non scartata (52,1% vs 49,7%), ma non nell'accessibilità energetica alle particelle libere.

Di conseguenza, la configurazione che minimizza lo spreco **non coincide** con quella che massimizza l'attività chimica. La geometria delle sorgenti e la diffusione interagiscono fortemente nel modello.

## Integrità, controlli e dati grezzi

- **GitHub Actions PASS:** suite integrale prima dei run, quattro shard prefissati (20 seed × 4 bracci), merge con hash identici del protocollo e copertura 320/320.
- **16 replay da seed**: un seed × quattro bracci per ciascuno shard, con stato finale completo, RNG, contatori dei legami, iniezione, overflow, dissipazione e numero di trasferimenti identici.
- **Contabilità energetica** a tutti i sei checkpoint per tutti e 320 i mondi: \`energy_stored + dissipated + unabsorbed = initial_energy + injected\`.
- I test sintetici verificano la topologia toroidale, il limite energetico del donatore che cede a più vicini, la conservazione esatta dell'energia, l'assenza di RNG consumato, gli stati con nessun contatto e il fatto che l'arm distribuito senza trasferimento usa **la configurazione M7.1 originale**.
- **Controllo incrociato indipendente sul file ZIP originale scaricato:** sono stati ricalcolati localmente i 320 bilanci energetici e le medie dei quattro bracci dai 320 record grezzi; tutte le asserzioni di copertura e i bilanci passano. I risultati 80/80 di movimento, particelle a zero energia e formazione legami sono confermati direttamente dai record.

## Interpretazione scientifica

Un meccanismo esplicito di diffusione locale dell'energia può moltiplicare il turnover chimico e rendere una risorsa energetica accessibile a particelle prima deprivate. **Non è emerso alcun organismo.** Sono presenti aggregati e anelli, ma non è osservata discendenza, informazione ereditaria, autoregolazione energetica selettiva, crescita funzionale o replicazione.

**Limite strutturale del nuovo meccanismo:** scambio a costo zero fra ogni coppia cardinale di particelle (non solo lungo legami), senza riconoscimento di strutture e senza vincoli biologici. Una quota energetica può essere trasferita più volte: 49.249 eventi/600 tick **non significa** 49.249 unità nuove create, dato che l'iniezione esterna rimane fissa a 19.200. La diffusione è intenzionalmente semplificata ed è dichiarata come **nuova fisica esterna**.

## Direzione consigliata — M7.3

La domanda successiva non è se la diffusione generica dia più movimento: M7.2 lo dimostra nelle condizioni studiate. È se **una configurazione materiale specifica** riesce a catturare, condurre o sfruttare l'energia **meglio di controlli abbinati con stessa densità e composizione**, producendo un effetto causale sulla propria persistenza o sulla produzione di altre strutture simili.

Un M7.3 rigoroso dovrebbe confrontare:
1. Energia trasportata su **contatti generici** (M7.2) vs **solo legami chimici**, a parità di energia generata e stesso seed;
2. Aggregati naturali con identica composizione/grado ma topologie diverse; metriche di flusso e sopravvivenza senza selezione post-hoc dei soli casi belli;
3. Controlli controfattuali a contatto e struttura di rete abbinati, senza inserire un replicatore completo;
4. Eventuali risultati di informazione o genealogia **separati** dalle metriche energetiche.

Solo la dimostrazione di un circuito causale tra struttura, approvvigionamento e produzione di altre strutture costituirebbe un progresso verso una dinamica prebiotica interessante; una diminuzione del Gini non basta.
