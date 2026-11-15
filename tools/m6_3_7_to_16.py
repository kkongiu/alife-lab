"""M6.3-7..16 — preregistered held-out physical and informational audit.

Frozen protocol committed as 417f27a before this runner.
ALife physical laws, RNG, configurations and historical evidence untouched.
One new 120-world campaign supports ten analysis steps (NOT ten samples).
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.structures import components, signature
from tools.m6_3_0_screen import make_world, toroidal_distance
from tools.m6_3_1_screen import (
    density_protocol, paired_initial_state, protocol as old_protocol,
    take_measurements, variants,
)
from tools.m6_3_2_audit import connected_status, eligible_partner_pairs, SOURCE, EDGES, ANCHORS

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m6_3_7_to_16/protocol.json"
OUTPUT=ROOT/"campaigns/m6_3_7_to_16/results.json"


def frozen_protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-3-7-to-16-heldout-v1"
    assert p["status"]=="frozen-before-runner-and-data-inspection"
    assert p["sample"]["seed_list"]==list(range(8201,8213))
    assert p["sample"]["densities"]==["baseline","enriched"]
    assert p["sample"]["arms"]==["A","B","A_reverse","B_reverse","C"]
    assert p["sample"]["expected_worlds"]==120
    assert p["sample"]["steps"]==450
    assert len(p["steps_plan"])==10
    return p


def class_of_phase(status):
    if status["pure"]:
        return "pure"
    if status["core_edges_retained"]:
        return "grown_with_original_edges"
    return "original_edges_missing"


class CoreEventSink:
    def __init__(self):
        self.pending=[]
    def emit(self,event):
        if event.id_a in SOURCE or event.id_b in SOURCE:
            self.pending.append((event.step+1,event.kind,tuple(sorted((event.id_a,event.id_b)))))
    def get(self,tick):
        events=[(kind,ids) for post,kind,ids in self.pending if post==tick]
        self.pending=[v for v in self.pending if v[0]!=tick]
        return events


def analyse_world(world,source_arm,target_signatures,steps=450):
    """No intervention. Track true event history versus post-step snapshots."""
    world.check()
    assert world.step==0
    prev=connected_status(world)
    assert prev["pure"]
    src_sig=target_signatures[source_arm.removesuffix("_reverse")]
    initial_rng=world.rng.fingerprint()
    initial_hash=world.state_hash_full()
    prev_deg=list(world.store.degree)
    prior_broken=set()
    first_break=None
    first_attachment=None
    first_loss=None
    last_pure=True
    first_loss_mode=None
    first_growth=None
    first_edge_absence=None
    observed=set()
    ever_shared=set()
    ticks=Counter()
    bond_events=Counter()
    added_species=Counter()
    exposures=Counter()
    new_motifs=Counter()
    sample_events=[]
    first_break_edge=None
    core_break_ticks=Counter()
    sink=CoreEventSink()
    world.event_sink=sink
    original_break_count_by_edge=Counter()
    original_reform_count_by_edge=Counter()
    per_step_first5=[]

    def observer(w):
        nonlocal prev_deg,first_break,first_attachment,first_growth
        nonlocal first_loss,first_loss_mode,first_edge_absence,first_break_edge,prev
        before=w.rng.draws
        s=w.store
        co=components(s)
        state=connected_status(w,co)
        phase=class_of_phase(state)
        ticks[f"{phase}_ticks"]+=1
        if state["core_edges_retained"]:
            ticks["original_edges_present_ticks"]+=1
        if state["core_connected"]:
            ticks["all_source_ids_connected_ticks"]+=1
        if state["core_edges_retained"] and prior_broken:
            ticks["original_edges_restored_after_break_ticks"]+=1
        if state["core_grown"]:
            ticks["grown_but_edges_present_ticks"]+=1
        if not state["pure"] and first_loss is None:
            first_loss=w.step
            first_loss_mode=(
                "mixed" if not state["core_edges_retained"] and state["direct_external_edges"]
                else "original_edge_loss" if not state["core_edges_retained"]
                else "attachment" if state["direct_external_edges"]
                else "unresolved"
            )
        if not state["core_edges_retained"] and first_edge_absence is None:
            first_edge_absence=w.step
        if state["attached_count"] and first_growth is None:
            first_growth=w.step

        events=sink.get(w.step)
        for kind,pair in events:
            if pair in EDGES:
                bond_events[f"original_{kind}"]+=1
                if kind=="break":
                    original_break_count_by_edge[str(pair)]+=1
                    if first_break is None:
                        first_break=w.step
                        first_break_edge=list(pair)
                    prior_broken.add(pair)
                    core_break_ticks[str(pair)]=w.step
                elif kind=="form" and pair in prior_broken:
                    original_reform_count_by_edge[str(pair)]+=1
            elif (pair[0] in SOURCE) != (pair[1] in SOURCE):
                if kind=="form":
                    outsider=pair[1] if pair[0] in SOURCE else pair[0]
                    i=s.index_of(outsider)
                    species=w.species_names[s.species[i]]
                    prev_group="free" if prev_deg[i]==0 else "bonded"
                    added_species[f"outward_{species}"]+=1
                    bond_events[f"attach_{prev_group}"]+=1
                    if first_attachment is None:
                        first_attachment={
                            "tick":w.step,"prior_degree":prev_deg[i],
                            "outward_species":species,"source_id":(
                                pair[0] if pair[0] in SOURCE else pair[1]
                            )
                        }
                else:
                    bond_events["external_break"]+=1
            else:
                bond_events[f"other_{kind}"]+=1

        eligible=eligible_partner_pairs(w)
        for key,value in eligible.items():
            exposures[f"{phase}_{key}"]+=value
        if eligible["energy_qualified_open_slots"]==0:
            ticks[f"{phase}_no_energy_open_slots_ticks"]+=1
        if eligible["open_slots"]==0:
            ticks[f"{phase}_zero_valence_slots_ticks"]+=1

        for indices,bonds in co:
            ids={s.ids[i] for i in indices}
            if ids & SOURCE:
                ever_shared.update(ids-SOURCE)
        for indices,bonds in co:
            if len(indices)!=4 or len(bonds)!=3:
                continue
            ids={s.ids[i] for i in indices}
            if ids & SOURCE:
                continue
            sig=signature(s,indices,bonds,w.species_names)
            if not sig.exact or sig.key not in target_signatures.values():
                continue
            variant=next(name for name,key in target_signatures.items() if key==sig.key)
            key=(sig.key,tuple(sorted(ids)))
            if key in observed:
                continue
            observed.add(key)
            near=any(toroidal_distance((s.xs[i],s.ys[i]),pos,s.width,s.height)<=2
                     for i in indices for pos in ANCHORS)
            shared=bool(ids & ever_shared)
            new_motifs[f"all_{variant}"]+=1
            if not shared:
                new_motifs[f"strict_{phase}_{'near' if near else 'far'}_{variant}"]+=1
                if near and len(sample_events)<12:
                    sample_events.append({
                        "step":w.step,"source_arm":source_arm,"variant":variant,
                        "ids":sorted(ids),"source_phase":phase
                    })
        if w.step<=5:
            per_step_first5.append({
                "tick":w.step,"phase":phase,"events":[
                    {"kind":kind,"ids":list(pair)} for kind,pair in events
                ]
            })
        prev_deg=list(s.degree)
        prev=state
        assert w.rng.draws==before,"non-read-only observer consumed RNG"

    for _ in range(steps):
        world.advance(1,observer=observer)
    world.event_sink=None
    world.check()
    assert sum(ticks[f"{ph}_ticks"] for ph in
               ("pure","grown_with_original_edges","original_edges_missing"))==steps
    assert first_break is None or first_break<=steps
    assert first_loss_mode != "unresolved"
    assert not sink.pending
    return {
        "seed":world.config.seed,"arm":source_arm,
        "first_actual_original_edge_break_tick":first_break,
        "first_broken_edge":first_break_edge,
        "right_censored_original_break":first_break is None,
        "first_original_edge_absent_snapshot":first_edge_absence,
        "first_attachment":first_attachment,
        "first_growth_tick":first_growth,
        "first_purity_loss_tick":first_loss,
        "first_purity_loss_mode":first_loss_mode or "censored",
        "original_edge_break_counts":dict(sorted(original_break_count_by_edge.items())),
        "original_edge_reform_counts":dict(sorted(original_reform_count_by_edge.items())),
        "last_original_edge_break_event_ticks":dict(sorted(core_break_ticks.items())),
        "ticks":dict(sorted(ticks.items())),
        "source_incident_events":dict(sorted(bond_events.items())),
        "new_attachment_species":dict(sorted(added_species.items())),
        "exposures":dict(sorted(exposures.items())),
        "new_motifs":dict(sorted(new_motifs.items())),
        "new_motif_examples":sample_events,
        "first_five_ticks":per_step_first5,
        "initial_hash":initial_hash,"final_hash":world.state_hash_full(),
        "initial_rng_fingerprint":initial_rng,
        "final_rng_fingerprint":world.rng.fingerprint(),
        "final_rng_draws":world.rng.draws,
        "formations":world.bonds_formed_total,
        "breaks":world.bonds_broken_total,
        "final_energy":world.energy(),
        "final_dissipated":world.dissipated,
        "steps":world.step,
    }


def aggregate(records,p):
    by={(r["density"],r["seed"],r["arm"]):r for r in records}
    densities=p["sample"]["densities"]
    arms=p["sample"]["arms"]
    result={}
    prefers={}
    for den in densities:
        all_rows=[r for r in records if r["density"]==den]
        arm_results={}
        for arm in arms:
            rows=[by[den,seed,arm] for seed in p["sample"]["seed_list"]]
            ticks=Counter()
            species=Counter()
            motifs=Counter()
            exposures=Counter()
            events=Counter()
            for r in rows:
                ticks.update(r["ticks"])
                species.update(r["new_attachment_species"])
                motifs.update(r["new_motifs"])
                exposures.update(r["exposures"])
                events.update(r["source_incident_events"])
            n=len(rows)
            phase_count=lambda phase:sum(
                motifs.get(f"strict_{phase}_near_{x}",0) for x in ("A","B")
            )
            near_counts={
                phase:{v:motifs.get(f"strict_{phase}_near_{v}",0)
                       for v in ("A","B","C")}
                for phase in ("pure","grown_with_original_edges","original_edges_missing")
            }
            risk=[r["first_actual_original_edge_break_tick"] for r in rows
                  if r["first_actual_original_edge_break_tick"] is not None]
            active=ticks["grown_with_original_edges_ticks"]
            arm_results[arm]={
                "cases":n,
                "first_loss_distribution":dict(Counter(r["first_purity_loss_mode"] for r in rows)),
                "first_break_observed":len(risk),
                "first_break_censored":n-len(risk),
                "mean_first_break_event_tick_if_observed":round(sum(risk)/len(risk),3) if risk else None,
                "mean_pure_ticks":round(ticks["pure_ticks"]/n,3),
                "mean_bonded_grown_ticks":round(active/n,3),
                "mean_initial_edges_present_ticks":round(
                    (ticks["pure_ticks"]+active)/n,3),
                "mean_core_connected_ticks":round(ticks["all_source_ids_connected_ticks"]/n,3),
                "total_original_breaks":events["original_break"],
                "total_original_form_events":events["original_form"],
                "time_restored_after_break":ticks["original_edges_restored_after_break_ticks"],
                "external_attachment_free":events["attach_free"],
                "external_attachment_prebonded":events["attach_bonded"],
                "attachment_species":dict(species),
                "no_energy_valence_slots_fraction_post_growth":round(
                    ticks["grown_with_original_edges_no_energy_open_slots_ticks"]/active,4
                ) if active else None,
                "no_valence_slots_fraction_post_growth":round(
                    ticks["grown_with_original_edges_zero_valence_slots_ticks"]/active,4
                ) if active else None,
                "eligible_free_by_phase":{
                    phase:{v:exposures.get(f"{phase}_eligible_{v}",0)
                           for v in ("S0","S1")}
                    for phase in ("pure","grown_with_original_edges","original_edges_missing")
                },
                "free_neighbors_by_phase":{
                    phase:{v:exposures.get(f"{phase}_free_adjacent_{v}",0)
                           for v in ("S0","S1")}
                    for phase in ("pure","grown_with_original_edges","original_edges_missing")
                },
                "strict_near_new_motifs":near_counts,
                "new_motifs_anywhere":{v:motifs.get(f"all_{v}",0) for v in ("A","B","C")},
            }
            if arm!="C":
                desired="A" if arm.startswith("A") else "B"
                other="B" if desired=="A" else "A"
                def count(r,variant):
                    return sum(r["new_motifs"].get(f"strict_{phase}_near_{variant}",0)
                               for phase in ("pure","grown_with_original_edges"))
                prefers[f"{den}/{arm}"]=sum(
                    count(r,desired)>count(r,other) for r in rows
                )
        result[den]=arm_results
    sufficient=True
    for den in densities:
        for arm in ("A","B","A_reverse","B_reverse"):
            d=result[den][arm]["strict_near_new_motifs"]
            total=sum(d[ph][v] for ph in ("pure","grown_with_original_edges")
                      for v in ("A","B"))
            sufficient &= total>=8
    preference=all(n>=9 for n in prefers.values())
    return {
        "by_density_and_arm":result,
        "source_matched_variant_preference_seed_counts":prefers,
        "gate":{
            "minimum_events_each_arm_and_density":bool(sufficient),
            "minimum_preference_nine_of_twelve":preference,
            "specificity_screen_signal":bool(sufficient and preference),
            "verdict":"screen_signal_requires_causal_validation" if sufficient and preference
                      else "underpowered_or_no_specificity"
        },
    }


def run():
    p=frozen_protocol()
    old=old_protocol()
    sig=variants(old)
    all_records=[]
    for density in p["sample"]["densities"]:
        for seed in p["sample"]["seed_list"]:
            d=density_protocol(old,density)
            for spec in d["model"]["fixture_species_counts"]:
                assert d["model"]["fixture_species_counts"][spec]==p["sample"]["density_counts"][density][spec]
            ref=None
            for arm in p["sample"]["arms"]:
                w=make_world(seed,arm,d)
                init=paired_initial_state(w)
                if ref is None:
                    ref=init
                else:
                    assert init==ref,"initial conditions not identical across motif arms"
                item=analyse_world(w,arm,sig,steps=p["sample"]["steps"])
                item["density"]=density
                all_records.append(item)
            print(f"seed {seed} density {density}: five arms completed",flush=True)

    assert len(all_records)==p["sample"]["expected_worlds"]
    replay_info=[]
    for density,seed,arm in p["integrity"]["preselected_replays"]:
        old_r=next(r for r in all_records if
                   (r["density"],r["seed"],r["arm"])==(density,seed,arm))
        fresh=make_world(seed,arm,density_protocol(old,density))
        previous=take_measurements(fresh,old,arm,sig)
        for a,b in [
            ("final_hash","final_hash"),
            ("final_rng_fingerprint","final_rng_fingerprint"),
            ("final_rng_draws","final_rng_draws"),
            ("final_energy","final_energy"),
            ("final_dissipated","final_dissipated"),
            ("formations","bond_formations"),
            ("breaks","bond_breaks"),
        ]:
            assert old_r[a]==previous[b],f"cross-observer replay mismatch {density}/{seed}/{arm}: {a}"
        assert old_r["ticks"].get("pure_ticks",0)==previous["active_template_ticks"]
        replay_info.append({
            "density":density,"seed":seed,"arm":arm,
            "matching_world_hash":old_r["final_hash"],
            "matching_rng_draws":old_r["final_rng_draws"]
        })
    result={
        "schema":p["schema"],
        "protocol_commit":"417f27a0481f5a8fb5ee6463098716c3bbeafcc9",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "n_worlds":len(all_records),
        "validation":{"preselected_cross_observer_replays":replay_info,
                      "laws_unchanged":True,"all_120_checks_passed":True},
        "summary":aggregate(all_records,p),
        "all_runs":all_records,
        "epistemic_status":"prospective new-seed synthetic-probe screen; noncausal",
        "scientific_verdict":"replication_and_heredity_not_demonstrated"
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("TEN_STEP_SUMMARY="+json.dumps({
        "n_worlds":result["n_worlds"],"summary":result["summary"],
        "validation":result["validation"],
        "scientific_verdict":result["scientific_verdict"],
    },sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    run()
