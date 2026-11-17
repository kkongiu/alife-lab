"""Posthoc independent physical audit of fixed M7.7 raw dataset.

Recreate native source worlds and 960 forks. Use original M7.3 physical
energy transfer and independently count genuine M6 event emissions and
candidate pairs. It is the SAME sample, not a new statistical replication.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
from alife.world import World
from alife.chemistry import _candidate_pairs
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import config_for, energy_transfer
from tools.m7_2_energy_distribution import ledger
from tools.m7_5_posthoc_independent_replay import IndependentEvents, source_component_size_from_scratch

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_7_mechanism"
SRC=BASE/"results.json"
DEST=BASE/"independent_posthoc.json"
ARMS=("no_transfer","bond_only","all_contacts")


def candidates(w,ids):
    s=w.store
    root=set(ids)
    return sum(
        (s.ids[a] in root)!=(s.ids[b] in root)
        and (a,b) not in s.bonds and (b,a) not in s.bonds
        for a,b in _candidate_pairs(w)
    )


def replay(row):
    assert row["selected"]
    seed=row["seed"]
    ids=tuple(row["source"]["ids"])
    original={tuple(sorted(pair)) for pair in row["source"]["edges"]}
    w=World.create(config_for(seed,"no_transfer"))
    w.advance(row["fork_tick"])
    w.check()
    assert w.state_hash_full()==row["parent_hash"]
    assert w.rng.fingerprint()==row["parent_rng"] and w.rng.draws==row["parent_rng_draws"]
    assert source_component_size_from_scratch(w,ids)==len(ids)
    present={tuple(sorted((w.store.ids[a],w.store.ids[b]))) for a,b in w.store.bonds}
    assert original.issubset(present)
    out={"seed":seed,"verified_arms":{}}
    first_breaks=[]
    for arm in ARMS:
        clone=clone_world(w)
        tape=IndependentEvents()
        clone.event_sink=tape
        first_break=None
        first_incident=None
        beforebreak=0
        allinc=0
        firststep=[]
        contact_series=[]
        for t in range(1,121):
            clone.advance(1)
            events=tape.events(clone.step)
            breaks={pair for kind,pair in events if kind=="break" and pair in original}
            formed=[pair for kind,pair in events if kind=="form" and ((pair[0] in ids)!=(pair[1] in ids))]
            if t==1:
                firststep=[list(edge) for edge in sorted(breaks)]
                first_breaks.append(tuple(map(tuple,firststep)))
            if first_break is None and breaks:
                first_break=t
            if formed and first_incident is None:
                first_incident=t
            allinc+=len(formed)
            if first_break is None:
                beforebreak+=len(formed)
            energy_transfer(clone,arm)
            contact_series.append(candidates(clone,ids))
        clone.check()
        ledger(clone,clone.configured_energy())
        size=source_component_size_from_scratch(clone,ids)
        growth=size is not None and size>len(ids)
        h=row["outcomes"][arm]
        assert contact_series==h["per_tick_opportunities"],(seed,arm,"contacts")
        assert sum(contact_series)==h["cumulative"]["energy_qualified_boundary_contacts"]
        assert h["first_original_break_tick"]==first_break
        assert h["first_external_incident_form_tick"]==first_incident
        assert h["incident_external_formation_count"]==allinc
        assert h["incident_external_formations_before_original_break"]==beforebreak
        assert h["source_incident_prebreak_binary"]==(beforebreak>0)
        assert h["first_step_original_break_pairs"]==firststep
        assert h["coherent_growth_at_120"]==growth
        assert h["all_original_edges_unbroken_120"]==(first_break is None)
        f=h["final"]
        assert f["full_hash"]==clone.state_hash_full()
        assert f["rng"]==clone.rng.fingerprint() and f["draws"]==clone.rng.draws
        assert f["stored_energy"]==clone.energy()
        assert f["injected"]==clone.injected
        assert f["dissipated"]==clone.dissipated
        assert f["unabsorbed"]==clone.unabsorbed
        assert f["global_new_bonds"]==clone.bonds_formed_total-w.bonds_formed_total
        assert f["global_broken_bonds"]==clone.bonds_broken_total-w.bonds_broken_total
        out["verified_arms"][arm]={"hash_rng_energy_exact":True,"candidate_timeline_exact":True,
            "break_and_incident_formation_exact":True,"growth":growth,"prebreak":beforebreak>0}
    assert len(set(first_breaks))==1
    return out


def main():
    raw=json.loads(SRC.read_text(encoding="utf-8"))
    assert raw["schema"]=="alife-m7-7-full-320-source-mechanistic-audit-v1"
    rows=raw["source_worlds"]
    assert len(rows)==320 and [r["seed"] for r in rows]==list(range(25001,25321))
    verified=[]
    for i,r in enumerate(rows):
        assert r["selected"]
        verified.append(replay(r))
        if (i+1)%20==0:
            print(f"M77_INDEPENDENT_PROGRESS {i+1}/320",flush=True)
    pre=Counter((r["verified_arms"]["bond_only"]["prebreak"],r["verified_arms"]["no_transfer"]["prebreak"]) for r in verified)
    grow=Counter((r["verified_arms"]["bond_only"]["growth"],r["verified_arms"]["no_transfer"]["growth"]) for r in verified)
    assert [pre[(True,False)],pre[(False,True)],pre[(True,True)],pre[(False,False)]]==[47,10,21,242]
    assert [grow[(True,False)],grow[(False,True)],grow[(True,True)],grow[(False,False)]]==[33,11,8,268]
    out={
        "schema":"alife-m7-7-fixed-sample-posthoc-independent-physical-audit-v1",
        "not_additional_independent_seeds":True,
        "original_M7_3_transport_used":True,
        "independent_native_candidate_and_break_observers":True,
        "replayed_320_sources":True,"verified_960_physical_forks":True,
        "paired_prebreak":{"bond_only_only":47,"no_transfer_only":10,"both":21,"neither":242},
        "paired_growth":{"bond_only_only":33,"no_transfer_only":11,"both":8,"neither":268},
        "results":verified
    }
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("M77_INDEPENDENT_FINAL="+json.dumps({"worlds":320,"forks":960,"passed":True,
        "prebreak_favorable_bond_only":47,"prebreak_favorable_control":10},sort_keys=True),flush=True)


if __name__=="__main__":
    main()
