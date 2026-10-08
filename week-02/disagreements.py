"""
disagreements.py — find listings where all three v2 models disagreed with my
tier, and write a review worksheet.

In  — labels.csv, the three predictions_{model}_v2.jsonl files, listings.csv
Out — data/disagreements_v2.csv, one row per listing all models got wrong,
      with blank columns for my review
"""

import csv
from pathlib import Path

from score import load_labels, load_predictions
from normalize import normalize_tier

HERE = Path(__file__).parent
MODELS = ["claude-sonnet-5", "claude-haiku-4-5", "claude-opus-5"]
LISTINGS_CSV = HERE.parent / "week-01" / "data" / "listings.csv"
OUT = HERE / "data" / "disagreements_v2.csv"


def main():
    labels = load_labels(HERE / "data" / "labels.csv")
    preds = {m: load_predictions(HERE / "data" / f"predictions_{m}_v2.jsonl") for m in MODELS}
    with LISTINGS_CSV.open("r", encoding="utf-8", newline="") as f:
        listings = {row["listing_id"]: row for row in csv.DictReader(f)}

    rows = []
    for lid, lab in labels.items():
        mine, _ = normalize_tier(lab["label_condition_tier"])
        theirs = [normalize_tier(preds[m][lid]["condition_tier"])[0] for m in MODELS]
        if all(t != mine for t in theirs):
            rows.append({
                "listing_id": lid,
                "my_tier": mine,
                "sonnet": theirs[0], "haiku": theirs[1], "opus": theirs[2],
                "models_agree": "Y" if len(set(theirs)) == 1 else "N",
                "my_confidence": lab["label_confidence"],
                "boundary_case": lab["boundary_case"],
                "my_notes": lab["label_notes"],
                "title": listings[lid]["raw_title"],
                "description": listings[lid]["raw_description"],
                "cause": "",
                "review_notes": "",
            })

    rows.sort(key=lambda r: r["models_agree"], reverse=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    agree = sum(1 for r in rows if r["models_agree"] == "Y")
    print(f"All three wrong: {len(rows)}  |  of those, models agree with each other: {agree}")


if __name__ == "__main__":
    main()
