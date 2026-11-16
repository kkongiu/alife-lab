"""M6.13 preregistration, independent seed-level adjudication and bare replay."""
from tools.m6_13_replication import (
    is_long_episode, protocol, replay, summarize, wilson,
)
from tools.m6_4_cycles import create_natural, protocol as natural_protocol
from tools.m6_12_precursors import study_world


def empty_world(seed, density):
    return {
        "seed":seed,"density":density,
        "result":{"episodes":[],"counts":{},"strata":{}}
    }


def episode(duration, first=True, mobile=True, censored=False):
    return {
        "resident_mobile":mobile, "duration_ticks":duration,
        "first_of_material_set":first, "right_censored":censored,
        "start_tick":200, "center":[3,3], "resident_id":77,
        "first_closure_tick":None, "ended_by":"end_of_run" if censored else "original_edge_broken",
        "closure_observed":False, "stratum":"free_mobile" if mobile else "empty"
    }


def sample():
    p=protocol()
    all_worlds=[]
    for density in p["sample"]["densities"]:
        for seed in range(p["sample"]["seeds"]["start"],
                          p["sample"]["seeds"]["end_inclusive"]+1):
            all_worlds.append(empty_world(seed,density))
    assert len(all_worlds)==800
    return p, all_worlds


def test_preregistration_fixed_shards_and_scope():
    p=protocol()
    assert p["sample"]["worlds"]==800
    assert p["sample"]["seeds"]["count"]==400
    assert p["preregistered_primary"]["no_posthoc_threshold_change"] is True
    assert p["integrity"]["no_src_changes"] is True
    shards=p["sample"]["frozen_shards"]
    pieces={(shard["density"],seed) for shard in shards
            for seed in range(shard["start"],shard["end"]+1)}
    assert len(pieces)==800
    assert pieces=={(density,seed) for density in p["sample"]["densities"]
                   for seed in range(12001,12401)}


def test_30tick_boundary_and_right_censoring():
    assert not is_long_episode(episode(29))
    assert is_long_episode(episode(30))
    assert is_long_episode(episode(30,censored=True))
    assert not is_long_episode(episode(500,mobile=False))
    ci=wilson(0,400)
    assert ci["low"]==0
    assert 0<ci["high"]<0.02
    assert wilson(400,400)["high"]==1
    assert wilson(0,0) is None


def test_same_seed_two_densities_counts_once_not_replication():
    p,worlds=sample()
    for w in worlds:
        if w["seed"]==12031:
            w["result"]["episodes"]=[episode(100)]
    summary=summarize(worlds,p)
    assert summary["primary_distinct_seeds_ge_30"]==1
    assert summary["decision"]=="single_not_independently_replicated"
    assert summary["first_material_distinct_seeds_ge_30"]==1
    assert summary["by_density"]["baseline"]["worlds_with_ge_30"]==1
    assert summary["by_density"]["enriched"]["worlds_with_ge_30"]==1


def test_distinct_seed_replication_and_first_material_sensitivity():
    p,worlds=sample()
    for w in worlds:
        if w["density"]=="baseline" and w["seed"]==12031:
            w["result"]["episodes"]=[episode(30,first=True,censored=True)]
        if w["density"]=="enriched" and w["seed"]==12044:
            w["result"]["episodes"]=[episode(282,first=False)]
    summary=summarize(worlds,p)
    assert summary["primary_distinct_seeds_ge_30"]==2
    assert summary["primary_qualifying_seeds"]==[12031,12044]
    assert summary["decision"]=="replicated_30tick_native_geometric_confinement_only"
    assert summary["first_material_distinct_seeds_ge_30"]==1
    assert summary["by_density"]["baseline"]["ge_30_right_censored_episodes"]==1
    assert summary["by_density"]["enriched"]["predefined_duration_thresholds"]["episodes_ge_250"]==1
    assert summary["by_density"]["enriched"]["predefined_duration_thresholds"].get("episodes_ge_500",0)==0


def test_small_bare_replay_of_unchanged_m6_observer():
    p=natural_protocol()
    original=create_natural(12001,"baseline",p)
    record=study_world(original,steps=3)
    w={"density":"baseline","seed":12001,"result":record}
    # replay() intentionally runs the specified short horizon, preserving original state.
    r=replay(w,p,3)
    assert r["full_hash"]==record["final"]["hash"]
