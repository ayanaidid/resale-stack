"""
What this does = Score model predictions against the golden labels. 

In = week-02/data/labels.csv, week-02/data/predictions_{model}.jsonl w/ model name passed on the command line
Out = prints label, prediction, and match counts to the terminal

What happens if predictions file is missing or counts don't match = a missing predictions file exits immediately with a 
message naming the path it looked for; a match count other than 150 prints all three counts first, then exits.

"""

import argparse
import csv
import json
from pathlib import Path

from normalize import normalize_brand, normalize_subcategory, normalize_tier

HERE = Path(__file__).parent
LABELS_CSV = HERE / "data" / "labels.csv"

def load_labels(path):
    """Return {listing_id: label_row} from labels.csv."""
    with path.open("r", encoding="utf-8", newline="") as f:
        return {row["listing_id"]: row for row in csv.DictReader(f)}


def load_predictions(path):
    """Return {listing_id: prediction_record} from a predictions JSONL file."""
    predictions = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            predictions[record["listing_id"]] = record
    return predictions


def main():
    parser = argparse.ArgumentParser(description="Score model predictions against the golden labels.")
    parser.add_argument("model", help="Model whose predictions to score, e.g. claude-sonnet-5")
    args = parser.parse_args()

    predictions_path = HERE / "data" / f"predictions_{args.model}.jsonl"
    if not predictions_path.exists():
        raise SystemExit(f"No predictions found at {predictions_path}")

    labels = load_labels(LABELS_CSV)
    predictions = load_predictions(predictions_path)
    shared_ids = labels.keys() & predictions.keys()

    print(f"Labels: {len(labels)}")
    print(f"Predictions: {len(predictions)}")
    print(f"Matched: {len(shared_ids)}")

    if len(shared_ids) != 150:
        raise SystemExit("Expected 150 matched listings — stopping.")


if __name__ == "__main__":
    main()
