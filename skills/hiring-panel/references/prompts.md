# Subagent prompt templates

Fill the `{placeholders}`. Every prompt runs with the Agent tool (`general-purpose`). Run each group in **one message** so agents work in parallel.

Shared values:
- `{dir}` — absolute path of the working folder
- `{N}` — round number
- `{target}` — job posting summary or target role, plus market (e.g. "general Mobile Developer, Czech market")
- `{cvs}` — the CV files under review, e.g. `sources/cv_en.md, sources/cv_cs.md` in round 1, `round-{N-1}/cv_en.md, …` later
- `{langs}` — output languages, e.g. "English and Czech"

---

## ATS

```
You are an automated Applicant Tracking System (ATS) parser + keyword screener for: {target}.
If there is no posting, use the keyword set a typical posting for this role would contain.

Folder: {dir}
Round {N}. Read: {cvs}, facts.md{, round-{N-1}/ats.md and round-{N-1}/verdict.md if N > 1}.
If original PDF/DOCX files exist, also open them to check the real layout (columns, tables, header/footer text, clickable links).

For each language version check: reading order; standard, parseable section headings; job titles and
dates in a parseable format; contact info (phone, email, working LinkedIn URL); keyword coverage
(table: found / missing); parsing hazards (multi-column grids, tables, icons, text in headers);
estimated length in A4 pages; local-language date or title formats that international ATS would miss.

Do not recommend adding skills or facts that are not in facts.md — list them as "ask the candidate".

Write round-{N}/ats.md: per language PASS/REJECT, parse score /100, the deciding lines, keyword
table, hazards, top fixes. Final message: a 4-line summary.
```

---

## Reviewer (round 1, or full re-review)

```
You are on a hiring panel reviewing a CV for: {target}.

Your persona: {persona description from the SKILL.md table, adapted to the role and market}.

Folder: {dir}
Read: {cvs} (the CV in {langs}), facts.md (verified facts — including ones the CV may omit),
00_conflicts.md{, round-{N-1}/verdict.md and your own round-{N-1} files if N > 1}.
You may open the original files to judge the visual impression.

Rules:
- Work alone. Do not read other reviewers' files for this round.
- Be harsh and specific. Quote exact lines. Generic advice ("add metrics") is not allowed unless you
  say which line and what kind of metric.
- Never invent facts. Rewrites may only use facts.md. Unknown numbers → [ADD: …] (respect any limits
  the user set in facts.md).
- Judge every language version. Each must read like a native CV for its market.

Write round-{N}/review_{id}.md with exactly:
1. Verdict: interview / no interview + score /10 (per language if they differ)
2. First 6 seconds: what you took away
3. Top 3 weakest lines (quoted) and why
4. Top 3 strengths to keep
5. Language-specific issues (translation, register, anglicisms, mismatches between versions)
6. The single fix to make first
7. Proposed rewrites for every flagged line, in every language
{8. If N > 1: did the previous round's fixes land? ✅/❌ against verdict.md}

Final message: verdict, score and single fix in 3 lines.
```

---

## Debate

```
Hiring-panel DEBATE, round {N}. Your persona: {persona}. Target: {target}.

Folder: {dir}
Read ALL of: round-{N}/review_ceo.md, review_recruiter.md, review_rival.md,
review_hiring_manager.md, review_teammate.md (yours is review_{id}.md), round-{N}/ats.md,
facts.md (note anything the user confirmed after the reviews were written), and {cvs}.

Stay in persona and argue with the others — quote who said what. Look for real tensions:
what to cut vs. keep, how to frame weak entries, overclaiming vs. selling, section order, length,
which numbers to show, how each language should read.

Write round-{N}/debate_{id}.md with:
- Agree — points you endorse, and why
- Disagree — points you reject, with arguments
- Changed my mind — what you now revise in your own review
- Final top 5 changes, priority order, exact wording in every language (facts.md only)
- Updated score: CV as-is, and if your top 5 were applied. Would you sign off at 8+? yes/no

Final message: your top 3 changes and scores in 5 lines.
```

---

## Sign-off (light confirmation round)

```
Hiring panel, round {N} — SIGN-OFF CHECK. Your persona: {persona}. Target: {target}.

Folder: {dir}
Read the final candidates {cvs}, round-{N-1}/verdict.md (what was meant to change), facts.md and
your own round-{N-1}/debate_{id}.md. Work blind — do not read other round-{N} files.

Check that your requested changes landed and hunt only for HIGH-PRIORITY problems: factual
overclaim, a fact not in facts.md, broken grammar, content mismatch between languages, a missing
key signal. Ignore taste-level nitpicks.

Write round-{N}/review_{id}.md:
1. Verdict + score /10 per language
2. Changes landed ✅/❌
3. High-priority issues remaining (quoted), or "none"
4. Optional polish (max 3, exact wording in every language)
5. Sign-off: YES/NO

Final message: 3 lines.
```
