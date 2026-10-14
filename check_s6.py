#!/usr/bin/env python3
"""
ctg-compare - S6. Presence, documents, and the maturity guard.

    C3   maximum age        (imported from check_s4 - specified in S4, never
                             actually exercised until Runs 2 and 3 here)
    C7a  masking level      controlled vocabulary
    C7b  who was masked     controlled vocabulary, list, multiset
    C9   results posted     a date. In M1.
    C10  method described   free text. PRESENCE ONLY. NOT in M1.
    C11a document labels    list, multiset. In M1.
    C11b document dates     list, multiset. In M1.

    + THE MATURITY GUARD, which is the substantive content of this session.

WHY THE GUARD EXISTS.

On this fixture C9, C10, C11a and C11b are all absent from B, from one single
cause. Without a guard the report supports:

    "Takeda disclosed their statistical model and their SAP;
     Alkermes disclosed neither."

That sentence is FALSE while every underlying field value is correct. The
wrong number has relocated out of the code and into the conclusion, which is
the layer a reader is actually harmed by.

TWO MECHANISMS, DELIBERATELY NOT ONE.

  1. A REPORT-LEVEL BANNER. Unconditional, purely factual. States each
     record's lifecycle inputs and makes no claim about why anything is
     missing. Belongs once, at the top, where nobody can miss it.

  2. A PER-VERDICT TAG, (M), only on fields in M1 - and it means
     CONFOUNDED, NOT EXCUSED. "This absence has a second possible
     explanation", never "this absence is fine".

WHY M1 IS SHORT. A generous M1 excuses absences, which is the single most
destructive thing this tool could do: it is the difference between "B has not
disclosed this" and "B has not disclosed this YET", and only one of those is
supported by a registry field.

    THE PRINCIPLE, so a stranger can hold the tool to it:
    THE ONLY ABSENCE THIS TOOL WILL EXCUSE ON MATURITY GROUNDS IS ONE THAT
    IS LOGICALLY IMPOSSIBLE OTHERWISE.

M1's membership was decided against 42 CFR 11.48, not against the fixture.
11.48 defines what constitutes clinical trial RESULTS information and
11.48(a)(5) places the protocol and SAP inside that list; the registry's own
guidance adds that they are "posted with other clinical trial results, in
accordance with 42 CFR 11.52". The pathway by which a document reaches the
registry IS the results submission - so a record with no results has no route
by which documents would appear. C11 is in M1.

C10 is NOT, and that distinction is the point. `description` is a
registration-time element. Nothing in 11.48 makes it results-bound. Its
absence is not explained by record maturity and this tool will not say it is.

TWO NOTATION TRAPS, each one character from silent wrongness:
    documentSection...   C11 is the ONLY check not under protocolSection
    hasResults           TOP LEVEL. protocolSection.hasResults returns None
                         silently and the guard never fires.

Run:  python3 check_s6.py                      the newest saved snapshots
      python3 check_s6.py --selftest           the seven acceptance runs
      python3 check_s6.py --selftest --record  same, and the TOOL writes the
                                               verdicts into the acceptance
                                               file. You mark P or F.
"""

import copy
import json
import re
import sys
from calendar import monthrange
from collections import Counter
from datetime import date
from pathlib import Path

import record
from check_s4 import (ARM_TYPES, DIFFERENT, NOT_REPORTED, PHASES, SAME,
                      UNPARSED, arm_types, dig, show, vocab_check, check_c3)

# ---------------------------------------------------------------------------
# SYSTEM SUITABILITY. Runs at import, before any record is read.
#
# This module depends on an imported `dig` that can resolve [n] indices.
# On 3 Oct 2026 it was handed one that could not: check_s4.dig stripped a
# bare [] but treated "primaryOutcomes[0]" as a literal key, missed, and
# returned None. C10 then reported a 683-character field as ABSENT - a real
# verdict word, a plausible-looking result, and wrong.
#
# A bioanalytical run proves the system is fit before the samples go on. Same
# idea, three lines: a known input with a known answer, checked at import. If
# a future refactor hands this module a weaker helper, it fails here with a
# message instead of silently downgrading a verdict.
# ---------------------------------------------------------------------------
_SUIT = {"x": {"y": [{"z": 7}, {"z": 8}]}}
assert dig(_SUIT, "x.y[0].z") == 7, (
    "SYSTEM SUITABILITY FAILED: the imported dig() cannot resolve [n] "
    "indices. Every [0] path in this module would silently return None and "
    "report present fields as absent. Refusing to run. See L6.")
