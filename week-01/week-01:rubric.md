# Condition Rubric — Week 1

Five tiers. Definitions, criteria, and boundary cases are my own judgment, informed by three years as a PM at The RealReal — not a reproduction of any internal grading system.

Tier names and the broad category-specific criteria are aligned to The RealReal's **public** condition standard (their published buyer/seller FAQ), so this rubric maps onto a real-world taxonomy rather than an invented one. Where their public language is imprecise, I've made the test explicit myself — see the note under Very Good.

**Written before any prompt or code.** The seller-speak predictions in Part 2 are pre-registered: they're my read on each phrase, recorded before seeing what the model does with them.

---

## Part 1 — The five tiers

| Tier | Definition | Observable criteria | Boundary case |
|---|---|---|---|
| **Pristine** | As-new condition with complete original packaging. No visible wear, and, depending on category, includes the full set of tags/box/dust bag. | • No scratches, scuffs, or visible wear anywhere on the item<br>• All functional elements work seamlessly (zippers, clasps, buckles, closures)<br>• Handbags/shoes/accessories: tags attached, box included, dust bag included<br>• Jewelry: no wear, tags not required<br>• Clothing: tags attached | An item that is visually and functionally flawless — zero wear, all hardware perfect — but is missing one piece of original packaging (e.g. tags detached but not lost, or no dust bag). Under this rubric that item does **not** qualify as Pristine, even though it looks brand new — it drops to Excellent. |
| **Excellent** | Visually and functionally like-new, but missing some or all original packaging. No meaningful wear. | • No visible wear, scuffs, or damage — same visual bar as Pristine<br>• All functional elements work seamlessly<br>• Handbags/shoes/accessories: missing tags and/or box and/or dust bag<br>• Jewelry: only extremely superficial wear allowed (e.g. faint surface scratches), even without full packaging expectation<br>• Clothing: unworn but tags not attached | An item with the first trace of actual use — one small, faint scuff, or a barely visible fold line in the leather from being carried once or twice — as opposed to zero wear at all. If the wear is visible but minor and isolated (one mark, not a pattern of use), it still reads as Excellent. Once there are multiple small marks or the wear is spread across the item rather than a single spot, it tips to Very Good. |
| **Very Good** | Clear signs of having been used, but wear is light and doesn't compromise the item's overall look or function. | • Handbags/accessories: lightly worn corners, light scratches, some interior wear (light staining, minor marks)<br>• Shoes: light sole wear, faint creasing at flex points<br>• Jewelry: minor scratches, small nicks, small dents<br>• Clothing: light markings or fading<br>• All function still works normally — no repairs needed, nothing broken | An item stays Very Good as long as it has **no more than four cosmetic marks**, each subtle enough not to be immediately noticeable, **and** no structural or functional issue of any kind. The moment either threshold is crossed — a fifth mark, or even one flaw that is structural/functional rather than cosmetic — it moves to Good. |
| **Good** | Clearly used, well-loved condition. Functionality intact throughout, but this reads unmistakably as a second-hand item, not a lightly-used one. | • Wear present in both severity and quantity — several flaws, or flaws severe enough to be immediately noticeable<br>• Interior: visible staining, marks of use, lining wear<br>• Hardware: visible wear, tarnish, or discoloration<br>• Fabric: pilling, noticeable discoloration<br>• Still fully functional — nothing broken, no repairs needed | An item crosses from Very Good into Good by **either** of two paths: (1) a single flaw that affects **structure** rather than just surface — one visibly worn or misshapen corner — regardless of how few other marks are present; or (2) **five or more cosmetic marks**, even if each is individually subtle, purely on accumulation. Path (1) dominates: one structural flaw outweighs several purely cosmetic ones. |
| **Fair** | Visible structural damage and/or repairs, but the item is still fully usable. The last tier before an item is no longer sellable in normal condition. | • Structural damage present (not just cosmetic), but not severe enough to make the item unusable<br>• Visible repairs allowed (e.g. re-stitching, hardware replacement), but not major reconstructive work like patches or panel replacement<br>• Multiple serious flaws may be present simultaneously<br>• Still functional for a buyer's practical use | The line from Good to Fair is crossed when wear starts to affect **function**, not just structure or appearance — a zipper noticeably harder to close, a strap attachment under visible stress, hardware that no longer sits flush. The item stays Fair rather than dropping below sellable as long as it can still fully perform its original purpose (a bag still closes and carries, a shoe can still be worn): **functional impairment without functional failure.** |

### Note on the Very Good / Good line

The RealReal's public condition standard describes this boundary by degree rather than by test: Very Good bags and accessories show "lightly worn" corners, light scratches, and some interior wear, while Good shows "worn" corners, moderate scratches, and interior wear. The same three criteria, escalated from light to moderate — with no stated threshold for where one becomes the other.

