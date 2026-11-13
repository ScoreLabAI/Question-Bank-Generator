# Item Design Rules

Hard-won rules from actual production runs. Everything here is something that reached the Critic (or worse, got banked) before anyone noticed — these aren't theoretical style preferences, each one has a run number attached.

Read this before generating. `distractor-patterns.md` covers what a wrong answer should be *built from*; this file covers ways an item can be broken even when every individual distractor is fine.

## Answer choices

**Numeric choices go in ascending order.** The Digital SAT lists purely numeric answer choices smallest to largest, always. This was violated repeatedly across runs 1–7 (12 banked questions had to be reordered retroactively). `validate_batch.py` now fails the batch on this, so it's cheap to get right up front and annoying to fix later. If you reorder choices after drafting, **move `correct_answer` and the `distractor_*_explanation` fields with them** — a desync between the key and the explanations is a worse defect than the ordering was.

For non-numeric choices (inequalities, expressions, ordered pairs, sentences) there's no strict rule, but group them sensibly — e.g. inequality choices grouped by symbol then ascending by boundary value, so `x < 1, x < 3, x > -3, x > 3` rather than shuffled.

**Choices must be genuinely parallel.** Four choices of similar length and grammatical shape. If the correct choice is visibly longer or more hedged than the other three, a test-wise student picks it without doing the work.

**In a contextual item, a distractor must be plausible in the STORY's units, not just reachable by a nameable error.** Run 11 hit this twice in one batch and the Critic rejected both. A hot-air-balloon descent item offered `79,200` minutes (the "multiplied by 60 instead of dividing" path — perfectly nameable, and about 55 days of descent); a heating-solution item offered `371` degrees Celsius (the "used the undivided difference as the rate" path, for a solution warming a few degrees a minute). Both are eliminable at a glance on real-world scale alone, so they test nothing. Worse, in the balloon case the choices formed a transparent ×60 ladder (22, 1,320, 79,200) that telegraphed the item's whole conversion structure. After building the choice set, reread it as a reader of the *story*: if one value is absurd in context, replace it with an error path whose value stays inside the scenario's plausible range. Both fixes here kept the same skill under test (balloon: `3,300`, the feet-still-to-descend reported as minutes; solution: `101`, from forgetting to halve when solving `2c = 34`).

## Answer-key placement

**Never key the answer to a value a memorized shortcut reaches.** The specific case that got flagged (run 7): a system-of-inequalities item keyed to the **origin (0, 0)**. "Test (0,0)" is a taught heuristic for shading inequalities, so a student who reflexively substitutes it lands on the credited answer without engaging the item. Same logic applies to keying an item to the most obvious round number in the stem.

**Vary the key position.** Don't let `correct_answer` drift toward one letter across a batch. Run 9 produced seven drafts that keyed only to A (4) and B (3), with nothing on C or D — no single question was wrong, and nobody noticed until assembly. `validate_batch.py` now emits a `[WARN]` (not a failure) when a batch of four or more uses fewer than three distinct key letters, or when one letter takes more than half the batch. It's a warning rather than a failure because ascending numeric ordering fixes the key position on numeric items, so some skew is genuinely unavoidable. The fix, where the choices are **not** purely numeric — statements, expressions, inequalities, ordered pairs — is to reorder them so the key moves, keeping the grouping sensible, and to move `correct_answer` and the `distractor_*_explanation` fields along with it.

## Ordered-pair and coordinate items

**Never place an answer choice exactly on a boundary line.** With a non-strict symbol (`<=`, `>=`) a point on the line is a solution; with a strict one it isn't. Putting a choice there manufactures an argument about strictness that has nothing to do with what you're testing. Check every choice against every boundary before finalizing.

**For a "which pair is a solution" item, make each wrong pair fail differently** — one satisfying only the first constraint, one only the second, one neither. A distractor set where all three fail the same way teaches nothing.

## Discrete contexts

**A physically discrete quantity must come out as a whole number.** Run 6 caught a system-setup item where the budget produced `d = 12.857…` devices. The student wasn't asked to solve it — but a fractional count in a discrete context is still a real defect, because any student who *does* solve it finds nonsense. Check that your solution is integral for anything counted in people, devices, tickets, blocks, or animals, and adjust a constant if it isn't.

**Round-down items need a non-integer boundary.** If you're asking for the *greatest whole number* satisfying an upper-bound inequality, choose numbers so the division doesn't come out even. If the boundary is exactly 8, there's no rounding decision to make and the item collapses to a plain solve.

## Graph-read items

**Every value the student must read has to land on a labeled gridline.** Discovered in run 5: with `y = 2x − 3` plotted over `y ∈ [−8, 10]`, matplotlib labeled y-ticks at even integers only, so the queried point (4, 5) fell *between* gridlines and the item was unanswerable as intended. Two fixes, use both:

1. Set `x_tick_step` and `y_tick_step` explicitly in `visual_data` (see `render_visual.py`). Don't let matplotlib derive spacing from the range.
2. Verify that the queried point **and all four answer choices** sit on labeled ticks.

An even slope with an odd intercept is the classic way to produce off-gridline integer points — watch for it.

**Check the tick/slope parity, not just the two points you happen to use.** Run 11 drafted `y = 3x + 4` with `y_tick_step: 2`. The author's own reading points, (0, 4) and (2, 10), were both on labeled gridlines, so the item looked fine — but a student reading the slope the natural way, one x-unit at a time, goes (0, 4) → (1, 7), and 7 sits between the labeled 6 and 8. The item was technically answerable and practically confusing. The condition to check is `slope × x_tick_step` being a whole multiple of `y_tick_step`; when it isn't, some adjacent-tick reads land between gridlines. **The safe default is `x_tick_step: 1` and `y_tick_step: 1` over a modest range**, so every integer point on the line is labeled and no reading strategy can go wrong. Both graph items in run 11 use it. `validate_batch.py` now emits a `[WARN]` when a linear graph spec fails the parity condition.

