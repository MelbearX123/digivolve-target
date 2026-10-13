"""HTTP API for finding evolution paths.

Run from server/: uvicorn api.main:app --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from digivolve.graph import Kind, build_graph, load_data
from digivolve.schema import STAGE
from digivolve.search import bfs

Requirements = dict[str, int | str | list[str]]


class Digimon(BaseModel):
    """A Digimon and its stage."""
    name: str
    stage: str


class PathStep(BaseModel):
    """One step of a path."""
    to: str
    kind: Kind
    requirements: Requirements


class PathResponse(BaseModel):
    """The fewest steps from start to target."""
    start: str
    target: str
    steps: list[PathStep]


def create_app(data) -> FastAPI:
    """Build the app around the given cleaned evolution data."""
    api = FastAPI(title="Digivolve")
    graph = build_graph(data)
    digimon = sorted(
        (Digimon(name=name, stage=entry[STAGE]) for name, entry in data.items()),
        key=lambda d: d.name.lower(),
    )

    @api.get("/digimon")
    def list_digimon() -> list[Digimon]:
        """All Digimon, sorted by name."""
        return digimon

    @api.get("/path")
    def find_path(start: str, target: str) -> PathResponse:
        """The fewest evolve/devolve/swap steps from start to target."""
        for name in (start, target):
            if name not in graph:
                raise HTTPException(status_code=404, detail=f"Unknown Digimon: {name}")
        steps = bfs(graph, start, target)
        if steps is None:
            raise HTTPException(status_code=404, detail=f"No path from {start} to {target}")
        return PathResponse(
            start=start,
            target=target,
            steps=[PathStep(to=s.to, kind=s.kind, requirements=s.requirements) for s in steps],
        )

    return api


app = create_app(load_data())
