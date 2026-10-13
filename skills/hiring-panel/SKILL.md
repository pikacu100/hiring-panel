---
name: hiring-panel
description: Review, fact-check and rebuild a CV/resume with a panel of AI reviewers — an ATS screen plus five blind personas (CEO, 30-second recruiter, competing applicant, hiring manager, future teammate). Reviewers judge independently, then debate each other's findings; the CV is rewritten and re-checked until the panel signs off. Works from existing CVs, a LinkedIn PDF export and/or a GitHub profile, and outputs content-identical CVs in any languages the user picks (MD, HTML, PDF). Use when the user runs /hiring-panel or asks to review, roast, rebuild or translate their CV/resume.
---

# Hiring Panel

Goal: one finished CV, rendered in **every language the user asked for, identical in content**, that survived an independent review, a group debate and a re-check — built only from facts the user can defend.

Talk to the user in the language they write to you in. Write each CV in its own language. Prompts for subagents are in English.

Supporting files in this skill's base directory:
- `references/prompts.md` — subagent prompt templates (ATS, reviewer, debate, sign-off)
- `scripts/cv2html.py` — renders the CV Markdown into a one-column, ATS-friendly A4 HTML page

## 0. Intake

Collect, from the user's message or with **one** AskUserQuestion round (only for what is missing):

1. **Sources** (any combination, at least one):
   - **Existing CVs** — file paths or a folder (PDF, DOCX, MD, TXT), any language, any number.
   - **LinkedIn** — ask for a **PDF export** (profile → *More* → *Save to PDF*). Direct fetching of linkedin.com is almost always blocked (HTTP 999); try the URL once if given, then ask for the PDF.
   - **GitHub** — a username or profile URL.
   - Other public links: portfolio, App Store / Google Play listings, personal site.
2. **Output languages** — e.g. `en`, `cs`, `de`. Default: the languages of the supplied CVs; if there are none, the user's conversation language; if that is not English, offer English as a second.
3. **Target** — a job posting (URL, file or text) or a target role ("general mobile developer", "senior data engineer", …). If none, use the role the sources imply and say so.

Tell the user the cost in one line: one full round = 11 subagent runs (ATS + 5 reviews + 5 debates); up to 3 rounds.

## 1. Working folder

Create `<folder of the first CV, or the current directory>/.hiring-panel/<YYYY-MM-DD_HHMM>/`. **Never modify the user's original files.**

```
sources/            faithful Markdown extractions of every source (cv_<lang>.md, linkedin.md, github.md, …)
facts.md            single source of truth (see below)
00_conflicts.md     contradictions and gaps between sources
round-N/            ats.md, review_<id>.md, debate_<id>.md, verdict.md, cv_<lang>.md, parity.md
final/              CV_<Name>_<LANG>.md / .html / .pdf
REPORT.md           summary for the user, in the user's language
```

## 2. Facts (the part that matters most)

1. **Extract** every source faithfully into `sources/`.
   - CVs and LinkedIn PDF: the Read tool reads PDFs; for DOCX use any available converter.
   - GitHub (public API, no auth needed):
     - `https://api.github.com/users/<user>` (name, company, blog, location, bio)
     - `https://api.github.com/users/<user>/repos?per_page=100&sort=updated` (mark forks — **forks are not contributions**)
     - `https://raw.githubusercontent.com/<user>/<user>/HEAD/README.md` (profile README)
     - READMEs of the top non-fork repos
     - Follow store / website links you find and record what they verifiably show (downloads, ratings, publisher).
2. **Build `facts.md`**: every employer, title, date, school, skill, number, project and link, each tagged with its source(s). Mark what is self-described (bio, README claims) vs. verified (store listing, live link).
3. **Write `00_conflicts.md`**: date or title mismatches between sources, facts present in one source only, broken or truncated links, outdated info (e.g. "student" after graduation), facts that exist on GitHub/LinkedIn but are missing from the CVs.
4. **Fact interview** — ask the user (one AskUserQuestion, ≤4 questions) only about:
   - real contradictions (different dates for the same job);
   - **high-value gaps** typical reviewers will hunt for in this role and that the sources don't answer — e.g. for engineers: state management / architecture, testing, release ownership, scale (users, traffic, revenue), team size. Offer "don't include" as an option.
   Record answers in `facts.md` under *Confirmed by user*, including any limits the user sets ("only this number", "don't mention X").

**Hard rule for the whole run:** no agent may invent employers, titles, dates, technologies, numbers or results. Unknown but useful numbers become placeholders — `[ADD: …]` in English, translated in other languages — unless the user said not to use any. Collect all placeholders for the report.

## 3. Round loop

For round N (start at 1):

