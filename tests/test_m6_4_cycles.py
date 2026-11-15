"""M6.4: demonstrated WL cyclic alias and non-invasive natural ring audit."""
from alife.particles import ParticleStore
from alife.structures import components, signature
from tools.m6_4_cycles import (
    analyze_cycle, create_natural, exact_cycle_key,
    protocol, study_world, summary,
)


def ring_store(labels, width=4, height=4):
    if len(labels)==4:
        xy=[(0,0),(1,0),(1,1),(0,1)]
    elif len(labels)==6:
        xy=[(0,0),(1,0),(2,0),(2,1),(1,1),(0,1)]
    else:
        raise ValueError("test ring sizes 4 or 6")
    n=len(labels)
    bonds=[(i,(i+1)%n,4) for i in range(n)]
    return ParticleStore(width,height,list(range(n)),
                         [x for x,y in xy],[y for x,y in xy],
                         list(labels),[8]*n,bonds)


def test_two_nonisomorphic_four_rings_share_legacy_wl_fingerprint():
    adjacent=ring_store((0,0,1,1))
    alternating=ring_store((0,1,0,1))
    names=["S0","S1"]
    aidx,abond=components(adjacent)[0]
    bidx,bbond=components(alternating)[0]
    original_a=signature(adjacent,aidx,abond,names)
    original_b=signature(alternating,bidx,bbond,names)
    assert original_a.exact is False and original_b.exact is False
    assert original_a.key==original_b.key, (
        "Proposed WL ambiguity must be an actual behavior of repo signature()"
    )
    key_a=exact_cycle_key(adjacent,aidx,abond,names)
    key_b=exact_cycle_key(alternating,bidx,bbond,names)
    assert key_a!=key_b
    assert key_a.startswith("C:") and key_b.startswith("C:")


def test_canonical_ring_signature_invariant_under_rotation_reflection():
    names=["S0","S1"]
    sequence=(0,0,1,0,1,1)
    signatures=[]
    for variant in (sequence,sequence[2:]+sequence[:2],tuple(reversed(sequence))):
        s=ring_store(variant)
        idx,bonds=components(s)[0]
        signatures.append(exact_cycle_key(s,idx,bonds,names))
    assert len(set(signatures))==1


def test_protocol_frozen_and_no_synthetic_bonds():
    p=protocol()
    assert p["world"]["expected_runs"]==24
    assert p["world"]["seeds"]==list(range(8601,8613))
    for den in ("baseline","enriched"):
        w=create_natural(8601,den,p)
        assert len(w.store.bonds)==0
        w.check()


def test_short_natural_world_replay_deterministic():
    p=protocol()
    w=create_natural(8601,"baseline",p)
    x=study_world(w,steps=12)
    replay=create_natural(8601,"baseline",p)
    replay.advance(12)
    assert x["final_hash"]==replay.state_hash_full()
    assert x["final_rng_fingerprint"]==replay.rng.fingerprint()
    assert x["final_rng_draws"]==replay.rng.draws
    assert x["total_ring_episodes"]>=0
    assert x["four_ring_episodes"]<=x["total_ring_episodes"]


def test_zero_cyclic_samples_remain_nulls_not_false_evidence():
    p=protocol()
    mock=[]
    for d in ("baseline","enriched"):
        for seed in p["world"]["seeds"]:
            mock.append({"density":d,"seed":seed,
                         "total_ring_episodes":0,"four_ring_episodes":0,
                         "total_chain4_episodes":0,
                         "ring_material_sets_distinct":0,"rings_from_prev_chain4":0,
                         "ring_episodes":[],"chain4_episode_lengths":[],
                         "observed_legacy_aliases":{}})
    out=summary(mock)
    assert out["observed_natural_signature_aliasing"] is False
    assert out["observed_long_lived_four_ring"] is False
