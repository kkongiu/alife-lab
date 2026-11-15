"""Regression tests for frozen M6.3-0 diagnostic; no engine changes."""
from copy import deepcopy

from alife.structures import signature
from tools.m6_3_0_screen import (
    frozen_protocol, make_world, signature_of_scaffold,
    event_counts_for_world, toroidal_distance,
)


def test_synthetic_templates_have_same_composition_but_distinct_exact_signatures():
    p=frozen_protocol()
    seed=p["model"]["seed_list"][0]
    a=make_world(seed,"A",p); b=make_world(seed,"B",p)
    sa,sb=signature_of_scaffold(a),signature_of_scaffold(b)
    assert sa and sb and sa!=sb
    assert signature_of_scaffold(make_world(seed,"A_reverse",p))==sa
    assert signature_of_scaffold(make_world(seed,"B_reverse",p))==sb
    assert signature_of_scaffold(make_world(seed,"unbonded_A",p)) is None
    assert signature_of_scaffold(make_world(seed,"unbonded_B",p)) is None
    assert a.counts()==b.counts()
    assert a.config.hash()==b.config.hash()


def test_fixed_background_and_rng_equal_on_initialization():
    p=frozen_protocol()
    seed=p["model"]["seed_list"][1]
    a=make_world(seed,"A",p)
    b=make_world(seed,"B",p)
    c=make_world(seed,"unbonded_B",p)
    for other in (b,c):
        assert other.rng.fingerprint()==a.rng.fingerprint()
        assert other.rng.draws==a.rng.draws
        assert [(other.store.xs[i],other.store.ys[i],other.store.species[i])
                for i in range(4,len(other.store))] == [
                   (a.store.xs[i],a.store.ys[i],a.store.species[i])
                   for i in range(4,len(a.store))
                ]


def test_energy_ledger_for_bonded_vs_unbonded_is_valid():
    p=frozen_protocol()
    seed=p["model"]["seed_list"][0]
    a=make_world(seed,"A",p)
    no_bond=make_world(seed,"unbonded_A",p)
    assert len(a.store.bonds)==3 and len(no_bond.store.bonds)==0
    assert a.dissipated==6 and no_bond.dissipated==0
    assert a.energy()==a.configured_energy()-6
    assert no_bond.energy()==no_bond.configured_energy()
    a.check();no_bond.check()


def test_toroidal_distance_wraps():
    assert toroidal_distance((0,0),(23,0),24,24)==1


def test_observer_does_not_consume_rng_and_is_reproducible_short_fixture():
    p=deepcopy(frozen_protocol())
    p["model"]["duration_steps"]=4
    w1=make_world(p["model"]["seed_list"][0],"A",p)
    w2=make_world(p["model"]["seed_list"][0],"A",p)
    a=signature_of_scaffold(w1)
    b=signature_of_scaffold(make_world(p["model"]["seed_list"][0],"B",p))
    result1=event_counts_for_world(w1,p,{"A":a,"B":b})
    result2=event_counts_for_world(w2,p,{"A":a,"B":b})
    assert result1==result2
    assert result1["elapsed_steps"]==4
    assert w1.state_hash_full()==w2.state_hash_full()
