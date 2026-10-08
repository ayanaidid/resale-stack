"""
What this does = Score model predictions against the golden labels. 

In = week-02/data/labels.csv, week-02/data/predictions_{model}.jsonl w/ model name passed on the command line
Out = prints label, prediction, match counts to the terminal, agreement, the confusion matrix, the matrix, and the slice.

What happens if predictions file is missing or counts don't match = a missing predictions file exits immediately with a 
message naming the path it looked for; a match count other than 150 prints all three counts first, then exits.

"""

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

from normalize import normalize_brand, normalize_subcategory, normalize_tier

HERE = Path(__file__).parent
LABELS_CSV = HERE / "data" / "labels.csv"
TIER_ORDER = ["pristine", "excellent", "very good", "good", "fair", "insufficient information"]
SHORT = {"pristine": "Pri", "excellent": "Exc", "very good": "VG",
         "good": "Good", "fair": "Fair", "insufficient information": "Insuf"}


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


def group_stats(ids, labels, predictions):
    """Return (count, tier agreements, model declined where I graded) for a set of IDs."""
    agree = 0
    model_declined = 0
    for lid in ids:
        mine, _ = normalize_tier(labels[lid]["label_condition_tier"])
        theirs, _ = normalize_tier(predictions[lid]["condition_tier"])
        if mine == theirs:
            agree += 1
        if theirs == "insufficient information" and mine != "insufficient information":
            model_declined += 1
    return len(ids), agree, model_declined


def main():
    parser = argparse.ArgumentParser(description="Score model predictions against the golden labels.")
    parser.add_argument("model", help="Model whose predictions to score, e.g. claude-sonnet-5")
    parser.add_argument("--prompt-version", choices=["v1", "v2"], default="v1")
    args = parser.parse_args()

    suffix = "" if args.prompt_version == "v1" else f"_{args.prompt_version}"
    predictions_path = HERE / "data" / f"predictions_{args.model}{suffix}.jsonl"
    if not predictions_path.exists():
        raise SystemExit(f"No predictions found at {predictions_path}")

    labels = load_labels(LABELS_CSV)
    predictions = load_predictions(predictions_path)
    shared_ids = labels.keys() & predictions.keys()

    print(f"Labels: {len(labels)}")
    print(f"Predictions: {len(predictions)}")
    print(f"Matched: {len(shared_ids)}")

    expected = 150
    if len(shared_ids) != expected:
        raise SystemExit(f"Expected {expected} matched listings — stopping.")
    n = len(shared_ids)

    brand_matches = 0
    for lid in shared_ids:
        mine = normalize_brand(labels[lid]["label_brand"])
        theirs = normalize_brand(predictions[lid]["brand"])
        if mine == theirs:
            brand_matches += 1

    print(f"Brand agreement: {brand_matches}/{n}")

    subcategory_matches = 0
    for lid in shared_ids:
        mine = normalize_subcategory(labels[lid]["label_subcategory"])
        theirs = normalize_subcategory(predictions[lid]["subcategory"])
        if mine == theirs:
            subcategory_matches += 1

    print(f"Subcategory agreement: {subcategory_matches}/{n}")

    tier_matches = 0
    for lid in shared_ids:
        mine, _ = normalize_tier(labels[lid]["label_condition_tier"])
        theirs, _ = normalize_tier(predictions[lid]["condition_tier"])
        if mine == theirs:
            tier_matches += 1

    print(f"Tier agreement: {tier_matches}/{n}")

    matrix = Counter()
    invalid = 0
    for lid in shared_ids:
        mine, mine_valid = normalize_tier(labels[lid]["label_condition_tier"])
        if not mine_valid:
            raise SystemExit(f"Invalid label tier for {lid}: '{mine}'")
        theirs, valid = normalize_tier(predictions[lid]["condition_tier"])
        if not valid:
            invalid += 1
            continue
        matrix[(mine, theirs)] += 1
    print(f"Invalid predictions: {invalid}")

    header = f"{'you/model':>12}"
    for col in TIER_ORDER:
        header += f"{SHORT[col]:>7}"
    print(header)

    for row in TIER_ORDER:
        line = f"{SHORT[row]:>12}"
        for col in TIER_ORDER:
            line += f"{matrix[(row, col)]:>7}"
        print(line)

    diagonal = sum(matrix[(t, t)] for t in TIER_ORDER)
    print(f"Diagonal: {diagonal}  (should equal tier agreement: {tier_matches})")
    print(f"Grid total + invalid: {sum(matrix.values()) + invalid}  (should be {n})")

    tagged = {lid for lid in shared_ids
              if "claim without evidence" in labels[lid]["label_notes"].lower()}
    untagged = shared_ids - tagged
    print(f"Tagged 'claim without evidence': {len(tagged)}  |  Untagged: {len(untagged)}")

    for name, ids in [("Tagged", tagged), ("Untagged", untagged)]:
        if not ids:
            continue
        group_n, agree, declined = group_stats(ids, labels, predictions)
        print(f"{name:>9}: agreement {agree}/{group_n} ({agree/group_n:.0%}), "
              f"model declined where you graded {declined}/{group_n}")


if __name__ == "__main__":
    main()
