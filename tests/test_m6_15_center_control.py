"""M6.15: pre-registered matched causal position intervention sanity checks."""
from collections import Counter

from support import make_energy_config, world_with
from tools.m6_12_precursors import precursor_candidates
from tools.m6_15_center_control import (
    HORIZONS, choose_remote_move, follow_pair, isolated_neighbors,
    protocol, relocate, summarize, torus_distance,
)


OFFSETS=((-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0))


def seven_path(occupied):
    cfg=make_energy_config(
        width=24,height=24,seed=715,
        species=[
            {"name":"S0","count":8,"move_probability":0.0,
             "energy":20,"max_bonds":2},
            {"name":"S3","count":1,"move_probability":0.6,
             "energy":8,"max_bonds":0},
        ],
        chemistry={
            "enabled":True,"bond_cost":2,"formation_probability":0.0,
            "break_probability":0.0,
            "allowed_pairs":[["S0","S0"]],"catalysis":[]
        }
    )
    coords=[((3+dx)%24,(3+dy)%24) for dx,dy in OFFSETS]
    coords.append((3,3) if occupied else (12,12))
    energies=[20]+[16]*7+[8]
    bonds=[(i,i+1,4) for i in range(7)]
    world=world_with(
        cfg,coords,[0]*8+[1],energy=energies,bonds=bonds
    )
    world.check()
    assert world.energy()==world.configured_energy()
    return world


def test_protocol_frozen_sample():
    p=protocol()
    assert p["sample"]["seed_start"]==15001
    assert p["sample"]["seed_end_inclusive"]==16000
    assert p["sample"]["seeds"]==1000
    assert p["integrity"]["no_changes_to_master"] is True
    assert p["sample"]["max_forks_per_world"]==1
    assert len(HORIZONS)==4 and HORIZONS[-1]==120
    observed=[i for shard in p["sample"]["shards"]
              for i in range(shard["start"],shard["end"]+1)]
    assert observed==list(range(15001,16001))


def test_remote_distance_and_torus():
    assert torus_distance((0,0),(23,0),24,24)==1
    assert torus_distance((0,0),(12,12),24,24)==24
    assert torus_distance((5,5),(10,6),24,24)==6


def test_empty_source_isolated_donor_to_center_without_energy_edit():
    w=seven_path(occupied=False)
    (cand,)=precursor_candidates(w)
    assert cand["stratum"]=="empty"
    choice=choose_remote_move(w,cand)
    assert choice["source_center_state"]=="natural_empty"
    assert choice["particle_id"]==8
    assert choice["destination"]==[3,3]
    assert isolated_neighbors(w.store,12,12)
    hash_before=w.state_hash_full()
    r=follow_pair(w,cand,choice,horizon=120,sham=True)
    assert w.state_hash_full()==hash_before
    assert r["same_first_step_source_breaks"] is True
    assert r["outcomes"]["center_empty"]["source_original_seven_edges_survive_120"]
    assert r["outcomes"]["center_occupied"]["source_original_seven_edges_survive_120"]
    assert all(
        r["outcomes"][arm]["initial_next_step_original_edge_breaks"]==[]
        for arm in ("center_occupied","center_empty")
    )


def test_occupied_source_remote_empty_isolated_and_sham_replay():
    w=seven_path(occupied=True)
    (cand,)=precursor_candidates(w)
    assert cand["stratum"]=="free_mobile"
    choice=choose_remote_move(w,cand)
    assert choice["source_center_state"]=="natural_occupied"
    assert choice["particle_id"]==8
    assert choice["original_position"]==[3,3]
    assert torus_distance(tuple(choice["destination"]), (3,3),24,24)>=7
    h=w.state_hash_full()
    r=follow_pair(w,cand,choice,horizon=120,sham=True)
    assert w.state_hash_full()==h
    assert r["same_first_step_source_breaks"]
    assert r["outcomes"]["center_occupied"]["source_original_seven_edges_survive_120"]
    assert r["outcomes"]["center_empty"]["source_original_seven_edges_survive_120"]


def test_relocation_checks_energy_species_rng_and_particle_counts():
    w=seven_path(occupied=True)
    initial=w.energy()
    signature=w.rng.fingerprint()
    original=Counter(w.store.species)
    old=relocate(w,8,(12,12))
    assert old==(3,3)
    assert w.energy()==initial
    assert w.rng.fingerprint()==signature
    assert Counter(w.store.species)==original
    assert w.store.grid[3*24+3]==-1
    assert w.store.grid[12*24+12]==8


def test_empty_selection_summary_and_no_unsupported_conclusions():
    p=protocol()
    rows=[
        {"seed":seed,"eligible":False,"reason":"no_native_seven_edge_precursor"}
        for seed in range(15001,16001)
    ]
    out=summarize(rows,p)
    assert out["paired_source_worlds"]==0
    assert out["decision"]=="no_selected_pairs"
    assert out["direct_one_step_edge_break_invariant"]=="passed"
    assert out["source_state_subcohorts"]["all"]["horizon_120"]["paired_occupied_minus_empty_survival"] is None


def test_paired_medium_term_discordance_from_independent_seed_is_measured_not_overclaimed():
    p=protocol()
    rows=[
        {"seed":seed,"eligible":False,"reason":"no_native_seven_edge_precursor"}
        for seed in range(15001,16001)
    ]
    outcomes={}
    for key,loss in (("center_empty",9),("center_occupied",None)):
        outcomes[key]={
            f"source_original_seven_edges_survive_{h}":loss is None or loss>h
            for h in HORIZONS
        }
    rows[0]={
        "seed":15001,"eligible":True,
        "pair":{
            "source_natural_center_state":"natural_empty",
            "first_rng_divergence_tick":1,
            "same_first_step_source_breaks":True,
            "outcomes":outcomes
        }
    }
    summary=summarize(rows,p)
    assert summary["paired_source_worlds"]==1
    assert summary["source_state_subcohorts"]["all"]["horizon_30"]["discordant_occupied_only"]==1
    assert summary["source_state_subcohorts"]["all"]["horizon_30"]["paired_occupied_minus_empty_survival"]==1.0
    assert summary["source_state_subcohorts"]["natural_occupied"]["pairs"]==0
