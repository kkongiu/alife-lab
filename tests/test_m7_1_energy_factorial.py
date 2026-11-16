"""M7.1 factorial: source flux, movement energy, paired initial conditions, ledger."""
from copy import deepcopy

from alife.config import Config
from alife.particles import ParticleStore
from alife.rng import RNG
from alife.world import World
from tools.m7_1_energy_factorial import (
    ARMS, CHECKPOINTS, HORIZON, ledger, make_config,
    paired_summary, protocol, replay, sample_world, source_features
)


def test_frozen_protocol_and_shard_coverage():
    p=protocol()
    assert p["sample"]["seeds"]=={"start":18001,"end_inclusive":18080,"count":80}
    assert p["sample"]["total_worlds"]==320
    assert p["preregistered_gates"]["primary_driven_mobility"].startswith("For driven_no_catalysis")
    assert p["physical_config"]["movement_cost_all_arms"]==1
    assert p["integrity"]["no_mutation_src"] is True
    assert p["integrity"]["no_mutation_master"] is True
    parts=[seed for sh in p["sample"]["frozen_shards"]
           for seed in range(sh["start"],sh["end"]+1)]
    assert parts==list(range(18001,18081))


def test_all_four_arms_share_positions_species_energy_rng():
    rows=[World.create(make_config(18001,arm)) for arm in ARMS]
    signatures=[
        (tuple(w.store.ids),tuple(w.store.xs),tuple(w.store.ys),
         tuple(w.store.species),tuple(w.store.energy),
         w.rng.fingerprint(),w.rng.draws,w.energy())
        for w in rows
    ]
    assert len(set(signatures))==1
    assert all(not w.store.bonds for w in rows)
    assert [len(w.config.energy.sources) for w in rows]==[0,16,0,16]
    assert [len(w.config.chemistry.catalysis) for w in rows]==[0,0,1,1]
    assert all(w.movement_cost==1 for w in rows)


def test_ledger_accounting_with_driven_sources_across_checkpoints():
    w=World.create(make_config(18001,"driven_no_catalysis"))
    initial=w.configured_energy()
    assert len(w.sources)==16
    assert ledger(w,initial)["energy_ledger_verified"] is True
    for step in range(1,26):
        w.advance(1)
        assert ledger(w,initial)["energy_ledger_verified"] is True
    w.check()
    assert w.injected==25*16*2
    assert w.energy()+w.dissipated+w.unabsorbed==initial+w.injected


def test_zero_energy_free_motion_requires_input_in_new_regime():
    cfg=make_config(18001,"closed_no_catalysis").to_dict()
    for s in cfg["species"]:
        s["count"]=1 if s["name"]=="S3" else 0
        if s["name"]=="S3":
            s["energy"]=0
    cfg["chemistry"]["catalysis"]=[]
    closed=World(Config.from_dict(cfg).validate(),RNG(18001),
                 ParticleStore(24,24,[0],[2],[2],[3],[0]))
    closed.check()
    assert source_features(closed)["free_mobile_energy_eligible"]==0
    closed.advance(64)
    assert closed.moves_total==0
    assert closed.energy()==0
    cfg["energy"]["sources"]=[{
        "x":2,"y":2,"rate_num":2,"rate_den":1,"capacity":12,"overflow":"discard"
    }]
    driven=World(Config.from_dict(cfg).validate(),RNG(18001),
                 ParticleStore(24,24,[0],[2],[2],[3],[0]))
    driven.check()
    driven.advance(64)
    driven.check()
    assert driven.moves_total>0
    assert driven.injected>0
    assert driven.energy()+driven.dissipated+driven.unabsorbed==driven.injected


def test_short_complete_world_replays():
    record=sample_world(18001,"driven_no_catalysis")
    assert sorted(x["tick"] for x in record["checkpoints"])==list(CHECKPOINTS)
    assert record["final"]["injected"]==16*2*HORIZON
    bare=replay(record)
    assert bare["success"] is True
    assert bare["bare_replay_full_hash"]==record["final"]["full_hash"]
    assert record["checkpoints"][-1]["energy_ledger_verified"] is True


def synthetic_record(seed,arm,late_moves,late_bonds):
    return {
        "seed":seed,"arm":arm,
        "initial_state":{
            "positions_species_energy_sha256":"same-seed-"+str(seed),
            "rng":"same-rng-"+str(seed),"rng_draws":264,
        },
        "late_501_600":{"accepted_moves":late_moves,
                        "new_native_bonds":late_bonds},
        "early_1_100":{"accepted_moves":5,"new_native_bonds":2},
        "final":{"injected":50 if arm.startswith("driven") else 0,
                 "stored_energy":100,"moves":late_moves+5},
        "final_topology":{"native_simple_ring_components":0}
    }


def test_paired_gates_are_world_level_not_arm_level():
    p=protocol()
    worlds=[]
    for seed in range(18001,18081):
        for arm in ARMS:
            movements=10 if arm.startswith("driven") and seed<=18060 else 0
            bonds=3 if arm.startswith("driven") and seed<=18048 else 0
            worlds.append(synthetic_record(seed,arm,movements,bonds))
    summary=paired_summary(worlds,p)
    assert summary["independent_paired_numeric_seeds"]==80
    assert summary["preregistered_decisions"]["sustained_driven_mobility"]=="passed"
    assert summary["preregistered_decisions"]["late_chemical_turnover_benefit"]=="passed"
    assert summary["paired_contrasts"]["energy_no_catalysis"]["late_501_600"]["seeds_raised"]==60
    assert summary["paired_contrasts"]["energy_no_catalysis"]["late_bonds_501_600"]["seeds_raised"]==48
    worlds[0]["late_501_600"]["accepted_moves"]=100  # closed improves for first seed
    summary=paired_summary(worlds,p)
    assert summary["preregistered_decisions"]["sustained_driven_mobility"]=="not_met"
