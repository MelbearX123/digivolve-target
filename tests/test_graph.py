"""Tests for digivolve.graph."""

import unittest

from digivolve.graph import Kind, Step, build_graph
from digivolve.schema import EVOLVES_INTO, STAGE


def entry(*evolves_into):
    """Build one cleaned Digimon entry."""
    return {STAGE: "Mega", EVOLVES_INTO: [list(e) for e in evolves_into]}


class BuildGraphTest(unittest.TestCase):
    """Tests for building the adjacency list."""

    def test_evolution_adds_free_devolution(self):
        """An evolution adds a free reverse de-evolution."""
        graph = build_graph({
            "Agumon": entry(("Greymon", {"Agent Rank": 1})),
            "Greymon": entry(),
        })
        self.assertEqual(graph["Agumon"], [Step("Greymon", Kind.EVOLVE)])
        self.assertEqual(graph["Agumon"][0].requirements, {"Agent Rank": 1})
        self.assertEqual(graph["Greymon"], [Step("Agumon", Kind.DEVOLVE)])
        self.assertEqual(graph["Greymon"][0].requirements, {})

    def test_form_swaps_are_not_reversed(self):
        """Form swaps keep their own two-way steps."""
        graph = build_graph({
            "Gallantmon": entry(("Gallantmon (X Antibody)", {})),
            "Gallantmon (X Antibody)": entry(("Gallantmon", {})),
        })
        self.assertEqual(graph["Gallantmon"], [Step("Gallantmon (X Antibody)", Kind.SWAP)])
        self.assertEqual(graph["Gallantmon (X Antibody)"], [Step("Gallantmon", Kind.SWAP)])

    def test_two_way_mode_change_has_no_duplicate_devolution(self):
        """An existing reverse evolution is not duplicated."""
        graph = build_graph({
            "Agunimon": entry(("BurningGreymon", {})),
            "BurningGreymon": entry(("Agunimon", {})),
        })
        self.assertEqual(graph["BurningGreymon"], [Step("Agunimon", Kind.EVOLVE)])

    def test_kinds_are_enum_members(self):
        """Step kinds are Kind members, not plain strings."""
        graph = build_graph({
            "Agumon": entry(("Greymon", {})),
            "Greymon": entry(("Greymon (X Antibody)", {})),
            "Greymon (X Antibody)": entry(),
        })
        for steps in graph.values():
            for step in steps:
                self.assertIsInstance(step.kind, Kind)


if __name__ == "__main__":
    unittest.main()