assert dig(_SUIT, "x.y[]") == _SUIT["x"]["y"], (
    "SYSTEM SUITABILITY FAILED: the imported dig() mishandles bare []. "
    "Refusing to run. See L6.")
assert dig(_SUIT, "x.y[9].z") is None, (
    "SYSTEM SUITABILITY FAILED: dig() did not return None for an "
    "out-of-range index. Refusing to run.")

REVIEW = "REVIEW"
NOT_REPORTED_M = "NOT REPORTED (M)"

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
TODAY = date.today()

MASKINGS = {"NONE", "SINGLE", "DOUBLE", "TRIPLE", "QUADRUPLE"}
WHO_MASKED = {"PARTICIPANT", "CARE_PROVIDER", "INVESTIGATOR",
              "OUTCOMES_ASSESSOR"}

P_MASK = "protocolSection.designModule.designInfo.maskingInfo.masking"
P_WHO = "protocolSection.designModule.designInfo.maskingInfo.whoMasked"
P_C9 = "protocolSection.statusModule.resultsFirstPostDateStruct.date"
P_C10 = "protocolSection.outcomesModule.primaryOutcomes[0].description"
P_DOCS = "documentSection.largeDocumentModule.largeDocs"
P_C11A = P_DOCS + "[].label"
P_C11B = P_DOCS + "[].date"
P_PCD = "protocolSection.statusModule.primaryCompletionDateStruct.date"

# M1 - the published list of maturity-dependent fields. Decided against the
# regulation, 3 Oct 2026. Three entries, one logical cause.
M1 = {P_C9, P_C11A, P_C11B}

# Printed non-membership reasoning. This is worth more than the list itself:
# a reader can see which near misses were considered and rejected.
NOT_M1 = {
    P_C10: ("`description` is available at REGISTRATION. Many sponsors fill "
            "it only when posting\n        results, but nothing requires them "
            "to wait. Its absence is therefore NOT\n        explained by "
            "record maturity, and this tool will not say it is."),
}


# ---------------------------------------------------------------------------
# dates. Partial dates are normal in this registry: "2027-05" and "2027" are
# both valid. We resolve to the LAST day of the stated period, because the
# question asked of the value is "has this period PASSED?", and a month that
# is still running has not.
# ---------------------------------------------------------------------------
def period_end(raw):
    if not isinstance(raw, str):
        return None, "field absent" if raw is None else f"not a date: {raw!r}"
    s = raw.strip()
    if re.fullmatch(r"\d{4}", s):
        return date(int(s), 12, 31), "year only - resolved to 31 Dec"
    if re.fullmatch(r"\d{4}-\d{2}", s):
        y, m = int(s[:4]), int(s[5:7])
        return date(y, m, monthrange(y, m)[1]), "month only - resolved to month end"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return date(int(s[:4]), int(s[5:7]), int(s[8:10])), None
    return None, f"could not read {raw!r} as a date"


def lifecycle(rec):
    """Every input that bears on record maturity. Inputs only - no verdict."""
    pcd = dig(rec, P_PCD)
    typ = dig(rec, "protocolSection.statusModule.primaryCompletionDateStruct.type")
    end, note = period_end(pcd)
    locs = dig(rec, "protocolSection.contactsLocationsModule.locations") or []
    return {
        "has_results": rec.get("hasResults"),          # TOP LEVEL. Not protocolSection.
        "status": dig(rec, "protocolSection.statusModule.overallStatus"),
        "results_posted": dig(rec, P_C9),
        "pcd": pcd, "pcd_type": typ, "pcd_end": end, "pcd_note": note,
        "passed": None if end is None else end < TODAY,
        "elapsed": None if end is None else (TODAY - end).days,
        "fda_drug": dig(rec, "protocolSection.oversightModule.isFdaRegulatedDrug"),
        "sites": len(locs),
        "us_sites": sum(1 for l in locs if l.get("country") == "United States"),
    }


