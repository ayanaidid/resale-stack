# Week 2 — Can I trust the model's condition grades?

**In one sentence:** I hand-graded 150 secondhand luxury listings, had three Claude models grade the same listings, and measured how often they matched me. Most of the early mismatches turned out to be my fault, not the models': my instructions to the model contradicted my own grading rules, and some of my grades were simply wrong.

---

## 1. What this week was for

In Week 1 I built a small tool that reads a resale listing (a Chanel bag on eBay, a pair of shoes on Poshmark) and pulls out three things: **brand**, **what kind of item it is**, and **what condition it's in** (Pristine, Excellent, Very Good, Good, Fair, or "Insufficient information").

Week 1 showed the tool *worked*. Week 2 asks a harder question: **does it get the right answer, and how would I know?**

You can't answer that by eyeballing a few results. You need an **answer key**: a set of listings where you already know the correct answer, written down before you see what the model says. In AI work this answer key is called a **golden set**, and checking the model against it is called an **eval** (short for evaluation). This week was about building both.

## 2. The answer key (golden set)

**150 listings**, each graded by hand by me.

| | |
|---|---|
| **Where they came from** | 60 written by platform staff (The RealReal 32, ThredUp 16, Fashionphile 12) and 90 written by individual sellers (Vestiaire 24, Poshmark 24, eBay 24, Vinted 18) |
| **What they are** | 50 handbags, 35 clothing, 35 shoes, 30 jewelry |
| **Fresh vs. re-graded** | 120 new; 30 were the Week 1 listings, re-graded "blind" (without looking at my old answers) |

For each listing I recorded brand, item type, condition, **how confident I was**, and whether it was a **borderline case**. Confidence and borderline flags matter because a wrong answer on a genuinely ambiguous listing means something different from a wrong answer on an obvious one.

Before grading, I wrote down **labeling instructions** (`labeling_instructions.md`) so I'd grade the same way on listing 140 as on listing 1. A few rules worth knowing:

- **Item type** follows The RealReal's categories (it's the market I know).
- **If the listing names no brand**, the brand is "Unbranded."
- **I dropped a planned "authentication" field.** Whether a listing *says* it's authentic doesn't tell you whether it *is*, and grading it would have measured nothing useful.
- **A bare claim ("excellent condition!") with no description still gets graded.** This rule turned out to be the most important thing I wrote all week (see section 5).

## 3. "Agreement," not "accuracy"

Every number below is how often the model **matched me**. That isn't the same as how often it was **right**:

- There is **one grader** (me). Nobody checked my work, so my mistakes are baked into the answer key.
- My rubric runs **stricter than the market**. Sellers routinely call things "Excellent" that I'd grade "Very Good."

So "70% agreement" means "matched my judgment 70% of the time." That's a useful number, but it's honest to call it agreement.

## 4. First results (prompt v1)

All three models got the **same instructions** (prompt "v1") and graded all 150 listings.

| Model | Brand | Item type | Condition |
|---|---|---|---|
| Sonnet 5 | 91% | 34% | **49%** |
| Haiku 4.5 | 91% | 32% | **59%** |
| Opus 5 | 91% | 20% | **51%** |

What this told me:

- **Brand is solved.** Above 90% every time.
- **Item type is noise.** I let the model describe item type in its own words ("crossbody," "shoulder bag," "satchel") instead of picking from a fixed list, so it rarely matched my exact word. That's a design flaw in my setup, not a model weakness. Fixing it means giving the model a fixed list to choose from (Week 3).
- **Condition is where the real problem was.** About half right. And the cheapest model (Haiku) beat the most expensive one (Opus). That was a clue that something besides "model intelligence" was going on.

## 5. The main discovery: my instructions contradicted my answer key

I built a **confusion matrix**: a grid showing, for every listing, what I said vs. what the model said. It shows *how* the model is wrong, not just *how often*.

