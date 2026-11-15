"""M6.8 independent energy-placement control: physics and frozen-gate tests."""
from copy import deepcopy

from support import make_energy_config, world_with
from tools.m6_5_ring_forks import clone_world, opening_edges, open_bond, ring4_candidates, status
from tools.m6_8_energy_control import (
    protocol, select_inert_s3, open_sequester, matched_fork, summary
)


def synthetic_square_with_inert():
    config=make_energy_config(
        seed=26,
        species=[
            {"name":"S0","count":2,"move_probability":0.0,"energy":20,"max_bonds":2},
            {"name":"S1","count":2,"move_probability":0.0,"energy":20,"max_bonds":2},
            {"name":"S3","count":1,"move_probability":0.0,"energy":8,"max_bonds":0},
        ],
        chemistry={
            "enabled":True,"bond_cost":2,
            "formation_probability":0.05,"break_probability":0.002,
            "allowed_pairs":[["S0","S0"],["S0","S1"],["S1","S1"]],
            "catalysis":[],
        }
    )
    world=world_with(
        config,[(0,0),(1,0),(1,1),(0,1),(4,4)],
        [0,0,1,1,2],
        energy=[16,16,16,16,8],
        bonds=[(0,1,4),(1,2,4),(2,3,4),(3,0,4)]
    )
    world.check()
    return world


def test_preregistered_seed_and_strong_weak_decisions():
    p=protocol()
    assert p["seeds"]==list(range(9401,9421))
    assert p["horizon"]==120 and p["early_horizon"]==10
    assert p["gate"]["min_forks_per_density"]==20
    assert p["gate"]["small_margin"]==.1
    assert p["gate"]["strong_margin"]==.15
    assert p["arms"]==[
        "keep_intact","open_refund_endpoints","open_sequester_in_S3"
    ]


def test_same_open_geometry_energy_and_rng_only_placement_differs():
    original=synthetic_square_with_inert()
    (ring,)=ring4_candidates(original)
    edge=opening_edges(ring)[0]
    w_refund=clone_world(original)
    w_s3=clone_world(original)
    index,distance=select_inert_s3(original,ring["ids"])
    assert original.store.ids[index]==4 and distance>=3
    initial_source=[original.store.energy[i] for i in range(4)]
    stored=open_bond(w_refund,edge)
    saved,id_,far=open_sequester(w_s3,edge,ring["ids"])
    assert id_==4 and far==distance and saved==stored
    assert w_s3.store.energy[:4]==initial_source
    assert w_refund.store.energy[index]+stored==w_s3.store.energy[index]
    assert w_refund.store.bonds==w_s3.store.bonds
    assert w_refund.store.degree==w_s3.store.degree
    assert w_refund.store.xs==w_s3.store.xs
    assert w_refund.store.ys==w_s3.store.ys
    assert w_refund.energy()==w_s3.energy()==original.energy()
    assert w_refund.rng.fingerprint()==w_s3.rng.fingerprint()==original.rng.fingerprint()
    assert status(w_refund,ring["ids"])["isolated"]
    assert status(w_s3,ring["ids"])["isolated"]
    assert not status(w_s3,ring["ids"])["ring"]


def test_three_arm_synthetic_stable_sham_and_original_noninvasive():
    original=synthetic_square_with_inert()
    (ring,)=ring4_candidates(original)
    original_hash=original.state_hash_full()
    original_rng=original.rng.fingerprint()
    p=deepcopy(protocol())
    p["horizon"]=10
    a=matched_fork(original,ring,p,sham=True)
    b=matched_fork(original,ring,p,sham=True)
    assert a==b
    assert original.state_hash_full()==original_hash
    assert original.rng.fingerprint()==original_rng
    for arm in p["arms"]:
        assert len(a["arms"][arm]["snapshots"])>=1
        assert a["arms"][arm]["final_energy"]<=original.energy()


def test_no_cases_do_not_claim_evidence():
    s=summary([],protocol())
    assert s["verdict"]=="underpowered"
    for den in ("baseline","enriched"):
        assert s["by_density"][den]["n_selected_forks"]==0


def test_paired_gate_needs_both_densities_with_large_same_sign():
    p=protocol()
    fixtures=[]
    for den in p["densities"]:
        for seed in p["seeds"]:
            for i in range(2):
                base={
                    "final_isolated":True,"isolated_ticks":120,
                    "first_ring_observed_tick":None,"first_loss_tick":None,
                    "opened_edge_formed_by_t10":False,
                }
                fixtures.append({
                    "density":den,"seed":seed,
                    "fork":{"endpoints_at_formation_cost_before_opening":2},
                    "arms":{
                        "keep_intact":dict(base),
                        "open_refund_endpoints":{**base,"opened_edge_formed_by_t10":True},
                        "open_sequester_in_S3":dict(base),
                    }
                })
    out=summary(fixtures,p)
    assert out["verdict"]=="allocation_effect_signal_needs_replication"
    for den in p["densities"]:
        assert out["by_density"][den]["refund_minus_sequester_early_formation"]==1
