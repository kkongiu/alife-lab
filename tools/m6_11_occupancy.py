"""M6.11: preregistered passive occupancy audit of spontaneous M6 lattice pockets.

No physical changes. Tests shells at fixed times, observes full native rings
at every tick, and counts independent worlds separately from dependent episodes.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from tools.m6_4_cycles import BreakRecorder, create_natural, protocol as natural_protocol
from tools.m6_10_pockets import BORDER_OFFSETS, observed_cycles

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "campaigns/m6_11_occupancy/protocol.json"
OUTPUT = ROOT / "campaigns/m6_11_occupancy/results.json"
# Clockwise 3x3 perimeter; exact original native material bonds only.
CLOCKWISE = ((-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0))


def protocol():
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema"] == "alife-m6-11-natural-pocket-occupancy-audit-v1"
    assert p["status"] == "frozen-before-analytical-code-and-new-results"
    assert p["sample"]["seeds"] == list(range(10001, 10101))
    assert p["sample"]["expected_worlds"] == 200
    assert p["sample"]["fixed_checkpoint_stride"] == 20
    return p


def center_occupation(store, center, species_specs):
    x, y = center
    i = store.grid[y * store.width + x]
    if i == -1:
        return {"id":None, "degree":None, "mobile":False, "species":None}
    return {
        "id":store.ids[i], "degree":store.degree[i],
        "mobile":species_specs[store.species[i]].move_probability > 0,
        "species":store.species[i]
    }


def shell_edges(store, center, bonds):
    """Returns None if any of eight sites is empty; else native edge count."""
    x, y = center
    ids = []
    for dx, dy in CLOCKWISE:
        xx = (x + dx) % store.width
        yy = (y + dy) % store.height
        index = store.grid[yy * store.width + xx]
        if index == -1:
            return None
        ids.append(store.ids[index])
    return sum(
        tuple(sorted((ids[k], ids[(k+1)%8]))) in bonds
        for k in range(8)
    )


def snapshot(store):
    # Copy is read-only relative to future simulator steps.
    return {
        "grid":tuple(store.grid), "ids":tuple(store.ids),
        "degree":tuple(store.degree), "species":tuple(store.species),
        "bonds":frozenset(
            tuple(sorted((store.ids[a], store.ids[b])))
            for a, b in store.bonds
        )
    }


def shell_from_snapshot(snap, center, width, height):
    x, y = center
    material = []
    for dx, dy in CLOCKWISE:
        ix = snap["grid"][((y+dy)%height)*width+((x+dx)%width)]
        if ix == -1:
            return None
        material.append(snap["ids"][ix])
    return sum(tuple(sorted((material[k],material[(k+1)%8]))) in snap["bonds"] for k in range(8))


def previous_center(snap, center, world):
    if snap is None:
        return None
    x, y = center
    store = world.store
    i = snap["grid"][y*store.width+x]
    return {
        "occupied":i != -1,
        "free_mobile": (
            i != -1 and snap["degree"][i] == 0
            and world.config.species[snap["species"][i]].move_probability > 0
        ),
        "full_shell_edge_count":shell_from_snapshot(
            snap, center, store.width, store.height
        )
    }


def shell_class(n):
    return "0-5" if n <= 5 else str(n)


def fixed_time_shells(world):
    """All geometrically closed eight-site shells, regardless of connectivity."""
    s = world.store
    native_bonds = {
        tuple(sorted((s.ids[a], s.ids[b]))) for a, b in s.bonds
    }
    counts = Counter()
    examples = []
    for y in range(s.height):
        for x in range(s.width):
            center = (x,y)
            edges = shell_edges(s, center, native_bonds)
            if edges is None:
                continue
            occupation = center_occupation(s, center, world.config.species)
            tag = shell_class(edges)
            counts[f"{tag}_shells"] += 1
            if occupation["id"] is None:
                counts[f"{tag}_empty"] += 1
            elif occupation["degree"] == 0 and occupation["mobile"]:
                counts[f"{tag}_free_mobile"] += 1
            elif occupation["degree"] == 0:
                counts[f"{tag}_free_immobile"] += 1
            else:
                counts[f"{tag}_bonded"] += 1
            if edges >= 7 and len(examples) < 5:
                examples.append({
                    "center":[x,y],"edges":edges,
                    "center_id":occupation["id"],
                    "center_degree":occupation["degree"]
                })
    return counts, examples


def study_world(world, steps=600, stride=20):
    assert world.step == 0
    world.check()
    assert not world.store.bonds
    original = {
        "hash":world.state_hash_full(),
        "rng":world.rng.fingerprint(),
        "draws":world.rng.draws
    }
    broken = BreakRecorder()
    world.event_sink = broken
    previous = None
    active = {}
    episodes = []
    counts = Counter()
    fixed = Counter()
    fixed_examples = []
    material_sets = set()

    def finish(key, tick, reason, censored=False):
        ep = active.pop(key)
        duration = tick - ep["start_tick"] + (1 if censored else 0)
        assert duration >= 1
        episodes.append({
            **ep, "duration_ticks":duration,
            "right_censored":censored, "ended_by":reason
        })

    def observe(w):
        nonlocal previous
        draws = w.rng.draws
        tick = w.step
        broken_edges = broken.pop(tick)
        rings, _ = observed_cycles(w)
        now = {}
        for ring in rings:
            if ring["size"] != 8 or ring["pocket"] is not True:
                continue
            key = (ring["ids"], ring["edges"])
            now[key] = ring
        for key, ep in list(active.items()):
            ring = now.get(key)
            breaking = bool(broken_edges.intersection(key[1]))
            if ring is None or breaking or list(ring["center"]) != ep["center"]:
                reason = "original_edge_broken" if breaking else "ring_or_geometry_lost"
                finish(key, tick, reason)
        for key, ring in now.items():
            if key in active:
                active_ep = active[key]
                occupant = center_occupation(w.store, ring["center"], w.config.species)
                assert occupant["id"] == active_ep["center_id"], "sealed perimeter changed resident"
                continue
            center = ring["center"]
            occ = center_occupation(w.store, center, w.config.species)
            assert occ["degree"] in (None,0)
            material_sets.add(ring["ids"])
            active[key] = {
                "start_tick":tick, "ids":list(ring["ids"]),
                "edges":[list(edge) for edge in ring["edges"]],
                "center":list(center), "signature":ring["signature"],
                "center_id":occ["id"],"center_degree":occ["degree"],
                "center_mobile":occ["mobile"],
                "prior_tick":previous_center(previous,center,w)
            }
            counts["pocket_births"] += 1
            if occ["id"] is None:
                counts["pocket_births_empty"] += 1
            else:
                counts["pocket_births_occupied"] += 1
        if tick % stride == 0:
            controls, examples = fixed_time_shells(w)
            fixed.update(controls)
            if examples and len(fixed_examples) < 10:
                fixed_examples.append({"tick":tick,"examples":examples})
        previous = snapshot(w.store)
        assert w.rng.draws == draws, "observer consumed random numbers"

    world.advance(steps,observer=observe)
    for key in list(active):
        finish(key,world.step,"end_of_run",censored=True)
    world.check()
    return {
        "initial":original,
        "final":{
            "hash":world.state_hash_full(),
            "rng":world.rng.fingerprint(), "draws":world.rng.draws,
            "energy":world.energy(), "dissipated":world.dissipated,
            "formed":world.bonds_formed_total, "broken":world.bonds_broken_total
        },
        "pocket_episodes":episodes,
        "distinct_pocket_material_sets":len(material_sets),
        "birth_counts":dict(counts),
        "fixed_shell_counts":dict(fixed),
        "fixed_examples":fixed_examples
    }


def summarize(worlds, p):
    by_density = {}
    for density in p["sample"]["densities"]:
        relevant = [w for w in worlds if w["density"] == density]
        counts = Counter()
        fixed = Counter()
        independent_trap = 0
        independent_pocket = 0
        first_episodes = []
        for w in relevant:
            result = w["result"]
            episodes = result["pocket_episodes"]
            counts.update(result["birth_counts"])
            fixed.update(result["fixed_shell_counts"])
            counts["episodes"] += len(episodes)
            counts["material_sets"] += result["distinct_pocket_material_sets"]
            counts["censored"] += sum(e["right_censored"] for e in episodes)
            if episodes:
                independent_pocket += 1
                first_episodes.append({"seed":w["seed"], **episodes[0]})
            if any(e["center_id"] is not None and e["center_mobile"]
                   and e["duration_ticks"] >= 30 for e in episodes):
                independent_trap += 1
        def ratio(n,d):
            return None if d == 0 else round(n/d, 6)
        rates = {
            k:{
                "shells":fixed[f"{k}_shells"],
                "empty":fixed[f"{k}_empty"],
                "free_mobile":fixed[f"{k}_free_mobile"],
                "bonded":fixed[f"{k}_bonded"],
                "free_immobile":fixed[f"{k}_free_immobile"],
                "empty_fraction":ratio(fixed[f"{k}_empty"],fixed[f"{k}_shells"]),
                "free_mobile_fraction":ratio(fixed[f"{k}_free_mobile"],fixed[f"{k}_shells"])
            } for k in ("0-5","6","7","8")
        }
        by_density[density] = {
            "worlds":len(relevant), "worlds_with_pockets":independent_pocket,
            "worlds_with_native_mobile_trap_30ticks":independent_trap,
            "births_and_episodes":dict(counts),
            "fixed_checkpoint_shells":rates,
            "first_pocket_birth_by_world":first_episodes
        }
    trapped = sum(x["worlds_with_native_mobile_trap_30ticks"] for x in by_density.values())
    return {
        "by_density":by_density,
        "independent_worlds_with_confirmed_geometric_trap":trapped,
        "decision":("replicated_native_geometric_trapping_only" if trapped>=2
                    else "one_case" if trapped==1 else "no_confirmed_trapping"),
        "caveat":"All fixed-time shell snapshots and repeated pocket episodes are dependent observations. No claim of causality, membranes, heredity or life."
    }


def run():
    p = protocol()
    natural = natural_protocol()
    worlds = []
    replays = []
    for density in p["sample"]["densities"]:
        for seed in p["sample"]["seeds"]:
            world = create_natural(seed,density,natural)
            result = study_world(world,p["sample"]["horizon_ticks"],
                                 p["sample"]["fixed_checkpoint_stride"])
            worlds.append({"density":density,"seed":seed,"result":result})
            if seed == p["sample"]["seeds"][0]:
                bare = create_natural(seed,density,natural)
                assert bare.state_hash_full() == result["initial"]["hash"]
                assert bare.rng.fingerprint() == result["initial"]["rng"]
                bare.advance(p["sample"]["horizon_ticks"])
                bare.check()
                expected = result["final"]
                assert bare.state_hash_full() == expected["hash"]
                assert bare.rng.fingerprint() == expected["rng"]
                assert bare.rng.draws == expected["draws"]
                assert bare.energy() == expected["energy"]
                assert bare.dissipated == expected["dissipated"]
                assert bare.bonds_formed_total == expected["formed"]
                assert bare.bonds_broken_total == expected["broken"]
                replays.append({"density":density,"seed":seed,"hash":expected["hash"]})
            print(f"M611_WORLD={density}/{seed} pockets={len(result['pocket_episodes'])}",flush=True)
    assert len(worlds) == p["sample"]["expected_worlds"]
    result = {
        "schema":"alife-m6-11-natural-pocket-occupancy-results-v1",
        "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "worlds":worlds, "summary":summarize(worlds,p),
        "replays":replays, "physical_laws_unchanged":True
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("M611_SUMMARY="+json.dumps(result["summary"],sort_keys=True),flush=True)
    return result


if __name__ == "__main__":
    run()
