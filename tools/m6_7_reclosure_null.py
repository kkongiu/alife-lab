"""M6.7: preregistered 10-tick bond-reclosure audit.

All physical transitions use native World.advance and original chemistry.
Observer sees existing _candidate_pairs at pre-step (a *proxy*, not the
full post-break/post-move candidate list) and receives original BondEvents.
No observer consumes random draws or modifies world state.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife import chemistry
from tools.m6_4_cycles import create_natural, protocol as natural_protocol
from tools.m6_5_ring_forks import clone_world, open_bond, opening_edges, ring4_candidates, status

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m6_7_reclosure_null/protocol.json"
OUTPUT=ROOT/"campaigns/m6_7_reclosure_null/results.json"


def prereg():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-7-reclosure-ordinary-chemistry-null-v1"
    assert p["status"]=="frozen-before-runner-and-results"
    assert p["prespecified_source"]["new_seeds"]==list(range(9201,9221))
    assert p["prespecified_source"]["max_precursor_ticks"]==600
    assert p["prespecified_source"]["tick_horizon"]==10
    assert abs(p["null_model"]["reference_probability_by_tick10"]-(1-.95**10))<1e-12
    return p


class RingEventSink:
    def __init__(self,ids):
        self.source_ids=set(ids)
        self.events=[]

    def emit(self,event):
        if event.id_a in self.source_ids or event.id_b in self.source_ids:
            self.events.append({
                "kind":event.kind,
                "step":int(event.step),
                "edge":tuple(sorted((int(event.id_a),int(event.id_b)))),
                "energy":event.energy,
            })


def target_edge_candidate(w,edge):
    """Read-only pre-dissipation approximation to native chemistry eligibility."""
    a=w.store.index_of(edge[0])
    b=w.store.index_of(edge[1])
    pair=tuple(sorted((a,b)))
    if pair in w.store.bonds:
        return False
    return any((i,j)==pair for i,j in chemistry._candidate_pairs(w))


def opened_followup(source,ring,edge,horizon,verify_sham=False):
    initial_hash=source.state_hash_full()
    initial_rng=source.rng.fingerprint()
    initial_draws=source.rng.draws
    w=clone_world(source)
    original_energy=w.energy()
    redistributed=open_bond(w,edge)
    assert w.energy()==original_energy
    assert w.rng.fingerprint()==initial_rng and w.rng.draws==initial_draws
    assert not status(w,ring["ids"])["ring"]
    assert status(w,ring["ids"])["isolated"]
    initial_open_hash=w.state_hash_full()
    sink=RingEventSink(ring["ids"])
    w.event_sink=sink

    initial_candidates=[]
    ring_present=[]
    edge_present=[]
    source_events=[]
    first_formation_tick=None
    first_ring_tick=None
    first_bond_tick=None
    events_after_form=0
    for tick in range(1,horizon+1):
        candidate=target_edge_candidate(w,edge)
        initial_candidates.append(candidate)
        start=len(sink.events)
        draw_count=w.rng.draws
        w.advance(1)
        assert w.rng.draws>=draw_count
        events=sink.events[start:]
        source_events.append([{"tick":tick,**e} for e in events])
        reformed=any(e["kind"]=="form" and e["edge"]==tuple(edge) for e in events)
        if reformed:
            events_after_form+=1
            if first_formation_tick is None:
                first_formation_tick=tick
        component=status(w,ring["ids"])
        ring_present.append(component["ring"])
        if component["ring"] and first_ring_tick is None:
            first_ring_tick=tick
        i=w.store.index_of(edge[0])
        j=w.store.index_of(edge[1])
        target_bond=tuple(sorted((i,j))) in w.store.bonds
        edge_present.append(target_bond)
        if target_bond and first_bond_tick is None:
            first_bond_tick=tick

    w.check()
    assert source.state_hash_full()==initial_hash
    assert source.rng.fingerprint()==initial_rng
    assert source.rng.draws==initial_draws
    result={
        "opened_edge":list(edge),
        "bond_energy_reallocated":redistributed,
        "initial_closed_hash":initial_hash,
        "initial_open_hash":initial_open_hash,
        "initial_rng_fingerprint":initial_rng,
        "initial_rng_draws":initial_draws,
        "first_formation_event_tick":first_formation_tick,
        "first_ring_snapshot_tick":first_ring_tick,
        "first_target_edge_snapshot_tick":first_bond_tick,
        "any_target_bond_formation_event":first_formation_tick is not None,
        "any_ring_snapshot":first_ring_tick is not None,
        "target_pre_step_candidate_flags":initial_candidates,
        "candidate_opportunities_before_first_event":sum(
            initial_candidates[:first_formation_tick] if first_formation_tick is not None else initial_candidates
        ),
        "candidate_ticks_before_first_event":first_formation_tick if first_formation_tick is not None else horizon,
        "target_edge_snapshot_flags":edge_present,
        "original_ring_snapshot_flags":ring_present,
        "formation_event_count":events_after_form,
        "source_bond_events":source_events,
        "final_full_hash":w.state_hash_full(),
        "final_rng_fingerprint":w.rng.fingerprint(),
        "final_rng_draws":w.rng.draws,
        "final_energy":w.energy(),
        "final_dissipated":w.dissipated,
        "final_formed":w.bonds_formed_total,
        "final_broken":w.bonds_broken_total,
        "final_isolated":status(w,ring["ids"])["isolated"],
    }
    if verify_sham:
        sham=clone_world(source)
        senergy=sham.energy()
        assert open_bond(sham,edge)==redistributed
        assert sham.energy()==senergy
        assert sham.state_hash_full()==initial_open_hash
        sham.advance(horizon)
        sham.check()
        assert sham.state_hash_full()==result["final_full_hash"]
        assert sham.rng.fingerprint()==result["final_rng_fingerprint"]
        assert sham.rng.draws==result["final_rng_draws"]
        assert sham.energy()==result["final_energy"]
        assert sham.dissipated==result["final_dissipated"]
        assert sham.bonds_formed_total==result["final_formed"]
        assert sham.bonds_broken_total==result["final_broken"]
    return result


def sample_density(density,p):
    natural=natural_protocol()
    settings=p["prespecified_source"]
    worlds=[]
    forks=[]
    for seed in settings["new_seeds"]:
        world=create_natural(seed,density,natural)
        seen=set()
        selected=0
        for _ in range(settings["max_precursor_ticks"]):
            world.advance(1)
            for ring in ring4_candidates(world):
                if ring["ids"] in seen:
                    continue
                seen.add(ring["ids"])
                lo,op=opening_edges(ring)
                source_hash=world.state_hash_full()
                source_rng=world.rng.fingerprint()
                cases={
                    "lowest_source_id_edge":opened_followup(
                        world,ring,lo,settings["tick_horizon"],
                        verify_sham=(seed==settings["new_seeds"][0] and selected==0)
                    ),
                    "opposite_disjoint_edge":opened_followup(
                        world,ring,op,settings["tick_horizon"]
                    ),
                }
                assert world.state_hash_full()==source_hash
                assert world.rng.fingerprint()==source_rng
                forks.append({
                    "density":density,"seed":seed,"tick":world.step,
                    "ring":ring,"cases":cases
                })
                selected+=1
                if selected>=2:
                    break
            if selected>=2:
                break
        worlds.append({
            "density":density,"seed":seed,
            "selected_rings":selected,
            "precursor_stopped_at_tick":world.step,
            "precursor_end_hash":world.state_hash_full(),
        })
        print(f"M67_SELECT={density}/{seed} rings={selected}",flush=True)
    return worlds,forks


def summarize(forks,p):
    out={}
    reference=p["null_model"]["reference_probability_by_tick10"]
    for density in p["prespecified_source"]["densities"]:
        d={}
        for arm in p["prespecified_source"]["opened_arms"]:
            trials=[f["cases"][arm] for f in forks if f["density"]==density]
            n=len(trials)
            hits=sum(x["any_target_bond_formation_event"] for x in trials)
            rings=sum(x["any_ring_snapshot"] for x in trials)
            pre_count=sum(x["candidate_opportunities_before_first_event"] for x in trials)
            exposed_count=sum(x["candidate_ticks_before_first_event"] for x in trials)
            rate=hits/n if n else None
            d[arm]={
                "n":n,
                "target_formed_at_least_once_by_tick10":hits,
                "first_ring_snapshot_by_tick10":rings,
                "fraction_formation":round(rate,4) if rate is not None else None,
                "delta_vs_naive_bernoulli":round(rate-reference,4) if rate is not None else None,
                "formation_tick_hist":dict(sorted(Counter(
                    str(x["first_formation_event_tick"]) if x["first_formation_event_tick"] else "none"
                    for x in trials
                ).items())),
                "candidate_eligible_pre_step_ticks_until_first_hit":pre_count,
                "ticks_until_first_hit_or_horizon":exposed_count,
                "pre_step_candidate_fraction":round(pre_count/exposed_count,4) if exposed_count else None,
                "target_event_but_no_ring_snapshot":sum(
                    x["any_target_bond_formation_event"] and not x["any_ring_snapshot"]
                    for x in trials
                ),
                "ring_snapshot_but_no_target_event":sum(
                    x["any_ring_snapshot"] and not x["any_target_bond_formation_event"]
                    for x in trials
                ),
            }
        out[density]=d

    nmin=p["decision"]["min_opened_forks_per_density_per_arm"]
    margin=p["decision"]["absolute_margin_to_naive_reference"]
    all_arms=[out[den][arm] for den in p["prespecified_source"]["densities"]
              for arm in p["prespecified_source"]["opened_arms"]]
    if any(x["n"]<nmin for x in all_arms):
        verdict=p["decision"]["label_if_underpowered"]
    elif all(abs(x["fraction_formation"]-reference)<=margin for x in all_arms):
        verdict=p["decision"]["label_if_all_four_strata_within_margin"]
    else:
        verdict=p["decision"]["label_if_any_stratum_outside_margin"]
    return {
        "naive_reference":round(reference,6),
        "reference_limit":"Assumes a fresh always-eligible independent Bernoulli trial each tick; NOT an exact prediction for competing live chemistry",
        "density_arm":out,
        "verdict":verdict,
        "scientific_claim":"diagnostic of ordinary contact kinetics, not biological self-repair or special repair mechanism",
    }


def run():
    p=prereg()
    worlds=[]
    forks=[]
    for density in p["prespecified_source"]["densities"]:
        a,b=sample_density(density,p)
        worlds+=a
        forks+=b
    score=summarize(forks,p)
    assert len(worlds)==40
    assert len(forks)<=80
    result={
        "schema":"m6-7-ordinary-contact-null-results-v1",
        "protocol_commit":"c6fc5f92bd9b35401f945028f6217b3c01a7fff0",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "source_worlds":len(worlds),
        "distinct_natural_ring_forks":len(forks),
        "opened_trajectories":len(forks)*2,
        "summary":score,
        "worlds":worlds,"forks":forks,
        "laws_unchanged":True,
        "no_special_repair_claim":True
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M67_BERNOULLI_NULL_SUMMARY="+json.dumps({
        "worlds":len(worlds),"forks":len(forks),
        "opened_trajectories":len(forks)*2,"summary":score
    },sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    run()
