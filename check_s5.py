#!/usr/bin/env python3
"""
ctg-compare - S5. C5 main measurement, C6 measurement timing.

FREE TEXT. Nobody constrains what a sponsor types here, so neither the age
reader (S3) nor the controlled vocabularies (S4) apply.

The whole logic is three steps. There is no fourth step where it gets clever:

    1. tidy both strings under N1 - the declared, published rule
    2. same words after tidying  -> SAME       if N1 removed nothing that
                                                differed between the two
                                    SAME (N1)  if it did - with the COUNT
    3. otherwise                 -> REVIEW, and print the word diff

The intelligence is in step 3's DISPLAY, not in a decision procedure. A good
diff lets a human rule in five seconds. No procedure can rule at all.

Run:  python3 check_s5.py                      the newest saved snapshots
      python3 check_s5.py --selftest           the five acceptance runs
      python3 check_s5.py --selftest --record  same, and the TOOL writes the
                                              verdicts into the acceptance
                                              file. You mark P or F. You
                                              type no verdict strings.
"""

import copy
import json
import re
import sys

import record
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

SAME, REVIEW, NOT_REPORTED = "SAME", "REVIEW", "NOT REPORTED"

# Added 1 Oct 2026, from her objection to Run 5.
#
# Run 5's SAME was correct under the rule as written - the test told N1 to
# ignore every distinguishing word and it obeyed. But the WORD "SAME" carries
# no trace of how much the rule had to erase to get there. Run 1's C6 and
# Run 5's C5 both printed SAME while one erased a single connector and the
# other erased a sentence.
#
# The fix is not to make the tool judge whether an erased word mattered - it
# cannot, and claiming it can is the failure this project exists to refuse.
# The fix is to report HOW MANY words it erased that DIFFERED, and put that
# in the verdict rather than the body. 1 is tidying. 10 is erasing. The
# reader judges; the number is not a judgement, it is a quantity.
SAME_N1 = "SAME (N1)"

# ---------------------------------------------------------------------------
# N1 - the tidying rule. Agreed 20 Sep 2026, before this file existed.
#
# THE CATEGORY, which is the actual rule: words that join two timepoints and
# carry no information about WHAT was measured, WHEN, or IN WHOM.
#
# The cap of 5 is a tripwire, not a principle. It exists so that adding a
# sixth entry forces a deliberate act rather than a reflex. The assert below
# makes the code enforce it instead of the comment merely requesting it.
#
# Deliberately NOT in the list, and why:
#   "change"    "change in X" and "X" are different endpoints - a delta
#               versus a level. Dropping it destroys that distinction.
#   "baseline"  names the timepoint the change is measured from.
#   the/in/of   would pass the category test, but no case we have met needs
#               them, and every entry spends audit budget.
# ---------------------------------------------------------------------------
N1_DROP = ["to", "from", "through", "and", ","]
N1_CAP = 5
assert len(N1_DROP) <= N1_CAP, (
    f"N1 has {len(N1_DROP)} entries, cap is {N1_CAP}. Raising the cap is "
    f"allowed, but it must be re-justified in writing first.")

PATHS = {
    "C5": ("MAIN MEASUREMENT",
           "protocolSection.outcomesModule.primaryOutcomes[0].measure"),
    "C6": ("MEASUREMENT TIMING",
           "protocolSection.outcomesModule.primaryOutcomes[0].timeFrame"),
}


def dig(rec, path):
    node = rec
    for raw in path.split("."):
        m = re.match(r"^([A-Za-z0-9_]+)(?:\[(\d+)\])?$", raw)
        key, idx = m.group(1), m.group(2)
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
        if idx is not None:
            if not isinstance(node, list) or int(idx) >= len(node):
                return None
            node = node[int(idx)]
    return node