def m_verdict(path, missing, lives):
    """Decide whether a NOT REPORTED earns the (M) tag, and say why either way.

    (M) is earned only when the field is in M1 AND every record missing it has
    a primary completion date that has NOT passed - i.e. no results obligation
    has been triggered, so no pathway for the value exists yet.

    When the date HAS passed, the tool does NOT compute whether the submission
    deadline has run. That is a legal determination with exceptions. It prints
    the date, the elapsed interval and today's date, and stops.
    """
    lines = []
    if path not in M1:
        lines.append("    o   NOT tagged (M). This field is not in M1:")
        lines.append(f"        {NOT_M1.get(path, 'not maturity-dependent.')}")
        return NOT_REPORTED, lines

    lines.append(f"    o   in M1 - this field cannot exist before results are posted.")
    undecided = []
    for lab in missing:
        lv = lives[lab]
        if lv["has_results"] or lv["results_posted"]:
            # The strongest case there is. The pathway EXISTED and the value is
            # still missing, so maturity explains nothing. Checked FIRST,
            # before the date, because it supersedes the date entirely.
            lines.append(f"        {lab}: HAS posted results "
                         f"({lv['results_posted']}). The submission pathway for")
            lines.append(f"            this field existed and the field is still "
                         f"absent. Record maturity")
            lines.append(f"            explains nothing here.")
            undecided.append(lab)
        elif lv["passed"] is None:
            lines.append(f"        {lab}: primary completion date unreadable "
                         f"({lv['pcd']!r}). Cannot assess.")
            undecided.append(lab)
        elif not lv["passed"]:
            lines.append(f"        {lab}: primary completion {lv['pcd']} "
                         f"({lv['pcd_type']}) has NOT passed. No results")
            lines.append(f"            obligation triggered as of {TODAY}. "
                         f"Absence has no other available cause.")
        else:
            lines.append(f"        {lab}: primary completion {lv['pcd']} "
                         f"({lv['pcd_type']}) passed {lv['elapsed']} days ago,")
            lines.append(f"            and results are still not posted. Whether "
                         f"the submission deadline has")
            lines.append(f"            run is a legal determination with "
                         f"exceptions - see 42 CFR 11.44.")
            lines.append(f"            NOT decided here. Today is {TODAY}.")
            undecided.append(lab)

    if undecided:
        lines.append("    o   NOT tagged (M): at least one record's absence is not "
                     "accounted for by")
        lines.append("        an untriggered obligation. Read the dates above and "
                     "rule yourself.")
        return NOT_REPORTED, lines

    lines.append("    M   TAGGED (M). This means CONFOUNDED, not EXCUSED - the "
                 "absence has a")
    lines.append("        second available explanation. It does not mean the "
                 "absence is fine.")
    return NOT_REPORTED_M, lines


# ---------------------------------------------------------------------------
def compare(cid, name, path, va, vb, lives, permitted=None, as_multiset=False,
            notes=()):
    lines = [f"    {path}", show("A", va), show("B", vb)]

    missing = [l for l, v in (("A", va), ("B", vb)) if v is None]
    empty = [l for l, v in (("A", va), ("B", vb))
             if isinstance(v, list) and not v]

    if missing:
        lines.append(f"    o   absent from {', '.join(missing)}. "
                     f"Absent is not equal.")
        verdict, extra = m_verdict(path, missing, lives)
        lines += extra
        lines += [f"    .   {n}" for n in notes]
        return verdict, lines

    if empty:
        lines.append(f"    o   PRESENT BUT EMPTY in {', '.join(empty)} - zero "
                     f"values is nothing to compare.")
        verdict, extra = m_verdict(path, empty, lives)
        lines += extra
        lines += [f"    .   {n}" for n in notes]
        return verdict, lines

    la = va if isinstance(va, list) else [va]
    lb = vb if isinstance(vb, list) else [vb]

    if permitted:
        bad = sorted({v for v in la + lb if v not in permitted}, key=str)
        if bad:
            lines.append(f"    ?   {', '.join(repr(b) for b in bad)} is not a "
                         f"permitted value for this field.")
            lines.append(f"        Permitted: {', '.join(sorted(permitted))}")
            lines.append("        Not guessed, not case-folded, not compared.")
            lines += [f"    .   {n}" for n in notes]
            return UNPARSED, lines

    if as_multiset:
        ca, cb = Counter(la), Counter(lb)
        if ca == cb:
            lines.append(f"    =   Same {len(la)} value(s). Order ignored.")
            lines += [f"    .   {n}" for n in notes]
            return SAME, lines
        only_a, only_b = ca - cb, cb - ca
        lines.append(f"    >   counts A={len(la)}  B={len(lb)}")
        if only_a:
            lines.append(f"        in A but not B: "
                         f"{', '.join(f'{k} x{v}' for k, v in sorted(only_a.items()))}")
        if only_b:
            lines.append(f"        in B but not A: "
                         f"{', '.join(f'{k} x{v}' for k, v in sorted(only_b.items()))}")
        lines += [f"    .   {n}" for n in notes]
        return DIFFERENT, lines

    if va == vb:
        lines.append(f"    =   Both are {va!r}.")
        lines += [f"    .   {n}" for n in notes]
        return SAME, lines
    lines.append(f"    >   A is {va!r}, B is {vb!r}.")
    lines += [f"    .   {n}" for n in notes]
    return DIFFERENT, lines