### 3a. ATS screen + independent panel — one message, 6 parallel subagents
Launch with the Agent tool (`general-purpose`), all in **one message** so they run in parallel and blind:
- 1× **ATS** prompt from `references/prompts.md`.
- 5× **Reviewer** prompt, one per persona:

| id | Persona | Reads the CV as… |
|---|---|---|
| `ceo` | CEO / founder of the hiring company | Does this person move the business? Impact, ownership, seniority signal, judgment. |
| `recruiter` | Recruiter with 30 seconds | Skim test: what sticks in 6 s, red flags, gaps, length, clarity of target role, working links. |
| `rival` | Another applicant for the same job | Competitive: where would I beat this CV? What is generic, unproven, padded? |
| `hiring_manager` | The manager they'd report to | Can they do the job from day one? Concrete skills, depth vs. buzzwords, role-specific signals. |
| `teammate` | The future colleague at the next desk | Credibility, overclaiming, collaboration, would claims survive a 10-minute technical chat? |

Adapt each persona's context to the target role and market (e.g. "Czech tech market", "US fintech", "agency in Berlin").

### 3b. Debate — 5 parallel subagents
When all reviews exist, launch the **Debate** prompt once per persona, in one message. Each reads all five reviews plus the ATS report and argues: agree / disagree / changed my mind / final top changes / updated score.

### 3c. Moderator verdict — you
Read every review and debate, write `round-N/verdict.md`:
- score table (review, debate as-is, projected);
- fix list **worst first**: quoted line, problem, how many reviewers back it, and how each disagreement was resolved and **why** (favour the side that stays within `facts.md` and avoids overclaiming);
- keep-unchanged list; rejected suggestions with reasons.

### 3d. Rewrite — all languages from one structure
Write `round-N/cv_<lang>.md` for every output language:
- One content structure, rendered into each language: same sections, same order, same roles, dates, bullets, numbers, skills, links.
- Translate naturally, using that market's CV conventions (section names, date format `MM/YYYY`, register). Job titles may stay in English where the local market searches for them in English — say so in the verdict.
- Follow the **CV Markdown format** below so the renderer works.
- **Parity check**: compare all languages bullet by bullet; fix drift; write `round-N/parity.md`.

### 3e. Next round or stop
Round N+1 reviewers also get the previous `verdict.md` and must report which fixes landed.
- From round 2 on, if the panel only needs confirmation, use the lighter **Sign-off** prompt instead of the full review.
- Skip the debate only when all five raise the **same** single issue or none.

**Stop** when any is true:
- every reviewer votes interview with ≥ 8/10 in every language **and** ATS passes every language;
- the latest round produced no new high-priority fixes;
- 3 rounds are done — report what is still open.

## 4. CV Markdown format

```markdown
# FULL NAME
**Headline — role · focus**
City, Country · +phone · email · linkedin.com/in/… · github.com/…

## SECTION
Paragraph text.

**Job title** | Company | Location | MM/YYYY – present
*Optional one-line description of the company or product.*
- Bullet starting with a verb
- Links as [label](https://…) or bare linkedin.com/… / github.com/…
```

Line 1 = name, line 2 = bold headline, line 3 = contact line; `**…** | …` lines are role headers. No tables, no columns, no icons.

## 5. Final output

1. Copy the last round's CVs to `final/CV_<Name>_<LANG>.md`, then render each:
   ```
   python <skill_dir>/scripts/cv2html.py final/CV_<Name>_<LANG>.md final/CV_<Name>_<LANG>.html <lang-code> "CV <Name>"
   ```
2. Print each HTML to PDF with a headless Chromium browser. Look for one in this order:
   - Windows: `C:\Program Files\Google\Chrome\Application\chrome.exe`, `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`, `%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe`
   - macOS: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge`
   - Linux: `google-chrome`, `chromium`, `chromium-browser`, `microsoft-edge` on PATH
   ```
   <browser> --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="<out.pdf>" "file:///<absolute path to .html>"
   ```
   If none is found, tell the user to open the HTML and print to PDF.
3. **Verify**: open each PDF with the Read tool — 1 page (2 max for senior profiles), nothing cut off, links present. If it overflows, tighten wording (not font size) and re-render.
4. Write `REPORT.md` in the user's language:
   - score table per reviewer per round, ATS before/after;
   - key debate outcomes and why;
   - list of changes;
   - parity confirmation;
   - every placeholder to fill in;
   - open questions (facts that would strengthen the CV if confirmed);
   - issues found in the sources themselves (e.g. typos on GitHub, broken LinkedIn URL).
5. Finish in chat (user's language): final scores, the 3 biggest changes, placeholders, open questions, and the paths to the PDFs.

## Privacy

Everything stays on the user's machine. Fetch only public pages the user pointed to (or that those pages link to). Never submit the user's data to forms, newsletters or third-party services.
