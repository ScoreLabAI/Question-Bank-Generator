# Distractor Construction Patterns

Source: direct analysis of 4 official College Board Digital SAT Practice Tests (5, 8, 9, 11) -- both the question booklets and their answer explanation PDFs, fetched from satsuite.collegeboard.org.

This exists because the original failure mode that started this whole pipeline was ambiguous distractors -- wrong answers that are actually defensible. The Critic subagent catches this after the fact, but it's cheaper and more reliable to have the Generator build distractors from these **specific, real, nameable patterns** in the first place rather than inventing something "plausible-sounding" from scratch. Every distractor should map to one of these patterns (or a clear variant of one) -- if you can't name which pattern a distractor uses, it's probably too vague and at risk of being defensible, which is exactly what the Critic will flag.

## Math patterns

- **Wrong quantity / wrong part of the figure or problem.** The distractor is a real, correctly-computed value from the problem -- just not the one the question asked for. e.g. "This is the length of arc PQ, not arc QR." / "This is the sum of the measures of angle Q and angle P, not the measure of angle R." / "This is the number of members who joined by day 4, not the number who join per day."
- **Wrong variable/quantity substituted.** A specific number from the problem gets plugged into the wrong slot. e.g. "This is the number of members that will have joined if 100 new members, not 10, join each day."
- **Sign, direction, or transformation error.** e.g. "This is the graph of y = f(x) - 5, rather than y = f(x) + 5." / "This function indicates the account balance is decreasing, rather than increasing, over time."
- **Swapped coefficients / roles in a word-problem equation.** e.g. an equation that assigns the points-per-win and points-per-draw values to the wrong outcome.
- **Algebraic near-miss on equivalent expressions.** A distractor that's almost the correct simplification but drops or mis-combines one term. e.g. "This expression is equivalent to 9x^5 + 5x^3, not 9x^5 + 5x^2."
- **Near-miss geometric relationship.** For angle/triangle problems, a distractor built from the *wrong but related* relationship -- e.g. treating two angles as complementary when they're actually congruent, or supplementary when they're actually complementary. Name both relationships in the explanation: "may result from concluding that angle M and angle Q are complementary rather than congruent."
- **Averaging two given values -- only when the queried point is actually the midpoint (weak otherwise).** Naive averaging instead of proper interpolation is a real student error, and "this is the average of the two values given, not the value at the requested point" is a legitimate explanation. But two independent Critics in run 9 both called it the weakest distractor on an item where the queried input (age 15) was *not* halfway between the two given inputs (ages 10 and 30): with no reason to average toward that specific point, the value isn't organically produced by any partially-correct procedure, and it reads as reverse-engineered. Use this pattern when the queried point genuinely sits at the midpoint; otherwise prefer an error path tied to the actual arithmetic, such as dropping the constant term or using a data point's output as the intercept.
- **Stock catch-all -- use sparingly, only when no clean error path exists.** "Choice Y is incorrect and may result from conceptual or calculation errors." Real tests use this a lot (roughly a third to half of Math distractors in some modules), but only for plausible-looking wrong numbers with no single clean derivation error -- don't reach for this as a shortcut when a specific pattern above actually applies. If you can name the error, name it.

## Reading & Writing patterns

- **Grammar/usage: name the specific violated rule, never "sounds worse."** Real distractors are refuted with an exact grammatical fault: "results in a comma splice," "results in a run-on sentence," "results in a dangling modifier," "the singular verb '...' doesn't agree in number with the plural subject," "requires the plural noun 'hands,' not the plural possessive noun 'hands'.'" Every Standard English Conventions distractor must be traceable to one specific, nameable rule violation -- this is the single most important pattern for this skill category, since it's the one most prone to real multiple-defensible-answer errors.
- **Plausible-but-inverted word meaning (Words in Context).** The distractor uses a real, correct dictionary definition of the target word -- just one that doesn't fit this context, sometimes because it inverts the passage's logic. e.g. "'overlook' would mean look past or fail to notice, so to say the poetry is 'hard to overlook' would mean it is very likely to be noticed" -- the real definition is right, but plugging it in produces the opposite of what the passage means.
- **Direction/logic reversal (inference, central ideas).** The distractor states something almost right but flips the causal or comparative direction. e.g. "the age of the crater found, not the cause of the crater"; "temperature has been falling rather than rising."
- **Data misread from a table/graph (Command of Evidence Quantitative).** The distractor cites a real number from the visual but attaches it to the wrong category, condition, or comparison -- e.g. inverting which of two values is larger, or citing the right number under the wrong row/column label. Always ground this in the actual visual_data so the mismatch is real and checkable, not just asserted.
- **True but insufficient / doesn't fully answer what was asked.** The distractor states something accurate and even supported by the passage or visual, but doesn't actually establish the specific claim the question asks about. e.g. "though the claim... is supported by the graph, this alone does not state whether..." This is a legitimate, common R&W pattern -- distinct from being simply wrong.
- **Unsupported by the text (inference/evidence).** The distractor makes a claim the passage never actually establishes, even though it sounds plausible or is a common real-world assumption. Explanation names the specific gap: "isn't supported by the text: although the text says X, it doesn't say Y."

## What to avoid

Don't build a distractor around vague qualities like "less precise," "less effective," or "awkward phrasing" unless you can also point to a specific, objective reason (a named grammar rule, a specific misread number, an inverted definition, etc.). If you can't articulate which pattern above a distractor uses, rewrite it -- that ambiguity is exactly what got flagged as this pipeline's original motivating problem.

## Quality bar for counterexample-only distractors (run 12)

On abstract "which must be true" items the distractors are all instances of one pattern — *true for some
qualifying functions and false for others* — so the pattern name alone no longer distinguishes a good
distractor from a weak one. Three additional tests, each traced to a run-12 defect:

1. **Its own witness.** The concrete function that falsifies this distractor must not be the same one that
   falsifies another distractor. One witness killing three choices makes a four-option item a one-idea item.
2. **Not equivalent to another choice.** Substitute whatever the stem forces (a zero intercept, a fixed point)
   and confirm no two choices reduce to the same condition.
3. **Not measure-zero.** "True exactly when the slope is 1" is not a usable *sometimes*. Prefer a distractor
   true across a range of qualifying functions, so a student who tests examples can actually encounter it.

Named error paths still matter and still belong in the explanation — the sign slip that puts a slope range on
the wrong side of zero, computing an intercept as 6m instead of 6/m, treating a maximum at an interior point as
a peak the graph then descends from — but on this item shape they sit alongside, not instead of, the three
tests above.
