"""M7.5 age-verified native network cohort selection and unchanged M7.3 physics."""
from support import make_energy_config, world_with

from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer as m73_transfer
from tools.m7_5_mature_feedback import (
    ARMS,HORIZON, update_edge_ages,candidate_networks,route_traced,follow,
    paired_table,protocol,summarize
)


def native_chain():
    cfg=make_energy_config(
        width=8,height=8,seed=321,
        species=[{
            "name":"S0","count":5,"move_probability":0.0,
            "energy":20,"max_bonds":2
        }],
        chemistry={
            "enabled":True,"bond_cost":2,
            "formation_probability":0.0,"break_probability":0.0,
            "allowed_pairs":[["S0","S0"]],"catalysis":[]
        }
    )
    w=world_with(
        cfg,positions=[(1,1),(2,1),(3,1),(4,1),(5,1)],
        species=[0]*5,energy=[24,12,16,16,16],
        bonds=[(0,1,4),(1,2,4),(2,3,4),(3,4,4)]
    )
    w.check()
    assert w.energy()==100
    return w


def test_protocol_frozen_and_seed_completeness():
    p=protocol()
    assert p["design"]["seeds_first"]==23001
    assert p["design"]["seeds_last"]==23320
    assert p["design"]["seeds"]==320
    assert p["design"]["parent_scan_start_tick"]==120
    assert p["design"]["parent_scan_stop_tick"]==500
    assert p["design"]["followup_steps"]==120
    assert p["gates"]["no_posthoc_threshold_changes"] is True
    assert p["integrity"]["no_src_or_master_changes"] is True
    assert [seed for sh in p["design"]["shards"]
            for seed in range(sh["start"],sh["end"]+1)]==list(range(23001,23321))


def test_native_source_size_and_aged_original_edge_gates():
    w=native_chain()
    present={(0,1),(1,2),(2,3),(3,4)}
    age={edge:19 for edge in present}
    assert candidate_networks(w,age)==[]
    age[(0,1)]=20
    age[(1,2)]=20
    (chosen,)=candidate_networks(w,age)
    assert chosen["ids"]==(0,1,2,3,4)
    assert chosen["size"]==5
    assert chosen["edges_n"]==4
    assert chosen["original_edges_aged_at_least20"]==2
    assert chosen["cyclomatic_number"]==0
    assert chosen["spare_valence_member_count"]==2


def test_actual_break_even_if_same_tick_reform_resets_age():
    old={(0,1):43,(1,2):24,(2,3):25}
    present={(0,1),(1,2),(3,4)}
    reset=update_edge_ages(old,present,{(0,1)})
    assert reset[(0,1)]==1
    assert reset[(1,2)]==25
    assert reset[(3,4)]==1
    assert (2,3) not in reset


def test_tracer_matches_original_m73_transfer_entire_material_state():
    original=native_chain()
    chosen=candidate_networks(original,{(0,1):20,(1,2):20,(2,3):8,(3,4):8})[0]
    for arm in ARMS:
        a=clone_world(original)
        b=clone_world(original)
        before_rng=a.rng.fingerprint(),a.rng.draws
        before_energy=a.energy()
        measured=route_traced(a,arm,chosen["ids"],chosen["edges"])
        actual=m73_transfer(b,arm)
        assert a.store.energy==b.store.energy
        assert a.state_hash_full()==b.state_hash_full()
        assert (a.rng.fingerprint(),a.rng.draws)==before_rng
        assert a.energy()==before_energy
        assert measured[0]==actual[0]
        assert sum(measured[1:4])+measured[6]==measured[0]
        assert measured[1]==measured[4]+measured[5]
        if arm=="bond_only":
            assert measured[2]==0 and measured[3]==0
        a.check()


def test_all_three_arms_have_same_initial_event_invariant_and_sham_replay():
    w=native_chain()
    age={(0,1):20,(1,2):20,(2,3):20,(3,4):20}
    c=candidate_networks(w,age)[0]
    before=w.state_hash_full(),w.rng.fingerprint(),w.rng.draws
    result=follow(w,c,replay=True)
    assert (w.state_hash_full(),w.rng.fingerprint(),w.rng.draws)==before
    assert set(result)==set(ARMS)
    for arm in ARMS:
        row=result[arm]
        assert row["first_step_original_break_pairs"]==[]
        assert row["all_original_bonds_never_broken_120"] is True
        assert row["coherent_growth_at_120"] is False
        assert row["root_incident_new_bond_events"]==0
        assert row["energy_ledger_verified"] is True
        assert len(row["checkpoints"])==5
    assert result["bond_only"]["flux_on_original_bond"]>0
    assert result["no_transfer"]["flux_events_all"]==0


def fake(seed,which=None):
    if which is None:
        return {"seed":seed,"selected":False,"reason":"no_aged_native_network"}
    vals={}
    # which=+1: favorable bond-only; -1: favorable control; 0: tied positive
    for arm in ARMS:
        v=(which>=0) if arm=="bond_only" else (which<=0)
        if arm=="all_contacts":v=False
        vals[arm]={
            "coherent_growth_at_120":v,
            "ever_coherent_growth":v,
            "all_original_bonds_never_broken_120":v,
            "root_incident_new_bond_events":1 if v else 0,
            "root_incident_bond_events_before_any_original_break":1 if v else 0,
            "world_new_bonds_120":1 if v else 0,
            "flux_on_original_bond":1 if arm=="bond_only" else 0,
            "flux_internal_root":1 if arm=="bond_only" else 0,
            "flux_into_root":0,"flux_out_of_root":0,
            "source_net_passive_flow":0
        }
    return {
        "seed":seed,"selected":True,"fork_tick":150,
        "source":{"size":6,"cyclomatic_number":0,"original_edges_aged_at_least20":3},
        "outcomes":vals
    }


def test_confirmation_gate_counts_discordant_seeds_not_arms_or_ties():
    p=protocol()
    rows=[fake(s) for s in range(23001,23321)]
    assert summarize(rows,p)["preregistered_decisions"]["coherent_growth_benefit"]=="not_met_or_underpowered"
    for k in range(50):
        rows[k]=fake(23001+k,1 if k<20 else -1 if k<30 else 0)
    s=summarize(rows,p)
    g=s["paired_comparisons"]["coherent_growth_at_120"]
    assert s["selected_mature_network_worlds"]==50
    assert (g["favorable_bond_only"],g["favorable_no_transfer"],g["discordant"])==(20,10,30)
    assert s["preregistered_decisions"]["coherent_growth_benefit"]=="passed"
    assert s["preregistered_decisions"]["original_bond_survival_benefit"]=="passed"
    rows[0]=fake(23001,-1)
    for k in range(2,12):rows[k]=fake(23001+k,-1)
    s=summarize(rows,p)
    assert s["preregistered_decisions"]["coherent_growth_benefit"]=="not_met_or_underpowered"
