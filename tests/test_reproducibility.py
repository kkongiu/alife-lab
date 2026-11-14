"""Riproducibilità: stesso seed, stesso stato, stesso risultato."""

from __future__ import annotations

import json

from alife.config import Config, load_config
from alife.world import World
from support import BASELINE, make_config


def test_same_seed_same_result() -> None:
    first = World.create(make_config(seed=1234))
    second = World.create(make_config(seed=1234))
    first.advance(120)
    second.advance(120)
    assert first.snapshot() == second.snapshot()
    assert first.state_hash() == second.state_hash()


def test_different_seed_different_result() -> None:
    first = World.create(make_config(seed=1))
    second = World.create(make_config(seed=2))
    first.advance(40)
    second.advance(40)
    assert first.state_hash() != second.state_hash()


def test_initial_placement_is_seed_deterministic() -> None:
    first = World.create(make_config(seed=99))
    second = World.create(make_config(seed=99))
    assert first.store.records() == second.store.records()


def test_repeated_advance_matches_single_call() -> None:
    stepwise = World.create(make_config(seed=5))
    oneshot = World.create(make_config(seed=5))
    for _ in range(5):
        stepwise.advance(6)
    oneshot.advance(30)
    assert stepwise.snapshot() == oneshot.snapshot()


def test_baseline_config_is_reproducible() -> None:
    config = Config.from_dict(json.loads(BASELINE.read_text())).validate()
    first = World.create(config)
    second = World.create(config)
    first.advance(25)
    second.advance(25)
    assert first.state_hash() == second.state_hash()
    assert first.counts() == second.counts()


def test_m1_run_reproduces_the_published_hash() -> None:
    """Golden hash: il codice M2 deve riprodurre un risultato M1 al passo 1000.

    Il valore proviene da `runs/baseline/metrics.jsonl`, prodotto dalla milestone
    M1: è la verifica che l'evoluzione del motore non abbia cambiato la semantica
    del caso senza chimica.
    """
    world = World.create(load_config(BASELINE))
    world.advance(1000)
    assert world.state_hash() == (
        "3f4a885afe5f4e2d6db7a6f44eece5a9f566983aa95df057d605daab25d553af"
    )
    assert world.moves_total > 0
    assert not world.store.bonds
