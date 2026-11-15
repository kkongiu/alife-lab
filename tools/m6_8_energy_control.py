"""M6.8: energy-allocation fork at naturally born four-rings.

Two opened arms have IDENTICAL geometry, bond set, valences, whole-system
energy and starting RNG; ONLY placement of stored bond energy differs.
One refunds endpoints (M6.5); one sequesters in an inert distant S3.
After intervention both evolve solely under unchanged original M6 physics.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from tools.m6_4_cycles import create_natural, protocol as natural_protocol
from tools.m6_5_ring_forks import (
    clone_world, open_bond, ring4_candidates, opening_edges, followup, status
)

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m6_8_energy_control/protocol.json"
OUTPUT=ROOT/"campaigns/m6_8_energy_control/results.json"


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-8-inert-energy-allocation-v1"
    assert p["status"]=="frozen-before-runner-and-outcomes"
    assert p["seeds"]==list(range(9401,9421))
    assert p["horizon"]==120 and p["early_horizon"]==10
    assert p["gate"]["strong_margin"]==.15
    return p


def toroidal_dist(s,a,b):
    ax,ay=s.xs[a],s.ys[a]
    bx,by=s.xs[b],s.ys[b]
    dx=abs(ax-bx)
    dy=abs(ay-by)
    return min(dx,s.width-dx)+min(dy,s.height-dy)


def select_inert_s3(w,ids):
    """Deterministic farthest nonbonding species S3, not a ring source atom."""
    s=w.store
    ring=[s.index_of(x) for x in ids]
    candidates=[]
    for idx,species_index in enumerate(s.species):
        if w.species_names[species_index]!="S3":
            continue
        assert w.max_bonds[species_index]==0
        if s.ids[idx] in ids:
            continue
        nearest=min(toroidal_dist(s,idx,core) for core in ring)
        candidates.append((nearest,s.ids[idx],idx))
    if not candidates:
        raise RuntimeError("No chemically inert S3 available. Do not silently select replacement.")
    nearest,identifier,index=max(candidates,key=lambda v:(v[0],-v[1]))
    return index,nearest


def open_sequester(w,edge,ids):
    """Open exact edge; move the stored energy to far non-reactive S3."""
    idx,distance=select_inert_s3(w,ids)
    s=w.store
    i=s.index_of(edge[0])
    j=s.index_of(edge[1])
    source_energies={i:s.energy[i],j:s.energy[j]}
    before=w.energy()
    saved=s.remove_bond(i,j)
    s.energy[idx]+=saved
    w.check()
    assert w.energy()==before
    assert all(s.energy[i]==energy for i,energy in source_energies.items())
    assert w.max_bonds[s.species[idx]]==0
    return saved,s.ids[idx],distance


class SourceEventSink:
    """Observe only events touching one of the four original material IDs."""
    def __init__(self,source_ids):
        self.material=set(source_ids)
        self.events=[]

    def emit(self,event):
        if event.id_a in self.material or event.id_b in self.material:
            self.events.append({
                "step":int(event.step),
                "kind":event.kind,
                "edge":tuple(sorted((int(event.id_a),int(event.id_b)))),
                "energy":int(event.energy),
            })


def execute_case(w,ids,edge,source_step,horizon,early):
    sink=SourceEventSink(ids)
    w.event_sink=sink
    result=followup(w,ids,horizon)
    matching=[
        1+ev["step"]-source_step for ev in sink.events
        if ev["kind"]=="form" and ev["edge"]==tuple(edge)
    ]
    result["first_opened_edge_formation_tick"]=min(matching) if matching else None
    result["opened_edge_formed_by_t10"]=any(x<=early for x in matching)
    result["ring_by_t10"]=(
        result["first_ring_observed_tick"] is not None
        and result["first_ring_observed_tick"]<=early
    )
    result["source_bond_events"]=sink.events
    return result


def matched_fork(original,ring,p,sham=False):
    ids=ring["ids"]
    edge=opening_edges(ring)[0]
    step=original.step
    original_hash=original.state_hash_full()
    rng=original.rng.fingerprint()
    draws=original.rng.draws
    energy=original.energy()

    neutral_probe,far=select_inert_s3(original,ids)
    s=original.store
    source_indices=[s.index_of(v) for v in ids]
    endpoint_indices=[s.index_of(v) for v in edge]
    source_energies=[s.energy[i] for i in source_indices]
    eligible_before=sum(s.energy[i]>=original.formation_cost for i in endpoint_indices)

    worlds={arm:clone_world(original) for arm in p["arms"]}
    neutral_id=s.ids[neutral_probe]
    saved=0
    for arm,w in worlds.items():
        assert w.energy()==energy
        assert w.state_hash_full()==original_hash
        assert w.rng.fingerprint()==rng and w.rng.draws==draws
        if arm=="open_refund_endpoints":
            saved=open_bond(w,edge)
        elif arm=="open_sequester_in_S3":
            stored,chosen,distance=open_sequester(w,edge,ids)
            assert stored==saved and chosen==neutral_id and distance==far
            assert [w.store.energy[i] for i in source_indices]==source_energies
        else:
            assert arm=="keep_intact"
        assert w.energy()==energy
        assert w.rng.fingerprint()==rng
        assert w.rng.draws==draws

    refund=worlds["open_refund_endpoints"]
    sink=worlds["open_sequester_in_S3"]
    assert refund.store.xs==sink.store.xs
    assert refund.store.ys==sink.store.ys
    assert refund.store.ids==sink.store.ids
    assert refund.store.species==sink.store.species
    assert refund.store.bonds==sink.store.bonds
    assert refund.store.degree==sink.store.degree
    assert not status(refund,ids)["ring"]
    assert not status(sink,ids)["ring"]
    assert status(refund,ids)["isolated"] and status(sink,ids)["isolated"]
    assert all(refund.store.energy[i]>=sink.store.energy[i] for i in endpoint_indices)
    assert refund.store.energy[neutral_probe]+saved==sink.store.energy[neutral_probe]

    start_info={
        "ids":list(ids),"opened_edge":list(edge),
        "source_ring_signature":ring["sig"],
        "original_world_step":step,"original_world_hash":original_hash,
        "neutral_s3_particle_id":neutral_id,
        "neutral_s3_distance_to_ring":far,
        "stored_bond_energy":saved,
        "original_four_source_energies":source_energies,
        "endpoints_at_formation_cost_before_opening":eligible_before,
        "energy_fork":energy,
        "rng_fingerprint_fork":rng,
        "rng_draws_fork":draws,
    }
    arms={}
    for arm,w in worlds.items():
        entry={
            "initial_hash":w.state_hash_full(),
            "initial_source_energies":[w.store.energy[i] for i in source_indices],
            "initial_neutral_s3_energy":w.store.energy[neutral_probe],
        }
        entry.update(execute_case(w,ids,edge,step,p["horizon"],p["early_horizon"]))
        arms[arm]=entry
    if sham:
        for arm in p["arms"]:
            w=clone_world(original)
            if arm=="open_refund_endpoints":
                assert open_bond(w,edge)==saved
            elif arm=="open_sequester_in_S3":
                assert open_sequester(w,edge,ids)[0]==saved
            w.advance(p["horizon"])
            w.check()
            assert w.state_hash_full()==arms[arm]["final_hash"]
            assert w.rng.fingerprint()==arms[arm]["final_rng_fingerprint"]
            assert w.rng.draws==arms[arm]["final_rng_draws"]
            assert w.energy()==arms[arm]["final_energy"]
            assert w.dissipated==arms[arm]["final_dissipated"]
    assert original.state_hash_full()==original_hash
    assert original.rng.fingerprint()==rng and original.rng.draws==draws
    return {"fork":start_info,"arms":arms}


def sample_density(density,p):
    natural=natural_protocol()
    worlds=[]
    selected=[]
    for seed in p["seeds"]:
        world=create_natural(seed,density,natural)
        observed=set()
        forks=[]
        for _ in range(p["select_until_tick"]):
            world.advance(1)
            for ring in ring4_candidates(world):
                if ring["ids"] in observed:
                    continue
                observed.add(ring["ids"])
                case=matched_fork(
                    world,ring,p,
                    sham=(seed==p["seeds"][0] and len(forks)==0)
                )
                case["density"]=density
                case["seed"]=seed
                forks.append(case)
                selected.append(case)
                if len(forks)==p["first_distinct_rings_per_world"]:
                    break
            if len(forks)==p["first_distinct_rings_per_world"]:
                break
        worlds.append({"density":density,"seed":seed,
                       "selected":len(forks),"selection_stopped_at_tick":world.step,
                       "precursor_hash_at_stop":world.state_hash_full()})
        print(f"M68_SELECT={density}/{seed} selected={len(forks)}",flush=True)
    return worlds,selected


def summary(cases,p):
    by_density={}
    for den in p["densities"]:
        subset=[f for f in cases if f["density"]==den]
        arms={}
        for arm in p["arms"]:
            rows=[f["arms"][arm] for f in subset]
            arms[arm]={
                "n":len(rows),
                "isolated_at_horizon":sum(r["final_isolated"] for r in rows),
                "isolated_rate":round(sum(r["final_isolated"] for r in rows)/len(rows),4)
                  if rows else None,
                "ring_by_horizon":sum(r["first_ring_observed_tick"] is not None
                                      for r in rows),
                "first_loss_observed":sum(r["first_loss_tick"] is not None for r in rows),
                "mean_isolated_ticks":round(sum(r["isolated_ticks"] for r in rows)/len(rows),3)
                  if rows else None,
                "opened_edge_reformed_by_t10":sum(r["opened_edge_formed_by_t10"] for r in rows)
                  if arm!="keep_intact" else None,
                "early_reformation_rate":round(sum(r["opened_edge_formed_by_t10"] for r in rows)/len(rows),4)
                  if rows and arm!="keep_intact" else None,
            }
        refund=arms["open_refund_endpoints"]
        neutral=arms["open_sequester_in_S3"]
        early=(refund["early_reformation_rate"]-neutral["early_reformation_rate"]
               if len(subset) else None)
        isolation=(refund["isolated_rate"]-neutral["isolated_rate"]
                   if len(subset) else None)
        by_density[den]={
            "n_selected_forks":len(subset),
            "arms":arms,
            "refund_minus_sequester_early_formation":round(early,4) if early is not None else None,
            "refund_minus_sequester_final_isolation":round(isolation,4) if isolation is not None else None,
            "all_original_source_endpoints_energy_sufficient":sum(
                x["fork"]["endpoints_at_formation_cost_before_opening"]==2
                for x in subset),
            "paired_early_refund_only":sum(
                x["arms"]["open_refund_endpoints"]["opened_edge_formed_by_t10"] and
                not x["arms"]["open_sequester_in_S3"]["opened_edge_formed_by_t10"]
                for x in subset),
            "paired_early_sequester_only":sum(
                x["arms"]["open_sequester_in_S3"]["opened_edge_formed_by_t10"] and
                not x["arms"]["open_refund_endpoints"]["opened_edge_formed_by_t10"]
                for x in subset),
        }

    strata=list(by_density.values())
    if any(x["n_selected_forks"]<p["gate"]["min_forks_per_density"] for x in strata):
        verdict="underpowered"
    else:
        early=[x["refund_minus_sequester_early_formation"] for x in strata]
        isolation=[x["refund_minus_sequester_final_isolation"] for x in strata]
        strong=p["gate"]["strong_margin"]
        small=p["gate"]["small_margin"]
        def strong_pair(contrasts):
            return (
                all(abs(x)>=strong for x in contrasts) and
                (all(x>0 for x in contrasts) or all(x<0 for x in contrasts))
            )
        if strong_pair(early) or strong_pair(isolation):
            verdict="allocation_effect_signal_needs_replication"
        elif all(abs(x)<=small for x in early+isolation):
            verdict="no_large_allocation_effect_detected_descriptive"
        else:
            verdict="mixed_or_uncertain_energy_allocation_effect"
    return {"by_density":by_density,"verdict":verdict,
            "scientific_limit":"same opened topology but different energy distribution; no pure life/self-repair claim"}


def run():
    p=protocol()
    all_worlds=[]
    all_cases=[]
    for den in p["densities"]:
        worlds,cases=sample_density(den,p)
        all_worlds+=worlds
        all_cases+=cases
    assert len(all_worlds)==p["n_worlds"]
    assert len(all_cases)<=p["max_forks"]
    score=summary(all_cases,p)
    payload={
        "schema":"m6-8-energy-allocation-results-v1",
        "protocol_commit":"aa8be77fe4c833e21caabffcf59ca67f9790d326",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "world_count":len(all_worlds),
        "fork_count":len(all_cases),
        "arms_per_fork":len(p["arms"]),
        "summary":score,
        "worlds":all_worlds,"forks":all_cases,
        "original_chemistry_laws_unchanged":True,
        "no_heredity_or_life_claim":True,
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print("M68_ENERGY_CONTROL_SUMMARY="+json.dumps({
        "world_count":len(all_worlds),"fork_count":len(all_cases),
        "summary":score
    },sort_keys=True),flush=True)
    return payload


if __name__=="__main__":
    run()
