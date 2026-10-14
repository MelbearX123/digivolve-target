"""Tests for api.main."""

import unittest

from fastapi.testclient import TestClient

from api.main import API_PREFIX, create_app
from digivolve.graph import Kind
from digivolve.schema import EVOLVES_INTO, JOGRESS, STAGE

DIGIMON_URL = f"{API_PREFIX}/digimon"
PATH_URL = f"{API_PREFIX}/path"

DATA = {
    "Koromon": {STAGE: "In-Training II", EVOLVES_INTO: [["Agumon", {"Agent Rank": 1}]]},
    "Agumon": {STAGE: "Rookie", EVOLVES_INTO: [
        ["Greymon", {"Agent Rank": 2, "ATK": 120}],
        ["Omnimon", {"Agent Rank": 8, JOGRESS: ["Agumon (Daring)", "Gabumon (Friendly)"]}],
    ]},
    "Greymon": {STAGE: "Champion", EVOLVES_INTO: []},
    "Omnimon": {STAGE: "Mega +", EVOLVES_INTO: []},
    "Lonelymon": {STAGE: "Mega", EVOLVES_INTO: []},
}


class ApiTest(unittest.TestCase):
    """Tests for the HTTP endpoints."""

    def setUp(self):
        self.client = TestClient(create_app(DATA))

    def test_list_digimon_sorted_with_stage(self):
        """/digimon lists every Digimon with its stage, sorted by name."""
        res = self.client.get(DIGIMON_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual([d["name"] for d in res.json()],
                         ["Agumon", "Greymon", "Koromon", "Lonelymon", "Omnimon"])
        self.assertEqual(res.json()[0], {"name": "Agumon", "stage": "Rookie"})

    def test_path_includes_kind_and_requirements(self):
        """/path returns each step with its kind and requirements."""
        res = self.client.get(PATH_URL, params={"start": "Greymon", "target": "Omnimon"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {
            "start": "Greymon",
            "target": "Omnimon",
            "steps": [
                {"to": "Agumon", "kind": Kind.DEVOLVE, "requirements": {}},
                {"to": "Omnimon", "kind": Kind.EVOLVE, "requirements": {
                    "Agent Rank": 8, JOGRESS: ["Agumon (Daring)", "Gabumon (Friendly)"]}},
            ],
        })

    def test_unknown_digimon_is_404(self):
        """An unknown name is a 404 that names it."""
        res = self.client.get(PATH_URL, params={"start": "Agumon", "target": "Pikachu"})
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()["detail"], "Unknown Digimon: Pikachu")

    def test_no_path_is_404(self):
        """Unreachable targets are a 404."""
        res = self.client.get(PATH_URL, params={"start": "Agumon", "target": "Lonelymon"})
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()["detail"], "No path from Agumon to Lonelymon")

    def test_missing_param_is_422(self):
        """Both query parameters are required."""
        self.assertEqual(self.client.get(PATH_URL, params={"start": "Agumon"}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
