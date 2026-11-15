"""M6.10: exact lattice pocket geometry, wrapped perimeter and immobile resident."""
from copy import deepcopy

from support import make_energy_config, world_with
from tools.m6_10_pockets import (
    BORDER_OFFSETS, observed_cycles, pocket_center, protocol,
    resident_unchanged, summarize
)
from alife.structures import components


CLOCKWISE=(
    (-1,-1),(0,-1),(1,-1),(1,0),
    (1,1),(0,1),(-1,1),(-1,0)
)


def synthetic_pocket(cx=3,cy=3,empty=False):
    cfg=make_energy_config(
        width=8,height=8,seed=71,
        species=[
            {"name":"S0","count":8,"move_probability":0.0,
             "energy":20,"max_bonds":2},
            {"name":"S3","count":0 if empty else 1,"move_probability":0.6,
             "energy":8,"max_bonds":0},
        ],
        chemistry={
            "enabled":True,"bond_cost":2,"formation_probability":0.0,
            "break_probability":0.0,
            "allowed_pairs":[["S0","S0"]],"catalysis":[]
        }
    )
    positions=[
        ((cx+dx)%8,(cy+dy)%8) for dx,dy in CLOCKWISE
    ]
    species=[0]*8
    energy=[16]*8
    if not empty:
        positions.append((cx,cy))
        species.append(1)
        energy.append(8)
    bonds=[(i,(i+1)%8,4) for i in range(8)]
    world=world_with(cfg,positions,species,energy=energy,bonds=bonds)
    world.check()
    return world


def test_protocol_precommitted_seeds_and_gate():
    p=protocol()
    assert p["sample"]["seeds"]==list(range(9801,9851))
    assert p["sample"]["expected_worlds"]==100
    assert p["sample"]["horizon_ticks"]==600
    assert p["decision"]["replicated"].startswith("If >=2 distinct worlds")


def test_square_perimeter_is_exact_eight_cycle_with_trapped_native_monomer():
    w=synthetic_pocket()
    (indices,_),=components(w.store)
    assert pocket_center(w.store,indices)==(3,3)
    rings,counts=observed_cycles(w)
    (ring,)=rings
    assert counts[8]==1
    assert ring["pocket"] is True
    assert ring["center"]==(3,3)
    assert ring["resident_id"]==8
    assert ring["resident_species"]=="S3"
    assert ring["resident_move_probability"]>0
    ep={"center":[3,3],"resident_id":8}
    for _ in range(40):
        w.advance(1)
        assert resident_unchanged(w,ep)
    w.check()


def test_wrapped_square_perimeter_and_empty_center():
    w=synthetic_pocket(cx=0,cy=0,empty=True)
    rings,counts=observed_cycles(w)
    assert len(rings)==1 and counts[8]==1
    assert rings[0]["pocket"] is True
    assert rings[0]["center"]==(0,0)
    assert rings[0]["resident_id"] is None
    for _ in range(8):
        w.advance(1)
        assert resident_unchanged(w,{"center":[0,0],"resident_id":None})


def test_eight_ring_without_lattice_interior_not_false_pocket():
    cfg=make_energy_config(
        width=8,height=8,
        species=[{"name":"S0","count":8,"move_probability":0.0,
                  "energy":20,"max_bonds":2}],
        chemistry={
            "enabled":True,"bond_cost":2,"formation_probability":0.0,
            "break_probability":0.0,"allowed_pairs":[["S0","S0"]],
            "catalysis":[]
        }
    )
    positions=[(0,0),(1,0),(2,0),(3,0),
               (3,1),(2,1),(1,1),(0,1)]
    w=world_with(cfg,positions,[0]*8,energy=[16]*8,
                 bonds=[(i,(i+1)%8,4) for i in range(8)])
    w.check()
    (indices,_),=components(w.store)
    assert pocket_center(w.store,indices) is None
    rings,counts=observed_cycles(w)
    assert counts[8]==1
    assert rings[0]["pocket"] is False


def _sample(seed,episodes):
    return {
        "density":"baseline","seed":seed,
        "result":{
            "pocket_episodes":episodes,
            "counts":{
                "all_distinct_8_ring_material_sets":len(episodes),
                "other_8_nonpocket_material_sets":0,
                "distinct_large_ring_material_sets":0,
            }
        }
    }


def test_natural_trap_gate_requires_two_distinct_worlds():
    p=protocol()
    episode={
        "resident_id":8,"resident_species":"S3",
        "resident_move_probability":0.6,
        "duration_observed_ticks":40,
        "right_censored":False
    }
    assert summarize([],p)["decision"]=="not_observed_under_preregistered_sample"
    assert summarize([_sample(1,[episode])],p)["decision"]=="one_exploratory_geometric_trap_case"
    assert summarize([_sample(1,[episode]),_sample(2,[episode])],p)["decision"]=="replicated_natural_geometric_trapping_without_biological_membrane"
