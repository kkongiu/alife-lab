"""M6.3-2 — five-stage post-hoc mechanistic audit of M6.3-1.

Protocol commit 43613a0 precedes the implementation.
Replays the SAME 160 controlled trajectories, never changes ALife physics,
retains all zero cases and checks independent replay against M6.3-1 observer.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

from alife.chemistry import VON_NEUMANN
from alife.particles import EMPTY
from alife.structures import components, signature
from tools.m6_3_0_screen import make_world, toroidal_distance
from tools.m6_3_1_screen import (
    density_protocol, paired_initial_state, protocol as m631_protocol,
    take_measurements, variants,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "campaigns/m6_3_2/protocol.json"
OUT = ROOT / "campaigns/m6_3_2/audit_results.json"
SOURCE = frozenset((0,1,2,3))
EDGES = frozenset(((0,1),(1,2),(2,3)))
ANCHORS = ((10,12),(11,12),(12,12),(13,12))


def audit_protocol() -> dict:
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"] == "alife-m6-3-2-five-stage-audit-v1"
    assert p["status"] == "frozen-before-audit-code-or-execution"
    assert p["integrity"]["expected_cases"] == 160
    assert p["integrity"]["expected_steps"] == 450
    assert p["core_edges"] == [[0,1],[1,2],[2,3]]
    return p


def classify_loss(original_edge_missing: bool, external_attachment: bool) -> str:
    """Net physical state immediately after pure scaffold is lost."""
    if original_edge_missing and external_attachment:
        return "mixed"
    if original_edge_missing:
        return "original_edge_loss"
    if external_attachment:
        return "attachment"
    return "other"


def connected_status(world, graph_components=None) -> dict:
    """Core material state; tracker IDs never imply genealogical relationships."""
    store=world.store
    edges={tuple(sorted((store.ids[a],store.ids[b]))) for a,b in store.bonds}
    retained=all(edge in edges for edge in EDGES)
    grouped=graph_components if graph_components is not None else components(store)
    containing=[]
    owner={}
    for indices,bonds in grouped:
        ids={store.ids[i] for i in indices}
        if ids & SOURCE:
            containing.append(ids)
            for pid in ids & SOURCE:
                owner[pid]=ids
    connected = len(owner)==4 and all(owner[i] == owner[0] for i in SOURCE)
    attached=set()
    if connected:
        attached=owner[0]-SOURCE
    else:
        for group in containing:
            attached.update(group-SOURCE)
    external_bonds=[
        (a,b) for a,b in edges if (a in SOURCE) != (b in SOURCE)
    ]
    pure = connected and retained and not attached and len(owner[0])==4
    return {
        "pure":pure,
        "core_edges_retained":retained,
        "core_connected":connected,
        "core_grown":retained and bool(attached),
        "attached_count":len(attached),
        "direct_external_edges":external_bonds,
        "missing_edges":[list(edge) for edge in sorted(EDGES-edges)],
        "core_comp_size":len(owner[0]) if connected else None,
    }


def eligible_partner_pairs(world) -> dict:
    """Post-step opportunity proxy for chemical eligibility, not actual
    pre-formation candidate sampling. Does not draw RNG or mutate state."""
    s=world.store
    allowed=world.allowed_pairs
    permitted=Counter()
    nearby=Counter()
    open_slots=0
    energy_open_slots=0
    for pid in sorted(SOURCE):
        i=s.index_of(pid)
        slots=world.max_bonds[s.species[i]]-s.degree[i]
        open_slots+=slots
        if slots>0 and s.energy[i]>=world.formation_cost:
            energy_open_slots+=slots
        x,y=s.xs[i],s.ys[i]
        for dx,dy in VON_NEUMANN:
            nx,ny=x+dx,y+dy
            if world.periodic:
                nx,ny=nx%s.width,ny%s.height
            elif not (0<=nx<s.width and 0<=ny<s.height):
                continue
            j=s.grid[ny*s.width+nx]
            if j==EMPTY or s.ids[j] in SOURCE:
                continue
            species=wname=world.species_names[s.species[j]]
            if s.degree[j] != 0:
                continue
            nearby[wname]+=1
            pair=(s.species[i],s.species[j])
            if (slots>0 and s.energy[i]>=world.formation_cost
                and s.energy[j]>=world.formation_cost
                and world.max_bonds[s.species[j]]>s.degree[j]
                and (pair in allowed or pair[::-1] in allowed)):
                permitted[wname]+=1
    return {
        "free_adjacent_S0":nearby["S0"],
        "free_adjacent_S1":nearby["S1"],
        "eligible_S0":permitted["S0"],
        "eligible_S1":permitted["S1"],
        "open_slots":open_slots,
        "energy_qualified_open_slots":energy_open_slots,
    }


class IncidentRecorder:
    """A BondEvent at pre-step t is visible in post-step state t+1."""
    def __init__(self):
        self.events=[]
    def emit(self,event):
        if event.id_a in SOURCE or event.id_b in SOURCE:
            self.events.append({
                "tick":event.step+1,
                "kind":event.kind,
                "ids":sorted((event.id_a,event.id_b)),
            })
    def take(self,tick):
        selection=[e for e in self.events if e["tick"]==tick]
        self.events=[e for e in self.events if e["tick"]!=tick]
        return selection


def analyse_one(world,p,arm,target_signatures):
    """One frozen historical world; no intervention or altered parameters."""
    assert world.step==0
    world.check()
    initial_sig=signature_of(world)
    canonical=target_signatures[arm.replace("_reverse","")]
    assert initial_sig==canonical
    seen=set()
    ever_shared=set()
    phase_counts=Counter()
    class_counts=Counter()
    first_loss=None
    first_original_loss=None
    first_growth=None
    first_loss_details=None
    tick_totals=Counter()
    local_events=Counter()
    samples=[]
    prev_status=connected_status(world)
    assert prev_status["pure"] and prev_status["core_edges_retained"]
    pre_degrees={pid:world.store.degree[world.store.index_of(pid)] for pid in world.store.ids}
    all_events=[]
    sink=IncidentRecorder()
    world.event_sink=sink
    start_hash=world.state_hash_full()
    start_rng=world.rng.fingerprint()
    start_draws=world.rng.draws
    first_loss_active=True
    def observe(w):
        nonlocal first_loss,first_original_loss,first_growth
        nonlocal first_loss_details,prev_status,pre_degrees,first_loss_active
        before_rng=w.rng.draws
        grouped=components(w.store)
        st=connected_status(w,grouped)
        events=sink.take(w.step)
        event_types=Counter()
        for event in events:
            pair=set(event["ids"])
            internal=pair <= SOURCE
            a,b=event["ids"]
            if event["kind"]=="break":
                kind="original_bond_break" if tuple(event["ids"]) in EDGES else "external_break"
            elif internal:
                kind="internal_form"
            else:
                newcomer=b if a in SOURCE else a
                kind=("attachment_form_prestep_free"
                      if pre_degrees[newcomer]==0
                      else "attachment_form_prestep_bonded")
            event_types[kind]+=1
            local_events[kind]+=1
        if first_loss is None and not st["pure"]:
            first_loss=w.step
            mode=classify_loss(
                not st["core_edges_retained"],bool(st["direct_external_edges"])
            )
            # First loss is a net-state classification; event causes may
            # include additional transient within-step reactions.
            cause={
                "tick":w.step,
                "mode":mode,
                "prestep_source_pure":prev_status["pure"],
                "poststep":st,
                "incident_events":events,
                "incident_event_kinds":dict(event_types),
            }
            first_loss_details=cause
            class_counts[mode]+=1
        if first_original_loss is None and not st["core_edges_retained"]:
            first_original_loss=w.step
        if first_growth is None and st["core_grown"]:
            first_growth=w.step

        if st["pure"]:
            phase="pure"
            tick_totals["pure_ticks"]+=1
        elif st["core_edges_retained"]:
            phase="core_grown"
            tick_totals["core_grown_ticks"]+=1
        else:
            phase="core_edges_missing"
            tick_totals["core_missing_ticks"]+=1

        if st["core_edges_retained"]:
            tick_totals["core_bond_retained_ticks"]+=1
        if st["core_connected"]:
            tick_totals["core_connected_ticks"]+=1
        if st["core_grown"]:
            tick_totals["core_grown_event_ticks"]+=1

        opportunities=eligible_partner_pairs(w)
        for key,val in opportunities.items():
            tick_totals[f"{phase}_{key}"]+=val

        for indices,bonds in grouped:
            members={w.store.ids[i] for i in indices}
            if members & SOURCE:
                ever_shared.update(members-SOURCE)

        for indices,bonds in grouped:
            members=frozenset(w.store.ids[i] for i in indices)
            if len(indices)!=4 or members & SOURCE:
                continue
            if len(bonds)!=3:
                continue
            s=signature(w.store,indices,bonds,w.species_names)
            if not s.exact or s.key not in target_signatures.values():
                continue
            key=(s.key,tuple(sorted(members)))
            if key in seen:
                continue
            seen.add(key)
            name=next(n for n,val in target_signatures.items() if val==s.key)
            near=any(
                toroidal_distance((w.store.xs[i],w.store.ys[i]),a,
                                   w.store.width,w.store.height)<=2
                for i in indices for a in ANCHORS
            )
            shared=bool(members & ever_shared)
            phase_counts[f"all_{name}"]+=1
            if not shared:
                phase_counts[f"strict_{phase}_{'near' if near else 'far'}_{name}"]+=1
                if near and len(samples)<20:
                    samples.append({"tick":w.step,"variant":name,
                                    "phase":phase,"ids":sorted(members)})

        assert before_rng==w.rng.draws,"observer must not consume RNG"
        prev_status=st
        pre_degrees={pid:w.store.degree[w.store.index_of(pid)] for pid in w.store.ids}

    for _ in range(p["integrity"]["expected_steps"]):
        world.advance(1,observer=observe)
    world.event_sink=None
    world.check()
    # A run that never leaves its pure state is right-censored, not an error.
    if first_loss_details is not None:
        assert first_loss_details["mode"]!="other",first_loss_details
    assert tick_totals["pure_ticks"]+tick_totals["core_grown_ticks"]+tick_totals["core_missing_ticks"]==450
    return {
        "seed":world.config.seed,"arm":arm,
        "first_loss_tick":first_loss,
        "first_loss":first_loss_details,
        "first_original_edge_loss_tick":first_original_loss,
        "first_core_growth_tick":first_growth,
        "ticks":dict(sorted(tick_totals.items())),
        "incident_bond_events":dict(sorted(local_events.items())),
        "motif_counts":dict(sorted(phase_counts.items())),
        "first_strict_near_events":samples,
        "initial_hash":start_hash,"final_hash":world.state_hash_full(),
        "config_hash":world.config.hash(),
        "initial_rng_draws":start_draws,"final_rng_draws":world.rng.draws,
        "initial_rng_fingerprint":start_rng,
        "final_rng_fingerprint":world.rng.fingerprint(),
        "formations":world.bonds_formed_total,
        "breaks":world.bonds_broken_total,
        "energy_final":world.energy(),"dissipated_final":world.dissipated,
    }


def signature_of(world):
    """Existing fixture helper has full exact-signature validation."""
    from tools.m6_3_0_screen import signature_of_scaffold
    return signature_of_scaffold(world)


def aggregate(rows,p):
    result={}
    for density in p["model"]["densities"]:
        subset=[r for r in rows if r["density"]==density]
        categories=Counter(r["first_loss"]["mode"] if r["first_loss"] else "censored" for r in subset)
        counts=Counter()
        motifs=Counter()
        for row in subset:
            counts.update(row["ticks"])
            motifs.update(row["motif_counts"])
        num=len(subset)
        result[density]={
            "worlds":num,
            "first_loss_categories":dict(categories),
            "first_loss_prestep_monomer_forms":sum(
                (r["first_loss"] or {"incident_event_kinds":{}})["incident_event_kinds"].get(
                    "attachment_form_prestep_free",0) for r in subset
            ),
            "first_loss_prestep_bonded_forms":sum(
                r["first_loss"]["incident_event_kinds"].get(
                    "attachment_form_prestep_bonded",0) for r in subset
            ),
            "mean_first_loss_tick_observed":round(sum(r["first_loss_tick"] for r in subset if r["first_loss_tick"] is not None)/sum(r["first_loss_tick"] is not None for r in subset),3) if any(r["first_loss_tick"] is not None for r in subset) else None,
            "right_censored_runs":sum(r["first_loss_tick"] is None for r in subset),
            "mean_pure_ticks":round(counts["pure_ticks"]/num,3),
            "mean_core_grown_ticks":round(counts["core_grown_ticks"]/num,3),
            "mean_core_edges_retained_ticks":round(counts["core_bond_retained_ticks"]/num,3),
            "mean_core_connected_ticks":round(counts["core_connected_ticks"]/num,3),
            "core_grown_worlds":sum(r["first_core_growth_tick"] is not None for r in subset),
            "initial_bond_broken_worlds":sum(r["first_original_edge_loss_tick"] is not None for r in subset),
            "eligible_pairs_while_pure":sum(
                counts.get(f"pure_eligible_{s}",0) for s in ("S0","S1")
            ),
            "eligible_pairs_while_core_grown":sum(
                counts.get(f"core_grown_eligible_{s}",0) for s in ("S0","S1")
            ),
            "free_neighbors_while_pure":sum(
                counts.get(f"pure_free_adjacent_{s}",0) for s in ("S0","S1")
            ),
            "strict_near_A_B_while_pure":sum(
                motifs.get(f"strict_pure_near_{s}",0) for s in ("A","B")
            ),
            "strict_near_A_B_while_core_grown":sum(
                motifs.get(f"strict_core_grown_near_{s}",0) for s in ("A","B")
            ),
            "strict_near_A_B_after_core_edge_loss":sum(
                motifs.get(f"strict_core_edges_missing_near_{s}",0)
                for s in ("A","B")
            ),
            "worlds_with_pure_eligible_pair":sum(
                (r["ticks"].get("pure_eligible_S0",0)
                +r["ticks"].get("pure_eligible_S1",0))>0
                for r in subset
            ),
        }
        per_arm={}
        for arm in p["model"]["arm_order"]:
            arm_rows=[r for r in subset if r["arm"]==arm]
            per_arm[arm]={
                "first_loss":dict(Counter(r["first_loss"]["mode"] if r["first_loss"] else "censored" for r in arm_rows)),
                "mean_pure_ticks":round(sum(r["ticks"]["pure_ticks"] for r in arm_rows)/len(arm_rows),3),
                "mean_core_retained_ticks":round(
                    sum(r["ticks"]["core_bond_retained_ticks"] for r in arm_rows)/len(arm_rows),3
                )
            }
        result[density]["arms"]=per_arm
    return result


def run():
    research=audit_protocol()
    earlier=m631_protocol()
    assert earlier["model"]["seed_list"] == list(range(8101,8117))
    targets=variants(earlier)
    assert len(set(targets.values()))==3
    cases=[]
    paired={}
    for density in earlier["model"]["densities"]:
        setup=density_protocol(earlier,density)
        for seed in earlier["model"]["seed_list"]:
            reference=None
            for arm in earlier["model"]["arm_order"]:
                w=make_world(seed,arm,setup)
                state=paired_initial_state(w)
                if reference is None:
                    reference=state
                assert state==reference,"initial state not energy/RNG-matched"
                result=analyse_one(w,research,arm,targets)
                result["density"]=density
                cases.append(result)
            print(f"{density}/{seed} complete: five arms",flush=True)

    # Independent, fixed preselected cross-observer verification (not selected
    # after scientific results) against the previous 6.3-1 instrumentation.
    comparisons=[]
    for density,seed,arm in research["integrity"]["two_fixed_replays"]:
        historical=next(r for r in cases if
                        (r["density"],r["seed"],r["arm"])==(density,seed,arm))
        control=take_measurements(
            make_world(seed,arm,density_protocol(earlier,density)),
            earlier,arm,targets
        )
        assert historical["final_hash"]==control["final_hash"]
        assert historical["initial_hash"]==control["initial_hash"]
        assert historical["final_rng_draws"]==control["final_rng_draws"]
        assert historical["final_rng_fingerprint"]==control["final_rng_fingerprint"]
        assert historical["formations"]==control["bond_formations"]
        assert historical["breaks"]==control["bond_breaks"]
        assert historical["energy_final"]==control["final_energy"]
        assert historical["dissipated_final"]==control["final_dissipated"]
        # Purity in the new observer must match *every* post-step active tick
        # reported in the earlier M6.3-1 tool.
        assert historical["ticks"]["pure_ticks"]==control["active_template_ticks"]
        comparisons.append({
            "density":density,"seed":seed,"arm":arm,
            "verified_hash":historical["final_hash"],
            "verified_pure_ticks":historical["ticks"]["pure_ticks"]
        })
    assert len(cases)==160
    summary=aggregate(cases,earlier)
    record={
        "schema":research["schema"],
        "protocol_commit":"43613a0818edab180a60cd70ab3cdfe7f1e43a51",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "source_conditions":"unchanged M6.3-1 fixtures, seeds, duration, engine",
        "n_cases":len(cases),
        "validation":{"reference_replays":comparisons,"no_engine_changes":True},
        "summary":summary,
        "cases":cases,
        "epistemic_status":"descriptive post-hoc physical audit, no transmission evidence",
        "scientific_verdict":"causal_replication_not_demonstrated"
    }
    OUT.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print("FIVE_STAGE_SUMMARY="+json.dumps({
        "n_cases":len(cases),"summary":summary,
        "reference_replays":comparisons,
        "verdict":record["scientific_verdict"],
    },sort_keys=True),flush=True)
    print("AUDIT_JSON="+str(OUT.relative_to(ROOT)),flush=True)
    return record


if __name__=="__main__":
    run()
