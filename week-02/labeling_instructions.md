## 1. Scope and procedure

**What to read.** Label from the `raw_title` and `raw_description` fields only.
Every entry produces four labels: `label_brand`, `label_subcategory`,
`label_condition_tier`, and `label_auth_flag`. Condition tiers are defined in
`week-01/rubric.md`.

Excluded columns — do not read these while labeling: `listed_price`,
`stated_condition`, `source_platform`, `image_urls`. Two reasons. Reading
`stated_condition` anchors your judgment to the platform's. And the model
received only title and description, so labeling with columns it never saw makes
a disagreement unreadable: you can't separate "the model was wrong" from "the
model didn't have that information." Hide the excluded columns in the sheet
rather than relying on willpower.

**Order.** Shuffle the rows before labeling and keep them shuffled. Grading five
listings from the same brand in a row calibrates you to that brand instead of to
the rubric.

**Session length.** No more than 45 minutes per session. Log the stop point in
`label_notes`. The limit exists because of fatigue drift — judgment shifts late
in a session and you won't notice it happening, so the stop points let you check
afterward whether labels from minute 40 skew differently from labels at minute 5.

**Every row.** `boundary_case`, `label_confidence`, and `label_notes` are filled
on every listing, not only difficult ones. `label_confidence` is your confidence
in your own label, recorded before you see any model output.

`boundary_case` and `label_confidence` measure different things. A listing can
be a boundary case you're highly confident about — the seam is defined in the
rubric and this one clearly falls on the Good side of it. A listing can also be
low-confidence without being a boundary case at all — a vague description where
nothing sits on a seam and you're simply unsure what you're looking at.

**When a listing can't be resolved.** Enter `Insufficient information` in
`label_condition_tier` and record why in `label_notes`. Fill `boundary_case` and
`label_confidence` as normal.

**Contradiction rule.** A contradiction is a listing whose description contains
a flaw that the title's condition claim would exclude — for example, a title
reading "excellent" over a description that states damage. When this happens,
discard the title's condition claim entirely and grade the item from the
description's evidence against the rubric. Mark `boundary_case = Y` and describe
both sides of the contradiction in `label_notes`.

A contradiction means too much information pointing in two directions, not too
little, so it never resolves to `Insufficient information`. If you find yourself
wanting to decline on a contradictory listing, log it — that's a signal the rule
isn't working.

**Field Key.**  
    - listing_id = The ID from listings.csv (L001). The join key. Never invent 
        one here.
    - label_pass = fresh or blind-relabel. Everything this week is fresh until
        Thursday's re-label of the Week 1 thirty.
    - labeled_at = ISO date you made the label (2026-09-16). Not the date the
        listing was captured.
    - anchored	= Y or N; did you see model output for this listing before
        labeling it? N for every Week 2 row. Y only exists to mark the Week 1 grades if you ever import them.
    - label_brand = The brand, as you'd resolve it. Your call on house vs  
        sub-brand, per section 2.
    - label_subcategory	= The most specific term the listing supports.
        Lowercase, singular, no hyphens (crossbody, not Cross-Body Bags). Starting vocabulary: shoulder bag, crossbody, tote, ankle boot, loafer, midi dress, cocktail ring, tennis bracelet — add new terms as you hit them and append them to the running list in NOTES.md. The extractor's subcategory field is unconstrained free text, so this is scored after normalization rather than by exact match.
    - label_condition_tier = One of your five tiers, or Insufficient
        information. Never blank.
    - label_confidence = low / medium / high. Your confidence in your own label,
        recorded before you see any model output.
    - boundary_case = Y or N; Did this sit on the line between two tiers.
    - label_notes = The specific phrase you graded on — your evidence. For    
        Insufficient information, why you couldn't grade it.

-----

## 2. Brand and subcategory

These are the control fields. They should be near-mechanical, and high agreement
here is what makes the condition tier numbers readable by contrast.

### Brand — how to write it (normalization)

Write the brand in canonical form: the full house name, lowercase-insensitive,
no accents or diacritics. `YSL`, `Yves Saint Laurent`, and `Saint Laurent` are
all one house and all get written `Saint Laurent`. `Céline` is written `Celine`.