**Widen the window so the answer is visible.** Run 11's two-line graph item plotted `x ∈ [-3, 3]` with the answer at `x = 5`. That is mathematically fine — the equations are fully determined and linear extrapolation is unambiguous — but a student who tries to locate the answer on the picture finds nothing there, and the stem carried no "if this pattern continues" cue. Either widen the range to contain the answer (what run 11 did) or add the cue. Don't ship a graph item whose answer is off-frame and unsignposted.

## Weakly-diagnostic shapes to avoid

**"Which value is NOT a solution" combined with a sign-flip inequality.** Flagged in run 7. A student who forgets to reverse the symbol when dividing by a negative concludes `x > 5` instead of `x < 5`, and then sees *three* of the four choices as non-solutions. The intended misconception doesn't converge on a single distractor, so the item can't discriminate. The shape is fine on its own — just not paired with a sign flip.

**On a "must be true" item, never include the direct logical NEGATION of the key.** Run 11's first structural draft offered `f(2.5) < 0` and `f(2.5) > 0` as two of the four choices. A contradictory pair is a flare: a test-wise student knows the writer didn't put two arbitrary opposites in the same list, narrows to those two without doing the algebra, and guesses at 50%. (It also leaves `f(2.5) = 0` in no choice at all, which looks like an oversight even when — as here — the givens make it impossible.) Replace the negation with another statement that is true for SOME qualifying functions and false for others, so all three distractors need a counterexample to kill. Run 11 swapped in `f(10) < 0`, which mirrors the existing `f(0) < 0` distractor on the other side of the constrained interval.

**Check that no plausible WRONG METHOD lands on a listed choice by coincidence.** This is distinct from checking that each distractor has an error path — it runs the other direction. Run 11's item gave line p as `y = 2x + 7` alongside `f(x) = c(x - 3) + 7`. The repeated `+ 7` invites a student to pattern-match the two forms and assume `c` equals p's slope, 2, skipping the intersection step entirely — and that shortcut produced exactly `21`, a listed choice. A wrong method that finds its own answer waiting in the choice list gets silently confirmed; the student never learns they were wrong. The fix was to renumber line p to `y = 3x + 1`, which leaves the intersection at (6, 19) and every downstream value identical while sending the false shortcut to 28, an off-menu number. Before finalizing, name the one or two shortcuts a hurried student would most likely try and confirm neither hits a choice. Repeated constants across two given expressions are the usual trigger.

**A distractor no error path produces.** If you can't name the specific mistake that yields a wrong choice, it's filler. Run 7 shipped `60` as "half of 120" on a two-variable system item; the Critic correctly called it arbitrary next to the two well-motivated distractors beside it. (Note the counter-case: dividing a total evenly while ignoring the second constraint *is* a standard College Board distractor. The test is whether you can name it, not whether it looks sophisticated.)

## Context coherence

**The story has to survive the algebra.** Run 7's first Systems draft bolted a negative coefficient (`−5t`) onto a pure "ticket sales" narrative with no justification for how selling something could subtract, and used two different prices for the same item across the two equations. The math was unambiguous and the answer was unique — the Critic flagged it anyway, correctly, because the scenario didn't support the equations.

The reliable fix for **opposite coefficients in a real-world system**: make equation 1 a **total** and equation 2 an explicitly stated **difference**, using the same per-unit values in both. The opposite signs then arise naturally instead of being reverse-engineered for clean elimination.

**A nonzero value at the origin needs a baseline that permits one.** Run 11 drafted two hikers whose elevation was measured "above the trailhead", with `f(t) = 15t + 200` — so a hiker standing at the trailhead at the moment she starts climbing is already 200 feet above it. The algebra was unimpeachable and the answer unique; the story was impossible. This shows up whenever an additive constant meets a baseline phrase ("above the trailhead", "from the starting line", "since the account was opened"). **Fix the framing, not the numbers**: re-base the measurement to something that legitimately starts nonzero — here, "elevation above sea level", which lets two trails have trailheads at 200 and 255 feet — so all four choices and the key survive untouched. Changing constants to force `f(0) = 0` usually breaks the item you meant to write.

