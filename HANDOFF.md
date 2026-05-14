# Sector Signals — Handoff Document
**Last updated:** end of Week 1, Day 3 (Thursday, May 14, 2026)
**Project status:** On track. Plumbing week ~60% complete.

---

## 0. For next-session Claude: read this first

This document is the single source of truth for resuming the project. The candidate (Johan) will paste this at the start of the next session. Treat sections 1-3 as **non-negotiable context** — they shape *how* you respond, not just *what* you respond about.

**Key operating principle:** Johan drives interpretation, judgment, and business decisions. Claude drives plumbing, syntax, multi-step pipelines, and debugging. **Never write code Johan won't read.** When sending scripts, explicitly flag 2-3 sections worth focusing on; mark the rest as skim-only.

---

## 1. Candidate background (Johan)

- **Year/major:** 2nd-year MIS major (Management Information Systems)
- **Programming experience:** "Slight" — can follow code logic from structure, doesn't know every library detail. Has working comfort with Python at the level of "I can see what a script is doing even if I don't recognize every function call." **This is the realistic baseline — don't overestimate or underestimate.**
- **Setup:** Dell XPS 15, Windows 11, VSCode as primary editor, PowerShell terminal, Postgres 18 installed locally
- **Domain context:** Has done consulting work on Cadence (CDNS) — has real knowledge of the EDA/semiconductor industry landscape. Don't talk down on semi-industry concepts; he knows the players and the business models.
- **Career goal:** Job search starting late 2026 (Aug-Dec). Sector Signals is portfolio centerpiece. Target roles: analyst-track positions where defending a data project in a 45-min interview is the bar.

### Working style preferences (observed across this session)

- **Asks meta-questions about the work itself.** "Is this worth memorizing?" "Should I look through the code?" These signal he's actively calibrating his learning approach. Take them seriously — they're not stalling, they're optimizing.
- **Wants reasoning, not just answers.** When Johan asks "why?" he means it. Brief explanations with concrete tradeoffs land better than hedged both-sides answers.
- **Prefers being given a recommendation when uncertain.** Asks "what's your recommendation?" rather than "give me options." When he says he's not sure, give a clear pick with reasoning — don't fence-sit.
- **Asks for "very briefly" when he just wants the answer.** Honor the request — give the short version first, then add context only if it serves him.
- **Reads code at "shape and logic" level, not line-by-line.** This is the correct level for a 2nd-year MIS student. Don't push for more rigor than the task requires; trust that repetition across the project locks in patterns.
- **Will paste error messages or terminal output for debugging.** Read carefully — every line of a stack trace matters. Identify the root cause before suggesting fixes.
- **Honest about gaps.** Will say "not sure" or "explain again." When this happens, slow down — don't pile on more material until the prior thing clicks.

### Communication norms

- Plain prose works fine. Don't over-format with headers for simple replies.
- Markdown tables are good for tradeoff comparisons and decision matrices.
- Avoid emoji unless he uses them first.
- He's a good sport about mistakes (his or Claude's). Don't grovel over typos; acknowledge briefly and move on.
- Has a sense of humor but the project is serious work — match tone to context.

---

## 2. Project elevator pitch

**Sector Signals** is a Postgres-backed analytical project tracking 12 US-listed semiconductor companies (the "semi 12") across four data dimensions: financials, patents, hiring signals, and qualitative news. The deliverable is a defensible, well-instrumented analytical project that supports a job search in late 2026 — something Johan can defend in 45-minute case interviews.

**The "semi 12":** AMD, ANSS, AVGO, CDNS, INTC, MRVL, MU, NVDA, QCOM, SNPS, TSM, TXN.

**Time window:** patents and financials cover 2021-01-01 → present (5 years).

**Why these 12:** EDA (CDNS, SNPS, ANSS), GPU/AI (NVDA, AMD), wireless/IP-licensing (QCOM, AVGO, MRVL), CPU/IDM (INTC), memory (MU), analog/embedded (TXN), foundry (TSM). Covers the major business models in semis.

---

## 3. Working approach — non-negotiable principles

