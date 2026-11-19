"""M8.1b single-new-law regressions, independent source controls and ledger."""
from collections import Counter

from alife_m8.sandbox import LAW_VERSION, WorldM8
from alife_m8.hopping_v1 import (
    WorldM81b, HOP_LAW_VERSION, HOP_COST, P_HOP_ATTEMPT
)
from tools.m8_1a_native_origin import run_world as frozen_m81a_world
from tools.m8_1b_campaign import (
    SEEDS, TICKS, MODES, protocol, initial_world,
    run_world, intact_native_source, free_four_corridor,
)


def test_m81b_frozen_protocol_and_original_law_unchanged():
    p = protocol()
    assert p["physics"]["inherited_law"] == LAW_VERSION
    assert p["physics"]["new_law_version"] == HOP_LAW_VERSION
    assert P_HOP_ATTEMPT == 0.25 and HOP_COST == 1
    assert p["frozen_experiment"]["total_physical_worlds"] == 256
    assert (SEEDS.start, SEEDS.stop - 1) == (620001, 620064)
    assert TICKS == 240 and len(MODES) == 4
    assert p["frozen_gates"]["corridor_effect"].startswith("At least 8/64")
    assert p["frozen_gates"]["informative_product"].startswith("At least 3/64")


def test_m81b_all_initial_material_unbound_paired_and_exactly_conserved():
    for seed in (620001, 620032, 620064):
        start = [initial_world(seed, arm) for arm in MODES]
        assert [initial for _, initial in start] == [start[0][1]] * 4
        for w, initial in start:
            assert len(initial) == 20
            assert Counter(p["species"] for p in initial) == {0:10, 1:10}
            assert len(w.particles) == 20 and not w.B and not w.H
            assert w.initial_matter == 80 and w.initial_energy == 500
            assert w.bath == {0:30, 1:30}
            w.check()


def test_m81b_all_hop_events_are_orthogonal_single_step_mass_and_energy_paid():
    w, _ = initial_world(620001, "hop_no_template")
    initial_positions = {i:(p.x,p.y) for i,p in w.particles.items()}
    for _ in range(35):
        old_len = len(w.events)
        w.step()
        for e in w.events[old_len:]:
            if e["kind"] == "hop":
                assert abs(e["from_x"]-e["to_x"]) + abs(e["from_y"]-e["to_y"]) == 1
                assert e["energy_cost"] == 1
                assert e["material_id"] in w.particles
                assert 0 <= e["to_x"] < 10 and 0 <= e["to_y"] < 5
        w.check()
    moves = [x for x in w.events if x["kind"] == "hop"]
    assert len(moves) > 0
    assert len(w.particles) == 20
    assert all(p.id in initial_positions for p in w.particles.values())
    assert all(p.species in (0,1) for p in w.particles.values())
    assert w.initial_energy == w.free_energy + w.dissipated + sum(w.B.values()) + sum(w.H.values())


def test_static_arm_matches_original_m81a_engine_on_new_seed_at_200_ticks():
    m8 = frozen_m81a_world(620001, "templated", ticks=200)
    control = run_world(620001, "static_templated", ticks=200)
    assert m8["first_source"] == control["first_source"]
    assert m8["all_native_physical_events"] == control["all_real_native_events"]
    assert m8["final_state"] == control["final_physical_metrics"]
    assert control["native_event_counts"].get("hop", 0) == 0


def test_hop_world_native_events_are_deterministically_reproducible():
    a = run_world(620003, "hop_templated", ticks=20)
    b = run_world(620003, "hop_templated", ticks=20)
    assert a == b
    assert a["full_physical_ledger_passed_every_tick"]
    assert a["law"] == HOP_LAW_VERSION


def test_free_corridor_requires_live_parent_and_never_manufactures_source():
    w, original = initial_world(620004, "hop_templated")
    assert free_four_corridor(w, None) is False
    candidate = {"x": 0, "y": 1, "material_ids":[0,1,2,3]}
    assert intact_native_source(w, candidate) is False
    assert free_four_corridor(w, candidate) is False
    assert len(original) == 20
