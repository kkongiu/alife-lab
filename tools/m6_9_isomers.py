"""M6.9: causal S0/S1 cyclic-isomer intervention on naturally formed 2+2 rings.

The four source atoms, topology, energy, and RNG are identical before the
intervention; only cyclic order of their species labels changes. This is a
controlled INITIAL-CONDITION perturbation, never a change in M6 physical laws.
If all ring bonds are intact, max-valence-two fully saturated atoms are
immobile and unavailable for new reactions. The full non-species universe
must therefore replay identically until the first source bond breaks.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.structures import components, signature_v2
from tools.m6_4_cycles import create_natural, protocol as natural_protocol
from tools.m6_5_ring_forks import clone_world, ring4_candidates, status

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m6_9_isomers/protocol.json"
OUTPUT=ROOT/"campaigns/m6_9_isomers/results.json"

PATTERNS={
    "adjacent_S0S0S1S1":(0,0,1,1),
    "alternating_S0S1S0S1":(0,1,0,1),
}


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-9-ring-sequence-isomer-causal-v1"
    assert p["status"]=="frozen-before-experimental-code-and-outcomes"
    assert p["natural_sample"]["seeds"]==list(range(9601,9651))
    assert p["natural_sample"]["expected_worlds"]==100
    assert p["natural_sample"]["max_precursor_tick"]==600
    assert p["natural_sample"]["followup_ticks"]==180
    assert p["preregistered_decision"]["large_effect_threshold"]==.15
    return p


def cyclic_order(ring):
    """Cycle order from existing source edges, unique up to reversal."""
    ids=tuple(ring["ids"])
    edges=ring["edges"]
    assert len(ids)==4 and len(edges)==4
    neighbours={v:[] for v in ids}
    for a,b in edges:
        neighbours[a].append(b)
        neighbours[b].append(a)
    assert all(len(x)==2 for x in neighbours.values())
    start=min(ids)
    previous=start
    current=min(neighbours[start])
    result=[start]
    while current!=start:
        assert current not in result and len(result)<4
        result.append(current)
        options=[v for v in neighbours[current] if v!=previous]
        assert len(options)==1
        previous,current=current,options[0]
    assert len(result)==4 and set(result)==set(ids)
    return tuple(result)


def _placements(pattern):
    n=len(pattern)
    variants=set()
    for orientation in (pattern,pattern[::-1]):
        for shift in range(n):
            variants.add(orientation[shift:]+orientation[:shift])
    return sorted(variants)


def two_plus_two(w,ring):
    s=w.store
    names=[w.species_names[s.species[s.index_of(v)]] for v in cyclic_order(ring)]
    return Counter(names)==Counter({"S0":2,"S1":2})


def assign_isomer(w,ring,variant):
    """Minimal S0/S1 swaps to requested cyclic isomer; preserve counts/energy."""
    assert variant in PATTERNS
    assert two_plus_two(w,ring)
    order=cyclic_order(ring)
    s=w.store
    original=[w.species_names[s.species[s.index_of(v)]] for v in order]
    # S0/S1 position count is preserved. Take the orientation requiring
    # the fewest species-label changes relative to naturally occurring ring.
    candidates=[
        tuple("S0" if value==0 else "S1" for value in labels)
        for labels in _placements(PATTERNS[variant])
    ]
    chosen=min(candidates,key=lambda labels:(
        sum(a!=b for a,b in zip(original,labels)),labels
    ))
    energy_before=w.energy()
    rng_before=w.rng.fingerprint()
    draws_before=w.rng.draws
    species_indices={name:w.species_names.index(name) for name in ("S0","S1")}
    changes=0
    for id_,before,after in zip(order,original,chosen):
        if before!=after:
            changes+=1
        s.species[s.index_of(id_)]=species_indices[after]
    assert Counter(w.species_names[s.species[s.index_of(v)]] for v in order)==Counter({"S0":2,"S1":2})
    assert w.energy()==energy_before
    assert w.rng.fingerprint()==rng_before and w.rng.draws==draws_before
    w.check()
    assert len(ring4_candidates(w))>=1
    exact=next(item["sig"] for item in ring4_candidates(w) if item["ids"]==ring["ids"])
    return {
        "source_labels":original,
        "assigned_labels":list(chosen),
        "changes_in_source_species_labels":changes,
        "exact_signature":exact,
    }


class SourceBreakObserver:
    def __init__(self,ids):
        self.ids=set(ids)
        self.events=[]

    def emit(self,event):
        if event.id_a in self.ids or event.id_b in self.ids:
            self.events.append({
                "step":int(event.step),
                "kind":event.kind,
                "edge":tuple(sorted((event.id_a,event.id_b))),
            })


def assert_prebreak_physics_identical(a,b,source_ids):
    """Reject hidden species-dependent effects while the source remains sealed.

    Ring species labels can differ by design; ALL OTHER state must be equal.
    """
    aa,bb=a.store,b.store
    assert aa.ids==bb.ids
    assert aa.xs==bb.xs
    assert aa.ys==bb.ys
    assert aa.energy==bb.energy
    assert aa.bonds==bb.bonds
    assert aa.degree==bb.degree
    ring=set(source_ids)
    assert all(sa==sb for id_,sa,sb in zip(aa.ids,aa.species,bb.species) if id_ not in ring)
    assert a.rng.fingerprint()==b.rng.fingerprint()
    assert a.rng.draws==b.rng.draws
    for field in (
        "step","moves_total","next_id","bonds_formed_total",
        "bonds_broken_total","injected","dissipated","unabsorbed"
    ):
        assert getattr(a,field)==getattr(b,field),field
    assert a.source_acc==b.source_acc and a.source_store==b.source_store
    assert a.energy()==b.energy()


def follow_pair(source,ring,p,sham=False):
    assert two_plus_two(source,ring)
    source_hash=source.state_hash_full()
    source_rng=source.rng.fingerprint()
    source_draws=source.rng.draws
    source_energy=source.energy()
    ids=ring["ids"]
    original_edges=set(map(tuple,ring["edges"]))
    arms={}
    placement={}
    for arm in PATTERNS:
        w=clone_world(source)
        placement[arm]=assign_isomer(w,ring,arm)
        assert w.energy()==source_energy
        assert w.rng.fingerprint()==source_rng and w.rng.draws==source_draws
        arms[arm]=w
    a,b=[arms[arm] for arm in PATTERNS]
    assert_prebreak_physics_identical(a,b,ids)
    assert placement["adjacent_S0S0S1S1"]["exact_signature"]!=placement["alternating_S0S1S0S1"]["exact_signature"]
    assert 0 in [entry["changes_in_source_species_labels"] for entry in placement.values()]
    if sum(v["changes_in_source_species_labels"] for v in placement.values())!=2:
        # Any original 2/2 pattern is adjacent or alternating; other
        # form is one S0/S1 position swap => two source labels modified.
        raise AssertionError("Expected a single two-label species exchange")

    horizon=p["natural_sample"]["followup_ticks"]
    sinks={arm:SourceBreakObserver(ids) for arm in PATTERNS}
    for arm,w in arms.items():
        w.event_sink=sinks[arm]

    first_break={arm:None for arm in PATTERNS}
    ring_flags={arm:[] for arm in PATTERNS}
    isolate_flags={arm:[] for arm in PATTERNS}
    old_event_counts={arm:0 for arm in PATTERNS}
    prebreak_equal_ticks=0

    for tick in range(1,horizon+1):
        for arm,w in arms.items():
            w.advance(1)
            new=sinks[arm].events[old_event_counts[arm]:]
            old_event_counts[arm]=len(sinks[arm].events)
            if first_break[arm] is None and any(
                event["kind"]=="break" and event["edge"] in original_edges
                for event in new
            ):
                first_break[arm]=tick
            state=status(w,ids)
            ring_flags[arm].append(state["ring"])
            isolate_flags[arm].append(state["isolated"])

        if (first_break["adjacent_S0S0S1S1"] is None
                and first_break["alternating_S0S1S0S1"] is None):
            assert_prebreak_physics_identical(a,b,ids)
            prebreak_equal_ticks+=1
        else:
            # A paired first-break time MUST coincide, or some hidden mechanism
            # affects sealed rings before the first physical rupture.
            assert first_break["adjacent_S0S0S1S1"]==first_break["alternating_S0S1S0S1"],(
                "First source-edge break differs despite identical pre-break chemistry",
                first_break
            )

    outcome={}
    for arm,w in arms.items():
        w.check()
        broken=first_break[arm]
        post_flags=ring_flags[arm][broken-1:] if broken is not None else []
        outcome[arm]={
            **placement[arm],
            "first_original_edge_break_tick":broken,
            "ring_at_final_tick":ring_flags[arm][-1],
            "isolated_at_final_tick":isolate_flags[arm][-1],
            "ring_ticks_total":sum(ring_flags[arm]),
            "isolated_ticks_total":sum(isolate_flags[arm]),
            "ring_ticks_from_first_break_inclusive":sum(post_flags),
            "ring_fraction_from_first_break_inclusive":round(sum(post_flags)/len(post_flags),6) if post_flags else None,
            "source_bond_events":sinks[arm].events,
            "final_hash":w.state_hash_full(),
            "final_rng_fingerprint":w.rng.fingerprint(),
            "final_rng_draws":w.rng.draws,
            "final_energy":w.energy(),
            "final_dissipated":w.dissipated,
            "final_formed":w.bonds_formed_total,
            "final_broken":w.bonds_broken_total
        }
    if sham:
        for arm in PATTERNS:
            other=clone_world(source)
            labels=assign_isomer(other,ring,arm)
            assert labels==placement[arm]
            other.advance(horizon)
            other.check()
            assert other.state_hash_full()==outcome[arm]["final_hash"]
            assert other.rng.fingerprint()==outcome[arm]["final_rng_fingerprint"]
            assert other.rng.draws==outcome[arm]["final_rng_draws"]
            assert other.energy()==outcome[arm]["final_energy"]
            assert other.dissipated==outcome[arm]["final_dissipated"]
    assert source.state_hash_full()==source_hash
    assert source.rng.fingerprint()==source_rng and source.rng.draws==source_draws
    return {
        "material_ids":list(ids),
        "original_signature":ring["sig"],
        "selected_tick":source.step,
        "first_break_both":first_break["adjacent_S0S0S1S1"],
        "prebreak_identical_full_physics_ticks":prebreak_equal_ticks,
        "initial_source_hash":source_hash,
        "initial_source_rng":source_rng,
        "arms":outcome
    }


def sample_density(den,p):
    natural=natural_protocol()
    worlds=[]
    selected=[]
    cfg=p["natural_sample"]
    for seed in cfg["seeds"]:
        w=create_natural(seed,den,natural)
        seen=set()
        cases=[]
        for _ in range(cfg["max_precursor_tick"]):
            w.advance(1)
            for ring in ring4_candidates(w):
                if ring["ids"] in seen or not two_plus_two(w,ring):
                    continue
                seen.add(ring["ids"])
                data=follow_pair(w,ring,p,sham=(seed==cfg["seeds"][0] and len(cases)==0))
                data["density"]=den
                data["precursor_seed"]=seed
                selected.append(data)
                cases.append(data)
                if len(cases)>=2:
                    break
            if len(cases)>=2:
                break
        worlds.append({
            "density":den,
            "seed":seed,
            "selected":len(cases),
            "selection_stop_tick":w.step,
            "final_precursor_hash":w.state_hash_full()
        })
        print(f"M69_PRECURSOR={den}/{seed} pairs={len(cases)}",flush=True)
    return worlds,selected


def summarize(forks,p):
    out={}
    cfg=p["natural_sample"]
    for den in cfg["densities"]:
        cases=[f for f in forks if f["density"]==den]
        broken=[f for f in cases if f["first_break_both"] is not None]
        arms={}
        for arm in PATTERNS:
            subset=[x["arms"][arm] for x in broken]
            n=len(subset)
            arms[arm]={
                "n_broken_pairs":n,
                "ring_at_180_after_original_break":sum(x["ring_at_final_tick"] for x in subset),
                "isolated_at_180_after_original_break":sum(x["isolated_at_final_tick"] for x in subset),
                "ring_at_180_rate":round(sum(x["ring_at_final_tick"] for x in subset)/n,4) if n else None,
                "isolated_at_180_rate":round(sum(x["isolated_at_final_tick"] for x in subset)/n,4) if n else None,
                "mean_fraction_ring_after_break":round(sum(x["ring_fraction_from_first_break_inclusive"] for x in subset)/n,4) if n else None,
                "native_placement_count":sum(x["changes_in_source_species_labels"]==0 for x in (f["arms"][arm] for f in cases))
            }
        a=arms["adjacent_S0S0S1S1"]
        b=arms["alternating_S0S1S0S1"]
        n=len(broken)
        out[den]={
            "natural_2S0_2S1_rings_selected":len(cases),
            "source_bond_break_pairs":n,
            "fully_synchronized_first_break_pairs":sum(
                f["arms"]["adjacent_S0S0S1S1"]["first_original_edge_break_tick"]==
                f["arms"]["alternating_S0S1S0S1"]["first_original_edge_break_tick"]
                for f in cases
            ),
            "unbroken_right_censored":len(cases)-n,
            "arms":arms,
            "delta_adjacent_minus_alternating_ring":round((a["ring_at_180_after_original_break"]-b["ring_at_180_after_original_break"])/n,4) if n else None,
            "delta_adjacent_minus_alternating_isolated":round((a["isolated_at_180_after_original_break"]-b["isolated_at_180_after_original_break"])/n,4) if n else None,
            "adjacent_only_ring_at_final":sum(
                f["arms"]["adjacent_S0S0S1S1"]["ring_at_final_tick"] and
                not f["arms"]["alternating_S0S1S0S1"]["ring_at_final_tick"]
                for f in broken
            ),
            "alternating_only_ring_at_final":sum(
                f["arms"]["alternating_S0S1S0S1"]["ring_at_final_tick"] and
                not f["arms"]["adjacent_S0S0S1S1"]["ring_at_final_tick"]
                for f in broken
            )
        }
    details=list(out.values())
    rule=p["preregistered_decision"]
    if any(x["natural_2S0_2S1_rings_selected"]<rule["min_selected_pairs_per_density"] or
           x["source_bond_break_pairs"]<rule["min_pairs_with_source_break_per_density"]
           for x in details):
        verdict="underpowered"
    else:
        ring=[x["delta_adjacent_minus_alternating_ring"] for x in details]
        isolated=[x["delta_adjacent_minus_alternating_isolated"] for x in details]
        big=rule["large_effect_threshold"]
        small=rule["small_effect_threshold"]
        def strong(ds):
            return all(abs(v)>=big for v in ds) and (
                all(v>0 for v in ds) or all(v<0 for v in ds))
        if strong(ring) or strong(isolated):
            verdict="sequence_sensitivity_signal_needs_new_seed_replication"
        elif all(abs(v)<=small for v in ring+isolated):
            verdict="no_large_sequence_effect_detected_descriptive"
        else:
            verdict="mixed_or_uncertain_sequence_effect"
    return {
        "by_density":out,
        "decision":verdict,
        "limits":"Paired species-label perturbation, not autonomous inheritance; correlated forks and no p-values."
    }


def run():
    p=protocol()
    worlds=[]
    forks=[]
    for den in p["natural_sample"]["densities"]:
        selected,paired=sample_density(den,p)
        worlds+=selected
        forks+=paired
    assert len(worlds)==100
    assert len(forks)<=200
    score=summarize(forks,p)
    result={
        "schema":"m6-9-natural-isomer-sequence-results-v1",
        "protocol_commit":"36e9f05214f86f4f5788beaae5e28cb8af76cfa6",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "natural_worlds":len(worlds),
        "matched_isomer_forks":len(forks),
        "summary":score,
        "worlds":worlds,
        "forks":forks,
        "original_M6_physics_unchanged":True,
        "no_heredity_claim":True
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M69_ISOMER_SUMMARY="+json.dumps({
        "worlds":len(worlds),"pairs":len(forks),"summary":score
    },sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    run()
