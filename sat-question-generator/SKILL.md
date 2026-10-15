---
name: sat-question-generator
description: Generates SAT practice questions (Math and Reading & Writing) for ScoreLab AI's question bank, using a three-stage generate -> adversarial-critique -> difficulty-calibration pipeline instead of a single naive generation pass. This is what catches the exact failure mode you get from asking a model for SAT questions directly: grammar or usage questions where more than one answer choice is technically defensible, or difficulty tags that don't match real SAT norms. Use this skill any time the user asks to generate SAT questions, build out or expand the ScoreLab AI question bank, create Math or Reading & Writing practice problems, or mentions needing verified single-answer SAT-style content -- even if they just say "make some more questions," "generate a batch for [skill]," or reference a skill category and difficulty level without naming the skill explicitly.
---

# SAT Question Generator (ScoreLab AI)

## Why this exists

A single LLM call asked to "write an SAT grammar question" reliably produces questions where more than one answer choice is defensible -- the model doesn't have anything forcing it to check its own work. This skill fixes that by treating question generation as a pipeline with three distinct roles, each played by a separate subagent so the critique step doesn't share the generator's blind spots:

1. **Generator** -- drafts the question against a strict rubric for one skill/difficulty combination.
2. **Critic** -- receives only the question and four choices (never told which is correct) and tries to build the strongest possible case for each one. If it can defend more than one, or can't defend the intended answer, the question is flagged.
3. **Calibrator** -- checks that the difficulty tag actually matches real SAT difficulty norms for that skill category, not just what the generator claimed.

Only questions that survive all three stages get assembled into the final batch.

## Before you start

You need:
- **Domain**: `math` or `reading_writing`
- **Skill category and subcategory**: see `references/sat-taxonomy.md` for the official Digital SAT breakdown. If the user names a skill informally ("grammar questions," "linear equations"), map it to the closest official category/subcategory yourself and confirm briefly if it's ambiguous.
- **Difficulty**: 1 (easy), 2 (medium), or 3 (hard)
- **Count**: how many questions to produce. Default to batches of 10-20 per skill/difficulty combination -- large enough to be efficient, small enough that a human can spot-check the output without it becoming a chore. If the user asks for a much larger number, run it as multiple sequential batches rather than one giant pass, so partial progress survives if something goes wrong midway.

If the user hasn't specified all of this, ask -- don't guess at domain or skill category, since that determines which rubric the generator uses.

## The pipeline

Run this per question, not per batch -- each question gets its own generator call, critic call, and (if needed) calibration call, so problems in one question don't get diluted across a batch. Use the Agent tool to spawn each subagent; keep them isolated (a fresh subagent per call) so the critic never inherits the generator's framing.

**Model:** pass `model: "sonnet"` explicitly on every Agent call in this pipeline (Generator, Critic, Calibrator). Sonnet has been sufficient for all three roles in testing -- it caught real ambiguity and calibration errors without needing Opus anywhere in the chain -- and pinning it explicitly avoids accidentally defaulting to a pricier model on a pipeline that runs unattended on a schedule.

### Step 1: Generate

Spawn a subagent with this task:

