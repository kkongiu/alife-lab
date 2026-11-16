"""M7.4 matched natural source-cohort energy conduction forks.

Scientific distinction: total-world new bonds are NOT same-material offspring.
Here *root* IDs and their original bonds are fixed before interventions.
No hand-crafted sources, particles, extra bonds, or active repair laws.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from alife.structures import components
from alife.world import World
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import config_for, energy_transfer, bond_pairs
from tools.m7_2_energy_distribution import contacts, ledger

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_4_material"
PROTOCOL=BASE/"protocol.json"
OUTPUT=BASE/"results.json"
ARMS=("no_transfer","bond_only","all_contacts")
HORIZON=120


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-4-native-material-cohort-paired-forks-v1"
    assert p["status"]=="preregistered_before_implementation_and_results"
    assert p["design"]["source_seeds"]=={"start":22001,"end_inclusive":22160,"count":160}
    assert p["design"]["followup_ticks"]==HORIZON
    assert len(p["design"]["shards"])==4
    return p


def native_pairs(w):
    s=w.store
    return {tuple(sorted((s.ids[a],s.ids[b]))) for a,b in s.bonds}


def source_candidates(w):
    """Choose first eligible maximal naturally bonded component, no outcomes consulted."""
    s=w.store
    choices=[]
    for indices,bonds in components(s):
        if not (3<=len(indices)<=10 and len(bonds)>=2):
            continue
        if not any(s.degree[i]<w.max_bonds[s.species[i]] for i in indices):
            continue
        ids=tuple(sorted(s.ids[i] for i in indices))
        edges=tuple(sorted(tuple(sorted((s.ids[a],s.ids[b]))) for a,b in bonds))
        assert len(edges)>=2
        choices.append({"ids":ids,"edges":edges,"size":len(ids),"edges_n":len(edges)})
    return sorted(choices,key=lambda x:x["ids"])


class EventTape:
    """Records native events, never changes physics or reads RNG."""
    def __init__(self):
        self.pending=[]
    def emit(self,event):
        self.pending.append((
            event.step+1,event.kind,
            tuple(sorted((event.id_a,event.id_b)))
        ))
    def pop(self,tick):
        events=[(kind,pair) for t,kind,pair in self.pending if t==tick]
        self.pending=[entry for entry in self.pending if entry[0]!=tick]
        return events


def coherent_root_size(w,original_ids):
    """Size only if all original material IDs are still connected to each other."""
    material=set(original_ids)
    for indices,_ in components(w.store):
        present={w.store.ids[i] for i in indices}
        if material.issubset(present):
            return len(present)
    return None


def route_source(w,arm,material_ids,original_edges):
    """Exact M7.3 transfer with classified source flow; same native-energy outcomes.

    All counts are event counts; energy can circulate multiple times. The source
    internal count does not prove net energy inflow (both endpoints are original).
    """
    if arm=="no_transfer":
        return (0,0,0,0,0,0)
    s=w.store
    source=set(material_ids)
    src_energies=tuple(s.energy)
    remaining=list(src_energies)
    before=w.energy()
    old_rng=w.rng.fingerprint(),w.rng.draws
    delta=[0]*len(src_energies)
    originals=set(s.bonds)
    pairs=bond_pairs(w) if arm=="bond_only" else contacts(s)
    n_internal=n_boundary_in=n_boundary_out=n_original=total=0
    bondroute=nonbondroute=0
    for i,j in pairs:
        if src_energies[i]-src_energies[j]>=2:
            donor,recipient=i,j
        elif src_energies[j]-src_energies[i]>=2:
            donor,recipient=j,i
        else:
            continue
        if remaining[donor]<1:
            continue
        remaining[donor]-=1
        delta[donor]-=1
        delta[recipient]+=1
        total+=1
        a=s.ids[donor] in source
        b=s.ids[recipient] in source
        if a and b:n_internal+=1
        if tuple(sorted((s.ids[donor],s.ids[recipient]))) in original_edges:
            n_original+=1
        elif a:n_boundary_out+=1
        elif b:n_boundary_in+=1
        if (i,j) in originals or (j,i) in originals:bondroute+=1
        else:nonbondroute+=1
    assert total==bondroute+nonbondroute
    for i,d in enumerate(delta):
        if d:s.energy[i]+=d
        assert s.energy[i]>=0
    assert w.energy()==before
    assert (w.rng.fingerprint(),w.rng.draws)==old_rng
    assert n_internal+n_boundary_in+n_boundary_out<=total
    if arm=="bond_only":assert nonbondroute==0
    return (total,n_internal,n_boundary_in,n_boundary_out,bondroute,n_original)


def follow(source,chosen,horizon=HORIZON,replay=False):
    """Three exact matched clones, none alter initial state or original laws."""
    originals=set(chosen["edges"])
    material=set(chosen["ids"])
    arms={name:clone_world(source) for name in ARMS}
    orig_hash=source.state_hash_full()
    orig_rng=(source.rng.fingerprint(),source.rng.draws)
    assert len({w.state_hash_full() for w in arms.values()})==1
    assert len({(w.rng.fingerprint(),w.rng.draws) for w in arms.values()})==1
    assert all(w.energy()==source.energy() for w in arms.values())
    assert originals.issubset(native_pairs(source))
    histories={}
    tapes={name:EventTape() for name in ARMS}
    for name,w in arms.items():
        w.event_sink=tapes[name]
        histories[name]={
            "first_original_break_tick":None,
            "first_incident_external_bond_tick":None,
            "incident_external_bond_events":0,
            "root_growth_ticks":0,
            "ever_coherent_growth":False,
            "first_coherent_growth_tick":None,
            "first_original_reclosure_tick":None,
            "root_original_edge_transfer_events":0,
            "root_internal_transfer_events":0,
            "root_boundary_energy_in_events":0,
            "root_boundary_energy_out_events":0,
            "all_transfer_events":0,
            "first_step_original_break_pairs":[],
            "snapshots":[],
        }
    for t in range(1,horizon+1):
        breaks_first={}
        for name,w in arms.items():
            w.advance(1)
            events=tapes[name].pop(w.step)
            breaking={edge for kind,edge in events if kind=="break"}
            formation={edge for kind,edge in events if kind=="form"}
            orig_broken=breaking&originals
            h=histories[name]
            if t==1:
                h["first_step_original_break_pairs"]=[list(edge) for edge in sorted(orig_broken)]
                breaks_first[name]=orig_broken
            if orig_broken and h["first_original_break_tick"] is None:
                h["first_original_break_tick"]=t
            external_events=[
                edge for edge in formation if (edge[0] in material)!=(edge[1] in material)
            ]
            if external_events:
                h["incident_external_bond_events"]+=len(external_events)
                if h["first_incident_external_bond_tick"] is None:
                    h["first_incident_external_bond_tick"]=t
            if h["first_original_break_tick"] is not None and h["first_original_reclosure_tick"] is None:
                # A previously broken edge can reform; presence in current
                # snapshot is not evidence for active self-repair.
                if originals.issubset(native_pairs(w)):
                    h["first_original_reclosure_tick"]=t
            flux=route_source(w,name,material,originals)
            h["all_transfer_events"]+=flux[0]
            h["root_internal_transfer_events"]+=flux[1]
            h["root_boundary_energy_in_events"]+=flux[2]
            h["root_boundary_energy_out_events"]+=flux[3]
            # Only currently existing ORIGINAL source pairs contribute.
            # The same material group can form other bonds later; they are
            # counted by internal, but not original-edge flows.
            h["root_original_edge_transfer_events"]+=flux[5]
            size=coherent_root_size(w,chosen["ids"])
            if size is not None and size>len(material):
                h["root_growth_ticks"]+=1
                h["ever_coherent_growth"]=True
                if h["first_coherent_growth_tick"] is None:
                    h["first_coherent_growth_tick"]=t
            if t in (1,10,30,60,120):
                ledger(w,w.configured_energy())
                h["snapshots"].append({
                    "relative_tick":t,
                    "coherent_root_component_size":size,
                    "all_original_source_edges_current":originals.issubset(native_pairs(w)),
                    "source_particle_energy_sum":sum(w.store.energy[w.store.index_of(i)] for i in material),
                    "source_internal_flow_events_cumulative":h["root_internal_transfer_events"],
                    "new_incident_external_bond_events_cumulative":h["incident_external_bond_events"]
                })
        if t==1:
            assert breaks_first["no_transfer"]==breaks_first["bond_only"]==breaks_first["all_contacts"],(
                "direct original bond break invariant",breaks_first
            )
    assert source.state_hash_full()==orig_hash
    assert (source.rng.fingerprint(),source.rng.draws)==orig_rng
    outcome={}
    for name,w in arms.items():
        w.check()
        ledger(w,w.configured_energy())
        h=histories[name]
        h["original_bonds_unbroken_120"]=h["first_original_break_tick"] is None
        h["coherent_growth_at_120"]=coherent_root_size(w,chosen["ids"]) is not None and (
            coherent_root_size(w,chosen["ids"])>len(material)
        )
        h["final_source_component_size"]=coherent_root_size(w,chosen["ids"])
        h["final_native_original_edges_present"]=sum(e in native_pairs(w) for e in originals)
        h["total_world_new_bonds"]=w.bonds_formed_total-source.bonds_formed_total
        h["final_energy"]=w.energy()
        h["final_rng_fingerprint"]=w.rng.fingerprint()
        h["final_rng_draws"]=w.rng.draws
        h["final_hash"]=w.state_hash_full()
        h["energy_ledger_pass"]=True
        outcome[name]=h
    if replay:
        # Same source fork cloned again from immutable source state.
        pair=clone_world(source)
        pair.advance(horizon)
        assert pair.state_hash_full()==arms["no_transfer"].state_hash_full()
        assert pair.rng.fingerprint()==arms["no_transfer"].rng.fingerprint()
        assert pair.rng.draws==arms["no_transfer"].rng.draws
        assert pair.energy()==arms["no_transfer"].energy()
    return outcome


def select_parent(seed,p):
    world=World.create(config_for(seed,"no_transfer"))
    assert not world.store.bonds
    initial_ids=tuple(world.store.ids)
    for _ in range(p["design"]["parent_search_ticks"]):
        world.advance(1)
        choices=source_candidates(world)
        if choices:
            chosen=choices[0]
            assert tuple(world.store.ids)==initial_ids
            return world,chosen
    return world,None


def study_seed(seed,p,replay=False):
    parent,chosen=select_parent(seed,p)
    if chosen is None:
        return {"seed":seed,"selected":False,"parent_ticks_examined":parent.step,
                "reason":"no_eligible_natural_source"}
    assert parent.step<=p["design"]["parent_search_ticks"]
    return {
        "seed":seed,"selected":True,
        "fork_tick":parent.step,
        "source":chosen,
        "source_start_energy":sum(parent.store.energy[parent.store.index_of(i)] for i in chosen["ids"]),
        "source_original_world_hash":parent.state_hash_full(),
        "source_original_rng":parent.rng.fingerprint(),
        "outcomes":follow(parent,chosen,p["design"]["followup_ticks"],replay=replay),
    }


def summarize(records,p):
    assert len(records)==160
    assert [r["seed"] for r in records]==list(range(22001,22161))
    selected=[r for r in records if r["selected"]]
    n=len(selected)
    def mean(values):
        return round(sum(values)/len(values),4) if values else None
    def count(name,property):
        return sum(r["outcomes"][name][property] for r in selected)
    by_arm={}
    for name in ARMS:
        by_arm[name]={
            "selected_source_worlds":n,
            "original_bond_unbroken_at_120":count(name,"original_bonds_unbroken_120"),
            "coherent_root_growth_at_120":count(name,"coherent_growth_at_120"),
            "ever_coherent_root_growth":count(name,"ever_coherent_growth"),
            "worlds_with_source_incident_external_bond":sum(
                r["outcomes"][name]["incident_external_bond_events"]>0 for r in selected),
            "mean_new_source_incident_bond_events":mean([
                r["outcomes"][name]["incident_external_bond_events"] for r in selected]),
            "mean_original_internal_flow_events":mean([
                r["outcomes"][name]["root_internal_transfer_events"] for r in selected]),
            "mean_exact_original_edge_transfer_events":mean([
                r["outcomes"][name]["root_original_edge_transfer_events"] for r in selected]),
            "mean_root_boundary_energy_in_events":mean([
                r["outcomes"][name]["root_boundary_energy_in_events"] for r in selected]),
            "mean_root_growth_ticks":mean([r["outcomes"][name]["root_growth_ticks"] for r in selected]),
            "mean_global_new_bonds":mean([
                r["outcomes"][name]["total_world_new_bonds"] for r in selected])
        }
    def discordant(prop,a="bond_only",b="no_transfer"):
        a_only=b_only=both=neither=0
        for r in selected:
            x=r["outcomes"][a][prop]
            y=r["outcomes"][b][prop]
            if x and not y:a_only+=1
            elif y and not x:b_only+=1
            elif x and y:both+=1
            else:neither+=1
        assert a_only+b_only+both+neither==n
        return {"bond_only_only":a_only,"no_transfer_only":b_only,
                "both":both,"neither":neither,"discordant":a_only+b_only,
                "bond_only_fraction_among_discordant":round(a_only/(a_only+b_only),6)
                    if a_only+b_only else None}
    growth=discordant("coherent_growth_at_120")
    survival=discordant("original_bonds_unbroken_120")
    def gate(table):
        if n<30 or table["discordant"]<20:
            return "not_met_or_underpowered"
        return ("passed" if 3*table["bond_only_only"]>=2*table["discordant"]
                else "not_met_or_underpowered")
    return {
        "source_seeds":160,"selected_native_source_worlds":n,
        "unselected_source_worlds":160-n,
        "by_arm":by_arm,
        "paired_causal_contrasts":{
            "growth_at_120":growth,"original_bond_unbroken_at_120":survival,
        },
        "preregistered_decisions":{
            "coherent_source_growth_benefit":gate(growth),
            "original_source_bond_survival_benefit":gate(survival),
            "minimum_selected":30,"minimum_discordant":20,
            "favorable_discordant_fraction_required":"2/3",
        },
        "limitations":"These are causal comparisons of an added bond-conduction REGIME on naturally selected cohorts. Equal initial microstates; future RNG diverges. Original native break probability unchanged. Coherent component growth is NOT reproduction, inheritance or metabolism. Observed incident bonds might involve external chemistry, not repairs to the original material."
    }


def run_shard(start,end):
    p=protocol()
    desc={"start":start,"end":end}
    assert desc in p["design"]["shards"]
    rows=[]
    replay_seeds=[]
    for seed in range(start,end+1):
        # First actually selected parent in each shard gets an independent
        # untouched natural no-transfer fork sham replay (not first raw seed).
        first_selected=not any(r["selected"] for r in rows)
        r=study_seed(seed,p,replay=first_selected)
        rows.append(r)
        if r["selected"] and first_selected:replay_seeds.append(seed)
        if (seed-start+1)%10==0:
            print(f"M74_PROGRESS shard={start}-{end} seed={seed} selected={sum(r['selected'] for r in rows)}",flush=True)
    assert len(rows)==end-start+1
    assert len(replay_seeds)<=1
    out={
        "schema":"alife-m7-4-material-shard-v1",
        "descriptor":desc,
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":rows,"sham_replay_source_seeds":replay_seeds,
        "original_core_unchanged":True
    }
    path=BASE/"shards"/f"{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M74_SHARD="+json.dumps({
        "start":start,"end":end,"source_worlds":len(rows),
        "selected":sum(r["selected"] for r in rows),
        "sham_replays":len(replay_seeds)},sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("*.json"))
    assert len(files)==4
    records=[]
    found=[]
    replay_seeds=[]
    for path in files:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m7-4-material-shard-v1"
        assert chunk["protocol_sha256"]==sha256(PROTOCOL.read_bytes()).hexdigest()
        assert chunk["original_core_unchanged"] is True
        d=chunk["descriptor"]
        assert d in p["design"]["shards"] and d not in found
        found.append(d)
        assert [r["seed"] for r in chunk["worlds"]]==list(range(d["start"],d["end"]+1))
        positives=[r for r in chunk["worlds"] if r["selected"]]
        assert len(chunk["sham_replay_source_seeds"])==(1 if positives else 0)
        if positives:assert chunk["sham_replay_source_seeds"]==[positives[0]["seed"]]
        records.extend(chunk["worlds"])
        replay_seeds.extend(chunk["sham_replay_source_seeds"])
    assert len(records)==160
    records.sort(key=lambda r:r["seed"])
    result={
        "schema":"alife-m7-4-complete-natural-material-cohort-forks-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "source_worlds":records,
        "replayed_first_selected_seed_per_shard":replay_seeds,
        "summary":summarize(records,p),
        "all_source_seeds_completed":True,
        "physics_src_unchanged":True
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M74_FINAL_SUMMARY="+json.dumps(result["summary"],sort_keys=True),flush=True)
    print("M74_SUCCESS="+str(len(records)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="cmd",required=True)
    one=sub.add_parser("shard")
    one.add_argument("--start",type=int,required=True)
    one.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    args=parser.parse_args()
    if args.cmd=="shard":run_shard(args.start,args.end)
    else:merge()


if __name__=="__main__":
    main()
