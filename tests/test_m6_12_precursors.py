"""M6.12 - independent observer and geometric precursor invariants."""
from tools.m6_4_cycles import create_natural, protocol as natural_protocol
from tools.m6_10_pockets import observed_cycles
from tools.m6_12_precursors import (
    chemically_eligible, material_intact, precursor_candidates, protocol,
    risk_key, study_world, summarize
)
from test_m6_10_pockets import synthetic_pocket


def seven_path(empty=False):
    world=synthetic_pocket(empty=empty)
    s=world.store
    edge=next(iter(s.bonds))
    refund=s.remove_bond(*edge)
    s.energy[edge[0]]+=refund
    world.check()
    return world


def test_protocol_was_frozen():
    p=protocol()
    assert p["fixed_sample"]["seed_start"]==11001
    assert p["fixed_sample"]["seed_end"]==11150
    assert p["fixed_sample"]["total_worlds"]==300
    assert p["decisions"]["biological_claims"] is False


def test_native_seven_path_is_geometric_barrier_before_eighth_bond():
    w=seven_path()
    (obj,)=precursor_candidates(w)
    assert obj["stratum"]=="free_mobile"
    assert obj["resident_mobile"] and obj["resident_id"]==8
    assert len(obj["edges"])==7
    assert chemically_eligible(w,obj["missing"])
    assert material_intact(w,obj,set())==(True,None)
    # The monomer cannot move before the eighth edge exists.
    for _ in range(35):
        w.advance(1)
        s=w.store
        assert (s.xs[8],s.ys[8])==(3,3)
        assert material_intact(w,obj,set())==(True,None)
    rings,_=observed_cycles(w)
    assert not any(r.get("pocket") is True for r in rings)


def test_empty_center_and_broken_original_edge():
    w=seven_path(empty=True)
    (obj,)=precursor_candidates(w)
    assert obj["stratum"]=="empty"
    assert obj["resident_id"] is None
    edge=next(iter(obj["edges"]))
    assert material_intact(w,obj,{edge})==(False,"original_edge_broken")


def test_eighth_edge_closure_is_not_enclosure_onset():
    w=seven_path()
    (obj,)=precursor_candidates(w)
    s=w.store
    ia,ib=[s.index_of(q) for q in obj["missing"]]
    s.energy[ia]-=2
    s.energy[ib]-=2
    s.add_bond(ia,ib,4)
    w.check()
    rings,_=observed_cycles(w)
    assert any(r.get("pocket") is True for r in rings)
    assert material_intact(w,obj,set())==(True,None)
    assert precursor_candidates(w)==[]


def test_short_natural_campaign_is_passive():
    p=natural_protocol()
    a=create_natural(11001,"baseline",p)
    b=create_natural(11001,"baseline",p)
    rec=study_world(a,steps=5)
    b.advance(5)
    b.check()
    assert rec["final"]["hash"]==b.state_hash_full()
    assert rec["final"]["rng"]==b.rng.fingerprint()
    assert rec["final"]["draws"]==b.rng.draws
    assert rec["final"]["energy"]==b.energy()
    assert rec["final"]["formed"]==b.bonds_formed_total


def test_empty_outcome_and_non_independence_gate():
    p=protocol()
    null={"density":"baseline","seed":11001,"result":{
        "counts":{},"episodes":[],"strata":{}
    }}
    a=summarize([null],p)
    assert a["decision"]=="no_confirmed_30tick_confinement"
    assert a["closure_comparison_underpowered"] is True
    assert a["by_density"]["baseline"]["worlds"]==1
    assert risk_key("free_mobile","S0-S1")=="free_mobile|S0-S1"
    first={"resident_mobile":True,"duration_ticks":31,"stratum":"free_mobile",
           "closure_observed":False}
    x={**null,"result":{"counts":{},"episodes":[first],"strata":{}}}
    assert summarize([x],p)["decision"]=="single_unreplicated_30tick_confinement"
    y={**x,"seed":11002}
    assert summarize([x,y],p)["decision"]=="repeated_native_geometric_confinement_only"


def test_posthoc_target_11110_reproduces_full_282_tick_barrier():
    """Result-informed independent rerun: not part of original preregistered gate."""
    p=natural_protocol()
    tracked=create_natural(11110,"enriched",p)
    observed=study_world(tracked,600)
    positive=[e for e in observed["episodes"] if e["resident_mobile"]]
    assert len(positive)==1
    ep=positive[0]
    assert ep["start_tick"]==225
    assert ep["resident_id"]==244
    assert ep["center"]==[20,6]
    assert ep["duration_ticks"]==282
    assert ep["first_closure_tick"]==231
    assert ep["ended_by"]=="original_edge_broken"
    bare=create_natural(11110,"enriched",p)
    bare.advance(600)
    bare.check()
    assert bare.state_hash_full()==observed["final"]["hash"]
    assert bare.rng.fingerprint()==observed["final"]["rng"]
    assert bare.rng.draws==observed["final"]["draws"]
    assert bare.energy()==observed["final"]["energy"]
    assert bare.dissipated==observed["final"]["dissipated"]
    assert bare.bonds_formed_total==observed["final"]["formed"]
    assert bare.bonds_broken_total==observed["final"]["broken"]