Correct obvious typos when the brand is clearly named — `Channel` becomes
`Chanel`. Do not infer a brand from a model name: a listing that says `Birkin`
with no house named anywhere is not labeled `Hermes`, because inferring it is a
judgment call the model may reasonably make differently, and the point of this
field is to compare like with like.

Brand is compared after normalization, not by exact string match. The scorer
lowercases both sides, strips accents and punctuation, collapses whitespace,
and applies a house alias list (`YSL` → `Saint Laurent`, and others added as
they come up). The running alias list lives in NOTES.md.

Exception: nouns that are inherently plural stay plural — earrings, pants, ski pants. The singular rule applies to terms that have a natural singular form (sneaker, not sneakers).

### Brand — which brand it is (identity)

**Sub-brands are labeled as themselves, not folded into the parent house.** A
diffusion or secondary line is a distinct brand for labeling purposes: `Marc by
Marc Jacobs` stays `Marc by Marc Jacobs` and does not become `Marc Jacobs`.
This is different from a naming variant of a single house, which normalizes per
the rule above. The test: if the parent sells it as a separate line with its own
name, it is a sub-brand; if it is the same house written a different way,
normalize it.

**Collaborations are labeled distinctly**, not as either parent alone. Format:
`Brand A x Brand B`, lowercase `x`, with the house that produced the item first.

**Two brands named in one description:** label the brand of the item itself, not
a brand mentioned for comparison or context. A Chanel bag described as
"similar to Dior" is `Chanel`.

**Brand absent:** `Insufficient information` — the same value used in
`label_condition_tier`, so the harness needs one rule and not two.

### Subcategory

Anchor: The RealReal's published handbag taxonomy, captured 2026-09-16.
Handbag subcategories are one of: `shoulder bag`, `crossbody`, `tote`,
`top handle`, `bucket bag`, `clutch`, `backpack`, `waist bag`, `luggage`.
Non-handbag categories (footwear, clothing, jewelry) have no anchored taxonomy
yet — use the most specific term the listing supports and append new terms to
the running list in NOTES.md.

**Default to the title.** If the listing names an item type, take the title's
term and normalize it to the taxonomy above. Only choose between terms when the
listing forces you to.

**Crossbody vs shoulder bag.** Strap length and intended wear: a crossbody has a
longer strap worn diagonally across the body, a shoulder bag a shorter strap
worn on one shoulder. Classic flaps and hobos are shoulder bags.

**Soft seam, and expect disagreement here.** Convertible bags with adjustable or
removable straps are genuinely both, and listings describe them inconsistently.
When a listing supports both terms and the title doesn't settle it, take the
term that appears first in the description, mark `boundary_case = Y`, and note
the ambiguity. This seam is expected to produce model disagreement, and those
disagreements should be read as taxonomy ambiguity rather than model error.

**Boundary case:** Not yet identified. Don't have a canonical disputed case from experience. Boundary cases here will be identified empirically from the first 50 labels and added.

-----

### 3. Condition tier

Tier definitions live in `week-01/rubric.md` and are not restated here. This
section is the labeling procedure that sits on top of them.

**Evidence rule.** Grade what the description states, not what it implies.
Silence is not evidence of good condition — a description that says nothing
about corners is not a description of intact corners. This is the rule most
likely to slip late in a session hence why there are session limits.

**Procedure, in order.**
1. Count the distinct cosmetic marks described
2. Check for structural language (torn lining, broken hardware, compromised handles)
3. If structural, apply the override regardless of the mark count, otherwise apply the four-mark ceiling
4. Assign the tier.

**Pristine requires packaging, by category.** Handbags/shoes/accessories: tags attached, box included, dust bag included. Jewelry: no wear, tags not required. Clothing: tags attached. *Packaging present, condition silent.* A listing that itemizes full packaging (box, dust bag, tags, accessories) but describes no wear and makes no condition claim does not reach Pristine. Packaging is a necessary condition for Pristine, not a sufficient one — the evidence rule still applies, and silence about the item's state is not evidence that the state is perfect. Grade it "excellent" with `label_confidence = low`, and note that packaging was present but uncorroborated.

Known failure point, pre-registered: this rule did not transfer to the model in
Week 1, and I expect the models to miss it again. Disagreements traceable to
packaging should be counted separately from disagreements about the item itself.

