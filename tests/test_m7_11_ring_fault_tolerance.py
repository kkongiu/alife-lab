"""M7.11 physical fault-tolerance, native exact ring age and prereg gates."""
from support import make_energy_config,world_with
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_4_material_feedback import native_pairs
from tools.m7_11_ring_fault_tolerance import (
    protocol,provenance,rings_now,excise_refund,
    transport_with_optional_suppression,connected_original_ids,
    induced_original_connected,follow_ring,summarize,study,ARMS,FIRST,LAST
)


def ring_fixture():
    cfg=make_energy_config(
        width=8,height=8,seed=711,
        species=[{"name":"S0","count":4,"move_probability":0,"energy":6,"max_bonds":2}],
        chemistry={"enabled":True,"bond_cost":2,
                   "formation_probability":0.0,"break_probability":0.0,
                   "allowed_pairs":[["S0","S0"]],"catalysis":[]}
    )
    w=world_with(cfg,positions=[(0,0),(1,0),(1,1),(0,1)],
                 species=[0,0,0,0],energy=[2,2,2,2],
                 bonds=[(0,1,4),(1,2,4),(2,3,4),(0,3,4)])
    assert w.energy()==w.configured_energy()==24
    assert len(w.store.bonds)==4
    w.check()
    return w


def ring_data(w):
    c=rings_now(w)
    assert len(c)==1
    assert c[0]["size"]==4
    assert c[0]["ids"]==(0,1,2,3)
    assert c[0]["edges"]==((0,1),(0,3),(1,2),(2,3))
    return c[0]


def test_frozen_preregistration_population_and_old_code_hashes():
    p=protocol()
    assert p["status"]=="frozen_before_runner_tests_and_results"
    assert (FIRST,LAST)==(29001,29640)
    assert p["sample"]["minimum_continuous_ring_age"]==20
    assert p["sample"]["last_scan_tick"]==600
    assert len(p["sample"]["shards"])==16
    assert [i for d in p["sample"]["shards"] for i in range(d["start"],d["end"]+1)]==list(range(FIRST,LAST+1))
    assert p["integrity"]["all_nulls_retained"]
    assert p["integrity"]["draft_PR_no_merge"]
    assert set(provenance())=={
        "m711_preregistered_protocol_sha256",
        "unchanged_original_M73_native_conduction_sha256",
        "unchanged_original_M64_cycle_observer_sha256"
    }


def test_original_native_M64_exact_cycle_recognition_and_connectivity():
    w=ring_fixture()
    r=ring_data(w)
    assert r["exact"].startswith("C:")
    assert connected_original_ids(w,r["ids"])
    assert induced_original_connected(w,r["ids"])
    assert not any(w.store.degree[i]!=2 for i in range(4))


def test_native_bond_refund_exact_conservation_rng_graph_and_no_repair():
    w=ring_fixture()
    ring=ring_data(w)
    ref=w.state_hash_full()
    before=w.energy(),w.dissipated,w.rng.fingerprint(),w.rng.draws
    t=excise_refund(w,(0,1))
    assert t["native_bond_energy_fully_refunded"]==4
    assert t["refunded_lower_material_id"]==2
    assert t["refunded_higher_material_id"]==2
    assert (w.energy(),w.dissipated,w.rng.fingerprint(),w.rng.draws)==before
    assert (0,1) not in native_pairs(w)
    assert set(native_pairs(w))==set(ring["edges"])-{(0,1)}
    assert w.store.energy==[4,4,2,2]
    assert connected_original_ids(w,ring["ids"])
    assert induced_original_connected(w,ring["ids"])
    assert w.state_hash_full()!=ref
    w.check()


def test_original_M73_transfer_and_ablation_match_without_rng():
    w=ring_fixture()
    ring=ring_data(w)
    a=clone_world(w)
    b=clone_world(w)
    original=a.rng.fingerprint(),a.rng.draws
    first=transport_with_optional_suppression(a,"intact_normal",set(ring["edges"]),(0,1))
    official=energy_transfer(clone_world(w),"bond_only")
    assert first["all_native_bond_energy_transfers"]==official[0]
    assert first["native_original_ring_edges_conduction"]==0
    other=transport_with_optional_suppression(b,"intact_ring_conduction_suppressed",set(ring["edges"]),(0,1))
    assert other["native_original_ring_edges_conduction"]==0
    assert a.state_hash_full()==b.state_hash_full()
    assert (a.rng.fingerprint(),a.rng.draws)==original
    opened=clone_world(w)
    excise_refund(opened,(0,1))
    yes=clone_world(opened)
    no=clone_world(opened)
    original_route=transport_with_optional_suppression(yes,"opened_normal",set(ring["edges"]),(0,1))
    skip=transport_with_optional_suppression(no,"opened_surviving_ring_conduction_suppressed",set(ring["edges"]),(0,1))
    assert original_route["native_original_ring_edges_conduction"]>0
    assert skip["native_original_ring_edges_conduction"]==0
    assert yes.store.energy!=no.store.energy
    assert yes.energy()==no.energy()==w.energy()