```
You are drafting one SAT [Math|Reading & Writing] question for ScoreLab AI's question bank.

Domain: {domain}
Skill category: {skill_category}
Skill subcategory: {skill_subcategory}
Difficulty: {difficulty} (1=easy, 2=medium, 3=hard)

Read C:\...\sat-question-generator\references\sat-taxonomy.md for what this skill category actually tests,
C:\...\sat-question-generator\references\questions-schema.md for the exact output fields required,
C:\...\sat-question-generator\references\topic-diversity.md for how to pick a scenario/passage subject that
doesn't repeat what's already in the bank -- check the used-topics log it points to before you commit to a
scenario -- C:\...\sat-question-generator\references\explanation-style.md for exactly how to write the
explanation and distractor_*_explanation fields so they match College Board's own published answer-explanation
convention, C:\...\sat-question-generator\references\distractor-patterns.md for the specific, real,
nameable patterns wrong answers should be built from, and
C:\...\sat-question-generator\references\item-design-rules.md for the ways an item can be broken even when
every individual distractor is fine (choice ordering, boundary points, gridline alignment, discrete-context
integers, context coherence). Every rule in that last file came from a real defect caught in a previous run.

You have READ-ONLY access for this task. Do not create, edit, or append to any file -- in particular do not
touch the used-topics log; the orchestrator updates it after a question is actually accepted. Your entire
output is the JSON object.

Requirements:
- Match official Digital SAT format and length exactly, including the passage-length-by-domain sub-ranges and
  fixed boilerplate question stems documented in sat-taxonomy.md (e.g. Words in Context completion items use
  "Which choice completes the text with the most logical and precise word or phrase?" verbatim).
- Order purely numeric answer choices ASCENDING (A smallest, D largest). This is a hard Digital SAT
  convention and the batch validator fails on it.
- Where the choices are NOT purely numeric (statements, expressions, inequalities, ordered pairs),
  group them sensibly and then check where the key landed. Do NOT instruct the Generator to avoid a
  specific letter: run 11 told ten generators "don't key A" and got A=1, B=3, C=4, D=2 -- the skew
  simply moved to C. Ask for a sensible grouping, then fix any batch-level skew at assembly by
  reordering the non-numeric items (moving `correct_answer` and the `distractor_*_explanation`
  fields with them), which is what `validate_batch.py`'s key-distribution WARN is there to prompt.
- If the scenario counts something discrete (people, tickets, devices, animals), the solution must come out
  as a whole number. Verify this before submitting.
- If the question uses a PIECEWISE model (a rate or rule that changes at some point -- the workhorse shape for
  hard Algebra items), evaluate BOTH branches at the changeover point and confirm they give the same value
  before submitting. A stated validity interval makes the math unambiguous but does not make a physically
  impossible jump acceptable; run 9 had a draft flagged for putting a tree trunk at 26 cm just before age 40
  and 62 cm at age 40. Fix a mismatch by adjusting a branch's constant, not its slope.
- Exactly one answer choice must be correct. Every distractor must be built from one of the specific, nameable
  patterns in distractor-patterns.md (e.g. a named grammar-rule violation, a wrong-part-of-figure value, an
  inverted word meaning, a data point misread from the wrong row/column) -- not a vaguely "awkward" or
  "less good" option. If you can't name which pattern a distractor uses, rewrite it before submitting. For
  grammar/usage questions (Standard English Conventions) specifically, this means every distractor must violate
  a SPECIFIC, NAMEABLE rule -- write that rule into the distractor's explanation field.
- If the item is an abstract "which must be true" structural item -- the shape that carries most of the Hard
  tags in the Algebra cells -- three extra checks apply before you submit, all from run 12's downgrades and
  Critic flags. (a) Each distractor must be falsified by a DIFFERENT concrete function; if one witness kills
  all three, the item calibrates Medium. (b) Substitute whatever the stem forces (a zero intercept, a fixed
  point) into every choice and confirm no two choices reduce to the SAME condition on the free parameter --
  logically equivalent choices let a student eliminate both for free. (c) If the choices are intervals, the
  keyed interval must not contain two or more of the others, or the widest-interval heuristic answers the item;
  note that a replacement distractor cannot merely be wider, since any interval containing the guaranteed one
  would be a second correct answer.
- Do not fabricate a passage and attribute it to a real, identifiable author or work -- see sat-taxonomy.md's
  source attribution guidance and use a generic, non-identifying framing instead.
- Write the explanation field to justify the correct answer, and a distractor explanation for each of the
  other three choices explaining exactly why it's wrong, following explanation-style.md precisely -- this is
  student-facing content and is NOT a place to economize on quality or length for cost reasons, even if other
  parts of this pipeline are optimized for token cost.
- Decide whether this question needs a visual (graph, table, or geometric figure) the same way the real Digital
  SAT would for this skill category -- check the visual guidance next to your skill category in
  sat-taxonomy.md. This isn't Math-only: Reading & Writing's Command of Evidence (Quantitative) needs a
  table or graph essentially always, the same way Math's Geometry and Trigonometry and Two-variable data do.
  Don't skip a visual just because a text-only version of the question is easier to write.
  If a visual is needed, set has_visual: true, visual_type accordingly, and write visual_data as precise
  structured numbers (never prose) following the spec format documented in scripts/render_visual.py's docstring.
  Leave visual_svg null -- you don't render it, the orchestrator does that in the next step.
  The renderer supports a SINGLE curve, TWO OR MORE curves on one grid (`functions`, for a system of
  equations where the answer is the intersection), SHADED half-planes with solid/dashed boundaries
  (`chart_type: "inequality"`, for linear inequalities and systems of them), scatterplots, bar charts,
  and the geometry shapes. If the question asks the student to READ A VALUE OFF the graph, you must set
  `x_tick_step` and `y_tick_step` so the queried point and all four answer choices land on labeled
  gridlines -- see item-design-rules.md, "Graph-read items".
- Output one JSON object matching the schema in questions-schema.md. Nothing else in your response.
```