**Candidate drives on:** hypotheses, interpretation, business judgment, decisions about what to include/exclude, validation of outputs, picking which observations are interview-worthy.

**Claude drives on:** boilerplate code, SQL syntax, library quirks, multi-step pipelines, debugging plumbing.

### Code-reading discipline (very important)

Johan reads every script before running it. Not line-by-line — at "what is this trying to do?" level, 5-10 min per script. **When generating code:**
- Add docstrings explaining the script's job
- Use section comments to break up logic
- Inline-comment any non-obvious choice or judgment call
- At the end of the response, explicitly flag 2-3 sections worth focused reading + 1-2 patterns the candidate will see again
- Mark pure plumbing as "skim only" so he doesn't waste effort

### Decision-making pattern

When a choice involves judgment (e.g. which assignee variants to include, whether to include a deprecated ticker), do this:
1. State the tradeoff briefly
2. Recommend a default with reasoning
3. Use `ask_user_input_v0` for the actual decision — let Johan choose with eyes open
4. If he says "your recommendation" or "I'm not sure," then *commit* to a pick with reasoning. Don't kick it back.

### Interview-moment framing

When the project surfaces something analytically interesting (a surprising number, a methodology choice, an anomaly, a lesson learned), name it explicitly as "interview-worthy" and draft 1-2 sentences he could use. Examples that worked this session:
- *"NVIDIA has 10x fewer patents than Qualcomm despite 3x the market cap. Patent volume ≠ innovation value."*
- *"Marvell uses 14 distinct legal entity names — typical of pre-2018 semi-industry IP-holding structures."*
- *"Flagged AVGO patent count as anomalously low and added to a real investigation TODO."*

The `interview_moments.md` file in the repo accumulates these. Suggest entries when relevant.

---

## 4. Tech stack & environment

- **OS:** Windows 11 on Dell XPS 15
- **Editor:** VSCode (Python extension installed, venv auto-detected)
- **Terminal:** PowerShell (not WSL — decided against WSL on D3; revisit if it becomes painful)
- **DB:** Postgres 18, local, port 5432
  - Binary path: `C:\Program Files\PostgreSQL\18\bin\psql.exe`
  - PATH is **not yet configured** — needs full path to call `psql` from terminal (minor TODO)
- **Language:** Python 3.x in venv at project root
- **Key libraries:** pandas, psycopg2-binary, sqlalchemy, requests, python-dotenv, yfinance
- **DB connection:** loaded from `.env` via python-dotenv; `load_financials.py` uses SQLAlchemy, `load_patents.py` uses psycopg2 directly (different but both fine)

### Critical environment notes

- **DB password was rotated on D3 end-of-session.** Verified by re-running `load_financials.py` against the new credentials. Connection works.
- **Lesson Johan learned on D3:** never paste passwords into chats. Don't lecture about this in future sessions — he's internalized it. If a similar slip happens, briefly redirect, don't moralize.
- **`.gitignore` correctly excludes `data/` and `.env`.** Verified clean on D3.

---

## 5. Folder structure (as of D3)

```
sector-signals/
├── etl/
│   ├── load_financials.py        ← Day 1: yfinance → Postgres
│   ├── edgar_backfill.py         ← Day 2: SEC EDGAR XBRL → Postgres
│   ├── download_patents.py       ← Day 3 NEW: streaming downloads with resume support
│   ├── explore_assignees.py      ← Day 3 NEW: throwaway, can be deleted Week 2
│   ├── assignee_mapping.py       ← Day 3 NEW: 95 org-name variants → 12 tickers
│   └── load_patents.py           ← Day 3 NEW: 4-way TSV join → patents table
├── sql/
│   └── schema.sql                ← all CREATE TABLE DDL, run on Day 2
├── data/                         ← GITIGNORED, holds 4 patent TSVs (~1.7 GB)
├── venv/
├── .env                          ← DB credentials (gitignored)
├── .gitignore
├── requirements.txt
├── interview_moments.md          ← running log of analytical findings
└── HANDOFF.md                    ← this file
```

---

## 6. Database state (as of D3)

