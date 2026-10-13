"""Shortest path search over the evolution graph."""

from collections import deque

from digivolve.graph import Step


def bfs(graph: dict[str, list[Step]], start: str, target: str) -> list[Step] | None:
    """Return the fewest Steps from start to target, or None if unreachable.

    graph is an adjacency list: {name: [Step, ...]}.
    """
    if start not in graph or target not in graph:
        return None

    came_from: dict[str, tuple[str, Step] | None] = {start: None}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current == target:
            break
        for step in graph[current]:
            if step.to not in came_from:
                came_from[step.to] = (current, step)
                queue.append(step.to)

    if target not in came_from:
        return None

    path = []
    node = target
    while (link := came_from[node]) is not None:
        node, step = link
        path.append(step)
    path.reverse()
    return path
