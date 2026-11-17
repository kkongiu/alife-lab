"""M7.10 native recruited-first-bond functional intervention and heldout gates."""
from support import make_energy_config,world_with
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_10_recruited_link_function import (
    ARMS, CHECKPOINTS, protocol, provenance, excise_and_refund,
    predicted_bond_energy_route, route,follow,summarize,study
)
from tools import m7_5_mature_feedback as original


def prepared():
    cfg=make_energy_config(
        width=8,height=8,seed=710,
        species=[{"name":"S0","count":4,"move_probability":0.0,
                  "energy":6,"max_bonds":3}],
        chemistry={
            "enabled":True,"bond_cost":2,
            "formation_probability":0.0,"break_probability":0.0,
            "allowed_pairs":[["S0","S0"]],"catalysis":[]
        }
    )
    world=world_with(cfg,positions=[(0,0),(1,0),(2,0),(4,4)],
                     species=[0]*4,energy=[16,2,0,6],
                     bonds=[(0,1,4),(1,2,4)])
    world.check()
    return world


def source():
    return {
        "ids":(0,1),"edges":((0,1),),
        "size":2,"cyclomatic_number":0
    }


def first():
    return {"native_first_link":[1,2],
            "native_first_recruited_outsider_id":2}


def test_frozen_protocol_stable_m75_and_all_640_heldout_seeds():
    p=protocol()
    assert p["status"]=="frozen_before_experimental_code_or_results"
    assert p["sampling"]["seed_first"]==28001
    assert p["sampling"]["seed_last"]==28640
    assert p["sampling"]["seed_count"]==640
    assert [s for d in p["sampling"]["shards"] for s in range(d["start"],d["end"]+1)]==list(range(28001,28641))
    assert p["integrity"]["draft_stacked_PR_no_merge"]
    assert p["integrity"]["full_test_suite_before_sampling"]
    assert p["frozen_decisions"]["no_posthoc_threshold_changes"]
    assert p["forks"]["timepoints"]==list(CHECKPOINTS)
    assert len(provenance()["m710_protocol_sha256"])==64


def test_selected_link_excised_with_exact_native_energy_refund_no_rng():
    w=prepared()
    oldenergy=w.energy()
    oldbond=w.store.bonds[(1,2)]
    oldrng=w.rng.fingerprint(),w.rng.draws
    olddiss=w.dissipated
    met=excise_and_refund(w,(1,2))
    assert oldbond==4
    assert met["excised_native_bond_energy"]==oldbond
    assert w.store.energy[1]==4
    assert w.store.energy[2]==2
    assert (1,2) not in w.store.bonds
    assert w.energy()==oldenergy
    assert w.dissipated==olddiss
    assert (w.rng.fingerprint(),w.rng.draws)==oldrng
    assert (0,1) in w.store.bonds
    w.check()


def test_suppressed_single_link_transport_matches_original_m73_elsewhere():
    w=prepared()
    ref=clone_world(w)
    intact=clone_world(w)
    suppressed=clone_world(w)
    before=w.rng.fingerprint(),w.rng.draws
    exp=predicted_bond_energy_route(w,(0,1),(1,2),False)
    assert exp["transfers_on_selected_original_new_link"]>=1
    official=energy_transfer(ref,"bond_only")
    predicted=route(intact,"native_intact",(0,1),(1,2))
    assert predicted["transfers_total"]==official[0]
    assert predicted["transfers_on_selected_original_new_link"]==exp["transfers_on_selected_original_new_link"]
    assert intact.store.energy==ref.store.energy
    assert intact.state_hash_full()==ref.state_hash_full()
    no=route(suppressed,"bond_intact_conduction_ablated",(0,1),(1,2))
    assert no["transfers_on_selected_original_new_link"]==0
    assert (1,2) in suppressed.store.bonds
    assert suppressed.energy()==intact.energy()==w.energy()
    assert (suppressed.rng.fingerprint(),suppressed.rng.draws)==before
    suppressed.check()


