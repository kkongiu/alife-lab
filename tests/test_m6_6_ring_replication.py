"""M6.6 locked independent-seed replication and no-adaptive-gate checks."""
from copy import deepcopy
from tools.m6_5_ring_forks import protocol as predecessor, summary as old_summary
from tools.m6_6_ring_replication import compatible_original, registered, secondary


def test_new_seed_protocol_before_runner():
    p=registered()
    assert p["fixed_sampling"]["seeds"]==list(range(9001,9021))
    assert not set(p["fixed_sampling"]["seeds"]) & set(predecessor()["sampling"]["seeds"])
    assert p["fixed_sampling"]["expected_worlds"]==40
    assert p["original_M65_gate_unchanged"]["keep_vs_lowest_required_absolute_difference_each_density"]==.2


def test_only_seed_dimension_changed_from_predecessor_algorithm():
    registered_p=registered()
    old=predecessor()
    new=compatible_original(registered_p)
    old["sampling"]["seeds"]=list(range(9001,9021))
    assert old==new, "No M6.5 algorithm, duration or decision gate may be changed"


def test_null_cases_are_insufficient_and_no_adaptive_positive_gate():
    p=registered()
    old=compatible_original(p)
    s=old_summary([],old)
    assert s["gate_passed"] is False
    assert s["verdict"]=="underpowered"
    sec=secondary([],p)
    for den in ("baseline","enriched"):
        assert sec[den]["fork_count"]==0
        assert all(n==0 for n in sec[den]["arm_measurements"]["keep_ring"]["isolated_at_selected_steps"].values())


def test_reclosure_secondary_has_no_impact_on_primary_gate():
    p=registered()
    fake={
        "final_isolated":True,
        "final_ring":True,
        "isolated_ticks":120,
        "first_loss_tick":None,
        "first_loss_reason":None,
        "first_ring_observed_tick":1,
        "snapshots":[
            {"step_since_fork":1,"isolated":True},
            {"step_since_fork":10,"isolated":True},
            {"step_since_fork":50,"isolated":True},
            {"step_since_fork":120,"isolated":True},
        ]
    }
    items=[{
        "density":"baseline","precursor_seed":9001,"fork_world_step":10,
        "arms":{
            "keep_ring":dict(fake),
            "open_lowest_edge":dict(fake),
            "open_opposite_edge":dict(fake)
        },
    }]
    d=secondary(items,p)
    assert d["baseline"]["arm_measurements"]["open_lowest_edge"]["rings_reclosed_by_step10"]==1
    assert d["baseline"]["arm_measurements"]["open_opposite_edge"]["rings_with_any_reclosure"]==1
    assert old_summary(items,compatible_original(p))["gate_passed"] is False
