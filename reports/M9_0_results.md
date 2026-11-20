# M9.0 — Primo reattore chimico astratto: report scientifico

**20 novembre 2026 — prima campagna completata: 312 mondi validi, tutti i tre gate preregistrati superati.**

## Tracciabilità

- [Protocollo congelato prima di qualunque implementazione M9.0 o risultato — commit 0d95259](https://github.com/kkongiu/alife-lab/commit/0d95259bfa6929806dc5b4a5d3fe9f13858342d0).
- [GitHub Actions #44779981943 — PASS per tutti i test storici M6, nuovi M9 e campagna](https://github.com/kkongiu/alife-lab/actions/runs/44779981943).
- [Artefatto #14652356092 — tutti i 312 mondi e gli eventi reali, inclusi i risultati nulli](https://github.com/kkongiu/alife-lab/actions/runs/44779981943/artifacts/14652356092).
- [PR #50 — laboratorio indipendente da M8, non unito a master](https://github.com/kkongiu/alife-lab/pull/50).

### Domanda

Può una piccola chimica di reazione, con regole e risorse generali ma senza una struttura già costruita, **generare e mantenere reti di catalisi in modo causalmente dipendente dai catalizzatori che produce?**

**Sì nel significato limitato del nostro modello**: in 9 delle 12 chimiche preassegnate, il controllo informativo indicava un ciclo nel grafo delle reazioni, e in almeno 5/8 seed appaiati la popolazione media tardiva dei dimeri con catalisi ON era almeno 3 unità superiore sia a catalisi OFF sia alla catalisi disattivata dopo il tick 150.

Questo **non** dimostra l'emergenza di leggi chimiche nuove, organizzazioni cellulari, trasmissione di un genoma, ereditarietà o origine della vita.

## Motore M9.0

Reattore ben mescolato e non spaziale:

- Molecole di base: `A` e `B`.
- Quattro dimeri orientati: `AA`, `AB`, `BA`, `BB`.
- Ingresso continuo di 3 molecole A e 3 molecole B per tick e 8 token di energia libera per tick.
- Washout di ogni molecola con probabilità 0,04 per tick; idrolisi di ciascun dimero con probabilità 0,03 per tick.
- Legame `X + Y -> XY` con probabilità 0,004 in assenza di catalisi e 0,65 quando esiste il catalizzatore molecolare assegnato e la catalisi è abilitata.
- Formazione di un dimero trasferisce un token dal pool alla sua energia di legame. L'idrolisi recupera il token, l'esportazione di un dimero esporta anche l'energia del suo legame. Overflow energetico oltre 64 va in dissipazione.
- Conservazione **esatta del materiale** contabilizzando entrate/uscite, e del bilancio dei token energetici a ogni tick.

I token energetici sono un'astrazione contabile, **non** una termodinamica realistica. Il rapporto di probabilità catalizzata/non catalizzata è **162,5 volte**; questo conferisce al modello un feedback potente già programmato.

## Campagna preregistrata

**8 seed 730001–730008**, **300 tick**, comparazione di tre bracci per ogni seed: catalisi attiva sempre (ON), disattivata sempre (OFF), e disattivata dopo il tick 150 (SWITCH-OFF). La finestra primaria tardiva è tick **220–300** compresi, 81 osservazioni di ciascun mondo.

- **Controllo positivo**: catalizzatore AA introdotto deliberatamente a tick 0 e regola `AA` che catalizza `A + A -> AA`. Sono 8 × 3 = 24 mondi artificialmente preseminati.
- **Esplorazione non preseminata**: 12 diverse chimiche generate una sola volta con assegnazione deterministica hash dei catalizzatori ai quattro prodotti. La vasca parte completamente vuota: nessun dimero o catalizzatore iniziale. Sono 12 × 8 × 3 = 288 mondi.

**Totale: 312 mondi**, campione non ampliato dopo il risultato.

## Risultati

| Rete | Ciclo nel grafo catalitico | Seed con ON superiore a OFF e SWITCH-OFF di almeno 3 (su 8) | Dimeri medi tardivi ON | OFF | SWITCH-OFF |
|---|---|---:|---:|---:|---:|
| **Controllo positivo AA preseminato** | Sì | **8/8** | 9,88 | 0,08 | 0,08 |
| 0 | Sì | **7/8** | 32,77 | 0,27 | 0,33 |
| 1 | Sì | **7/8** | 25,73 | 0,27 | 0,33 |
| 2 | Sì | **6/8** | 10,08 | 0,27 | 0,33 |
| 3 | Sì | 3/8 | 8,08 | 0,27 | 0,27 |
| 4 | Sì | **7/8** | 20,45 | 0,27 | 0,33 |
| 5 | Sì | **7/8** | 17,75 | 0,27 | 0,33 |
| 6 | No | 2/8 | 2,54 | 0,27 | 0,27 |
| 7 | Sì | **6/8** | 25,20 | 0,27 | 0,27 |
| 8 | Sì | **7/8** | 16,48 | 0,27 | 0,27 |
| 9 | Sì | **7/8** | 16,19 | 0,27 | 0,27 |
| 10 | Sì | 4/8 | 14,42 | 0,27 | 0,33 |
| 11 | Sì | **6/8** | 8,68 | 0,27 | 0,27 |

Per il controllo positivo la misura è **solo AA**; per ciascuna rete non preseminata è il **numero totale di dimeri**. Le medie riportate aggregano i valori di ciascun mondo nella finestra tardiva e poi gli 8 semi numerici. I seed 0..11 sono identificativi delle **chimiche**, non seed pseudo-casuali.

**Le reti che soddisfano il gate prima di qualunque selezione ex post sono esattamente:** 0, 1, 2, 4, 5, 7, 8, 9, 11 (**9/12**). La rete 6 non presenta alcun ciclo nel grafo delle regole ed è NO_GO, le reti 3 e 10 non soddisfano il requisito di almeno 5/8 repliche appaiate, nonostante medie ON superiori.

## Gate fissati prima della campagna

1. **Integrità dei 312 mondi e dei bilanci di materia ed energia:** **PASS**. Tutti i 300 tick di ciascun mondo verificati; regressioni storiche e nuove PASS.
2. **Controllo positivo deliberatamente autocatalitico:** **PASS 8/8**, soglia fissata ≥6/8.
3. **Reti chimiche non preseminate con circuito di feedback e dipendenza dal catalizzatore, almeno due reti con ≥5/8 seed ciascuna:** **PASS 9/12**.

## Interpretazione e limiti che non dobbiamo aggirare

**Ciò che abbiamo osservato:** il reattore genera dimeri da un flusso di soli monomeri; alcune reazioni diventano molto più frequenti quando sono presenti i dimeri che le catalizzano; il mantenimento tardivo è drasticamente più debole quando disabilitiamo le proprietà catalitiche. Questo è coerente con un'autocatalisi a livello di rete nel modello implementato e l'intervento ON/OFF ne supporta un effetto causale sui conteggi.

**Ciò che NON abbiamo osservato:** un individuo, un figlio distinto, la trasmissione di una variante ereditabile o competizione evolutiva. Non è una prova dell'origine della vita e non è stato generato spontaneamente il sistema di leggi catalitiche: tali leggi erano parte della configurazione hash iniziale.

**Limite metodologico:** circa 11/12 delle mappe presentano cicli catalitici nelle regole; la frequenza 9/12 non è una prevalenza universale della vita, ma il risultato su 12 reti piccole e già caratterizzate da una potenzialmente forte catalisi. La differenza di tassi 0,65 vs 0,004 (162,5×) rende plausibile un ampio effetto anche in una rete priva di altre qualità vitali.

**Decisione di ricerca:** archiviare M9.0 come validazione positiva di un laboratorio di rete autocatalitica. Il prossimo compito NON è scrivere «vita emersa», ma verificare robustezza, rete effettivamente attiva e composizioni alternative trasmissibili, con una **nuova** preregistrazione. Una perturbazione selettiva del singolo catalizzatore o una riduzione preregistrata della catalisi potrebbe discriminare semplici circuiti che amplificano dal mantenimento più generale di una organizzazione collettiva.

**Nessun risultato precedente M8 è stato modificato e nessuna PR storica è stata unita a `master`.**
