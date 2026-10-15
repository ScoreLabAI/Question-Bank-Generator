#!/usr/bin/env python3
"""
Validates a batch of generated SAT questions against the ScoreLab AI questions-table schema.

Usage:
    python validate_batch.py <path_to_batch.json>

Exits non-zero if any question fails structural validation. Prints a per-question report.
This is a deterministic, script-level check -- it catches schema/completeness problems,
it does NOT catch whether the question content is actually correct (that's the Critic
subagent's job in the pipeline).
"""
import json
import re
import sys

# Canonical taxonomy, kept in sync with references/sat-taxonomy.md and the progress tracker.
# A Generator subagent invented "Systems of two linear inequalities in two variables" once --
# a plausible-sounding subcategory that doesn't exist in the official breakdown. It would have
# silently created an orphan cell in the bank, so the names are pinned here.
VALID_CATEGORIES = {
    "Advanced Math", "Algebra", "Craft and Structure", "Expression of Ideas",
    "Geometry and Trigonometry", "Information and Ideas",
    "Problem-Solving and Data Analysis", "Standard English Conventions",
}
VALID_SUBCATEGORIES = {
    "Area and volume", "Boundaries", "Central Ideas and Details", "Circles",
    "Command of Evidence (Quantitative)", "Command of Evidence (Textual)",
    "Cross-Text Connections", "Equivalent expressions", "Evaluating statistical claims",
    "Form, Structure, and Sense", "Inference from sample statistics and margin of error",
    "Inferences", "Linear equations in one variable", "Linear equations in two variables",
    "Linear functions", "Linear inequalities in one or two variables",
    "Lines, angles, and triangles",
    "Nonlinear equations in one variable and systems of equations in two variables",
    "Nonlinear functions",
    "One-variable data: distributions and measures of center and spread",
    "Percentages", "Probability and conditional probability",
    "Ratios, rates, proportional relationships, and units", "Rhetorical Synthesis",
    "Right triangles and trigonometry",
    "Systems of two linear equations in two variables", "Text Structure and Purpose",
    "Transitions", "Two-variable data: models and scatterplots", "Words in Context",
}

REQUIRED_FIELDS = [
    "section", "skill_category", "skill_subcategory", "difficulty", "module_type",
    "question_text", "answer_a", "answer_b", "answer_c", "answer_d",
    "correct_answer", "explanation", "is_diagnostic", "is_active",
]
ANSWER_FIELDS = ["answer_a", "answer_b", "answer_c", "answer_d"]
DISTRACTOR_FIELDS = {
    "A": ["distractor_b_explanation", "distractor_c_explanation", "distractor_d_explanation"],
    "B": ["distractor_a_explanation", "distractor_c_explanation", "distractor_d_explanation"],
    "C": ["distractor_a_explanation", "distractor_b_explanation", "distractor_d_explanation"],
    "D": ["distractor_a_explanation", "distractor_b_explanation", "distractor_c_explanation"],
}


def validate_question(q, idx):
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in q or q[field] in (None, ""):
            errors.append(f"missing or empty required field '{field}'")

    if "section" in q and q["section"] not in ("math", "reading_writing"):
        errors.append(f"invalid section '{q.get('section')}' (must be math or reading_writing)")

    if "difficulty" in q and q["difficulty"] not in (1, 2, 3):
        errors.append(f"invalid difficulty '{q.get('difficulty')}' (must be 1, 2, or 3)")

    if "correct_answer" in q and q["correct_answer"] not in ("A", "B", "C", "D"):
        errors.append(f"invalid correct_answer '{q.get('correct_answer')}' (must be A, B, C, or D)")

    answers = [q.get(f) for f in ANSWER_FIELDS]
    if any(a in (None, "") for a in answers):
        errors.append("one or more answer choices are empty")
    elif len(set(a.strip().lower() for a in answers if a)) != 4:
        errors.append("answer choices are not all distinct (possible duplicate)")

    correct = q.get("correct_answer")
    if correct in DISTRACTOR_FIELDS:
        for field in DISTRACTOR_FIELDS[correct]:
            if not q.get(field):
                errors.append(f"missing distractor explanation '{field}' for a wrong choice")
        # The correct choice must NOT carry a distractor explanation. If it does, the answer key
        # and the explanations have desynced -- almost always a sign the choices were reordered
        # after the fact without the key being updated.
        own = f"distractor_{correct.lower()}_explanation"
        if q.get(own):
            errors.append(
                f"correct_answer is {correct} but '{own}' is non-empty -- the key and the "
                f"explanations disagree about which choice is correct"
            )

    errors.extend(validate_taxonomy(q))
    errors.extend(validate_choice_order(q))
    errors.extend(validate_explanation_letters(q))
    errors.extend(validate_visual(q))

    return errors