### Schema
- `companies (ticker, name, country, ...)` — 12 rows, all semi-12 tickers present
- `financials_quarterly (ticker, quarter, revenue, rd_spend, net_income, operating_margin)` — composite PK `(ticker, quarter)`
- `stock_prices_daily (ticker, trade_date, open, high, low, close, volume)` — composite PK `(ticker, trade_date)`
- `patents (patent_id PK, assignee_ticker FK→companies, grant_date, title, cpc_class, inventor_count)` — **61,519 rows**

### Per-ticker patent counts (sanity-check reference for future re-loads)

| Ticker | Count | Notes |
|---|---|---|
| TSM | 16,925 | Foundry, files heavily |
| QCOM | 14,995 | IP-licensing biz model |
| INTC | 10,880 | Old-school IDM |
| MU | 8,816 | Memory specialist |
| TXN | 4,461 | Analog/embedded |
| NVDA | 1,600 | Notably low — moat is design, not IP volume |
| AMD | 1,381 | Lean vs INTC |
| MRVL | 1,071 | 14 legal entity variants |
| SNPS | 537 | EDA tools |
| CDNS | 371 | EDA tools |
| **AVGO** | **350** | **🚩 ANOMALY — investigate Week 2** |
| ANSS | 132 | Got acquired by SNPS July 2025 |
| **Total** | **61,519** | |

---

## 7. What we built on Day 3 (full detail)

### The patents pipeline — four scripts working together

**1. `etl/download_patents.py`** — fetches 4 PatentsView bulk TSVs from S3:
- `g_patent.tsv.zip` (219 MB) — patent_id, title, grant_date
- `g_assignee_disambiguated.tsv.zip` (342 MB) — assignee org names
- `g_inventor_disambiguated.tsv.zip` (667 MB) — inventor records
- `g_cpc_current.tsv.zip` (472 MB) — CPC classifications

Key patterns: streaming download (chunked, flat memory), resume-on-failure via `.part` files + HTTP `Range` headers, idempotent (size-check skips completed files). Note: PatentsView migrated to `data.uspto.gov` on March 20, 2026 — legacy S3 URLs still work but may stop eventually.

**2. `etl/explore_assignees.py`** — exploration tool, not production. Reads 8.6M assignee rows, runs substring search per ticker, prints top 15 variants with patent counts. Johan eyeballs output to identify real variants vs false positives. **Throwaway script** — can be deleted in Week 2.

**3. `etl/assignee_mapping.py`** — curated exact-match mapping of 95 organization-name variants to 12 tickers, with documented judgment calls (see §8). Self-checks for duplicates when run directly.

**4. `etl/load_patents.py`** — joins 4 TSVs, filters to 2021+ and our 12 companies, inserts into Postgres:
- Step 1: assignee join → 252,082 unique patents mapped to tickers (108 co-assignee duplicates dropped)
- Step 2: patent metadata join + date filter (grant_date ≥ 2021-01-01) → 61,519 patents
- Step 3: CPC classification join (primary class, cpc_sequence=0) → 259 patents have no primary CPC (NULL is fine)
- Step 4: inventor groupby + nunique for inventor_count
- Step 5: psycopg2 `execute_values` batched insert with `ON CONFLICT DO NOTHING`
- Runtime: ~22 min total on Johan's machine (inventor groupby is slowest step — predicted 3-5 min, was wrong)

### Patterns Johan saw repeatedly today (worth reinforcing in future sessions)

- **Substring for exploration, exact-match for production.** Loose discovery, strict production.
- **Filter early, join late.** Date filter on `g_patent` reduced 9.4M rows → 1.7M before joining to ticker set.
- **Idempotency via `ON CONFLICT DO NOTHING`.** Same pattern as `load_financials.py`.
- **`nunique` vs `count`.** Distinct entities vs total rows — silent bug source.
- **`usecols` on `pd.read_csv`.** Don't load columns you don't need.
- **Streaming downloads.** Flat memory regardless of file size.
- **`.part` files + atomic rename.** Same pattern as database commit.

---

## 8. Judgment calls made on Day 3 (must defend in interviews)