The biggest single pattern: **the model said "Insufficient information" on listings where I had given a grade.** That accounted for 29–38 listings per model, which was 38–51% of all condition mismatches. It wasn't random noise. It was systematic.

Looking at those listings, most were **bare claims**: a seller writes "excellent condition" and nothing else. My labeling rule said *grade these* (take the seller's word, but never above Excellent). But the prompt I'd given the model said *decline these* when there's no supporting evidence. **The model was following its instructions. The instructions were wrong.** In AI work this is called a **spec mismatch**: the rules you grade by aren't the rules you gave the model.

The contradiction lived in **two places**: the main instructions *and* the short description attached to the condition field. Fixing only one wouldn't have worked.

I'd tagged 37 listings (25% of the set) as "claim without evidence." On those, v1 matched me only **16–22%** of the time.

I also had a theory that Haiku beat the others because it was better at reading bare claims. **That was wrong.** On the tagged listings, Haiku and Sonnet tied (8 of 37). Haiku's lead came from the other listings.

## 6. The fix, tested properly (prompt v2)

I wrote prompt **v2**: same grading rubric, but with the bare-claims rule aligned to my labeling instructions.

To make sure I wasn't fooling myself, **I wrote down my predictions before running it** (in `NOTES.md`). This is called **pre-registering**. It stops you from looking at results and then deciding that's what you expected. I predicted:

- Agreement on the 37 tagged listings would rise to about 60%. **Result: 67% combined.** ✅
- Opus would gain the most. **Result: Opus went from 6 to 28 of 37.** ✅

I also limited myself to **one attempt**. If I'd tweaked the prompt over and over until the score looked good, I'd have tuned it to these 150 listings and learned nothing about new ones.

**Regression test.** A fix in one place can break things elsewhere, so I also checked the listings that *weren't* bare claims. They improved too: from 58→71% (Sonnet), 71→78% (Haiku), 62→75% (Opus). The old "decline" rule had been suppressing grades across the board.

| Condition agreement | v1 | v2 | Change |
|---|---|---|---|
| Sonnet 5 | 49% | **70%** | +21 pts |
| Haiku 4.5 | 59% | **73%** | +14 pts |
| Opus 5 | 51% | **75%** | +24 pts |

**The cost of the fix.** v2 now gives a grade in a few more cases where I said "Insufficient information" (Sonnet's count went from 6 to 9, and 8 of those 9 were graded Excellent). In resale, guessing too high is the more expensive mistake: a buyer gets something worse than promised and returns it. It's small, but it's real, and it's worth watching.

## 7. The 24 listings every model got wrong, and why

After v2, **24 listings were missed by all three models** (scored against my original labels). I went back through each one by hand and gave it one cause:

| Cause | Count | What it means |
|---|---|---|
| **My label was wrong** | 13 | On re-reading, my grade was the mistake |
| **Rubric gap** | 6 | My rules didn't cover the case, so both answers were defensible |
| **Spec mismatch** | 5 | My labeling instructions and the model's prompt said different things |
| Model error | **0** | Not one clean case of a model misreading a clear rule |

**Does it mean anything when all three models agree with each other?** Only a little. Of the 17 listings where all three gave the *same* wrong-by-my-key answer, 10 were my mistakes (about 6 in 10). Of the 7 where they split, 3 were my mistakes (about 4 in 10). Agreement among the models is a mild hint about where to look first, and on 24 listings I can't claim more than that. Every disagreement still needs a human look. *(An earlier version of this README said 13 of 17 and 0 of 7. That was a counting error, now corrected.)*

Here is every listing. "Models" is Sonnet / Haiku / Opus.

### My label was wrong (13)

| Listing | Item | My grade | Models | Why |
|---|---|---|---|---|
| L017 | Soeur leather flats | Excellent | Insufficient ×3 | It only says it comes with a box and dust bag. Packaging says nothing about wear. The models were right. |
| L067 | Hermès Birkin 35 | Excellent | Pristine / Pristine / **Insufficient** | Same problem: a long list of what's in the box, not a word about condition. Only Opus got it right. |
| L037 | Balenciaga City bag | Very Good | Excellent ×3 | Says "Like New" and nothing else. My own rule is to grade a bare claim (never above Excellent). I played it safe and broke my own rule. |
| L127 | Anthropologie earrings | Very Good | Excellent ×3 | Same: a bare "Like New." |
| L123 | DVF leather mules | Insufficient | Excellent ×3 | The title says "Excellent Condition." I read the description, not the title, and missed it. |
| L096 | Tory Burch loafers | Very Good | Good ×3 | The seller said "good" and listed scratches and scuffs. I graded *higher* than the seller did. |
| L061 | Van Cleef Alhambra earrings | Very Good | Excellent ×3 | The only flaw is faint scratches on the metal. Under my rubric, that's Excellent. |
| L108 | Prada cashmere sweater | Excellent | Pristine ×3 | Never worn, tag attached. That's Pristine. I was being cautious. |
| L109 | Toteme cashmere skirt | Excellent | Pristine ×3 | New with tags. Same as above. |
| L083 | Ferragamo Hug bag | Very Good | Good ×3 | Five or more wear marks are listed. My rubric says that's Good. |
| L082 | Hermès Bolide | Very Good | Good / Good / Fair | Five marks listed, which is Good under my rubric. I wanted to change the rule so my answer would count. I didn't (see below). |
| L105 | Louis Vuitton Sistina | Very Good | Good ×3 | One ink stain inside a pocket. Visible staining is Good, however few marks there are. |
| L035 | JW Pei bag | Very Good | Fair / Good / Fair | "Zipper is a little difficult, but works fine." I missed that line. My rubric's own example of Fair is a zipper that's hard to close. |

### Rubric gap (6)

| Listing | Item | My grade | Models | Why, and how it was settled |
|---|---|---|---|---|
| L039 | Louis Vuitton Speedy 25 | Good | Fair ×3 | About 18 listed flaws, including cracked and peeling leather, but nothing broken. My rubric contradicted itself on Good vs. Fair. New rule: 3+ structural flaws = Fair. |
| L048 | Gucci Ophidia bag | Good | Fair ×3 | Seam tear, frayed stitching, corner and edge wear. Same Good-vs-Fair gap, settled by the same rule. |
| L028 | Eugenia Kim flats | Very Good | Excellent ×3 | Says both "New Without Original Box" *and* "Very good condition." No rule for two conflicting statements. New rule: if no wear is described, grade to the lower one. My Very Good stands. |
| L030 | Nike Air Force 1 | Good | Very Good ×3 | Says "Good" in one place and "Very good" in another. Grade to the lower: Good stands. |
| L142 | Michael Kors satchel | Very Good | Excellent ×3 | Labeled "Very good," but the seller writes "only used a handful of times, like new." Under the new rule, Very Good stands. |
| L140 | Leather jacket | Very Good | **Good** / Excellent / Excellent | Platform says "Good," seller says "great shape, no defects." Grade to the lower: changed to Good. Only Sonnet got it right. |

### Spec mismatch (5)

All five have **"w/ Tags" in the title** and nothing about condition in the description. My labeling instructions didn't count tags as evidence. The prompt did, so the models graded them. I decided the prompt had it right (tags still attached means the item hasn't been worn), changed my labels, and wrote the rule down.

| Listing | Item | My grade | Models | Changed to |
|---|---|---|---|---|
| L034 | Strathberry shoulder bag w/ Tags | Insufficient | Excellent ×3 | Excellent |
| L065 | Chloé clutch w/ Tags | Insufficient | Excellent / Pristine / Excellent | Excellent |
| L068 | Fendi ski pants w/ Tags | Insufficient | Pristine ×3 | Pristine |
| L070 | Saint Laurent blazer w/ Tags | Insufficient | Excellent / Pristine / Pristine | Pristine |
| L071 | Brunello Cucinelli pants w/ Tags | Insufficient | Excellent / Pristine / Pristine | Pristine |

### Three stories from the list

**I wasn't reading titles.** In 6 of the 24 (the five "w/ Tags" listings plus L123's "Excellent Condition"), the fact that decided the grade was in the title, and I'd graded from the description. The models read everything they were given. A human skimming 150 listings doesn't. That's a real limit of hand-labeling, and it's why the answer key needs a second look.

