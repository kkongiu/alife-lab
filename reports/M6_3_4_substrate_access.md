# M6.3-4 — Accessibilità ai substrati e valenza disponibile

**Step 3/5 — separare disponibilità di substrato e durata della forma sorgente.** Sono rianalizzati i medesimi 160 run; nessuna nuova fisica, nessun evento di bond forzato. [Artefatto completo](https://github.com/kkongiu/alife-lab/actions/runs/43737009689/artifacts/14170732108).

A ogni tick post-transizione si contano vicini liberi delle quattro particelle sorgente, poi si selezionano le coppie **staticamente eleggibili** per legame: distanza von Neumann uno, specie consentite, entrambi sotto valenza massima e con energia sufficiente. Questa è una **sonda di accessibilità post-step**, NON il numero esatto delle coppie effettivamente campionate dalla chimica nella fase di formazione.

| Misura, somma su 80 run | Baseline (200) | Enriched (264) |
|---|---:|---:|
| Coppie sorgente–substrato eleggibili mentre la sonda è pura | **1.015** | **720** |
| Vicini S0/S1 liberi mentre è pura | 1.710 | 1.237 |
| Tick con forma pura (somma sugli 80 run) | 2.734 | 642 |
| Coppie eleggibili **per tick di forma pura** | **0,37** | **1,12** |
| Coppie eleggibili mentre il nucleo è cresciuto ma conserva i legami originali | **695** | **604** |
| Tick con nucleo cresciuto e legami originali presenti | circa 17.453 | circa 26.025 |
| Coppie eleggibili per tick in tale fase | circa 0,040 | circa 0,023 |
| Run con almeno una coppia eleggibile in forma pura | 65/80 | 60/80 |

**Risultato:** la maggiore densità porta più occasioni **per unità di tempo in cui la catena è pura**, ma il rapido attacco di particelle riduce molto questa finestra. Quando il nucleo è già cresciuto, la disponibilità di coppie sorgente–monomero eleggibili per tick è più bassa, **compatibile** con saturazione di valenza o geometria ostacolata.

**Limiti:** le opportunità sono misurate **dopo** un avanzamento, non precisamente nel momento in cui il motore esamina una coppia; non stimano una probabilità causale, né certificano quali superfici siano cataliticamente attive. I rapporti per tick sono descrittivi, non `rate constants`.

**Decisione strumentale:** un futuro test mirato dovrà distinguere il numero di monomeri liberi dalle coppie che il nucleo può effettivamente incorporare, evitando di allentare il detector per produrre artificialmente un evento positivo.
