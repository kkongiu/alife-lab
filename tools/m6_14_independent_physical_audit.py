"""M6.14 posthoc independent physical audit of ALL first-genesis positive worlds.

Does not import M6.12 precursor_candidates, M6.10 observed_cycles,
M6.14 study_world or any previous classifier. Reconstructs exact 3x3
seven-/eight-link geometry directly from particle store, checks no earlier
full/native seven-member-source material shape, and verifies every original
bond and unchanged mobile resident at each tick. Uses fixed completed
GitHub Actions artifact as data, not as trusted executable instructions.

Posthoc replication of trajectories is NOT new independent scientific seeds.
"""
from __future__ import annotations

import json
from pathlib import Path

from tools.m6_4_cycles import BreakRecorder, create_natural, protocol as natural_protocol

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"campaigns/m6_14_first_genesis/merged_results.json"
OUT=ROOT/"campaigns/m6_14_first_genesis/independent_crosscheck.json"
OFFSETS=((-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0))


def material_bonds(s):
    """All bonds as persistent material ID pairs; no M6.14 detector calls."""
    return {tuple(sorted((s.ids[a],s.ids[b]))) for a,b in s.bonds}


def exact_native_material_shape(s, material_ids):
    """A valid all-native eight-ID 7-path or 8-ring in ANY 3x3 perimeter."""
    ids=set(material_ids)
    assert len(ids)==8
    positions={(s.xs[s.index_of(ident)],s.ys[s.index_of(ident)]) for ident in ids}
    if len(positions)!=8:
        return None
    candidates=set()
    for x,y in positions:
        for dx,dy in OFFSETS:
            candidates.add(((x-dx)%s.width,(y-dy)%s.height))
    existing=material_bonds(s)
    internal={edge for edge in existing if edge[0] in ids and edge[1] in ids}
    # Exclude any external attachments: M6.12's strict connected component rule.
    if any(
        s.degree[s.index_of(ident)] != sum(ident in edge for edge in internal)
        for ident in ids
    ):
        return None
    for center in candidates:
        cx,cy=center
        expected={((cx+dx)%s.width,(cy+dy)%s.height) for dx,dy in OFFSETS}
        if positions != expected:
            continue
        clockwise=[
            s.grid[((cy+dy)%s.height)*s.width+((cx+dx)%s.width)]
            for dx,dy in OFFSETS
        ]
        if -1 in clockwise:
            continue
        material=[s.ids[idx] for idx in clockwise]
        if set(material)!=ids:
            continue
        possible={tuple(sorted((material[j],material[(j+1)%8]))) for j in range(8)}
        if not internal.issubset(possible) or len(possible)!=8:
            continue
        if len(internal)==7:
            degrees=sorted(sum(ident in e for e in internal) for ident in ids)
            if degrees==[1,1,2,2,2,2,2,2]:
                return {"kind":"seven","center":center,"edges":internal}
        elif len(internal)==8 and internal==possible:
            return {"kind":"eight","center":center,"edges":internal}
    return None


