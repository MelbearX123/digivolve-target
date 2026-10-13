"""Build a two-way adjacency list from the cleaned evolution data."""

import json
from dataclasses import dataclass, field
from enum import StrEnum

from digivolve.schema import CLEAN_DATA_PATH, EVOLVES_INTO, is_form_swap


class Kind(StrEnum):
    """How a Step moves between Digimon."""
    EVOLVE = "evolve"
    DEVOLVE = "devolve"
    SWAP = "swap"


@dataclass(frozen=True)
class Step:
    """One move to another Digimon, with what it requires."""
    to: str
    kind: Kind
    requirements: dict = field(default_factory=dict, compare=False)


def build_graph(data):
    """Map each Digimon to the Steps it can take.

    Every evolution A -> B also adds a free de-evolution B -> A, unless the
    data already has B -> A (form swaps and other two-way mode changes).
    """
    graph = {name: [] for name in data}
    forward = {(src, dst) for src, entry in data.items() for dst, _ in entry[EVOLVES_INTO]}

    for src, entry in data.items():
        for dst, reqs in entry[EVOLVES_INTO]:
            kind = Kind.SWAP if is_form_swap(src, dst) else Kind.EVOLVE
            graph[src].append(Step(dst, kind, reqs))
            if (dst, src) not in forward:
                graph[dst].append(Step(src, Kind.DEVOLVE))
    return graph


def load_graph(path=CLEAN_DATA_PATH):
    """Load the cleaned JSON file and build its graph."""
    with open(path, encoding="utf-8") as f:
        return build_graph(json.load(f))
