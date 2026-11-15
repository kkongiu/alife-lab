"""M6.10: passive geometric pocket detection in spontaneous M6 dynamics.

A minimal von-Neumann 3x3 sealed pocket needs an 8-member cycle on the
eight perimeter sites. A free particle at the center is geometrically
blocked by the fully occupied four neighboring perimeter cells.
All worlds start with ZERO bonds; NO artificial ring or particle is added.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.structures import components, signature_v2
from tools.m6_4_cycles import BreakRecorder, create_natural, protocol as natural_protocol

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m6_10_pockets/protocol.json"
OUTPUT=ROOT/"campaigns/m6_10_pockets/results.json"

BORDER_OFFSETS=(
    (-1,-1),(0,-1),(1,-1),
    (-1,0),(1,0),
    (-1,1),(0,1),(1,1)
)


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-10-spontaneous-lattice-pockets-v1"
    assert p["status"]=="frozen-before-code-and-results"
    assert p["sample"]["seeds"]==list(range(9801,9851))
    assert p["sample"]["horizon_ticks"]==600
    assert p["sample"]["expected_worlds"]==100
    return p


def pocket_center(s,indices):
    """Unique center (cx,cy) if 8 positions are a toroidal 3x3 perimeter."""
    if len(indices)!=8:
        return None
    points={(s.xs[i],s.ys[i]) for i in indices}
    if len(points)!=8 or s.width<5 or s.height<5:
        return None
    found=set()
    for x,y in points:
        for dx,dy in BORDER_OFFSETS:
            cx=(x-dx)%s.width
            cy=(y-dy)%s.height
            expected={
                ((cx+ox)%s.width,(cy+oy)%s.height)
                for ox,oy in BORDER_OFFSETS
            }
            if points==expected:
                found.add((cx,cy))
    if not found:
        return None
    assert len(found)==1,("multiple 3x3 centers",found)
    return next(iter(found))


def observed_cycles(world):
    """Read-only enumeration; distinguish exact 3x3 ring geometry."""
    s=world.store
    rings=[]
    ring_snapshots=Counter()
    for indices,bonds in components(s):
        if len(indices)<4 or len(bonds)!=len(indices):
            continue
        if any(s.degree[i]!=2 for i in indices):
            continue
        assert len(indices)%2==0, "odd cycle on even periodic square grid"
        n=len(indices)
        ring_snapshots[n]+=1
        ids=tuple(sorted(s.ids[i] for i in indices))
        if n!=8:
            rings.append({"size":n,"ids":ids,"pocket":None})
            continue
        edge_ids=tuple(sorted(tuple(sorted((s.ids[a],s.ids[b]))) for a,b in bonds))
        sig=signature_v2(s,indices,bonds,world.species_names)
        assert sig.exact and sig.key.startswith("C2:")
        center=pocket_center(s,indices)
        if center is None:
            rings.append({
                "size":8,"ids":ids,"edges":edge_ids,
                "signature":sig.key,"pocket":False
            })
            continue
        index=s.grid[center[1]*s.width+center[0]]
        occupant_id=s.ids[index] if index!=-1 else None
        occupant_species=world.species_names[s.species[index]] if index!=-1 else None
        occupant_move=world.config.species[s.species[index]].move_probability if index!=-1 else None
        if index!=-1:
            assert index not in indices
            assert s.degree[index]==0,(
                "center resident bonded despite sealed ring",center,occupant_id
            )
        rings.append({
            "size":8,
            "ids":ids,
            "edges":edge_ids,
            "signature":sig.key,
            "pocket":True,
            "center":center,
            "resident_id":occupant_id,
            "resident_species":occupant_species,
            "resident_move_probability":occupant_move
        })
    return rings,ring_snapshots


def resident_unchanged(w,ep):
    center=ep["center"]
    i=w.store.grid[center[1]*w.store.width+center[0]]
    occupant_id=None if i==-1 else w.store.ids[i]
    assert occupant_id==ep["resident_id"],(
        "center particle changed while original sealed perimeter persists",
        w.step,ep["resident_id"],occupant_id
    )
    if i!=-1:
        assert w.store.degree[i]==0
    return True


def study_world(w,steps=600):
    assert w.step==0
    w.check()
    assert not w.store.bonds
    initial_hash=w.state_hash_full()
    initial_rng=w.rng.fingerprint()
    initial_draws=w.rng.draws

    broken=BreakRecorder()
    w.event_sink=broken
    episodes=[]
    active={}
    counts=Counter()
    all_8_ids=set()
    other_8_ids=set()
    all_big_ids=set()

    def finish(key,tick,reason,censored=False):
        ep=active.pop(key)
        length=tick-ep["start_tick"]+(1 if censored else 0)
        assert length>=1,(tick,ep)
        episodes.append({
            **ep,
            "duration_observed_ticks":length,
            "last_observed_tick":tick if censored else tick-1,
            "ended_by":reason,
            "right_censored":censored,
            "verified_resident_unmoved_during_episode":True,
        })

    def observer(world):
        before_draws=world.rng.draws
        t=world.step
        broken_edges=broken.pop(t)
        rings,observed=observed_cycles(world)
        for n,count in observed.items():
            counts[f"ring_{n}_snapshots"]+=count

        pocket_now={}
        for ring in rings:
            if ring["size"]==8:
                all_8_ids.add(ring["ids"])
                if ring["pocket"] is False:
                    other_8_ids.add(ring["ids"])
                else:
                    key=(ring["ids"],ring["edges"])
                    pocket_now[key]=ring
                    counts["pocket8_snapshots"]+=1
                    if ring["resident_id"] is not None:
                        counts["occupied_pocket8_snapshots"]+=1
            elif ring["size"]>=10:
                all_big_ids.add(ring["ids"])

        for key,ep in list(active.items()):
            new=pocket_now.get(key)
            interrupted=bool(broken_edges.intersection(tuple(map(tuple,ep["edges"]))))
            if new is None or interrupted or tuple(new["center"])!=tuple(ep["center"]):
                why=("source_bond_break" if interrupted else
                     "perimeter_lost" if new is None else "geometry_changed")
                finish(key,t,why)

        for key,ring in pocket_now.items():
            if key not in active:
                active[key]={
                    "start_tick":t,
                    "ids":list(ring["ids"]),
                    "edges":[list(edge) for edge in ring["edges"]],
                    "signature":ring["signature"],
                    "center":list(ring["center"]),
                    "resident_id":ring["resident_id"],
                    "resident_species":ring["resident_species"],
                    "resident_move_probability":ring["resident_move_probability"]
                }
            # A ring intact over this interval is a physical barrier to the
            # center site. Never paper over an observed occupant identity change.
            resident_unchanged(world,active[key])
        assert world.rng.draws==before_draws

    w.advance(steps,observer=observer)
    for key in list(active):
        finish(key,w.step,"right_censored_at_horizon",censored=True)
    w.check()
    counts["all_distinct_8_ring_material_sets"]=len(all_8_ids)
    counts["other_8_nonpocket_material_sets"]=len(other_8_ids)
    counts["distinct_large_ring_material_sets"]=len(all_big_ids)
    summary={
        "initial_hash":initial_hash,
        "initial_rng":initial_rng,
        "initial_rng_draws":initial_draws,
        "final_hash":w.state_hash_full(),
        "final_rng":w.rng.fingerprint(),
        "final_rng_draws":w.rng.draws,
        "final_energy":w.energy(),
        "final_dissipated":w.dissipated,
        "bonds_formed":w.bonds_formed_total,
        "bonds_broken":w.bonds_broken_total,
        "counts":dict(sorted(counts.items())),
        "pocket_episodes":episodes,
    }
    return summary


def summarize(worlds,p):
    from collections import Counter
    by_density={}
    for den in p["sample"]["densities"]:
        samples=[w for w in worlds if w["density"]==den]
        episodes=[ep for w in samples for ep in w["result"]["pocket_episodes"]]
        occupied=[ep for ep in episodes if ep["resident_id"] is not None]
        persistent=[
            ep for ep in occupied
            if ep["resident_move_probability"]>0
            and ep["duration_observed_ticks"]>=30
        ]
        independent_persistent_worlds={
            w["seed"] for w in samples
            if any(ep["resident_id"] is not None and
                   ep["resident_move_probability"]>0 and
                   ep["duration_observed_ticks"]>=30
                   for ep in w["result"]["pocket_episodes"])
        }
        by_density[den]={
            "worlds":len(samples),
            "worlds_with_native_3x3_pocket":sum(bool(w["result"]["pocket_episodes"]) for w in samples),
            "pocket_episodes":len(episodes),
            "occupied_pocket_episodes":len(occupied),
            "long_lived_occupied_pocket_episodes_at_least_30":len(persistent),
            "worlds_with_long_lived_occupied_pocket":len(independent_persistent_worlds),
            "censored_pocket_episodes":sum(ep["right_censored"] for ep in episodes),
            "longest_pocket_episode_observed":max((ep["duration_observed_ticks"] for ep in episodes),default=0),
            "distinct_8_cycle_material_sets":sum(w["result"]["counts"]["all_distinct_8_ring_material_sets"] for w in samples),
            "other_8_nonpocket_material_sets":sum(w["result"]["counts"]["other_8_nonpocket_material_sets"] for w in samples),
            "distinct_large_ring_material_sets":sum(w["result"]["counts"]["distinct_large_ring_material_sets"] for w in samples),
            "ring_snapshot_counts":dict(sorted(Counter({
                str(n):sum(w["result"]["counts"].get(f"ring_{n}_snapshots",0) for w in samples)
                for n in (4,6,8,10,12,14,16)
            }).items())),
            "examples":episodes[:6],
        }
    all_episodes=[ep for w in worlds for ep in w["result"]["pocket_episodes"]]
    trapped_world_count=sum(x["worlds_with_long_lived_occupied_pocket"] for x in by_density.values())
    if trapped_world_count>=2:
        decision="replicated_natural_geometric_trapping_without_biological_membrane"
    elif trapped_world_count==1:
        decision="one_exploratory_geometric_trap_case"
    elif all_episodes:
        decision="geometric_pocket_without_long_lived_trapping"
    else:
        decision="not_observed_under_preregistered_sample"
    return {
        "by_density":by_density,
        "worlds_with_geometric_trap":trapped_world_count,
        "decision":decision,
        "caveat":"Geometrical occupation barriers from static bonded atoms are not biological membranes, self-maintaining cells, or replication."
    }


def run():
    p=protocol()
    natural=natural_protocol()
    worlds=[]
    replays=[]
    for den in p["sample"]["densities"]:
        for seed in p["sample"]["seeds"]:
            world=create_natural(seed,den,natural)
            record=study_world(world,p["sample"]["horizon_ticks"])
            worlds.append({"density":den,"seed":seed,"result":record})
            if seed==p["sample"]["seeds"][0]:
                bare=create_natural(seed,den,natural)
                assert bare.state_hash_full()==record["initial_hash"]
                assert bare.rng.fingerprint()==record["initial_rng"]
                bare.advance(p["sample"]["horizon_ticks"])
                bare.check()
                assert bare.state_hash_full()==record["final_hash"]
                assert bare.rng.fingerprint()==record["final_rng"]
                assert bare.rng.draws==record["final_rng_draws"]
                assert bare.energy()==record["final_energy"]
                assert bare.dissipated==record["final_dissipated"]
                assert bare.bonds_formed_total==record["bonds_formed"]
                assert bare.bonds_broken_total==record["bonds_broken"]
                replays.append({"density":den,"seed":seed,"hash":record["final_hash"]})
            print(f"M610_WORLD={den}/{seed} pockets={len(record['pocket_episodes'])} rings8={record['counts']['all_distinct_8_ring_material_sets']}",flush=True)
    assert len(worlds)==100
    analysis=summarize(worlds,p)
    result={
        "schema":"m6-10-natural-lattice-pocket-results-v1",
        "protocol_commit":"9425d97119934e51b3ee4dc8b8155224af903dae",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":worlds,
        "summary":analysis,
        "replays":replays,
        "physical_laws_unchanged":True,
        "no_biological_membrane_claim":True
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M610_POCKET_SUMMARY="+json.dumps({
        "n_worlds":len(worlds),"summary":analysis,"replays":replays
    },sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    run()
