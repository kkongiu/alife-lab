"""POSTHOC independent M7.5 physical replay against frozen M7.5 artifact.

Does NOT call the M7.5 cohort selector, custom energy route, follow(), or
growth classifier. Recreates the parent microstate by native World.advance,
uses original M7.3 energy_transfer, and independently follows original
break EVENTS and original source-ID connectivity. This is validation of the
same 320 seeds, NOT new independent scientific sampling.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import json

from alife.world import World
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import config_for, energy_transfer
from tools.m7_2_energy_distribution import ledger

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_5_mature"
DATA=BASE/"results.json"
OUTPUT=BASE/"posthoc_independent_replay.json"
ARMS=("no_transfer","bond_only","all_contacts")


class IndependentEvents:
    def __init__(self):
        self.lines=[]
    def emit(self,event):
        self.lines.append((event.step+1,event.kind,tuple(sorted((event.id_a,event.id_b)))))
    def events(self,tick):
        selected=[(kind,pair) for t,kind,pair in self.lines if t==tick]
        self.lines=[row for row in self.lines if row[0]!=tick]
        return selected


def source_component_size_from_scratch(w,source_ids):
    """Independent graph traversal: no M7.4 coherent_root_size call."""
    s=w.store
    adj={}
    for a,b in s.bonds:
        ia,ib=s.ids[a],s.ids[b]
        adj.setdefault(ia,set()).add(ib)
        adj.setdefault(ib,set()).add(ia)
    start=source_ids[0]
    seen={start}
    stack=[start]
    while stack:
        u=stack.pop()
        for v in adj.get(u,()):
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) if all(i in seen for i in source_ids) else None


def verify(row):
    seed=row["seed"]
    assert row["selected"]
    assert row["fork_tick"]==120,("unexpected fork tick",seed,row["fork_tick"])
    parent=World.create(config_for(seed,"no_transfer"))
    assert not parent.store.bonds
    parent.advance(row["fork_tick"])
    parent.check()
    assert parent.state_hash_full()==row["source_fork_full_hash"]
    assert parent.rng.fingerprint()==row["source_fork_rng"]
    assert parent.rng.draws==row["source_fork_draws"]
    ids=tuple(row["source"]["ids"])
    originals={tuple(sorted(pair)) for pair in row["source"]["edges"]}
    assert len(ids)>=5 and len(originals)>=4
    existing={tuple(sorted((parent.store.ids[a],parent.store.ids[b])))
              for a,b in parent.store.bonds}
    assert originals.issubset(existing)
    assert source_component_size_from_scratch(parent,ids)==len(ids)
    result={"seed":seed,"source_ids":list(ids),
            "source_size":len(ids),"parent_full_hash_matched":True,
            "arms":{}}
    first={}
    for arm in ARMS:
        world=clone_world(parent)
        sink=IndependentEvents()
        world.event_sink=sink
        first_break=None
        first_step=[]
        for t in range(1,121):
            world.advance(1)
            breaks={pair for kind,pair in sink.events(world.step)
                    if kind=="break"} & originals
            if t==1:
                first_step=[list(edge) for edge in sorted(breaks)]
            if first_break is None and breaks:
                first_break=t
            # Use M7.3 ORIGINAL already independently tested energy route
            # rather than new M7.5 flux-classifying transport.
            energy_transfer(world,arm)
        world.check()
        ledger(world,world.configured_energy())
        status=source_component_size_from_scratch(world,ids)
        growth=status is not None and status>len(ids)
        intact=first_break is None
        expected=row["outcomes"][arm]
        assert expected["coherent_growth_at_120"]==growth,(seed,arm,"growth")
        assert expected["all_original_bonds_never_broken_120"]==intact,(seed,arm,"edge")
        assert expected["first_original_bond_break_relative_tick"]==first_break,(seed,arm,"break tick")
        assert expected["first_step_original_break_pairs"]==first_step,(seed,arm,"first-step breaks")
        f=expected["final"]
        assert f["full_hash"]==world.state_hash_full(),(seed,arm,"material hash")
        assert f["rng"]==world.rng.fingerprint() and f["draws"]==world.rng.draws
        assert f["energy"]==world.energy()
        assert f["injected"]==world.injected
        assert f["unabsorbed"]==world.unabsorbed
        assert f["dissipated"]==world.dissipated
        assert f["formed"]==world.bonds_formed_total
        assert f["broken"]==world.bonds_broken_total
        first[arm]=first_step
        result["arms"][arm]={
            "growth":growth,"original_edges_unbroken":intact,
            "first_original_break_tick":first_break,
            "final_hash_matched":True,
            "rng_energy_counters_matched":True
        }
    assert first["no_transfer"]==first["bond_only"]==first["all_contacts"]
    result["first_step_original_break_invariant"]=True
    return result


def main():
    frozen=json.loads(DATA.read_text(encoding="utf-8"))
    assert frozen["schema"]=="alife-m7-5-320-native-aged-cohort-result-v1"
    assert frozen["all_320_source_seed_worlds_present"] is True
    rows=frozen["worlds"]
    assert len(rows)==320 and [x["seed"] for x in rows]==list(range(23001,23321))
    validated=[]
    for i,row in enumerate(rows):
        validated.append(verify(row))
        if (i+1)%20==0:
            print(f"M75_POSTHOC_PROGRESS verified={i+1}/320",flush=True)
    assert len(validated)==320
    tab=Counter(
        (row["arms"]["bond_only"]["growth"],row["arms"]["no_transfer"]["growth"])
        for row in validated
    )
    assert (tab[(True,False)],tab[(False,True)],tab[(True,True)],tab[(False,False)])==(41,18,10,251)
    out={
        "schema":"alife-m7-5-posthoc-independent-physical-replay-v1",
        "not_new_independent_seeds":True,
        "does_not_change_preregistered_outcomes":True,
        "physics_uses_original_M7_3_transfer_not_M7_5_route":True,
        "all_320_selected_sources_and_960_forks_replayed":True,
        "original_material_survival_and_growth_independently_classified":True,
        "320_validated_source_worlds":len(validated),
        "960_validated_forks":len(validated)*3,
        "growth_discordance":{"bond_only_only":41,"no_transfer_only":18,
                              "both":10,"neither":251},
        "results":validated
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("M75_POSTHOC_FINAL="+json.dumps({
        "replayed_sources":320,
        "replayed_forks":960,
        "growth_bond_only_only":41,
        "growth_no_transfer_only":18,
        "all_verified":True
    },sort_keys=True),flush=True)


if __name__=="__main__":
    main()
