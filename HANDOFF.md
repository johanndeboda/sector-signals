# HANDOFF — sector-signals

Last updated: end of Day 8 (2026-06-01).

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
learning PostgreSQL, git, API patterns, etc. through this project). Don't
assume deep CS background. When there's a choice between "impressive but
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
  To recreate the env: `pip install -r requirements.txt`.
- **gitignored:** `venv/`, `__pycache__/`, `*.pyc`, `.env`, `data/`,
  `.ipynb_checkpoints/`, `.vscode/`, `.DS_Store`, `*_test.json`
  (the last added Day 7 to keep curl debug artifacts out).

---

## 4. Repo layout (the parts that matter)

```
etl/
  load_patents.py      # USPTO patents loader (Days 1–3)
  load_hiring.py       # Careers-page job loader (Days 4–8) ← active file
sql/
  schema.sql           # table definitions
HANDOFF.md             # this file
requirements.txt
.env                   # gitignored
```

The pipeline is intentionally one-script-per-signal-type. Each script is
idempotent: re-running on the same day inserts only net-new rows via
`ON CONFLICT DO NOTHING` on a `(record_id, snapshot_date)` PK.

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

---

## 7. ATS landscape (complete as of Day 8)

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

## 8. Current data state (snapshot 2026-06-01)

From DB after final Day 8 run:

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
(SNPS, ANSS, TSM) are blocked/skipped.

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
- **Connection resets are transient.** Several runs during Day 8 hit
  `ConnectionResetError` mid-pagination on various tickers. Always
  resolved on re-run. The idempotent insert design handles this — re-run
  inserts only net-new rows. A retry decorator would help but is not
  blocking (Day 9 candidate).
- **Oracle HCM URL encoding quirk.** The `finder` param uses semicolons
  and commas as internal delimiters. `limit`, `sortBy`, `offset` go
  inside `finder` (comma-separated), not as top-level `&` params.
  Semicolons in `facetsList` must be percent-encoded (`%3B`). Python's
  `requests` library will double-encode if you use the `params` dict —
  the URL must be built manually as an f-string.
- **Run time is ~20–30 min** for a full 9-ticker sweep. NVDA's faceted
  mode (14 facets × pagination × sleep) is the bulk. Acceptable for
  daily batch but could be optimized with concurrency.

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

---

## 11. Day 9 plan

In priority order:

1. **Retry logic for flaky connections.** Days 7–8 saw repeated
   `ConnectionResetError` mid-pagination. A simple retry decorator
   (3 attempts, exponential backoff) on each page request would make
   the daily run more reliable. Small change, high impact.

2. **Update the stale module docstring** at the top of `load_hiring.py`
   (still says "Day 4 SCOPE"). Should reflect the 5-ATS, 9-ticker
   reality.

3. **Playwright path for SNPS + TSM.** If both are unblocked, that's
   11 of 12 tickers (ANSS stays skipped). Playwright adds a real
   dependency (`pip install playwright && playwright install chromium`).
   Worth it only if the project will run long enough to justify the
   maintenance. Decision: revisit after analysis layer is built.

4. **Begin the analysis / timeseries layer.** The ingestion pipeline is
   ~75% complete (9/12 tickers). Enough data to start building:
   - Daily job-count timeseries per ticker
   - Category distribution comparisons
   - Hiring velocity (new postings per day)
   - Cross-signal joins with patent data
   This is the next major phase of the project.

5. **Per-job category enrichment** for non-faceted Workday tickers and
   Oracle HCM. Low priority — the aggregated facet counts may be
   sufficient for analysis.

### Stretch

- **Concurrent fetching.** `asyncio` + `aiohttp` or `ThreadPoolExecutor`
  to fetch multiple tickers in parallel. Would cut run time from ~25 min
  to ~5 min. Not blocking but nice for daily ops.
- **INTC / AVGO Workday re-verification.** Both were added Day 6 from
  config alone. Row counts in §7 look reasonable but haven't been
  sanity-checked against their public careers-page totals.

---

## 12. How to start the next session

Hand Claude this file plus a short prompt like `start day 9`. Claude should:

1. Read this HANDOFF in full.
2. Open §11 and pick the top priority that isn't already done.
3. Ask before writing any code if there's a judgment call (scope
   trade-off, dependency decision, architecture choice for analysis).

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

DB sanity check:
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d sector_signals -c "SELECT ticker, COUNT(*) AS n_jobs, COUNT(posted_date) AS with_date, COUNT(category) AS with_category, MIN(posted_date) AS oldest, MAX(posted_date) AS newest FROM hiring_signals WHERE snapshot_date = CURRENT_DATE GROUP BY ticker ORDER BY ticker;"
```

Test an endpoint without Python (cURL bisection):
```powershell
curl.exe -s -o test.json -w "size=%{size_download} status=%{http_code}`n" "<URL>" -H "User-Agent: Mozilla/5.0 ..." -H "X-Requested-With: XMLHttpRequest" -H "Referer: <listings page>"
```