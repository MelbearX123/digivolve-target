"""Keys, labels and naming rules for the Digimon evolution data."""

RAW_DATA_PATH = "digimon_evolutions.json"
CLEAN_DATA_PATH = "digimon_evolutions_clean.json"

# Per-Digimon entry keys.
STAGE = "stage"
EVOLVES_INTO = "evolves_into"

# Requirement keys.
REQ_ITEM = "Req. Item"
JOGRESS = "Jogress"
RAW_JOGRESS_PREFIX = "Jogress Partner"
RAW_AT_LEAST = "≥"

# Form naming.
X_ANTIBODY_SUFFIX = " (X Antibody)"
OMNIMON_PREFIX = "Omnimon"


def base_form(name):
    """Strip the X Antibody suffix, if any."""
    return name.removesuffix(X_ANTIBODY_SUFFIX)


def is_x_antibody(name):
    """Whether the Digimon is an X Antibody form."""
    return name.endswith(X_ANTIBODY_SUFFIX)


def is_form_swap(src, dst):
    """Whether src -> dst is a form swap rather than a real evolution."""
    if src.startswith(OMNIMON_PREFIX) and dst.startswith(OMNIMON_PREFIX):
        return True
    return base_form(src) == base_form(dst)
