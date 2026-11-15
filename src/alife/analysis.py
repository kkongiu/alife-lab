"""Analisi combinata: tracker delle strutture e rilevatore di copie.

L'analisi è un livello separato dal motore, ma il suo stato è parte
dell'esperimento: per riprendere un run senza perdere eventi e discendenze va
salvato e ripristinato insieme al mondo. Il file `analysis.json` accompagna il
checkpoint e contiene:

- il tracker completo (strutture attive, contatori, vite concluse, firme viste);
- il rilevatore completo (criteri, candidati, verifiche di persistenza pendenti,
  generazioni);
- il passo a cui lo stato si riferisce, per rifiutare un ripristino incoerente.

Il file è scritto in modo atomico, come i checkpoint.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from .replication import ReplicationDetector
from .structures import Tracker

if TYPE_CHECKING:
    from .world import World

ANALYSIS_FORMAT = "alife-analysis"
ANALYSIS_SCHEMA = 1


class AnalysisError(ValueError):
    """Stato di analisi mancante, incoerente o non ripristinabile."""


class Analysis:
    """Osserva un mondo con tracker e rilevatore, con stato serializzabile."""

    def __init__(
        self,
        out_dir: str | Path | None = None,
        detector: ReplicationDetector | None = None,
    ) -> None:
        self.tracker = Tracker(out_dir)
        self.detector = detector if detector is not None else ReplicationDetector()

    def observe(self, world: "World") -> None:
        self.tracker.observe(world)
        self.detector.observe(world, self.tracker)

    def summary(self) -> dict:
        return {
            "structures": self.tracker.summary(),
            "replication": self.detector.summary(),
        }

    def to_dict(self) -> dict:
        return {
            "format": ANALYSIS_FORMAT,
            "schema_version": ANALYSIS_SCHEMA,
            "step": self.tracker.last_step,
            "tracker": self.tracker.to_dict(),
            "detector": self.detector.to_dict(),
        }

    @classmethod
    def from_dict(
        cls, data: object, out_dir: str | Path | None = None
    ) -> "Analysis":
        if not isinstance(data, dict):
            raise AnalysisError("analysis: atteso un oggetto JSON")
        if data.get("format") != ANALYSIS_FORMAT:
            raise AnalysisError(f"analysis: formato inatteso {data.get('format')!r}")
        if data.get("schema_version") != ANALYSIS_SCHEMA:
            raise AnalysisError(
                f"analysis: schema {data.get('schema_version')!r}, atteso {ANALYSIS_SCHEMA}"
            )
        analysis = cls.__new__(cls)
        try:
            analysis.tracker = Tracker.from_dict(data["tracker"], out_dir)
            analysis.detector = ReplicationDetector.from_dict(data["detector"])
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, AnalysisError):
                raise
            raise AnalysisError(f"analysis: stato non valido ({exc})") from exc
        return analysis

    def save(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.to_dict(), ensure_ascii=True)
        handle, temporary = tempfile.mkstemp(
            dir=str(destination.parent), prefix=destination.name + ".", suffix=".tmp"
        )
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                stream.write(payload)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        except BaseException:
            if os.path.exists(temporary):
                os.unlink(temporary)
            raise
        return destination

    @classmethod
    def load(cls, path: str | Path, out_dir: str | Path | None = None) -> "Analysis":
        source = Path(path)
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise AnalysisError(f"analysis non trovato: {source}") from exc
        except json.JSONDecodeError as exc:
            raise AnalysisError(f"analysis JSON non valido ({source}): {exc}") from exc
        return cls.from_dict(data, out_dir)

    def check_step(self, step: int) -> None:
        """Rifiuta un ripristino se lo stato non è al passo del mondo."""
        if self.tracker.last_step != step:
            raise AnalysisError(
                f"analysis: stato al passo {self.tracker.last_step}, mondo al passo {step}"
            )

    def close(self) -> None:
        self.tracker.close()