**Give each Generator a MANDATED SHAPE, not just a list of scenarios to avoid.** Run 11 ran ten
generators against one cell and gave each a different explicit structural mandate ("an abstract
'which must be true' item where two distractors are true for some qualifying functions but not all,
so eliminating them requires generating a counterexample"; "a graph where reading the graph is only
the first step and a second function contains an unknown constant fixed by a stated condition"; and
so on), each with the cell's confirmed-Hard and confirmed-Medium findings pasted in. Not one of the
ten collided with another or with the bank, so no near-duplicate rejection was needed at all -- the
first run since the near-duplicate rule was written to spend nothing on that failure mode. Naming
the shape also makes the Calibrator's verdict interpretable: you learn which *shape* calibrated
down, not just which question did. Write the mandate from the receiving cell's tracker `note`.

Before sending the draft to critique, the orchestrator does two cheap deterministic checks:

- **Near-duplicate check.** Compare the new question's scenario AND its underlying numbers against the
  used-topics log and the master bank. A question that reuses a shape already in the same cell (e.g. another
  `x + y = <total>` / `x - y = <difference>` system when one is already banked) should be rejected and
  regenerated *before* spending a Critic call on it, with the specific collision named in the regeneration
  prompt. Run 6 caught one this way; it is much cheaper than discovering it after critique. Compare on
  SHAPE, not nouns -- see "Near-duplicates within a cell" in `references/item-design-rules.md` for the four
  axes to check (shape family, source of the key structure, direction of the solve, ingredient list). Run 10
  rejected an item here that differed from a banked one only in industry and numbers. When a cell's
  confirmed-Hard shape family is already saturated, the Generator prompt should mandate a specific variation
  (a different direction of solve, a different source for the hidden structure) rather than only listing
  scenarios to avoid.
- **Choice ordering.** If the four choices are purely numeric and not ascending, fix the order and move
  `correct_answer` and the `distractor_*_explanation` fields along with them before critique.

### Step 1b: Render the visual (if applicable)

If the generated question has `has_visual: true` and `visual_type` is `"graph"` or `"geometry"`, render it yourself (the orchestrator) by writing `visual_data` to a temp JSON file and running:

```
python scripts/render_visual.py <spec.json> <output.svg>
```

This is a deterministic script, not a subagent call -- no tokens, no model involved. Read the resulting SVG file and set the question's `visual_svg` field to its contents. If `visual_type` is `"table"`, skip this step entirely -- `visual_data` alone is what the frontend needs, there's nothing to render. If the script errors (malformed spec), that's a signal the Generator's visual_data was invalid -- treat it like a flagged question and regenerate with the specific error message.

### Step 2: Adversarial critique

Take the generator's JSON output and spawn a **new, separate subagent** (don't reuse the generator's context) with:

