"""
normalize.py: This Python script standardizes raw text inputs by stripping accents, normalizing case, and cleaning punctuation to allow for consistent and predictable string comparisons. It provides targeted normalization pipelines for data fields like brands, subcategories, and condition tiers, returning boolean validation flags alongside the cleaned text to immediately capture structural schema violations

What it does: converts label strings and model outputs to a common baseline form so they can be accurately compared
Input: a string (or anything, including None)
Output: for brand and subcategory, a cleaned string; for tier, a tuple of the cleaned string and whether it's a valid rubric tier
On failure: non-strings and empty values return an empty string rather than raising, and an unrecognized tier comes back with is_valid = False rather than being silently corrected.
"""

import re
import unicodedata

# 1. Brand alias dictionary for mapping cleaned variations to a standard name
BRAND_ALIASES = {
    "ysl": "saint laurent",
    "y s l": "saint laurent",
    "tiffany co": "tiffany and co",  # Handles the & vs 'and' gap
    "not stated": "unbranded",       # Extractor's absent-brand value → label convention
}

def clean_text(s) -> str:
    # Guard clause: handle non-strings, None, or falsy inputs safely
    if not s or not isinstance(s, str):
        return ""
        
    # Step 1: Lowercase
    s = s.lower()
    
    # Step 2: Strip accents (NFKD decomposition + dropping combining marks)
    s = unicodedata.normalize('NFKD', s)
    s = "".join(c for c in s if unicodedata.category(c) != 'Mn')
    
    # Step 3: Remove punctuation — periods, ampersands, hyphens, apostrophes (NO spaces!)
    target_punctuation = ".&-'"
    punct_table = str.maketrans("", "", target_punctuation)
    s = s.translate(punct_table)
    
    # Step 4: Collapse multiple spaces into one, strip leading/trailing
    s = re.sub(r'\s+', ' ', s).strip()
    
    return s

def normalize_brand(s) -> str:
    """Cleans the text first, then checks the alias dictionary."""
    cleaned = clean_text(s)
    return BRAND_ALIASES.get(cleaned, cleaned)

SUBCATEGORY_ALIASES = {}  # populated after the first model run

def normalize_subcategory(s) -> str:
    """Cleans and applies subcategory aliases, which are populated from mismatches after the first run."""
    cleaned = clean_text(s)
    return SUBCATEGORY_ALIASES.get(cleaned, cleaned)

VALID_TIERS = {"pristine", "excellent", "very good", "good", "fair",
               "insufficient information"}

def normalize_tier(s):
    """Returns (cleaned_tier, is_valid). is_valid is False when a model
    emits a tier outside the rubric — a schema violation, not a scoring miss."""
    cleaned = clean_text(s)
    return cleaned, cleaned in VALID_TIERS

# --- Brand-focused Test Block ---
if __name__ == "__main__":
    test_cases = [
        # Accent check
        ("Hermès", "hermes", "Accent removal failed"),
        
        # Alias checks
        ("Y.S.L.", "saint laurent", "Y.S.L. punctuation alias failed"),
        ("YSL", "saint laurent", "YSL direct alias failed"),
        
        # Space preservation check (The bug fix verification)
        ("Saint Laurent", "saint laurent", "Spaces were incorrectly deleted"),
        
        # The '&' vs 'and' scenario (Resolved via the new alias)
        ("Tiffany & Co.", "tiffany and co", "Tiffany & Co. normalization failed"),
        
        # Expected Failure / Design Boundary Check
        ("Cross-Body Bag", "crossbody bag", "Hyphen behavior changed unexpectedly"),
        
        # Safety/Guard check
        (None, "", "Falsy/None guard failed"),
        (123.45, "", "Float guard failed"),

        # Extractor absent-brand value maps to label convention
        ("Not stated", "unbranded", "Not stated alias failed"),
        ("Unbranded", "unbranded", "Unbranded passthrough failed"),
    ]
    
    print("Running brand normalization tests...\n")
    for input_val, expected, error_msg in test_cases:
        result = normalize_brand(input_val)
        status = "PASS" if result == expected else "FAIL"
        print(f"[{status}] Input: {repr(input_val)} -> Got: {repr(result)} (Expected: {repr(expected)})")

    print("\nTier tests:")
    for inp, expected in [("Very Good", ("very good", True)),
                          ("Mint", ("mint", False)),
                          (None, ("", False))]:
        r = normalize_tier(inp)
        print(("PASS" if r == expected else "FAIL"), repr(inp), "->", r)
