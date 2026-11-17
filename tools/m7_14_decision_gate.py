"""M7.14 research reset: executable capability and information-inheritance gate.

Base: master, NOT the stacked M7 branches. This script does not modify
the native physics or assert pattern copying is mathematically impossible.
It audits specific explicit laws and calibrates a future causal inheritance
detector with synthetic traces clearly NOT evidence of digital life.

Distinguish:
- M6 / M7 chemical bond structure persistence and stochastic reclosure;
- information-bearing new material offspring with causally traceable
  parent-to-child sequence and distinct material;
- inherited change persisting to grandchildren, checked in a controlled
  parent-edited counterpart with identical resources/random draws.
"""
from __future__ import annotations

import ast
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.config import Config, SpeciesConfig, ChemistryConfig, CatalysisRule
from alife.world import World
from alife.particles import ParticleStore

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_14_decision"
PROTOCOL=BASE/"protocol.json"
RESULT=BASE/"result.json"
SOURCES=(
    "src/alife/config.py","src/alife/particles.py",
    "src/alife/chemistry.py","src/alife/dynamics.py","src/alife/world.py"
)
SEEDS=tuple(range(41001,41013))
HORIZON=40
MIN_STABLE=20
MIN_GENERATIONS=3


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-14-mechanism-capability-and-decision-gate-v1"
    assert p["status"]=="frozen_before_gate_implementation_or_results"
    assert p["verification"]["simulation"].find("41001")>=0
    assert p["integrity"]["no_new_native_physics"]
    assert p["integrity"]["branch_off_master"]
    assert p["decision_gate"]["stop_conditions"]
    return p


def material_lineage(events):
    """Evaluate declared physical events, NOT infer from same visual signatures.

    Each event must have explicit parent ID, exact material ID sets, order,
    source sequences and persisted child. Three distinct parent-child edges
    are necessary; matching strings alone or recycled parent material fail.
    """
    assert isinstance(events,list)
    prior={}
    edges={}
    emitted={}
    reasons=[]
    for event in events:
        needed={
            "parent_id","child_id","parent_sequence","child_sequence",
            "parent_material_ids","child_material_ids","parent_birth_tick",
            "child_birth_tick","child_persist_ticks","formation_mechanism"
        }
        if not needed.issubset(event):
            reasons.append("missing_lineage_fields")
            continue
        parent,child=event["parent_id"],event["child_id"]
        parent_material=set(event["parent_material_ids"])
        child_material=set(event["child_material_ids"])
        if not parent_material or not child_material or parent_material.intersection(child_material):
            reasons.append("overlapping_or_empty_material")
            continue
        if (not isinstance(event["parent_sequence"],str)
            or not isinstance(event["child_sequence"],str)
            or len(event["parent_sequence"])<4
            or len(event["child_sequence"])!=len(event["parent_sequence"])
            or set(event["child_sequence"])-set("01")
            or set(event["parent_sequence"])-set("01")):
            reasons.append("no_defined_reproducible_sequence")
            continue
        if (event["parent_birth_tick"]>=event["child_birth_tick"]
            or event["child_persist_ticks"]<MIN_STABLE
            or parent==child):
            reasons.append("invalid_temporal_order_or_persistence")
            continue
        if event["formation_mechanism"]!="unforced_local_reaction":
            reasons.append("non_native_or_manually_copied_child")
            continue
        if parent in emitted and emitted[parent] != (
            event["parent_material_ids"],event["parent_sequence"]
        ):
            reasons.append("inconsistent_parent_material")
            continue
        if parent in prior:
            prev=prior[parent]
            if (tuple(event["parent_material_ids"])!=prev["material"]
                or event["parent_sequence"]!=prev["sequence"]
                or event["parent_birth_tick"]!=prev["birth_tick"]):
                reasons.append("parent_not_same_prior_child")
                continue
        if child in prior:
            reasons.append("duplicate_child_identity")
            continue
        prior[child]={
            "parent":parent,
            "birth_tick":event["child_birth_tick"],
            "material":tuple(event["child_material_ids"]),
            "sequence":event["child_sequence"]
        }
        emitted[parent]=(event["parent_material_ids"],event["parent_sequence"])
        edges[child]=parent
    deepest=0
    for child in edges:
        generation=0
        current=child
        seen=set()
        while current in edges and current not in seen:
            seen.add(current)
            generation+=1
            current=edges[current]
        if current in seen:
            reasons.append("cycle_in_lineage_records")
            continue
        deepest=max(deepest,generation)
    return {
        "physical_parent_child_edges_validated":len(edges),
        "max_verified_generations":deepest,
        "three_generation_lineage_candidate":deepest>=MIN_GENERATIONS,
        "reasons_rejected":sorted(Counter(reasons).items()),
        "physical_provenance_externally_audited":False,
        "status":"schema_validation_only_NOT_native_reproduction_evidence"
    }


