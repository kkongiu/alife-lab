"""M6.14: test the stricter first-born source-material gate and zero-world handling."""
from tools.m6_14_first_genesis import (
    first_birth_provenance, is_primary, is_long, protocol, replay,
    study_world, summarize, wilson
)
from tools.m6_4_cycles import create_natural, protocol as natural_protocol


MATERIAL=(4,6,7,9,11,13,15,18)


def episode(duration=30, first=True, mobile=True, censored=False):
    return {
        "resident_mobile":mobile, "duration_ticks":duration,
        "right_censored":censored,"new_material_first_seven_edge":first,
        "start_tick":104,"center":[3,4],"resident_id":20,
        "first_eighth_bond_tick":None, "historical_first_kind":"seven",
        "prior_seven_edge_episodes":0 if first else 1,
        "ended_by":"right_censored_at_horizon" if censored else "original_edge_broken"
    }


def sample():
    p=protocol()
    worlds=[
        {"seed":seed,"density":"enriched",
         "result":{"counts":{},"episodes":[],"first_material_shapes":{}}}
        for seed in range(p["sample"]["seed_first"],p["sample"]["seed_last"]+1)
    ]
    return p,worlds


def test_preregistration_and_exact_shard_coverage():
    p=protocol()
    assert p["sample"]["seed_first"]==13001
    assert p["sample"]["seed_last"]==14600
    assert p["sample"]["expected_worlds"]==1600
    assert p["primary"]["no_threshold_change_after_results"] is True
    assert p["integrity"]["no_src_changes"] is True
    observed=[
        seed for shard in p["sample"]["shards"]
        for seed in range(shard["start"],shard["end"]+1)
    ]
    assert observed==list(range(13001,14601))


def test_no_prior_material_shape_is_first_seven_edge_genesis():
    first=first_birth_provenance(MATERIAL,{}, {},{},205)
    assert first["new_material_first_seven_edge"] is True
    assert first["first_material_ever_seen"] is True
    assert first["historical_first_kind"]=="seven"
    prior_ring=first_birth_provenance(MATERIAL,{MATERIAL:"eight"}, {},{},205)
    assert prior_ring["new_material_first_seven_edge"] is False
    assert prior_ring["historical_first_kind"]=="eight"
    prior_seven=first_birth_provenance(MATERIAL,{MATERIAL:"seven"},
                                      {MATERIAL:2},{MATERIAL:180},205)
    assert prior_seven["new_material_first_seven_edge"] is False
    assert prior_seven["prior_seven_edge_episodes"]==2
    assert prior_seven["ticks_since_prior_ending"]==25


def test_preregistered_gate_boundary_and_censoring():
    assert is_primary(episode(30,first=True))
    assert is_primary(episode(30,first=True,censored=True))
    assert not is_primary(episode(29,first=True))
    assert not is_primary(episode(160,first=False))
    assert not is_primary(episode(120,first=True,mobile=False))
    assert is_long(episode(160,first=False))
    assert wilson(0,1600)["low"]==0


def test_same_recurrent_events_do_not_make_two_seed_first_success():
    p,worlds=sample()
    worlds[0]["result"]["episodes"]=[episode(180,first=False)]
    worlds[1]["result"]["episodes"]=[episode(100,first=False)]
    s=summarize(worlds,p)
    assert s["status"]=="no_first_genesis_replication"
    assert s["primary_first_genesis_worlds_ge30"]==0
    assert s["all_episode_worlds_ge30"]==2
    assert s["recurrent_only_world_seeds_ge30"]==[13001,13002]


def test_two_distinct_new_first_seeds_meet_confirmatory_gate():
    p,worlds=sample()
    worlds[0]["result"]["episodes"]=[episode(29,first=True),episode(150,first=False)]
    worlds[1]["result"]["episodes"]=[episode(30,first=True)]
    worlds[2]["result"]["episodes"]=[episode(282,first=True,censored=True)]
    s=summarize(worlds,p)
    assert s["status"]=="replicated_first_genesis_native_geometric_confinement_only"
    assert s["primary_qualifying_first_genesis_seeds"]==[13002,13003]
    assert s["primary_first_genesis_worlds_ge30"]==2
    assert s["all_episode_worlds_ge30"]==3
    assert s["prespecified_cutoff_breakdown"]["worlds_first_ge_250"]==1
    assert s["counts"]["right_censored"]==1


def test_passive_short_native_world_exact_bare_replay():
    natural=natural_protocol()
    a=create_natural(13001,"enriched",natural)
    r=study_world(a,steps=3)
    b={"seed":13001,"density":"enriched","result":r}
    check=replay(b,natural,3)
    assert check["full_hash"]==r["final"]["hash"]
    assert check["rng"]==r["final"]["rng"]
