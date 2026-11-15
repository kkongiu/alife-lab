# M6.3-25 — Test, hash, RNG ed energia

Protocollo preregistrato [d76e2e6](https://github.com/kkongiu/alife-lab/commit/d76e2e6a3d69b0ab94a607288fcf21ffd70ec0ca), [CI completa PASS](https://github.com/kkongiu/alife-lab/actions/runs/43741951791), [144 mondi, dati integrali](https://github.com/kkongiu/alife-lab/actions/runs/43741951791/artifacts/14173016026). Dieci analisi dello STESSO campione: 12 seed nuovi (8401–8412), 2 densità, 6 sonde, 450 tick. Fisica invariata.

Suite pytest e 144/144 run PASS. I due replay prefissati verificano hash finale, RNG, dissipazione, energia, conteggi di formazioni/rotture e tempi di purezza contro l'osservatore precedente. Hash baseline/8401/A: 0ca3a415ea156d8a19787b3c124c9324cf9fffd3fabac42ccfbf980fd868871a; enriched/8401/D: 91ce32e73cfec287d9db3809417d87ee1338828ab9ee4318231cb3ff7b2de2ea. Nessuna modifica al motore, detector o master.