def causal_bit_edit(control):
    """Toy data gate: require a specific changed parent bit changes child bit.

    A declarative calibration, NOT proof of causal intervention from a
    self-reported event. Native experiment will need full physical state
    evidence and pair-keyed common-RNG counterfactuals.
    """
    wanted={
        "parent_before","parent_after","child_before","child_after",
        "same_substrates","same_energy","same_pair_random_draws",
        "independent_child_material"
    }
    if not isinstance(control,dict) or not wanted.issubset(control):
        return False
    if not all(control[k] is True for k in (
        "same_substrates","same_energy","same_pair_random_draws",
        "independent_child_material"
    )):
        return False
    pa,pb,ca,cb=(control[x] for x in (
        "parent_before","parent_after","child_before","child_after"))
    if not all(isinstance(x,str) and len(x)>=4 and set(x)<=set("01") for x in (pa,pb,ca,cb)):
        return False
    if len({len(x) for x in (pa,pb,ca,cb)})!=1:
        return False
    changed=[i for i,(a,b) in enumerate(zip(pa,pb)) if a!=b]
    return (
        len(changed)==1
        and ca!=cb
        and ca==pa
        and cb==pb
        and all(ca[j]==cb[j] for j in range(len(ca)) if j!=changed[0])
    )


def synthetic_controls():
    """No positive here is an emergent organism: ONLY detector calibration."""
    def edge(g, parent=None,child=None, seq="0101",materials=None,
             parents=None,child_material=None,source="unforced_local_reaction"):
        parent=parent or f"G{g}"
        child=child or f"G{g+1}"
        return {
            "parent_id":parent,"child_id":child,
            "parent_sequence":seq,"child_sequence":seq,
            "parent_material_ids":parents if parents is not None else list(range(g*4,g*4+4)),
            "child_material_ids":child_material if child_material is not None else list(range((g+1)*4,(g+2)*4)),
            "parent_birth_tick":g*25,"child_birth_tick":(g+1)*25,
            "child_persist_ticks":30,"formation_mechanism":source
        }
    synthetic_valid=[edge(i) for i in range(3)]
    same_signature_no_link=[edge(i,parent=f"isolated{i}",child=f"isolated{i+10}") for i in range(3)]
    shared_material=[edge(i) for i in range(3)]
    shared_material[1]["child_material_ids"]=shared_material[1]["parent_material_ids"]
    one_generation=[edge(0)]
    manual_copy=[edge(i,source="explicit_clone_instruction") for i in range(3)]
    bit_edit={
        "parent_before":"0101","parent_after":"0111",
        "child_before":"0101","child_after":"0111",
        "same_substrates":True,"same_energy":True,
        "same_pair_random_draws":True,"independent_child_material":True
    }
    no_causal_change=dict(bit_edit,child_after="0101")
    disconnected=material_lineage(same_signature_no_link)
    good=material_lineage(synthetic_valid)
    shared=material_lineage(shared_material)
    only1=material_lineage(one_generation)
    manual=material_lineage(manual_copy)
    assert good["three_generation_lineage_candidate"]
    assert not disconnected["three_generation_lineage_candidate"]
    assert not shared["three_generation_lineage_candidate"]
    assert not only1["three_generation_lineage_candidate"]
    assert not manual["three_generation_lineage_candidate"]
    assert causal_bit_edit(bit_edit)
    assert not causal_bit_edit(no_causal_change)
    return {
        "three_generations_with_disjoint_IDs_and_explicit_parent_link":"pass_synthetic_positive",
        "same_sequence_without_ancestry":"correctly_rejected",
        "overlapping_material":"correctly_rejected",
        "single_generation":"correctly_rejected",
        "explicit_clone_instruction":"correctly_rejected",
        "controlled_single_parent_bit_edit_changes_child":"pass_synthetic_positive",
        "parent_bit_edit_child_unaffected":"correctly_rejected",
        "real_native_heredity_observed":False,
        "synthetic_fixtures_are_not_evidence_of_artificial_life":True
    }


