# M8.1a — Origine da monomeri liberi: report del campione congelato

**18 novembre 2026 — campagna completata: software PASS, risultato scientifico parzialmente negativo.**
I risultati seguenti provengono da [GitHub Actions #44412124197](https://github.com/kkongiu/alife-lab/actions/runs/44412124197) e dall'[archivio integrale #14476369876](https://github.com/kkongiu/alife-lab/actions/runs/44412124197/artifacts/14476369876).

## Tracciabilità e separazione fra preregistrazione e risultati

- Protocollo fissato **prima** di implementazione e risultati: [05a574d](https://github.com/kkongiu/alife-lab/commit/05a574dedff2680fe367ac90b1d5cb1c0d81f497).
- Fisica M8.0 esistente **immutata**; M6/M7, `master` e M8.0 PR #44 non modificati.
- 64 mondi sorgente (seed 610001–610064) × 3 modi = **192** traiettorie; **200 passi** ciascuna, nessun mondo escluso.
- Inizializzazione: 20 monomeri iniziali **non legati**, con 10 di specie 0 e 10 di specie 1 collocati casualmente in 20 siti distinti; **zero B/H**, nessun template costruito; energia totale 500, materia totale 80.
- Il primo candidato spontaneo è sempre il primo segmento con quattro ID iniziali e tre legami B *realmente* formati, senza selezione ex post.
- Figlio valido solo se costituito da **quattro nuovi ID**, ciascuno catturato *dopo* la nascita del primo candidato tramite contatto H reale con il monomero parentale nella medesima posizione, tre legami B reali, nessun H residuo verso il genitore, componente B *esattamente* di quattro ID e persistenza ≥20 tick.
- Tutti i test di regressione e gli invarianti fisici della campagna sono PASS; il fallimento di un criterio scientifico non è un errore di CI.

## Risultati completi delle tre condizioni

| Misura (64 mondi per condizione) | Templating | Identità rimescolata | Senza templating |
| --- | ---: | ---: | ---: |
| Mondi con una prima catena B nativa di 4 monomeri iniziali | **30** | **30** | **29** |
| Prodotti materiali distinti e persistenti ≥20 tick | **0** | **0** | **0** |
| Prodotti informativi esatti e persistenti | **0** | **0** | **0** |
| Catture da H della prima catena selezionata dopo la sua nascita | **16** | **16** | **0** |
| Tutte le catture fisiche da tutte le catene | 1.647 | 1.647 | 0 |
| Nuovi legami B formati globalmente | 2.529 | 2.529 | 483 |

Il numero 16 è la somma degli eventi di cattura da parte della **prima catena selezionata** nei 64 mondi, NON il numero di figli, non il numero di mondi con figli e non una probabilità stimata. Le 1.647 catture comprendono invece tutte le sorgenti native nei 64 mondi informativamente attivi. **Non è stato osservato alcun prodotto figlio completo** secondo il criterio preregistrato.

## Gate congelati

1. **Integrità fisica**: PASS per tutte le 192 traiettorie e ciascuno dei 200 passi.
2. **Origine spontanea senza templating ≥12/64**: **PASS — 29/64**.
3. **Prodotti informativi: ≥4/64 attivi e almeno 3 più che nel controllo rimescolato**: **NO_GO — 0/64 contro 0/64**.

## Interpretazione

**Esiste nucleazione spontanea di catene B nella chimica a superficie fissa di M8.0** quando il mondo inizia con monomeri liberi anziché una catena preassemblata. La soglia preregistrata è superata nella condizione `no_template`. Si osserva anche attività globale di reclutamento chimico e l'effetto previsto di controllo sulla frequenza complessiva degli eventi.

**NON è dimostrata la produzione spontanea di un figlio fisicamente indipendente e persistente dalla prima catena.** Le prime catene selezionate originano soltanto 16 catture totali nei 64 mondi informativi, rispetto a 1.647 catture provenienti da tutte le catene presenti. È un segnale di scarsità di opportunità per la parentela che il rilevatore preregistrato segue, ma **non dimostra da solo** se la causa sia affollamento dei siti, tempi di nucleazione, geometria fissa, scarsa separazione H, oppure eccessiva selettività dell'endpoint. Queste ipotesi richiedono un audit ulteriore prima di cambiare la legge fisica.

Le cifre active e shuffled sono uguali per catture e legami perché il canale di identità chimica altera le specie scelte, non le probabilità meccaniche di cattura/B nello schema M8.0. Questo non significa che sia stata dimostrata copiatura informativa.

**STOP**: niente aumento opportunistico di campione, durata o densità e niente claim di vita/replicazione multigenerazionale. Il passo razionale successivo è un **audit retrospettivo soltanto diagnostico** dei risultati congelati: disponibilità di quattro siti adiacenti quando nasce la prima catena, tempi fino a primo legame B e prima H, durata dei contatti H, percentuale di prodotti materiali parziali e indicatori di saturazione. Solo dopo formulare una ipotesi M8.1b esplicita con preregistrazione separata. La fisica M8.0 resta congelata.
