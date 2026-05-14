# Sector Signals — Project Handoff Doc (v2)

> **How to use this doc:** Drop into a new Claude conversation at the start. Say: *"I'm continuing the Sector Signals project. Here's the full brief. I'm on [Week X, Day Y]. Help me with [task]."* Claude will have full context without re-reading prior chats.

---

## 1. Candidate Profile

- **Year/Major:** 2nd-year MIS major
- **Time commitment:** 20–25 hrs/week (compressed timeline — see §6)
- **Resume timing goal:** Project done by late June / early July 2026; remaining summer used for company research + interview prep before Aug–Sep application season
- **Target roles:** Business/Data Analyst leaning, flexible across consulting, product, strategy
- **Target companies:** Open — not narrowed to FAANG / Big 4 / F500
- **Build in public:** Yes (3–5 LinkedIn posts across project, public GitHub)
- **Location:** Bay Area (strong fit for semi recruiting — Cadence, Synopsys, NVIDIA, AMD, Applied Materials)

### Technical baseline (at project start)
- **Python:** Scripts, pandas, basic data cleaning
- **SQL:** Basic SELECTs, WHERE, simple JOINs (via SQLite previously)
- **Excel:** Pivots, VLOOKUP/XLOOKUP
- **Pushing into:** Intermediate→advanced SQL/Python, Postgres, Tableau, LLM API workflows
- **No prior:** Tableau, Power BI, NLP, forecasting, cloud DBs

### Prior relevant experience — Cadence Design Systems consulting project
Analyzed Cadence's industry/competitors, ran external touchpoint audit, student perception survey, built improvement prototypes for social media/early careers/job listings, performed Generative Engine Optimization analysis. Gained semiconductor + EDA industry domain knowledge. **This project compounds that story** — semi is the demo industry because of this prior context.

---

## 2. Project: "Sector Signals"

### Working framing
**Sector Signals: A continuously-updating intelligence pipeline that integrates financial, innovation, and hiring data to surface strategic signals before they appear in earnings. Demoed on semiconductors.**

Reframed from the original "Semi Signals" to be sector-agnostic in architecture, semi-focused in execution. This dual framing lets the candidate pitch *both* domain depth (semis) AND systems thinking (reusable pipeline) depending on the recruiter.

### Core thesis question
*What hiring and innovation signals predict strategic and financial shifts across an industry before they show up in earnings?*

### Strategic rationale
1. **Story compounding:** Builds on Cadence consulting → coherent 2-year narrative
2. **Differentiation:** Multi-source ETL + LLM workflows is rare at junior level
3. **Domain defensibility:** Can speak confidently about semi industry in interviews
4. **Bay Area recruiting fit:** Local semi companies hire heavily
5. **Real systems work:** Not "I analyzed a Kaggle CSV"
6. **AI-native:** Uses Claude API for unstructured text classification (the 2026 differentiator)

### Final deliverables (target)
- PostgreSQL database, 5+ years multi-source data, ~12 companies
- Python ETL scripts (idempotent, re-runnable, documented, in GitHub)
- Analytical Jupyter notebook (EDA, correlations, insights)
- Tableau Public dashboard (shareable link)
- 1-page executive summary (consulting-style PDF)
- LinkedIn posts: 3–5 across project (kickoff, mid-project, dashboard preview, final)
- GitHub repo with strong README
- **Pivot from YouTube video critique:** GitHub Actions nightly ETL workflow → "live system" signal

---

## 3. Tech Stack (Locked In)

| Layer | Tool | Rationale |
|---|---|---|
| Database | **PostgreSQL 16** + pgAdmin | Industry-standard, strong resume signal |
| Code editor | VSCode | Already familiar |
| Language | Python (pandas, sqlalchemy, psycopg2, yfinance, requests, anthropic) | Familiar; anthropic SDK for LLM workflows |
| Ad-hoc | Excel | Familiar |
| Dashboard | **Tableau Public** | Free, shareable link, portfolio-friendly |
| Version control | Git + GitHub (public repo) | Build in public |
| AI/NLP | **Anthropic Claude API** | LLM classification + structured extraction |
| Automation | **GitHub Actions** (Week 9) | Nightly ETL re-run = "live system" signal |
| Distribution | LinkedIn | Build in public |

**Considered + rejected:** BigQuery (overcomplicated), SQLite (weaker signal), DuckDB (less recognized), Power BI (less shareable), Kaggle-only data (weak skill signal).

