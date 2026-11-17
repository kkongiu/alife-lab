"""M7.8: frozen native geometry + common pair-keyed chemical lotteries.

Selected cohorts are NATURAL using the untouched M7.5 source selector.
One optional energy transfer occurs on exact clones with no native timestep.
Then a single isolated formation-only chemical sweep uses M6 geometry,
candidate iterator, threshold, valence/energy rechecks and payments,
but hash-coupled per-pair RNG (external to the native simulator).

This is an experimental reaction counterfactual, NOT World.advance().
No hidden movements, bond break events, decay, injection or RNG draws.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from alife.chemistry import _candidate_pairs, _catalysis_factor
from tools.m6_5_ring_forks import clone_world
from tools.m7_2_energy_distribution import contacts, ledger
from tools.m7_3_bond_energy import energy_transfer
from tools.m7_7_cohort_mechanism import interface_potential
from tools import m7_5_mature_feedback as original

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"campaigns/m7_8_frozen"
PROTOCOL=BASE/"protocol.json"
RESULTS=BASE/"results.json"
OLD_M75=ROOT/"tools/m7_5_mature_feedback.py"
ARMS=("sham","bond_only","all_contacts","unbonded_budget_matched")
SALTS=tuple(range(32))
FIRST=26001
LAST=26640


def protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"]=="alife-m7-8-frozen-native-pairwise-chemistry-v1"
    assert p["status"]=="preregistered_before_runner_and_outcomes"
    sample=p["sample"]
    assert (sample["start"],sample["end_inclusive"],sample["seed_count"])==(FIRST,LAST,640)
    assert p["chemistry"]["coupled_lottery_count"]==len(SALTS)==32
    assert len(sample["shards"])==16
    assert [s for d in sample["shards"] for s in range(d["start"],d["end"]+1)]==list(range(FIRST,LAST+1))
    assert set(p["interventions"])==set(ARMS)|{"physical_freeze"}
    assert original.protocol()["design"]["parent_scan_start_tick"]==120
    assert p["integrity"]["historical_M7_3_M7_5_M7_6_M7_7_modules_and_protocols_untouched"]
    return p


def provenance():
    return {
        "m78_prereg_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "m75_untouched_source_sha256":sha256(OLD_M75.read_bytes()).hexdigest()
    }


def pair_draw(seed,salt,id_a,id_b):
    """Same uniform 64-bit draw for pair identity in ALL physical arms."""
    assert salt in SALTS and seed>=FIRST
    lo,hi=sorted((id_a,id_b))
    pre=f"alife-m7-8|{seed}|{salt}|{lo}|{hi}".encode("ascii")
    return int.from_bytes(sha256(pre).digest()[:8],"big")


def nonbonded_budget_transfer(w,budget):
    """One synchronous unbonded-only pass capped to bond-only event count.

    This matches NUMBER of accepted transfer passes when enough eligible
    unbonded contacts exist, NOT donor/recipient energies or locations.
    """
    assert budget>=0
    s=w.store
    old_energy=w.energy()
    old_rng=w.rng.fingerprint(),w.rng.draws
    old_state=(tuple(s.xs),tuple(s.ys),tuple(s.species),tuple(sorted(s.bonds.items())))
    before=tuple(s.energy)
    rem=list(before)
    delta=[0]*len(before)
    bond_set=set(s.bonds)
    accepted=0
    for a,b in contacts(s):
        if accepted>=budget:break
        if (a,b) in bond_set or (b,a) in bond_set:continue
        if before[a]-before[b]>=2:donor,recipient=a,b
        elif before[b]-before[a]>=2:donor,recipient=b,a
        else:continue
        if rem[donor]<1:continue
        rem[donor]-=1
        delta[donor]-=1
        delta[recipient]+=1
        accepted+=1
    for idx,change in enumerate(delta):
        if change:
            s.energy[idx]+=change
            assert s.energy[idx]>=0
    assert sum(s.energy)==sum(before) and w.energy()==old_energy
    assert (w.rng.fingerprint(),w.rng.draws)==old_rng
    assert old_state==(tuple(s.xs),tuple(s.ys),tuple(s.species),tuple(sorted(s.bonds.items())))
    assert 0<=accepted<=budget
    return {"requested_budget":budget,"accepted_unbonded_transfers":accepted,
            "budget_shortfall":budget-accepted}


def apply_intervention(parent,arm,budget):
    w=clone_world(parent)
    rng=(parent.rng.fingerprint(),parent.rng.draws)
    total=parent.energy()
    old_graph=tuple(sorted(parent.store.bonds.items()))
    positions=(tuple(parent.store.xs),tuple(parent.store.ys),tuple(parent.store.species))
    if arm=="sham":
        flow={"transfer_events":0,"bond_route":0,"unbonded_route":0}
    elif arm in ("bond_only","all_contacts"):
        t,b,u=energy_transfer(w,arm)
        flow={"transfer_events":t,"bond_route":b,"unbonded_route":u}
    elif arm=="unbonded_budget_matched":
        data=nonbonded_budget_transfer(w,budget)
        flow={"transfer_events":data["accepted_unbonded_transfers"],
              "bond_route":0,"unbonded_route":data["accepted_unbonded_transfers"],**data}
    else:raise ValueError(arm)
    assert w.energy()==total and (w.rng.fingerprint(),w.rng.draws)==rng
    assert tuple(sorted(w.store.bonds.items()))==old_graph
    assert (tuple(w.store.xs),tuple(w.store.ys),tuple(w.store.species))==positions
    assert w.step==parent.step
    ledger(w,w.configured_energy())
    return w,flow


def formation_only_pair_keyed(world,source_ids,seed,salt):
    """One M6-native-format formation-only sweep with pair-specific exogenous RNG.

    Original chemistry.form_bonds behavior:
      - iterate _candidate_pairs() LIVE (may change after early bonds);
      - native formation_probability threshold; if catalytic, same factor;
      - draw BEFORE rechecking valence/energy/existing bond;
      - pay same formation_cost into bond energy/dissipation.
    Pair draw is keyed by MATERIAL IDs, not by candidate ordering.
    """
    assert salt in SALTS
    old_rng=(world.rng.fingerprint(),world.rng.draws)
    old_pos=(tuple(world.store.xs),tuple(world.store.ys),tuple(world.store.species))
    s=world.store
    group=set(source_ids)
    formed=[]
    boundary=[]
    attempted=0
    for a,b in _candidate_pairs(world):
        attempted+=1
        factor=_catalysis_factor(world,a,b)
        limit=world.formation_threshold
        if factor>1.0:
            limit=int(min(1.0,world.chemistry.formation_probability*factor)*(1<<64))
        if pair_draw(seed,salt,s.ids[a],s.ids[b])>=limit:
            continue
        if s.degree[a]>=world.max_bonds[s.species[a]]:
            continue
        if s.degree[b]>=world.max_bonds[s.species[b]]:
            continue
        if s.energy[a]<world.formation_cost or s.energy[b]<world.formation_cost:
            continue
        if (a,b) in s.bonds or (b,a) in s.bonds:
            continue
        id_a,id_b=s.ids[a],s.ids[b]
        cost=world.formation_cost
        extra=world.formation_dissipation
        s.energy[a]-=cost
        s.energy[b]-=cost
        s.add_bond(a,b,2*(cost-extra))
        world.dissipated+=2*extra
        world.bonds_formed_total+=1
        edge=(min(id_a,id_b),max(id_a,id_b))
        formed.append(edge)
        if (id_a in group)!=(id_b in group):
            boundary.append(edge)
    assert old_rng==(world.rng.fingerprint(),world.rng.draws)
    assert old_pos==(tuple(s.xs),tuple(s.ys),tuple(s.species))
    world.check()
    ledger(world,world.configured_energy())
    return {"salt":salt,"native_pairs_attempted":attempted,
            "all_new_bonds":len(formed),
            "original_to_external_bonds":[list(x) for x in boundary],
            "formed_original_to_external":len(boundary),
            "formed_all_pair_ids":[list(x) for x in formed],
            "after_one_formation_sweep_full_hash":world.state_hash_full()}


def run_one(seed,prior,replay=False):
    parent,cohort,selection=original.select_parent(seed,prior)
    if cohort is None:
        return {"seed":seed,"selected":False,"reason":"no_eligible_original_m75_native_cohort",
                "parent_ticks_scanned":parent.step}
    source_ids=tuple(cohort["ids"])
    source_edges=tuple(cohort["edges"])
    original_hash=parent.state_hash_full()
    original_rng=parent.rng.fingerprint(),parent.rng.draws
    original_world=parent.energy()
    pre=interface_potential(parent,source_ids)
    assert original_world==parent.configured_energy()+parent.injected-parent.dissipated-parent.unabsorbed
    bond=clone_world(parent)
    target=energy_transfer(bond,"bond_only")[0]
    assert bond.rng.fingerprint()==parent.rng.fingerprint()
    arms={}
    for arm in ARMS:
        state,flux=apply_intervention(parent,arm,target)
        val=interface_potential(state,source_ids)
        assert val["unbonded_geometrical_boundary_contacts"]==pre["unbonded_geometrical_boundary_contacts"]
        assert val["species_valence_qualified_boundary_contacts"]==pre["species_valence_qualified_boundary_contacts"]
        if arm=="sham":
            assert state.state_hash_full()==original_hash
            assert flux["transfer_events"]==0
        if arm=="bond_only":
            assert state.state_hash_full()==bond.state_hash_full()
            assert flux["transfer_events"]==target
            assert val["root_material_particle_energy"]==pre["root_material_particle_energy"],(
                "maximal component: all extant bonds are internal")
        results=[]
        for salt in SALTS:
            candidate=clone_world(state)
            record=formation_only_pair_keyed(candidate,source_ids,seed,salt)
            results.append(record)
        total=sum(r["formed_original_to_external"] for r in results)
        raw={"arm":arm,"after_one_transfer_full_hash":state.state_hash_full(),
             "energy_conservation_verified":True,
             "transfer":flux,"static_interface":val,
             "boundary_eligibility_change_vs_sham":val["energy_qualified_boundary_contacts"]-pre["energy_qualified_boundary_contacts"],
             "original_source_energy_after":val["root_material_particle_energy"],
             "lotteries":results,
             "mean_external_formed_per_lottery":round(total/len(SALTS),6),
             "total_external_formed_across_32_lotteries":total,
             "lotteries_with_any_external_formed":sum(r["formed_original_to_external"]>0 for r in results),
             "mean_all_new_bonds_per_lottery":round(
                sum(r["all_new_bonds"] for r in results)/len(SALTS),6)}
        assert raw["original_source_energy_after"]>=0
        arms[arm]=raw
        assert parent.state_hash_full()==original_hash
        assert (parent.rng.fingerprint(),parent.rng.draws)==original_rng
    if replay:
        # An additional complete from-seed replay of the same fixed original
        # cohort and one deterministic M7.3 bond pass.
        independent,chosen,_=original.select_parent(seed,prior)
        assert independent.state_hash_full()==original_hash
        assert chosen["ids"]==cohort["ids"] and chosen["edges"]==cohort["edges"]
        independent_bond=clone_world(independent)
        assert energy_transfer(independent_bond,"bond_only")[0]==target
        assert independent_bond.state_hash_full()==arms["bond_only"]["after_one_transfer_full_hash"]
        # Full same-material chemistry recheck for salt0, without using prior
        # arm's cloned formation state.
        trial=formation_only_pair_keyed(independent_bond,source_ids,seed,0)
        assert trial==arms["bond_only"]["lotteries"][0]
    assert parent.state_hash_full()==original_hash
    assert (parent.rng.fingerprint(),parent.rng.draws)==original_rng
    return {"seed":seed,"selected":True,"fork_tick":parent.step,
            "source":cohort,"selection":selection,
            "source_parent_hash":original_hash,"source_rng":parent.rng.fingerprint(),
            "source_rng_draws":parent.rng.draws,
            "pre_intervention_interface":pre,
            "bond_only_transfer_budget":target,
            "arms":arms}


def summarize(rows,p):
    assert len(rows)==640 and [r["seed"] for r in rows]==list(range(FIRST,LAST+1))
    selected=[r for r in rows if r["selected"]]
    n=len(selected)
    def avg(xs):
        return round(sum(xs)/len(xs),6) if xs else None
    def compare(field):
        scores=[]
        for r in selected:
            a=r["arms"]["bond_only"][field]
            b=r["arms"]["sham"][field]
            scores.append(a-b)
        favor=sum(x>0 for x in scores)
        against=sum(x<0 for x in scores)
        ties=len(scores)-favor-against
        return {"favor_bond_only":favor,"favor_sham":against,"ties":ties,
                "discordant":favor+against,
                "fraction_favor_bond_only":round(favor/(favor+against),6)
                    if favor+against else None,
                "mean_paired_delta":avg(scores)}
    gains=compare("boundary_eligibility_change_vs_sham")
    formation=compare("total_external_formed_across_32_lotteries")
    def armstats(arm):
        group=[r["arms"][arm] for r in selected]
        return {
            "mean_eligible_external_pairs_postpass":avg([x["static_interface"]["energy_qualified_boundary_contacts"] for x in group]),
            "worlds_with_nonzero_transport":sum(x["transfer"]["transfer_events"]>0 for x in group),
            "mean_transfer_events":avg([x["transfer"]["transfer_events"] for x in group]),
            "mean_real_external_new_bonds_per_coupled_lottery":avg([x["total_external_formed_across_32_lotteries"]/32 for x in group]),
            "mean_external_new_bond_events_across_32_lotteries":avg([x["total_external_formed_across_32_lotteries"] for x in group]),
            "source_worlds_with_any_reactive_external_formation_in_32_lotteries":sum(x["total_external_formed_across_32_lotteries"]>0 for x in group)
        }
    arms={a:armstats(a) for a in ARMS}
    matched=[
        r["arms"]["unbonded_budget_matched"]["transfer"]
        for r in selected
    ]
    possible=sum(x["budget_shortfall"]==0 for x in matched)
    pure=[]
    for r in selected:
        a=r["arms"]["bond_only"]["total_external_formed_across_32_lotteries"]
        b=r["arms"]["unbonded_budget_matched"]["total_external_formed_across_32_lotteries"]
        pure.append(a-b)
    strat={
        "size_5_8":sum(r["source"]["size"]<=8 for r in selected),
        "size_9_16":sum(r["source"]["size"]>=9 for r in selected),
        "tree":sum(r["source"]["cyclomatic_number"]==0 for r in selected),
        "cyclic":sum(r["source"]["cyclomatic_number"]>0 for r in selected)
    }
    primary="passed" if (
        n>=40 and gains["discordant"]>=20 and gains["favor_bond_only"]>=15
        and 5*gains["favor_bond_only"]>=4*gains["discordant"]
    ) else "not_met_or_underpowered"
    secondary="passed" if (
        n>=40 and formation["discordant"]>=15
        and 3*formation["favor_bond_only"]>=2*formation["discordant"]
    ) else "not_met_or_underpowered"
    return {
        "source_seed_worlds":640,
        "eligible_nat_source_worlds":n,
        "ineligible_nat_source_worlds":640-n,
        "selected_source_strata":strat,
        "per_arm":arms,
        "paired_mechanism": {
            "native_new_external_energetic_pair_activation":gains,
            "coupled_actual_external_formation_count_32_per_seed":formation,
            "bond_vs_unbonded_matched_count_coupled_formation": {
                "favor_bond_only":sum(x>0 for x in pure),
                "favor_unbonded":sum(x<0 for x in pure),
                "ties":sum(x==0 for x in pure),
                "mean_delta_32_lotteries":avg(pure)
            }
        },
        "unbonded_comparator":{
            "selected_sources_with_exactly_equal_transfer_count_to_bond_only":possible,
            "sources_with_unbonded_transfer_budget_shortfall":n-possible,
            "mean_shortfall_events":avg([x["budget_shortfall"] for x in matched])
        },
        "preregistered_decisions":{
            "direct_energetic_activation":primary,
            "actual_coupled_pair_formation_benefit":secondary,
            "primary_required_min_sources":40,
            "primary_required_min_discordants":20,
            "primary_required_min_strict_positive_sources":15,
            "primary_required_favorable_fraction":"4/5",
            "secondary_required_min_discordants":15,
            "secondary_required_favorable_fraction":"2/3",
            "no_claim_of_topology_specificity_from_sham_comparison":True
        },
        "caveat":"Isolated chemistry uses exogenous pair-keyed lotteries on frozen geometry and no movement, breaking, injection or source dynamics, so is not native full World.advance. Seed is independent unit; 32 lotteries are repeated coupled trials on same state."
    }


def run_shard(start,end):
    p=protocol()
    d={"start":start,"end":end}
    assert d in p["sample"]["shards"]
    rows=[]
    first_replayed=None
    prior=original.protocol()
    for seed in range(start,end+1):
        r=run_one(seed,prior,replay=(first_replayed is None))
        rows.append(r)
        if r["selected"] and first_replayed is None:first_replayed=seed
        if (seed-start+1)%10==0:
            print(f"M78_PROGRESS shard={start}-{end} seed={seed} selected={sum(x['selected'] for x in rows)}",flush=True)
    assert len(rows)==end-start+1
    obj={"schema":"alife-m7-8-shard-v1",
         "descriptor":d,"provenance":provenance(),
         "source_worlds":rows,
         "first_selected_bare_source_and_chemical_replay":first_replayed,
         "no_native_or_historic_changes":True}
    path=BASE/"shards"/f"{start}-{end}.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("M78_SHARD="+json.dumps({"start":start,"end":end,"sources":len(rows),
                                 "selected":sum(x["selected"] for x in rows),
                                 "first_replayed":first_replayed},sort_keys=True),flush=True)


def merge():
    p=protocol()
    files=sorted((BASE/"shards").glob("*.json"))
    assert len(files)==16,(len(files),"need 16")
    expected=provenance()
    seen=[]
    rows=[]
    replays=[]
    for path in files:
        d=json.loads(path.read_text(encoding="utf-8"))
        assert d["schema"]=="alife-m7-8-shard-v1"
        assert d["provenance"]==expected
        assert d["no_native_or_historic_changes"] is True
        desc=d["descriptor"]
        assert desc in p["sample"]["shards"] and desc not in seen
        seen.append(desc)
        sh=d["source_worlds"]
        assert [r["seed"] for r in sh]==list(range(desc["start"],desc["end"]+1))
        first=next((r["seed"] for r in sh if r["selected"]),None)
        assert first==d["first_selected_bare_source_and_chemical_replay"]
        if first is not None:replays.append(first)
        rows.extend(sh)
    assert all(x in seen for x in p["sample"]["shards"])
    rows.sort(key=lambda x:x["seed"])
    s=summarize(rows,p)
    output={
        "schema":"alife-m7-8-full-640-frozen-source-reaction-causality-v1",
        "provenance":expected,
        "source_worlds":rows,
        "first_source_replays_per_nonempty_shard":replays,
        "summary":s,
        "all_640_seed_worlds_and_16_shards_complete":True,
        "original_native_M6_and_M7_3_through_M7_7_code_unchanged":True
    }
    RESULTS.parent.mkdir(parents=True,exist_ok=True)
    RESULTS.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("M78_FINAL_SUMMARY="+json.dumps(s,sort_keys=True),flush=True)
    print("M78_SUCCESS="+str(len(rows)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    cmd=parser.add_subparsers(dest="cmd",required=True)
    sh=cmd.add_parser("shard")
    sh.add_argument("--start",type=int,required=True)
    sh.add_argument("--end",type=int,required=True)
    cmd.add_parser("merge")
    a=parser.parse_args()
    if a.cmd=="shard":run_shard(a.start,a.end)
    else:merge()


if __name__=="__main__":
    main()