```
You are adversarially reviewing one SAT question before it enters a paid product's question bank. You are NOT
told which answer is "correct" -- figure out independently whether the question has exactly one defensible
answer.

Question: {question_text}
A: {answer_a}
B: {answer_b}
C: {answer_c}
D: {answer_d}
{if has_visual: include visual_data here, e.g. "This question references a graph/figure described by
this data: {visual_data}"}

For each of the four choices, argue the strongest possible case that it is the correct answer. Be genuinely
adversarial -- you're trying to find a flaw, not confirm the question is fine.

If this question has a visual, also check that the visual_data actually matches what the question text and
correct answer claim -- e.g. if the question says "the line passes through (0, -3)" the function's intercept in
visual_data must actually be -3, and if the answer depends on reading a specific point off a scatterplot, that
point must actually be in the points list. A visual that doesn't match the text is exactly as bad as an
ambiguous answer choice -- flag it the same way. If the student must read a value off the graph, also check
that the queried point and all four choices fall on LABELED gridlines given the tick steps in visual_data.

Then check the STEM for internal consistency, independent of the answer choices:
- Is every quantity defined once and used consistently, with no term defined two different ways?
- Could any noun phrase be read two ways by a careful student?
- Does the real-world scenario actually support the algebra? A negative coefficient in a story about
  quantities sold, two different prices for the same item across two equations, or a physically discrete
  quantity that comes out fractional are all real defects even when the math has a unique answer.

Then check the ANSWER-CHOICE SET as a set, which is where run 12 found four defects the mathematics didn't
reveal:
- Are any two choices logically EQUIVALENT once the stem's constraint is applied, so they must stand or fall
  together? A student can eliminate both without doing the mathematics.
- If the choices are intervals or ranges, does one choice CONTAIN two or more of the others, so that "pick the
  widest" answers the item?
- Is any choice true only at a single exact parameter value, making it effectively always false?
- Does one concrete counterexample falsify more than one choice at once?

Finally, audit the EXPLANATIONS, which are shown to students and are part of the product:
{include the explanation and all three distractor_*_explanation fields here}
For each distractor explanation, actually RUN the error it describes and confirm that error produces THAT
choice's value. An explanation that describes a mechanism leading to a different choice is a defect --
it ships to a paying student at the moment they got the question wrong. Also say whether any distractor
looks arbitrary, i.e. no named error path plausibly produces it.

Then report:
1. Which choice(s) you could build a real case for (ideally exactly one).
2. Whether the question has any factual, logical, or grammatical flaw independent of the answer choices,
   including stem self-consistency and context coherence.
3. If applicable, whether the visual_data matches the question's and answer's claims.
4. For each distractor explanation: does the mechanism it names actually produce that choice's value?
5. Whether any distractor is arbitrary rather than built from a nameable error.
6. A verdict: PASS (exactly one defensible answer, no flaws, visual matches, explanations accurate) or
   FLAG (multiple defensible answers, a flaw, a visual/text mismatch, or an inaccurate explanation).

If FLAG, explain specifically what's wrong so the question can be rewritten.
```

**Add a named concern to the Critic prompt when the orchestrator has already spotted something.**
Between generation and critique the orchestrator reads the draft anyway (for the ordering and
near-duplicate checks). Anything that looks off during that read -- a choice that is orders of
magnitude out of scale, a constant repeated across two given expressions, a model whose value at
zero contradicts its stated baseline, a pair of choices that are logical negations, an explanation
whose mechanism looks compound -- should be written into the Critic prompt as an explicit
"ALSO EVALUATE THIS SPECIFIC DESIGN CONCERN" paragraph, asking for a verdict AND a concrete
replacement value or wording if the concern holds. Run 11 did this on six of ten items; every one
came back with a specific, verified fix (a replacement distractor with its own error path, an exact
stem rewording) rather than a vague "consider revising", which is what makes the difference between
a FLAG you can apply in place and a FLAG that costs a regeneration. Keep the paragraph as a genuine
question -- "assess whether X is a defect, and if so propose a fix" -- not an assertion, so a
critic that disagrees can say so. Two of run 11's named concerns came back "not a defect", with
reasoning, and were correctly dropped.

If the critic's chosen answer doesn't match the generator's `correct_answer`, or the verdict is FLAG, treat this as a failure (see "Handling flagged questions" below).

**Not every FLAG needs a full regeneration.** Sort the critic's findings into three buckets:
- *Correctness* (multiple defensible answers, wrong key, visual/text mismatch, incoherent context) -> full
  regeneration per "Handling flagged questions".