**Agreement isn't a vote.** On the Hermès Birkin (L067), two models said Pristine, I said Excellent, and only Opus said "Insufficient information," which was the right answer. The listing describes everything in the box and nothing about the bag. If I'd gone with the majority, I'd have been wrong too. Each model still has to be checked against the rule, not against the others.

**I didn't move the goalposts.** On the Hermès Bolide (L082), my rubric says five marks means Good. I'd graded it Very Good, and my first instinct was to change the rule to "more than five" so my grade would count. That's changing the test after seeing the answer, the exact thing pre-registering is meant to stop. The rule stayed, and my label was marked wrong.

## 8. Rules I added or fixed

The review exposed holes in my rubric. Each was decided and written down:

| Rule | Decision |
|---|---|
| **Box and dust bag only** | Packaging isn't evidence of condition → "Insufficient information" |
| **Tags still attached** | Evidence the item is unworn, in every category → Pristine or Excellent per the rubric |
| **Good vs. Fair** | The rubric contradicted itself. Now Fair means: it doesn't work properly, OR it has 3+ structural flaws, OR the listing says it needs repair (including platform boilerplate like "may require repair") |
| **Two conflicting condition statements** | If no wear is described, grade to the **lower** statement. If wear is described, the description wins |
| **Visible staining** | Good, regardless of how many marks |

