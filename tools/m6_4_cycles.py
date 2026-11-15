"""M6.4: spontaneous cycle survey and EXACT species-labelled cycle signatures.

Protocol 7c34fc0 committed before this observer. Original ALife physical
laws unchanged; no seeded template, no genome, no artificial replicator.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

from alife.config import Config
from alife.structures import components, signature
from alife.world import World

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"campaigns/m6_4_cycles/protocol.json"
OUTPUT=ROOT/"campaigns/m6_4_cycles/results.json"
M6=ROOT/"campaigns/m6/configs/unfed-6101.json"


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m6-4-spontaneous-cycles-exact-observer-v1"
    assert p["status"]=="frozen-before-analytical-code-and-new-results"
    assert p["world"]["seeds"]==list(range(8601,8613))
    assert p["world"]["expected_runs"]==24
    assert p["world"]["steps"]==600
    return p


def create_natural(seed:int,density:str,p:dict)->World:
    cfg=json.loads(M6.read_text(encoding="utf-8"))
    cfg["seed"]=seed
    cfg["grid"]=p["world"]["grid"]
    counts=p["world"]["densities"][density]
    for spec in cfg["species"]:
        spec["count"]=counts[spec["name"]]
    world=World.create(Config.from_dict(cfg).validate())
    assert not world.store.bonds,"natural start must have zero bonds"
    return world


def exact_cycle_key(store,indices,bonds,species_names):
    """Canonical decorated simple cycle modulo rotation and reversal.

    Works ONLY for a connected 2-regular graph (simple ring). Unlike
    the legacy WL fingerprint, equality here is exact isomorphism.
    """
    if len(indices)<4 or len(bonds)!=len(indices):
        raise ValueError("not a cycle")
    neighbors={i:[] for i in indices}
    for a,b in bonds:
        neighbors[a].append(b)
        neighbors[b].append(a)
    if any(len(neighbors[i])!=2 for i in indices):
        raise ValueError("not two-regular")
    start=min(indices)
    order=[start]
    previous=start
    current=min(neighbors[start])
    while current!=start:
        if current in order or len(order)>len(indices):
            raise ValueError("not a simple cycle")
        order.append(current)
        following=[i for i in neighbors[current] if i!=previous]
        if len(following)!=1:
            raise ValueError("branching cycle")
        previous,current=current,following[0]
    if len(order)!=len(indices):
        raise ValueError("disconnected")
    names=tuple(species_names[store.species[i]] for i in order)
    reverse=names[::-1]
    n=len(names)
    canonical=min([names[i:]+names[:i] for i in range(n)]+
                  [reverse[i:]+reverse[:i] for i in range(n)])
    return "C:"+",".join(canonical)


def analyze_cycle(store,indices,bonds,species_names):
    if len(bonds)!=len(indices) or len(indices)<4:
        return None
    if any(store.degree[i]!=2 for i in indices):
        return None
    key=exact_cycle_key(store,indices,bonds,species_names)
    old=signature(store,indices,bonds,species_names)
    assert old.exact is False
    edges=frozenset(
        tuple(sorted((store.ids[a],store.ids[b]))) for a,b in bonds)
    ids=tuple(sorted(store.ids[i] for i in indices))
    return {
        "ids":ids,"edges":edges,
        "exact":key,"wl":old.key,"size":len(indices),
        "composition":dict(old.composition),
    }


def analyze_chain4(store,indices,bonds,species_names):
    if len(indices)!=4 or len(bonds)!=3:
        return None
    degrees=sorted(store.degree[i] for i in indices)
    if degrees!=[1,1,2,2]:
        return None
    ids=tuple(sorted(store.ids[i] for i in indices))
    edges=frozenset(tuple(sorted((store.ids[a],store.ids[b]))) for a,b in bonds)
    sig=signature(store,indices,bonds,species_names)
    assert sig.exact
    return {"ids":ids,"edges":edges,"size":4,"exact":sig.key}


class BreakRecorder:
    def __init__(self):
        self.pending=[]
    def emit(self,event):
        if event.kind=="break":
            self.pending.append((event.step+1,tuple(sorted((event.id_a,event.id_b)))))
    def pop(self,tick):
        broken=set(pair for t,pair in self.pending if t==tick)
        self.pending=[entry for entry in self.pending if entry[0]!=tick]
        return broken


def study_world(world,steps=600):
    world.check()
    assert world.step==0 and not world.store.bonds
    initial_hash=world.state_hash_full()
    initial_rng=world.rng.fingerprint()
    initial_draws=world.rng.draws
    current_rings={}
    current_chains={}
    recorded=[]
    chains=[]
    occurrence=Counter()
    new_ring_size=Counter()
    material_ring_sets=set()
    all_exact_by_wl=defaultdict(set)
    direct_chain_closures=0
    episode_serial=0
    sink=BreakRecorder()
    world.event_sink=sink

    def finish(target,holder,tick,reason,output):
        episode=holder.pop(target)
        duration=tick-episode["born"]
        assert duration>=1,(target,tick,episode)
        output.append({
            "birth_tick":episode["born"],"duration_ticks":duration,
            "ended_by":reason,"censored":False,
            "material_ids":list(target),"signature":episode["exact"],
            **({"wl_fingerprint":episode["wl"],"size":episode["size"],
                "from_previous_chain4":episode["from_chain4"]}
               if "wl" in episode else {"size":4}),
        })

    def observer(w):
        nonlocal direct_chain_closures,episode_serial
        before=w.rng.draws
        broken=sink.pop(w.step)
        rings_now={}
        chains_now={}
        for indices,bonds in components(w.store):
            ring=analyze_cycle(w.store,indices,bonds,w.species_names)
            if ring:
                assert ring["size"]%2==0,"odd ring on even periodic von Neumann grid"
                rings_now[ring["ids"]]=ring
                occurrence[f"ring_size_{ring['size']}_snapshots"]+=1
                all_exact_by_wl[ring["wl"]].add(ring["exact"])
                continue
            chain=analyze_chain4(w.store,indices,bonds,w.species_names)
            if chain:
                chains_now[chain["ids"]]=chain
                occurrence["chain4_snapshots"]+=1
        old_chains=set(current_chains.keys())
        # End prior episode whenever a frozen edge breaks within this tick,
        # EVEN if it was recreated later that same tick.
        for ident,ep in list(current_rings.items()):
            new=rings_now.get(ident)
            why=("bond_break" if broken & ep["edges"] else
                 "no_longer_ring" if new is None else
                 "topology_changed" if new["edges"]!=ep["edges"] or new["exact"]!=ep["exact"]
                 else None)
            if why is not None:
                finish(ident,current_rings,w.step,why,recorded)
        for ident,ep in list(current_chains.items()):
            new=chains_now.get(ident)
            why=("bond_break" if broken & ep["edges"] else
                 "no_longer_chain" if new is None else
                 "topology_changed" if new["edges"]!=ep["edges"] or new["exact"]!=ep["exact"]
                 else None)
            if why is not None:
                finish(ident,current_chains,w.step,why,chains)

        for ident,ring in rings_now.items():
            if ident not in current_rings:
                episode_serial+=1
                from_chain=(ring["size"]==4 and ident in old_chains)
                if from_chain: direct_chain_closures+=1
                current_rings[ident]={
                    **ring,"born":w.step,
                    "from_chain4":from_chain,"episode_id":episode_serial,
                }
                material_ring_sets.add(ident)
                new_ring_size[str(ring["size"])]+=1
        for ident,chain in chains_now.items():
            if ident not in current_chains:
                current_chains[ident]={**chain,"born":w.step}
        assert before==w.rng.draws,"observer drew random values"

    for _ in range(steps):
        world.advance(1,observer=observer)
    world.event_sink=None
    world.check()
    for ident,ep in current_rings.items():
        recorded.append({
            "birth_tick":ep["born"],"duration_ticks":steps+1-ep["born"],
            "ended_by":"right_censored","censored":True,
            "material_ids":list(ident),"signature":ep["exact"],
            "wl_fingerprint":ep["wl"],"size":ep["size"],
            "from_previous_chain4":ep["from_chain4"],
        })
    for ident,ep in current_chains.items():
        chains.append({
            "birth_tick":ep["born"],"duration_ticks":steps+1-ep["born"],
            "ended_by":"right_censored","censored":True,
            "material_ids":list(ident),"signature":ep["exact"],"size":4,
        })
    alias={
        fuzzy:sorted(exacts) for fuzzy,exacts in all_exact_by_wl.items()
        if len(exacts)>1
    }
    assert world.step==steps
    return {
        "seed":world.config.seed,
        "total_ring_episodes":len(recorded),
        "total_chain4_episodes":len(chains),
        "four_ring_episodes":sum(r["size"]==4 for r in recorded),
        "rings_from_prev_chain4":direct_chain_closures,
        "ring_material_sets_distinct":len(material_ring_sets),
        "ring_sizes_episode_counts":dict(sorted(new_ring_size.items())),
        "distinct_exact_rings":len(set(r["signature"] for r in recorded)),
        "distinct_legacy_WL_rings":len(set(r["wl_fingerprint"] for r in recorded)),
        "observed_legacy_aliases":alias,
        "ring4_long_50":sum(r["size"]==4 and r["duration_ticks"]>=50 for r in recorded),
        "chain4_long_50":sum(r["duration_ticks"]>=50 for r in chains),
        "ring_episodes":recorded,
        "chain4_episode_lengths":[{"born":r["birth_tick"],
                                   "duration":r["duration_ticks"],
                                   "censored":r["censored"],
                                   "reason":r["ended_by"]}
                                  for r in chains],
        "ring4_snapshot_total":occurrence.get("ring_size_4_snapshots",0),
        "chain4_snapshot_total":occurrence["chain4_snapshots"],
        "first_hash":initial_hash,
        "final_hash":world.state_hash_full(),
        "initial_rng_fingerprint":initial_rng,
        "final_rng_fingerprint":world.rng.fingerprint(),
        "initial_rng_draws":initial_draws,
        "final_rng_draws":world.rng.draws,
        "formations":world.bonds_formed_total,
        "breaks":world.bonds_broken_total,
        "dissipated":world.dissipated,
        "energy_final":world.energy(),
    }


def summary(rows):
    densities={}
    global_alias=defaultdict(set)
    for den in ("baseline","enriched"):
        part=[r for r in rows if r["density"]==den]
        assert len(part)==12
        re=sum(r["total_ring_episodes"] for r in part)
        ri=sum(r["four_ring_episodes"] for r in part)
        ch=sum(r["total_chain4_episodes"] for r in part)
        ring4_times=[r["duration_ticks"] for row in part
                     for r in row["ring_episodes"] if r["size"]==4]
        chain4_times=[r["duration"] for row in part
                      for r in row["chain4_episode_lengths"]]
        alias=defaultdict(set)
        for row in part:
            for fp,variants in row["observed_legacy_aliases"].items():
                alias[fp].update(variants)
            for ep in row["ring_episodes"]:
                global_alias[ep["wl_fingerprint"]].add(ep["signature"])
        densities[den]={
            "universes":len(part),
            "universes_with_natural_rings":sum(r["total_ring_episodes"]>0 for r in part),
            "all_ring_episodes":re,
            "four_ring_episodes":ri,
            "four_chain_episodes":ch,
            "distinct_ring_material_sets":sum(r["ring_material_sets_distinct"] for r in part),
            "direct_chain4_to_ring4_closures":sum(r["rings_from_prev_chain4"] for r in part),
            "four_ring_episodes_duration_at_least_50":sum(t>=50 for t in ring4_times),
            "four_chain_episodes_duration_at_least_50":sum(t>=50 for t in chain4_times),
            "mean_four_ring_episode_ticks":round(sum(ring4_times)/len(ring4_times),3) if ring4_times else None,
            "mean_four_chain_episode_ticks":round(sum(chain4_times)/len(chain4_times),3) if chain4_times else None,
            "legacy_WL_alias_within_worlds":{k:sorted(v) for k,v in alias.items()},
        }
    colliding={key:sorted(val) for key,val in global_alias.items() if len(val)>1}
    return {
        "by_density":densities,
        "cross_world_fingerprint_collisions":colliding,
        "observed_natural_signature_aliasing":bool(colliding),
        "observed_long_lived_four_ring":any(
            r["size"]==4 and r["duration_ticks"]>=50
            for row in rows for r in row["ring_episodes"]
        )
    }


def run():
    p=protocol()
    rows=[]
    for density in p["world"]["densities"]:
        for seed in p["world"]["seeds"]:
            w=create_natural(seed,density,p)
            row=study_world(w,steps=p["world"]["steps"])
            row["density"]=density
            rows.append(row)
            print(f"{density}/{seed}: {row['four_ring_episodes']} natural four-ring episodes",flush=True)
    assert len(rows)==p["world"]["expected_runs"]
    checks=[]
    for density,seed in p["integrity"]["replay_fixed"]:
        hist=next(row for row in rows if row["density"]==density and row["seed"]==seed)
        w=create_natural(seed,density,p)
        w.advance(p["world"]["steps"])
        w.check()
        assert hist["final_hash"]==w.state_hash_full()
        assert hist["final_rng_fingerprint"]==w.rng.fingerprint()
        assert hist["final_rng_draws"]==w.rng.draws
        assert hist["formations"]==w.bonds_formed_total
        assert hist["breaks"]==w.bonds_broken_total
        assert hist["dissipated"]==w.dissipated
        assert hist["energy_final"]==w.energy()
        checks.append({"density":density,"seed":seed,"final_hash":hist["final_hash"]})
    record={
        "protocol_commit":"7c34fc0b41f67b48a08ef60fdb480b15da039dd3",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "schema":p["schema"],
        "n_runs":len(rows),
        "summary":summary(rows),
        "tests":"Synthetic ring-4 exact-signature alias is tested in pytest",
        "worlds":rows,
        "replay_checks":checks,
        "law_changes":False,
        "replication_claim":False,
        "epistemic_status":"natural rings and exact cyclic observability, NOT reproduction",
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print("M64_CYCLE_SUMMARY="+json.dumps({
        "n_runs":record["n_runs"],"summary":record["summary"],
        "replays":record["replay_checks"]
    },sort_keys=True),flush=True)
    return record


if __name__=="__main__":
    run()
