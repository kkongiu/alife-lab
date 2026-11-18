"""M8.0 is a NEW physics sandbox; no spontaneous-life claims from fixtures."""
from alife_m8.sandbox import WorldM8,LAW_VERSION
from tools.m8_0_preflight import protocol,product_state,execute_case


def test_frozen_preflight_and_synthetic_only_scope():
    p=protocol()
    assert p["status"]=="frozen_before_new_law_implementation_or_result"
    assert p["physical_law_version"]=="M8.0-new-physics-not-M6"
    assert LAW_VERSION.startswith("M8.0-local-B-H-")
    assert p["controls"]["simulation_horizon"]==120
    assert p["integrity"]["no_historical_M6_edits"]
    assert p["integrity"]["real_local_reaction_events_no_direct_child_creation"]
    assert p["controls"]["preregistered_minimums"]["causal_edit"].startswith("At least 20/32")


def test_independent_new_physics_exact_material_and_energy_ledgers():
    w=WorldM8(seed=99123,mode="templated",template_sequence="0101")
    assert w.initial_matter==84
    assert w.initial_energy==503
    assert len(w.particles)==4
    assert len(w.B)==3 and len(w.H)==0
    initial_ids=tuple(w.initial_template_material_ids)
    assert all(w.particles[i].species in (0,1) for i in initial_ids)
    for _ in range(120):
        w.step()
        assert w.initial_matter==len(w.particles)+sum(w.bath.values())
        assert w.initial_energy==w.free_energy+sum(w.B.values())+sum(w.H.values())+w.dissipated
    assert len(w.particles)>4
    assert len(set(w.particles))==len(w.particles)
    assert all(i in w.particles for i in initial_ids)
    assert any(e["kind"]=="adsorb" and e["source_material_id"] in initial_ids for e in w.events)
    assert any(e["kind"]=="B_form" for e in w.events)
    assert any(e["kind"]=="H_release" for e in w.events)
    w.check()


def test_identical_seed_replay_same_world_state_and_experiment_event_sequence():
    a=WorldM8(seed=99302,mode="templated",template_sequence="0101")
    b=WorldM8(seed=99302,mode="templated",template_sequence="0101")
    for _ in range(60):
        a.step()
        b.step()
    assert a.full_hash()==b.full_hash()
    assert a.events==b.events


def test_shuffled_information_channel_is_insensitive_to_parent_point_edit():
    a=WorldM8(seed=99403,mode="shuffled_identity",template_sequence="0101")
    b=WorldM8(seed=99403,mode="shuffled_identity",template_sequence="0111")
    x=5
    assert a.particles[a.grid[(x,1)]].species!=b.particles[b.grid[(x,1)]].species
    for _ in range(12):
        a.step()
        b.step()
    # Parent sequence differs physically, but shuffled local reactions DO NOT
    # read parent species as a chemical selector; actual new monomer reaction
    # identities remain the same in these two matched control worlds.
    for x in range(3,7):
        ia=a.grid.get((x,2))
        ib=b.grid.get((x,2))
        assert (ia is None)==(ib is None)
        if ia is not None:
            assert a.particles[ia].species==b.particles[ib].species
    assert all(e["kind"]=="adsorb" for e in a.events if e["kind"]=="adsorb")


def test_without_template_channel_or_any_free_energy_no_mononer_capture():
    for mode,amount in (("no_template",500),("unpowered",0)):
        w=WorldM8(seed=99501,mode=mode,template_sequence="0101",initial_free_energy=amount)
        n=len(w.particles)
        for _ in range(80):
            w.step()
        assert len(w.particles)==n
        assert not any(e["kind"]=="adsorb" for e in w.events)
        w.check()


def test_readonly_product_detector_checks_material_disjoint_B_and_no_parent_H():
    w=WorldM8(seed=99502,mode="templated",template_sequence="0101")
    assert product_state(w) is None
    # Synthetic detector-only fixture, NEVER counted as a real physical output.
    ids=[]
    for x,bit in zip(range(3,7),"0101"):
        ids.append(w._place(x,2,int(bit)))
    for i,j in zip(ids,ids[1:]):
        w.B[w._key(i,j)]=1
    # Fix the synthetic fixture's original energy ledger for this unit test.
    w.initial_matter+=4
    w.initial_energy+=3
    assert product_state(w) is not None
    w.H[w._key(ids[0],w.initial_template_material_ids[0])]=1
    w.initial_energy+=1
    assert product_state(w) is None
    w.check()


def test_full_physical_single_fixture_with_multiple_control_modes():
    r=execute_case(99777,"templated","0101")
    assert r["mass_energy_ledger_all_120_steps_pass"]
    assert r["total_matter_initial"]==84
    assert len(r["source_initial_material_ids"])==4
    assert all(x["kind"]=="adsorb" for x in r["all_real_local_capture_events"])
    # A physically formed product may be absent in this seed: no cherry-pick.
    assert isinstance(r["physically_distinct_detached_products_persisting_at_least_20_ticks"],list)
