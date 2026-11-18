"""M8.1a integrity and observer controls. No output-dependent seed selection."""
from collections import Counter

from alife_m8.sandbox import LAW_VERSION
from tools.m8_1a_native_origin import (
    initial_feedstock, initial_world, native_daughters,
    first_native_source, protocol, run_world,
)


def test_m81a_protocol_frozen_before_code_and_exact_existing_m8_physics():
    p = protocol()
    assert p["physics"]["law"] == LAW_VERSION
    assert p["physics"]["background_adsorption"] == 0
    assert p["frozen_campaign"]["total_worlds"] == 192
    assert p["frozen_campaign"]["seeds"] == {
        "start": 610001, "end_inclusive": 610064, "count": 64
    }
    assert p["frozen_campaign"]["ticks_per_world"] == 200
    assert p["frozen_decision"]["origin_go"].startswith("At least 12")
    assert p["frozen_decision"]["informational_go"].startswith("At least 4")


def test_m81a_unbound_feedstock_exact_mass_energy_and_no_manufactured_B_H():
    for seed in (610001, 610002, 610003):
        w, initial = initial_world(seed, "templated")
        assert w.initial_template_material_ids == ()
        assert w.tick == 0
        assert len(initial) == len(w.particles) == 20
        assert not w.B and not w.H
        assert Counter(i["species"] for i in initial) == {0: 10, 1: 10}
        assert w.bath == {0: 30, 1: 30}
        assert w.initial_matter == 80 and w.initial_energy == 500
        assert len({(i["x"], i["y"]) for i in initial}) == 20
        w.check()


def test_m81a_identical_start_across_three_controls_independent_of_mode():
    for seed in (610001, 610032, 610064):
        initial = initial_feedstock(seed)
        assert initial == initial_feedstock(seed)
        assert len(initial) == 20
        starts = [initial_world(seed, mode)[1] for mode in (
            "templated", "shuffled_identity", "no_template"
        )]
        assert starts == [starts[0]] * 3
    assert initial_feedstock(610001) != initial_feedstock(610002)


def test_m81a_no_template_never_adsorbs_without_background_even_with_initial_monomers():
    result = run_world(610001, "no_template", ticks=15)
    assert result["integrity_passed"]
    assert result["initial_state"]["initial_B_count"] == 0
    assert result["initial_state"]["initial_H_count"] == 0
    assert result["event_counts"].get("adsorb", 0) == 0
    assert result["first_persistent_material_product"] is None
    assert result["first_persistent_informative_product"] is None
    assert result["final_state"]["exact_mass_and_energy_invariants"]


def test_m81a_replayed_worlds_are_deterministic_and_event_provenance_is_real():
    a = run_world(610002, "templated", ticks=20)
    b = run_world(610002, "templated", ticks=20)
    assert a == b
    assert a["initial_state"]["matter_total"] == 80
    assert a["initial_state"]["energy_total"] == 500
    assert all(e["kind"] in {"adsorb", "B_form", "B_break", "H_release"}
               for e in a["all_native_physical_events"])


def test_m81a_detector_never_confuses_unbonded_material_with_origin_or_product():
    w, initial = initial_world(610003, "templated")
    ids = {p["material_id"] for p in initial}
    assert first_native_source(w, ids, set()) is None
    assert native_daughters(w, {
        "tick": 0, "x": 0, "y": 1,
        "material_ids": [0, 1, 2, 3], "sequence": "0101"
    }, ids, {}) == []
