"""M7.11 — natural aged native ring break, reclosure and passive redundancy.

M6/M7.3 ORIGINAL native World.advance and M7.3 energy_transfer untouched.
Select a naturally formed unbranched 4/6/8 material ring which has retained
EXACT original bonds without any real native BREAK event for >=20 ticks.
ONE natural ring per heldout numeric seed, first eligible by time and IDs.

Fork four counterfactuals with/without ONE selected cut and with/without
deliberately suppressed energy transfers on surviving original ring edges.
Refill ALL chemical bond energy on excision, no RNG draw or added dissipation.
No synthetic repair law, no organism claim.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.structures import components
from tools.m6_4_cycles import analyze_cycle
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import config_for,energy_transfer,bond_pairs
from tools.m7_2_energy_distribution import ledger
from tools.m7_4_material_feedback import EventTape,native_pairs,coherent_root_size
from alife.world import World

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_11_ring_resilience"
PFILE=BASE/"protocol.json"
OUT=BASE/"results.json"
OLD_M73=ROOT/"tools/m7_3_bond_energy.py"
OLD_M64=ROOT/"tools/m6_4_cycles.py"
FIRST,LAST=29001,29640
HORIZON=120
SCAN_LIMIT=600
MIN_AGE=20
CHECKPOINTS=(1,10,30,60,120)
ARMS=("intact_normal","intact_ring_conduction_suppressed",
      "opened_normal","opened_surviving_ring_conduction_suppressed")
OPEN=("opened_normal","opened_surviving_ring_conduction_suppressed")


def protocol():
    p=json.loads(PFILE.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-11-natural-aged-cycle-fault-tolerance-v1"
    assert p["status"]=="frozen_before_runner_tests_and_results"
    s=p["sample"]
    assert (s["seed_first"],s["seed_last"],s["seed_count"])==(FIRST,LAST,640)
    assert (s["first_scan_tick"],s["last_scan_tick"],s["minimum_continuous_ring_age"])==(120,600,20)
    assert len(s["shards"])==16
    assert [k for d in s["shards"] for k in range(d["start"],d["end"]+1)]==list(range(FIRST,LAST+1))
    assert p["interventions"]["followup_ticks"]==HORIZON
    assert p["interventions"]["checkpoints"]==list(CHECKPOINTS)
    assert p["integrity"]["no_change_to_master_core_src_or_prior_M6_M7"]
    return p


def provenance():
    return {
        "m711_preregistered_protocol_sha256":sha256(PFILE.read_bytes()).hexdigest(),
        "unchanged_original_M73_native_conduction_sha256":sha256(OLD_M73.read_bytes()).hexdigest(),
        "unchanged_original_M64_cycle_observer_sha256":sha256(OLD_M64.read_bytes()).hexdigest()
    }


def rings_now(world):
    """Use exactly original M6.4 graph-based simple cycle recognition."""
    found=[]
    s=world.store
    for members,edges in components(s):
        if len(members) not in (4,6,8):continue
        ring=analyze_cycle(s,members,edges,world.species_names)
        if ring is None:continue
        assert len(ring["ids"])==len(ring["edges"])==len(members)
        assert len(ring["ids"])%2==0
        found.append({
            "ids":tuple(ring["ids"]),
            "edges":tuple(sorted(ring["edges"])),
            "size":ring["size"],
            "exact":ring["exact"],
            "composition":dict(ring["composition"])
        })
    return sorted(found,key=lambda x:x["ids"])


def scan_first_native_aged_ring(seed):
    """No retrospectively selected bonds, worlds, ring ages or future outcomes."""
    w=World.create(config_for(seed,"no_transfer"))
    assert w.step==0 and not w.store.bonds
    original_seed_hash=w.state_hash_full()
    ages={}
    seen_any=False
    observed_episode_count=0
    tape=EventTape()
    w.event_sink=tape
    for tick in range(1,SCAN_LIMIT+1):
        w.advance(1)
        events=tape.pop(w.step)
        broken={pair for kind,pair in events if kind=="break"}
        energy_transfer(w,"bond_only")
        records=rings_now(w)
        if records:seen_any=True
        next_ages={}
        for rec in records:
            key=(rec["ids"],rec["edges"])
            if key not in ages or any(edge in broken for edge in rec["edges"]):
                age=1
                observed_episode_count+=1
            else:
                age=ages[key]+1
            next_ages[key]=age
            rec["continuous_snapshot_age"]=age
        ages=next_ages
        if tick>=120:
            candidates=[r for r in records if r["continuous_snapshot_age"]>=MIN_AGE]
            if candidates:
                chosen=min(candidates,key=lambda x:x["ids"])
                assert w.step==tick
                assert set(chosen["edges"]).issubset(native_pairs(w))
                w.event_sink=None
                w.check()
                ledger(w,w.configured_energy())
                return w,chosen,{
                    "seed":seed,"selected":True,
                    "selected_tick":tick,
                    "candidate_aged_rings_same_tick":len(candidates),
                    "seen_any_native_cycle":True,
                    "native_ring_episodes_seen":observed_episode_count,
                    "original_initial_full_hash":original_seed_hash
                }
    w.event_sink=None
    w.check()
    return None,None,{
        "seed":seed,"selected":False,
        "reason":"native_cycles_observed_but_none_aged_20_by_600" if seen_any else "no_native_simple_4_6_8_ring_by_600",
        "seen_any_native_cycle":seen_any,
        "native_ring_episodes_seen":observed_episode_count,
        "scan_ticks":SCAN_LIMIT,
        "original_initial_full_hash":original_seed_hash
    }


def excise_refund(world,pair):
    """Remove exactly one native bond and refund all its already stored energy."""
    i,j=sorted((world.store.index_of(identifier) for identifier in pair))
    assert (i,j) in world.store.bonds
    before=(world.energy(),world.dissipated,world.rng.fingerprint(),world.rng.draws)
    original=world.store.bonds[(i,j)]
    world.store.remove_bond(i,j)
    world.store.energy[i]+=(original+1)//2
    world.store.energy[j]+=original//2
    assert (world.energy(),world.dissipated,world.rng.fingerprint(),world.rng.draws)==before
    assert tuple(sorted(pair)) not in native_pairs(world)
    world.check()
    ledger(world,world.configured_energy())
    return {
        "native_bond_energy_fully_refunded":original,
        "refunded_lower_material_id":(original+1)//2,
        "refunded_higher_material_id":original//2,
        "zero_extra_dissipation_or_rng":True
    }


def connected_original_ids(world,ids):
    """All ring material IDs share one current bonded component, possibly via outsiders."""
    return coherent_root_size(world,ids) is not None


def induced_original_connected(world,ids):
    """More stringent: all IDs connected using ONLY edges among these original IDs."""
    selected=set(ids)
    adjacency={i:set() for i in selected}
    for a,b in native_pairs(world):
        if a in selected and b in selected:
            adjacency[a].add(b)
            adjacency[b].add(a)
    visited={min(selected)}
    stack=list(visited)
    while stack:
        a=stack.pop()
        for b in adjacency[a]:
            if b not in visited:
                visited.add(b)
                stack.append(b)
    return len(visited)==len(selected)


def transport_with_optional_suppression(world,arm,original_edges,cut):
    """Original M7.3 snapshot donor budget and ID order, just skipping named edges."""
    suppressed=set()
    if arm=="intact_ring_conduction_suppressed":
        suppressed=set(original_edges)
    elif arm=="opened_surviving_ring_conduction_suppressed":
        suppressed=set(original_edges)-{cut}
    old=(world.energy(),world.rng.fingerprint(),world.rng.draws)
    store=world.store
    original=tuple(store.energy)
    remaining=list(original)
    delta=[0]*len(original)
    proposals=0
    original_edge_transfers=0
    cut_edge_transfers=0
    ring_allowed_transfers=0
    for ia,ib in bond_pairs(world):
        pair=tuple(sorted((store.ids[ia],store.ids[ib])))
        if pair in suppressed:continue
        if original[ia]-original[ib]>=2:donor,recipient=ia,ib
        elif original[ib]-original[ia]>=2:donor,recipient=ib,ia
        else:continue
        if remaining[donor]<1:continue
        remaining[donor]-=1
        delta[donor]-=1
        delta[recipient]+=1
        proposals+=1
        if pair in original_edges:
            original_edge_transfers+=1
            ring_allowed_transfers+=1
        if pair==cut:cut_edge_transfers+=1
    assert sum(delta)==0
    if suppressed:
        for idx,change in enumerate(delta):
            store.energy[idx]+=change
        assert all(e>=0 for e in store.energy)
    else:
        official=energy_transfer(world,"bond_only")
        assert official==(proposals,proposals,0)
        assert store.energy==[v+d for v,d in zip(original,delta)]
    assert (world.energy(),world.rng.fingerprint(),world.rng.draws)==old
    assert not (set(original_edges) & suppressed)==set() or original_edge_transfers==0
    return {
        "native_original_ring_edges_conduction":original_edge_transfers,
        "native_cut_pair_conduction":cut_edge_transfers,
        "all_native_bond_energy_transfers":proposals
    }


def follow_ring(parent,ring,validation=False):
    """Four 120-tick trajectories from first naturally aged ring."""
    ids=tuple(ring["ids"])
    edges=set(ring["edges"])
    cut=min(edges)
    assert len(ids)==len(edges) in (4,6,8)
    assert edges.issubset(native_pairs(parent))
    original_hash=parent.state_hash_full()
    original_rng=parent.rng.fingerprint(),parent.rng.draws
    worlds={arm:clone_world(parent) for arm in ARMS}
    assert len({w.state_hash_full() for w in worlds.values()})==1
    assert len({(w.rng.fingerprint(),w.rng.draws) for w in worlds.values()})==1
    excisions={arm:excise_refund(worlds[arm],cut) for arm in OPEN}
    assert excisions[OPEN[0]]==excisions[OPEN[1]]
    assert worlds[OPEN[0]].state_hash_full()==worlds[OPEN[1]].state_hash_full()
    assert worlds["intact_normal"].state_hash_full()==worlds["intact_ring_conduction_suppressed"].state_hash_full()
    assert len(native_pairs(worlds[OPEN[0]])&edges)==len(edges)-1
    assert connected_original_ids(worlds[OPEN[0]],ids)
    assert induced_original_connected(worlds[OPEN[0]],ids)
    assert len({w.energy() for w in worlds.values()})==1
    assert all((w.rng.fingerprint(),w.rng.draws)==original_rng for w in worlds.values())

    tapes={arm:EventTape() for arm in ARMS}
    outcome={}
    for arm,w in worlds.items():
        w.event_sink=tapes[arm]
        outcome[arm]={
            "first_original_ring_edge_break_tick":None,
            "first_OTHER_ring_edge_break_tick":None,
            "first_selected_cut_edge_real_form_tick":None,
            "first_anytime_cut_edge_reclosure_tick":None,
            "exact_cut_edge_reformed_before_any_other_original_break":False,
            "selected_cut_reclosure_event_count":0,
            "any_original_ring_edge_break_events":0,
            "ring_original_edge_transfer_events":0,
            "cut_material_pair_transfer_events":0,
            "all_world_bond_transfer_events":0,
            "first_native_step_hash_before_transport":None,
            "first_native_step_rng_before_transport":None,
            "first_native_step_ring_break_event_pairs":[],
            "checkpoints":[]
        }
    for relative in range(1,HORIZON+1):
        for arm,w in worlds.items():
            w.advance(1)
            events=tapes[arm].pop(w.step)
            h=outcome[arm]
            if relative==1:
                h["first_native_step_hash_before_transport"]=w.state_hash_full()
                h["first_native_step_rng_before_transport"]=(w.rng.fingerprint(),w.rng.draws)
            ring_breaks={
                pair for kind,pair in events if kind=="break" and pair in edges
            }
            other_breaks=ring_breaks-{cut}
            if relative==1:
                h["first_native_step_ring_break_event_pairs"]=[list(x) for x in sorted(ring_breaks)]
            if ring_breaks and h["first_original_ring_edge_break_tick"] is None:
                h["first_original_ring_edge_break_tick"]=relative
            if other_breaks and h["first_OTHER_ring_edge_break_tick"] is None:
                h["first_OTHER_ring_edge_break_tick"]=relative
            h["any_original_ring_edge_break_events"]+=sum(
                1 for kind,pair in events if kind=="break" and pair in edges
            )
            actual_reform=any(kind=="form" and pair==cut for kind,pair in events)
            if actual_reform:
                h["selected_cut_reclosure_event_count"]+=1
                if h["first_anytime_cut_edge_reclosure_tick"] is None:
                    h["first_anytime_cut_edge_reclosure_tick"]=relative
            if actual_reform and cut in native_pairs(w):
                if h["first_selected_cut_edge_real_form_tick"] is None:
                    h["first_selected_cut_edge_real_form_tick"]=relative
                if (arm in OPEN and h["first_OTHER_ring_edge_break_tick"] is None):
                    h["exact_cut_edge_reformed_before_any_other_original_break"]=True
            flux=transport_with_optional_suppression(w,arm,edges,cut)
            h["ring_original_edge_transfer_events"]+=flux["native_original_ring_edges_conduction"]
            h["cut_material_pair_transfer_events"]+=flux["native_cut_pair_conduction"]
            h["all_world_bond_transfer_events"]+=flux["all_native_bond_energy_transfers"]
            if relative in CHECKPOINTS:
                ledger(w,w.configured_energy())
                w.check()
                current=native_pairs(w)
                h["checkpoints"].append({
                    "relative_tick":relative,
                    "all_original_ring_material_ids_connected":connected_original_ids(w,ids),
                    "original_material_induced_graph_connected":induced_original_connected(w,ids),
                    "exact_original_ring_closed_now":edges.issubset(current),
                    "all_original_ring_edges_currently_present":sum(edge in current for edge in edges),
                    "selected_original_cut_edge_present":cut in current,
                    "original_ring_particle_energy":sum(w.store.energy[w.store.index_of(i)] for i in ids),
                    "ring_edge_transfer_events_cumulative":h["ring_original_edge_transfer_events"]
                })
        if relative==1:
            for a,b in (
                ("intact_normal","intact_ring_conduction_suppressed"),
                ("opened_normal","opened_surviving_ring_conduction_suppressed")
            ):
                assert outcome[a]["first_native_step_hash_before_transport"]==outcome[b]["first_native_step_hash_before_transport"]
                assert outcome[a]["first_native_step_rng_before_transport"]==outcome[b]["first_native_step_rng_before_transport"]
                assert outcome[a]["first_native_step_ring_break_event_pairs"]==outcome[b]["first_native_step_ring_break_event_pairs"]
    assert parent.state_hash_full()==original_hash
    assert (parent.rng.fingerprint(),parent.rng.draws)==original_rng
    for arm,w in worlds.items():
        h=outcome[arm]
        h["original_ring_material_connected_at_120"]=connected_original_ids(w,ids)
        h["original_ring_induced_material_connected_at_120"]=induced_original_connected(w,ids)
        h["exact_original_ring_all_edges_present_at_120"]=edges.issubset(native_pairs(w))
        h["original_ring_never_suffered_native_break"]=h["first_original_ring_edge_break_tick"] is None
        h["energy_ledger_valid"]=True
        assert len(h["checkpoints"])==len(CHECKPOINTS)
        if arm=="intact_ring_conduction_suppressed":
            assert h["ring_original_edge_transfer_events"]==0
        if arm=="opened_surviving_ring_conduction_suppressed":
            assert h["ring_original_edge_transfer_events"]==h["cut_material_pair_transfer_events"]
        w.check()
        ledger(w,w.configured_energy())
        h["final"]={
            "full_hash":w.state_hash_full(),"rng":w.rng.fingerprint(),
            "draws":w.rng.draws,"energy":w.energy(),"dissipated":w.dissipated,
            "unabsorbed":w.unabsorbed,"injected":w.injected,
            "formed":w.bonds_formed_total,"broken":w.bonds_broken_total
        }
    if validation:
        ref=clone_world(parent)
        for _ in range(HORIZON):
            ref.advance(1)
            energy_transfer(ref,"bond_only")
        assert ref.state_hash_full()==outcome["intact_normal"]["final"]["full_hash"]
        assert (ref.rng.fingerprint(),ref.rng.draws)==(
            outcome["intact_normal"]["final"]["rng"],outcome["intact_normal"]["final"]["draws"])
    return {
        "target_original_cycle_edge":list(cut),
        "identical_cut_refund_metadata":excisions[OPEN[0]],
        "outcomes":outcome
    }


def study(seed,replay=False):
    parent,ring,scan=scan_first_native_aged_ring(seed)
    if ring is None:
        return {"seed":seed,"selected":False,"scan":scan}
    old=(parent.state_hash_full(),parent.rng.fingerprint(),parent.rng.draws)
    result=follow_ring(parent,ring,validation=replay)
    assert (parent.state_hash_full(),parent.rng.fingerprint(),parent.rng.draws)==old
    return {
        "seed":seed,"selected":True,
        "scan":scan,
        "native_original_ring":{
            "ids":list(ring["ids"]),"edges":[list(p) for p in ring["edges"]],
            "size":ring["size"],"exact":ring["exact"],
            "composition":ring["composition"],
            "continuous_snapshot_age":ring["continuous_snapshot_age"]
        },
        "original_full_hash":old[0],"original_rng":old[1],"original_rng_draws":old[2],
        **result
    }


def paired(selected,endpoint,a,b):
    counts={"favor_treatment":0,"favor_control":0,"both":0,"neither":0}
    for r in selected:
        aa=bool(r["outcomes"][a][endpoint])
        bb=bool(r["outcomes"][b][endpoint])
        if aa and not bb:counts["favor_treatment"]+=1
        elif bb and not aa:counts["favor_control"]+=1
        elif aa and bb:counts["both"]+=1
        else:counts["neither"]+=1
    n=counts["favor_treatment"]+counts["favor_control"]
    counts["discordant"]=n
    counts["favorable_fraction"]=round(counts["favor_treatment"]/n,6) if n else None
    assert sum(counts[x] for x in ("favor_treatment","favor_control","both","neither"))==len(selected)
    return counts


def summarize(rows,p):
    assert len(rows)==640
    assert [r["seed"] for r in rows]==list(range(FIRST,LAST+1))
    selected=[r for r in rows if r["selected"]]
    n=len(selected)
    prim=paired(selected,"exact_cut_edge_reformed_before_any_other_original_break",
                "opened_normal","opened_surviving_ring_conduction_suppressed")
    sec=paired(selected,"original_ring_material_connected_at_120",
               "intact_normal","opened_normal")
    def decision(row):
        if n<40:return "not_met_insufficient_natural_aged_rings"
        if row["discordant"]<25:return "not_met_insufficient_discordant_worlds"
        return "passed" if 3*row["favor_treatment"]>=2*row["discordant"] else "not_met_favorable_fraction"
    def avg(xs):
        return round(sum(xs)/len(xs),5) if xs else None
    arms={}
    for a in ARMS:
        obs=[r["outcomes"][a] for r in selected]
        arms[a]={
            "selected_worlds":n,
            "original_ring_material_connected_at_120":sum(x["original_ring_material_connected_at_120"] for x in obs),
            "original_ring_induced_only_connected_at_120":sum(x["original_ring_induced_material_connected_at_120"] for x in obs),
            "exact_original_ring_all_edges_present_at_120":sum(x["exact_original_ring_all_edges_present_at_120"] for x in obs),
            "exact_cut_edge_reclosed_preotherbreak":sum(x["exact_cut_edge_reformed_before_any_other_original_break"] for x in obs),
            "cut_pair_reformed_anytime":sum(x["first_anytime_cut_edge_reclosure_tick"] is not None for x in obs),
            "mean_original_ring_edge_energy_transfers":avg([x["ring_original_edge_transfer_events"] for x in obs]),
            "mean_all_native_bond_transfers":avg([x["all_world_bond_transfer_events"] for x in obs]),
            "original_ring_suffered_no_native_break_events":sum(x["original_ring_never_suffered_native_break"] for x in obs)
        }
    null=Counter(r["scan"]["reason"] for r in rows if not r["selected"])
    return {
        "total_independent_natural_seed_worlds":640,
        "naturally_selected_aged_ring_worlds":n,
        "ineligible_worlds":640-n,
        "null_reasons":dict(null),
        "mean_first_aged_ring_selection_tick":avg([r["scan"]["selected_tick"] for r in selected]),
        "selected_ring_size_distribution":dict(Counter(str(r["native_original_ring"]["size"]) for r in selected)),
        "mean_original_selected_ring_continuous_age":avg([r["native_original_ring"]["continuous_snapshot_age"] for r in selected]),
        "arms":arms,
        "paired_comparisons":{
            "primary_native_exact_cut_reclosure_before_other_break_vs_suppress_energy":prim,
            "secondary_ring_intact_vs_cut_material_cohesion_t120":sec
        },
        "preregistered_decisions":{
            "original_ring_surviving_edges_energy_help_exact_native_reclosure":decision(prim),
            "original_ring_physical_redundancy_preserves_material_cohesion":decision(sec),
            "minimum_eligible_natural_ring_source_worlds":40,
            "minimum_discordant_source_worlds_per_gate":25,
            "required_favorable_fraction":"2/3",
            "no_claim_of_active_or_biological_repair":True
        },
        "limitations":"Cyclic closed native ring and cut chain differ at t0 by one redundant edge and endpoint energy/valences; same total energy does not equal same particle energy or RNG draw sequence. Intact-vs-cut cohesion can reflect passive graph topology. Exact native reclosure is stochastic reversible chemistry, not directed adaptive repair. No heredity or life."
    }


def run_shard(start,end):
    p=protocol()
    d={"start":start,"end":end}
    assert d in p["sample"]["shards"]
    rows=[]
    first=None
    for seed in range(start,end+1):
        r=study(seed,replay=(first is None))
        rows.append(r)
        if r["selected"] and first is None:first=seed
        if (seed-start+1)%10==0:
            print(f"M711_PROGRESS {start}-{end} seed={seed} selected={sum(x['selected'] for x in rows)}",flush=True)
    assert len(rows)==end-start+1
    obj={
        "schema":"alife-m7-11-native-ring-shard-v1",
        "descriptor":d,"provenance":provenance(),
        "worlds":rows,
        "first_selected_native_ring_120tick_sham_replay":first,
        "all_native_src_and_prior_code_unchanged":True
    }
    path=BASE/"shards"/f"{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M711_SHARD="+json.dumps({"start":start,"end":end,"worlds":len(rows),"selected":sum(x["selected"] for x in rows),"replay":first},sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("*.json"))
    assert len(files)==16
    expected=provenance()
    records=[]
    seen=[]
    replays=[]
    for path in files:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m7-11-native-ring-shard-v1"
        assert chunk["provenance"]==expected
        assert chunk["all_native_src_and_prior_code_unchanged"] is True
        d=chunk["descriptor"]
        assert d in p["sample"]["shards"] and d not in seen
        seen.append(d)
        rows=chunk["worlds"]
        assert [x["seed"] for x in rows]==list(range(d["start"],d["end"]+1))
        first=next((x["seed"] for x in rows if x["selected"]),None)
        assert first==chunk["first_selected_native_ring_120tick_sham_replay"]
        if first is not None:replays.append(first)
        records.extend(rows)
    assert all(x in seen for x in p["sample"]["shards"])
    records.sort(key=lambda r:r["seed"])
    summary=summarize(records,p)
    payload={
        "schema":"alife-m7-11-full-640-native-aged-cyclic-fault-tolerance-v1",
        "provenance":expected,
        "worlds":records,"shard_first_selected_replayed_seed":replays,
        "summary":summary,
        "all_640_seed_worlds_16_preregistered_shards_complete":True,
        "native_M6_M7_3_M6_4_engines_unchanged":True
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print("M711_FINAL_SUMMARY="+json.dumps(summary,sort_keys=True),flush=True)
    print("M711_SUCCESS="+str(len(records)),flush=True)


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="command",required=True)
    sh=sub.add_parser("shard")
    sh.add_argument("--start",type=int,required=True)
    sh.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    args=ap.parse_args()
    if args.command=="shard":run_shard(args.start,args.end)
    else:merge()


if __name__=="__main__":main()
