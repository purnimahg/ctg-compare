#!/usr/bin/env python3
"""
ctg-compare - S7. The report renderer.  report.py -> report.md

This is the first output read by SOMEONE ELSE. The failure mode changes here:
every session before this one could produce a wrong VERDICT. From here, a
CORRECT set of verdicts can still produce a wrong CONCLUSION - through
ordering, omission or emphasis. None of those is a bug. All of them are
decisions, and they are made in this file.

THE FOUR DECISIONS, agreed 4 Oct before this code existed:

  ORDER     Precondition, then Maturity, then Comparability.
            If C1 and C8 say the trials do not share a phase or a comparator
            structure, every comparability verdict below is conditional on a
            comparison that may not be meaningful. Printing "C2 DIFFERENT"
            above "C1 DIFFERENT" invites a reader to compare minimum ages
            between a Phase 2 and a Phase 3 trial - a precise answer to a
            question that should not have been asked.

  COUNTS    11 checks / 13 comparisons, both COMPUTED, never literals.
            C7 and C11 each split in two during S6. A hard-coded 13 is wrong
            the moment C12 arrives.

  LEGEND    GENERATED from the verdict constants. A hand-written legend is
            the same defect class as a hand-typed verdict, and this repo has
            been bitten by that five times.

  REFUSAL   The report states counts. It never states a conclusion.
            Counting is not concluding. "4 of 13 comparisons are NOT
            REPORTED, 3 confounded by record maturity" is a count.
            "These trials are broadly comparable" is a conclusion, and this
            tool has no standing to reach one. A reader can check a count;
            if they could check a judgement they would not need the tool.

AND THE ARITHMETIC GUARD, added by amendment on 4 Oct for a specific reason:
the hand-written reference count block in S7's acceptance criteria was
written WRONG - 'SAME 3' against four listed checks, in a column summing to
12 under a printed total of 13 - and it survived a read. A corrupted
reference standard does not announce itself; it silently certifies whatever
the code returns. So the renderer asserts its own arithmetic and refuses to
write a report that does not add up.

Run:  python3 report.py                      render report.md
      python3 report.py --selftest           the six acceptance runs
      python3 report.py --selftest --record  same, tool writes the verdicts
"""

import copy
import json
import re
import sys
from collections import Counter, OrderedDict
from datetime import date, timezone, datetime
from pathlib import Path

import record
import check_c2
import check_s4
import check_s5
import check_s6
from check_s6 import DELETE, lifecycle, set_path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE / "report.md"

# ---------------------------------------------------------------------------
# THE LEGEND, assembled from the modules' own constants. Nothing here is a
# string literal typed for the report - if a module renames a verdict, this
# list changes with it, and any verdict emitted that is not in this list
# makes the render FAIL rather than quietly fall out of the counts.
# ---------------------------------------------------------------------------
LEGEND = OrderedDict([
    (check_s4.SAME,
     "Both records carry the field and the values match."),
    (check_s5.SAME_N1,
     "Matched only after rule N1 removed words that DIFFERED. The count of "
     "erased words is shown; the tool does not judge whether they mattered."),
    (check_s4.DIFFERENT,
     "Both records carry the field and the values do not match."),
    (check_s5.REVIEW,
     "Free text, still unlike after N1. The tool is not authorised to rule "
     "on meaning in either direction. A word diff is printed instead."),
    (check_s4.NOT_REPORTED,
     "Absent from at least one record, or present and empty. Silence is not "
     "agreement."),
    (check_s6.NOT_REPORTED_M,
     "Absent, AND the record missing it has no results obligation triggered "
     "yet. CONFOUNDED, not excused."),
    (check_s4.UNPARSED,
     "Present but unreadable - outside the field's controlled vocabulary, or "
     "not parseable as a value. Never guessed."),
])

