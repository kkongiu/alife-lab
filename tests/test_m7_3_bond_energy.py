"""M7.3: bonded vs incidental contact energy flow, matched native seeds and gates."""
from support import make_energy_config, world_with

from tools.m7_2_energy_distribution import (
    config_for as m72_config,
    diffuse_contact_energy,
    run_world as m72_run_world,
)
from tools.m7_3_bond_energy import (
    ARMS, energy_transfer, config_for, protocol, run_world,
    bare_replay, summary,
)


def fixture():
    cfg=make_energy_config(
        seed=519,width=8,height=8,
        species=[
            {"name":"S0","count":2,"move_probability":0.0,
             "energy":7,"max_bonds":2},
            {"name":"S1","count":1,"move_probability":0.0,
             "energy":5,"max_bonds":0},
        ],
        chemistry={
            "enabled":True,"bond_cost":2,
            "formation_probability":0.0,"break_probability":0.0,
            "allowed_pairs":[["S0","S0"]],"catalysis":[]
        }
    )
    # Total initial configured energy 7+7+5=19; particle 10+0+5,
    # plus four units in the original S0-S0 chemical bond.
    w=world_with(
        cfg,positions=[(0,0),(1,0),(2,0)],
        species=[0,0,1],energy=[10,0,5],bonds=[(0,1,4)]
    )
    w.check()
    assert w.energy()==19
    return w


def test_preregistration_frozen_before_runner():
    p=protocol()
    assert p["status"]=="preregistered_before_code_and_results"
    assert p["design"]["seed_first"]==20001
    assert p["design"]["seed_last"]==20100
    assert p["design"]["worlds"]==300
    assert len(p["design"]["shards"])==4
    assert p["integrity"]["master_unchanged"] is True
    assert p["integrity"]["no_src_changes"] is True
    assert [s for sh in p["design"]["shards"]
            for s in range(sh["start"],sh["end"]+1)]==list(range(20001,20101))
    assert list(ARMS)==p["design"]["arms"]


def test_bond_only_transport_excludes_unbonded_contacts():
    w=fixture()
    before=w.rng.fingerprint()
    draws=w.rng.draws
    energy=w.energy()
    bond_set=dict(w.store.bonds)
    positions=(list(w.store.xs),list(w.store.ys))
    assert energy_transfer(w,"bond_only")==(1,1,0)
    assert w.store.energy==[9,1,5]
    assert w.energy()==energy
    assert w.rng.fingerprint()==before and w.rng.draws==draws
    assert w.store.bonds==bond_set
    assert (w.store.xs,w.store.ys)==positions
    w.check()


def test_all_contacts_includes_unbonded_and_matches_m72():
    w=fixture()
    other=fixture()
    assert energy_transfer(w,"all_contacts")==(2,1,1)
    assert diffuse_contact_energy(other)==(2,2)
    assert w.store.energy==[9,2,4]
    assert other.store.energy==w.store.energy
    w.check()
    other.check()


def test_no_transfer_identity_and_bond_zero_cannot_transfer():
    w=fixture()
    initial=w.state_hash_full()
    assert energy_transfer(w,"no_transfer")==(0,0,0)
    assert w.state_hash_full()==initial
    w.store.remove_bond(0,1)
    # refund bound energy to endpoint to maintain original total after fixture edit
    w.store.energy[0]+=4
    w.check()
    assert energy_transfer(w,"bond_only")==(0,0,0)


def test_all_three_arms_exact_original_source_configuration():
    configs=[config_for(20001,a) for a in ARMS]
    original=m72_config(20001,"dispersed_no_transfer")
    assert all(c.hash()==original.hash() for c in configs)
    assert all(c.canonical_json()==original.canonical_json() for c in configs)
    assert len(original.energy.sources)==16
    assert original.energy.movement_cost==1
    assert original.chemistry.catalysis==()


def test_complete_m72_natural_contact_replay_matches_m73():
    r=run_world(20001,"all_contacts")
    original=m72_run_world(20001,"dispersed_contact_transfer")
    assert r["final"]["full_hash"]==original["final"]["hash"]
    assert r["final"]["rng"]==original["final"]["rng_fingerprint"]
    assert r["final"]["draws"]==original["final"]["rng_draws"]
    assert r["final"]["stored"]==original["final"]["energy_stored"]
    assert r["final"]["unabsorbed"]==original["final"]["unabsorbed"]
    assert r["final"]["transfer_events"]==original["final"]["contact_transfers"]
    assert r["late_501_600"]["moves"]==original["late_501_600"]["moves"]
    assert bare_replay(r)["full_hash_rng_energy_and_routes_match"]


def fake_record(seed,arm,formed,moves,zeros,transfer):
    return {
        "seed":seed,"arm":arm,
        "config_hash":"same",
        "initial":{
            "initial_particles_hash":"same-"+str(seed),
            "rng":"rng-"+str(seed),"draws":264
        },
        "checkpoints":[{
            "energy_in_bonded_particles":200,
            "energy_in_free_particles":100,
            "zero_energy_particles":zeros,
            "free_mobile_energy_eligible":20,
            "gini":0.6
        }],
        "late_501_600":{"moves":moves,"new_bonds":formed},
        "final":{
            "injected":19200,"unabsorbed":9000,
            "transfer_events":transfer,
            "bond_route_events":transfer if arm=="bond_only" else 0,
            "nonbonded_route_events":transfer if arm=="all_contacts" else 0
        },
        "topology_at_600":{"native_simple_ring_components":0}
    }


def test_frozen_gate_thresholds_count_paired_seed_not_ticks():
    p=protocol()
    rows=[]
    for seed in range(20001,20101):
        num=seed-20000
        rows.extend([
            fake_record(seed,"no_transfer",5,5,110,0),
            fake_record(seed,"bond_only",6 if num<=60 else 4,10,100,
                        1 if num<=70 else 0),
            fake_record(seed,"all_contacts",8,15 if num<=75 else 9,
                        90 if num<=70 else 105,3)
        ])
    s=summary(rows,p)
    assert s["preregistered_decisions"]["bond_network_chemical_benefit"]=="passed"
    assert s["preregistered_decisions"]["generic_contacts_exceed_bond_transport"]=="passed"
    c=s["preregistered_decisions"]["component_thresholds"]
    assert c["bond_worlds_with_transport"]==70
    assert c["bond_more_late_formations_seeds"]==60
    assert c["generic_more_late_moves_seeds"]==75
    assert c["generic_fewer_zero_energy_seeds"]==70
    rows[1]["late_501_600"]["new_bonds"]=4
    s2=summary(rows,p)
    assert s2["preregistered_decisions"]["bond_network_chemical_benefit"]=="not_met"
