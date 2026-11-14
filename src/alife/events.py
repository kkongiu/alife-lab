"""Registro eventi della chimica: un file JSONL per run, attivabile dalla CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TextIO


class EventLog:
    """Scrive gli eventi di legame in formato JSON Lines."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._stream: TextIO = self.path.open("w", encoding="utf-8")

    def emit(self, event) -> None:
        self._stream.write(
            json.dumps(
                {
                    "kind": event.kind,
                    "step": event.step,
                    "id_a": event.id_a,
                    "id_b": event.id_b,
                    "energy": event.energy,
                    "catalyzed": bool(event.catalyzed),
                },
                ensure_ascii=True,
            )
            + "\n"
        )

    def close(self) -> None:
        self._stream.close()

    def __enter__(self) -> "EventLog":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
