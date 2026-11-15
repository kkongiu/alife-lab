"""Preregistra la campagna M6: seed, configurazioni, numero di esperimenti.

Scrive `campaigns/m6/manifest.json` e una configurazione per ogni run. Il
manifest contiene l'hash di ogni configurazione: `run_campaign.py` rifiuta di
eseguire un run la cui configurazione non corrisponde.

Il manifest va creato e versionato **prima** dei run. `--force` esiste solo per
correzioni esplicite: una nuova preregistrazione deve avere un nuovo identificativo.

Uso: .venv/bin/python tools/preregister_m6.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from alife import __version__
from alife.config import Config
from alife.metrics import git_commit, runtime_versions

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "campaigns" / "m6"
BASE_CONFIG = ROOT / "configs" / "m3_baseline.json"

SEEDS = [6101, 6102, 6103, 6104, 6105]
STEPS = 3000

SOURCE_POSITIONS = [(32, 32), (64, 32), (96, 32), (32, 64), (64, 64), (96, 64), (32, 96), (64, 96), (96, 96)]

CONDITIONS = {
    "closed": {
        "description": "chimica M3 senza costi, senza decadimento, senza sorgenti: energia conservata",
        "energy": {
            "movement_cost": 0,
            "formation_dissipation": 0,
            "breaking_dissipation": 0,
            "particle_decay": {"num": 0, "den": 1},
            "bond_decay": {"num": 0, "den": 1},
            "sources": [],
        },
    },
    "unfed": {
        "description": "costi e decadimento attivi, nessuna sorgente: sistema non alimentato",
        "sources_rate": 0,
    },
    "fed-low": {
        "description": "come unfed con 9 sorgenti a 1 quanto per passo",
        "sources_rate": 1,
    },
    "fed-mid": {
        "description": "come unfed con 9 sorgenti a 2 quanti per passo",
        "sources_rate": 2,
    },
    "fed-high": {
        "description": "come unfed con 9 sorgenti a 4 quanti per passo",
        "sources_rate": 4,
    },
}

DECISION_RULE = {
    "candidate_condition": "almeno 3 seed su 5 classificati 'replication' e mediana delle copie persistenti >= 5",
    "otherwise": "nessuna evidenza di replicazione in questa campagna",
    "control_check": "se 'closed' o 'unfed' risultano 'replication', il criterio è invalido: REVISE",
    "independence": "un singolo seed non è evidenza; i run nulli sono registrati come tali",
}


def config_for(condition: str, seed: int, base: dict) -> dict:
    raw = json.loads(json.dumps(base))
    raw["seed"] = seed
    spec = CONDITIONS[condition]
    if "energy" in spec:
        raw["energy"] = json.loads(json.dumps(spec["energy"]))
    else:
        rate = spec["sources_rate"]
        raw["energy"]["sources"] = [
            {
                "x": x,
                "y": y,
                "rate_num": rate,
                "rate_den": 1,
                "capacity": 30,
            }
            for x, y in SOURCE_POSITIONS
        ] if rate else []
    return raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Preregistra la campagna M6")
    parser.add_argument("--force", action="store_true", help="sovrascrive una preregistrazione esistente")
    args = parser.parse_args()

    manifest_path = CAMPAIGN / "manifest.json"
    if manifest_path.exists() and not args.force:
        print(f"preregistrazione già presente: {manifest_path}")
        print("usare --force solo per una revisione esplicita")
        return 1

    base = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
    (CAMPAIGN / "configs").mkdir(parents=True, exist_ok=True)

    runs = []
    for condition in CONDITIONS:
        for seed in SEEDS:
            raw = config_for(condition, seed, base)
            config = Config.from_dict(raw).validate()
            path = CAMPAIGN / "configs" / f"{condition}-{seed}.json"
            path.write_text(json.dumps(config.to_dict(), indent=2) + "\n", encoding="utf-8")
            runs.append(
                {
                    "id": f"{condition}-{seed}",
                    "condition": condition,
                    "seed": seed,
                    "config": str(path.relative_to(CAMPAIGN)),
                    "config_hash": config.hash(),
                }
            )

    manifest = {
        "campaign": "m6",
        "version": 1,
        "preregistered_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool_version": __version__,
        "git_commit": git_commit(ROOT),
        "versions": runtime_versions(),
        "base_config": str(BASE_CONFIG.relative_to(ROOT)),
        "base_config_hash": hashlib.sha256(BASE_CONFIG.read_bytes()).hexdigest(),
        "hypothesis": (
            "Verificare se il rilevatore preregistrato segnala copie persistenti in "
            "ambienti alimentati, non alimentati e chiusi. L'ipotesi di replicazione "
            "spontanea non è assunta: la campagna è progettata per poterla smentire."
        ),
        "observations_vs_hypotheses": (
            "Il report separa le misure (osservazioni) dalle spiegazioni proposte "
            "(ipotesi non dimostrate). Nessun run viene presentato come replicazione "
            "senza la classificazione del rilevatore e la ripetizione su seed indipendenti."
        ),
        "seeds": SEEDS,
        "steps": STEPS,
        "conditions": {
            name: spec["description"] for name, spec in CONDITIONS.items()
        },
        "detector": {
            "radius": 2,
            "persist_steps": 10,
            "min_size": 4,
            "min_copies": 5,
            "min_generation": 2,
        },
        "metrics": [
            "strutture attive",
            "nascite, morti, crescite, riduzioni, scissioni, fusioni, trasformazioni",
            "vita media e massima delle strutture",
            "firme distinte e passi con ambiguità",
            "copie candidate e persistenti",
            "generazione massima persistente",
            "classificazione del rilevatore",
            "energia interna, iniettata, dissipata, non assorbita e identità",
            "hash completo dello stato",
        ],
        "decision_rule": DECISION_RULE,
        "runs": runs,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"preregistrazione scritta: {manifest_path}")
    print(f"{len(runs)} run: {len(CONDITIONS)} condizioni × {len(SEEDS)} seed × {STEPS} passi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
