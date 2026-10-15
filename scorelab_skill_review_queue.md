# ScoreLab Skill Review Queue

Proposals the automated runs deliberately did **not** apply on their own, because they change pipeline
structure, cost/quality tradeoffs, or what a difficulty tag means. Each entry says what prompted it and
what the concrete change would be, so you can accept or reject without re-deriving the context.

Runs append here at Step 5 of the pipeline. Safe fixes are applied directly and recorded in the run log
instead; only judgement calls land in this file.

**How to clear an item:** decide, then either apply it and delete the entry, or mark it `REJECTED` with a
one-line reason so future runs stop re-proposing it.

---

## Open

### 1. Is a 10-question target realistic for hard single-variable linear equations? (raised run 3, still open)
**Prompted by:** Algebra / Linear equations in one variable / d3 took **31 hard attempts across five runs to
land 10 accepted** — a 32% yield. The other 21 were calibrated down to Medium and banked there, which is why
that d2 cell now sits at 28/10.
**Proposal:** either lower `target_count` for d3 cells to 5, or accept the low yield and budget ~3x the
generation cost for every d3 cell. This affects every remaining d3 cell in the tracker (there are many, and
only one has ever been attempted), so it's worth deciding before a run starts on a fresh one.
**Why not applied automatically:** changes target counts, which is a product decision about bank shape.

### 2. Overshoot cells are absorbing a lot of relabeled questions (raised run 4, still open)
**Prompted by:** Linear equations in one variable d2 is at **28/10**, Linear equations in two variables d1 at
11/10, purely from questions relabeled by the Calibrator and banked per SKILL.md rather than discarded.
**Proposal:** either cap how far a cell can overshoot (and start discarding beyond it), or explicitly bless
overshoot and stop treating `target_count` as a ceiling. Currently the skill says bank them, and the tracker
says the cell is "complete" while it keeps growing — internally consistent but probably not intended.
**Why not applied automatically:** changes what the target counts mean.

### 3. Should the Critic see the difficulty tag? (raised run 7)
**Prompted by:** The Critic is deliberately not told the correct answer, which works well. It is also not told
the claimed difficulty — that goes only to the Calibrator. Several Critic reports this run included difficulty
observations anyway ("this is a lot of steps for an Easy item"), which the Calibrator then re-derived.
**Proposal:** consider passing the difficulty tag to the Critic as context, or explicitly instructing it to
ignore difficulty. Either would remove duplicated reasoning; the current state is ambiguous.
**Why not applied automatically:** changes what the Critic is told, which is the isolation the pipeline
depends on. Not something to alter on one run's impression.

### 4. Calibration batching is now sanctioned — watch whether verdicts drift (raised run 7)
**Prompted by:** Runs 6 and 7 both batched several questions into one Calibrator call to cut cost, and SKILL.md
has now been updated to allow it. Batching is safe in principle (no answer key to hide) but has not been
A/B'd against per-question calibration.
**Proposal:** on some future run, calibrate one cell both ways and compare verdicts. If batched calibration is
more lenient or more prone to anchoring on the first question in the batch, revert to per-question.
**Why not applied automatically:** it's a validation task with a cost, not a fix.

### 5. Generator subagents can write files despite read-only instructions (raised run 9)
**Prompted by:** The Generator prompt says, in bold terms, "You have READ-ONLY access for this task. Do not
create, edit, or append to any file." One of run 9's seven Generators wrote `question_output.json` into the
scratch outputs directory anyway, then disclosed it unprompted in its final message. No harm done — it landed
in the throwaway outputs folder, not the Claude Creations folder, and did not touch the used-topics log, which
is the file the instruction actually exists to protect. But the instruction is currently enforced by nothing
except the subagent's cooperation, and it was only caught because that subagent volunteered it.
**Proposal:** spawn Generator, Critic, and Calibrator subagents with a restricted tool set (read and search
tools only, no Write/Edit) rather than relying on prompt text, so the guarantee is structural. If the Agent
tool in this environment can't restrict tools per call, the fallback is for the orchestrator to snapshot the
mtime of `scorelab_used_topics.md` before each Generator call and verify it afterward.
**Why not applied automatically:** changes the pipeline's subagent configuration and isolation model, which
SKILL.md Step 5 reserves for human review.

