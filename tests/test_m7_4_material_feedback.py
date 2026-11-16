"""M7.4 same-source natural material feedback and falsifiable source-specific gates."""
from support import make_energy_config,world_with
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer as m73_transfer
from tools.m7_4_material_feedback import (
    ARMS, HORIZON, EventTape, coherent_root_size, follow, native_pairs,
    protocol, route_source, source_candidates, summarize
)


def fixture():
    cfg=make_energy_config(
        seed=741,width=8,height=8,
        species=[
            {"name":"S0","count":3,"move_probability":0.0,
             "energy":20,"max_bonds":2}
        ],
        chemistry={
            "enabled":True,"bond_cost":2,"formation_probability":0.0,
            "break_probability":0.0,
            "allowed_pairs":[["S0","S0"]],"catalysis":[]
        }
    )
    w=world_with(cfg,[(1,1),(2,1),(3,1)],[0,0,0],
                 energy=[16,16,20],bonds=[(0,1,4),(1,2,4)])
    assert w.energy()==w.configured_energy()
    w.check()
    return w


def test_preregistration_fixed_before_any_code():
    p=protocol()
    assert p["design"]["source_seeds"]["start"]==22001
    assert p["design"]["source_seeds"]["end_inclusive"]==22160
    assert p["design"]["source_seeds"]["count"]==160
    assert p["design"]["followup_ticks"]==120
    assert p["integrity"]["no_src_changes"] and p["integrity"]["no_master_changes"]
    assert p["preregistered_decisions"]["no_posthoc_threshold_change"]
    keys=[s for d in p["design"]["shards"] for s in range(d["start"],d["end"]+1)]
    assert keys==list(range(22001,22161))


def test_frozen_native_component_selection_and_root_status():
    w=fixture()
    (chosen,)=source_candidates(w)
    assert chosen["ids"]==(0,1,2)
    assert chosen["edges"]==((0,1),(1,2))
    assert chosen["size"]==3
    assert set(chosen["edges"])==native_pairs(w)
    assert coherent_root_size(w,chosen["ids"])==3


def test_route_follows_exact_existing_M73_energy_chemistry():
    w=fixture()
    c=source_candidates(w)[0]
    for arm in ARMS:
        a=clone_world(w)
        b=clone_world(w)
        start_energy=a.energy()
        start_rng=(a.rng.fingerprint(),a.rng.draws)
        data=route_source(a,arm,set(c["ids"]),set(c["edges"]))
        official=m73_transfer(b,arm)
        assert a.store.energy==b.store.energy
        assert a.state_hash_full()==b.state_hash_full()
        assert (a.rng.fingerprint(),a.rng.draws)==start_rng
        assert a.energy()==start_energy
        assert data[0]==official[0]
        assert data[4]==official[1]
        assert data[5]>=0 and data[5]<=data[1]
    assert route_source(clone_world(w),"no_transfer",set(c["ids"]),set(c["edges"]))==(0,0,0,0,0,0)


def test_empty_event_tape_does_not_draw_rng():
    w=fixture()
    tape=EventTape()
    w.event_sink=tape
    before=w.rng.fingerprint()
    tape.pop(7)
    assert w.rng.fingerprint()==before
    assert tape.pending==[]


def test_three_matched_forks_preserve_source_and_original_bond_break_invariant():
    w=fixture()
    chosen=source_candidates(w)[0]
    hash0=w.state_hash_full()
    rng0=w.rng.fingerprint()
    outcomes=follow(w,chosen,HORIZON,replay=True)
    assert set(outcomes)==set(ARMS)
    assert w.state_hash_full()==hash0
    assert w.rng.fingerprint()==rng0
    for arm in ARMS:
        h=outcomes[arm]
        assert h["first_step_original_break_pairs"]==[]
        assert h["original_bonds_unbroken_120"] is True
        assert h["coherent_growth_at_120"] is False
        assert h["incident_external_bond_events"]==0
        assert h["energy_ledger_pass"] is True
        assert h["total_world_new_bonds"]==0
    assert outcomes["bond_only"]["root_original_edge_transfer_events"]>0
    assert outcomes["no_transfer"]["root_original_edge_transfer_events"]==0


def fake(seed,selected,yes_growth,yes_survival):
    if not selected:
        return {"seed":seed,"selected":False,"reason":"no_eligible_natural_source"}
    outcomes={}
    for arm in ARMS:
        gr=yes_growth if arm=="bond_only" else False
        sv=yes_survival if arm=="bond_only" else False
        outcomes[arm]={
            "coherent_growth_at_120":gr,
            "original_bonds_unbroken_120":sv,
            "ever_coherent_growth":gr,
            "incident_external_bond_events":1 if gr else 0,
            "root_internal_transfer_events":1 if arm=="bond_only" else 0,
            "root_original_edge_transfer_events":1 if arm=="bond_only" else 0,
            "root_boundary_energy_in_events":0,
            "root_growth_ticks":1 if gr else 0,
            "total_world_new_bonds":1 if gr else 0
        }
    return {"seed":seed,"selected":True,"outcomes":outcomes}


def test_preregistered_gates_require_discouraging_ties_and_minimum_samples():
    p=protocol()
    rows=[fake(seed,False,False,False) for seed in range(22001,22161)]
    z=summarize(rows,p)
    assert z["selected_native_source_worlds"]==0
    assert z["preregistered_decisions"]["coherent_source_growth_benefit"]=="not_met_or_underpowered"
    for k in range(60):
        rows[k]=fake(22001+k,True,k<25,k<20)
    good=summarize(rows,p)
    assert good["selected_native_source_worlds"]==60
    assert good["paired_causal_contrasts"]["growth_at_120"]["discordant"]==25
    assert good["preregistered_decisions"]["coherent_source_growth_benefit"]=="passed"
    assert good["preregistered_decisions"]["original_source_bond_survival_benefit"]=="passed"
    rows[0]["outcomes"]["bond_only"]["coherent_growth_at_120"]=False
    rows[0]["outcomes"]["no_transfer"]["coherent_growth_at_120"]=True
    # Unequal pair counts and less than 2/3 favorable could fail by editing rows.
    for k in range(3,19):
        rows[k]["outcomes"]["bond_only"]["coherent_growth_at_120"]=False
        rows[k]["outcomes"]["no_transfer"]["coherent_growth_at_120"]=True
    worse=summarize(rows,p)
    assert worse["preregistered_decisions"]["coherent_source_growth_benefit"]=="not_met_or_underpowered"
