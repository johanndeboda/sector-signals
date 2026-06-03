# Sector Signals — Project Handoff

**Last updated:** end of Day 10 (2026-06-02)
**Owner:** Johann
**Repo:** `sector-signals` (local: `C:\Users\Johan\sector-signals`, Windows, PowerShell, venv)

> This document is the single source of truth between work sessions. It is rebuilt/updated at the end of each working day. The next session should read it **in full** before doing anything. Items marked **[CONFIRM]** couldn't be verified from memory — check them against the repo before relying on them.

---

## 0. How to use this handoff

**Next Claude session — start here:**
1. Read this whole file first. Do not start coding until you have.
2. Go to §11 (Roadmap), pick the top item not yet done, start there.
3. Before writing code on any judgment call (where a file goes, which normalization approach, scope trade-offs), **ask Johann first** with a clear recommendation.
4. Follow §6 (How Claude should work) exactly — the working dynamic matters as much as the code.

**Johann — to update this at end of day:** say "update the handoff." Claude refreshes §9 (data state), §10 (progress log), §11 (roadmap), §12 (open items), keeping everything else current. Keep the structure identical session to session so handoffs stay consistent.

---

## 1. What this project is

A data pipeline + analysis project that tracks **hiring signals** (and later **patents**) across major US-listed **semiconductor companies** to infer where the industry is investing — by company, geography, and role type. Thesis: public job postings are a free, structured, leading signal of corporate intent (expansion, geographic strategy, R&D focus) that you can scrape, normalize, store, and analyze.

It is a **portfolio project** to land Johann a data/analyst **internship**. Every output is built to be (a) verifiable, (b) a differentiator, (c) something he can talk through in an interview, and (d) a vehicle for leveling up his technical skills.

---

## 2. Candidate profile, qualifications & goals

**Background**
- 2nd-year **MIS** major.
- Bay Area (Union City, CA).
- Hardware: Dell XPS 15. Dev env: Windows, PowerShell, VS Code, Python venv, local PostgreSQL.

**Technical skills — honest self-assessment (Day 1 baseline; update as he grows):**
- **Python:** can write scripts, use pandas, basic data cleaning.
- **SQL:** basic `SELECT`/`WHERE`/simple `JOIN`s (came from SQLite + DB Browser).
- **Excel:** pivots, VLOOKUP/XLOOKUP, basic formulas.
- **No prior experience (at Day 1):** Tableau, Power BI, PostgreSQL, cloud tools, NLP, forecasting.
- Through this project he has already started using PostgreSQL, SQLAlchemy, more advanced pandas, regex normalization, and matplotlib/seaborn — these are *new* skills being built live (see §4).

**Prior experience — Cadence Design Systems consulting (via Marketing Association).** A student consulting program for Cadence (a major EDA / semiconductor-design-software company). The team: analyzed Cadence's industry and competitors; ran an external touchpoint audit and a student-perception survey; synthesized the research into frameworks and improvement **prototypes for Cadence's social media, early-careers website, job listings, and a new benefits page**; and ran a **Generative Engine Optimization (GEO)** analysis (an emerging topic) to build further frameworks and refine the prototypes. He delivered weekly presentations (public-speaking + professional-conduct reps). **Takeaways: he already has real semiconductor/EDA domain knowledge and consulting-style "turn analysis into actionable business deliverables" experience.**

**Goals**
- **Primary target roles:** Business/Data Analyst (open to consulting, product, strategy, intelligence).
- **Target companies:** open — not narrowed to FAANG/Big 4/F500.
- **Timeline:** project **resume-ready by the start of fall internship recruiting (~Aug–Dec)**. As of Day 10 Johann wants it **effectively done in ~1–2 months (possibly less)** because **summer school is starting** and his time will compress. These are consistent: aim for a polished, finished **core by ~mid-July–August**. (See §11 — scope is triaged to this.)
- **Time commitment:** ~10–20 hrs/week over summer, **likely dropping** as summer school ramps. Plan for shrinking hours — favor work that compounds passively (see the scrape-automation pivot in §11).
- **Builds in public:** yes — willing to post **weekly LinkedIn updates** and maintain a **public GitHub**. (This is why the GitHub-rendered notebooks and a public dashboard URL matter; see §11.)

