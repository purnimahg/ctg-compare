#!/usr/bin/env python3
"""
ctg-compare - step 1: fetch

Downloads the ClinicalTrials.gov record for each trial ID in TRIALS and
saves one file per trial into data/, stamped with today's date.

Run:  python3 fetch.py
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

TRIALS = [
    "NCT06470828",   # Takeda   - TAK-861 / oveporexton
    "NCT07455383",   # Alkermes - ALKS 2680 / alixorexton
]

BASE = "https://clinicaltrials.gov/api/v2/studies"
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


def fetch_one(nct_id):
    """Ask the registry for one record. Returns (url, http_status, raw_bytes)."""
    url = f"{BASE}/{nct_id}?format=json"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return url, resp.status, resp.read()


def die(message):
    """Stop loudly. Nothing gets saved on the way out."""
    print("FAILED")
    print("")
    for line in message.strip().split("\n"):
        print("  " + line)
    print("")
    sys.exit(1)


def main():
    DATA.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc)
    datestr = stamp.strftime("%Y-%m-%d")

    log_lines = []
    saved = []

    for nct_id in TRIALS:
        print(f"fetching {nct_id} ... ", end="", flush=True)

        try:
            url, status, raw = fetch_one(nct_id)
        except urllib.error.HTTPError as e:
            die(f"{nct_id}: the server answered HTTP {e.code} ({e.reason}).\n"
                f"Nothing was saved.\n"
                f"Check the ID is real: https://clinicaltrials.gov/study/{nct_id}")
        except urllib.error.URLError as e:
            die(f"{nct_id}: could not reach clinicaltrials.gov ({e.reason}).\n"
                f"Nothing was saved. Check your internet connection.")

        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            die(f"{nct_id}: the server sent something that is not JSON.\n"
                f"Nothing was saved.")

        # Known-answer check: did we get back the record we actually asked for?
        got_id = record["protocolSection"]["identificationModule"]["nctId"]
        if got_id != nct_id:
            die(f"Asked for {nct_id} but the server returned {got_id}.\n"
                f"Nothing was saved.")

        out = DATA / f"{nct_id}_{datestr}.json"
        out.write_text(json.dumps(record, indent=2), encoding="utf-8")
        saved.append(out)

        updated = record["protocolSection"]["statusModule"]["lastUpdatePostDateStruct"]["date"]
        print(f"ok   ({len(raw):,} bytes; sponsor last edited this record {updated})")

        log_lines.append(
            f"{stamp.isoformat(timespec='seconds')}  HTTP {status}  "
            f"{len(raw)} bytes  record_last_updated={updated}  {url}"
        )

    with open(HERE / "retrieval_log.txt", "a", encoding="utf-8") as fh:
        fh.write("\n".join(log_lines) + "\n")

    print("")
    print(f"Saved {len(saved)} file(s) into  {DATA}")
    for p in saved:
        print(f"   {p.name}")
    print("")
    print("Retrieval details appended to  retrieval_log.txt")


if __name__ == "__main__":
    main()
