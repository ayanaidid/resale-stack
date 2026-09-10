#!/usr/bin/env python3
"""
What this does = 
    Reads data/listings.csv, filters to the rows tagged for this run (in_run_30 == "Y"), and runs each one through extract_listing().
    Results are appended to data/extractions.jsonl, one JSON object per line, keyed back to the source row by listing_id. 
    Failures (after retries) are logged to errors.log with the listing_id and the error.

Rerunning the script skips any listing_id already present in data/extractions.jsonl, so an interrupted run can be resumed by just
running it again.

In — data/listings.csv. in_run_30 == "Y" drives the filter
Out — data/extractions.jsonl, one JSON object per line, joined back to the source row by listing_id. Appended, not overwritten.

Fails:
    API errors retry five times with exponential backoff, then get logged to errors.log and the run continues
    Non-API errors (a KeyError, a typo) fail immediately without retrying, log, and continue — so a bug in extract_listing produces 30 error lines, not a crash
    Malformed lines in extractions.jsonl from a crash get skipped with a warning and that listing gets reprocessed
    Writes are flushed after each row, so a crash loses at most one row
"""

import csv
import json
import logging
import os
import random
import time
from pathlib import Path

from dotenv import load_dotenv
import anthropic

load_dotenv()

LISTINGS_CSV = Path("data/listings.csv")
OUTPUT_JSONL = Path("data/extractions.jsonl")
ERROR_LOG = Path("errors.log")

MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 1.0
BACKOFF_MULTIPLIER = 2.0

logging.basicConfig(
    filename=ERROR_LOG,
    level=logging.ERROR,
    format="%(asctime)s %(message)s",
)


def extract_listing(row):
    """
    Take a single listing (dict) from listings.csv, as produced by
    csv.DictReader, and call the Anthropic API to pull structured
    resale data out of it.

    Args:
        row: dict mapping CSV column names (listing_id, source_platform,
            raw_title, raw_description, listed_price, stated_condition,
            etc.) to their string values for one listing.

    Returns:
        dict of extracted fields to write out as JSON. Should NOT
        include "listing_id" itself -- the caller attaches that
        separately when writing the record.

    Raises:
        Whatever the anthropic client raises on API failure (e.g.
        anthropic.APIError and its subclasses) -- the caller retries
        on those with exponential backoff.
    """
    raise NotImplementedError("extract_listing is not implemented yet")


def load_done_ids(path):
    """Return the set of listing_ids already written to the output file."""
    done = set()
    if not path.exists():
        return done
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(f"Warning: could not parse {path} line {line_number}, skipping")
                continue
            listing_id = record.get("listing_id")
            if listing_id:
                done.add(listing_id)
    return done


def call_with_retry(row):
    """Call extract_listing, retrying API errors with exponential backoff."""
    delay = INITIAL_BACKOFF_SECONDS
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return extract_listing(row)
        except anthropic.APIError as e:
            if attempt == MAX_RETRIES:
                raise
            sleep_for = delay + random.uniform(0, delay * 0.1)
            print(
                f"  API error on attempt {attempt}/{MAX_RETRIES} ({e}); "
                f"retrying in {sleep_for:.1f}s"
            )
            time.sleep(sleep_for)
            delay *= BACKOFF_MULTIPLIER


def main():
    if not LISTINGS_CSV.exists():
        raise SystemExit(f"Cannot find {LISTINGS_CSV}")

    done_ids = load_done_ids(OUTPUT_JSONL)
    if done_ids:
        print(f"Resuming: {len(done_ids)} listings already extracted, skipping those.")

    with LISTINGS_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if row.get("in_run_30") == "Y"]

    todo = [row for row in rows if row["listing_id"] not in done_ids]
    print(f"{len(rows)} listings in run, {len(todo)} left to process.")

    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)

    processed = 0
    failed = 0
    with OUTPUT_JSONL.open("a", encoding="utf-8") as out:
        for i, row in enumerate(todo, start=1):
            listing_id = row["listing_id"]
            print(f"[{i}/{len(todo)}] {listing_id} ...", end=" ", flush=True)
            try:
                result = call_with_retry(row)
            except Exception as e:
                logging.error("listing_id=%s error=%s", listing_id, e)
                failed += 1
                print("FAILED (logged to errors.log)")
                continue

            record = {"listing_id": listing_id, **result}
            out.write(json.dumps(record) + "\n")
            out.flush()
            processed += 1
            print("done")

    print(f"Finished. {processed} extracted, {failed} failed this run.")


if __name__ == "__main__":
    main()
