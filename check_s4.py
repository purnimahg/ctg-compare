#!/usr/bin/env python3
"""
ctg-compare - S4. C1 phase, C3 maximum age, C4 sex, C8 arm types.

Three of these read CONTROLLED VOCABULARIES: the registry permits a fixed
set of words and nothing else. A value outside that set is not a difference,
it is a value we cannot interpret - so it returns UNPARSED, never SAME and
never DIFFERENT. Case is NOT folded. "Male" is not "MALE"; if a record says
"Male" something is wrong and the tool's job is to surface that, not to
decide what the sponsor meant.

C3 reuses the age reader written in S3 - imported, not re-implemented, so
there is only one place where months become years.

Run:  python3 check_s4.py              the newest saved snapshots
      python3 check_s4.py --selftest   the six acceptance runs
"""

import copy
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

SAME, DIFFERENT, NOT_REPORTED, UNPARSED = "SAME", "DIFFERENT", "NOT REPORTED", "UNPARSED"

_spec = importlib.util.spec_from_file_location("c2", HERE / "check_c2.py")
_c2 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_c2)
to_years = _c2.to_years

PHASES = {"NA", "EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4"}
SEXES = {"ALL", "FEMALE", "MALE"}
ARM_TYPES = {"EXPERIMENTAL", "ACTIVE_COMPARATOR", "PLACEBO_COMPARATOR",
             "SHAM_COMPARATOR", "NO_INTERVENTION", "OTHER"}


def dig(rec, path):
    """Walk a dotted path. Handles all three notations from S2:

        a.b.c        one value at c
        a.b[0].c     the FIRST element of list b, then c      <- just one
        a.b[].c      the list b itself, for the caller to map <- all of them

    [n] SUPPORT ADDED 3 Oct 2026. Until then this function silently returned
    None for any path containing [0], while check_s5.dig handled it correctly.
    Two implementations of the same helper, one regex apart, in one repo.
    S6's C10 reads primaryOutcomes[0].description and reported the field
    ABSENT from a record holding 683 characters of it. See L6.
    """
    node = rec
    for raw in path.split("."):
        m = re.match(r"^([A-Za-z0-9_]+)(?:\[(\d*)\])?$", raw)
        if m is None:
            return None
        key, idx = m.group(1), m.group(2)
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
        if idx:                       # [0], [1], ... ; bare [] falls through
            if not isinstance(node, list) or int(idx) >= len(node):
                return None
            node = node[int(idx)]
    return node


def arm_types(rec):
    arms = dig(rec, "protocolSection.armsInterventionsModule.armGroups")
    if arms is None:
        return None
    return [a.get("type") for a in arms]


def show(lab, raw, extra=""):
    if raw is None:
        return f"    {lab}   -- field absent --"
    if isinstance(raw, list):
        return f"    {lab}   [{len(raw)}] {', '.join(str(v) for v in raw)}{extra}"
    return f"    {lab}   \"{raw}\"{extra}"


def vocab_check(name, path, va, vb, permitted, as_multiset, structural_note=None):
    """One comparison against a controlled vocabulary."""
    lines = [f"    {path}", show("A", va), show("B", vb)]

    if va is None or vb is None:
        which = [l for l, v in (("A", va), ("B", vb)) if v is None]
        lines.append(f"    o   absent from {', '.join(which)}. Absent is not equal.")
        return NOT_REPORTED, lines

    # THE EMPTY-LIST GUARD. Added 3 Oct 2026, retroactively, after S6 Run 5.
    #
    # Counter([]) == Counter([]) is True. Without this block, two trials that
    # declare ZERO arms return SAME from the multiset branch below - a
    # confident agreement about nothing, produced by code with no bug in it.
    # This shipped and passed S4 acceptance on 16 Sep because S4's runs only
    # ever fed it real, populated lists.
    #
    # A field that is present and says zero is not the same as a field that is
    # absent, and neither is comparable. Both report NOT REPORTED; the reason
    # line says which.
    if (isinstance(va, list) and not va) or (isinstance(vb, list) and not vb):
        which = [l for l, v in (("A", va), ("B", vb))
                 if isinstance(v, list) and not v]
        lines.append(f"    o   PRESENT BUT EMPTY in {', '.join(which)}. The field "
                     f"exists and declares zero values.")
        lines.append("        Zero values is not noise - it is nothing to compare. "
                     "[] == [] is True, so")
        lines.append("        without this guard the multiset branch returns SAME. "
                     "Found 3 Oct 2026 by")
        lines.append("        S6 Run 5, in code that passed S4 acceptance on 16 Sep. "
                     "Logged L5.")
        return NOT_REPORTED, lines

    la = va if isinstance(va, list) else [va]
    lb = vb if isinstance(vb, list) else [vb]
    bad = sorted({v for v in la + lb if v not in permitted}, key=str)
    if bad:
        lines.append(f"    ?   {', '.join(repr(b) for b in bad)} is not a permitted "
                     f"value for this field.")
        lines.append(f"        Permitted: {', '.join(sorted(permitted))}")
        lines.append("        Not guessed, not case-folded, not compared. A human must look.")
        return UNPARSED, lines

    if as_multiset:
        ca, cb = Counter(la), Counter(lb)
        if ca == cb:
            lines.append(f"    =   Same {len(la)} value(s). Order ignored.")
            if structural_note:
                lines.append(f"        {structural_note}")
            return SAME, lines
        only_a, only_b = ca - cb, cb - ca
        lines.append(f"    >   counts A={len(la)}  B={len(lb)}")
        if only_a:
            lines.append(f"        in A but not B: "
                         f"{', '.join(f'{k} x{v}' for k, v in sorted(only_a.items()))}")
        if only_b:
            lines.append(f"        in B but not A: "
                         f"{', '.join(f'{k} x{v}' for k, v in sorted(only_b.items()))}")
        return DIFFERENT, lines

    if va == vb:
        lines.append(f"    =   Both are {va!r}.")
        return SAME, lines
    lines.append(f"    >   A is {va!r}, B is {vb!r}.")
    return DIFFERENT, lines


