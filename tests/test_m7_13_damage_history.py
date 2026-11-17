"""M7.13 test: second lesion intent-to-treat, energy-matched first-lesion sham."""
from support import make_energy_config,world_with
from tools import m7_13_damage_history as m
from tools.m7_11_ring_fault_tolerance import rings_now


def setup():
    cfg=make_energy_config(width=8,height=8,seed=813,
        species=[{"name":"S0","count":4,"move_probability":0.0,"energy":6,"max_bonds":2}],
        chemistry={"enabled":True,"bond_cost":2,"formation_probability":0.0,
                   "break_probability":0.0,"allowed_pairs":[["S0","S0"]],"catalysis":[]})
    w=world_with(cfg,positions=[(0,0),(1,0),(1,1),(0,1)],
        species=[0,0,0,0],energy=[2,2,2,2],
        bonds=[(0,1,4),(0,3,4),(1,2,4),(2,3,4)])
    assert w.configured_energy()==w.energy()==24
    w.check()
    ring=rings_now(w)[0]
    return w,ring


def test_frozen_protocol_and_independent_new_seed_population():
    p=m.protocol()
    assert p["status"]=="preregistered_before_M712_outcomes_and_M713_runner"
    assert (m.FIRST,m.LAST)==(31001,31640)
    assert len(p["sample"]["shards"])==16
    assert [s for d in p["sample"]["shards"] for s in range(d["start"],d["end"]+1)]==list(range(m.FIRST,m.LAST+1))
    assert p["integrity"]["never_filter_first_repair_success"]
    assert p["integrity"]["report_all_missed_second_targets_as_failures"]
    assert len(m.provenance()["m713_protocol_sha256"])==64


def test_energy_only_zero_bond_and_true_excised_have_exact_same_particle_energy():
    w,ring=setup()
    first=min(ring["edges"])
    original=w.state_hash_full(),w.rng.fingerprint(),w.rng.draws
    arms,meta=m.apply_first(w,first)
    assert arms["first_lesion"].store.energy==arms["energy_only_first_sham"].store.energy
    assert len(arms["first_lesion"].store.bonds)==3
    assert len(arms["energy_only_first_sham"].store.bonds)==4
    assert len(arms["no_first_lesion"].store.bonds)==4
    idx=tuple(sorted(arms["energy_only_first_sham"].store.index_of(i) for i in first))
    assert arms["energy_only_first_sham"].store.bonds[idx]==0
    assert meta["same_postfirst_lesion_and_energy_sham_particle_energy"]
    assert len({a.energy() for a in arms.values()})==1
    assert (w.state_hash_full(),w.rng.fingerprint(),w.rng.draws)==original


def test_full_synthetic_two_120_tick_native_regime_replay_and_ITT_missing_target():
    w,ring=setup()
    old=w.state_hash_full(),w.rng.fingerprint(),w.rng.draws
    res=m.follow(w,ring,validate=True)
    assert set(res["arms"])==set(m.ARMS)
    assert (w.state_hash_full(),w.rng.fingerprint(),w.rng.draws)==old
    assert res["first_original_cut_ID_pair"]!=res["second_original_precommitted_distinct_cut_ID_pair"]
    for name,x in res["arms"].items():
        assert len(x["checkpoints"])==8
        assert x["second_target_chemically_cut_at_t120"]
        assert x["second_challenge_ITT_success"] is False
        assert x["final"]["energy"]>=0
        assert x["first_t120"] is not None
    assert res["arms"]["no_first_lesion"]["first_edge_present_at_t120"]
    assert not res["arms"]["first_lesion"]["first_edge_present_at_t120"]


def mock(seed,exp=None,naive=None,sham=None):
    if exp is None:
        return {"seed":seed,"selected":False,"scan":{"reason":"no_ring"}}
    arms={}
    for arm,score in [("first_lesion",exp),("no_first_lesion",naive),("energy_only_first_sham",sham)]:
        arms[arm]={
            "second_target_chemically_cut_at_t120":True,
            "second_challenge_ITT_success":bool(score),
            "second_challenge_and_connected_at_t240":bool(score),
            "all_original_ring_connected_at_t240":True,
            "exact_original_ring_closed_at_t240":True,
            "first_edge_present_at_t120":True,
            "second_target_first_real_FORM_after_second_cut":11 if score else None
        }
    return {"seed":seed,"selected":True,"native_first_aged_ring":{"size":4},"arms":arms}


def test_frozen_gates_and_comparisons_keep_all_null_and_failed_first_repair():
    rows=[mock(s) for s in range(m.FIRST,m.LAST+1)]
    assert m.summarize(rows)["preregistered_decisions"]["first_damage_history_improves_second_native_recovery"]=="not_met_insufficient_natural_rings"
    for j in range(50):
        seed=m.FIRST+j
        if j<20:rows[j]=mock(seed,True,False,False)
        elif j<30:rows[j]=mock(seed,False,True,True)
        else:rows[j]=mock(seed,False,False,False)
    s=m.summarize(rows)
    assert s["selected_naturally_aged_native_ring_worlds"]==50
    assert s["paired_second_challenge"]["preregistered_primary_first_lesion_vs_no_first_lesion"]["discordant"]==30
    assert s["preregistered_decisions"]["first_damage_history_improves_second_native_recovery"]=="passed"
    assert s["preregistered_decisions"]["first_topology_damage_beats_same_particle_energy_refund_sham"]=="passed"
    for j in range(8):rows[j]=mock(m.FIRST+j,False,True,True)
    fail=m.summarize(rows)
    assert fail["preregistered_decisions"]["first_damage_history_improves_second_native_recovery"]=="not_met_favorable_fraction"


def test_first_heldout_natural_source_has_all_three_original_native_regimes():
    result=m.run_one(m.FIRST,verify=True)
    assert result["seed"]==m.FIRST
    if result["selected"]:
        assert result["native_first_aged_ring"]["size"] in (4,6,8)
        assert set(result["arms"])==set(m.ARMS)
        assert result["first_original_cut_ID_pair"]!=result["second_original_precommitted_distinct_cut_ID_pair"]
        assert all(len(x["checkpoints"])==8 for x in result["arms"].values())
    else:
        assert result["scan"]["reason"] in (
            "native_cycles_observed_but_none_aged_20_by_600",
            "no_native_simple_4_6_8_ring_by_600"
        )
