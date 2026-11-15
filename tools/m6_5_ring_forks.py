"""M6.5: preregistered paired forks at NATURALLY formed 4-rings.

The intervention changes a *cloned initial state*, NOT any law. Opening a
bond releases only stored bond energy to its endpoints (dissipation retained).
No life, replication, genotype or statistically independent fork claim.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife.particles import ParticleStore
from alife.rng import RNG
from alife.structures import components, signature_v2
from alife.world import World
from tools.m6_4_cycles import create_natural, protocol as source_protocol

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "campaigns/m6_5_ring_forks/protocol.json"
OUT = ROOT / "campaigns/m6_5_ring_forks/results.json"


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-5-ring-opening-forks-v1"
    assert p["status"]=="frozen-before-implementation-and-results"
    assert p["sampling"]["seeds"]==list(range(8801,8813))
    assert p["sampling"]["followup_steps"]==120
    assert p["decision"]["min_selected_pairs"]==20
    return p


def clone_world(src: World) -> World:
    """Exact in-memory replay from a complete existing world state."""
    s=src.store
    bonds=[
        (s.ids[a],s.ids[b],stored)
        for (a,b),stored in sorted(s.bonds.items())
    ]
    store=ParticleStore(
        s.width,s.height,list(s.ids),list(s.xs),list(s.ys),
        list(s.species),list(s.energy),bonds,
    )
    rand=RNG(src.config.seed)
    rand.set_state(src.rng.state())
    rand.draws=src.rng.draws
    copy=World(
        src.config,rand,store,step=src.step,moves_total=src.moves_total,
        next_id=src.next_id,bonds_formed_total=src.bonds_formed_total,
        bonds_broken_total=src.bonds_broken_total,
        injected=src.injected,dissipated=src.dissipated,
        unabsorbed=src.unabsorbed,source_acc=list(src.source_acc),
        source_store=list(src.source_store),
    )
    copy.check()
    assert src.state_hash_full()==copy.state_hash_full()
    assert src.rng.fingerprint()==copy.rng.fingerprint()
    assert src.rng.draws==copy.rng.draws
    return copy


def ring4_candidates(world):
    result=[]
    s=world.store
    for indices,bonds in components(s):
        if len(indices)!=4 or len(bonds)!=4:
            continue
        if any(s.degree[i]!=2 for i in indices):
            continue
        sig=signature_v2(s,indices,bonds,world.species_names)
        if not sig.exact or not sig.key.startswith("C2:"):
            continue
        ids=tuple(sorted(s.ids[i] for i in indices))
        edges=tuple(sorted(
            tuple(sorted((s.ids[a],s.ids[b]))) for a,b in bonds
        ))
        result.append({"ids":ids,"edges":edges,"sig":sig.key})
    return sorted(result,key=lambda x:x["ids"])


def opening_edges(ring):
    lower=ring["edges"][0]
    opposites=[
        pair for pair in ring["edges"]
        if set(pair).isdisjoint(lower)
    ]
    assert len(opposites)==1
    return lower,opposites[0]


def open_bond(w,edge):
    """Physical state perturbation, NEVER a change to the bond break rule."""
    a_id,b_id=edge
    a=w.store.index_of(a_id)
    b=w.store.index_of(b_id)
    before_energy=w.energy()
    stored=w.store.remove_bond(a,b)
    w.store.energy[a]+=stored//2
    w.store.energy[b]+=stored-(stored//2)
    w.check()
    assert w.energy()==before_energy
    return stored


def status(w,ids):
    s=w.store
    target=set(ids)
    owner={}
    for indices,bonds in components(s):
        members={s.ids[i] for i in indices}
        for id_ in members & target:
            owner[id_]=members
    connected=len(owner)==len(ids) and all(owner.get(i)==owner.get(ids[0]) for i in ids)
    isolated=connected and owner[ids[0]]==target
    external=any((members-target) for members in owner.values())
    if isolated:
        groups=components(s)
        for indices,bonds in groups:
            members={s.ids[i] for i in indices}
            if members==target:
                ring=(len(indices)==4 and len(bonds)==4 and
                      all(s.degree[i]==2 for i in indices))
                return {"isolated":True,"ring":ring,"external":False,
                        "fragmented":False}
    return {"isolated":False,"ring":False,"external":bool(external),
            "fragmented":not connected}


def followup(w,ids,horizon):
    beginning=w.step
    assert status(w,ids)["isolated"]
    first_loss=None
    first_loss_reason=None
    first_recovered=None
    first_ring=None
    isolated_ticks=0
    ring_ticks=0
    ever_lost=False
    start_energy=w.energy()
    start_hash=w.state_hash_full()
    start_rng=w.rng.fingerprint()
    start_draws=w.rng.draws
    observations=[]
    def observe(w):
        nonlocal first_loss,first_loss_reason,first_recovered,first_ring
        nonlocal isolated_ticks,ring_ticks,ever_lost
        draws=w.rng.draws
        state=status(w,ids)
        if state["isolated"]:
            isolated_ticks+=1
            if ever_lost and first_recovered is None:
                first_recovered=w.step-beginning
        elif first_loss is None:
            first_loss=w.step-beginning
            first_loss_reason=("mixed" if state["external"] and state["fragmented"]
                               else "attachment" if state["external"]
                               else "fragmentation")
            ever_lost=True
        if state["ring"]:
            ring_ticks+=1
            if first_ring is None:
                first_ring=w.step-beginning
        if w.step-beginning in (1,10,50,120):
            observations.append({
                "step_since_fork":w.step-beginning,
                **state,
            })
        assert w.rng.draws==draws
    for _ in range(horizon):
        w.advance(1,observer=observe)
    w.check()
    final=status(w,ids)
    assert w.energy()<=w.configured_energy()+w.injected
    return {
        "final_isolated":final["isolated"],
        "final_ring":final["ring"],
        "isolated_ticks":isolated_ticks,
        "ring_ticks":ring_ticks,
        "first_loss_tick":first_loss,
        "first_loss_reason":first_loss_reason,
        "first_recovered_tick":first_recovered,
        "first_ring_observed_tick":first_ring,
        "initial_energy":start_energy,
        "final_energy":w.energy(),
        "final_dissipated":w.dissipated,
        "initial_hash":start_hash,
        "final_hash":w.state_hash_full(),
        "initial_rng_fingerprint":start_rng,
        "initial_rng_draws":start_draws,
        "final_rng_fingerprint":w.rng.fingerprint(),
        "final_rng_draws":w.rng.draws,
        "final_formed":w.bonds_formed_total,
        "final_broken":w.bonds_broken_total,
        "snapshots":observations,
    }


def paired_experiment(src,ring,p,sham_check=False):
    assert status(src,ring["ids"])=={
        "isolated":True,"ring":True,"external":False,"fragmented":False
    }
    before_hash=src.state_hash_full()
    before_rng=src.rng.fingerprint()
    begin_energy=src.energy()
    low,opp=opening_edges(ring)
    arms={}
    baseline=None
    for label in p["sampling"]["arms"]:
        fork=clone_world(src)
        assert fork.state_hash_full()==before_hash
        assert fork.rng.fingerprint()==before_rng
        if label=="open_lowest_edge":
            saved=open_bond(fork,low)
        elif label=="open_opposite_edge":
            saved=open_bond(fork,opp)
        else:
            saved=0
        assert fork.energy()==begin_energy
        assert fork.rng.fingerprint()==before_rng
        assert (len(ring4_candidates(fork))>=1)==(label=="keep_ring") if label=="keep_ring" else True
        if label!="keep_ring":
            assert status(fork,ring["ids"])["isolated"]
            assert not status(fork,ring["ids"])["ring"]
        result=followup(fork,ring["ids"],p["sampling"]["followup_steps"])
        result["bond_stored_energy_redistributed"]=saved
        arms[label]=result
        if label=="keep_ring":
            baseline=result
    if sham_check:
        sham=clone_world(src)
        comparison=followup(sham,ring["ids"],p["sampling"]["followup_steps"])
        assert comparison=={
            k:v for k,v in baseline.items()
            if k!="bond_stored_energy_redistributed"
        }, "Untouched sham diverged from untouched control"
    assert src.state_hash_full()==before_hash
    return {"ring":ring,"fork_world_step":src.step,"arms":arms}


def sample_density(density,p):
    source=source_protocol()
    worlds=[]
    selected=[]
    for seed in p["sampling"]["seeds"]:
        w=create_natural(seed,density,source)
        seen=set()
        forks=[]
        for _ in range(p["sampling"]["precursor_max_tick"]):
            w.advance(1)
            for ring in ring4_candidates(w):
                if ring["ids"] in seen:
                    continue
                seen.add(ring["ids"])
                data=paired_experiment(
                    w,ring,p,sham_check=(seed==p["sampling"]["seeds"][0] and len(forks)==0)
                )
                data["density"]=density
                data["precursor_seed"]=seed
                forks.append(data)
                selected.append(data)
                if len(forks)>=2  # frozen protocol: first two distinct material sets per world:
                    break
            if len(forks)>=2  # frozen protocol: first two distinct material sets per world:
                break
        worlds.append({
            "density":density,"seed":seed,
            "selected_pairs":len(forks),
            "selection_stop_tick":w.step,
            "parent_world_hash_at_stop":w.state_hash_full(),
        })
        print(f"{density}/{seed}: selected {len(forks)} natural ring forks",flush=True)
    return worlds,selected


def summary(forks,p):
    by_den={}
    for den in p["sampling"]["densities"]:
        group=[x for x in forks if x["density"]==den]
        rates={}
        for arm in p["sampling"]["arms"]:
            rows=[x["arms"][arm] for x in group]
            rates[arm]={
                "forks":len(rows),
                "isolated_at_horizon":sum(x["final_isolated"] for x in rows),
                "ring_at_horizon":sum(x["final_ring"] for x in rows),
                "isolated_tick_mean":round(sum(x["isolated_ticks"] for x in rows)/len(rows),3)
                  if rows else None,
                "first_loss_observed":sum(x["first_loss_tick"] is not None for x in rows),
                "first_loss_attachments":sum(x["first_loss_reason"]=="attachment" for x in rows),
                "ring_ever_observed_post_fork":sum(x["first_ring_observed_tick"] is not None
                                                   for x in rows),
            }
        keep=rates["keep_ring"]["isolated_at_horizon"]
        lowest=rates["open_lowest_edge"]["isolated_at_horizon"]
        opposite=rates["open_opposite_edge"]["isolated_at_horizon"]
        n=len(group)
        by_den[den]={
            "selected_pairs":n,
            "branches":rates,
            "paired_isolation_contrast_lowest":round((keep-lowest)/n,4) if n else None,
            "paired_isolation_contrast_opposite":round((keep-opposite)/n,4) if n else None,
            "discordant_keep_only_lowest":sum(
                x["arms"]["keep_ring"]["final_isolated"] and
                not x["arms"]["open_lowest_edge"]["final_isolated"] for x in group),
            "discordant_open_only_lowest":sum(
                x["arms"]["open_lowest_edge"]["final_isolated"] and
                not x["arms"]["keep_ring"]["final_isolated"] for x in group),
        }
    good=(len(forks)>=p["decision"]["min_selected_pairs"] and
          all(by_den[d]["paired_isolation_contrast_lowest"] is not None and
              by_den[d]["paired_isolation_contrast_lowest"]>=.2 and
              by_den[d]["paired_isolation_contrast_opposite"] is not None and
              by_den[d]["paired_isolation_contrast_opposite"]>0
              for d in p["sampling"]["densities"]))
    verdict=("ring_closure_protection_signal" if good
             else "underpowered" if len(forks)<p["decision"]["min_selected_pairs"]
             else "no_robust_ring_closure_protection")
    return {"by_density":by_den,"gate_passed":good,"verdict":verdict}


def run():
    p=protocol()
    universes=[]
    forks=[]
    for density in p["sampling"]["densities"]:
        records,selected=sample_density(density,p)
        universes.extend(records)
        forks.extend(selected)
    result={
        "schema":p["schema"],
        "protocol_commit":"f66973fd7b456dff87c104474cfb471245dc6257",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "num_natural_worlds":len(universes),
        "num_paired_forks":len(forks),
        "summary":summary(forks,p),
        "source_worlds":universes,
        "paired_forks":forks,
        "causal_scope":"effect of combined specified bond opening and stored-energy redistribution on same fork world",
        "no_replication_claim":True,
        "laws_unchanged":True,
    }
    assert len(universes)==24
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M65_FORK_SUMMARY="+json.dumps({
        "n_worlds":len(universes),"n_forks":len(forks),
        "summary":result["summary"]
    },sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    run()
