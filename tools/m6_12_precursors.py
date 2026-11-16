"""M6.12 — passive seven-native-edge 3x3 precursor / resident occupancy audit.

Original M6 physical laws and seeded initial states are untouched.
The geometric barrier may pre-exist the eighth bond: all four cardinal sites
are occupied by immobile bonded members of the seven-edge path.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import json

from alife.structures import components
from tools.m6_4_cycles import BreakRecorder, create_natural, protocol as natural_protocol
from tools.m6_10_pockets import pocket_center
from tools.m6_11_occupancy import CLOCKWISE, center_occupation

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m6_12_precursors/protocol.json"
OUTPUT=ROOT/"campaigns/m6_12_precursors/results.json"


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-12-native-seven-edge-precursor-audit-v1"
    assert p["status"]=="preregistered-before-runner-or-results"
    assert p["fixed_sample"]["seed_start"]==11001
    assert p["fixed_sample"]["seed_end"]==11150
    assert p["fixed_sample"]["total_worlds"]==300
    return p


def ring_border(store, center):
    """Original material particle IDs in clockwise perimeter order."""
    x,y=center
    indices=[]
    for dx,dy in CLOCKWISE:
        i=store.grid[((y+dy)%store.height)*store.width+((x+dx)%store.width)]
        if i==-1:
            return None
        indices.append(i)
    return indices


def precursor_candidates(world):
    """Exact connected 8-particle, 7-bond perimeter PATH, no off-path bonds."""
    s=world.store
    result=[]
    for indices,bonds in components(s):
        if len(indices)!=8 or len(bonds)!=7:
            continue
        if sorted(s.degree[i] for i in indices)!=[1,1,2,2,2,2,2,2]:
            continue
        center=pocket_center(s,indices)
        if center is None:
            continue
        ordered=ring_border(s,center)
        if ordered is None or set(indices)!=set(ordered):
            continue
        existing=frozenset(tuple(sorted((s.ids[a],s.ids[b]))) for a,b in bonds)
        possible=[
            tuple(sorted((s.ids[ordered[k]],s.ids[ordered[(k+1)%8]])))
            for k in range(8)
        ]
        if len(set(possible))!=8 or not existing.issubset(possible):
            continue
        missing=[edge for edge in possible if edge not in existing]
        if len(missing)!=1:
            continue
        ends=[s.index_of(q) for q in missing[0]]
        if any(s.degree[i]!=1 for i in ends):
            continue
        resident=center_occupation(s,center,world.config.species)
        if resident["id"] is None:
            stratum="empty"
        elif resident["degree"]==0 and resident["mobile"]:
            stratum="free_mobile"
        else:
            stratum="other_occupied"
        pair=tuple(sorted(world.species_names[s.species[i]] for i in ends))
        result.append({
            "center":tuple(center),
            "ids":tuple(sorted(s.ids[i] for i in indices)),
            "positions":tuple((s.ids[i],s.xs[i],s.ys[i]) for i in indices),
            "edges":existing,
            "missing":missing[0],
            "pair":"-".join(pair),
            "stratum":stratum,
            "resident_id":resident["id"],
            "resident_mobile":resident["degree"]==0 and resident["mobile"],
            "resident_degree":resident["degree"]
        })
    return result


def chemically_eligible(world, missing):
    s=world.store
    ia,ib=(s.index_of(x) for x in missing)
    a,b=s.species[ia],s.species[ib]
    if (a,b) not in world.allowed_pairs and (b,a) not in world.allowed_pairs:
        return False
    if s.degree[ia]>=world.max_bonds[a] or s.degree[ib]>=world.max_bonds[b]:
        return False
    if s.energy[ia]<world.formation_cost or s.energy[ib]<world.formation_cost:
        return False
    return True


def material_intact(world, ep, broken_edges):
    """Exact frozen native geometry and original 7 bonds, even across reclosures."""
    if ep["edges"].intersection(broken_edges):
        return False, "original_edge_broken"
    s=world.store
    for ident,x,y in ep["positions"]:
        i=s.index_of(ident)
        if (s.xs[i],s.ys[i])!=(x,y):
            return False, "material_position_changed"
    for id_a,id_b in ep["edges"]:
        a,b=s.index_of(id_a),s.index_of(id_b)
        if tuple(sorted((a,b))) not in s.bonds:
            return False, "original_bond_missing"
    cx,cy=ep["center"]
    resident=center_occupation(s,(cx,cy),world.config.species)
    if ep["stratum"] in ("empty","free_mobile"):
        assert resident["id"]==ep["resident_id"],(
            "occupied immutable shell changed center resident",world.step,ep, resident
        )
    return True,None


def risk_key(stratum, pair):
    return stratum+"|"+pair


def study_world(world, steps=600):
    assert world.step==0 and not world.store.bonds
    world.check()
    initial_hash=world.state_hash_full()
    initial_rng=world.rng.fingerprint()
    initial_draws=world.rng.draws
    rec=BreakRecorder()
    world.event_sink=rec
    active={}
    episodes=[]
    counts=Counter()
    strata=defaultdict(Counter)
    first_sets=set()
    examples=[]

    def end(key,tick,why,censored=False):
        ep=active.pop(key)
        length=tick-ep["start_tick"]+(1 if censored else 0)
        assert length>=1,(tick,ep)
        record={
            "start_tick":ep["start_tick"],"duration_ticks":length,
            "ended_by":why,"right_censored":censored,
            "center":list(ep["center"]), "ids":list(ep["ids"]),
            "original_edges":[list(e) for e in sorted(ep["edges"])],
            "stratum":ep["stratum"],"pair":ep["pair"],
            "resident_id":ep["resident_id"],"resident_mobile":ep["resident_mobile"],
            "first_of_material_set":ep["first_of_material_set"],
            "exposures":ep["exposures"],
            "eligible_exposures":ep["eligible_exposures"],
            "closure_observed":ep["closed_tick"] is not None,
            "first_closure_tick":ep["closed_tick"],
            "full_original_path_intact":True
        }
        episodes.append(record)
        if ep["resident_mobile"] and length>=30:
            counts["native_mobile_30tick_barrier_episodes"]+=1
        if ep["closed_tick"] is not None:
            counts["original_seven_to_eight_closures"]+=1
        if len(examples)<12 and (ep["resident_mobile"] or ep["closed_tick"] is not None):
            examples.append(record)

    def add_risk(ep,w,tick):
        if tick>=steps or ep["closed_tick"] is not None:
            return
        ep["exposures"]+=1
        k=risk_key(ep["stratum"],ep["pair"])
        stats=strata[k]
        stats["risk_all"]+=1
        if ep["first_of_material_set"]:
            stats["risk_first_material_set"]+=1
        eligible=chemically_eligible(w,ep["missing"])
        ep["eligible_at_last_tick"]=eligible
        if eligible:
            stats["risk_eligible"]+=1
            ep["eligible_exposures"]+=1
            if ep["first_of_material_set"]:
                stats["risk_eligible_first_material_set"]+=1

    def observe(w):
        draws=w.rng.draws
        t=w.step
        broken=rec.pop(t)
        # First evaluate all pending one-step follow-ups. No future-state peeking.
        for key,ep in list(active.items()):
            intact,reason=material_intact(w,ep,broken)
            if not intact:
                end(key,t,reason)
                continue
            missing=ep["missing"]
            a,b=(w.store.index_of(x) for x in missing)
            is_closed=tuple(sorted((a,b))) in w.store.bonds
            if ep["closed_tick"] is None and is_closed:
                ep["closed_tick"]=t
                counts["closures_from_at_risk"]+=1
                stats=strata[risk_key(ep["stratum"],ep["pair"])]
                stats["closures_all"]+=1
                # Only conditional on last snapshot's chemical eligibility.
                if ep["eligible_at_last_tick"]:
                    stats["closures_eligible"]+=1
                    if ep["first_of_material_set"]:
                        stats["closures_eligible_first_material_set"]+=1
            # A valid 7-original-edge barrier survives even after edge 8 closes.
            if not is_closed and ep["closed_tick"] is None:
                add_risk(ep,w,t)
        # Discover newly created native precursor episodes.
        for obj in precursor_candidates(w):
            key=(obj["center"],obj["ids"],obj["edges"])
            if key in active:
                continue
            first=obj["ids"] not in first_sets
            first_sets.add(obj["ids"])
            ep={**obj,"start_tick":t,"first_of_material_set":first,
                "exposures":0,"eligible_exposures":0,"closed_tick":None,
                "eligible_at_last_tick":False}
            active[key]=ep
            counts["native_seven_edge_episodes"]+=1
            if first:
                counts["distinct_material_sets"]+=1
            counts["birth_"+obj["stratum"]]+=1
            strata[risk_key(obj["stratum"],obj["pair"])]["episodes"]+=1
            if first:
                strata[risk_key(obj["stratum"],obj["pair"])]["first_material_sets"]+=1
            add_risk(ep,w,t)
        assert draws==w.rng.draws,"observer consumed random stream"

    world.advance(steps,observer=observe)
    for key in list(active):
        end(key,world.step,"end_of_run",censored=True)
    world.check()
    return {
        "initial":{"hash":initial_hash,"rng":initial_rng,"draws":initial_draws},
        "final":{"hash":world.state_hash_full(),"rng":world.rng.fingerprint(),
                 "draws":world.rng.draws,"energy":world.energy(),
                 "dissipated":world.dissipated,"formed":world.bonds_formed_total,
                 "broken":world.bonds_broken_total},
        "counts":dict(counts),
        "strata":{k:dict(v) for k,v in sorted(strata.items())},
        "episodes":episodes,
        "examples":examples
    }


def summarize(worlds,p):
    out={}
    independent_with_mobile=0
    independent_with_30=0
    for density in p["fixed_sample"]["densities"]:
        select=[w for w in worlds if w["density"]==density]
        counts=Counter()
        aggregate=defaultdict(Counter)
        valid_mobile_worlds=0
        mobile_risk_worlds=0
        thirty_worlds=0
        closure_worlds=0
        for w in select:
            r=w["result"]
            counts.update(r["counts"])
            for k,v in r["strata"].items():
                aggregate[k].update(v)
            if any(e["stratum"]=="free_mobile" for e in r["episodes"]):
                valid_mobile_worlds+=1
            if any(k.startswith("free_mobile|") and v.get("risk_eligible",0)>0
                   for k,v in r["strata"].items()):
                mobile_risk_worlds+=1
            if any(e["resident_mobile"] and e["duration_ticks"]>=30
                   for e in r["episodes"]):
                thirty_worlds+=1
            if any(e["closure_observed"] for e in r["episodes"]):
                closure_worlds+=1
        independent_with_mobile+=mobile_risk_worlds
        independent_with_30+=thirty_worlds
        def calc(s):
            return {
                **dict(s),
                "closure_per_eligible_risk_tick":(
                    round(s.get("closures_eligible",0)/s["risk_eligible"],6)
                    if s.get("risk_eligible",0)>0 else None)
            }
        out[density]={
            "worlds":len(select),"worlds_with_mobile_precursor":valid_mobile_worlds,
            "worlds_with_eligible_mobile_precursor":mobile_risk_worlds,
            "worlds_with_geometric_30tick_mobile_barrier":thirty_worlds,
            "worlds_with_seven_to_eight_closure":closure_worlds,
            "episode_counts":dict(counts),
            "by_center_state_and_pair":{k:calc(v) for k,v in sorted(aggregate.items())}
        }
    criterion=(
        "repeated_native_geometric_confinement_only" if independent_with_30>=2
        else "single_unreplicated_30tick_confinement" if independent_with_30==1
        else "no_confirmed_30tick_confinement"
    )
    return {
        "by_density":out,
        "independent_worlds_with_eligible_mobile_precursor":independent_with_mobile,
        "independent_worlds_with_30tick_confinement":independent_with_30,
        "decision":criterion,
        "closure_comparison_underpowered":independent_with_mobile<5,
        "caveat":"7-edge connected shell is already a geometrical barrier for a center mobile monomer; eighth bond is not onset. Repeated tick exposures are not independent and observational occupancy groups are not causally matched."
    }


def run():
    p=protocol()
    natural=natural_protocol()
    worlds=[]
    replays=[]
    for density in p["fixed_sample"]["densities"]:
        for seed in range(p["fixed_sample"]["seed_start"],p["fixed_sample"]["seed_end"]+1):
            world=create_natural(seed,density,natural)
            record=study_world(world,p["fixed_sample"]["horizon_ticks"])
            worlds.append({"density":density,"seed":seed,"result":record})
            if seed==p["fixed_sample"]["seed_start"]:
                bare=create_natural(seed,density,natural)
                assert bare.state_hash_full()==record["initial"]["hash"]
                assert bare.rng.fingerprint()==record["initial"]["rng"]
                bare.advance(p["fixed_sample"]["horizon_ticks"])
                bare.check()
                expected=record["final"]
                assert bare.state_hash_full()==expected["hash"]
                assert bare.rng.fingerprint()==expected["rng"]
                assert bare.rng.draws==expected["draws"]
                assert bare.energy()==expected["energy"]
                assert bare.dissipated==expected["dissipated"]
                assert bare.bonds_formed_total==expected["formed"]
                assert bare.bonds_broken_total==expected["broken"]
                replays.append({"density":density,"seed":seed,"hash":expected["hash"]})
            print(f"M612_WORLD={density}/{seed} 7chain={record['counts'].get('native_seven_edge_episodes',0)} resident={record['counts'].get('birth_free_mobile',0)} 30tick={record['counts'].get('native_mobile_30tick_barrier_episodes',0)}",flush=True)
    assert len(worlds)==p["fixed_sample"]["total_worlds"]
    result={
        "schema":"alife-m6-12-native-seven-edge-result-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":worlds,"summary":summarize(worlds,p),
        "replays":replays,"laws_unchanged":True
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M612_SUMMARY="+json.dumps(result["summary"],sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    run()
