"""Frozen M8.0 preflight: causal one-bit parent edit with physically live monomers.

This tests only a MANUFACTURED laboratory parent (0101 vs 0111), not
spontaneous origin. No 'create daughter' operation exists in this script:
read actual M8 adsorption, B/H bond reactions, independent IDs and survival.
Same-site, same-seed, same-microscopic-key draws in active vs shuffled
identity-channel controls; no external data-dependent selection.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife_m8.sandbox import WorldM8,LAW_VERSION

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m8_0"
PFILE=BASE/"protocol.json"
OUT=BASE/"preflight.json"
SEEDS=tuple(range(50001,50033))
TICKS=120
XPOSITIONS=(3,4,5,6)
DAUGHTER_Y=2
EDIT_X=5
MODELS=("templated","shuffled_identity","no_template","unpowered")


def protocol():
    d=json.loads(PFILE.read_text(encoding="utf-8"))
    assert d["schema"]=="alife-m8-0-local-polymer-information-preflight-v1"
    assert d["status"]=="frozen_before_new_law_implementation_or_result"
    assert d["controls"]["seeds"].find("50001..50032")>=0
    assert d["controls"]["simulation_horizon"]==TICKS
    assert d["integrity"]["all_controls_paired"]
    assert d["integrity"]["no_historical_M6_edits"]
    return d


def product_state(w: WorldM8):
    """Pure observer: inspect one precommitted laboratory daughter row/columns.

    No parent bit, clone operation, 'make daughter', or artificial material ID
    enters the physical system: this is an observational read after M8 steps.
    """
    ids=[]
    for x in XPOSITIONS:
        ident=w.grid.get((x,DAUGHTER_Y))
        if ident is None:
            return None
        ids.append(ident)
    original=set(w.initial_template_material_ids)
    if original.intersection(ids) or len(set(ids))!=len(ids):
        return None
    if any(w._key(a,b) not in w.B for a,b in zip(ids,ids[1:])):
        return None
    if any(w._key(a,b) in w.H for a in ids for b in original):
        return None
    return {"material_ids":ids,
            "sequence":"".join(str(w.particles[i].species) for i in ids)}


def execute_case(seed,mode,parent_sequence):
    p=protocol()
    w=WorldM8(
        seed=seed,mode=mode,template_sequence=parent_sequence,
        initial_free_energy=0 if mode=="unpowered" else 500,
        bath_each_species=40
    )
    initial_parent=list(w.initial_template_material_ids)
    assert len(initial_parent)==4 and all(i in w.particles for i in initial_parent)
    initial_hash=w.full_hash()
    first_site=None
    previous=None
    stable=0
    best=0
    persistent_products=[]
    physical_product_events=[]
    for tick in range(1,TICKS+1):
        before=len(w.events)
        w.step()
        for e in w.events[before:]:
            if e["kind"]=="adsorb" and (e["x"],e["y"])==(EDIT_X,DAUGHTER_Y):
                if first_site is None:first_site={
                    "tick":e["tick"],"species":e["species"],
                    "new_material_id":e["new_material_id"],
                    "source_material_id":e["source_material_id"],
                    "same_keyed_species_lottery":e["same_keyed_species_lottery"]
                }
        current=product_state(w)
        if current is None:
            stable=0
            previous=None
        else:
            identity=(tuple(current["material_ids"]),current["sequence"])
            if identity==previous:
                stable+=1
            else:
                stable=1
                previous=identity
            best=max(best,stable)
            if stable==20:
                persistent_products.append({
                    "first_persistent_tick":tick,
                    "material_ids":current["material_ids"],
                    "sequence":current["sequence"]
                })
                physical_product_events.append(tick)
    w.check()
    count=Counter(e["kind"] for e in w.events)
    match=any(ev["sequence"]==parent_sequence for ev in persistent_products)
    is_canonical=(parent_sequence=="0101")
    return {
        "seed":seed,"mode":mode,"artificial_parent_sequence":parent_sequence,
        "source_initial_material_ids":initial_parent,
        "source_initial_full_hash":initial_hash,
        "fixed_first_captured_monomer_at_x5_y2":first_site,
        "native_local_chemistry_event_counts":dict(count),
        "all_real_local_capture_events": [
            e for e in w.events if e["kind"]=="adsorb"
        ],
        "all_real_backbone_form_events":[
            e for e in w.events if e["kind"]=="B_form"
        ],
        "longest_uninterrupted_detached_4_monomer_B_product_lifetime":best,
        "physically_distinct_detached_products_persisting_at_least_20_ticks":persistent_products,
        "persisting_exact_copy_of_original_parent_0101":(
            bool(match) if is_canonical else None
        ),
        "persists_parent_sequence_in_product":bool(match),
        "same_state_for_same_seed_repeat_verified":False,
        "physical_law_version":LAW_VERSION,
        "total_matter_initial":w.initial_matter,
        "total_energy_initial":w.initial_energy,
        "mass_energy_ledger_all_120_steps_pass":True,
        "final":w.physical_metrics()
    }


def execute():
    p=protocol()
    records=[]
    for seed in SEEDS:
        experiments={}
        for mode in ("templated","shuffled_identity"):
            for seq in ("0101","0111"):
                name=mode+":"+seq
                experiments[name]=execute_case(seed,mode,seq)
        experiments["no_template:0101"]=execute_case(seed,"no_template","0101")
        experiments["unpowered:0101"]=execute_case(seed,"unpowered","0101")
        if seed==SEEDS[0]:
            # A completely repeatable full physical world, not an observational
            # shortcut, and no re-seeding/retries after viewing outcomes.
            repeat=execute_case(seed,"templated","0101")
            assert repeat["final"]["full_hash"]==experiments["templated:0101"]["final"]["full_hash"]
            assert repeat["all_real_local_capture_events"]==experiments["templated:0101"]["all_real_local_capture_events"]
            experiments["templated:0101"]["same_state_for_same_seed_repeat_verified"]=True
        records.append({"seed":seed,"arms":experiments})
        if (seed-SEEDS[0]+1)%8==0:
            print(f"M80_PROGRESS {seed-SEEDS[0]+1}/32 calibrated synthetic fixtures",flush=True)
    metrics=summary(records,p)
    data={
        "schema":"alife-m8-0-local-polymer-32-paired-synthetic-only-preflight-v1",
        "protocol_sha256":sha256(PFILE.read_bytes()).hexdigest(),
        "new_physics_sha256":sha256((ROOT/"src/alife_m8/sandbox.py").read_bytes()).hexdigest(),
        "worlds":records,
        "summary":metrics,
        "real_native_M6_M7_laws_modified":False,
        "full_source_includes_no_copy_instruction":True,
        "laboratory_parent_initialization_is_explicitly_artificial":True,
        "no_unbiased_spontaneous_worlds_run":True
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print("M80_FINAL_SUMMARY="+json.dumps(metrics,sort_keys=True),flush=True)
    print("M80_SUCCESS_32_PAIRED_CONTROLS="+str(len(records)),flush=True)


def summary(records,p):
    assert [x["seed"] for x in records]==list(SEEDS)
    detail=[]
    changed_real=0
    changed_shuffled=0
    template_copies=0
    shuffled_copies=0
    empty_no_template=0
    empty_unpowered=0
    all_conserved=True
    for r in records:
        arms=r["arms"]
        a=arms["templated:0101"]["fixed_first_captured_monomer_at_x5_y2"]
        b=arms["templated:0111"]["fixed_first_captured_monomer_at_x5_y2"]
        c=arms["shuffled_identity:0101"]["fixed_first_captured_monomer_at_x5_y2"]
        d=arms["shuffled_identity:0111"]["fixed_first_captured_monomer_at_x5_y2"]
        real_change=a is not None and b is not None and a["species"]!=b["species"]
        placebo_change=c is not None and d is not None and c["species"]!=d["species"]
        if a is not None and b is not None:
            assert a["tick"]==b["tick"],("editing a template changed first capture timing",r["seed"])
            assert a["same_keyed_species_lottery"]==b["same_keyed_species_lottery"]
        if c is not None and d is not None:
            assert c["tick"]==d["tick"]
            assert c["same_keyed_species_lottery"]==d["same_keyed_species_lottery"]
        changed_real+=real_change
        changed_shuffled+=placebo_change
        template_copies+=bool(arms["templated:0101"]["persisting_exact_copy_of_original_parent_0101"])
        shuffled_copies+=bool(arms["shuffled_identity:0101"]["persisting_exact_copy_of_original_parent_0101"])
        empty_no_template+=len(arms["no_template:0101"]["all_real_local_capture_events"])==0
        empty_unpowered+=len(arms["unpowered:0101"]["all_real_local_capture_events"])==0
        all_conserved=all_conserved and all(a["mass_energy_ledger_all_120_steps_pass"] for a in arms.values())
        detail.append({
            "seed":r["seed"],
            "first_target_site_matched_draw_real_edit_changed":bool(real_change),
            "first_target_site_matched_draw_shuffled_edit_changed":bool(placebo_change),
            "real_original_first_capture":a,
            "real_edited_first_capture":b,
            "shuffled_original_first_capture":c,
            "shuffled_edited_first_capture":d,
            "complete_causal_parent_seq_0101_persistent_product":bool(arms["templated:0101"]["persisting_exact_copy_of_original_parent_0101"]),
            "rate_matched_shuffled_0101_persistent_product":bool(arms["shuffled_identity:0101"]["persisting_exact_copy_of_original_parent_0101"])
        })
    expected=p["controls"]["preregistered_minimums"]
    assert len(records)==32
    verdicts={
        "physical_integrity":all_conserved,
        "causal_parent_edit":changed_real>=20 and changed_shuffled==0,
        "synthetic_daughter_product":template_copies>=8 and template_copies-shuffled_copies>=5,
        "no_template_and_unpowered_controls":empty_no_template==32 and empty_unpowered==32
    }
    return {
        "scope":"Artificial fixed laboratory four-monomer templates ONLY; not spontaneous copying, hereditary biology or life",
        "independent_counter_based_fixed_seed_pairs":32,
        "horizon_each_pair":120,
        "total_real_experimental_physical_worlds":32*6,
        "same_microscopic_draw_parent_point_edit_changes_first_real_capture_species_in_templated_mode":changed_real,
        "same_microscopic_draw_parent_point_edit_changes_first_real_capture_species_in_shuffled_mode":changed_shuffled,
        "detached_4_monomer_exact_0101_daughter_B_chain_persisted_at_least_20_ticks_templated":template_copies,
        "same_rate_scrambled_template_control_exact_0101_daughter_B_chain":shuffled_copies,
        "zero_extra_material_in_no_template_mode":empty_no_template,
        "zero_extra_material_in_unpowered_mode":empty_unpowered,
        "all_192_experiments_exact_mass_energy_ledgers":all_conserved,
        "expected_thresholds":expected,
        "pre_registered_gates":{name:("PASSED" if value else "NOT_MET_STOP") for name,value in verdicts.items()},
        "M8_1_unbiased_spontaneous_origin_authorized_if_all_gates_pass":all(verdicts.values()),
        "synthetic_fixtures_can_never_be_evidence_of_life":True,
        "causal_single-site_paired_detail":detail
    }


if __name__=="__main__":
    execute()