**A stated per-unit MINIMUM must not exceed a stated hard CAPACITY CAP elsewhere in the same stem (run 17).**
Run 17's first draft of a candidate-rejection item required 45 guests to "each receive at least 4 skewers"
(a stated floor of 200 skewers once the head table's 20 are added) while separately stating the venue's
warming trays "can hold at most 160 skewers" and that the caterer "will fill the trays to their full
capacity" — i.e., only 160 would actually be served. Both clauses are presented as certain facts, but
200 > 160 means the story asserts the minimum is both required and guaranteed to be missed, with no
narrative resolution. Worse, the ambiguous phrase "at most 160 skewers at one time" (left open whether
trays could be refilled across the event) gave a second, equally literal reading under which the stated
200-skewer minimum IS what gets served — making that reading's resulting value a genuinely defensible
second answer, not just a careless-error distractor. This is the same family as the floor/cap
candidate-rejection shape that reliably calibrates Hard, but it fails at the correctness stage, before
difficulty is even relevant. The fix that worked: lower the per-unit minimum (4 skewers/guest -> 2) so the
stated floor (110) sits safely below the stated cap (160) — the naive-candidate-gets-rejected-by-the-cap
trap survives untouched, but no two stated facts contradict each other anymore. Before submitting any
candidate-rejection item built on a floor-vs-cap (or minimum-vs-maximum) pair, compute both numbers and
confirm the floor is strictly less than the cap; if it isn't, adjust the floor's rate or count, not the cap.

**A piecewise real-world model must be CONTINUOUS at the changeover.** Run 9's first dendrochronology draft gave a tree's trunk diameter as `D = 0.6a + 30` for ages 40 and up, with two earlier data points implying `D = 0.6a + 2`... which puts the trunk at 26 cm just before age 40 and 62 cm at age 40. The Critic flagged it, correctly: the narrative ("the wildfire increased the tree's growth *rate*") licenses a change in **slope** at the branch point, never a jump in **level**, and a trunk diameter is physically continuous. Stated validity intervals (`valid only for a < 40` / `a >= 40`) do *not* rescue this — they make the math unambiguous while leaving the story impossible, and the answer was uniquely determined the whole time. The two-branch shape is the workhorse of the hard Algebra cells, so this check applies constantly: before submitting, evaluate **both** branches at the changeover point and confirm they agree. Where they don't, adjust one branch's constant, not its slope, so the rate story survives.

**Every quantity in the stem must be defined once and used consistently.** Run 3 had to regenerate a cycling item that defined "official recorded time" as both the elapsed start-to-finish time *and* ride time plus a 4-minute penalty — a direct self-contradiction — and never said which one the speed threshold applied to. Run 3 also regenerated a grain-silo item where "sets aside 100 bushels for seed stock" was genuinely ambiguous between *removed from* and *still in* the silo, and the second reading made a second choice defensible.

Before submitting, reread the stem asking: could any noun phrase here be read two ways by a careful student?

## Explanations

**A distractor explanation must actually describe a path that produces that value.** Run 7 found two explanations on one item that described the wrong mechanism — the explanation for `x > −3` in fact laid out the arithmetic that yields `x > 3`, a different answer choice. This is invisible to structural validation and is student-facing, so it ships straight to a paying user at the exact moment they got the question wrong and are trying to understand why.

Verify each explanation by *running the error it describes* and confirming you land on that choice's value.

**Say WHERE in the solve the error happens, and check the path end-to-end from there.** Run 11 caught two explanations that named a plausible error but described a path nobody could actually walk. One claimed a student "treats the slope as +1 instead of −1" and then evaluated `f(x) = x + (a + b)` — but a genuine +1 slope forces the intercept to `b − a`, not `a + b`, and gives `2b`, not the `2(a + b)` on offer; the explanation had quietly kept an intercept that only follows from the *correct* slope. The other said a sign error produced `21` without saying when it occurred: made early, the error changes the constant and yields ≈53.7 (no listed choice); made only at the final evaluation, it yields 21. Both were fixed by pinning the error to one step and re-running from there ("after correctly determining that f(x) = −x + (a + b), a student who drops the negative sign when substituting…"). A compound error silently mixing correct and incorrect intermediate values is not a path a student takes — it is a value working backward in search of a story.

**Don't attribute a real fabricated passage to a real person or work.** Covered in `sat-taxonomy.md`; repeated here because it's a hard rule, not a preference.

## Near-duplicates within a cell

**A near-duplicate is a repeated SHAPE, not a repeated noun.** Run 10 generated an embroidery-thread item — a fixed setup quantity, a machine consuming from a finite bobbin at a fast rate, a slower hand rate once the bobbin empties, and "what is the total at t = 240?" — for the same cell that already held a soda-bottling item: a fixed setup quantity, a machine consuming from a finite cap cartridge at a fast rate, a slower hand rate once the cartridge empties, and "what is the total at t = 90?" Different industry, different numbers, identical item. Changing the nouns does not produce a new question.

Before critique, check a draft against the used-topics log on all four of these axes, not just the scenario:

- the **shape family** (hidden-threshold piecewise, abstract must-be-true, candidate-rejection, and so on),
- the **source of the key structure** — a consumable resource, a fixed capacity, a stated validity interval, a graph,
- the **direction of the solve** — evaluate forward at a given input, or solve backward from a target value,
- the **ingredient list** — an additive head start, a rate change, a unit conversion.

A draft matching an existing item on all four is a duplicate even with a brand-new setting; a draft that differs on the direction of the solve or the source of the structure is generally a genuine new item. When a cell's confirmed-Hard shape family is saturated in one direction, vary the direction or the structural source in the Generator prompt explicitly, rather than only supplying a "don't reuse these scenarios" list — run 10's regeneration prompt had to name the collision and mandate the inverse direction to get a distinct item.

## Nested or tiled interval choices (run 12)

When the answer choices are intervals — a range for a slope, a range for an x-intercept — check whether the
keyed interval CONTAINS the others. Run 12 produced two items with this defect independently: an x-intercept
location item whose key was literally the union of two distractors, and a slope-range item whose three
distractors tiled the key. In both, a student who knows no mathematics can reason "the widest interval, the one
containing the others, is the safe answer on a must-be-true item" and score the item without engaging it.

The fix has a constraint that is easy to get wrong: on a must-be-true item, **any interval containing the
guaranteed one is also a correct answer**, so a replacement distractor cannot simply be wider. It has to stick
out past the key on one side WHILE omitting part of the guaranteed range, or sit somewhere the key does not
reach at all (a sign-slip range on the wrong side of zero works well). Fixing only one of three nested
distractors is not enough — run 12's first fix left two subsets in place, and the widest-interval heuristic
still landed on the key. `validate_batch.py` now WARNs when the keyed interval is a superset of two or more
other choices.

## Two choices that are logically equivalent under the stem (run 12)

Two answer choices can look different and be the same claim once the stem's constraint is applied. Both of
these shipped to critique in run 12:

- f linear with f(2x) = 2f(x) forces f(x) = mx, so "f(1) = 2" and "the slope of f is 2" are true under exactly
  the same condition, m = 2.
- f linear with f(2) = 7, so "the slope of f is positive" and "f(-6) < 7" both reduce to m > 0.

This is a real defect, not a nitpick. A student who notices that two choices stand or fall together can
eliminate both, on the sound grounds that a single-answer item cannot have two correct choices — without doing
the mathematics. It also quietly reduces a four-option item to three. Before submitting, substitute the
constraint the stem forces (b = 0, or a fixed point) into every choice and check that no two reduce to the same
condition on the free parameter.

## Must-be-true items: each distractor needs its OWN witness (run 12)

The abstract "which must be true" shape is the only one that reliably calibrates Hard in the Algebra linear
cells, but the shape alone does not earn the tag. Run 12's Calibrator downgraded four of nine items to Medium,
and the line it drew was consistent:

- If the stem's conditions determine the function COMPLETELY, all the distractors become always-false rather
  than sometimes-true, no counterexample construction is possible, and the item is "deduce one fact, then use
  it once" — Medium, however elegant the central insight. (Run 12's interior-extremum item, where an interior
  maximum forces a linear function to be constant, is the clean example: a genuinely nice insight, still
  Medium.)
