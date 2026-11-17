"""M7.9: original native energy multiset equality and fixed paired gates."""
from support import make_energy_config,world_with
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools import m7_5_mature_feedback as reference
from tools.m7_9_energy_placement import (
    ARMS,RANKS,SALTS,SEED_FIRST,SEED_LAST,protocol,provenance,
    order_by_hash,root_energy,root_permute,nonroot_energy_signature,
    fixed_graph_signature,one_arm,run_one,summarize
)


def fixture():
    cfg=make_energy_config(
        width=8,height=8,seed=709,
        species=[{"name":"S0","count":3,"move_probability":0.0,"energy":6,"max_bonds":2}],
        chemistry={"enabled":True,"bond_cost":2,"formation_probability":1.0,
                   "break_probability":0.0,"allowed_pairs":[["S0","S0"]],"catalysis":[]}
    )
    w=world_with(cfg,positions=[(0,0),(1,0),(2,0)],
                 species=[0,0,0],energy=[10,1,3],bonds=[(0,1,4)])
    assert w.energy()==w.configured_energy()==18
    w.check()
    return w


def test_preregistered_seed_disjointness_shards_and_exact_four_ranks():
    p=protocol()
    assert p["status"]=="preregistered_before_implementation_and_results"
    assert (SEED_FIRST,SEED_LAST)==(27001,27640)
    assert p["sample"]["count"]==640
    assert len(p["sample"]["shards"])==16
    assert p["interventions"]["permutation_ranks"]==list(RANKS)==[0,1,2,3]
    assert p["integrity"]["original_native_src_master_all_history_unchanged"]
    assert p["integrity"]["preserve_negative_and_tie_seeds"]
    assert p["gates"]["no_posthoc_changes_to_seed_horizon_thresholds_permutation_or_lottery_count"]
    assert [k for d in p["sample"]["shards"] for k in range(d["start"],d["end"]+1)]==list(range(27001,27641))
    assert set(range(27001,27641)).isdisjoint(set(range(26001,26641)))
    assert len(SALTS)==32
    assert len(provenance()["original_m75_selection_sha256"])==64


def test_root_spatial_energy_permutation_has_exact_same_post_conduction_distribution():
    w=fixture()
    w_hash=w.state_hash_full()
    parent_rng=(w.rng.fingerprint(),w.rng.draws)
    post=clone_world(w)
    budget=energy_transfer(post,"bond_only")
    assert budget==(1,1,0)
    root=(0,1)
    assert root_energy(post,root)==(9,2)
    exterior=nonroot_energy_signature(post,root)
    graph=fixed_graph_signature(post)
    for rank in RANKS:
        order=order_by_hash(27001,rank,root)
        assert set(order)==set(root) and len(order)==len(root)
        x,m=root_permute(post,root,27001,rank)
        assert sum(root_energy(x,root))==11
        assert sorted(root_energy(x,root))==[2,9]
        assert m["same_energy_multiset_as_original_bond_only"]
        assert m["outside_original_cohort_energy_unchanged"]
        assert nonroot_energy_signature(x,root)==exterior
        assert fixed_graph_signature(x)==graph
        assert x.energy()==post.energy()
        assert (x.rng.fingerprint(),x.rng.draws)==parent_rng
        assert m["positions_whose_energy_changed"] in (0,2)
        assert post.store.energy==[9,2,3]
    assert w.state_hash_full()==w_hash


def test_one_arm_repeats_exact_32_original_M78_lotteries_with_same_pairs():
    w=fixture()
    parent_hash=w.state_hash_full()
    before=one_arm(w,(0,1),27001,{"sham":True})
    post=clone_world(w)
    energy_transfer(post,"bond_only")
    after=one_arm(post,(0,1),27001,{"bond":True})
    assert len(before["lotteries"])==len(after["lotteries"])==len(SALTS)
    assert before["total_source_external_bonds_across_32_salts"]==0
    assert after["total_source_external_bonds_across_32_salts"]==32
    assert after["native_energetic_boundary_interface"]["energy_qualified_boundary_contacts"]==1
    assert w.state_hash_full()==parent_hash
    assert before["ledger_ok"] and after["ledger_ok"]
    assert after["lotteries"][0]["original_to_external_bonds"]==[[1,2]]


def fake(seed,eligibility_delta=0,formation_delta=0):
    # 4 fixed scrambles, each with same score; deltas are exact 4-fold sign.
    a={}
    for arm in ARMS:
        if arm=="bond_only":
            q=1 if eligibility_delta>0 else 0
            f=1 if formation_delta>0 else 0
        elif arm.startswith("root_scramble"):
            q=1 if eligibility_delta<0 else 0
            f=1 if formation_delta<0 else 0
        else:q=f=0
        a[arm]={
            "native_energetic_boundary_interface":{"energy_qualified_boundary_contacts":q},
            "total_source_external_bonds_across_32_salts":f,
            "intervention_metadata":{"positions_whose_energy_changed":0},
        }
    return {"seed":seed,"selected":True,"native_source":{"cyclomatic_number":0},
            "bond_only_native_transfer_events":0,"arms":a}


def test_both_preregistered_gates_and_both_fail_without_threshold_changes():
    p=protocol()
    rows=[]
    for i,seed in enumerate(range(SEED_FIRST,SEED_LAST+1)):
        v=1 if i<22 else -1 if i<30 else 0
        rows.append(fake(seed,v,v))
    s=summarize(rows,p)
    x=s["comparisons"]["primary_equal_root_energy_multiset_static_pair_eligibility"]
    y=s["comparisons"]["secondary_equal_root_energy_multiset_actual_coupled_external_formations"]
    assert (x["favor_original_bond_placement"],x["favor_randomized_placement"],x["discordant"])==(22,8,30)
    assert (y["favor_original_bond_placement"],y["favor_randomized_placement"],y["discordant"])==(22,8,30)
    assert s["preregistered_decisions"]["primary_original_location_advantage"]=="passed"
    assert s["preregistered_decisions"]["secondary_original_location_reaction_advantage"]=="passed"
    for i in range(8):
        rows[i]=fake(SEED_FIRST+i,-1,-1)
    fail=summarize(rows,p)
    assert fail["preregistered_decisions"]["primary_original_location_advantage"]=="not_met_favorable_fraction"
    assert fail["preregistered_decisions"]["secondary_original_location_reaction_advantage"]=="not_met_favorable_fraction"
    for i in range(8,30):
        rows[i]=fake(SEED_FIRST+i,0,0)
    no_power=summarize(rows,p)
    assert no_power["preregistered_decisions"]["primary_original_location_advantage"]=="not_met_insufficient_discordants"
    assert no_power["preregistered_decisions"]["secondary_original_location_reaction_advantage"]=="not_met_insufficient_discordants"


def test_new_native_seed_full_sham_bond_and_four_shuffle_replay():
    r=run_one(27001,reference.protocol(),replay=True)
    assert r["seed"]==27001 and r["selected"]
    assert 5<=r["native_source"]["size"]<=16
    assert r["native_source"]["original_edges_aged_at_least20"]>=2
    assert set(r["arms"])==set(ARMS)
    assert r["root_energy_total_unchanged_by_bond_pass"]
    base=sorted(r["post_bond_root_energy_id_order"])
    for rank in RANKS:
        o=r["arms"][f"root_scramble_{rank}"]
        assert sorted(o["source_energy_post"])==base
        assert o["intervention_metadata"]["outside_original_cohort_energy_unchanged"]
    for arm in ARMS:
        assert len(r["arms"][arm]["lotteries"])==32
        assert [x["salt"] for x in r["arms"][arm]["lotteries"]]==list(SALTS)
