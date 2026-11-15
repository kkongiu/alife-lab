"""Versioned detector: exact ring identity without changing historical tracker."""
import json
import pytest

from alife.particles import ParticleStore
from alife.structures import (
    CYCLE_SIGNATURE_SCHEME, ExactCycleTrackerV2, Tracker,
    components, signature, signature_v2,
)
from support import make_energy_config, world_with


def _ring(labels, coords=None):
    xy=coords or [(0,0),(1,0),(1,1),(0,1)]
    size=len(labels)
    return ParticleStore(8,8,list(range(size)),
                         [x for x,y in xy],[y for x,y in xy],
                         list(labels),[8]*size,
                         [(i,(i+1)%size,4) for i in range(size)])


def _sig(store, fn):
    (indices,bonds),=components(store)
    return fn(store,indices,bonds,["S0","S1"])


def test_real_four_ring_WL_alias_resolved_only_when_opted_in():
    adjacent=_ring([0,0,1,1])
    alternating=_ring([0,1,0,1])
    historical=[_sig(a,signature) for a in (adjacent,alternating)]
    fixed=[_sig(a,signature_v2) for a in (adjacent,alternating)]
    assert historical[0].key==historical[1].key
    assert historical[0].key.startswith("F:")
    assert not historical[0].exact and not historical[1].exact
    assert fixed[0].key!=fixed[1].key
    assert all(s.key.startswith("C2:") and s.exact for s in fixed)
    assert fixed[0].composition==fixed[1].composition
    assert json.loads(fixed[0].key[3:]) == ["S0","S0","S1","S1"]
    assert json.loads(fixed[1].key[3:]) == ["S0","S1","S0","S1"]


def test_rotation_and_reversal_invariant_even_when_particle_ids_change():
    a=_ring([0,0,1,1])
    b=_ring([1,0,0,1])
    c=_ring([1,1,0,0])
    assert len({_sig(x,signature_v2).key for x in (a,b,c)})==1


def test_tree_behavior_and_original_keys_unchanged():
    s=ParticleStore(8,8,[0,1,2], [0,1,2],[0,0,0],
                    [0,1,0],[8,8,8], [(0,1,4),(1,2,4)])
    assert _sig(s,signature)==_sig(s,signature_v2)
    assert _sig(s,signature_v2).exact


def test_multi_cycle_non_simple_graph_remains_explicitly_fuzzy():
    # Square plus a tail: one non-regular cyclic component with 5 nodes.
    s=ParticleStore(8,8,list(range(5)),[0,1,1,0,0],[0,0,1,1,2],
                    [0,1,0,1,0],[8]*5,
                    [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,4,4)])
    assert _sig(s,signature_v2)==_sig(s,signature)
    assert not _sig(s,signature_v2).exact


def test_detector_checkpoint_opt_in_explicit_and_legacy_unchanged():
    config=make_energy_config(
        species=[
            {"name":"S0","count":2,"move_probability":0.0,
             "energy":20,"max_bonds":2},
            {"name":"S1","count":2,"move_probability":0.0,
             "energy":20,"max_bonds":2},
        ],
        chemistry={"enabled":False},
    )
    w=world_with(config,[(0,0),(1,0),(1,1),(0,1)],[0,0,1,1],
                 bonds=[(0,1,4),(1,2,4),(2,3,4),(3,0,4)])
    old=Tracker()
    new=ExactCycleTrackerV2()
    initial=(w.state_hash_full(),w.rng.state(),w.rng.draws)
    old.observe(w)
    new.observe(w)
    assert (w.state_hash_full(),w.rng.state(),w.rng.draws)==initial
    assert next(iter(old.active.values())).signature.key.startswith("F:")
    assert next(iter(new.active.values())).signature.key.startswith("C2:")
    legacy=old.to_dict()
    fixed=new.to_dict()
    assert "signature_scheme" not in legacy
    assert fixed["signature_scheme"]==CYCLE_SIGNATURE_SCHEME
    with pytest.raises(ValueError,match="no implicit migration"):
        ExactCycleTrackerV2.from_dict(legacy)
    restored=ExactCycleTrackerV2.from_dict(fixed)
    assert restored.to_dict()==fixed
    assert Tracker.from_dict(legacy).to_dict()==legacy
    # Confirm both restored trackers continue with their own scheme.
    w.step=1
    restored.observe(w)
    assert next(iter(restored.active.values())).signature.key.startswith("C2:")
