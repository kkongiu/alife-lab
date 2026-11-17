"""POSTHOC independent M7.9 native-source and original M6 reaction oracle audit.

Checks all 640 source-world identities and native M7.3 bond conduction, plus
all 4 root-energy permutation full states. For each informative original
source (nonzero bond-only vs mean-scrambled contrast on either frozen gate),
and 16 shard sentinels, verifies all 6x32 isolated native reaction sweeps
via the ACTUAL ORIGINAL M6 chemistry.form_bonds with an injected exogenous
pair-keyed raw() oracle (not the M7.8 formation reimplementation).

NO new source seeds. NO changes to preregistered outcomes or data.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from tools import m7_5_mature_feedback as m75
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_2_energy_distribution import ledger
from tools.m7_8_posthoc_native_oracle import native_m6_original_form_bonds_with_coupled_oracle

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_9_placement"
PRIMARY=BASE/"results.json"
DEST=BASE/"posthoc_original_M6_oracle.json"
ARMS=("sham","bond_only","root_scramble_0","root_scramble_1","root_scramble_2","root_scramble_3")


def independent_scramble(state,source_ids,seed,rank):
    w=clone_world(state)
    ids=tuple(sorted(source_ids))
    energies=tuple(w.store.energy[w.store.index_of(i)] for i in ids)
    before=tuple(sorted(energies))
    root_total=sum(energies)
    original_sum=w.energy()
    outside={
        identifier:w.store.energy[w.store.index_of(identifier)]
        for identifier in w.store.ids if identifier not in ids
    }
    ranks={
        identifier:sha256(
            f"alife-m7-9|{seed}|{rank}|{identifier}".encode("ascii")
        ).digest() for identifier in ids
    }
    reordered=tuple(sorted(ids,key=lambda x:(ranks[x],x)))
    for identifier,value in zip(reordered,energies):
        w.store.energy[w.store.index_of(identifier)]=value
    reallocated=tuple(w.store.energy[w.store.index_of(i)] for i in ids)
    assert tuple(sorted(reallocated))==before
    assert sum(reallocated)==root_total and w.energy()==original_sum
    assert all(w.store.energy[w.store.index_of(i)]==value for i,value in outside.items())
    ledger(w,w.configured_energy())
    w.check()
    return w


def verify_source(row,old):
    seed=row["seed"]
    parent,candidate,_=m75.select_parent(seed,old)
    assert row["selected"] and candidate is not None
    assert parent.state_hash_full()==row["native_parent_full_hash"]
    assert parent.rng.fingerprint()==row["native_parent_rng_fingerprint"]
    assert parent.rng.draws==row["native_parent_rng_draws"]
    assert list(candidate["ids"])==row["native_source"]["ids"]
    assert [list(e) for e in candidate["edges"]]==row["native_source"]["edges"]
    ids=tuple(candidate["ids"])
    energies_pre=tuple(parent.store.energy[parent.store.index_of(i)] for i in ids)
    assert list(energies_pre)==row["original_root_energy_id_order"]
    bond=clone_world(parent)
    total=energy_transfer(bond,"bond_only")[0]
    assert total==row["bond_only_native_transfer_events"]
    assert bond.state_hash_full()==row["arms"]["bond_only"]["after_energy_intervention_full_hash"]
    assert parent.state_hash_full()==row["arms"]["sham"]["after_energy_intervention_full_hash"]
    byarm={"sham":parent,"bond_only":bond}
    old_energies=sorted(bond.store.energy[bond.store.index_of(i)] for i in ids)
    for rank in range(4):
        shuffled=independent_scramble(bond,ids,seed,rank)
        named=f"root_scramble_{rank}"
        assert shuffled.state_hash_full()==row["arms"][named]["after_energy_intervention_full_hash"],(
            seed,named,"mismatching independently reconstructed energy assignment")
        assert sorted(shuffled.store.energy[shuffled.store.index_of(i)] for i in ids)==old_energies
        byarm[named]=shuffled
    return ids,byarm


def verify_chemistry(row,ids,states):
    seed=row["seed"]
    comparisons=0
    for arm,state in states.items():
        outcome=row["arms"][arm]
        for salt in range(32):
            sample=clone_world(state)
            events,draws=native_m6_original_form_bonds_with_coupled_oracle(sample,seed,salt)
            expected=outcome["lotteries"][salt]
            formed=[
                [min(x.id_a,x.id_b),max(x.id_a,x.id_b)]
                for x in events
            ]
            incidents=[
                edge for edge in formed
                if (edge[0] in ids)!=(edge[1] in ids)
            ]
            assert expected["salt"]==salt
            assert draws==expected["native_pairs_attempted"],(seed,arm,salt,"draw count")
            assert formed==expected["formed_all_pair_ids"],(seed,arm,salt,"bond IDs")
            assert incidents==expected["original_to_external_bonds"],(seed,arm,salt,"source recruitment")
            assert sample.state_hash_full()==expected["after_one_formation_sweep_full_hash"],(
                seed,arm,salt,"complete physical state")
            assert sample.rng.fingerprint()==state.rng.fingerprint()
            assert sample.rng.draws==state.rng.draws
            comparisons+=1
    assert comparisons==6*32
    return comparisons


def main():
    data=json.loads(PRIMARY.read_text(encoding="utf-8"))
    assert data["schema"]=="alife-m7-9-full-native-root-placement-640-world-audit-v1"
    assert data["all_640_seeds_in_16_shards"]
    cases=data["worlds"]
    assert len(cases)==640
    assert [r["seed"] for r in cases]==list(range(27001,27641))
    informative={
        r["seed"] for r in cases if r["selected"]
        and (
            4*r["arms"]["bond_only"]["native_energetic_boundary_interface"]["energy_qualified_boundary_contacts"]
            !=sum(r["arms"][f"root_scramble_{j}"]["native_energetic_boundary_interface"]["energy_qualified_boundary_contacts"] for j in range(4))
            or
            4*r["arms"]["bond_only"]["total_source_external_bonds_across_32_salts"]
            !=sum(r["arms"][f"root_scramble_{j}"]["total_source_external_bonds_across_32_salts"] for j in range(4))
        )
    }
    sentinels=set(data["first_selection_and_pairwise_replay_seed_per_nonempty_shard"])
    assert len(sentinels)==16
    selected_for_chemistry=informative|sentinels
    old=m75.protocol()
    verified=[]
    checked=0
    for i,row in enumerate(cases):
        assert row["selected"],"posthoc requires handling null sources if found"
        source_ids,states=verify_source(row,old)
        if row["seed"] in selected_for_chemistry:
            checked+=verify_chemistry(row,source_ids,states)
            verified.append(row["seed"])
        if (i+1)%80==0:
            print(f"M79_POSTHOC_PROGRESS parents={i+1}/640 oracle_lotteries={checked}",flush=True)
    assert checked==len(verified)*192
    result={
        "schema":"alife-m7-9-original-M6-form-bonds-posthoc-oracle-audit-v1",
        "source_worlds_all_rebuilt_from_seed":640,
        "all_four_root_energy_permutations_verified":640*4,
        "informative_discordant_worlds":len(informative),
        "shard_sentinels":len(sentinels),
        "selected_unique_worlds_for_native_M6_chemistry_audit":len(verified),
        "native_original_form_bonds_full_6_arm_32_salt_sweeps_checked":checked,
        "all_raw_pair_draws_actual_bonds_complete_state_hash_and_energy_match":True,
        "not_a_new_independent_statistical_replication":True,
        "preregistered_primary_secondary_decisions_unchanged":True,
        "verified_seeds":verified
    }
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M79_POSTHOC_FINAL="+json.dumps({
        "parents_rebuilt":640,
        "informed_seeds":len(informative),
        "oracle_seeds":len(verified),
        "oracle_sweeps":checked,
        "pass":True
    },sort_keys=True),flush=True)


if __name__=="__main__":
    main()