def inspect_case(seed, ep, final_state):
    p=natural_protocol()
    w=create_natural(seed,"enriched",p)
    rec=BreakRecorder()
    w.event_sink=rec
    start=ep["start_tick"]
    duration=ep["duration_ticks"]
    stop=start+duration
    ids=tuple(sorted(ep["ids"]))
    center=tuple(ep["center"])
    resident=ep["resident_id"]
    orig={tuple(sorted(pair)) for pair in ep["original_edges"]}
    assert len(ids)==8 and len(orig)==7
    assert ep["new_material_first_seven_edge"] is True
    assert ep["prior_seven_edge_episodes"]==0
    assert ep["historical_first_kind"]=="seven"
    assert ep["resident_mobile"] is True
    assert duration>=30
    original_locations=None
    checked_ticks=0
    earlier_shape_ticks=[]
    observed_eighth=None
    break_at_end=[]
    first_resident_bond_tick=None
    free_unbonded_prefix_ticks=0
    max_resident_degree=0

    def inspect(world):
        nonlocal original_locations,checked_ticks,observed_eighth,break_at_end
        nonlocal first_resident_bond_tick,free_unbonded_prefix_ticks,max_resident_degree
        tick=world.step
        broken=rec.pop(tick)
        s=world.store
        if tick<start:
            earlier=exact_native_material_shape(s,ids)
            if earlier is not None:
                earlier_shape_ticks.append({"tick":tick,"kind":earlier["kind"]})
            return
        if tick==stop and not ep["right_censored"]:
            break_at_end=sorted(broken.intersection(orig))
            assert break_at_end,("no source break at expected episode stop",seed,stop)
            return
        if tick>=stop:
            return
        if tick==start:
            shape=exact_native_material_shape(s,ids)
            assert shape and shape["kind"]=="seven"
            assert shape["center"]==center
            assert shape["edges"]==orig
        elif broken.intersection(orig):
            raise AssertionError(("original source edge broke within claimed episode",seed,tick))
        existing=material_bonds(s)
        assert orig.issubset(existing),("original edge not present",seed,tick)
        locations={i:(s.xs[s.index_of(i)],s.ys[s.index_of(i)]) for i in ids}
        if original_locations is None:
            original_locations=locations
        assert locations==original_locations,("material moved",seed,tick)
        cx,cy=center
        idx=s.grid[cy*s.width+cx]
        assert idx!=-1 and s.ids[idx]==resident,("resident left center",seed,tick)
        degree=s.degree[idx]
        max_resident_degree=max(max_resident_degree,degree)
        if degree==0 and first_resident_bond_tick is None:
            free_unbonded_prefix_ticks+=1
        elif degree>0 and first_resident_bond_tick is None:
            first_resident_bond_tick=tick
        # Geometry may confine a now-BONDED native resident. The frozen
        # primary gate requires grade=0 at first sighting and same ID later,
        # but does not require grade=0 at every subsequent tick. Keep these
        # scientifically different durations separate.
        if tick==start:
            assert degree==0,("resident bonded at birth",seed,tick)
        assert world.config.species[s.species[idx]].move_probability>0
        if observed_eighth is None:
            # Detect missing perimeter edge by computing native shape directly.
            shape=exact_native_material_shape(s,ids)
            if shape is not None and shape["kind"]=="eight":
                observed_eighth=tick
        checked_ticks+=1

    w.advance(600,observer=inspect)
    w.check()
    assert not earlier_shape_ticks,("previous seven or eight native material shape",seed,earlier_shape_ticks)
    assert checked_ticks==duration,(seed,checked_ticks,duration)
    assert observed_eighth==ep["first_eighth_bond_tick"],(
        "eighth-bond tick mismatch",seed,observed_eighth,ep["first_eighth_bond_tick"]
    )
    if not ep["right_censored"]:
        assert break_at_end and stop<=600
    else:
        assert stop==601,("right censor interval convention",seed,stop)
    f=final_state
    assert w.state_hash_full()==f["hash"]
    assert w.rng.fingerprint()==f["rng"] and w.rng.draws==f["draws"]
    assert w.energy()==f["energy"] and w.dissipated==f["dissipated"]
    assert w.bonds_formed_total==f["formed"] and w.bonds_broken_total==f["broken"]
    bare=create_natural(seed,"enriched",p)
    bare.advance(600)
    bare.check()
    assert bare.state_hash_full()==w.state_hash_full()
    assert bare.rng.fingerprint()==w.rng.fingerprint()
    assert bare.rng.draws==w.rng.draws
    assert bare.energy()==w.energy()
    assert bare.dissipated==w.dissipated
    assert bare.bonds_formed_total==w.bonds_formed_total
    assert bare.bonds_broken_total==w.bonds_broken_total
    return {
        "seed":seed,"first_tick":start,"last_intact_tick":stop-1,
        "duration_verified":duration,"center":list(center),"resident_id":resident,
        "observed_eighth_bond_tick":observed_eighth,
        "initial_material_shapes_before_tick":len(earlier_shape_ticks),
        "original_break_tick":None if ep["right_censored"] else stop,
        "source_edges_broken_on_end":[list(edge) for edge in break_at_end],
        "first_resident_bond_tick":first_resident_bond_tick,
        "unbonded_prefix_ticks":free_unbonded_prefix_ticks,
        "resident_ever_bonded_during_barrier":first_resident_bond_tick is not None,
        "max_resident_degree":max_resident_degree,
        "identical_final_full_hash_rng_energy_bond_counters":True
    }


def main():
    payload=json.loads(DATA.read_text(encoding="utf-8"))
    assert payload["schema"]=="alife-m6-14-independent-first-genesis-results-v1"
    assert payload["all_shards_complete"] is True
    assert payload["physics_unchanged"] is True
    assert len(payload["worlds"])==1600
    selected={}
    for w in payload["worlds"]:
        episodes=[ep for ep in w["result"]["episodes"] if
                  ep["resident_mobile"] and ep["new_material_first_seven_edge"]
                  and ep["duration_ticks"]>=30]
        if episodes:
            assert len(episodes)==1,("unexpected >1 primary first episode in one world",w["seed"])
            selected[w["seed"]]=(episodes[0],w["result"]["final"])
    assert sorted(selected)==payload["summary"]["primary_qualifying_first_genesis_seeds"]
    assert len(selected)==payload["summary"]["primary_first_genesis_worlds_ge30"]
    details=[]
    for seed,(ep,fin) in sorted(selected.items()):
        check=inspect_case(seed,ep,fin)
        details.append(check)
        print(f"M614_PHYSICAL_AUDIT_PASS seed={seed} duration={check['duration_verified']}",flush=True)
    strictly_unbonded=[x["seed"] for x in details if x["unbonded_prefix_ticks"]>=30]
    result={
        "schema":"alife-m6-14-independent-posthoc-physical-audit-v2",
        "posthoc":True,
        "not_new_random_seeds":True,
        "original_preregistered_decision_unmodified":True,
        "n_independently_replayed_primary_worlds":len(details),
        "posthoc_strict_unbonded_first_30_ticks_seed_count":len(strictly_unbonded),
        "posthoc_strict_unbonded_first_30_ticks_seeds":strictly_unbonded,
        "results":details
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M614_PHYSICAL_FINAL="+json.dumps({
        "independent_primary_worlds_checked":len(details),
        "max_duration":max(x["duration_verified"] for x in details),
        "posthoc_strict_unbonded_first_30_ticks_count":len(strictly_unbonded),
        "strict_seeds":strictly_unbonded,
        "all_passed":True},sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    main()
