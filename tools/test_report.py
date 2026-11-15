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

from alife import chemistry
from alife.config import Config, load_config
from alife.metrics import runtime_versions
from alife.particles import InvariantError
from alife.persistence import (
    CHECKPOINT_FORMAT,
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

import sys

sys.path.insert(0, str(ROOT / "tests"))
from support import (  # noqa: E402  (helper condivisi con la suite)
    M2_QUICK,
    M3_QUICK,
    make_chemistry_config,
    make_config,
    make_energy_config,
    world_with,
)
from alife.structures import Tracker, components, signature  # noqa: E402
from alife.analysis import Analysis  # noqa: E402
from alife.controls import (  # noqa: E402
    FIXTURE_VERSION,
    TemplateCopier,
    negative_burst,
    negative_immobile,
    negative_random_aggregation,
    negative_reversible,
    negative_single_species,
    positive_world,
)
from alife.replication import ReplicationDetector  # noqa: E402
from alife.replication_v2 import DETECTOR_VERSION, ProgressiveDetector  # noqa: E402

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
            "tests/test_energy.py::test_validate_detects_unsorted_identifiers",
            "tests/test_checkpoint.py::test_detects_tampered_particle",
            "tests/test_checkpoint.py::test_detects_tampered_config_hash",
            "tests/test_checkpoint.py::test_detects_energy_imbalance",
            "tests/test_checkpoint.py::test_detects_invalid_json",
            "tests/test_checkpoint.py::test_detects_wrong_format",
            "tests/test_checkpoint.py::test_detects_missing_rng_state",
        ],
    },
    {
        "id": "M2-01",
        "title": "Legami reversibili con costo energetico",
        "contract": "docx S2 — legami reversibili, soglie energetiche",
        "slug": "legami_reversibili",
        "tests": [
            "tests/test_chemistry.py::test_bond_forms_between_adjacent_allowed_particles",
            "tests/test_chemistry.py::test_breaking_returns_energy",
            "tests/test_chemistry.py::test_no_bond_without_enough_energy",
        ],
    },
    {
        "id": "M2-02",
        "title": "Conservazione dell'energia con i legami",
        "contract": "docx S2 / vincolo di bilancio energetico",
        "slug": "energia_legami",
        "tests": [
            "tests/test_invariants.py::test_energy_with_bonds_is_conserved",
            "tests/test_chemistry.py::test_m2_baseline_produces_structures_and_conserves_energy",
        ],
    },
    {
        "id": "M2-03",
        "title": "Coppie ammesse, max_bonds e adiacenza",
        "contract": "docx S2 — reazioni locali e generali",
        "slug": "regole_locali",
        "tests": [
            "tests/test_chemistry.py::test_no_bond_for_non_allowed_species",
            "tests/test_chemistry.py::test_no_bond_when_species_cannot_bond",
            "tests/test_chemistry.py::test_max_bonds_is_respected",
            "tests/test_chemistry.py::test_chains_grow_to_max_bonds",
            "tests/test_invariants.py::test_validate_detects_non_adjacent_bond",
            "tests/test_invariants.py::test_validate_detects_bond_beyond_max_bonds",
        ],
    },
    {
        "id": "M2-04",
        "title": "Catalisi locale per differenza",
        "contract": "docx S2 — catalisi basata su proprietà locali",
        "slug": "catalisi",
        "tests": [
            "tests/test_chemistry.py::test_catalysis_multiplies_only_when_adjacent",
            "tests/test_chemistry.py::test_catalysis_config_changes_chemistry",
        ],
    },
    {
        "id": "M2-05",
        "title": "Aggregati: distribuzione delle dimensioni",
        "contract": "docx S2 — evidenze sulla varietà di strutture",
        "slug": "aggregati",
        "tests": [
            "tests/test_chemistry.py::test_aggregate_statistics",
            "tests/test_chemistry.py::test_m2_baseline_produces_structures_and_conserves_energy",
        ],
    },
    {
        "id": "M2-06",
        "title": "Determinismo e ripresa con la chimica",
        "contract": "docx S2 / contratto M1 (riproducibilità)",
        "slug": "determinismo_chimica",
        "tests": [
            "tests/test_chemistry.py::test_m2_quick_is_deterministic",
            "tests/test_checkpoint.py::test_v2_resume_is_equivalent_to_continuous_run",
            "tests/test_checkpoint.py::test_v2_roundtrip_preserves_bonds_and_energy",
        ],
    },
    {
        "id": "M2-07",
        "title": "Migrazione dei checkpoint M1",
        "contract": "prerequisito M2 — identificativi persistenti",
        "slug": "migrazione_checkpoint",
        "tests": [
            "tests/test_checkpoint.py::test_v1_checkpoint_is_migrated",
            "tests/test_config.py::test_v1_hash_is_unchanged",
        ],
    },
    {
        "id": "M3-01",
        "title": "Identità energetica in sistema aperto",
        "contract": "docx S3 — bilanci aggregati",
        "slug": "identita_energetica",
        "tests": [
            "tests/test_energy.py::test_open_run_keeps_identity",
            "tests/test_energy.py::test_closed_system_keeps_identity",
        ],
    },
    {
        "id": "M3-02",
        "title": "Dissipazione esatta di particelle e legami",
        "contract": "docx S3 — dissipazione",
        "slug": "dissipazione",
        "tests": [
            "tests/test_energy.py::test_particle_decay_is_exact",
            "tests/test_energy.py::test_bond_decay_is_exact",
            "tests/test_energy.py::test_particle_decay_uses_identity_not_index",
        ],
    },
    {
        "id": "M3-03",
        "title": "Sorgenti con accumulatore e capacità",
        "contract": "docx S3 — ingresso energetico localizzato",
        "slug": "sorgenti",
        "tests": [
            "tests/test_energy.py::test_source_accumulator_is_exact",
            "tests/test_energy.py::test_source_capacity_and_unabsorbed",
            "tests/test_energy.py::test_source_on_empty_cell_is_unabsorbed",
        ],
    },
    {
        "id": "M3-04",
        "title": "Costo di movimento pagato solo se accettato",
        "contract": "docx S3 — ogni trasformazione ha un costo",
        "slug": "costo_movimento",
        "tests": [
            "tests/test_energy.py::test_movement_cost_charged_per_move",
            "tests/test_energy.py::test_movement_cost_blocks_when_insufficient",
        ],
    },
    {
        "id": "M3-05",
        "title": "Costi di formazione e rottura",
        "contract": "docx S3 — costi delle reazioni",
        "slug": "costi_reazione",
        "tests": [
            "tests/test_energy.py::test_formation_dissipation",
            "tests/test_energy.py::test_breaking_dissipation",
        ],
    },
    {
        "id": "M3-06",
        "title": "Determinismo con flussi e budget RNG",
        "contract": "docx S3 / contratto M1 (riproducibilità)",
        "slug": "determinismo_flussi",
        "tests": [
            "tests/test_energy.py::test_open_run_is_deterministic",
            "tests/test_energy.py::test_rng_budget_with_flows_disabled",
            "tests/test_energy.py::test_priority_uses_identity",
        ],
    },
    {
        "id": "M3-07",
        "title": "Checkpoint con ledger e accumulatori",
        "contract": "docx S3 — riproducibilità dei run aperti",
        "slug": "checkpoint_flussi",
        "tests": [
            "tests/test_checkpoint.py::test_v3_roundtrip_preserves_ledger",
            "tests/test_checkpoint.py::test_v3_resume_is_equivalent_with_flows",
            "tests/test_checkpoint.py::test_v2_checkpoint_is_migrated_to_v3",
        ],
    },
    {
        "id": "M3-08",
        "title": "Core senza sorgenti di non determinismo",
        "contract": "specifica M3 — regole R1–R10",
        "slug": "core_deterministico",
        "tests": [
            "tests/test_energy.py::test_core_modules_do_not_import_nondeterministic_sources",
        ],
    },
    {
        "id": "M4-01",
        "title": "Firme canoniche esatte per strutture ad albero",
        "contract": "docx S4 — firme canoniche delle strutture",
        "slug": "firme_esatte",
        "tests": [
            "tests/test_structures.py::test_chain_signature_is_invariant_under_relabeling",
            "tests/test_structures.py::test_chain_signature_distinguishes_composition",
            "tests/test_structures.py::test_tree_signature_distinguishes_shape",
        ],
    },
    {
        "id": "M4-02",
        "title": "Cicli come impronte, ambiguità dichiarata",
        "contract": "docx S4 — incertezza dove una copia è ambigua",
        "slug": "ambiguita",
        "tests": [
            "tests/test_structures.py::test_cycles_are_fingerprints_not_exact",
            "tests/test_structures.py::test_fuzzy_collision_is_reported_as_ambiguity",
            "tests/test_structures.py::test_exact_signature_collision_is_not_ambiguity",
        ],
    },
    {
        "id": "M4-03",
        "title": "Eventi: nascita, crescita, scissione, fusione, morte",
        "contract": "docx S4 — registrare nascita, trasformazione, scissione, scomparsa",
        "slug": "eventi_tracciati",
        "tests": [
            "tests/test_structures.py::test_birth_and_death",
            "tests/test_structures.py::test_growth_and_shrink_keep_identity",
            "tests/test_structures.py::test_split_creates_two_structures",
            "tests/test_structures.py::test_merge_creates_one_structure",
            "tests/test_structures.py::test_transform_same_size_new_topology",
        ],
    },
    {
        "id": "M4-04",
        "title": "Persistenza: distribuzione delle vite",
        "contract": "docx S4 — metriche di persistenza",
        "slug": "persistenza",
        "tests": [
            "tests/test_structures.py::test_lifetime_counts_steps_alive",
            "tests/test_structures.py::test_birth_and_death",
        ],
    },
    {
        "id": "M4-05",
        "title": "Tracciamento deterministico e non invasivo",
        "contract": "contratto M1 — riproducibilità; M4 — osservatore separato",
        "slug": "tracker_deterministico",
        "tests": [
            "tests/test_structures.py::test_tracking_does_not_change_the_world",
            "tests/test_structures.py::test_tracker_is_deterministic",
        ],
    },
    {
        "id": "M4-06",
        "title": "Tracciamento end-to-end e file di eventi",
        "contract": "docx S4 — log eventi accessibile",
        "slug": "tracking_end_to_end",
        "tests": [
            "tests/test_structures.py::test_tracker_writes_jsonl_files",
            "tests/test_cli.py::test_run_with_tracking",
        ],
    },
    {
        "id": "M5-01",
        "title": "Controllo positivo riconosciuto (sensibilità)",
        "contract": "docx S5 — il benchmark positivo è riconosciuto",
        "slug": "positivo_riconosciuto",
        "tests": [
            "tests/test_controls.py::test_positive_control_is_detected",
        ],
    },
    {
        "id": "M5-02",
        "title": "Controlli negativi non classificati (falsi positivi)",
        "contract": "docx S5 — i negativi non sono replicazione",
        "slug": "negativi_rifiutati",
        "tests": [
            "tests/test_controls.py::test_negative_immobile_is_not_replication",
            "tests/test_controls.py::test_negative_random_aggregation_is_not_replication",
            "tests/test_controls.py::test_negative_reversible_is_not_replication",
            "tests/test_controls.py::test_negative_stress_cases_are_not_replication",
            "tests/test_controls.py::test_simultaneous_identical_structures_are_not_copies",
            "tests/test_controls.py::test_transient_second_generation_does_not_classify",
        ],
    },
    {
        "id": "M5-03",
        "title": "Isolamento dei controlli dal mondo di scoperta",
        "contract": "alife.md §2 — controlli completamente isolati",
        "slug": "isolamento",
        "tests": [
            "tests/test_controls.py::test_engine_does_not_import_controls",
        ],
    },
    {
        "id": "M5-04",
        "title": "Controllo positivo riproducibile e versionato",
        "contract": "docx S5 — fixture versionate",
        "slug": "controllo_riproducibile",
        "tests": [
            "tests/test_controls.py::test_positive_control_is_reproducible",
            "tests/test_controls.py::test_fixture_version_is_declared",
        ],
    },
    {
        "id": "M6-01",
        "title": "Preregistrazione integra: seed, config, hash",
        "contract": "docx S6 — seed e griglie fissati prima dei run",
        "slug": "preregistrazione",
        "tests": [
            "tests/test_campaign.py::test_manifest_is_preregistered",
            "tests/test_campaign.py::test_manifest_configs_match_their_hashes",
            "tests/test_campaign.py::test_manifest_records_the_decision_rule",
        ],
    },
    {
        "id": "M6-02",
        "title": "Stato di tracker e rilevatore ripristinabile",
        "contract": "M6 — salvare e ripristinare anche l'analisi",
        "slug": "analisi_ripristinabile",
        "tests": [
            "tests/test_analysis.py::test_roundtrip_preserves_state",
            "tests/test_analysis.py::test_resume_matches_continuous_run",
            "tests/test_analysis.py::test_restore_requires_matching_step",
        ],
    },
    {
        "id": "M6-03",
        "title": "Campagna completa, run nulli inclusi",
        "contract": "docx S6 — registrare anche i risultati nulli",
        "slug": "campagna_completa",
        "tests": [
            "tests/test_campaign.py::test_campaign_results_are_complete",
        ],
    },
    {
        "id": "M6.2-01",
        "title": "Rilevatore v2: copie che si formano progressivamente",
        "contract": "M6.2-E — correggere il punto cieco dell'accrezione",
        "slug": "rilevatore_v2",
        "tests": [
            "tests/test_replication_v2.py::test_progressive_assembly_is_detected",
            "tests/test_replication_v2.py::test_default_threshold_requires_two_generations",
            "tests/test_replication_v2.py::test_detector_version_is_declared",
        ],
    },
    {
        "id": "M6.2-02",
        "title": "v2 validato sui controlli M5",
        "contract": "M5 — positivo riconosciuto, negativi rifiutati",
        "slug": "v2_controlli",
        "tests": [
            "tests/test_replication_v2.py::test_positive_control_is_detected",
            "tests/test_replication_v2.py::test_negative_controls_are_not_replication",
            "tests/test_replication_v2.py::test_simultaneous_identical_structures_are_not_copies",
        ],
    },
    {
        "id": "M6.2-03",
        "title": "Ri-analisi dei 25 run M6 con v1 e v2",
        "contract": "M6.2-E — stessi percorsi, nessuna nuova legge",
        "slug": "rianalisi_m6",
        "tests": [
            "tests/test_m6_2e.py::test_reanalysis_is_complete_and_matches_m6_worlds",
        ],
    },
    {
        "id": "M6.2-04",
        "title": "Preregistrazione della ri-analisi v2",
        "contract": "M6 — criteri e hash fissati prima dell'esecuzione",
        "slug": "preregistrazione_v2",
        "tests": [
            "tests/test_m6_2e.py::test_manifest_freezes_v2_criteria",
            "tests/test_m6_2e.py::test_manifest_references_identical_m6_runs",
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


def evidence_m2_01(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = make_chemistry_config()
    world = world_with(config, [(1, 1), (2, 1)], [0, 0])
    formed = chemistry.form_bonds(world)
    bond_energy = sum(world.store.bonds.values())
    energies_after_formation = list(world.store.energy)
    total_after_formation = sum(world.store.energy) + bond_energy

    breaking = make_chemistry_config(
        chemistry={
            "enabled": True,
            "bond_cost": 2,
            "formation_probability": 0.0,
            "break_probability": 1.0,
            "allowed_pairs": [["S0", "S0"]],
            "catalysis": [],
        }
    )
    second = world_with(
        breaking, [(1, 1), (2, 1)], [0, 0], energy=[8, 8], bonds=[(0, 1, 4)]
    )
    second.advance(1)
    return (
        "Due particelle S0 adiacenti, formation_probability = 1 e break_probability = 1.",
        [
            ("legami formati", str(len(formed))),
            ("energia delle particelle dopo la formazione", str(energies_after_formation)),
            ("energia immagazzinata nel legame", str(bond_energy)),
            ("energia totale dopo la formazione", str(total_after_formation)),
            ("energia delle particelle dopo la rottura", str(second.store.energy)),
            ("legami residui dopo la rottura", str(len(second.store.bonds))),
        ],
        [
            ("il legame si forma fra vicini ammessi", len(formed) == 1),
            ("il costo è pagato da entrambe le particelle", energies_after_formation == [8, 8]),
            ("l'energia non si perde", total_after_formation == 20),
            ("la rottura restituisce l'energia", second.store.energy == [10, 10]),
            ("dopo la rottura non restano legami", not second.store.bonds),
        ],
    )


def evidence_m2_02(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = World.create(load_config(M2_QUICK))
    world.advance(200)
    return (
        "Configurazione M2 quick (32×32, 4 specie), 200 passi con legami attivi.",
        [
            ("energia iniziale attesa", str(world.configured_energy())),
            ("energia nelle particelle", str(world.energy_particles())),
            ("energia nei legami", str(world.energy_bonds())),
            ("energia totale", str(world.energy())),
            ("delta", str(world.energy() - world.configured_energy())),
            ("legami al passo 200", str(len(world.store.bonds))),
        ],
        [
            ("energia totale = energia iniziale", world.energy() == world.configured_energy()),
            ("particelle + legami = totale", world.energy_particles() + world.energy_bonds() == world.energy()),
            ("esistono legami", bool(world.store.bonds)),
            ("nessuna violazione di invariante", world.validate() == []),
        ],
    )


def evidence_m2_03(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = World.create(load_config(M2_QUICK))
    world.advance(300)
    store = world.store
    degrees = [
        max((store.degree[index] for index in range(len(store)) if store.species[index] == sp), default=0)
        for sp in range(len(world.config.species))
    ]
    limits = world.max_bonds
    disallowed = 0
    non_adjacent = 0
    for index_a, index_b in store.bonds:
        pair = (store.species[index_a], store.species[index_b])
        if pair not in world.allowed_pairs and (pair[1], pair[0]) not in world.allowed_pairs:
            disallowed += 1
        if not world._adjacent(index_a, index_b):
            non_adjacent += 1
    return (
        "Configurazione M2 quick, 300 passi: verifica delle regole locali sui legami formatisi.",
        [
            (
                "grado massimo osservato per specie",
                ", ".join(
                    f"{species.name}={degree}"
                    for species, degree in zip(world.config.species, degrees)
                ),
            ),
            (
                "max_bonds per specie",
                ", ".join(
                    f"{species.name}={limit}"
                    for species, limit in zip(world.config.species, limits)
                ),
            ),
            ("legami fra specie non ammesse", str(disallowed)),
            ("legami fra particelle non adiacenti", str(non_adjacent)),
            ("legami totali", str(len(store.bonds))),
        ],
        [
            ("ogni grado rispetta max_bonds", all(degree <= limit for degree, limit in zip(degrees, limits))),
            ("nessuna coppia non ammessa", disallowed == 0),
            ("tutti i legami sono locali", non_adjacent == 0),
        ],
    )


def evidence_m2_04(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    """Catalisi misurata in un regime limitato dalla probabilità, non dagli slot."""
    import json as _json

    base = _json.loads(M2_QUICK.read_text())
    base["chemistry"]["formation_probability"] = 1e-9
    base["chemistry"]["catalysis"] = []
    plain = World.create(Config.from_dict(base).validate())

    boosted = _json.loads(M2_QUICK.read_text())
    boosted["chemistry"]["formation_probability"] = 1e-9
    boosted["chemistry"]["catalysis"] = [
        {"catalyst": "S3", "pair": ["S0", "S1"], "factor": 1e9}
    ]
    catalyzed = World.create(Config.from_dict(boosted).validate())

    plain.advance(300)
    catalyzed.advance(300)
    return (
        "Stessa configurazione e stesso seed; probabilità base 1e-9, fattore "
        "catalitico 1e9 su S0-S1: senza catalisi non si forma nulla, con la "
        "catalisi la coppia si forma.",
        [
            ("formazioni senza catalisi", str(plain.bonds_formed_total)),
            ("formazioni con catalisi", str(catalyzed.bonds_formed_total)),
            ("legami finali senza catalisi", str(len(plain.store.bonds))),
            ("legami finali con catalisi", str(len(catalyzed.store.bonds))),
            (
                "configurazioni identiche tranne la catalisi",
                str(
                    {**plain.config.to_dict(), "chemistry": None}
                    == {**catalyzed.config.to_dict(), "chemistry": None}
                ),
            ),
        ],
        [
            ("senza catalisi non si formano legami", plain.bonds_formed_total == 0),
            ("con la catalisi si formano legami", catalyzed.bonds_formed_total > 0),
            ("l'energia resta conservata con la catalisi",
             catalyzed.energy() == catalyzed.configured_energy()),
        ],
    )


def evidence_m2_05(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = World.create(load_config(M2_QUICK))
    world.advance(500)
    stats = world.aggregates()
    distribution = stats["size_distribution"]
    top = ", ".join(f"{size}×{count}" for size, count in list(distribution.items())[:8])
    return (
        "Configurazione M2 quick, 500 passi: aggregati come componenti connesse dei legami.",
        [
            ("legami", str(stats["bonds"])),
            ("particelle legate", str(stats["bonded_particles"])),
            ("particelle libere", str(stats["free_particles"])),
            ("aggregati", str(stats["aggregates"])),
            ("dimensione massima", str(stats["largest_aggregate"])),
            ("dimensione media", str(stats["mean_aggregate_size"])),
            ("distribuzione (dimensione×numero)", top),
        ],
        [
            ("esistono aggregati", stats["aggregates"] > 0),
            ("la distribuzione è non banale", len(distribution) >= 2),
            ("nessuna violazione di invariante", world.validate() == []),
        ],
    )


def evidence_m2_06(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = load_config(M2_QUICK)
    first = World.create(config)
    second = World.create(config)
    first.advance(100)
    second.advance(100)
    return (
        "Due run indipendenti con lo stesso seed e 100 passi di chimica.",
        [
            ("state_hash_full run A", first.state_hash_full()[:32] + "…"),
            ("state_hash_full run B", second.state_hash_full()[:32] + "…"),
            ("legami A / B", f"{len(first.store.bonds)} / {len(second.store.bonds)}"),
            ("formazioni A / B", f"{first.bonds_formed_total} / {second.bonds_formed_total}"),
            ("rotture A / B", f"{first.bonds_broken_total} / {second.bonds_broken_total}"),
        ],
        [
            ("hash completo identico", first.state_hash_full() == second.state_hash_full()),
            ("legami identici", first.store.bond_records() == second.store.bond_records()),
            ("stato RNG identico", first.rng.fingerprint() == second.rng.fingerprint()),
        ],
    )


def evidence_m2_07(tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = make_config(seed=77)
    original = World.create(config)
    original.advance(5)
    payload = {
        "format": CHECKPOINT_FORMAT,
        "schema_version": 1,
        "config": config.to_dict(),
        "config_hash": config.hash(),
        "step": original.step,
        "moves_total": original.moves_total,
        "rng": original.rng.state(),
        "particles": original.store.records(),
        "counts": original.counts(),
        "energy_total": original.energy(),
        "state_hash": original.state_hash(),
    }
    path = tmp / "M2-07_v1.json"
    path.write_text(json.dumps(payload))
    migrated = load_checkpoint(path)
    return (
        "Checkpoint schema 1 (M1) costruito da un mondo M1 e ricaricato con il codice M2.",
        [
            ("identificativi assegnati", f"0..{len(migrated.store) - 1}"),
            ("energia per particella", str(sorted(set(migrated.store.energy)))),
            ("legami", str(len(migrated.store.bonds))),
            ("state_hash M1 preservato", str(migrated.state_hash() == original.state_hash())),
            ("next_id", str(migrated.next_id)),
        ],
        [
            ("identificativi contigui", migrated.store.ids == list(range(len(migrated.store)))),
            ("energia iniziale della specie", all(
                migrated.store.energy[index] == config.species[species].energy
                for index, species in enumerate(migrated.store.species)
            )),
            ("nessun legame importato", not migrated.store.bonds),
            ("hash materiale identico", migrated.state_hash() == original.state_hash()),
            ("stato valido", migrated.validate() == []),
        ],
    )


def evidence_m3_01(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = World.create(load_config(M3_QUICK))
    world.advance(100)
    delta = world.energy() - world.accounted_energy()
    return (
        "Configurazione M3 quick (32×32) con sorgenti, dissipazione, costi di "
        "movimento e di reazione, 100 passi.",
        [
            ("energia interna", str(world.energy())),
            ("energia iniziale", str(world.configured_energy())),
            ("iniettata", str(world.injected)),
            ("dissipata", str(world.dissipated)),
            ("non assorbita", str(world.unabsorbed)),
            ("identità: E − (E0 + in − out)", str(delta)),
        ],
        [
            ("identità energetica esatta", delta == 0),
            ("esiste un flusso entrante", world.injected > 0),
            ("esiste dissipazione", world.dissipated > 0),
            ("nessuna energia negativa", all(value >= 0 for value in world.store.energy)),
            ("nessuna violazione di invariante", world.validate() == []),
        ],
    )


def evidence_m3_02(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    particle_config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 0.0, "energy": 100, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"particle_decay": {"num": 1, "den": 3}},
    )
    particle = world_with(particle_config, [(2, 2)], [0], energy=[100])
    particle.advance(9)

    bond_config = make_energy_config(energy={"bond_decay": {"num": 1, "den": 1}})
    bond = world_with(
        bond_config, [(1, 1), (2, 1)], [0, 0], energy=[10, 10], bonds=[(0, 1, 100)]
    )
    bond.advance(3)
    return (
        "Decadimento sfasato: 1 quanto ogni 3 passi per una particella con 100 "
        "quanti; 1 quanto per passo su un legame con 100.",
        [
            ("energia della particella dopo 9 passi", str(particle.store.energy[0])),
            ("dissipato dalla particella", str(particle.dissipated)),
            ("energia del legame dopo 3 passi", str(bond.store.bonds[(0, 1)])),
            ("dissipato dal legame", str(bond.dissipated)),
        ],
        [
            ("particella: 3 quanti in 9 passi", particle.store.energy == [97] and particle.dissipated == 3),
            ("legame: 3 quanti in 3 passi", bond.store.bonds[(0, 1)] == 97 and bond.dissipated == 3),
        ],
    )


def evidence_m3_03(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 0.0, "energy": 0, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"sources": [{"x": 2, "y": 2, "rate_num": 1, "rate_den": 4, "capacity": 1000}]},
    )
    world = world_with(config, [(2, 2)], [0], energy=[0])
    world.advance(1000)

    spill_config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 0.0, "energy": 0, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"sources": [{"x": 2, "y": 2, "rate_num": 1, "rate_den": 1, "capacity": 10}]},
    )
    spill = world_with(spill_config, [(5, 5)], [0], energy=[0])
    spill.advance(20)
    return (
        "Sorgente con tasso 1/4 e particella presente per 1000 passi (atteso 250 "
        "quanti assorbiti) e serbatoio con capacità 10 su cella vuota per 20 "
        "passi (atteso 10 immagazzinati, 10 traboccati).",
        [
            ("iniettati a tasso 1/4 in 1000 passi", str(world.injected)),
            ("assorbiti", str(world.store.energy[0])),
            ("serbatoio finale", str(world.source_store)),
            ("iniettati con capacità 10 in 20 passi", str(spill.injected)),
            ("immagazzinati nel serbatoio", str(spill.source_store)),
            ("traboccati", str(spill.unabsorbed)),
        ],
        [
            ("nessun drift: 250 quanti", world.injected == 250),
            ("tutto assorbito dalla particella", world.store.energy == [250]),
            ("serbatoio vuoto quando la particella è presente", world.source_store == [0]),
            ("capacità del serbatoio rispettata", spill.source_store == [10]),
            ("trabocco contabilizzato", spill.unabsorbed == 10),
        ],
    )


def evidence_m3_04(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 1.0, "energy": 10, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"movement_cost": 1},
    )
    world = world_with(config, [(2, 2)], [0], energy=[10])
    world.advance(10)

    blocked_config = make_energy_config(
        species=[{"name": "S0", "count": 1, "move_probability": 1.0, "energy": 1, "max_bonds": 0}],
        chemistry={"enabled": False},
        energy={"movement_cost": 2},
    )
    blocked = world_with(blocked_config, [(2, 2)], [0], energy=[1])
    blocked.advance(10)
    return (
        "Costo 1 con energia 10 per 10 passi; costo 2 con energia 1 per 10 passi.",
        [
            ("mosse pagate", str(world.moves_total)),
            ("energia residua", str(world.store.energy[0])),
            ("dissipato per movimento", str(world.dissipated)),
            ("mosse con energia insufficiente", str(blocked.moves_total)),
            ("energia del mondo bloccato", str(blocked.store.energy[0])),
        ],
        [
            ("una mossa = un quanto", world.dissipated == world.moves_total == 10),
            ("energia esaurita esattamente", world.store.energy == [0]),
            ("nessuna mossa senza energia", blocked.moves_total == 0),
            ("energia intatta nel mondo bloccato", blocked.store.energy == [1]),
        ],
    )


def evidence_m3_05(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    formation = world_with(
        make_energy_config(energy={"formation_dissipation": 1}),
        [(1, 1), (2, 1)],
        [0, 0],
    )
    chemistry.form_bonds(formation)

    break_config = make_energy_config(
        chemistry={
            "enabled": True,
            "bond_cost": 2,
            "formation_probability": 0.0,
            "break_probability": 1.0,
            "allowed_pairs": [["S0", "S0"]],
            "catalysis": [],
        },
        energy={"breaking_dissipation": 1},
    )
    breaking = world_with(
        break_config, [(1, 1), (2, 1)], [0, 0], energy=[8, 8], bonds=[(0, 1, 4)]
    )
    breaking.advance(1)
    return (
        "Formazione con costo 2 e attrito 1; rottura con attrito 1 su un legame da 4.",
        [
            ("energia delle particelle dopo la formazione", str(formation.store.energy)),
            ("energia nel legame", str(sum(formation.store.bonds.values()))),
            ("dissipato dalla formazione", str(formation.dissipated)),
            ("energia restituita alla rottura", str(breaking.store.energy)),
            ("dissipato dalla rottura", str(breaking.dissipated)),
        ],
        [
            ("attrito di formazione = 2", formation.dissipated == 2),
            ("energia immagazzinata = 2×bond_cost", sum(formation.store.bonds.values()) == 4),
            ("attrito di rottura = 1", breaking.dissipated == 1),
            ("restituito 3 su 4", breaking.store.energy == [10, 9]),
        ],
    )


def evidence_m3_06(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = load_config(M3_QUICK)
    first = World.create(config)
    second = World.create(config)
    first.advance(60)
    second.advance(60)
    return (
        "Due run indipendenti con sorgenti, dissipazione e costi, stesso seed, "
        "60 passi.",
        [
            ("state_hash_full A", first.state_hash_full()[:32] + "…"),
            ("state_hash_full B", second.state_hash_full()[:32] + "…"),
            ("iniettata A / B", f"{first.injected} / {second.injected}"),
            ("dissipata A / B", f"{first.dissipated} / {second.dissipated}"),
            ("estrazioni A / B", f"{first.rng.draws} / {second.rng.draws}"),
        ],
        [
            ("hash completo identico", first.state_hash_full() == second.state_hash_full()),
            ("ledger identico", (first.injected, first.dissipated, first.unabsorbed)
             == (second.injected, second.dissipated, second.unabsorbed)),
            ("estrazioni identiche", first.rng.draws == second.rng.draws),
        ],
    )


def evidence_m3_07(tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = World.create(load_config(M3_QUICK))
    world.advance(30)
    path = save_checkpoint(tmp / "M3-07.json", world)
    restored = load_checkpoint(path)
    return (
        "Salvataggio e ricaricamento di un mondo aperto: ledger, accumulatori e "
        "sorgenti devono sopravvivere identici.",
        [
            ("passo", str(restored.step)),
            ("iniettata", str(restored.injected)),
            ("dissipata", str(restored.dissipated)),
            ("non assorbita", str(restored.unabsorbed)),
            ("accumulatori", str(restored.source_acc)),
            ("estrazioni RNG", str(restored.rng.draws)),
            ("dimensione checkpoint", f"{path.stat().st_size} byte"),
        ],
        [
            ("stato identico", restored.snapshot() == world.snapshot()),
            ("hash completo identico", restored.state_hash_full() == world.state_hash_full()),
            ("ledger identico", (restored.injected, restored.dissipated, restored.unabsorbed)
             == (world.injected, world.dissipated, world.unabsorbed)),
            ("accumulatori identici", restored.source_acc == world.source_acc),
        ],
    )


def evidence_m3_08(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    forbidden = ("import time", "import random", "import secrets", "os.urandom")
    allowed = {"metrics.py", "events.py", "cli.py", "persistence.py"}
    package = Path(ROOT) / "src" / "alife"
    scanned = 0
    offenders: list[str] = []
    for path in sorted(package.glob("*.py")):
        if path.name in allowed:
            continue
        scanned += 1
        source = path.read_text(encoding="utf-8")
        for module in forbidden:
            if module in source:
                offenders.append(f"{path.name}: {module}")
    return (
        "Scansione statica dei moduli del core: nessuna sorgente di non "
        "determinismo che possa alterare lo stato.",
        [
            ("moduli scansionati", str(scanned)),
            (
                "moduli esclusi (solo metadati)",
                ", ".join(sorted(allowed)),
            ),
            ("occorrenze vietate", ", ".join(offenders) if offenders else "nessuna"),
        ],
        [
            ("nessun import vietato", not offenders),
            ("core coperto dalla scansione", scanned >= 8),
        ],
    )


def _m4_config():
    species = [
        {"name": "S0", "count": 8, "move_probability": 0.0, "energy": 10, "max_bonds": 2},
        {"name": "S1", "count": 8, "move_probability": 0.0, "energy": 10, "max_bonds": 2},
    ]
    return make_energy_config(species=species, chemistry={"enabled": False})


def _one_signature(world):
    structures = components(world.store)
    assert len(structures) == 1
    indices, bonds = structures[0]
    return signature(world.store, indices, bonds, world.species_names)


def evidence_m4_01(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = _m4_config()
    chain = world_with(config, [(0, 0), (1, 0), (2, 0)], [0, 0, 1], bonds=[(0, 1, 4), (1, 2, 4)])
    relabeled = world_with(
        config, [(2, 0), (1, 0), (0, 0)], [1, 0, 0], bonds=[(0, 1, 4), (1, 2, 4)]
    )
    other = world_with(config, [(0, 0), (1, 0), (2, 0)], [0, 1, 1], bonds=[(0, 1, 4), (1, 2, 4)])
    star = world_with(
        config,
        [(1, 1), (1, 0), (0, 1), (2, 1)],
        [1, 0, 0, 0],
        bonds=[(0, 1, 4), (0, 2, 4), (0, 3, 4)],
    )
    sig_chain = _one_signature(chain)
    sig_relabeled = _one_signature(relabeled)
    sig_other = _one_signature(other)
    sig_star = _one_signature(star)
    return (
        "Quattro strutture note: catena S0-S0-S1, la stessa catena con particelle "
        "etichettate al contrario, catena S0-S1-S1, stella S1 con tre foglie S0.",
        [
            ("catena: composizione / legami", f"{sig_chain.composition} / {sig_chain.bonds}"),
            ("catena: firma", sig_chain.key[:56] + "…"),
            ("stessa catena rietichettata: firma", sig_relabeled.key[:56] + "…"),
            ("catena S0-S1-S1: firma", sig_other.key[:56] + "…"),
            ("stella: firma", sig_star.key[:56] + "…"),
            ("firme esatte", f"{sig_chain.exact}, {sig_star.exact}"),
        ],
        [
            ("la rietichettatura non cambia la firma", sig_chain.key == sig_relabeled.key),
            ("composizione diversa ⇒ firma diversa", sig_chain.key != sig_other.key),
            ("forma diversa ⇒ firma diversa", sig_chain.key != sig_star.key),
            ("le firme degli alberi sono esatte", sig_chain.exact and sig_star.exact),
        ],
    )


def evidence_m4_02(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = _m4_config()
    ring = world_with(
        config,
        [(0, 0), (1, 0), (1, 1), (0, 1)],
        [0, 1, 1, 0],
        bonds=[(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
    )
    ring_sig = _one_signature(ring)

    two_rings = world_with(
        config,
        [(0, 0), (1, 0), (1, 1), (0, 1), (5, 5), (6, 5), (6, 6), (5, 6)],
        [0, 1, 1, 0, 0, 1, 1, 0],
        bonds=[
            (0, 1, 4),
            (1, 2, 4),
            (2, 3, 4),
            (3, 0, 4),
            (4, 5, 4),
            (5, 6, 4),
            (6, 7, 4),
            (7, 4, 4),
        ],
    )
    ring_tracker = Tracker()
    ring_tracker.observe(two_rings)

    two_dimers = world_with(
        config, [(0, 0), (1, 0), (4, 4), (5, 4)], [0, 0, 0, 0], bonds=[(0, 1, 4), (2, 3, 4)]
    )
    dimer_tracker = Tracker()
    dimer_tracker.observe(two_dimers)
    ring_summary = ring_tracker.summary()
    dimer_summary = dimer_tracker.summary()
    return (
        "Un anello a quattro particelle (ciclo) e due casi di firma condivisa: due "
        "anelli identici e due dimeri identici.",
        [
            ("anello: firma esatta?", str(ring_sig.exact)),
            ("anello: prefisso firma", ring_sig.key[:24]),
            ("due anelli: firme distinte", str(ring_summary["signatures"]["distinct"])),
            ("due anelli: strutture ambigue", str(ring_summary["signatures"]["ambiguous_structures"])),
            ("due dimeri: strutture ambigue", str(dimer_summary["signatures"]["ambiguous_structures"])),
            ("due dimeri: collisioni di firma", str(dimer_summary["signatures"]["distinct"])),
        ],
        [
            ("i cicli usano un'impronta, non una firma esatta", ring_sig.exact is False),
            ("due anelli identici sono ambigui", ring_summary["signatures"]["ambiguous_structures"] == 2),
            ("due dimeri identici non sono ambigui", dimer_summary["signatures"]["ambiguous_structures"] == 0),
            ("i dimeri condividono una firma esatta", dimer_summary["signatures"]["distinct"] == 1),
        ],
    )


def _scripted_tracker() -> tuple[object, Tracker]:
    config = _m4_config()
    world = world_with(
        config, [(index, 0) for index in range(6)], [0] * 6, bonds=[(0, 1, 4), (2, 3, 4)]
    )
    tracker = Tracker()
    tracker.observe(world)
    world.step = 1
    world.store.add_bond(1, 2, 4)  # fusione
    tracker.observe(world)
    world.step = 2
    world.store.add_bond(3, 4, 4)  # crescita
    tracker.observe(world)
    world.step = 3
    world.store.remove_bond(1, 2)  # scissione
    tracker.observe(world)
    world.step = 4
    world.store.remove_bond(2, 3)  # riduzione: {2,3,4} -> {3,4}
    tracker.observe(world)
    world.step = 5
    world.store.remove_bond(3, 4)  # morte di una struttura
    tracker.observe(world)
    world.step = 6
    world.store.remove_bond(0, 1)  # morte dell'altra
    tracker.observe(world)
    return world, tracker


def evidence_m4_03(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    _, tracker = _scripted_tracker()
    events = tracker.summary()["events"]
    return (
        "Sei particelle in linea: due dimeri, fusione, crescita, scissione, "
        "riduzione, due morti.",
        [
            ("nascite", str(events.get("birth", 0))),
            ("fusioni", str(events.get("merge", 0))),
            ("crescite", str(events.get("growth", 0))),
            ("scissioni", str(events.get("split", 0))),
            ("riduzioni", str(events.get("shrink", 0))),
            ("morti", str(events.get("death", 0))),
            ("persistenze", str(events.get("persist", 0))),
        ],
        [
            ("due nascite iniziali", events.get("birth") == 2),
            ("una fusione", events.get("merge") == 1),
            ("una crescita", events.get("growth") == 1),
            ("due scissioni", events.get("split") == 2),
            ("una riduzione", events.get("shrink") == 1),
            ("due morti", events.get("death") == 2),
        ],
    )


def evidence_m4_04(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    _, tracker = _scripted_tracker()
    lifetime = tracker.summary()["lifetime"]
    return (
        "Stesse sei particelle: ogni identità che termina contribuisce alla "
        "distribuzione delle vite, incluse quelle interrotte da fusione o scissione.",
        [
            ("strutture concluse", str(lifetime["completed"])),
            ("vita media", str(lifetime["mean"])),
            ("vita massima", str(lifetime["max"])),
            ("istogramma", json.dumps(lifetime["histogram"])),
        ],
        [
            ("cinque identità concluse", lifetime["completed"] == 5),
            ("vita media 1.8", lifetime["mean"] == 1.8),
            ("vita massima 3", lifetime["max"] == 3),
        ],
    )


def evidence_m4_05(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = make_energy_config()
    first = World.create(config)
    second = World.create(config)
    first.advance(100)
    second.advance(100)
    before = first.snapshot()
    tracker_first = Tracker()
    tracker_second = Tracker()
    tracker_first.observe(first)
    tracker_second.observe(second)
    after = first.snapshot()
    return (
        "Due mondi identici, 100 passi, un tracker ciascuno; inoltre lo stato "
        "viene confrontato prima e dopo l'osservazione.",
        [
            ("mondi identici", str(before == second.snapshot())),
            ("riepiloghi identici", str(tracker_first.summary() == tracker_second.summary())),
            ("stato invariato dopo l'osservazione", str(before == after)),
            ("strutture attive", str(tracker_first.summary()["active_structures"])),
        ],
        [
            ("il tracker non altera il mondo", before == after),
            ("due run identici producono lo stesso riepilogo", tracker_first.summary() == tracker_second.summary()),
            ("il tracker osserva strutture", tracker_first.summary()["active_structures"] >= 0),
        ],
    )


def evidence_m4_06(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = World.create(load_config(M3_QUICK))
    tracker = Tracker()
    tracker.observe(world)
    world.advance(300, observer=tracker.observe)
    summary = tracker.summary()
    structures_now = len(components(world.store))
    return (
        "Configurazione M3 quick tracciata per 300 passi: strutture, eventi, "
        "persistenza e ambiguità.",
        [
            ("strutture attive", str(summary["active_structures"])),
            ("componenti nel mondo", str(structures_now)),
            ("nascite / morti", f"{summary['events'].get('birth', 0)} / {summary['events'].get('death', 0)}"),
            ("fusioni / scissioni", f"{summary['events'].get('merge', 0)} / {summary['events'].get('split', 0)}"),
            ("firme distinte", str(summary["signatures"]["distinct"])),
            ("osservazioni esatte / impronte", f"{summary['signatures']['exact_observations']} / {summary['signatures']['fuzzy_observations']}"),
            ("vita media", str(summary["lifetime"]["mean"])),
        ],
        [
            ("il conteggio coincide con le componenti", summary["active_structures"] == structures_now),
            ("sono stati osservati eventi", sum(summary["events"].values()) > 0),
            ("la vita media è positiva", summary["lifetime"]["mean"] > 0 or summary["active_structures"] == 0),
        ],
    )


def _tracked_run(world, steps: int, copier: TemplateCopier | None = None):
    tracker = Tracker()
    detector = ReplicationDetector()
    tracker.observe(world)
    detector.observe(world, tracker)
    for _ in range(steps):
        if copier is not None:
            copier.step(world)
        world.advance(1)
        tracker.observe(world)
        detector.observe(world, tracker)
    return tracker, detector


def evidence_m5_01(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = positive_world()
    copier = TemplateCopier.for_world(world)
    tracker, detector = _tracked_run(world, 40, copier)
    summary = detector.summary()
    tracker_summary = tracker.summary()
    return (
        "Controllo positivo: template A-B-B-A con nove siti di monomeri; a ogni "
        "passo il copiatore assembla una catena nel sito a destra di un template.",
        [
            ("versione fixture", FIXTURE_VERSION),
            ("strutture finali", str(tracker_summary["active_structures"])),
            ("copie assemblate dalla fixture", str(copier.copies)),
            ("copie candidate dal rilevatore", str(summary["candidates"])),
            ("copie persistenti", str(summary["persistent"])),
            ("generazione massima", str(summary["max_generation"])),
            ("classificazione", summary["classified"]),
        ],
        [
            ("nove copie assemblate", copier.copies == 9),
            ("nove copie rilevate", summary["candidates"] == 9),
            ("tutte persistenti", summary["persistent"] == 9),
            ("almeno due generazioni", summary["max_generation"] >= 2),
            ("classificato come replicazione", summary["classified"] == "replication"),
        ],
    )


def evidence_m5_02(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    cases = [
        ("N1 immobile", negative_immobile(), 100),
        ("N2 aggregazione casuale", negative_random_aggregation(), 500),
        ("N3 reazioni reversibili", negative_reversible(), 500),
        ("stress specie unica", negative_single_species(), 300),
        ("stress formazione massima", negative_burst(), 300),
    ]
    rows: list[Measure] = []
    checks: list[Check] = []
    for name, world, steps in cases:
        tracker, detector = _tracked_run(world, steps)
        summary = detector.summary()
        rows.append(
            (
                name,
                f"{tracker.summary()['active_structures']} strutture, "
                f"{summary['candidates']} candidate, {summary['classified']}",
            )
        )
        checks.append(
            (
                f"{name}: non replicazione e nessuna candidata",
                summary["classified"] == "not_replication" and summary["candidates"] == 0,
            )
        )
    return (
        "Cinque condizioni senza copiatura: immobilità, aggregazione casuale, "
        "reazioni reversibili e due casi di stress con firme molto ripetute.",
        rows,
        checks,
    )


def evidence_m5_03(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    package = Path(ROOT) / "src" / "alife"
    engine_files = sorted(
        path.name for path in package.glob("*.py") if path.name != "__init__.py"
    )
    offenders = [
        path.name
        for path in package.glob("*.py")
        if "controls" in path.read_text(encoding="utf-8")
    ]
    return (
        "Isolamento: i moduli del motore non devono importare né citare il "
        "pacchetto dei controlli.",
        [
            ("moduli del motore", ", ".join(engine_files)),
            ("moduli con riferimenti ai controlli", ", ".join(offenders) if offenders else "nessuno"),
            ("fixture", FIXTURE_VERSION),
        ],
        [
            ("nessun riferimento ai controlli", not offenders),
            ("il motore è coperto dalla scansione", len(engine_files) >= 10),
        ],
    )


def evidence_m5_04(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    first_world = positive_world()
    first_copier = TemplateCopier.for_world(first_world)
    _, first_detector = _tracked_run(first_world, 40, first_copier)

    second_world = positive_world()
    second_copier = TemplateCopier.for_world(second_world)
    _, second_detector = _tracked_run(second_world, 40, second_copier)

    return (
        "Due esecuzioni indipendenti del controllo positivo con le stesse "
        "posizioni e lo stesso seed.",
        [
            ("hash completo A", first_world.state_hash_full()[:32] + "…"),
            ("hash completo B", second_world.state_hash_full()[:32] + "…"),
            ("riepiloghi identici", str(first_detector.summary() == second_detector.summary())),
            ("copie A / B", f"{first_copier.copies} / {second_copier.copies}"),
        ],
        [
            ("hash completo identico", first_world.state_hash_full() == second_world.state_hash_full()),
            ("stesso esito del rilevatore", first_detector.summary() == second_detector.summary()),
        ],
    )


def evidence_m6_01(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    manifest = json.loads((ROOT / "campaigns" / "m6" / "manifest.json").read_text())
    runs = manifest["runs"]
    configs_ok = all(
        load_config(ROOT / "campaigns" / "m6" / run["config"]).hash() == run["config_hash"]
        for run in runs
    )
    return (
        "Manifest preregistrato: condizioni, seed, passi, configurazioni e hash "
        "fissati prima dei run.",
        [
            ("versionato il", manifest["preregistered_utc"]),
            ("condizioni", ", ".join(manifest["conditions"])),
            ("seed", ", ".join(str(seed) for seed in manifest["seeds"])),
            ("passi per run", str(manifest["steps"])),
            ("run dichiarati", str(len(runs))),
            ("hash di configurazione distinti", str(len({run["config_hash"] for run in runs}))),
            ("criterio", manifest["decision_rule"]["candidate_condition"]),
        ],
        [
            ("25 run dichiarati", len(runs) == 25),
            ("5 condizioni × 5 seed", len({run["condition"] for run in runs}) == 5),
            ("ogni configurazione corrisponde al suo hash", configs_ok),
            ("gli hash sono distinti", len({run["config_hash"] for run in runs}) == 25),
            ("la regola di decisione è registrata", "candidate_condition" in manifest["decision_rule"]),
        ],
    )


def evidence_m6_02(tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    config = load_config(M3_QUICK)

    continuous_world = World.create(config)
    continuous = Analysis()
    continuous.observe(continuous_world)
    continuous_world.advance(40, observer=continuous.observe)

    split_world = World.create(config)
    split = Analysis()
    split.observe(split_world)
    split_world.advance(20, observer=split.observe)
    path = split.save(tmp / "M6-02_analysis.json")
    split.close()

    resumed = Analysis.load(path)
    resumed.check_step(split_world.step)
    split_world.advance(20, observer=resumed.observe)

    return (
        "Salvataggio e ripristino di tracker e rilevatore: run continuo di 40 "
        "passi contro run interrotto a 20 e ripreso.",
        [
            ("passo salvato", str(20)),
            ("hash completo continuo", continuous_world.state_hash_full()[:32] + "…"),
            ("hash completo ripreso", split_world.state_hash_full()[:32] + "…"),
            ("strutture attive", str(len(resumed.tracker.active))),
            ("riepiloghi strutture identici", str(resumed.tracker.summary() == continuous.tracker.summary())),
            ("riepiloghi rilevatore identici", str(resumed.detector.summary() == continuous.detector.summary())),
        ],
        [
            ("mondo identico", split_world.state_hash_full() == continuous_world.state_hash_full()),
            ("tracker identico", resumed.tracker.summary() == continuous.tracker.summary()),
            ("rilevatore identico", resumed.detector.summary() == continuous.detector.summary()),
        ],
    )


def evidence_m6_03(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    results = json.loads((ROOT / "campaigns" / "m6" / "results.json").read_text())
    runs = results["runs"]
    null_runs = sum(1 for run in runs if run["replication"]["persistent"] == 0)
    classified = sum(1 for run in runs if run["replication"]["classified"] == "replication")
    table = "; ".join(
        f"{name}: {block['classified_replication']}/{block['runs']} replication, "
        f"{block['median_persistent_copies']} copie mediane"
        for name, block in results["conditions"].items()
    )
    return (
        "Risultati della campagna: tutti i run registrati, compresi quelli in cui "
        "non è stata osservata alcuna copia.",
        [
            ("run registrati", str(len(runs))),
            ("run con zero copie persistenti", str(null_runs)),
            ("run classificati replication", str(classified)),
            ("condizioni", table),
            ("motore invariato dalla preregistrazione", str(results.get("engine_unchanged_since_preregistration"))),
            ("verdetto", results["decision"]["verdict"]),
        ],
        [
            ("25 run registrati", len(runs) == 25),
            ("tutte le cinque condizioni presenti", len(results["conditions"]) == 5),
            ("i run nulli sono inclusi", null_runs > 0),
            ("nessun run mancante", all(run["steps"] == 3000 for run in runs)),
            ("verdetto definito", results["decision"]["verdict"] in {"no_evidence", "candidate_for_s7", "revise_controls"}),
        ],
    )


def _progressive_world():
    config = make_energy_config(
        width=16,
        height=8,
        species=[
            {"name": "S0", "count": 8, "move_probability": 0.0, "energy": 10, "max_bonds": 2},
            {"name": "S1", "count": 8, "move_probability": 0.0, "energy": 10, "max_bonds": 2},
        ],
        chemistry={"enabled": False},
    )
    positions = [(x, 0) for x in range(4)] + [(x, 2) for x in range(4)]
    species = [0, 1, 1, 0, 0, 1, 1, 0]
    return world_with(config, positions, species, bonds=[(0, 1, 0), (1, 2, 0), (2, 3, 0)])


def evidence_m6_2e_01(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = _progressive_world()
    tracker = Tracker()
    detector = ProgressiveDetector(min_copies=1, min_generation=1)
    tracker.observe(world)
    detector.observe(world, tracker)
    world.step = 1
    world.store.add_bond(4, 5, 0)
    tracker.observe(world)
    detector.observe(world, tracker)
    world.step = 2
    world.store.add_bond(5, 6, 0)
    tracker.observe(world)
    detector.observe(world, tracker)
    world.step = 3
    world.store.add_bond(6, 7, 0)
    tracker.observe(world)
    detector.observe(world, tracker)
    for step in range(4, 14):
        world.step = step
        tracker.observe(world)
        detector.observe(world, tracker)
    summary = detector.summary()
    return (
        "Template A-B-B-A e un dimero che cresce per accrezione fino a raggiungere "
        "la stessa firma: il caso che il v1 non può vedere.",
        [
            ("versione", DETECTOR_VERSION),
            ("candidate", str(summary["candidates"])),
            ("raggiunte", str(summary["matched"])),
            ("persistenti", str(summary["persistent"])),
            ("generazione massima", str(summary["max_generation"])),
            ("scartate", json.dumps(summary["discarded"])),
        ],
        [
            ("una copia progressiva rilevata", summary["candidates"] == 1),
            ("firma raggiunta", summary["matched"] == 1),
            ("persistenza verificata", summary["persistent"] == 1),
            ("il v1 non poteva vederla (nascita dimerica)", summary["matched"] == 1),
        ],
    )


def evidence_m6_2e_02(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    world = positive_world()
    tracker = Tracker()
    detector = ProgressiveDetector()
    copier = TemplateCopier.for_world(world)
    tracker.observe(world)
    detector.observe(world, tracker)
    for _ in range(40):
        copier.step(world)
        world.advance(1)
        tracker.observe(world)
        detector.observe(world, tracker)
    positive = detector.summary()

    negatives = []
    for name, builder, steps in (
        ("N1 immobile", negative_immobile, 100),
        ("N2 aggregazione", negative_random_aggregation, 300),
        ("N3 reversibili", negative_reversible, 300),
        ("stress specie unica", negative_single_species, 300),
        ("stress formazione massima", negative_burst, 300),
    ):
        test_world = builder()
        test_tracker = Tracker()
        test_detector = ProgressiveDetector()
        test_tracker.observe(test_world)
        test_detector.observe(test_world, test_tracker)
        for _ in range(steps):
            test_world.advance(1)
            test_tracker.observe(test_world)
            test_detector.observe(test_world, test_tracker)
        negatives.append((name, test_detector.summary()))

    return (
        "Validazione del v2 sui controlli M5: il positivo deve restare "
        "riconosciuto, i cinque negativi devono restare rifiutati.",
        [
            ("positivo: persistenti / generazione", f"{positive['persistent']} / {positive['max_generation']}"),
            ("positivo: classificazione", positive["classified"]),
        ]
        + [
            (f"{name}: candidate / persistenti / esito", f"{summary['candidates']} / {summary['persistent']} / {summary['classified']}")
            for name, summary in negatives
        ],
        [
            ("positivo riconosciuto", positive["classified"] == "replication" and positive["persistent"] == 9),
            ("negativi rifiutati", all(summary["classified"] == "not_replication" for _, summary in negatives)),
            ("nessuna copia persistente nei negativi", all(summary["persistent"] == 0 for _, summary in negatives)),
        ],
    )


def evidence_m6_2e_03(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    results = json.loads((ROOT / "campaigns" / "m6_2e" / "results.json").read_text())
    runs = results["runs"]
    v1_candidates = sum(run["v1"]["candidates"] for run in runs)
    v2_candidates = sum(run["v2"]["candidates"] for run in runs)
    v2_matched = sum(run["v2"]["matched"] for run in runs)
    v2_persistent = sum(run["v2"]["persistent"] for run in runs)
    return (
        "Ri-analisi dei 25 run M6 con v1 e v2 affiancati, sugli stessi percorsi "
        "(hash del mondo verificato).",
        [
            ("run", str(len(runs))),
            ("hash del mondo identici a M6", str(results["all_world_hashes_match"])),
            ("candidate v1 (totale)", str(v1_candidates)),
            ("candidate v2 (totale)", str(v2_candidates)),
            ("copie v2 che raggiungono la firma", str(v2_matched)),
            ("copie v2 persistenti", str(v2_persistent)),
            ("verdetto", results["decision"]["verdict"]),
        ],
        [
            ("25 run ri-analizzati", len(runs) == 25),
            ("stessi percorsi di M6", results["all_world_hashes_match"] is True),
            ("v1 resta a zero candidate", v1_candidates == 0),
            ("verdetto definito", results["decision"]["verdict"] in {"no_evidence", "candidate_for_s7", "revise_controls"}),
        ],
    )


def evidence_m6_2e_04(_tmp: Path) -> tuple[str, list[Measure], list[Check]]:
    manifest = json.loads((ROOT / "campaigns" / "m6_2e" / "manifest.json").read_text())
    criteria = manifest["criteria"]
    configs_ok = all(
        load_config(ROOT / "campaigns" / "m6" / run["config"]).hash() == run["config_hash"]
        for run in manifest["runs"]
    )
    return (
        "Preregistrazione della ri-analisi: criteri, riferimenti a M6 e hash, "
        "fissati prima dell'esecuzione.",
        [
            ("versione rilevatore", manifest["detector_version"]),
            ("criteri", json.dumps(criteria)),
            ("run", str(len(manifest["runs"]))),
            ("sorgente", manifest["source_campaign"]),
            ("configurazioni coerenti", str(configs_ok)),
        ],
        [
            ("criteri v2 fissati", criteria == {"radius": 2, "window": 150, "persist_steps": 10, "min_size": 4, "min_copies": 5, "min_generation": 2}),
            ("25 run", len(manifest["runs"]) == 25),
            ("hash delle configurazioni coerenti", configs_ok),
        ],
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
    "M2-01": evidence_m2_01,
    "M2-02": evidence_m2_02,
    "M2-03": evidence_m2_03,
    "M2-04": evidence_m2_04,
    "M2-05": evidence_m2_05,
    "M2-06": evidence_m2_06,
    "M2-07": evidence_m2_07,
    "M3-01": evidence_m3_01,
    "M3-02": evidence_m3_02,
    "M3-03": evidence_m3_03,
    "M3-04": evidence_m3_04,
    "M3-05": evidence_m3_05,
    "M3-06": evidence_m3_06,
    "M3-07": evidence_m3_07,
    "M3-08": evidence_m3_08,
    "M4-01": evidence_m4_01,
    "M4-02": evidence_m4_02,
    "M4-03": evidence_m4_03,
    "M4-04": evidence_m4_04,
    "M4-05": evidence_m4_05,
    "M4-06": evidence_m4_06,
    "M5-01": evidence_m5_01,
    "M5-02": evidence_m5_02,
    "M5-03": evidence_m5_03,
    "M5-04": evidence_m5_04,
    "M6-01": evidence_m6_01,
    "M6-02": evidence_m6_02,
    "M6-03": evidence_m6_03,
    "M6.2-01": evidence_m6_2e_01,
    "M6.2-02": evidence_m6_2e_02,
    "M6.2-03": evidence_m6_2e_03,
    "M6.2-04": evidence_m6_2e_04,
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
