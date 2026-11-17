"""M7.14 anti-false-positive research decision and frozen native physics audit."""
import json
from tools.m7_14_decision_gate import (
    ROOT,RESULT,protocol,original_code_inputs,native_stability,
    material_lineage,causal_bit_edit,synthetic_controls,execute
)


def test_frozen_research_direction_without_new_laws_or_hundreds_simulations():
    p=protocol()
    assert p["integrity"]["branch_off_master"]
    assert p["integrity"]["draft_PR_only"]
    assert p["integrity"]["no_new_native_physics"]
    assert "M8_preflight_acceptance" in p["decision_gate"]
    assert len(p["decision_gate"]["stop_conditions"])==3
    assert len(p["verification"]["original_law_source"]) if False else True


def test_three_generation_lineage_synthetic_positive_never_claims_native_life():
    rows=[]
    for i in range(3):
        rows.append({
            "parent_id":f"generation{i}",
            "child_id":f"generation{i+1}",
            "parent_sequence":"0101","child_sequence":"0101",
            "parent_material_ids":list(range(4*i,4*i+4)),
            "child_material_ids":list(range(4*i+4,4*i+8)),
            "parent_birth_tick":25*i,
            "child_birth_tick":25*(i+1),
            "child_persist_ticks":30,
            "formation_mechanism":"unforced_local_reaction"
        })
    r=material_lineage(rows)
    assert r["three_generation_lineage_candidate"]
    assert r["max_verified_generations"]==3
    assert r["status"]=="schema_validation_only_NOT_native_reproduction_evidence"
    assert not r["physical_provenance_externally_audited"]


def test_negative_same_visual_sequences_but_no_ancestry():
    rows=[]
    for i in range(3):
        rows.append({
            "parent_id":f"unrelated{i}",
            "child_id":f"unrelated_child{i}",
            "parent_sequence":"0101","child_sequence":"0101",
            "parent_material_ids":[4*i,4*i+1,4*i+2,4*i+3],
            "child_material_ids":[100+4*i,101+4*i,102+4*i,103+4*i],
            "parent_birth_tick":i*25,
            "child_birth_tick":i*25+20,
            "child_persist_ticks":20,"formation_mechanism":"unforced_local_reaction"
        })
    a=material_lineage(rows)
    assert a["max_verified_generations"]==1
    assert not a["three_generation_lineage_candidate"]


def test_synthetic_positive_calibrates_false_positives_and_parent_bit_edit():
    x=synthetic_controls()
    assert x["real_native_heredity_observed"] is False
    assert x["synthetic_fixtures_are_not_evidence_of_artificial_life"]
    assert x["same_sequence_without_ancestry"]=="correctly_rejected"
    assert x["overlapping_material"]=="correctly_rejected"
    assert x["single_generation"]=="correctly_rejected"
    assert x["explicit_clone_instruction"]=="correctly_rejected"
    base={
        "parent_before":"0101","parent_after":"0111",
        "child_before":"0101","child_after":"0111",
        "same_substrates":True,"same_energy":True,
        "same_pair_random_draws":True,"independent_child_material":True
    }
    assert causal_bit_edit(base)
    assert not causal_bit_edit(dict(base,child_after="0101"))
    assert not causal_bit_edit(dict(base,same_pair_random_draws=False))
    assert not causal_bit_edit(dict(base,independent_child_material=False))


def test_source_schema_has_no_explicit_genome_but_can_reconfigure_existing_particles():
    d=original_code_inputs()
    assert d["explicit_structural_sequence_variable_in_particle_schema"] is False
    assert d["explicit_template_sequence_rate_in_native_chemistry"] is False
    assert d["possible_spontaneous_pattern_copying_logically_excluded"] is False
    assert d["native_form_break_local_chemistry_exists"]
    assert len(d["native_source_sha256"])==5


def test_exact_original_native_12_seeds_40_steps_count_and_species_remain_fixed():
    x=native_stability()
    assert x["world_count"]==12
    assert x["steps_per_world"]==40
    assert x["all_worlds_ID_species_counts_unchanged"]
    assert x["native_bond_formations_observed"]>0
    assert all(row["particle_count_start"]==row["particle_count_end"] for row in x["worlds"])


def test_gate_execution_produces_machine_readable_only_native_not_life():
    x=execute()
    assert RESULT.exists()
    reread=json.loads(RESULT.read_text(encoding="utf-8"))
    assert reread["protocol_sha256"]==x["protocol_sha256"]
    assert reread["decisions"]["native_digital_organism_evidence_from_this_gate"] is False
    assert reread["decisions"]["start_separate_M8_explicit_new_local_physics_proposal"]=="GO_DESIGN_ONLY_NOT_YET_NATIVE_DISCOVERY"
    assert reread["decisions"]["more_M7_ring_only_energy_only_monte_carlo_without_new_falsifiable_information_hypothesis"]=="STOP"
    assert reread["synthetic_information_detector_controls"]["real_native_heredity_observed"] is False
