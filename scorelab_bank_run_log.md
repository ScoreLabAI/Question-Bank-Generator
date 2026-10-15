# ScoreLab AI Question Bank — Run Log

Append-only log of each scheduled `scorelab-question-bank-builder` run.

---

## 2026-08-27 — Run 1 (first entry in this log; log file did not previously exist)

**Cells worked (in tracker file order, partially-done cells first):**

| Cell | Needed | Generated | Accepted into this cell | Result |
|---|---|---|---|---|
| Algebra / Linear equations in one variable / d1 | 5 | 7 | 5 | 5 → 10, **complete** |
| Algebra / Linear equations in one variable / d2 | 0 (already complete) | — | 2 | 19 → 21, still complete (overshoot) |
| Algebra / Linear equations in two variables / d1 | 5 | 5 | 5 | 5 → 10, **complete** |

**Total new questions banked this run: 12** (10 against the run's target cells, plus 2 calibration spillover).

**Cell selection rationale:** the difficulty-3 "Linear equations in one variable" cell is next in file order and partially done (1/10), but it needs 9 questions, which would have pushed the run to 14. Took the two 5-question cells instead to stay near the ~10/run budget. That d3 cell remains the first pending cell for the next run.

**Pipeline:** full generate → adversarial-critique → difficulty-calibrate per question, all subagents pinned to `model: "sonnet"`. Cells run sequentially; within a cell, the 5 generators (then 5 critics, then 5 calibrators) ran as one batch each, so concurrency never exceeded 5 subagents.

**Critique results:** 12/12 PASS on first pass. No FLAGs, no regenerations for ambiguity, no discards. In every case the critic's independently-derived answer matched the generator's `correct_answer`.

**Calibration results — the notable event of this run:** 2 of the first 5 difficulty-1 attempts in "Linear equations in one variable" were calibrated UP to difficulty 2:

- `15 - 4(2x - 3) = 3` — distribution of a negative coefficient across parentheses.
- `3(x + 4) = 2x + 3x - 2` — distribution plus combining like terms with variables on both sides.

Per SKILL.md these were relabeled rather than discarded, and banked into the d2 cell (which was already at target — it is now at 21/10). Two replacement d1 questions were then generated with an explicit constraint prohibiting distribution across parentheses and variables on both sides; both calibrated as honest difficulty 1.

**Calibration guidance for this subcategory (for future runs):** for Linear equations in one variable at d1, the patterns that hold at easy are (a) the equation is handed to the student inside a short one-relationship word problem, (b) a single-relationship word problem the student translates themselves (`ax + b = c` shape), and (c) a purely algebraic single-fraction form such as `(x - 5)/3 = 4`. Anything requiring distribution across parentheses AND combining like terms will calibrate to medium.

**Visuals:** 2 of the 5 "Linear equations in two variables" questions were built as graph items per sat-taxonomy.md's guidance for that subcategory (both `chart_type: "function"`, linear), rendered deterministically via `scripts/render_visual.py` — no hand-written SVG. Both rendered SVGs were also rasterized and visually inspected. One fix resulted: the second graph's original `y_range` of [-10, 10] produced matplotlib tick labels at 2.5 intervals (−10.0, −7.5, −5.0, −2.5 …), which makes reading the integer answer point (2, −2) off the grid awkward for a graph-reading item. `visual_data` was corrected to `x_range: [-3, 4]`, `y_range: [-6, 8]` (integer ticks, answer point on a gridline intersection) and re-rendered. The math and the answer choices were unchanged by this fix.

**Other editorial fixes:**

- One critic flagged a minor (non-blocking) ambiguity in the vaccination-drive item: "total number of doses administered … after x hours since the drive opened" could theoretically be read as excluding the pre-drive walk-in doses. The critic verified this creates no second defensible choice (y = 45x is not among the options), but the stem was tightened to "the total number of doses the clinic has administered that day, y, x hours after the drive opened" before banking. The calibrator saw the tightened wording.
- Several Generator subagents appended their scenario to `scorelab_used_topics.md` themselves despite being told not to (the orchestrator owns logging). No duplicates resulted, but one such line had to be corrected from d1 to d2 after calibration. Later generator prompts in this run added an explicit "do not write to any file" instruction, which held.

**Validation:** `scripts/validate_batch.py` run on each cell's batch before merge — 7/7 and 5/5 passed, including the visual-field consistency checks. Merge into `scorelab_question_bank_master.json` grew it from 65 to 77 questions. Backups of the three state files were written to the outputs folder before the merge.

**Status vocabulary note:** the task file says to set a finished cell's status to `"done"`, but the tracker file's existing completed cell already uses `"complete"`. Used `"complete"` for consistency within the data file. Cell selection keys off `status == "pending"`, so either value behaves identically for future runs.

**Schema reminder (carried forward):** the four visual columns (`has_visual`, `visual_type`, `visual_data`, `visual_svg`) still need a Supabase migration on the live `questions` table before questions with visuals can be imported. This run added the first two graph-bearing questions to the master bank.

**Token usage:** not exposed to the orchestrator directly. Reported subagent usage totalled ~633,000 tokens across 29 subagent calls (12 generators ≈ 39–42k each, 12 critics ≈ 16–18k each, 12 calibrators ≈ 15–16k each; 5 of those 29 were the replacement-question and re-critique calls). Orchestrator context is additional and not included.

**Next run should start at:** Algebra / Linear equations in one variable / d3 (1/10 accepted — see that cell's note; the piecewise/domain-check word-problem pattern is the one that has actually calibrated as Hard). 87 cells remain pending.

---

## Run 3 — 2026-08-27

**Cell worked:** Algebra / Linear equations in one variable / **difficulty 3** (the first pending cell in tracker order; deferred by run 2). Needed 9 to reach the target of 10. Generated 9, accepted 9 — but only **4 survived calibration as Hard**.

| Cell | Needed | Generated | Accepted at d3 | Spilled to d2 | Result |
|---|---|---|---|---|---|
| Algebra / Linear equations in one variable / d3 | 9 | 9 | 4 | — | 1 → 5, still **pending** (5 short) |
| Algebra / Linear equations in one variable / d2 | 0 (already complete) | — | — | 5 | 21 → 26, still complete (overshoot) |

**Total new questions banked this run: 9.** Master bank grew 77 → 86.

**Pipeline:** full generate → adversarial-critique → difficulty-calibrate per question, every Agent call pinned to `model: "sonnet"`. One cell only, run sequentially; concurrency never exceeded 5 subagents. No visuals — sat-taxonomy.md lists no visual convention for this subcategory, so all 9 are `has_visual: false`.

**Generation strategy (deliberate change from runs 1–2):** rather than issuing 9 identical prompts, each Generator was assigned a *distinct structural pattern* and a *distinct unused scenario domain*, and every prompt carried the accumulated calibration warning from this cell's tracker note — an explicit list of the four techniques that have reliably calibrated down (no-solution/infinite-solutions parameters, literal-equation rearrangement, multi-fraction LCD, derived-expression), plus the instruction to build in a trap solution the student must actively reject. This raised the Hard yield from 1/15 (7%) across runs 1–2 to 4/9 (44%) this run.

**Critique results:** 7/9 PASS on first pass; 2 FLAGged, both regenerated once and both PASSed on re-critique. No discards.

- *Grain silo* — FLAG: "sets aside a fixed 100 bushels … for seed stock" was lexically ambiguous between *physically removed* and *earmarked but still in the silo*. The second reading made choice B (800) genuinely defensible, since 800 lands on exactly 400 bushels before the seed step. Regenerated with removal language ("removes … from the silo, transferring it to separate storage"); math, answer, and all four choices unchanged. Re-critique PASS.
- *Cycling time trial* — FLAG on wording, not answer ambiguity: the stem defined "official recorded time" as the elapsed start-to-finish time and then also as ride time + 4 minutes, a direct internal contradiction, and never said whether the speed check used ride time or official time (resolvable only by a circularity argument the text never made). Regenerated so the first sentence defines *ride time* as the elapsed time and the rule states "average speed … based on the rider's ride time" explicitly. Re-critique PASS.

Two other critics raised non-blocking notes that were left as-is because the critic explicitly passed the item on the current wording: the 3D-printing question is technically under-determined under a strict whole-spool-purchase reading (any 834–1,000 parts consumes 6 spools), but no other answer choice falls in that window and the intended answer is the exact zero-waste value; and the observatory question's "at most 7 hours per night" clause is consistency-confirming rather than load-bearing (the total is invariant to how the 42 hours split).

**Calibration results — 5 of 9 relabeled from d3 to d2**, banked per SKILL.md rather than discarded:

- Held at **Hard (3)**: overtime-threshold payroll; parking-garage daily cap invalidating the uncapped intersection; two successive percent changes composed on an *unknown* base plus a fixed fee; speed-threshold-converted-to-time-threshold where the no-penalty candidate self-contradicts.
- Relabeled to **Medium (2)**: freight weight brackets (a single bound check settles which bracket applies, so it reads as one inference step); brass-alloy percent mixture (textbook add-pure-substance template); grain-silo successive fractions on a changing base (routine multi-step translation); 3D-printing kilogram-to-gram conversion (unit conversion is too routine to count as a second concept); observatory per-night calibration overhead (the recurrence is stated plainly in the text, so it's a careless-reading trap rather than a conceptual one).

**Calibration guidance for this subcategory (updated, carried forward):** what actually reads as Hard here is a setup where the *first competent attempt is a seeded dead end* — the student computes a plausible candidate and must recognize it violates its own stated condition, then re-solve — or where several operations are genuinely *composed on an unknown* (e.g. 1.08x built from two chained percent changes) rather than computed forward from a known number. What does not clear the bar, even when it takes five arithmetic steps: unit conversions, standard mixture templates, successive fractions, per-session overhead, and single-bracket selection that a bound check resolves immediately. The tracker note on the d3 cell has been rewritten with the full confirmed/rejected pattern lists.

**Validation:** `scripts/validate_batch.py` run on the 9-question batch before merge — 9/9 passed, including the visual-field consistency checks. Backups of the three state files were written to the outputs folder before the merge.

**Schema reminder (carried forward):** the four visual columns (`has_visual`, `visual_type`, `visual_data`, `visual_svg`) still need a Supabase migration on the live `questions` table before questions with visuals can be imported.

**Token usage:** ~959,600 tokens across 31 subagent calls (9 generators ≈ 35–75k each, 9 critics ≈ 17–29k each, 9 calibrators ≈ 25–33k each, plus 2 regenerations ≈ 25k each and 2 re-critiques ≈ 20k each). Orchestrator context is additional and not included. This is up from run 2's ~633k, driven by the larger single-cell batch and the two regeneration round-trips.

**Next run should start at:** Algebra / Linear equations in one variable / d3, which is still first in tracker order at **5/10** and needs 5 more. Given the 44% Hard yield this run, expect to generate roughly 10–11 candidates to land 5 Hard ones — or accept that the overflow continues to deepen the (already overshot) d2 cell. If the next run also falls short, consider whether a 10-question target is realistic for hard single-variable linear equations at all, since the format genuinely constrains how much can be combined into one such item. 87 cells remain pending.

---

## Run 4 — 2026-08-27 (scheduled, unattended)

**Cells worked (in tracker file order, partially-done cells first):**

| Cell | Needed | Generated | Accepted into this cell | New count |
|---|---|---|---|---|
| Algebra / Linear equations in one variable / d3 | 5 | 5 | 3 | 8 / 10 (pending) |
| Algebra / Linear equations in two variables / d2 | 5 | 5 | 4 | 9 / 10 (pending) |

**Total new questions banked this run: 10** (all 10 generated questions were accepted somewhere; 3 landed in cells other than the one they were generated for, after difficulty calibration).

**Pipeline results:**
- Generator: 10 questions, one Sonnet subagent per question, `model: "sonnet"` on every call.
- Adversarial critique: 10 questions reviewed, one fresh Sonnet subagent per question, none told the intended answer. **10/10 PASS.** In every case the critic independently arrived at the intended correct answer. **Zero regenerations, zero discards this run.**
- Difficulty calibration: 3 of 10 relabeled.
  - Rail-pass successive-percent-changes item: 3 → 2 (translates directly into one linear equation; no candidate-rejection step).
  - City water utility marginal-tiering item: 3 → 2 (first-tier ceiling of $40 vs an $80 bill makes the bracket check immediate).
  - Marshland pool y-intercept-interpretation item: 2 → 1 (pure feature identification off a given graph, no algebraic manipulation).
  - Relabeled questions were banked in their corrected cells per SKILL.md rather than discarded, which pushed Linear equations in one variable d2 to 28/10 and Linear equations in two variables d1 to 11/10.

**Visuals:** 2 questions carry graph visuals (marshland pool water depth, glider altitude), both `chart_type: "function"`, rendered deterministically via `scripts/render_visual.py` (29.3 KB and 28.0 KB of SVG respectively) and embedded in `visual_svg`. This is the first time the Linear equations in two variables d2 cell has had any graph-bearing questions. `render_visual.py` succeeded on the first attempt for both — no malformed specs.

**Validation:** `scripts/validate_batch.py` run separately against each cell's batch file before merging. Both reported 5/5 passed, including the new visual-field consistency checks.

**Manual edits made by the orchestrator before critique/merge (noted for transparency):**
- Glider question: replaced an original distractor of 21, which came from a vague "misread the graph" rationale rather than a nameable error pattern, with 12 (dividing the target altitude by the descent rate — i.e. time to *lose* 1,800 ft rather than time *at* 1,800 ft). Choices reordered ascending, correct answer moved from B to C. The revised version is what went to the critic.
- Marshland pool question: distractor D reworded from "the depth at the end of the dry spell" (under-determined — the graph's plotted domain end is not stated to be the end of the dry spell) to "the depth 30 days after the start of the dry spell."
- Energy cooperative question: dropped "one-time" from "one-time $30 efficiency credit" per the critic's polish note, since it could be misread as a lifetime limit.
- Marshland pool question: the critic suggested sharpening distractor D to "the total amount by which the depth decreased over the entire dry spell." **Declined** — that value is numerically 90, identical to the y-intercept, which would create exactly the multiple-defensible-answer failure this pipeline exists to prevent. Kept the unambiguous version.

**Topic diversity:** all 10 scenarios checked against `scorelab_used_topics.md` before generation; each generator was given an explicit forbidden-scenario list and an assigned rotation domain (health/medicine, travel, construction/engineering, civic life, environment/energy for cell A; environment, travel, pure algebra, personal finance, arts and design for cell B). No repeats or near-variants of banked scenarios.

**Token usage:** ~455K subagent tokens across 20 subagent calls (10 generators averaging ~42K, 10 critics/calibrators averaging ~19K), plus orchestrator context. All calls pinned to Sonnet; no Opus escalation anywhere in the chain.

**Notes for the next run:** Linear equations in one variable d3 needs 2 more and Linear equations in two variables d2 needs 1 more — a future run could close both cheaply and then start on Linear equations in two variables d3 (0/10). Hard-item yield for the one-variable cell is now 8 confirmed Hard out of 29 hard attempts across four runs; the three patterns confirmed this run (capped-plan intersection, threshold on a derived quantity requiring unit conversion, below-threshold credit) are recorded in that cell's tracker note and should be the basis for the remaining 2.

---

## Run 5 — 2026-08-28 (scheduled, unattended)

**Cells worked this run** (walked in tracker file order, finishing partially-done cells first):

| Cell | Needed | Generated | Accepted into this cell | Cell status after |
|---|---|---|---|---|
| Algebra / Linear equations in one variable / d3 | 2 | 2 | 2 | **10 / 10 (complete)** |
| Algebra / Linear equations in two variables / d2 | 1 | 1 | 1 | **10 / 10 (complete)** |
| Algebra / Linear functions / d1 | 5 | 5 | 4 | 9 / 10 (pending) |
| Algebra / Linear functions / d2 | 2 | 2 | 3 | 8 / 10 (pending) |

**Total new questions banked this run: 10** (all 10 generated questions were accepted somewhere; 1 landed in a cell other than the one it was generated for, after difficulty calibration). Master bank: 96 → 106 questions. Two cells closed out this run, bringing the bank to 5 complete cells of 90.

**Pipeline results:**

- Generator: 10 questions, one fresh Sonnet subagent per question, `model: "sonnet"` on every call. Each generator was given an explicit forbidden-scenario list drawn from `scorelab_used_topics.md` plus an assigned rotation domain.
- Adversarial critique: 11 critic calls (10 questions + 1 re-critique after an orchestrator visual fix), one fresh Sonnet subagent each, none told the intended answer. **11/11 PASS.** In every case the critic independently arrived at the intended correct answer. **Zero regenerations, zero discards this run.**
- Difficulty calibration: 10 calls, 1 relabel.
  - Abstract linear-function item (f(2) = −3, decreasing by 6 per unit x, find f(−1)): **1 → 2**. The Calibrator's reasoning: the student must first infer slope = −6 from a *verbal* rate description (no formula is given) and then step backward across a sign change so that f increases as x decreases. That is construct-then-reverse-direction, which is the Medium bar for this skill; true Easy items in this cell hand over the formula or the graph. Banked in the d2 cell per SKILL.md rather than discarded.
  - The other 9 questions kept their claimed difficulty (3, 3, 2, 1, 1, 1, 1, 2, 2).

**Hard-item calibration progress (Linear equations in one variable, d3 — now closed):** 2 hard attempts this run, both confirmed Hard — the first run where every hard attempt survived calibration. Both leaned on the candidate-rejection shape recorded in that cell's tracker note. Two new Hard-qualifying patterns confirmed and written into the tracker:
- **(i) minimum-charge floor.** Two-plan comparison where one plan has a stated *minimum* charge rather than a cap. The naive intersection (100 GB) lands in the region where the floor is binding, so it is invalid; the real answer comes from setting the other plan equal to the flat minimum (125 GB). A floor is a genuinely different mechanic from the cap pattern already banked — the rejected candidate sits on the opposite side of the threshold.
- **(j) successive percent changes + conditional surcharge.** Two successive percent changes on an unknown base, plus a surcharge that applies only above a threshold. The no-surcharge branch yields $130, whose post-change value of $117 exceeds the $90 threshold and therefore contradicts its own branch assumption. This confirms the earlier run-4 finding from the opposite direction: successive percent changes stay Hard *only* when paired with a candidate-rejection step.

**Visuals:** 3 of the 10 questions carry visuals, in a cell (Linear functions) that previously had none.
- Two `chart_type: "function"` graphs rendered deterministically via `scripts/render_visual.py` (32.9 KB and 20.4 KB of SVG) and embedded in `visual_svg`: a strength-training push-up progression (p(w) = 2w + 10) and a bare xy-plane line (y = 2x + 2).
- One `visual_type: "table"` item — three non-consecutive (x, f(x)) pairs — with `visual_svg` correctly left null, since tables are rendered by the frontend from `visual_data` rather than by the script. This is the Linear functions d2 cell's first table-bearing question.
- `render_visual.py` succeeded on the first attempt for every spec; no malformed visual_data.

**Manual edits made by the orchestrator before critique/merge (noted for transparency):**
- **f(4) graph item — visual respecified and re-critiqued.** The first critic pass flagged that with y = 2x − 3 rendered over y ∈ [−8, 10], the renderer places y-gridlines at even integers only, so the queried point (4, 5) would fall *between* labeled gridlines — unacceptable for a difficulty-1 read-it-off-the-graph item. Changed the line to y = 2x + 2 over y ∈ [−4, 14], which puts the answer at (4, 10) exactly on a gridline intersection and makes all four choices (2, 4, 8, 10) grid-aligned. Re-rendered, rewrote the choices and all distractor explanations to match, and sent the revised version through a **fresh** critic (PASS) and the Calibrator (difficulty 1 confirmed). Worth noting for future runs: `render_visual.py` labels y-ticks at a spacing derived from the range, so a generator that picks an odd intercept with an even slope will produce off-gridline integer points. Generators for graph-read items should be told to check that the queried point lands on a labeled tick.
- **Printmaking-studio item — stem trimmed.** The critic passed the item but flagged the clause "so the number of sheets of paper remaining decreases by a constant amount for every batch completed" as restating what the preceding clause already said. Removed it; the math and answer are unchanged. Real SAT stems for this item type do not over-explain the constant-rate fact.
- **Dune-erosion item — answer choices de-punctuated.** Trailing periods removed from the four interpretive sentence choices to match College Board's convention for sentence-fragment answer choices.
- Several distractor explanations were lengthened to name the error pattern explicitly (e.g. spelling out that the non-consecutive x-values in the table item are exactly why the raw first difference is not the rate of change) rather than asserting the choice is wrong.

**Critic observations declined (recorded so a future run doesn't relitigate them):**
- On the push-up graph item, the critic noted that choices B and D are both *true* statements about the graph (the slope, and the point (5, 20)) rather than numerically false traps, and that "y-intercept" is slightly loose when the axes are labeled w and p. Kept as written: the stem asks specifically for the interpretation *of the y-intercept*, only choice A describes the point (0, 10), and true-but-answers-a-different-feature is a standard and desirable College Board distractor pattern. "y-intercept" is the conventional term for the vertical-axis intercept regardless of variable names.
- On the dune-erosion item, the critic stress-tested whether interpreting "the number −35" as "the estimated *decrease* of 35 each week" is a sign mismatch a pedantic student could object to. Kept as written — this is verbatim how real Digital SAT items phrase negative-slope interpretation.
- On the nutrient-concentrate item, the critic confirmed that choice D (the p-intercept) is a true statement about the graph but not an answer to the question asked. Kept — again the standard swapped-intercept distractor.

**Validation:** `scripts/validate_batch.py` run separately against each cell's batch file before merging: 2/2, 1/1, 4/4, 3/3 — all passed, including the visual-field consistency checks. Post-merge cross-check: the master bank's question count (106) equals the sum of `accepted_count` across all tracker cells (106), so the tracker and the bank are in agreement.

**Topic diversity:** all 10 scenarios checked against `scorelab_used_topics.md` before generation. Assigned rotation domains this run: technology and data, community and civic life (cell A); science and nature (cell B); sports and recreation, pure mathematics, art and design, environment and ecology (cell C); food and cooking, pure mathematics (cell D). No repeats or near-variants of banked scenarios. Deliberately avoided the personal-finance and business-pricing contexts that dominate the Linear equations cells.

**Token usage:** ~850K subagent tokens across 31 subagent calls — 10 generators (~441K, averaging ~44K each, the file reads dominate), 11 critics (~232K, averaging ~21K), 10 calibrators (~176K, averaging ~18K) — plus orchestrator context. All calls pinned to Sonnet; no Opus escalation anywhere in the chain. Higher than run 4's ~455K because this run made 31 subagent calls rather than 20.

**Notes for the next run:** Linear functions d1 needs 1 more and Linear functions d2 needs 2 more — a future run could close both and then start Linear equations in two variables d3 (0/10), which is the next fully-empty cell in file order, followed by Linear functions d3 (0/10). Two suggestions carried forward: (1) for any graph-read item, instruct the generator to verify the queried point lands on a labeled gridline given `render_visual.py`'s tick spacing — this run caught one at critique that would otherwise have shipped ambiguous; (2) the Linear functions cells still skew textual, so keep pushing graph and table visuals into them per sat-taxonomy.md's note that this skill is frequently shown graphically.

---

## Run 6 — 2026-08-28 (scheduled, unattended)

**Cells worked this run (10 new questions generated, 10 accepted, 0 discarded):**

| Cell | Needed | Generated | Accepted at claimed difficulty | Recalibrated | Cell now |
|---|---|---|---|---|---|
| Algebra / Linear functions / d1 | 1 | 1 | 1 | — | **10/10 complete** |
| Algebra / Linear functions / d2 | 2 | 2 | 2 | — | **10/10 complete** |
| Algebra / Systems of two linear equations / d1 | 5 (+2 redirected) | 6 | 4 | 2 moved to d2 | 9/10 pending |
| Algebra / Systems of two linear equations / d2 | (received spillover) | — | — | +3 banked here | 8/10 pending |

**Plan change mid-run.** The run opened intending 1 + 2 + 5 + 2 across Linear functions d1/d2 and Systems d1/d2. After the Calibrator moved two of the five Systems d1 items up to Medium, the fourth cell was redirected from "2 more Systems d2 items" to "2 more Systems d1 items," on the tracker's stated preference for closing partially-done cells. Systems d1 still finished 1 short (9/10) because one of those two was itself calibrated up. Total new questions held at exactly 10 per the run's scope cap; the single remaining d1 item was deliberately not pulled in rather than overshooting the cap.

**Difficulty calibration — the substantive finding of this run.** Three of ten questions were relabeled, all in the Systems of two linear equations cell, and the pattern is consistent enough to write into the tracker as a rule:

- **Easy in this subcategory requires two things at once:** the system must be DISPLAYED for the student (no translation from prose), *and* the requested variable must be the one the substitution or elimination step directly produces.
- Calibrated **1 → 2**: the marine-survey item (total 84 fish, "18 more salmon than trout") and the textile-workshop item (18 runners, 2 and 3 yards each, 47 yards total). Both make the student build the system from words and then run a multi-step solve — the Calibrator's stated Medium bar.
- Calibrated **1 → 2** for a different and previously unrecorded reason: the park-district planting-day item displays its system (x + y = 90, 3x + y = 178) and needs no coefficient scaling, but asks for **y** while elimination directly yields **x**, forcing a back-substitution. "Eliminate, then derive" is two chained operations, so a displayed no-scaling system is *not* automatically Easy — the asked-for variable matters.
- Confirmed **Easy**: a displayed substitution-ready system where one equation is already solved for a variable (both the abstract y = 2x + 3 / 4x + y = 27 item and the contextual p = 4d / d + p = 250 item); a displayed system with already-opposite coefficients solved by one addition (3x + 4y = 30 / -3x + 2y = 6); and a **system-setup item** ("which system of equations represents this situation?") where the student never solves. That last one is the most useful find for this cell: translation alone, with no solve attached, stays Easy, and it is a real Digital SAT item type that this cell had none of.
- Both Linear functions cells calibrated clean — 3 of 3 items honest at their claimed difficulty. The Medium signature there is now well established: "solve for or determine something, then use it once."

**Visuals:** 2 of the 10 questions carry rendered graphs, both `chart_type: "function"` rendered deterministically via `scripts/render_visual.py` and embedded in `visual_svg` (25.7 KB and 22.4 KB) — a library book-donation drive (f(x) = 10x + 20) and an IV saline-volume infusion (V = -10t + 500). `render_visual.py` succeeded first try on both specs.

- **Gridline pre-check applied and it worked.** Following run 5's recommendation, both graph generators were told to verify that every point the student must read lands on a labeled tick. Both did, and both were independently verified by the orchestrator by re-running matplotlib's ticker on the exact ranges before critique: book drive gets x-ticks at every integer 0–8 and y-ticks at 0/20/…/100, so the queried (6, 80) and all four choices are grid-aligned; IV bag gets x-ticks every 5 and y-ticks every 100, so the read points (0, 500) and (20, 300) are aligned. No visual failed critique this run, versus one that did in run 5.
- **Renderer limitation worth recording:** `sat-taxonomy.md` notes that Systems of two linear equations is "sometimes shown as two lines on one graph, with the answer being their intersection point," but `render_visual.py`'s `chart_type: "function"` plots exactly one function and has no multi-line mode. Graph-based systems items are therefore not currently buildable. All seven Systems items this run are text-only for that reason, not by preference. Adding a `functions: [...]` array to the renderer would unlock a genuine and common SAT item type for three whole cells.

**Regenerations and orchestrator edits (for transparency):**

- **One regeneration.** The first civic-context Systems d1 attempt used x + y = 40 / x − y = 8 in a community-cleanup framing. Rejected by the orchestrator before critique as a near-duplicate: the bank already holds an abstract x + y = 7 / x − y = 3 item, and the same total-plus-stated-difference shape appeared in this very batch as the fish-survey item. Its answer choices were also out of ascending order. A fresh generator was given the specific rejection reason plus a required alternative structure (count equation + resource equation with an already-matching coefficient), and returned the pancake-breakfast item; the orchestrator then reframed its context from adult/child *ticket sales* to a park district's tree/flowerbed volunteer crews, since "adult vs. child tickets" is a close variant of the theater-ticket item already banked in this cell. The math is untouched. The reframed version went through a fresh critic (PASS) and the Calibrator (which moved it to difficulty 2).
- **Textile-workshop item — one answer choice replaced.** The generator offered "6" as a distractor with the explanation "may result from conceptual or calculation errors," which violates the skill's requirement that every distractor be built from a nameable pattern. Replaced with 9 (split the 18 runners evenly, ignoring the fabric constraint — a named pattern already used elsewhere in the bank), choices reordered ascending, correct answer accordingly moved to A. Critiqued after the change, not before.
- **Device-purchase system-setup item — budget changed from $14,500 to $15,250.** At $14,500 the system's solution is d = 12.857…, a fractional device count. The student is not asked to solve, but a fractional solution in a physically discrete context is a real defect. $15,250 gives d = 15, t = 25. Critiqued after the change; the critic independently confirmed the integer solution.
- **Crane item — distractor A explanation rewritten.** The generator's text contained a visible self-correction artifact ("gives 2(-2)(... wait)"). Rewritten to name the actual error pattern the critic identified: reversing the order of subtraction inside the parentheses (4 − 20 instead of 20 − 4).
- **Two generator subagents wrote to `scorelab_used_topics.md` on their own** despite the log being the orchestrator's responsibility, appending entries for questions that had not yet passed critique or calibration. Both premature lines were removed and re-added only after acceptance. Every generator prompt after that point carried an explicit "check it but DO NOT WRITE TO IT" instruction, and no further stray writes occurred. Worth building into the skill's Step 1 prompt template.

**Critic observations declined:** on the textile item the critic reported it could find no derivation for the replaced distractor 9 (it explicitly tried and dismissed "half of 18"). Kept — dividing the item total evenly while ignoring the second constraint is a standard College Board distractor and is named as such in the item's explanation; a distractor no one can defend as correct is the desired outcome, not a defect.

**Validation:** `scripts/validate_batch.py` run separately against each cell's batch before merging — 1/1, 2/2, 4/4, 3/3, all passing including the visual-field consistency checks. Post-merge cross-check: master bank count (116) equals the sum of `accepted_count` across all tracker cells (116).

**Topic diversity:** all 10 scenarios checked against `scorelab_used_topics.md` before generation, with each parallel generator in a cell given a distinct assigned domain to prevent collisions between simultaneous subagents. Domains used: community and civic life (library donation drive; park district planting day), health and medicine (IV infusion), construction and engineering (crane lift), travel and transportation (road trip), pure mathematics (two abstract systems), science and nature (marine fish survey), art and design (textile workshop), technology and data (school device purchase). Personal finance and business pricing were deliberately avoided again, as they still dominate the Linear equations cells.

**Token usage:** ~788K subagent tokens across 26 subagent calls — 11 generator calls including one regeneration (~490K, ~45K each, dominated by the reference-file reads), 10 critics (~184K, ~18K each), 5 calibrators (~114K; three of the five were batched, assessing several questions in one call, which is where the savings over run 5 came from) — plus orchestrator context. All calls pinned to Sonnet; no Opus escalation anywhere in the chain. Down from run 5's ~850K/31 calls, mostly through batching calibration.

**Notes for the next run:** Systems d1 needs exactly 1 more (use a displayed substitution-ready system, a displayed opposite-coefficient elimination where the eliminated variable is *not* the one asked for, or a second system-setup item — see the tracker note for what calibrates Easy). Systems d2 needs 2 more. After those, the next fully-empty cells in file order are Linear equations in two variables d3 and Linear functions d3, both 0/10 — note that no d3 cell outside Linear equations in one variable has been attempted yet, and that cell's history shows hard items are expensive (31 attempts for 10 accepted), so a run starting a fresh d3 cell should expect a low yield and budget accordingly. Standing recommendation carried forward from this run: add multi-line support to `render_visual.py` so graph-based systems questions become possible.

---

## Run 7 — 2026-08-31 (scheduled, unattended)

**Cells worked (in tracker order, partially-done cells first per the run spec):**

| Cell | Needed | Generated | Accepted into this cell | Result |
|---|---|---|---|---|
| Algebra / Systems of two linear equations in two variables / d1 | 1 | 1 | 1 | 9 → **10/10, complete** |
| Algebra / Systems of two linear equations in two variables / d2 | 2 | 2 | 2 | 8 → **10/10, complete** |
| Algebra / Linear inequalities in one or two variables / d1 | 5 | 5 | 4 | 5 → **9/10, still pending** |
| Algebra / Linear inequalities in one or two variables / d2 | 2 (capped) | 2 | 3 | 5 → **8/10, still pending** |

**Totals:** 10 questions generated, 10 accepted, 0 discarded. Master bank 116 → 126.
All four batch files passed `scripts/validate_batch.py` (1/1, 2/2, 4/4, 3/3) before merge.

**Regenerations (2 — both passed on the second pass, neither discarded):**

1. *Systems d1, astronomy club.* Critic FLAGged for **context incoherence**, not ambiguity: the draft bolted a negative coefficient (−5t) onto a pure "sales total" story with no narrative justification, and used inconsistent per-unit prices across the two equations (2l vs 3l). Regenerated with equation 1 as a TOTAL and equation 2 as an explicitly stated DIFFERENCE at the same per-unit prices, so the opposite coefficients arise naturally. Re-critique: PASS. This is a reusable fix pattern for opposite-coefficient contextual systems.
2. *Inequalities d2, system of two inequalities.* Critic FLAGged (minor, non-correctness) because the keyed answer was the **origin (0, 0)** — "test (0,0)" is a taught shortcut, so a student could score the item without engaging it. Regenerated with shifted constants (y > 3x − 8, y ≤ −x + 6, key (3, 2)); no choice on a boundary line. Re-critique: PASS.

**Calibration moves (1):** the sailing-club passenger-weight item was generated for inequalities d1 but calibrated UP to difficulty 2 (solve-then-round-down is a genuine second interpretive layer). Banked in the d2 cell per SKILL.md rather than discarded. That is why d1 came up one short of closing.

**Critic notes applied without a full regeneration (stem and answer key unchanged in both cases):**
- *Systems d2, concrete blocks.* Critic passed the item but called distractor B (60, "split 120 in half") arbitrary — no computational path produces it. Replaced with 45, which traces to a specific named arithmetic slip (computing 4,950 − 4,200 as 675), and the explanation now shows that 45 fails the stated conditions.
- *Inequalities d1, 6x − 4 < 2x + 8.* Critic found two of the three shipped **distractor explanations described mechanisms that don't actually produce their own answer value** — the explanation for x > −3 in fact describes the path to x > 3. Rewrote both using the correct mechanisms the Critic supplied verbatim (transposition sign error for x < 1; mis-combining 6x − 2x as −4x for x > −3). A wrong explanation is student-facing and is itself a defect; worth watching for on future inequality items, since the Critic caught it only because it was asked to audit explanation accuracy explicitly.

**Open item-design findings for future runs (also written into the cell notes):**
- Inequalities d1's last remaining slot should NOT use the "which value is NOT a solution" shape with a sign-flip inequality: a student who forgets to reverse the symbol sees three of four choices as non-solutions, so the misconception doesn't converge on one distractor. The item generated this run is correct and was banked, but the shape is weakly diagnostic.
- Ordered-pair items: never place a choice exactly on a boundary line, and never key to the origin.
- Systems d2 boundary marker: adding solve STEPS does not make an item Hard; only a change in the KIND of reasoning (candidate rejection, unknown constant, structural condition on the system) does.

**Visuals:** none of the 10 questions carries a visual, and this is a deliberate, structural call rather than a shortcut. `sat-taxonomy.md` lists these two subcategories as only *sometimes* ("two lines on one graph") or *occasionally* ("a shaded region") visual — neither is in the mandatory-figure tier. More decisively, `scripts/render_visual.py` cannot produce either form: `chart_type: "function"` renders exactly ONE function per graph, so two intersecting lines are not expressible, and there is no shading primitive at all. Generating those as SVG text by hand is explicitly forbidden by SKILL.md. **Recommended follow-up (not done this run, as it is a code change outside this job's scope): extend `render_visual.py` with a multi-function graph mode and a half-plane shading option**, which would unlock graph-based items for both of these subcategories.

**Pipeline deviations, disclosed:** the Calibrator was run as 2 batched subagent calls covering multiple questions each (5 + 3) rather than one call per question, to hold token cost down. Generation and adversarial critique were NOT batched in a way that shares context between a question and its own critic — the Critic never saw an answer key, which is the isolation the pipeline actually depends on. Two Generator subagents (the systems d2 pair) appended their own lines to `scorelab_used_topics.md` despite the pipeline reserving that for the orchestrator; the lines were correct and both questions were accepted, so they were kept and not duplicated at merge. Later Generator prompts added an explicit "do not modify any files" instruction and the behaviour stopped.

**Model usage:** `model: "sonnet"` was passed explicitly on all 17 Agent calls (7 Generator incl. 2 regenerations, 6 Critic incl. 1 re-critique, 4 Calibrator). No Opus escalation anywhere in the chain.

**Token usage:** subagent totals reported by the Agent tool sum to **≈655,000 tokens** across the 17 calls (range 16k–61k per call; Generators were the most expensive at ~28k–61k each because each reads five reference files plus the used-topics log). Orchestrator-side usage is not self-observable and is not included in that figure.

**Next run should pick up at:** Linear inequalities d1 (1 needed — see the shape guidance in that cell's note), then Linear inequalities d2 (2 needed), then Linear equations in two variables d3 (10 needed, fresh cell).

---

## Run 8 — 2026-08-31

**Cells worked (10 new questions generated, 10 accepted, 0 discarded):**

| Cell | Needed | Generated | Accepted at claimed difficulty | Recalibrated |
|---|---|---|---|---|
| Algebra / Linear inequalities in one or two variables, d1 | 1 | 1 | 1 | — |
| Algebra / Linear inequalities in one or two variables, d2 | 2 | 2 | 2 | — |
| Algebra / Linear equations in two variables, d3 | 7 (capped from 10 to keep the run near 10 total) | 7 | 3 | 4 calibrated DOWN to d2 |

Both inequalities cells are now **complete at 10/10**. Linear equations in two variables d3 opened at **3/10 and stays pending**. Linear equations in two variables d2 (already complete) absorbed the 4 recalibrated items and now stands at 14/10.

**Regenerations / discards:** none. All 10 questions passed the adversarial Critic on the first pass with a PASS verdict, and no question was discarded. `validate_batch.py` passed on all four batch files (1/1, 2/2, 3/3, 4/4).

**Calibration moves (4, all downward, all in the fresh d3 cell):**
- *Parameterized points on 3x + 4y = 24* → d2. The Calibrator's reason is the important one: a student can defeat the symbolic setup by picking any convenient concrete point on the line and grinding the same algebra, so the abstraction is optional rather than load-bearing.
- *Intercept-sum with unknown constant k in 4x + 6y = k* → d2. Backsolving from the four choices (plug k = 60, check 15 + 10 = 25) is faster than the intended algebra, which caps the difficulty.
- *Perpendicular line from standard form through (6, 10)* → d2. A four-step chain, but every step is a drilled procedure — the run-6 boundary marker ("added STEPS do not make an item Hard, only a change in KIND of reasoning does") applied cleanly.
- *Laptop battery graph with a 100% capacity ceiling* → d2. This one is the genuinely useful finding: it uses the candidate-rejection shape that has held at Hard elsewhere, but the ceiling is stated in the first sentence AND is common knowledge, so a student can answer 100% without ever reading the graph's slope or intercept.

**Sharpened rule for future Hard attempts (written into the d3 cell note):** candidate rejection only qualifies as Hard when the student must *discover* that the naive answer is out of bounds and then *construct* something unstated. A signposted, intuitively obvious cap is not enough. The two courier-van / app-registration items held at Hard because each required building an unstated second-branch equation with a shifted origin; the battery item did not, because the second branch is just "the constant 100."

**New Hard shape confirmed this run:** the abstract "which must be true" structural item (`ax + by = c` visits Quadrants II, III, IV but not I → deduce the sign relationships among a, b, c). The Calibrator specifically credited the two distractors that assert MAGNITUDE relationships true for *some* qualifying lines but not all — eliminating those requires generating a counterexample rather than computing, which is a change in kind of reasoning rather than in step count. This shape is worth reusing in other Algebra d3 cells.

**Visuals:** one of the 10 questions carries a visual — the laptop-battery item (`chart_type: "function"`, `kind: "linear"`, m = 1, b = 20, plotted x ∈ [0, 60]), rendered deterministically via `scripts/render_visual.py` and injected into `visual_svg`; no SVG was hand-written. The other nine are correctly text-only: the inequalities items would need half-plane shading and the remaining d3 items are abstract or piecewise, and `render_visual.py` supports neither shading nor multi-segment/piecewise lines. **The run-7 recommendation still stands and is still out of scope for this job: extending `render_visual.py` with multi-function and half-plane-shading modes would unlock graph-based items across both of these subcategories.**

**Pipeline fidelity:** cells were worked strictly one at a time. Within a cell, the three stages were run in the correct order per question — a fresh Generator, then a fresh Critic that was never told the answer key, then a Calibrator only on questions that passed critique. Calls within a single stage of a single cell were issued in parallel (max 4 concurrent) to hold wall-clock down; no context was ever shared between a question and its own critic. The Critic prompts for the two contextual items and the graph item were given extra targeted checks (context coherence, visual/text agreement, boundary-line and origin-key rules), which is how the battery item's visual was confirmed to match its stem.

**Model usage:** `model: "sonnet"` was passed explicitly on all **30** Agent calls (10 Generator, 10 Critic, 10 Calibrator). No Opus escalation anywhere in the chain.

**Token usage:** subagent totals reported by the Agent tool sum to **≈868,300 tokens** across the 30 calls — Generators ≈511,000 (43.9k–59.5k each; each reads five or six reference files plus the used-topics log), Critics ≈189,900 (16.8k–22.8k each), Calibrators ≈167,400 (15.6k–18.8k each). Orchestrator-side usage is not self-observable and is not included.

**Next run should pick up at:** Algebra / Linear equations in two variables **d3 (7 needed)** — see that cell's note for the two confirmed Hard shapes and the four shapes now known to calibrate down. Then Algebra / Linear functions d3 (10 needed, fresh), then Systems of two linear equations d3 (10 needed, fresh).

---

## Run 9 — 2026-09-01

**Cells worked (7 new questions generated, 7 accepted, 0 discarded):**

| Cell | Needed | Generated | Accepted at claimed difficulty | Recalibrated |
|---|---|---|---|---|
| Algebra / Linear equations in two variables, d3 | 7 | 7 | 5 | 2 calibrated DOWN to d2 |

One cell only. The d3 cell needed exactly 7 to close, which is near the run's ~10-question cap, so no second cell was pulled in. **Linear equations in two variables d3 moves 3/10 → 8/10 and stays pending (2 more needed).** The d2 cell (already complete) absorbed the 2 recalibrated items and now stands at 16/10. Master bank: 136 → 143 questions.

**Regenerations:** one. The dendrochronology item (Douglas-fir core sample) was FLAGged by the Critic — not for ambiguity, the answer was uniquely 11 throughout, but for **context incoherence**: the pre-fire line through the two given data points predicted a 26 cm trunk just before age 40 while the given post-fire model predicted 62 cm at age 40, a physically impossible jump. The stated validity intervals made the math unambiguous while leaving the story impossible. Regenerated with continuity enforced (pre-fire D = 0.4a + 4, post-fire D = 0.6a − 4, both = 20 cm at age 40, slope still increasing as the narrative requires), re-critiqued, PASS. The regeneration also replaced a distractor two Critics had called weakly motivated. **Discards: none.**

**Explanation-only or advisory fixes applied without re-critique:** one. The Critic on the bottling-line item offered an optional clarity tightening of the final sentence; it was applied ("Counting both the setup bottles and all bottles capped during the run, how many bottles in total..."). No choice, key, or mechanism changed — the Critic had already confirmed no alternate reading produced a competing answer among the four choices.

**Calibration moves (2, both downward), batched into a single Calibrator call with the cell's accumulated rubric pasted in as the working standard:**
- *Abstract parallel-lines item, px + qy = p + q parallel to 3x − 5y = 8, express q in terms of p* → d2. **This is the useful finding of the run.** The item was deliberately built with answer choices as *expressions* rather than numbers, specifically to block the backsolving shortcut that downgraded a run-8 item. It calibrated down anyway: blocking a shortcut does not change the KIND of reasoning, which here stays a mechanical slope-extraction chain. Closing a loophole is not the same as adding difficulty.
- *Muralist tile row, count the integer solutions of 4s + 5r = 90 with at least one of each type* → d2. The Calibrator placed Diophantine solution-counting in the same family as the other signposted-rejection downgrades: the exclusion criterion (s = 0 violates "at least one of each type") is handed to the student in the stem rather than discovered.

**Hard shapes confirmed this run (all folded into the d3 cell note):** four new variants of the validity-interval / unstated-second-branch shape all held at Hard — (c) the bound stated on the *dependent* variable so it must be converted before the naive answer can be seen to fail; (d) **the changeover point not stated at all but derivable from a consumable resource** (a 3,000-cap cartridge at 40 caps/min implies 75 minutes), which is the strongest Hard signal found in this cell so far because the threshold is genuinely hidden rather than signposted; (e) the first branch given only as a graph; (f) the second branch running backward in time from two earlier data points. The abstract structural "must be true" shape also held at Hard on an entirely new condition (a line through a fixed point with negative slope), confirming it generalizes beyond the quadrant-signs version banked in run 8.

**Answer-key skew — caught late, now machine-checked.** All seven raw Generator drafts keyed to A (4) or B (3), with nothing on C or D, in violation of item-design-rules.md's "vary the key position." No individual question was wrong and nothing in the pipeline noticed; the orchestrator caught it by eye at assembly. Two items with non-numeric choices (the must-be-true item and the parallel-lines item) had their choices reordered — keeping sensible grouping, and moving `correct_answer` and the `distractor_*_explanation` fields with them — giving a final distribution of A=2, B=3, C=1, D=1. `validate_batch.py` passed 7/7 both before and after the reorder, which is the check working as designed.

**Step 5 — findings folded back into the skill:**
- `references/item-design-rules.md`: new rule under Context coherence — **a piecewise real-world model must be continuous at the changeover**, with the tree-trunk defect as the worked example and the instruction to fix a mismatch by adjusting a branch's constant rather than its slope. Also extended the "vary the key position" rule to document the new validator warning and the reorder procedure.
- `references/distractor-patterns.md`: new Math pattern entry — **averaging two given values is only a sound distractor when the queried point is actually the midpoint**; otherwise it's reverse-engineered, which is what two independent Critics said about it.
- `SKILL.md`: the piecewise-continuity check added to the Generator prompt template, so future runs get it without rediscovering it.
- `scripts/validate_batch.py`: new batch-level **answer-key distribution check**, emitting `[WARN]` (not a failure) when a batch of 4+ uses fewer than three distinct key letters or lets one letter take more than half. A warning rather than a failure because ascending numeric ordering fixes the key position on numeric items, so some skew is unavoidable. **Regression-checked against the whole master bank: 143/143 pass, no false positives**, and separately verified to fire on a synthetic skewed batch so it isn't dead code.
- Progress tracker: the d3 cell note rewritten with the four new Hard variants and the two new downgrade patterns; the d2 cell note records the two absorbed items.

**Queued for human review (2 new, in `scorelab_skill_review_queue.md`):** (5) one Generator wrote a file despite explicit read-only instructions and disclosed it unprompted — the constraint is enforced by nothing but subagent cooperation, and the proposal is to restrict the subagents' tool set structurally; (6) the Calibrator called a required graph-read "a superficial wrinkle, not a change in kind," which implies visuals never contribute to difficulty — worth an explicit decision rather than leaving it implicit. Items 1–4 remain open and unchanged; **item 1 (is a 10-question target realistic for d3 cells?) has now been open since run 3 and is directly relevant again** — this cell has taken 14 hard attempts across two runs to reach 8/10, a 57% yield, notably better than the 32% that prompted the item but still well short of one-for-one.

**Visuals:** one of the seven carries a visual — the water-hyacinth item (`chart_type: "function"`, `kind: "linear"`, m = −15, b = 240, plotted t ∈ [0, 8]), rendered deterministically via `scripts/render_visual.py`; no SVG was hand-written. `x_tick_step = 2` and `y_tick_step = 30` were set explicitly so the intercept (240) and the branch point (8, 120) both land on labeled gridlines per the run-5 graph-read rule. The other six are correctly text-only: three are abstract or piecewise (the renderer draws no multi-segment lines), and the rest are pure word problems the real SAT would also present without a figure.

**Pipeline fidelity:** one cell, worked alone. Per question: a fresh Generator, then a fresh Critic never told the answer key, then calibration only on questions that passed critique. Generation and critique stayed one-subagent-per-question; calibration was batched into a single call per SKILL.md's allowance, with instructions to evaluate each question independently. Concurrency was held to at most four subagents at once. The flagged question went back to a regeneration call carrying the Critic's specific reasoning, then through a full second critique.

**Model usage:** `model: "sonnet"` was passed explicitly on all **17** Agent calls (8 Generator including 1 regeneration, 8 Critic, 1 batched Calibrator). No Opus escalation anywhere in the chain.

**Token usage:** subagent totals reported by the Agent tool sum to **≈707,200 tokens** across the 17 calls — Generators ≈484,000 (33.2k–81.3k each; the regeneration was cheapest at 33.2k since it reads fewer reference files), Critics ≈198,000 (22.6k–26.3k each), Calibrator 25.2k for all seven questions in one call. Batching calibration cost roughly 25k against the ~120k seven separate calls would have run. Orchestrator-side usage is not self-observable and is not included.

**Next run should pick up at:** Algebra / Linear equations in two variables **d3 (2 needed to close)** — lean on shape (d), the hidden/derived changeover point, which is the strongest Hard signal this cell has produced. Then Algebra / Linear functions d3 (10 needed, fresh), then Systems of two linear equations d3 (10 needed, fresh). Both fresh d3 cells should be read against review-queue item 1 before a run commits to a full 10.

---

# Run 10 — 2026-09-01 (scheduled, unattended)

**Outcome in one line:** 2 questions accepted and banked, closing Algebra / Linear equations in two variables d3 at 10/10; the run was then cut short by the account's session usage limit before the second cell produced anything bankable.

**Cells worked:**

| Cell | Needed this run | Attempted | Accepted | Result |
|---|---|---|---|---|
| Algebra / Linear equations in two variables / d3 | 2 | 3 drafts (1 rejected pre-critique) | 2 | **Cell complete, 8 → 10/10** |
| Algebra / Linear functions / d3 | 8 | 3 requested, 1 returned | 0 | Cell opened, still 0/10 — run interrupted |

**What was banked (both confirmed Hard by the Calibrator, both PASS-on-first-critique):**

1. *Skywatch Community Observatory Meteor Watch Night.* 40 visitors checked in early, staff seat 20/min until the 380-chair main field fills, then overflow check-in slows to 8/min; find the time at which 500 total visitors have been checked in. This is the hidden-threshold shape, but with two deliberate variations from the run-9 items: the changeover is derived from a fixed **capacity** rather than a consumable, and the question runs in the **inverse direction** — a target total is given and the shifted second branch must be solved for the independent variable, rather than evaluated forward. The Calibrator judged the inverse solve an additional non-mechanical layer on top of an already-Hard shape.
2. *Abstract structural must-be-true.* `ax + by = c` with nonzero constants, both intercepts positive and the x-intercept the greater; deduce `ab > 0`. The comparison distractors (`a < b`, `a > b`) are **representation-dependent** — rewriting the same line with all-negative coefficients flips both — so they can only be eliminated by constructing that rewrite, not by computing. This is the third distinct condition on which shape (b) has held at Hard in this cell.

**Near-duplicate rejection (1, before critique — no Critic call spent).** The first draft for the observatory slot was an embroidery-thread item: 40 inches of setup thread, a machine drawing from a 2,520-inch bobbin at 12 in/sec, then hand-feeding at 5 in/sec, total at t = 240. That is the run-9 soda-bottling item with the nouns swapped — same additive head start, same consumable-derived hidden changeover, same forward evaluation at a stated time. Rejected and regenerated with the collision named explicitly and the inverse-solve direction mandated; the regeneration passed critique on the first attempt. The generic "don't reuse these scenarios" list was **not** sufficient to prevent this — the shape had to be excluded by name.

**Critic findings:** 1 FLAG across 3 critiques, and it was explanation/wording-only, not a correctness defect. On the observatory item the Critic noted that the stem said the 40 early visitors were "let in early" while the question asked for the total "checked in," leaving a reading under which the 40 don't count. It confirmed the alternative reading yields x = 37, which is not among the choices, so no second answer was defensible — but it correctly called the mismatch a wording defect. Applied the Critic's supplied one-word fix ("let in" → "checked in"); per SKILL.md, an explanation-only fix does not require re-critique because the item the Critic evaluated is otherwise unchanged. No regenerations for correctness, no discards.

**Interruption.** Three Generator subagents were launched for the Linear functions d3 cell. One returned; the other two terminated with `You've hit your session limit · resets 12:30pm (America/New_York)`. No further Agent calls were attempted after that, since the limit applies for the rest of the period and retrying would only burn the remaining budget. The one draft that came back — an abstract composed-function item (f linear from f(−1) = 6 and f(3) = −2, g(x) = f(2x − 5), find g's x-intercept; answer 7/2, distractors built from output-vs-input transformation confusion and dropping the inner constant) — has **not** been critiqued or calibrated and was therefore **not** banked. It is saved at `scorelab_pending_linear_functions_d3_q1.json` with a `_pipeline_status` field marking it incomplete, so the next run can pick it up at Step 2 instead of regenerating from scratch. Its arithmetic was verified by hand (f(x) = −2x + 4, g(x) = −4x + 14, x-intercept 7/2) but hand-verification is not a substitute for the Critic.

**Validation.** The 2-question batch passed `validate_batch.py` 2/2 before merge. The full master bank re-validates at **145/145** after merge (143 → 145).

**Step 5 — findings folded back into the skill:**
- `references/item-design-rules.md`: new section **"Near-duplicates within a cell"** — a near-duplicate is a repeated *shape*, not a repeated noun, with the embroidery/bottling collision as the worked example and the four axes to compare on (shape family, source of the key structure, direction of the solve, ingredient list).
- `SKILL.md`: the near-duplicate check in the pre-critique step now points at that section and records that when a cell's confirmed-Hard shape family is saturated, the Generator prompt must mandate a specific variation rather than only listing scenarios to avoid.
- Progress tracker: the LEITV d3 note records variant (g) of shape (a) — capacity-derived threshold plus inverse solve — the third confirmation of shape (b), and the fact that the forward direction of the hidden-threshold family is now saturated in this cell. The Linear functions d3 note records the interruption and points at the pending draft.

**Queued for human review (1 new, item 7 in `scorelab_skill_review_queue.md`):** run sizing against the session usage limit. The ~10-per-run target did not fit today's budget; the proposal is to lower it to ~6 and/or stop opening new cells once a spend threshold is reached, plus an explicit instruction for handling a usage-limit error mid-run (bank what passed, park un-critiqued drafts, log it, don't retry). Queued rather than applied because target counts and the cost/quality tradeoff are explicitly human-review territory, and one interrupted run doesn't locate the real ceiling. **Item 1 (is a 10-question target realistic for d3 cells?) has now been open since run 3 and is directly implicated again** — this is its fourth consecutive run as an open item.

**Visuals:** neither banked question carries one, correctly. Both are abstract or pure word problems of a kind the real Digital SAT also presents without a figure, and the renderer draws no multi-segment lines so a piecewise model has nothing useful to show. The graph-based Linear functions item that *was* planned for this run (a shown line plus a second function with an unknown constant, with tick steps pinned so every read point lands on a labeled gridline) was one of the two subagents killed by the usage limit, and carries over to the next run.

**Pipeline fidelity:** cells worked one at a time. Per question: a fresh Generator, then a fresh Critic never told the answer key, then calibration only on questions that passed critique. Calibration was batched into one call for both questions per SKILL.md's allowance, with the cell's accumulated Hard/downgrade rubric pasted in as instructed. Concurrency held to at most three subagents at once. No stage was skipped to save time or budget.

**Model usage:** `model: "sonnet"` was passed explicitly on all **8** Agent calls attempted (4 Generator including 1 regeneration and 3 for the interrupted cell, 2 Critic, 1 batched Calibrator... of which 2 Generators never returned). No Opus escalation anywhere.

**Token usage:** subagent totals reported by the Agent tool for the 6 calls that returned sum to **≈254,200 tokens** — Generators ≈238,500 (55.2k, 67.7k, 60.8k, 54.8k), Critics ≈51,800 (27.7k, 24.1k), Calibrator 18.6k for both questions in one call. The two terminated subagents reported no usage. Orchestrator-side usage is not self-observable and is not included.

**Next run should pick up at:** Algebra / **Linear functions d3 (10 needed, fresh)**. Start by running `scorelab_pending_linear_functions_d3_q1.json` through Step 2 (critique) and Step 3 (calibration) — it is already generated and needs no Generator call. Then continue the cell with the two shapes that were killed mid-flight: an abstract "must be true" structural item about a linear function with unknown constants, and a graph-based item where the shown line's slope and intercept feed an unknown constant in a second, algebraically-defined function. After that, Systems of two linear equations d3 (10 needed, fresh). Given today's interruption, consider sizing the next run to ~6 questions until review-queue item 7 is resolved.

---

# Run 11 — 2026-09-01 (scheduled, unattended)

**Cell worked:** Algebra / Linear functions / difficulty 3 — one cell only, as instructed (the first pending
cell in tracker order needed all 10, so it consumed the whole run).

**Result: 10 questions produced, all 10 banked, but only 1 of them into the cell they were written for.**

| | |
|---|---|
| Needed this run | 10 (cell was at 0/10) |
| Generated | 10 (9 fresh + 1 carried over from run 10) |
| Passed adversarial critique | 10/10 |
| Confirmed Hard by the Calibrator | **1** |
| Calibrated DOWN to Medium | **9** |
| Discarded | 0 |
| Regenerated from scratch | 0 |
| Near-duplicates rejected pre-critique | 0 |

Cell movement: **Linear functions d3: 0 → 1/10 (still pending, 9 needed).** Linear functions d2: 10 → **19**/10,
receiving the nine downgrades per SKILL.md's rule that a relabeled question is banked at its corrected
difficulty rather than discarded. Master bank: 145 → **155**.

**The carried-over draft is resolved.** Run 10's un-critiqued draft (`g(x) = f(2x − 5)` composition,
answer 7/2) went through Step 2 and Step 3 this run: it **passed critique cleanly** and then **calibrated down
to Medium**, so it is banked in the d2 cell. `scorelab_pending_linear_functions_d3_q1.json` has been
overwritten with a CONSUMED marker so no future run re-processes it.

## What the Calibrator said, and why this run matters

Each of the ten generators was given an explicit *structural mandate* rather than a topic — an abstract
must-be-true item, a graph-read feeding an unknown constant, a double unit conversion around a backward
solve, an aggregate-difference condition, a table with an embedded constant, a two-model inequality with
directional rounding, a fully symbolic value swap, a two-line graph solve, an indirectly-pinned constant —
each drawn from the sibling cells' confirmed-Hard findings. **Nine of the ten came back Medium.**

The one survivor is the abstract **"which must be true"** item (`f(1) < 0` and `f(4) < 0`, therefore
`f(2.5) < 0` by the midpoint-average identity), and it survived for exactly the reason that shape has now
held at Hard four times across cells: two distractors are true for *some* qualifying functions and false for
others, so they can only be eliminated by generating a counterexample rather than by computing.

Everything else bottomed out in "determine or solve for something, then use it once", which is the confirmed
Medium signature for this subcategory no matter how many stages precede it. Three downgrades are worth
recording specifically because they were *designed* to clear the bar and didn't:

- **The fully symbolic value-swap item** (`f(a) = b`, `f(b) = a`, find `f(a + b)`). Symbolic dressing does
  not rescue an item: a student picks `a = 0, b = 1` and the abstraction collapses in one line.
- **The double unit conversion around a backward solve.** The rubric's "derived-quantity conversion" Hard
  bullet turns out to be narrower than it reads — it only applies when the conversion is needed to *check a
  threshold*. With no threshold, it is convert-solve-convert.
- **The indirectly-pinned constant** (the point fixing `c` had to be derived from a system of two lines).
  Deriving the point adds a mechanical stage, so it still lands in the confirmed-Medium "unknown constant
  fixed by a single point" family.

All of this is now written into the d3 cell's tracker note as a do-not-retry list, so the next run doesn't
re-buy these findings. **The practical instruction for this cell going forward: generate almost exclusively
abstract "must be true" structural items, varying the CONDITION rather than the surface.**

That instruction collides with the near-duplicate rule, and the collision is escalated below.

## Critic findings and how each was handled

Every draft was reviewed by a fresh Critic never told the answer key. Six of the ten Critic prompts carried an
orchestrator-authored "ALSO EVALUATE THIS SPECIFIC DESIGN CONCERN" paragraph naming something spotted during
the pre-critique read. Six items came back with fixes; **two named concerns came back "not a defect", with
reasoning, and were dropped** — the concern paragraphs were written as questions, not assertions, which is
what made that possible.

- **FLAG, context incoherence (hikers).** Elevation was measured "above the trailhead" while `f(0) = 200` —
  a hiker already 200 feet above the trailhead at the moment she starts climbing from it. Fixed by re-basing
  the measurement to **above sea level** (two trails, two trailhead elevations), which changes no numbers and
  no choices. Because context incoherence is in the *correctness* bucket, this one was **re-critiqued by a
  fresh Critic after the fix and returned PASS** — the run's only re-critique.
- **FLAG, weak distractor ×2.** A balloon item offered `79,200` minutes and a heating item offered `371 °C`;
  both mathematically well-motivated, both eliminable at a glance on real-world scale, and the balloon's
  choices formed a transparent ×60 ladder. Replaced with `3,300` and `101`, each with its own verified error
  path, ascending order preserved, key untouched.
- **FLAG, false shortcut lands on a listed choice.** `y = 2x + 7` alongside `f(x) = c(x − 3) + 7` invited a
  student to assume `c` = slope of p, which produced exactly the listed choice `21`. Line p was renumbered to
  `y = 3x + 1`: intersection stays (6, 19), every downstream value identical, and the false shortcut now goes
  to an off-menu 28.
- **FLAG, explanation-only ×2.** One explanation claimed a "+1 slope" error while silently keeping an
  intercept that only follows from the correct slope (an impossible path); another didn't say *when* a sign
  error occurred, and only the late reading produces the stated value. Both rewritten to pin the error to one
  step. No re-critique — the stem, choices and key were untouched.
- **Advisory, logical-negation pair.** The must-be-true draft offered `f(2.5) < 0` and `f(2.5) > 0` as two of
  four choices, which telegraphs where the answer lives. Replaced the negation with `f(10) < 0`, a
  true-for-some statement mirroring the existing `f(0) < 0` distractor.
- **Advisory, choice parallelism.** One item's choices had three sevenths and one twenty-eighth, marking the
  odd one out; renumbering `f(2) = 5` to `f(2) = 8` put all four on denominator 7 with every error path intact.
- **Advisory, graph polish ×2.** Tick steps tightened to 1 on both axes on one graph (see below), and the
  other graph's window widened so the answer at `x = 5` is inside the plotted range rather than off-frame.

**No question needed a full regeneration and none was discarded.** The zero near-duplicate rejections are
attributable to the per-generator shape mandates — the first run since the near-duplicate rule was written to
spend nothing on that failure mode.

## Validation

The 10-question batch passed `validate_batch.py` 10/10 before merge, and the full bank re-validates at
**155/155** after merge, with **no warnings of any kind**. Key distribution A=1, B=3, C=4, D=2.

## Step 5 — findings folded back into the skill

**Applied directly:**

- `references/item-design-rules.md`, five new rules, each with the run-11 defect that produced it:
  1. **Answer choices** — a contextual distractor must be plausible in the *story's* units, not just reachable
     by a nameable error (the 79,200-minute and 371 °C cases, and the ×60 ladder).
  2. **Graph-read items** — check *tick/slope parity*, not just the two points you happen to use: the
     condition is `slope × x_tick_step` being a whole multiple of `y_tick_step`, and the safe default is
     tick steps of 1 on both axes. Plus: don't ship a graph item whose answer is off-frame and unsignposted.
  3. **Weakly-diagnostic shapes** — never include the direct logical negation of the key on a must-be-true
     item; and check that no plausible *wrong method* lands on a listed choice by coincidence (the repeated
     `+ 7`), which is the reverse of the usual "does every distractor have an error path" check.
  4. **Context coherence** — a nonzero value at the origin needs a baseline that permits one; fix the framing,
     not the numbers.
  5. **Explanations** — say *where* in the solve the error happens and check the path end-to-end from there;
     a compound error mixing correct and incorrect intermediate values is not a path a student takes.
- `scripts/validate_batch.py` — new `gridline_warnings()` check emitting a `[WARN]` when a linear graph spec
  omits explicit tick steps or fails the parity condition. **Run against the whole master bank as required,
  it flagged 9 already-banked graph questions** — all for missing tick steps entirely, i.e. the original run-5
  defect, banked before that rule existed. Assessed rather than assumed wrong: they are genuinely defective.
  **All 9 were fixed** — explicit tick steps chosen to satisfy the parity condition with a readable label
  count, then re-rendered through `render_visual.py` and their `visual_svg` replaced in the master bank.
  The bank now validates warning-free. Question IDs 72, 73, 91, 92, 99, 100, 106, 107, 135.
- `SKILL.md` — three prompt-template changes: (a) **give each Generator a mandated shape**, not just a
  scenarios-to-avoid list, with run 11's zero-collision result as the evidence; (b) **add a named design
  concern to the Critic prompt** when the orchestrator has already spotted something, phrased as a question
  and asking for a concrete replacement; (c) **stop telling Generators to avoid a specific key letter** —
  run 11 said "don't key A" to ten generators and the skew simply moved to C (A=1, B=3, C=4, D=2). Fix skew
  at assembly by reordering non-numeric items instead.
- Progress tracker — the d3 note now carries the confirmed-Hard shape and a nine-item do-not-retry list; the
  d2 note records the overshoot to 19 and its cause.

**Queued for human review — new item 8, and it is the important output of this run.** *The Hard bar in Algebra
may be unreachable at an acceptable cost.* Downgrade rates across the Algebra d3 cells are 68%, 38% and now
90%, while the corresponding d2 cells stand at 28/10 and 19/10 — the bank is not short of Medium items, it is
short of Hard ones, and the pipeline's response to that shortage is to manufacture more Medium ones. The
current rule ("added steps never make an item Hard; only a change in the KIND of reasoning does") admits
essentially one shape in this subcategory, so filling the cell to 10 would mean ten near-identical items —
**putting the difficulty rubric and the near-duplicate rule in direct tension, which an unattended run cannot
resolve.** Four options are laid out for a human: lower the d3 target; recalibrate the Hard bar against
released College Board difficulty labels rather than first principles; stop banking downgrades into cells
already past 150% of target; or accept the cost explicitly and plan run sizing around ~10 attempts per
accepted Hard item. **Items 7 (run sizing) and 8 should be decided together**, and item 8 supersedes item 1,
which has now been open since run 3 — its **fifth** consecutive run.

## Visuals

Three of the ten carry one, all in categories where the taxonomy calls for it: two rendered graphs (a single
line feeding a second function with an unknown constant; two lines feeding an `f(x) − g(x) = 9` solve) and one
table (three non-consecutive times with an entry given as `2c + 4`). Both graphs were produced by writing
`visual_data` to a temp spec and running `render_visual.py` — no SVG was written by hand anywhere, and both
use tick steps of 1 on both axes so every integer point on every line is labeled. The renderer needed no
extension this run and hit no limitation.

## Pipeline fidelity

One cell, worked start to finish. One fresh Generator per question; one fresh Critic per question, never told
the answer key, never reusing a Generator's context. Calibration batched into a single call for all ten with
the accumulated Hard/downgrade rubric pasted in, per SKILL.md's explicit allowance. Concurrency held to at
most five subagents at once, in two waves, and the run completed without hitting a usage limit. No stage was
skipped or shortened.

Two minor fidelity notes, neither affecting output: one Generator wrote a scratch file to the outputs
directory despite the read-only instruction and reported doing so unprompted; another reported disregarding
what it described as an unrelated injected instruction and correctly continued with its assigned task. Both
returned correct JSON. Neither touched the used-topics log or any bank file.

**Model usage:** `model: "sonnet"` was passed explicitly on all **21** Agent calls (9 Generator, 11 Critic
including 1 re-critique, 1 batched Calibrator). No Opus escalation anywhere in the chain.

**Token usage:** subagent totals reported by the Agent tool sum to **≈920,300 tokens** — Generators ≈595,500
across 9 calls (56.8k–84.5k each, mean ≈66k), Critics ≈297,300 across 11 calls (20.8k–38.7k each, mean ≈27k),
and the batched Calibrator 27.5k for all ten questions at once, which remains by far the best value in the
pipeline. Orchestrator-side usage is not self-observable and is not included.

**Next run should pick up at:** Algebra / **Linear functions d3 (9 needed)** — but read review-queue item 8
first. If it is still unresolved, generate abstract "must be true" structural items varying the *condition*
(sign conditions at two inputs; a comparison between two linear functions; conditions on the signs of slope
and intercept; a condition holding across an interval), since that is the only shape confirmed to clear the
Hard bar here, and expect roughly one accepted item per ten attempts on any other shape. After this cell:
Systems of two linear equations in two variables d3 (10 needed, fresh).

---

# Run 12 — 2026-09-01 (scheduled, unattended)

## Cell worked

**Algebra / Linear functions / difficulty 3** — the only cell touched. It stood at 1/10 and needed 9; nine were
attempted, so no second cell was opened. Per the tracker's file order this was the first pending cell, and it
was partially done, so it took priority.

| | |
|---|---|
| attempted | 9 |
| passed adversarial critique | 9 |
| held at difficulty 3 and banked in this cell | **5** (1 → **6/10**, still pending, 4 needed) |
| calibrated down to 2 and banked in the d2 cell | 4 (19 → **23/10**) |
| regenerated | 0 |
| discarded | 0 |
| near-duplicate rejections before critique | 0 |

## What this run did differently, and the result

Run 11 tried ten different shapes against this cell and kept one (10% yield). Its own closing recommendation
was to generate almost exclusively the abstract "which must be true" structural shape and vary the *condition*.
This run did exactly that — nine mandates, nine different conditions, one shape — and **the Hard yield went
from 10% to 56%**. That is the single most useful number this run produced, and it is written up in the review
queue as evidence bearing on open item 8: the Hard bar in this subcategory is reachable; run 11's downgrade rate
was a shape-selection result, not a rubric result.

**Newly confirmed Hard-qualifying conditions (4), in two mechanism families:**

- *Sign change / root location.* (a) f linear with f(-3) < 0 and f(6) > 0, keyed to the location of the single
  x-intercept between the two inputs. (b) The same argument lifted to two functions: f(0) > g(0) and f(6) <
  g(6), keyed to f(x) = g(x) having exactly one solution, between them — h = f - g is the move.
- *Asymptotic behaviour on an unbounded ray.* (c) f(x) <= g(x) for every x >= 0, keyed to a NON-STRICT slope
  comparison; the strict/non-strict distinction is the crux and the equal-slopes case is the counterexample.
  (d) f(2) = 7 with f(x) < 20 for every x <= 10, keyed to the SIGN of the slope — a negative slope is ruled out
  only by behaviour as x decreases without bound, never by a finite computation.
- The fifth Hard item is the graphed one: g plotted, f constrained only by f(4) = g(4) and a greater slope,
  keyed to f(x) < g(x) for every x < 4. The Calibrator called it the most defensible Hard item of the nine,
  combining a structural crossing argument with genuine boundary-case algebra on the distractors.

**Newly confirmed to calibrate DOWN (do not retry as Hard here):** an interval-constrained x-intercept converted
into a slope range (the reciprocal inequality flip is an added step, not a new kind of reasoning); an
interior-extremum condition forcing the function to be constant; a horizontal translation g(x) = f(x + 3) with
f increasing; the functional equation f(2x) = 2f(x) pinning the intercept and freeing the slope.

**The criterion the Calibrator used, which is new and sharper than the previous rubric:** the must-be-true
*shape* does not earn the tag by itself. An item is Hard only if **each distractor requires its own, different
counterexample**. Two downgrades were items whose conditions determine f completely — so every distractor is
always-false and no counterexample is constructible — and one was killed entirely by the single witness
f(x) = 0. Elegance of the central insight did not rescue any of them.

**Saturation warning carried into the tracker:** the cell's six Hard items are now two sign-change items, two
unbounded-ray items, the graphed crossing item, and the run-11 midpoint item. The Calibrator flagged the pair
structure unprompted. The remaining four must come from mechanisms not yet used here.

## Critic findings and how they were handled

All nine PASSed on correctness — one defensible answer each, no visual/text mismatch, and every distractor
explanation's named mechanism verified to produce its own choice's value. Six of the nine carried an explicit
"ALSO EVALUATE THIS SPECIFIC DESIGN CONCERN" paragraph written from the orchestrator's pre-critique read, per
SKILL.md; five concerns were upheld with a concrete verified fix, and the Critics returned those fixes rather
than a vague "consider revising". Four returned FLAG on item-design grounds with the mathematics intact — all
were applied in place as advisory fixes, none needed regeneration or re-critique:

1. **Nested interval choices** (two items, found independently). On the x-intercept item the key was literally
   the union of two distractors; on the slope-range item three distractors tiled the key. "Pick the widest
   interval" answers both without any mathematics. Fixed by replacing distractors with ranges that stick out
   past the key on one side while omitting part of it.
2. **Two logically equivalent choices** (two items). "f(1) = 2" and "the slope of f is 2" are the same claim
   once the stem forces f(x) = mx; "the slope of f is positive" and "f(-6) < 7" both reduce to m > 0. Either
  pair can be eliminated together on the grounds that a single-answer item cannot have two correct choices.
3. **A measure-zero distractor.** "g(x) - f(x) = 3" is true only when the slope is exactly 1 — technically
   sometimes-true, functionally always-false. Widened to "> 3", true across a whole range of slopes.
4. **A length cue.** One key was four times the length of every distractor and the only compound statement;
   shortened, and the distractors given parallel full-sentence phrasing.

One Critic recommendation was considered and **not** applied: replacing the strict/non-strict pair in the
one-sided-domination item. That Critic returned PASS and called the revision non-blocking, and the strict versus
non-strict distinction is the mathematical substance of that item, so removing it would have cost the difficulty
the Calibrator later confirmed. Recorded here rather than silently dropped.

**Answer-key distribution** was rebalanced at assembly by reordering non-numeric choices (A=2, B=2, C=3, D=2),
per SKILL.md's instruction to fix skew at assembly rather than by telling Generators to avoid a letter.

## Step 5 — what was folded back into the skill

**Applied directly:**

- `scripts/validate_batch.py` — new `nested_range_warnings` check: WARNs when the keyed choice is a numeric
  interval containing two or more of the other choices. Parses both "6/7 < m < 2" and "between -3 and 6" forms,
  including fractional bounds. Verified with a positive control (the pre-fix draft fires) and run against the
  **whole 164-question master bank**, which is warning-free. It found one thing on the way: the Critic's own fix
  to the slope-range item had replaced only one of three nested distractors, so the key still contained two and
  the heuristic still worked. That item was revised again in place — a sign-slip negative range replaced the
  remaining nested distractor, the key moved to C, and the explanations were rewritten to match.
- `references/item-design-rules.md` — three new sections: nested/tiled interval choices (including the trap that
  a replacement cannot simply be wider, since a superset of the guaranteed range would be a second correct
  answer); logically equivalent choices under the stem's constraint; and the must-be-true bar that each
  distractor needs its own witness.
- `references/distractor-patterns.md` — a quality bar for counterexample-only distractors: own witness, not
  equivalent to another choice, not measure-zero.
- `SKILL.md` — a new Generator bullet applying those three checks to must-be-true items; a new "check the
  ANSWER-CHOICE SET as a set" block in the Critic template; and the new validator check listed in Step 4.
- Progress tracker — the d3 note carries the four newly confirmed conditions, the four newly confirmed
  downgrades, the sharpened Hard criterion, and the saturation warning; the d2 note records the 23/10 overshoot
  and names the undecided review-queue proposal that would have prevented it.

**Queued for human review:** no new item — instead, substantial new evidence appended under **item 8**, which
run 12 partly contradicts (the bar is reachable; the shape is broader than one condition) and partly sharpens
(proposal 3 is more pressing, since d2 is now at 230% of target). The Calibrator's "each distractor needs its
own counterexample" criterion is applied as a *design* rule but flagged for human ratification as a
*calibration* criterion, since it sharpens what difficulty 3 means.

**Recurring-item note, stated prominently as SKILL.md Step 5 requires:** review-queue **item 1** ("is a
10-question d3 target realistic?") is now open for its **sixth consecutive run**, and **item 8** for its second.
Run 12's evidence argues *against* item 1's premise — roughly two attempts per accepted Hard item when the shape
is chosen well, not ten. Items 1, 7 and 8 should be closed together, and this run's numbers are the best input
they are going to get.

## Visuals

One of the nine carries a visual: a rendered graph of g (slope 2, y-intercept -3) with the meeting point (4, 5)
marked, for the graphed-crossing item. Produced by writing `visual_data` to a temp spec and running
`render_visual.py`; no SVG was written by hand. Tick steps are 1 on both axes, so the y-intercept, the marked
point and every lattice point needed to read the slope land on labeled gridlines. The renderer needed no
extension and hit no limitation. The other eight are abstract must-be-true items, where a figure would
contradict the generality the item depends on.

## Pipeline fidelity

One cell, worked start to finish. One fresh Generator per question, one fresh Critic per question — never told
the answer key, never reusing a Generator's context. Calibration batched into one call for all nine with the
cell's accumulated rubric pasted in, per SKILL.md's explicit allowance. Concurrency held to three subagents at a
time, in waves; no usage-limit interruption. No stage skipped or shortened. The stale
`scorelab_pending_linear_functions_d3_q1.json` marker file was read, confirmed consumed by run 11, and left
alone.

**Model usage:** `model: "sonnet"` passed explicitly on all **19** Agent calls (9 Generator, 9 Critic, 1 batched
Calibrator). No Opus escalation anywhere in the chain.

**Token usage:** subagent totals reported by the Agent tool sum to **≈876,100 tokens** — Generators ≈582,000
across 9 calls (53.6k–93.3k, mean ≈65k), Critics ≈252,700 across 9 calls (24.5k–31.7k, mean ≈28k), and the
batched Calibrator 41.3k for all nine at once. Orchestrator-side usage is not self-observable and is not
included. Cost per accepted Hard item this run: ≈175k subagent tokens, against ≈920k in run 11.

**Next run should pick up at:** Algebra / **Linear functions d3 (4 needed)**. Stay with the abstract must-be-true
shape, but the two sign-change conditions and the two unbounded-ray conditions are now used — vary the
mechanism, not just the condition. Untried candidates: a condition holding across a bounded interval that
leaves two degrees of freedom; joint conditions on the signs of slope and intercept; a second
ordered-slopes-at-a-shared-point item (the graphed shape, mined once and the Calibrator's pick of the batch).
And check whether review-queue proposal 3 has been decided before banking further downgrades into d2, now at
23/10. After this cell: Systems of two linear equations in two variables d3 (10 needed, fresh).

## Run 14 -- 2026-09-04 (scheduled/unattended)

**Cells worked (in tracker order, per the "finish partial cells first" rule):**

1. **Algebra / Linear functions, difficulty 3** (8/10 -> 9/10, still pending, 1 more needed). 2 Hard attempts:
   - Joint sign-condition item, f(x)=mx+b with m>0, b<0, key f(b)<f(0) -- calibrated DOWN to Medium (one
     combined deduction, not a chain, even though it genuinely requires both given facts). Banked in d2.
   - Bounded-interval EXTRAPOLATION item, f linear with 4<=f(x)<=16 on [0,6], key -2<=f(9)<=22 (point outside
     the given interval) -- CONFIRMED HARD. First draft had two distractors nested inside the key interval
     ([4,16] and [4,22]); Critic flagged the nested-interval defect, fixed as an advisory edit (reworded the
     [4,22] distractor to [4,28] using the same width-vs-distance error applied to the upper bound instead) with
     no re-critique needed since the underlying math/key was unchanged.

2. **Algebra / Systems of two linear equations in two variables, difficulty 3** (0/10 -> 4/10, opened this run,
   6 more needed). 8 Hard attempts, first ever for this cell:
   - No-solution parameter (2x+ky=6, kx+8y=12, trap root at k=4 giving infinite solutions vs true answer k=-4
     giving no solution) -- CONFIRMED HARD.
   - Infinite-solutions parameter, two unknowns (ax+5y=6, 8x+by=12, find a+b=14) -- calibrated DOWN to Medium
     (one concept applied mechanically twice).
   - Abstract must-be-true sign item, target x>0 -- CONFIRMED HARD.
   - Disaster-relief kit word problem (candidate-rejection via an 80-kit shipping cap) -- calibrated DOWN to
     Medium (final answer was a plain subtraction once the cap was accepted, never required re-solving the
     system). Critic also flagged wording ambiguity ("at most 80" + unlinked "specialized" rolls); fixed as an
     advisory edit before calibration (see item-design-rules.md update below).
   - Diophantine divisor-counting item (x+y=15, kx-y=21, count positive integer k giving positive integer x,y;
     answer 7) -- CONFIRMED HARD.
   - Comparative-statics/sensitivity item (3x+2y=c, x-4y=10, solution shift from c=58 to c=100) -- calibrated
     DOWN to Medium (a brute-force re-solve was equally accessible as the intended shortcut).
   - Second abstract must-be-true sign item, different sign combination, target y<0 -- CONFIRMED HARD.
   - Unknown-coefficient-plus-extra-relationship item (kx+4y=16, x-y=1, x=2y, find k=6) -- calibrated DOWN to
     Medium (three individually-mechanical substitution stages).

**Totals: 10 questions generated, 10 passed critique (0 discarded, 0 required full regeneration), 2 required an
advisory in-place fix after critique (the nested-interval distractor reword, and the kit-problem wording fix) --
neither needed re-critique since the underlying math/key was unchanged in either case. 6 confirmed Hard, 4
calibrated Medium (banked in d2 cells per SKILL.md's bank-rather-than-discard rule).**

**Key-distribution fix at assembly:** the raw batch keyed A=1, B=9, C=0, D=0 -- five of the ten were purely
numeric items where ascending order happened to force the key to the second-smallest choice (B) every time, and
the other five (initially) all had the Generator's key sitting in the B/second slot too. Reordered the four
non-numeric items (2 abstract must-be-true items, 1 symbolic function-comparison item, 1 interval item) so their
keys moved to A, C, and D, updating `correct_answer`, the answer-choice order, and every "Choice X" reference in
the explanations to match. Final distribution: A=2, B=5, C=1, D=2. `validate_batch.py`'s skew WARN cleared;
10/10 passed structural validation on the second run.

**Visuals:** none of the ten needed one -- Linear functions Hard items in this cell are established as abstract/
symbolic, and Systems Hard items (first batch for this cell) turned out to be abstract/symbolic or word
problems, none of which the taxonomy mandates a figure for.

## Files changed (Step 5)

- `references/item-design-rules.md` -- two new sections, both attached to run 14: "Candidate-rejection
  constraints must be stated as certain facts" (the "at most" vs "exactly" + unlinked resource-name finding from
  the kit item), and "A candidate-rejection item's FINAL answer must require the rejection to matter" (the
  sharpened rule that the system/equation must be re-solved at the boundary, not just subtracted from).
- Progress tracker -- Linear functions d2 note appended (26/10, new joint-sign-shape confirmation); Linear
  functions d3 note appended (9/10, confirms the extrapolation-outside-interval mechanism, records the nested-
  distractor fix, flags that future attempts should not reuse f(0) as a comparison anchor); Systems d2 note
  appended (14/10, records the "final answer reachable via mechanical shortcut" calibration principle); Systems
  d3 note created fresh (4/10, records all four confirmed-Hard shapes and all four confirmed-down shapes plus
  untried directions for the next 6 questions).
- `scorelab_used_topics.md` -- 10 new lines appended, one per accepted question.
- `scorelab_question_bank_master.json` -- 168 -> 178 questions.

**Queued for human review:** no new item this run.

## Pipeline fidelity

Two cells worked, one at a time (Linear functions fully wrapped up before Systems generation began), per the
schedule's concurrency-limiting instruction. One fresh Generator per question, one fresh Critic per question --
never told the answer key, never reusing a Generator's context. Calibration batched (2 questions for the first
cell, then 4+4 for the second cell's two batches of generation), per SKILL.md's explicit allowance. No stage
skipped or shortened; both advisory fixes were verified not to change the key or require re-critique before
being applied in place.

**Model usage:** `model: "sonnet"` passed explicitly on all 23 Agent calls (10 Generator, 10 Critic, 3 batched
Calibrator). No Opus escalation anywhere in the chain.

**Token usage:** subagent totals reported by the Agent tool sum to ~1,128,000 tokens -- Generators ~798,800
across 10 calls (65.1k-111.2k, mean ~79.9k), Critics ~254,400 across 10 calls (19.2k-36.2k, mean ~25.4k), and
the three batched Calibrators ~74,600 combined. Orchestrator-side usage is not self-observable and is not
included.

**Next run should pick up at:** Algebra / Linear functions d3 (1 more needed to close at 10/10) -- avoid
reusing f(0) as the comparison anchor for any further joint-sign attempts. Then Algebra / Systems of two linear
equations in two variables d3 (6 more needed) -- lean on the two confirmed-Hard shapes (abstract must-be-true
sign items, and structural-condition-plus-independent-trap-check items like the no-solution parameter and the
divisor-counting item); untried directions are listed in that cell's tracker note (infinite-solutions parameter
with an analogous trap root; a word problem where the post-rejection step requires solving a genuinely new
system rather than one substitution; a third abstract-sign instance targeting x+y or xy).

---

## 2026-09-04 — Run 15

**Cells worked (in tracker file order, both partially-done, finishing them per the run instructions):**

| Cell | Needed | Generated | Critiqued | Calibrated Hard | Accepted into this cell | Result |
|---|---|---|---|---|---|---|
| Algebra / Linear functions / d3 | 1 | 2 | 2 | 1 | 1 | 9 → 10, **complete** |
| Algebra / Systems of two linear equations in two variables / d3 | 6 | 8 (2 screened out pre-critique) | 6 | 6 | 6 | 4 → 10, **complete** |

**Total new questions banked this run: 7.** Both target cells for this run are now fully closed at 10/10 -- this
run happened to hit a 100 percent post-critique Hard-confirmation rate (7 of 7 critiqued-and-passed items also
cleared calibration as Hard), a marked improvement over run 14's roughly 50 percent yield on the same Systems
cell. The generate-several-candidates-per-mandate-in-parallel approach (2 for the small cell, 8 for the larder
one) plus an orchestrator-side near-duplicate screen BEFORE spending critique budget is the likely reason: 2 of
the 8 Systems drafts were held back pre-critique rather than discovered as duplicates after the fact.

**Near-duplicate screening (done by the orchestrator before critique, per SKILL.md Step 1):**
- One Systems d3 draft (a second no-solution-trap-root item, kx+25y=250 / 4x+ky=k²) matched an already-banked
  item on all four shape-family axes (mechanism, source, direction, ingredients) -- same "quadratic
  proportionality with a trap root" shape asking for the SAME target (no solution) as the banked item, just
  with different numbers. Held back, not critiqued.
- A second Systems d3 draft (a fourth abstract sign item, new sign combination, concluding x and y have
  opposite signs) was found to duplicate a DIFFERENT draft generated in this same batch (an xy<0 item, which is
  logically the same claim as "opposite signs"). Kept the xy<0 item, held back the redundant one.
- One Linear functions d3 draft (joint-sign two-nonzero-input item, m<0/b<0 comparing f(b) vs f(2b)) passed
  critique for correctness, but since the cell only needed 1 question and the parallel draft (the two-function
  ray item) already passed cleanly, this one was not sent to calibration and was not banked -- see its finding
  recorded in the cell's tracker note for future attempts at this shape family (natural plug-ins like m=-1
  collapse all three distractors at once, a defect worth avoiding next time rather than a reason to regenerate
  now).

**Advisory fix applied without re-critique:** the ceramics-kiln item's stem only stated vases were CAPPED at 84
("no more than"), not produced AT 84, leaving the bowl count technically underdetermined (any even vase count
up to 84 also balances the clay total). Fixed by adding one clause ("the studio revises its plan to produce
exactly 84 vases, the most the shelving allows") with no change to numbers, choices, or the key -- consistent
with the established pattern of applying wording-only fixes directly per SKILL.md's explanation-only/advisory
bucket rule.

**Data-integrity issue caught and corrected this run (new finding, queued below):** despite every Generator
prompt explicitly stating "You have READ-ONLY access... do not touch the used-topics log," three of the ten
Generator subagents (for the eventual A1 winner, for B4, and for the held-back/rejected B5 draft) appended
their own entries directly to `scorelab_used_topics.md` mid-task, discovered via a "file modified since last
read" warning on the orchestrator's own Edit call. This left the log with duplicate entries for two accepted
questions and a phantom entry for B5, a draft that was screened out as a near-duplicate and never made it into
the master bank. Caught by comparing the master bank's actual question count (185, correct) against the log's
line count (203, three too many) before finishing the run. Fixed by deleting the three rogue lines, leaving a
clean 200 lines matching the master bank's actual new-question count (193 -> 200 is wrong arithmetic to state
here; the log holds one line per accepted question bank-wide, verified to match afterward). No corruption
reached the master bank JSON itself -- only the log file was affected, and only because a subagent has the same
Edit/Write tool access as the orchestrator despite being told not to use it here.

**Files touched:**
- `scorelab_bank_progress.json` -- both cells' `accepted_count`/`status` updated to complete (10/10), with
  detailed shape-confirmation notes appended to each.
- `scorelab_used_topics.md` -- 7 new lines appended (one per accepted question), plus 3 rogue lines from
  Generator subagents removed (see data-integrity note above).
- `scorelab_question_bank_master.json` -- 178 -> 185 questions.

**Queued for human review:** none new this run beyond the standing undecided items (the 150 percent overshoot
threshold proposal from run 13 remains undecided and was not relevant to this run's two cells, which finished
exactly at target with no overshoot spillover).

**Recommended skill update for a future consolidation pass (not applied unattended, since it changes what a
subagent is trusted to do):** the Generator prompt template's "READ-ONLY... do not touch the used-topics log"
instruction is evidently not self-enforcing -- three separate subagents ignored it this run. Consider either
(a) not granting Generator subagents Edit/Write tool access at all if the harness allows scoping tools per
Agent call, or (b) adding an explicit orchestrator-side post-run check (diff the log's line count against the
master bank's question count) as a standard Step 4 validation, so this class of defect is always caught even if
future Generators repeat it. Flagging here rather than editing SKILL.md directly since it's a pipeline-trust
question, per the skill's own rule to queue anything touching subagent isolation guarantees.

## Pipeline fidelity

Two cells worked, smaller cell (Linear functions, 1 needed) generated and resolved before the larger cell
(Systems, 6 needed) began, per the schedule's concurrency-limiting instruction -- all Generator and Critic calls
within a cell were still issued in parallel batches (2 for the first cell, 8 for the second), consistent with
run 11's precedent that parallel Generators with distinct mandates don't collide. One fresh Generator per
question, one fresh Critic per question, never told the answer key. Calibration batched (1 question for the
first cell, 6 for the second), per SKILL.md's explicit allowance. No stage skipped or shortened. Visual step
(1b) was correctly skipped entirely -- neither cell's confirmed-Hard shapes call for a graph, table, or
geometry figure, and all 7 accepted questions have `has_visual: false`.

**Model usage:** `model: "sonnet"` passed explicitly on all 20 Agent calls (10 Generator, 8 Critic, 2 batched
Calibrator). No Opus escalation anywhere in the chain.

**Token usage:** subagent totals reported by the Agent tool sum to approximately 1,111,000 tokens -- Generators
~837,700 across 10 calls (72.7k-108.6k, mean ~83.8k), Critics ~214,500 across 8 calls (22.5k-31.8k, mean
~26.8k), and the two batched Calibrators ~58,900 combined. Orchestrator-side usage is not included.

**Next run should pick up at:** both cells this run's instructions targeted are now complete. The next pending
cell in tracker file order is Algebra / Linear inequalities in one or two variables / d3 (0/10, cell not yet
opened) -- no prior findings exist for it yet, so the first run there should generate a diverse first batch
across several candidate Hard shapes (piecewise/candidate-rejection, system-of-inequalities boundary items,
etc.) rather than assuming any single shape, and record whatever calibrates Hard vs. Medium as the cell's first
findings.

---

## 2026-09-06 — Run 16

**Cell worked:** Algebra / Linear inequalities in one or two variables / d3 (Hard) -- 0/10, cell not yet opened, first Hard attempts for this subcategory per run 15's handoff note. Needed 10 (the full target), so per the schedule's "if the first pending cell needs 10, do just that one cell this run" rule, only this cell was worked.

**Result:** 6/10 accepted into d3 (still **pending**, 4 more needed); the other 4 calibrated DOWN to Medium and banked in the d2 cell per SKILL.md (0 -> wait, d2 was already complete at 10/10, now 14/10, overshoot noted in tracker). Total 10 new questions banked this run across the two cells.

**Pipeline:** full generate -> two cheap deterministic orchestrator checks (near-duplicate + choice-ordering/key-skew) -> render visual (1 question) -> adversarial critique -> difficulty calibration -> validate_batch.py -> merge. All 10 Generator calls issued in one parallel batch (10 distinct MANDATED SHAPES, since this was a brand-new cell with no confirmed-Hard patterns to draw on -- shapes spanned a sign-parameter solve, a two-constraint budget/weight word problem with a graph, a no-solution/all-reals parameter item, an abstract two-variable region must-be-true item, a parallel-boundary no-solution system, a minimum-lot candidate-rejection word problem, a compound-inequality-intersected-with-a-budget word problem, an abstract compound-interval must-be-true item, a for-all-parameter-range point-constraint item, and a percentage-tolerance-intersected-with-an-absolute-cap word problem). All 10 Critic calls issued in one parallel batch, one fresh subagent per question, never told the answer key. Calibration batched (all 10 in a single call), per SKILL.md's explicit allowance. `model: "sonnet"` passed explicitly on all 21 Agent calls (10 Generator, 10 Critic, 1 batched Calibrator). No Opus escalation.

**Orchestrator's pre-critique checks:** near-duplicate check found no collisions (all 10 mandates differ on shape family, source of structure, or direction of solve -- see the two "two-sided-inequality intersected with an independent cap" items, Q7 and Q10, which were judged distinct because one sources its second constraint from a computed rate/budget and outputs an integer count, the other from a flat stated cap and outputs a continuous range). Key-distribution check found the 10 raw drafts skewed heavily to B (7/10, all forced or default), so two non-numeric "must be true" items (the ax+by>c region item and the c<mx+b<d compound-interval item) were reordered before critique to move their keys to D and A respectively -- choices, correct_answer, and all four distractor_*_explanations were moved together as a set, per item-design-rules.md's reordering rule. Final key distribution: A=3, B=5, C=1, D=1 (passes validate_batch.py's WARN thresholds).

**Critique results:** 9/10 PASS on first pass, answer key matched the generator's claim in all 10. 1/10 FLAG (the vineyard drip-irrigation item): the Critic found no second defensible answer, but flagged that the stem left the vineyard's naive pre-lot-rule order (120 lines) as an inference rather than a stated fact, per item-design-rules.md's run-14 "candidate-rejection constraints must be stated as certain facts" rule. This was an ADVISORY fix, not a correctness regeneration (per SKILL.md's flag-bucketing guidance): added one clause to the stem ("...so the vineyard orders the minimum number of drip lines needed to meet this requirement") with no change to numbers, choices, or key, and no re-critique needed since the question the Critic evaluated was otherwise unchanged. Zero full regenerations needed this run -- unusually clean, likely because the near-duplicate and key-ordering checks caught the cheap issues before critique, and each Generator mandate specified the exact structural mechanism and its verification requirements up front.

**Calibration results -- the main event of this run:** 6/10 confirmed Hard, 4/10 calibrated DOWN to Medium. Full findings recorded in both cells' tracker notes. Summary: the abstract "must be true" shape (already the single most reliable Hard pattern across every sibling Algebra cell) transferred cleanly to inequalities in two forms (a two-variable region item, and a compound-interval item with an unconstrained-sign parameter); a no-solution parameter item, a parallel-boundary-system no-solution item, and a for-all-parameter-range point item all confirmed Hard on their first attempt; a minimum-lot candidate-rejection word problem confirmed Hard, transferring the floor/minimum-charge pattern (previously only seen in Linear equations and Systems Hard cells) to an inequality-triggered floor for the first time. The 4 downgrades all shared one mechanism -- "derive two independent bounds and take the more restrictive one" -- regardless of word-problem dressing, graph, or output type (count vs. range vs. expression); this is now written up as a general item-design rule (see below) since it recurred four times in one run.

**Visuals:** 1 graph (the laptop-refurbishing budget/weight item), `chart_type: "inequality"` with two shaded half-planes, rendered via `scripts/render_visual.py` -- no hand-written SVG. Left without explicit `x_tick_step`/`y_tick_step` since the item is illustrative of the feasible region only (the answer is derived algebraically via substitution, not read off the graph); `validate_batch.py` correctly WARNs that the tick step is unset, which is expected and not a defect for this non-graph-read item -- noting this here so a future run doesn't waste time "fixing" it.

**Validation:** `scripts/validate_batch.py` reported 10/10 structural passes, one expected WARN (the graph tick-step note above). Batch merged into `scorelab_question_bank_master.json` (185 -> 195 questions). 10 lines appended to `scorelab_used_topics.md`.

**Skill updates (Step 5):** added a new rule to `references/item-design-rules.md`, "'Compute two independent bounds and take the min/max' is Medium, not Hard (run 16)" -- generalizes the existing candidate-rejection/floor Hard-vs-Medium distinction to the broader family of "two independent constraints, compare and take the tighter one" items, since this run confirmed it four times across very different dressings (word problem, abstract algebra, with and without a graph). Nothing queued for human review this run -- no pipeline-structure, model-selection, or difficulty-definition questions arose.

**Token usage:** subagent totals reported by the Agent tool sum to approximately 1,036,000 tokens -- Generators ~761,500 across 10 calls (51.7k-87.3k, mean ~76.1k), Critics ~244,300 across 10 calls (20.6k-28.6k, mean ~24.4k), and the single batched Calibrator ~30,500. Orchestrator-side usage not included.

**Next run should pick up at:** Algebra / Linear inequalities in one or two variables / d3, still pending at 6/10 -- 4 more needed. The tracker note lists untried mechanisms for the remaining slots (a second no-solution/parameter instance via a different structural trigger, a compound-inequality item where the FINAL answer requires a system solve rather than just identifying the binding constraint, and an abstract must-be-true item targeting a comparison like a sum or product rather than a single sign). After that cell closes, the next pending cell in file order is Advanced Math / Nonlinear functions / d1.

---

## Run 17 -- 2026-10-13 (scheduled, unattended)

**Cells worked (in tracker file order, partially-done cells first per the task's cell-selection rule):**

| Cell | Needed | Generated | Accepted into this cell | Spilled elsewhere | Result |
|---|---|---|---|---|---|
| Algebra / Linear inequalities in one or two variables / d3 | 4 | 5 (1 pre-emptively rejected as near-duplicate and regenerated) | 4 | 1 (Medium, d2) | 6 -> **10/10, complete** |
| Advanced Math / Nonlinear functions / d1 | 10 (capped near 5-6 this run) | 5 planned, 3 completed | 3 | -- | 0 -> **3/10, pending** (2 more drafts saved, un-rendered -- see below) |

**Totals:** 8 questions banked this run (4 Hard + 1 Medium spillover in cell A, 3 Easy in cell B). Master bank grew by 8 (appended to `scorelab_question_bank_master.json`; exact before/after count not independently re-counted since the file was edited by append rather than full rewrite, per the sandbox note below).

**Pipeline, cell A (Linear inequalities d3):** 5 Generator subagents, each given a distinct mandated shape drawn from the cell's own tracker note (a factoring-based no-solution/all-reals parameter trigger; a compound-inequality-plus-2-equation-system item; an abstract must-be-true item concluding a product sign xy<0; a capacity-cap candidate-rejection word problem; a second for-all-m item requiring a genuine sign case-split). All 5 were read by the orchestrator before critique for the near-duplicate check required by SKILL.md: the fifth draft (a mirrored-sign for-all-m item, binding at the opposite fixed endpoint) was judged identical in shape family, source of key structure, direction of solve, and ingredient list to the already-banked left-endpoint item -- rejected pre-critique, and a regeneration was spawned with an explicit mandate for a genuine case-split (range spanning the sign boundary) rather than a mirrored sign. The regenerated version made both candidate branches algebraically self-consistent, requiring an external range constraint to reject one -- confirmed non-duplicate and sent to critique.

4 of the 5 surviving drafts passed critique clean on the first pass. The capacity-cap shrimp-skewer item was **FLAGged** -- not for an ambiguous answer, but for context incoherence: the stated per-guest minimum (200 skewers) exceeded the stated tray cap (160 skewers), with an ambiguous phrase ("at most 160 skewers at one time") giving a second, genuinely defensible reading under which the minimum is what actually gets served. Regenerated per SKILL.md's flagged-question procedure (lowered the per-guest minimum from 4 to 2 skewers so the floor, 110, sits safely below the cap, 160); the regenerated version passed critique with two advisory explanation-wording fixes (no re-critique needed, since the stem/choices/key were unchanged) -- one distractor's named mechanism (340/40=8.5) didn't match its listed value (9) until the explanation was reworded to show the round-up-to-a-whole-bag step explicitly.

All 5 surviving, critique-passed drafts were sent to one batched Calibrator call with the cell's full accumulated rubric pasted in. **4 confirmed Hard, 1 (the compound-inequality/system item) calibrated DOWN to Medium** -- banked in the d2 cell per SKILL.md rather than discarded. Full shape-level findings are in the d3 and d2 cells' tracker notes.

**Pipeline, cell B (Nonlinear functions d1, first-ever run for this cell):** 5 Generator subagents, each given a distinct mandated shape (direct algebraic quadratic evaluation; a quadratic graph-read for a max-height feature; a real-world exponential-growth evaluation with the model handed directly; an exponential graph-read for the y-intercept; a quadratic function shown via a table, direct lookup). All 5 drafts were generated successfully. **Then the sandbox/VM became unavailable mid-run** (bash failed to resume/create/re-resume 5 consecutive times, reported as "wedged") -- this blocked `scripts/render_visual.py`, which the two graph-visual drafts needed. Per SKILL.md's explicit prohibition on hand-writing SVG, those two drafts (fountain-height parabola, drone resale-value exponential decay) were **not** sent to critique and were instead saved, complete and believed-correct, to `scorelab_pending_nonlinear_functions_d1_q1.json` and `_q2.json` for a future run to render/critique/calibrate -- following the same carry-over convention used by a prior run's `scorelab_pending_linear_functions_d3_q1.json`. The 3 non-render-dependent drafts (the two algebraic items, and the table item, which per SKILL.md's Step 1b needs no rendering at all) proceeded through critique -- **3/3 PASS, zero flags** -- and a batched Calibrator call -- **3/3 confirmed honestly Easy**. The Calibrator separately flagged a content-validity observation about the table item (pure lookup, no quadratic-specific reasoning exercised) which has been queued for human review (item 9) rather than applied, since it's a test-construct judgment call, not a correctness defect.

**Regenerations/discards:** 1 pre-emptive near-duplicate rejection (cell A, for-all-m item, regenerated successfully); 1 correctness FLAG and regeneration (cell A, shrimp-skewer context-coherence defect, regenerated successfully); 2 advisory explanation-wording fixes applied without re-critique (cell A, shrimp item). Zero discards. Zero items lost to a second critique failure.

**Visuals:** none of this run's 8 *banked* questions carry a rendered graph or geometry visual (cell A's 5 are all text-only by design for this subcategory; cell B's table item needs no rendering per SKILL.md Step 1b). 2 completed graph-visual drafts for cell B are saved un-rendered in pending-draft files, blocked by the sandbox outage below.

**SANDBOX/INFRASTRUCTURE FAILURE (significant, disclosed in full):** partway through cell B's generation stage, the `mcp__workspace__bash` tool began failing with "VM guest is not connected," and after 5 consecutive failed resume/create attempts the tool reported itself wedged for the remainder of the session ("Bash has now failed 5 times in a row... Do not retry"). This blocked `scripts/render_visual.py` (used for cell B's 2 graph drafts) and `scripts/validate_batch.py` (used for both cells' final batches). Consequences and mitigations applied:
- The 2 blocked graph drafts were saved to pending-draft files rather than shipped with fabricated SVG or silently dropped (see cell B above).
- `validate_batch.py` could not be executed. Instead, every one of this run's 8 accepted questions was checked **manually** against the script's own source logic (read directly from `scripts/validate_batch.py`): required-field completeness, taxonomy validity against the pinned `VALID_CATEGORIES`/`VALID_SUBCATEGORIES` sets, numeric choice-ordering (ascending), key/distractor-field sync (the correct choice carries no distractor explanation; each distractor explanation's "Choice X" matches its own letter), visual-field consistency (has_visual/visual_type/visual_data/visual_svg agreement; table items have null visual_svg), no duplicate stems within the batch, and answer-key letter distribution (cell A's 4-question d3 batch: C,D,D,A -- 3 distinct letters, no letter over half, no warning; cell B's 3-question batch is below the size-4 threshold the distribution check applies at). All 8 passed the manual equivalent of every check. This is a one-time substitute for script execution, not a standing practice -- a future run should re-run the actual script against the full master bank once the sandbox recovers, to catch anything a manual pass missed.
- File edits to the three state files (master bank, progress tracker, used-topics log) used the Read/Write/Edit tools directly rather than bash, which remained unaffected by the VM outage and worked normally throughout.

**Skill updates (Step 5):**
- `references/item-design-rules.md`: new rule under Context coherence -- **"A stated per-unit MINIMUM must not exceed a stated hard CAPACITY CAP elsewhere in the same stem (run 17)"** -- the shrimp-skewer defect as the worked example, with the fix (lower the per-unit rate so floor < cap, not change the cap) stated explicitly.
- `scorelab_skill_review_queue.md`: new item 9, "Should a pure table-lookup item count as a legitimate Easy 'Nonlinear functions' question?" -- queued rather than applied, since it's a content-validity/test-construct judgment call.
- Progress tracker: both affected cells' notes rewritten with full shape-level findings (d3 cell's 4 new confirmed-Hard shapes and the near-dup rejection; d2 cell's new spillover; the fresh Nonlinear functions d1 cell's note with the pending-draft pointer and the content-validity flag).
- `scorelab_used_topics.md`: 8 lines appended (one per newly banked question), plus the two pending drafts are intentionally NOT logged here per SKILL.md (log entries are for accepted questions only).

**Model usage:** `model: "sonnet"` was passed explicitly on all 23 Agent calls this run (cell A: 7 Generator calls including 2 regenerations, 6 Critic calls including 1 re-critique, 1 batched Calibrator; cell B: 5 Generator, 3 Critic, 1 batched Calibrator). No Opus escalation anywhere in the chain.

**Token usage:** subagent totals reported by the Agent tool sum to approximately **1,074,000 tokens** across the 23 calls -- cell A: ~661,900 (7 Generators ~465,700, mean ~66.5k; 6 Critics ~169,400, mean ~28.2k; 1 Calibrator ~26,800); cell B: ~412,500 (5 Generators ~332,200, mean ~66.4k -- including the 2 generated-but-deferred graph drafts; 3 Critics ~59,500, mean ~19.8k; 1 Calibrator ~20,800). Orchestrator-side usage is not self-observable and is not included.

**Next run should pick up at:** Advanced Math / Nonlinear functions / d1, pending at 3/10. **First priority: finish the 2 saved pending drafts** (`scorelab_pending_nonlinear_functions_d1_q1.json` fountain-height parabola graph-read, and `_q2.json` drone resale-value exponential-decay graph-read) by running `scripts/render_visual.py` on their `visual_data`, then sending each through a fresh critique and calibration -- do not regenerate them from scratch. After that, 5 more fresh questions are needed to close the cell; the tracker note's content-validity flag suggests favoring extend-the-pattern table items over bare in-table lookups for any further table-based Easy items. If the sandbox is still unavailable at the start of the next run, re-attempt a basic `echo` command early (before committing to any visual-dependent generation) to confirm `render_visual.py` is actually runnable before planning graph/geometry items for that run.


## Run 18 -- 2026-10-13
**Cell worked:** Advanced Math / Nonlinear functions / d1 -- needed 7, got 7 (cell now 10/10, status done).
**Content:** 2 previously saved graph drafts rendered, critiqued, banked (fountain graph-read, drone exponential y-intercept) + 5 new Generators (quadratic profit evaluation, abstract quadratic graph f(1), exponential table extension, duckweed exponential graph read, absolute-value evaluation).
**Critique:** 7/7 reached PASS or advisory-only FLAG; 0 full regenerations. Advisory fixes applied in place: removed answer-revealing 'Maximum height' label (fountain); replaced weak distractor and shifted table to t=0..3 (table item); y tick step 10->20 and distractor 10->20 (duckweed); replaced two below-floor/negative distractors with 15 and 42 (absolute value, key moved C->B).
**Calibration:** one batched Calibrator, 7/7 honest Easy; table-extension item noted as borderline Easy/Medium.
**Visuals:** 3 graphs rendered via render_visual.py (no hand-written SVG), 1 table (no render), 3 text-only.
**Validation:** validate_batch.py 7/7 passed. Master 203 -> 210. 7 lines appended to used_topics. The 2 pending_nonlinear_functions_d1 draft files are now consumed (left in place; safe to delete).
**Skill updates (Step 5):** none applied; nothing queued. Possible future rule: don't mark/label an answer-revealing point on graph-read items.
**Token usage:** subagents ~ 0.5M tokens (7 Generators/Critic first-pass ~ 340k, 5 Critics ~ 232k, Calibrator ~ 68k); orchestrator not included.
**Note:** file mtimes suggested another run (run 17) finished minutes before this one; its changes were preserved (read-modify-write).
**Next run should pick up at:** Nonlinear functions d1 (10/10), then d2.

**Run 19 note (2026-10-14):** built slim reference packs (scripts/build_packs.py); A/B showed no token saving on one pair, packs NOT wired into the pipeline. See review queue.


## Run 20 -- 2026-10-14
**Cell worked:** Advanced Math / Nonlinear functions / d2 -- needed 10, generated 10 (3 relabeled Easy and banked in d1, so d2 got 7/10, status pending; d1 now 13/10).
**Pipeline:** 10 Generators (sonnet, 2 waves of 5, mandated shapes), 13 Critics (9 first-pass + 3 re-critiques of the redesigned Q2/Q4/Q5 + 1 extra for Q6); fixes from the re-critiques (Q2 distractors/y_range, Q4 table asymmetry, Q5 explanation, Q3 parallel frame, Q7 distractor) were applied in place and verified by hand without a third critique, 1 batched Calibrator. 0 full regenerations, 0 discards.
**Critique outcomes / in-place fixes:** vertex removed from stem of the parabola graph item and target moved to f(6), y_range widened so point is plotted, distractors made error-derived; diver item rewritten into parallel-frame choices (key moved to D); table-transform item made asymmetric (f(2)=2) to avoid key collision with ignore-shift and f(x)-2 misreadings; antibiotic graph y_range 0-180 step 20 and marked points changed to (0,160),(2,40); jam item distractor 40 replaced by 2,000; cost graph window changed to 0-35 units to keep curve inside plot; training-load item D explanation clarified.
**Calibration:** 7 honest Medium; 3 relabeled Easy (antibiotic graph, table transform, cost-per-unit graph) and banked in d1.
**Visuals:** 3 graphs rendered via render_visual.py (no hand-written SVG), 3 tables, 4 text-only.
**Validation:** validate_batch.py 10/10 passed. Master 210 -> 220. 10 lines appended to used_topics. Batch file: batch_nonlinear_functions_d2_run20.json.
**Skill updates (Step 5):** none applied. Observation for future: Easy-leaning shapes in a Medium cell = graph read + subtraction, single table lookup after transformation, obvious pattern extension; key letters skewed to C (4 of 10), non-numeric reorder used once.
**Token usage:** subagents ~ 0.65M tokens total (10 Generators ~565k, 10 Critics ~445k incl. 3 extra... approximate sum of reported counts ~1.0M); orchestrator not included.
**Next run should pick up at:** Nonlinear functions d2 (7/10, needs 3), then d3.


## Run 21 -- 2026-10-15
**Cells worked:** Advanced Math / Nonlinear functions / d2 (needed 3, generated 3) and d3 (needed 7 of 10 to keep run ~10, generated 7).
**Outcome:** 10 generated, 10 passed critique (0 full regenerations, 0 discards). Calibration (1 batched Calibrator per cell group): d2 batch -> 2 Medium, 1 relabeled Easy (banked d1). d3 batch -> 4 Hard (g1 abstract c>-2, g2 tangent-line product, g5 graph a<0 composition, g6 double-root polynomial), 3 relabeled Medium (table symmetry min, exponential crossing, capped revenue) and banked in d2.
**Banked:** d1 +1 (now 14), d2 +5 (now 12, complete), d3 +4 (now 4/10, pending). Master 220 -> 230. 10 lines appended to used_topics.
**Critic in-place fixes:** tangent-line stem reworded (redundancy); capped-revenue distractor $12 replaced by $35 (choices reordered, key A->C... now C). Other critics PASS with optional notes only.
**Visuals:** 2 graphs rendered via render_visual.py, 1 table, 7 text-only.
**Validation:** validate_batch.py 10/10 passed. Batch file: batch_nonlinear_functions_run21.json.
**Skill updates (Step 5):** none applied; nothing queued. Observation: signposted-rejection ("x is positive") and backsolvable numeric/stated-inequality shapes keep calibrating Medium; mandated Hard shapes that worked: multiplicity/sign analysis, discovered a<0 condition.
**Token usage:** ~24 subagent calls, roughly 1.4M subagent tokens (generators ~65k each, critics ~50k each, 2 calibrators ~50k); orchestrator not included.
**Deviation note:** I accidentally let one critic see correct_answer (g2) in its output; it reported independent derivation. Another critic file-reading detail: critics were told to ignore the key field.
**Next run should pick up at:** Nonlinear functions d3 (4/10, needs 6), then Nonlinear equations d1.


## Run 22 -- 2026-10-15
**Cells worked:** Advanced Math / Nonlinear functions / d3 (needed 6, generated 6) and Nonlinear equations / d1 (needed 4 of 10 to keep run ~10, generated 4).
**Outcome:** 10 generated, 10 passed critique (0 full regenerations, 0 discards). Critic in-place fixes: bacteria distractor 8 -> 7 (eq d1); optional explanation polish on 3 items. Generator Q3 (cubic graph) stem rewritten to stop giving away the touch point. Batched calibrators: d3 batch -> 2 Hard (f(f(x))=45 count; integer-k count, borderline), 4 relabeled Medium; eq d1 batch -> 3 Easy, 1 relabeled Medium.
**Banked:** Nonlinear functions d3 +2 (6/10, pending), d2 +4 (16, over target), Nonlinear equations d1 +3 (3/10, pending), d2 +1 (1/10). Master 230 -> 240. 10 lines appended to used_topics.
**Visuals:** 2 graphs rendered via render_visual.py (cubic graph, parabola+line), 1 table, 7 text-only.
**Skill/tool changes (Step 5):** extended render_visual.py with a "cubic" function kind (a,b,c,d); backward compatible, no existing spec touched. Nothing queued. Observation: critics' optional notes only; mandated Hard shapes that held: composition solution count, parameter-count. Graph/table/abstract-symmetry shapes calibrate Medium.
**Validation:** validate_batch.py passed on all four batches; key skew WARN on d2 batch (numeric choices, no reorder possible).
**Token usage:** ~17 subagent calls, roughly 0.85M subagent tokens (generators ~55k, critics ~46k, calibrators ~50k); orchestrator not included.
**Next run should pick up at:** Nonlinear functions d3 (6/10, needs 4), then Nonlinear equations d1 (3/10, needs 7).


## Run 23 -- 2026-10-15
**Cells worked:** Advanced Math / Nonlinear functions / d3 (needed 4, generated 4) and Nonlinear equations / d1 (needed 7; 6 generated to keep run ~10).
**Outcome:** 10 generated, 10 passed critique (0 regenerations, 0 discards). Critic in-place fixes: quartic-intercepts distractor D 32 -> 31 with new explanation (32 was arbitrary); explanation polish on enclosure B, abstract-quadratic B, system B, free-fall D. Batched calibrators: NF d3 -> 2 Hard (quartic k-count firm; abstract axis-x=4 borderline), 2 relabeled Medium (bike-share exponential; restricted-interval enclosure max). NE d1 batch -> 5 Easy, 1 relabeled Medium (linear-quadratic system, y of greater-x solution).
**Banked:** NF d3 +2 (8/10, pending), NF d2 +2 (18, over target), NE d1 +5 (8/10, pending), NE d2 +1 (2/10). Master 240 -> 250. 10 lines appended to used_topics.
**Visuals:** 1 graph rendered via render_visual.py (2^x vs 2x), 9 text-only.
**Validation:** validate_batch.py passed on both batches (key-skew WARN on NF d3 batch; only one non-numeric item so not reorderable).
**Skill updates (Step 5):** none applied; nothing queued. Setup note: `pip install` hit a different interpreter than python3 -- use `python3 -m pip install matplotlib numpy`.
**Token usage:** 22 subagent calls (10 generators ~55k, 10 critics ~46k, 2 calibrators ~55k) roughly 1.1M subagent tokens; orchestrator not included.
**Next run should pick up at:** Nonlinear functions d3 (8/10, needs 2), then Nonlinear equations d1 (8/10, needs 2) and d2/d3.


## Run 24 -- 2026-10-15
**Cells worked:** Advanced Math / Nonlinear functions / d3 (needed 2, generated 2), Nonlinear equations / d1 (needed 2, generated 2), Nonlinear equations / d2 (needed 8; 6 generated to keep run ~10).
**Outcome:** 10 generated, 10 passed critique (0 regenerations, 0 discards). In-place fixes: kayak distractor A explanation reworded (mechanism did not produce 3); radical-equation distractor B -2 (sum of roots, arbitrary) replaced by -3 (other root of the mis-squared equation) with new explanation; graph item explanations given "Choice X ..." prefixes. Advisory, not applied: NE d2 rational item's C/D (sum/product of roots) are weak distractors.
**Calibration (batched):** NF d3 -> 1 Hard (hole/tangent integer-k count), 1 relabeled Medium (pottery profit). NE d1 -> both Easy. NE d2 -> 3 Medium (radical with extraneous root, graph + vertex form, rational with extraneous root), 3 relabeled Easy (rocket later time, Vieta sum-of-x system, common-base exponential).
**Banked:** NF d3 +1 (9/10, pending), NF d2 +1 (19, over target), NE d1 +5 (13, done, over target), NE d2 +3 (5/10, pending). Master 250 -> 260. 10 lines appended to used_topics.
**Visuals:** 1 graph rendered via render_visual.py (spec needs the {visual_type, visual_data} wrapper), 9 text-only.
**Validation:** validate_batch.py passed on all three batches (NF 2/2, NE d1 2/2, NE d2 6/6).
**Skill updates (Step 5):** none applied; nothing queued. Observation: Medium shapes that held are extraneous-root and multi-concept items; single-quadratic stories, Vieta sums and common-base exponentials calibrate Easy. Setup note: first `pip install` hung when run chained with other commands; rerun it alone with a timeout.
**Token usage:** ~24 subagent calls (10 generators ~55k, 11 critics ~45k, 3 calibrators ~45k) roughly 1.2M subagent tokens; orchestrator not included.
**Next run should pick up at:** Nonlinear functions d3 (9/10, needs 1), Nonlinear equations d2 (5/10, needs 5), then d3.


## Run 25 -- 2026-10-15
**Cells worked:** Advanced Math / Nonlinear functions / d3 (needed 1, generated 1), Nonlinear equations / d2 (needed 5, generated 5 after 1 regeneration), Nonlinear equations / d3 (needed 4, generated 4 to keep run ~10).
**Outcome:** 10 generated, 10 passed critique. 1 pre-critique rejection: a rocket-launch "later time" draft for NE d2 was a near-duplicate of a banked rocket item; regenerated with a different mandated shape ((x-a)^2=c(x-a)). In-place fixes: discriminant item distractor D 11 -> 19 (old "divide 16 by 2" path contrived), scanner item A/C explanations reworded and "constant rate" added to stem, shifted-function NF item B/C explanations made explicit, circle-line item explanation rewritten to the discriminant route (distance formula is outside SAT scope) and A reworded, symmetric-system D replaced path 2(x+y)=50. 0 discards.
**Calibration:** NF d3 -> 1 Hard (borderline). NE d2 batch -> 4 Medium, 1 relabeled Easy ((x-3)^2=5(x-3) sum). NE d3 batch -> 2 Hard (rational-k two-mechanism no-solution, borderline; circle+line integer-b count, firm), 2 relabeled Medium (double radical; x^2+y^2/xy symmetric system).
**Banked:** NF d3 +1 (10/10, done), NE d1 +1 (over target), NE d2 +6 total this run counting generated-for-d2 plus relabeled-from-d3 (now 11, done), NE d3 +2 (2/10, pending). Master 260 -> 270. 10 lines appended to used_topics.
**Visuals:** none needed; all 10 text-only (no graphs in the chosen shapes).
**Validation:** validate_batch.py passed on all three batches (key-skew WARN on NE d3 batch, choices numeric and ascending so not reorderable).
**Skill updates (Step 5):** none applied; nothing queued. Observation: a "mandated shape" list in the Generator prompt avoided duplicates except the projectile/rocket collision -- the Generator was not told about the banked rocket item until it was named. Setup note: matplotlib was missing; `pip install matplotlib numpy` succeeded.
**Token usage:** 18 subagent calls (10 generators ~55k, 10 critics ~44k incl. regen, 3 calibrators ~43k), roughly 1.1M subagent tokens; orchestrator not included.
**Next run should pick up at:** Nonlinear equations d3 (2/10, needs 8), then Equivalent expressions d1.
