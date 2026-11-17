"""M7.8 frozen native microstate causal pair-reaction and prereg gate tests."""
from support import make_energy_config, world_with
from alife.chemistry import form_bonds
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_7_cohort_mechanism import interface_potential
from tools.m7_8_frozen_reactions import (
    ARMS,SALTS,protocol,provenance,pair_draw,apply_intervention,
    formation_only_pair_keyed,nonbonded_budget_transfer,
    run_one,summarize,FIRST,LAST
)
from tools import m7_5_mature_feedback as original


def fixture():
    cfg=make_energy_config(
        width=8,height=8,seed=700,
        species=[{"name":"S0","count":3,"move_probability":0.0,
                  "energy":6,"max_bonds":2}],
        chemistry={"enabled":True,"bond_cost":2,"formation_probability":1.0,
                   "break_probability":0.0,"allowed_pairs":[["S0","S0"]],"catalysis":[]}
    )
    w=world_with(cfg,positions=[(0,0),(1,0),(2,0)],
                 species=[0,0,0],energy=[10,1,3],bonds=[(0,1,4)])
    assert w.configured_energy()==w.energy()==18
    w.check()
    return w


def test_prereg_frozen_completeness_and_no_native_changes():
    p=protocol()
    assert p["status"]=="preregistered_before_runner_and_outcomes"
    assert (FIRST,LAST)==(26001,26640)
    assert len(p["sample"]["shards"])==16
    assert len(SALTS)==32
    assert p["integrity"]["master_untouched"]
    assert p["integrity"]["original_world_native_core_untouched"]
    assert p["integrity"]["no_handplanted_bonds_or_particles"]
    assert p["preregistered_decisions"]["no_posthoc_threshold_or_arms_changes"]
    assert p["preregistered_decisions"]["no_life_selfmaintenance_replication_claim"]
    assert [seed for d in p["sample"]["shards"] for seed in range(d["start"],d["end"]+1)]==list(range(FIRST,LAST+1))
    assert set(provenance())=={"m78_prereg_sha256","m75_untouched_source_sha256"}


def test_pair_draw_permutation_fixed_and_no_lottery_order_coupling():
    a=pair_draw(26001,0,1,2)
    assert a==pair_draw(26001,0,2,1)
    assert 0<=a<1<<64
    assert a!=pair_draw(26001,1,1,2)
    assert a!=pair_draw(26002,0,1,2)
    assert a!=pair_draw(26001,0,1,3)


def test_native_bond_transfer_causes_new_energetic_external_pair_at_frozen_geometry():
    w=fixture()
    before=w.state_hash_full(),w.rng.fingerprint(),w.rng.draws
    initial=interface_potential(w,(0,1))
    assert initial["energy_qualified_boundary_contacts"]==0
    assert initial["species_valence_qualified_boundary_contacts"]==1
    unchanged,_=apply_intervention(w,"sham",1)
    positive,flow=apply_intervention(w,"bond_only",1)
    eligible=interface_potential(positive,(0,1))
    assert flow["transfer_events"]==1
    assert positive.store.energy==[9,2,3]
    assert eligible["energy_qualified_boundary_contacts"]==1
    assert eligible["species_valence_qualified_boundary_contacts"]==1
    assert eligible["unbonded_geometrical_boundary_contacts"]==1
    assert sum(positive.store.energy[i] for i in (0,1))==sum(unchanged.store.energy[i] for i in (0,1))
    assert (w.state_hash_full(),w.rng.fingerprint(),w.rng.draws)==before


def test_isolated_native_chemical_formation_uses_same_costs_and_chemistry():
    src=fixture()
    sham,_=apply_intervention(src,"sham",1)
    bond,_=apply_intervention(src,"bond_only",1)
    before=sham.rng.fingerprint(),sham.rng.draws
    assert formation_only_pair_keyed(sham,(0,1),26001,0)["formed_original_to_external"]==0
    candidate=formation_only_pair_keyed(bond,(0,1),26001,0)
    assert candidate["formed_original_to_external"]==1
    assert candidate["original_to_external_bonds"]==[[1,2]]
    assert (bond.rng.fingerprint(),bond.rng.draws)==before
    assert bond.store.energy==[9,0,1]
    assert bond.store.bonds[(1,2)]==4
    assert bond.energy()==src.energy()==18
    # SAME original native chemistry with a one-pair scripted acceptance draw,
    # used only in the synthetic unit test, never in the M7.8 production runs.
    reference,_=apply_intervention(src,"bond_only",1)
    class Oracle:
        def raw(self):return 0
    reference.rng=Oracle()
    native=form_bonds(reference)
    assert len(native)==1
    assert reference.store.energy==bond.store.energy
    assert reference.store.bonds==bond.store.bonds
    assert reference.bonds_formed_total==bond.bonds_formed_total
    assert reference.dissipated==bond.dissipated


