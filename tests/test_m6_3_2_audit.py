"""M6.3-2: physical and statistical gates, no engine edits."""
from copy import deepcopy

import pytest
from tools.m6_3_0_screen import make_world
from tools.m6_3_1_screen import density_protocol, protocol as previous_protocol
from tools.m6_3_2_audit import (
    audit_protocol, analyse_one, classify_loss, connected_status,
    eligible_partner_pairs, signature_of,
)


@pytest.mark.parametrize("edge_missing,attached,expected",[
    (False,True,"attachment"),
    (True,False,"original_edge_loss"),
    (True,True,"mixed"),
    (False,False,"other"),
])
def test_first_loss_net_state_classification(edge_missing,attached,expected):
    assert classify_loss(edge_missing,attached)==expected


def test_original_core_is_pure_and_exposure_is_read_only():
    p=previous_protocol()
    w=make_world(8101,"A",density_protocol(p,"baseline"))
    before=(w.state_hash_full(),w.rng.state(),w.rng.draws)
    status=connected_status(w)
    assert status["pure"]
    assert status["core_edges_retained"] and status["core_connected"]
    assert not status["core_grown"]
    assert status["direct_external_edges"]==[]
    assert status["missing_edges"]==[]
    measured=eligible_partner_pairs(w)
    assert measured["open_slots"]>=1
    assert measured["eligible_S0"]>=0
    assert measured["eligible_S1"]>=0
    assert before==(w.state_hash_full(),w.rng.state(),w.rng.draws)


def test_growth_and_break_are_distinct_net_states():
    # Never advances an artificial world as natural evidence. Only verifies
    # structural interpretation of a synthetic state via isolated fixture.
    p=previous_protocol()
    w=make_world(8101,"A",density_protocol(p,"baseline"))
    # Test status recognition by removing a bond without changing the engine.
    # This is NOT a physically valid energy transition: do not call check().
    store=w.store
    store.remove_bond(0,1)
    after=connected_status(w)
    assert not after["core_edges_retained"]
    assert not after["pure"]
    assert after["missing_edges"]==[[0,1]]


def test_short_deterministic_audit_does_not_change_original_hash():
    old=previous_protocol()
    p=deepcopy(audit_protocol())
    p["integrity"]["expected_steps"]=7
    targets={
        arm:signature_of(make_world(8101,arm,density_protocol(old,"baseline")))
        for arm in ("A","B","C")
    }
    assert len(set(targets.values()))==3
    setup=density_protocol(old,"baseline")
    first=make_world(8101,"A",setup)
    second=make_world(8101,"A",setup)
    one=analyse_one(first,p,"A",targets)
    two=analyse_one(second,p,"A",targets)
    assert one==two
    assert one["final_hash"]==first.state_hash_full()==second.state_hash_full()
    assert sum(one["ticks"].get(k,0) for k in
               ("pure_ticks","core_grown_ticks","core_missing_ticks"))==7
