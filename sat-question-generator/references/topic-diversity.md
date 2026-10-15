# Topic and Scenario Diversity

The skill category/subcategory/difficulty taxonomy controls what math or grammar concept a question tests. It does nothing to control what real-world scenario or passage subject the question is dressed up in -- and left alone, generation tends to reach for the same handful of "safe" defaults over and over (ticket sales, gym memberships, a scientist from Harvard). A bank where every third question is about ticket pricing reads as cheap and repetitive even if every question is individually correct.

## Before generating

Read `scorelab_used_topics.md` in the Claude Creations folder (one directory up from this skill). It's a running log of the scenario/subject used by every question already accepted into the bank. Skim it for the skill category you're about to write for, and avoid reusing a scenario, named figure, or setup that already appears -- not just exact duplicates, but close variants (e.g. if "concert ticket pricing" is logged, don't write "movie ticket pricing" either; pick a different domain entirely).

## After generating

Append one line per newly accepted question to `scorelab_used_topics.md`, in the same format as existing entries: `- [skill_category/skill_subcategory, d<difficulty>] <short scenario description>`.

## Domain rotation

When a question needs a real-world scenario (Math word problems) or a passage subject (Reading & Writing), rotate through these domains rather than defaulting to the same one. Don't force a domain where it doesn't fit, but treat repeatedly landing on the same domain as a signal to deliberately pick something else next time:

**Math word-problem contexts:** business/commerce (pricing, budgets, sales, inventory), science and nature (population, chemistry mixtures, physics motion, astronomy), sports and recreation, food and cooking, travel and transportation, technology and data, personal finance, construction and engineering, art and design, community and civic life (elections, surveys, public services), health and medicine.

**Reading & Writing passage subjects:** history and historical figures, science and nature, biography (rotate across fields, eras, genders, and cultural backgrounds -- don't default to the same archetype every time), arts and culture, business and economics, technology and innovation, sports, environment and conservation, social science, literature and language.

For biographical/historical passages specifically, vary the kind of person featured -- not always a scientist, not always from the same country or era, not always framed the same way ("a Harvard astronomer who...").
