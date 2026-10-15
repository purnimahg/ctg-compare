#!/usr/bin/env python3
"""
ctg-compare - provenance.

PUBLISHED, in this project, means: public repo, runnable by a stranger,
**every claim traceable to source field + retrieval date.** This module is
the clause after the second comma. Without it the repo holds thirteen
verdicts and no way for a reader to tell which bytes produced them.

TWO HONEST DISTINCTIONS, both of which a careless version would get wrong.

1. RESPONSE BYTES are not FILE BYTES.
   retrieval_log.txt records the API response as received: 57,613 for
   NCT06470828 on 14 Sep. The file on disk is 101,421, because fetch.py
   pretty-prints the JSON before saving. Both numbers are correct. Printing
   one under the other's label is off by 76%, looks entirely plausible, and
   cannot be checked at a glance. See L8.

2. A CHECKSUM YOU GENERATE FROM THE THING YOU ARE CHECKING IS DECORATION.
   provenance.json records a fingerprint AT FETCH TIME, from the bytes as
   received. The four snapshots already in data/ were fetched on 2 and 14
   Sep, before this file existed. Computing their fingerprints now reads them
   from the files being checked, so the manifest would agree by construction
   and prove nothing. Those snapshots are therefore reported as
   `computed post hoc` and real tamper detection begins at the next fetch.

   ● That column is the most defensible thing in the session and the most
   tempting to drop. Writing the hashes in today and calling it provenance
   would look identical to a reader and be worth nothing.
"""

import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
LOG = HERE / "retrieval_log.txt"
MANIFEST = HERE / "provenance.json"

SNAP = re.compile(r"^(NCT\d+)_(\d{4}-\d{2}-\d{2})\.json$")
LOGLINE = re.compile(
    r"^(?P<ts>\S+)\s+HTTP (?P<status>\d+)\s+(?P<bytes>\d+) bytes\s+"
    r"record_last_updated=(?P<updated>\S+)\s+(?P<url>\S+)")


class ProvenanceMissing(Exception):
    pass


def protocol_fingerprint(record):
    blob = json.dumps(record["protocolSection"], sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:12]


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]


def retrieval_index():
    """{(nct, YYYY-MM-DD): {ts, status, response_bytes, updated, url}}"""
    if not LOG.exists():
        raise ProvenanceMissing(
            f"{LOG.name} is missing. Every number in the report traces back "
            f"to a retrieval recorded in that file; without it there is no "
            f"chain of custody and the report must not be written.")
    idx = {}
    for line in LOG.read_text().splitlines():
        m = LOGLINE.match(line.strip())
        if not m:
            continue
        nct = re.search(r"(NCT\d+)", m.group("url"))
        if not nct:
            continue
        day = m.group("ts")[:10]
        idx[(nct.group(1), day)] = {
            "ts": m.group("ts"), "status": int(m.group("status")),
            "response_bytes": int(m.group("bytes")),
            "updated": m.group("updated"), "url": m.group("url")}
    return idx


def manifest():
    if not MANIFEST.exists():
        return {}
    try:
        return json.loads(MANIFEST.read_text())
    except json.JSONDecodeError:
        return {}


def record_fetch(nct, day, fingerprint, response_bytes, ts):
    """Called by fetch.py, from the bytes AS RECEIVED. This is the only
    place a fingerprint is recorded independently of the file on disk."""
    m = manifest()
    m[f"{nct}_{day}"] = {"nct": nct, "snapshot": day, "retrieved": ts,
                         "response_bytes": response_bytes,
                         "protocol_fingerprint": fingerprint,
                         "recorded": "at fetch"}
    MANIFEST.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")


def facts(nct, day, record, today=None):
    """Everything provenance-bearing about one snapshot. Raises if the
    retrieval that produced it was never logged."""
    idx = retrieval_index()
    path = DATA / f"{nct}_{day}.json"
    key = (nct, day)
    if key not in idx:
        raise ProvenanceMissing(
            f"{path.name} exists but no retrieval is logged for {nct} on "
            f"{day}. A snapshot with no recorded retrieval has no chain of "
            f"custody. Refusing to write a report that cites it.")
    log = idx[key]
    fp = protocol_fingerprint(record)
    man = manifest().get(f"{nct}_{day}")

    if man and man.get("protocol_fingerprint") == fp:
        verified = "recorded at fetch — matches"
    elif man:
        verified = "RECORDED AT FETCH — DOES NOT MATCH"
    else:
        verified = "computed post hoc — not independently verified"

    today = today or date.today()
    age = (today - date(int(day[:4]), int(day[5:7]), int(day[8:10]))).days
    return {
        "nct": nct, "snapshot": day, "file": path.name,
        "retrieved": log["ts"], "status": log["status"],
        "response_bytes": log["response_bytes"],
        "file_bytes": path.stat().st_size,
        "file_sha256_12": file_sha(path),
        "protocol_fingerprint_12": fp,
        "sponsor_last_edited": log["updated"],
        "age_days": age, "verified": verified,
        "url": log["url"],
    }
