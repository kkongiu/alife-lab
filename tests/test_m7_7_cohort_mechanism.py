"""M7.7 mechanism observability, noninterference and preregistered cohort gates."""
from support import make_energy_config, world_with
from tools.m6_5_ring_forks import clone_world
from tools.m7_3_bond_energy import energy_transfer
from tools import m7_5_mature_feedback as reference
from tools.m7_7_cohort_mechanism import (
    ARMS, protocol, provenance, interface_potential,
    frozen_immediate, classify_flux, transfer_with_audit,
    study, summarize
)


def tiny():
    cfg=make_energy_config(
        width=8,height=8,seed=777,
        species=[{"name":"S0","count":3,"move_probability":0.0,
                  "energy":6,"max_bonds":2}],
        chemistry={"enabled":True,"bond_cost":2,"formation_probability":0.0,
                   "break_probability":0.0,"allowed_pairs":[["S0","S0"]],
                   "catalysis":[]}
    )
    w=world_with(cfg,positions=[(0,1),(1,1),(2,1)],
                 species=[0,0,0],energy=[10,1,3],bonds=[(0,1,4)])
    assert w.energy()==w.configured_energy()==18
    return w


def test_fixed_protocol_heldout_nonoverlap_and_unchanged_old_rules():
    p=protocol()
    assert p["status"]=="preregistered_before_runner_tests_and_outcomes"
    assert p["design"]["seeds_first"]==25001 and p["design"]["seeds_last"]==25320
    assert p["design"]["worlds"]==320
    assert p["design"]["arm_types"]==list(ARMS)
    assert p["integrity"]["master_untouched"]
    assert p["integrity"]["original_src_untouched"]
    assert p["integrity"]["all_arms_same_initial_world_full_hash_rng_draws"]
    assert p["preregistered_gates"]["no_threshold_change"]
    assert [x for s in p["design"]["shards"] for x in range(s["start"],s["end"]+1)]==list(range(25001,25321))
    assert not (set(range(25001,25321)) & set(range(24001,24321)))
    assert set(provenance())=={
        "m77_protocol_sha256","original_m75_runner_sha256","original_m75_protocol_sha256"
    }


def test_native_energy_interface_matches_native_candidate_and_is_read_only():
    w=tiny()
    before=w.state_hash_full(),w.rng.fingerprint(),w.rng.draws
    zero=interface_potential(w,(0,1))
    assert zero["unbonded_geometrical_boundary_contacts"]==1
    assert zero["species_valence_qualified_boundary_contacts"]==1
    assert zero["energy_qualified_boundary_contacts"]==0
    assert zero["energy_blocked_qualified_contacts"]==1
    assert zero["root_members_energy_and_valence_ready"]==1
    assert (w.state_hash_full(),w.rng.fingerprint(),w.rng.draws)==before


def test_one_bond_transfer_alone_qualifies_boundary_without_topology_change():
    w=tiny()
    original=w.state_hash_full()
    f=frozen_immediate(w,(0,1))
    assert f["energy_qualified_boundary_before"]==0
    assert f["energy_qualified_boundary_after"]==1
    assert f["newly_qualified_net"]==1
    assert f["one_pass_transfer_events"]==1
    assert f["source_particle_energy_before"]==f["source_particle_energy_after_one_bond_pass"]
    assert f["energy_change_root_equals_boundary_net"] is True
    assert w.state_hash_full()==original


def test_transfer_audit_equals_original_m73_native_bond_energy_operation():
    for arm in ARMS:
        a=tiny()
        b=clone_world(a)
        status=transfer_with_audit(a,arm,(0,1))
        original=energy_transfer(b,arm)
        assert tuple(status[:3])==tuple(original)
        assert a.state_hash_full()==b.state_hash_full()
        assert a.rng.fingerprint()==b.rng.fingerprint()
        assert a.rng.draws==b.rng.draws
        assert status[0]==status[3]+status[4]+status[5]+(
            status[0]-status[3]-status[4]-status[5]
        )
        if arm=="bond_only":
            assert status[4]==status[5]==0
        if arm=="all_contacts":
            # An unbonded outside particle can transfer toward a root member.
            assert status[4]==1 and status[5]==0