def test_four_arm_normal_native_dynamics_no_spontaneous_break_or_reclosure():
    w=ring_fixture()
    ring=ring_data(w)
    ring["continuous_snapshot_age"]=20
    before=(w.state_hash_full(),w.rng.fingerprint(),w.rng.draws)
    o=follow_ring(w,ring,validation=True)
    assert set(o["outcomes"])==set(ARMS)
    assert o["target_original_cycle_edge"]==[0,1]
    assert o["identical_cut_refund_metadata"]["zero_extra_dissipation_or_rng"]
    assert (w.state_hash_full(),w.rng.fingerprint(),w.rng.draws)==before
    for arm,h in o["outcomes"].items():
        assert len(h["checkpoints"])==5
        assert h["first_original_ring_edge_break_tick"] is None
        assert h["energy_ledger_valid"]
        assert h["original_ring_material_connected_at_120"]
        assert h["original_ring_induced_material_connected_at_120"]
    assert o["outcomes"]["opened_normal"]["exact_cut_edge_reformed_before_any_other_original_break"] is False
    assert o["outcomes"]["opened_surviving_ring_conduction_suppressed"]["exact_cut_edge_reformed_before_any_other_original_break"] is False
    assert o["outcomes"]["intact_normal"]["exact_original_ring_all_edges_present_at_120"]
    assert not o["outcomes"]["opened_normal"]["exact_original_ring_all_edges_present_at_120"]


def mock(seed,a=None,b=None,c=None):
    if a is None:
        return {"seed":seed,"selected":False,"scan":{"reason":"null"}}
    outcomes={}
    for arm in ARMS:
        early=bool(a if arm=="opened_normal" else b)
        if arm=="intact_normal":cohesive=bool(c)
        elif arm=="opened_normal":cohesive=not bool(c)
        else:cohesive=True
        outcomes[arm]={
            "exact_cut_edge_reformed_before_any_other_original_break":early,
            "original_ring_material_connected_at_120":cohesive,
            "original_ring_induced_material_connected_at_120":cohesive,
            "exact_original_ring_all_edges_present_at_120":False,
            "first_anytime_cut_edge_reclosure_tick":None,
            "ring_original_edge_transfer_events":0,
            "all_world_bond_transfer_events":0,
            "original_ring_never_suffered_native_break":True
        }
    return {
        "seed":seed,"selected":True,
        "scan":{"selected_tick":130},
        "native_original_ring":{"size":4,"continuous_snapshot_age":20},
        "outcomes":outcomes
    }


def test_seed_not_event_pair_sign_gates_pass_fail_underpowered_and_all_nulls():
    p=protocol()
    r=[mock(seed) for seed in range(FIRST,LAST+1)]
    x=summarize(r,p)
    assert x["naturally_selected_aged_ring_worlds"]==0
    assert x["preregistered_decisions"]["original_ring_surviving_edges_energy_help_exact_native_reclosure"]=="not_met_insufficient_natural_aged_rings"
    # 50 eligible, of which 30 discordant; 20 favorable (exactly 2/3).
    for k in range(50):
        val=1 if k<20 else -1 if k<30 else 0
        r[k]=mock(FIRST+k,val>0,val<0,val>0)
    s=summarize(r,p)
    a=s["paired_comparisons"]["primary_native_exact_cut_reclosure_before_other_break_vs_suppress_energy"]
    assert (a["favor_treatment"],a["favor_control"],a["discordant"])==(20,10,30)
    assert s["preregistered_decisions"]["original_ring_surviving_edges_energy_help_exact_native_reclosure"]=="passed"
    # Secondary synthetic controls chosen to have 20 wins, 10 losses.
    b=s["paired_comparisons"]["secondary_ring_intact_vs_cut_material_cohesion_t120"]
    assert (b["favor_treatment"],b["favor_control"])==(20,30) or b["favor_treatment"]==20
    for k in range(10):
        r[k]=mock(FIRST+k,False,True,False)
    s2=summarize(r,p)
    assert s2["preregistered_decisions"]["original_ring_surviving_edges_energy_help_exact_native_reclosure"]=="not_met_favorable_fraction"


def test_real_native_seed_never_generates_manufactured_ring():
    outcome=study(FIRST,replay=True)
    assert outcome["seed"]==FIRST
    if outcome["selected"]:
        a=outcome["native_original_ring"]
        assert a["size"] in (4,6,8)
        assert a["continuous_snapshot_age"]>=20
        assert outcome["scan"]["selected_tick"]>=120
        assert len(a["ids"])==len(a["edges"])
        assert len(outcome["outcomes"])==4
    else:
        assert outcome["scan"]["reason"] in (
            "no_native_simple_4_6_8_ring_by_600",
            "native_cycles_observed_but_none_aged_20_by_600"
        )
