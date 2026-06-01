# HANDOFF — sector-signals

Last updated: end of Day 9 (2026-06-01).

This is the working memory between Claude sessions. Read this first.

---

## 1. What this project is

A 12-ticker semiconductor-sector signal pipeline. For each ticker we ingest
multiple "signal" datasets (patents, hiring, etc.) into Postgres, snapshot
daily, then later join everything into a per-ticker timeseries for analysis.

Tickers (the "semi-12"): NVDA, AMD, AVGO, QCOM, INTC, TSM, MU, MRVL, CDNS,
SNPS, ANSS, TXN.

Repo: `github.com/johanndeboda/sector-signals` (branch: `main`).

---

## 2. Who's building this (optimize for this person)

- **Name:** Johann De Boda
- **Year/Major:** 2nd-year MIS major, Bay Area (Union City, CA)
- **Hardware:** Dell XPS 15

**Technical skills (honest):**
- Python: scripts, pandas, basic data cleaning. Learning intermediate.
- SQL: basic SELECTs, WHERE, simple JOINs (learned via SQLite + DB Browser).
  PostgreSQL is new as of this project.
- Excel: pivots, VLOOKUP/XLOOKUP, basic formulas.
- Jupyter/VS Code notebooks: new as of Day 9.
- No prior experience: Tableau, Power BI, cloud tools, NLP, forecasting.
- Willing to learn: intermediate/advanced SQL and Python, plus 1–2 new tools.

**Domain experience:** Cadence Design Systems consulting project (via Marketing
Association) — performed competitive analysis, external touchpoint audit,
student perception survey, social media/careers page prototypes, and a
Generative Engine Optimization analysis for Cadence. Already has semiconductor
and EDA industry knowledge and consulting-style deliverable experience.

**Target roles:** Business/Data Analyst (open to consulting, product, strategy,
intelligence). Not narrowed to FAANG/Big 4/F500.

**Timeline:** Resume-ready by fall internship recruiting (~Aug–Dec 2026).
10–20 hrs/week over summer.

**What matters for the portfolio:**
- Projects that show **measurable impact and results**, not just technical skills.
- Clear differentiator vs. other 2nd-year MIS candidates.
- Coherent interview story that builds on the Cadence experience.
- Technical depth that signals "ready for an analyst internship."
- Comfortable building in public: weekly LinkedIn updates, public GitHub.

**Communication preferences:** Concise, no fluff. Verify info via search when
uncertain. Ask clarifying questions before big recommendations.

**Implication for Claude:** Explain new concepts when they come up (Johann is
learning PostgreSQL, git, API patterns, Jupyter, etc. through this project).
Don't assume deep CS background. When there's a choice between "impressive but
opaque" and "clear and explainable in an interview," choose the latter.

---

## 3. Environment

- **OS:** Windows, PowerShell.
- **Python:** in `venv/` at repo root. Activate with `venv\Scripts\Activate.ps1`.
- **DB:** PostgreSQL **18.3**, local. `psql.exe` is NOT on PATH — call it with
  the full path:
  ```
  & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d sector_signals -c "..."
  ```
  Connection details live in `.env` (gitignored): `DB_HOST`, `DB_PORT`,
  `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
- **Deps:** see `requirements.txt`. New as of Day 7: `beautifulsoup4`.
  New as of Day 9: `ipykernel`, `matplotlib`, `seaborn`, `sqlalchemy`.
  `requirements.txt` is regenerated via `pip freeze` so it includes all
  transitive deps with pinned versions (longer than a hand-curated list,
  but reproducible).
  To recreate the env: `pip install -r requirements.txt`.
- **Notebooks:** VS Code's native Jupyter support (no standalone jupyter
  server). Kernel = the repo venv. Common foot-gun: VS Code defaults to
  global Python — explicitly select the `venv` kernel via top-right
  "Select Kernel" → "Python Environments" → the one with `venv\Scripts\` in
  the path.
- **gitignored:** `venv/`, `__pycache__/`, `*.pyc`, `.env`, `data/`,
  `.ipynb_checkpoints/`, `.vscode/`, `.DS_Store`, `*_test.json`.

---

## 4. Repo layout (the parts that matter)

```
etl/
  load_patents.py      # USPTO patents loader (Days 1–3)
  load_hiring.py       # Careers-page job loader (Days 4–9) ← active file
