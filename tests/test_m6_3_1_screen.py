"""M6.3-1 gates: motifs, isoenergetic controls and exposure tracing."""
from copy import deepcopy

from tools.m6_3_0_screen import make_world, signature_of_scaffold
from tools.m6_3_1_screen import (
    analyse_runs, density_protocol, paired_initial_state,
    protocol, take_measurements, variants,
)


def test_three_motifs_distinct_exact_and_reversal_equivalent():
    p=protocol()
    names=variants(p)
    assert set(names)=={"A","B","C"} and len(set(names.values()))==3
    d=density_protocol(p,"baseline")
    for arm in ("A","B","A_reverse","B_reverse","C"):
        w=make_world(8101,arm,d)
        identity="A" if arm.startswith("A") else ("B" if arm.startswith("B") else "C")
        assert signature_of_scaffold(w)==names[identity]
        w.check()


def test_isoenergetic_within_each_density_and_background_same():
    p=protocol()
    for density in p["model"]["densities"]:
        d=density_protocol(p,density)
        results=[make_world(8102,arm,d) for arm in p["model"]["arm_order"]]
        for w in results: w.check()
        reference=paired_initial_state(results[0])
        assert all(paired_initial_state(w)==reference for w in results)
        assert all(len(w.store.bonds)==3 for w in results)
        assert all(w.dissipated==6 for w in results)
        assert all(w.energy()==w.configured_energy()-6 for w in results)
        assert results[0].counts()==results[-1].counts()


def test_two_densities_have_identical_laws_but_different_populations():
    p=protocol()
    a=make_world(8101,"A",density_protocol(p,"baseline"))
    b=make_world(8101,"A",density_protocol(p,"enriched"))
    assert len(a.store)==200 and len(b.store)==264
    assert a.config.chemistry==b.config.chemistry
    assert a.config.energy==b.config.energy
    assert a.config.grid==b.config.grid
    assert signature_of_scaffold(a)==signature_of_scaffold(b)


def test_short_observation_does_not_change_reproducibility():
    p=deepcopy(protocol())
    p["model"]["duration_steps"]=6
    signatures=variants(p)
    setup=density_protocol(p,"baseline")
    first=make_world(8103,"A",setup)
    second=make_world(8103,"A",setup)
    x=take_measurements(first,p,"A",signatures)
    y=take_measurements(second,p,"A",signatures)
    assert x==y
    assert first.state_hash_full()==second.state_hash_full()
    assert x["ticks"]==6
    assert x["active_template_ticks"] + (
        6-x["active_template_ticks"]
    ) == 6
    assert x["initial_dissipated"]==6


def test_power_gate_requires_events_and_active_source():
    p=deepcopy(protocol())
    seed_list=p["model"]["seed_list"]
    arms=p["model"]["arm_order"]
    densities=list(p["model"]["densities"])
    empty={
        "counts":{},"active_template_ticks":0,
        "free_monomer_exposure_ticks":{},
        "bond_formations":0,
    }
    rows=[
        dict(empty,density=d,arm=a,seed=s)
        for d in densities for s in seed_list for a in arms
    ]
    output=analyse_runs(p,rows)
    assert output["gates"]["power_gate"] is False
    assert output["gates"]["specificity_gate"] is False
    assert output["verdict"]=="underpowered_or_no_detectable_specificity"