**What Johann is optimizing for (let this shape every build decision):**
1. **Measurable impact and results**, not just "I used X tool." Findings should be concrete and defensible.
2. A **clear differentiator** vs. other 2nd-year MIS candidates.
3. A **coherent interview story that builds on the Cadence experience** (see §3).
4. **Technical depth that signals "ready for an analyst internship."**

---

## 3. The interview story / why this project (the differentiator)

This is the narrative spine — Claude should frame outputs to reinforce it, and Johann should tell it this way:

> At Cadence (consulting), I worked on the *demand side* of semiconductor hiring — auditing and prototyping improvements to one company's job listings, early-careers site, and employer presence, including a GEO analysis. That made me ask: what does hiring activity across the *whole* semiconductor sector reveal about where the industry is actually investing? So I built a data pipeline to find out — scraping job postings from nine chip companies across five different ATS platforms, normalizing the mess, and analyzing it by company, geography, and role.

Why it's strong: it connects **domain knowledge** (EDA/semis) + **consulting deliverables** (frameworks, actionable insight) + **new technical depth** (pipelines, SQL, normalization, viz) into one coherent thread, on the *same industry and even the same artifact* (job listings) he already worked on. His GEO experience also ties directly to the project's planned **AI feature** (§11). Few 2nd-year MIS candidates have this kind of through-line — lean on it.

---

## 4. Learning goals — skills to grow (NOT just deliverables)

Johann explicitly wants to **expand his technical skills across everything this project touches**, and to *understand what Claude is doing* — not just receive finished work. Treat the project as a skill-building curriculum. As Claude works, it should **briefly explain the technique and why** (concise — a few sentences, not a lecture), so each piece is something Johann can explain in an interview.

Skill ladder this project develops (track progress; useful for the resume "skills demonstrated" list):
- **Python / pandas:** basic → intermediate/advanced (groupby, crosstab, apply, normalization functions, `.value_counts(normalize=True)`, reshaping).
- **SQL / PostgreSQL:** basic SELECT → intermediate (CTEs, `FILTER`, `STRING_AGG`, aggregation, window functions later, joins across tables). PostgreSQL from zero → comfortable.
- **Data cleaning / normalization:** regex, accent-folding, lexicon/override design, handling messy real-world fields (done for `location`; coming for `category`).
- **Analysis concepts:** concentration metrics (HHI), region/role mix, time-series deltas, and — interpretation discipline (claims must not outrun the data).
- **Data viz / BI:** matplotlib/seaborn (in progress) → **Tableau or Power BI** (new) for the dashboard.
- **Engineering practices:** idempotent ETL, git hygiene, environment/secrets management, scheduling/automation.
- **AI/API:** building a small Claude-API-powered feature (the "insight narrator," §11) — ties to his GEO background.
- **Verification & communication:** sourcing claims, building-in-public write-ups.

---

## 5. (intentionally merged — see §6)

---

## 6. How Claude should work on this — REPLICATE THIS DYNAMIC

The working style that's been effective. Match it.

