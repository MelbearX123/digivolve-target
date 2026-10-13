import unittest

from scripts.clean_data import clean, clean_reqs, is_form_swap


def entry(stage, *evolves_into):
    return {"stage": stage, "evolves_into": [list(e) for e in evolves_into]}


class CleanDataTest(unittest.TestCase):
    def test_numeric_requirements_become_ints(self):
        reqs = clean_reqs({"Agent Rank": "≥ 8", "ATK": "≥ 2280", "Valor(Agent Skills)": "46"})
        self.assertEqual(reqs, {"Agent Rank": 8, "ATK": 2280, "Valor(Agent Skills)": 46})

    def test_jogress_partners_pulled_into_list(self):
        reqs = clean_reqs({
            "Agent Rank": "≥ 8",
            "Req. Item": "Digi-Egg of Miracles",
            "Jogress Partner #1": "BlackWarGreymon (Reckless)",
            "Jogress Partner #2": "MetalGarurumon (Black) (Friendly)",
        })
        self.assertEqual(reqs, {
            "Agent Rank": 8,
            "Req. Item": "Digi-Egg of Miracles",
            "Jogress": ["BlackWarGreymon (Reckless)", "MetalGarurumon (Black) (Friendly)"],
        })

    def test_is_form_swap(self):
        self.assertTrue(is_form_swap("Gallantmon", "Gallantmon (X Antibody)"))
        self.assertTrue(is_form_swap("Gallantmon (X Antibody)", "Gallantmon"))
        self.assertTrue(is_form_swap("Omnimon", "Omnimon Zwart"))
        self.assertFalse(is_form_swap("WarGreymon", "Omnimon"))
        self.assertFalse(is_form_swap("Gallantmon", "Jesmon (X Antibody)"))

    def test_x_antibody_swaps_use_base_form_requirements(self):
        base = {"Agent Rank": "≥ 7", "HP": "≥ 2960", "SPD": "≥ 1980"}
        mislabeled = {"Agent Rank": "≥ 7", "SP": "≥ 2960", "Talent": "≥ 1980"}
        data = {
            "UlforceVeedramon": entry("Mega", ("UlforceVeedramon (X Antibody)", mislabeled)),
            "UlforceVeedramon (X Antibody)": entry("Mega", ("UlforceVeedramon", base)),
        }
        out = clean(data)
        expected = {"Agent Rank": 7, "HP": 2960, "SPD": 1980}
        self.assertEqual(out["UlforceVeedramon"]["evolves_into"], [["UlforceVeedramon (X Antibody)", expected]])
        self.assertEqual(out["UlforceVeedramon (X Antibody)"]["evolves_into"], [["UlforceVeedramon", expected]])

    def test_form_swaps_drop_jogress_but_real_jogress_keeps_it(self):
        omnimon = {
            "Agent Rank": "≥ 8",
            "Jogress Partner #1": "WarGreymon (Daring)",
            "Jogress Partner #2": "MetalGarurumon (Friendly)",
        }
        data = {
            "WarGreymon": entry("Mega", ("Omnimon", omnimon)),
            "Omnimon Zwart": entry("Mega +", ("Omnimon", omnimon)),
            "Omnimon": entry("Mega +"),
        }
        out = clean(data)
        self.assertEqual(out["WarGreymon"]["evolves_into"][0][1]["Jogress"],
                         ["WarGreymon (Daring)", "MetalGarurumon (Friendly)"])
        self.assertEqual(out["Omnimon Zwart"]["evolves_into"], [["Omnimon", {"Agent Rank": 8}]])
        self.assertEqual(out["Omnimon"], {"stage": "Mega +", "evolves_into": []})


if __name__ == "__main__":
    unittest.main()