- *Explanation-only* (a distractor explanation names a mechanism that doesn't produce its value) -> the stem,
  choices, and key are untouched, so apply the critic's corrected wording directly. The critic supplies the
  right mechanism as part of its report; no second Generator call is needed. Record it in the run log.
- *Advisory* (a weak-but-not-wrong distractor, a stylistic nitpick) -> your judgement. Fixing a weak distractor
  by swapping one value is cheap and usually worth it; verify the replacement isn't defensible as correct.

An explanation-only or advisory fix does not need a re-critique, since the question the critic evaluated has
not changed. A correctness fix always does.

### Step 3: Difficulty calibration

Only run this on questions that passed Step 2. Spawn another subagent:

```
Check whether this SAT question's actual difficulty matches its claimed difficulty tag.

Question: {question_text}
Skill category: {skill_category}
Claimed difficulty: {difficulty} (1=easy, 2=medium, 3=hard)

Reference real Digital SAT difficulty norms for this skill category (sentence/passage complexity, number of
solution steps, how many concepts must be combined, vocabulary level). Report whether the claimed difficulty
is honest, and if not, what it should be.
```

If the calibrator disagrees with the difficulty tag, correct the `difficulty` field rather than discarding the question -- a mistagged-but-otherwise-valid question is still usable once relabeled.

**Give the calibrator the cell's accumulated findings.** Every cell in the progress tracker carries a `note`
recording which shapes have calibrated Easy/Medium/Hard for that exact skill and difficulty. Paste the relevant
findings into the calibrator prompt as a working rubric. Without them the calibrator reasons from generic SAT
norms and produces inconsistent verdicts across runs; with them, verdicts are stable and the note compounds.

**Calibration may be batched.** Unlike critique, calibration has no isolation requirement -- there is no answer
key to hide -- so several questions can go to one calibrator call as long as the prompt says to evaluate each
independently and return a separate verdict per question. Runs 6 and 7 both did this and it cut calibration
cost substantially with no loss of signal. Generation and critique must stay one-subagent-per-question.

**Where a relabeled question gets banked.** Put it in the cell matching its corrected difficulty, even if that
cell is already at target. Do not discard it and do not leave it mistagged. Overshoot is acceptable and several
cells are well past 10 as a result; a wrongly-tagged question in the right-sized cell is worse than a correctly
tagged question in an oversized one. Note the overshoot and its cause in the receiving cell's tracker note, and
remember the cell the question was *generated* for still needs one more.

### Step 4: Assemble and validate

Once a question has passed critique (and had its difficulty corrected if needed), add it to the batch's output JSON array. After the full batch is done, run `scripts/validate_batch.py` against the output file. This is a fast deterministic check that doesn't need another subagent call. It verifies:

- structural completeness (all required fields, exactly one `correct_answer` in A-D, four non-empty distinct choices, all three distractor explanations present)
- `skill_category` / `skill_subcategory` are real entries in the official taxonomy -- a Generator once invented a plausible-sounding subcategory that would have created an orphan cell in the bank
- purely numeric answer choices are in ascending order
- the answer key and the explanations agree: the correct choice carries no distractor explanation, `explanation` names the correct letter, and each distractor explanation names its own letter (this is what catches a botched choice reorder)
- visual field consistency, and the mandatory-figure categories
- nested interval choices: a WARN when the keyed choice is a numeric interval containing two or more of the
  other choices (added run 12)
- no two questions in the batch share a stem

A batch must pass before it is merged into the master bank. If a check fails, fix the batch and re-run -- don't merge past a failure.

## Handling flagged questions

Don't just discard a flagged question -- that wastes the generation cost and tells you nothing. Instead:

1. Spawn one regeneration attempt: give the generator subagent the critic's specific flag reasoning and ask it to fix that exact issue (not start over from scratch).
2. If the flag was about visual_data (mismatch with the question text, or a render_visual.py error), the regeneration only needs to fix visual_data -- re-run Step 1b to render the corrected version before sending it back to critique.
3. Run the regenerated question through the critic again.
4. If it fails a second time, discard it and note it in your summary to the user -- some skill/difficulty combinations are just harder to generate cleanly (grammar boundary questions especially), and that's useful signal, not noise.

## Step 5: Fold what you learned back into this skill

**Run this at the end of every batch, before writing the run log.** It is not optional and it is not a
"if there's time" step.

The reason it exists: for the first seven runs, findings went into the run log and stayed there. The gridline
defect was diagnosed in run 5, manually worked around in run 6, and was still not in the skill by run 7 — every
run rediscovered it or got lucky. Extending `render_visual.py` was recommended in runs 6 and 7 and deferred
both times. A skill that doesn't absorb its own findings makes the same mistakes indefinitely.

Go through this run's Critic FLAGs, calibration surprises, near-duplicate rejections, validator failures, and
anything you had to explain to a subagent that the reference files should have told it. For each finding,
decide which bucket it's in.

**Apply directly (safe — do these yourself, now):**
- A new item-design rule -> add it to `references/item-design-rules.md` with the run number attached.
- A new distractor pattern, or a pattern confirmed weak -> `references/distractor-patterns.md`.
- A mechanically checkable defect -> add a check to `scripts/validate_batch.py`, then **run it against the
  whole master bank** to confirm it doesn't false-positive on already-accepted questions. If it flags existing
  questions, they are probably genuinely defective — assess before assuming the check is wrong.
- A renderer limitation you had to work around -> extend `scripts/render_visual.py`, then re-render every
  existing spec in the bank to prove backward compatibility.
- Wording that had to be added to a Generator/Critic/Calibrator prompt to get a good result -> put it in the
  prompt template in this file so the next run gets it for free.
- Cell-specific calibration findings -> the cell's `note` in the progress tracker (already routine).

**Queue for human review (do NOT apply unattended):** append to `scorelab_skill_review_queue.md` in the
Claude Creations folder, with the run number, what prompted it, and a concrete proposal.
- Anything changing the pipeline's *structure* — dropping a stage, changing what the Critic is or isn't told,
  changing subagent isolation.
- Anything changing model selection or the cost/quality tradeoff.
- Anything changing what difficulty 1/2/3 *means*, or target counts.
- Anything you'd be applying on a single run's evidence where you're genuinely unsure it generalizes.
- Anything touching student-facing tone or the College Board conventions in `explanation-style.md`, since
  those were validated against real practice tests and shouldn't drift on one run's impression.

Rules for the safe bucket: make the smallest edit that captures the finding, always attach the run number so a
future reader can trace it, and never delete an existing rule to resolve a conflict — if a new finding
contradicts an old one, add it alongside and queue the conflict for review. If a finding recurs across three
runs and is still sitting in the review queue, say so prominently in the run log rather than quietly requeueing.

Then note in the run log which files you changed and what you queued.

## Output format

Deliver the batch as a single JSON array (one object per question) matching `references/questions-schema.md`, saved to a file the user can review, plus a short summary: questions requested, questions accepted, questions regenerated once and passed, questions discarded after two failures (with the reason for each).

## Reference files

- `references/sat-taxonomy.md` -- official Digital SAT domain/skill/subcategory breakdown and content norms. Read this before generating anything in a skill category you haven't handled yet in this session.
- `references/questions-schema.md` -- exact output schema matching ScoreLab AI's Supabase `questions` table.
- `references/item-design-rules.md` -- ways an item can be broken even when every distractor is individually fine: choice ordering, answer-key placement, boundary points, discrete-context integers, gridline alignment, weakly-diagnostic shapes, context coherence, explanation accuracy. Every rule traces to a real defect from a numbered run. Read alongside `distractor-patterns.md`.
- `references/topic-diversity.md` -- how to pick scenarios/passage subjects that don't repeat what's already in the bank.
- `references/explanation-style.md` -- College Board's actual answer-explanation convention, with real examples, for the student-facing explanation fields.
- `references/distractor-patterns.md` -- real, nameable distractor-construction patterns pulled directly from official practice tests, for both Math and Reading & Writing. Read this before writing any distractor -- it's the most direct fix for the original ambiguous-answer problem this whole pipeline exists to catch.
- `scripts/validate_batch.py` -- run this on the assembled batch before handing it back to the user.
- `scripts/render_visual.py` -- deterministically renders a graph or geometry visual_data spec into SVG. Read its docstring for the exact spec format before writing visual_data. Never generate SVG markup yourself as text -- always run this script.
