"""Independent M7.10 replay must match original selected native first link."""
from tools import m7_5_mature_feedback as old
from tools.m7_10_independent_posthoc import (
    derive_native_acquisition,independent_fork_check,
    independent_remove_bond_full_refund,independent_conduct
)
from tools.m7_10_recruited_link_function import (
    select_first_acquired_native,follow
)
from support import make_energy_config,world_with
from tools.m6_5_ring_forks import clone_world


def fixture():
    cfg=make_energy_config(
        width=8,height=8,seed=710,
        species=[{"name":"S0","count":4,"move_probability":0.0,"energy":6,"max_bonds":3}],
        chemistry={"enabled":True,"bond_cost":2,"formation_probability":0,
                   "break_probability":0,"allowed_pairs":[["S0","S0"]],
                   "catalysis":[]}
    )
    return world_with(cfg,positions=[(0,0),(1,0),(2,0),(4,4)],
                      species=[0]*4,energy=[8,2,0,6],
                      bonds=[(0,1,4),(1,2,4)])


def test_original_M73_native_energy_and_independent_per_edge_suppression():
    w=fixture()
    old=clone_world(w)
    ctrl=clone_world(w)
    total,link,inwards,outwards=independent_conduct(old,"native_intact",(0,1),(1,2))
    assert total>=1 and link>=1
    assert inwards>=0 and outwards>=0
    total2,link2,_,_=independent_conduct(ctrl,"bond_intact_conduction_ablated",(0,1),(1,2))
    assert total2<total and link2==0
    assert old.energy()==ctrl.energy()==w.energy()
    assert old.state_hash_full()!=ctrl.state_hash_full()


def test_independent_real_native_source_first_eligibility_matches_M710():
    seed=28005
    o,source,first,reason=derive_native_acquisition(seed,old.protocol())
    p,cohort,chosen,decision=select_first_acquired_native(seed,old.protocol())
    assert (o is None)==(p is None)
    assert reason==decision["reason"]
    if o is not None:
        assert o.state_hash_full()==p.state_hash_full()
        assert o.rng.fingerprint()==p.rng.fingerprint()
        assert list(first["pair"])==chosen["native_first_link"]
        assert first["outsider"]==chosen["native_first_recruited_outsider_id"]
        assert list(source["ids"])==list(cohort["ids"])
        row=follow(p,cohort,chosen)
        stored={"seed":seed,"outcomes":row["outcomes"],
                "intervention_excised_refund_metadata":row["intervention_excised_refund_metadata"]}
        assert independent_fork_check(stored,o,source,first)
