"""M7.5: mature/aged naturally formed native bond-cohort paired forks.

Pre-registered before this runner in campaigns/m7_5_mature/protocol.json.
No modification to historical src physics or prior native experiments.
An aged *edge substructure* does not necessarily make whole component old.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.structures import components
from alife.world import World
from tools.m6_5_ring_forks import clone_world
from tools.m7_2_energy_distribution import contacts, ledger
from tools.m7_3_bond_energy import config_for, bond_pairs
from tools.m7_4_material_feedback import EventTape, native_pairs, coherent_root_size

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_5_mature"
PFILE=BASE/"protocol.json"
OUT=BASE/"results.json"
ARMS=("no_transfer","bond_only","all_contacts")
HORIZON=120
CHECKPOINTS=(1,10,30,60,120)


def protocol():
    p=json.loads(PFILE.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-5-preregistered-aged-native-network-cohort-forks-v1"
    assert p["status"]=="frozen_before_runner_tests_and_results"
    assert p["design"]["seeds"]==320
    assert p["design"]["seeds_first"]==23001 and p["design"]["seeds_last"]==23320
    assert p["design"]["parent_scan_start_tick"]==120
    assert p["design"]["parent_scan_stop_tick"]==500
    assert p["design"]["followup_steps"]==HORIZON
    assert len(p["design"]["shards"])==8 and p["design"]["arms"]==list(ARMS)
    return p


def update_edge_ages(age, present, broken):
    """Post-step ages: a broken/reformed bond is NEW at that snapshot."""
    return {pair:(age.get(pair,0)+1 if pair not in broken else 1)
            for pair in present}


def candidate_networks(w,age):
    """Maximal native component satisfying prereg rules, sorted by material IDs."""
    s=w.store
    found=[]
    for members,bonds in components(s):
        if not (5<=len(members)<=16 and len(bonds)>=4):
            continue
        if not any(s.degree[i]<w.max_bonds[s.species[i]] for i in members):
            continue
        ids=tuple(sorted(s.ids[i] for i in members))
        edgeids=tuple(sorted(tuple(sorted((s.ids[a],s.ids[b]))) for a,b in bonds))
        ages=[age[pair] for pair in edgeids]
        old=sum(value>=20 for value in ages)
        if old<2:
            continue
        available=sum(s.degree[i]<w.max_bonds[s.species[i]] for i in members)
        assert len(edgeids)-len(ids)+1>=0
        found.append({
            "ids":ids, "edges":edgeids, "size":len(ids),
            "edges_n":len(edgeids), "original_edge_ages":ages,
            "original_edges_aged_at_least20":old,
            "max_aged_edge_ticks":max(ages),
            "spare_valence_member_count":available,
            "cyclomatic_number":len(edgeids)-len(ids)+1,
            "composition":dict(Counter(w.species_names[s.species[i]] for i in members)),
            "source_particle_energy_at_fork":sum(s.energy[i] for i in members),
            "source_original_bond_energy_at_fork":sum(s.bonds[(a,b)] for a,b in bonds),
            "source_ready_original_members_at_fork":sum(
                s.degree[i]<w.max_bonds[s.species[i]]
                and s.energy[i]>=w.formation_cost for i in members
            )
        })
    return sorted(found,key=lambda x:x["ids"])


def select_parent(seed,p):
    w=World.create(config_for(seed,"no_transfer"))
    assert not w.store.bonds and w.step==0
    initial_hash=w.state_hash_full()
    ages={}
    tape=EventTape()
    w.event_sink=tape
    for _ in range(p["design"]["parent_scan_stop_tick"]):
        before=w.rng.draws
        w.advance(1)
        events=tape.pop(w.step)
        broken={pair for kind,pair in events if kind=="break"}
        ages=update_edge_ages(ages,native_pairs(w),broken)
        assert w.rng.draws>=before
        if w.step<p["design"]["parent_scan_start_tick"]:
            continue
        eligible=candidate_networks(w,ages)
        if eligible:
            found=eligible[0]
            # Observer tape is not copied into fork worlds.
            w.check()
            w.event_sink=None
            return w,found,{"earliest_eligible_tick":w.step,"candidates_at_tick":len(eligible)}
    w.event_sink=None
    w.check()
    return w,None,{"earliest_eligible_tick":None,"candidates_at_tick":0,
                   "initial_hash":initial_hash}


def route_traced(w,arm,source_ids,original_edges):
    """Clone M7.3 transfer semantics, independently classify accepted flux.

    Return (all, current_source_internal, inward, outward, original_bond,
            other_source_internal, outside_outside).
    *Never* classify source/internal transfer as influx.
    """
    if arm=="no_transfer":return (0,0,0,0,0,0,0)
    s=w.store
    root=set(source_ids)
    original=frozenset(original_edges)
    before_hash_rng=(w.rng.fingerprint(),w.rng.draws)
    before_energy=w.energy()
    snapshot=tuple(s.energy)
    remaining=list(snapshot)
    delta=[0]*len(snapshot)
    edges=set(s.bonds)
    candidates=bond_pairs(w) if arm=="bond_only" else contacts(s)
    total=internal=inside=outside=on_original=other_internal=elsewhere=0
    for i,j in candidates:
        if snapshot[i]-snapshot[j]>=2:
            donor,recipient=i,j
        elif snapshot[j]-snapshot[i]>=2:
            donor,recipient=j,i
        else:
            continue
        if remaining[donor]<1:continue
        remaining[donor]-=1
        delta[donor]-=1
        delta[recipient]+=1
        total+=1
        di=s.ids[donor] in root
        ri=s.ids[recipient] in root
        pair=tuple(sorted((s.ids[donor],s.ids[recipient])))
        if di and ri:
            internal+=1
            if pair in original and ((i,j) in edges or (j,i) in edges):
                on_original+=1
            else:
                other_internal+=1
        elif not di and ri:inside+=1
        elif di and not ri:outside+=1
        else:elsewhere+=1
    for idx,change in enumerate(delta):
        if change:
            s.energy[idx]+=change
            assert s.energy[idx]>=0
    assert total==internal+inside+outside+elsewhere
    assert internal==on_original+other_internal
    if arm=="bond_only":
        assert all((i,j) in edges or (j,i) in edges for i,j in candidates)
    assert sum(s.energy)==sum(snapshot)
    assert w.energy()==before_energy
    assert (w.rng.fingerprint(),w.rng.draws)==before_hash_rng
    return (total,internal,inside,outside,on_original,other_internal,elsewhere)


def source_energy(w,source_ids):
    s=w.store
    indices=[s.index_of(i) for i in source_ids]
    return {
        "source_particle_energy":sum(s.energy[i] for i in indices),
        "source_original_members_energy_ready":sum(
            s.energy[i]>=w.formation_cost and
            s.degree[i]<w.max_bonds[s.species[i]] for i in indices
        ),
        "source_all_original_members_connected_component_size":coherent_root_size(w,source_ids)
    }


def follow(parent,chosen,replay=False):
    """Matched original states, standard 120 steps, observer-only root tracking."""
    ids=tuple(chosen["ids"])
    original=frozenset(chosen["edges"])
    root=set(ids)
    start_full_hash=parent.state_hash_full()
    start_rng=(parent.rng.fingerprint(),parent.rng.draws)
    initial_energy=parent.configured_energy()
    assert original.issubset(native_pairs(parent))
    ws={a:clone_world(parent) for a in ARMS}
    assert len({w.state_hash_full() for w in ws.values()})==1
    assert len({(w.rng.fingerprint(),w.rng.draws) for w in ws.values()})==1
    assert all(w.energy()==parent.energy() for w in ws.values())
    tape={a:EventTape() for a in ARMS}
    out={}
    for arm,w in ws.items():
        w.event_sink=tape[arm]
        out[arm]={
            "first_original_bond_break_relative_tick":None,
            "first_original_reclosure_relative_tick":None,
            "root_incident_new_bond_events":0,
            "root_incident_bond_events_before_any_original_break":0,
            "first_root_incident_relative_tick":None,
            "coherent_growth_ticks":0,
            "ever_coherent_growth":False,
            "first_coherent_growth_relative_tick":None,
            "flux_events_all":0,
            "flux_internal_root":0,
            "flux_into_root":0,
            "flux_out_of_root":0,
            "flux_on_original_bond":0,
            "flux_on_other_internal":0,
            "first_step_original_break_pairs":[],
            "checkpoints":[]
        }
    for t in range(1,HORIZON+1):
        current_first={}
        for arm,w in ws.items():
            w.advance(1)
            event=tape[arm].pop(w.step)
            h=out[arm]
            broken={pair for kind,pair in event if kind=="break"} & original
            if t==1:
                current_first[arm]=broken
                h["first_step_original_break_pairs"]=[list(edge) for edge in sorted(broken)]
            if broken and h["first_original_bond_break_relative_tick"] is None:
                h["first_original_bond_break_relative_tick"]=t
            newly_incident=[
                pair for kind,pair in event if kind=="form"
                and ((pair[0] in root)!=(pair[1] in root))
            ]
            if newly_incident:
                h["root_incident_new_bond_events"]+=len(newly_incident)
                if h["first_root_incident_relative_tick"] is None:
                    h["first_root_incident_relative_tick"]=t
                if h["first_original_bond_break_relative_tick"] is None:
                    h["root_incident_bond_events_before_any_original_break"]+=len(newly_incident)
            if (h["first_original_bond_break_relative_tick"] is not None
                    and h["first_original_reclosure_relative_tick"] is None
                    and original.issubset(native_pairs(w))):
                h["first_original_reclosure_relative_tick"]=t

            flux=route_traced(w,arm,root,original)
            for k,v in zip((
                "flux_events_all","flux_internal_root","flux_into_root",
                "flux_out_of_root","flux_on_original_bond",
                "flux_on_other_internal"
            ),flux):
                h[k]+=v
            size=coherent_root_size(w,ids)
            if size is not None and size>len(root):
                h["coherent_growth_ticks"]+=1
                h["ever_coherent_growth"]=True
                if h["first_coherent_growth_relative_tick"] is None:
                    h["first_coherent_growth_relative_tick"]=t
            if t in CHECKPOINTS:
                ledger(w,initial_energy)
                h["checkpoints"].append({
                    "relative_tick":t,
                    **source_energy(w,ids),
                    "original_bonds_currently_present":sum(edge in native_pairs(w) for edge in original),
                    "root_incident_bonds_formed_cumulative":h["root_incident_new_bond_events"],
                    "original_edge_flow_cumulative":h["flux_on_original_bond"],
                    "root_net_boundary_flow_cumulative":h["flux_into_root"]-h["flux_out_of_root"]
                })
        if t==1:
            assert current_first["no_transfer"]==current_first["bond_only"]==current_first["all_contacts"],(
                "first step break invariant",current_first
            )
    assert parent.state_hash_full()==start_full_hash
    assert (parent.rng.fingerprint(),parent.rng.draws)==start_rng
    for arm,w in ws.items():
        w.check()
        ledger(w,initial_energy)
        h=out[arm]
        size=coherent_root_size(w,ids)
        h["coherent_growth_at_120"]=size is not None and size>len(root)
        h["all_original_bonds_never_broken_120"]=h["first_original_bond_break_relative_tick"] is None
        h["source_final_coherent_component_size"]=size
        h["world_new_bonds_120"]=w.bonds_formed_total-parent.bonds_formed_total
        h["source_net_passive_flow"]=h["flux_into_root"]-h["flux_out_of_root"]
        h["energy_ledger_verified"]=True
        h["final"]={
            "full_hash":w.state_hash_full(),
            "rng":w.rng.fingerprint(),
            "draws":w.rng.draws,
            "energy":w.energy(),
            "injected":w.injected,
            "unabsorbed":w.unabsorbed,
            "dissipated":w.dissipated,
            "formed":w.bonds_formed_total,
            "broken":w.bonds_broken_total
        }
    if replay:
        bare=clone_world(parent)
        bare.advance(HORIZON)
        bare.check()
        assert bare.state_hash_full()==ws["no_transfer"].state_hash_full()
        assert bare.rng.fingerprint()==ws["no_transfer"].rng.fingerprint()
        assert bare.rng.draws==ws["no_transfer"].rng.draws
        assert bare.energy()==ws["no_transfer"].energy()
    return out


def study(seed,p,replay=False):
    w,source,selection=select_parent(seed,p)
    if source is None:
        return {"seed":seed,"selected":False,
                "ticks_scanned":w.step,"reason":"no_aged_native_network",
                "candidate_count":0}
    return {
        "seed":seed,"selected":True,
        "fork_tick":w.step,
        "source":source,
        "source_fork_full_hash":w.state_hash_full(),
        "source_fork_rng":w.rng.fingerprint(),
        "source_fork_draws":w.rng.draws,
        "selection":selection,
        "outcomes":follow(w,source,replay=replay)
    }


def paired_table(selected,metric,a="bond_only",b="no_transfer"):
    a_only=b_only=both=neither=0
    for item in selected:
        x=bool(item["outcomes"][a][metric])
        y=bool(item["outcomes"][b][metric])
        if x and not y:a_only+=1
        elif y and not x:b_only+=1
        elif x and y:both+=1
        else:neither+=1
    assert a_only+b_only+both+neither==len(selected)
    n=a_only+b_only
    return {
        "favorable_bond_only":a_only,
        "favorable_no_transfer":b_only,
        "both":both,"neither":neither,
        "discordant":n,
        "favorable_fraction":round(a_only/n,6) if n else None
    }


def summarize(records,p):
    assert len(records)==320
    assert [r["seed"] for r in records]==list(range(23001,23321))
    sel=[r for r in records if r["selected"]]
    n=len(sel)
    def avg(values):return round(sum(values)/len(values),4) if values else None
    arms={}
    for a in ARMS:
        arms[a]={
            "selected_worlds":n,
            "coherent_growth_at_120":sum(x["outcomes"][a]["coherent_growth_at_120"] for x in sel),
            "ever_coherent_growth":sum(x["outcomes"][a]["ever_coherent_growth"] for x in sel),
            "original_bonds_unbroken_120":sum(x["outcomes"][a]["all_original_bonds_never_broken_120"] for x in sel),
            "mean_incident_bonds":avg([x["outcomes"][a]["root_incident_new_bond_events"] for x in sel]),
            "mean_incident_before_first_break":avg([x["outcomes"][a]["root_incident_bond_events_before_any_original_break"] for x in sel]),
            "mean_global_new_bonds":avg([x["outcomes"][a]["world_new_bonds_120"] for x in sel]),
            "mean_original_edge_flows":avg([x["outcomes"][a]["flux_on_original_bond"] for x in sel]),
            "mean_internal_flows":avg([x["outcomes"][a]["flux_internal_root"] for x in sel]),
            "mean_boundary_in":avg([x["outcomes"][a]["flux_into_root"] for x in sel]),
            "mean_boundary_out":avg([x["outcomes"][a]["flux_out_of_root"] for x in sel]),
            "mean_boundary_net":avg([x["outcomes"][a]["source_net_passive_flow"] for x in sel])
        }
    growth=paired_table(sel,"coherent_growth_at_120")
    survival=paired_table(sel,"all_original_bonds_never_broken_120")
    def gate(x):
        if n<40 or x["discordant"]<25:
            return "not_met_or_underpowered"
        return "passed" if 3*x["favorable_bond_only"]>=2*x["discordant"] else "not_met_or_underpowered"
    groups=Counter()
    birth=Counter()
    for x in sel:
        source=x["source"]
        groups["size5to8" if source["size"]<=8 else "size9to16"]+=1
        groups["cyclic" if source["cyclomatic_number"]>=1 else "tree"]+=1
        birth[str(x["fork_tick"]//50*50)]+=1
    return {
        "source_seeds":320,"selected_mature_network_worlds":n,
        "unselected_worlds":320-n,
        "source_structure_strata":dict(groups),
        "source_fork_50_tick_buckets":dict(birth),
        "mean_source_size":avg([r["source"]["size"] for r in sel]),
        "mean_old_edges_per_source":avg([r["source"]["original_edges_aged_at_least20"] for r in sel]),
        "per_arm":arms,
        "paired_comparisons":{
            "coherent_growth_at_120":growth,
            "all_original_bonds_unbroken_120":survival
        },
        "preregistered_decisions":{
            "coherent_growth_benefit":gate(growth),
            "original_bond_survival_benefit":gate(survival),
            "minimum_sources":40,
            "minimum_discordant":25,
            "minimum_favorable_discordance":"2/3"
        },
        "caveats":"The age requirement establishes two aged original edges, not the lifetime of the full selected component. Causal comparisons are of the applied conduction regime with future global RNG stream divergence, not a proven biological repair or metabolism mechanism. Coherent growth is not a descendant."
    }


def run_shard(start,end):
    p=protocol()
    d={"start":start,"end":end}
    assert d in p["design"]["shards"]
    records=[]
    sham_replay_seed=None
    for seed in range(start,end+1):
        item=study(seed,p,replay=(sham_replay_seed is None))
        records.append(item)
        if item["selected"] and sham_replay_seed is None:sham_replay_seed=seed
        if (seed-start+1)%5==0:
            print(f"M75_PROGRESS shard={start}-{end} seed={seed} selected={sum(x['selected'] for x in records)}",flush=True)
    assert len(records)==end-start+1
    result={
        "schema":"alife-m7-5-mature-source-shard-v1",
        "descriptor":d,
        "protocol_sha256":sha256(PFILE.read_bytes()).hexdigest(),
        "worlds":records,
        "sham_replayed_first_selected_seed":sham_replay_seed,
        "original_core_unchanged":True
    }
    path=BASE/"shards"/f"seeds-{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M75_SHARD="+json.dumps({
        "start":start,"end":end,"source_worlds":len(records),
        "selected":sum(x["selected"] for x in records),
        "sham_replayed_first_selected_seed":sham_replay_seed
    },sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("seeds-*.json"))
    assert len(files)==len(p["design"]["shards"]),(len(files),"need exactly eight")
    seen=[]
    records=[]
    sham=[]
    for file in files:
        chunk=json.loads(file.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m7-5-mature-source-shard-v1"
        assert chunk["protocol_sha256"]==sha256(PFILE.read_bytes()).hexdigest()
        assert chunk["original_core_unchanged"] is True
        d=chunk["descriptor"]
        assert d in p["design"]["shards"] and d not in seen
        seen.append(d)
        rows=chunk["worlds"]
        assert [r["seed"] for r in rows]==list(range(d["start"],d["end"]+1))
        first=next((r["seed"] for r in rows if r["selected"]),None)
        assert chunk["sham_replayed_first_selected_seed"]==first
        records.extend(rows)
        if first is not None:sham.append(first)
    assert all(d in seen for d in p["design"]["shards"])
    records.sort(key=lambda r:r["seed"])
    summary=summarize(records,p)
    merged={
        "schema":"alife-m7-5-320-native-aged-cohort-result-v1",
        "protocol_sha256":sha256(PFILE.read_bytes()).hexdigest(),
        "worlds":records,
        "sham_replayed_first_selected_seed_per_nonempty_shard":sham,
        "summary":summary,
        "all_320_source_seed_worlds_present":True,
        "all_original_physics_unchanged":True
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(merged,indent=2)+"\n",encoding="utf-8")
    print("M75_FINAL_SUMMARY="+json.dumps(summary,sort_keys=True),flush=True)
    print("M75_SUCCESS="+str(len(records)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    commands=parser.add_subparsers(dest="cmd",required=True)
    run=commands.add_parser("shard")
    run.add_argument("--start",type=int,required=True)
    run.add_argument("--end",type=int,required=True)
    commands.add_parser("merge")
    args=parser.parse_args()
    if args.cmd=="shard":run_shard(args.start,args.end)
    else:merge()


if __name__=="__main__":
    main()
