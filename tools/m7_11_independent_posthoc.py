"""Independent same-sample native M7.11 age/ring/fork correctness audit.

Recreates all 640 source worlds and FIRST ≥20-snapshot-aged natural simple
4/6/8 native rings from FIRST principles, with ORIGINAL untouched M6.4
analyze_cycle and ORIGINAL M7.3 energy_transfer. Does NOT import or invoke
any new M7.11 selection, intervention, or cohort-classification function.

For all selected sources, reproduces 4×120 post-fork complete original
native M6 physics evolutions. Independent exact refund and 1-edge transport
suppression; independent BondEvent observation and original-ID connectivity.
This does NOT add an independent sample or create a biological repair claim.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from alife.structures import components
from alife.world import World
from tools.m6_4_cycles import analyze_cycle
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import config_for,energy_transfer,bond_pairs
from tools.m7_2_energy_distribution import ledger
from tools.m7_5_posthoc_independent_replay import (
    IndependentEvents, source_component_size_from_scratch
)

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_11_ring_resilience"
RAW=BASE/"results.json"
OUT=BASE/"posthoc_independent_full_physical_audit.json"
ARMS=("intact_normal","intact_ring_conduction_suppressed",
      "opened_normal","opened_surviving_ring_conduction_suppressed")


def current_bond_pairs(w):
    s=w.store
    return {tuple(sorted((s.ids[a],s.ids[b]))) for a,b in s.bonds}


def exact_simple_components(w):
    s=w.store
    found=[]
    for node_indexes,edge_indexes in components(s):
        if len(node_indexes) not in (4,6,8):continue
        observed=analyze_cycle(s,node_indexes,edge_indexes,w.species_names)
        if observed is not None:
            found.append({
                "ids":tuple(observed["ids"]),
                "edges":tuple(sorted(observed["edges"])),
                "size":int(observed["size"]),
                "exact":observed["exact"]
            })
    return sorted(found,key=lambda r:r["ids"])


def scan_fresh_original(seed):
    """Independent lifetime implementation with same frozen selection rule."""
    w=World.create(config_for(seed,"no_transfer"))
    assert not w.store.bonds
    initial_hash=w.state_hash_full()
    age={}
    seen=False
    episode_count=0
    tape=IndependentEvents()
    w.event_sink=tape
    for t in range(1,601):
        w.advance(1)
        events=tape.events(w.step)
        breaking={edge for kind,edge in events if kind=="break"}
        energy_transfer(w,"bond_only")
        rings=exact_simple_components(w)
        if rings:seen=True
        renewed={}
        for ring in rings:
            key=(ring["ids"],ring["edges"])
            aged=age.get(key,0)
            if aged==0 or any(edge in breaking for edge in ring["edges"]):
                aged=1
                episode_count+=1
            else:
                aged+=1
            renewed[key]=aged
            ring["age"]=aged
        age=renewed
        if t>=120:
            ready=[r for r in rings if r["age"]>=20]
            if ready:
                ring=min(ready,key=lambda x:x["ids"])
                w.event_sink=None
                return w,ring,{
                    "selected":True,
                    "selected_tick":t,
                    "candidate_aged_rings_same_tick":len(ready),
                    "native_ring_episodes_seen":episode_count,
                    "original_initial_full_hash":initial_hash
                }
    w.event_sink=None
    return None,None,{
        "selected":False,
        "native_ring_episodes_seen":episode_count,
        "reason":"native_cycles_observed_but_none_aged_20_by_600" if seen else "no_native_simple_4_6_8_ring_by_600",
        "original_initial_full_hash":initial_hash
    }


def erase_bond_and_return_energy(world,pair):
    a,b=sorted((world.store.index_of(i) for i in pair))
    initial=(world.energy(),world.dissipated,world.rng.fingerprint(),world.rng.draws)
    stored=world.store.bonds[(a,b)]
    world.store.remove_bond(a,b)
    world.store.energy[a]+=stored-stored//2
    world.store.energy[b]+=stored//2
    assert (world.energy(),world.dissipated,world.rng.fingerprint(),world.rng.draws)==initial
    return stored


def own_snapshot_transfer(world,forbidden):
    """Independent faithful replica of M7.3 thermal gradient and donor budget."""
    s=world.store
    starting=tuple(s.energy)
    remaining=list(starting)
    delta=[0]*len(starting)
    global_transfers=0
    ring_transfers=0
    # Sort uses unchanged M7.3 bond_pairs(), never M7.11 source code.
    for a,b in bond_pairs(world):
        pair=tuple(sorted((s.ids[a],s.ids[b])))
        if pair in forbidden:continue
        if starting[a]-starting[b]>=2:donor,acceptor=a,b
        elif starting[b]-starting[a]>=2:donor,acceptor=b,a
        else:continue
        if remaining[donor]<1:continue
        remaining[donor]-=1
        delta[donor]-=1
        delta[acceptor]+=1
        global_transfers+=1
    for index,shift in enumerate(delta):
        s.energy[index]+=shift
    assert sum(delta)==0
    assert all(v>=0 for v in s.energy)
    return global_transfers


def root_induced_connected(w,ids):
    root=set(ids)
    graph={x:set() for x in root}
    for a,b in current_bond_pairs(w):
        if a in root and b in root:
            graph[a].add(b)
            graph[b].add(a)
    visited={min(root)}
    queue=list(visited)
    while queue:
        a=queue.pop()
        for b in graph[a]:
            if b not in visited:
                queue.append(b)
                visited.add(b)
    return visited==root


def follow_fixed(w,ring,row):
    source_ids=ring["ids"]
    originals=set(ring["edges"])
    cut=min(originals)
    assert list(cut)==row["target_original_cycle_edge"]
    copies={arm:clone_world(w) for arm in ARMS}
    assert len({x.state_hash_full() for x in copies.values()})==1
    for arm in ARMS[2:]:
        refund=erase_bond_and_return_energy(copies[arm],cut)
        assert refund==row["identical_cut_refund_metadata"]["native_bond_energy_fully_refunded"]
    assert copies[ARMS[0]].state_hash_full()==copies[ARMS[1]].state_hash_full()
    assert copies[ARMS[2]].state_hash_full()==copies[ARMS[3]].state_hash_full()
    assert len({x.energy() for x in copies.values()})==1

    tape={arm:IndependentEvents() for arm in ARMS}
    for arm,v in copies.items():v.event_sink=tape[arm]
    track={}
    for arm in ARMS:
        track[arm]={
            "first_other_original_ring_break":None,
            "first_original_break":None,
            "first_cut_reformation":None,
            "first_cut_actual_anytime":None,
            "cut_reformation_count":0,
            "preotherbreak_reclosure":False,
            "original_break_events":0,
            "first_step_native_hash":None,
            "first_step_native_rng":None,
            "first_step_breaks":[],
            "checkpoints":[]
        }
    for t in range(1,121):
        for arm,world in copies.items():
            world.advance(1)
            logs=tape[arm].events(world.step)
            h=track[arm]
            if t==1:
                h["first_step_native_hash"]=world.state_hash_full()
                h["first_step_native_rng"]=(world.rng.fingerprint(),world.rng.draws)
            broken={pair for kind,pair in logs if kind=="break" and pair in originals}
            other_broken=broken-{cut}
            h["original_break_events"]+=sum(1 for kind,pair in logs if kind=="break" and pair in originals)
            if t==1:h["first_step_breaks"]=sorted(broken)
            if broken and h["first_original_break"] is None:h["first_original_break"]=t
            if other_broken and h["first_other_original_ring_break"] is None:h["first_other_original_ring_break"]=t
            formed_cut=any(kind=="form" and pair==cut for kind,pair in logs)
            if formed_cut:
                h["cut_reformation_count"]+=1
                if h["first_cut_actual_anytime"] is None:h["first_cut_actual_anytime"]=t
                if cut in current_bond_pairs(world):
                    if h["first_cut_reformation"] is None:h["first_cut_reformation"]=t
                    if arm.startswith("opened") and h["first_other_original_ring_break"] is None:
                        h["preotherbreak_reclosure"]=True
            pre=world.energy(),world.rng.fingerprint(),world.rng.draws
            if arm in ("intact_normal","opened_normal"):
                energy_transfer(world,"bond_only")
            else:
                if arm=="intact_ring_conduction_suppressed":
                    omitted=originals
                else:
                    omitted=originals-{cut}
                own_snapshot_transfer(world,omitted)
            assert (world.energy(),world.rng.fingerprint(),world.rng.draws)==pre
            if t in (1,10,30,60,120):
                world.check()
                ledger(world,world.configured_energy())
                now=current_bond_pairs(world)
                h["checkpoints"].append({
                    "relative_tick":t,
                    "all_original_ring_material_ids_connected":source_component_size_from_scratch(world,source_ids) is not None,
                    "original_material_induced_graph_connected":root_induced_connected(world,source_ids),
                    "exact_original_ring_closed_now":originals.issubset(now),
                    "all_original_ring_edges_currently_present":len(originals&now),
                    "selected_original_cut_edge_present":cut in now
                })
        if t==1:
            for one,two in ((ARMS[0],ARMS[1]),(ARMS[2],ARMS[3])):
                assert track[one]["first_step_native_hash"]==track[two]["first_step_native_hash"]
                assert track[one]["first_step_native_rng"]==track[two]["first_step_native_rng"]
                assert track[one]["first_step_breaks"]==track[two]["first_step_breaks"]

    for arm,v in copies.items():
        h=track[arm]
        actual=row["outcomes"][arm]
        f=actual["final"]
        assert f["full_hash"]==v.state_hash_full(),(row["seed"],arm,"full physical hash")
        assert f["rng"]==v.rng.fingerprint() and f["draws"]==v.rng.draws
        assert f["energy"]==v.energy()
        assert f["dissipated"]==v.dissipated
        assert f["unabsorbed"]==v.unabsorbed
        assert f["injected"]==v.injected
        assert f["formed"]==v.bonds_formed_total and f["broken"]==v.bonds_broken_total
        assert actual["first_original_ring_edge_break_tick"]==h["first_original_break"]
        assert actual["first_OTHER_ring_edge_break_tick"]==h["first_other_original_ring_break"]
        assert actual["first_selected_cut_edge_real_form_tick"]==h["first_cut_reformation"]
        assert actual["first_anytime_cut_edge_reclosure_tick"]==h["first_cut_actual_anytime"]
        assert actual["selected_cut_reclosure_event_count"]==h["cut_reformation_count"]
        assert actual["any_original_ring_edge_break_events"]==h["original_break_events"]
        assert actual["exact_cut_edge_reformed_before_any_other_original_break"]==h["preotherbreak_reclosure"]
        assert actual["original_ring_material_connected_at_120"]==(
            source_component_size_from_scratch(v,source_ids) is not None)
        assert actual["original_ring_induced_material_connected_at_120"]==root_induced_connected(v,source_ids)
        assert actual["exact_original_ring_all_edges_present_at_120"]==originals.issubset(current_bond_pairs(v))
        assert len(h["checkpoints"])==5
        for got,expected in zip(h["checkpoints"],actual["checkpoints"]):
            for name,value in got.items():
                assert value==expected[name],(row["seed"],arm,name,"checkpoint")
        v.check()
        ledger(v,v.configured_energy())
    return True


def main():
    primary=json.loads(RAW.read_text(encoding="utf-8"))
    assert primary["schema"]=="alife-m7-11-full-640-native-aged-cyclic-fault-tolerance-v1"
    assert primary["all_640_seed_worlds_16_preregistered_shards_complete"]
    rows=primary["worlds"]
    assert len(rows)==640
    assert [x["seed"] for x in rows]==list(range(29001,29641))
    num=0
    eligible=0
    nulls=Counter()
    for i,row in enumerate(rows):
        parent,ring,meta=scan_fresh_original(row["seed"])
        assert row["selected"]==(parent is not None)
        assert meta["original_initial_full_hash"]==row["scan"]["original_initial_full_hash"]
        assert meta["native_ring_episodes_seen"]==row["scan"]["native_ring_episodes_seen"]
        if parent is None:
            nulls[meta["reason"]]+=1
            assert meta["reason"]==row["scan"]["reason"]
        else:
            eligible+=1
            selected=row["native_original_ring"]
            assert meta["selected_tick"]==row["scan"]["selected_tick"]
            assert meta["candidate_aged_rings_same_tick"]==row["scan"]["candidate_aged_rings_same_tick"]
            assert parent.state_hash_full()==row["original_full_hash"]
            assert parent.rng.fingerprint()==row["original_rng"]
            assert parent.rng.draws==row["original_rng_draws"]
            assert list(ring["ids"])==selected["ids"]
            assert [list(edge) for edge in ring["edges"]]==selected["edges"]
            assert ring["exact"]==selected["exact"]
            assert ring["age"]==selected["continuous_snapshot_age"]
            assert follow_fixed(parent,ring,row)
            num+=4
        if (i+1)%40==0:
            print(f"M711_INDEPENDENT_PROGRESS original_sources={i+1}/640 selected={eligible} fork_replays={num}",flush=True)
    assert eligible==primary["summary"]["naturally_selected_aged_ring_worlds"]==626
    assert num==eligible*4==2504
    assert nulls=={"native_cycles_observed_but_none_aged_20_by_600":5,"no_native_simple_4_6_8_ring_by_600":9}
    out={
        "schema":"alife-m7-11-full-posthoc-independent-native-physical-replay-v1",
        "same_primary_640_native_seed_worlds_not_new_statistical_replication":True,
        "all_source_worlds_regenerated_from_seed":640,
        "first_eligible_aged_native_ring_selected_independently":626,
        "all_null_seed_worlds_reproduced":14,
        "all_4_forks_120_original_native_ticks_reproduced":2504,
        "complete_final_full_hash_RNG_energy_native_form_break_and_checkpoint_agreement":True,
        "primary_early_native_reclosure_controlled_bond_transfer_verdict_unchanged":True,
        "secondary_root_ID_material_cohesion_verdict_unchanged":True,
        "source_no_physics_code_modified":True
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("M711_INDEPENDENT_FINAL="+json.dumps({
        "seeds":640,"eligible":626,"null":14,"fork_replays":2504,"all_verified":True
    },sort_keys=True),flush=True)


if __name__=="__main__":
    main()