sql/
  schema.sql           # table definitions
analysis/              # NEW Day 9 — Jupyter notebooks for signal analysis
  01_hiring_snapshot.ipynb
HANDOFF.md             # this file
requirements.txt
.env                   # gitignored
```

The pipeline is intentionally one-script-per-signal-type. Each script is
idempotent: re-running on the same day inserts only net-new rows via
`ON CONFLICT DO NOTHING` on a `(record_id, snapshot_date)` PK.

Analysis lives in `analysis/` as numbered notebooks (`01_`, `02_`, ...) so
the narrative reads left-to-right when browsing on GitHub. Notebooks are
committed **with outputs intact** so charts render on github.com without
cloning — explicit portfolio decision, opposite of the "strip outputs"
convention used in collaborative production work.

---

## 5. Database schema (hiring_signals)

```sql
CREATE TABLE hiring_signals (
    job_id        TEXT NOT NULL,         -- "<TICKER>:<rawid>" — guaranteed unique within ticker
    ticker        TEXT NOT NULL,
    snapshot_date DATE NOT NULL,         -- day we observed this posting
    title         TEXT,
    location      TEXT,
    posted_date   DATE,                  -- when the company says the job was posted
    category      TEXT,                  -- ATS-defined (Workday jobFamilyGroup, Eightfold department, etc.)
    ats           TEXT,                  -- "workday" | "jibe" | "talentbrew" | "eightfold" | "oracle_hcm"
    job_url       TEXT,
    PRIMARY KEY (job_id, snapshot_date)
);
```

`patents` table follows the same shape, see `sql/schema.sql`. All fetchers
yield 9-key dicts matching the columns above — that contract is enforced
in `insert_jobs()`.

---

## 6. Day-by-day history (compressed)

- **Day 1–3:** USPTO patent loader. Tickers → CPC codes → daily snapshots.
  Production-stable.
- **Day 4:** Workday job loader for NVDA/CDNS/MRVL. Discovered Workday's
  global 2000-result cap; built `force_faceted` mode for NVDA that loops
  per-jobFamilyGroup facet to recover full count.
- **Day 5:** Added Jibe fetcher for AMD. Discovered AMD's public careers
  (`careers.amd.com`) is a Jibe-fronted portal over an iCIMS back-end.
  Established the "tag the layer the fetcher actually talks to" rule
  (`ats="jibe"`, not `"icims"`). Built the `FETCHERS` dispatch registry so
  adding a platform = write one function + add one line.
- **Day 6:** Config-only — added INTC and AVGO once their Workday tenants
  were confirmed. Both standard, no faceting needed.
- **Day 7:** TalentBrew fetcher for SNPS. Structurally complete but
  shipped disabled — `careers.synopsys.com` is behind stateful anti-bot
  fingerprinting (likely Akamai Bot Manager). cURL-bisection confirmed
  the gate is JS-issued cookies, not header-based.
- **Day 8:** Three new tickers live:
  - **QCOM** — Eightfold AI (not TalentBrew as the Day 7 plan guessed).
    New `fetch_eightfold_jobs()` fetcher. Clean GET API, no auth,
    Unix timestamps, `department` field gives free categories.
  - **MU** — Also Eightfold. Config-only addition (same fetcher as QCOM).
    Biggest ticker at ~3000 jobs.
  - **TXN** — Oracle HCM Cloud. New `fetch_oracle_hcm_jobs()` fetcher.
    Quirk: `limit`/`offset`/`sortBy` go inside the `finder` param
    (comma-delimited), not as separate `&` query params. Semicolons in
    `facetsList` must be percent-encoded (`%3B`). No per-job category.
  - **TSM** — Investigated. Server-side rendered HTML (no XHR API),
    returns 403 on plain requests. Anti-bot gated. Disabled.
  - **ANSS** — Confirmed: `careers.ansys.com` redirects to SNPS.
    Same TalentBrew, same anti-bot gate. Stays disabled.
  - **Playwright decision:** Only SNPS + TSM are gated (ANSS is a
    redirect). Two tickers isn't enough to justify adding Playwright
    as a dependency. Revisit if a third appears.
- **Day 9:** Two work streams shipped, two clean commits to `main`.
  - **Ingestion hardening (commit 1):**
    - Added `_request_with_retry(method, url, ...)` helper at the top of
      `load_hiring.py` (3 attempts, exponential backoff 1s→2s, retries
      on `ConnectionResetError`, `requests.exceptions.ConnectionError`,
      `ChunkedEncodingError`, `Timeout`). Re-raises after final attempt
      so `main()`'s existing `except` clauses still catch terminal
      failures.
    - Decorated the **single-page request sites**, not the pagination
      loops — so a transient reset retries one page instead of
      restarting the whole ticker. 5 call sites swapped (lines 127, 209,
      320, 570, 678 covering all 5 active fetchers).
    - Refreshed stale module docstring (was Day 4-era, only described
      Workday; now lists all 5 ATS platforms and the registry pattern).
    - Removed dead `from email.mime import base` import.
  - **Analysis kickoff (commit 2):**
    - New `analysis/` folder + first notebook `01_hiring_snapshot.ipynb`.
    - Jupyter env wired into VS Code: `ipykernel`, `matplotlib`,
      `seaborn`, `sqlalchemy` added to `requirements.txt`. `sqlalchemy`
      so `pandas.read_sql` doesn't throw the noisy "DBAPI2 not tested"
      warning against raw `psycopg2` connections.
    - Notebook ships with: DB connection cell, per-ticker open-jobs
      summary query, bar chart, and an analyst-style **Observations**
      markdown cell.
    - Key findings (verified against latest 10-Ks):
      - MU leads the hiring book at 3,024 open postings vs NVDA's
        2,654 — consistent with Micron's active CHIPS-Act fab buildout
        (Idaho, New York).
      - NVDA still has the higher hiring **intensity** (6.3% vs 5.7%
        open-role ratio) — raw count overstates large companies, ratio
        is the fairer comparison.
      - AVGO is the standout anomaly: 338 open postings against a
        33k-employee base (1.0% ratio), and workforce *shrank* 10.8%
        YoY (37k → 33k per Nov 2025 10-K). Consolidation mode post-
        VMware, not growth mode. Worth tracking snapshot-over-snapshot.
  - **INTC/AVGO sanity check:** browser-eyeballed against careers-page
    totals — 713/340 displayed vs 715/338 in DB. Within noise (<1%).
    Both Workday tenants confirmed healthy.

---

## 7. ATS landscape (complete as of Day 8, unchanged Day 9)

| ATS | Tickers | API style | Category? | Date quality |
|-----|---------|-----------|-----------|--------------|
| Workday | NVDA, CDNS, MRVL, INTC, AVGO | POST JSON | Only via faceting (NVDA) | Relative ("5 Days Ago"), caps at 30d |
| Jibe | AMD | GET JSON | Yes (`categories[].name`) | Real ISO timestamps |
| Eightfold | QCOM, MU | GET JSON | Yes (`department`) | Unix timestamps (real dates) |
| Oracle HCM | TXN | GET JSON | No (aggregated only) | Real ISO dates |
| TalentBrew | SNPS (disabled) | GET JSON+HTML | Yes | MM/DD/YYYY |
| Unknown/SSR | TSM (disabled) | N/A | N/A | N/A |
| Skip | ANSS | N/A | N/A | Redirects to SNPS |

**"Tag what we talk to" rule:** AMD = Jibe(front) + iCIMS(back) → `ats="jibe"`.
SNPS = TalentBrew(front) + Avature(back) → `ats="talentbrew"`. The fetcher
talks to the front-end API; the back-end ATS is irrelevant to the tag.

**Config fields required per ATS:**
- **Workday:** `host`, `tenant`, `site`. Optional: `force_faceted`, `facet_param`.
- **Jibe:** `host` only.
- **Eightfold:** `host`, `domain` (e.g. `"qualcomm.com"`), `ticker`.
  Page size is 10, server-determined — no `limit` param in the API.
- **Oracle HCM:** `tenant_host` (API host, e.g. `"edbz.fa.us2.oraclecloud.com"`),
  `public_host` (careers site, e.g. `"careers.ti.com"`). Two different hosts.
- **TalentBrew:** `host` only.
- **TSM (for future Playwright):** URL pattern is
  `careers.tsmc.com/en_US/careers/SearchJobs/?jobRecordsPerPage=10&jobOffset=0`.
  Server-side rendered HTML, no XHR API. Returns 403 without a real browser.

---

## 8. Current data state (snapshot 2026-06-01, end of Day 9)

From DB:

```
 ticker | n_jobs | with_date | with_category |   oldest   |   newest
