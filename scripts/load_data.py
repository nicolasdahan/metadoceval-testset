"""Minimal loader for MetaDocEval JSON files.

The released test set is structured as one JSON file per (language pair,
system) combination, in `data/{lang}_{system}.json`. Each file maps a
perturbation type to a list of contrastive instances. See README.md for the
full schema.

Library usage:

    from scripts.load_data import load, iter_entries

    data = load("data/en_fr_aya.json")
    for entry in iter_entries(data, perturbation="tense_consistency"):
        src = entry["src"]
        sys, pert = entry["sys"], entry["sys_perturbed"]
        ...

CLI usage:

    python3 scripts/load_data.py data/en_fr_aya.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterator


def load(path: str | Path) -> dict:
    """Load a MetaDocEval JSON file and return the parsed dict."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def iter_entries(data: dict, perturbation: str | None = None) -> Iterator[dict]:
    """Yield contrastive instances.

    If `perturbation` is given, only yield entries from that perturbation type.
    Otherwise yield from all perturbation types in declaration order.
    """
    if perturbation is not None:
        if perturbation not in data:
            raise KeyError(
                f"Perturbation '{perturbation}' not found. Available: {sorted(data)}"
            )
        yield from data[perturbation]
        return
    for entries in data.values():
        yield from entries


def _summarise(path: Path) -> None:
    data = load(path)
    print(f"File: {path}")
    print(f"Perturbation categories: {len(data)}")
    total = 0
    for pert, entries in data.items():
        print(f"  {pert:<28} {len(entries):>6} instances")
        total += len(entries)
    print(f"  {'TOTAL':<28} {total:>6} instances")

    # Show one example
    first_cat = next(iter(data))
    if data[first_cat]:
        sample = data[first_cat][0]
        print(f"\nExample entry from '{first_cat}':")
        for k, v in sample.items():
            if isinstance(v, str) and len(v) > 80:
                print(f"  {k:<14}: {v[:80]}...")
            else:
                print(f"  {k:<14}: {v}")


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} data/en_fr_aya.json", file=sys.stderr)
        raise SystemExit(2)
    _summarise(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
