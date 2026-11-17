"""Independent M7.11 observer and native M7.3 transport audit tests."""
from support import make_energy_config,world_with
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_11_independent_posthoc import (
    exact_simple_components,erase_bond_and_return_energy,
    own_snapshot_transfer,root_induced_connected
)
from tools.m7_11_ring_fault_tolerance import (
    rings_now,excise_refund
)


def square():
    cfg=make_energy_config(
        width=8,height=8,seed=812,
        species=[{"name":"S0","count":4,"move_probability":0.0,"energy":6,"max_bonds":2}],
        chemistry={"enabled":True,"bond_cost":2,
                   "formation_probability":0.0,"break_probability":0.0,
                   "allowed_pairs":[["S0","S0"]],"catalysis":[]}
    )
    w=world_with(cfg,positions=[(0,0),(1,0),(1,1),(0,1)],
                 species=[0]*4,energy=[2,2,2,2],
                 bonds=[(0,1,4),(1,2,4),(2,3,4),(0,3,4)])
    assert w.energy()==w.configured_energy()==24
    return w


def test_own_exact_native_ring_component_is_independent_equivalent():
    w=square()
    independent=exact_simple_components(w)
    prereg=rings_now(w)
    assert len(independent)==len(prereg)==1
    for key in ("ids","edges","size","exact"):
        assert independent[0][key]==prereg[0][key]
    assert root_induced_connected(w,(0,1,2,3))


def test_original_native_thermal_gradient_reproduced_when_all_edges_enabled():
    w=square()
    original=clone_world(w)
    replica=clone_world(w)
    cut=(0,1)
    a=excise_refund(original,cut)
    stored=erase_bond_and_return_energy(replica,cut)
    assert stored==a["native_bond_energy_fully_refunded"]==4
    assert replica.state_hash_full()==original.state_hash_full()
    assert root_induced_connected(replica,(0,1,2,3))
    official=clone_world(replica)
    transfers=energy_transfer(official,"bond_only")
    assert own_snapshot_transfer(replica,set())==transfers[0]
    assert official.state_hash_full()==replica.state_hash_full()
    held=clone_world(original)
    assert own_snapshot_transfer(held,set(exact_simple_components(w)[0]["edges"])-{cut})==0
    assert held.state_hash_full()!=official.state_hash_full()
    assert held.energy()==official.energy()==w.energy()
