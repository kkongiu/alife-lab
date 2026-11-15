"""M6.5 paired counterfactual: complete clone, energy-conserving ring opening."""
from copy import deepcopy

from support import make_energy_config, world_with
from tools.m6_5_ring_forks import (
    clone_world, followup, open_bond, opening_edges, paired_experiment,
    protocol, ring4_candidates, status, summary,
)


def _synthetic_ring():
    """Valid square ring assembled ONLY for a controlled invariant test.

    Unlike the straight M6.3 fixture, ids 0 and 3 are grid-neighbors.
    """
    cfg=make_energy_config(
        species=[
            {"name":"S0","count":2,"move_probability":0.0,
             "energy":20,"max_bonds":2},
            {"name":"S1","count":2,"move_probability":0.0,
             "energy":20,"max_bonds":2},
        ],
        chemistry={
            "enabled": True, "bond_cost":2,
            "formation_probability":0.0,"break_probability":0.0,
            "allowed_pairs":[["S0","S0"],["S0","S1"],["S1","S1"]],
            "catalysis":[],
        },
    )
    w=world_with(
        cfg,[(0,0),(1,0),(1,1),(0,1)],[0,0,1,1],
        energy=[16,16,16,16],
        bonds=[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],
    )
    w.check()
    return w


def test_protocol_locked_before_runner():
    p=protocol()
    assert p["sampling"]["seeds"]==list(range(8801,8813))
    assert p["sampling"]["max_selected"]==48
    assert p["sampling"]["followup_steps"]==120
    assert p["sampling"]["arms"]==[
        "keep_ring","open_lowest_edge","open_opposite_edge"
    ]


def test_exact_clone_retains_rng_hash_and_accounting():
    src=_synthetic_ring()
    cloned=clone_world(src)
    assert cloned is not src
    assert cloned.store is not src.store
    assert cloned.rng is not src.rng
    assert cloned.state_hash_full()==src.state_hash_full()
    assert cloned.energy()==src.energy()
    assert cloned.rng.fingerprint()==src.rng.fingerprint()
    cloned.advance(3)
    src.advance(3)
    assert cloned.state_hash_full()==src.state_hash_full()
    assert cloned.rng.fingerprint()==src.rng.fingerprint()


def test_open_both_opposite_ring_edges_conserves_energy():
    src=_synthetic_ring()
    (ring,)=ring4_candidates(src)
    assert ring["sig"].startswith("C2:")
    low,opp=opening_edges(ring)
    assert set(low).isdisjoint(opp)
    for e in (low,opp):
        w=clone_world(src)
        initial=(w.energy(),w.rng.fingerprint(),w.rng.draws)
        saved=open_bond(w,e)
        assert saved>=0
        assert w.energy()==initial[0]
        assert w.rng.fingerprint()==initial[1]
        assert w.rng.draws==initial[2]
        assert status(w,ring["ids"])["isolated"]
        assert not status(w,ring["ids"])["ring"]
        assert len(w.store.bonds)==len(src.store.bonds)-1
        w.check()


def test_short_synthetic_fork_repeatable_and_sham_exact():
    src=_synthetic_ring()
    ring=ring4_candidates(src)[0]
    p=deepcopy(protocol())
    p["sampling"]["followup_steps"]=5
    a=paired_experiment(src,ring,p,sham_check=True)
    b=paired_experiment(src,ring,p,sham_check=True)
    assert a==b
    for arm in p["sampling"]["arms"]:
        assert len(a["arms"][arm]["snapshots"])>=1
        assert a["arms"][arm]["initial_energy"]==src.energy()


def test_null_outcomes_never_become_positive_signal():
    p=deepcopy(protocol())
    rows=[]
    for den in p["sampling"]["densities"]:
        for seed in p["sampling"]["seeds"]:
            base={
                "final_isolated":False,"final_ring":False,
                "isolated_ticks":0,"first_loss_tick":1,
                "first_loss_reason":"attachment",
                "first_ring_observed_tick":None,
            }
            rows.append({
                "density":den,"precursor_seed":seed,
                "arms":{arm:dict(base) for arm in p["sampling"]["arms"]}
            })
    r=summary(rows,p)
    assert r["gate_passed"] is False
    assert r["verdict"]=="no_robust_ring_closure_protection"