- If ONE witness falsifies all three distractors, same verdict. Run 12's functional-equation item, f(2x) =
  2f(x), was killed by the single function f(x) = 0.
- A distractor true only at one exact parameter value — "g(x) − f(x) = 3", true iff the slope is exactly 1 — is
  technically sometimes-true but functionally always-false, since a student sampling a few examples will never
  land on it. Widen it to an inequality ("> 3", true for a whole range of slopes) so it carries the same
  misconception with real weight.

So the bar is: three distractors, each requiring a DIFFERENT counterexample, over a substantial set of
qualifying functions.

## Candidate-rejection constraints must be stated as certain facts (run 14)

A capacity/cap constraint that will force a naive solution to be rejected has to be phrased so the binding
value is a stated FACT, not something the reader must infer. Run 14's first draft of a disaster-relief kit
item said the supplier "could send only enough specialized bandage rolls to assemble AT MOST 80 advanced
kits," then separately said the organization "used every specialized bandage roll it received." Read
strictly, this only establishes a cap of ≤80 — concluding the actual count was exactly 80 requires the
reader to infer the cap was binding, which is a standard convention in these items but is a real inferential
gap, not a stated fact. The fix: state the resolved value directly ("could send only enough... to assemble
**exactly** 80 advanced kits"). Separately, when a stem introduces a rate with plain wording ("10 bandage
rolls for each advanced kit") and later refers to the same resource with a qualifier ("specialized bandage
rolls") to set up the constraint, tie the two explicitly ("...the bandage rolls used for advanced kits...")
rather than introducing what reads like a second, undefined resource pool.

## A candidate-rejection item's FINAL answer must require the rejection to matter (run 14)

Distinct from the above: even with clean wording, run 14's kit item calibrated DOWN to Medium because once
the cap value (80) is accepted as fact, the final answer is `total_kits − cap`, a single subtraction that
never touches the system that was built to discover the cap was binding. The system was load-bearing only
for the DISCOVERY step (proving the naive 100 exceeds 80), not for computing the actual answer. This is a
sharper version of the general Hard-difficulty rule already established in the Algebra Hard cells: the KEY
itself — the specific arithmetic that produces the credited choice — has to require the non-mechanical
reasoning, not just some earlier step in the story. A candidate-rejection word problem only earns Hard when
the value substituted at the boundary must be run back through a genuine equation (ideally one requiring a
coefficient division or a second unknown, not a bare total-minus-part) to reach the final answer — see the
confirmed-Hard piecewise items in the Linear equations cells, where the post-rejection step is always a full
equation solve, never a single subtraction.

## "Compute two independent bounds and take the min/max" is Medium, not Hard (run 16)

A generalization of the rule above, confirmed four separate times in one run across very different dressing.
Run 16 (Linear inequalities in one or two variables, Hard cell) generated: a two-constraint budget/weight word
problem (two separate linear inequalities, one variable fixed by a stated fact, substitute and compare the two
resulting bounds); a compound flow-rate inequality intersected with an independent labor-budget inequality
(same "derive two bounds, the tighter one wins" shape, plus a rounding step); a percentage-tolerance compound
inequality intersected with an independent absolute cap (same shape again, output as a range instead of a
count); and even a purely abstract sign-parameter solve (isolate x with a parameter in the coefficient, use a
given bound on the parameter to fix the coefficient's sign). All four calibrated DOWN to Medium. The common
thread: each is a sequence of two or more MECHANICAL, INDEPENDENT procedures — solve constraint A, solve
constraint B, compare, maybe round — with no step that requires discovering a non-obvious structural
relationship between them. A graph attached to illustrate the two boundary lines does not change this (the
laptop item had one); neither does the word-problem dressing, the number of constraints, or whether the answer
is a count, a range, or an expression in a parameter. Contrast with the confirmed-Hard candidate-rejection
floor/minimum-lot pattern (two sections up): the difference is that after the binding constraint is
identified, a Hard item requires running the accepted value back through a SEPARATE equation needing a
coefficient division or a second unknown, while a Medium "two bounds, take the min" item stops at the
comparison itself. Before mandating a "two constraints, find which binds" shape for a Hard cell, add a further
required step beyond the comparison — a genuine post-comparison equation solve (as in the floor/minimum-lot
shape), a boundary case requiring a non-obvious strict/non-strict resolution, or a "must be true" structural
claim — or expect the item to calibrate to Medium regardless of how many constraints or how much word-problem
dressing it carries.

## Run 152 additions

**CoE (Quantitative) exposure tables: keep the exposure gap moderate.** The volcano tremor-station table held Hard
(~48%) with the keyed row's exposure at 1/2-1/4 of the others; the earbud-battery table with the keyed row at 1/4-1/8
of the others calibrated Medium (~62%) because a lone extreme-outlier row points students straight at it. Aim for
the keyed row to differ from its rivals by roughly 2-2.5x on exposure, with counts close enough that raw totals mislead.

**CoE (Quantitative) choices describe data in plain values, never gridline positions.** A run-152 Generator, told
not to list paired values, wrote choices like "the post-training bar ends at the fourth labeled line" -- off-format
for the Digital SAT. If an oblique key is wanted, make it a threshold/relationship statement in plain words, not a
description of chart geometry.

**Don't label a mechanism "the standard account" unless it is real science.** A run-152 Inferences draft presented
slow gene expression as the standard account of ABA-driven stomatal closure; in reality ABA closes stomata within
minutes via ion channels. Students may absorb passage framing as fact. When a passage needs a hypothetical
mechanism, attribute it to the (invented) researcher's own proposal and use an invented compound name.

## Run 153 additions

**CoE (Quantitative) exposure tables: at least two distractors must mention the target row.** A run-153 flu-clinic
table had no stem hint about exposure and a fresh relational key, yet calibrated Medium (~70%) because only the key
and one distractor named the target branch; students dropped the two off-target choices by relevance alone. The
banked Hard volcano item had two distractors about the target row (raw total, share). Also: a stem sentence noting
that exposure "differed from site to site" names the metric as surely as the word "rate" (run-153 meteor item, ~65%).

**Don't reuse a banked key template in the same cell.** Two run-153 CoE drafts reproduced the volcano key
("at least twice as long, yet none twice as many") with new nouns; one was rejected pre-critique as a near-duplicate.
When mandating the exposure-table shape, name the banked key template and require a different relational form.

**Inferences: dense register alone does not make an item Hard.** Seven run-153 drafts written in a scholarly register
(concession to track, abstract paraphrased keys, distractors reusing passage vocabulary) all calibrated Medium
(48-72%). The key was still the one modest or qualified option, so overreaching distractors fell away. The two
lowest (~48% and ~55%) both had a highly abstract key plus a distractor that restated the account the passage
had just undercut.

## Run 154 additions

**CoE (Quantitative) exposure tables: the key must not be the only two-column choice.** A run-154 sociolinguistics table
(metric never named, wrong-base share column, key "at least 14 more hours, but none more than 54 more switches") still
calibrated ~52% because the key was the only choice that set exposure against count; a ferry before/after table went
~70% because the key was the only choice in ratio language. The fox camera-trap table that held Hard (~40%) had all three
distractors about the target row, and two of them also combined exposure with count or share -- including a TRUE
target-vs-one-rival comparison that fails only because it leaves out the closest rival. The key used a fresh threshold
form ("only at X was [exposure] smaller than four times [count]").

**Inferences: a sentence added to kill one distractor can revive another.** A run-154 oyster-midden draft added
"population and diet stayed constant" to rule out a rising-harvest distractor; the critic pointed out that constant
diet plus smaller oysters implies MORE oysters harvested, making that distractor defensible. When adding a fact to
eliminate a choice, check what else the fact entails. Also: when a mechanism acts on a shared resource (a bay's beds,
a shared aquifer), a comparison group must be stated to draw on a separate resource, or the prediction does not follow.

**FSS tense items: mark the time sequence inside the clause, not only in another sentence (run 155).** A Sirin
council draft keyed "had been spent" in reported speech ("the treasurer informed members that the proceeds ___ spent"),
with the earlier date given only in a prior sentence. The critic correctly found the simple past "were" acceptable:
reported speech allows the simple past when context supplies the order. The fix put a past reference point in the
same clause ("By 1791, the proceeds ... had paid for ...") and dropped the simple past from the choices.

**FSS: avoid two distractors that fail for the same reason (run 155).** Two non-finite forms ("suggesting",
"having suggested") fall together once a student knows a finite verb is needed. Replace one with a form that fails a
different rule (run 155 used a redundant subject pronoun, "it suggests"). Do not use a bare past-tense form as the
replacement where the passage doesn't force present tense, because it agrees with any subject and may be defensible.

**Rhetorical Synthesis "difference" notes: two near-synonyms are a real difference to a careful student (run 155).**
A bells draft meant "a wooden beam" vs "a log" as a non-contrast. The critic found it defensible as "where they part
ways". If a feature is shared, state it once ("In both traditions, ...") instead of in two differently worded notes.

**Rhetorical Synthesis: every detail in a choice must appear in the notes (run 155).** "In each of three different
cities" was flagged because the notes said "three trusts", not cities. Words such as "city", "wild", or "first" must be
in the notes or they become a reason to eliminate the key. Also do not name an invented item close to a real one in
the stated country (a "Rokel-1" rice in Sierra Leone sat next to the real ROK series and was renamed).

## Run 156 additions

**Transitions: a distractor that can reattach to an EARLIER sentence is a second key.** "In fact," (after a concession,
reinforcing the claim two sentences back) and "Moreover," (adding a second parallel example) were both judged defensible.
Transition words can skip over an aside, so a distractor fails only if it misfits every sentence it could attach to.

**Transitions: evidence that rules out the tempting relation must be at or before the blank.** A sequence-vs-cause draft
put the anti-causal evidence in the sentence after the blank; "Consequently," was defensible, and a following "however"
even read as rebutting it. Putting "rather than to the app" inside the blank sentence fixed it (~55%, Medium).

**Transitions: avoid "Finally," after a chronological list and "Admittedly," as distractors.** "Finally," also opens a
concluding remark, and "Admittedly," can read as a concession to the reader; both were arguable keys.

**Transitions: "one feature" is ambiguous between "a single" and "one of several".** If the key is "Specifically," over
"For example,", name the category so that there is only one (e.g. "one suffix on its verbs").

**Facts in dressed passages: indigo is a vat dye (no mordant).** A run-156 draft had mordants fixing indigo; madder is the
mordant-dependent plant dye. Check dye/fiber chemistry and any "the X" generalization ("certain mordants").

## Run 157 additions

**FSS tense cue must govern the MAIN clause (run 157).** A "Not one of the varieties that growers were testing during
the drought of 2008 ___ capable" draft put the only past-time marker inside the relative clause. The critic found
present perfect ("has been") defensible for the main verb. Fronting the marker ("During the drought of 2008, not one
of ...") fixed it. This is the same lesson as run 155's reported-speech item: the time cue has to attach to the blank's clause.

**FSS 2x2 pronoun x verb grids calibrate Easy (run 157).** "its/their findings suggest/suggests" went ~82%. The verb
half is decided by the adjacent noun ("findings"), so it never hides the controlling element. Don't use this shape for d2/d3.

## Run 158 additions

**Rhetorical Synthesis: a "procedural detail" distractor must not hint at selection (run 158).** "212 enrolled after more
families than expected signed up" was read by the critic as a self-selection limitation, which made the "not a limitation"
distractor defensible. Use a plainly neutral method detail (e.g. how arrival times were recorded).

**Rhetorical Synthesis: "challenge an assumption" goals must require stating the assumption (run 158).** With the goal
"challenge a common assumption", a choice giving the contradicting finding alone was defensible. "Present a finding ... as
a challenge to a common assumption" fixed it.

**Rhetorical Synthesis: if the key's explanation says "main clause", check that it is (run 158).** A key written "X and Y
are companies that both mark ..." puts the similarity in a relative clause, which undercuts the reason given for rejecting
a subordinate-clause distractor. Put the shared feature in the key's main clause.

## Run 159 additions

**Transitions Hard: the first two Hard R&W d3 items came from abstract passages (run 159).** "By extension," (a tone-perception
finding generalized to all speech perception, ~44%) and "Hence," (an art-critic's structural claim whose preceding
"rather than" sentence looks like a contrast, ~45%) calibrated Hard. Both used a dense scholarly register in which the relation
has to be reconstructed, and two distractors each fit a plausible misreading (restatement/example; summary/contrast). Concrete
narratives with explicit dates or engineering stages ("Previously," ~77%; "Ultimately," ~74%) stayed Easy/Medium even with
less common keys. The key's rarity alone ("Fittingly," ~58%) does not make an item Hard.

**Transitions: "Still," reattaches to earlier setbacks (run 159).** After a multi-stage story of failures, then a fix, "Still,"
was defensible as "despite those failures". It was swapped for "Similarly,". Same family as the run-156 reattachment rule.

## Run 160 additions

**Transitions Hard: which abstract-register relations reach Hard (run 160).** 8 abstract-register gens, each with a different
mandated key. Two reached Hard: "More broadly," (narrow lease rulings widened to all private law; "For example,"/"In short,"
misreadings, ~47%) and "Nonetheless," (a framework, then a specific quantitative anomaly immediately before the blank, then a
return that carries its own "because" reason; "Therefore,"/"Specifically," misreadings, ~48%). The abstract register did NOT
lift restatement ("In other words," ~70%), inverse ("Conversely," ~76%), purpose ("To that end," ~55%), cross-domain parallel
("Likewise," ~52%) or substitution after an explicit denial ("Instead," ~72%). For Transitions d3, mandate generalization of
scope or concession-then-return; other relations will mostly bank as d2 overshoot.

**Transitions: a limitation sentence right before a method sentence makes "As a result," a second key (run 160).** "The documents
cannot supply such an account. ______ researchers are cross-reading other sources" let "As a result," attach to the limitation,
because a deliberate response can still be a result. For a purpose key ("To that end,"), put the GOAL sentence immediately
before the blank and move any limitation earlier.

**Transitions: an "Accordingly," blank sentence must not restate the premise (run 160).** A practice that literally embodies the
premise ("her editions print each song as a pitch cycle plus entry rule" after "a song is a procedure") made "That is,"
defensible. An earlier version with "less a fixed piece than a procedure" made "Instead," defensible. The item was discarded
after two FLAGs. The consequence has to be a downstream action that does not paraphrase or replace anything in the premise.

**Transitions: when a concession is followed by a return, name the anomaly in the blank sentence (run 160).** "______ landmark
binding remains the best account" let "Therefore," reattach to an earlier supporting sentence. Rewording to "______ the Tessarun
result does not displace landmark binding, which remains ..." tied the blank to the anomaly, and the item still calibrated Hard.

## Run 161 additions

**Transitions Hard: mandating only the two Hard relations works (run 161).** 8 abstract-register gens, each given a mandated key
and misreading set from the run-159/160 findings: 6 calibrated Hard (45-49%), and all 8 passed the critic on the first pass.
Concession-then-return was 4/4 Hard ("Even so," "Nevertheless," "Still," with a single quantitative anomaly right before the blank and
a blank sentence that names it and gives its own "because" reason distinct from the earlier support). "By extension," and "More broadly,"
were Hard. "Hence," was Hard when the prior "rather than" pseudo-contrast concerned a method and the consequence was two downstream
effects. Two items went Medium: "More generally," (~54%), where "in any ... tradition ... may" made the widening explicit and only one
distractor tempted, and "Thus," (~58%), a linear consequence whose sentence after the blank reinforced it. For a generalization key,
keep the scope jump implicit (no "any"/"all" right after the blank) and make two distractors tempting. For a consequence key, give it
two effects and let the pseudo-contrast carry the misreading.

## Run 162 additions

**Inferences Hard: the first two Hard items came from one shape (run 162).** 8 gens with mandated shapes under anti-cue rules
(key not longest, all choices equal length and equally hedged, two distractors fitting named misreadings). Both Hard items
(~47%, ~49%) were "received account undercut by THREE separate quiet details": a granary register (dialect, auditors count only
sacks, famine relief by recorded total regardless of family size) and bridge cutwaters (placement only above a raft boom, none at
an equal-current bridge below it, costly granite recut each spring). Each had an abstract key that names no single detail, a
distractor rescuing the received account, and a distractor fitting the most salient detail that only a quieter detail defeats.
The Transitions Hard relations did NOT transfer: concession-then-return (~66-68%) and implicit scope generalization (~57-66%) went
Medium because an Inferences stem has to lay out the mechanism and the confound. Single-literary-critic undercut readings with two
details (~54%) and "rather than" method consequences (~56%) also stayed Medium. For Inferences d3, mandate the three-detail
undercut-received-account shape in institutional/technological history, with one detail being an absence or contrast case.

**Inferences: a restatement distractor that is TRUE is a second key (run 162).** A "For example" misreading that restates the
finding the mechanism was proposed to explain (B: "explains why the children produce wrong plurals for rarely heard nouns") is a
true consequence of the mechanism, so it was defensible. Fix: make the restatement also limit scope ("applies only to plural nouns").

**Inferences: a key must name the passage's actual cause (run 162).** A sunbird key said "the abundance ... can raise the cost ...
even faster", but the passage attributed the intruder surge to a neighboring fig tree, not nectar abundance. Flagged.

**Inferences: a distractor that names the true "what" can still be tempting even with an overreach tail (run 162).** Pointed
cutwaters really do deflect logs, so "keep rafts moving" was partly defensible until a wear detail (points recut every spring) was
added to separate impact damage from passage of logs. When the key and a distractor share a real-world mechanism, add one passage
detail that only the key explains.

## Run 163 additions

**Inferences Hard: the three-detail undercut shape is now confirmed (run 163, 5 Hard of 8).** All 8 gens were mandated to the run-162
shape. Five calibrated Hard (~45-50%), three Medium (~52-57%). What separated them: Hard items had an abstract key whose decisive
support was a QUIET detail (a fair copy sent to accounts, councils paying to recut dies, a boundary road lit with no traffic), and each
distractor was defeated by a different detail. The Medium items had either a key that echoed an explicit passage phrase ("said nothing
about how much to take") or two distractors that each died on a single explicit sentence ("inspectors never checked what a bottle held").
Assign each generator a different subject area AND steer the key type (economic vs jurisdictional vs civic/status) so a wave of keys
does not all converge on "fees/revenue" (wave 1 of run 163 did).

**Inferences: a "by contrast" rival-killer must name what it contrasts with (run 163).** Two critics flagged a dangling "by contrast"
after a sentence about a different entity (e.g. "Highland inspectors, by contrast," directly after a sentence about the lowland post).
Use "meanwhile" or attach the contrast explicitly.

**Inferences: a co-occurrence-only key needs one positive link (run 163).** A millstone-notch key (notches encode the villages'
grinding order) rested only on Tarsen having both a fixed order and notches while Dovrel had neither; the critic called it a leap.
Adding "each stone bears exactly seven notches" (seven villages) gave a positive link and the item still calibrated ~50%.

**Inferences: a key that depends on an unstated premise about the target site is under-supported (run 163).** An apothecary item's key
(tint marks guild stock against unlicensed healers) required inferring that Marrowick HAD unlicensed healers from the fact that the
comparison city barred them. State the target-site side of any contrast explicitly.

## Run 164 additions

**Inferences Hard: steering away from economic keys still works (run 164, 3 Hard of 4 surviving).** Keys steered to labor-time
discipline (mill whistle, ~48%), institutional prestige (seed lists sent only to gardens already on the roll, ~46%) and donor
commemoration (chained books with givers' plates, ~50%) all reached Hard. The co-owner-identification key went Medium (~56%) because
the stem said "each household cutting a pattern of its own into its wheels", which nearly states the key.

**Inferences: an "it was already X before the signal" detail must show the THING the distractor names was already running (run 164).**
"Steam was already up twenty minutes before the first blast" did not kill "cue the engine room to start the machinery", because
raising steam normally precedes starting the engine. "The engine already turning twenty minutes before the first blast and running
on after the closing one" did.

**Inferences: a training/skill-transmission key competes with an inspection distractor (run 164, discarded item).** A proof sheet that
a journeyman marks with errors reads as quality control as easily as teaching. Two fixes in a row left inspection arguable. If you use
a training key, the passage must say whose work the marks were on AND that the object inspected was already approved.

**FSS Hard: the first Hard item came from a noun-clause subject (run 164, ~50%).** "That the copyists ... altered dozens of glosses
... to reconcile conflicting dialect forms ______ that ..." with choices suggest / to suggest / suggesting / suggests. The subject's
number is carried by no noun, plural nouns sit right before the blank, and the plural "suggest" sounds right by ear. Replacing a
second plural-verb distractor ("have suggested") with a non-finite one ("to suggest") follows the run-155 rule. Rules students know
by name stayed Medium even when the key sounds odd: mandative subjunctive "be moved" (~55%), "every X and every Y ... was" (~58%),
"had lain" (~60%). A collective noun with "whose members" before the blank went Easy (~80%).

## Run 165 additions

**FSS Hard: the noun-clause subject family is the one reliable Hard lever (run 165).** Run 164's "That ..." clause was joined by a
"Whether ..." clause (~52%, mangrove propagules "... ______ largely on" -> "depends") and a "How ..." clause with a present-perfect cue
in the main clause (~52%, "... ______ musicologists for more than a century now" -> "has divided"; distractors have divided / divided /
has been divided). Shapes that put a number-carrying noun at the head of the subject went Medium even when the noun was hidden:
gerund subject (~60%), "the only one of ... that" (~58%), fronted-adjective inversion (~58%), fraction + noncount noun (~58%), "to
whoever" (~56%). A one-person "the designer and chief engineer, [name]," compound subject went Easy (~85%), because the name gives it away.

**FSS: avoid "What"-clause subjects (run 165).** A free relative "What the engineers learned ... ______" was FLAGGED because "what" can be
notionally plural, so "have shaped" is defensible. Use That/Whether/How clauses, which are always singular.

**FSS: an infinitive subject invites a purpose-phrase parse (run 165).** "To reconstruct X ______ careful filtering" let "it requires"
stand as "To reconstruct X, it requires ..." (an expletive "it" with a fronted purpose phrase). A gerund subject removes that parse.

**FSS: a plural-form title alone is not a safe singular subject (run 165).** The critic defended a plural verb with "Letters from the
Salt Flats" read notionally as a set of letters. Adding a head noun ("book-length poem") fixes it, but that also makes the item Medium.

**FSS: limit the {plural lure, -ing participle, "it" + verb} distractor template (run 165).** Four of ten drafts converged on it, and the
calibrator called "it + verb" and the bare participle "obvious eliminations" every time. The two Hard items in this run used a tense
or voice distractor ("divided", "has been divided") or a plural lure that sounds right by ear. Also, "it + verb" after a fronted phrase
needs an explanation that names the dangling or unattached phrase, not only a "redundant subject".

## Run 166 additions

**FSS Hard: interrogative noun clauses plus a tense-locking time cue (run 166, 6 Hard of 8).** Why/Whether/When/How/Which-clause
subjects all reached Hard (~50-54%) when a cue fixed the tense ("ever since ... the 1950s", "since the 1930s", "Until ... was published
in 2020", "in the four centuries since") and a second distractor was a tense or voice error ("had puzzled", "has documented" with no
object). "Which of the three X ..." also works. A "That" clause went Medium once a second visible rule gave it away: "not only
explains ... but also ______" (parallelism, ~65%), or a plural complement after the blank ("among the chief reasons", ~58%).

**FSS: soft present cues leave the simple past defensible (run 166).** "Even today" let "was never settled" pass ("never solved, even
today"), and a fronted "In 2019," let "is the question the survey set out to answer" pass. Use a since-phrase or an until-clause, which
grammatically requires the perfect or the past.

**FSS: a sentence-initial "That + adjective + noun" reads as a demonstrative (run 166).** "That heavy snow slid off ... ______" let the
non-finite "being" stand as a trailing participle ("That heavy snow slid ..., being among the reasons"). With a That-clause subject,
make all four choices finite. Under the demonstrative parse every finite choice then fails, so only the noun-clause parse survives.

**FSS: "both" after an object pronoun creates a garden path (run 166).** "...before mordanting them both explains" reads as "them
both". Use "not only ... but also", or avoid the correlative.

## Run 167 additions

**FSS noun-clause subjects: a singular predicate noun after the blank gives the number away (run 167).** "Who carved the
figures ... ______ an open question for more than a century now" calibrated ~62%, because the singular complement "an open
question" signals a singular verb. Use a transitive predicate with a PLURAL object ("has puzzled archaeologists"). A
"Where"-clause with that fix still came out at ~58%: "Where ..." reads as one obvious unit. "Which of the three ..." and
"Whether ..." clauses remain the most reliable Hard shapes.

**Rhetorical Synthesis emphasis: "X, but Y" does not decide emphasis firmly enough to be a wrong answer (run 167).** A critic
defended "usefulness, but limitation" as acknowledging the limitation while emphasizing usefulness, because the sentence
LEADS with the usefulness. A strict mirror pair works: "Although [limitation], [usefulness]" (key) against
"Although [usefulness], [limitation]". Likewise, a trailing participle ("..., concluding that ...") can carry sentence-final
emphasis. Don't use it as the only failure of a rival that contains every goal element.

**Rhetorical Synthesis: "conditions" in a goal is ambiguous with procedural study conditions (run 167).** "Indicating the
conditions under which it was observed" let a scheduling and randomization rival count. Name what you mean: "the population
and setting in which the finding was observed". Avoid "applies to", which overstates what a study that tested one group shows.

**Rhetorical Synthesis Hard: the first Hard RS item came from a STANCE goal (run 167).** "Present the findings as a
qualification of, rather than a refutation of, X's hypothesis" calibrated ~50%. All four choices carried the same accurate
data and differed only in how they related it to the prior claim: contradict / consistent only under one condition (key) /
confirm / neutral report that includes the cause but takes no stance. Goals that name a structural element (a limitation, a
conclusion, conditions, interpretations, a cause) stayed Medium (55-74%) even with mirror-image rivals, because the key
can be found by checking which choice has the named element. Physical facts in dressed notes need a check too: fresh
pond water cannot stay liquid below 0 °C, so a sub-zero setting needs saline water.
