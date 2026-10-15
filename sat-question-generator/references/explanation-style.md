# Explanation Style Guide

The `explanation` and `distractor_*_explanation` fields are shown directly to students in the app -- they are the final product, not internal reasoning. Match College Board's own published answer-explanation convention exactly, pulled from official SAT Practice Test answer explanation PDFs (satsuite.collegeboard.org). This applies only to these two fields. It does NOT apply to the Critic or Calibrator subagents' internal reasoning, which can stay terse and process-oriented since students never see it.

## Math

**Correct answer:** Start with "Choice X is correct." followed by a concise derivation that restates the given information in the problem's own terms ("It's given that...") and walks the most direct path to the answer, ending with a "Therefore, ..." line that restates the result in context.

Example (real College Board explanation):
> Choice B is correct. Subtracting 61 from each side of the given equation yields |p| = 4. By the definition of absolute value, if |p| = 4, then p = 4 or p = -4. Of the given choices, 4 is a solution to the given equation.

**Wrong answers:** "Choice Y is incorrect." followed by one of two things:
- A specific, named misconception or error path that produces that exact wrong value, when one naturally exists ("This is the quotient, not the difference, of 65 and 61." / "This is the measure of angle K, not angle J.")
- When no single clean error path is the point of the distractor (e.g., it's just a plausible-looking wrong number), the stock phrase: "Choice Y is incorrect and may result from conceptual or calculation errors."

Do not pad wrong-answer explanations with extra teaching commentary. Keep them one to two sentences.

## Reading & Writing

**Correct answer:** Start with "Choice X is the best answer because..." (this skill's word choice is deliberate for R&W -- College Board consistently uses "best answer," not "correct," here, unlike Math). Justify by referencing specific details or wording from the passage, not abstract grammar rules alone -- ground it in the text.

Example (real College Board explanation, vocabulary-in-context):
> Choice D is the best answer because as used in the text, "clear" most nearly means transparent, or see-through. Muir states that the water beneath the boat "was so clear that it was almost invisible," suggesting that those on the boat were able to see through the water and easily observe plants and fish below the surface.

**Wrong answers:** "Choice Y is incorrect." followed by a specific reason tied to the passage -- for vocabulary-in-context questions, this typically means naming the alternate meaning the wrong choice would introduce and showing why that meaning doesn't fit the context:

> Choice A is incorrect. In some contexts "clear" can mean "simple," or uncomplicated, but Muir is describing the water, and water isn't typically described as either simple or complicated.

For Standard English Conventions (grammar/punctuation) questions specifically, name the exact rule violated rather than a passage-meaning mismatch, since that's the actual thing being tested -- this skill's existing instruction to cite a "specific, nameable rule" for grammar distractors still applies; just wrap it in this same "Choice Y is incorrect because..." phrasing rather than a bare rule citation.

**Confirmed against 4 additional real practice tests (5, 8, 9, 11) -- these variations are legitimate, not deviations to avoid:**

- **Standard English Conventions correct-answer pattern is slightly different from the rest of R&W.** Real explanations often use two short sentences rather than one "because" clause: "Choice A is the best answer. The convention being tested is the use of punctuation to mark boundaries between supplements and clauses." -- naming the tested convention explicitly (comma splice, run-on, dangling modifier, subject-verb agreement, etc.) before or instead of walking through the specific sentence. Either this two-sentence form or the single "because" form is acceptable for Boundaries/Form-Structure-and-Sense questions; pick whichever reads more naturally for the specific rule.
- **Wrong-answer phrasing has two acceptable forms, used interchangeably even within the same real test:** "Choice Y is incorrect because [reason]." and "Choice Y is incorrect. [Reason as a separate sentence]." Both are fine -- don't force every distractor into the "because" form if the reasoning reads more naturally as its own sentence.
- **The Math stock phrase appears with minor wording variance in real explanations** -- "may result from conceptual or calculation errors" and "may result from conceptual or computational errors" both appear. Either is fine; don't treat this as a typo to correct.
- Grammar distractor explanations should name the specific fault the same way real explanations do: "results in a comma splice," "results in a run-on sentence," "results in a dangling modifier," "doesn't agree in number with the plural subject." A vague "this is grammatically incorrect" is not sufficient -- always name the rule.

## What NOT to do

Don't write in a generic tutoring voice ("Great question! Let's break this down..."). Don't add encouragement or meta-commentary. Don't over-explain past the point College Board's own explanations stop. The tone is neutral, terse, and confident -- it reads like a answer key, not a lesson.
