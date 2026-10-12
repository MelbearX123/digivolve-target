"""Clean the raw Grindosaur scrape into the format used by the path finder.

Fixes applied:
  - Numeric requirements are stored as ints ("≥ 2280" -> 2280).
  - Jogress partners are pulled into a single "Jogress" list.
  - Form swaps (X Antibody <-> base form, and between Omnimon forms) never
    require Jogress partners.
  - X Antibody swaps (both directions) use the base form's requirements,
    since Grindosaur mislabels the X Antibody ones.

Usage: python scripts/clean_data.py [raw.json] [out.json]
"""

import json
import sys

X_SUFFIX = " (X Antibody)"
STRING_REQS = {"Req. Item"}


def is_form_swap(src, dst):
    if src.startswith("Omnimon") and dst.startswith("Omnimon"):
        return True
    return src.removesuffix(X_SUFFIX) == dst.removesuffix(X_SUFFIX)


def clean_reqs(raw):
    reqs = {}
    jogress = []
    for key, value in raw.items():
        if key.startswith("Jogress Partner"):
            jogress.append(value)
        elif key in STRING_REQS:
            reqs[key] = value
        else:
            reqs[key] = int(value.removeprefix("≥").strip())
    if jogress:
        reqs["Jogress"] = jogress
    return reqs


def target_requirements(data):
    """Requirements for evolving into each Digimon (identical across sources)."""
    reqs = {}
    for entry in data.values():
        for dst, raw in entry["evolves_into"]:
            reqs.setdefault(dst, raw)
    return reqs


def clean(data):
    base_reqs = target_requirements(data)
    out = {}
    for src, entry in data.items():
        evolves_into = []
        for dst, raw in entry["evolves_into"]:
            if X_SUFFIX in src or X_SUFFIX in dst:
                raw = base_reqs[dst.removesuffix(X_SUFFIX)]
            reqs = clean_reqs(raw)
            if is_form_swap(src, dst):
                reqs.pop("Jogress", None)
            evolves_into.append([dst, reqs])
        out[src] = {"stage": entry["stage"], "evolves_into": evolves_into}
    return out


def main():
    raw_path = sys.argv[1] if len(sys.argv) > 1 else "digimon_evolutions.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "digimon_evolutions_clean.json"
    with open(raw_path, encoding="utf-8") as f:
        data = json.load(f)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(clean(data), f, indent=1, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
