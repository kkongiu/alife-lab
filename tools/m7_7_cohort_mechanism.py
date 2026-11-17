"""M7.7 — preregistered mechanistic audit on held-out native material cohorts.

Selection and physics = UNCHANGED M7.5 source selection, M7.3 energy_transfer,
and original native World.advance. All observations are RNG-free. A post-step
candidate is NOT an earlier same-tick native chemical formation lottery.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.chemistry import _candidate_pairs
from tools.m6_5_ring_forks import clone_world
from tools.m7_2_energy_distribution import contacts, ledger
from tools.m7_3_bond_energy import energy_transfer, bond_pairs
from tools import m7_5_mature_feedback as reference
from tools.m7_4_material_feedback import EventTape, native_pairs, coherent_root_size

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_7_mechanism"
PFILE=BASE/"protocol.json"
RESULTS=BASE/"results.json"
REF_SOURCE=ROOT/"tools/m7_5_mature_feedback.py"
REF_PROTOCOL=ROOT/"campaigns/m7_5_mature/protocol.json"
ARMS=("no_transfer","bond_only","all_contacts")
HORIZON=120


def protocol():
    p=json.loads(PFILE.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-7-native-cohort-energy-opportunity-audit-v1"
    assert p["status"]=="preregistered_before_runner_tests_and_outcomes"
    d=p["design"]
    assert (d["seeds_first"],d["seeds_last"],d["worlds"])==(25001,25320,320)
    assert d["follow_steps"]==HORIZON and d["arm_types"]==list(ARMS)
    assert len(d["shards"])==8
    assert [seed for s in d["shards"] for seed in range(s["start"],s["end"]+1)]==list(range(25001,25321))
    old=reference.protocol()
    assert (old["design"]["parent_scan_start_tick"],old["design"]["parent_scan_stop_tick"])==(120,500)
    assert old["design"]["followup_steps"]==120
    return p


def provenance():
    return {
        "m77_protocol_sha256":sha256(PFILE.read_bytes()).hexdigest(),
        "original_m75_runner_sha256":sha256(REF_SOURCE.read_bytes()).hexdigest(),
        "original_m75_protocol_sha256":sha256(REF_PROTOCOL.read_bytes()).hexdigest()
    }


def interface_potential(w,material):
    """Poststep native local static opportunities, without RNG consumption.

    - geometric original-external unbonded contacts
    - chemical species+valence-qualified subset, energy ignored
    - energy-qualified subset exactly as native chemistry._candidate_pairs

    Chemistry is executed BEFORE optional poststep transport, so these are
    NEXT-step prospective static opportunities, not draws made at this step.
    """
    s=w.store
    roots=set(material)
    before=w.rng.fingerprint(),w.rng.draws
    geometrical=chemical=energy_ready=0
    actual=set()
    for ia,ib in _candidate_pairs(w):
        if (s.ids[ia] in roots)!=(s.ids[ib] in roots):
            actual.add((ia,ib))
    energy_set=set()
    for a,b in contacts(s):
        if (s.ids[a] in roots)==(s.ids[b] in roots):
            continue
        if (a,b) in s.bonds or (b,a) in s.bonds:
            continue
        geometrical+=1
        sa,sb=s.species[a],s.species[b]
        if not ((sa,sb) in w.allowed_pairs or (sb,sa) in w.allowed_pairs):
            continue
        if s.degree[a]>=w.max_bonds[sa] or s.degree[b]>=w.max_bonds[sb]:
            continue
        chemical+=1
        if s.energy[a]>=w.formation_cost and s.energy[b]>=w.formation_cost:
            energy_ready+=1
            energy_set.add((a,b))
    assert actual==energy_set,("candidate mismatch",actual,energy_set)
    assert geometrical>=chemical>=energy_ready
    available=sum(
        s.degree[s.index_of(identifier)]<w.max_bonds[s.species[s.index_of(identifier)]]
        and s.energy[s.index_of(identifier)]>=w.formation_cost
        for identifier in roots
    )
    original_energy=sum(s.energy[s.index_of(identifier)] for identifier in roots)
    assert (w.rng.fingerprint(),w.rng.draws)==before
    return {
        "unbonded_geometrical_boundary_contacts":geometrical,
        "species_valence_qualified_boundary_contacts":chemical,
        "energy_qualified_boundary_contacts":energy_ready,
        "energy_blocked_qualified_contacts":chemical-energy_ready,
        "root_members_energy_and_valence_ready":available,
        "root_material_particle_energy":original_energy
    }


def classify_flux(w,arm,root_ids):
    """Nonmutating replica of ORIGINAL M7.3 proposal order, used for audit only.

    This does not affect the real energy route; after original M7.3
    energy_transfer, its accepted count/route counts and actual root-energy
    change must match these independent prepass predictions.
    """
    if arm=="no_transfer":return (0,0,0,0,0,0)
    s=w.store
    original_energies=tuple(s.energy)
    rem=list(original_energies)
    bonds=set(s.bonds)
    pairs=bond_pairs(w) if arm=="bond_only" else contacts(s)
    roots=set(root_ids)
    all_events=along_bonds=across_nonbond=internal=inflow=outflow=0
    for a,b in pairs:
        if original_energies[a]-original_energies[b]>=2:
            donor,recip=a,b
        elif original_energies[b]-original_energies[a]>=2:
            donor,recip=b,a
        else:continue
        if rem[donor]<1:continue
        rem[donor]-=1
        all_events+=1
        if (a,b) in bonds or (b,a) in bonds:along_bonds+=1
        else:across_nonbond+=1
        donor_root=s.ids[donor] in roots
        recip_root=s.ids[recip] in roots
        if donor_root and recip_root:internal+=1
        elif not donor_root and recip_root:inflow+=1
        elif donor_root and not recip_root:outflow+=1
    assert all_events==along_bonds+across_nonbond
    assert internal+inflow+outflow<=all_events
    if arm=="bond_only":assert across_nonbond==0
    return (all_events,along_bonds,across_nonbond,internal,inflow,outflow)


def transfer_with_audit(w,arm,root_ids):
    before=(w.energy(),w.rng.fingerprint(),w.rng.draws)
    source_before=sum(w.store.energy[w.store.index_of(i)] for i in root_ids)
    forecast=classify_flux(w,arm,root_ids)
    official=energy_transfer(w,arm)
    source_after=sum(w.store.energy[w.store.index_of(i)] for i in root_ids)
    assert tuple(official)==forecast[:3]
    assert source_after-source_before==forecast[4]-forecast[5]
    assert (w.energy(),w.rng.fingerprint(),w.rng.draws)==before
    return forecast


def frozen_immediate(parent,source_ids):
    """A t0 separate material-state clones, no native step, no RNG draw."""
    oldhash=parent.state_hash_full()
    no=clone_world(parent)
    conducted=clone_world(parent)
    pre=interface_potential(no,source_ids)
    f=transfer_with_audit(conducted,"bond_only",source_ids)
    post=interface_potential(conducted,source_ids)
    assert no.state_hash_full()==oldhash
    assert parent.state_hash_full()==oldhash
    assert no.rng.fingerprint()==conducted.rng.fingerprint()
    assert no.rng.draws==conducted.rng.draws
    assert pre["unbonded_geometrical_boundary_contacts"]==post["unbonded_geometrical_boundary_contacts"]
    assert pre["species_valence_qualified_boundary_contacts"]==post["species_valence_qualified_boundary_contacts"]
    return {
        "original_full_world_unchanged":True,
        "source_particle_energy_before":pre["root_material_particle_energy"],
        "source_particle_energy_after_one_bond_pass":post["root_material_particle_energy"],
        "energy_qualified_boundary_before":pre["energy_qualified_boundary_contacts"],
        "energy_qualified_boundary_after":post["energy_qualified_boundary_contacts"],
        "newly_qualified_net":post["energy_qualified_boundary_contacts"]-pre["energy_qualified_boundary_contacts"],
        "pre_original_root_energetic_ready_count":pre["root_members_energy_and_valence_ready"],
        "post_original_root_energetic_ready_count":post["root_members_energy_and_valence_ready"],
        "one_pass_transfer_events":f[0],
        "energy_change_root_equals_boundary_net":True
    }


def follow_with_mechanisms(parent,chosen,reference_replay=False):
    material=tuple(chosen["ids"])
    original=set(chosen["edges"])
    assert original.issubset(native_pairs(parent))
    assert len(material)>=5
    base_hash=parent.state_hash_full()
    base_rng=parent.rng.fingerprint(),parent.rng.draws
    worlds={a:clone_world(parent) for a in ARMS}
    assert len({w.state_hash_full() for w in worlds.values()})==1
    assert len({(w.rng.fingerprint(),w.rng.draws) for w in worlds.values()})==1
    tapes={a:EventTape() for a in ARMS}
    rows={}
    for arm,w in worlds.items():
        w.event_sink=tapes[arm]
        start=interface_potential(w,material)
        rows[arm]={
            "poststep_t0":start,
            "first_original_break_tick":None,
            "first_external_incident_form_tick":None,
            "first_step_original_break_pairs":[],
            "incident_external_formation_count":0,
            "incident_external_formations_before_original_break":0,
            "cumulative":{
                "unbonded_geometrical_boundary_contacts":0,
                "species_valence_qualified_boundary_contacts":0,
                "energy_qualified_boundary_contacts":0,
                "energy_blocked_qualified_contacts":0,
                "root_members_energy_and_valence_ready":0,
                "root_material_particle_energy":0,
            },
            "per_tick_opportunities":[],
            "total_transfer_events":0,
            "transfer_on_existing_native_bonds":0,
            "transfer_on_unbonded_contacts":0,
            "source_internal_passes":0,
            "source_incoming_passes":0,
            "source_outgoing_passes":0,
            "checkpoints":[]
        }
    for t in range(1,HORIZON+1):
        first_step={}
        for arm,w in worlds.items():
            w.advance(1)
            events=tapes[arm].pop(w.step)
            h=rows[arm]
            broken={edge for kind,edge in events if kind=="break"} & original
            new_source=[
                edge for kind,edge in events
                if kind=="form" and ((edge[0] in material)!=(edge[1] in material))
            ]
            if t==1:
                first_step[arm]=broken
                h["first_step_original_break_pairs"]=[list(x) for x in sorted(broken)]
            if broken and h["first_original_break_tick"] is None:
                h["first_original_break_tick"]=t
            if new_source:
                if h["first_external_incident_form_tick"] is None:
                    h["first_external_incident_form_tick"]=t
                h["incident_external_formation_count"]+=len(new_source)
                if h["first_original_break_tick"] is None:
                    h["incident_external_formations_before_original_break"]+=len(new_source)
            flux=transfer_with_audit(w,arm,material)
            for k,v in zip((
                "total_transfer_events","transfer_on_existing_native_bonds",
                "transfer_on_unbonded_contacts","source_internal_passes",
                "source_incoming_passes","source_outgoing_passes"
            ),flux):h[k]+=v
            metric=interface_potential(w,material)
            for key in h["cumulative"]:
                h["cumulative"][key]+=metric[key]
            h["per_tick_opportunities"].append(metric["energy_qualified_boundary_contacts"])
            if t in (1,10,30,60,120):
                ledger(w,w.configured_energy())
                h["checkpoints"].append({
                    "relative_tick":t,
                    **metric,
                    "coherent_root_component_size":coherent_root_size(w,material),
                    "original_material_bonds_intact_in_snapshot":original.issubset(native_pairs(w)),
                    "all_passive_root_boundary_net":h["source_incoming_passes"]-h["source_outgoing_passes"]
                })
        if t==1:
            assert first_step["no_transfer"]==first_step["bond_only"]==first_step["all_contacts"]
    assert parent.state_hash_full()==base_hash
    assert (parent.rng.fingerprint(),parent.rng.draws)==base_rng
    for arm,w in worlds.items():
        ledger(w,w.configured_energy())
        w.check()
        h=rows[arm]
        size=coherent_root_size(w,material)
        h["coherent_growth_at_120"]=size is not None and size>len(material)
        h["all_original_edges_unbroken_120"]=h["first_original_break_tick"] is None
        h["source_incident_prebreak_binary"]=h["incident_external_formations_before_original_break"]>0
        h["final"]={
            "full_hash":w.state_hash_full(),"rng":w.rng.fingerprint(),"draws":w.rng.draws,
            "stored_energy":w.energy(),"injected":w.injected,
            "unabsorbed":w.unabsorbed,"dissipated":w.dissipated,
            "global_new_bonds":w.bonds_formed_total-parent.bonds_formed_total,
            "global_broken_bonds":w.bonds_broken_total-parent.bonds_broken_total
        }
        assert len(h["per_tick_opportunities"])==120
        assert len(h["checkpoints"])==5
        assert sum(h["per_tick_opportunities"])==h["cumulative"]["energy_qualified_boundary_contacts"]
    if reference_replay:
        # Independently use the untouched older M7.5 physical observer for
        # all arms, and compare full state/energy/RNG and source fate.
        old=reference.follow(parent,chosen,replay=True)
        for arm in ARMS:
            assert old[arm]["final"]["full_hash"]==rows[arm]["final"]["full_hash"]
            assert old[arm]["final"]["rng"]==rows[arm]["final"]["rng"]
            assert old[arm]["final"]["draws"]==rows[arm]["final"]["draws"]
            assert old[arm]["final"]["energy"]==rows[arm]["final"]["stored_energy"]
            assert old[arm]["coherent_growth_at_120"]==rows[arm]["coherent_growth_at_120"]
            assert old[arm]["all_original_bonds_never_broken_120"]==rows[arm]["all_original_edges_unbroken_120"]
            assert old[arm]["root_incident_new_bond_events"]==rows[arm]["incident_external_formation_count"]
            assert old[arm]["root_incident_bond_events_before_any_original_break"]==rows[arm]["incident_external_formations_before_original_break"]
            assert old[arm]["first_original_bond_break_relative_tick"]==rows[arm]["first_original_break_tick"]
    return rows


def study(seed,old_p,replay=False):
    # Only the original M7.5 source selector can determine eligibility.
    parent,chosen,selection=reference.select_parent(seed,old_p)
    if chosen is None:
        return {"seed":seed,"selected":False,"ticks_scanned":parent.step,
                "reason":"no_native_cohort_per_original_m75_selection"}
    return {
        "seed":seed,"selected":True,
        "fork_tick":parent.step,
        "source":chosen,
        "parent_hash":parent.state_hash_full(),
        "parent_rng":parent.rng.fingerprint(),
        "parent_rng_draws":parent.rng.draws,
        "source_selection":selection,
        "frozen_t0_energy_only_mechanism":frozen_immediate(parent,chosen["ids"]),
        "outcomes":follow_with_mechanisms(parent,chosen,reference_replay=replay)
    }


def pair_disc(rows,metric,getter):
    counts={"bond_only_only":0,"no_transfer_only":0,"both":0,"neither":0}
    for r in rows:
        a=bool(getter(r["outcomes"]["bond_only"]))
        b=bool(getter(r["outcomes"]["no_transfer"]))
        if a and not b:counts["bond_only_only"]+=1
        elif b and not a:counts["no_transfer_only"]+=1
        elif a and b:counts["both"]+=1
        else:counts["neither"]+=1
    total=counts["bond_only_only"]+counts["no_transfer_only"]
    counts["discordant"]=total
    counts["favorable_fraction"]=round(counts["bond_only_only"]/total,6) if total else None
    return counts


def summarize(records,p):
    assert len(records)==320
    assert [x["seed"] for x in records]==list(range(25001,25321))
    chosen=[x for x in records if x["selected"]]
    n=len(chosen)
    def avg(values):
        return round(sum(values)/len(values),5) if values else None
    byarm={}
    for arm in ARMS:
        rows=[r["outcomes"][arm] for r in chosen]
        byarm[arm]={
            "selected_worlds":n,
            "mean_cumulative_energetic_eligible_interface":avg([
                h["cumulative"]["energy_qualified_boundary_contacts"] for h in rows]),
            "mean_cumulative_valence_qualified_interface":avg([
                h["cumulative"]["species_valence_qualified_boundary_contacts"] for h in rows]),
            "mean_cumulative_geometry_contacts":avg([
                h["cumulative"]["unbonded_geometrical_boundary_contacts"] for h in rows]),
            "mean_cumulative_energy_blocked":avg([
                h["cumulative"]["energy_blocked_qualified_contacts"] for h in rows]),
            "mean_source_energy_eligible_members":avg([
                h["cumulative"]["root_members_energy_and_valence_ready"]/120 for h in rows]),
            "mean_actual_external_incident_formations":avg([h["incident_external_formation_count"] for h in rows]),
            "worlds_with_actual_prebreak_incident_formation":sum(h["source_incident_prebreak_binary"] for h in rows),
            "mean_actual_prebreak_incident_formations":avg([h["incident_external_formations_before_original_break"] for h in rows]),
            "coherent_growth_at_120":sum(h["coherent_growth_at_120"] for h in rows),
            "never_broken_original_edges":sum(h["all_original_edges_unbroken_120"] for h in rows),
            "mean_total_global_new_bonds":avg([h["final"]["global_new_bonds"] for h in rows]),
            "mean_root_boundary_net_passive_transfers":avg([
                h["source_incoming_passes"]-h["source_outgoing_passes"] for h in rows])
        }
    delta_interface=[
        r["outcomes"]["bond_only"]["cumulative"]["energy_qualified_boundary_contacts"]
        -r["outcomes"]["no_transfer"]["cumulative"]["energy_qualified_boundary_contacts"]
        for r in chosen
    ]
    signs={"favor_bond_only":sum(x>0 for x in delta_interface),
           "favor_no_transfer":sum(x<0 for x in delta_interface),
           "tied":sum(x==0 for x in delta_interface)}
    signs["non_tied"]=signs["favor_bond_only"]+signs["favor_no_transfer"]
    signs["favorable_fraction"]=round(signs["favor_bond_only"]/signs["non_tied"],6) if signs["non_tied"] else None
    forms=pair_disc(chosen,"prebreak_incident",lambda h:h["source_incident_prebreak_binary"])
    growth=pair_disc(chosen,"growth",lambda h:h["coherent_growth_at_120"])
    survival=pair_disc(chosen,"survival",lambda h:h["all_original_edges_unbroken_120"])
    source_counts=Counter("tree" if r["source"]["cyclomatic_number"]==0 else "cycle" for r in chosen)
    stable=[r["frozen_t0_energy_only_mechanism"] for r in chosen]
    def gate(sign,minimum):
        if n<40 or sign["non_tied"]<minimum:
            return "not_met_or_underpowered"
        return "passed" if 3*sign["favor_bond_only"]>=2*sign["non_tied"] else "not_met_or_underpowered"
    def paired_gate(c,min_discord):
        if n<40 or c["discordant"]<min_discord:
            return "not_met_or_underpowered"
        return "passed" if 3*c["bond_only_only"]>=2*c["discordant"] else "not_met_or_underpowered"
    decision={
        "primary_energetic_interface":gate(signs,40),
        "secondary_prebreak_recruitment":paired_gate(forms,25),
        "descriptive_original_m75_growth_gate_on_NEW_heldout_seeds":paired_gate(growth,25),
        "preregistered_thresholds_preserved":True
    }
    return {
        "source_worlds":320,
        "eligible_source_worlds":n,
        "ineligible_source_worlds":320-n,
        "source_topology":dict(source_counts),
        "mean_initial_source_size":avg([r["source"]["size"] for r in chosen]),
        "per_arm":byarm,
        "frozen_immediate_t0":{
            "worlds_with_new_boundary_energy_qualified_pairs_after_bond_only_pass":sum(
                x["newly_qualified_net"]>0 for x in stable),
            "worlds_with_lost_boundary_energy_qualified_pairs_after_bond_only_pass":sum(
                x["newly_qualified_net"]<0 for x in stable),
            "worlds_with_same_boundary_energy_qualified_pairs":sum(
                x["newly_qualified_net"]==0 for x in stable),
            "mean_onepass_root_energy_change":avg([
                x["source_particle_energy_after_one_bond_pass"]-x["source_particle_energy_before"] for x in stable]),
            "mean_onepass_root_internal_transfer_events":avg([x["one_pass_transfer_events"] for x in stable])
        },
        "paired_comparisons":{
            "energetically_eligible_poststep_boundary_interface_sum":signs,
            "actual_incident_form_before_original_break":forms,
            "coherent_growth_at_120":growth,
            "all_original_edges_unbroken_120":survival,
            "mean_energy_interface_sum_difference":avg(delta_interface)
        },
        "preregistered_decisions":decision,
        "interpretation_limit":"Static post-transport qualified contacts are not probabilities of actual native same-step formation: the chemistry's formation sweep happens before the optional transfer, and source material and RNG diverge across arms. A directional association is NOT proof of mediation or information transfer."
    }


def run_shard(start,end):
    p=protocol()
    d={"start":start,"end":end}
    assert d in p["design"]["shards"]
    old=reference.protocol()
    rows=[]
    sham_seed=None
    for seed in range(start,end+1):
        row=study(seed,old,replay=(sham_seed is None))
        rows.append(row)
        if row["selected"] and sham_seed is None:sham_seed=seed
        if (seed-start+1)%10==0:
            print(f"M77_PROGRESS {start}-{end} seed={seed} selected={sum(r['selected'] for r in rows)}",flush=True)
    assert len(rows)==end-start+1
    out={
        "schema":"alife-m7-7-mechanism-seed-shard-v1",
        "descriptor":d,
        "provenance":provenance(),
        "worlds":rows,
        "reference_M75_replayed_first_selected_seed":sham_seed,
        "no_historical_law_changes":True
    }
    path=BASE/"shards"/f"{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M77_SHARD="+json.dumps({"start":start,"end":end,"source_worlds":len(rows),
                                 "selected":sum(r["selected"] for r in rows),"cross_replay":sham_seed},sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("*.json"))
    assert len(files)==8
    expectedprov=provenance()
    seen=[]
    rows=[]
    replays=[]
    for path in files:
        shard=json.loads(path.read_text(encoding="utf-8"))
        assert shard["schema"]=="alife-m7-7-mechanism-seed-shard-v1"
        assert shard["provenance"]==expectedprov
        assert shard["no_historical_law_changes"] is True
        d=shard["descriptor"]
        assert d in p["design"]["shards"] and d not in seen
        seen.append(d)
        cases=shard["worlds"]
        assert [r["seed"] for r in cases]==list(range(d["start"],d["end"]+1))
        first=next((r["seed"] for r in cases if r["selected"]),None)
        assert first==shard["reference_M75_replayed_first_selected_seed"]
        if first is not None:replays.append(first)
        rows.extend(cases)
    assert all(d in seen for d in p["design"]["shards"])
    rows.sort(key=lambda r:r["seed"])
    summary=summarize(rows,p)
    out={
        "schema":"alife-m7-7-full-320-source-mechanistic-audit-v1",
        "provenance":expectedprov,
        "source_worlds":rows,
        "reference_m75_crossreplay_seeds":replays,
        "summary":summary,
        "all_320_seeds_and_eight_shards_complete":True,
        "no_changes_to_original_M75_M76_or_core_src":True
    }
    RESULTS.parent.mkdir(parents=True,exist_ok=True)
    RESULTS.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("M77_FINAL_SUMMARY="+json.dumps(summary,sort_keys=True),flush=True)
    print("M77_SUCCESS="+str(len(rows)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="cmd",required=True)
    s=sub.add_parser("shard")
    s.add_argument("--start",type=int,required=True)
    s.add_argument("--end",type=int,required=True)
    sub.add_parser("merge")
    a=parser.parse_args()
    if a.cmd=="shard":run_shard(a.start,a.end)
    else:merge()


if __name__=="__main__":
    main()
