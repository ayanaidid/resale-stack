
---
## Wednesday, Sept 16, 2026
On anchored: that the Week 1 grades were done with model output visible, that this is anchoring, and that the column exists so the golden set can distinguish labels made blind from labels that might have been pulled toward the model's answer. Note that everything in Week 2 is N and the Thursday re-label is the reason you can measure the difference at all.

On label_confidence: that it's your own confidence in your label, not the model's. The reason it's there: it lets you check where disagreements land. If models disagree with you mostly on your low-confidence rows, the rubric is doing its job and the hard cases are genuinely hard. If they disagree on rows you marked high-confidence, something's wrong with either the rubric or your application of it — and that's a finding, not noise.

**Pre-registered prediction:**
Written before any Week 2 labeling. Recorded so the result can be checked
against what I actually expected, rather than against what seems obvious
afterward.

*The axis.* Platforms are grouped by who writes the listing copy, not by who
authenticates. Staff-written: The RealReal, Fashionphile, ThredUp.
Seller-written: Vestiaire Collective, Poshmark, eBay, Vinted. Vestiaire
authenticates but its listings are written by sellers, so it sits with the
seller-written group. The prediction is about description consistency, which
tracks who writes the copy.

*Prediction 1 — agreement by who writes the copy.* Agreement between my labels
and the models' will be at least 10 percentage points higher on staff-written
listings than on seller-written ones. Reasoning: staff write to a house style,
so their descriptions should be more consistent and more explicit about wear.
This is not independent of Week 1 — on the 20 listings where both the model and
I assigned a real tier, staff-written agreed 3 of 6 (50%) and seller-written 5
of 14 (36%). That is a 14-point gap in the predicted direction on six listings,
which is far too small to mean anything. The prediction is that it survives at
150.

*Prediction 1b — agreement by evidence density.* Agreement will be higher on
listings that describe wear in specific terms than on sparse listings, and this
gap will be larger than the gap in Prediction 1. Reasoning: who writes the copy
is only a proxy for how much condition evidence a description carries, and I
think it is a weak one. Staff write at volume against a template, and Week 1
shows exactly this: I marked the text ungradeable on 4 of 10 staff-written
listings versus 1 of 20 seller-written, because The RealReal and ThredUp push
condition into structured fields and leave the description as attribute soup.
If 1b holds and 1 doesn't, the finding is that evidence density explains
agreement and who writes the copy doesn't.

These two predictions pull against each other, deliberately. Prediction 1 says
staff-written copy is easier to agree on. The Week 1 ungradeable counts say
staff-written copy is more often empty of condition evidence. At least one of
these is wrong and I want it on record which I expected to win.

*Prediction 2 — direction of the skew.* Where the models disagree with me they
will grade more generously, as in Week 1 (9 of 12 disagreements). The skew will
be worse on sparse listings than on detailed ones, on both platform groups.
Reasoning: a description that states little leaves more room for the model to
fill the gap, and it fills it in the flattering direction.

*How these get checked (Thursday).* Agreement is scored separately for
staff-written and seller-written listings, and separately for listings with and
without substantive wear description. Evidence density is approximated by
`label_confidence` and by whether the listing hit the `Insufficient information`
bar.

*Week 1 baseline.* Condition-tier agreement was 8 of 20 (40%) on the subset
where both the model and I assigned a real tier, or 8 of 30 (27%) across all
graded listings. The model declined on 10 of 30. Platform split of the 30:
10 staff-written, 20 seller-written.

---
## Thursday, Oct 1, 2026
- scripts that read files need paths anchored to the code, not the working directory. It's the kind of bug that only surfaces when something else starts calling your code — which is exactly what Week 2 is doing to Week 1.

---
## Tuesday, Oct 6, 2026

*Brand-absent rule amended*
Changed the rule for listings that name no brand from `Insufficient
information` to `Unbranded`. The original rule reused the condition-tier value
for consistency, but I never applied it: all nine no-brand rows were already
labeled `Unbranded`, so the written rule and my practice had diverged. Six of
the nine are fine jewelry sold on materials rather than a house name, where
`Unbranded` describes how the item is actually sold. `Unbranded` here means the
listing names no brand, not that the item has none — for the three clothing and
shoe rows the seller may simply have left it out.

Rows affected by the amendment: zero. No re-labeling needed.

*Alias added: `not stated` → `unbranded`*
The Week 1 extractor's schema instructs the model to output `Not stated` when no
brand is named. My labels use `Unbranded` for the same case. Added an alias in
`normalize.py` so these score as a match. Legitimate under the alias rule: both
strings describe the same thing — no brand named in the listing — and without
the alias every no-brand row would count as a model miss for a wording
difference.

*Blind re-label limitation*
Recognition of Week 1 listings was not recorded during the blind re-label pass.
The re-label had roughly three weeks of separation from the original grading,
with Week 1 files closed and rows shuffled. Intra-rater agreement on these 30
should be read as an upper bound on consistency, since residual memory can't be
ruled out.