# ---------------------------------------------------------------------------
# WHAT THE REPORT MAY NOT SAY. Published so a stranger can audit the refusal
# rather than take it on trust, and enforced against the rendered text.
# ---------------------------------------------------------------------------
FORBIDDEN = [
    "are comparable", "not comparable", "broadly comparable",
    "directly comparable", "is comparable", "aren't comparable",
    "more transparent", "less transparent", "more forthcoming",
    "better disclosure", "worse disclosure",
    "we conclude", "we assess", "overall assessment", "our view",
    "score:", "grade:", "rating:", "ranked",
]

PRECONDITION, MATURITY, COMPARABILITY = "PRECONDITION", "MATURITY", "COMPARABILITY"

CATEGORY_MEANING = {
    PRECONDITION: "Is a comparison meaningful at all? Shared phase, shared "
                  "arm structure.",
    MATURITY: "Is the record complete enough to compare, or simply young?",
    COMPARABILITY: "Are the two trials measuring the same thing in the same "
                   "people?",
}


def comparisons(a, b):
    """Every comparison the tool performs, once each, in registry order.

    C3 is taken from check_s6 only. It is specified in BOTH check_s4.CHECKS
    and check_s6.CHECKS (s6 imports s4's implementation), and including both
    would count one check twice - the exact arithmetic error this session is
    about.
    """
    lv = {"A": lifecycle(a), "B": lifecycle(b)}
    s4 = dict((cid, fn) for cid, _, fn in check_s4.CHECKS)
    s6 = dict((cid, fn) for cid, _, fn in check_s6.CHECKS)

    reg = [
        # cid    category       path-bearing callable
        ("C1",  PRECONDITION,  "phase",              lambda: s4["C1"](a, b)),
        ("C8",  PRECONDITION,  "arm types",          lambda: s4["C8"](a, b)),
        ("C9",  MATURITY,      "results posted",     lambda: s6["C9"](a, b, lv)),
        ("C10", MATURITY,      "method described",   lambda: s6["C10"](a, b, lv)),
        ("C11a", MATURITY,     "document labels",    lambda: s6["C11a"](a, b, lv)),
        ("C11b", MATURITY,     "document dates",     lambda: s6["C11b"](a, b, lv)),
        ("C2",  COMPARABILITY, "minimum age",        lambda: check_c2.check(a, b)),
        ("C3",  COMPARABILITY, "maximum age",        lambda: s6["C3"](a, b, lv)),
        ("C4",  COMPARABILITY, "sex eligible",       lambda: s4["C4"](a, b)),
        ("C5",  COMPARABILITY, "main measurement",   lambda: check_s5.check("C5", a, b)),
        ("C6",  COMPARABILITY, "measurement timing", lambda: check_s5.check("C6", a, b)),
        ("C7a", COMPARABILITY, "masking level",      lambda: s6["C7a"](a, b, lv)),
        ("C7b", COMPARABILITY, "who was masked",     lambda: s6["C7b"](a, b, lv)),
    ]
    out = []
    for cid, cat, name, fn in reg:
        verdict, lines = fn()
        path = next((l.strip() for l in lines
                     if l.strip().startswith(("protocolSection", "documentSection"))),
                    "(path not reported)")
        out.append({"cid": cid, "base": re.sub(r"[ab]$", "", cid),
                    "category": cat, "name": name,
                    "verdict": verdict, "path": path, "lines": lines})
    return out, lv


class ArithmeticFailure(Exception):
    pass


def assert_arithmetic(rows):
    """Added by amendment 4 Oct. The human reference count block for this
    session was written wrong and survived a read, so the machine checks."""
    if not rows:
        raise ArithmeticFailure(
            "Zero comparisons. A report that renders cleanly with an empty "
            "table and counts of zero is the most plausible-looking wrong "
            "answer this tool could produce. Refusing to write.")

    dupes = [c for c, n in Counter(r["cid"] for r in rows).items() if n > 1]
    if dupes:
        raise ArithmeticFailure(f"Comparison(s) appear more than once: {dupes}")

    total = len(rows)
    by_verdict = Counter(r["verdict"] for r in rows)
    by_category = Counter(r["category"] for r in rows)

    unknown = set(by_verdict) - set(LEGEND)
    if unknown:
        raise ArithmeticFailure(
            f"Verdict(s) {sorted(unknown)} emitted but absent from the "
            f"generated legend. They would be printed without explanation, or "
            f"silently dropped from the counts while the total still added up. "
            f"Refusing to write.")

    if sum(by_verdict.values()) != total:
        raise ArithmeticFailure("verdict counts do not sum to the total")
    if sum(by_category.values()) != total:
        raise ArithmeticFailure("category counts do not sum to the total")

    return total, by_verdict, by_category


