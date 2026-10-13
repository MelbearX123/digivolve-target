"""Tests for digivolve.schema."""

import unittest

from digivolve.schema import base_form, is_form_swap, is_x_antibody


class SchemaTest(unittest.TestCase):
    """Tests for the form naming rules."""

    def test_is_form_swap(self):
        """X Antibody pairs and Omnimon forms are swaps; Jogress is not."""
        self.assertTrue(is_form_swap("Gallantmon", "Gallantmon (X Antibody)"))
        self.assertTrue(is_form_swap("Gallantmon (X Antibody)", "Gallantmon"))
        self.assertTrue(is_form_swap("Omnimon", "Omnimon Zwart"))
        self.assertFalse(is_form_swap("WarGreymon", "Omnimon"))
        self.assertFalse(is_form_swap("Gallantmon", "Jesmon (X Antibody)"))

    def test_x_antibody_helpers(self):
        """base_form strips only the X Antibody suffix."""
        self.assertTrue(is_x_antibody("Jesmon (X Antibody)"))
        self.assertFalse(is_x_antibody("MetalGarurumon (Black)"))
        self.assertEqual(base_form("Jesmon (X Antibody)"), "Jesmon")
        self.assertEqual(base_form("MetalGarurumon (Black)"), "MetalGarurumon (Black)")


if __name__ == "__main__":
    unittest.main()
