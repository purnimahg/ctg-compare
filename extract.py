#!/usr/bin/env python3
"""
ctg-compare - step 2: extract

Pulls the same values field-map.md was filled in with, out of the saved
snapshots, and writes them to fields.csv.

This step does NOT compare anything. It only reads. Comparison is S3 onward.

Run:  python3 extract.py
"""

import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE / "fields.csv"

MISSING = "ABSENT"

# ---------------------------------------------------------------------------
# The checks. One path per row - a path is never allowed to mean two things.
# C7 and C11 each read two paths, so they get two rows. field-map.md records
# them on two lines too, so the two line up.
#
# THREE NOTATIONS, THREE DIFFERENT INSTRUCTIONS - this is the whole file:
#
#   a.b.c        one value at c
#   a.b[0].c     the FIRST element of list b, then c        <- just one
#   a.b[].c      EVERY element of list b, c from each       <- all of them
#
# The two checks written with [] are exactly the two that were misread by
# hand on 14 Sep. The notation was carrying the instruction and it was not
# loud enough. It has to be loud enough for the code.
# ---------------------------------------------------------------------------
CHECKS = [
    ("C1",   "phase",              "protocolSection.designModule.phases"),
    ("C2",   "minimum age",        "protocolSection.eligibilityModule.minimumAge"),
    ("C3",   "maximum age",        "protocolSection.eligibilityModule.maximumAge"),
    ("C4",   "sex eligible",       "protocolSection.eligibilityModule.sex"),
    ("C5",   "main measurement",   "protocolSection.outcomesModule.primaryOutcomes[0].measure"),
    ("C6",   "measurement timing", "protocolSection.outcomesModule.primaryOutcomes[0].timeFrame"),
    ("C7a",  "masking",            "protocolSection.designModule.designInfo.maskingInfo.masking"),
    ("C7b",  "who masked",         "protocolSection.designModule.designInfo.maskingInfo.whoMasked"),
    ("C8",   "arm types",          "protocolSection.armsInterventionsModule.armGroups[].type"),
    ("C9",   "results posted",     "protocolSection.statusModule.resultsFirstPostDateStruct.date"),
    ("C10",  "method described",   "protocolSection.outcomesModule.primaryOutcomes[0].description"),
    ("C11a", "document labels",    "documentSection.largeDocumentModule.largeDocs[].label"),
    ("C11b", "document dates",     "documentSection.largeDocumentModule.largeDocs[].date"),
]

STEP = re.compile(r"^([A-Za-z0-9_]+)(?:\[(\d*)\])?$")


class PathError(Exception):
    """The path is wrong, as opposed to the data being absent."""


def resolve(node, path):
    """Walk a dotted path. Returns (value, count).

    count is the number of list items the path collected, or None for a
    plain single value. Returns (MISSING, None) when a step simply is not
    there. Raises PathError when a step IS there but is the wrong shape,
    because that is a defect in the spec, not missing data from a sponsor.
    """
    for i, raw in enumerate(path.split(".")):
        m = STEP.match(raw)
        if not m:
            raise PathError(f"cannot parse step {raw!r} in path {path!r}")
        key, idx = m.group(1), m.group(2)

        if not isinstance(node, dict):
            raise PathError(f"expected an object at {'.'.join(path.split('.')[:i])!r} "
                            f"in {path!r}, found {type(node).__name__}")
        if key not in node:
            return MISSING, None
        node = node[key]

        if m.group(0).endswith("]"):
            if not isinstance(node, list):
                raise PathError(f"path {path!r} uses [] at {key!r} but that is "
                                f"a {type(node).__name__}, not a list")
            rest = path.split(".")[i + 1:]
            if idx != "":                      # [0] - exactly one element
                n = int(idx)
                if n >= len(node):
                    return MISSING, len(node)
                node = node[n]
                if rest:
                    sub, _ = resolve(node, ".".join(rest))
                    return sub, None
                return node, None
            # []  - every element
            collected = []
            for item in node:
                if rest:
                    sub, _ = resolve(item, ".".join(rest))
                    collected.append(sub)
                else:
                    collected.append(item)
            return collected, len(collected)

    return node, (len(node) if isinstance(node, list) else None)


def render(value):
    if value is MISSING or value == MISSING:
        return MISSING
    if isinstance(value, list):
        return ", ".join(render(v) for v in value) if value else "EMPTY LIST"
    return str(value)


def load():
    """Newest saved snapshot per trial."""
    fname = re.compile(r"^(NCT\d+)_(\d{4}-\d{2}-\d{2})\.json$")
    best = {}
    for f in sorted(DATA.glob("*.json")):
        m = fname.match(f.name)
        if m and (m.group(1) not in best or best[m.group(1)][0] < m.group(2)):
            best[m.group(1)] = (m.group(2), f)
    return {k: (v[0], json.loads(v[1].read_text()), v[1].name)
            for k, v in sorted(best.items())}


def main():
    studies = load()
    if len(studies) < 2:
        print("Need at least two saved snapshots in data/. Run fetch.py.")
        sys.exit(1)

    ids = list(studies)
    print("Reading the newest snapshot of each trial:")
    for n in ids:
        print(f"   {n}   {studies[n][2]}")
    print()

    rows = []
    for cid, name, path in CHECKS:
        row = {"check": cid, "field": name, "path": path}
        absent_everywhere = True
        for label, nct in zip("AB", ids):
            try:
                val, count = resolve(studies[nct][1], path)
            except PathError as e:
                print(f"PATH ERROR in {cid}: {e}")
                sys.exit(1)
            if val != MISSING:
                absent_everywhere = False
            row[f"{label}_count"] = "-" if count is None else str(count)
            row[f"{label}_value"] = render(val)

        # A path absent from EVERY study is almost certainly a typo, not real
        # absence. Genuine absence is asymmetric: a sponsor reports it and
        # another does not. Symmetric absence means we spelled it wrong, and
        # a silent blank there would be indistinguishable from a real finding.
        if absent_everywhere:
            print(f"PATH ERROR in {cid}: {path!r} is absent from ALL "
                  f"{len(ids)} studies.")
            print("  That is far more likely a misspelled path than a real "
                  "finding. Fix the path, or if the absence is genuine, say so "
                  "explicitly in CHECKS. Nothing written.")
            sys.exit(1)

        rows.append(row)

    cols = ["check", "field", "path", "A_count", "A_value", "B_count", "B_value"]
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    w = max(len(r["A_value"]) for r in rows)
    for r in rows:
        print(f"{r['check']:<5} {r['field']:<20} "
              f"A[{r['A_count']}] {r['A_value'][:58]:<58}  "
              f"B[{r['B_count']}] {r['B_value'][:58]}")

    print(f"\n{len(rows)} rows written to  {OUT.name}")
    print("Now check every value against field-map.md by eye. That is the test.")


if __name__ == "__main__":
    main()