def validate_taxonomy(q):
    errors = []
    cat, sub = q.get("skill_category"), q.get("skill_subcategory")
    if cat and cat not in VALID_CATEGORIES:
        errors.append(f"skill_category '{cat}' is not in the official taxonomy")
    if sub and sub not in VALID_SUBCATEGORIES:
        errors.append(f"skill_subcategory '{sub}' is not in the official taxonomy")
    return errors


NUM_RE = re.compile(r"^\s*-?\$?\s*-?[\d,]+(?:\.\d+)?\s*%?\s*$")


def _as_number(s):
    """Parse a choice as a plain number, or return None if it isn't purely numeric.
    Handles the '$1,250' / '-3' / '8.5' / '40%' forms real choices use."""
    if not isinstance(s, str) or not NUM_RE.match(s):
        return None
    cleaned = s.strip().replace("$", "").replace(",", "").replace("%", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def validate_choice_order(q):
    """The Digital SAT lists purely numeric answer choices in ascending order. Out-of-order
    choices reached critique twice (runs 6 and 7) before anyone noticed, so it's checked here."""
    values = [_as_number(q.get(f)) for f in ANSWER_FIELDS]
    if any(v is None for v in values):
        return []  # not a purely numeric choice set -- ordering convention doesn't apply
    if values != sorted(values):
        return [
            f"numeric answer choices are not in ascending order: {values} -- "
            f"the Digital SAT orders numeric choices ascending, so A-D must be sorted "
            f"(remember to move correct_answer with them)"
        ]
    return []


def validate_explanation_letters(q):
    """Each explanation should name its own choice letter. Catches key/explanation desync,
    which is the specific failure mode introduced when answer choices get reordered."""
    errors = []
    correct = q.get("correct_answer")
    expl = q.get("explanation") or ""
    m = re.search(r"\bChoice\s+([ABCD])\b", expl)
    if m and correct in ("A", "B", "C", "D") and m.group(1) != correct:
        errors.append(
            f"explanation says 'Choice {m.group(1)}' but correct_answer is '{correct}' -- "
            f"the key and the explanation disagree"
        )
    for letter in "ABCD":
        if letter == correct:
            continue
        text = q.get(f"distractor_{letter.lower()}_explanation") or ""
        m = re.search(r"\bChoice\s+([ABCD])\b", text)
        if m and m.group(1) != letter:
            errors.append(
                f"distractor_{letter.lower()}_explanation says 'Choice {m.group(1)}' -- "
                f"it should refer to Choice {letter} (explanations likely got reordered)"
            )
    return errors


def validate_visual(q):
    errors = []
    has_visual = q.get("has_visual", False)
    visual_type = q.get("visual_type")
    visual_data = q.get("visual_data")
    visual_svg = q.get("visual_svg")

    if has_visual:
        if visual_type not in ("graph", "table", "geometry"):
            errors.append(f"has_visual is true but visual_type is invalid: '{visual_type}'")
        if not visual_data:
            errors.append("has_visual is true but visual_data is missing/empty")
        if visual_type in ("graph", "geometry") and not visual_svg:
            errors.append(
                f"visual_type is '{visual_type}' but visual_svg is missing -- "
                f"render_visual.py must be run on visual_data before this question is accepted"
            )
        if visual_type == "table" and visual_svg:
            errors.append("visual_type is 'table' but visual_svg is set -- tables don't get rendered, only graph/geometry do")
    else:
        if visual_type or visual_data or visual_svg:
            errors.append("has_visual is false but visual_type/visual_data/visual_svg is set -- should all be null")

    # Geometry and Trigonometry questions are essentially never valid without a figure -- see sat-taxonomy.md.
    if q.get("skill_category") == "Geometry and Trigonometry" and not has_visual:
        errors.append(
            "skill_category is 'Geometry and Trigonometry' but has_visual is false -- "
            "this domain needs a figure in virtually every real case, double check this is intentional"
        )
    if q.get("skill_subcategory", "").startswith("Two-variable data") and not has_visual:
        errors.append(
            "skill_subcategory is 'Two-variable data' but has_visual is false -- "
            "this subcategory is specifically about scatterplots, double check this is intentional"
        )

    # Command of Evidence (Quantitative) is the one R&W subcategory that needs a table/graph essentially always.
    if q.get("skill_subcategory", "").startswith("Command of Evidence (Quantitative)") and not has_visual:
        errors.append(
            "skill_subcategory is 'Command of Evidence (Quantitative)' but has_visual is false -- "
            "this subcategory is specifically about reading data from a table or graph, double check this is intentional"
        )

    return errors


def gridline_warnings(q, idx):
    """Tick/slope parity on linear graph specs (added run 11).

    item-design-rules.md, "Graph-read items": every value the student must read has to land on a
    labeled gridline. Run 5 fixed that by requiring explicit tick steps, but run 11 showed the tick
    steps can be set and the item still be awkward: y = 3x + 4 with y_tick_step 2 puts the author's
    chosen reading points (0, 4) and (2, 10) on gridlines, while the natural adjacent-integer read
    (0, 4) -> (1, 7) lands between the labeled 6 and 8.

    The condition is slope * x_tick_step being a whole multiple of y_tick_step -- when it holds,
    stepping one labeled x-tick always lands on a labeled y-tick. This is a WARNING, not a failure:
    an item whose reading points are all on gridlines is still answerable, and some legitimate
    specs (scatterplots, non-linear curves) fall outside the check entirely.
    """
    warnings = []
    if not q.get("has_visual") or q.get("visual_type") != "graph":
        return warnings
    vd = q.get("visual_data") or {}
    if vd.get("chart_type") not in ("function", "inequality"):
        return warnings

    xs, ys = vd.get("x_tick_step"), vd.get("y_tick_step")
    if not isinstance(xs, (int, float)) or not isinstance(ys, (int, float)) or not xs or not ys:
        warnings.append(
            f"#{idx}: graph spec is missing an explicit x_tick_step/y_tick_step -- set both so every "
            f"value the student must read lands on a labeled gridline"
        )
        return warnings

    entries = vd.get("functions") or vd.get("inequalities") or []
    if not entries and vd.get("function"):
        entries = [vd["function"]]
    for e in entries:
        if e.get("kind") != "linear":
            continue
        m = (e.get("params") or {}).get("m")
        if not isinstance(m, (int, float)):
            continue
        rise = abs(m) * xs
        if rise and abs(rise / ys - round(rise / ys)) > 1e-9:
            warnings.append(
                f"#{idx}: linear graph with slope {m}, x_tick_step {xs}, y_tick_step {ys} -- stepping "
                f"one labeled x-tick moves {rise} in y, which is not a multiple of y_tick_step, so the "
                f"natural adjacent-tick slope read lands between gridlines. Safest fix: set both tick "
                f"steps to 1 over a modest range."
            )
    return warnings


def _parse_interval(text):
    """Parse an answer choice that states a numeric interval, or return None.

    Recognizes the two forms the bank actually uses:
        "6/7 < m < 2"   /  "1/2 <= x <= 3"    (a compound inequality)
        "between -3 and 6"                     (prose)
    Fractions like 6/7 and negatives are handled. Anything else returns None, so
    the caller silently skips choices that aren't intervals.
    """
    t = (text or "").strip().rstrip(".")
    num = r"-?\d+(?:\.\d+)?(?:\s*/\s*\d+)?"

    m = re.search(rf"({num})\s*<=?\s*[A-Za-z]\w*\s*<=?\s*({num})", t)
    if not m:
        m = re.search(rf"between\s+({num})\s+and\s+({num})", t, re.IGNORECASE)
    if not m:
        return None
    lo, hi = _bound_value(m.group(1)), _bound_value(m.group(2))
    if lo is None or hi is None or lo >= hi:
        return None
    return (lo, hi)


def _bound_value(s):
    """Numeric value of one interval endpoint. Unlike _as_number this accepts fractions
    such as 6/7 and 3/2, which is how slope bounds are written in these choices."""
    s = (s or "").strip()
    try:
        if "/" in s:
            n, d = s.split("/", 1)
            return float(n.strip()) / float(d.strip())
        return float(s)
    except (ValueError, ZeroDivisionError):
        return None


def nested_range_warnings(q, idx):
    """Flag a keyed interval that is a superset of two or more of the other choices.

    Added run 12. Two items that run generated -- an x-intercept-location item and a
    slope-range item -- had three answer choices that tiled or nested inside the correct
    one, so the correct interval was literally the union of its rivals. A student who knows
    no mathematics can pick "the widest interval that contains the others" and score the
    item. Both were caught by Critics, but the pattern is mechanical, so it belongs here.

    Note the constraint on the fix: on a "must be true" item, any interval CONTAINING the
    guaranteed one is also correct, so a replacement distractor has to stick out on one side
    while omitting part of the guaranteed range. This is a WARNING, not a failure -- a key
    that contains exactly one other choice is normal and not exploitable.
    """
    warnings = []
    key = q.get("correct_answer")
    if key not in "ABCD":
        return warnings
    intervals = {}
    for L in "ABCD":
        iv = _parse_interval(q.get(f"answer_{L.lower()}"))
        if iv:
            intervals[L] = iv
    if key not in intervals or len(intervals) < 3:
        return warnings
    klo, khi = intervals[key]
    contained = [
        L for L, (lo, hi) in intervals.items()
        if L != key and klo <= lo and hi <= khi and (klo, khi) != (lo, hi)
    ]
    if len(contained) >= 2:
        warnings.append(
            f"#{idx}: the keyed choice {key} ({klo}, {khi}) is a superset of choices "
            f"{', '.join(contained)} -- a student can pick the widest interval without doing the "
            "mathematics. Replace one distractor with an interval that sticks out past the key on "
            "one side while omitting part of it (a pure superset of the key would be a second "
            "correct answer)."
        )
    return warnings


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_batch.py <path_to_batch.json>")
        sys.exit(2)

    path = sys.argv[1]
    with open(path) as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("ERROR: batch file must contain a JSON array of question objects")
        sys.exit(2)

    total = len(data)
    failed = 0
    bad = set()

    for idx, q in enumerate(data):
        errors = validate_question(q, idx)
        if errors:
            bad.add(idx)
            label = q.get("skill_subcategory", f"question {idx}")
            print(f"[FAIL] #{idx} ({label}):")
            for e in errors:
                print(f"    - {e}")

    grid = []
    for idx, q in enumerate(data):
        grid.extend(gridline_warnings(q, idx))
    if grid:
        print("\n[WARN] graph gridline/tick parity:")
        for w in grid:
            print(f"    - {w}")

    nested = []
    for idx, q in enumerate(data):
        nested.extend(nested_range_warnings(q, idx))
    if nested:
        print("\n[WARN] nested/superset interval answer choices:")
        for w in nested:
            print(f"    - {w}")

    # Batch-level: identical stems within one batch. A near-duplicate check against the whole
    # bank is the orchestrator's job (it needs the master file), but exact in-batch repeats
    # are free to catch here.
    seen = {}
    for idx, q in enumerate(data):
        key = " ".join((q.get("question_text") or "").split()).lower()
        if key and key in seen:
            print(f"[FAIL] #{idx}: question_text is identical to #{seen[key]} in this batch")
            bad.add(idx)
        seen.setdefault(key, idx)

    # Batch-level: answer-key letter distribution (added run 9).
    # item-design-rules.md says "vary the key position -- don't let correct_answer drift toward one
    # letter across a batch." In run 9 all seven raw Generator drafts keyed to A or B and none to C
    # or D; nobody noticed until the orchestrator eyeballed it at assembly time. This is a WARNING,
    # not a failure: for purely numeric choices the ascending-order rule fixes the key position, so
    # a skewed batch is sometimes unavoidable and should not block a merge. It is also suppressed
    # for small batches, where skew carries no signal.
    if total >= 4:
        keys = [q.get("correct_answer") for q in data if q.get("correct_answer") in "ABCD"]
        counts = {L: keys.count(L) for L in "ABCD"}
        distinct = sum(1 for L in "ABCD" if counts[L])
        if keys and (distinct < 3 or max(counts.values()) > len(keys) / 2):
            dist = ", ".join(f"{L}={counts[L]}" for L in "ABCD")
            print(
                f"\n[WARN] answer-key distribution is skewed across this batch ({dist}). "
                "Where the choices are NOT purely numeric, reorder them so the key moves -- and move "
                "correct_answer and the distractor_*_explanation fields with it."
            )

    failed = len(bad)
    passed = total - failed
    print(f"\n{passed}/{total} questions passed structural validation.")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