def test_full_three_arm_native_followup_uses_unchanged_original_dynamics_and_no_new_recruit():
    w=prepared()
    before=w.state_hash_full(),w.rng.fingerprint(),w.rng.draws
    result=follow(w,source(),first(),firststep_sham_replay=True)
    assert set(result["outcomes"])==set(ARMS)
    assert result["intervention_excised_refund_metadata"]["world_energy_and_rng_unchanged"]
    assert (w.state_hash_full(),w.rng.fingerprint(),w.rng.draws)==before
    for arm,h in result["outcomes"].items():
        assert len(h["checkpoints"])==5
        assert h["first_original_root_edge_break_relative_tick"] is None
        assert h["any_second_distinct_outsider_form_before_original_break"] is False
        assert h["all_original_root_bonds_never_broken_120"]
        assert h["energy_ledger_verified"]
    assert result["outcomes"]["native_intact"]["first_native_step_full_hash_before_transport"]==result["outcomes"]["bond_intact_conduction_ablated"]["first_native_step_full_hash_before_transport"]
    assert result["outcomes"]["bond_intact_conduction_ablated"]["selected_pair_transfers"]==0


def mock(seed,ablation=None,excised=None):
    if ablation is None:
        return {"seed":seed,"qualifies":False,"selection":{"reason":"null"}}
    p=bool(ablation)
    outcome={}
    for arm in ARMS:
        v=p if arm=="native_intact" else (
            bool(excised) if arm=="recruited_edge_excised_refunded" else False
        )
        outcome[arm]={
            "any_second_distinct_outsider_form_before_original_break":v,
            "any_second_distinct_outsider_form_and_coherent_root_before_original_break":v,
            "all_original_root_bonds_never_broken_120":True,
            "first_recruited_outsider_in_final_root_component":True,
            "any_other_new_outsider_in_final_root_component":v,
            "selected_pair_transfers":0,
            "total_source_boundary_passive_transfer_in":0,
            "total_source_boundary_passive_transfer_out":0,
            "final_root_coherent_size":7
        }
    return {
        "seed":seed,"qualifies":True,
        "source":{"cyclomatic_number":0},
        "first_native_new_recruited_link":{"first_link_native_form_relative_tick":12},
        "outcomes":outcome
    }


def test_frozen_seed_discordant_gate_and_null_retention():
    p=protocol()
    rows=[mock(s) for s in range(28001,28641)]
    assert summarize(rows,p)["preregistered_decisions"]["native_new_link_conduction_enables_second_recruitment"]=="not_met_insufficient_selected_source_worlds"
    for j in range(50):
        seed=28001+j
        if j<20:rows[j]=mock(seed,True,False)
        elif j<30:rows[j]=mock(seed,False,True)
        else:rows[j]=mock(seed,False,False)
    # For primary, mock uses suppressed=False, thus 20 discordant only
    s=summarize(rows,p)
    assert s["eligible_first_prebreak_recruited_native_bond"]==50
    assert s["preregistered_decisions"]["native_new_link_conduction_enables_second_recruitment"]=="not_met_insufficient_discordant_source_worlds"
    assert s["paired_comparisons"]["secondary_kept_link_vs_energy_refunded_excised_link"]["discordant"]==30
    assert s["preregistered_decisions"]["native_new_link_itself_enables_second_recruitment"]=="passed"
    # Change enough secondary favorable worlds to reversals.
    for j in range(9):rows[j]=mock(28001+j,False,True)
    failed=summarize(rows,p)
    assert failed["preregistered_decisions"]["native_new_link_itself_enables_second_recruitment"]=="not_met_favorable_fraction"


def test_one_new_real_seed_never_assumes_outcome_before_selection():
    item=study(28001,original.protocol(),replay=True)
    assert item["seed"]==28001
    if item["qualifies"]:
        assert set(item["outcomes"])==set(ARMS)
        assert item["source"]["size"]>=5
        assert len(item["first_native_new_recruited_link"]["native_first_link"])==2
        assert item["first_native_new_recruited_link"]["prior_original_material_break_events"]==0
    else:
        assert item["selection"]["reason"] in (
            "no_m75_native_aged_source",
            "original_root_bond_broke_before_first_eligible_recruitment",
            "no_incident_native_recruitment_before_original_break_or_time_limit"
        )