--------+--------+-----------+---------------+------------+------------
 AMD    |   1087 |      1087 |          1087 | 2025-05-07 | 2026-06-01
 AVGO   |    338 |       338 |             0 | 2026-05-02 | 2026-06-01
 CDNS   |    623 |       623 |             0 | 2026-05-02 | 2026-06-01
 INTC   |    715 |       714 |             0 | 2026-05-02 | 2026-06-01
 MRVL   |    677 |       677 |             0 | 2026-05-02 | 2026-06-01
 MU     |   3024 |      3023 |          2858 | 2024-05-23 | 2026-05-31
 NVDA   |   2654 |      2654 |          2654 | 2026-05-02 | 2026-06-01
 QCOM   |   1985 |      1985 |          1985 | 2025-03-12 | 2026-05-31
 TXN    |    470 |       470 |             0 | 2025-02-05 | 2026-06-01
```

Nine tickers live, 11,573 jobs in today's snapshot. Three remaining
(SNPS, ANSS, TSM) are blocked/skipped. Total rows in `hiring_signals`
across all snapshots: ~62.9k (≈5–6 days of accumulated history as of EOD 9).

---

## 9. Known issues / quirks

- **Workday `posted_date` resolution caps at 30 days.** Workday returns
  a relative phrase (`"Posted 30+ Days Ago"`), so anything older than a
  month parses as `snapshot - 30`. AMD's Jibe and Eightfold tickers
  (QCOM, MU) give real timestamps, hence the older `oldest` dates in §8.
  Documented, not a bug.
- **`category` is NULL for non-faceted Workday + Oracle HCM.** Workday's
  `_paginate_workday` only stamps `category` when fetching by
  `jobFamilyGroup` facet (NVDA). Oracle HCM has categories only in
  aggregated facets, not per-job. CDNS, MRVL, INTC, AVGO, TXN all show
  `with_category=0`. Either enrich via secondary requests or accept the
  gap. Currently accepted.
- **MU has ~166 jobs without category.** Some Eightfold postings don't
  have the `department` field set. Minor, not actionable.
- **`insert_jobs()` rowcount is cosmetic.** We print `len(rows)`
  submitted, not actual new inserts, because psycopg2's `execute_values`
  rowcount under `ON CONFLICT DO NOTHING` is unreliable. To know real
  inserts: query the table.
- **Skip message wording is slightly misleading.** When SNPS is disabled
  the log says "ats=talentbrew, not yet implemented" but the fetcher
  *is* implemented. Cosmetic.
- **Oracle HCM URL encoding quirk.** The `finder` param uses semicolons
  and commas as internal delimiters. `limit`, `sortBy`, `offset` go
  inside `finder` (comma-separated), not as top-level `&` params.
  Semicolons in `facetsList` must be percent-encoded (`%3B`). Python's
  `requests` library will double-encode if you use the `params` dict —
  the URL must be built manually as an f-string.
- **Run time is ~20–30 min** for a full 9-ticker sweep. NVDA's faceted
  mode (14 facets × pagination × sleep) is the bulk. Acceptable for
  daily batch but could be optimized with concurrency.
- **Location strings are unstandardized across ATSes.** "Santa Clara, CA"
  vs "Santa Clara, California, USA" vs "USA - California - Santa Clara"
  all appear depending on platform. Any geographic analysis needs a
  normalization step. Not blocking, but planned for Day 10.

### Resolved this day
- ~~Transient `ConnectionResetError` mid-pagination needs retries~~ —
  resolved Day 9 via `_request_with_retry` helper.

---

## 10. Key methodologies (reference)

### cURL-bisection (Days 5, 7, 8)

When a request works in the browser but not in Python:

1. DevTools → Network → right-click the request → **Copy as cURL**.
2. Paste in PowerShell. If it works, strip headers one at a time until
   it breaks — that header was the gate.
3. If it fails immediately with the **exact** browser headers from the
   same machine/IP, the gate isn't header-based. It's stateful:
   JS-issued cookies (`_abck` / `bm_sz` from Akamai/Imperva), browser
   fingerprinting, etc. No amount of header tuning will help — you need
   Playwright or curl-impersonate.

This is how SNPS was diagnosed as blocked in ~3 steps instead of a long
debugging spiral. Also confirmed TSM (403 on plain curl).

### Two-layer ATS pattern

Many companies stack a front-end portal on a different back-end ATS:
- AMD = **Jibe** (front) + **iCIMS** (back)
- SNPS = **TalentBrew** (front) + **Avature** (back)

The Day 5 plan guessed "iCIMS for AMD" and Day 7 guessed "Avature for
SNPS" — both based on the back-end. Live DevTools inspection revealed
the front-end was different each time. **Always inspect the Network tab
before assuming an ATS from plan docs or prior research.**

### Plan-doc accuracy track record

| Ticker | Plan-doc guess | Actual (via Network tab) |
|--------|---------------|--------------------------|
| AMD | iCIMS | Jibe |
| SNPS | Avature | TalentBrew |
| QCOM | TalentBrew | Eightfold |
| TXN | Oracle HCM | Oracle HCM ✓ |

Rule: always verify by Network tab inspection first. The plan is wrong
more often than it's right.

### Verification by 10-K (Day 9)

For analysis claims involving headcount, market cap, or workforce trends,
pull the most recent 10-K (or aggregator citing it) before committing
numbers to the public notebook. Day 9 found that off-the-cuff employee
counts (NVDA 36k, MU 48k, AVGO 37k) were all one fiscal year stale; the
verified current numbers (42k, 53k, 33k) materially changed the AVGO
story — the YoY decline (37k → 33k) was the *strongest* evidence for
the consolidation-mode framing, not a footnote.

Rule: any specific number that goes on the portfolio gets verified
against a primary source (10-K, investor relations) before commit.

### Retry placement (Day 9)

When wrapping HTTP calls in retries, decorate the **smallest unit that
makes one request**, not the surrounding loop. A retry on
`_paginate_workday` would restart pagination from page 1 on a transient
failure at page 47. A retry on the single `requests.post(...)` call
retries only page 47, preserving progress. Same logic: smallest possible
blast radius.

---

## 11. Day 10 plan

In priority order:

1. **Geographic spread analysis** — addresses the open question teed
   up in `01_hiring_snapshot.ipynb`'s observations cell. Use the
   `location` field to compare cross-ticker geographic concentration
   (US vs Asia vs EU, single-HQ vs distributed). **Real work item:**
   location strings are unstandardized across ATSes — a normalization
   step (regex extraction of country/region, or a manual mapping table
   for the top ~30 location strings) is required before the analysis
   means anything. New cells in `01_hiring_snapshot.ipynb` OR a new
   `02_hiring_geography.ipynb` — decide based on how long the
   normalization detour gets. If clean, append; if it sprawls, split.

2. **Category mix analysis** — the second open question from Day 9
   observations. Limited coverage: only NVDA, AMD, QCOM, MU have
   per-job categories. Each uses a different taxonomy (Workday
   `jobFamilyGroup` vs Jibe `categories[].name` vs Eightfold
   `department`), so cross-ticker comparison needs a mapping layer.
   Practical scope: do *within-ticker* category breakdowns first
   (one stacked bar per ticker showing role-mix), defer cross-ticker
   normalization until a clear analysis use-case demands it.

3. **Snapshot-over-snapshot delta** — by Day 10 the DB has 2–3 days
   of accumulated history per ticker. A simple delta query (jobs
   added / removed since yesterday's snapshot, per ticker) becomes
   meaningful and gives the first true *flow* signal. Worth a small
   cell at end of `01_` to start tracking.

### Stretch

- **Hiring velocity** — for tickers with real `posted_date` coverage
  (AMD, MU, QCOM, TXN), bucket postings into weekly bins and chart
  velocity. Workday tickers limited to the past 30 days but still
  show recent trend. Powerful chart for the portfolio.
- **Cross-signal join with patents.** Both tables share `ticker` and
  `snapshot_date`. First exploratory join: per-ticker monthly counts of
  (new patents, new job postings) side-by-side. Sets up the
  cross-signal narrative the project name promises.
- **Concurrent fetching.** `asyncio` + `aiohttp` or
  `ThreadPoolExecutor` to fetch multiple tickers in parallel. Would
  cut run time from ~25 min to ~5 min. Not blocking but nice for
  daily ops.
- **Playwright path for SNPS + TSM.** Still deferred. Worth
  revisiting only if the analysis layer hits a place where the missing
  three tickers are a real gap.
- **Per-job category enrichment** for non-faceted Workday + Oracle
  HCM. Low priority; revisit when an analysis specifically wants it.

---

## 12. How to start the next session

Hand Claude this file plus a short prompt like `start day 10`. Claude should:

1. Read this HANDOFF in full.
2. Open §11 and pick the top priority that isn't already done.
3. Ask before writing any code if there's a judgment call (scope
   trade-off, dependency decision, architecture choice for analysis).
4. For analysis work, default to extending `01_hiring_snapshot.ipynb`
   unless the new analysis is structurally separate enough to warrant
   `02_*.ipynb`. Commit notebooks with outputs intact.

---

## 13. Useful commands

Activate venv:
```powershell
venv\Scripts\Activate.ps1
```

Run the hiring loader:
```powershell
python etl/load_hiring.py
```

DB sanity check (today's snapshot, per-ticker):
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d sector_signals -c "SELECT ticker, COUNT(*) AS n_jobs, COUNT(posted_date) AS with_date, COUNT(category) AS with_category, MIN(posted_date) AS oldest, MAX(posted_date) AS newest FROM hiring_signals WHERE snapshot_date = CURRENT_DATE GROUP BY ticker ORDER BY ticker;"
```

Total rows across all snapshots:
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d sector_signals -c "SELECT COUNT(*) FROM hiring_signals;"
```

Test an endpoint without Python (cURL bisection):
```powershell
curl.exe -s -o test.json -w "size=%{size_download} status=%{http_code}`n" "<URL>" -H "User-Agent: Mozilla/5.0 ..." -H "X-Requested-With: XMLHttpRequest" -H "Referer: <listings page>"
```

Open the analysis notebook (VS Code):
```powershell
code analysis/01_hiring_snapshot.ipynb
```
Then select the venv kernel via top-right "Select Kernel" if VS Code
defaults to global Python.