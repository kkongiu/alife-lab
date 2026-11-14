"""Interfaccia a riga di comando: run, resume, inspect.

Il motore è utilizzabile interamente senza interfaccia grafica.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from . import __version__
from .config import Config, ConfigError, load_config
from .metrics import MetricsRecorder, git_commit, runtime_versions
from .particles import InvariantError
from .persistence import CheckpointError, load_checkpoint, save_checkpoint
from .world import World

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _manifest(config: Config, command: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "tool": "alife",
        "tool_version": __version__,
        "command": command,
        "argv": sys.argv[1:],
        "cwd": str(Path.cwd()),
        "python_executable": sys.executable,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seed": config.seed,
        "config_hash": config.hash(),
        "config_schema_version": config.schema_version,
        "versions": runtime_versions(),
        "git_commit": git_commit(PROJECT_ROOT),
    }
    if extra:
        payload.update(extra)
    return payload


def _execute(
    world: World,
    steps: int,
    out_dir: Path,
    metrics_every: int,
    command_line: str,
    extra_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / "config.resolved.json", world.config.to_dict())
    _write_json(out_dir / "manifest.json", _manifest(world.config, command_line, extra_manifest))

    recorder = MetricsRecorder(out_dir, metrics_every)
    try:
        recorder.observe(world)
        world.advance(steps, observer=recorder.observe)
        summary = recorder.summary(world)
    finally:
        recorder.close()

    world.check()
    save_checkpoint(out_dir / "checkpoint.json", world)
    _write_json(out_dir / "summary.json", summary)
    return summary


def _report(summary: dict[str, Any], out_dir: Path, label: str) -> None:
    print(
        f"{label}: {summary['steps']} passi in {summary['duration_s']:.2f} s "
        f"({summary['steps_per_second']:.1f} passi/s), "
        f"{summary['particles_total']} particelle, "
        f"{summary['moves_total']} spostamenti, "
        f"energia {summary['energy']['total']}, "
        f"hash {summary['state_hash'][:16]}"
    )
    print(f"Artefatti in: {out_dir}")


def _cmd_run(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    if args.seed is not None:
        config = replace(config, seed=args.seed).validate()

    world = World.create(config)
    out_dir = Path(args.out)
    every = args.metrics_every or config.metrics.every
    summary = _execute(
        world,
        args.steps,
        out_dir,
        every,
        "run",
        {"config_source": str(Path(args.config).resolve())},
    )
    _report(summary, out_dir, "run")
    return 0


def _cmd_resume(args: argparse.Namespace) -> int:
    checkpoint_path = Path(args.checkpoint)
    world = load_checkpoint(checkpoint_path)
    initial_step = world.step
    out_dir = Path(args.out) if args.out else checkpoint_path.parent / "resume"
    every = args.metrics_every or world.config.metrics.every
    summary = _execute(
        world,
        args.steps,
        out_dir,
        every,
        "resume",
        {
            "resumed_from": str(checkpoint_path.resolve()),
            "initial_step": initial_step,
        },
    )
    _report(summary, out_dir, f"resume (da passo {initial_step})")
    return 0


def _cmd_inspect(args: argparse.Namespace) -> int:
    world = load_checkpoint(args.checkpoint)
    payload = {
        "checkpoint": str(Path(args.checkpoint).resolve()),
        "step": world.step,
        "moves_total": world.moves_total,
        "particles": world.counts(),
        "particles_total": len(world.store),
        "occupancy": round(world.occupancy(), 6),
        "energy_total": world.energy(),
        "state_hash": world.state_hash(),
        "rng_fingerprint": world.rng.fingerprint(),
        "config_hash": world.config.hash(),
        "invariants": world.validate() or "ok",
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alife",
        description="Motore di vita artificiale headless (milestone M1).",
    )
    parser.add_argument("--version", action="version", version=f"alife {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="crea un universo da configurazione ed evolve")
    run.add_argument("--config", required=True, help="file JSON di configurazione")
    run.add_argument("--steps", type=int, required=True, help="numero di passi da eseguire")
    run.add_argument("--out", required=True, help="directory di output")
    run.add_argument("--metrics-every", type=int, default=None, help="un record ogni N passi")
    run.add_argument("--seed", type=int, default=None, help="sovrascrive il seed della config")
    run.set_defaults(handler=_cmd_run)

    resume = subparsers.add_parser("resume", help="riprende da un checkpoint")
    resume.add_argument("--checkpoint", required=True, help="checkpoint.json di partenza")
    resume.add_argument("--steps", type=int, required=True, help="passi aggiuntivi")
    resume.add_argument("--out", default=None, help="directory di output (default: <ckpt>/resume)")
    resume.add_argument("--metrics-every", type=int, default=None)
    resume.set_defaults(handler=_cmd_resume)

    inspect = subparsers.add_parser("inspect", help="ispeziona un checkpoint senza evolvere")
    inspect.add_argument("--checkpoint", required=True)
    inspect.set_defaults(handler=_cmd_inspect)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    steps = getattr(args, "steps", None)
    if steps is not None and steps < 0:
        parser.error("--steps deve essere >= 0")
    if getattr(args, "metrics_every", None) is not None and args.metrics_every < 1:
        parser.error("--metrics-every deve essere >= 1")
    try:
        return int(args.handler(args))
    except (ConfigError, CheckpointError, InvariantError) as exc:
        print(f"errore: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"errore di I/O: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
