# Official Digital SAT Structure

Source: College Board Digital SAT Suite Assessments Framework, as of 2026. Weights are approximate testing-blueprint targets College Board publishes for how the real test is composed -- use them to guide how you distribute a generated bank across categories, not as a hard constraint on any single batch.

Total test: 2 hours 14 minutes, two sections (Reading & Writing, then Math), each split into two adaptive modules with a break between sections.

---

## Reading & Writing (54 questions total: 27 per module)

Passages are short: 25-150 words, one question per passage. Keep generated passages within this range -- a long, essay-style passage is not Digital SAT format. Confirmed by direct word counts across 4 real practice tests, length varies meaningfully by domain, not uniformly across the full range:
- **Words in Context, Boundaries, Transitions** run shortest, typically 25-60 words -- often just one or two sentences.
- **Central Ideas, Text Structure and Purpose, Command of Evidence (both Textual and Quantitative)** run longer, typically 70-110 words -- these need enough room to establish a claim, a study, or an argument before the question can be asked.
Match these sub-ranges, not just the outer 25-150 bound -- a 100-word Words in Context passage or a 30-word Command of Evidence setup would both be off-model.

**Source attribution caution:** real literary excerpts carry an attribution line ("The following text is adapted from [Author]'s [year] [work]...") and sometimes a copyright line. Do not fabricate a quotation and attribute it to a real, identifiable author/title -- that risks putting inaccurate or misattributed content in front of students under a real person's name. Either write original passage text with a generic, non-identifying framing ("The following text is adapted from a work of literary fiction...", "The following text is from an article about...") or, if you use a genuinely public-domain source you can verify, attribute it accurately. When in doubt, use the generic framing -- it's indistinguishable to a student and carries no accuracy risk.

**Fixed boilerplate question stems** -- real tests reuse these verbatim rather than varying the phrasing; match them exactly rather than writing a creative paraphrase:
- Words in Context / completion items: "Which choice completes the text with the most logical and precise word or phrase?"
- Underlined-sentence function items: "Which choice best states the function of the underlined sentence in the text as a whole?"
- Command of Evidence (Quantitative): "Which choice best describes data from the [graph/table] that support [the claim/researcher's conclusion]?"

### Craft and Structure (~28%)
- **Words in Context** -- vocabulary-in-context, precise word choice given a passage.
- **Text Structure and Purpose** -- how a passage is organized, or why the author included a specific detail.
- **Cross-Text Connections** -- relationship between two short related passages (agreement, disagreement, one extending the other).

### Information and Ideas (~26%)
- **Central Ideas and Details** -- main point or key supporting detail of a passage.
- **Command of Evidence (Textual)** -- which quotation/detail best supports a claim. Text-only, no visual.
- **Command of Evidence (Quantitative)** -- which data point best supports or completes a claim, where the data is shown in an actual **table or graph** (`visual_type: "table"` or `"graph"`), not described in prose. This is the one Reading & Writing subcategory that needs a visual essentially always -- treat `has_visual: true` as close to mandatory here, the same way it is for Math's Geometry and Trigonometry. The passage sets up the claim; the table/graph is what the student has to actually read to answer. Don't write this as a purely textual question with the data quoted in the passage instead -- that's not the real format.
- **Inferences** -- what logically follows from the passage, phrased as "the most logical completion" for R&W-style inference items. Text-only, no visual.

None of the other Reading & Writing subcategories (Craft and Structure, Standard English Conventions, Expression of Ideas) use visuals on the real test -- they're passage/sentence-based. Command of Evidence (Quantitative) is the single exception in this section.

### Standard English Conventions (~26%)
- **Boundaries** -- sentence boundaries, punctuation (commas, semicolons, colons, dashes), joining/separating clauses correctly. This is the category most prone to multiple-defensible-answer errors -- every distractor MUST violate a specific, nameable punctuation or grammar rule, not just "read worse."
- **Form, Structure, and Sense** -- subject-verb agreement, pronoun-antecedent agreement, verb tense/form, modifier placement.

### Expression of Ideas (~20%)
- **Rhetorical Synthesis** -- given bullet-point notes, which sentence best accomplishes a stated goal (e.g., "which choice most effectively compares X and Y").
- **Transitions** -- best transition word/phrase to connect two sentences or ideas (however, therefore, in addition, etc.).

---

## Math (44 questions total: 22 per module)

Calculator permitted throughout. Questions are either multiple-choice (4 options) or student-produced response (numeric entry) -- for this question bank, generate multiple-choice only, matching the `questions` table's answer_a-d / correct_answer structure.

