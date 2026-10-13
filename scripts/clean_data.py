"""Clean the raw Grindosaur scrape into the format used by the path finder.

Fixes applied:
  - Numeric requirements are stored as ints ("≥ 2280" -> 2280).
  - Jogress partners are pulled into a single "Jogress" list.
  - Form swaps (X Antibody <-> base form, and between Omnimon forms) never
    require Jogress partners.
  - X Antibody swaps (both directions) use the base form's requirements,
    since Grindosaur mislabels the X Antibody ones.

Usage: python -m scripts.clean_data [raw.json] [out.json]
"""

import json
import sys

from digivolve.schema import (
    CLEAN_DATA_PATH,
    EVOLVES_INTO,
    JOGRESS,
    RAW_AT_LEAST,
    RAW_DATA_PATH,
    RAW_JOGRESS_PREFIX,
    REQ_ITEM,
    STAGE,
    base_form,
    is_form_swap,
    is_x_antibody,
)

STRING_REQS = {REQ_ITEM}


def clean_reqs(raw):
    """Convert one raw requirement dict to ints plus a Jogress list."""
    reqs = {}
    jogress = []
    for key, value in raw.items():
        if key.startswith(RAW_JOGRESS_PREFIX):
            jogress.append(value)
        elif key in STRING_REQS:
            reqs[key] = value
        else:
            reqs[key] = int(value.removeprefix(RAW_AT_LEAST).strip())
    if jogress:
        reqs[JOGRESS] = jogress
    return reqs


def target_requirements(data):
    """Requirements for evolving into each Digimon (identical across sources)."""
    reqs = {}
    for entry in data.values():
        for dst, raw in entry[EVOLVES_INTO]:
            reqs.setdefault(dst, raw)
    return reqs


def clean(data):
    """Return the cleaned copy of the raw scrape."""
    base_reqs = target_requirements(data)
    out = {}
    for src, entry in data.items():
        evolves_into = []
        for dst, raw in entry[EVOLVES_INTO]:
            if is_x_antibody(src) or is_x_antibody(dst):
                raw = base_reqs[base_form(dst)]
            reqs = clean_reqs(raw)
            if is_form_swap(src, dst):
                reqs.pop(JOGRESS, None)
            evolves_into.append([dst, reqs])
        out[src] = {STAGE: entry[STAGE], EVOLVES_INTO: evolves_into}
    return out


def main():
    """Read the raw scrape and write the cleaned file."""
    raw_path = sys.argv[1] if len(sys.argv) > 1 else RAW_DATA_PATH
    out_path = sys.argv[2] if len(sys.argv) > 2 else CLEAN_DATA_PATH
    with open(raw_path, encoding="utf-8") as f:
        data = json.load(f)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(clean(data), f, indent=1, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
