"""M7.2 passive energy transfer, source spatial geometry and frozen seed gates."""
from alife.config import Config
from alife.world import World
from support import world_with
from tools.m7_1_energy_factorial import make_config as old_m71_make_config
from tools.m7_2_energy_distribution import (
    ARMS, bare_replay, config_for, contacts, diffuse_contact_energy,
    gini_nonnegative, ledger, paired_summary, protocol, run_world,
)


def fixture(energy=4, neighbors=((1,0),(0,1)), origin=(0,0)):
    """Tiny original World energy fixture with persistent IDs and zero bonds."""
    species=[
        {"name":"HIGH","count":1,"move_probability":0.0,
         "energy":energy,"max_bonds":0},
        {"name":"LOW","count":len(neighbors),"move_probability":0.0,
         "energy":0,"max_bonds":0},
    ]
    c=Config.from_dict({
        "schema_version":3,"seed":7121,
        "grid":{"width":24,"height":24,"boundary":"periodic"},
        "neighborhood":"von_neumann","placement":"random_uniform",
        "species":species,
        "metrics":{"every":50},
        "chemistry":{"enabled":False},
        "energy":{"movement_cost":1},
    }).validate()
    pos=[origin]+list(neighbors)
    return world_with(c,pos,[0]+[1]*len(neighbors))


def test_frozen_protocol_complete_sample_and_budget():
    p=protocol()
    assert p["design"]["seed_first"]==19001
    assert p["design"]["seed_last"]==19080
    assert p["design"]["paired_worlds"]==320
    assert p["controlled_energy"]["total_generated_per_world"]==19200
    assert p["integrity"]["no_src_changes"] is True
    assert p["integrity"]["master_unmodified"] is True
    assert [s for shard in p["design"]["shards"]
            for s in range(shard["start"],shard["end"]+1)]==list(range(19001,19081))
    assert set(ARMS)==set(p["design"]["arm_labels"])


def test_source_configurations_and_no_transfer_are_unchanged_M7_1():
    a=config_for(19001,"dispersed_no_transfer")
    original=old_m71_make_config(19001,"driven_no_catalysis")
    assert a.canonical_json()==original.canonical_json()
    assert a.hash()==original.hash()
    b=config_for(19001,"clustered_no_transfer")
    c=config_for(19001,"clustered_contact_transfer")
    assert b.canonical_json()==c.canonical_json()
    assert set((s.x,s.y) for s in a.energy.sources)=={
        (x,y) for x in (2,8,14,20) for y in (2,8,14,20)
    }
    assert set((s.x,s.y) for s in b.energy.sources)=={
        (x,y) for x in (10,11,12,13) for y in (10,11,12,13)
    }
    assert len(a.energy.sources)==len(b.energy.sources)==16
    assert all(s.rate_num==2 and s.rate_den==1 and s.capacity==12 for s in b.energy.sources)
    assert sum(s.rate_num for s in b.energy.sources)==32


def test_identical_initial_state_four_arm():
    worlds=[World.create(config_for(19001,arm)) for arm in ARMS]
    start=[
        (tuple(w.store.ids),tuple(w.store.xs),tuple(w.store.ys),
         tuple(w.store.species),tuple(w.store.energy),
         w.rng.fingerprint(),w.rng.draws)
        for w in worlds
    ]
    assert len(set(start))==1
    assert all(not w.store.bonds for w in worlds)


def test_contact_transfer_two_neighbors_conserves_energy_and_rng():
    w=fixture(energy=4)
    oldhash=w.state_hash_full()
    erng=w.rng.fingerprint()
    draws=w.rng.draws
    total=w.energy()
    assert len(contacts(w.store))==2
    moved=diffuse_contact_energy(w)
    assert moved==(2,2)
    assert w.store.energy==[2,1,1]
    assert w.energy()==total
    assert w.rng.fingerprint()==erng and w.rng.draws==draws
    assert w.state_hash_full()!=oldhash
    w.check()


def test_torus_neighbor_contact_and_donor_exhaustion():
    w=fixture(energy=2,neighbors=((23,0),(1,0),(0,1)),origin=(0,0))
    assert len(contacts(w.store))==3
    assert diffuse_contact_energy(w)==(2,2)
    assert w.store.energy[0]==0
    assert sum(w.store.energy)==2
    assert sorted(w.store.energy[1:])==[0,1,1]
    w.check()


def test_no_contact_and_zero_energy_no_transfer():
    w=fixture(energy=0,neighbors=((12,12),))
    assert contacts(w.store)==[]
    assert diffuse_contact_energy(w)==(0,0)
    assert w.store.energy==[0,0]
    w.check()


def test_gini_corner_cases():
    assert gini_nonnegative([])==0.0
    assert gini_nonnegative([0,0,0])==0.0
    assert gini_nonnegative([2,2,2])==0.0
    assert gini_nonnegative([0,4])==0.5


def test_actual_600_tick_energy_ledger_and_bare_replay():
    p=protocol()
    rec=run_world(19001,"clustered_contact_transfer",p)
    assert rec["final"]["injected"]==19200
    assert rec["final"]["contact_transfers"]>0
    assert len(rec["checkpoints"])==6
    assert all(row["energy_ledger_pass"] for row in rec["checkpoints"])
    assert rec["final"]["energy_stored"]+rec["final"]["dissipated"]+rec["final"]["unabsorbed"]==rec["initial"]["energy"]+19200
    assert bare_replay(rec,p)["full_hash_and_rng_equal"] is True


def fake_record(seed,arm,overflow,zeros,moves,bonds=1):
    return {
        "seed":seed,"arm":arm,
        "initial":{
            "ids_positions_species_energy_sha256":str(seed)+"s",
            "rng_fingerprint":str(seed)+"r","rng_draws":264,
            "energy":2000
        },
        "checkpoints":[{
            "particle_energy_gini":0.5,
            "zero_energy_particles":zeros,
            "free_mobile_energy_eligible":10,
        }],
        "late_501_600":{"moves":moves,"new_bonds":bonds},
        "final":{
            "injected":19200,"unabsorbed":overflow,"energy_stored":4000,
            "contact_transfers":4 if "contact_transfer" in arm else 0
        },
        "native_final_topology":{"native_simple_ring_components":0}
    }


def test_paired_gates_frozen_thresholds_exact():
    p=protocol()
    worlds=[]
    for seed in range(19001,19081):
        first=seed<=19060
        transfer_good=seed<=19050
        movement_good=seed<=19048
        values={
            "dispersed_no_transfer":(600 if first else 900,100,20 if movement_good else 10),
            "clustered_no_transfer":(900 if first else 600,100,10 if movement_good else 20),
            "dispersed_contact_transfer":(600,80 if transfer_good else 120,
                                          30 if movement_good else 5),
            "clustered_contact_transfer":(900,105,15)
        }
        for arm,(overflow,zeros,moves) in values.items():
            worlds.append(fake_record(seed,arm,overflow,zeros,moves))
    s=paired_summary(worlds,p)
    assert s["preregistered_decisions"]["source_distribution"]=="passed"
    assert s["preregistered_decisions"]["passive_local_transport"]=="passed"
    assert s["contrasts"]["source_no_transfer"]["by_metric"]["overflow"]["a_lower"]==60
    assert s["contrasts"]["transport_dispersed"]["by_metric"]["zero_energy_particles"]["a_lower"]==50
    assert s["contrasts"]["transport_dispersed"]["by_metric"]["late_moves"]["a_greater"]==48
