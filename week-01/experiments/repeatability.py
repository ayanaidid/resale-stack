"""
repeatability.py

What this does: runs three listings through extract_listing() five times
each, with identical settings, and records every result. Tests whether
the same input produces the same output across repeated calls, and
whether that depends on how ambiguous the listing is.

Originally designed as a temperature matrix (3 listings x 2 temperatures
x 5 runs). Sonnet 5 rejects non-default temperature/top_p/top_k with a
400 error, so the temperature axis is unavailable. Holding all settings
at default removes the sampling-parameter confound entirely: any
variance observed is not attributable to a knob I set.

In: data/listings.csv, filtered to the three listing_ids below.
Out: experiments/repeatability_runs.jsonl, one JSON object per call,
     with listing_id and run number attached.

Fails: no retry wrapper. An API error stops the script. The file is
opened in append mode, so a partial run followed by a rerun will
duplicate rows — delete the output file before rerunning.
"""

import csv
import json
from pathlib import Path

from extract import extract_listing

# L001 = clean, detailed description (Courreges skirt, "never worn, with tag")
# L007 = contradictory (eBay sample jeans, "new without tag with possible irregularities")
# L022 = vague/minimal ("Cream converse dupes")
LISTINGS = ["L001", "L007", "L022"]
REPEATS = 5

OUT = Path("experiments/repeatability_runs.jsonl")


def main():
    rows = {r["listing_id"]: r for r in csv.DictReader(open("data/listings.csv"))}
    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("a", encoding="utf-8") as out:
        for lid in LISTINGS:
            for run in range(1, REPEATS + 1):
                print(f"{lid} run={run}/{REPEATS} ...", end=" ", flush=True)
                result = extract_listing(rows[lid])
                record = {
                    "listing_id": lid,
                    "run": run,
                    **result,
                }
                out.write(json.dumps(record) + "\n")
                out.flush()
                print("done")

    print(f"\nFinished. {len(LISTINGS) * REPEATS} calls written to {OUT}")


if __name__ == "__main__":
    main()