# The report PUBLISHES the forbidden list so the refusal can be audited rather
# than trusted - which puts every forbidden phrase into the document, and the
# first thing the guard ever caught was its own documentation. The published
# block is fenced between these markers and excluded from the scan.
#
# That exclusion is a HOLE IN THE GUARD, so it is kept narrow, visible in the
# rendered markdown as an HTML comment, and tested: Run 5 plants a conclusion
# OUTSIDE the zone and the guard must still refuse it.
NOSCAN_OPEN = "<!-- published refusal list - excluded from the refusal scan -->"
NOSCAN_CLOSE = "<!-- end published refusal list -->"


def scannable(text):
    return re.sub(re.escape(NOSCAN_OPEN) + r".*?" + re.escape(NOSCAN_CLOSE),
                  "", text, flags=re.S)


def assert_refusal(text):
    hits = [p for p in FORBIDDEN if p in scannable(text).lower()]
    if hits:
        raise ArithmeticFailure(
            f"Report contains forbidden phrasing {hits}. The report states "
            f"counts; it does not state conclusions. Refusing to write.")


def render(a, b, nct_a, nct_b, snap_a, snap_b):
    rows, lv = comparisons(a, b)
    total, by_verdict, by_category = assert_arithmetic(rows)
    checks = len({r["base"] for r in rows})
    la, lb = lv["A"], lv["B"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    L = []
    w = L.append
    w(f"# ctg-compare — comparability report")
    w("")
    w(f"**A** · [{nct_a}](https://clinicaltrials.gov/study/{nct_a}) · "
      f"snapshot {snap_a}  ")
    w(f"**B** · [{nct_b}](https://clinicaltrials.gov/study/{nct_b}) · "
      f"snapshot {snap_b}  ")
    w(f"Rendered {now} · **{checks} checks / {total} comparisons**")
    w("")
    w("This report names where two registered trials are not measuring the "
      "same thing in the same patients. It reports counts and field values. "
      "It does not reach a conclusion about either trial — see *What this "
      "report will not say*, below.")
    w("")

    w("## Counts")
    w("")
    w("| Verdict | n | Comparisons |")
    w("|---|---|---|")
    for v in LEGEND:
        ids = [r["cid"] for r in rows if r["verdict"] == v]
        w(f"| {v} | {len(ids)} | {', '.join(ids) or '—'} |")
    w(f"| **total** | **{total}** | |")
    w("")
    for c in (PRECONDITION, MATURITY, COMPARABILITY):
        ids = [r["cid"] for r in rows if r["category"] == c]
        w(f"- **{c}** {len(ids)} — {', '.join(ids)}")
    w("")

    w("## Record maturity")
    w("")
    fired = la["has_results"] != lb["has_results"]
    w(f"**{'DIFFERENT LIFECYCLE STAGES' if fired else 'Same lifecycle stage'}** "
      f"— this block prints whether or not it fires, because an absent check "
      f"and a passed check look identical to a reader.")
    w("")
    w("| | A | B |")
    w("|---|---|---|")
    for label, k in (("results posted", "results_posted"),
                     ("overall status", "status"),
                     ("primary completion", "pcd"),
                     ("…date type", "pcd_type"),
                     ("FDA-regulated drug", "fda_drug")):
        w(f"| {label} | {la[k]} | {lb[k]} |")
    w(f"| US sites / total | {la['us_sites']} / {la['sites']} | "
      f"{lb['us_sites']} / {lb['sites']} |")
    w("")
    if fired:
        w("Every NOT REPORTED below may reflect this rather than a sponsor's "
          "disclosure practice. Verdicts tagged **(M)** are the ones where a "
          "results obligation has not yet been triggered at all. **(M) means "
          "confounded, not excused.** The submission deadline itself is a "
          "legal determination with exceptions — see 42 CFR 11.44 — and is "
          "not computed here.")
        w("")

    for c in (PRECONDITION, MATURITY, COMPARABILITY):
        sel = [r for r in rows if r["category"] == c]
        w(f"## {c} — {len(sel)}")
        w("")
        w(f"*{CATEGORY_MEANING[c]}*")
        w("")
        if c == COMPARABILITY:
            pre_bad = [r["cid"] for r in rows
                       if r["category"] == PRECONDITION
                       and r["verdict"] != check_s4.SAME]
            if pre_bad:
                w(f"> **Read the PRECONDITION section first.** {', '.join(pre_bad)} "
                  f"did not return SAME, so every row below is conditional on a "
                  f"comparison whose basis is in question.")
                w("")
        w("| Check | | Verdict | Field |")
        w("|---|---|---|---|")
        for r in sel:
            w(f"| {r['cid']} | {r['name']} | **{r['verdict']}** | `{r['path']}` |")
        w("")

    w("## What this report will not say")
    w("")
    w("The verdicts above are counts over registry fields. This tool has no "
      "standing to turn them into an overall judgement, so the rendered text "
      "is checked mechanically against a published list of phrasings it may "
      "not contain:")
    w("")
    w(NOSCAN_OPEN)
    w("")
    w("```")
    for p in FORBIDDEN:
        w(f"  {p}")
    w("```")
    w("")
    w(NOSCAN_CLOSE)
    w("")
    w("A render containing any of them fails and writes nothing. The list is "
      "published so the refusal can be audited rather than trusted — which "
      "necessarily puts every forbidden phrase into this document, so the "
      "block above is fenced out of the scan. That exclusion is the one hole "
      "in the guard; it is marked in the source of this file and tested "
      "against a planted sentence outside it.")
    w("")
    w("Three boundaries worth naming explicitly:")
    w("")
    w("- **A document-presence field attests existence, not completeness.** "
      "42 CFR 11.48(a)(5) permits redacting trade secret and confidential "
      "commercial information before submission, so a posted statistical "
      "analysis plan may have its model redacted. See `KNOWN-LIMITATIONS.md`, L4.")
    w("- **Free-text eligibility criteria are not parsed.** They are printed "
      "verbatim elsewhere under *human read required*, and no claim is made.")
    w("- **The assay behind an eligibility threshold is absent from every "
      "field path, permanently.** Two trials can enrol materially different "
      "populations and the registry will not show it.")
    w("")

    w("## Verdict legend")
    w("")
    w("Generated from the verdict constants in the code at render time, not "
      "written into this template.")
    w("")
    for v, meaning in LEGEND.items():
        w(f"- **{v}** — {meaning}")
    w("")

    text = "\n".join(L) + "\n"
    assert_refusal(text)
    return text, rows, total, by_verdict, by_category


def load():
    f = re.compile(r"^(NCT\d+)_(\d{4}-\d{2}-\d{2})\.json$")
    best = {}
    for p in sorted(DATA.glob("*.json")):
        m = f.match(p.name)
        if m and (m.group(1) not in best or best[m.group(1)][0] < m.group(2)):
            best[m.group(1)] = (m.group(2), p)
    return [(n, v[0], json.loads(v[1].read_text())) for n, v in sorted(best.items())]


def summary(total, by_verdict, by_category, checks):
    out = [f"    {checks} checks / {total} comparisons"]
    for v in LEGEND:
        out.append(f"    {v:<18} {by_verdict.get(v, 0)}")
    out.append(f"    {'':<18} --")
    out.append(f"    {'':<18} {total}")
    for c in (PRECONDITION, MATURITY, COMPARABILITY):
        out.append(f"    {c:<18} {by_category.get(c, 0)}")
    return "\n".join(out)


def selftest():
    s = load()
    (na, sa, a), (nb, sb, b) = s[0], s[1]

    def head(n, t):
        record.set_run(f"Run {n}")
        print("=" * 72); print(f"RUN {n} - {t}"); print("=" * 72)

    head(1, "render the real fixture")
    text, rows, total, bv, bc = render(a, b, na, nb, sa, sb)
    OUT.write_text(text)
    checks = len({r["base"] for r in rows})
    print(summary(total, bv, bc, checks))
    print(f"\n    report.md written, {len(text.splitlines())} lines")
    print("    Compare the block above to AMENDMENT 1 in the acceptance file.")
    record.log("counts", f"SAME={bv.get(check_s4.SAME,0)} total={total}")
    print()

    head(2, "the arithmetic guard - a duplicated comparison")
    bad = rows + [rows[0]]
    try:
        assert_arithmetic(bad)
        print("    !! NO FAILURE. The guard did not fire."); record.log("arith", "NO FAILURE")
    except ArithmeticFailure as e:
        print(f"    refused: {e}"); record.log("arith", "refused duplicate")
    print()

    head(3, 'precondition failure - B phases set to ["PHASE2"]')
    b3 = set_path(b, "protocolSection.designModule.phases", ["PHASE2"])
    t3, r3, tot3, bv3, bc3 = render(a, b3, na, nb, sa, sb)
    pre = [r for r in r3 if r["category"] == PRECONDITION]
    print(f"    C1 verdict: {[r['verdict'] for r in pre if r['cid']=='C1'][0]}")
    lead = "Read the PRECONDITION section first" in t3
    print(f"    comparability section carries the conditional warning: {lead}")
    print(f"    comparability rows still printed: "
          f"{len([r for r in r3 if r['category']==COMPARABILITY])}")
    record.log("precond", "warned, not suppressed" if lead else "NO WARNING")
    print()

    head(4, "legend drift - a check returns a verdict the legend lacks")
    drifted = [dict(r) for r in rows]
    drifted[0]["verdict"] = "PROBABLY FINE"
    try:
        assert_arithmetic(drifted)
        print("    !! NO FAILURE - the state would print unexplained, or drop")
        print("       out of the counts while the total still added up.")
        record.log("legend", "NO FAILURE")
    except ArithmeticFailure as e:
        print(f"    refused: {str(e)[:120]}...")
        record.log("legend", "refused unknown verdict")
    print()

    head(5, "the refusal test")
    try:
        assert_refusal(text)
        print("    rendered report contains none of the "
              f"{len(FORBIDDEN)} forbidden phrasings")
        record.log("refusal", "clean")
    except ArithmeticFailure as e:
        print(f"    !! {e}"); record.log("refusal", "FORBIDDEN PHRASE PRESENT")
    print("    and the guard itself works:")
    try:
        assert_refusal("These two trials are comparable.")
        print("    !! NO FAILURE on a planted conclusion.")
        record.log("refusal-guard", "NO FAILURE")
    except ArithmeticFailure:
        print("    refused a planted sentence asserting comparability")
        record.log("refusal-guard", "refused planted conclusion")
    print()

    head(6, "the empty report - renderer handed zero results")
    try:
        assert_arithmetic([])
        print("    !! NO FAILURE. An empty report would have been written.")
        record.log("empty", "NO FAILURE")
    except ArithmeticFailure as e:
        print(f"    refused: {str(e)[:150]}...")
        record.log("empty", "refused empty")
    print()
    print("Mark each line against acceptance/S7-report-renderer.md.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        if "--record" in sys.argv:
            body = record.capture(selftest)
            record.append("S7-report-renderer.md", "S7 selftest, 6 runs", body)
        else:
            selftest()
    else:
        s = load()
        (na, sa, a), (nb, sb, b) = s[0], s[1]
        text, rows, total, bv, bc = render(a, b, na, nb, sa, sb)
        OUT.write_text(text)
        print(summary(total, bv, bc, len({r["base"] for r in rows})))
        print(f"\nreport.md written to {OUT}")
