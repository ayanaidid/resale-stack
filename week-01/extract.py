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

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are grading the condition of secondhand resale listings against a specific rubric. Use only the rubric below — not general knowledge or intuitions about how resale platforms grade condition.

TIER DEFINITIONS

PRISTINE
Definition: As-new condition with complete original packaging. No visible wear, and, depending on category, includes the full set of tags/box/dust bag.
Criteria: No scratches, scuffs, or visible wear anywhere on the item. All functional elements work seamlessly (zippers, clasps, buckles, closures). Handbags/shoes/accessories: tags attached, box included, dust bag included. Jewelry: no wear, tags not required. Clothing: tags attached.
Boundary: An item that is visually and functionally flawless but missing one piece of original packaging does NOT qualify as Pristine, even though it looks brand new — it drops to Excellent.

EXCELLENT
Definition: Visually and functionally like-new, but missing some or all original packaging. No meaningful wear.
Criteria: No visible wear, scuffs, or damage — same visual bar as Pristine. All functional elements work seamlessly. Handbags/shoes/accessories: missing tags and/or box and/or dust bag. Jewelry: only extremely superficial wear allowed (e.g. faint surface scratches). Clothing: unworn but tags not attached.
Boundary: An item with the first trace of actual use — one small faint scuff, or a barely visible fold line from being carried once or twice. If the wear is minor and isolated (one mark, not a pattern of use), it is still Excellent. Once there are multiple small marks, or wear spread across the item rather than a single spot, it tips to Very Good.

VERY GOOD
Definition: Clear signs of having been used, but wear is light and doesn't compromise the item's overall look or function.
Criteria: Handbags/accessories: lightly worn corners, light scratches, some interior wear. Shoes: light sole wear, faint creasing at flex points. Jewelry: minor scratches, small nicks, small dents. Clothing: light markings or fading. All function still works normally — no repairs needed, nothing broken.
Boundary: An item stays Very Good as long as it has no more than four cosmetic marks, each subtle enough not to be immediately noticeable, AND no structural or functional issue of any kind. The moment either threshold is crossed — a fifth mark, or even one flaw that is structural or functional rather than cosmetic — it moves to Good.

GOOD
Definition: Clearly used, well-loved condition. Functionality intact throughout, but this reads unmistakably as a second-hand item.
Criteria: Wear present in both severity and quantity. Interior: visible staining, marks of use, lining wear. Hardware: visible wear, tarnish, discoloration. Fabric: pilling, noticeable discoloration. Still fully functional — nothing broken, no repairs needed.
Boundary: An item crosses from Very Good into Good by EITHER (1) a single flaw that affects structure rather than just surface — one visibly worn or misshapen corner — regardless of how few other marks are present, or (2) five or more cosmetic marks, even if each is individually subtle. Path (1) dominates: one structural flaw outweighs several purely cosmetic ones.

FAIR
Definition: Visible structural damage and/or repairs, but the item is still fully usable. The last tier before an item is no longer sellable in normal condition.
Criteria: Structural damage present (not just cosmetic), but not severe enough to make the item unusable. Visible repairs allowed (re-stitching, hardware replacement) but not major reconstructive work like patches or panel replacement. Multiple serious flaws may be present. Still functional for a buyer's practical use.
Boundary: The line from Good to Fair is crossed when wear starts to affect function, not just structure or appearance — a zipper noticeably harder to close, a strap attachment under visible stress, hardware that no longer sits flush. The item stays Fair as long as it can still fully perform its original purpose: functional impairment without functional failure.

GRADING INSTRUCTIONS

Grade based only on what the listing text describes. Do not infer condition from price, brand, or item type. If the listing does not contain enough information about wear to place it in a tier, use "Insufficient information" rather than guessing.

If the listing states a condition label from its platform (e.g. "Very good", "Pre-owned - Good", "New with tags"), do not simply repeat it. Grade the described wear against the rubric above and assign the tier that fits, even if it differs from the platform's label.
"""

RESALE_LISTING_TOOL = {
    "name": "listing_evaluator",
    "description": "Decode the components of a resale listing from a resale website to understand its various properties.",
    "input_schema": {
         "type": "object",
         "properties": {
            "brand": {
                "type": "string",
                "description": "name brand of the item in question. Use 'Not stated' if the listing does not name one."
            },
            "model": {
                "type": "string",
                "description": "the model of the item itself per brand designation. Use 'Not stated' if the listing does not name one."
            },
            "subcategory": {
                "type": "string",
                "description": "The specific item type, more precise than a broad category. Examples: shoulder bag, crossbody, tote, ankle boot, loafer, midi dress, cocktail ring, tennis bracelet. Use the most specific term the listing supports."
            },
            "material": {
                "type": "string",
                "description": "fabric and raw materials the item is composed of. Use 'Not stated' if the listing does not name one."
            },
            "disclosed_flaws": {
                "type": "array",
                "items": {"type": "string"},
                "description": "every flaw or issue listed in the items raw description or raw title, including any itemized condition or flaw list. empty list if none are named."
            },
            "condition_tier": {
                "type": "string",
                "enum": ["Pristine", "Excellent", "Very Good", "Good", "Fair", "Insufficient information"],
                "description": "assign the tier by grading the described wear against the rubric in the system prompt, not by repeating any condition label that appears in the listing."
            },
            "seller_speak_translation": {
                "type": "string",
                "description": "Identify any euphemistic or hedging language the listing uses about condition (e.g. 'gently used', 'some patina', 'loved', 'priced accordingly', 'honest wear'), and state plainly what each phrase implies about actual wear. If the listing describes condition in direct, literal terms with no euphemism, say 'No euphemistic language'." 
            },
            "confidence": {
                "type": "number",
                "description": "how confident are you in this extraction, 0 to 1."
            }
         },
    "required": ["brand", "model", "subcategory", "material", "disclosed_flaws", "condition_tier", "seller_speak_translation", "confidence"]
    }    
}


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
    user_message = f"Title: {row['raw_title']}\n\nDescription: {row['raw_description']}"
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        tools=[RESALE_LISTING_TOOL],
        tool_choice={"type": "tool", "name": "listing_evaluator"},
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    extracted = None
    for block in message.content:
        if block.type == "tool_use":
            extracted = block.input
            break

    if extracted is None:
        raise ValueError("No tool_use block in response")

    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    cost_usd = (input_tokens * 2 + output_tokens * 10) / 1_000_000

    return {
        **extracted,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
    }


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
