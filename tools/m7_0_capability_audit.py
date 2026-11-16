"""M7.0 deterministic mechanism audit of existing M6 laws.

Not a spontaneous replication experiment and not a modification of model physics.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json

from alife.config import Config
from alife.particles import ParticleStore
from alife.rng import RNG
from alife.world import World
from alife.chemistry import _candidate_pairs
from tools.m6_4_cycles import create_natural, protocol as natural_protocol, M6

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m7_0_capability/protocol.json"
OUTPUT=ROOT/"campaigns/m7_0_capability/audit.json"
OFFSETS=((-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0))


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-0-capability-audit-v1"
    assert p["status"]=="frozen_before_code_and_audit"
    assert len(p["checks"])==5
    return p


def one_species_config(name,number,energy=None,grid=8,seed=777):
    """Change only sampled species counts and optional INITIAL energy."""
    d=json.loads(M6.read_text(encoding="utf-8"))
    d["grid"]={"width":grid,"height":grid,"boundary":"periodic"}
    d["seed"]=seed
    for spec in d["species"]:
        spec["count"]=number if spec["name"]==name else 0
        if spec["name"]==name and energy is not None:
            spec["energy"]=energy
    return Config.from_dict(d).validate()


def verify_finite_population():
    natural=natural_protocol()
    w=create_natural(17001,"enriched",natural)
    old=tuple(w.store.ids)
    initial_energy=w.energy()
    last_energy=initial_energy
    movement=False
    count=len(w.store)
    assert count==264 and not w.sources and not w.catalysis_lookup
    for t in range(120):
        previous_moves=w.moves_total
        w.advance(1)
        movement=movement or w.moves_total>previous_moves
        assert len(w.store)==count and tuple(w.store.ids)==old
        assert w.energy()<=last_energy,(
            "unexpected energy gain without active sources",t,last_energy,w.energy())
        last_energy=w.energy()
    w.check()
    return {
        "world_seed":17001,"horizon":120,
        "particles_start":count,"particles_end":len(w.store),
        "particle_ids_unchanged":True,
        "energy_start":initial_energy,"energy_end":last_energy,
        "energy_monotone_nonincreasing":True,
        "native_particle_motion_observed":movement,
        "empty_catalysis_rules":len(w.chemistry.catalysis)==0,
        "empty_energy_sources":len(w.sources)==0
    }


def verify_energy_free_motion():
    c=one_species_config("S3",1,energy=0,seed=778)
    w=World.create(c)
    i=w.species_names.index("S3")
    assert w.move_thresholds[i]>0
    assert w.movement_cost==0
    assert w.energy()==0 and w.configured_energy()==0
    assert len(w.store)==1
    original_id=w.store.ids[0]
    initial_pos=w.store.position_of(0)
    w.advance(128)
    w.check()
    assert w.energy()==0
    assert w.store.ids==[original_id]
    assert w.moves_total>0,"native mobile particle did not move with zero energy"
    return {
        "source_law_movement_cost":w.movement_cost,
        "native_species":"S3",
        "native_species_move_probability":c.species[i].move_probability,
        "initial_particle_energy":0,
        "steps":128,
        "moves_with_total_energy_zero":w.moves_total,
        "position_start":list(initial_pos),
        "position_end":list(w.store.position_of(0)),
        "unchanged_particle_id":original_id
    }


def verify_saturated_ring():
    c=one_species_config("S0",8,grid=8,seed=779)
    species_index=next(i for i,spec in enumerate(c.species) if spec.name=="S0")
    positions=[((3+dx)%8,(3+dy)%8) for dx,dy in OFFSETS]
    bonds=[(i,(i+1)%8,4) for i in range(8)]
    s=ParticleStore(
        8,8,list(range(8)),
        [x for x,y in positions],
        [y for x,y in positions],
        [species_index]*8,[8]*8,bonds
    )
    w=World(c,RNG(c.seed),s)
    w.check()
    assert sum(w.store.degree)==16
    assert all(deg==2 for deg in w.store.degree)
    assert all(w.store.degree[i]==w.max_bonds[w.store.species[i]] for i in range(8))
    assert not list(_candidate_pairs(w))
    assert w.energy()==w.configured_energy()
    return {
        "fixture_not_spontaneous":True,
        "native_species":"S0","native_max_bonds":2,
        "ring_source_ids":list(s.ids),
        "native_ring_edges":len(s.bonds),
        "external_chemical_bond_slots_before_break":0,
        "formation_candidate_pairs_while_saturated":0,
        "total_energy_conserved_in_fixture":True
    }


def run():
    p=protocol()
    native=json.loads(M6.read_text(encoding="utf-8"))
    assert native["chemistry"]["catalysis"]==[]
    assert native["energy"]["sources"]==[]
    assert native["energy"]["movement_cost"]==0
    assert dict((entry["name"],entry["max_bonds"]) for entry in native["species"])=={
        "S0":2,"S1":2,"S2":1,"S3":0
    }
    finite=verify_finite_population()
    zero=verify_energy_free_motion()
    ring=verify_saturated_ring()
    result={
        "schema":"alife-m7-0-capability-audit-result-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "original_M6_laws_unchanged":True,
        "native_source_config_facts":{
            "catalysis_rules":0,"energy_sources":0,
            "movement_energy_cost":0,
            "max_bonds":{"S0":2,"S1":2,"S2":1,"S3":0}
        },
        "native_population_energy_audit":finite,
        "zero_energy_motion_mechanism_fixture":zero,
        "saturated_ring_mechanism_fixture":ring,
        "interpretation":"M6 contains no particle birth/death or hereditary template rules and currently lacks catalytic energy organization; it permits motion at zero energy. None of this formally excludes emergent pattern copying by material rearrangement. No spontaneous genotype or reproduction observed.",
        "scientific_status":"deterministic_law_capabilities_only_not_spontaneous_life"
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M7_AUDIT_SUMMARY="+json.dumps(result,sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    run()
