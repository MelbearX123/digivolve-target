"""Tests for scripts.clean_data."""

import unittest

from digivolve.schema import EVOLVES_INTO, JOGRESS, RAW_JOGRESS_PREFIX, REQ_ITEM, STAGE
from scripts.clean_data import clean, clean_reqs

ULFORCE = "UlforceVeedramon"
ULFORCE_X = "UlforceVeedramon (X Antibody)"


def entry(stage, *evolves_into):
    """Build one raw Digimon entry."""
    return {STAGE: stage, EVOLVES_INTO: [list(e) for e in evolves_into]}


class CleanDataTest(unittest.TestCase):
    """Tests for cleaning the raw scrape."""

    def test_numeric_requirements_become_ints(self):
        """"≥ N" and bare numbers become ints."""
        reqs = clean_reqs({"Agent Rank": "≥ 8", "ATK": "≥ 2280", "Valor(Agent Skills)": "46"})
        self.assertEqual(reqs, {"Agent Rank": 8, "ATK": 2280, "Valor(Agent Skills)": 46})

    def test_jogress_partners_pulled_into_list(self):
        """Jogress partners become one list, keeping their personality."""
        reqs = clean_reqs({
            "Agent Rank": "≥ 8",
            REQ_ITEM: "Digi-Egg of Miracles",
            f"{RAW_JOGRESS_PREFIX} #1": "BlackWarGreymon (Reckless)",
            f"{RAW_JOGRESS_PREFIX} #2": "MetalGarurumon (Black) (Friendly)",
        })
        self.assertEqual(reqs, {
            "Agent Rank": 8,
            REQ_ITEM: "Digi-Egg of Miracles",
            JOGRESS: ["BlackWarGreymon (Reckless)", "MetalGarurumon (Black) (Friendly)"],
        })

    def test_x_antibody_swaps_use_base_form_requirements(self):
        """Both directions of an X Antibody swap use the base form's requirements."""
        base = {"Agent Rank": "≥ 7", "HP": "≥ 2960", "SPD": "≥ 1980"}
        mislabeled = {"Agent Rank": "≥ 7", "SP": "≥ 2960", "Talent": "≥ 1980"}
        data = {
            ULFORCE: entry("Mega", (ULFORCE_X, mislabeled)),
            ULFORCE_X: entry("Mega", (ULFORCE, base)),
        }
        out = clean(data)
        expected = {"Agent Rank": 7, "HP": 2960, "SPD": 1980}
        self.assertEqual(out[ULFORCE][EVOLVES_INTO], [[ULFORCE_X, expected]])
        self.assertEqual(out[ULFORCE_X][EVOLVES_INTO], [[ULFORCE, expected]])

    def test_form_swaps_drop_jogress_but_real_jogress_keeps_it(self):
        """Swaps into Omnimon need no partners; real Jogress does."""
        omnimon = {
            "Agent Rank": "≥ 8",
            f"{RAW_JOGRESS_PREFIX} #1": "WarGreymon (Daring)",
            f"{RAW_JOGRESS_PREFIX} #2": "MetalGarurumon (Friendly)",
        }
        data = {
            "WarGreymon": entry("Mega", ("Omnimon", omnimon)),
            "Omnimon Zwart": entry("Mega +", ("Omnimon", omnimon)),
            "Omnimon": entry("Mega +"),
        }
        out = clean(data)
        self.assertEqual(out["WarGreymon"][EVOLVES_INTO][0][1][JOGRESS],
                         ["WarGreymon (Daring)", "MetalGarurumon (Friendly)"])
        self.assertEqual(out["Omnimon Zwart"][EVOLVES_INTO], [["Omnimon", {"Agent Rank": 8}]])
        self.assertEqual(out["Omnimon"], {STAGE: "Mega +", EVOLVES_INTO: []})


if __name__ == "__main__":
    unittest.main()
