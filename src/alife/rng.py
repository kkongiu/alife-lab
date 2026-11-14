"""Generatore casuale deterministico con stato serializzabile.

Scelta: PCG64 di NumPy, usato esclusivamente tramite ``random_raw()``.
``random_raw`` restituisce un uint64 e il flusso e' stabile fra versioni di NumPy,
al contrario dei metodi di distribuzione (``random``, ``integers``) che possono
cambiare implementazione. Ogni decisione della simulazione e' quindi espressa in
aritmetica intera sui bit grezzi del generatore.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

import numpy as np

STATE_KEYS = ("bit_generator", "state", "has_uint32", "uinteger")


class RNGError(ValueError):
    """Stato del generatore mancante o incoerente."""


class RNG:
    """Wrapper minimo e serializzabile attorno a NumPy PCG64."""

    __slots__ = ("_bitgen", "draws")

    def __init__(self, seed: int) -> None:
        if seed < 0:
            raise RNGError("seed negativa")
        self._bitgen = np.random.PCG64(int(seed))
        self.draws = 0

    def raw(self) -> int:
        """Prossimo uint64 del flusso (0 .. 2**64-1)."""
        self.draws += 1
        return int(self._bitgen.random_raw())

    def state(self) -> dict[str, Any]:
        state = self._bitgen.state
        return {
            "bit_generator": state["bit_generator"],
            "state": {key: int(value) for key, value in state["state"].items()},
            "has_uint32": int(state["has_uint32"]),
            "uinteger": int(state["uinteger"]),
        }

    def set_state(self, state: Mapping[str, Any]) -> None:
        try:
            missing = [key for key in STATE_KEYS if key not in state]
            if missing:
                raise RNGError(f"stato RNG incompleto: mancano {missing}")
            inner = state["state"]
            if not isinstance(inner, Mapping):
                raise RNGError("stato RNG: campo 'state' non è un oggetto")
            self._bitgen.state = {
                "bit_generator": str(state["bit_generator"]),
                "state": {key: int(value) for key, value in inner.items()},
                "has_uint32": int(state["has_uint32"]),
                "uinteger": int(state["uinteger"]),
            }
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, RNGError):
                raise
            raise RNGError(f"stato RNG non valido: {exc}") from exc

    def fingerprint(self) -> str:
        payload = json.dumps(self.state(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RNG):
            return NotImplemented
        return self.fingerprint() == other.fingerprint()
