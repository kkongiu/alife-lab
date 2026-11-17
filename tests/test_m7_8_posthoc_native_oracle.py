"""Verify M7.8 posthoc ORIGINAL M6 form_bonds pair-keyed oracle is faithful."""
from support import make_energy_config,world_with
from alife import chemistry
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_8_frozen_reactions import formation_only_pair_keyed
from tools.m7_8_posthoc_native_oracle import native_m6_original_form_bonds_with_coupled_oracle


def fixture():
    cfg=make_energy_config(
        width=8,height=8,seed=777,
        species=[{"name":"S0","count":3,"move_probability":0,"energy":6,"max_bonds":2}],
        chemistry={"enabled":True,"bond_cost":2,"formation_probability":1,
                   "break_probability":0,"allowed_pairs":[["S0","S0"]],"catalysis":[]}
    )
    w=world_with(cfg,positions=[(0,0),(1,0),(2,0)],
                 species=[0,0,0],energy=[10,1,3],bonds=[(0,1,4)])
    w.check()
    return w


def test_original_m6_formation_oracle_matches_counterfactual_and_restores_module():
    root=fixture()
    energy_transfer(root,"bond_only")
    oldcand=chemistry._candidate_pairs
    for salt in range(6):
        a=clone_world(root)
        b=clone_world(root)
        outcome=formation_only_pair_keyed(a,(0,1),26001,salt)
        before=b.rng
        native,draws=native_m6_original_form_bonds_with_coupled_oracle(b,26001,salt)
        assert chemistry._candidate_pairs is oldcand
        assert b.rng is before
        assert draws==outcome["native_pairs_attempted"]
        assert b.state_hash_full()==a.state_hash_full()
        assert b.bonds_formed_total==a.bonds_formed_total
        assert b.dissipated==a.dissipated
        assert [[min(e.id_a,e.id_b),max(e.id_a,e.id_b)] for e in native]==outcome["formed_all_pair_ids"]
