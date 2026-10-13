"""Tests for digivolve.search."""

import unittest

from digivolve.graph import Kind, Step
from digivolve.search import bfs


def adj(edges):
    """Build an adjacency list from (src, dst) pairs, all as evolutions."""
    graph = {}
    for src, dst in edges:
        graph.setdefault(src, []).append(Step(dst, Kind.EVOLVE))
        graph.setdefault(dst, [])
    return graph


class BfsTest(unittest.TestCase):
    """Tests for breadth-first search."""

    def test_start_is_target(self):
        """Start equal to target is an empty path."""
        self.assertEqual(bfs(adj([("A", "B")]), "A", "A"), [])

    def test_unreachable_returns_none(self):
        """No path returns None."""
        self.assertIsNone(bfs(adj([("A", "B"), ("C", "D")]), "A", "D"))

    def test_unknown_name_returns_none(self):
        """An unknown Digimon returns None."""
        self.assertIsNone(bfs(adj([("A", "B")]), "A", "Z"))

    def test_shortest_path_wins(self):
        """The route with fewer steps is chosen."""
        graph = adj([("A", "B"), ("B", "C"), ("C", "D"), ("A", "E"), ("E", "D")])
        self.assertEqual([s.to for s in bfs(graph, "A", "D")], ["E", "D"])

    def test_path_through_devolution(self):
        """Paths can go through a de-evolution."""
        graph = {
            "Greymon": [Step("Agumon", Kind.DEVOLVE)],
            "Agumon": [Step("Greymon", Kind.EVOLVE), Step("GeoGreymon", Kind.EVOLVE)],
            "GeoGreymon": [Step("Agumon", Kind.DEVOLVE)],
        }
        path = bfs(graph, "Greymon", "GeoGreymon")
        self.assertEqual([(s.to, s.kind) for s in path],
                         [("Agumon", Kind.DEVOLVE), ("GeoGreymon", Kind.EVOLVE)])


if __name__ == "__main__":
    unittest.main()
