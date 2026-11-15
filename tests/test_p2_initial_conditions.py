"""P2: unit tests for initial-condition controls and deterministic sham selection."""
import json

from alife.config import Config
from alife.world import World
from tools.p2_initial_conditions import (
    PROTOCOL, choose_shams, duplicate_world, readout, translate_initial_group,
)
from support import make_energy_config, world_with


def _setup(obstacle=False):
    cfg = make_energy_config(
        width=8, height=8,
        species=[{"name":"S0", "count":5 if obstacle else 4,
                  "move_probability":0.0,"energy":10,"max_bonds":2}],
        chemistry={"enabled":True,"bond_cost":0,"formation_probability":0.0,
                   "break_probability":0.0,
                   "allowed_pairs":[["S0","S0"]],"catalysis":[]},
    )
    coords=[(0,0),(1,0),(2,0),(3,0)]
    if obstacle: coords.append((1,1))
    return world_with(cfg,coords,[0]*len(coords))


def test_clone_remains_independent_and_replays_identically():
    original=_setup()
    replica=duplicate_world(original)
    assert replica is not original and replica.store is not original.store
    assert replica.state_hash_full()==original.state_hash_full()
    replica.advance(4); original.advance(4)
    assert replica.state_hash_full()==original.state_hash_full()
    assert replica.rng.state()==original.rng.state()


def test_t0_relocation_preserves_energy_rng_and_bonds():
    original=_setup()
    replica=duplicate_world(original)
    before=(original.state_hash_full(),replica.rng.state(),
            replica.rng.draws,replica.energy())
    ok, reason=translate_initial_group(replica,(0,1,2,3),(0,2))
    assert ok and reason is None
    assert replica.state_hash_full()!=before[0]
    assert original.state_hash_full()==before[0]
    assert replica.rng.state()==before[1]
    assert replica.rng.draws==before[2]
    assert replica.energy()==before[3]
    assert replica.store.bond_records()==[]
    replica.check()


def test_collision_is_invalid_without_modifying_clone():
    w=_setup(obstacle=True)
    before=(w.state_hash_full(),w.rng.fingerprint())
    assert translate_initial_group(w,(0,1,2,3),(0,1))==(False,"occupied_target")
    assert (w.state_hash_full(),w.rng.fingerprint())==before
    w.check()


def test_shams_are_disjoint_composition_and_reproducible():
    config=Config.from_dict({
        "schema_version":3,"seed":6101,
        "grid":{"width":16,"height":16,"boundary":"periodic"},
        "neighborhood":"von_neumann","placement":"random_uniform",
        "species":[{"name":"S0","count":36,"move_probability":0.5,
                    "energy":12,"max_bonds":2}],
        "chemistry":{"enabled":True,"bond_cost":2,
                     "formation_probability":0.05,"break_probability":0.002,
                     "allowed_pairs":[["S0","S0"]],"catalysis":[]},
        "energy":{},"metrics":{"every":5},
    }).validate()
    w=World.create(config)
    selected=(0,1,2,3); seeds=(4,5)
    first=choose_shams(w,selected,seeds)
    second=choose_shams(World.create(config),selected,seeds)
    assert first==second
    all_ids=set(first[0]+first[1])
    assert len(all_ids)==8
    assert all_ids.isdisjoint(selected+seeds)
    assert all(w.store.species[w.store.index_of(i)]==0 for i in all_ids)


def test_protocol_is_frozen_and_initial_intervention_precedes_history():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["status"]=="preregistered-before-execution"
    assert p["rationale"]["protocol_intervention_step"]==0
    assert p["rationale"]["first_cross_history_observed_step"]==2
    assert p["criteria"]["end_step"]==845
    assert len(p["criteria"]["shifts"])==16


def test_seed_component_exactness_is_not_equated_to_ancestry():
    w=_setup()
    w.store.add_bond(0,1,0)
    w.store.add_bond(1,2,0)
    w.store.add_bond(2,3,0)
    w.check()
    # Hypothetical parents and daughter IDs must be disjoint for this check;
    # testing only that a connected chain is not automatically a copied child.
    result=readout(w,parents=(0,1),seeds=(2,3),expected="T:(S0:(S0:(S0:(S0:))))")
    assert result["all_six"] is True
    assert result["contains_no_parent_particles"] is False
    assert result["exact_target"] is True
