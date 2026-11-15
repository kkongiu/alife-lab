"""M6.9 sequence-isomer causal fork: no hidden pre-break physics change."""
from copy import deepcopy
from collections import Counter

from support import make_energy_config, world_with
from tools.m6_5_ring_forks import clone_world, ring4_candidates
from tools.m6_9_isomers import (
    PATTERNS, assert_prebreak_physics_identical, assign_isomer,
    cyclic_order, follow_pair, protocol, summarize, two_plus_two
)


def _world(break_probability=0.002):
    config=make_energy_config(
        seed=61,
        species=[
            {"name":"S0","count":2,"move_probability":0.5,"energy":20,"max_bonds":2},
            {"name":"S1","count":2,"move_probability":0.4,"energy":20,"max_bonds":2},
            {"name":"S3","count":1,"move_probability":0.6,"energy":8,"max_bonds":0},
        ],
        chemistry={
            "enabled":True,"bond_cost":2,
            "formation_probability":0.05,
            "break_probability":break_probability,
            "allowed_pairs":[["S0","S0"],["S0","S1"],["S1","S1"]],
            "catalysis":[],
        },
    )
    w=world_with(config,
                 [(0,0),(1,0),(1,1),(0,1),(4,4)],
                 [0,0,1,1,2],
                 energy=[16,16,16,16,8],
                 bonds=[(0,1,4),(1,2,4),(2,3,4),(3,0,4)])
    w.check()
    return w


def test_protocol_locked_new_seeds_and_gate():
    p=protocol()
    assert p["natural_sample"]["seeds"]==list(range(9601,9651))
    assert p["natural_sample"]["max_precursor_tick"]==600
    assert p["natural_sample"]["followup_ticks"]==180
    assert p["preregistered_decision"]["large_effect_threshold"]==.15


def test_two_plus_two_cycle_and_canonical_order():
    w=_world()
    (ring,)=ring4_candidates(w)
    assert two_plus_two(w,ring)
    order=cyclic_order(ring)
    assert len(order)==4 and set(order)==set(ring["ids"])


def test_isomer_assignment_preserves_energy_geometry_population_and_rng():
    w=_world()
    ring=ring4_candidates(w)[0]
    arms={}
    for variant in PATTERNS:
        c=clone_world(w)
        before=(c.energy(),list(c.store.energy),list(c.store.xs),
                list(c.store.ys),dict(c.store.bonds),c.rng.fingerprint(),
                c.rng.draws)
        out=assign_isomer(c,ring,variant)
        assert c.energy()==before[0]
        assert c.store.energy==before[1]
        assert c.store.xs==before[2] and c.store.ys==before[3]
        assert c.store.bonds==before[4]
        assert c.rng.fingerprint()==before[5] and c.rng.draws==before[6]
        assert Counter(c.store.species)==Counter(w.store.species)
        assert out["exact_signature"].startswith("C2:")
        arms[variant]=(c,out)
    assert arms["adjacent_S0S0S1S1"][1]["exact_signature"]!=arms["alternating_S0S1S0S1"][1]["exact_signature"]
    assert sum(arms[x][1]["changes_in_source_species_labels"] for x in PATTERNS)==2
    assert_prebreak_physics_identical(arms["adjacent_S0S0S1S1"][0],
                                      arms["alternating_S0S1S0S1"][0],
                                      ring["ids"])


def test_unbroken_pair_has_identical_physical_prefix():
    original=_world(break_probability=0.0)
    ring=ring4_candidates(original)[0]
    p=deepcopy(protocol())
    p["natural_sample"]["followup_ticks"]=12
    f=follow_pair(original,ring,p,sham=True)
    assert f["first_break_both"] is None
    assert f["prebreak_identical_full_physics_ticks"]==12
    for arm in PATTERNS:
        assert f["arms"][arm]["ring_at_final_tick"]
        assert f["arms"][arm]["first_original_edge_break_tick"] is None


def test_forced_break_synchronous_even_when_mobility_then_differs():
    original=_world(break_probability=1.0)
    ring=ring4_candidates(original)[0]
    p=deepcopy(protocol())
    p["natural_sample"]["followup_ticks"]=4
    f=follow_pair(original,ring,p,sham=True)
    assert f["first_break_both"]==1
    assert f["prebreak_identical_full_physics_ticks"]==0
    for arm in PATTERNS:
        assert f["arms"][arm]["first_original_edge_break_tick"]==1


def test_zero_forks_underpowered_no_false_discovery():
    s=summarize([],protocol())
    assert s["decision"]=="underpowered"
    for den in ("baseline","enriched"):
        assert s["by_density"][den]["source_bond_break_pairs"]==0
        assert s["by_density"][den]["natural_2S0_2S1_rings_selected"]==0
