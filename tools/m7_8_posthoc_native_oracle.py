"""Posthoc M7.8 correctness audit using the ORIGINAL native M6 form_bonds.

Recreate ALL 640 original native source microstates from physical seeds.
For EACH outcome-informative source (nonzero bond-only/sham eligible or real
coupled-formation contrast), plus first source of each fixed shard, replay
all 32 pair-coupled chemical lotteries across ALL FOUR arms via untouched
native chemistry.form_bonds. The sole experimental alteration is a
temporary pair-keyed raw() oracle and candidate iterator wrapper for
supplying the preregistered exogenous draw to the ORIGINAL function.
Restore both objects immediately. No world advance, no sources/decay/break.

This is a POSTHOC verification of the SAME experiment, NOT new samples.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from alife import chemistry
from tools.m6_5_ring_forks import clone_world
from tools.m7_2_energy_distribution import contacts, ledger
from tools.m7_3_bond_energy import energy_transfer
from tools import m7_5_mature_feedback as parent_selection

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_8_frozen"
PRIMARY=BASE/"results.json"
OUT=BASE/"posthoc_original_native_form_bonds_oracle.json"
ARMS=("sham","bond_only","all_contacts","unbonded_budget_matched")


def independent_pair_draw(seed,salt,ia,ib):
    a,b=sorted((ia,ib))
    message=f"alife-m7-8|{seed}|{salt}|{a}|{b}".encode("ascii")
    return int.from_bytes(sha256(message).digest()[:8],"big")


def independent_unbonded_budget(w,budget):
    store=w.store
    bond_set=set(store.bonds)
    snapshot=tuple(store.energy)
    remaining=list(snapshot)
    deltas=[0]*len(snapshot)
    count=0
    for a,b in contacts(store):
        if count>=budget:break
        if (a,b) in bond_set or (b,a) in bond_set:continue
        if snapshot[a]-snapshot[b]>=2:donor,recipient=a,b
        elif snapshot[b]-snapshot[a]>=2:donor,recipient=b,a
        else:continue
        if remaining[donor]<1:continue
        remaining[donor]-=1
        deltas[donor]-=1
        deltas[recipient]+=1
        count+=1
    for index,value in enumerate(deltas):
        store.energy[index]+=value
        assert store.energy[index]>=0
    assert sum(snapshot)==sum(store.energy)
    return count


def native_m6_original_form_bonds_with_coupled_oracle(w,seed,salt):
    """Original M6 chemistry.form_bonds; only exogenous per-pair RNG oracle."""
    original_rng=w.rng
    original_candidates=chemistry._candidate_pairs

    class PairOracle:
        current=None
        calls=0
        def raw(self):
            assert self.current is not None
            self.calls+=1
            return independent_pair_draw(seed,salt,*self.current)

    oracle=PairOracle()
    def wrapped_candidates(world):
        for a,b in original_candidates(world):
            oracle.current=(world.store.ids[a],world.store.ids[b])
            yield a,b

    chemistry._candidate_pairs=wrapped_candidates
    w.rng=oracle
    try:
        native=chemistry.form_bonds(w)
    finally:
        w.rng=original_rng
        chemistry._candidate_pairs=original_candidates
    ledger(w,w.configured_energy())
    w.check()
    assert w.rng is original_rng
    return native,oracle.calls


def arm_state(parent,arm,budget):
    w=clone_world(parent)
    if arm=="bond_only":
        count=energy_transfer(w,"bond_only")[0]
    elif arm=="all_contacts":
        count=energy_transfer(w,"all_contacts")[0]
    elif arm=="unbonded_budget_matched":
        count=independent_unbonded_budget(w,budget)
    elif arm=="sham":
        count=0
    else:raise ValueError(arm)
    ledger(w,w.configured_energy())
    w.check()
    return w,count


def compare_original_case(row,parent):
    root=set(row["source"]["ids"])
    budget=row["bond_only_transfer_budget"]
    total=0
    for arm in ARMS:
        state,count=arm_state(parent,arm,budget)
        original=row["arms"][arm]
        assert original["after_one_transfer_full_hash"]==state.state_hash_full(),(
            row["seed"],arm,"one-pass material mismatch")
        assert original["transfer"]["transfer_events"]==count
        assert original["original_source_energy_after"]==sum(
            state.store.energy[state.store.index_of(i)] for i in root)
        for salt in range(32):
            world=clone_world(state)
            native,draws=native_m6_original_form_bonds_with_coupled_oracle(world,row["seed"],salt)
            expected=original["lotteries"][salt]
            pairs=[(min(event.id_a,event.id_b),max(event.id_a,event.id_b)) for event in native]
            boundary=[p for p in pairs if (p[0] in root)!=(p[1] in root)]
            assert draws==expected["native_pairs_attempted"],(
                row["seed"],arm,salt,"candidate draw mismatch")
            assert [list(p) for p in pairs]==expected["formed_all_pair_ids"],(
                row["seed"],arm,salt,"formed pairs differ")
            assert [list(p) for p in boundary]==expected["original_to_external_bonds"],(
                row["seed"],arm,salt,"source incident pairs differ")
            assert world.state_hash_full()==expected["after_one_formation_sweep_full_hash"],(
                row["seed"],arm,salt,"state hash mismatch")
            assert world.rng.fingerprint()==parent.rng.fingerprint()
            assert world.rng.draws==parent.rng.draws
            total+=1
    return total


def main():
    data=json.loads(PRIMARY.read_text(encoding="utf-8"))
    assert data["schema"]=="alife-m7-8-full-640-frozen-source-reaction-causality-v1"
    rows=data["source_worlds"]
    assert len(rows)==640 and [x["seed"] for x in rows]==list(range(26001,26641))
    assert all(x["selected"] for x in rows)
    informative={
        r["seed"] for r in rows
        if (r["arms"]["bond_only"]["boundary_eligibility_change_vs_sham"]!=0
            or (r["arms"]["bond_only"]["total_external_formed_across_32_lotteries"] !=
                r["arms"]["sham"]["total_external_formed_across_32_lotteries"]))
    }
    replaylist=set(data["first_source_replays_per_nonempty_shard"])
    assert len(replaylist)==16
    informative|=replaylist
    old=parent_selection.protocol()
    checked=0
    output=[]
    for idx,row in enumerate(rows):
        w,found,_=parent_selection.select_parent(row["seed"],old)
        assert w.state_hash_full()==row["source_parent_hash"],(row["seed"],"parent hash")
        assert w.rng.fingerprint()==row["source_rng"]
        assert w.rng.draws==row["source_rng_draws"]
        assert found["ids"]==row["source"]["ids"]
        assert found["edges"]==row["source"]["edges"]
        if row["seed"] in informative:
            lotteries=compare_original_case(row,w)
            output.append({"seed":row["seed"],"native_form_bonds_oracle_lotteries_checked":lotteries})
            checked+=lotteries
        if (idx+1)%80==0:
            print(f"M78_POSTHOC_PROGRESS parent={idx+1}/640 chemistry_lotteries={checked}",flush=True)
    assert len(informative)==len(output)
    assert checked==len(informative)*4*32
    s=data["summary"]["paired_mechanism"]
    assert s["native_new_external_energetic_pair_activation"]["favor_bond_only"]==26
    assert s["native_new_external_energetic_pair_activation"]["favor_sham"]==6
    assert s["coupled_actual_external_formation_count_32_per_seed"]["favor_bond_only"]==25
    assert s["coupled_actual_external_formation_count_32_per_seed"]["favor_sham"]==5
    result={
        "schema":"alife-m7-8-original-M6-native-form_bonds-posthoc-audit-v1",
        "all_640_native_source_worlds_recreated_from_seed":True,
        "informative_and_shard_sentinel_seed_count":len(informative),
        "all_32_lotteries_and_four_arms_native_oracle_verified_for_informative_seeds":True,
        "native_M6_form_bonds_reaction_sweeps_verified":checked,
        "untouched_native_M6_chemistry_original_candidates_and_rng_restored":True,
        "not_new_independent_seeds_and_preregistered_verdict_unchanged":True,
        "checked_seeds":output
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M78_POSTHOC_FINAL="+json.dumps({
        "all_sources_rebuilt":640,
        "informative_worlds_checked":len(informative),
        "four_arm_salt_lotteries_verified":checked,"passed":True
    },sort_keys=True),flush=True)


if __name__=="__main__":
    main()
