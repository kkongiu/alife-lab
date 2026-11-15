"""Controlli di validazione (M5).

Questo pacchetto è **isolato** dall'universo di scoperta: il motore
(`alife.world`, `alife.dynamics`, `alife.chemistry`, `alife.structures`) non
importa nulla da qui. Un test statico lo verifica.

Contiene:

- `positive`: un sistema di copiatura noto e dichiarato, usato come benchmark;
- `negatives`: tre controlli negativi (immobilità, aggregazione casuale,
  reazioni reversibili senza ereditarietà).

Le fixture sono costruite da codice con posizioni fisse e parametri espliciti:
sono versionate insieme al test che le usa.
"""

from .fixtures import (
    FIXTURE_VERSION,
    TemplateCopier,
    negative_burst,
    negative_immobile,
    negative_random_aggregation,
    negative_reversible,
    negative_single_species,
    positive_world,
)

__all__ = [
    "FIXTURE_VERSION",
    "TemplateCopier",
    "negative_burst",
    "negative_immobile",
    "negative_random_aggregation",
    "negative_reversible",
    "negative_single_species",
    "positive_world",
]