def original_code_inputs():
    """Audit exact original immutable source and the law's explicit inputs."""
    files={name:ROOT/name for name in SOURCES}
    tree={name:ast.parse(file.read_text(encoding="utf-8"))
          for name,file in files.items()}
    functions={}
    for name,module in tree.items():
        functions[name]={
            x.name for x in ast.walk(module)
            if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))
        }
    assert {"form_bonds","break_bonds","_candidate_pairs","_catalysis_factor"}.issubset(
        functions["src/alife/chemistry.py"])
    assert {"_propose_moves","step"}.issubset(
        functions["src/alife/dynamics.py"])
    assert {"advance","create"}.issubset(
        functions["src/alife/world.py"])
    fields=set(SpeciesConfig.__dataclass_fields__)
    assert fields=={"name","count","move_probability","energy","max_bonds"}
    assert set(CatalysisRule.__dataclass_fields__)=={"catalyst","pair","factor"}
    assert "ids" in ParticleStore.__slots__ and "species" in ParticleStore.__slots__
    assert not any(x in ParticleStore.__slots__ for x in (
        "genome","heritable_sequence","replication_program","memory"))
    explicit_chemistry=files["src/alife/chemistry.py"].read_text(encoding="utf-8")
    # A simple law signature fact, not a claim no emergent material information.
    assert "_candidate_pairs" in explicit_chemistry
    assert "_catalysis_factor" in explicit_chemistry
    return {
        "native_source_sha256":{
            k:sha256(p.read_bytes()).hexdigest() for k,p in files.items()
        },
        "persistent_particles_store_fields":list(ParticleStore.__slots__),
        "immutable_species_config_fields":sorted(fields),
        "catalog_catalysis_rule_fields":sorted(CatalysisRule.__dataclass_fields__),
        "explicit_structural_sequence_variable_in_particle_schema":False,
        "explicit_template_sequence_rate_in_native_chemistry":False,
        "native_form_break_local_chemistry_exists":True,
        "possible_spontaneous_pattern_copying_logically_excluded":False,
        "finding":"Current native laws have species-dependent chemistry and degree, energy, adjacency and species-catalyst dependence, but no explicit sequence reading or heritable copy reaction; graph topology can influence these local conditions indirectly."
    }


def native_stability():
    cfg_original=json.loads((ROOT/"configs/m2_quick.json").read_text(encoding="utf-8"))
    rows=[]
    for seed in SEEDS:
        cfg=dict(cfg_original)
        cfg["seed"]=seed
        world=World.create(Config.from_dict(cfg).validate())
        initial_ids=tuple(world.store.ids)
        initial_species=tuple(world.store.species)
        initial_energy=world.energy()
        for _ in range(HORIZON):
            world.advance(1)
            assert tuple(world.store.ids)==initial_ids
            assert tuple(world.store.species)==initial_species
            assert len(world.store)==len(initial_ids)
        world.check()
        rows.append({
            "seed":seed,"steps":world.step,
            "particle_count_start":len(initial_ids),
            "particle_count_end":len(world.store),
            "all_persistent_material_ids_unchanged":True,
            "all_particle_species_unchanged":True,
            "native_bonds_formed_total":world.bonds_formed_total,
            "native_bonds_broken_total":world.bonds_broken_total,
            "energy_start":initial_energy,"energy_end":world.energy(),
            "final_full_state_hash":world.state_hash_full()
        })
    return {
        "config":"unchanged master configs/m2_quick.json; only seed varies",
        "numeric_seed_first":SEEDS[0],"numeric_seed_last":SEEDS[-1],
        "world_count":len(rows),"steps_per_world":HORIZON,
        "all_worlds_ID_species_counts_unchanged":True,
        "native_bond_formations_observed":sum(x["native_bonds_formed_total"] for x in rows),
        "worlds":rows,
        "note":"Finite sample verifies implemented simulator behavior; no proof that fixed material forbids copying material structure."
    }


def execute():
    p=protocol()
    psha=sha256(PROTOCOL.read_bytes()).hexdigest()
    law=original_code_inputs()
    native=native_stability()
    calibration=synthetic_controls()
    stop={
        "more_M7_ring_only_energy_only_monte_carlo_without_new_falsifiable_information_hypothesis":
            "STOP",
        "current_M6_chemistry_can_make_structures_but_has_explicit_heritable_sequence_copying":
            "NO",
        "causal_information_detector_controls_all_work":
            "PASS_CALIBRATION_ONLY",
        "start_separate_M8_explicit_new_local_physics_proposal":
            "GO_DESIGN_ONLY_NOT_YET_NATIVE_DISCOVERY",
        "prior_original_laws_unmodified":True,
        "native_digital_organism_evidence_from_this_gate":False
    }
    obj={
        "schema":"alife-m7-14-mechanism-research-decision-result-v1",
        "protocol_sha256":psha,
        "law_audit":law,
        "native_stability":native,
        "synthetic_information_detector_controls":calibration,
        "decisions":stop,
        "scientific_status":"original_native_physics_capability_and_detector_calibration_only",
        "frozen_next_preflight_acceptance":p["decision_gate"]["M8_preflight_acceptance"],
        "stopping_rules":p["decision_gate"]["stop_conditions"]
    }
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("M714_FINAL="+json.dumps({
        "native_original_seed_worlds":len(native["worlds"]),
        "native_steps_each":HORIZON,
        "native_particle_ID_species_unchanged":True,
        "native_bonds_formed":native["native_bond_formations_observed"],
        "detector_calibration":calibration,
        "decision":stop
    },sort_keys=True),flush=True)
    return obj


if __name__=="__main__":
    execute()
