"""M7.9 posthoc independent permutation and original native M6 oracle tests."""
from support import make_energy_config,world_with
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_8_frozen_reactions import formation_only_pair_keyed
from tools.m7_9_energy_placement import root_permute
from tools.m7_9_original_M6_oracle_audit import (
    independent_scramble,
    native_m6_original_form_bonds_with_coupled_oracle
)


def fixture():
    cfg=make_energy_config(
        width=8,height=8,seed=770,
        species=[{"name":"S0","count":3,"move_probability":0.0,
                  "energy":6,"max_bonds":2}],
        chemistry={
            "enabled":True,"bond_cost":2,"formation_probability":1.0,
            "break_probability":0.0,"allowed_pairs":[["S0","S0"]],
            "catalysis":[]
        }
    )
    w=world_with(cfg,positions=[(0,0),(1,0),(2,0)],
                 species=[0,0,0],energy=[10,1,3],bonds=[(0,1,4)])
    assert w.configured_energy()==w.energy()==18
    return w


def test_independent_hash_energy_permutation_is_exact_reconstruction():
    parent=fixture()
    candidate=clone_world(parent)
    t,b,u=energy_transfer(candidate,"bond_only")
    assert (t,b,u)==(1,1,0)
    for rank in range(4):
        original,meta=root_permute(candidate,(0,1),27001,rank)
        oracle=independent_scramble(candidate,(0,1),27001,rank)
        assert oracle.state_hash_full()==original.state_hash_full()
        assert oracle.store.energy==original.store.energy
        assert sorted(oracle.store.energy[:2])==[2,9]
        assert oracle.rng.fingerprint()==parent.rng.fingerprint()
        assert meta["rank"]==rank


def test_original_m6_native_formation_matches_M78_isolated_counterfactual():
    frozen=fixture()
    energy_transfer(frozen,"bond_only")
    for salt in (0,1,9,31):
        original=clone_world(frozen)
        test=clone_world(frozen)
        expected=formation_only_pair_keyed(test,(0,1),27001,salt)
        native,calls=native_m6_original_form_bonds_with_coupled_oracle(original,27001,salt)
        assert calls==expected["native_pairs_attempted"]
        assert original.state_hash_full()==test.state_hash_full()
        assert [[min(x.id_a,x.id_b),max(x.id_a,x.id_b)] for x in native]==expected["formed_all_pair_ids"]
