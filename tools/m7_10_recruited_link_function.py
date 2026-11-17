"""M7.10: functional causal forks of FIRST native prebreak recruited bond.

The first acquired original-root -> exterior material link forms SPONTANEOUSLY
via unchanged native M6 chemistry during original M7.3 bond-conduction world
evolution. One selected source and earliest eligible native link per numeric
seed; no future-outcome filtering.

Two deliberate ablations:
  (1) keep native physical bond, forbid only that pair's future M7.3 energy
      conduction (otherwise identical original native M6 dynamics);
  (2) remove just acquired bond, refund EXISTING stored bond energy to the
      two endpoints in original M6 ID order, no added dissipation/no RNG.
Neither is a native physical law. All experimental changes local to tools/.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.structures import components
from tools.m6_5_ring_forks import clone_world
from tools.m7_4_material_feedback import EventTape, native_pairs
from tools.m7_3_bond_energy import energy_transfer,bond_pairs
from tools.m7_2_energy_distribution import ledger
from tools import m7_5_mature_feedback as original

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_10_functional"
PFILE=BASE/"protocol.json"
RESULT=BASE/"results.json"
OLD_M75=ROOT/"tools/m7_5_mature_feedback.py"
OLD_M73=ROOT/"tools/m7_3_bond_energy.py"
ARMS=("native_intact","bond_intact_conduction_ablated","recruited_edge_excised_refunded")
CHECKPOINTS=(1,10,30,60,120)
HORIZON=120
FIRST=28001
LAST=28640


def protocol():
    p=json.loads(PFILE.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-10-native-first-recruited-bond-functional-forks-v1"
    assert p["status"]=="frozen_before_experimental_code_or_results"
    s=p["sampling"]
    assert (s["seed_first"],s["seed_last"],s["seed_count"])==(FIRST,LAST,640)
    assert s["selection_horizon_steps"]==HORIZON
    assert s["followup_steps"]==HORIZON
    assert len(s["shards"])==16
    assert [i for x in s["shards"] for i in range(x["start"],x["end"]+1)]==list(range(FIRST,LAST+1))
    assert p["forks"]["timepoints"]==list(CHECKPOINTS)
    assert original.protocol()["design"]["parent_scan_start_tick"]==120
    assert p["integrity"]["no_change_to_src_or_prior_M6_M7_files"]
    return p


def provenance():
    return {
        "m710_protocol_sha256":sha256(PFILE.read_bytes()).hexdigest(),
        "original_M75_source_sha256":sha256(OLD_M75.read_bytes()).hexdigest(),
        "original_M73_conduction_sha256":sha256(OLD_M73.read_bytes()).hexdigest()
    }


def component_containing_root(world,ids):
    root=set(ids)
    store=world.store
    for indexes,_ in components(store):
        current={store.ids[i] for i in indexes}
        if root.issubset(current):
            return current
    return None


def select_first_acquired_native(seed,p):
    """Original source plus FIRST newly chemically formed root-outside bond.

    A source is ineligible forever once an original material bond actually
    BREAKS, including same-tick break/reform. Never select retrospectively
    based on its eventual duration or future success.
    """
    parent,source,selection=original.select_parent(seed,p)
    if source is None:
        return None,None,None,{
            "source_selected":False,"reason":"no_m75_native_aged_source",
            "scan_tick":parent.step
        }
    root=set(source["ids"])
    original_pairs=set(source["edges"])
    assert original_pairs.issubset(native_pairs(parent))
    recorder=EventTape()
    parent.event_sink=recorder
    for rel in range(1,HORIZON+1):
        parent.advance(1)
        events=recorder.pop(parent.step)
        original_breaks=[
            pair for kind,pair in events if kind=="break" and pair in original_pairs
        ]
        # Native poststep M7.3 conduction is part of the baseline; no
        # intervention until AFTER a naturally first selected new bond.
        energy_transfer(parent,"bond_only")
        if original_breaks:
            parent.event_sink=None
            return None,None,None,{
                "source_selected":True,"reason":"original_root_bond_broke_before_first_eligible_recruitment",
                "source_tick":selection["earliest_eligible_tick"],
                "first_original_break_relative_tick":rel
            }
        form=[
            pair for kind,pair in events if kind=="form"
            and ((pair[0] in root)!=(pair[1] in root))
            and pair in native_pairs(parent)
        ]
        if form:
            chosen=min(form)
            newcomer=next(value for value in chosen if value not in root)
            assert component_containing_root(parent,root) is not None
            parent.event_sink=None
            parent.check()
            ledger(parent,parent.configured_energy())
            return parent,source,{
                "native_first_link":list(chosen),
                "native_first_recruited_outsider_id":newcomer,
                "first_link_native_form_relative_tick":rel,
                "first_link_world_absolute_tick":parent.step,
                "same_tick_native_original_to_outside_form_event_count":len(form),
                "prior_original_material_break_events":0
            },{
                "source_selected":True,"reason":"first_prebreak_native_recruited_edge",
                "source_tick":selection["earliest_eligible_tick"],
                "first_link_relative_tick":rel
            }
    parent.event_sink=None
    parent.check()
    return None,None,None,{
        "source_selected":True,
        "reason":"no_incident_native_recruitment_before_original_break_or_time_limit",
        "source_tick":selection["earliest_eligible_tick"],
        "scan_steps":HORIZON
    }


def excise_and_refund(world,pair_ids):
    """Explicit nonphysical intervention: no new formation or break lottery.

    Return ALL bond-stored energy to endpoints in the same ID order as M6
    break_bonds() but without any extra breaking dissipation. The bond's
    original formation dissipation remains paid in every arm.
    """
    a,b=sorted((world.store.index_of(i) for i in pair_ids))
    assert (a,b) in world.store.bonds
    before=(world.energy(),world.dissipated,world.rng.fingerprint(),world.rng.draws)
    stored=world.store.bonds[(a,b)]
    world.store.remove_bond(a,b)
    world.store.energy[a]+=stored-stored//2
    world.store.energy[b]+=stored//2
    assert world.energy()==before[0]
    assert world.dissipated==before[1]
    assert (world.rng.fingerprint(),world.rng.draws)==before[2:]
    assert tuple(sorted(pair_ids)) not in native_pairs(world)
    world.check()
    ledger(world,world.configured_energy())
    return {"excised_native_bond_energy":stored,
            "refunded_to_lower_original_id":stored-stored//2,
            "refunded_to_higher_original_id":stored//2,
            "no_additional_dissipation":True,
            "world_energy_and_rng_unchanged":True}


def predicted_bond_energy_route(world,root_ids,selected_pair,suppress):
    """Exactly M7.3 snapshot/remaining-budget conductor, plus optional skip.

    Does NOT mutate world. Separately classify original-cohort boundary
    transfers and selected acquired edge while keeping accepted ordering.
    """
    s=world.store
    before=tuple(s.energy)
    rem=list(before)
    delta=[0]*len(before)
    root=set(root_ids)
    chosen=frozenset(selected_pair)
    total=0
    onlink=0
    to_root=0
    from_root=0
    link_to_root=0
    link_from_root=0
    for a,b in bond_pairs(world):
        pair=frozenset((s.ids[a],s.ids[b]))
        if suppress and pair==chosen:
            continue
        if before[a]-before[b]>=2:
            donor,recipient=a,b
        elif before[b]-before[a]>=2:
            donor,recipient=b,a
        else:continue
        if rem[donor]<1:continue
        rem[donor]-=1
        delta[donor]-=1
        delta[recipient]+=1
        total+=1
        in_a=s.ids[donor] in root
        in_b=s.ids[recipient] in root
        if in_a and not in_b:from_root+=1
        if in_b and not in_a:to_root+=1
        if pair==chosen:
            onlink+=1
            if in_a and not in_b:link_from_root+=1
            if in_b and not in_a:link_to_root+=1
    assert sum(delta)==0
    return {
        "transfers_total":total,
        "transfers_on_selected_original_new_link":onlink,
        "source_boundary_transfers_in":to_root,
        "source_boundary_transfers_out":from_root,
        "selected_link_transfers_in":link_to_root,
        "selected_link_transfers_out":link_from_root,
        "energy_deltas":delta
    }


def route(world,arm,root_ids,selected_pair):
    suppress=arm=="bond_intact_conduction_ablated"
    expectation=predicted_bond_energy_route(world,root_ids,selected_pair,suppress=suppress)
    before=(world.energy(),world.rng.fingerprint(),world.rng.draws)
    snapshot=list(world.store.energy)
    if suppress:
        for i,d in enumerate(expectation["energy_deltas"]):
            if d:
                world.store.energy[i]+=d
                assert world.store.energy[i]>=0
        assert expectation["transfers_on_selected_original_new_link"]==0
    else:
        n,nb,nu=energy_transfer(world,"bond_only")
        assert n==nb==expectation["transfers_total"] and nu==0
        assert world.store.energy==[x+y for x,y in zip(snapshot,expectation["energy_deltas"])]
    assert (world.energy(),world.rng.fingerprint(),world.rng.draws)==before
    return {k:v for k,v in expectation.items() if k!="energy_deltas"}


def follow(parent,source,first,firststep_sham_replay=False):
    """120 native M6 steps after acquisition; three paired energy-valid arms."""
    root=tuple(source["ids"])
    original=set(source["edges"])
    link=tuple(first["native_first_link"])
    outsider=first["native_first_recruited_outsider_id"]
    initial=set(root)|{outsider}
    assert set(link)&set(root) and outsider not in root
    assert set(link)-set(root)=={outsider}
    assert link in native_pairs(parent)
    assert original.issubset(native_pairs(parent))
    baseline_hash=parent.state_hash_full()
    baseline_rng=(parent.rng.fingerprint(),parent.rng.draws)
    arms={a:clone_world(parent) for a in ARMS}
    assert len({w.state_hash_full() for w in arms.values()})==1
    assert len({(w.rng.fingerprint(),w.rng.draws) for w in arms.values()})==1
    excision=excise_and_refund(arms["recruited_edge_excised_refunded"],link)
    assert arms["native_intact"].state_hash_full()==arms["bond_intact_conduction_ablated"].state_hash_full()
    assert arms["native_intact"].energy()==arms["recruited_edge_excised_refunded"].energy()
    assert arms["recruited_edge_excised_refunded"].dissipated==parent.dissipated

    tapes={a:EventTape() for a in ARMS}
    outcomes={}
    for arm,w in arms.items():
        w.event_sink=tapes[arm]
        outcomes[arm]={
            "first_original_root_edge_break_relative_tick":None,
            "first_acquired_link_native_break_relative_tick":None,
            "first_second_distinct_outsider_formation_relative_tick":None,
            "any_second_distinct_outsider_form_before_original_break":False,
            "any_second_distinct_outsider_form_and_coherent_root_before_original_break":False,
            "second_distinct_outsider_formation_event_count_before_original_break":0,
            "distinct_second_outsider_ids_before_original_break":[],
            "total_other_native_form_events_from_initial_extended_ids":0,
            "selected_pair_transfers":0,
            "selected_pair_transfers_root_to_outsider":0,
            "selected_pair_transfers_outsider_to_root":0,
            "total_source_boundary_passive_transfer_in":0,
            "total_source_boundary_passive_transfer_out":0,
            "total_native_bond_energy_transfers":0,
            "first_native_step_full_hash_before_transport":None,
            "first_native_step_rng_before_transport":None,
            "first_native_step_break_events_on_original_root":[],
            "checkpoints":[]
        }
    newly_recruited={a:set() for a in ARMS}
    for t in range(1,HORIZON+1):
        for arm,w in arms.items():
            w.advance(1)
            events=tapes[arm].pop(w.step)
            h=outcomes[arm]
            if t==1:
                h["first_native_step_full_hash_before_transport"]=w.state_hash_full()
                h["first_native_step_rng_before_transport"]=w.rng.fingerprint()
            original_break={
                pair for kind,pair in events if kind=="break" and pair in original
            }
            if t==1:h["first_native_step_break_events_on_original_root"]=[list(x) for x in sorted(original_break)]
            if original_break and h["first_original_root_edge_break_relative_tick"] is None:
                h["first_original_root_edge_break_relative_tick"]=t
            if any(kind=="break" and pair==link for kind,pair in events):
                if h["first_acquired_link_native_break_relative_tick"] is None:
                    h["first_acquired_link_native_break_relative_tick"]=t
            formed_other=[
                pair for kind,pair in events if kind=="form"
                and ((pair[0] in initial)!=(pair[1] in initial))
            ]
            h["total_other_native_form_events_from_initial_extended_ids"]+=len(formed_other)
            if h["first_original_root_edge_break_relative_tick"] is None:
                for pair in formed_other:
                    other=next(i for i in pair if i not in initial)
                    newly_recruited[arm].add(other)
                    h["second_distinct_outsider_formation_event_count_before_original_break"]+=1
                    if not h["any_second_distinct_outsider_form_before_original_break"]:
                        h["first_second_distinct_outsider_formation_relative_tick"]=t
                    h["any_second_distinct_outsider_form_before_original_break"]=True
                    if component_containing_root(w,root) is not None:
                        cc=component_containing_root(w,root)
                        if other in cc:
                            h["any_second_distinct_outsider_form_and_coherent_root_before_original_break"]=True
            flow=route(w,arm,root,link)
            h["selected_pair_transfers"]+=flow["transfers_on_selected_original_new_link"]
            h["selected_pair_transfers_root_to_outsider"]+=flow["selected_link_transfers_out"]
            h["selected_pair_transfers_outsider_to_root"]+=flow["selected_link_transfers_in"]
            h["total_source_boundary_passive_transfer_in"]+=flow["source_boundary_transfers_in"]
            h["total_source_boundary_passive_transfer_out"]+=flow["source_boundary_transfers_out"]
            h["total_native_bond_energy_transfers"]+=flow["transfers_total"]
            if t in CHECKPOINTS:
                w.check()
                ledger(w,w.configured_energy())
                cc=component_containing_root(w,root)
                h["checkpoints"].append({
                    "relative_tick":t,
                    "original_root_all_ids_connected":cc is not None,
                    "recruited_first_outsider_in_original_root_component":cc is not None and outsider in cc,
                    "new_second_outsider_ids_in_original_root_component":sorted(cc-initial) if cc is not None else [],
                    "original_root_bonds_currently_all_present":original.issubset(native_pairs(w)),
                    "first_new_link_currently_present":link in native_pairs(w),
                    "original_root_particle_energy":sum(w.store.energy[w.store.index_of(i)] for i in root),
                    "first_outsider_particle_energy":w.store.energy[w.store.index_of(outsider)],
                    "selected_new_link_energy_passes_cumulative":h["selected_pair_transfers"],
                    "source_boundary_net_passes_cumulative":h["total_source_boundary_passive_transfer_in"]-h["total_source_boundary_passive_transfer_out"]
                })
        if t==1:
            a=outcomes["native_intact"]
            b=outcomes["bond_intact_conduction_ablated"]
            assert a["first_native_step_full_hash_before_transport"]==b["first_native_step_full_hash_before_transport"]
            assert a["first_native_step_rng_before_transport"]==b["first_native_step_rng_before_transport"]
            assert a["first_native_step_break_events_on_original_root"]==b["first_native_step_break_events_on_original_root"]
    assert parent.state_hash_full()==baseline_hash
    assert (parent.rng.fingerprint(),parent.rng.draws)==baseline_rng
    for arm,w in arms.items():
        w.check()
        ledger(w,w.configured_energy())
        h=outcomes[arm]
        h["distinct_second_outsider_ids_before_original_break"]=sorted(newly_recruited[arm])
        h["all_original_root_bonds_never_broken_120"]=h["first_original_root_edge_break_relative_tick"] is None
        h["originally_acquired_link_never_broken_after_fork_120"]=(
            h["first_acquired_link_native_break_relative_tick"] is None if arm!="recruited_edge_excised_refunded" else None
        )
        cc=component_containing_root(w,root)
        h["final_root_coherent_size"]=len(cc) if cc is not None else None
        h["first_recruited_outsider_in_final_root_component"]=cc is not None and outsider in cc
        h["any_other_new_outsider_in_final_root_component"]=cc is not None and bool(cc-initial)
        h["native_first_edge_present_at_120"]=link in native_pairs(w)
        h["energy_ledger_verified"]=True
        h["final"]={
            "full_hash":w.state_hash_full(),
            "rng":w.rng.fingerprint(),"draws":w.rng.draws,
            "energy":w.energy(),"injected":w.injected,"unabsorbed":w.unabsorbed,
            "dissipated":w.dissipated,
            "formed":w.bonds_formed_total,"broken":w.bonds_broken_total
        }
        assert len(h["checkpoints"])==len(CHECKPOINTS)
    assert outcomes["bond_intact_conduction_ablated"]["selected_pair_transfers"]==0
    if firststep_sham_replay:
        replay=clone_world(parent)
        for _ in range(HORIZON):
            replay.advance(1)
            energy_transfer(replay,"bond_only")
        replay.check()
        assert replay.state_hash_full()==outcomes["native_intact"]["final"]["full_hash"]
        assert replay.rng.fingerprint()==outcomes["native_intact"]["final"]["rng"]
        assert replay.rng.draws==outcomes["native_intact"]["final"]["draws"]
    return {"intervention_excised_refund_metadata":excision,"outcomes":outcomes}


def study(seed,old,replay=False):
    world,source,first,selection=select_first_acquired_native(seed,old)
    if first is None:
        return {"seed":seed,"qualifies":False,"selection":selection}
    oldhash=world.state_hash_full()
    oldrng=world.rng.fingerprint(),world.rng.draws
    results=follow(world,source,first,firststep_sham_replay=replay)
    assert (world.state_hash_full(),world.rng.fingerprint(),world.rng.draws)==(oldhash,*oldrng)
    return {
        "seed":seed,"qualifies":True,"selection":selection,
        "source":{"ids":list(source["ids"]),"original_edges":[list(x) for x in source["edges"]],"size":source["size"],"cyclomatic_number":source["cyclomatic_number"]},
        "first_native_new_recruited_link":first,
        "selected_native_poststep_full_hash":oldhash,
        "selected_native_rng":oldrng[0],"selected_native_draws":oldrng[1],
        **results
    }


def paired(selected,field,arm_a="native_intact",arm_b="bond_intact_conduction_ablated"):
    counts={"favor_native_intact":0,"favor_control":0,"both":0,"neither":0}
    for row in selected:
        a=bool(row["outcomes"][arm_a][field])
        b=bool(row["outcomes"][arm_b][field])
        if a and not b:counts["favor_native_intact"]+=1
        elif b and not a:counts["favor_control"]+=1
        elif a and b:counts["both"]+=1
        else:counts["neither"]+=1
    n=counts["favor_native_intact"]+counts["favor_control"]
    counts["discordant"]=n
    counts["favorable_fraction"]=round(counts["favor_native_intact"]/n,6) if n else None
    assert counts["discordant"]+counts["both"]+counts["neither"]==len(selected)
    return counts


def summarize(records,p):
    assert len(records)==640 and [r["seed"] for r in records]==list(range(FIRST,LAST+1))
    eligible=[r for r in records if r["qualifies"]]
    n=len(eligible)
    key="any_second_distinct_outsider_form_before_original_break"
    p1=paired(eligible,key,arm_b="bond_intact_conduction_ablated")
    p2=paired(eligible,key,arm_b="recruited_edge_excised_refunded")
    def gate(row):
        if n<40:return "not_met_insufficient_selected_source_worlds"
        if row["discordant"]<25:return "not_met_insufficient_discordant_source_worlds"
        return "passed" if 3*row["favor_native_intact"]>=2*row["discordant"] else "not_met_favorable_fraction"
    def mean(values):return round(sum(values)/len(values),5) if values else None
    arms={}
    for arm in ARMS:
        r=[x["outcomes"][arm] for x in eligible]
        arms[arm]={
            "independent_source_worlds":n,
            "second_distinct_native_outside_recruitment_before_first_original_break":sum(x[key] for x in r),
            "second_recruitment_strictly_coherent_source_before_break":sum(x["any_second_distinct_outsider_form_and_coherent_root_before_original_break"] for x in r),
            "original_root_never_broken":sum(x["all_original_root_bonds_never_broken_120"] for x in r),
            "first_new_recruited_id_in_original_coherent_root_at_120":sum(x["first_recruited_outsider_in_final_root_component"] for x in r),
            "another_new_recruited_id_in_root_at_120":sum(x["any_other_new_outsider_in_final_root_component"] for x in r),
            "mean_selected_pair_energy_conduction_events":mean([x["selected_pair_transfers"] for x in r]),
            "mean_root_boundary_net_passes":mean([x["total_source_boundary_passive_transfer_in"]-x["total_source_boundary_passive_transfer_out"] for x in r]),
            "mean_final_coherent_root_size":mean([x["final_root_coherent_size"] for x in r if x["final_root_coherent_size"] is not None])
        }
    reasons=Counter(x["selection"]["reason"] for x in records if not x["qualifies"])
    return {
        "numeric_source_worlds":640,"eligible_first_prebreak_recruited_native_bond":n,
        "no_eligible_recruited_bond":640-n,
        "null_reasons":dict(reasons),
        "mean_first_recruited_native_bond_relative_tick":mean([r["first_native_new_recruited_link"]["first_link_native_form_relative_tick"] for r in eligible]),
        "native_source_topology":{
            "tree":sum(r["source"]["cyclomatic_number"]==0 for r in eligible),
            "cyclic":sum(r["source"]["cyclomatic_number"]>0 for r in eligible)
        },
        "per_arm":arms,
        "paired_comparisons":{
            "primary_kept_link_conduction_vs_selected_edge_transport_suppressed":p1,
            "secondary_kept_link_vs_energy_refunded_excised_link":p2
        },
        "preregistered_decisions":{
            "native_new_link_conduction_enables_second_recruitment":gate(p1),
            "native_new_link_itself_enables_second_recruitment":gate(p2),
            "minimum_selected_seed_worlds":40,
            "minimum_discordant_seed_pairs_each_gate":25,
            "favorable_fraction_required":"2/3",
            "two_biological_gates_only":True
        },
        "scientific_caveats":"First-root bond break kills primary prebreak recruitment eligibility, but original newly recruited bond can break and the first recruit ID could later form bonds detached from root; strict physically connected counterpart reported separately. Excised energy refund changes particle energy/valence/PRNG trajectory; not a pure independent RNG controlled reaction. Native conduction arm vs suppressed-link arm starts EXACT same microstate but later RNG may diverge. No descendants or biological maintenance inferred."
    }


def run_shard(start,end):
    p=protocol()
    d={"start":start,"end":end}
    assert d in p["sampling"]["shards"]
    rows=[]
    sentinel=None
    old=original.protocol()
    for seed in range(start,end+1):
        r=study(seed,old,replay=(sentinel is None))
        rows.append(r)
        if r["qualifies"] and sentinel is None:sentinel=seed
        if (seed-start+1)%10==0:
            print(f"M710_PROGRESS {start}-{end} seed={seed} eligible={sum(x['qualifies'] for x in rows)}",flush=True)
    assert len(rows)==end-start+1
    output={
        "schema":"alife-m7-10-source-shard-v1",
        "descriptor":d,
        "provenance":provenance(),
        "worlds":rows,
        "first_selected_native_source_sham_replay":sentinel,
        "no_native_chemistry_or_prior_code_changed":True
    }
    path=BASE/"shards"/f"seeds-{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M710_SHARD="+json.dumps({
        "start":start,"end":end,"worlds":len(rows),
        "eligible":sum(x["qualifies"] for x in rows),
        "first_sham_replayed_seed":sentinel
    },sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("seeds-*.json"))
    assert len(files)==16,("missing frozen shard(s)",len(files))
    pv=provenance()
    seen=[]
    worlds=[]
    sentinels=[]
    for path in files:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m7-10-source-shard-v1"
        assert chunk["provenance"]==pv
        assert chunk["no_native_chemistry_or_prior_code_changed"] is True
        desc=chunk["descriptor"]
        assert desc in p["sampling"]["shards"] and desc not in seen
        seen.append(desc)
        rows=chunk["worlds"]
        assert [r["seed"] for r in rows]==list(range(desc["start"],desc["end"]+1))
        first=next((r["seed"] for r in rows if r["qualifies"]),None)
        assert first==chunk["first_selected_native_source_sham_replay"]
        worlds.extend(rows)
        if first is not None:sentinels.append(first)
    assert all(d in seen for d in p["sampling"]["shards"])
    worlds.sort(key=lambda x:x["seed"])
    summary=summarize(worlds,p)
    payload={
        "schema":"alife-m7-10-full-640-natural-first-new-link-functional-outcomes-v1",
        "provenance":pv,
        "worlds":worlds,
        "shard_first_source_replayed_seeds":sentinels,
        "summary":summary,
        "all_640_original_seed_worlds_16_fixed_shards_included":True,
        "native_source_and_core_physics_unmodified":True
    }
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print("M710_FINAL_SUMMARY="+json.dumps(summary,sort_keys=True),flush=True)
    print("M710_SUCCESS="+str(len(worlds)),flush=True)


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    sh=sub.add_parser("shard")
    sh.add_argument("--start",type=int,required=True)
    sh.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    a=ap.parse_args()
    if a.cmd=="shard":run_shard(a.start,a.end)
    else:merge()


if __name__=="__main__":
    main()