1. **Concise & direct.** Lead with the answer/next action. Minimal fluff, minimal formatting on simple replies. Caveats short.
2. **Verify current info via search** when uncertain, especially anything going into the portfolio (headcounts, market facts, "why" attributions, tool terms). Example Day 10: verified NVDA's Israel/Mellanox base and Micron's Asia footprint before letting them anchor observations.
3. **Ask clarifying questions before big recommendations / architecture decisions.** Notebook placement, normalization strategy, scope trade-offs — surface the call with a recommendation; let Johann decide.
4. **Profile before you build.** Never commit to an approach blind — look at the actual data first (we profiled location strings before choosing regex-vs-mapping). Do the same for `category` next.
5. **Build iteratively and verifiably.** No large blind notebooks. Hand cells in stages; Johann runs them locally and pastes output; refine from real results.
6. **Claude can't run the code.** No DB/network in chat — Postgres is on Johann's local machine. Claude writes cells, Johann runs + pastes, Claude iterates. Plan around this loop.
7. **Don't hand fresh `.ipynb` files that would wipe local outputs.** Johann's local notebooks hold the real chart/table outputs needed for GitHub rendering. Give *cells to paste*, not replacement files.
8. **Observations & analysis = GUIDED QUESTIONS, then PRESSURE-TEST.** For interpretive writing: Claude gives the numbers + pointer to the cell + plain-language questions; **Johann writes the observation in his own words**; then Claude pressure-tests (flags claims that outrun evidence, logic errors, unsupported attributions) **without rewriting his prose**. Methodology boilerplate (e.g., a coverage caveat) is fine for Claude to draft; *interpretation* is his. This is how he learns and keeps the work authentically his.
9. **Teach as you go (§4).** Briefly explain each technique and why — concisely.
10. **DO NOT fabricate or over-sharpen prior findings.** *(Hard lesson from Day 10 — two mistakes; don't repeat.)* Reference only what's *actually written* in existing notebooks. Don't paraphrase a past conclusion from memory or add specificity that wasn't there (e.g., "fab expansion" → "US CHIPS-Act Idaho/NY"). **Never assert a finding that needs data not yet built** (e.g., "workforce shrank over the year" is impossible without the time-series delta). When a claim needs data Johann doesn't have, say so.
11. **Match existing conventions** (§8) so new code reads like the same author.
12. **Reinforce the interview story (§3) and build-in-public goal** — when a milestone lands, it's a LinkedIn-able moment; flag it.

---

## 7. Technical architecture

- **Stack:** Python 3.13.13; `pandas`, `SQLAlchemy` + `psycopg2`, `python-dotenv`, `matplotlib`, `seaborn`. Virtualenv `venv`. Jupyter for analysis.
- **Database:** PostgreSQL, **local on Johann's Windows machine** (`localhost:5432`). Credentials in `.env` (gitignored); connection string built from `DB_USER / DB_PASSWORD / DB_HOST / DB_PORT / DB_NAME`.
- **Repo layout** (**[CONFIRM]** exact tree against repo):
  - `etl/load_hiring.py` — main scraper/loader (~861 lines). Pulls open jobs from each company's ATS, normalizes to a common row shape, upserts into `hiring_signals`. Idempotent. Handles Workday's 2000-result cap via **faceted fetching** (re-queries per location facet) with location-facet auto-detection.
  - `etl/test_bulk_download.py` — patents spike (PatentsView S3 bulk download test). Patents pipeline not built out.
  - `analysis/01_hiring_snapshot.ipynb` — hiring footprint by ticker (done).
  - `analysis/02_hiring_geography.ipynb` — geographic spread (done Day 10).
  - `interview_moments.md` — Johann's running notes of interview talking points.
  - `.env` (gitignored), `.gitignore`, `schema.sql` **[CONFIRM]**.
- **9 active tickers:** NVDA, AMD, QCOM, MU, INTC, MRVL, CDNS, AVGO, TXN. **SNPS (Synopsys) disabled** (TalentBrew ATS needs HTML scraping).
- **ATS → ticker → location-field map** (matters for any field normalization):

  | ATS | Tickers | Raw location field |
  |-----|---------|--------------------|
  | Workday | NVDA, CDNS, MRVL, INTC, AVGO | `locationsText` (emits "N Locations" for multi-site roles!) |
  | Jibe | AMD | `full_location` |
  | Eightfold | QCOM, MU | `locations[0]` |
  | Oracle HCM | TXN | `PrimaryLocation` |
  | TalentBrew | SNPS (disabled) | scraped `<span class="job-location">` |

- **Key data-quality gotcha:** Workday returns a *count* ("2 Locations", "3 Locations", …) instead of a place for multi-site postings. ~12.9% of all postings — entirely the five Workday tickers, worst on NVDA — have no usable location; bucketed "Multiple (unspecified)". Recovering them needs per-job Workday detail requests ("enrichment") — logged stretch item, not done.

---

## 8. Conventions

- **Notebook connection cell:** `os` + `pandas` + `create_engine` + `load_dotenv()`; engine string from env vars; a small sanity `SELECT` as the output.
- **Charts:** seaborn `whitegrid`; `figsize` ~`(10,5)`–`(11,6)`; `steelblue` for single-series bars; data labels via `ax.text`; `plt.tight_layout()`.
- **Observations cells:** markdown, bold lead-in per observation + prose, ending with an "open question to test next." Written by Johann via the guided-questions method (§6.8). Header: "Observations — <topic> (Day N)".
- **Commits:** notebooks committed **with outputs intact** (render on GitHub as portfolio pieces). Always `Restart & Run All` → Save before committing. Stage files **explicitly** (`git add <file>`), never blind `git add -A`; keep `.env` out of every commit.
- **Build-in-public:** notebooks must render cleanly on public GitHub; milestones become weekly LinkedIn updates.

---

## 9. Data state (current)

- `hiring_signals`: ~**62,951** total historical rows; **~11,573** in the latest snapshot (9 tickers).
- Snapshots are **point-in-time**, keyed by `snapshot_date`. **[CONFIRM]** whether the daily scrape is **automated** — highest-leverage open question (§11).
- Geography normalization (Day 10): **87.1%** of latest-snapshot postings resolved to a country/region; 12.9% "Multiple"; **0.0%** unknown.
- Region totals (latest snapshot, resolved): Asia 5,143 · North America 3,814 · Europe 434 · Middle East 401 · Latin America 276 · Oceania 8.
- Top countries: US 3,611 · India 1,732 · Taiwan 1,183 · Singapore 1,005 · China 441 · Israel 373 · Japan 356 · Malaysia 271 · Canada 203 · Mexico 201.

---

## 10. Progress log & key findings

**Day 9 — `01_hiring_snapshot.ipynb` (footprint by ticker):**
- MU leads the open-jobs book (~3,024) ahead of NVDA (~2,654) — surprising given NVDA's profile; Johann attributed it to Micron's *fab expansion / staffing megaprojects* (he did **not** specify US fabs — don't add that).
- Raw counts overstate large/diversified firms; per-headcount, NVDA's hiring *intensity* (~6.3% open-role ratio) exceeds MU's (~5.7%).
- AVGO anomaly: very large (~$1T mkt cap, ~37k employees) but a notably *small* open-jobs book.
- Open question: is cross-ticker count driven by **geographic spread** or **role/sector breadth**?

**Day 10 — `02_hiring_geography.ipynb` (geographic spread) — DONE & pushed:**
- Location normalizer: 462 distinct raw strings → country + region via a 3-pass classifier (country-token substring match → US state name/abbr → curated city overrides), plus accent-folding, punctuation normalization, and a "N Locations" multi-site rule. 0.0% unknown. Auditable/explainable in an interview.
- Cross-ticker **region mix** (% of geo-resolved), a **concentration metric** (top-region share + regional HHI), and top-countries.
- Findings (Johann's, pressure-tested): **Asia outweighs North America** even for US-listed firms (5,143 vs 3,814); **MU most concentrated** (74% Asia, HHI 0.608); **NVDA the Middle East outlier** (~17%, ≈3× any peer — Israel, its largest R&D base outside the US, from the 2020 Mellanox acquisition); **AVGO most US-centric** (68% NA); **Intel most globally distributed** (lowest HHI; only firm with material Latin America + Middle East presence).
- Verified NVDA/Israel and Micron/Asia via web search before committing.
- **Process note:** Claude twice over-attributed Day 9 claims (sharpened "fab expansion" → "US CHIPS-Act fabs"; invented "workforce shrank YoY"). Both corrected. See §6.10 — do not repeat.
- Still-unproven claim in Johann's Day 10 observations: that Asian jobs are "production and manufacturing" — the geography data can't confirm role *type*. The **category analysis (next) is what tests it.**

---

## 11. Roadmap & prioritization (scoped to ~1–2 months / fall recruiting)

Triage hard against the deadline and shrinking hours. A finished, polished core beats a sprawling unfinished one. Bias toward work that compounds passively.

**HIGHEST-LEVERAGE — DO FIRST (compounds in the background):**
- **[CONFIRM + likely ACTION] Automate the daily scrape.** The project's most valuable signal is the **time-series delta** (how hiring books change over time), which needs snapshots *accumulating*. If `load_hiring.py` isn't already scheduled (Windows Task Scheduler / cron), set that up **now** — every un-scraped day is permanently lost data, and this runs itself while Johann is in summer school. Confirm current state; automate if manual.

**CORE (must-do for the portfolio):**
1. **Category mix analysis** (`03_hiring_category.ipynb` — Day 10 priority 2). Does role *type* vary by region/ticker (e.g., Asia weighted to manufacturing/ops vs. US to design/R&D)? Directly tests the unproven "production and manufacturing" claim. **Expect the same normalization problem as locations** — `category` is almost certainly ATS-specific; profile it first (§6.4).
2. **Snapshot-over-snapshot delta** (`04_hiring_trends.ipynb` — Day 10 priority 3). The flow signal: who's accelerating/decelerating. Depends on accumulated snapshots (hence the automation priority).
3. **The dashboard (capstone).** Interactive, multi-insight, showing how signals relate. **Tool: lean Tableau Public** — free public-URL publishing = a clean portfolio link, which fits the build-in-public goal (Power BI's free public-web sharing is more restricted). **Verify both tools' current free/publishing terms when scoping** (they change). Decide early; don't build twice. This is a brand-new skill for Johann — budget learning time.
4. **One concrete AI feature — pin it down, don't let it balloon.** Recommended: an **AI "insight narrator"** — feed the real analysis numbers to the Claude API and have it generate a plain-English readout of a chart/finding (buildable via the API-in-artifacts pattern). Ties to his **GEO background** and his "learn what Claude's doing" goal. Avoid vague "AI integration" that dilutes the project's real strength (engineering + verification rigor).

**STRETCH (only if time):**
- Patents pipeline + analysis (PatentsView). Currently a download spike only.
- **Cross-signal join (hiring × patents)** — where "how aspects relate" gets powerful; would elevate the dashboard. May get *promoted* to core if the dashboard leans on it — decide with Johann.
- Workday per-job location enrichment (recover the 12.9% "Multiple" bucket).

**CUT first if the deadline tightens:** deep patents work and the cross-signal join. Don't sacrifice a polished dashboard + finished hiring analyses for them.

---

## 12. Open decisions / TODOs

- **[CONFIRM]** Is the daily scrape automated? (Drives §11.)
- **[DECIDE]** Tableau vs Power BI — lean Tableau Public; verify current terms at scoping time.
- **[DECIDE]** Exact AI feature scope — recommend the "insight narrator"; confirm with Johann.
- **[DECIDE]** Promote cross-signal (hiring × patents) to core, or keep stretch?
- **[CONFIRM]** Repo tree, `schema.sql`, and patents table schema against the actual repo.
- **[TRACK]** Keep a running "skills demonstrated" list (§4) for the resume.
- Open analytical question (Day 9; partly answered by geography, fully once category is done): is cross-ticker hiring volume driven by geographic spread or role breadth?

---

## 13. Next session — exact starting point

Day 10 (geography) is shipped and pushed. Begin Day 11 by:
1. Reading this handoff fully.
2. **Confirming whether the daily scrape is automated** (§11 top item). If not, set it up first — highest leverage, compounds.
3. Then start **category mix analysis** (`03_hiring_category.ipynb`): profile the `category` field across ATSes first (§6.4), surface the placement/normalization call to Johann (§6.3), proceed iteratively (§6.5–6.7), write observations via guided questions + pressure-test (§6.8), and explain techniques as you go (§4/§6.9).