That ambiguity is the single most consequential gap in the taxonomy, because it's the boundary most listings actually sit near. The four-mark ceiling and the structural-flaw override above are my attempt to make that line operational — a test a human or a model could apply consistently, rather than a judgment call re-litigated per item.

**Open question for Week 1 error analysis:** the four-mark ceiling is a hard number derived from judgment, not from data. It's the part of this rubric most likely to break on contact with real listings. If items with three marks read as Good, or five-mark items read as Very Good, that goes in NOTES.md rather than being silently overridden — the tension is itself evidence about whether mark-counting is the right mental model at all, or whether the real judgment is more holistic than any count.

---

## Part 2 — Seller-speak translations (pre-registered predictions)

Twenty phrases sellers actually use, and what I believe each one means. **Written before running any of them through the model.**

Two distinct types of phrase emerged while writing these, and the distinction matters more than I expected:

- **Direct wear descriptors** (1, 2, 3, 8, 9, 10, 14, 18, 19) — genuinely attempting to describe condition.
- **Framing / hedge phrases** (11, 12, 13, 15, 16, 17, 20) — doing rhetorical work instead: justifying a price, pre-empting disappointment, or reframing a flaw as a feature.

For the second group, the prediction isn't really about wear level. It's about *why the seller chose that phrasing* — which is a different and probably harder thing for a model to catch.

| # | Euphemism | Predicted tier | My read |
|---|---|---|---|
| 1 | "Minor wear consistent with age" | Very Good | Used, but not heavily since purchase. Light folding in the material, very light scratches/scuffs, possibly minor lining damage. |
| 2 | "Some patina" | Very Good | Slight discoloration and/or minor cosmetic damage to the exterior. |
| 3 | "Light scuffing" | Good | A few scuffs on the exterior, noticeable at first glance. The phrase undersells its own severity — "noticeable at a glance" is past what "light" implies. |
| 4 | "Loved" | Very Good / Good cusp | Used, and relatively a lot. Sits right on the boundary. |
| 5 | "Well-loved" | Good / Fair cusp | Escalation of #4. Significant wear and tear, exterior issues very visible. |
| 6 | "Needs a little TLC" | Fair | Likely needs repair to be usable or presentable. |
| 7 | "As-is" | Fair | Heavily used, no repairs performed. Buyer inherits the work — discoloration, scuffing/scratches, structural damage. |
| 8 | "Gently used" | Very Good | Used only a few times, but the use shows. A scuff or two, a scratch, light folding. |
| 9 | "Pre-loved" | Good | Reads closer to "well-loved" than to "loved" — the prefix implies a fuller life than the softer phrasing suggests. |
| 10 | "Signs of gentle wear" | Very Good | Synonym of #1 / #8. |
| 11 | "Beautiful vintage patina" | Good | "Vintage" reframes wear as charm. Actual condition likely worse than "some patina" alone would suggest. |
| 12 | "Minor flaws as pictured" | Good | A disclosure phrase rather than a euphemism — trust the photos over the adjective. |
| 13 | "Priced accordingly" | Fair | An economic hedge. Sellers reach for this when the price needs justifying, which implies worse-than-typical condition. Full prediction requires the listed price. |
| 14 | "Small imperfection(s)" | Very Good | Literal-meaning synonym of #1 / #3. |
| 15 | "Shows its age gracefully" | Good | Same reframing risk as #11. |
| 16 | "Honest wear" | Good | Seller pre-empting disappointment. Usually signals more wear than a plain description would. |
| 17 | "No major flaws" | Very Good (low confidence) | Says nothing at all about minor flaws. A hedge, not a description. |
| 18 | "Everyday wear and tear" | Very Good | Synonym of #1. |
| 19 | "Some wear on corners" | Good | Maps almost literally onto this rubric's own Good-tier criteria. |
| 20 | "Odor-free" / "from a smoke-free home" | Good | The meta-signal is stronger than the literal claim: why mention it unless it was a plausible concern? Suggests an item well-worn enough that a buyer would reasonably wonder. |

### What I'm actually testing

Two separate hypotheses, worth scoring separately in Thursday's error analysis:

1. **Tier agreement** — does the model land on the same tier I did for each phrase?
2. **Framing detection** — does the model read #11, #13, #15, #16, and #20 as rhetorical moves, or does it take them at face value? My prediction is that it handles the direct descriptors well and the framing phrases poorly, because the framing group requires inferring seller *intent* from word choice rather than parsing a stated fact.

If hypothesis 2 holds, that's the more interesting finding, and it's the one that comes from having sat on the platform side rather than from knowing anything about models.
