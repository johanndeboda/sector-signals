# Sector Signals — Project Handoff

**Last updated:** end of Day 12 (2026-06-17)
**Owner:** Johann
**Repo:** `sector-signals` — public: https://github.com/johanndeboda/sector-signals (local: `C:\Users\Johan\sector-signals`, Windows, PowerShell, venv, VS Code). README, this handoff, and the scheduled scrape workflow are committed and current as of Day 12.

> This document is the single source of truth between work sessions. It is updated at the end of each working day. The next session must read it **in full** before doing anything. Items marked **[CONFIRM]** couldn't be verified from memory — check against the repo before relying on them.

---

## 0. How to use this handoff

**Next Claude session — start here:**
1. Read this whole file first. Do not start coding until you have.
2. Go to §13 (Next session — exact starting point) and begin there. §10 has the full roadmap.
3. Before writing code on any judgment call (where a file goes, which normalization approach, scope trade-offs), **ask Johann first** with a clear recommendation.
4. Follow §5 (How Claude should work) exactly — the working dynamic matters as much as the code.

**How to WRITE the next handoff (do it this same way every time — Johann's explicit instruction):**
- At end of each working day, when Johann says "update the handoff" (or "wrap the day"), rewrite this file so the next session lands *exactly* where this one left off — including how to respond and operate, not just what was done.
- **Update:** §6 (architecture, when it changes), §8 (data state), §9 (progress log — append the new day), §10 (roadmap — re-prioritize, mark done), §12 (open items), §13 (next-session start).
- **Preserve and keep current:** §1 (project), §2 (profile), §3 (interview story), §4 (learning goals), §5 (working style), §7 (conventions), §11 (recruiting & prep).
- **Rules:** Be comprehensive — do not trim for length; missing context is worse than a long doc. Keep `[CONFIRM]` markers honest (don't assert what you didn't verify). Never fabricate or over-sharpen prior findings (see §5.10). Record any mistakes made so they aren't repeated. Keep the section structure identical session to session.
- Johann replaces the repo's `HANDOFF.md` with the new version and commits it. **Never put secrets (DB passwords, connection strings with credentials) in this file or any committed file.**

---

## 1. What this project is

A data pipeline + analysis project that scrapes and analyzes signals across major US-listed **semiconductor companies** to infer where the industry is investing — by company, geography, and role type. Core method thesis: public job postings are a free, structured, leading signal of corporate intent (expansion, geographic strategy, R&D focus) that you can scrape, normalize, store, and analyze.

**Substantive thesis (added Day 12, framed in the README as the guiding question — not yet a finding):** how is AI — and its rapid, ongoing advancement — reshaping the semiconductor industry, in terms of *who they hire*, *how they patent*, and *how they perform financially*? The angle grew out of Johann's Cadence consulting work (Cadence is heavily AI-positioned in EDA) and ties his domain background to a timely, interviewer-compelling question. **Where AI is detectable in the existing data:** (a) **hiring** — AI/ML job titles, the cleanest/most direct signal; (b) **patents** — CPC class **G06N** plus a few others (G06F18, G06V, G10L15, G06F40) and title keywords, with a known caveat that a pure-G06N filter *undercounts* because AI-as-method patents (e.g., AI-accelerator hardware for chipmakers) are often filed under hardware classes; (c) **financials** — timing/correlation only (post-2022 AI surge, NVDA the obvious case) — **must be framed as correlation, never "AI caused X"** (ties to §5.10). The AI signal in this dataset will come mostly from NVDA / fabless / IDM names; the EDA firms (where Cadence sits) patent far less and aren't all in the hiring feed — so Cadence is the *origin of the question*, NVDA is where the data speaks loudest.

The data model is **architected for multiple signals**, and three secondary signals are built and loaded (patents, financials, stock prices) in addition to the primary hiring signal. The **hiring signal is the spine** of the analysis and the most developed. The committed core (see §10) is "hiring done well + dashboard + a light AI layer," with a **cross-signal angle** available because the other data is already in the warehouse.

It is a **portfolio project** to land Johann a data/analyst **internship**. Every output is built to be (a) verifiable, (b) a differentiator, (c) something he can explain in an interview, and (d) a vehicle for genuinely learning the technical skills involved.

---

## 2. Candidate profile, qualifications & goals

**Background**
- 2nd-year **MIS** major, SJSU (projected grad 2028). Bay Area. Windows / PowerShell / VS Code / Python venv.

**Technical skills — honest self-assessment (update as he grows):**
- **Python:** scripts, pandas, basic data cleaning → intermediate (groupby/crosstab/normalization).
- **SQL:** basic `SELECT`/`WHERE`/`JOIN` → CTEs, aggregation, `STRING_AGG`, `GROUP BY ... HAVING`.
- **Excel:** pivots, VLOOKUP/XLOOKUP, formulas.
- **Built live during this project:** PostgreSQL, SQLAlchemy, regex normalization, matplotlib/seaborn, git workflow, GitHub Actions / CI, cloud Postgres (Neon), `pg_dump`/`pg_restore` migration, secrets management. **New as of Day 12:** debugging serverless DB connection lifecycle (idle drops), idempotent all-or-nothing writes / completeness guards, converting a one-off CI test into a scheduled production workflow, reading/writing YAML workflow files.
- **Still ahead:** Tableau (dashboard), the lightweight Claude-API insight layer; the AI-signal analyses (hiring + patents).

**Prior experience — Cadence Design Systems consulting (via SJSU Marketing Association).** Student consulting for Cadence (a major EDA / semiconductor-design-software firm): analyzed Cadence's industry and competitors; ran an external touchpoint audit and student-perception survey; built improvement **prototypes for social media, the early-careers website, job listings, and a benefits page**; ran a **Generative Engine Optimization (GEO)** analysis. Weekly presentations. **Takeaway: real semiconductor/EDA domain knowledge + consulting "turn analysis into deliverables" experience.** Directly seeds the AI thesis (§1, §3) and the planned AI layer (§10).

**Goals**
- **Primary target roles:** Business/Data Analyst, Business Intelligence, Data Analyst (open to consulting, product, strategy). California preferred, open to relocation.
- **Recruiting:** rising junior, targeting **Summer 2027** internships. Wave 1 (Jul–Oct 2026) opens soon — see §11.
- **Timeline:** project **effectively done by the start of July 2026** (summer school compresses time). Achievable for the snapshot-based core; the time-series/trends piece is a mid-July "v2" because it needs weeks of accumulated data — and that data is now accumulating automatically (see §10/§13).
- **Time commitment:** ~10–20 hrs/week, likely shrinking. Favor work that compounds passively (the cloud automation, now done, is exactly this).
- **Builds in public:** weekly LinkedIn updates, public GitHub.

**What Johann is optimizing for (let this shape every build decision):**
1. **Measurable impact and results**, not just "I used X tool."
2. A **clear differentiator** vs. other 2nd-year MIS candidates.
3. A **coherent interview story that builds on the Cadence experience** (§3).
4. **Technical depth that signals "ready for an analyst internship."**
5. **Genuinely understanding everything he builds** (§4) — non-negotiable.

---

## 3. The interview story / why this project (the differentiator)

The narrative spine — reinforce it in outputs; Johann should tell it this way:

> At Cadence (consulting), I worked on the *demand side* of semiconductor hiring — auditing and prototyping improvements to one company's job listings, early-careers site, and employer presence, including a GEO analysis. That made me ask: what does hiring activity across the *whole* semiconductor sector reveal about where the industry is actually investing — and, given how AI-positioned Cadence is, how is AI specifically reshaping who these firms hire, what they patent, and how they perform? So I built a data pipeline to find out — scraping job postings from nine chip companies across five different ATS platforms, normalizing the mess, and analyzing it by company, geography, and role — then automated it as a scheduled cloud pipeline so the data collects itself.

Why it's strong: connects **domain knowledge** (EDA/semis) + **consulting deliverables** + **new technical depth** into one thread, on the *same industry and the same artifact* (job listings) he already worked on, now with a timely AI lens. His GEO experience ties directly to the planned AI layer (§10). Few 2nd-years have this through-line — lean on it.

---

## 4. Learning goals — Johann must UNDERSTAND, not just receive

Johann has stated this is a priority: he's uneasy building things he can't fully explain, and breaks down the code one script at a time (second-wave pass with ChatGPT). Treat the project as a skill-building curriculum, not just a deliverable.

- **Claude does code walkthroughs as part of building** — when introducing or touching code, explain *what it does and why*, in plain language at his level, concisely.
- Offer to have Johann **explain code back** to check understanding when it matters.
- Reassurance that's true: **the hardest code is already done.** `load_hiring.py` (five ATS integrations, faceted Workday workaround, idempotent upserts, and now cloud-resilient connection handling + completeness guard) is the most technical piece. The patents/financials pipelines are also built (Johann confirmed he can explain them). Remaining core work (category analysis, cross-signal, dashboard, light AI) is equal or lower complexity.

Skill ladder this project develops (track for the resume "skills demonstrated" list):
- Python/pandas: basic → intermediate (groupby, crosstab, apply, normalization, reshaping).
- SQL/PostgreSQL: basic SELECT → CTEs, `FILTER`, `STRING_AGG`, `GROUP BY ... HAVING`, aggregation, joins, window functions.
- Data cleaning/normalization: regex, accent-folding, lexicon/override design, assignee-name → ticker mapping.
- Analysis concepts: concentration metrics (HHI), region/role mix, time-series deltas, **interpretation discipline (claims must not outrun the data)**.
- Viz/BI: matplotlib/seaborn → Tableau (new).
- **Engineering practices: idempotent ETL, git hygiene, secrets/env management, CI/CD (GitHub Actions), cloud database (Neon), DB migration, serverless connection handling, scheduled workflows + completeness guards.**
- AI/API: the lightweight Claude-API "insight narrator" (ties to GEO background).
- Verification & communication: sourcing claims, building-in-public write-ups.

---

## 5. How Claude should work on this — REPLICATE THIS DYNAMIC

The working style that's been effective. Match it.

1. **Concise & direct.** Lead with the answer/next action. Minimal fluff, minimal formatting on simple replies. Short caveats.
2. **Verify current info via search** when uncertain, especially anything going into the portfolio (headcounts, market facts, "why" attributions, tool terms, CI specifics). Day 12 examples: verified the AI patent CPC classes (G06N et al.) and the GitHub Actions Node-20 deprecation + current action versions before relying on them.
3. **Ask clarifying questions before big recommendations / architecture decisions.** Surface the call with a recommendation; let Johann decide. He defers to Claude's judgment but wants to understand the reasoning.
4. **Profile before you build.** Never commit to an approach blind — look at the actual data first.
5. **Build iteratively and verifiably.** No large blind notebooks. Hand cells/changes in stages; Johann runs them and pastes output; refine from real results.
6. **Claude can't run the code.** No DB/network in chat. Claude writes cells/commands, Johann runs + pastes, Claude iterates. Plan around this loop.
7. **Don't hand fresh `.ipynb` files that would wipe local outputs.** Give *cells to paste*, not replacement files. Throwaway exploration cells are fine.
8. **Observations & analysis = GUIDED QUESTIONS, then PRESSURE-TEST.** For interpretive writing: Claude gives the numbers + pointer to the cell + plain-language questions; **Johann writes the observation in his own words**; then Claude pressure-tests (flags claims that outrun evidence, logic errors, unsupported attributions) **without rewriting his prose**. Methodology boilerplate is fine for Claude to draft; *interpretation* is his. (Same applies to README framing — Day 12, Claude flagged an "all workflows and operations" over-claim in the thesis paragraph and left the wording to Johann.)
9. **Teach as you go (§4).** Explain each technique and why — briefly. Do code walkthroughs when introducing something new (Day 12: walked through the connection lifecycle, the completeness guard, and what YAML/GitHub Actions are).
10. **DO NOT fabricate or over-sharpen prior findings, or assume undocumented state.** Reference only what's *actually* in the repo/DB. Never assert a finding that needs data not yet built. When a claim needs data Johann doesn't have, say so. Verify against the live repo/DB, not memory — the handoff has been found stale before.
11. **Match existing conventions** (§7) so new code reads like the same author.
12. **Reinforce the interview story (§3) and build-in-public goal** — when a milestone lands, flag it as a LinkedIn-able moment and capture it in `interview_moments.md`.
13. **Protect scope (§10).** Don't quietly re-expand scope; if something tempts scope creep, name the trade-off and let him decide.
14. **Security:** never have Johann paste secrets (DB passwords, full connection strings) into chat; if one is exposed, tell him to rotate it. Keep credentials in `.env` (gitignored) and GitHub Actions secrets only.

---

## 6. Technical architecture

- **Stack:** Python 3.13.x; `pandas`, `psycopg2` (+ `SQLAlchemy` in notebooks), `python-dotenv`, `requests`, `beautifulsoup4`, `matplotlib`, `seaborn`. Virtualenv `venv`. Jupyter for analysis.
- **Database — cloud (Neon).** Source of truth is **Neon** (managed serverless **PostgreSQL 18**, US-West, free tier). Migrated from local PG18 on Day 11 via `pg_dump -Fc` → `pg_restore`. The local copy still exists as a backup but is not the source of truth. Both the scheduled scraper and Johann's analysis notebooks read/write Neon.
- **Credentials:** `.env` (gitignored) holds the active **Neon** values; the old local values are commented out in the same file (`DB_HOST=localhost` distinguishes them). `psycopg2` default `sslmode=prefer` connects to Neon over SSL fine. **The same 5 values are stored as GitHub Actions repository secrets** (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`) for the scheduled workflow (added Day 12). **[CONFIRM]** whether the Neon password was rotated this session (it was exposed in chat Day 11; rotation was recommended — verify `.env` + the `DB_PASSWORD` secret match the current password).
- **ETL scripts (`etl/`):**
  - `load_hiring.py` — main scraper/loader (5 ATS integrations; Workday faceted fetch for the 2,000 cap; per-request retry). **Day 12 changes:** (1) a `connect()` helper, (2) `main()` restructured to **scrape all tickers first, then write once at the end** — the DB connection is only open for the single final insert, so it never sits idle during scraping (this fixed Neon dropping the idle connection mid-run and cascading failures to later tickers), and (3) a **completeness guard** — tracks `expected` (the 9 enabled tickers) vs `succeeded`; if any are missing it prints `INCOMPLETE`, **writes nothing, and `sys.exit(1)`** so a partial run can never pollute the series and the failure is visible. *Most technical file; now cloud-hardened.*
  - `detect_ats.py` — ATS-detection helper.
  - `load_patents.py`, `download_patents.py`, `test_bulk_download.py` — patents ingest (PatentsView bulk download → `patents`).
  - `assignee_mapping.py`, `explore_assignees.py` — map raw patent assignee names → tickers.
  - `load_financials.py`, `edgar_backfill.py` — financials from SEC EDGAR → `financials_quarterly`.
  - **[CONFIRM]** the loader that populated `stock_prices_daily` was not identified in `etl/` during the Day-11 inventory — locate it before relying on/refreshing that table.
- **Analysis (`analysis/`):** `01_hiring_snapshot.ipynb` (done), `02_hiring_geography.ipynb` (done). `03_hiring_category.ipynb` is the next core notebook (§13).
- **CI / automation:** `.github/workflows/scrape.yml` — **the production scheduled scrape (Day 12).** Triggers: daily `schedule: cron "17 9 * * *"` (~09:17 UTC / ~2 AM PT) + `workflow_dispatch`. Runs on `ubuntu-latest`, `timeout-minutes: 40`, installs only `psycopg2-binary requests beautifulsoup4 python-dotenv`, injects the 5 Neon secrets as job `env:`, runs `python etl/load_hiring.py`. No commit/coverage step — data persists to Neon, and the script's own log + the guard's exit code are the coverage signal. **Replaces the old `derisk-scrape.yml`** (the throwaway de-risk test, now deleted). **[ACTION]** action versions: `actions/checkout` and `actions/setup-python` should be `@v6` (Node-24-native); if still on `@v4`/`@v5` they emit a harmless Node-20 deprecation warning — bump to silence it and future-proof (Node 20 removed from runners fall 2026).
- **Other files:** `sql/schema.sql`, `requirements.txt` (Windows-frozen — **not Linux-portable**; the workflow uses an explicit install list instead, so this is low-priority now but still worth fixing), `.env.example`, `.gitignore`, `HANDOFF.md`, `README.md`, `interview_moments.md`.

- **Schema (`sql/schema.sql`) — 6 tables; FOUR populated:**
  - `companies` — 12-ticker universe: CDNS, SNPS, ANSS (EDA); NVDA, AMD, QCOM, AVGO, MRVL (Fabless); INTC, MU, TXN (IDM); TSM (Foundry). Cols: ticker, name, segment, hq_country.
  - `hiring_signals` — THE primary table. One row per (job_id, snapshot_date). Cols: job_id, ticker, snapshot_date, title, location (raw), posted_date, category, ats, job_url, captured_at.
  - `patents` — POPULATED. One assignee per patent (patent_id unique). Cols: patent_id, assignee_ticker, grant_date, title, `cpc_class` (key for the AI-patent cut — see §1/§10), inventor_count.
  - `financials_quarterly` — POPULATED. Cols: ticker, quarter, revenue, rd_spend, net_income, operating_margin.
  - `stock_prices_daily` — POPULATED. Cols: ticker, date, open, high, low, close, volume.
  - `job_postings` — legacy/dead, empty. **[CLEANUP]** consider dropping.
  - **[CONFIRM]** `schema.sql` may itself be stale (it predates the patents/financials/stocks tables); Neon has the real schema from the `pg_dump` migration, but confirm a match before ever re-applying it.
- **Active vs seeded:** 12 seeded; **9 active in the hiring pipeline** (AMD, AVGO, CDNS, INTC, MRVL, MU, NVDA, QCOM, TXN). SNPS disabled (TalentBrew anti-bot; needs Playwright); ANSS skipped (acquired by SNPS); TSM disabled (SSR + 403; needs Playwright).
- **ATS → ticker → location-field map:**

  | ATS | Tickers | Raw location field | `category` populated? |
  |-----|---------|--------------------|-----------------------|
  | Workday | NVDA, CDNS, MRVL, INTC, AVGO | `locationsText` ("N Locations" for multi-site) | **NVDA only** (faceted on `jobFamilyGroup`); CDNS/MRVL/INTC/AVGO = NULL |
  | Jibe | AMD | `full_location` | yes (`categories[0].name`) |
  | Eightfold | QCOM, MU | `locations[0]` | yes (`department`) |
  | Oracle HCM | TXN | `PrimaryLocation` | **NULL** (not per-job) |
  | TalentBrew | SNPS (disabled) | scraped `<span class="job-location">` | yes (when enabled) |

- **Key data-quality gotchas (hiring):** (1) Workday returns a *count* ("2 Locations") for multi-site postings (~12.9%, all five Workday tickers) — bucketed "Multiple (unspecified)". (2) **`category` coverage is MIXED** (see table) — populated for **NVDA, AMD, QCOM, MU**; **NULL for CDNS, MRVL, INTC, AVGO, TXN**. This directly shapes the category-mix analysis (§13): profile coverage first; a naive cross-ticker category comparison will be biased by the 5 NULL tickers.

---

## 7. Conventions

- **Notebook connection cell:** `os` + `pandas` + `create_engine` + `load_dotenv()`; engine string from env vars; a small sanity `SELECT`. **Use `load_dotenv(override=True)`** (or restart the kernel) when `.env` changed mid-session.
- **Charts:** seaborn `whitegrid`; `figsize` ~`(10,5)`–`(11,6)`; `steelblue` single-series bars; data labels via `ax.text`; `plt.tight_layout()`.
- **Observations cells:** markdown, bold lead-in per observation + prose, ending with an "open question to test next." Written by Johann via the guided-questions method (§5.8). Header: "Observations — <topic> (Day N)".
- **Commits:** notebooks committed **with outputs intact** (render on GitHub). `Restart & Run All` → Save before committing. Stage files **explicitly** (`git add <file>`), never `git add -A`. Keep `.env` and data dumps out of every commit (verify with `git check-ignore .env`). Day-12 pattern: group changes into clean, logically-separate commits (e.g., script hardening / workflow / README were three commits).
- **psql vs PowerShell:** label SQL commands explicitly as psql vs PowerShell. Full psql path on Windows: `& "C:\Program Files\PostgreSQL\18\bin\psql.exe"`.
- **Build-in-public:** notebooks render cleanly on public GitHub; milestones → weekly LinkedIn updates.

---

## 8. Data state (current — in NEON)

- `companies`: **12**
- `hiring_signals`: **[CONFIRM exact total]** — was 110,621 at end of Day 11; grew Day 12 with new snapshots (a 9/9 local run ~10,969 rows, plus the GitHub test run ~11,041 rows that was mostly `ON CONFLICT` no-ops against the same-day local run). **Run a count to confirm the current total before quoting it anywhere.**
  - **Snapshot quality — important for trends:** historical snapshots remain **irregular/partial** (manual, pre-automation), and at least one recent **6/9 partial** snapshot exists from the run that exposed the connection bug. The **completeness guard only protects snapshots written from Day 12 onward.** So: the **guaranteed-clean 9-ticker series starts 2026-06-17**; any trends/time-series work must either start from that date or explicitly filter to complete (9-ticker) snapshots and discard pre-automation partials.
- `patents`: **61,519** rows, 12 tickers, grant window **2021–2025**. One assignee per patent. Per-ticker: TSM 16,925 · QCOM 14,995 · INTC 10,880 · MU 8,816 · TXN 4,461 · NVDA 1,600 · AMD 1,381 · MRVL 1,071 · SNPS 537 · CDNS 371 · AVGO 350 · ANSS 132 (EDA firms patent far less than fabs/IDMs — sensible). `cpc_class` present → enables the AI-patent cut (§1). PatentsView **bulk download** (lagged source); a rerun wouldn't add 2026 grants without a config change — refresh deliberately only if/when patents freshness matters.
- `financials_quarterly`: **215** rows, 12 tickers, ~5 yrs quarterly. TSM sparse (foreign filer); ANSS ends Q1 2025 (Synopsys acquisition closed Jul 17 2025 — verified).
- `stock_prices_daily`: **13,805** rows = 11 tickers × 1,255 trading days (2021-05-14 → 2026-05-13). No ANSS (delisted). ~1 month stale.
- `job_postings`: **0** (dead table).

(Prior Day-10 geography findings still hold for the latest *complete* snapshot: ~87.1% resolved to a country, 12.9% "Multiple", 0.0% unknown; Asia 5,143 > North America 3,814 > Europe 434 > Middle East 401 > Latin America 276 > Oceania 8.)

---

## 9. Progress log & key findings

**Day 9 — `01_hiring_snapshot.ipynb`:** MU leads open jobs (~3,024) ahead of NVDA (~2,654) — Johann attributed it to Micron's fab expansion / staffing megaprojects (**did NOT specify US fabs — don't add that**); per-headcount NVDA hiring *intensity* (~6.3%) exceeds MU's (~5.7%). AVGO anomaly (huge mkt cap, small jobs book). Open question: is cross-ticker count driven by geographic spread or role/sector breadth?

**Day 10 — `02_hiring_geography.ipynb` — DONE:** 462 raw location strings → country/region via 3-pass classifier, 0.0% unknown. Findings (pressure-tested): Asia > NA even for US-listed firms; MU most concentrated (74% Asia, HHI 0.608); NVDA Middle East outlier (~17%, Israel/Mellanox); AVGO most US-centric; Intel most globally distributed. Verified key claims via search. **Process note:** Claude twice over-attributed Day-9 claims during this work; both corrected (§5.10).

**Day 11 — Consolidation audit + cloud migration:** discovered patents/financials/stocks pipelines all built (handoff was stale); full data inventory; identified the real problem — hiring snapshots irregular/partial because the manual scrape's laptop sleeps mid-run. De-risked the datacenter-IP question (GREEN, 9/9). Provisioned Neon (PG18), migrated the DB, repointed `.env`. Process lesson: trust the live repo/DB over the handoff.
  - **Interview moments from Day 11 (add to `interview_moments.md` if not already there):** (1) **caught a silent data-quality bug** — partial snapshots (3–9 of 9 tickers) would create fake trends; added a completeness gate; (2) **de-risked before building** — a short spike to test the riskiest assumption (datacenter-IP blocking) before a ~4-hr build; (3) **designed a cloud pipeline** — managed cloud Postgres + scheduled job, separating where data *lives* from what *runs the code*; (4) **validated data against reality** — a company vanished from the stock feed and its financials stopped mid-2025, matching its acquisition exactly; (5) **knew the data model's limits** — read a structural "0" as a schema limitation, not a finding; (6) **CI/CD hands-on** — built/debugged a GitHub Actions workflow (runners, service containers, secrets, OS-portability).

**Day 12 — Half 2 of the cloud build: scrape fully automated (spanned two sittings; 2026-06-17):**
- **Connection bug found & fixed.** A manual run came back **6/9** (MU/AMD/TXN failed). Diagnosed from the logs as a **DB-connection drop, not anti-bot**: AMD/TXN had *fetched* their data fine and only failed on the *write*; MU's fatal error was `SSL connection has been closed unexpectedly`. Root cause: `load_hiring.py` opened **one psycopg2 connection at the top of `main()`** and held it across the whole ~25-min run; Neon's serverless compute dropped the idle connection during a slow ticker, then every later ticker failed with `connection already closed`. Local Postgres had masked this (never drops idle connections). **Fix (chosen over a minimal per-ticker reconnect):** restructured to **scrape all → write once at the end** (connection only open for the final insert) + added a `connect()` helper. Verified with a clean **9/9 local run (10,969 rows)**.
- **Completeness guard added** to `load_hiring.py`: `expected` vs `succeeded`; partial → no write + `sys.exit(1)` (requires `import sys`). Code-reviewed and confirmed correct.
- **GitHub secrets configured** (5 Neon values). **Workflow built:** `derisk-scrape.yml` → `scrape.yml` (daily cron + `workflow_dispatch`, Neon creds from secrets, throwaway Postgres removed).
- **Test run PASSED on GitHub against Neon:** 9/9 tickers, 11,041 rows, ~14 min, guard reported `9/9` — proving the full cloud path (Action → secrets → Neon) end-to-end. **The trends clock starts 2026-06-17.**
- **AI thesis added to the README** as the guiding question (not findings). Committed in 3 clean commits + pushed.
- **Process / things to not repeat:** Claude initially suggested `pool_pre_ping` (a SQLAlchemy feature) before seeing that the loader uses raw psycopg2 — corrected once the code was read. (Reinforces §5.2/§5.10: read the actual code before prescribing.) Also: a Node-20 deprecation warning in the Action is harmless; the real fix is bumping action versions to `@v6` (§6, §12).
- **Interview moments to add to `interview_moments.md`:**
  1. **Cloud migration surfaced a connection-resilience bug the local DB had hidden** — diagnosed a mid-run failure as an idle-connection drop (not anti-bot), fixed by writing once at the end, and added an all-or-nothing completeness guard so partial runs can't pollute the time-series. *(Debugging + systems thinking + data integrity — the analyst differentiator.)*
  2. **Shipped a self-running cloud pipeline** — turned a one-off CI test into a scheduled GitHub Action writing complete daily snapshots to managed Postgres, with zero ongoing effort. *(Initiative / data-engineering.)*

---

## 10. Roadmap & prioritization (target: core done ~July 1; trends as a mid-July v2)

Scope discipline still applies — don't silently re-expand (§5.13).

**DONE (Day 12):**
- ~~Automate the scrape into Neon via GitHub Actions, with a completeness guard.~~ ✅ Live and tested. Data now accumulates automatically; **the trends clock started 2026-06-17.**

**CORE (committed scope for the ~July-1 deliverable — none of these need data to accumulate):**
1. **Category mix analysis** (`03_hiring_category.ipynb`) — **NEXT (see §13).** Does role *type* vary by region/ticker? **Profile `category` coverage first** — it's populated for NVDA/AMD/QCOM/MU but NULL for CDNS/MRVL/INTC/AVGO/TXN (§6), so a classifier/normalization or a coverage-aware approach is needed. **AI lens:** add an "AI/ML roles" cut (titles + categories) per the thesis (§1).
2. **Cross-signal analysis** — hiring × patents or × financials. **Pivot decision (Day 12, lean toward AI angle):** prefer **AI-role hiring × AI-class patents by firm** over a generic hiring-vs-R&D cut — more coherent with the thesis, same effort. Uses already-loaded data → no accumulation wait. **Patents stay bounded** to this one AI-flavored cut for now (don't expand into a standalone patents project pre-July). When built, decide the **AI-patent definition**: narrow (G06N) vs broader (G06N + other CPC + title keywords) — narrow undercounts (§1).
3. **Dashboard (capstone)** — interactive, multi-insight, **Tableau Public** (verify current free/publishing terms when scoping). New skill — budget learning time; main risk to July 1.
4. **Lightweight AI insight layer** — ~20–40 line function feeding real analysis numbers to the Claude API → plain-English readout. Ties to GEO background. Keep lightweight.

**DEFERRED to mid-July v2 (calendar-blocked, not effort-blocked):**
- **Snapshot-over-snapshot trends** (`04_hiring_trends.ipynb`). Now *unblocked and on the clock* — the automated pipeline writes complete 9/9 snapshots daily from 2026-06-17. Build once there's ~3–4 weeks of clean history. **Must use only complete (9-ticker) snapshots** (§8).

**FUTURE / optional:**
- Workday per-job location enrichment (recover the 12.9% "Multiple" bucket).
- Deeper patents/financials analysis beyond the one cross-signal cut.
- SNPS/TSM via Playwright (deferred until >2 gated sites justify it).

---

## 11. Recruiting & prep

**Summer-2027 internship timing:**
- **Wave 1 (Jul–Oct 2026):** finance, Big Tech, top consulting. Opens soon — set up LinkedIn/Handshake/career-page alerts starting July 2026.
- **Wave 2 (Nov 2026–Feb 2027):** most mid-size companies; peaks Dec–Feb — bulk of data/business-analyst roles.
- **Wave 3 (Mar–May 2027):** startups, nonprofits, government, smaller firms.
- **Rule:** apply within ~2 weeks of any posting (mostly rolling). The "done by July" target is well-calibrated for Wave 1.

**Setup tips (highest leverage first):**
1. **README is the most-read file** — keep it accurate, lead with what's built, add a chart screenshot. Now worth a one-line architecture note (scraper → **scheduled GitHub Action** → cloud Postgres → analysis) — strong signal.
2. **Quantify everything on the resume** ("scraped ~11k postings across 9 firms / 5 ATS platforms; normalized 460+ location formats to 100% coverage; **automated daily collection via a scheduled cloud pipeline with an all-or-nothing completeness guard**").
3. **Rehearse the Cadence → AI-thesis → project story** (§3) in 30-sec and 2-min versions.
4. **Build in public:** weekly LinkedIn post, each with ONE concrete finding — the "pipeline now runs itself" milestone is a clean post.
5. **Referrals beat cold applications** — Cadence / Marketing Association contacts, alumni tool.

**Interview fundamentals (practice cold):**
- **SQL:** `GROUP BY` + aggregate, `INNER` vs `LEFT JOIN`, a CTE (`WITH`), `GROUP BY ... HAVING`. **The join muscle is the gap** — practice a `companies`↔`hiring_signals` join for hiring intensity. DataLemur / StrataScratch.
- **Excel:** build a pivot (same op as SQL GROUP BY / pandas crosstab).
- **Explain a chart in 3 layers:** what it shows → so what → now what.
- **STAR stories** (write 5–6): hard technical problem = the 5-ATS normalizer **or the cloud connection-resilience fix**; found-an-insight = geography findings; *intellectual honesty* = caught the partial-snapshot bug + the Day-9 over-attribution; *judgment* = the de-risk spike; teamwork = Cadence; initiative = built + automated the pipeline solo. Keep `interview_moments.md` current.

---

## 12. Open decisions / TODOs

- **[ACTION]** Commit `interview_moments.md` (it was modified but left uncommitted Day 12) — add the two Day-12 moments (§9) and commit/push.
- **[ACTION]** Bump `actions/checkout` and `actions/setup-python` to `@v6` in `scrape.yml` to clear the Node-20 deprecation warning and future-proof (§6). 2-line edit; not urgent (Node 20 removed fall 2026).
- **[CONFIRM]** Was the Neon password rotated this session? (Exposed in chat Day 11.) Verify `.env` + the `DB_PASSWORD` secret hold the current password.
- **[CONFIRM]** Verify the **first automatic cron run** fires (check the Actions tab on/after the next ~09:17 UTC) and lands a clean 9/9 snapshot.
- **[CONFIRM]** Current `hiring_signals` row count (don't quote the old 110,621 — run a fresh count; §8).
- **[OPTIONAL]** README thesis paragraph — light grammar polish + soften the "AI within *all* workflows and operations" over-claim (Johann's wording to keep; §5.8).
- **[LOW-PRI]** `requirements.txt` not Linux-portable (workflow uses explicit install, so deprioritized). **[CLEANUP]** drop dead `job_postings` table; ensure no `sector.dump` committed.
- **[CONFIRM]** Locate the `stock_prices_daily` loader (§6).
- **[NOTEBOOK FIX]** The `WHERE snapshot_date = CURRENT_DATE` pattern returns empty when the scraper hasn't run that day — long-term fix is `MAX(snapshot_date)`.
- **[DECIDE later]** Tableau vs Power BI — leaning Tableau Public; verify free/publishing terms at scoping.
- Open analytical question: is cross-ticker hiring volume driven by geographic spread or role breadth? (Category analysis answers the role half.)

---

## 13. Next session — exact starting point

Day 12 shipped the full cloud automation (scheduled scrape → Neon, completeness-guarded, tested 9/9) + the AI thesis in the README. **The cloud build is DONE.** Begin the CORE analysis work:

1. **Read this handoff fully.** Verify live state, not memory (§5.10): a quick `hiring_signals` count + a check that the latest snapshot is complete (9 tickers).
2. **Quick housekeeping (cheap, do first):** commit `interview_moments.md` with the two Day-12 moments; bump the workflow actions to `@v6`; glance at the Actions tab to confirm the first scheduled cron run landed a clean 9/9 (§12).
3. **Start category mix analysis (`03_hiring_category.ipynb`).** First **profile the `category` field** across ATSes (§6) — confirm it's populated for NVDA/AMD/QCOM/MU and NULL for CDNS/MRVL/INTC/AVGO/TXN. Then **surface the call to Johann** (§5.3): how to handle the NULL tickers — derive a classifier from titles, restrict the analysis to the populated tickers, or normalize the heterogeneous category vocabularies into a common scheme. Build iteratively (§5.5–5.7); observations via guided questions + pressure-test (§5.8); teach as you go (§4). **Add the AI/ML-roles cut** per the thesis (§1, §10).
4. **Cross-signal (hiring × patents, AI-leaning)** is the other near-term core item and needs no accumulation wait — see §10 for the pivot decisions (lean AI; keep patents bounded; pick the AI-patent definition when building).

The trends/v2 clock started 2026-06-17 — once there's ~3–4 weeks of clean complete snapshots (≈ mid-July), `04_hiring_trends.ipynb` becomes buildable (complete-snapshots only).