"""M7.10 POSTHOC independent native-physics replay of frozen 640 seed sample.

Do not use M7.10 source selector, conduction predictor, excision helper,
follow(), source material classifier or statistical gate. Recreate original
M7.5 native sources from each SEED; reproduce FIRST native M6 recruitment
with independent event recorder and original M7.3 bond conduction. Then
replay all three fork arms with independent refund/suppression implementations.

This is correctness verification on the SAME 640 numerical source worlds,
not independent scientific sampling or newly selected source subjects.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from tools import m7_5_mature_feedback as old_selector
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer, bond_pairs
from tools.m7_2_energy_distribution import ledger
from tools.m7_5_posthoc_independent_replay import IndependentEvents

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_10_functional"
SOURCE=BASE/"results.json"
OUT=BASE/"posthoc_independent_physics.json"
ARMS=("native_intact","bond_intact_conduction_ablated","recruited_edge_excised_refunded")


def bond_ids(w):
    return {
        tuple(sorted((w.store.ids[a],w.store.ids[b])))
        for a,b in w.store.bonds
    }


def root_cc(w,original_ids):
    """Fresh, non-M7.10 recursive adjacency traversal by persistent IDs."""
    s=w.store
    adjacency={}
    for i,j in s.bonds:
        a,b=s.ids[i],s.ids[j]
        adjacency.setdefault(a,set()).add(b)
        adjacency.setdefault(b,set()).add(a)
    root=set(original_ids)
    visited={next(iter(root))}
    stack=list(visited)
    while stack:
        u=stack.pop()
        for v in adjacency.get(u,()):
            if v not in visited:
                visited.add(v)
                stack.append(v)
    return visited if root.issubset(visited) else None


def derive_native_acquisition(seed,old):
    p,source,selector=old_selector.select_parent(seed,old)
    if source is None:
        return None,None,None,"no_m75_native_aged_source"
    root=set(source["ids"])
    originals=set(source["edges"])
    recorder=IndependentEvents()
    p.event_sink=recorder
    for relative in range(1,121):
        p.advance(1)
        events=recorder.events(p.step)
        broken={pair for kind,pair in events if kind=="break" and pair in originals}
        energy_transfer(p,"bond_only")
        if broken:
            p.event_sink=None
            return None,None,None,"original_root_bond_broke_before_first_eligible_recruitment"
        pairs=sorted(pair for kind,pair in events if kind=="form"
                     and ((pair[0] in root)!=(pair[1] in root))
                     and pair in bond_ids(p))
        if pairs:
            p.event_sink=None
            pair=pairs[0]
            outsider=next(i for i in pair if i not in root)
            assert root_cc(p,root) is not None
            p.check()
            ledger(p,p.configured_energy())
            return p,source,{
                "pair":pair,
                "outsider":outsider,
                "relative_tick":relative,
                "absolute_tick":p.step
            },"first_prebreak_native_recruited_edge"
    p.event_sink=None
    return None,None,None,"no_incident_native_recruitment_before_original_break_or_time_limit"


def independent_remove_bond_full_refund(world,pair):
    s=world.store
    a,b=sorted((s.index_of(value) for value in pair))
    old=(world.energy(),world.dissipated,world.rng.fingerprint(),world.rng.draws)
    value=s.bonds[(a,b)]
    s.remove_bond(a,b)
    s.energy[a]+=(value+1)//2
    s.energy[b]+=value//2
    assert (world.energy(),world.dissipated,world.rng.fingerprint(),world.rng.draws)==old
    world.check()
    ledger(world,world.configured_energy())
    return value


def independent_conduct(world,arm,root,selected_pair):
    """Own native M7.3 snapshot-gradient (not the M7.10 transfer observer).

    For intact + excised arms, actually CALL original M7.3 code and compare
    our independent forecast. For suppressed arm, apply the forecast while
    skipping exactly the chosen native material pair.
    """
    s=world.store
    initial=tuple(s.energy)
    rem=list(initial)
    delta=[0]*len(initial)
    selected=frozenset(selected_pair)
    root=set(root)
    suppress=arm=="bond_intact_conduction_ablated"
    transfer=selected_count=source_in=source_out=0
    for a,b in bond_pairs(world):
        pair=frozenset((s.ids[a],s.ids[b]))
        if suppress and pair==selected:continue
        if initial[a]-initial[b]>=2:
            give,receive=a,b
        elif initial[b]-initial[a]>=2:
            give,receive=b,a
        else:continue
        if rem[give]==0:continue
        rem[give]-=1
        delta[give]-=1
        delta[receive]+=1
        transfer+=1
        if pair==selected:selected_count+=1
        if s.ids[give] in root and s.ids[receive] not in root:source_out+=1
        if s.ids[give] not in root and s.ids[receive] in root:source_in+=1
    pre_energy=world.energy()
    prng=(world.rng.fingerprint(),world.rng.draws)
    if suppress:
        for i,d in enumerate(delta):
            s.energy[i]+=d
        assert selected_count==0
    else:
        actual=energy_transfer(world,"bond_only")
        assert actual==(transfer,transfer,0)
        assert tuple(s.energy)==tuple(v+d for v,d in zip(initial,delta))
    assert world.energy()==pre_energy
    assert (world.rng.fingerprint(),world.rng.draws)==prng
    return transfer,selected_count,source_in,source_out


def independent_fork_check(row,p,source,first):
    ids=tuple(source["ids"])
    original=set(source["edges"])
    recruited=first["outsider"]
    pair=first["pair"]
    group=set(ids)|{recruited}
    worlds={name:clone_world(p) for name in ARMS}
    assert worlds["native_intact"].state_hash_full()==worlds["bond_intact_conduction_ablated"].state_hash_full()
    refund=independent_remove_bond_full_refund(worlds["recruited_edge_excised_refunded"],pair)
    assert refund==row["intervention_excised_refund_metadata"]["excised_native_bond_energy"]
    recorders={a:IndependentEvents() for a in ARMS}
    for arm,w in worlds.items():
        w.event_sink=recorders[arm]
    trackers={
        a:{"first_root_break":None,"first_link_break":None,
           "second_ids":set(),"first_second":None,
           "second_coherent":False,
           "selected_transfers":0,"source_in":0,"source_out":0,
           "first_step_hash":None,
           "checkpoints":[]}
        for a in ARMS
    }
    for t in range(1,121):
        for arm,w in worlds.items():
            w.advance(1)
            events=recorders[arm].events(w.step)
            x=trackers[arm]
            if t==1:x["first_step_hash"]=w.state_hash_full()
            broken={bond for kind,bond in events if kind=="break"}
            if x["first_root_break"] is None and original.intersection(broken):
                x["first_root_break"]=t
            if x["first_link_break"] is None and pair in broken:
                x["first_link_break"]=t
            for kind,bond in events:
                if kind!="form":continue
                if (bond[0] in group)==(bond[1] in group):continue
                if x["first_root_break"] is not None:continue
                newcomer=next(value for value in bond if value not in group)
                x["second_ids"].add(newcomer)
                if x["first_second"] is None:x["first_second"]=t
                cc=root_cc(w,ids)
                if cc is not None and newcomer in cc:
                    x["second_coherent"]=True
            _,selected_count,flow_in,flow_out=independent_conduct(w,arm,ids,pair)
            x["selected_transfers"]+=selected_count
            x["source_in"]+=flow_in
            x["source_out"]+=flow_out
            if t in (1,10,30,60,120):
                ledger(w,w.configured_energy())
                w.check()
                cc=root_cc(w,ids)
                x["checkpoints"].append({
                    "relative_tick":t,
                    "first_new_link_currently_present":pair in bond_ids(w),
                    "original_root_all_ids_connected":cc is not None,
                    "recruited_first_outsider_in_original_root_component":cc is not None and recruited in cc,
                    "new_second_outsider_ids_in_original_root_component":sorted(cc-group) if cc is not None else []
                })
        if t==1:
            assert trackers["native_intact"]["first_step_hash"]==trackers["bond_intact_conduction_ablated"]["first_step_hash"]
    for arm,w in worlds.items():
        x=trackers[arm]
        originalrow=row["outcomes"][arm]
        cc=root_cc(w,ids)
        assert x["first_root_break"]==originalrow["first_original_root_edge_break_relative_tick"],(row["seed"],arm,"root break tick")
        assert x["first_link_break"]==originalrow["first_acquired_link_native_break_relative_tick"]
        assert x["first_second"]==originalrow["first_second_distinct_outsider_formation_relative_tick"]
        assert (x["first_second"] is not None)==originalrow["any_second_distinct_outsider_form_before_original_break"]
        assert x["second_coherent"]==originalrow["any_second_distinct_outsider_form_and_coherent_root_before_original_break"]
        assert sorted(x["second_ids"])==originalrow["distinct_second_outsider_ids_before_original_break"]
        assert x["selected_transfers"]==originalrow["selected_pair_transfers"]
        assert x["source_in"]==originalrow["total_source_boundary_passive_transfer_in"]
        assert x["source_out"]==originalrow["total_source_boundary_passive_transfer_out"]
        assert (cc is not None and recruited in cc)==originalrow["first_recruited_outsider_in_final_root_component"]
        assert (cc is not None and bool(cc-group))==originalrow["any_other_new_outsider_in_final_root_component"]
        assert (len(cc) if cc is not None else None)==originalrow["final_root_coherent_size"]
        assert len(x["checkpoints"])==5
        for expected,actual in zip(originalrow["checkpoints"],x["checkpoints"]):
            for key in actual:
                assert actual[key]==expected[key],(row["seed"],arm,key)
        final=originalrow["final"]
        assert w.state_hash_full()==final["full_hash"],(row["seed"],arm,"hash")
        assert (w.rng.fingerprint(),w.rng.draws)==(final["rng"],final["draws"])
        for name,got in {
            "energy":w.energy(),"injected":w.injected,"unabsorbed":w.unabsorbed,
            "dissipated":w.dissipated,"formed":w.bonds_formed_total,
            "broken":w.bonds_broken_total
        }.items():
            assert final[name]==got,(row["seed"],arm,name)
        ledger(w,w.configured_energy())
    return True


def main():
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    assert source["schema"]=="alife-m7-10-full-640-natural-first-new-link-functional-outcomes-v1"
    rows=source["worlds"]
    assert len(rows)==640
    assert [r["seed"] for r in rows]==list(range(28001,28641))
    old=old_selector.protocol()
    selection_verified=0
    forks_verified=0
    for idx,row in enumerate(rows):
        parent,cohort,first,reason=derive_native_acquisition(row["seed"],old)
        assert row["qualifies"]==(parent is not None)
        if parent is not None:
            assert reason=="first_prebreak_native_recruited_edge"
            assert parent.state_hash_full()==row["selected_native_poststep_full_hash"],(row["seed"],"parent hash")
            assert parent.rng.fingerprint()==row["selected_native_rng"]
            assert parent.rng.draws==row["selected_native_draws"]
            assert list(first["pair"])==row["first_native_new_recruited_link"]["native_first_link"]
            assert first["outsider"]==row["first_native_new_recruited_link"]["native_first_recruited_outsider_id"]
            assert first["relative_tick"]==row["first_native_new_recruited_link"]["first_link_native_form_relative_tick"]
            assert first["absolute_tick"]==row["first_native_new_recruited_link"]["first_link_world_absolute_tick"]
            assert list(cohort["ids"])==row["source"]["ids"]
            assert independent_fork_check(row,parent,cohort,first)
            forks_verified+=3
        else:
            assert reason==row["selection"]["reason"],(row["seed"],"null source reason")
        selection_verified+=1
        if (idx+1)%40==0:
            print(f"M710_INDEPENDENT_PROGRESS sources={idx+1}/640 forks={forks_verified}",flush=True)
    assert selection_verified==640
    assert forks_verified==3*source["summary"]["eligible_first_prebreak_recruited_native_bond"]
    assert source["summary"]["paired_comparisons"]["primary_kept_link_conduction_vs_selected_edge_transport_suppressed"]["discordant"]==0
    assert source["summary"]["paired_comparisons"]["secondary_kept_link_vs_energy_refunded_excised_link"]["favor_native_intact"]==12
    assert source["summary"]["paired_comparisons"]["secondary_kept_link_vs_energy_refunded_excised_link"]["favor_control"]==21
    result={
        "schema":"alife-m7-10-posthoc-independent-full-physical-source-replay-v1",
        "all_native_640_source_selection_scenarios_replayed":True,
        "native_original_M7_3_conduction_replayed_without_M710_detector":True,
        "independent_material_source_graph_and_native_break_event_observers":True,
        "all_qualified_forks_replayed_and_full_final_hashes_RNG_ledgers_matched":True,
        "original_seed_worlds_recreated":640,
        "eligible_selected_worlds":forks_verified//3,
        "individual_full_120_step_forks_reproduced":forks_verified,
        "primary_discordant_paired_worlds":0,
        "secondary_favorable_native_intact":12,
        "secondary_favorable_excised":21,
        "same_sample_correctness_not_new_independent_statistical_replication":True,
        "preregistered_verdict_unchanged":True
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M710_INDEPENDENT_FINAL="+json.dumps({
        "original_sources":640,"selected":forks_verified//3,
        "fully_reproduced_forks":forks_verified,"pass":True
    },sort_keys=True),flush=True)


if __name__=="__main__":
    main()