def check_c3(a, b):
    p = "protocolSection.eligibilityModule.maximumAge"
    ra, rb = dig(a, p), dig(b, p)
    ya, na = to_years(ra)
    yb, nb = to_years(rb)
    lines = [f"    {p}"]
    for lab, raw, y, note in (("A", ra, ya, na), ("B", rb, yb, nb)):
        shown = "-- field absent --" if raw is None else f'"{raw}"'
        read = f"read as {y:.2f} years" if y is not None else f"NOT READ: {note}"
        lines.append(f"    {lab}   {shown:<22} {read}")
    if ra is None or rb is None:
        lines.append("    o   absent. Absent is not equal.")
        return NOT_REPORTED, lines
    if ya is None or yb is None:
        lines.append("    ?   present but not readable as an age. Not guessed.")
        return UNPARSED, lines
    if abs(ya - yb) <= 0.01:
        lines.append(f"    =   Both read as {ya:.2f} years.")
        return SAME, lines
    older, gap = ("A", ya - yb) if ya > yb else ("B", yb - ya)
    lines.append(f"    >   {older} admits up to {gap:.2f} years older.")
    return DIFFERENT, lines


CHECKS = [
    ("C1", "PHASE", lambda a, b: vocab_check(
        "phase", "protocolSection.designModule.phases",
        dig(a, "protocolSection.designModule.phases"),
        dig(b, "protocolSection.designModule.phases"),
        PHASES, True)),
    ("C3", "MAXIMUM AGE", check_c3),
    ("C4", "SEX ELIGIBLE", lambda a, b: vocab_check(
        "sex", "protocolSection.eligibilityModule.sex",
        dig(a, "protocolSection.eligibilityModule.sex"),
        dig(b, "protocolSection.eligibilityModule.sex"),
        SEXES, False)),
    ("C8", "ARM TYPES", lambda a, b: vocab_check(
        "arm types", "protocolSection.armsInterventionsModule.armGroups[].type",
        arm_types(a), arm_types(b), ARM_TYPES, True,
        structural_note=("This says the two trials share a STRUCTURE - same mix of "
                         "placebo,\n        experimental and comparator arms. It says "
                         "NOTHING about the drugs.\n        Arm labels and intervention "
                         "names are not compared by this check."))),
]


def run(a, b):
    for cid, name, fn in CHECKS:
        verdict, lines = fn(a, b)
        print(f"{cid}  {name}{' ' * max(1, 46 - len(name) - len(verdict))}{verdict}")
        print("\n".join(lines)); print()


def load():
    f = re.compile(r"^(NCT\d+)_(\d{4}-\d{2}-\d{2})\.json$")
    best = {}
    for p in sorted(DATA.glob("*.json")):
        m = f.match(p.name)
        if m and (m.group(1) not in best or best[m.group(1)][0] < m.group(2)):
            best[m.group(1)] = (m.group(2), p)
    return [(n, json.loads(v[1].read_text())) for n, v in sorted(best.items())]


def selftest():
    s = load()
    if len(s) < 2:
        print("Need two snapshots in data/."); sys.exit(1)
    a, b = s[0][1], s[1][1]

    def arms_edited(rec, fn):
        r = copy.deepcopy(rec)
        r["protocolSection"]["armsInterventionsModule"]["armGroups"] = \
            fn(r["protocolSection"]["armsInterventionsModule"]["armGroups"])
        return r

    def head(n, t):
        print("=" * 70); print(f"RUN {n} - {t}"); print("=" * 70)

    head(1, "the real thing, both 14 Sep snapshots unedited"); run(a, b)

    head(2, "C8, B's arms REORDERED (nothing else changed)")
    run(a, arms_edited(b, lambda g: list(reversed(g))))

    head(3, "C8, one of B's EXPERIMENTAL arms changed to ACTIVE_COMPARATOR")
    def swap(g):
        g = copy.deepcopy(g)
        for arm in g:
            if arm["type"] == "EXPERIMENTAL":
                arm["type"] = "ACTIVE_COMPARATOR"; break
        return g
    run(a, arms_edited(b, swap))

    head(4, "C8, an arm REMOVED from B (B has 2, A has 3)")
    run(a, arms_edited(b, lambda g: g[:-1]))

    head(5, 'C1, B phases changed to ["PHASE2", "PHASE3"]')
    r = copy.deepcopy(b); r["protocolSection"]["designModule"]["phases"] = ["PHASE2", "PHASE3"]
    run(a, r)

    head(6, 'C4, B sex changed to "Male" (not a permitted value)')
    r = copy.deepcopy(b); r["protocolSection"]["eligibilityModule"]["sex"] = "Male"
    run(a, r)

    print("Now mark each run against acceptance/S4-exact-match-family.md.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        s = load()
        print(f"A = {s[0][0]}   B = {s[1][0]}\n"); run(s[0][1], s[1][1])
