# Week 1 — The Listing Decoder

A command-line tool that reads a secondhand resale listing and returns a structured record: brand, model, subcategory, material, disclosed flaws, a condition tier graded against a rubric I wrote, a plain-language translation of any euphemistic seller language, and a self-reported confidence score.

Run over 30 hand-collected listings from 7 platforms. Total cost: **$0.27**.

The interesting part isn't that it works. It's the 30 listings where I graded every field myself and counted the disagreements.

---

## What's in here

| Path | What it is |
|---|---|
| `rubric.md` | Five condition tiers with observable criteria and boundary cases. Written before any code. Includes 20 pre-registered predictions about what seller euphemisms actually mean. |
| `extract.py` | The tool. Reads the CSV, calls the API with a constrained output schema, writes JSONL. |
| `data/listings.csv` | 61 listings collected by hand. 30 tagged `in_run_30` for this run; 31 held back for Week 2. |
| `data/extractions.jsonl` | What the model returned for each of the 30. |
| `analysis/grading_sheet.csv` | Every listing, its extraction, and my own grade on each field. This is the actual work. |
| `experiments/repeatability.py` | Three listings, five identical runs each. |
| `NOTES.md` | Everything I didn't recognize, and what it turned out to mean. ~30 entries. |

## How to run it

```bash
python3 -m venv venv && source venv/bin/activate
pip install anthropic python-dotenv
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
python3 extract.py
```

Resumable — rerunning skips any `listing_id` already in `extractions.jsonl`.

---

## The data

Collected by hand, by copy-paste. No scraping: scripted collection violates these platforms' terms of service, and doing it manually is where most of what follows came from.

**Platforms:** The RealReal (6), Vestiaire Collective (5), Poshmark (5), eBay (5), Vinted (5), ThredUp (2), Fashionphile (2)

**Categories:** handbags (9), clothing (8), shoes (8), jewelry (5)

Deliberately split between consignment platforms, where staff write standardized copy, and peer-to-peer marketplaces, where sellers write their own. That distinction turned out to matter more than the platform names.

---

## Where it was wrong

I graded all 30 listings myself against my own rubric, recording my tier before looking at the model's. Counts below.

### Condition tier: 8 of 20 (40%)

Denominator is the 20 listings where the model and I both assigned a real tier. The other 10 are cases where one of us declined — counted separately below, because mixing them inflates or deflates the number depending on which way you lean.

**The model grades higher than I do.** Of the 12 disagreements, it graded the item *up* a tier on 9 and *down* on 3. Eleven of twelve disagreements are a single tier apart; only one is two tiers. It isn't confused about condition — it's consistently one notch more generous.

### The same skew appears in the platforms

I also compared my grade to each platform's own condition label:

| | Agree with me | Disagree | Label doesn't map |
|---|---|---|---|
| Platform labels | 17 | 10 | 3 |

On the 10 disagreements, the platform grades **higher** than me on 9 of 10.

So: two independent sources — a frontier model and seven resale platforms — both skew generous against the same rubric, at almost the same rate. The model didn't invent leniency about condition. It reproduced a convention that already exists in how the industry describes wear.

Also worth noting: I agree with platform labels (17/27, 63%) considerably more often than with the model (8/20, 40%), despite my rubric being stricter than any platform's published standard.

### Three of thirty listings use vocabulary that doesn't map at all

Vinted's "Satisfactory." Poshmark's free-text "Great Condition." One listing with no condition field whatsoever. My rubric's tier names are drawn from The RealReal's public standard, and a tenth of listings use condition language that doesn't sit on that ladder in any direction.

### The Pristine rule didn't survive

My rubric makes Pristine category-conditional: handbags, shoes, and accessories need tags *and* box *and* dust bag; clothing needs tags; jewelry needs neither. The model applied "has tags → Pristine" uniformly across every category.

