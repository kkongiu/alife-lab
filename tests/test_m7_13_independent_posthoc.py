"""M7.13 posthoc native physics independent intervention oracle unit tests."""
from support import make_energy_config,world_with
from tools.m7_11_ring_fault_tolerance import rings_now
from tools.m7_13_damage_history import follow
from tools.m7_13_independent_posthoc import independent_refund,physical_replay
from tools.m6_5_ring_forks import clone_world


def fixture():
    cfg=make_energy_config(width=8,height=8,seed=909,
        species=[{"name":"S0","count":4,"move_probability":0.0,"energy":6,"max_bonds":2}],
        chemistry={"enabled":True,"bond_cost":2,"formation_probability":0.0,
                   "break_probability":0.0,"allowed_pairs":[["S0","S0"]],"catalysis":[]})
    w=world_with(cfg,positions=[(0,0),(1,0),(1,1),(0,1)],
        species=[0,0,0,0],energy=[2,2,2,2],
        bonds=[(0,1,4),(0,3,4),(1,2,4),(2,3,4)])
    assert w.energy()==w.configured_energy()==24
    return w,rings_now(w)[0]


def test_replay_independent_first_damage_and_exact_particle_sham_energy():
    parent,ring=fixture()
    target=sorted(ring["edges"])[0]
    cut=clone_world(parent)
    sham=clone_world(parent)
    old_rng=(parent.rng.fingerprint(),parent.rng.draws)
    cost=independent_refund(cut,target,False)
    cost2=independent_refund(sham,target,True)
    assert cost==cost2==4
    assert cut.store.energy==sham.store.energy
    assert len(cut.store.bonds)==3 and len(sham.store.bonds)==4
    assert cut.energy()==sham.energy()==parent.energy()
    assert (cut.rng.fingerprint(),cut.rng.draws)==old_rng
    assert (sham.rng.fingerprint(),sham.rng.draws)==old_rng


def test_full_three_arm_independent_original_native_240_step_replay():
    parent,ring=fixture()
    raw=follow(parent,ring,validate=True)
    row={
        "seed":909,
        "target":None,
        "first_original_cut_ID_pair":raw["first_original_cut_ID_pair"],
        "second_original_precommitted_distinct_cut_ID_pair":raw["second_original_precommitted_distinct_cut_ID_pair"],
        "t0_intervention_energy_metadata":raw["t0_intervention_energy_metadata"],
        "arms":raw["arms"]
    }
    assert physical_replay(parent,ring,row)
    assert parent.energy()==parent.configured_energy()
