"""M8.0 independent outcome observer on the ORIGINAL fixed 32×6 physical data.

Does NOT call M8.0 preflight execute_case(), product_state(), summary() or
any mutable preflight data generator. Re-runs the precommitted synthetic cases
on the unchanged NEW M8 simulator, verifies event traces, independent material
ID B-component ancestry, 20 physically detached consecutive ticks, exact
energy/matter ledgers and full hashes against the immutable CI artifact.

The simulator law is shared; this is an INDEPENDENT OUTCOME DETECTOR and
same-law physical replay, NOT independent implementation of physical laws,
not a new biological sample or evidence of spontaneous emergence.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from alife_m8.sandbox import WorldM8

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m8_0"
RAW=BASE/"preflight.json"
OUT=BASE/"independent_observer_audit.json"
COLS=(3,4,5,6)
TICKS=120
MODES=("templated","shuffled_identity","no_template","unpowered")
SEEDS=tuple(range(50001,50033))


def backbone_component(w,source):
    seen=set()
    queue=[source]
    while queue:
        current=queue.pop()
        if current in seen:continue
        seen.add(current)
        for a,b in w.B:
            if current==a and b not in seen:queue.append(b)
            if current==b and a not in seen:queue.append(a)
    return seen


def strict_physical_daughter(w):
    ids=[w.grid.get((x,2)) for x in COLS]
    if None in ids or len(set(ids))!=4:return None
    if set(ids).intersection(w.initial_template_material_ids):return None
    # Stronger than first observer: entire native B component must be EXACTLY
    # these 4 physical monomers, not a four-site fragment of a larger chain.
    if backbone_component(w,ids[0])!=set(ids):return None
    if any(w._key(a,b) not in w.B for a,b in zip(ids,ids[1:])):return None
    if any(w._key(a,b) in w.H for a in ids for b in w.initial_template_material_ids):return None
    return tuple(ids),"".join(str(w.particles[i].species) for i in ids)


def replay(seed,mode,sequence,stored):
    w=WorldM8(
        seed=seed,mode=mode,template_sequence=sequence,
        initial_free_energy=0 if mode=="unpowered" else 500,
        bath_each_species=40
    )
    source_hash=w.full_hash()
    assert source_hash==stored["source_initial_full_hash"],(seed,mode,sequence,"initial")
    first=None
    strong20=[]
    last=None
    consecut=0
    for t in range(1,TICKS+1):
        previous=w.grid.get((5,2))
        w.step()
        current=w.grid.get((5,2))
        if previous is None and current is not None:
            assert first is None
            e=[x for x in w.events if x["kind"]=="adsorb" and x["new_material_id"]==current]
            assert len(e)==1 and e[0]["tick"]==t
            first={"tick":t,"species":w.particles[current].species,
                   "new_material_id":current,"source_material_id":e[0]["source_material_id"],
                   "same_keyed_species_lottery":e[0]["same_keyed_species_lottery"]}
            # For actual local capture both parent and new monomer must appear
            # as an H contact, not be created by the outcome observer.
            assert e[0]["source_material_id"] is not None
            source=e[0]["source_material_id"]
            assert w._key(current,source) in w.H
            assert abs(w.particles[source].y-w.particles[current].y)==1
        d=strict_physical_daughter(w)
        if d is None:
            last=None
            consecut=0
        else:
            consecut=consecut+1 if last==d else 1
            last=d
            if consecut==20:
                strong20.append({"first_persistent_tick":t,
                                 "material_ids":list(d[0]),"sequence":d[1]})
        assert w.initial_matter==len(w.particles)+sum(w.bath.values())
        assert w.initial_energy==w.free_energy+w.dissipated+sum(w.B.values())+sum(w.H.values())
    assert first==stored["fixed_first_captured_monomer_at_x5_y2"],(seed,mode,sequence,"first capture")
    assert stored["all_real_local_capture_events"]==[e for e in w.events if e["kind"]=="adsorb"]
    assert stored["all_real_backbone_form_events"]==[e for e in w.events if e["kind"]=="B_form"]
    assert stored["native_local_chemistry_event_counts"]==dict(Counter(e["kind"] for e in w.events))
    assert stored["total_matter_initial"]==w.initial_matter
    assert stored["total_energy_initial"]==w.initial_energy
    assert stored["final"]==w.physical_metrics()
    original=stored["physically_distinct_detached_products_persisting_at_least_20_ticks"]
    assert strong20==original,(seed,mode,sequence,"independently stricter B-component detached product")
    copy=any(x["sequence"]==sequence for x in strong20)
    assert copy==stored["persists_parent_sequence_in_product"]
    w.check()
    return {
        "first_site":first,
        "strict_B_connected_exact_4_material_products":strong20,
        "exact_source_sequence_persistent_at_least_20":copy,
        "real_local_capture_count":sum(e["kind"]=="adsorb" for e in w.events),
        "real_native_backbone_B_form_count":sum(e["kind"]=="B_form" for e in w.events),
        "all_material_and_energy_ledgers_and_full_physics_hash_match":True
    }


def main():
    raw=json.loads(RAW.read_text(encoding="utf-8"))
    assert raw["schema"]=="alife-m8-0-local-polymer-32-paired-synthetic-only-preflight-v1"
    assert raw["no_unbiased_spontaneous_worlds_run"]
    rows=raw["worlds"]
    assert [r["seed"] for r in rows]==list(SEEDS)
    counts=Counter()
    for i,record in enumerate(rows):
        seed=record["seed"]
        per={}
        for mode in ("templated","shuffled_identity"):
            for sequence in ("0101","0111"):
                key=mode+":"+sequence
                per[key]=replay(seed,mode,sequence,record["arms"][key])
        for mode in ("no_template","unpowered"):
            key=mode+":0101"
            per[key]=replay(seed,mode,"0101",record["arms"][key])
        a=per["templated:0101"]["first_site"]
        b=per["templated:0111"]["first_site"]
        c=per["shuffled_identity:0101"]["first_site"]
        d=per["shuffled_identity:0111"]["first_site"]
        counts["real_edits_change_material_species"]+=bool(a and b and a["species"]!=b["species"])
        counts["shuffled_edits_change_material_species"]+=bool(c and d and c["species"]!=d["species"])
        counts["physical_templated_0101_exact_persistent_child"]+=per["templated:0101"]["exact_source_sequence_persistent_at_least_20"]
        counts["physical_scrambled_0101_exact_persistent_child"]+=per["shuffled_identity:0101"]["exact_source_sequence_persistent_at_least_20"]
        counts["no_template_physically_unfed_capture_zero"]+=per["no_template:0101"]["real_local_capture_count"]==0
        counts["unpowered_capture_zero"]+=per["unpowered:0101"]["real_local_capture_count"]==0
        counts["active_capture_total"]+=per["templated:0101"]["real_local_capture_count"]
        counts["shuffled_capture_total"]+=per["shuffled_identity:0101"]["real_local_capture_count"]
        counts["active_native_B_form_total"]+=per["templated:0101"]["real_native_backbone_B_form_count"]
        counts["shuffled_native_B_form_total"]+=per["shuffled_identity:0101"]["real_native_backbone_B_form_count"]
        if (i+1)%8==0:
            print(f"M80_INDEPENDENT_PROGRESS {i+1}/32 exact six-arm replays",flush=True)
    expected=raw["summary"]
    assert counts["real_edits_change_material_species"]==expected["same_microscopic_draw_parent_point_edit_changes_first_real_capture_species_in_templated_mode"]==32
    assert counts["shuffled_edits_change_material_species"]==expected["same_microscopic_draw_parent_point_edit_changes_first_real_capture_species_in_shuffled_mode"]==0
    assert counts["physical_templated_0101_exact_persistent_child"]==expected["detached_4_monomer_exact_0101_daughter_B_chain_persisted_at_least_20_ticks_templated"]==18
    assert counts["physical_scrambled_0101_exact_persistent_child"]==expected["same_rate_scrambled_template_control_exact_0101_daughter_B_chain"]==0
    assert counts["no_template_physically_unfed_capture_zero"]==32
    assert counts["unpowered_capture_zero"]==32
    # New physics starts without any monomer if template=None and p_background=0.
    # This is an explicit M8.1 spontaneous-origin BLOCKER, not an unknown.
    empty=WorldM8(seed=50001,mode="templated",template_sequence=None)
    for _ in range(120):empty.step()
    assert not empty.particles and not empty.B and not empty.H
    result={
        "schema":"alife-m8-0-complete-independent-observer-replay-v1",
        "same_original_32_fixed_synthetic_seed_pairs_not_new_samples":True,
        "all_192_laboratory_physics_cases_replayed":True,
        "no_preflight_source_observer_or_product_classifier_called":True,
        "strict_exact_B_component_four_atom_product_detector_matched":True,
        "all_actual_advertised_independent_material_capture_events_and_B_events_matched":True,
        "all_mass_energy_invariants_at_all_120_steps_and_final_physics_hash_matched":True,
        "all_four_original_prereg_gates_verified_and_unchanged":True,
        "counts":dict(counts),
        "important_m8_1_spontaneous_origin_blocker":
            "Current M8.0 background adsorption probability is exactly 0. With NO planted polymer and an empty initially occupied lattice there is no mechanism to nucleate any particle or B bond. M8.1 must openly version a new background adsorption/nucleation law and preregister it BEFORE unbiased seed-world search.",
        "limitations":"This validates outcome observer and reproduces physical traces using THE SAME M8 implementation. It is not independent reimplementation of chemical laws or a new sample. Parent-edit 32/32 is expected from a binary match/mismatch selection rule under exactly paired random draws."
    }
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("M80_INDEPENDENT_FINAL="+json.dumps(result,sort_keys=True),flush=True)


if __name__=="__main__":main()
