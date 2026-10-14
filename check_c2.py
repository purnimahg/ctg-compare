#!/usr/bin/env python3
"""
ctg-compare - C2, minimum age. The first check that makes a claim.

Decision recorded in acceptance/S3-C2-minimum-age.md: option (b) -
convert to a common unit (years), then compare. That choice buys the
ability to handle paediatric trials, which state ages in months or days
and are not malformed. It costs a conversion step, and a conversion step
is a new place to be silently wrong - so the output shows the raw string
AND what it was read as, on every line, always.

Run:  python3 check_c2.py              compare the newest saved snapshots
      python3 check_c2.py --selftest   run the four acceptance scenarios
"""

import copy
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
PATH = "protocolSection.eligibilityModule.minimumAge"

SAME, DIFFERENT, NOT_REPORTED = "SAME", "DIFFERENT", "NOT REPORTED"
UNPARSED = "UNPARSED"          # value present but not understood - never guess

TOLERANCE = 0.01               # years

# ClinicalTrials.gov writes ages as "<number> <Unit>", unit singular or plural.
PER_YEAR = {"year": 1.0, "month": 12.0, "week": 52.1775, "day": 365.25}
AGE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s+(year|month|week|day)s?\s*$", re.I)


def dig(record, path):
    node = record
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def to_years(raw):
    """Returns (years, note). years is None when the string is not understood.

    Never guesses. 'N/A', '16', '16 fortnights' all come back unparsed rather
    than being coerced into a number, because a wrong number here is worse
    than no number.
    """
    if raw is None:
        return None, "field absent"
    m = AGE.match(str(raw))
    if not m:
        return None, f"could not read {raw!r} as an age"
    value, unit = float(m.group(1)), m.group(2).lower()
    return value / PER_YEAR[unit], None


def check(record_a, record_b, label_a="A", label_b="B"):
    raw_a, raw_b = dig(record_a, PATH), dig(record_b, PATH)
    yrs_a, note_a = to_years(raw_a)
    yrs_b, note_b = to_years(raw_b)

    lines = [f"    {PATH}"]
    for lab, raw, yrs, note in ((label_a, raw_a, yrs_a, note_a),
                                (label_b, raw_b, yrs_b, note_b)):
        shown = "-- field absent --" if raw is None else f'"{raw}"'
        read = f"read as {yrs:.2f} years" if yrs is not None else f"NOT READ: {note}"
        lines.append(f"    {lab}   {shown:<24} {read}")

    if raw_a is None or raw_b is None:
        verdict = NOT_REPORTED
        which = [l for l, r in ((label_a, raw_a), (label_b, raw_b)) if r is None]
        lines.append(f"    o   {PATH} is absent from {', '.join(which)}. "
                     f"Absent is not equal. No comparison is possible.")
    elif yrs_a is None or yrs_b is None:
        verdict = UNPARSED
        lines.append("    ?   A value is present but could not be read as an age. "
                     "Not guessed, not compared. A human must look.")
    elif abs(yrs_a - yrs_b) <= TOLERANCE:
        verdict = SAME
        lines.append(f"    =   Both read as {yrs_a:.2f} years "
                     f"(agree within {TOLERANCE} years).")
    else:
        verdict = DIFFERENT
        older, gap = (label_b, yrs_b - yrs_a) if yrs_b > yrs_a else (label_a, yrs_a - yrs_b)
        lines.append(f"    >   {older} enrols from {gap:.2f} years older. "
                     f"The two trials do not cover the same ages.")

    return verdict, "\n".join(lines)


def emit(verdict, body):
    print(f"C2  MINIMUM AGE{' ' * max(1, 44 - len(verdict))}{verdict}")
    print(body)
    print()


def load_newest():
    fname = re.compile(r"^(NCT\d+)_(\d{4}-\d{2}-\d{2})\.json$")
    best = {}
    for f in sorted(DATA.glob("*.json")):
        m = fname.match(f.name)
        if m and (m.group(1) not in best or best[m.group(1)][0] < m.group(2)):
            best[m.group(1)] = (m.group(2), f)
    return [(n, json.loads(v[1].read_text())) for n, v in sorted(best.items())]


def selftest():
    studies = load_newest()
    if len(studies) < 2:
        print("Need two snapshots in data/. Run fetch.py."); sys.exit(1)
    (na, a), (nb, b) = studies[0], studies[1]

    def edited(rec, new):
        r = copy.deepcopy(rec)
        el = r["protocolSection"]["eligibilityModule"]
        if new is None:
            el.pop("minimumAge", None)
        else:
            el["minimumAge"] = new
        return r

    print("=" * 68)
    print("RUN 1 - the real thing, both 14 Sep snapshots unedited")
    print("=" * 68)
    emit(*check(a, b))

    print("=" * 68)
    print('RUN 2 - forced match: B edited to "16 Years"')
    print("=" * 68)
    emit(*check(a, edited(b, "16 Years")))

    print("=" * 68)
    print('RUN 3 - THE TRAP: B edited to "16 Months"')
    print("=" * 68)
    emit(*check(a, edited(b, "16 Months")))

    print("=" * 68)
    print("RUN 4 - absence: minimumAge deleted from B entirely")
    print("=" * 68)
    emit(*check(a, edited(b, None)))

    print("=" * 68)
    print("NOT IN YOUR FOUR RUNS - values a sponsor could really write")
    print("=" * 68)
    for odd in ["N/A", "16", "16 Fortnights", "18 Days"]:
        print(f"--- B = {odd!r} ---")
        emit(*check(a, edited(b, odd)))

    print("Now open acceptance/S3-C2-minimum-age.md and mark each run "
          "against what you wrote BEFORE this existed.")


def main():
    if "--selftest" in sys.argv:
        selftest(); return
    studies = load_newest()
    if len(studies) < 2:
        print("Need two snapshots in data/. Run fetch.py."); sys.exit(1)
    print(f"A = {studies[0][0]}   B = {studies[1][0]}\n")
    emit(*check(studies[0][1], studies[1][1]))


if __name__ == "__main__":
    main()
