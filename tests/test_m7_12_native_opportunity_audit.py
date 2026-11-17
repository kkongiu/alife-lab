"""M7.12: original pair candidate audit leaves native physics and RNG untouched."""
from support import make_energy_config,world_with
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_12_native_opportunity_audit import (
    protocol,provenance,adjacent,initial_static,advance_with_exact_candidate_audit,
    run_one,summary,FIRST,LAST
)


def fixture():
    cfg=make_energy_config(
        width=8,height=8,seed=812,
        species=[{"name":"S0","count":4,"move_probability":0.0,"energy":6,"max_bonds":2}],
        chemistry={"enabled":True,"bond_cost":2,"formation_probability":0.0,
                   "break_probability":0.0,"allowed_pairs":[["S0","S0"]],"catalysis":[]}
    )
    w=world_with(cfg,positions=[(0,0),(1,0),(1,1),(0,1)],
                 species=[0,0,0,0],energy=[4,4,2,2],
                 bonds=[(1,2,4),(2,3,4),(0,3,4)])
    assert w.configured_energy()==w.energy()==24
    return w


def test_prereg_and_new_640_seed_worlds():
    p=protocol()
    assert p["status"]=="preregistered_before_new_runner_and_observed_outcomes"
    assert (FIRST,LAST)==(30001,30640)
    assert len(p["sample"]["shards"])==16
    assert [s for d in p["sample"]["shards"] for s in range(d["start"],d["end"]+1)]==list(range(FIRST,LAST+1))
    assert len(provenance()["unchanged_M6_chemistry_sha256"])==64


def test_native_generator_observer_detects_energetic_neighbor_without_changes():
    w=fixture()
    pair=(0,1)
    assert adjacent(w,pair)
    status=initial_static(w,pair,{(0,1),(0,3),(1,2),(2,3)})
    assert status["still_anchored_by_surviving_original_bonds"]
    assert status["native_both_endpoints_energetically_eligible"]
    assert status["native_valence_available"]
    assert status["is_an_actual_native_pair_candidate_now"]
    reference=clone_world(w)
    watched=clone_world(w)
    captured=advance_with_exact_candidate_audit(watched,pair)
    reference.advance(1)
    assert captured and captured[0]["candidate_at_exact_native_formation_stage"]
    assert reference.state_hash_full()==watched.state_hash_full()
    assert reference.rng.fingerprint()==watched.rng.fingerprint()
    energy_transfer(watched,"bond_only")
    energy_transfer(reference,"bond_only")
    assert reference.state_hash_full()==watched.state_hash_full()


def test_no_candidate_when_endpoint_lacks_native_energy():
    w=fixture()
    w.store.energy[0]=0
    status=initial_static(w,(0,1),{(0,1),(0,3),(1,2),(2,3)})
    assert not status["native_both_endpoints_energetically_eligible"]
    assert not status["is_an_actual_native_pair_candidate_now"]


def test_first_real_seed_same_no_observer_native_full_120_step_hash():
    row=run_one(FIRST,verify=True)
    assert row["seed"]==FIRST
    if row["selected"]:
        assert row["t0_cut_pair_native_geometry_energy_valence"]["adjacent"]
        assert len(row["frozen_same-geometry_32_pair_lotteries"])==32
        assert len(row["native_candidate_exposures"])==row["pre_event_or_censor_ticks"]
        assert row["actual_target_pair_candidate_attempts_before_first_event_or_censor"]<=row["pre_event_or_censor_ticks"]
        assert all(not x["actual_native_target_FORM_event"] or x["target_at_native_formation_stage"] for x in row["native_candidate_exposures"])
    else:
        assert "reason" in row["scan"]