def tidy(text, drop=None):
    """Apply N1. Returns (tidied string, KEPT tokens, REMOVED tokens,
    punctuation-removal counts). Nothing else happens to the text - no
    stemming, no synonyms, no guessing.

    The REMOVED list is the audit trail and is the only reason this function
    returns four things instead of two. Without it a verdict can say two
    strings matched but not what was thrown away to make them match."""
    drop = N1_DROP if drop is None else drop
    chars = [d for d in drop if len(d) == 1 and not d.isalnum()]
    words = {d.lower() for d in drop if d not in chars}
    t = text.lower()
    punct = Counter()
    for c in chars:
        punct[c] += t.count(c)
        t = t.replace(c, " ")
    kept, removed = [], []
    for w in t.split():
        (removed if w in words else kept).append(w)
    return " ".join(kept), kept, removed, punct


def wrap(label, text, width=62, indent=14):
    out, line = [], ""
    for word in str(text).split():
        if len(line) + len(word) + 1 > width:
            out.append(line); line = word
        else:
            line = f"{line} {word}".strip()
    out.append(line)
    pad = " " * indent
    return "\n".join((f"    {label:<10}{out[0]}" if i == 0 else pad + l)
                     for i, l in enumerate(out))


def check(cid, a, b, drop=None):
    name, path = PATHS[cid]
    drop = N1_DROP if drop is None else drop
    ra, rb = dig(a, path), dig(b, path)

    lines = []
    if ra is not None and rb is not None:
        lines.append(wrap("A raw", f'"{ra}"'))
        lines.append(wrap("B raw", f'"{rb}"'))
        lines.append("")
    lines.append(f"    {path}")
    lines.append(wrap(f"N1 ({len(drop)})", " . ".join(repr(d) for d in drop)))

    if ra is None or rb is None:
        which = [l for l, r in (("A", ra), ("B", rb)) if r is None]
        lines.append(f"    o   absent from {', '.join(which)}. Absent is not equal.")
        return NOT_REPORTED, lines

    identical_raw = (ra == rb)
    ta, toka, rma, pa = tidy(ra, drop)
    tb, tokb, rmb, pb = tidy(rb, drop)

    lines.append(wrap("A tidied", ta))
    lines.append(wrap("B tidied", tb))

    ca, cb = Counter(toka), Counter(tokb)
    shared, only_a, only_b = ca & cb, ca - cb, cb - ca

    def fmt(c):
        return " . ".join(k for k, v in sorted(c.items()) for _ in range(v)) or "(none)"

    lines.append(wrap("shared", fmt(shared)))
    lines.append(wrap("only A", fmt(only_a)))
    lines.append(wrap("only B", fmt(only_b)))

    if not only_a and not only_b:
        # ERASED DIFFERENCE.
        # Of the words N1 removed, how many were NOT matched by the same word
        # removed from the other string? Those are exactly the words that
        # WOULD have appeared as only-in-A or only-in-B had N1 left them
        # alone - i.e. the words whose removal changed the verdict.
        # A word N1 dropped from BOTH strings changed nothing and is not
        # counted. That asymmetry is the whole measurement.
        da, db = Counter(rma), Counter(rmb)
        erased = da - db
        erased.update(db - da)
        n_erased = sum(erased.values())
        n_punct = sum((pa - pb).values()) + sum((pb - pa).values())

        lines.append(wrap("A N1 cut", fmt(da)))
        lines.append(wrap("B N1 cut", fmt(db)))
        lines.append(wrap("erased", fmt(erased) if n_erased else "(none)"))

        verdict = SAME if n_erased == 0 else SAME_N1

        if identical_raw:
            lines.append("    =   The two strings were IDENTICAL BEFORE N1 was "
                         "applied. N1 did not manufacture this match.")
        elif n_erased == 0:
            lines.append("    =   N1 removed nothing that DIFFERED between the two "
                         "strings. Whatever it")
            lines.append("        removed, it removed from both. The match does not "
                         "depend on the rule,")
            lines.append("        so the verdict is a plain SAME.")
        else:
            s = "" if n_erased == 1 else "S"
            lines.append(f"    !   AGREEMENT REQUIRED ERASING {n_erased} WORD{s} "
                         f"THAT DIFFERED - listed above")
            lines.append("        as 'erased'. The tool does NOT judge whether those "
                         "words mattered; it")
            lines.append("        cannot, and this is not the place where it starts "
                         "pretending to. It")
            lines.append("        reports the SIZE of the erasure. A small number is "
                         "tidying. A large")
            lines.append("        one is a rule doing work the evidence should be "
                         "doing. Read the two")
            lines.append("        RAW lines at the top and decide which this is.")

        if n_punct:
            lines.append(f"    o   also removed {n_punct} punctuation mark(s) "
                         f"unevenly. NOT counted above:")
            lines.append("        punctuation is orthographic, and counting it would "
                         "inflate a number")
            lines.append("        that is meant to mean 'words of substance thrown "
                         "away'.")

        if ta != tb:
            lines.append("    o   SAME WORDS, DIFFERENT ORDER. This check compares "
                         "the SET of words,")
            lines.append("        not their sequence - word order is being treated as "
                         "carrying no")
            lines.append("        meaning. See KNOWN-LIMITATIONS.md, L3, for when "
                         "that is wrong.")

        return verdict, lines

    lines.append("    ?   Words differ after N1. This tool does not rule on what "
                 "free text MEANS,")
    lines.append("        in either direction. The difference is listed above; "
                 "you rule on it.")
    return REVIEW, lines