I also added **definitions** to the rubric (structural flaw, cosmetic flaw, functional impairment, how to count flaws by location).

In total **29 labels were amended**. Each one is marked in the file with "AMENDED 2026-10-09" and a reason, so nothing was changed silently. I also caught and reversed one of my own over-corrections (L013).

## 9. Results with corrected labels (read the warning first)

⚠️ **These numbers flatter the models.** I changed labels *after* seeing what the models said. Even with honest intentions, that pushes the answer key toward the models. **The original-label numbers in section 6 are the headline.** These are here to show how much of the remaining gap was my own error.

| Condition agreement | v1 original | v1 corrected | v2 original | v2 corrected |
|---|---|---|---|---|
| Sonnet 5 | 49% | 57% | 70% | **82%** |
| Haiku 4.5 | 59% | 65% | 73% | **81%** |
| Opus 5 | 51% | 62% | 75% | **87%** |

Correcting my labels added 8–17 points. Roughly half of v2's remaining disagreement was me, not the model.

## 10. Cost

| Model | Price per million tokens, input / output (a token is roughly ¾ of a word) | v2 agreement (original labels) |
|---|---|---|
| Haiku 4.5 | $1 / $5 | 73% |
| Sonnet 5 | $2 / $10 | 70% |
| Opus 5 | $5 / $25 | 75% |

**Haiku is within a couple of points of the best model at about a fifth of Opus's price.** But 150 listings isn't enough to rank models that are this close. A gap of 2–3 points here is 3–5 listings, which is within run-to-run noise. The honest conclusion: *the cheap model is good enough to keep testing*, not *the cheap model is just as good*.

