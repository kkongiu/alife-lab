"""M6.15 paired counterfactual source-bond stability of naturally formed 7-edge cages.

Strictly intervention-on-POSITION of one unbonded mobile particle, not a
change of M6 physical rules. Remote relocation has its own indirect effects;
no claim that the medium-term difference identifies a local/biological effect.

The one-step native-original-edge break equality is a deterministically
falsifiable invariant of M6: break_bonds comes BEFORE movement/formation, and
every original bond gets identical ordered RNG rolls in both matched clones.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import json

from tools.m6_4_cycles import create_natural, protocol as natural_protocol, BreakRecorder
from tools.m6_12_precursors import precursor_candidates
from tools.m6_5_ring_forks import clone_world
from tools.m6_13_replication import wilson

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m6_15_center_control"
PROTOCOL=BASE/"protocol.json"
OUTPUT=BASE/"results.json"
NEIGHBORS=((0,-1),(1,0),(0,1),(-1,0))
HORIZONS=(10,30,60,120)


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-15-paired-native-center-position-counterfactual-v1"
    assert p["status"]=="frozen_before_code_and_outcomes"
    assert p["sample"]["seeds"]==1000
    assert p["sample"]["seed_start"]==15001 and p["sample"]["seed_end_inclusive"]==16000
    assert p["sample"]["fork_horizon_ticks"]==120
    assert len(p["sample"]["shards"])==5
    assert p["sample"]["max_forks_per_world"]==1
    return p


def torus_distance(cell_a,cell_b,width,height):
    xa,ya=cell_a
    xb,yb=cell_b
    dx=abs(xa-xb)
    dy=abs(ya-yb)
    return min(dx,width-dx)+min(dy,height-dy)


def isolated_neighbors(s,x,y):
    return all(s.grid[((y+dy)%s.height)*s.width+((x+dx)%s.width)]==-1
               for dx,dy in NEIGHBORS)


def choose_remote_move(world,candidate):
    """Returns (particle_id, destination(x,y), naturally_occupied) or None.

    The natural eight-site ring is untouched in both arms. The remote donor/
    destination is isolated at intervention time so as to minimize, NOT remove,
    spillovers from the off-center vacancy and moving particle.
    """
    s=world.store
    cx,cy=candidate["center"]
    index=s.grid[cy*s.width+cx]
    if index!=-1:
        if s.degree[index]!=0:
            return None
        if world.config.species[s.species[index]].move_probability<=0:
            return None
        for cell in range(s.width*s.height):
            if s.grid[cell]!=-1:
                continue
            x,y=cell % s.width,cell // s.width
            if torus_distance((cx,cy),(x,y),s.width,s.height)<7:
                continue
            if isolated_neighbors(s,x,y):
                return {
                    "source_center_state":"natural_occupied",
                    "particle_id":s.ids[index],
                    "original_position":[cx,cy],
                    "destination":[x,y],
                    "source_remote_cell":[x,y]
                }
        return None

    # Natural empty-center cohort: isolated native donor, deterministic ID order.
    for i,ident in enumerate(s.ids):
        if s.degree[i]!=0:
            continue
        if world.config.species[s.species[i]].move_probability<=0:
            continue
        x,y=s.xs[i],s.ys[i]
        if torus_distance((cx,cy),(x,y),s.width,s.height)<7:
            continue
        if isolated_neighbors(s,x,y):
            return {
                "source_center_state":"natural_empty",
                "particle_id":ident,
                "original_position":[x,y],
                "destination":[cx,cy],
                "source_remote_cell":[x,y]
            }
    return None


def relocate(w,id_,destination):
    """Pure source-condition intervention: no particle births, bonds or energy edits."""
    s=w.store
    i=s.index_of(id_)
    assert s.degree[i]==0
    dx,dy=destination
    assert 0<=dx<s.width and 0<=dy<s.height
    old=(s.xs[i],s.ys[i])
    oldcell=old[1]*s.width+old[0]
    newcell=dy*s.width+dx
    assert s.grid[newcell]==-1 and s.grid[oldcell]==i
    energy=w.energy()
    bonds=dict(s.bonds)
    rng=w.rng.fingerprint()
    draws=w.rng.draws
    s.grid[oldcell]=-1
    s.grid[newcell]=i
    s.xs[i],s.ys[i]=dx,dy
    w.check()
    assert w.energy()==energy
    assert s.bonds==bonds
    assert rng==w.rng.fingerprint() and draws==w.rng.draws
    assert len(s.ids)==sum(spec.count for spec in w.config.species)
    return old


def original_material_bonds(world):
    s=world.store
    return {
        tuple(sorted((s.ids[a],s.ids[b])))
        for a,b in s.bonds
    }


def follow_pair(source,candidate,choice,horizon=120,sham=False):
    assert horizon==120 or horizon<120  # short harness tests only
    assert choice is not None
    state=(source.state_hash_full(),source.rng.fingerprint(),source.rng.draws,
           source.energy(),source.step,source.bonds_formed_total,
           source.bonds_broken_total)
    edges=frozenset(candidate["edges"])
    assert len(edges)==7 and edges.issubset(original_material_bonds(source))
    assert candidate["stratum"] in ("empty","free_mobile")
    src_occ=choice["source_center_state"]
    assert (src_occ=="natural_empty")==(candidate["stratum"]=="empty")

    natural=clone_world(source)
    edited=clone_world(source)
    old=relocate(edited,choice["particle_id"],choice["destination"])
    assert list(old)==choice["original_position"]
    assert original_material_bonds(edited)==original_material_bonds(natural)
    assert edited.store.degree==natural.store.degree
    assert edited.store.energy==natural.store.energy
    assert edited.store.species==natural.store.species
    assert edited.rng.fingerprint()==natural.rng.fingerprint()
    assert edited.rng.draws==natural.rng.draws
    assert edited.energy()==natural.energy()

    if src_occ=="natural_empty":
        arms={"center_empty":natural,"center_occupied":edited}
    else:
        arms={"center_occupied":natural,"center_empty":edited}

    first_loss={arm:None for arm in arms}
    break_sinks={arm:BreakRecorder() for arm in arms}
    first_rng_divergence=None
    first_8_edge={arm:None for arm in arms}
    first_bond_events={arm:[] for arm in arms}
    start_step=source.step
    for name,w in arms.items():
        w.event_sink=break_sinks[name]

    # Material identities and original seven bonds are the same on both arms.
    ring_ids=set(candidate["ids"])
    assert len(ring_ids)==8
    for t in range(1,horizon+1):
        current_breaks={}
        for name,w in arms.items():
            w.advance(1)
            reported=break_sinks[name].pop(w.step)
            relevant=reported.intersection(edges)
            current_breaks[name]=relevant
            if t==1:
                first_bond_events[name]=[list(e) for e in sorted(relevant)]
            if first_loss[name] is None and relevant:
                first_loss[name]=t
            if first_8_edge[name] is None:
                # Explicitly independent from source-original seven continuity.
                s=w.store
                source_graph=original_material_bonds(w)
                all_cycle=set()
                cx,cy=candidate["center"]
                order=[
                    (-1,-1),(0,-1),(1,-1),(1,0),
                    (1,1),(0,1),(-1,1),(-1,0)
                ]
                member=[]
                for dx,dy in order:
                    ix=s.grid[((cy+dy)%s.height)*s.width+((cx+dx)%s.width)]
                    if ix==-1: break
                    member.append(s.ids[ix])
                if len(member)==8 and set(member)==ring_ids:
                    all_cycle={tuple(sorted((member[k],member[(k+1)%8])))
                               for k in range(8)}
                if (first_loss[name] is None and len(all_cycle)==8
                        and all_cycle.issubset(source_graph)
                        and edges.issubset(source_graph)):
                    first_8_edge[name]=t
        # Prove necessary null: same native original bond graph, same RNG before
        # the first break step => same seven-source-edge breaks at t=1.
        if t==1:
            assert current_breaks["center_empty"]==current_breaks["center_occupied"],(
                "M6 direct original-source-break invariant violated",candidate,choice,
                current_breaks
            )
        if first_rng_divergence is None and (
            arms["center_empty"].rng.fingerprint()!=arms["center_occupied"].rng.fingerprint()
            or arms["center_empty"].rng.draws!=arms["center_occupied"].rng.draws
        ):
            first_rng_divergence=t

    for w in arms.values():
        w.check()
    if sham:
        cloned=clone_world(source)
        cloned.advance(horizon)
        cloned.check()
        w=natural
        assert cloned.state_hash_full()==w.state_hash_full()
        assert cloned.rng.fingerprint()==w.rng.fingerprint()
        assert cloned.rng.draws==w.rng.draws
        assert cloned.energy()==w.energy()
        assert cloned.bonds_formed_total==w.bonds_formed_total
        assert cloned.bonds_broken_total==w.bonds_broken_total

    after=(source.state_hash_full(),source.rng.fingerprint(),source.rng.draws,
           source.energy(),source.step,source.bonds_formed_total,
           source.bonds_broken_total)
    assert after==state
    outcomes={}
    for name,w in arms.items():
        outcomes[name]={
            "original_first_bond_break_relative_tick":first_loss[name],
            "source_original_seven_edges_survive_10":first_loss[name] is None or first_loss[name]>10,
            "source_original_seven_edges_survive_30":first_loss[name] is None or first_loss[name]>30,
            "source_original_seven_edges_survive_60":first_loss[name] is None or first_loss[name]>60,
            "source_original_seven_edges_survive_120":first_loss[name] is None,
            "initial_next_step_original_edge_breaks":first_bond_events[name],
            "first_full_eight_edge_tick_from_fork":first_8_edge[name],
            "final_hash":w.state_hash_full(),
            "rng":w.rng.fingerprint(),
            "rng_draws":w.rng.draws,
            "energy":w.energy(),
            "dissipated":w.dissipated,
            "formed":w.bonds_formed_total,
            "broken":w.bonds_broken_total
        }
    return {
        "fork_tick":start_step,
        "original_world_hash":state[0],
        "original_rng_fingerprint":state[1],
        "original_rng_draws":state[2],
        "source_material_ids":list(candidate["ids"]),
        "original_source_edges":[list(x) for x in sorted(edges)],
        "source_center":list(candidate["center"]),
        "source_natural_center_state":src_occ,
        "relocation":choice,
        "first_rng_divergence_tick":first_rng_divergence,
        "same_first_step_source_breaks":(
            first_bond_events["center_empty"]==first_bond_events["center_occupied"]),
        "outcomes":outcomes
    }


def study_seed(seed,p,natural):
    parent=create_natural(seed,p["sample"]["density"],natural)
    first_candidate_seen=False
    failed_remote_candidates=0
    for t in range(1,p["sample"]["parent_horizon_ticks"]+1):
        parent.advance(1)
        candidates=sorted(precursor_candidates(parent),key=lambda c:(c["center"],c["ids"]))
        if not candidates:
            continue
        first_candidate_seen=True
        for cand in candidates:
            if cand["stratum"] not in ("empty","free_mobile"):
                continue
            choice=choose_remote_move(parent,cand)
            if choice is None:
                failed_remote_candidates+=1
                continue
            experiment=follow_pair(parent,cand,choice,
                                   p["sample"]["fork_horizon_ticks"],
                                   sham=(seed==p["sample"]["seed_start"]))
            assert experiment["same_first_step_source_breaks"]
            return {
                "seed":seed, "eligible":True, "selected_tick":t,
                "first_candidate_ever_seen":first_candidate_seen,
                "failed_remote_candidates":failed_remote_candidates,
                "pair":experiment
            }
    return {
        "seed":seed, "eligible":False,
        "reason":"remote_unavailable" if first_candidate_seen else "no_native_seven_edge_precursor",
        "failed_remote_candidates":failed_remote_candidates
    }


def summarize(worlds,p):
    assert len(worlds)==p["sample"]["seeds"]
    assert [w["seed"] for w in worlds]==list(range(p["sample"]["seed_start"],p["sample"]["seed_end_inclusive"]+1))
    select=[w for w in worlds if w["eligible"]]
    counts=Counter(w.get("reason","eligible") for w in worlds)
    strata={}
    comparisons={}
    for cohort in ("all","natural_empty","natural_occupied"):
        group=select if cohort=="all" else [
            w for w in select if w["pair"]["source_natural_center_state"]==cohort
        ]
        pairs=len(group)
        div=sum(w["pair"]["first_rng_divergence_tick"] is not None for w in group)
        pre=sum(w["pair"]["first_rng_divergence_tick"]==1 for w in group)
        comp={
            "pairs":pairs,"worlds":pairs,
            "rng_diverged_by_120_worlds":div,
            "rng_diverged_at_first_tick_worlds":pre,
            "all_first_step_original_breaks_match":all(w["pair"]["same_first_step_source_breaks"] for w in group),
        }
        for h in HORIZONS:
            yes=0
            no=0
            both=0
            neither=0
            for w in group:
                outcomes=w["pair"]["outcomes"]
                a=outcomes["center_occupied"][f"source_original_seven_edges_survive_{h}"]
                b=outcomes["center_empty"][f"source_original_seven_edges_survive_{h}"]
                if a and not b: yes+=1
                elif b and not a: no+=1
                elif a and b: both+=1
                else: neither+=1
            assert yes+no+both+neither==pairs
            comp[f"horizon_{h}"]={
                "occupied_survives":yes+both,
                "empty_survives":no+both,
                "both_survive":both,"neither_survive":neither,
                "discordant_occupied_only":yes,
                "discordant_empty_only":no,
                "paired_occupied_minus_empty_survival":round((yes-no)/pairs,6) if pairs else None,
                "paired_effect_not_pure_local_caused_by_remote_move_and_rng_coupling":True
            }
        strata[cohort]=comp
    return {
        "worlds":len(worlds),"paired_source_worlds":len(select),
        "selection_counts":dict(counts),
        "source_state_subcohorts":strata,
        "decision":(
            "no_selected_pairs" if not select
            else "descriptive_paired_position_intervention_complete"
        ),
        "direct_one_step_edge_break_invariant":"passed" if all(
            w["pair"]["same_first_step_source_breaks"] for w in select) else "FAILED",
        "non_claims":"Contrasts at >1 tick are consequences of moving a free particle between center and remote place, including changed move/formation opportunities and possibly desynchronized RNG draws; cannot alone establish biological feedback, membrane self-maintenance or causal local-center effect."
    }


def run_shard(start,end):
    p=protocol()
    assert {"start":start,"end":end} in p["sample"]["shards"]
    natural=natural_protocol()
    worlds=[]
    for seed in range(start,end+1):
        w=study_seed(seed,p,natural)
        worlds.append(w)
        if (seed-start+1)%20==0:
            print(f"M615_PROGRESS {start}-{end} seed={seed} pairs={sum(x['eligible'] for x in worlds)}",flush=True)
    assert len(worlds)==end-start+1
    result={
        "schema":"alife-m6-15-paired-center-shard-v1",
        "descriptor":{"start":start,"end":end},
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":worlds,
        "unchanged_M6_physics":True
    }
    path=BASE/"shards"/f"enriched-{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M615_SHARD="+json.dumps({"start":start,"end":end,"worlds":len(worlds),
          "pairs":sum(w["eligible"] for w in worlds)},sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("*.json"))
    assert len(files)==len(p["sample"]["shards"])
    found=[]
    worlds=[]
    for path in files:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m6-15-paired-center-shard-v1"
        assert chunk["protocol_sha256"]==sha256(PROTOCOL.read_bytes()).hexdigest()
        assert chunk["unchanged_M6_physics"] is True
        desc=chunk["descriptor"]
        assert desc in p["sample"]["shards"] and desc not in found
        found.append(desc)
        assert [w["seed"] for w in chunk["worlds"]]==list(range(desc["start"],desc["end"]+1))
        worlds+=chunk["worlds"]
    assert all(x in found for x in p["sample"]["shards"])
    worlds.sort(key=lambda x:x["seed"])
    summary=summarize(worlds,p)
    output={
        "schema":"alife-m6-15-paired-center-results-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":worlds,"summary":summary,
        "all_shards_complete":True,
        "source_M6_physics_unchanged":True
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("M615_SUMMARY="+json.dumps(summary,sort_keys=True),flush=True)
    print("M615_MERGED="+str(len(worlds)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)
    shard=sub.add_parser("shard")
    shard.add_argument("--start",type=int,required=True)
    shard.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    args=parser.parse_args()
    if args.command=="shard":
        run_shard(args.start,args.end)
    else:
        merge()


if __name__=="__main__":
    main()
