# M6.2-E P0/P1 — Tracciamento osservazionale di `unfed-6101`

**Data:** 2026-11-15 · **Stato:** esperimento osservazionale verificato in GitHub Actions  
**Issue:** [#4](https://github.com/kkongiu/alife-lab/issues/4) ·
**PR:** [#6](https://github.com/kkongiu/alife-lab/pull/6) (stacked su PR #1)  
**Workflow verificato:** [43724019476](https://github.com/kkongiu/alife-lab/actions/runs/43724019476)  
**Dati grezzi:** artefatto `m6-2e-unfed-6101-particle-trace`
([JSON da GitHub Actions](https://github.com/kkongiu/alife-lab/actions/runs/43724019476/artifacts/14165772490)).

## Scopo, condizioni e limiti

Scomporre l'unica corrispondenza di firma persistente di M6.2-E in
**eventi fisici effettivi**, anziché equiparare prossimità e somiglianza a
discendenza. Risultato osservazionale, **non** esperimento causale
randomizzato; nessuna nuova legge chimica o probabilità introdotta.

- Universo: `unfed-6101`, configurazione/seed e hash congelati da M6.
- Timeline campionata ad **ogni tick da 770 a 846**, inclusi.
- Observer: tracker di componenti, particelle selezionate, posizioni,
  energia, firma, legami, distanza e prelievi RNG.
- Gli eventi di reazione sono catturati dall'hook già esistente
  `world.event_sink`. `BondEvent.step=t` è l'evento nella transizione
  che termina con la fotografia del tick `t+1`.
- L'analisi cattura tutti i conteggi di eventi di legame per tick e
  dettagli degli eventi entro raggio 3 dalle otto particelle seguite.
- Il successivo replay fino a 3.000 passi ha prodotto **l'identico hash
  integrale M6**; l'osservazione non consuma RNG.
- Controlli di validità e regressioni del detector `v2.1` in CI: pass.

## La scoperta centrale: precursore comune

Al **passo 770**, **prima** dell'esistenza dei due identificativi di
struttura che il v2 mette in relazione, le particelle della futura
struttura template (143, 290, 388, 414) e le due particelle fondatrici
della candidata (93, 245) sono **già connesse in un'unica struttura
di sei particelle**.

Legami a 770 (ID particellari):

```text
93—245
 |
414—290—143—388
```

**Il disegno testuale non rappresenta necessariamente la geometria**
del reticolo; rappresenta solo gli spigoli. I legami verificati erano:
`93–245`, `93–414`, `143–290`, `143–388`, `290–414`.

Al **passo 771** si rompe `93–414`, separando:
- il frammento di quattro particelle che il tracker denomina
  **struttura 850** (lineage 568);
- il dimero `93–245`, denominato **struttura 849** (lineage 735).

Non si tratta quindi di un template originale e di una figlia
indipendente: **sono frammenti di un precursore condiviso**.
I lineage del tracker descrivono la **continuità materiale**, non
un albero biologico di generazione.

## Sequenza delle reazioni locali

| Tick osservato | Reazione | Lettura |
|---:|---|---|
| 770 | — | Precursore di **6 particelle**, già contenente i futuri frammenti |
| 771 | rottura **93–414** | Split; appare il template 850 e il dimero 849 |
| 786 | rottura **93–245** | Il dimero gemello viene distrutto |
| 792 | formazione **93–245** | Ricompare il dimero; tracker assegna **nuova struttura 872** |
| 794 | rottura **40–477** | Dissociazione di un altro legame preesistente |
| 800 | formazione **93–477** | La candidata 872 cresce a tre particelle |
| 814 | rottura **42–481** | Evento locale, ma **non** incidente sulle otto particelle monitorate (distanza minima 3) |
| 835 | formazione **40–477** | La candidata raggiunge quattro particelle, firma `S0–S0–S0–S0` |
| 845 | nessuna modifica rilevante alla firma | La stessa struttura rimane persistente |

La distanza minima tra template 850 e frammento/futura candidata,
nel reticolo toroidale, è **1** ai passi 771, 792, 800, 835 e 845.
Questo descrive la **prossimità**, non ne attribuisce l'effetto causale.

La configurazione del componente della candidata al passo 835
è data dai legami:
- `93–245`
- `93–477`
- `40–477`

Il componente al tick 835 è dunque `245—93—477—40`.
Non è la comparsa in un unico passo di una nuova catena: è
l'**assemblaggio di più legami e frammenti**.

## Rapporto con la precedente verifica controfattuale (#3)

Lo spostamento del presunto template al passo **791** avviene **dopo**
la struttura comune al tick 770, la sua scissione al tick 771 e una
precedente storia di legami `93–245`.

Pertanto il controfattuale già eseguito **non elimina la possibilità**
che vincoli spaziali e la storia del precursore comune abbiano inciso
sull'assemblaggio. Questa non è una prova che lo abbiano fatto: è un
**fattore confondente documentato**.

Nel mondo originale la catena omogenea `S0–S0–S0–S0` era già stata
osservata prima del passo 792 in 26 eventi del registro, associati a
20 ID di struttura distinti (non necessariamente 20 nascite autonome).
Questa frequenza di fondo riduce la specificità della sola firma.

## Giudizio: metodo GO, riproduzione causale NON dimostrata

**P0:** le regressioni del v2.1 su split, merge, perdita temporanea di
firma, template equidistanti e controlli M5 hanno superato `pytest`
su GitHub Actions. La versione **v2 originale** resta congelata.

**P1:** timeline e contabilità sono riproducibili; hash finale M6 invariato,
RNG non alterato dall'osservazione. **Gate strumentale superato.**

**Interpretazione:** è ora accertato un precursore comune, seguito da
scissione e riassemblaggio. Pertanto il semplice match v2 del passo 835
**non costituisce prova di copia causale** e non giustifica M7. Non
sosteniamo neppure un'impossibilità matematica di templating locale.

**Limiti residui:** i sette eventi sono tutti quelli registrati entro
il raggio locale prefissato, non tutti i processi fisici che potrebbero
incidere indirettamente. La storia anteriore al passo 770 non è qui
ricostruita integralmente. I tie-break dei template equidistanti rimangono
una regola deterministica del detector, **non** un criterio causale.

## Prossimo esperimento: P2, pre-registrato e su PR separata

1. Estendere la ricostruzione al **precursore prima del tick 770**, per
   verificare da quando le sei particelle risultano connesse.
2. Definire il tempo d'intervento prima dell'assemblaggio del
   precursore, non solo prima del secondo dimero.
3. Preregistrare baseline, spostamenti/spatial shams, numero di tentativi
   e controlli di occupazione/densità **prima** dei risultati.
4. Registrare il **primo punto di divergenza** della traiettoria, conteggio
   e impronte RNG; escludere false inferenze da stream sequenziali divergenti.
5. Includere controlli sintetici con e senza dipendenza causale nota.
6. Non attribuire significatività statistica a un singolo caso
   selezionato dopo l'osservazione. Nessuna modifica alla dinamica RNG,
   alle leggi o al livello M7 senza decisione documentata.