(I tried Opus 5.5 too, but it doesn't support the feature I use to force a structured answer, so it was left out.)

## 11. Prediction scorecard

| Prediction (written before results) | Result |
|---|---|
| Models will be more generous than me when they disagree | **Mostly held.** True for Sonnet and Haiku; Opus was balanced in v1 and slightly *stricter* in v2 |
| Models will miss my category-specific Pristine rule | **Held**, especially Sonnet |
| v2 lifts bare-claim agreement to ~60% | **Held** (67%) |
| Opus gains most from v2 | **Held** |
| Staff-written listings agree 10+ points more than seller-written | **Not tested yet** |
| Detailed listings agree more than sparse ones | **Not tested yet** |
| Models are more generous on sparse listings | **Not tested yet** |

The three untested predictions need a breakdown by platform and listing detail. That's still owed.

## 12. Limits (what these numbers can't tell you)

- **One grader.** No second person checked my labels.
- **v2 was written after seeing v1 results on these same 150 listings.** The guardrails help, but the real test is new listings.
- **Prompt and field description changed together in v2**, so I can't say which change did what.
- **One run per model.** Big shifts (+20 points) are solid. Small gaps between models aren't.
- **I only reviewed the 24 listings all three models missed**, not the ones only one model missed.
- **The blind re-grade of the Week 1 listings hasn't been compared** to my Week 1 grades yet. That comparison would show how consistent I am with myself.

## 13. What I learned

1. **Check your instructions before blaming the model.** The biggest improvement this week came from fixing a contradiction I wrote, not from a better model.
2. **The answer key is a product too.** 13 of 24 hard cases were my own mistakes, six of them because I under-read the title. A golden set needs review and version control like anything else.
3. **Write predictions down first.** It's the only way to know whether a result surprised you.
4. **Look at *how* it's wrong, not just *how often*.** The confusion matrix found the problem. The headline percentage never would have.
5. **Cheaper can be close enough**, but only a bigger test can prove it.

## 14. Next: Week 3

- **Prompt v3** that adds the new rules (packaging, tags, conflicting statements, Fair). Ideally the prompt is generated directly from `rubric.md`, so the rules and the prompt can never drift apart again.
- **Run v3 on 5,000 listings it's never seen**, and re-run these 150 as a regression check.
- **Give item type a fixed list** to choose from.
- **Stop retrying errors that will never succeed.** When I ran out of API credit mid-run, the tool kept retrying pointlessly.
- Still owed: platform and listing-detail breakdowns (the untested predictions), plus the blind re-grade comparison.

---

## What's in this folder

| File | What it is |
|---|---|
| `labeling_instructions.md` | The rules I graded by, plus a log of every rule change |
| `data/labels.csv` | The answer key: 150 listings, my grades, confidence, notes (29 amended rows marked) |
| `data/predictions_<model>.jsonl` | What each model said with prompt v1 |
| `data/predictions_<model>_v2.jsonl` | What each model said with prompt v2 |
| `data/disagreements_v2.csv` | The 24 listings all three models missed, with the cause of each |
| `normalize.py` | Cleans up text so "YSL" and "Saint Laurent" count as the same brand (13 tests) |
| `harness.py` | Sends every listing to a model and saves the answers. If it stops partway, it picks up where it left off |
| `score.py` | Compares model answers to the answer key and prints agreement plus the confusion grid |
| `disagreements.py` | Finds the listings every model got wrong |
| `results/week2_evaluation_results.xlsx` | Every number in this README, in one workbook |
| `NOTES.md` | My running log, including predictions written before each run |

Related files in `week-01/`: `extract.py` (holds prompts v1 and v2), `rubric.md` (the condition grading rubric), `data/listings.csv` (the 150 listings).

## How to run it

From the repo root, with the Week 1 virtual environment active (`source week-01/venv/bin/activate`):

```bash
# Get model answers (prompt v1 or v2)
python3 week-02/harness.py claude-haiku-4-5 --prompt-version v2

# Score them against the answer key
python3 week-02/score.py claude-haiku-4-5 --prompt-version v2

# List the listings all three v2 models missed
python3 week-02/disagreements.py
```

Running the harness calls the Anthropic API and costs money. An API key goes in `week-01/.env`.
