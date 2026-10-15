#!/usr/bin/env python3
"""Builds slim, per-cell Generator reference packs from the full reference files (run 19 trial).

The full reference files remain the single source of truth. A pack is a deterministic
concatenation of whole sections of those files -- nothing is reworded or summarized.
Each pack ends with a list of the sections it OMITTED, so the Generator knows what exists.

Usage:
  python build_packs.py            # (re)build all packs into references/packs/
  python build_packs.py --check    # exit 1 if any pack is stale or incomplete
  python build_packs.py --show math 1   # print which sections go in the pack for math, difficulty 1

Quality-first rule: a section is dropped ONLY when it cannot apply to the cell
(wrong domain, or a Hard-shape rule on a difficulty-1 cell). Anything uncertain is included.
"""
import os, re, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "references")
PACKS = os.path.join(REF, "packs")

# file -> {header substring: (domain, min_difficulty)}; domain in all|math|rw. Unlisted headers = all, d1.
RULES = {
 "sat-taxonomy.md": {
   "Reading & Writing (54": ("rw", 1), "Math (44": ("math", 1),
   "Craft and Structure": ("rw", 1), "Information and Ideas": ("rw", 1),
   "Standard English Conventions": ("rw", 1), "Expression of Ideas": ("rw", 1),
   "Algebra (~35%)": ("math", 1), "Advanced Math": ("math", 1),
   "Problem-Solving and Data Analysis": ("math", 1), "Geometry and Trigonometry": ("math", 1),
   "Visual presentation conventions": ("math", 1),
 },
 "distractor-patterns.md": {"Math patterns": ("math", 1), "Reading & Writing patterns": ("rw", 1)},
 "explanation-style.md": {"## Math": ("math", 1), "## Reading & Writing": ("rw", 1)},
 "item-design-rules.md": {
   "Ordered-pair and coordinate": ("math", 1), "Graph-read items": ("math", 1),
   "Must-be-true items": ("math", 2), "Candidate-rejection constraints": ("math", 2),
   "A candidate-rejection item": ("math", 2), "Compute two independent bounds": ("math", 2),
 },
}
ALWAYS = ["questions-schema.md", "topic-diversity.md"]
ORDER = ["sat-taxonomy.md", "questions-schema.md", "topic-diversity.md",
         "explanation-style.md", "distractor-patterns.md", "item-design-rules.md"]

def split(text):
    parts, cur_h, cur = [], None, []
    for line in text.splitlines(keepends=True):
        if re.match(r"^#{2,3} ", line) and not line.startswith("####"):
            parts.append((cur_h, "".join(cur))); cur_h, cur = line.strip(), [line]
        else:
            cur.append(line)
    parts.append((cur_h, "".join(cur)))
    return parts  # first entry is the preamble (header None)

def rule(fn, header):
    for key, val in RULES.get(fn, {}).items():
        if header and key in header: return val
    return ("all", 1)

def sections_for(fn, domain, diff):
    text = open(os.path.join(REF, fn), encoding="utf-8").read()
    inc, omit = [], []
    parent_dom = None
    for h, body in split(text):
        if h is None: inc.append(body); continue
        dom, mind = rule(fn, h)
        is_h2 = h.startswith("## ")
        if is_h2: parent_dom = dom if dom != "all" else None
        # H3 inherits a domain restriction from its H2 parent unless it has its own rule
        if dom == "all" and not is_h2 and parent_dom: dom = parent_dom
        ok = (dom in ("all", domain)) and diff >= mind
        (inc if ok else omit).append(body if ok else h)
    return "".join(inc), omit

def build_pack(domain, diff):
    out = [f"# Generator reference pack: {domain}, difficulty {diff}\n\n"
           "(Auto-built by scripts/build_packs.py from the full reference files; sections are verbatim. "
           "The full files remain authoritative -- if anything below seems to conflict with or be missing "
           "a rule you need, read the full file named in the OMITTED list.)\n\n"]
    omitted = []
    for fn in ORDER:
        body, omit = sections_for(fn, domain, diff)
        out.append(f"\n<!-- ===== {fn} ===== -->\n{body}\n")
        omitted += [f"{fn}: {o}" for o in omit]
    out.append("\n<!-- ===== OMITTED SECTIONS (not applicable to this cell; see full files) ===== -->\n")
    out += [f"- {o}\n" for o in omitted] or ["- (none)\n"]
    return "".join(out)

def cells():
    return [(d, k) for d in ("math", "rw") for k in (1, 2, 3)]

def main():
    args = sys.argv[1:]
    if args[:1] == ["--show"]:
        d, k = args[1], int(args[2])
        for fn in ORDER:
            body, omit = sections_for(fn, d, k)
            print(fn, "included", len(body), "bytes; omitted:", omit)
        return
    os.makedirs(PACKS, exist_ok=True)
    bad = 0
    for d, k in cells():
        p = os.path.join(PACKS, f"{d}_d{k}_pack.md")
        new = build_pack(d, k)
        if "--check" in args:
            if not os.path.exists(p) or open(p, encoding="utf-8").read() != new:
                print("STALE/MISSING:", p); bad += 1
        else:
            open(p, "w", encoding="utf-8").write(new)
            print(f"wrote {p} ({len(new)} bytes)")
    if "--check" in args:
        print("packs OK" if not bad else f"{bad} pack(s) stale -- rerun build_packs.py (or fall back to the full files)")
        sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