def doc_field(rec, key):
    ds = dig(rec, P_DOCS)
    if ds is None:
        return None
    return [d.get(key) for d in ds]


REDACTION = ("A document-presence field attests EXISTENCE, not COMPLETENESS. "
             "42 CFR 11.48(a)(5)\n        permits redacting trade secret and "
             "confidential commercial information before\n        submission, so "
             "`hasSap: true` does not mean the statistical model is legible.\n"
             "        See KNOWN-LIMITATIONS.md, L4.")

C10_NOTE = ("PRESENCE ONLY. This check does not adjudicate what the text "
            "MEANS - that is\n        C5/C6's machinery and rule N1. Both "
            "present and non-identical returns REVIEW.")


def check_c10(a, b, lives):
    ra, rb = dig(a, P_C10), dig(b, P_C10)
    pa = None if ra is None else f"{len(ra)} chars"
    pb = None if rb is None else f"{len(rb)} chars"
    lines = [f"    {P_C10}",
             f"    A   {pa or '-- field absent --'}",
             f"    B   {pb or '-- field absent --'}"]
    missing = [l for l, v in (("A", ra), ("B", rb)) if v is None]
    if missing:
        lines.append(f"    o   absent from {', '.join(missing)}. "
                     f"Absent is not equal.")
        verdict, extra = m_verdict(P_C10, missing, lives)
        lines += extra
        lines.append(f"    .   {C10_NOTE}")
        return verdict, lines
    if ra == rb:
        lines.append("    =   Byte-identical.")
        lines.append(f"    .   {C10_NOTE}")
        return SAME, lines
    lines.append("    ?   Both describe a method, and the descriptions differ. "
                 "This check reports")
    lines.append("        PRESENCE. It does not rule on free text in either "
                 "direction.")
    lines.append(f"    .   {C10_NOTE}")
    return REVIEW, lines


def banner(a, b):
    la, lb = lifecycle(a), lifecycle(b)
    fired = la["has_results"] != lb["has_results"]
    bar = "!" * 72 if fired else "-" * 72
    print(bar)
    print("MATURITY GUARD - " + ("FIRED" if fired else "silent") +
          f"   (today: {TODAY})")
    print(bar)
    if fired:
        print("  The two records are at DIFFERENT LIFECYCLE STAGES. Every NOT")
        print("  REPORTED below may reflect that rather than sponsor disclosure")
        print("  practice. This banner states facts about the records and makes")
        print("  no claim about the cause of any absence.")
    else:
        print("  Both records agree on hasResults. No lifecycle confound from")
        print("  this input. Absences below are not explained by it.")
    print()
    rows = [
        ("hasResults", "has_results"),
        ("overallStatus", "status"),
        ("primary completion", "pcd"),
        ("  ...date type", "pcd_type"),
        ("  ...passed?", "passed"),
        ("  ...days elapsed", "elapsed"),
        ("results posted", "results_posted"),
        ("isFdaRegulatedDrug", "fda_drug"),
        ("US sites / total", None),
    ]
    print(f"  {'':<22}{'A':<28}{'B':<28}")
    for label, key in rows:
        if key is None:
            va = f"{la['us_sites']} / {la['sites']}"
            vb = f"{lb['us_sites']} / {lb['sites']}"
        else:
            va, vb = la[key], lb[key]
        print(f"  {label:<22}{str(va):<28}{str(vb):<28}")
    print()
    print("  The third cause of absence, checked rather than overlooked: the")
    print("  11.48 obligation binds only on an 'applicable clinical trial'. A")
    print("  trial that is not one owes nothing, and absence would mean neither")
    print("  opacity nor timing. isFdaRegulatedDrug and US site counts are")
    print("  printed above because they bear on it. 'Applicable clinical trial'")
    print("  is a defined legal term with more conditions than two fields, so")
    print("  this tool states the inputs and does not rule.")
    print()
    print(f"  M1 (maturity-dependent fields, {len(M1)}):")
    for p in sorted(M1):
        print(f"    {p}")
    print()
    return la, lb


