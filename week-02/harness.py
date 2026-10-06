#!/usr/bin/env python3
"""
What this does =
    Reads week-01/data/listings.csv and week-02/data/labels.csv, joins them on
    listing_id, and keeps only listings that have a label (the golden set).
    Runs each joined row through extract_listing() (imported from
    week-01/extract.py, not reimplemented) for the model given on the command
    line, and writes one JSON object per row to week-02/data/predictions_{model}.jsonl.

Usage: python3 harness.py <model> [--limit N]

In  — week-01/data/listings.csv, week-02/data/labels.csv (joined on listing_id)
Out — week-02/data/predictions_{model}.jsonl, one JSON object per line:
      listing_id, the full model output (extracted fields + token usage +
      cost), appended, not overwritten.

Resumable — rerunning skips any listing_id already present in
predictions_{model}.jsonl.

Fails — API errors retry with backoff inside call_with_retry() (week-01);
anything that still raises after that is logged to errors.log with the
listing_id and the run continues.
"""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

HERE = Path(__file__).parent
LISTINGS_CSV = HERE.parent / "week-01" / "data" / "listings.csv"
LABELS_CSV = HERE / "data" / "labels.csv"
ERROR_LOG = HERE / "errors.log"

sys.path.insert(0, str(HERE.parent / "week-01"))
from extract import call_with_retry, extract_listing, MODEL_RATES  # noqa: E402

logging.basicConfig(
    filename=ERROR_LOG,
    level=logging.ERROR,
    format="%(asctime)s %(message)s",
    force=True,
)


def load_joined_rows(listings_csv, labels_csv):
    """Join listings and labels on listing_id, keep only labeled listings."""
    with listings_csv.open("r", encoding="utf-8", newline="") as f:
        listings_by_id = {row["listing_id"]: row for row in csv.DictReader(f)}

    with labels_csv.open("r", encoding="utf-8", newline="") as f:
        label_ids = [row["listing_id"] for row in csv.DictReader(f)]

    joined = [listings_by_id[lid] for lid in label_ids if lid in listings_by_id]
    return joined


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


def score(labels, predictions):
    """
    Compare golden labels against model predictions and report agreement.

    Will join labels.csv rows to predictions_{model}.jsonl rows by
    listing_id, normalize brand/subcategory/condition_tier (via
    week-02/normalize.py) on both sides, and report per-field accuracy plus
    a confusion matrix for condition_tier. Not implemented yet.
    """
    raise NotImplementedError


def main():
    parser = argparse.ArgumentParser(description="Run extract_listing over the labeled golden set.")
    parser.add_argument("model", help="Model name to pass to extract_listing, e.g. claude-sonnet-5")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N joined rows (for testing)")
    args = parser.parse_args()

    if args.model not in MODEL_RATES:
        raise SystemExit(f"Unknown model '{args.model}'. Valid: {', '.join(MODEL_RATES)}")

    if not LISTINGS_CSV.exists():
        raise SystemExit(f"Cannot find {LISTINGS_CSV}")
    if not LABELS_CSV.exists():
        raise SystemExit(f"Cannot find {LABELS_CSV}")

    rows = load_joined_rows(LISTINGS_CSV, LABELS_CSV)
    if len(rows) != 150:
        print(f"WARNING: expected 150 joined rows, got {len(rows)}")

    if args.limit is not None:
        rows = rows[: args.limit]

    output_path = HERE / "data" / f"predictions_{args.model}.jsonl"

    done_ids = load_done_ids(output_path)
    if done_ids:
        print(f"Resuming: {len(done_ids)} listings already predicted, skipping those.")

    todo = [row for row in rows if row["listing_id"] not in done_ids]
    print(f"{len(rows)} listings joined, {len(todo)} left to process.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    processed = 0
    failed = 0
    with output_path.open("a", encoding="utf-8") as out:
        for i, row in enumerate(todo, start=1):
            listing_id = row["listing_id"]
            print(f"[{i}/{len(todo)}] {listing_id} ...", end=" ", flush=True)
            try:
                result = call_with_retry(row, model=args.model)
            except Exception as e:
                logging.error("listing_id=%s model=%s error=%s", listing_id, args.model, e)
                failed += 1
                print("FAILED (logged to errors.log)")
                continue

            record = {"listing_id": listing_id, **result}
            out.write(json.dumps(record) + "\n")
            out.flush()
            processed += 1
            print("done")

    print(f"Finished. {processed} predicted, {failed} failed this run.")


if __name__ == "__main__":
    main()