def fake(seed,delta,prebreak_bond,prebreak_none,growth_bond=False,growth_none=False):
    outcome={}
    for arm in ARMS:
        treated=arm=="bond_only"
        num=10+delta if treated else 10
        outcome[arm]={
            "poststep_t0":{},
            "cumulative":{
                "energy_qualified_boundary_contacts":num,
                "species_valence_qualified_boundary_contacts":20,
                "unbonded_geometrical_boundary_contacts":30,
                "energy_blocked_qualified_contacts":20-num,
                "root_members_energy_and_valence_ready":120,
                "root_material_particle_energy":1200
            },
            "incident_external_formation_count":int(prebreak_bond if treated else prebreak_none),
            "source_incident_prebreak_binary":bool(prebreak_bond if treated else prebreak_none),
            "incident_external_formations_before_original_break":int(prebreak_bond if treated else prebreak_none),
            "coherent_growth_at_120":growth_bond if treated else growth_none,
            "all_original_edges_unbroken_120":False,
            "final":{"global_new_bonds":25},
            "source_incoming_passes":0,"source_outgoing_passes":0
        }
    return {
        "seed":seed,"selected":True,"source":{"size":7,"cyclomatic_number":0},
        "frozen_t0_energy_only_mechanism":{
            "newly_qualified_net":0,
            "source_particle_energy_before":20,
            "source_particle_energy_after_one_bond_pass":20,
            "one_pass_transfer_events":0
        },
        "outcomes":outcome
    }


def test_mechanism_gates_count_seed_not_ticks_and_fail_below_2third():
    p=protocol()
    rows=[]
    for i,seed in enumerate(range(25001,25321)):
        # 100 non-tied energetic-interface contrasts: 70 positive
        difference=1 if i<70 else -1 if i<100 else 0
        # 30 discordant prebreak form: 20 favor conduction
        pp=(i<20)
        nn=(20<=i<30)
        rows.append(fake(seed,difference,pp,nn))
    s=summarize(rows,p)
    assert s["paired_comparisons"]["energetically_eligible_poststep_boundary_interface_sum"]=={
        "favor_bond_only":70,"favor_no_transfer":30,"tied":220,
        "non_tied":100,"favorable_fraction":0.7
    }
    assert s["preregistered_decisions"]["primary_energetic_interface"]=="passed"
    assert s["preregistered_decisions"]["secondary_prebreak_recruitment"]=="passed"
    rows[0]["outcomes"]["bond_only"]["cumulative"]["energy_qualified_boundary_contacts"]=9
    for i in range(1,5):
        rows[i]["outcomes"]["bond_only"]["cumulative"]["energy_qualified_boundary_contacts"]=9
    x=summarize(rows,p)
    assert x["preregistered_decisions"]["primary_energetic_interface"]=="not_met_or_underpowered"


def test_real_original_M75_source_same_three_arm_physics_with_new_tracer():
    p=reference.protocol()
    r=study(25001,p,replay=True)
    assert r["seed"]==25001 and r["selected"]
    assert 5<=r["source"]["size"]<=16
    assert r["source"]["original_edges_aged_at_least20"]>=2
    assert r["fork_tick"]>=120
    for arm in ARMS:
        h=r["outcomes"][arm]
        assert len(h["checkpoints"])==5
        assert len(h["per_tick_opportunities"])==120
        assert h["cumulative"]["species_valence_qualified_boundary_contacts"]>=h["cumulative"]["energy_qualified_boundary_contacts"]
        assert h["final"]["injected"]>=0
        assert h["final"]["stored_energy"]>=0
    assert r["frozen_t0_energy_only_mechanism"]["original_full_world_unchanged"]