CHECKS = [
    ("C3", "MAXIMUM AGE",
     lambda a, b, lv: check_c3(a, b)),
    ("C7a", "MASKING LEVEL",
     lambda a, b, lv: compare("C7a", "masking", P_MASK,
                              dig(a, P_MASK), dig(b, P_MASK), lv,
                              permitted=MASKINGS)),
    ("C7b", "WHO WAS MASKED",
     lambda a, b, lv: compare("C7b", "whoMasked", P_WHO,
                              dig(a, P_WHO), dig(b, P_WHO), lv,
                              permitted=WHO_MASKED, as_multiset=True)),
    ("C9", "RESULTS POSTED",
     lambda a, b, lv: compare("C9", "results posted", P_C9,
                              dig(a, P_C9), dig(b, P_C9), lv)),
    ("C10", "METHOD DESCRIBED", check_c10),
    ("C11a", "DOCUMENT LABELS",
     lambda a, b, lv: compare("C11a", "document labels", P_C11A,
                              doc_field(a, "label"), doc_field(b, "label"), lv,
                              as_multiset=True, notes=(REDACTION,))),
    ("C11b", "DOCUMENT DATES",
     lambda a, b, lv: compare("C11b", "document dates", P_C11B,
                              doc_field(a, "date"), doc_field(b, "date"), lv,
                              as_multiset=True, notes=(REDACTION,))),
]


def emit(cid, name, verdict, lines):
    record.log(cid, verdict)
    print(f"{cid}  {name}{' ' * max(1, 46 - len(name) - len(verdict))}{verdict}")
    print("\n".join(lines)); print()


def run(a, b, only=None):
    la, lb = banner(a, b)
    lives = {"A": la, "B": lb}
    for cid, name, fn in CHECKS:
        if only and cid not in only:
            continue
        verdict, lines = fn(a, b, lives)
        emit(cid, name, verdict, lines)


def load():
    f = re.compile(r"^(NCT\d+)_(\d{4}-\d{2}-\d{2})\.json$")
    best = {}
    for p in sorted(DATA.glob("*.json")):
        m = f.match(p.name)
        if m and (m.group(1) not in best or best[m.group(1)][0] < m.group(2)):
            best[m.group(1)] = (m.group(2), p)
    return [(n, json.loads(v[1].read_text())) for n, v in sorted(best.items())]


def set_path(rec, dotted, value):
    """Edit a copy. dotted uses [n] for list indices. Deletes when value is
    the sentinel DELETE."""
    r = copy.deepcopy(rec)
    node = r
    parts = dotted.split(".")
    for raw in parts[:-1]:
        m = re.match(r"^([A-Za-z0-9_]+)(?:\[(\d+)\])?$", raw)
        node = node[m.group(1)]
        if m.group(2) is not None:
            node = node[int(m.group(2))]
    last = parts[-1]
    if value is DELETE:
        node.pop(last, None)
    else:
        node[last] = value
    return r


class _Delete:
    def __repr__(self):
        return "DELETE"


DELETE = _Delete()


