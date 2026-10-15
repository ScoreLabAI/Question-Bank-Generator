# Output Schema

Every generated question must be a single JSON object with exactly these fields, matching ScoreLab AI's Supabase `questions` table. The Generator subagent should output this directly; do not add extra fields or omit any of these.

```json
{
  "section": "math | reading_writing",
  "skill_category": "e.g. Algebra, Standard English Conventions",
  "skill_subcategory": "e.g. Linear equations in two variables, Boundaries",
  "difficulty": 1,
  "module_type": "standard",
  "question_text": "The full question stem. For Reading & Writing, include the passage inline as part of this field.",
  "answer_a": "Choice A text",
  "answer_b": "Choice B text",
  "answer_c": "Choice C text",
  "answer_d": "Choice D text",
  "correct_answer": "A",
  "explanation": "Why the correct answer is right.",
  "distractor_a_explanation": "Why A is wrong (omit or leave empty if A is correct)",
  "distractor_b_explanation": "Why B is wrong (omit or leave empty if B is correct)",
  "distractor_c_explanation": "Why C is wrong (omit or leave empty if C is correct)",
  "distractor_d_explanation": "Why D is wrong (omit or leave empty if D is correct)",
  "is_diagnostic": false,
  "is_active": true,
  "has_visual": false,
  "visual_type": null,
  "visual_data": null,
  "visual_svg": null
}
```

## Visual fields

Real Digital SAT Math questions frequently include a graph, table, or geometric figure -- especially in Advanced Math (function graphs), Problem-Solving and Data Analysis (scatterplots, bar graphs, data tables), and Geometry and Trigonometry (every question in this category needs a figure). Don't default to a purely textual/algebraic framing just because it's easier -- if the real SAT would show a visual for this skill category, this question should too. See `references/sat-taxonomy.md` for which subcategories typically need one.

- `has_visual`: `true` if this question includes a graph, table, or figure, `false` otherwise.
- `visual_type`: `"graph"`, `"table"`, or `"geometry"` when `has_visual` is true, otherwise `null`.
- `visual_data`: structured JSON describing the visual precisely (exact function coefficients, point coordinates, side lengths, table rows, etc.) -- see `scripts/render_visual.py`'s docstring for the exact spec format per type. Never describe a visual in prose; the whole point is that the numbers here are unambiguous enough for a script to render deterministically. `null` when `has_visual` is false.
- `visual_svg`: the rendered SVG markup, produced by running `scripts/render_visual.py` on the `visual_data` (for `graph` and `geometry` only -- `table` needs no rendering, the frontend renders `visual_data`'s rows/columns directly as an HTML table). `null` for `table` type and when `has_visual` is false. Do not write this field yourself -- it comes from actually running the script, not from generating SVG markup as text.

This is a new addition to the original schema -- the live Supabase `questions` table will need these four columns added via migration before generated questions with visuals can be imported. Flag this to the user rather than assuming it's already there.

### Table format

`table` is the one visual_type that doesn't go through `render_visual.py` -- there's nothing to render, the frontend displays `visual_data`'s rows and columns directly as an HTML table. Use this exact structure:

```json
{
  "headers": ["Charge (kWh)", "Number of days"],
  "rows": [["8", "3"], ["11", "4"], ["16", "2"], ["23", "6"]]
}
```

This applies both to Math (frequency tables, two-way tables in Problem-Solving and Data Analysis) and Reading & Writing (Command of Evidence (Quantitative) questions that present data alongside the passage). `visual_svg` stays `null` for this type -- don't attempt to render it.

## Field notes

- `difficulty`: integer 1-3 only (1=easy, 2=medium, 3=hard). This may be corrected by the Calibrator step -- always output the calibrated value, not the generator's original guess, in the final batch.
- `correct_answer`: exactly one of `"A"`, `"B"`, `"C"`, `"D"`.
- `distractor_*_explanation`: write explanations for the three WRONG choices only (leave the correct choice's own distractor field blank or omit it). Each explanation should name the specific reason that choice is wrong -- for grammar/usage questions, name the rule it violates.
- `is_diagnostic`: leave `false` unless the user explicitly asks for diagnostic-pool questions.
- `is_active`: always `true` for a question that passed the pipeline.
- Do not include `id` or `created_at` -- Supabase generates these on insert.

## Final batch file

Assemble all accepted questions from a batch into a single JSON array and save as one file, e.g. `batch_<skill_category>_<difficulty>.json`. This is the file `scripts/validate_batch.py` expects as input, and the format that can be bulk-imported into Supabase directly.
