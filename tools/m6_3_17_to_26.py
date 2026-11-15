"""M6.3-17..26: frozen reactive-terminal mechanism audit (NO law changes).

Protocol commit d76e2e6 PRECEDES this executable. One 144-world
campaign supports ten analyses; terminal S1-S2 chemistry does NOT
constitute replication or heredity. All physical rules unchanged.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from alife.chemistry import VON_NEUMANN, _candidate_pairs
from alife.particles import EMPTY
from alife.structures import components, signature
from tools.m6_3_0_screen import make_world, signature_of_scaffold, toroidal_distance
from tools.m6_3_1_screen import (
    density_protocol, paired_initial_state, protocol as earlier_protocol,
    take_measurements,
)
from tools.m6_3_2_audit import connected_status, SOURCE, EDGES, ANCHORS

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "campaigns/m6_3_17_to_26/protocol.json"
RESULT = ROOT / "campaigns/m6_3_17_to_26/results.json"
VARIANTS = ("A","B","C","D")


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-3-17-to-26-reactive-termini-v1"
    assert p["status"]=="frozen-before-runner-and-outcome-inspection"
    assert p["world"]["seed_list"]==list(range(8401,8413))
    assert p["world"]["arm_order"]==[
        "A","B","A_reverse","B_reverse","C","D"
    ]
    assert p["world"]["expected_worlds"]==144
    assert len(p["ten_gates"])==10
    return p


def fixture_protocol(p,density):
    old=earlier_protocol()
    d=density_protocol(old,density)
    d["model"]["variant_sites"]=p["world"]["sequences"]
    d["model"]["arm_order"]=p["world"]["arm_order"]
    d["model"]["bonded_arms"]=p["world"]["arm_order"]
    d["model"]["seed_list"]=p["world"]["seed_list"]
    assert d["model"]["fixture_species_counts"]==p["world"]["densities"][density]
    return d


def all_signatures(p):
    f=fixture_protocol(p,"baseline")
    keys={arm:signature_of_scaffold(make_world(8401,arm,f))
          for arm in VARIANTS}
    assert all(keys.values()) and len(set(keys.values()))==4
    assert signature_of_scaffold(make_world(8401,"A_reverse",f))==keys["A"]
    assert signature_of_scaffold(make_world(8401,"B_reverse",f))==keys["B"]
    return keys


def terminal_s2_opportunities(world):
    """Pre-reaction/static list of legal terminal-S2 bond candidates.
    Reads EXACT generator from unchanged chemistry, does not draw RNG."""
    s=world.store
    eligible=0
    for ia,ib in _candidate_pairs(world):
        a,b=s.ids[ia],s.ids[ib]
        if (a in (0,3)) == (b in (0,3)):
            continue
        outsider=ib if a in (0,3) else ia
        if world.species_names[s.species[outsider]]=="S2":
            eligible+=1
    near_s2=0
    for terminal_id in (0,3):
        i=s.index_of(terminal_id)
        x,y=s.xs[i],s.ys[i]
        for dx,dy in VON_NEUMANN:
            xx,yy=x+dx,y+dy
            if world.periodic: xx,yy=xx%s.width,yy%s.height
            elif not (0<=xx<s.width and 0<=yy<s.height): continue
            j=s.grid[yy*s.width+xx]
            if j!=EMPTY and s.ids[j] not in SOURCE and world.species_names[s.species[j]]=="S2":
                near_s2+=1
    return {"adjacent_terminal_S2":near_s2,"eligible_terminal_S2":eligible}


class IncidentSink:
    """BondEvents are recorded in engine order, mapped to post-transition tick."""
    def __init__(self):
        self.pending=[]
    def emit(self,event):
        if event.id_a in SOURCE or event.id_b in SOURCE:
            self.pending.append((event.step+1,event.kind,
                                 tuple(sorted((event.id_a,event.id_b)))))
    def pop(self,tick):
        result=[(kind,pair) for t,kind,pair in self.pending if t==tick]
        self.pending=[x for x in self.pending if x[0]!=tick]
        return result


def run_world(world,arm,target_signatures,duration=450):
    world.check()
    assert world.step==0
    source_key=target_signatures[arm.replace("_reverse","")]
    assert signature_of_scaffold(world)==source_key
    initially=terminal_s2_opportunities(world)
    invariant_initial=paired_initial_state(world)
    starting_hash=world.state_hash_full()
    first_break=None
    first_loss=None
    first_growth=None
    unbroken=True
    seen=set()
    ever_shared=set()
    phase_ticks=Counter()
    exposed=Counter()
    event_counts=Counter()
    attachment_species=Counter()
    motif_counts=Counter()
    broken_edges=set()
    restored_edges=Counter()
    source_s2_events=[]
    first_five=[]
    sink=IncidentSink()
    world.event_sink=sink

    def observe(w):
        nonlocal first_break,first_loss,first_growth,unbroken
        before=w.rng.draws
        s=w.store
        ev=sink.pop(w.step)
        if any(kind=="break" and ids in EDGES for kind,ids in ev):
            unbroken=False
            if first_break is None:
                first_break=w.step
        for kind,ids in ev:
            if ids in EDGES:
                event_counts[f"original_{kind}"]+=1
                if kind=="break":
                    broken_edges.add(ids)
                elif ids in broken_edges:
                    restored_edges[str(ids)]+=1
            elif (ids[0] in SOURCE) != (ids[1] in SOURCE):
                if kind=="form":
                    outside=ids[1] if ids[0] in SOURCE else ids[0]
                    outside_species=w.species_names[s.species[s.index_of(outside)]]
                    attachment_species[outside_species]+=1
                    event_counts[f"attachment_{outside_species}"]+=1
                    terminal=ids[0] if ids[0] in SOURCE else ids[1]
                    if outside_species=="S2" and terminal in (0,3):
                        source_s2_events.append({
                            "tick":w.step,"terminal_id":terminal,
                            "unbroken_core_window":unbroken
                        })
                        if unbroken:
                            event_counts["accepted_terminal_S2_unbroken"]+=1
                else:
                    event_counts["external_break"]+=1
        co=components(s)
        state=connected_status(w,co)
        phase=("pure" if state["pure"] else
               "grown_with_original_edges" if state["core_edges_retained"]
               else "original_edges_missing")
        phase_ticks[f"{phase}_ticks"]+=1
        if unbroken:
            phase_ticks["continuous_unbroken_core_ticks"]+=1
            opportunity=terminal_s2_opportunities(w)
            for k,v in opportunity.items():
                exposed[f"unbroken_{k}"]+=v
        if state["core_edges_retained"]:
            phase_ticks["core_edges_present_ticks"]+=1
        if state["core_edges_retained"] and not unbroken:
            phase_ticks["restored_core_edges_present_ticks"]+=1
        if first_loss is None and not state["pure"]:
            first_loss=w.step
        if first_growth is None and state["attached_count"]>0:
            first_growth=w.step

        for indices,bonds in co:
            members={s.ids[i] for i in indices}
            if members & SOURCE:
                ever_shared.update(members-SOURCE)
        for indices,bonds in co:
            if len(indices)!=4 or len(bonds)!=3:
                continue
            members={s.ids[i] for i in indices}
            if members & SOURCE:
                continue
            sig=signature(s,indices,bonds,w.species_names)
            if not sig.exact or sig.key not in target_signatures.values():
                continue
            key=(sig.key,tuple(sorted(members)))
            if key in seen:
                continue
            seen.add(key)
            variant=next(k for k,v in target_signatures.items() if v==sig.key)
            near=any(toroidal_distance((s.xs[i],s.ys[i]),pos,s.width,s.height)<=2
                     for i in indices for pos in ANCHORS)
            common_history=bool(members & ever_shared)
            motif_counts[f"all_{variant}"]+=1
            if not common_history:
                motif_counts[f"strict_{phase}_{'near' if near else 'far'}_{variant}"]+=1
        if w.step<=5:
            first_five.append({
                "tick":w.step,"unbroken":unbroken,
                "events":[{"kind":k,"ids":list(ids)} for k,ids in ev]
            })
        assert before==w.rng.draws,"observer consumed RNG"

    for _ in range(duration):
        world.advance(1,observer=observe)
    world.event_sink=None
    world.check()
    assert not sink.pending
    assert sum(phase_ticks[f"{ph}_ticks"] for ph in
        ("pure","grown_with_original_edges","original_edges_missing"))==duration
    return {
        "seed":world.config.seed,"arm":arm,
        "source_terminal_species":[
            world.species_names[world.store.species[world.store.index_of(i)]]
            for i in (0,3)],
        "initial_s2_opportunities":initially,
        "initial_paired_background_hash":starting_hash,
        "first_original_bond_break_tick":first_break,
        "first_break_right_censored":first_break is None,
        "first_purity_loss_tick":first_loss,
        "first_growth_tick":first_growth,
        "source_events":dict(sorted(event_counts.items())),
        "attachment_species":dict(sorted(attachment_species.items())),
        "source_S2_terminal_formations":source_s2_events,
        "original_edge_reformations":dict(sorted(restored_edges.items())),
        "phase_ticks":dict(sorted(phase_ticks.items())),
        "terminal_s2_exposure":dict(sorted(exposed.items())),
        "new_independent_motifs":dict(sorted(motif_counts.items())),
        "initial_rng_fingerprint":invariant_initial[2],
        "final_hash":world.state_hash_full(),
        "final_rng_fingerprint":world.rng.fingerprint(),
        "final_rng_draws":world.rng.draws,
        "final_energy":world.energy(),
        "final_dissipated":world.dissipated,
        "formed":world.bonds_formed_total,
        "broken":world.bonds_broken_total,
        "first_five":first_five,
        "ticks":world.step,
    }


def summarize(records,p):
    out={}
    for density in p["world"]["densities"]:
        table={}
        for arm in p["world"]["arm_order"]:
            selected=[r for r in records if r["density"]==density and r["arm"]==arm]
            assert len(selected)==len(p["world"]["seed_list"])
            def total(path):
                return sum(path(r) for r in selected)
            near={
                v:total(lambda r:sum(
                    r["new_independent_motifs"].get(f"strict_{ph}_near_{v}",0)
                    for ph in ("pure","grown_with_original_edges")))
                for v in VARIANTS}
            table[arm]={
                "runs":len(selected),
                "terminal_species":selected[0]["source_terminal_species"],
                "initial_eligible_S2_pairs":total(
                    lambda r:r["initial_s2_opportunities"]["eligible_terminal_S2"]),
                "initial_adjacent_S2":total(
                    lambda r:r["initial_s2_opportunities"]["adjacent_terminal_S2"]),
                "unbroken_eligible_terminal_S2_pair_snapshots":total(
                    lambda r:r["terminal_s2_exposure"].get(
                        "unbroken_eligible_terminal_S2",0)),
                "accepted_terminal_S2_while_unbroken":total(
                    lambda r:r["source_events"].get("accepted_terminal_S2_unbroken",0)),
                "runs_with_accepted_terminal_S2_unbroken":total(
                    lambda r:int(r["source_events"].get(
                        "accepted_terminal_S2_unbroken",0)>0)),
                "mean_pure_ticks":round(total(
                    lambda r:r["phase_ticks"].get("pure_ticks",0))/len(selected),3),
                "mean_core_edges_present_ticks":round(total(
                    lambda r:r["phase_ticks"].get("core_edges_present_ticks",0))/len(selected),3),
                "mean_continuously_unbroken_ticks":round(total(
                    lambda r:r["phase_ticks"].get("continuous_unbroken_core_ticks",0))/len(selected),3),
                "first_bond_break_observed":total(
                    lambda r:int(not r["first_break_right_censored"])),
                "total_accepted_S0_S1_S2_source_bonds":{
                    s:total(lambda r:r["attachment_species"].get(s,0))
                    for s in ("S0","S1","S2")},
                "new_strict_near_motifs_while_source_edges_present":near,
            }
        out[density]=table
    terminal_gate=all(
        out[den]["D"]["accepted_terminal_S2_while_unbroken"] >
        out[den]["C"]["accepted_terminal_S2_while_unbroken"]
        and out[den]["D"]["accepted_terminal_S2_while_unbroken"]>0
        for den in p["world"]["densities"]
    )
    return {
        "density_arm":out,
        "gate":{
            "terminal_mechanism_verified":terminal_gate,
            "interpretation":(
                "verified_local_terminal_chemistry_not_inheritance"
                if terminal_gate else "mechanism_unconfirmed_or_opportunity_limited"
            ),
            "hereditary_replication_demonstrated":False
        }
    }


def run():
    p=protocol()
    signatures=all_signatures(p)
    records=[]
    for density in p["world"]["densities"]:
        fixture=fixture_protocol(p,density)
        for seed in p["world"]["seed_list"]:
            initial=None
            pairsets={}
            for arm in p["world"]["arm_order"]:
                w=make_world(seed,arm,fixture)
                paired=paired_initial_state(w)
                if initial is None: initial=paired
                else: assert paired==initial,"initial background/energy/RNG mismatch"
                pairsets[arm]=tuple(_candidate_pairs(w))
                row=run_world(w,arm,signatures,duration=p["world"]["steps_per_world"])
                row["density"]=density
                records.append(row)
            assert pairsets["A"]==pairsets["B"]
            assert pairsets["A_reverse"]==pairsets["B_reverse"]
            print(f"{density}/{seed}: six arms verified",flush=True)
    assert len(records)==p["world"]["expected_worlds"]
    checks=[]
    for density,seed,arm in p["integrity"]["fixed_replay_selections"]:
        earlier=next(row for row in records
                     if (row["density"],row["seed"],row["arm"])==(density,seed,arm))
        fixture=fixture_protocol(p,density)
        old=earlier_protocol()
        # This independent observer has no requirements on the initial
        # *source variant*. It takes frozen duration and the 4 exact motifs.
        reference=take_measurements(make_world(seed,arm,fixture),
                                    old,arm,signatures)
        assert earlier["final_hash"]==reference["final_hash"]
        assert earlier["final_rng_fingerprint"]==reference["final_rng_fingerprint"]
        assert earlier["final_rng_draws"]==reference["final_rng_draws"]
        assert earlier["final_energy"]==reference["final_energy"]
        assert earlier["final_dissipated"]==reference["final_dissipated"]
        assert earlier["formed"]==reference["bond_formations"]
        assert earlier["broken"]==reference["bond_breaks"]
        assert earlier["phase_ticks"].get("pure_ticks",0)==reference["active_template_ticks"]
        checks.append({"density":density,"seed":seed,"arm":arm,
                       "verified_final_hash":earlier["final_hash"]})
    report={
        "protocol_commit":"d76e2e6a3d69b0ab94a607288fcf21ffd70ec0ca",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "schema":"alife-m6-3-17-to-26-results-v1",
        "n_worlds":len(records),
        "signatures":signatures,
        "summary":summarize(records,p),
        "verification":{
            "all_world_checks_passed":True,
            "paired_initials_passed":True,
            "A_B_initial_candidate_sets_equal":True,
            "reverse_A_B_initial_candidate_sets_equal":True,
            "cross_observer_replays":checks,
            "no_physics_changes":True
        },
        "per_world":records,
        "epistemic_status":"positive local chemistry possible; no causal template replication inferred",
        "biological_verdict":"no_evidence_of_heredity_or_digital_organism"
    }
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("TEN_STAGE_TERMINAL_SUMMARY="+json.dumps({
        "n_worlds":report["n_worlds"],"signatures":signatures,
        "summary":report["summary"],"verification":report["verification"],
        "biological_verdict":report["biological_verdict"],
    },sort_keys=True),flush=True)
    return report


if __name__=="__main__":
    run()
