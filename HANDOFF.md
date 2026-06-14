# Sector Signals — Project Handoff

**Last updated:** end of Day 11 (2026-06-14)
**Owner:** Johann
**Repo:** `sector-signals` — public: https://github.com/johanndeboda/sector-signals (local: `C:\Users\Johan\sector-signals`, Windows, PowerShell, venv, VS Code). README and this handoff are committed and current as of Day 11.

> This document is the single source of truth between work sessions. It is updated at the end of each working day. The next session must read it **in full** before doing anything. Items marked **[CONFIRM]** couldn't be verified from memory — check against the repo before relying on them.

---

## 0. How to use this handoff

**Next Claude session — start here:**
1. Read this whole file first. Do not start coding until you have.
2. Go to §13 (Next session — exact starting point) and begin there. §10 has the full roadmap.
3. Before writing code on any judgment call (where a file goes, which normalization approach, scope trade-offs), **ask Johann first** with a clear recommendation.
4. Follow §5 (How Claude should work) exactly — the working dynamic matters as much as the code.

**How to WRITE the next handoff (do it this same way every time — Johann's explicit instruction):**
- At end of each working day, when Johann says "update the handoff," rewrite this file so the next session lands *exactly* where this one left off — including how to respond and operate, not just what was done.
- **Update:** §8 (data state), §9 (progress log — append the new day with key findings), §10 (roadmap — re-prioritize, mark done), §12 (open items), §13 (next-session start).
- **Preserve and keep current:** §1 (project), §2 (profile), §3 (interview story), §4 (learning goals), §5 (working style), §6 (architecture), §7 (conventions), §11 (recruiting & prep).
- **Rules:** Be comprehensive — do not trim for length; missing context is worse than a long doc. Keep `[CONFIRM]` markers honest (don't assert what you didn't verify). Never fabricate or over-sharpen prior findings (see §5.10). Record any mistakes made so they aren't repeated. Keep the section structure identical session to session.
- Johann replaces the repo's `HANDOFF.md` with the new version and commits it. **Never put secrets (DB passwords, connection strings with credentials) in this file or any committed file.**

---

## 1. What this project is

A data pipeline + analysis project that scrapes and analyzes signals across major US-listed **semiconductor companies** to infer where the industry is investing — by company, geography, and role type. Core thesis: public job postings are a free, structured, leading signal of corporate intent (expansion, geographic strategy, R&D focus) that you can scrape, normalize, store, and analyze.

The data model is **architected for multiple signals**, and as of Day 11 **three secondary signals are actually built and loaded** (patents, financials, stock prices) in addition to the primary hiring signal. The **hiring signal is the spine** of the analysis and the most developed. The committed core (see §10) remains "hiring done well + dashboard + a light AI layer," now with a **cross-signal angle** available because the other data is already in the warehouse.

It is a **portfolio project** to land Johann a data/analyst **internship**. Every output is built to be (a) verifiable, (b) a differentiator, (c) something he can explain in an interview, and (d) a vehicle for genuinely learning the technical skills involved.

---

## 2. Candidate profile, qualifications & goals

**Background**
- 2nd-year **MIS** major, SJSU (projected grad 2028). Bay Area. Windows / PowerShell / VS Code / Python venv / PostgreSQL.

**Technical skills — honest self-assessment (Day 1 baseline; update as he grows):**
- **Python:** scripts, pandas, basic data cleaning → now intermediate (groupby/crosstab/normalization).
- **SQL:** basic `SELECT`/`WHERE`/`JOIN` → now CTEs, aggregation, `STRING_AGG`, `GROUP BY ... HAVING`.
- **Excel:** pivots, VLOOKUP/XLOOKUP, formulas.
- **Built live during this project:** PostgreSQL, SQLAlchemy, regex normalization, matplotlib/seaborn, git workflow. **New as of Day 11:** GitHub Actions / CI, cloud Postgres (Neon), `pg_dump`/`pg_restore` database migration, secrets management, the datacenter-IP/scraping consideration.
- **Still ahead:** Tableau (dashboard), the lightweight Claude-API insight layer.

**Prior experience — Cadence Design Systems consulting (via SJSU Marketing Association).** Student consulting for Cadence (a major EDA / semiconductor-design-software firm): analyzed Cadence's industry and competitors; ran an external touchpoint audit and student-perception survey; built improvement **prototypes for social media, the early-careers website, job listings, and a benefits page**; ran a **Generative Engine Optimization (GEO)** analysis. Weekly presentations (public-speaking reps). **Takeaway: real semiconductor/EDA domain knowledge + consulting "turn analysis into deliverables" experience.**

**Goals**
- **Primary target roles:** Business/Data Analyst, Business Intelligence, Data Analyst (open to consulting, product, strategy). California preferred, open to relocation.
- **Recruiting:** rising junior, targeting **Summer 2027** internships.
- **Timeline:** Johann wants the project **effectively done by the start of July 2026** (summer school compresses his time). This is achievable for the **snapshot-based core**; the time-series/trends piece is the one part that can't make July 1 because it needs weeks of accumulated data — it's deferred to a mid-July "v2" (see §10).
- **Time commitment:** ~10–20 hrs/week, likely shrinking. Favor work that compounds passively (hence the cloud automation, §10).
- **Builds in public:** yes — weekly LinkedIn updates, public GitHub.

**What Johann is optimizing for (let this shape every build decision):**
1. **Measurable impact and results**, not just "I used X tool."
2. A **clear differentiator** vs. other 2nd-year MIS candidates.
3. A **coherent interview story that builds on the Cadence experience** (§3).
4. **Technical depth that signals "ready for an analyst internship."**
5. **Genuinely understanding everything he builds** (§4) — non-negotiable.

---

## 3. The interview story / why this project (the differentiator)

The narrative spine — reinforce it in outputs; Johann should tell it this way:

> At Cadence (consulting), I worked on the *demand side* of semiconductor hiring — auditing and prototyping improvements to one company's job listings, early-careers site, and employer presence, including a GEO analysis. That made me ask: what does hiring activity across the *whole* semiconductor sector reveal about where the industry is actually investing? So I built a data pipeline to find out — scraping job postings from nine chip companies across five different ATS platforms, normalizing the mess, and analyzing it by company, geography, and role — then automated it as a scheduled cloud pipeline so the data collects itself.

Why it's strong: connects **domain knowledge** (EDA/semis) + **consulting deliverables** + **new technical depth** into one thread, on the *same industry and the same artifact* (job listings) he already worked on. His GEO experience ties directly to the planned AI layer (§10). Few 2nd-years have this through-line — lean on it.

---

## 4. Learning goals — Johann must UNDERSTAND, not just receive

Johann has stated this is a priority: he's uneasy building things he can't fully explain, and breaks down the code one script at a time (second-wave pass with ChatGPT). Treat the project as a skill-building curriculum, not just a deliverable.

- **Claude does code walkthroughs as part of building** — when introducing or touching code, explain *what it does and why*, in plain language at his level, concisely.
- Offer to have Johann **explain code back** to check understanding when it matters.
- Reassurance that's true: **the hardest code is already done.** `load_hiring.py` (five ATS integrations, faceted Workday workaround, idempotent upserts) is the most technical piece. The patents/financials pipelines are also built (Johann confirmed Day 11 he can explain them). Remaining core work (category analysis, cross-signal, dashboard, light AI) is equal or lower complexity.

Skill ladder this project develops (track for the resume "skills demonstrated" list):
- Python/pandas: basic → intermediate (groupby, crosstab, apply, normalization, reshaping).
- SQL/PostgreSQL: basic SELECT → CTEs, `FILTER`, `STRING_AGG`, `GROUP BY ... HAVING`, aggregation, joins, window functions.
- Data cleaning/normalization: regex, accent-folding, lexicon/override design, assignee-name → ticker mapping.
- Analysis concepts: concentration metrics (HHI), region/role mix, time-series deltas, **interpretation discipline (claims must not outrun the data)**.
- Viz/BI: matplotlib/seaborn → Tableau (new).
- **Engineering practices: idempotent ETL, git hygiene, secrets/env management, CI/CD (GitHub Actions), cloud database (Neon), DB migration. (Several added Day 11.)**
- AI/API: the lightweight Claude-API "insight narrator" (ties to GEO background).
- Verification & communication: sourcing claims, building-in-public write-ups.

---

## 5. How Claude should work on this — REPLICATE THIS DYNAMIC

The working style that's been effective. Match it.

1. **Concise & direct.** Lead with the answer/next action. Minimal fluff, minimal formatting on simple replies. Short caveats.
2. **Verify current info via search** when uncertain, especially anything going into the portfolio (headcounts, market facts, "why" attributions, tool terms). Day 11 examples: verified the Synopsys–Ansys close date and Neon's free-tier + Postgres-18 support before relying on them.
3. **Ask clarifying questions before big recommendations / architecture decisions.** Surface the call with a recommendation; let Johann decide.
4. **Profile before you build.** Never commit to an approach blind — look at the actual data first. (Day 11: profiled every table before drawing conclusions.)
5. **Build iteratively and verifiably.** No large blind notebooks. Hand cells in stages; Johann runs them locally and pastes output; refine from real results.
6. **Claude can't run the code.** No DB/network in chat. Claude writes cells/commands, Johann runs + pastes, Claude iterates. Plan around this loop.
7. **Don't hand fresh `.ipynb` files that would wipe local outputs.** Give *cells to paste*, not replacement files. Throwaway exploration cells are fine.
8. **Observations & analysis = GUIDED QUESTIONS, then PRESSURE-TEST.** For interpretive writing: Claude gives the numbers + pointer to the cell + plain-language questions; **Johann writes the observation in his own words**; then Claude pressure-tests (flags claims that outrun evidence, logic errors, unsupported attributions) **without rewriting his prose**. Methodology boilerplate is fine for Claude to draft; *interpretation* is his.
9. **Teach as you go (§4).** Explain each technique and why — briefly. Do code walkthroughs when asked or when introducing something new (Day 11: walked through the GitHub Actions YAML and the de-risk logic).
10. **DO NOT fabricate or over-sharpen prior findings, or assume undocumented state.** Reference only what's *actually* in the repo/DB. Never assert a finding that needs data not yet built. When a claim needs data Johann doesn't have, say so. (Day 11: the handoff itself was found badly stale — always verify against the live repo/DB, not memory.)
11. **Match existing conventions** (§7) so new code reads like the same author.
12. **Reinforce the interview story (§3) and build-in-public goal** — when a milestone lands, flag it as a LinkedIn-able moment and capture it in `interview_moments.md`.
13. **Protect scope (§10).** Don't quietly re-expand scope; if something tempts scope creep, name the trade-off and let him decide. (Day 11: kept the patents-curiosity side-quest from ballooning; deferred trends to protect the July-1 core.)
14. **Security:** never have Johann paste secrets (DB passwords, full connection strings) into chat; if one is exposed, tell him to rotate it. Keep credentials in `.env` (gitignored) and GitHub Actions secrets only.

---

## 6. Technical architecture

- **Stack:** Python 3.13.x; `pandas`, `SQLAlchemy` + `psycopg2`, `python-dotenv`, `requests`, `beautifulsoup4`, `matplotlib`, `seaborn`. Virtualenv `venv`. Jupyter for analysis.
- **Database — MIGRATED TO CLOUD on Day 11.** Source of truth is now **Neon** (managed serverless **PostgreSQL 18**, US-West, free tier — 0.5 GB, ample for ~185k rows). The full local DB was migrated via `pg_dump -Fc` → `pg_restore --no-owner --no-acl`. The **local PostgreSQL 18.3** copy still exists but is no longer the source of truth; the local code now points at Neon. Going forward, both the scheduled scraper (once built, §13) and Johann's analysis notebooks read/write Neon — so collection no longer depends on his laptop being awake.
- **Credentials:** `.env` (gitignored), `DB_USER / DB_PASSWORD / DB_HOST / DB_PORT / DB_NAME` now hold the **Neon** values (old local values are commented out in `.env`, not deleted, for easy revert). `psycopg2`/SQLAlchemy default `sslmode=prefer` connects to Neon over SSL fine. **[CONFIRM]** the Neon password was exposed in chat on Day 11 and should be **rotated** in the Neon console if not already done; update `.env` (and GitHub secrets) with the new one.
- **ETL scripts (`etl/`)** — discovered Day 11 that far more is built than the Day-10 handoff documented:
  - `load_hiring.py` (~861 lines) — main scraper/loader. Pulls open jobs from each company's ATS, normalizes to a common row shape, **idempotent** upserts into `hiring_signals`. Handles Workday's 2,000-result cap via **faceted fetching**. Has per-fetch retry logic. *Most technical file.*
  - `detect_ats.py` — ATS-detection helper.
  - `load_patents.py`, `download_patents.py`, `test_bulk_download.py` — patents ingest (PatentsView bulk download → `patents`).
  - `assignee_mapping.py`, `explore_assignees.py` — map raw patent assignee names → target tickers (this is why each patent row carries one `assignee_ticker`).
  - `load_financials.py`, `edgar_backfill.py` — financials from **SEC EDGAR** → `financials_quarterly`.
  - **[CONFIRM]** the loader that populated `stock_prices_daily` (13,805 rows) was **not** identified in `etl/` during the Day-11 inventory — locate it (or note how stocks were loaded) before relying on/refreshing that table.
- **Analysis (`analysis/`):** `01_hiring_snapshot.ipynb` (done), `02_hiring_geography.ipynb` (done). `03_hiring_category.ipynb` is the next core notebook.
- **CI:** `.github/workflows/derisk-scrape.yml` — a **throwaway de-risk test** built Day 11 (runs `load_hiring.py` on a GitHub runner against a disposable Postgres service container; `workflow_dispatch` only). It proved the scrape works from a GitHub datacenter IP. In Half 2 (§13) this becomes the real scheduled workflow (or is replaced by one). Install step uses `pip install psycopg2-binary requests beautifulsoup4 python-dotenv` (NOT `requirements.txt`, which is a Windows `pip freeze` and won't install on Linux — see §12). `timeout-minutes: 40` (scrape takes ~24 min).
- **Other files:** `sql/schema.sql`, `requirements.txt` (Windows-frozen — not Linux-portable), `.env.example`, `.gitignore`, `HANDOFF.md`, `README.md`, `interview_moments.md`. Note `sector.dump` (migration artifact) should be deleted/gitignored — not committed.

- **Schema (`sql/schema.sql`) — 6 tables; FOUR now populated (was "only hiring" on Day 10):**
  - `companies` — 12-ticker target universe: CDNS, SNPS, ANSS (EDA); NVDA, AMD, QCOM, AVGO, MRVL (Fabless); INTC, MU, TXN (IDM); TSM (Foundry). Cols: ticker, name, segment, hq_country.
  - `hiring_signals` — THE primary table. One row per (job_id, snapshot_date). Cols: job_id, ticker, snapshot_date, title, location (raw), posted_date, category (NULL on ingest — derived later), ats, job_url, captured_at.
  - `patents` — **POPULATED.** Cols: patent_id, assignee_ticker, grant_date, title, cpc_class, inventor_count. **One assignee per patent** (patent_id is unique). 
  - `financials_quarterly` — **POPULATED.** Cols: ticker, quarter, revenue, rd_spend, net_income, operating_margin.
  - `stock_prices_daily` — **POPULATED.** Cols: ticker, date, open, high, low, close, volume.
  - `job_postings` — **legacy/dead, empty (0 rows).** **[CLEANUP]** consider dropping.
  - **[CONFIRM]** `schema.sql` may itself be stale (it predates the patents/financials/stocks tables). The migration used `pg_dump` of the *live* DB, so Neon has the real schema regardless — but if `schema.sql` is ever re-applied, confirm it matches the live tables first.
- **Active vs seeded:** 12 tickers seeded; **9 active in the hiring pipeline** (AMD, AVGO, CDNS, INTC, MRVL, MU, NVDA, QCOM, TXN). SNPS disabled (TalentBrew needs HTML scraping); ANSS and TSM not scraped.
- **ATS → ticker → location-field map:**

  | ATS | Tickers | Raw location field |
  |-----|---------|--------------------|
  | Workday | NVDA, CDNS, MRVL, INTC, AVGO | `locationsText` (emits "N Locations" for multi-site roles!) |
  | Jibe | AMD | `full_location` |
  | Eightfold | QCOM, MU | `locations[0]` |
  | Oracle HCM | TXN | `PrimaryLocation` |
  | TalentBrew | SNPS (disabled) | scraped `<span class="job-location">` |

- **Key data-quality gotcha (hiring):** Workday returns a *count* ("2 Locations") instead of a place for multi-site postings (~12.9% of postings, all five Workday tickers) — bucketed "Multiple (unspecified)". Recovering them needs per-job Workday detail requests — logged future item.

---

## 7. Conventions

- **Notebook connection cell:** `os` + `pandas` + `create_engine` + `load_dotenv()`; engine string from env vars; a small sanity `SELECT` as output. **Use `load_dotenv(override=True)`** (or restart the kernel) when `.env` changed mid-session, or old values stick.
- **Charts:** seaborn `whitegrid`; `figsize` ~`(10,5)`–`(11,6)`; `steelblue` single-series bars; data labels via `ax.text`; `plt.tight_layout()`.
- **Observations cells:** markdown, bold lead-in per observation + prose, ending with an "open question to test next." Written by Johann via the guided-questions method (§5.8). Header: "Observations — <topic> (Day N)".
- **Commits:** notebooks committed **with outputs intact** (render on GitHub). `Restart & Run All` → Save before committing. Stage files **explicitly** (`git add <file>`), never `git add -A`. Keep `.env` and data dumps out of every commit (verify with `git check-ignore .env`).
- **Build-in-public:** notebooks render cleanly on public GitHub; milestones → weekly LinkedIn updates.

---

## 8. Data state (current — now in NEON)

All counts verified Day 11 against Neon (post-migration). Local DB holds the same data as a backup.

- `companies`: **12**
- `hiring_signals`: **110,621** rows across **~13–14 point-in-time snapshots** (snapshot_dates May 19 → Jun 13 2026, 9 active tickers).
  - **CRITICAL QUALITY ISSUE:** snapshots are **irregular and partial** — only **3–9 of 9 tickers** captured per run, with date gaps (e.g., nothing Jun 2–8). **Cause: the scrape is run manually and the laptop sleeps mid-run** (not a code bug — the scrape itself runs clean). 
  - **Implication:** time-series / snapshot-over-snapshot analysis is **NOT yet reliable** — comparing a 6-ticker day to a 9-ticker day produces fake swings. Trends work is gated on (a) automation (Half 2) and (b) a completeness guard so partial snapshots are excluded/never written. See §10 and §13.
- `patents`: **61,519** rows, 12 tickers, grant window **2021–2025**. One assignee per patent (so "patents with multiple assignees" is structurally 0 — a data-model fact, not a finding). Per-ticker: TSM 16,925 · QCOM 14,995 · INTC 10,880 · MU 8,816 · TXN 4,461 · NVDA 1,600 · AMD 1,381 · MRVL 1,071 · SNPS 537 · CDNS 371 · AVGO 350 · ANSS 132. (EDA firms patent far less than fabs/IDMs — sensible.)
- `financials_quarterly`: **215** rows, 12 tickers, ~5 yrs of quarterly revenue / R&D / net income / operating margin. **Two explainable gaps:** TSM sparse (7 quarters, from 2024 — it's a foreign filer, reports differently to the SEC); ANSS ends Q1 2025 (acquired by Synopsys, deal closed **Jul 17 2025** — verified).
- `stock_prices_daily`: **13,805** rows = **11 tickers × 1,255 trading days** (2021-05-14 → 2026-05-13). **No ANSS** (delisted post-acquisition). Clean and uniform; ~1 month stale (no auto-refresh).
- `job_postings`: **0** (dead table).

**Data-integrity note (a talking point):** the ANSS pattern — gone from stocks, financials tapering at Q1 2025 — independently reflects the real Synopsys acquisition. Good sanity check that the pipelines mirror reality.

(Prior geography findings from Day 10 still hold for the latest *complete* snapshot: ~87.1% resolved to a country, 12.9% "Multiple", 0.0% unknown; Asia 5,143 > North America 3,814 > Europe 434 > Middle East 401 > Latin America 276 > Oceania 8.)

---

## 9. Progress log & key findings

**Day 9 — `01_hiring_snapshot.ipynb` (footprint by ticker):**
- MU leads the open-jobs book (~3,024) ahead of NVDA (~2,654) — surprising given NVDA's profile; Johann attributed it to Micron's *fab expansion / staffing megaprojects* (did **not** specify US fabs — don't add that).
- Raw counts overstate large/diversified firms; per-headcount, NVDA's hiring *intensity* (~6.3%) exceeds MU's (~5.7%).
- AVGO anomaly: very large (~$1T mkt cap) but a notably *small* open-jobs book.
- Open question: is cross-ticker count driven by **geographic spread** or **role/sector breadth**?

**Day 10 — `02_hiring_geography.ipynb` — DONE & pushed:**
- Location normalizer: 462 distinct raw strings → country + region via a 3-pass classifier; 0.0% unknown; auditable.
- Findings (Johann's, pressure-tested): Asia > North America even for US-listed firms; MU most concentrated (74% Asia, HHI 0.608); NVDA Middle East outlier (~17%, Israel/Mellanox); AVGO most US-centric (68% NA); Intel most globally distributed. Verified NVDA/Israel and Micron/Asia via search.
- Also: scope tightened, README rewritten, handoff expanded.
- **Process notes:** Claude twice over-attributed Day 9 claims; both corrected. See §5.10.

**Day 11 — Consolidation audit + cloud migration (this session):**
- **Started from a patents curiosity** ("how many patents have multiple chip-company assignees?"). Found the answer is structurally **0** — `patents` stores one assignee per patent, so co-assignment can't be represented (data-model fact, not a finding). More importantly, this exposed that the **handoff was badly stale**: patents/financials/stocks pipelines are all **built and loaded**, contradicting the Day-10 doc. → Johann chose to **consolidate before building more**.
- **Full data inventory** (see §8): patents/financials/stocks are real and mostly solid, with explainable quirks (TSM foreign filer; ANSS Synopsys acquisition reflected in the data). **The one real problem: hiring snapshots are irregular + partial** because the scrape runs manually and the laptop sleeps mid-run — which would silently corrupt any trend analysis.
- **Decision:** automate the scrape **off the laptop** (a laptop is a bad host for an accumulating job). Chose **GitHub Actions + cloud Postgres (Neon)** over Windows Task Scheduler — more robust *and* a portfolio piece.
- **De-risk test (the main work):** before committing ~4 hrs to cloud setup, tested the one assumption that could kill it — would the ATS sites block a GitHub datacenter IP? Built a throwaway Action running the real scrape against a disposable Postgres. After debugging (ran locally by mistake first; then the Windows `requirements.txt` failed to install on Linux — fixed by installing only the 4 actual deps), it came back **GREEN: all 9 tickers, counts matching local.** Cloud plan confirmed viable.
- **Half 1 of cloud build — DONE:** provisioned Neon (PG18), migrated the full local DB via `pg_dump`/`pg_restore`, verified counts in Neon (companies 12, financials 215, stocks 13,805, patents 61,519, hiring 110,621 — hiring higher than the earlier 99,752 because a local scrape run added today's snapshot before the dump), and **repointed `.env` to Neon** (test reads 61,519 from Neon ✓).
- **Process / things to not repeat:** (1) the Day-10 handoff was trusted over the live repo and was wrong — always verify against the actual DB/repo. (2) Neon password was pasted in chat — rotate it (§6). (3) `requirements.txt` isn't Linux-portable.
- **Interview moments from Day 11 (add these to `interview_moments.md`):**
  1. **Caught a silent data-quality bug** — partial snapshots (3–9 of 9 tickers) would create fake trends; added a completeness gate before trusting any time-series. *(Signals data skepticism — the analyst differentiator.)*
  2. **De-risked before building** — 30-min spike to test the riskiest assumption (datacenter-IP blocking) before a 4-hr build. *(Engineering judgment / fail-fast.)*
  3. **Designed a cloud pipeline** — moved to managed cloud Postgres + scheduled job so data collects automatically; separated where data *lives* from what *runs the code*. *(Systems/data-engineering thinking.)*
  4. **Validated data against reality** — a company vanished from the stock feed and its financials stopped mid-2025, matching its acquisition exactly. *(Connecting data to real events.)*
  5. **Knew the data model's limits** — read a "0" as a schema limitation, not a finding. *(Modeling literacy, no over-claiming.)*
  6. **CI/CD hands-on** — built/debugged a GitHub Actions workflow (runners, service containers, secrets, OS-portability).

---

## 10. Roadmap & prioritization (target: core done ~July 1; trends as a mid-July v2)

Scope discipline still applies — don't silently re-expand (§5.13). Note that patents/financials/stocks, formerly "future," are now **built**, which makes a cross-signal analysis cheap.

**IN PROGRESS — finish first (Half 2 of the cloud build):**
- **Automate the scrape into Neon via GitHub Actions.** De-risk passed and Neon is live (Half 1 done). Remaining: see §13. This is the highest-leverage item — it makes hiring data accumulate reliably and is the **gate for trends**. Includes a **completeness guard** (only write/keep a snapshot when all 9 tickers succeed) so partial runs stop polluting the series.

**CORE (committed scope for the ~July-1 deliverable — none of these need data to accumulate):**
1. **Category mix analysis** (`03_hiring_category.ipynb`). Does role *type* vary by region/ticker (Asia → manufacturing/ops vs. US → design/R&D)? Tests the still-unproven "Asian jobs are production/manufacturing" claim. **`category` is NULL on ingest — needs a classifier; profile it first (§5.4).**
2. **Cross-signal analysis** (NEW — replaces trends for the July-1 milestone). Hiring × financials or × patents (e.g., hiring intensity vs. R&D spend). Uses data that's already loaded → no accumulation wait, and a stronger differentiator than a 2-week time-series.
3. **Dashboard (capstone).** Interactive, multi-insight, **Tableau Public** (verify current free/publishing terms when scoping). New skill — budget learning time. Likely the biggest time sink and the main risk to July 1.
4. **Lightweight AI insight layer.** ~20–40 line function: feed real analysis numbers to the Claude API → plain-English readout. Ties to GEO background. Keep it lightweight; do NOT embed live AI in Tableau.

**DEFERRED to mid-July v2 (calendar-blocked, not effort-blocked):**
- **Snapshot-over-snapshot trends** (`04_hiring_trends.ipynb`). Needs weeks of clean, complete snapshots from the automated pipeline. Ship as a "build-in-public" update once the data's ripe.

**FUTURE / optional:**
- Workday per-job location enrichment (recover the 12.9% "Multiple" bucket).
- Deeper patents/financials analysis beyond the one cross-signal cut.

---

## 11. Recruiting & prep (so the strategy survives to next session)

**Summer-2027 internship timing (recruiting runs earlier than people expect):**
- **Wave 1 (Jul–Oct 2026):** finance, Big Tech, top consulting. (Amazon/Databricks Jul–Aug; Google ~mid-Oct.)
- **Wave 2 (Nov 2026–Feb 2027):** most mid-size companies; peaks Dec–Feb — bulk of data/business-analyst roles.
- **Wave 3 (Mar–May 2027):** startups, nonprofits, government, smaller firms.
- **Rule:** apply within the first ~2 weeks of any posting (mostly rolling); set up LinkedIn/Handshake/career-page alerts starting July 2026. The "done by July" target is well-calibrated for being ready when Wave 1 opens.

**Setup tips (highest leverage first):**
1. **README is the most-read file** — keep it accurate, lead with what's built, add a chart screenshot. Now also worth a one-line architecture note (scraper → scheduled GitHub Action → cloud Postgres → analysis) — that's a strong signal.
2. **Quantify everything on the resume** ("scraped ~11k postings across 9 firms / 5 ATS platforms; normalized 460+ location formats to 100% coverage; automated daily collection via a scheduled cloud pipeline").
3. **Rehearse the Cadence → project story** (§3) in 30-sec and 2-min versions.
4. **Build in public:** weekly LinkedIn post, each with ONE concrete finding.
5. **Referrals beat cold applications** — Cadence / Marketing Association contacts, school alumni tool.

**Interview fundamentals (practice cold):**
- **SQL:** `GROUP BY` + aggregate, `INNER` vs `LEFT JOIN`, a CTE (`WITH`), and `GROUP BY ... HAVING` (used Day 11 for the co-assignment check). The **join muscle is the gap** — practice a `companies`↔`hiring_signals` join for hiring intensity. DataLemur / StrataScratch for reps.
- **Excel:** build a pivot (same operation as SQL GROUP BY / pandas crosstab).
- **Explain a chart in 3 layers:** what it shows → so what → now what.
- **STAR stories** (write 5–6): hard technical problem = the 5-ATS normalizer; found-an-insight = geography findings; *intellectual honesty* = caught partial-snapshot bug + the Day-9 over-attribution; *judgment* = the de-risk spike; teamwork = Cadence; initiative = built the pipeline solo. Keep `interview_moments.md` current (see §9 Day-11 list).

---

## 12. Open decisions / TODOs

- **[ACTION]** Rotate the Neon DB password (exposed in chat Day 11); update `.env` + GitHub secrets.
- **[ACTION]** Add the Neon connection as **GitHub Actions secrets** (Half 2 prerequisite — see §13).
- **[CONFIRM]** Locate the loader that populates `stock_prices_daily` (not found in `etl/` during Day-11 inventory).
- **[ACTION]** Fix `requirements.txt` so it's Linux-portable (regenerate with only real deps, not a Windows `pip freeze`), and/or keep a separate minimal CI install list.
- **[CLEANUP]** Drop the dead `job_postings` table. Delete `sector.dump` and ensure it's gitignored.
- **[DECIDE later]** Tableau vs Power BI — leaning Tableau Public; verify free/publishing terms at scoping.
- **[TRACK]** Keep the running "skills demonstrated" list (§4) and `interview_moments.md` current.
- Open analytical question: is cross-ticker hiring volume driven by geographic spread or role breadth? (Category analysis answers the role half.)

---

## 13. Next session — exact starting point (Half 2 of the cloud build)

Day 11 shipped: full data audit, cloud migration to Neon (Half 1), `.env` repointed, de-risk passed, this handoff. **Half 1 (provision + migrate + repoint) is done.** Begin Half 2:

1. **Read this handoff fully.** Then verify live state, not memory (§5.10): quick count check against Neon (companies/patents/hiring/etc.) to confirm the migration held.
2. **Rotate the Neon password** if not already done (§12), and grab the fresh connection string.
3. **Add GitHub Actions secrets** so the scheduled workflow can reach Neon: GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**. Add the 5 Neon values as separate secrets: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`.
4. **Turn `derisk-scrape.yml` into the real scheduled workflow** (or add a new `scrape.yml`):
   - Trigger: `schedule:` (cron, daily) + keep `workflow_dispatch` for manual runs. (Cron is UTC; pick a time, e.g. early-AM PT.)
   - Remove the throwaway Postgres service container; instead inject the **Neon** creds from secrets into the job `env`.
   - Keep `timeout-minutes: 40` and the minimal `pip install` (psycopg2-binary requests beautifulsoup4 python-dotenv).
   - **Add a completeness guard:** the run should only commit a snapshot if all 9 tickers succeeded (else skip writing / mark incomplete) — so partial runs never pollute the time-series. Decide whether to enforce this in `load_hiring.py` or as a workflow check; surface the call to Johann (§5.3).
   - Verify with a manual `workflow_dispatch` run that a clean snapshot lands in Neon.
5. **Then resume CORE analysis (§10):** start **category mix analysis** (`03_hiring_category.ipynb`) — profile the `category` field across ATSes first (§5.4), surface the classifier/normalization call (§5.3), build iteratively (§5.5–5.7), observations via guided questions + pressure-test (§5.8), teach as you go (§4, §5.9). Cross-signal analysis (hiring × financials/patents) is the other near-term core item and needs no accumulation wait.

Once the scheduled scrape is confirmed writing clean daily snapshots to Neon, the trends/v2 clock starts — note the date so the deferred `04_hiring_trends.ipynb` can be built once there's enough complete history (mid-July).