Of five Pristine calls: both clothing and jewelry correct (those categories don't require packaging), both shoes and handbag wrong. A category-conditional rule stated explicitly in the system prompt did not transfer.

### Field-level errors were rare

Two across 30 listings, both on material:
- **L044** — invented "Canvas," which appears nowhere in the listing
- **L032** — described the canvas as the exterior when the listing specifies it as lining

Brand, model, and subcategory were correct on every listing, and perfectly stable across repeated runs. **Stated facts extract reliably. Judgments don't.**

---

## Two design decisions that collided

This is the finding I'd have missed without grading by hand.

The model returned "Insufficient information" on 10 of 30 listings. I assumed it was being over-cautious. On grading, the 10 split into two completely different failures:

**Five were correct.** The RealReal and Vinted put condition in a structured field and leave `raw_description` as attribute soup — Brand, Size, Color dumps with no prose about wear. There is genuinely nothing in the text to grade. My prompt deliberately excludes the platform's `stated_condition` field, so the model saw no condition information at all. Declining was right.

**Five were caused by my own prompt.** On these, the description *does* state a condition — "in good condition," "Very Good" — but describes no actual wear. My system prompt says:

> If the listing states a condition label from its platform, do not simply repeat it. Grade the described wear against the rubric above.

The model obeyed. It refused to transcribe the label, found no described wear to grade, and took the escape hatch I'd given it. Both instructions were reasonable in isolation. Together they produce a model that declines on any listing where condition is *asserted* but not *described* — which is a large fraction of real listings.

I'm not fixing this yet. See below.

---

## Repeatability

**The experiment I planned doesn't exist anymore.** I intended to run each listing at temperature 0 and temperature 1 to measure sampling variance. Claude Sonnet 5 rejects any non-default `temperature`, `top_p`, or `top_k` with a 400 error — the parameter has been removed on this model. Most writing about LLM nondeterminism assumes temperature is a knob you have. On a current frontier model, it isn't.

That made the experiment cleaner. I ran three listings five times each at default settings, so there is no sampling parameter to attribute variance to.

| Listing | Description | Tier across 6 runs |
|---|---|---|
| L007 | Longest, 4–5 disclosed flaws, heavy hedging | **Excellent ×6** |
| L001 | Clean spec prose, zero flaws | Pristine ×4, Excellent ×2 |
| L022 | "Cream converse dupes." Almost nothing. | Pristine ×5, Excellent ×1 |

**Instability tracks absence of evidence, not complexity.** The longest and messiest listing was perfectly stable. The two with nothing to grade both flipped. My Pristine/Excellent boundary turns on packaging, which listings almost never mention — so the model isn't weighing evidence, it's deciding what silence means, and that decision isn't stable across identical calls.

Brand and subcategory were identical on all 18 runs.

### One malformed response

One of six runs on L007 returned a tool call that violated its own schema: the `required` field `confidence` was absent, and its value had leaked into the adjacent string field as literal text — `</seller_speak_translation>\n<parameter name="confidence">0.7`. The model emitted its own tool-call syntax as content. The SDK did not reject it, and my code wrote it through unvalidated.

Constrained decoding removes format errors *almost* always. Not always. About 1 in 18 runs here.

---

## Cost

| | |
|---|---|
| 30 listings | **$0.2725** |
| Per listing | ~$0.0091 |
| Typical call | ~2,900 input tokens, ~260 output |

**Input dominates, which inverts the usual advice.** Output tokens cost 5× input on this model, so the standard lever is "make the model say less." Here input is roughly 78% of cost, because the system prompt carries my full rubric (~1,000 tokens) on every call and my listings average ~2,000 tokens — inflated by a deliberate choice to store descriptions verbatim, including platform boilerplate and composition percentages that tell you nothing about condition.

The real levers are caching the system prompt, which is byte-identical across all 30 calls, and trimming boilerplate at prompt time rather than at collection time.

**Do not extrapolate this number.** Multiplying $0.0091 by a million listings ignores batch pricing (50% off) and prompt caching (input at 10% on cache hits), both of which apply directly to this workload. Week 3 runs 5,000+ listings through the batch API and produces a number worth quoting.

---

## What I'm deliberately not doing

Every finding above suggests an obvious fix — tighten the Pristine language, rework the instruction that caused the declining, add schema validation.

I'm not making any of them this week. I have a 40% agreement number measured against 30 labels I made myself, and no instrument that would tell me whether a change improved things or moved the problem somewhere I wasn't looking. Changing the prompt now means my published results describe a system that no longer exists, tuned against a sample of 30.

Week 2 is 150 hand-labeled listings and an eval harness. Then changes can be measured instead of guessed at.

---

## Limitations

**I graded them.** One annotator, no second opinion, my own rubric. On reviewing the disagreements I changed my mind on 8 of 18 — which is a useful thing to know about the reliability of a golden set built by one person, and an argument for how carefully Week 2 needs to be done.

**Five of my labels are guesses.** On the listings where the text genuinely doesn't support a tier, I assigned one anyway by defaulting toward the middle. That is exactly the behavior I criticized the model for. Those rows are flagged `gradeable_from_text = N` in the grading sheet and excluded from the 40%.

**n=30, and thinner than that per cut.** ThredUp and Fashionphile contribute 2 listings each. Platform-level rates in here are directional, not measured.

**The euphemism hypothesis is untested, not confirmed.** I predicted the model would handle direct descriptors ("gently used") well and framing phrases ("priced accordingly," "odor-free") poorly, because the second group requires inferring why a seller chose those words. Result: 18 agree, 0 disagree, 12 not applicable. No listing in the 30 contained the framing language the hypothesis is about. It remains a prediction.

**The held-back 31 listings have never been through the model**, so Week 2's golden set can be labeled without anchoring on its output.

---

## Week 2

150 hand-labeled listings. An eval harness that runs this tool against them and reports accuracy per field, a confusion matrix for condition tier, and every disagreement. Then the same harness against three different models.

The specific questions this week generated:

1. Does the generosity skew hold at 150? Is it uniform across categories, or concentrated at particular tier boundaries?
2. Does separating "grade the wear" from "record the stated label" into two fields fix the declining problem without reintroducing transcription?
3. How often does the malformed-tool-call failure actually occur across a larger run?
4. Does my four-mark ceiling for Very Good survive contact with 150 listings, or is condition judgment more holistic than any count?