---

## 4. Data Sources

| Dataset | Source | Status | Notes |
|---|---|---|---|
| Financials (quarterly + daily stock) | `yfinance` + SEC EDGAR | ✅ Loaded Week 1 D1–D2 | ~14k daily prices, 215 quarterly rows |
| Patents | **PatentsView bulk TSV downloads (hosted on ODP/S3)** | 🔧 In progress — Week 1 D2 prep; load Day 3+ | PatentSearch API decommissioned 3/20/26; bulk files confirmed live |
| Job postings | Greenhouse/Lever APIs or Kaggle | TBD Week 2 | LLM classification on raw titles |
| Earnings transcripts | Motley Fool scrape or Kaggle | Week 4 (promoted from stretch) | LLM structured signal extraction — core differentiator |

### Target companies (12)
- **EDA:** Cadence (CDNS), Synopsys (SNPS), Ansys (ANSS)
- **Fabless:** NVIDIA (NVDA), AMD, Qualcomm (QCOM), Broadcom (AVGO), Marvell (MRVL)
- **IDM:** Intel (INTC), Micron (MU), Texas Instruments (TXN)
- **Foundry:** TSMC (TSM)

---

## 5. Database Schema (Loaded)

Five tables, all FK back to `companies` via ticker. Composite PKs on time-series tables (ticker + date/quarter).

```
companies
  ticker (PK)  |  name  |  segment (EDA/Fabless/IDM/Foundry)  |  hq_country

financials_quarterly
  (ticker, quarter) (PK)  |  revenue  |  rd_spend  |  net_income  |  operating_margin

stock_prices_daily
  (ticker, date) (PK)  |  open  |  high  |  low  |  close  |  volume

patents
  patent_id (PK)  |  assignee_ticker (FK)  |  grant_date  |  title  |  cpc_class  |  inventor_count

job_postings
  posting_id (PK)  |  ticker (FK)  |  posted_date  |  title  |  location  |
  function (LLM)  |  seniority (LLM)  |  signal_tag (LLM)
```

`companies` table is seeded with all 12 tickers. Schema lives at `sql/schema.sql` in the repo.

**Design principles baked in:**
- Idempotent ETL — all loaders use `ON CONFLICT DO NOTHING` so daily re-runs don't duplicate
- LLM-classified fields are nullable, filled by separate enrichment scripts after raw load
- Time-series tables use composite PKs to enable cleanly partitioned upserts

---

## 6. Compressed 5–6 Week Roadmap

Compressed from original 10-week plan because of 20–25 hr/week commitment and high motivation. Buffer time after = company research + interview prep.

| Week | Focus | Output |
|---|---|---|
| 1 | Env setup, schema, financial ETL, patent ETL | Working Postgres DB + financials + stock prices + patents loaded |
| 2 | Job posting ETL, LLM job classification | Job postings table populated, jobs enriched via Claude API |
| 3 | Data quality, joins, core analysis (revenue, R&D, hiring trends) | Jupyter notebook with first findings |
| 4 | Cross-source correlations + LLM earnings extraction | Key thesis findings, earnings signals table |
| 5 | Forecasting + Tableau dashboard | Dashboard published, predictive layer |
| 6 (buffer) | Writeup, polish, GitHub Action, LinkedIn posts | Portfolio-ready, "live system" signal active |

**Note on Week 1 scope creep (intentional):** Patent ETL was originally scoped for Week 2, but with financials done in Week 1 D1–D2 ahead of schedule, patents starts in Week 1. This buys a half-week of buffer back into Weeks 3–4 (the analysis weeks that matter most).

**Why analysis weeks (3–4) don't compress further:** Insight quality is a thinking problem, not a code problem. Rushing produces shallow findings — the "basic project" trap. Plumbing weeks (1–2, 5) can be sprinted; analysis weeks need breathing room.

---

## 7. Working Agreement Between Candidate and Claude

This is critical. Project must build genuine analyst skill, not just produce artifacts.

### Claude does for candidate / hand-holds on:
- Environment setup, debugging install issues
- Boilerplate code (connection strings, file I/O, plumbing)
- Concept explanations *before* candidate hits them (joins, CTEs, correlation, etc.)
- Code review and pointing out blind spots
- Schema design and architecture decisions

