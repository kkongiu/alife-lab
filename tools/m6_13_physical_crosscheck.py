"""Post-hoc, independent physical-state audit of M6.13 positives.

Not a preregistered scientific test or a replacement for the fixed M6.13 gate.
Runs original M6 physics but intentionally does NOT use the M6.12 precursor
observer, M6.13 episode tracker or M6.13 summary decisions. Confirms the
material geometry and original seven bonds tick by tick for the positive cases.
"""
from __future__ import annotations

import json
from pathlib import Path

from tools.m6_4_cycles import create_natural, protocol as natural_protocol, BreakRecorder

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"campaigns/m6_13_replication/posthoc_crosscheck.json"
OFFSETS=((-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0))
CASES=(
    {"seed":12199,"start":217,"duration":51,"center":(22,8),"resident":260,
     "ids":(9,24,39,56,81,112,138,172),
     "edges":((9,56),(9,138),(24,39),(24,56),(39,172),(81,112),(112,172)),
     "closure":220},
    {"seed":12229,"start":24,"duration":105,"center":(1,8),"resident":254,
     "ids":(29,35,39,82,87,143,147,191),
     "edges":((29,39),(29,147),(35,39),(35,143),(82,87),(87,143),(147,191)),
     "closure":74},
    {"seed":12321,"start":344,"duration":160,"center":(14,11),"resident":253,
     "ids":(8,25,27,33,99,110,133,144),
     "edges":((8,110),(8,133),(25,33),(25,99),(27,33),(99,133),(110,144)),
     "closure":362}
)


def bonds_by_material(s):
    return {tuple(sorted((s.ids[a],s.ids[b]))) for a,b in s.bonds}


def perimeter_ids(s, center):
    x,y=center
    indices=[s.grid[((y+dy)%s.height)*s.width+((x+dx)%s.width)] for dx,dy in OFFSETS]
    assert -1 not in indices, "unsealed physical perimeter"
    return tuple(s.ids[i] for i in indices)


def inspect_case(case):
    natural=natural_protocol()
    w=create_natural(case["seed"],"enriched",natural)
    recorded=BreakRecorder()
    w.event_sink=recorded
    original=frozenset(tuple(sorted(pair)) for pair in case["edges"])
    assert len(original)==7
    center=case["center"]
    resident=case["resident"]
    start=case["start"]
    stop=start+case["duration"]
    original_pos=None
    missing=None
    first_close=None
    observed=0
    break_at_expected=None

    def inspect(world):
        nonlocal original_pos, missing, first_close, observed, break_at_expected
        t=world.step
        broken=recorded.pop(t)
        if t<start:
            return
        s=world.store
        if t==stop:
            break_at_expected=sorted(broken.intersection(original))
            assert break_at_expected, (case["seed"],"no original edge break at claimed stop",stop)
            return
        if t>stop:
            return
        # Exact matching to fixed-world original identities at EVERY tick.
        b=bonds_by_material(s)
        assert original.issubset(b), (case["seed"],t,"original bond missing")
        if t>start:
            assert not broken.intersection(original),(
                case["seed"],t,"transient original bond break in episode"
            )
        ordered=perimeter_ids(s,center)
        assert set(ordered)==set(case["ids"]),(case["seed"],t,ordered)
        here={i:(s.xs[s.index_of(i)],s.ys[s.index_of(i)]) for i in case["ids"]}
        if original_pos is None:
            original_pos=here
            expected={tuple(sorted((ordered[k],ordered[(k+1)%8]))) for k in range(8)}
            assert original.issubset(expected) and len(expected)==8
            absent=expected-original
            assert len(absent)==1
            missing=next(iter(absent))
        assert here==original_pos
        cx,cy=center
        center_index=s.grid[cy*s.width+cx]
        assert center_index!=-1
        assert s.ids[center_index]==resident,(case["seed"],t,"resident changed")
        assert s.degree[center_index]==0,(case["seed"],t,"resident acquired external bond")
        assert world.config.species[s.species[center_index]].move_probability>0
        if missing in b and first_close is None:
            first_close=t
        observed+=1

    w.advance(600,observer=inspect)
    w.check()
    assert observed==case["duration"], (case["seed"],observed,case["duration"])
    assert first_close==case["closure"], (case["seed"],first_close)
    assert break_at_expected is not None
    # This is an independent world without the audit observer, not a checkpoint
    # copied from the audited world.
    bare=create_natural(case["seed"],"enriched",natural)
    bare.advance(600)
    bare.check()
    assert bare.state_hash_full()==w.state_hash_full()
    assert bare.rng.fingerprint()==w.rng.fingerprint()
    assert bare.rng.draws==w.rng.draws
    assert bare.energy()==w.energy()
    assert bare.dissipated==w.dissipated
    assert bare.bonds_formed_total==w.bonds_formed_total
    assert bare.bonds_broken_total==w.bonds_broken_total
    return {
        "seed":case["seed"],"density":"enriched",
        "resident":resident,"center":list(center),
        "start_tick":start,"last_intact_tick":stop-1,
        "original_edge_break_tick":stop,
        "duration_verified":observed,"first_eighth_edge_tick":first_close,
        "original_edges_broken_at_stop":[list(e) for e in break_at_expected],
        "physical_geometry_checks_passed":True,
        "full_hash_rng_energy_equivalence":True
    }


def main():
    results=[inspect_case(case) for case in CASES]
    output={
        "schema":"alife-m6-13-posthoc-independent-physical-audit-v1",
        "posthoc":True,
        "does_not_change_original_preregistered_gate":True,
        "same_original_M6_world_laws":True,
        "results":results
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("M613_POSTHOC_CHECK="+json.dumps(output,sort_keys=True),flush=True)
    return output


if __name__=="__main__":
    main()