1. **AVGO includes pre-2016 Avago Technologies entities.** Avago acquired Broadcom in 2016, kept Broadcom name, kept AVGO ticker. Avago's Singapore-based IP holding subsidiaries continued filing patents under "Avago Technologies" names for years post-merger. Including them captures full legal continuity under AVGO. Date filter handles time-window aspect downstream.

2. **INTC excludes loose "intel" substring matches.** Substring search caught 16,000+ false positives (AT&T Intellectual Property, Panasonic Intellectual Property, etc.). Production mapping uses exact names: Intel Corporation, Intel IP Corporation, Intel Mobile Communications GmbH only.

3. **ANSS is kept in the schema despite July 2025 Synopsys acquisition.** Treated as analytical case study — "company that disappeared mid-window" is interesting, not a reason to exclude.

4. **MRVL lumps all 14 legal entities (Bermuda, Singapore, Israel, US subsidiaries) as one bucket.** Typical pre-2018 semi-industry IP-holding structure for tax optimization. Splitting them would obscure the operating-company view.

5. **MU includes typo "Micron Technology, lnc."** (lowercase L instead of capital I). Data-entry error in PatentsView's source feed; real Micron patents miscategorized. Including catches them.

6. **TSM includes garbled string "TAIWAN SEMICONDUCTOR MTAIWANANUFACTURING CO., LTD."** Same reasoning as Micron — feed corruption, real TSMC filing.

7. **Co-assignee deduplication.** Patents with multiple assignees among our 12 tickers — 108 such cases — get one ticker arbitrarily (deterministic via sort). Acknowledged in code comments. Possible Week 3 sidebar on cross-company collaboration.

8. **Inner join for patent metadata (drops patents with missing grant_date).** Acceptable data-quality decision: don't insert rows without a date. Left join for CPC (some patents have no primary class — NULL is fine).

---

## 9. Open questions / TODO

| Item | Status | Notes |
|---|---|---|
| **AVGO patent count anomaly** | 🚩 NEW from D3 | Only 350 patents in window — implausibly low for one of the most patent-heavy semi companies. Likely a post-2021 IP-holding entity not in `assignee_mapping.py`. Investigate Week 2 by re-running `explore_assignees.py` with broader substring or checking PatentsView forum for known re-org. |
| Q4 financials gap (10-K vs 10-Q) | Known issue from D2 | Q4 financials live in 10-K filings; current EDGAR script only pulls 10-Q. Fix Week 2 by adding 10-K parsing. |
| Add `C:\Program Files\PostgreSQL\18\bin` to PATH | Quality-of-life | 60-second fix. Avoids typing full path to `psql.exe`. |
| `cur.rowcount` logging bug in `load_patents.py` | Cosmetic | After batched `execute_values`, `cur.rowcount` only reports last batch. Showed "Inserted 19 new rows" when 61,519 actually landed. Fix when convenient. |
| Co-assigned patents | Logged, not analyzed | 108 patents in our universe have ≥2 of our 12 tickers as co-assignees. Possible Week 3 sidebar (cross-company collaboration signal). |
| Delete `explore_assignees.py` from repo | Cleanup | Throwaway exploration script. Was useful for D3, no longer needed. Delete in Week 2 cleanup pass. |

---

## 10. Roadmap (remaining)

### Week 1 — plumbing (current)
- ✅ D1: Postgres setup + companies + financials loader
- ✅ D2: EDGAR backfill + schema for patents table
- ✅ D3: Patents ETL end-to-end (downloads → mapping → loader → Postgres)
- ⏭ **D4 (next session): Hiring signals ETL** — see §11
- D5: News/qualitative data ETL + Week 1 wrap

### Week 2 — analytical layer
- Reusable SQL views (e.g. `v_patents_quarterly` aggregated counts per ticker per quarter)
- First exploratory notebook: cross-source correlation checks
- **Re-investigate AVGO patent gap (see §9)**
- Fix Q4 financials gap by parsing 10-Ks

### Week 3 — first analyses
- 3-5 driving analytical questions with clean charts
- Cross-source observations (e.g. "do hiring spikes precede patent surges?")

### Week 4-5
- Claude API integration for news summarization
- Comparative analyses across tickers

