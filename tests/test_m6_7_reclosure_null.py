"""M6.7: fixed 5% physics reference and completely non-invasive read-only audit."""
from copy import deepcopy
import math

from support import make_energy_config, world_with
from tools.m6_5_ring_forks import ring4_candidates, opening_edges
from tools.m6_7_reclosure_null import (
    prereg, target_edge_candidate, opened_followup, summarize
)


def synthetic_square():
    cfg=make_energy_config(
        seed=23,
        species=[
            {"name":"S0","count":2,"move_probability":0.0,
             "energy":20,"max_bonds":2},
            {"name":"S1","count":2,"move_probability":0.0,
             "energy":20,"max_bonds":2},
        ],
        chemistry={
            "enabled":True,"bond_cost":2,
            "formation_probability":0.05,"break_probability":0.002,
            "allowed_pairs":[["S0","S0"],["S0","S1"],["S1","S1"]],
            "catalysis":[],
        },
    )
    world=world_with(
        cfg,[(0,0),(1,0),(1,1),(0,1)],
        [0,0,1,1],energy=[16,16,16,16],
        bonds=[(0,1,4),(1,2,4),(2,3,4),(3,0,4)]
    )
    world.check()
    return world


def test_preregistered_new_seeds_and_correct_fixed_ideal_reference():
    p=prereg()
    s=p["prespecified_source"]
    assert s["new_seeds"]==list(range(9201,9221))
    assert s["tick_horizon"]==10
    assert s["opened_arms"]==["lowest_source_id_edge","opposite_disjoint_edge"]
    assert math.isclose(p["null_model"]["reference_probability_by_tick10"],
                        1-(1-0.05)**10,abs_tol=1e-12)
    assert p["decision"]["absolute_margin_to_naive_reference"]==0.10


def test_only_source_pair_unbonded_is_candidate_before_any_chemistry():
    w=synthetic_square()
    ring,=ring4_candidates(w)
    low,op=opening_edges(ring)
    assert target_edge_candidate(w,low) is False
    from tools.m6_5_ring_forks import open_bond,clone_world
    for edge in (low,op):
        c=clone_world(w)
        open_bond(c,edge)
        assert target_edge_candidate(c,edge) is True
        assert c.energy()==w.energy()


def test_opened_observer_preserves_exact_replay_and_rng():
    w=synthetic_square()
    ring,=ring4_candidates(w)
    low,op=opening_edges(ring)
    initial=w.state_hash_full()
    rng=w.rng.fingerprint()
    initial_draws=w.rng.draws
    first=opened_followup(w,ring,low,10,verify_sham=True)
    second=opened_followup(w,ring,op,10,verify_sham=True)
    duplicate=opened_followup(w,ring,low,10,verify_sham=True)
    assert duplicate==first
    assert len(first["target_pre_step_candidate_flags"])==10
    assert len(second["original_ring_snapshot_flags"])==10
    assert first["candidate_ticks_before_first_event"]<=10
    assert 0<=first["candidate_opportunities_before_first_event"]<=10
    assert w.state_hash_full()==initial
    assert w.rng.fingerprint()==rng and w.rng.draws==initial_draws
    w.check()


def test_all_zero_forks_are_underpowered_not_success():
    p=prereg()
    s=summarize([],p)
    assert s["verdict"]=="underpowered"
    for den in ("baseline","enriched"):
        for arm in ("lowest_source_id_edge","opposite_disjoint_edge"):
            x=s["density_arm"][den][arm]
            assert x["n"]==0
            assert x["fraction_formation"] is None


def test_gate_pre_registered_in_each_of_four_strata():
    p=prereg()
    proto=p["prespecified_source"]
    out=[]
    for den in proto["densities"]:
        for seed in proto["new_seeds"]:
            for idx in range(2):
                out.append({
                    "density":den,"seed":seed,
                    "cases":{
                        arm:{
                            "any_target_bond_formation_event":False,
                            "any_ring_snapshot":False,
                            "candidate_opportunities_before_first_event":10,
                            "candidate_ticks_before_first_event":10,
                            "first_formation_event_tick":None,
                        } for arm in proto["opened_arms"]
                    }
                })
    result=summarize(out,p)
    assert result["verdict"]=="deviation_from_naive_contact_reference_in_at_least_one_stratum"
    for den in proto["densities"]:
        for arm in proto["opened_arms"]:
            assert result["density_arm"][den][arm]["n"]==40
