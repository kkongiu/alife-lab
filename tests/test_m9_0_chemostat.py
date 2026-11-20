"""Scientific sanity checks M9.0; include full unchanged historical M6 tests."""
from collections import Counter

from alife_m9.chemostat import (
    Chemostat, LAW, catalyst_map, directed_cycle, SPECIES, DIMERS,
    FEED_EACH_MONOMER, ENERGY_FEED, ENERGY_POOL_CAP,
    P_WASHOUT, P_HYDROLYSIS, P_LIGATION_BACKGROUND,
    P_LIGATION_CATALYZED
)
from tools.m9_0_campaign import protocol, execute_world, summarize, SEEDS, TICKS


def test_m90_protocol_is_preregistered_before_implementation():
    p = protocol()
    assert p["fixed_campaign"]["total_worlds"] == 312
    assert p["fixed_campaign"]["switch_off_after_tick"] == 150
    assert p["positive_control"]["network"].startswith("AA autocatalyzes")
    assert p["unseeded_exploration"]["chemistry_maps"].startswith("Fixed 12")
    assert len(SEEDS) == 8 and TICKS == 300


def test_m90_positive_fixture_is_explicit_only_random_chemistries_start_empty():
    pos = Chemostat(730001, catalyst_map("positive"), "on", seeded_positive=True)
    assert pos.counts["AA"] == 1
    assert pos.initial_matter == 2 and pos.initial_energy == 1
    for i in range(12):
        w = Chemostat(730001, catalyst_map(i), "on")
        assert w.initial_matter == w.initial_energy == 0
        assert w.internal_atoms() == 0 and w.bond_energy() == 0
        assert w.catalysts == catalyst_map(i)
        assert set(w.catalysts) == set(DIMERS)
        assert all(v is None or v in DIMERS for v in w.catalysts.values())


def test_m90_open_chemostat_exact_mass_and_energy_each_tick_and_no_negative_populations():
    for chem in ("positive", 0, 5, 11):
        for mode in ("on", "off", "switch_off"):
            w = Chemostat(730001, catalyst_map(chem), mode,
                          seeded_positive=(chem == "positive"))
            for t in range(1, 61):
                state = w.step()
                assert state["tick"] == t
                assert state["atoms_inside"] + state["atoms_out"] == (
                    w.initial_matter + 6*t
                )
                assert state["energy_pool"] + state["energy_bonds_inside"] + (
                    state["energy_bonds_out"] + state["energy_dissipated"]
                ) == w.initial_energy + 8*t
                assert 0 <= state["energy_pool"] <= ENERGY_POOL_CAP
                assert all(v >= 0 for v in state["counts"].values())


def test_m90_catalysis_keeps_catalyst_not_consumed_directly():
    w = Chemostat(730003, catalyst_map("positive"), "on", seeded_positive=True)
    w.free_energy = 8
    w.total_energy_fed = 8
    # Apply only the one native synthesis stage to probe stoichiometry,
    # leaving the fixed positive AA catalyst itself untouched by reactants.
    w.counts["A"] = 4
    w.total_atoms_fed += 4
    original_AA = w.counts["AA"]
    w._ligations()
    w.check()
    assert w.counts["AA"] >= original_AA
    assert w.counts["A"] + 2*w.counts["AA"] == 4 + 2*original_AA


def test_m90_unseeded_network_map_and_cycle_detector_are_deterministic():
    assert catalyst_map("positive") == {
        "AA": "AA", "AB": None, "BA": None, "BB": None
    }
    assert directed_cycle(catalyst_map("positive")) is True
    assert catalyst_map(0) == catalyst_map(0)
    assert catalyst_map(0) != catalyst_map(1)
    assert directed_cycle({"AA": None, "AB": None, "BA": None, "BB": None}) is False
    assert directed_cycle({"AA": "AA", "AB": None, "BA": None, "BB": None}) is True
    assert directed_cycle({"AA": "AB", "AB": "AA", "BA": None, "BB": None}) is True


def test_m90_mode_off_has_no_catalyzed_ligations_and_switch_off_has_none_after_150():
    w = Chemostat(730003, catalyst_map("positive"), "switch_off", seeded_positive=True)
    for _ in range(170):
        w.step()
    assert all(e["tick"] <= 150 for e in w.events
               if e["kind"] == "ligation" and e["catalytic_channel_used"])


def test_m90_world_replay_is_exactly_deterministic_and_modes_paired():
    a = execute_world(730001, 0, "on")
    b = execute_world(730001, 0, "on")
    c = execute_world(730001, 0, "off")
    assert a == b
    assert a["initial"] == c["initial"]
    assert a["explicitly_seeded_positive_fixture"] is False
    assert a["exact_atom_and_energy_ledgers_all_steps"]
    assert c["catalyst_used_ligations"] == 0