def emit(cid, verdict, lines):
    name = PATHS[cid][0]
    record.log(cid, verdict)
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


def edited(rec, cid, value):
    r = copy.deepcopy(rec)
    key = "measure" if cid == "C5" else "timeFrame"
    r["protocolSection"]["outcomesModule"]["primaryOutcomes"][0][key] = value
    return r


def selftest():
    s = load()
    if len(s) < 2:
        print("Need two snapshots in data/."); sys.exit(1)
    a, b = s[0][1], s[1][1]

    def head(n, t):
        record.set_run(f"Run {n}")
        print("=" * 72); print(f"RUN {n} - {t}"); print("=" * 72)

    head(1, "the real thing, both 14 Sep snapshots unedited")
    emit("C5", *check("C5", a, b))
    emit("C6", *check("C6", a, b))

    head(2, "C6 forced identical - B's timeFrame set byte-for-byte to A's")
    emit("C6", *check("C6", a, edited(b, "C6", dig(a, PATHS["C6"][1]))))

    head(3, 'C6 one digit changed - B set to "Baseline to Week 13"')
    emit("C6", *check("C6", a, edited(b, "C6", "Baseline to Week 13")))

    head(4, "C5 unrelated measurement - B set to body weight")
    emit("C5", *check("C5", a,
                      edited(b, "C5", "Change in body weight from baseline to Week 12")))

    # Run 5. To make these two sentences match, N1 must swallow every word
    # that distinguishes them. That takes 9 more entries - the list grows
    # from 5 to 14. The size of that jump is itself the finding.
    OVERREACH = N1_DROP + ["the", "4", "wake", "trials",
                           "(msl)", "on", "by", "dose", "level"]
    head(5, f"N1 OVERREACH - drop list grown from {len(N1_DROP)} to "
            f"{len(OVERREACH)} entries")
    emit("C5", *check("C5", a, b, drop=OVERREACH))
    print("    ^ Read in this order: the two RAW lines, the verdict, 'erased'.")
    print("      The verdict is SAME (N1), not SAME. The parenthesis says the")
    print("      match exists ONLY because the rule removed words that differed,")
    print("      and the count says how many. Run 1's C6 above reached agreement")
    print("      by erasing 1 word. This reached it by erasing an order of")
    print("      magnitude more. The bare word SAME hid that difference; a number")
    print("      cannot. The tool still never decides whether 'by dose level'")
    print("      matters - it states the price of agreement and hands you the")
    print("      judgement, which is the only honest division of labour here.\n")

    print("Now mark each run against acceptance/S5-free-text.md.")
    print("Or re-run with --record and let the tool write the verdicts for you.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        if "--record" in sys.argv:
            body = record.capture(selftest)
            record.append("S5-free-text.md", "S5 selftest, 5 runs", body)
        else:
            selftest()
    else:
        s = load()
        print(f"A = {s[0][0]}   B = {s[1][0]}\n")
        emit("C5", *check("C5", s[0][1], s[1][1]))
        emit("C6", *check("C6", s[0][1], s[1][1]))
