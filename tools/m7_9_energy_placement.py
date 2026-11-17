"""M7.9 — preregistered frozen native cohort energy-placement ablation.

All parent worlds selected using ORIGINAL M7.5; baseline M7.3 bond-only
conduction unchanged; M7.8 original experimental M6-compatible isolated
pair-keyed chemistry unchanged. The only NEW intervention is to assign the
EXACT same original-cohort post-conduction energy multiset to different
cohort material IDs, four deterministic frozen permutations per seed.

Scrambling is a deliberate nonphysical CONTROL for LOCATION specificity,
not a spontaneous physical rule or an implementable native energy process.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from tools import m7_5_mature_feedback as reference
from tools.m7_3_bond_energy import energy_transfer
from tools.m6_5_ring_forks import clone_world
from tools.m7_7_cohort_mechanism import interface_potential
from tools.m7_8_frozen_reactions import formation_only_pair_keyed
from tools.m7_2_energy_distribution import ledger

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_9_placement"
PFILE=BASE/"protocol.json"
OUT=BASE/"results.json"
OLD_SOURCE=ROOT/"tools/m7_5_mature_feedback.py"
OLD_M78=ROOT/"tools/m7_8_frozen_reactions.py"
RANKS=(0,1,2,3)
SALTS=tuple(range(32))
SEED_FIRST=27001
SEED_LAST=27640
ARMS=("sham","bond_only","root_scramble_0","root_scramble_1","root_scramble_2","root_scramble_3")


def protocol():
    p=json.loads(PFILE.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-9-frozen-root-energy-placement-ablation-v1"
    assert p["status"]=="preregistered_before_implementation_and_results"
    assert (p["sample"]["seed_first"],p["sample"]["seed_last"],p["sample"]["count"])==(SEED_FIRST,SEED_LAST,640)
    assert p["interventions"]["permutation_ranks"]==list(RANKS)
    assert len(p["sample"]["shards"])==16
    assert [k for d in p["sample"]["shards"] for k in range(d["start"],d["end"]+1)]==list(range(SEED_FIRST,SEED_LAST+1))
    assert reference.protocol()["design"]["parent_scan_start_tick"]==120
    assert p["integrity"]["original_native_src_master_all_history_unchanged"]
    return p


def provenance():
    return {
        "m79_protocol_sha256":sha256(PFILE.read_bytes()).hexdigest(),
        "original_m75_selection_sha256":sha256(OLD_SOURCE.read_bytes()).hexdigest(),
        "original_m78_pairwise_chemistry_sha256":sha256(OLD_M78.read_bytes()).hexdigest(),
    }


def order_by_hash(seed,rank,root_ids):
    assert rank in RANKS
    assert SEED_FIRST<=seed<=SEED_LAST
    ids=tuple(sorted(root_ids))
    assert len(set(ids))==len(ids)
    return tuple(sorted(ids,key=lambda material:(
        sha256(f"alife-m7-9|{seed}|{rank}|{material}".encode("ascii")).digest(),
        material
    )))


def root_energy(w,root_ids):
    return tuple(w.store.energy[w.store.index_of(i)] for i in sorted(root_ids))


def nonroot_energy_signature(w,root_ids):
    root=set(root_ids)
    return sha256(json.dumps([
        [identifier,w.store.energy[w.store.index_of(identifier)]]
        for identifier in sorted(w.store.ids)
        if identifier not in root
    ],separators=(",",":")).encode("utf-8")).hexdigest()


def fixed_graph_signature(w):
    s=w.store
    return (
        tuple(s.ids),tuple(s.xs),tuple(s.ys),tuple(s.species),
        tuple(sorted(s.bonds.items())),tuple(s.degree)
    )


def root_permute(postbond,root_ids,seed,rank):
    """Exact original cohort energy multiset, reassigned by frozen hash rank."""
    w=clone_world(postbond)
    origin_ids=tuple(sorted(root_ids))
    origin_values=root_energy(w,origin_ids)
    graph=fixed_graph_signature(w)
    total=w.energy()
    rng=w.rng.fingerprint(),w.rng.draws
    exterior=nonroot_energy_signature(w,origin_ids)
    targets=order_by_hash(seed,rank,origin_ids)
    for value,identifier in zip(origin_values,targets):
        w.store.energy[w.store.index_of(identifier)]=value
    permuted=root_energy(w,origin_ids)
    assert tuple(sorted(permuted))==tuple(sorted(origin_values))
    assert sum(permuted)==sum(origin_values)
    assert fixed_graph_signature(w)==graph
    assert w.energy()==total
    assert nonroot_energy_signature(w,origin_ids)==exterior
    assert (w.rng.fingerprint(),w.rng.draws)==rng
    w.check()
    ledger(w,w.configured_energy())
    return w,{
        "rank":rank,
        "target_ids_for_ascending_original_energy_order":list(targets),
        "root_energy_id_ascending":list(permuted),
        "positions_whose_energy_changed":sum(a!=b for a,b in zip(permuted,origin_values)),
        "same_energy_multiset_as_original_bond_only":True,
        "same_root_total_energy":True,
        "outside_original_cohort_energy_unchanged":True
    }


def one_arm(w,source_ids,seed,metadata):
    """All 32 chemistry lotteries share exact same per-pair original hash draw."""
    before_hash=w.state_hash_full()
    before_rng=w.rng.fingerprint(),w.rng.draws
    before_energy=w.energy()
    static=interface_potential(w,source_ids)
    shots=[]
    for salt in SALTS:
        fresh=clone_world(w)
        outcome=formation_only_pair_keyed(fresh,source_ids,seed,salt)
        assert outcome["salt"]==salt
        shots.append(outcome)
    assert w.state_hash_full()==before_hash
    assert (w.rng.fingerprint(),w.rng.draws)==before_rng
    assert w.energy()==before_energy
    total=sum(x["formed_original_to_external"] for x in shots)
    return {
        "intervention_metadata":metadata,
        "after_energy_intervention_full_hash":before_hash,
        "rng_unchanged":True,"ledger_ok":True,
        "native_energetic_boundary_interface":static,
        "source_energy_post":list(root_energy(w,source_ids)),
        "lotteries":shots,
        "total_source_external_bonds_across_32_salts":total,
        "mean_source_external_bonds_per_salt":round(total/len(SALTS),6),
        "salts_with_any_source_attachment":sum(x["formed_original_to_external"]>0 for x in shots)
    }


def run_one(seed,old,replay=False):
    parent,selected,selection=reference.select_parent(seed,old)
    if selected is None:
        return {
            "seed":seed,"selected":False,
            "scanned_parent_ticks":parent.step,
            "reason":"no_eligible_native_M7_5_cohort"
        }
    root_ids=tuple(sorted(selected["ids"]))
    old_hash=parent.state_hash_full()
    old_rng=parent.rng.fingerprint(),parent.rng.draws
    old_total=parent.energy()
    root_pre=root_energy(parent,root_ids)
    exterior_pre=nonroot_energy_signature(parent,root_ids)
    parent_graph=fixed_graph_signature(parent)

    conducted=clone_world(parent)
    t,b,u=energy_transfer(conducted,"bond_only")
    assert b==t and u==0
    assert fixed_graph_signature(conducted)==parent_graph
    assert (conducted.rng.fingerprint(),conducted.rng.draws)==old_rng
    assert conducted.energy()==old_total
    post=root_energy(conducted,root_ids)
    assert sum(post)==sum(root_pre),("maximal native cohort should contain only internal current bonds")
    conducted_nonroot=nonroot_energy_signature(conducted,root_ids)

    arms={}
    arms["sham"]=one_arm(parent,root_ids,seed,{"physical_bond_conduction_passes":0,"scramble":False})
    arms["bond_only"]=one_arm(conducted,root_ids,seed,{
        "physical_bond_conduction_passes":1,
        "original_m73_native_transfers":t,
        "scramble":False
    })
    for rank in RANKS:
        shuffled,meta=root_permute(conducted,root_ids,seed,rank)
        assert nonroot_energy_signature(shuffled,root_ids)==conducted_nonroot
        arms[f"root_scramble_{rank}"]=one_arm(shuffled,root_ids,seed,meta)
    assert set(arms)==set(ARMS)
    assert arms["sham"]["after_energy_intervention_full_hash"]==old_hash
    assert arms["bond_only"]["source_energy_post"]==list(post)
    assert arms["sham"]["source_energy_post"]==list(root_pre)
    assert nonroot_energy_signature(parent,root_ids)==exterior_pre
    assert fixed_graph_signature(parent)==parent_graph
    assert parent.state_hash_full()==old_hash
    assert (parent.rng.fingerprint(),parent.rng.draws)==old_rng

    if replay:
        independent,cohort,_=reference.select_parent(seed,old)
        assert independent.state_hash_full()==old_hash
        assert tuple(cohort["ids"])==tuple(selected["ids"])
        independent_bond=clone_world(independent)
        assert energy_transfer(independent_bond,"bond_only")==(t,t,0)
        assert independent_bond.state_hash_full()==arms["bond_only"]["after_energy_intervention_full_hash"]
        for name,root_state in (
            ("sham",independent),
            ("bond_only",independent_bond),
            ("root_scramble_0",root_permute(independent_bond,root_ids,seed,0)[0])
        ):
            oracle=formation_only_pair_keyed(clone_world(root_state),root_ids,seed,0)
            assert oracle==arms[name]["lotteries"][0],(seed,name,"first-shard unmodified original reaction replay")
    return {
        "seed":seed,"selected":True,
        "parent_tick":parent.step,
        "native_source":selected,
        "selected_without_future_outcomes":selection,
        "native_parent_full_hash":old_hash,
        "native_parent_rng_fingerprint":old_rng[0],
        "native_parent_rng_draws":old_rng[1],
        "original_root_energy_id_order":list(root_pre),
        "post_bond_root_energy_id_order":list(post),
        "root_energy_multiset_post_bond":sorted(post),
        "root_energy_total_unchanged_by_bond_pass":True,
        "root_energy_total":sum(post),
        "external_energy_sha256_parent":exterior_pre,
        "external_energy_sha256_post_bond":conducted_nonroot,
        "bond_only_native_transfer_events":t,
        "arms":arms
    }


def compare_treatment(rows,calc):
    favor=against=ties=0
    deltas=[]
    for r in rows:
        delta=calc(r)
        deltas.append(delta)
        if delta>0:favor+=1
        elif delta<0:against+=1
        else:ties+=1
    n=favor+against
    assert n+ties==len(rows)
    return {
        "favor_original_bond_placement":favor,
        "favor_randomized_placement":against,
        "ties":ties,
        "discordant":n,
        "favorable_fraction":round(favor/n,6) if n else None,
        "mean_fourfold_delta":round(sum(deltas)/len(deltas),6) if deltas else None
    }


def summarize(rows,p):
    assert len(rows)==640
    assert [r["seed"] for r in rows]==list(range(SEED_FIRST,SEED_LAST+1))
    sample=[r for r in rows if r["selected"]]
    n=len(sample)
    def avg(values):
        return round(sum(values)/len(values),6) if values else None
    def q(r,arm):
        return r["arms"][arm]["native_energetic_boundary_interface"]["energy_qualified_boundary_contacts"]
    def f(r,arm):
        return r["arms"][arm]["total_source_external_bonds_across_32_salts"]
    eligible=compare_treatment(sample,lambda r:4*q(r,"bond_only")-sum(q(r,f"root_scramble_{j}") for j in RANKS))
    formed=compare_treatment(sample,lambda r:4*f(r,"bond_only")-sum(f(r,f"root_scramble_{j}") for j in RANKS))
    def gate(x,min_disc):
        if n<40 or x["discordant"]<min_disc:
            return "not_met_insufficient_discordants"
        return "passed" if 3*x["favor_original_bond_placement"]>=2*x["discordant"] else "not_met_favorable_fraction"
    def armstats(a):
        return {
            "mean_static_energetic_boundary_contacts":avg([q(r,a) for r in sample]),
            "mean_new_external_bonds_over_32_coupled_salts":avg([f(r,a) for r in sample]),
            "source_worlds_with_any_new_external_bond_in_32_salts":sum(f(r,a)>0 for r in sample),
            "mean_root_sites_energy_changed_relative_to_original_bond":avg([
                r["arms"][a]["intervention_metadata"].get("positions_whose_energy_changed",0)
                for r in sample])
        }
    perarm={a:armstats(a) for a in ARMS}
    controls={
        "mean_scrambled_static_interface_over_four_rank_conditions":avg([
            sum(q(r,f"root_scramble_{j}") for j in RANKS)/4 for r in sample
        ]),
        "mean_scrambled_new_external_bonds_over_32_salts":avg([
            sum(f(r,f"root_scramble_{j}") for j in RANKS)/4 for r in sample
        ]),
        "source_worlds_with_all_four_scrambles_energy_vector_unchanged":sum(
            all(r["arms"][f"root_scramble_{j}"]["intervention_metadata"]["positions_whose_energy_changed"]==0
                for j in RANKS) for r in sample),
        "mean_original_bond_transport_events":avg([r["bond_only_native_transfer_events"] for r in sample]),
        "original_source_topologies":{
            "tree":sum(r["native_source"]["cyclomatic_number"]==0 for r in sample),
            "cyclic":sum(r["native_source"]["cyclomatic_number"]>0 for r in sample)
        }
    }
    return {
        "source_seed_count":640,
        "native_cohorts_selected":n,
        "native_cohorts_absent":640-n,
        "root_placement_arms":list(ARMS),
        "per_arm":perarm,
        "comparisons":{
            "primary_equal_root_energy_multiset_static_pair_eligibility":eligible,
            "secondary_equal_root_energy_multiset_actual_coupled_external_formations":formed
        },
        "descriptive_controls":controls,
        "preregistered_decisions":{
            "primary_original_location_advantage":gate(eligible,25),
            "secondary_original_location_reaction_advantage":gate(formed,20),
            "minimum_source_worlds":40,
            "minimum_eligible_discordants":25,
            "minimum_reaction_discordants":20,
            "required_seed_fraction":"2/3",
            "all_original_chemistry_and_conduction_untouched":True
        },
        "caveats":"Scrambles are NONPHYSICAL spatial-energy permutation ablations; they preserve the exact root energy multiset and all native geometry/bonds but need not be achievable by one locally allowed transfer pass. Within-source 4 ranks and 32 lotteries are not independent source units. Success would support native energy PLACEMENT advantage versus this artificial shuffle, NOT emergent self-maintenance or metabolism."
    }


def run_shard(start,end):
    p=protocol()
    d={"start":start,"end":end}
    assert d in p["sample"]["shards"]
    old=reference.protocol()
    rows=[]
    first=None
    for seed in range(start,end+1):
        r=run_one(seed,old,replay=(first is None))
        rows.append(r)
        if r["selected"] and first is None:first=seed
        if (seed-start+1)%10==0:
            print(f"M79_PROGRESS {start}-{end} seed={seed} selected={sum(x['selected'] for x in rows)}",flush=True)
    obj={
        "schema":"alife-m7-9-shard-v1",
        "descriptor":d,
        "provenance":provenance(),
        "source_worlds":rows,
        "first_original_source_and_reaction_replay_seed":first,
        "all_src_and_historical_code_unchanged":True
    }
    path=BASE/"shards"/f"seeds-{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M79_SHARD="+json.dumps({
        "start":start,"end":end,"worlds":len(rows),
        "selected":sum(r["selected"] for r in rows),"replay":first
    },sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("seeds-*.json"))
    assert len(files)==16,(len(files),"exact shards required")
    prov=provenance()
    seen=[]
    worlds=[]
    sentinels=[]
    for path in files:
        chunk=json.loads(path.read_text(encoding="utf-8"))
        assert chunk["schema"]=="alife-m7-9-shard-v1"
        assert chunk["provenance"]==prov
        assert chunk["all_src_and_historical_code_unchanged"]
        desc=chunk["descriptor"]
        assert desc in p["sample"]["shards"] and desc not in seen
        seen.append(desc)
        rows=chunk["source_worlds"]
        assert [r["seed"] for r in rows]==list(range(desc["start"],desc["end"]+1))
        first=next((r["seed"] for r in rows if r["selected"]),None)
        assert first==chunk["first_original_source_and_reaction_replay_seed"]
        if first is not None:sentinels.append(first)
        worlds.extend(rows)
    assert all(s in seen for s in p["sample"]["shards"])
    worlds.sort(key=lambda x:x["seed"])
    summary=summarize(worlds,p)
    payload={
        "schema":"alife-m7-9-full-native-root-placement-640-world-audit-v1",
        "provenance":prov,
        "worlds":worlds,
        "first_selection_and_pairwise_replay_seed_per_nonempty_shard":sentinels,
        "summary":summary,
        "all_640_seeds_in_16_shards":True,
        "unmodified_M6_M7_3_M7_5_M7_7_M7_8":True
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print("M79_FINAL_SUMMARY="+json.dumps(summary,sort_keys=True),flush=True)
    print("M79_SUCCESS="+str(len(worlds)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="cmd",required=True)
    sh=sub.add_parser("shard")
    sh.add_argument("--start",type=int,required=True)
    sh.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    args=parser.parse_args()
    if args.cmd=="shard":run_shard(args.start,args.end)
    else:merge()


if __name__=="__main__":
    main()
