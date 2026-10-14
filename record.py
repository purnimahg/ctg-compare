#!/usr/bin/env python3
"""
ctg-compare - the acceptance recorder.

WHY THIS FILE EXISTS. Added 3 Oct 2026.

Twice now an acceptance record has disagreed with what the tool actually
printed, and both times the RECORD was the thing that was wrong:

  20 Sep   the block was marked "Yes" directly above a written description
           of a failure.
  3 Oct    Run 1's C6 and Run 5's C5 printed SAME (N1), with counts of 1 and
           10. They were written down as SAME - erasing the exact distinction
           the amendment was created to make - and the block was still
           marked YES.

Neither of those is carelessness to be fixed with more carefulness. Hand
transcription from a screen into a document is a step with NO PROVENANCE:
the number in the record is only as good as the typing, and nobody proofreads
their own typing against a screen they have already closed.

A bioanalytical run does not let the analyst retype instrument output into
the report. The instrument writes the result. The analyst signs the
judgement. That division is not bureaucracy - it is the reason the report
means anything.

So, from here on:

    the TOOL writes the verdicts        - transcription is not a judgement
                                          and belongs to nobody
    the HUMAN writes the criteria first - and marks PASS or FAIL after
                                          - marking IS a judgement and
                                            belongs to a person

This module is also a down-payment on S8 (provenance). Any number in the
final report that a human retyped is a number with no chain of custody,
and the whole claim of this repo is that every number has one.
"""

import io
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ACCEPTANCE = HERE / "acceptance"

_ROWS = []
_RUN = ""


def set_run(label):
    """Name the run that subsequent verdicts belong to."""
    global _RUN
    _RUN = str(label)


def log(cid, verdict):
    """Called by the checker for every verdict it emits. The checker is the
    only thing that ever writes a verdict string."""
    _ROWS.append((_RUN, cid, verdict))


def stamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _table():
    if not _ROWS:
        return "    (no verdicts emitted - this is itself a failure)\n"
    wr = max(len(r) for r, _, _ in _ROWS)
    wv = max(len(v) for _, _, v in _ROWS)
    out = []
    for run, cid, verdict in _ROWS:
        out.append(f"    {run:<{wr}}  {cid}  {verdict:<{wv}}   [    ]")
    return "\n".join(out) + "\n"


def capture(fn):
    """Run fn(), returning (printed output, verdict rows). Output still goes
    to the terminal - this captures in addition, it does not swallow."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn()
    body = buf.getvalue()
    print(body, end="")
    return body


def append(acceptance_filename, tag, body):
    """APPEND a machine-written results block to the acceptance file. Never
    edits what is already there - an acceptance file is evidence, and
    evidence is added to, not revised."""
    path = ACCEPTANCE / acceptance_filename
    if not path.exists():
        print(f"\n!! {path} does not exist. Nothing appended.")
        return None

    block = (
        f"\n\n---\n\n"
        f"## MACHINE-WRITTEN RESULTS - {tag} - {stamp()}\n\n"
        f"    Written by record.py from the tool's own output. NOT typed by\n"
        f"    hand. The verdict column is the tool's; the bracket is yours.\n\n"
        f"    Put P or F in each bracket. One mark per line, no summary mark,\n"
        f"    and no 'yes, but' - a line that needs a sentence to explain it\n"
        f"    is an F with a note underneath.\n\n"
        f"{_table()}\n"
        f"    Notes on any F:\n\n\n"
        f"<details><summary>full tool output, verbatim</summary>\n\n"
        f"```\n{body}```\n\n</details>\n")

    with path.open("a") as fh:
        fh.write(block)
    print(f"\n>> {len(_ROWS)} verdicts appended to acceptance/{acceptance_filename}")
    print(f">> Open it, put P or F in each bracket. You type no verdicts.")
    return path
