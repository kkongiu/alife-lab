"""Genera un file di risultati per ogni test e un'evidenza per gli 8 test obbligatori.

Produce:
  reports/tests/junit.xml        risultato macchina-leggibile di pytest
  reports/tests/pytest.log       log completo dell'esecuzione
  reports/tests/results.json     tutti i casi con stato, durata, output
  reports/tests/index.md         indice con riepilogo
  reports/tests/cases/*.md       un file per ogni caso di test
  reports/tests/evidence/M1-0N_*.md  evidenza misurata dei test obbligatori

Uso: .venv/bin/python tools/test_report.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from alife.config import Config, load_config
from alife.metrics import runtime_versions
from alife.particles import InvariantError
from alife.persistence import (
    CheckpointError,
    load_checkpoint,
    save_checkpoint,
    world_to_checkpoint,
)
from alife.rng import RNG
from alife.world import World

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "tests"
CASES_DIR = OUT / "cases"
EVIDENCE_DIR = OUT / "evidence"

sys.path.insert(0, str(ROOT / "tests"))
from support import make_config  # noqa: E402  (helper condiviso con la suite)

REQUIRED = [
    {
        "id": "M1-01",
        "title": "Conservazione del numero di particelle",
        "contract": "alife.md §7, punto 1",
        "slug": "conservazione_particelle",
        "tests": ["tests/test_invariants.py::test_particle_count_conserved"],
    },
    {
        "id": "M1-02",
        "title": "Conservazione della quantità per specie",
        "contract": "alife.md §7, punto 2",
        "slug": "conservazione_specie",
        "tests": ["tests/test_invariants.py::test_species_quantities_conserved"],
    },
    {
        "id": "M1-03",
        "title": "Assenza di occupazione multipla",
        "contract": "alife.md §7, punto 3",
        "slug": "occupazione_unica",
        "tests": ["tests/test_invariants.py::test_no_multiple_occupancy"],
    },
    {
        "id": "M1-04",
        "title": "Rispetto dei confini configurati",
        "contract": "alife.md §7, punto 4",
        "slug": "confini",
        "tests": [
            "tests/test_invariants.py::test_periodic_boundaries",
            "tests/test_dynamics.py::test_closed_boundary_keeps_particles_inside",
        ],
    },
    {
        "id": "M1-05",
        "title": "Riproducibilità con identico seed",
        "contract": "alife.md §7, punto 5",
        "slug": "riproducibilita",
        "tests": ["tests/test_reproducibility.py::*"],
    },
    {
        "id": "M1-06",
        "title": "Integrità del salvataggio e caricamento",
        "contract": "alife.md §7, punto 6",
        "slug": "checkpoint",
        "tests": [
            "tests/test_checkpoint.py::test_roundtrip_preserves_state",
            "tests/test_checkpoint.py::test_repeated_save_load_cycles_are_stable",
            "tests/test_checkpoint.py::test_checkpoint_does_not_mutate_world",
            "tests/test_checkpoint.py::test_no_temporary_file_left_behind",
        ],
    },
    {
        "id": "M1-07",
        "title": "Equivalenza tra esecuzione continua e interrotta/ripresa",
        "contract": "alife.md §7, punto 7",
        "slug": "ripresa_equivalente",
        "tests": [
            "tests/test_checkpoint.py::test_resume_is_equivalent_to_continuous_run",
            "tests/test_cli.py::test_resume_matches_continuous_run",
        ],
    },
    {
        "id": "M1-08",
        "title": "Rilevamento di una violazione intenzionale delle invarianti",
        "contract": "alife.md §7, punto 8",
        "slug": "violazioni_intenzionali",
        "tests": [
            "tests/test_invariants.py::test_validate_detects_duplicate_cell",
            "tests/test_invariants.py::test_validate_detects_out_of_bounds_particle",
            "tests/test_invariants.py::test_validate_detects_grid_desynchronisation",
            "tests/test_invariants.py::test_validate_detects_missing_particle",
            "tests/test_invariants.py::test_validate_detects_invalid_species_index",
            "tests/test_checkpoint.py::test_detects_tampered_particle",
            "tests/test_checkpoint.py::test_detects_tampered_config_hash",
            "tests/test_checkpoint.py::test_detects_energy_imbalance",
            "tests/test_checkpoint.py::test_detects_invalid_json",
            "tests/test_checkpoint.py::test_detects_wrong_format",
            "tests/test_checkpoint.py::test_detects_missing_rng_state",
        ],
    },
]

Measure = tuple[str, str]
Check = tuple[str, bool]


# --------------------------------------------------------------------------- #
# Esecuzione e parsing di pytest
# --------------------------------------------------------------------------- #
def run_pytest() -> tuple[int, float]:
    started = time.perf_counter()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "-o",
            "junit_logging=all",
            f"--junitxml={OUT / 'junit.xml'}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - started
    (OUT / "pytest.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    return result.returncode, elapsed


def parse_junit() -> list[dict[str, Any]]:
    tree = ET.parse(OUT / "junit.xml")
    cases: list[dict[str, Any]] = []
    for element in tree.iter("testcase"):
        classname = element.get("classname", "")
        module = classname.split(".")[-1] if classname else "test_sconosciuto"
        name = element.get("name", "")
        status = "passed"
        detail = ""
        for child in element:
            if child.tag in ("failure", "error"):
                status = "failed" if child.tag == "failure" else "error"
                detail = (child.get("message") or "").strip() or (child.text or "").strip()
            elif child.tag == "skipped":
                status = "skipped"
                detail = (child.get("message") or "").strip()
        output = ""
        for child in element:
            if child.tag == "system-out" and child.text:
                output += child.text
        cases.append(
            {
                "node": f"tests/{module}.py::{name}",
                "module": f"{module}.py",
                "name": name,
                "status": status,
                "seconds": round(float(element.get("time", 0.0) or 0.0), 4),
                "detail": detail,
                "output": output.strip(),
            }
        )
    return cases


def expand(selectors: list[str], cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for selector in selectors:
        if selector.endswith("::*"):
            prefix = selector[:-2]
            selected.extend(case for case in cases if case["node"].startswith(prefix))
        else:
            selected.extend(case for case in cases if case["node"] == selector)
    return selected


# --------------------------------------------------------------------------- #
# Evidenze misurate
# --------------------------------------------------------------------------- #
def _diagnose(action: Callable[[], None]) -> str:
    try:
        action()
    except (InvariantError, CheckpointError) as exc:
        text = " ".join(str(exc).split())
        return text if len(text) <= 300 else text[:299] + "…"
    return "NESSUN ERRORE (atteso un errore)"


def evidence_01(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = make_config(seed=101, width=16, height=16)
    world = World.create(config)
    before_particles, before_hash = len(world.store), world.state_hash()
    world.advance(150)
    problems = world.validate()
    return (
        "Configurazione 16×16, specie A=12 B=8, seed 101, 150 passi.",
        [
            ("particelle iniziali", str(before_particles)),
            ("particelle finali", str(len(world.store))),
            ("delta", str(len(world.store) - before_particles)),
            ("hash iniziale", before_hash[:32] + "…"),
            ("hash finale", world.state_hash()[:32] + "…"),
            ("violazioni rilevate", str(len(problems))),
        ],
        [
            ("numero di particelle invariato", len(world.store) == before_particles),
            ("nessuna violazione di invariante", problems == []),
            ("lo stato è cambiato (la simulazione ha evoluto)", world.state_hash() != before_hash),
        ],
    )


def evidence_02(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = World.create(make_config(seed=102, width=16, height=16))
    before = world.counts()
    world.advance(150)
    after = world.counts()
    measures: list[Measure] = []
    checks: list[Check] = []
    for name in before:
        measures.append((f"specie {name}: iniziale → finale", f"{before[name]} → {after[name]}"))
        checks.append((f"specie {name} conservata", before[name] == after[name]))
    measures.append(("conteggi finali", json.dumps(after)))
    checks.append(("conteggi finali = configurazione", after == {"A": 12, "B": 8}))
    return ("Configurazione 16×16, specie A=12 B=8, seed 102, 150 passi.", measures, checks)


def evidence_03(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = World.create(make_config(seed=103, width=16, height=16))
    world.advance(150)
    positions = list(zip(world.store.xs, world.store.ys))
    unique = len(set(positions))
    occupied = world.store.occupied_cells()
    grid_consistent = all(
        world.store.grid[y * world.store.width + x] == index
        for index, (x, y) in enumerate(positions)
    )
    return (
        "Configurazione 16×16, 20 particelle, seed 103, 150 passi.",
        [
            ("particelle", str(len(positions))),
            ("celle distinte occupate", str(unique)),
            ("celle occupate secondo la griglia", str(occupied)),
            ("celle con più di un occupante", str(len(positions) - unique)),
        ],
        [
            ("posizioni tutte distinte", unique == len(positions)),
            ("griglia coerente con le posizioni", grid_consistent),
            ("celle occupate = particelle", occupied == len(positions)),
        ],
    )


def evidence_04(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    periodic = World.create(make_config(seed=104, width=20, height=20, boundary="periodic"))
    periodic.advance(200)
    closed = World.create(make_config(seed=104, width=10, height=10, boundary="closed"))
    closed.advance(50)
    p_out = sum(
        1 for x, y in zip(periodic.store.xs, periodic.store.ys) if not (0 <= x < 20 and 0 <= y < 20)
    )
    c_out = sum(
        1 for x, y in zip(closed.store.xs, closed.store.ys) if not (0 <= x < 10 and 0 <= y < 10)
    )
    return (
        "Periodico: 20×20, seed 104, 200 passi. Chiuso: 10×10, seed 104, 50 passi.",
        [
            (
                "periodico: intervallo x / y",
                f"{min(periodic.store.xs)}..{max(periodic.store.xs)} / "
                f"{min(periodic.store.ys)}..{max(periodic.store.ys)}",
            ),
            ("periodico: particelle fuori griglia", str(p_out)),
            (
                "chiuso: intervallo x / y",
                f"{min(closed.store.xs)}..{max(closed.store.xs)} / "
                f"{min(closed.store.ys)}..{max(closed.store.ys)}",
            ),
            ("chiuso: particelle fuori griglia", str(c_out)),
        ],
        [
            ("confini periodici rispettati", p_out == 0),
            ("confini chiusi rispettati", c_out == 0),
            ("nessuna violazione (periodico)", periodic.validate() == []),
            ("nessuna violazione (chiuso)", closed.validate() == []),
        ],
    )


def evidence_05(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    first = World.create(make_config(seed=1234, width=16, height=16))
    second = World.create(make_config(seed=1234, width=16, height=16))
    third = World.create(make_config(seed=1235, width=16, height=16))
    first.advance(120)
    second.advance(120)
    third.advance(120)
    same = first.snapshot() == second.snapshot()
    return (
        "Due universi con seed 1234 e uno con seed 1235, 120 passi ciascuno.",
        [
            ("hash seed 1234 (run A)", first.state_hash()[:32] + "…"),
            ("hash seed 1234 (run B)", second.state_hash()[:32] + "…"),
            ("hash seed 1235", third.state_hash()[:32] + "…"),
            ("spostamenti run A / run B", f"{first.moves_total} / {second.moves_total}"),
            ("fingerprint RNG uguale", str(first.rng.fingerprint() == second.rng.fingerprint())),
        ],
        [
            ("stesso seed ⇒ stesso stato completo", same),
            ("stesso seed ⇒ stesso hash", first.state_hash() == second.state_hash()),
            ("stesso seed ⇒ stesso numero di mosse", first.moves_total == second.moves_total),
            ("seed diverso ⇒ stato diverso", first.state_hash() != third.state_hash()),
        ],
    )


def evidence_06(tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = World.create(make_config(seed=106, width=16, height=16))
    world.advance(17)
    path = save_checkpoint(tmp / "M1-06_checkpoint.json", world)
    restored = load_checkpoint(path)
    payload = json.loads(path.read_text())
    tampered = dict(payload)
    tampered["particles"] = [list(entry) for entry in payload["particles"]]
    tampered["particles"][0][2] = (tampered["particles"][0][2] + 1) % 2
    broken = tmp / "M1-06_corrotto.json"
    broken.write_text(json.dumps(tampered))
    message = _diagnose(lambda: load_checkpoint(broken))
    return (
        "Universo 16×16, seed 106, 17 passi: salvataggio, ricaricamento e "
        "corruzione intenzionale di una specie.",
        [
            ("dimensione checkpoint", f"{path.stat().st_size} byte"),
            ("passo ricaricato", str(restored.step)),
            ("hash originale = hash ricaricato", str(restored.state_hash() == world.state_hash())),
            ("RNG originale = RNG ricaricato", str(restored.rng.fingerprint() == world.rng.fingerprint())),
            ("errore sul file corrotto", message),
        ],
        [
            ("stato identico dopo il caricamento", restored.snapshot() == world.snapshot()),
            ("configurazione identica", restored.config == world.config),
            ("file corrotto rifiutato", "hash dello stato" in message),
        ],
    )


def evidence_07(tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = make_config(seed=107, width=16, height=16)
    continuous = World.create(config)
    continuous.advance(60)
    interrupted = World.create(config)
    interrupted.advance(20)
    path = save_checkpoint(tmp / "M1-07_checkpoint.json", interrupted)
    resumed = load_checkpoint(path)
    resumed.advance(40)
    return (
        "Seed 107: run continuo di 60 passi contro run interrotto a 20 e ripreso per 40.",
        [
            ("hash continuo", continuous.state_hash()[:32] + "…"),
            ("hash ripreso", resumed.state_hash()[:32] + "…"),
            ("mosse continue / riprese", f"{continuous.moves_total} / {resumed.moves_total}"),
            ("fingerprint RNG uguale", str(continuous.rng.fingerprint() == resumed.rng.fingerprint())),
            ("passo finale", str(resumed.step)),
        ],
        [
            ("hash di stato identico", resumed.state_hash() == continuous.state_hash()),
            ("numero di mosse identico", resumed.moves_total == continuous.moves_total),
            ("stato RNG identico", continuous.rng.fingerprint() == resumed.rng.fingerprint()),
        ],
    )


def evidence_08(tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = World.create(make_config(seed=108, width=16, height=16))
    mutations: list[tuple[str, Callable[[], None]]] = []

    duplicate = World.create(make_config(seed=108, width=16, height=16))
    duplicate.store.xs[1] = duplicate.store.xs[0]
    duplicate.store.ys[1] = duplicate.store.ys[0]
    mutations.append(("doppia occupazione", duplicate.check))

    outside = World.create(make_config(seed=108, width=16, height=16))
    outside.store.xs[0] = -1
    mutations.append(("particella fuori griglia", outside.check))

    desync = World.create(make_config(seed=108, width=16, height=16))
    desync.store.grid[0] = 999
    mutations.append(("griglia desincronizzata", desync.check))

    missing = World.create(make_config(seed=108, width=16, height=16))
    missing.store.xs.pop()
    missing.store.ys.pop()
    missing.store.species.pop()
    mutations.append(("particella mancante", missing.check))

    invalid_species = World.create(make_config(seed=108, width=16, height=16))
    invalid_species.store.species[0] = 7
    mutations.append(("specie inesistente", invalid_species.check))

    checkpoint_world = World.create(make_config(seed=108, width=16, height=16))
    checkpoint_world.advance(2)
    payload = world_to_checkpoint(checkpoint_world)
    payload["energy_total"] = int(payload["energy_total"]) + 1
    energy_path = tmp / "M1-08_energia.json"
    energy_path.write_text(json.dumps(payload))
    mutations.append(("energia alterata", lambda: load_checkpoint(energy_path)))

    measures: list[Measure] = []
    checks: list[Check] = []
    for name, action in mutations:
        message = _diagnose(action)
        measures.append((name, message))
        checks.append((f"{name}: rilevata", "NESSUN ERRORE" not in message))
    return (
        "Sei violazioni introdotte deliberatamente su stati validi; ogni caso deve "
        "produrre un errore esplicito.",
        measures,
        checks,
    )


BUILDERS: dict[str, Callable[..., tuple[str, list[Measure], list[Check]]]] = {
    "M1-01": evidence_01,
    "M1-02": evidence_02,
    "M1-03": evidence_03,
    "M1-04": evidence_04,
    "M1-05": evidence_05,
    "M1-06": evidence_06,
    "M1-07": evidence_07,
    "M1-08": evidence_08,
}


# --------------------------------------------------------------------------- #
# Scrittura dei file
# --------------------------------------------------------------------------- #
def _clean_output(text: str) -> str:
    """Rimuove le intestazioni vuote che pytest aggiunge al JUnit XML."""
    ignored = {
        "Captured Log",
        "Captured Out",
        "Captured stdout",
        "Captured stderr",
        "Captured stdout call",
        "Captured stderr call",
    }
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped in ignored or set(stripped) == {"-"}:
            continue
        if "Captured Log" in stripped or "Captured Out" in stripped:
            continue
        lines.append(line)
    return "\n".join(lines)


def write_case_file(index: int, case: dict[str, Any], requirement: str | None) -> str:
    filename = f"{index:02d}_{case['module'].removesuffix('.py')}__{case['name']}.md"
    filename = filename.replace("/", "_").replace(":", "_")
    status = case["status"].upper()
    output = _clean_output(case["output"])
    lines = [
        f"# {case['name']}",
        "",
        f"- Nodo pytest: `{case['node']}`",
        f"- Stato: **{status}**",
        f"- Durata: {case['seconds']:.4f} s",
        f"- Modulo: `tests/{case['module']}`",
        f"- Requisito: {requirement or 'test aggiuntivo (non obbligatorio dal contratto)'}",
        f"- Comando: `.venv/bin/python -m pytest \"{case['node']}\"`",
        "",
    ]
    if case["detail"]:
        lines += ["## Dettaglio dell'errore", "", "```", case["detail"], "```", ""]
    if output:
        lines += ["## Output", "", "```", output, "```", ""]
    else:
        lines += ["## Output", "", "Nessun output: il test verifica asserzioni.", ""]
    (CASES_DIR / filename).write_text("\n".join(lines), encoding="utf-8")
    return filename


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    CASES_DIR.mkdir(exist_ok=True)
    EVIDENCE_DIR.mkdir(exist_ok=True)
    for stale in list(CASES_DIR.glob("*.md")) + list(EVIDENCE_DIR.glob("*.md")):
        stale.unlink()

    returncode, elapsed = run_pytest()
    cases = parse_junit()

    requirement_of: dict[str, str] = {}
    evidence_rows: list[dict[str, Any]] = []

    with __import__("tempfile").TemporaryDirectory() as temporary:
        tmp = Path(temporary)
        for requirement in REQUIRED:
            for case in expand(requirement["tests"], cases):
                requirement_of[case["node"]] = f"{requirement['id']} — {requirement['title']}"
            scenario, measures, checks = BUILDERS[requirement["id"]](tmp)
            selected = expand(requirement["tests"], cases)
            tests_ok = bool(selected) and all(case["status"] == "passed" for case in selected)
            evidence_ok = all(value for _, value in checks)
            status = "PASS" if tests_ok and evidence_ok else "FAIL"
            filename = f"{requirement['id']}_{requirement['slug']}.md"
            lines = [
                f"# {requirement['id']} — {requirement['title']}",
                "",
                f"- Requisito: {requirement['contract']}",
                f"- Esito: **{status}**",
                f"- Eseguito: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
                f"- Test pytest associati: {len(selected)} "
                f"({sum(1 for case in selected if case['status'] == 'passed')} superati)",
                "",
                "## Scenario",
                "",
                scenario,
                "",
                "## Misure",
                "",
                "| Voce | Valore |",
                "|---|---|",
            ]
            for label, value in measures:
                lines.append(f"| {label} | {value} |")
            lines += ["", "## Verifiche", "", "| Verifica | Esito |", "|---|---|"]
            for label, value in checks:
                lines.append(f"| {label} | {'OK' if value else 'FALLITA'} |")
            lines += ["", "## Test pytest associati", ""]
            for case in selected:
                lines.append(f"- `{case['node']}` → **{case['status'].upper()}** ({case['seconds']:.4f} s)")
            lines.append("")
            (EVIDENCE_DIR / filename).write_text("\n".join(lines), encoding="utf-8")
            evidence_rows.append(
                {
                    "id": requirement["id"],
                    "title": requirement["title"],
                    "status": status,
                    "file": f"evidence/{filename}",
                    "tests": [case["node"] for case in selected],
                    "tests_passed": sum(1 for case in selected if case["status"] == "passed"),
                    "checks": [{"name": name, "ok": ok} for name, ok in checks],
                    "measures": dict(measures),
                }
            )

    case_rows: list[dict[str, Any]] = []
    for index, case in enumerate(sorted(cases, key=lambda item: item["node"]), start=1):
        filename = write_case_file(index, case, requirement_of.get(case["node"]))
        case_rows.append({**case, "file": f"cases/{filename}"})

    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = len(cases) - passed
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "command": ".venv/bin/python -m pytest -v",
        "exit_code": returncode,
        "duration_s": round(elapsed, 3),
        "total": len(cases),
        "passed": passed,
        "failed": failed,
        "versions": runtime_versions(),
        "required": evidence_rows,
        "cases": case_rows,
    }
    (OUT / "results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    index_lines = [
        "# Risultati dei test",
        "",
        f"Generato: {payload['generated_utc']} · Comando: `{payload['command']}`",
        "",
        f"**{passed} superati, {failed} falliti, {len(cases)} casi in {elapsed:.2f} s** "
        f"(exit code {returncode}).",
        "",
        "## Test obbligatori del contratto",
        "",
        "| ID | Requisito | Esito | File | Test pytest |",
        "|---|---|---|---|---|",
    ]
    for row in evidence_rows:
        index_lines.append(
            f"| {row['id']} | {row['title']} | **{row['status']}** | "
            f"[{Path(row['file']).name}]({row['file']}) | "
            f"{row['tests_passed']}/{len(row['tests'])} superati |"
        )
    index_lines += [
        "",
        "## Tutti i casi",
        "",
        "| # | Caso | Stato | Durata (s) | File |",
        "|---|---|---|---|---|",
    ]
    for index, row in enumerate(case_rows, start=1):
        index_lines.append(
            f"| {index} | `{row['node']}` | {row['status'].upper()} | "
            f"{row['seconds']:.4f} | [{Path(row['file']).name}]({row['file']}) |"
        )
    index_lines += [
        "",
        "## File",
        "",
        "- `junit.xml` — risultato macchina-leggibile (JUnit XML)",
        "- `pytest.log` — log completo di pytest",
        "- `results.json` — tutti i casi e le evidenze in forma strutturata",
        "- `cases/` — un file per ogni caso di test",
        "- `evidence/` — un file per ogni test obbligatorio, con misure reali",
        "",
    ]
    (OUT / "index.md").write_text("\n".join(index_lines), encoding="utf-8")

    print(
        f"{passed}/{len(cases)} test superati in {elapsed:.2f} s; "
        f"{len(evidence_rows)} evidenze; report in {OUT}"
    )
    return 0 if returncode == 0 and all(row["status"] == "PASS" for row in evidence_rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