### Candidate drives on:
- Writing analysis SQL queries (Claude teaches concept → candidate writes → Claude reviews)
- Forming hypotheses about what to look for
- Interpreting results — *what does this correlation mean?*
- Choosing what's interesting enough for the dashboard
- Writing exec summary and LinkedIn posts (candidate's voice)
- Choosing how to frame findings

### Pattern shift in Week 3+
Claude's default response changes from *"here's the code, run it"* to *"here's the concept, here's a starter example on a different table, you try it on yours, paste back what you wrote and what came out, we'll iterate."* Candidate tries for ~15 min before asking.

### Why this matters
In interviews, candidate needs to say *"I noticed X, which made me ask Y, so I ran Z."* That's only authentic if candidate did the noticing.

---

## 8. Teaching Style Notes

- **Explain the why, not just the how.** Candidate wants to learn the ropes, not just go through motions.
- **Concise responses, minimize token usage.** No bloat, no repetition, no over-explaining what's already clear.
- **Don't overdo the teaching framing.** Light touch — explain concepts when relevant, don't moralize.
- **Use plain English first, technical terms second.** "Primary key = the column that uniquely identifies each row" before "PK enforces uniqueness."

---

## 9. Current State (as of end of Week 1, Day 2)

**Completed:**
- ✅ All environment setup (Python, Postgres, Git, VSCode, venv, packages)
- ✅ Repo on GitHub, schema loaded, 5 tables + 12 companies seeded
- ✅ `etl/load_financials.py` — yfinance loader, idempotent, working
- ✅ `etl/edgar_backfill.py` — SEC EDGAR backfill (US filers, 5yr quarterly)
- ✅ Data loaded: ~14k daily prices (11 tickers, 5yr), 215 quarterly financials (~5yr for US filers)
- ✅ ANSS handled (delisted via Synopsys acquisition July 2025; pre-acquisition data preserved via EDGAR)
- ✅ TSM scoped to yfinance-only (foreign filer, 20-F not 10-Q)
- ✅ `interview_moments.md` started — 7+ entries (added patents API pivot)
- ✅ Anthropic API key obtained and added to .env
- ✅ USPTO.gov account created + linked to ID.me
- ✅ USPTO ODP API key obtained and added to .env
- ✅ `.env.example` created and committed (template with all 3 API key vars listed)

**Patents data source pivot (Week 1 Day 2 afternoon):**
- Original plan: query PatentSearch API per company for 5yr granted patents
- Discovered on first test call: API decommissioned March 20, 2026; data migrated to bulk TSV downloads
- New plan: download 4 PatentsView TSV files from S3, filter to 12 companies in pandas, upsert to Postgres
- Verified S3 URLs return HTTP 200 (tested `g_assignee_disambiguated.tsv.zip` — 359 MB confirmed)
- ODP API key not wasted: still required for other ODP APIs (assignments, file wrapper) potentially used in Week 3–4 enrichment

**Next up (Week 1, Day 3 — patents ETL execution):**
- Download 4 PatentsView TSV files (~2.5 GB total) into `data/` folder (gitignored):
  - `g_patent.tsv.zip` (~1 GB) — patent id, title, grant date
  - `g_assignee_disambiguated.tsv.zip` (~359 MB) — patent → org mapping
  - `g_inventor_disambiguated.tsv.zip` (~500 MB) — patent → inventors
  - `g_cpc_current.tsv.zip` (~600 MB) — patent → CPC classification
- Build `etl/assignee_mapping.py` — dict of ticker → list of org name variants for all 12 companies (e.g. "NVDA" → ["NVIDIA Corporation", "Nvidia Corp."])
  - Use exploration query against `g_assignee_disambiguated` to find real variants in the data, not guessed
- Write `etl/load_patents.py`:
  - Read `g_assignee_disambiguated` with pandas (likely chunked due to size), filter to target orgs
  - Join against `g_patent` (for title, grant_date), `g_cpc_current` (primary CPC), `g_inventor_disambiguated` (count → inventor_count)
  - Filter `grant_date` to 2021-01-01 onward (5yr window)
  - Idempotent upsert to `patents` table via `ON CONFLICT DO NOTHING`
- Sanity-check loaded data in pgAdmin: counts per ticker, date range, no zero `inventor_count`, expect NVDA in thousands and TSM low (foreign filer)

---

## 10. Project Folder Structure

```
sector-signals/
├── venv/                  # Python virtual env (gitignored)
├── etl/                   # ETL scripts (one per data source)
│   ├── load_financials.py
│   └── edgar_backfill.py
├── notebooks/             # Jupyter analysis notebooks
├── sql/                   # schema.sql + analytical queries
│   └── schema.sql
├── data/                  # Raw downloads (gitignored)
├── .env                   # Secrets (gitignored)
├── .env.example           # Template, in repo
├── .gitignore
├── README.md
├── requirements.txt
├── interview_moments.md   # Running log of interview-worthy anecdotes
└── HANDOFF.md             # This file
```

### `.env` contents (template — see `.env.example` in repo)
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sector_signals
DB_USER=postgres
DB_PASSWORD=<real_password>
ANTHROPIC_API_KEY=<real_key>
USPTO_ODP_API_KEY=<real_key>
```

---

## 11. Open Decisions / TBD

- [x] ~~Patent data source~~ — PatentsView bulk TSV downloads from S3 (API was decommissioned 3/20/26, pivoted Week 1 Day 2)
- [ ] Job postings source — Greenhouse/Lever per-company vs. Kaggle (decision in Week 2)
- [ ] Forecasting model (ARIMA vs. Prophet vs. regression) — Week 5
- [ ] TSM financial backfill depth — accept yfinance-only, or build 20-F parser later? — defer to Week 3
- [ ] Q4 financial data gap — EDGAR returns ~3 quarters/year because Q4 lives in 10-K; do we backfill? — defer to Week 3
- [ ] CPC classification: store only primary class (current schema) vs. extend schema to store all CPC codes per patent — defer until Week 3 analysis reveals whether multi-class matters

---

## 12. Habit to Maintain Throughout Project

**`interview_moments.md`** — Every time something interesting happens (weird data bug fixed, surprising finding, tradeoff weighed), drop 2 sentences in. By Week 4 there'll be 20+ raw anecdotes for interviews that would otherwise be forgotten. Highest-ROI habit of the project.

**Recent additions:**
- W1 D2: PatentsView API was reportedly "in transition" per original plan; discovered via DNS failure on first test call that it had actually been fully decommissioned March 20. Pivoted same-session to bulk TSV approach.

---

## 13. Resume / Interview Framing (draft)

### Resume bullets (refine post-project with real numbers)
- Designed and built a PostgreSQL relational database integrating financials, patent filings, and job postings for 12 major semiconductor companies, ingesting [X] records via idempotent Python ETL pipelines with nightly GitHub Actions refresh.
- Used Anthropic Claude API to classify [X] unstructured job postings and extract structured signals from earnings call transcripts, enabling cross-source correlation analysis.
- Identified [specific insight] by analyzing hiring, R&D spend, and patent output trends — recommended [action].
- Built and published a Tableau Public dashboard visualizing competitive intelligence across the semi/EDA ecosystem.
- Forecasted [metric] using [ARIMA/Prophet] achieving [X%] accuracy on holdout data.

### Interview pitches
- **10-sec:** "Data pipeline pulling financials, patents, and job postings for semi companies into Postgres, with AI to find signals predicting industry shifts."
- **30-sec:** Full project description leading with business problem, ending with sector-agnostic architecture framing.
- **2-min:** Problem (consulting work on Cadence) → Approach (multi-source pipeline) → Tools (Postgres/Python/Claude API/Tableau) → Insight (TBD) → Reflection (TBD).

### Tailored opening hooks (same project, different framings)
- Semi company: *"I analyzed hiring at 12 semi companies including yours and found..."*
- Consulting firm: *"I built a competitive intelligence system surfacing strategic signals across an industry."*
- Fintech / other sector: *"I built a reusable analytics pipeline — semis was the demo, architecture extends to any sector."*

---

## 14. How to Use This Doc

**Starting a new chat:**
> "I'm continuing the Sector Signals project. Here's the full handoff doc. I'm on Week 1, Day 3. Help me write the patents ETL script."

**Returning after a break:**
> "Continuing Sector Signals. Handoff attached. I last completed [X]. Let's keep going from [Y]."

**Asking for a pivot or new direction:**
> "Continuing Sector Signals. Handoff attached. Considering [change]. Walk me through whether it makes sense."

The handoff doc should be updated by Claude at the end of each major milestone (end of each week, or at significant pivots) so the "Current State" section in §9 stays accurate.