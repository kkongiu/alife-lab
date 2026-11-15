# M6.3-3 — Sopravvivenza del nucleo materiale

**Step 2/5 — distinguere l'isolamento di quattro particelle dalla persistenza dei loro legami.** Stesse 160 traiettorie M6.3-1 e medesima analisi del protocollo [M6.3-2](../campaigns/m6_3_2/protocol.json). [CI riuscita](https://github.com/kkongiu/alife-lab/actions/runs/43737009689).

Le tre categorie sono diverse:
- **Forma pura:** esattamente gli ID 0–3, collegati dai legami `0–1`, `1–2`, `2–3`, nessun estraneo nella componente.
- **Nucleo con legami originali presenti:** i **tre legami specifici** sono presenti, anche se l'aggregato ha acquisito altre particelle.
- **Nucleo materialmente connesso:** i quattro ID sono nello stesso componente, anche se alcuni legami originali sono stati sostituiti.

| Misura (tick medi su 450; 80 run/densità) | 200 particelle | 264 particelle |
|---|---:|---:|
| Forma pura | **34,18** | **8,03** |
| Nucleo con tre legami originali presenti | **252,34** | **333,34** |
| Nucleo cresciuto ma con tre legami ancora presenti | **218,16** | **325,31** |
| Quattro ID originali ancora connessi | **268,78** | **336,40** |
| Primo tick di rottura di un legame originale, media tra i run con rottura | **158,79** | **145,30** |
| Run con almeno una rottura originale entro 450 tick | 77/80 | 78/80 |

**Interpretazione:** il nucleo non diventa necessariamente meno persistente ad alta densità. Viene inglobato più rapidamente in un aggregato più grande; i suoi legami originali si osservano presenti per una porzione considerevole della simulazione.

**Cautela indispensabile:** `tre legami presenti per 333 tick` NON significa `tre legami rimasti ininterrotti per 333 tick`. Un legame può rompersi e riformarsi. La prima rottura avviene mediamente intorno ai passi 145–159 **solo fra i run in cui è osservata**. Non stiamo misurando né selezione naturale né sopravvivenza biologica.

**Esito:** M6.3-1 classificava come `inactive` anche strutture ancora riconoscibili come **nuclei originali cresciuti**. Il prossimo osservatore dovrà distinguere le due condizioni senza assimilare la crescita a riproduzione.