### Algebra (~35%)
- **Linear equations in one variable**
- **Linear equations in two variables** -- often includes a graph of the line(s) (`visual_type: "graph"`, `chart_type: "function"`), especially for questions about slope/intercept meaning or systems shown graphically.
- **Linear functions** -- frequently shown as a graph rather than posed purely algebraically (interpreting slope, y-intercept, or a specific point from a graph). Don't always default to the algebraic-only version.
- **Systems of two linear equations in two variables** -- sometimes shown as two lines on one graph, with the answer being their intersection point.
- **Linear inequalities in one or two variables** -- occasionally shown as a shaded region on a graph.

### Advanced Math (~35%)
- **Nonlinear functions** -- very commonly includes a graph (parabola, exponential curve) that the question asks the student to interpret (`chart_type: "function"`, kind `quadratic` or `exponential`).
- **Nonlinear equations in one variable and systems of equations in two variables** (quadratics, polynomials, exponentials) -- sometimes graph-based (where do two curves intersect).
- **Equivalent expressions** (factoring, simplifying) -- rarely needs a visual.

### Problem-Solving and Data Analysis (~15%)
- **Ratios, rates, proportional relationships, and units** -- occasionally a table.
- **Percentages** -- occasionally a table.
- **One-variable data**: distributions, measures of center and spread -- very commonly a **table** (frequency table) or bar graph.
- **Two-variable data**: models and scatterplots -- almost always needs a **scatterplot** visual (`chart_type: "scatter"`, often with a best-fit line), this is the category's namesake.
- **Probability and conditional probability** -- frequently a two-way frequency table (`visual_type: "table"`).
- **Inference from sample statistics and margin of error** -- occasionally a table of sample data.
- **Evaluating statistical claims** -- occasionally a table or scatterplot backing the claim being evaluated.

### Geometry and Trigonometry (~15%)
- **Area and volume** -- needs a **geometry** figure (rectangle, or a described 3D solid) essentially always.
- **Lines, angles, and triangles** -- needs a **geometry** figure (`triangle`) essentially always.
- **Right triangles and trigonometry** -- needs a **geometry** figure (`right_triangle`) essentially always.
- **Circles** -- needs a **geometry** figure (`circle`) essentially always.

Geometry and Trigonometry is the one domain where skipping the visual isn't a stylistic choice -- a geometry question without a figure usually isn't a valid Digital SAT question at all, since the shape's dimensions and labels ARE the problem. Treat `has_visual: true` as close to mandatory for this entire skill category.

### Visual presentation conventions (confirmed from 4 real practice tests)

- **Figures are drawn to scale by default.** Every real Math module opens with standing directions: "Unless otherwise indicated: All variables and expressions represent real numbers. Figures provided are drawn to scale. All figures lie in a plane." `render_visual.py` already renders shapes at their true proportions, which matches this default -- don't second-guess it. A per-question disclaimer "Note: Figure not drawn to scale." only appears as an explicit exception on the small number of questions where the shape is deliberately not proportional; since this pipeline always renders true-to-scale figures, you don't need this disclaimer at all in generated questions.
- **State units in the question text too, not just on the axis.** Real graph questions narrate the unit in prose even though it's also on the axis label -- e.g. "the height above the water y, in meters, of the diver x seconds after diving." Do the same: mention the unit in `question_text`, not only in `visual_data`'s `x_label`/`y_label`.
- **Table captions are a short, title-case noun phrase directly above the table, no colon** -- e.g. "Depths at Which Four Deep-Sea Fish Species Live," "Average Number and Duration of Torpor Bouts and Arousal Episodes for Alaska Marmots and Arctic Ground Squirrels, 2008-2011." Use this style for any `table` visual_data you add a title to.
- Standard reference phrasing for introducing a visual in the question stem: "The graph shown gives...", "The table shows...", "In the figure shown, ...". Real tests never say "the graph below" or "the graph above" (the visual is always adjacent in the digital interface) -- avoid directional language.

---

## Difficulty norms (for the Calibrator)

- **Easy (1)**: single concept, 1-2 solution steps (Math) or a direct, explicitly-stated detail (R&W). Common vocabulary.
- **Medium (2)**: combines two related concepts or requires one inference step beyond the literal text/equation.
- **Hard (3)**: multiple concepts combined, non-obvious setup, or requires eliminating subtly-wrong distractors that require real understanding to rule out (not just careless-error traps).

## Adaptive module routing (context, not part of generation)

In the real test and in ScoreLab AI's diagnostic, Module 1 mixes difficulties; Module 2 is routed easy or hard based on Module 1 performance. This doesn't change how you generate individual questions -- `module_type` (`standard` / `easy_module` / `hard_module`) is assigned at the bank-organization level, not something the Generator subagent needs to reason about per question. Default to `module_type: "standard"` unless the user specifies otherwise.