### 6. Should a required visual count toward difficulty? (raised run 9)
**Prompted by:** Run 9's water-hyacinth item gives the first branch of a piecewise model *only* as a graph, so
the student must read the slope and intercept off it before they can build anything. The Calibrator held the
item at Hard but explicitly called the graph-read "a superficial wrinkle, not a change in kind," crediting the
branch construction alone. Read against the governing principle this cell has accumulated ("added steps do not
make an item Hard, only a change in KIND of reasoning does"), that implies visuals never contribute to
difficulty — they change the presentation, not the reasoning.
**Proposal:** decide whether that's the intended stance. If it is, say so in `sat-taxonomy.md` so Generators
stop treating a visual as a way to reach a difficulty tag, and keep requiring visuals purely for format
fidelity. If it isn't, the Calibrator prompt needs to say what a visual is worth.
**Why not applied automatically:** it bears on what difficulty 1/2/3 means, and rests on one Calibrator remark
on one item.

### 9. Should a pure table-lookup item count as a legitimate Easy "Nonlinear functions" question? (raised run 17)
**Prompted by:** Run 17 opened the Advanced Math / Nonlinear functions / difficulty-1 cell and generated a
table item (a round-robin tournament's quadratic games-played function f, shown via a 5-row table, asking
for a direct lookup of f(7)). The Calibrator confirmed it honestly Easy under the literal rubric ("a direct,
explicitly-stated detail" is exactly the Easy bar), but flagged that the item never exercises anything
specific to quadratic or nonlinear reasoning — no formula use, no extrapolation, no curvature, nothing that
would change if f were linear instead. A student with zero understanding of what makes a function
"nonlinear" answers it correctly as easily as one who understands it.
**Proposal:** either (a) accept this as a legitimate Easy anchor/floor item for the cell (real Digital SAT
banks likely include some low-discrimination items), and leave the shape available for future Easy table
items in this and other nonlinear-function cells; or (b) tighten the mandate for future Easy table items in
this subcategory to require reading a value just OUTSIDE the given rows (extending the visible pattern by
one step), which keeps the step count low enough to stay Easy while at least touching the function's actual
behavior rather than being pure lookup.
**Why not applied automatically:** it's a content-validity/test-construct judgment call about what an Easy
item in this skill category should measure, not a correctness defect — exactly the kind of thing Step 5
reserves for human review rather than resolving on one run's impression.

---

## Resolved

*(none yet)*

## Run 10 (2026-09-01) -- run sizing vs. the account session usage limit

**What prompted it:** Run 10 hit the account's session usage limit ("resets 12:30pm") partway through its
second cell, killing two Generator subagents mid-flight. The run banked 2 of a planned 10 questions. The
scheduled task's own instructions cite staying under usage limits per period as the reason for the ~10
questions-per-run cap, so the current cap is evidently still too large for a 5-hourly cadence, at least on
days where earlier sessions have already consumed budget.

**Why this is queued rather than applied:** changing the per-run question target is explicitly in the
human-review bucket (it changes target counts and the cost/quality tradeoff), and one run's evidence does not
establish where the real ceiling is -- the limit may have been reached because of other activity on the
account today rather than because of this pipeline.

**Concrete proposal, for a human to accept or reject:**
1. Lower the per-run target from ~10 new questions to ~6, and let the higher run frequency make up the
   throughput. A run that completes is worth more than a larger run that dies halfway.
2. Alternatively, or in addition, have the orchestrator finish and bank cell-by-cell (already the rule) AND
   stop opening a new cell once the run has spent a set budget, rather than committing to a fixed count up
   front.
3. Add an explicit instruction for what to do when a subagent returns a usage-limit error: bank everything
   that has passed the full pipeline, write any un-critiqued drafts to a `scorelab_pending_*.json` file for
   the next run to pick up (run 10 did this by judgement, not by instruction), and record the interruption in
   the run log rather than retrying.

Item 3 is arguably safe to apply directly, but it is bundled here because it only makes sense alongside a
decision on 1 and 2.

---

## Item 8 — The Hard bar in Algebra may be unreachable at an acceptable cost (run 11)

**What prompted it:** Run 11 generated ten items for Algebra / Linear functions / difficulty 3, every one of
them built to an explicit Hard-shaped mandate drawn from the sibling cells' confirmed findings. All ten
passed adversarial critique. **The Calibrator kept exactly one at difficulty 3 and moved nine to difficulty 2.**
The cell went from 0/10 to 1/10 at a cost of ten Generator calls, eleven Critic calls and one batched
Calibrator call.

This is not an isolated result; it is the sharpest instance of a pattern now visible across every Algebra d3
cell in the tracker:

| cell | Hard attempts | confirmed Hard | downgrade rate |
|---|---|---|---|
| Linear equations in one variable d3 | 31 | 10 | 68% |
| Linear equations in two variables d3 | 16 | 10 | 38% |
| Linear functions d3 | 10 | 1 | **90%** |

And the downgrades land somewhere: **Linear functions d2 is now at 19 against a target of 10, and Linear
equations in one variable d2 is at 28.** The bank is not short of Medium items. It is short of Hard ones, and
the pipeline's response to that shortage is to manufacture more Medium ones.

The Calibrator is not being erratic — given the rubric it was handed, its nine downgrades are individually
well-argued and consistent with prior runs. The question is whether the rubric's bar is the right one.
The operative rule, inherited from run 7, is that *added steps never make an item Hard; only a change in the
KIND of reasoning does*. Under that rule, essentially one shape clears the bar in this subcategory: the
abstract "which must be true" structural item whose distractors require counterexamples. Ten of those in one
cell would be a repetitive cell, which the near-duplicate rule in `item-design-rules.md` exists to prevent.
**Those two rules are now in direct tension, and neither can be relaxed unilaterally by an unattended run.**

**Why this is queued rather than applied:** it touches what difficulty 1/2/3 *means* and the per-cell target
counts — both explicitly human-review territory — and it would change the cost/quality tradeoff. It is also
exactly the kind of finding that should not be resolved on one run's evidence, even though the run in
question is unusually informative.

**Concrete proposals, for a human to choose among (they are not mutually exclusive):**
1. **Lower the d3 target** from 10 to something like 5, on the view that real Digital SAT forms contain far
   fewer genuinely hard items per skill than 10, and a bank of 5 excellent Hard items beats 10 padded ones.
2. **Recalibrate the Hard bar.** The current rule may be stricter than College Board's own norms: on a real
   adaptive form, a long multi-stage mechanical chain with several plausible error paths *does* function as a
   hard item, because difficulty there is empirical (how many students miss it) rather than structural. If so,
   several of run 11's nine — the double unit conversion, the two-model inequality with directional rounding,
   the indirectly-pinned constant — plausibly belong at 3. Resolving this properly probably means checking
   the rubric against released College Board difficulty labels rather than reasoning from first principles.
3. **Stop banking downgrades into cells already well past target.** Once a cell is at, say, 150% of target,
   a downgraded question could be discarded (and the run log record it) instead of deepening an overshoot.
   This trades against the current rule that a correctly-tagged question in an oversized cell beats a
   mistagged one, which is sound in principle but has produced a 19/10 and a 28/10 cell.
4. **Accept the cost explicitly**, and record that d3 cells are expected to need roughly 10 attempts per
   accepted item, so run sizing and scheduling can be planned around it rather than being surprised each run.

**Interaction with item 7 (run sizing):** if proposal 2 is rejected and the cost is accepted, a ~10-question
run will keep yielding 1–3 bankable Hard items, and the ~6-question run size proposed in item 7 would yield
under one. Items 7 and 8 should be decided together.

**Note on item 1:** "is a 10-question target realistic for d3 cells?" has now been open since run 3. This is
its **fifth** consecutive run as an open item, and run 11 is the strongest evidence yet that the answer is no.
Item 8 supersedes item 1; they should be closed together.

### Run 12 evidence on item 8 — the shape, not the bar, was driving the yield (2026-09-01)

Run 12 worked the same cell (Algebra / Linear functions / d3) and followed run 11's own recommendation
literally: **all nine attempts were the abstract "which must be true" structural shape, varying only the
condition** (opposite-sign values at two inputs; two functions whose order reverses; one-sided domination on an
unbounded ray; an interval-constrained intercept; an interior extremum; a horizontal translation; a functional
equation; an upper bound on a ray; a graphed function paired with a constrained one).

**Result: 5 of 9 held at Hard — a 56% yield, against run 11's 10%.** The cell went 1/10 → 6/10 in one run.

This materially changes the picture item 8 paints, and the change should be weighed before any of its four
proposals is adopted:

- The Hard bar is **not** unreachable. When the Generator is pointed at the confirmed shape, more than half the
  attempts clear it. Run 11's 90% downgrade rate reflected ten *different* shapes being tried, only one of
  which was the confirmed one.
- The shape is **not** as narrow as feared. Four distinct conditions cleared the bar, in two mechanism families
  (sign-change/root-location, and asymptotic behaviour on an unbounded ray), each usable with one function or
  two. That is more headroom than "ten near-identical items", though not unlimited — the Calibrator explicitly
  flagged that this run's five Hard items are two pairs plus a singleton, and warned about saturation.
- So the tension item 8 identifies between the difficulty rubric and the near-duplicate rule is **real but
  softer** than one-shape-only. The open question is narrower: is a cell of ten items drawn from three or four
  mechanism families acceptable diversity, or not?
- The Calibrator also drew a **sharper line within the shape** than the rubric previously had, and it is worth
  ratifying or rejecting explicitly: an item is Hard only if each distractor needs its OWN counterexample. Two
  of this run's downgrades were items whose conditions determined the function completely (so no counterexample
  is constructible) and one where a single trivial witness killed all three distractors. That criterion has
  been written into `item-design-rules.md` as a design rule, but as a *calibration* criterion it belongs to a
  human, since it sharpens what difficulty 3 means.

**Proposal 3 is now more pressing, not less.** Linear functions d2 absorbed this run's four downgrades and
stands at **23 against a target of 10** — 230% of target, the largest overshoot in the bank, ahead of Linear
equations in one variable d2 at 28/10 in absolute terms only because that cell started earlier. Until proposal
3 is decided, runs will keep following SKILL.md and banking downgrades into a cell that has not needed items
since run 6.

**Item 1 is now on its sixth consecutive run open.** Run 12's evidence argues against its premise: a 10-item d3
target looks reachable at roughly two attempts per accepted item when the shape is chosen well, rather than
the ten attempts run 11 implied.

## Run 19 -- slim reference packs trial (2026-10-14)
**What prompted it:** user asked to try shrinking Generator reference reading to cut cost per question, with quality control the top priority.
**Built (not wired in):** `scripts/build_packs.py` plus `references/packs/{math,rw}_d{1,2,3}_pack.md`. Packs are verbatim concatenations of whole sections of the full reference files (domain-irrelevant sections dropped; Hard-shape item-design rules dropped only at difficulty 1). `--check` verifies the packs match the sources. Math d1 pack is 43.6 KB vs 58.8 KB full (-26%).
**A/B result (1 pair, same Easy quadratic graph-read mandate):** pack Generator 82.0k subagent tokens / 5 tool calls; full-files Generator 52.6k / 4 calls. Both outputs were correct, single-answer and gridline-aligned; the pack output followed the "Choice X is correct/incorrect" explanation convention while the full-files output omitted it. So: no measurable token saving on this sample (run-to-run variance and fixed subagent overhead dominate the ~4k tokens of reading saved), no quality loss either.
**Proposal:** do NOT wire the packs into SKILL.md yet. Revisit only if a larger sample (5+ pairs) shows a consistent saving; the bigger levers are batching several questions per Generator call and per Critic call (queued earlier), which change pipeline structure.
