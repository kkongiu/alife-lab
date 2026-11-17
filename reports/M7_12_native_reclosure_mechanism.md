# M7.12 — Le richiusure native degli anelli si spiegano con contatto ripetuto e probabilità chimica ordinaria

**Data:** 17 novembre 2026. **Stato:** campione di **640 universi nuovi** terminato, **16/16** shard e regressioni **PASS**. La verifica osservativa sul collegamento fra una vera formazione chimica ed un'effettiva coppia candidata di M6 è **PASS**: 0 eventi FORM senza vera candidatura. La frequenza per tentativo è compatibile con la probabilità nativa, senza aggiungere alcun meccanismo speciale di recupero.

## Tracciabilità

- [Preregistrazione, commit `abf426b`, PRIMA del runner e degli esiti](https://github.com/kkongiu/alife-lab/commit/abf426b6688c78b33efad29ac67920057dfb5ea1).
- [CI principale #44176318607 — regressioni, 16 shard, 640/640 seed: PASS](https://github.com/kkongiu/alife-lab/actions/runs/44176318607).
- [Dati grezzi completi, artifact #14369832681](https://github.com/kkongiu/alife-lab/actions/runs/44176318607/artifacts/14369832681).
- [Codice osservazionale `tools/m7_12_native_opportunity_audit.py`](../tools/m7_12_native_opportunity_audit.py).
- [PR #40, bozza](https://github.com/kkongiu/alife-lab/pull/40).
- Nessuna modifica a `master`, alle funzioni native `src/alife`, alla fisica, alla chimica, al selettore M7.11, né ai precedenti protocolli M6–M7.11.

## Disegno: osservare il tentativo, non inferirlo dal legame finale

Il primo anello nativo spontaneo di 4/6/8 particelle (stessa selezione M7.11 invariata, prima componente chimica ciclica massimale con almeno 20 snapshot di legami inalterati, t≥120 fino a t600) è ricostruito in ciascuno di **640 nuovi mondi**, seed numerici `30001–30640`; tutti i casi senza anelli sono conservati.

Si clona lo stesso microstato, si apre soltanto il primo legame originale in ordine lessicografico e si restituisce **tutta** la sua energia immagazzinata agli estremi, senza dissipazione extra o uso di RNG, come nel controllo M7.11. L'evoluzione successiva è **120 normali tick M6** con la consueta conduzione M7.3: niente spostamenti artificiali, catalisi, tassi modificati o nuova chimica.

La differenza da M7.11 è il **nuovo osservatore non invasivo**: durante ciascun passo nativo, e soltanto fino alla prima vera formazione del legame o alla prima rottura di un altro legame originale, un wrapper temporaneo registra quando l'iteratore **originale** `alife.chemistry._candidate_pairs` consegna davvero la coppia tagliata alla lotteria nativa di formazione. Il wrapper restituisce **esattamente** la stessa sequenza di indici, senza estrarre numeri casuali o cambiare soglie. Ogni vero evento `BondEvent(kind='form')` deve avere avuto un candidato reale in **quello stesso passo**. Dopo il passo si ripristina la funzione originale.

In parallelo si misurano, per ogni passo ancora a rischio, l'adiacenza geometrica e l'ancoraggio dei due estremi agli altri legami originali. In un controllo distinto, sono eseguiti **32** sweep chimici sperimentali a geometria congelata usando la lotteria accoppiata M7.8; sono prove ripetute **sullo stesso stato**, non 32 mondi indipendenti e non passi nativi.

## Criteri prestabiliti

**Verifica primaria del meccanismo nativo (non un test di vita o di riparazione attiva).** Almeno 40 mondi con anelli, almeno 100 vere candidature della coppia tagliata, almeno il 95% delle reali formazioni della coppia deve essere preceduto da una candidatura nell'identico passo. È essenzialmente un **test di integrità dell'osservatore e di completezza della spiegazione tramite la chimica originale**: il successo non rappresenta una scoperta indipendente di nuove leggi.

**Frequenza descrittiva.** Dividere il numero di veri eventi di formazione iniziale della coppia per il numero di candidati osservati prima della prima chiusura o censura; confrontare il valore con la probabilità nativa fissata `formation_probability=0.05`. La fascia descrittiva prestabilita è 3–7%, con almeno 100 tentativi. L'intervallo di Wilson al 95% assume approssimativamente tentativi indipendenti: le traiettorie RNG globali e la censura al primo successo limitano il significato statistico.

## Risultati finali sui 640 mondi originali

| Misura | Valore |
|---|---:|
| Universi originali | **640/640** |
| Primi anelli spontanei con età sufficiente | **627/640** |
| Mondi negativi conservati | 13 |
| Anelli a 4, 6, 8 membri | **541 / 74 / 12** |
| Richiusure native dello stesso legame PRIMA di altre rotture originali | **437/627 = 69,70%** |
| Passi complessivi precedenti a prima richiusura o prima censura | **17.993** |
| Vere candidature originali della coppia tagliata nello stadio nativo di formazione | **9.049** |
| FORM reali del taglio mentre la coppia era ancora a rischio | **442** |
| FORM reali senza una vera candidatura M6 | **0** |
| Rapporto FORM / candidature | **442/9.049 = 4,8845%** |
| Frequenza fisica originale M6 per candidato ammissibile | **5,0000%** |
| Intervallo Wilson approssimativo al 95% | **4,46–5,35%** |
| Tempo a rischio con estremi ancora adiacenti | **100%** |
| Tempo a rischio con estremi ancora ancorati ai rimanenti legami originali | **100%** |
| FORM del target in 627×32 tentativi chimici a geometria congelata (controfattuali, non nativi) | **999** |

**Perché i FORM a rischio sono 442 ma le richiusure valide 437?** Nel criterio di richiusura M7.11 un evento su un altro legame originale **nello stesso tick** invalida il recupero. Lo scanner delle candidature conta comunque la FORM reale. Nessuna delle 442 FORM è avvenuta senza un candidato nativo.

L'equivalenza `4,88%` vs `5,00%` non è un'uguaglianza matematica garantita; rientra però nell'intervallo prestabilito e nell'intervallo approssimativo. **Non richiede** un bonus speciale per il materiale danneggiato: il motore M6 testa normalmente la coppia adiacente come qualunque altra coppia compatibile di particelle con energia sufficiente.

### Geometria e chimica ordinaria

Il motivo per cui la coppia ha molte possibilità di reagire non è che l'anello «riconosca» la mancanza del legame:

- Il primo taglio di un anello semplice lascia ancora un **cammino collegato** che unisce i suoi due estremi: non sposta le particelle.
- Nei **17.993** passi ancora osservati prima del primo target FORM o della censura, i due ID tagliati sono rimasti **adiacenti** e ciascuno era **ancorato** ad almeno un legame originale superstite. La fisica nativa non richiede che i due estremi si cerchino.
- Solo in **9.049/17.993** passi la coppia risultava effettivamente candidata alla formazione nello stadio chimico M6. Il resto può essere escluso per l'energia disponibile, la valenza o la chimica nel momento del tentativo, pur conservando l'adiacenza.
- Per ciascuna vera candidatura, il tentativo segue la normale soglia M6 del **5%**. Ripetere tale possibilità per molti tick rende frequente la chiusura.

I 32 tentativi addizionali a geometria congelata sono un controfattuale sperimentale accoppiato, non una normale evoluzione `World.advance`, e non devono essere aggregati ai 9.049 veri tentativi nativi per gonfiare il campione.

## Integrità del risultato

- Il workflow ha superato l'intera suite prima di avviare i 16 shard e ha fuso **esattamente 640** record, inclusi i 13 fallimenti di selezione.
- Primo seed con anello di ogni shard riprodotto, **senza wrapper né osservatore aggiuntivo**, per 120 tick, con hash completo e RNG finali esattamente uguali alla traiettoria osservata. L'instrumentazione non consuma valori casuali.
- Ogni ramo usa lo stesso motore di energia M7.3 e le stesse soglie fisiche M6, senza cambiare la funzione originale sul disco. Il wrapper è limitato a un singolo passo e ripristinato immediatamente.
- Il ledger completo resta valido dopo l'apertura energeticamente conservativa e a fine traiettoria; nessun evento chimico è stato inferito solo dalle fotografie del grafo.
- L'unità statistica per la frequenza dei mondi rimane **un seed nativo**, 640 mondi. Le 9.049 candidature e i 20.064 sweep chimici congelati sono esposizioni dipendenti entro questi mondi.

## Conclusione

**La richiusura frequente degli anelli M7.11 è compatibile, nei dati osservati, con la normale probabilità chimica e con il fatto che i due estremi restano in contatto geometrico.** Non osserviamo alcun evento di formazione del taglio che richieda una speciale regola di riparazione.

Si tratta di una spiegazione di **meccanismo fisico interno al modello** e di una verifica del rilevatore nativo, non di una dimostrazione formale che non possa mai emergere una rete con riparazione selettiva.

M7.13 sfrutta questa conoscenza per chiedere qualcosa di diverso: un precedente episodio di danno modifica, sullo stesso materiale originale e con un secondo bersaglio scelto in anticipo, la capacità di affrontare una **seconda** perturbazione? Il test deve evitare completamente di selezionare soltanto i sopravvissuti e distinguere la perdita del legame dalla mera riallocazione dell'energia. Un eventuale miglioramento sarebbe comunque prova di effetto storico del trattamento, non di memoria biologica senza ulteriori controlli.
