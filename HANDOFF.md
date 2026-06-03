# Sector Signals — Project Handoff

**Last updated:** end of Day 10 (2026-06-02)
**Owner:** Johann
**Repo:** `sector-signals` (local: `C:\Users\Johan\sector-signals`, Windows, PowerShell, venv, VS Code)

> This document is the single source of truth between work sessions. It is updated at the end of each working day. The next session must read it **in full** before doing anything. Items marked **[CONFIRM]** couldn't be verified from memory — check against the repo before relying on them.

---

## 0. How to use this handoff

**Next Claude session — start here:**
1. Read this whole file first. Do not start coding until you have.
2. Go to §10 (Roadmap), pick the top item not yet done, start there.
3. Before writing code on any judgment call (where a file goes, which normalization approach, scope trade-offs), **ask Johann first** with a clear recommendation.
4. Follow §5 (How Claude should work) exactly — the working dynamic matters as much as the code.

**How to WRITE the next handoff (do it this same way every time — Johann's explicit instruction):**
- At end of each working day, when Johann says "update the handoff," rewrite this file so the next session lands *exactly* where this one left off — including how to respond and operate, not just what was done.
- **Update:** §8 (data state), §9 (progress log — append the new day with key findings), §10 (roadmap — re-prioritize, mark done), §12 (open items), §13 (next-session start).
- **Preserve and keep current:** §1 (project), §2 (profile), §3 (interview story), §4 (learning goals), §5 (working style), §6 (architecture), §7 (conventions), §11 (recruiting & prep).
- **Rules:** Be comprehensive — do not trim for length; missing context is worse than a long doc. Keep `[CONFIRM]` markers honest (don't assert what you didn't verify). Never fabricate or over-sharpen prior findings (see §5.10). Record any mistakes made so they aren't repeated. Keep the section structure identical session to session.
- Johann replaces the repo's `HANDOFF.md` with the new version and commits it.

---

## 1. What this project is

A data pipeline + analysis project that scrapes and analyzes **hiring signals** across major US-listed **semiconductor companies** to infer where the industry is investing — by company, geography, and role type. Thesis: public job postings are a free, structured, leading signal of corporate intent (expansion, geographic strategy, R&D focus) that you can scrape, normalize, store, and analyze.

The data model is **architected for multiple signals** (patents, financials, stock) but this build **implements the hiring signal end-to-end** and demonstrates it thoroughly. Scope was deliberately tightened on Day 10 (see §10) to "one signal done well + dashboard + a light AI layer," prioritizing depth of understanding and a finishable, robust result over breadth.

It is a **portfolio project** to land Johann a data/analyst **internship**. Every output is built to be (a) verifiable, (b) a differentiator, (c) something he can explain in an interview, and (d) a vehicle for genuinely learning the technical skills involved.

---

## 2. Candidate profile, qualifications & goals

**Background**
- 2nd-year **MIS** major. Bay Area (Union City, CA). Dell XPS 15; Windows / PowerShell / VS Code / Python venv / local PostgreSQL.

**Technical skills — honest self-assessment (Day 1 baseline; update as he grows):**
- **Python:** can write scripts, use pandas, basic data cleaning.
- **SQL:** basic `SELECT`/`WHERE`/simple `JOIN`s (from SQLite + DB Browser).
- **Excel:** pivots, VLOOKUP/XLOOKUP, basic formulas.
- **No prior experience (Day 1):** Tableau, Power BI, PostgreSQL, cloud tools, NLP, forecasting.
- **Built live during this project:** PostgreSQL, SQLAlchemy, intermediate pandas, regex normalization, matplotlib/seaborn, git workflow, CTEs/aggregation in SQL. These are new skills in progress (see §4).

**Prior experience — Cadence Design Systems consulting (via Marketing Association).** Student consulting program for Cadence (a major EDA / semiconductor-design-software company). The team analyzed Cadence's industry and competitors; ran an external touchpoint audit and a student-perception survey; synthesized it into frameworks and improvement **prototypes for Cadence's social media, early-careers website, job listings, and a new benefits page**; and ran a **Generative Engine Optimization (GEO)** analysis to build further frameworks. He delivered weekly presentations (public-speaking + professional-conduct reps). **Takeaway: real semiconductor/EDA domain knowledge + consulting-style "turn analysis into actionable deliverables" experience.**

**Goals**
- **Primary target roles:** Business/Data Analyst (open to consulting, product, strategy, intelligence).
- **Target companies:** open — not narrowed.
- **Timeline:** project **resume-ready by the start of fall recruiting**; as of Day 10 Johann wants it **effectively done in ~1–2 months (possibly less)** because **summer school is starting** and time will compress. Aim for a polished, finished **core by ~mid-July–August**. (See §11 for the actual recruiting calendar — this target is well-calibrated.)
- **Time commitment:** ~10–20 hrs/week over summer, **likely shrinking**. Favor work that compounds passively (see scrape automation, §10).
- **Builds in public:** yes — willing to post **weekly LinkedIn updates** and maintain a **public GitHub**.

**What Johann is optimizing for (let this shape every build decision):**
1. **Measurable impact and results**, not just "I used X tool."
2. A **clear differentiator** vs. other 2nd-year MIS candidates.
3. A **coherent interview story that builds on the Cadence experience** (§3).
4. **Technical depth that signals "ready for an analyst internship."**
5. **Genuinely understanding everything he builds** (§4) — non-negotiable.

---

## 3. The interview story / why this project (the differentiator)

The narrative spine — reinforce it in outputs; Johann should tell it this way:

> At Cadence (consulting), I worked on the *demand side* of semiconductor hiring — auditing and prototyping improvements to one company's job listings, early-careers site, and employer presence, including a GEO analysis. That made me ask: what does hiring activity across the *whole* semiconductor sector reveal about where the industry is actually investing? So I built a data pipeline to find out — scraping job postings from nine chip companies across five different ATS platforms, normalizing the mess, and analyzing it by company, geography, and role.

Why it's strong: connects **domain knowledge** (EDA/semis) + **consulting deliverables** + **new technical depth** into one thread, on the *same industry and the same artifact* (job listings) he already worked on. His GEO experience ties directly to the planned AI layer (§10). Few 2nd-years have this through-line — lean on it.

---

## 4. Learning goals — Johann must UNDERSTAND, not just receive

Johann has stated this is a priority and a current weak point: he's uneasy building things he can't fully explain, and has started breaking down the ETL code one script at a time (with ChatGPT) to understand it. Treat the project as a skill-building curriculum, not just a deliverable.

- **Claude does code walkthroughs as part of building** — when introducing or touching code, explain *what it does and why*, in plain language at his level, concisely. Johann then does a "second-wave" pass with ChatGPT. (Confirmed workflow Day 10.)
- Offer to have Johann **explain code back** to check understanding when it matters.
- Reassurance that's true: **the hardest code is already done.** `load_hiring.py` (five ATS integrations, faceted Workday workaround, idempotent upserts) is the most technical piece. Remaining *core* work (category analysis, time-series, dashboard, light AI) is equal or lower complexity. Complexity only spikes with the **future** items (patents/financials/cross-signal) — which is partly why those were cut from core.

Skill ladder this project develops (track for the resume "skills demonstrated" list):
- Python/pandas: basic → intermediate/advanced (groupby, crosstab, apply, normalization, reshaping).
- SQL/PostgreSQL: basic SELECT → CTEs, `FILTER`, `STRING_AGG`, aggregation, joins, window functions; Postgres from zero → comfortable.
- Data cleaning/normalization: regex, accent-folding, lexicon/override design, messy real-world fields.
- Analysis concepts: concentration metrics (HHI), region/role mix, time-series deltas, interpretation discipline (claims must not outrun the data).
- Viz/BI: matplotlib/seaborn → Tableau (new).
- Engineering practices: idempotent ETL, git hygiene, secrets/env management, scheduling/automation.
- AI/API: the lightweight Claude-API "insight narrator" (ties to GEO background).
- Verification & communication: sourcing claims, building-in-public write-ups.

---

## 5. How Claude should work on this — REPLICATE THIS DYNAMIC

The working style that's been effective. Match it.

1. **Concise & direct.** Lead with the answer/next action. Minimal fluff, minimal formatting on simple replies. Short caveats.
2. **Verify current info via search** when uncertain, especially anything going into the portfolio (headcounts, market facts, "why" attributions, tool terms). Day 10 example: verified NVDA's Israel/Mellanox base and Micron's Asia footprint before they anchored observations.
3. **Ask clarifying questions before big recommendations / architecture decisions.** Notebook placement, normalization strategy, scope trade-offs — surface the call with a recommendation; let Johann decide.
4. **Profile before you build.** Never commit to an approach blind — look at the actual data first (we profiled location strings before choosing regex-vs-mapping). Do the same for `category` next.
5. **Build iteratively and verifiably.** No large blind notebooks. Hand cells in stages; Johann runs them locally and pastes output; refine from real results.
6. **Claude can't run the code.** No DB/network in chat — Postgres is on Johann's local machine. Claude writes cells, Johann runs + pastes, Claude iterates. Plan around this loop.
7. **Don't hand fresh `.ipynb` files that would wipe local outputs.** Johann's local notebooks hold the real chart/table outputs needed for GitHub rendering. Give *cells to paste*, not replacement files.
8. **Observations & analysis = GUIDED QUESTIONS, then PRESSURE-TEST.** For interpretive writing: Claude gives the numbers + pointer to the cell + plain-language questions; **Johann writes the observation in his own words**; then Claude pressure-tests (flags claims that outrun evidence, logic errors, unsupported attributions) **without rewriting his prose**. Methodology boilerplate (e.g., a coverage caveat) is fine for Claude to draft; *interpretation* is his. This is how he learns and keeps the work authentically his.
9. **Teach as you go (§4).** Explain each technique and why — briefly. Do code walkthroughs when asked or when introducing something new.
10. **DO NOT fabricate or over-sharpen prior findings.** *(Hard lesson from Day 10 — two mistakes; do not repeat.)* Reference only what's *actually written* in existing notebooks. Don't paraphrase a past conclusion from memory or add specificity that wasn't there (e.g., "fab expansion" → "US CHIPS-Act Idaho/NY"). **Never assert a finding that needs data not yet built** (e.g., "workforce shrank over the year" is impossible without the time-series delta). When a claim needs data Johann doesn't have, say so.
11. **Match existing conventions** (§7) so new code reads like the same author.
12. **Reinforce the interview story (§3) and build-in-public goal** — when a milestone lands, flag it as a LinkedIn-able moment.
13. **Protect scope (§10).** Johann reduced scope deliberately. Don't quietly re-expand it; if something tempts scope creep, name the trade-off and let him decide.

---

## 6. Technical architecture

- **Stack:** Python 3.13.13; `pandas`, `SQLAlchemy` + `psycopg2`, `python-dotenv`, `matplotlib`, `seaborn`. Virtualenv `venv`. Jupyter for analysis. PostgreSQL **18.3**, local (`localhost:5432`).
- **Credentials:** `.env` (gitignored), with `.env.example` as the template. Connection string from `DB_USER / DB_PASSWORD / DB_HOST / DB_PORT / DB_NAME`.
- **Repo layout** (verified Day 10):
  - `etl/load_hiring.py` — main scraper/loader (~861 lines). Pulls open jobs from each company's ATS, normalizes to a common row shape, upserts into `hiring_signals`. Idempotent. Handles Workday's 2,000-result cap via **faceted fetching** with location-facet auto-detection. *(This is the most technical file; Johann is studying it.)*
  - `etl/test_bulk_download.py` — patents spike (PatentsView S3 bulk download test). Patents pipeline not built.
  - `analysis/01_hiring_snapshot.ipynb` — hiring footprint by ticker (done).
  - `analysis/02_hiring_geography.ipynb` — geographic spread (done Day 10).
  - `sql/schema.sql` — full schema (see below).
  - `data/` — local raw cache (gitignored). `venv/` (gitignored).
  - `interview_moments.md` — Johann's running interview-talking-points notes.
  - `requirements.txt`, `.env.example`, `.gitignore`, `HANDOFF.md`, `README.md`.
  - **[CLEANUP]** a stray `notebooks/` folder exists (leftover from the Day-1 plan; real work is in `analysis/`). Delete if empty/legacy.

- **Schema (`sql/schema.sql`) — 6 tables, only one populated:**
  - `companies` — seeds a **12-ticker target universe**: CDNS, SNPS, ANSS (EDA); NVDA, AMD, QCOM, AVGO, MRVL (Fabless); INTC, MU, TXN (IDM); TSM (Foundry). Columns: ticker, name, segment, hq_country.
  - `hiring_signals` — **THE populated table.** One row per (job_id, snapshot_date), so the same posting captured on different days yields multiple rows (enables first-seen/last-seen/posting-age). Columns: job_id, ticker, snapshot_date, title, location (raw), posted_date, category (derived later, NULL on ingest), ats, job_url, captured_at. Indexed on (ticker, snapshot_date) and (ticker).
  - `financials_quarterly`, `stock_prices_daily`, `patents` — **defined but EMPTY** (scaffolding for the multi-signal vision; future work).
  - `job_postings` — **legacy/dead table** superseded by `hiring_signals`; unused. **[CLEANUP]** consider dropping to avoid confusion.
- **Active vs seeded:** 12 tickers seeded; **9 active in the hiring pipeline** (AMD, AVGO, CDNS, INTC, MRVL, MU, NVDA, QCOM, TXN). SNPS seeded but disabled (TalentBrew needs HTML scraping); ANSS and TSM seeded but not scraped.
- **ATS → ticker → location-field map** (matters for field normalization):

  | ATS | Tickers | Raw location field |
  |-----|---------|--------------------|
  | Workday | NVDA, CDNS, MRVL, INTC, AVGO | `locationsText` (emits "N Locations" for multi-site roles!) |
  | Jibe | AMD | `full_location` |
  | Eightfold | QCOM, MU | `locations[0]` |
  | Oracle HCM | TXN | `PrimaryLocation` |
  | TalentBrew | SNPS (disabled) | scraped `<span class="job-location">` |

- **Key data-quality gotcha:** Workday returns a *count* ("2 Locations", "3 Locations", …) instead of a place for multi-site postings. ~12.9% of all postings — entirely the five Workday tickers, worst on NVDA — have no usable location; bucketed "Multiple (unspecified)". Recovering them needs per-job Workday detail requests ("enrichment") — logged future item, not done.

---

## 7. Conventions

- **Notebook connection cell:** `os` + `pandas` + `create_engine` + `load_dotenv()`; engine string from env vars; a small sanity `SELECT` as the output.
- **Charts:** seaborn `whitegrid`; `figsize` ~`(10,5)`–`(11,6)`; `steelblue` for single-series bars; data labels via `ax.text`; `plt.tight_layout()`.
- **Observations cells:** markdown, bold lead-in per observation + prose, ending with an "open question to test next." Written by Johann via the guided-questions method (§5.8). Header: "Observations — <topic> (Day N)".
- **Commits:** notebooks committed **with outputs intact** (render on GitHub). Always `Restart & Run All` → Save before committing. Stage files **explicitly** (`git add <file>`), never blind `git add -A`; keep `.env` out of every commit.
- **Build-in-public:** notebooks render cleanly on public GitHub; milestones become weekly LinkedIn updates.

---

## 8. Data state (current)

- `hiring_signals`: **62,951** total historical rows; **11,573** in the latest snapshot (9 active tickers).
- Snapshots are **point-in-time**, keyed by `snapshot_date`. **[CONFIRM]** whether the daily scrape is **automated** — highest-leverage open question (§10).
- Geography normalization (Day 10): **87.1%** of latest-snapshot postings resolved to a country; 12.9% "Multiple (unspecified)"; **0.0%** unknown.
- Region totals (latest snapshot, resolved): Asia 5,143 · North America 3,814 · Europe 434 · Middle East 401 · Latin America 276 · Oceania 8.
- Top countries: US 3,611 · India 1,732 · Taiwan 1,183 · Singapore 1,005 · China 441 · Israel 373 · Japan 356 · Malaysia 271 · Canada 203 · Mexico 201.

---

## 9. Progress log & key findings

**Day 9 — `01_hiring_snapshot.ipynb` (footprint by ticker):**
- MU leads the open-jobs book (~3,024) ahead of NVDA (~2,654) — surprising given NVDA's profile; Johann attributed it to Micron's *fab expansion / staffing megaprojects* (he did **not** specify US fabs — don't add that).
- Raw counts overstate large/diversified firms; per-headcount, NVDA's hiring *intensity* (~6.3% open-role ratio) exceeds MU's (~5.7%).
- AVGO anomaly: very large (~$1T mkt cap, ~37k employees) but a notably *small* open-jobs book.
- Open question: is cross-ticker count driven by **geographic spread** or **role/sector breadth**?

**Day 10 — `02_hiring_geography.ipynb` (geographic spread) — DONE & pushed:**
- Location normalizer: 462 distinct raw strings → country + region via a 3-pass classifier (country-token match → US state name/abbr → curated city overrides), plus accent-folding, punctuation normalization, and a "N Locations" multi-site rule. 0.0% unknown. Auditable/explainable.
- Cross-ticker **region mix**, a **concentration metric** (top-region share + regional HHI), and top-countries.
- Findings (Johann's, pressure-tested): **Asia > North America** even for US-listed firms (5,143 vs 3,814); **MU most concentrated** (74% Asia, HHI 0.608); **NVDA the Middle East outlier** (~17%, ≈3× any peer — Israel, its largest R&D base outside the US, from the 2020 Mellanox acquisition); **AVGO most US-centric** (68% NA); **Intel most globally distributed** (lowest HHI; only firm with material Latin America + Middle East presence).
- Verified NVDA/Israel and Micron/Asia via web search before committing.
- Also done Day 10: **scope tightened** (§10), **README rewritten** for accuracy, **this handoff expanded**.
- **Process notes:** Claude twice over-attributed Day 9 claims (sharpened "fab expansion" → "US CHIPS-Act fabs"; invented "workforce shrank YoY"). Both corrected. See §5.10 — do not repeat. Still-unproven claim in Johann's Day 10 observations: that Asian jobs are "production and manufacturing" — geography data can't confirm role *type*; the **category analysis (next) tests it.**

---

## 10. Roadmap & prioritization (tightened scope, ~1–2 months / fall recruiting)

Scope was deliberately reduced on Day 10 to **one signal done well**: depth + understanding + a finishable, robust result over breadth. Don't re-expand it silently (§5.13).

**HIGHEST-LEVERAGE — DO FIRST (compounds in the background):**
- **[CONFIRM + likely ACTION] Automate the daily scrape.** The most valuable signal is the **time-series delta**, which needs snapshots *accumulating*. If `load_hiring.py` isn't already scheduled (Windows Task Scheduler), set that up **now** — every un-scraped day is permanently lost data, and it runs itself while Johann is in summer school.

**CORE (the committed scope):**
1. **Category mix analysis** (`03_hiring_category.ipynb`). Does role *type* vary by region/ticker (Asia → manufacturing/ops vs. US → design/R&D)? Directly tests the unproven "production and manufacturing" claim. **Expect the same normalization problem as locations** — the `category` field is currently NULL on ingest and will need a classifier; profile it first (§5.4).
2. **Snapshot-over-snapshot delta** (`04_hiring_trends.ipynb`). Who's accelerating/decelerating hiring over time. Depends on accumulated snapshots (hence the automation priority).
3. **Dashboard (capstone).** Interactive, multi-insight, in **Tableau Public** (free public-URL publishing = clean portfolio link; verify current terms when scoping). Brand-new skill for Johann — budget learning time.
4. **Lightweight AI insight layer.** A small (~20–40 line) notebook/script function: feed the real analysis numbers to the Claude API → get a plain-English readout. Ties to his GEO background and his "learn what Claude's doing" goal. **Keep it lightweight — do NOT try to embed live AI inside Tableau** (that's the version that becomes a lot of work).

**FUTURE (out of current scope — schema already accommodates):**
- **Patents** (USPTO/PatentsView) — *earn-it stretch*: only if the core finishes early. It's the second signal that would unlock the differentiating **cross-signal analysis (hiring × patents)** — but it's a whole new scraper + normalizer and the main source of added complexity/timeline risk. Don't commit the timeline to it.
- **Financials** (SEC EDGAR / market data).
- **Cross-signal analysis.**
- Workday per-job location enrichment (recover the 12.9% "Multiple" bucket).

---

## 11. Recruiting & prep (so the strategy survives to next session)

**Summer-2027 internship timing (verified Day 10 — recruiting runs much earlier than people expect):**
- **Wave 1 (Jul–Oct 2026):** finance, Big Tech, top consulting. Tech specifically opens Jul–Oct (Amazon/Databricks Jul–Aug; Google ~mid-Oct, 2–4 week window). Big 4 advisory ~Aug 2026.
- **Wave 2 (Nov 2026–Feb 2027):** most mid-size companies; peaks Dec–Feb — the bulk of data/business-analyst roles.
- **Wave 3 (Mar–May 2027):** startups, nonprofits, government, smaller firms.
- MBB consulting 2027 cycle is largely closed already (priority rounds Jan–Apr 2026; Bain R2 to Aug 31).
- **Rule:** apply within the first ~2 weeks of any posting (mostly rolling); set up alerts on LinkedIn / Handshake / company career pages starting July 2026. Johann's "done by ~August" target is well-calibrated.

**Setup tips (highest leverage first):**
1. **README is the most-read file** — keep it accurate, lead with what's built, add a chart screenshot (one image proves it's real).
2. **Quantify everything on the resume** (e.g., "scraped ~11.5k postings across 9 firms / 5 ATS platforms; normalized 460+ location formats to 100% coverage; surfaced finding X").
3. **Rehearse the Cadence → project story** (§3) in 30-second and 2-minute versions.
4. **Build in public:** weekly LinkedIn post, each with ONE concrete finding (not "I learned pandas").
5. **Referrals beat cold applications** — use Cadence/Marketing Association contacts and the school's LinkedIn alumni tool; the project is a natural reason to reach out for a 15-min informational chat.

**Interview fundamentals checklist (practice these cold):**
- **SQL:** write `GROUP BY` + aggregate, `INNER` vs `LEFT JOIN`, and a CTE (`WITH`) from scratch. (He's already used GROUP BY and CTEs in this project; the join muscle is the gap — practice by adding a `companies`-to-`hiring_signals` join to compute hiring intensity. DataLemur / StrataScratch for reps.)
- **Excel:** build a pivot table (it's the same operation as a SQL GROUP BY / pandas crosstab — rebuild the geography `mix` table as a pivot to internalize that).
- **Explain a chart in 3 layers:** what it shows → so what (business meaning) → now what (what a decision-maker does). Most candidates stop at layer 1.
- **STAR behavioral stories** (write ~5–6, rehearse aloud). Project material maps cleanly: hard technical problem = the 5-ATS normalizer; found-an-insight = the geography findings; *was-wrong/intellectual-honesty* = caught the Day-9 over-attribution and built an honest coverage caveat (a strong one); teamwork/communication = Cadence presentations; initiative/self-teaching = built the pipeline solo.

---

## 12. Open decisions / TODOs

- **[CONFIRM]** Is the daily scrape automated? (Drives §10.)
- **[CONFIRM]** README screenshot: export the geography chart to `docs/` and add it.
- **[CLEANUP]** Delete the stray `notebooks/` folder (if empty/legacy) and consider dropping the dead `job_postings` table.
- **[DECIDE later]** Tableau vs Power BI — leaning Tableau Public; verify current free/publishing terms at scoping time.
- **[DECIDE later]** Whether to promote patents (cross-signal) from future to core — only if core finishes early.
- **[TRACK]** Keep a running "skills demonstrated" list (§4) for the resume.
- Open analytical question (Day 9; partly answered by geography, fully once category is done): is cross-ticker hiring volume driven by geographic spread or role breadth?

---

## 13. Next session — exact starting point

Day 10 shipped: geography analysis (pushed), corrected README, tightened scope, this handoff. Begin Day 11 by:
1. Reading this handoff fully.
2. **Confirming whether the daily scrape is automated** (§10 top item). If not, set it up first — highest leverage, compounds.
3. Then start **category mix analysis** (`03_hiring_category.ipynb`): profile the `category` source field across ATSes first (§5.4), surface the placement/normalization call to Johann (§5.3), proceed iteratively (§5.5–5.7), write observations via guided questions + pressure-test (§5.8), and explain techniques / offer a walkthrough as you go (§4, §5.9).