### Week 6
- GitHub Actions for nightly refresh (all loaders idempotent — designed for this)
- Public-ready write-up + portfolio README

---

## 11. Next session plan (Week 1 Day 4) — START HERE

**Theme:** Hiring signals ETL. Goal: produce a `hiring_signals` table with job-posting counts per ticker per time period.

### First decision of the session: which data source?

| Source | Pros | Cons |
|---|---|---|
| LinkedIn (scraped) | Best signal (company-level, real-time) | ToS issues; requires proxy/scraper; fragile |
| BLS QCEW | Government, clean, free | ~5 month lag; industry-level not company-level |
| Indeed/Glassdoor | Decent signal | Same scraping concerns as LinkedIn |
| Revelio Labs API | Clean, commercial-grade, company-level | Paid (not viable for student project) |
| LinkedIn via proxy service (e.g. Bright Data) | Best signal, legal-ish | Costs money |
| Company career pages (direct) | Free, no ToS gray area, company-level | Each company's site is different — bespoke scrapers |

**Recommended starting point:** scrape company career pages directly for the 12 tickers. Free, no ToS gray area, gives company-level signal. Bottleneck: each company's career site has a different structure. Discuss tradeoff with Johan at session start.

### Plan: ~2 hours

1. (15 min) Discuss data source tradeoffs with Johan, pick one with him
2. (10 min) Define `hiring_signals` table schema, add to `sql/schema.sql`, create table
3. (60 min) Write loader script following pattern from `load_patents.py`
4. (20 min) Run it, sanity-check, investigate anomalies
5. (15 min) Update HANDOFF.md, commit

### Pre-session recommendation (10 min, optional)

Johan should skim `etl/load_patents.py` one more time — D4's loader will mirror its structure (read source → filter → transform → insert with conflict handling).

---

## 12. Reproducibility checklist (for "rebuild from scratch" scenarios)

1. Clone repo
2. `python -m venv venv && venv\Scripts\Activate.ps1`
3. `pip install -r requirements.txt`
4. Create `.env` from `.env.template` (template needs to be created — TODO)
5. `& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d sector_signals -f sql/schema.sql`
6. `python etl/load_financials.py`
7. `python etl/edgar_backfill.py`
8. `python etl/download_patents.py` (~15 min download)
9. `python etl/load_patents.py` (~22 min load)
10. Verify: `SELECT COUNT(*) FROM patents;` should return **61,519** (give or take new patents granted since D3)

---

## 13. Specific behaviors next-session Claude should NOT do

Anti-patterns to avoid based on what worked vs didn't on D3:

- ❌ Don't write code without flagging which sections matter to read. Johan will read everything if you don't direct his attention — wastes 30-50 min.
- ❌ Don't fence-sit when Johan asks for a recommendation. If he says "your call," pick one with reasoning.
- ❌ Don't ask 5 clarifying questions at once. One at a time, address ambiguity in answer first.
- ❌ Don't use `ask_user_input_v0` for things Johan has already told you. Read this handoff carefully.
- ❌ Don't lecture about discipline (passwords, git, etc.) more than once per issue. Mention, move on, trust him to internalize.
- ❌ Don't predict runtimes too precisely. Day 3 patents load was 22 min, predicted 3-5. Better to say "could be 5-30 min depending on your disk."
- ❌ Don't bury the lede. When Johan asks "very briefly" or "what does X do," give the answer in sentence 1, context in sentence 2+.
- ❌ Don't write placeholder code Johan will run verbatim ("cd path\to\sector-signals"). Either give a real path or make it obvious it's a placeholder.

---

## 14. Things to do BEFORE next session (Johan)

- ✅ DB password rotated (done D3 evening)
- ⏭ Commit Day 3 work: `git add etl/ HANDOFF.md && git commit -m "Week 1 Day 3: Complete patents ETL" && git push`
- ⏭ (Optional) Add Postgres bin to PATH for quality-of-life
- ⏭ (Optional) Decide which hiring data source to investigate before D4 starts — see §11

---

**End of handoff. Next session: paste this entire document at the start of the new chat.**