def selftest():
    s = load()
    if len(s) < 2:
        print("Need two snapshots in data/."); sys.exit(1)
    a, b = s[0][1], s[1][1]

    def head(n, t):
        record.set_run(f"Run {n}")
        print("=" * 72); print(f"RUN {n} - {t}"); print("=" * 72)

    head(1, "the real thing, both 14 Sep snapshots unedited")
    run(a, b)

    head(2, 'C3 unit trap - B maximumAge set to "840 Months" (= 70 years)')
    b2 = set_path(b, "protocolSection.eligibilityModule.maximumAge", "840 Months")
    run(a, b2, only={"C3"})
    print("    ^ SAME here also proves to_years is IMPORTED from check_c2.py")
    print("      rather than reimplemented. If C3 had its own copy of the")
    print("      conversion, this is the run where the two would drift.\n")

    head(3, "C3 absent - B maximumAge deleted")
    run(a, set_path(b, "protocolSection.eligibilityModule.maximumAge", DELETE),
        only={"C3"})

    head(4, "C1 absent - A designModule.phases deleted (S4 gap closed)")
    a4 = set_path(a, "protocolSection.designModule.phases", DELETE)
    v, lines = vocab_check("phase", "protocolSection.designModule.phases",
                           dig(a4, "protocolSection.designModule.phases"),
                           dig(b, "protocolSection.designModule.phases"),
                           PHASES, True)
    emit("C1", "PHASE", v, lines)

    head(5, "THE EMPTY-LIST TRAP - BOTH records' armGroups set to []")
    a5 = set_path(a, "protocolSection.armsInterventionsModule.armGroups", [])
    b5 = set_path(b, "protocolSection.armsInterventionsModule.armGroups", [])
    v, lines = vocab_check("arm types",
                           "protocolSection.armsInterventionsModule.armGroups[].type",
                           arm_types(a5), arm_types(b5), ARM_TYPES, True)
    emit("C8", "ARM TYPES", v, lines)
    print("    ^ Symmetric ON PURPOSE. One empty list is easy to catch; two is")
    print("      the case that agrees with itself. Before the 3 Oct guard this")
    print("      printed SAME, with the line 'Same 0 value(s). Order ignored.'")
    print("      Clean code, no error, wrong answer - found by writing this")
    print("      criterion before the code it tests. Logged L5.\n")

    head(6, "THE GUARD SWITCHED OFF - B given posted results "
            "(THREE coupled fields)")
    # AMENDED 3 Oct 2026. As first specified this run moved two fields and
    # produced a record that CANNOT EXIST: results posted 2026-09-01 against a
    # primary completion date of 2027-05. The guard - keyed on the regulation
    # rather than on hasResults - correctly refused to be switched off by it,
    # and C11a kept its (M) tag, which is the opposite of what this run exists
    # to show. The criteria were wrong, not the code. The coupling is THREE
    # fields: results cannot be posted before the trial reaches primary
    # completion.
    b6 = set_path(b, "hasResults", True)
    b6 = set_path(b6, "protocolSection.statusModule.primaryCompletionDateStruct",
                  {"date": "2026-04-30", "type": "ACTUAL"})
    b6 = set_path(b6, "protocolSection.statusModule.resultsFirstPostDateStruct",
                  {"date": "2026-09-01", "type": "ACTUAL"})
    run(a, b6, only={"C9", "C10", "C11a"})
    print("    ^ The only run that proves the guard can turn OFF. A guard that")
    print("      always fires is indistinguishable from one that is hard-coded,")
    print("      and would quietly excuse every absence in every comparison.")
    print("      C11a has lost its (M) tag: B posted results, so the pathway")
    print("      existed, and the documents are still absent. The absence has")
    print("      become a disclosure fact rather than a timing artefact.")
    print("      THREE fields moved together - hasResults, primaryCompletion")
    print("      and resultsFirstPost - because a record cannot post results")
    print("      before reaching primary completion. Coupled factors are")
    print("      varied together AND the coupling is stated. Getting that")
    print("      coupling wrong is what the first version of this run did,")
    print("      and the tool caught it by refusing the impossible record.\n")

    head(7, 'C7 made internally inconsistent - A masking set to "TRIPLE"')
    a7 = set_path(a, P_MASK, "TRIPLE")
    run(a7, b, only={"C7a", "C7b"})
    print("    ^ A now claims TRIPLE masking while naming TWO masked parties.")
    print("      Neither sub-check notices. That blind spot is the point of the")
    print("      run and the argument for C12 (record-against-itself), logged")
    print("      for v0.2. A merged C7 would have printed one verdict here and")
    print("      hidden both halves.\n")

    print("Now mark each run against acceptance/S6-presence-and-maturity.md,")
    print("or re-run with --record and let the tool write the verdicts.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        if "--record" in sys.argv:
            body = record.capture(selftest)
            record.append("S6-presence-and-maturity.md",
                          "S6 selftest, 7 runs", body)
        else:
            selftest()
    else:
        s = load()
        print(f"A = {s[0][0]}   B = {s[1][0]}\n")
        run(s[0][1], s[1][1])