**Insufficient information.** Decline only when the title and description contain no condition language at all — no claim, no wear descriptors, nothing about the item's state. A sparse listing is not automatically a decline; a silent one is.

Do not use `Insufficient information` for contradictions — see the contradiction
rule in section 1. Too much information pointing two ways is not too little.

**Bare claims.** A condition claim with no supporting detail ("excellent condition," "great shape") is gradeable. Take the claim, cap it below Pristine, mark label_confidence = low, and write "claim without evidence" in label_notes. This is a deliberate choice: the claim is the seller's own words in the free text, which is what the model received. It is not a contradiction of the evidence rule — silence is still not evidence of good condition, but an explicit claim is not silence. Platform condition boilerplate is common and splits two ways. 

Boilerplate asserting specific facts about the item's state ("brand new and has never been worn," "still has the original packaging") counts as evidence. Boilerplate asserting a verdict ("Pre-owned - Good," "gently used," "Very good condition") is a bare claim, however many words the platform wraps around it. Tagging: when this rule fires, `label_notes` begins with the literal phrase `claim without evidence`, followed by your reasoning. The phrase is what makes these rows findable at analysis time — free-text reasoning alone can't be
grouped. Expect a meaningful share of the set to land here, and expect agreement
with the models to be higher on these rows than elsewhere, since on them my
label is largely the seller's verdict in my tier names.

A phrase that summarizes wear without describing it is a verdict, not an observation. "Gently used," "lightly used," and "slightly worn" tell you the seller's opinion of the wear rather than what the wear is, and are treated as bare claims. "A few blemishes," "light creasing on the sleeves," and "loss of plating throughout" describe something observable and count as evidence.

**Pre-registered.** I recorded 0 declines in Week 1, but my own README identified 5 of the model's 10 declines as correct, meaning my labels and my judgment had already diverged before I noticed. The bar in this section is the fix. Week 2 measures whether my own bar is applied consistently (Thursday's blind re-label), and what the model's threshold costs in coverage.

**Calibration note.** In Week 1, three independent sources graded higher than I did: the model (9 of 12 disagreements), the platform labels (9 of 10), and The RealReal's own expert review. These labels reflect my rubric, built from three years defining and socializing condition tiers at a resale platform.

The gap is directional, not random — the disagreement runs one way, with other graders assigning a tier above mine. Anyone reading a model's accuracy against this set should read it as agreement with a stricter-than-market grader, not as absolute accuracy. Model "errors" in the generous direction may be the model reproducing the industry's standard rather than failing at the task, and that distinction is one of the things Week 2 is meant to surface.

My position on why the stricter standard is the right ground truth: market grades are set by parties with a commercial interest in higher tiers, since a higher grade sells faster and at a better price while the cost of over-grading — returns, disputes, condition complaints — lands later and often on someone else. Convergence among commercially interested graders is evidence of shared incentive, not shared accuracy. The test that would settle it is buyer-side: if return rates and condition complaints track the market's tiers better than mine, my rubric is the outlier. I can't run that test with this data, and I'd change my position if someone could.

Amendments to week-01/rubric.md are dated and logged, never made mid-pass, and any listing labeled under a superseded definition is re-labeled.

-----

### 4. Authentication flag -- removed

**Removal Reason.** Item authentication is often not disclosed in item description and if it is, actual authentication materials (serial number, paperwork, etc.) are attached in another part of the overall listing and will not be extracted from the title or description. Authenticity isn't assessable from text at all — it's a physical process — and you have no review outcomes to check labels against, so any label would be your guess treated as ground truth.Similarly, adjusting the fields to assess listing quality was also ruled out given the inclusion `Insufficient information` label and a `confidence` score measured (extracted) to assess whether the outputs from the listing are adequate already. 

**What it would take to flag.** The ground truth that exists is review outcomes — whether a listing actually got pulled and what the reviewer concluded. That isn't retrievable from public listing data at any N. It may be plausible to get at 5,000 listings but it would be based on a weaker proxy: listings that were later removed, relisted, or price-corrected. That's a Week 3 question at 5,000 listings, not a Week 2 one at 150.