def test_all_contacts_and_nonbonded_budget_controls_are_rng_free_and_honest():
    w=fixture()
    original=w.state_hash_full(),w.rng.fingerprint(),w.rng.draws
    budget=energy_transfer(clone_world(w),"bond_only")[0]
    matched,d=apply_intervention(w,"unbonded_budget_matched",budget)
    assert d["requested_budget"]==1
    assert d["transfer_events"]==0
    assert d["budget_shortfall"]==1
    assert matched.store.energy==w.store.energy
    full,d2=apply_intervention(w,"all_contacts",budget)
    assert d2["bond_route"]==1
    assert d2["transfer_events"]>=1
    assert full.energy()==w.energy()
    assert (w.state_hash_full(),w.rng.fingerprint(),w.rng.draws)==original
    assert nonbonded_budget_transfer(clone_world(w),0)["accepted_unbonded_transfers"]==0


def fake(seed,activation,formation):
    static=activation
    arms={}
    for arm in ARMS:
        treated=arm=="bond_only"
        change=static if treated else 0
        counts=32+formation if treated else 32
        arms[arm]={
            "static_interface":{"energy_qualified_boundary_contacts":20+change},
            "transfer":{"transfer_events":0,"budget_shortfall":0},
            "boundary_eligibility_change_vs_sham":change,
            "total_external_formed_across_32_lotteries":counts
        }
    return {
        "seed":seed,"selected":True,
        "source":{"size":7,"cyclomatic_number":0},
        "arms":arms
    }


def test_seed_level_preregistered_gates_with_paired_32_lottery_means():
    p=protocol()
    rows=[]
    for i,seed in enumerate(range(FIRST,LAST+1)):
        activation=1 if i<16 else -1 if i<20 else 0
        formation=1 if i<10 else -1 if i<15 else 0
        rows.append(fake(seed,activation,formation))
    summary=summarize(rows,p)
    assert summary["preregistered_decisions"]["direct_energetic_activation"]=="passed"
    assert summary["preregistered_decisions"]["actual_coupled_pair_formation_benefit"]=="passed"
    one=summary["paired_mechanism"]["native_new_external_energetic_pair_activation"]
    assert (one["favor_bond_only"],one["favor_sham"],one["discordant"])==(16,4,20)
    two=summary["paired_mechanism"]["coupled_actual_external_formation_count_32_per_seed"]
    assert (two["favor_bond_only"],two["favor_sham"],two["discordant"])==(10,5,15)
    rows[0]["arms"]["bond_only"]["boundary_eligibility_change_vs_sham"]=-1
    rows[0]["arms"]["bond_only"]["total_external_formed_across_32_lotteries"]=31
    s=summarize(rows,p)
    assert s["preregistered_decisions"]["direct_energetic_activation"]=="not_met_or_underpowered"
    assert s["preregistered_decisions"]["actual_coupled_pair_formation_benefit"]=="not_met_or_underpowered"


def test_one_real_heldout_natural_source_full_32_lotteries_and_direct_replay():
    row=run_one(26001,original.protocol(),replay=True)
    assert row["seed"]==26001
    assert row["selected"]
    assert 5<=row["source"]["size"]<=16
    assert row["source"]["original_edges_aged_at_least20"]>=2
    assert set(row["arms"])==set(ARMS)
    assert row["arms"]["bond_only"]["transfer"]["unbonded_route"]==0
    for name,arm in row["arms"].items():
        assert len(arm["lotteries"])==32
        assert [x["salt"] for x in arm["lotteries"]]==list(SALTS)
        assert sum(x["formed_original_to_external"] for x in arm["lotteries"])==arm["total_external_formed_across_32_lotteries"]
        assert arm["energy_conservation_verified"]
