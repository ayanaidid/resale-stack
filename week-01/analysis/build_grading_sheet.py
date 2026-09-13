"""
build_grading_sheet.py

What this does: joins the 30 source listings to their extracted records
and writes a single CSV for hand-grading. One row per listing, with the
input on the left, the model's output in the middle, and empty columns
on the right for my own judgments.

In: data/listings.csv (filtered to in_run_30 == "Y")
    data/extractions.jsonl
Out: analysis/grading_sheet.csv

Fails: raises KeyError if a listing tagged in_run_30 has no matching
extraction record. Handles the known malformed record (missing
'confidence') by writing an empty cell rather than crashing.

Run from week-01/:  python3 analysis/build_grading_sheet.py
"""

import csv
import json
from pathlib import Path

LISTINGS = Path("data/listings.csv")
EXTRACTIONS = Path("data/extractions.jsonl")
OUT = Path("analysis/grading_sheet.csv")

# Columns I fill in by hand while grading.
GRADING_COLUMNS = [
    "my_condition_tier",
    "tier_correct",           # Y / N
    "miss_type",              # wrong_extraction / hallucinated / wrong_tier / missed_flaw / misread_euphemism / none
    "field_errors",           # which fields were wrong, comma separated
    "euphemism_judgment",     # agree / disagree / n_a  -- vs my rubric predictions
    "grading_notes",
]


def main():
    extractions = {}
    for line in EXTRACTIONS.open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        extractions[record["listing_id"]] = record

    rows = []
    with LISTINGS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("in_run_30") != "Y":
                continue
            lid = row["listing_id"]
            ex = extractions[lid]

            rows.append({
                # --- input ---
                "listing_id": lid,
                "source_platform": row["source_platform"],
                "item_type": row["item_type"],
                "raw_title": row["raw_title"],
                "raw_description": row["raw_description"],
                "stated_condition": row["stated_condition"],
                "source_url": row["source_url"],
                # --- model output ---
                "m_brand": ex.get("brand", ""),
                "m_model": ex.get("model", ""),
                "m_subcategory": ex.get("subcategory", ""),
                "m_material": ex.get("material", ""),
                "m_disclosed_flaws": " | ".join(ex.get("disclosed_flaws", [])),
                "m_condition_tier": ex.get("condition_tier", ""),
                "m_seller_speak": ex.get("seller_speak_translation", ""),
                "m_confidence": ex.get("confidence", ""),
                # --- my grading, filled in by hand ---
                **{col: "" for col in GRADING_COLUMNS},
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
