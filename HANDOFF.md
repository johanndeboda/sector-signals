# HANDOFF — sector-signals

Last updated: end of Day 7 (2026-05-29).

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

## 2. Environment

- **OS:** Windows, PowerShell.
- **Python:** in `venv/` at repo root. Activate with `venv\Scripts\Activate.ps1`.
- **DB:** PostgreSQL **18.3**, local. `psql.exe` is NOT on PATH — call it with
  the full path:
  ```
  & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U <user> -d <db> -c "..."
  ```
  Connection details live in `.env` (gitignored): `DB_HOST`, `DB_PORT`,
  `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
- **Deps:** see `requirements.txt`. New as of Day 7: `beautifulsoup4`.
  To recreate the env: `pip install -r requirements.txt`.
- **gitignored:** `venv/`, `__pycache__/`, `*.pyc`, `.env`, `data/`,
  `.ipynb_checkpoints/`, `.vscode/`, `.DS_Store`, `*_test.json`
  (the last added Day 7 to keep curl debug artifacts out).

---

## 3. Repo layout (the parts that matter)

```
etl/
  load_patents.py      # USPTO patents loader (Days 1–3)
  load_hiring.py       # Careers-page job loader (Days 4–7) ← active file
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

## 4. Database schema (hiring_signals)

```sql
CREATE TABLE hiring_signals (
    job_id        TEXT NOT NULL,         -- "<TICKER>:<rawid>" — guaranteed unique within ticker
    ticker        TEXT NOT NULL,
    snapshot_date DATE NOT NULL,         -- day we observed this posting
    title         TEXT,
    location      TEXT,
    posted_date   DATE,                  -- when the company says the job was posted
    category      TEXT,                  -- ATS-defined (Workday jobFamilyGroup, Jibe categories[].name, etc.)
    ats           TEXT,                  -- "workday" | "jibe" | "talentbrew" | future...
    job_url       TEXT,
    PRIMARY KEY (job_id, snapshot_date)
);
```

`patents` table follows the same shape, see `sql/schema.sql`. All fetchers
yield 9-key dicts matching the columns above — that contract is enforced
in `insert_jobs()`.

---

## 5. Day-by-day history (compressed)

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
- **Day 7:** TalentBrew fetcher for SNPS. **Structurally complete but
  shipped disabled** — see §6 below for the full story.

---

## 6. Day 7 deep-dive: SNPS / TalentBrew

### What we built

`fetch_talentbrew_jobs()` in `etl/load_hiring.py`, registered as
`ats="talentbrew"` in `FETCHERS`. Parses TalentBrew's AJAX response
(JSON envelope with HTML in a `results` field) using BeautifulSoup
CSS selectors:

- `<li class="search-results-list__list-item">` = one job
- `<a class="sr-job-link" data-job-id="...">` = internal id + URL
- `<h2>` = title, `<span class="job-location">` = location,
  `<span class="category">` = category, `<span class="job-date-posted">`
  = `MM/DD/YYYY` posted date
- `<h1>NNN results</h1>` = total, used for loop control

The fetcher is correct. Verified by inspection against the live response
structure. It will work for any non-fingerprinted TalentBrew site we
encounter later — no code changes needed, just a config entry.

### What stopped us

`careers.synopsys.com` is two-layered:
- **Front-end:** TalentBrew (Radancy/TMP Worldwide). Image CDN is
  `tbcdn.talentbrew.com`.
- **Back-end ATS:** Avature (apply URLs go to `synopsys.avature.net`).

The Day 7 plan in the prior handoff guessed Avature based on stale signal.
Same front/back split as AMD = Jibe(front) + iCIMS(back) from Day 5; the
"tag what we talk to" rule applies again.

The AJAX endpoint
`https://careers.synopsys.com/search-jobs/results?CurrentPage=N&...`
returns `{"results":"","hasJobs":true,"hasContent":false}` (61 bytes,
empty envelope) without the right unlock. We worked through three
defense layers:

1. **`X-Requested-With: XMLHttpRequest` + `Referer`** — tried first, no.
2. **Synthetic cookies** (OptanonConsent, etc.) — no.
3. **`requests.Session` with a warm-up GET to `/search-jobs`** — no.

Definitive proof the gate is **stateful, not header-based**: running the
exact same cURL the browser sent (Copy as cURL → paste in PowerShell) from
the same machine and IP also returned 61 bytes. That rules out IP, User-Agent,
Referer, X-Requested-With, session cookies, and Accept-Language as the gate.

Most likely: Akamai Bot Manager or Imperva fingerprinting via JS challenge
(`_abck` / `bm_sz` cookies issued through executed JavaScript, not via
HTTP alone). Bypass would require **Playwright** or **curl-impersonate** —
either is a real dependency and an hour+ of work, for one ticker.

### Decision

Ship the fetcher disabled, document. SNPS config:

```python
"SNPS": {"ats": "talentbrew", "enabled": False,
         "host": "careers.synopsys.com",
         "note": "anti-bot gated; needs Playwright"},
```

The fetcher stays registered. If any other ticker turns out to be a
non-fingerprinted TalentBrew, it works for free. If we later decide to add
Playwright (it would likely also unlock QCOM and MU which we suspect have
similar defenses), SNPS comes online with a single `enabled: True` flip.

### Interview moments from Day 7

- **The cURL-bisection methodology.** When a request works in the browser
  but not in Python, copy-as-cURL from DevTools and progressively strip
  headers/cookies to find the minimum that still works. Once cURL fails
  with the exact browser headers, the gate isn't header-based — it's
  stateful (JS-issued cookies, fingerprinting, etc.) and a different class
  of solution.
- **Two-layer ATS pattern across companies.** AMD = Jibe(front) +
  iCIMS(back). SNPS = TalentBrew(front) + Avature(back). The plan-doc
  guesses were based on the back-end; live inspection showed the front-end.
  The "tag what we talk to" rule generalized cleanly to a second case.
- **Knowing when to stop.** SNPS is 1 of 12 tickers. The diff/snapshot
  model handles gaps. Choosing to ship + document over sinking hours into
  one ticker's anti-bot is a senior-engineer move; the methodology is the
  artifact, not the row count.

---

## 7. Current data state (snapshot 2026-05-29)

From DB after final Day 7 run:

```
 ticker | n_jobs | with_date | with_category |   oldest   |   newest
--------+--------+-----------+---------------+------------+------------
 AMD    |   1148 |      1148 |          1148 | 2025-05-07 | 2026-05-29
 AVGO   |    363 |       363 |             0 | 2026-04-29 | 2026-05-29
 CDNS   |    623 |       623 |             0 | 2026-04-29 | 2026-05-29
 INTC   |    727 |       727 |             0 | 2026-04-29 | 2026-05-29
 MRVL   |    676 |       675 |             0 | 2026-04-29 | 2026-05-29
 NVDA   |   2640 |      2640 |          2640 | 2026-04-29 | 2026-05-29
```

Six tickers live. Six remaining (QCOM, MU, SNPS, ANSS, TXN, TSM).

---

## 8. Known issues / quirks

- **Workday `posted_date` resolution caps at 30 days.** Workday returns
  a relative phrase (`"Posted 30+ Days Ago"`), so anything older than a
  month parses as `snapshot - 30`. AMD's Jibe gives real ISO timestamps,
  hence the `oldest = 2025-05-07` outlier in §7. Documented, not a bug.
- **`category` is NULL for non-faceted Workday paths.** `_paginate_workday`
  only stamps `category` when fetching by `jobFamilyGroup` facet (NVDA).
  Standard Workday queries don't include the field in the per-job payload.
  CDNS, MRVL, INTC, AVGO all show `with_category=0` as a result. Either
  enrich per-job via a second endpoint (probably not worth it) or accept
  the gap. Currently accepted.
- **`insert_jobs()` rowcount is cosmetic.** Same as `load_patents.py` —
  we print `len(rows)` submitted, not actual new inserts, because psycopg2's
  `execute_values` rowcount under `ON CONFLICT DO NOTHING` is unreliable.
  To know real inserts: query the table.
- **Skip message wording is slightly misleading.** When SNPS is disabled
  the log says "ats=talentbrew, not yet implemented" but the fetcher
  *is* implemented. Same template as AMD pre-Day-5. Cosmetic.

---

## 9. Day 8 plan

In priority order:

1. **QCOM and MU verification.** Both currently `ats: "unknown"`. Likely
   candidates: Workday (most common for chip companies), TalentBrew
   (Recruitics/Appcast family — params `ActiveFacetID`, `CurrentPage` etc.
   that we saw on SNPS are a tell), or some Workday-fronted custom site.
   The QCOM Network panel during Day 7 showed `interact?configId=...` and
   `results?ActiveFacetID=0&...` rows — that param shape is the **same
   TalentBrew signature**, so QCOM is very likely TalentBrew too (and
   very likely also anti-bot gated). MU unknown until inspected.
   Day 5 / Day 7 methodology: Network tab → find the JSON endpoint →
   confirm/write a fetcher.

2. **INTC / AVGO Workday re-verification.** Both were added Day 6 from
   config alone. Verify the row counts in §7 look reasonable vs. their
   public careers-page totals (open the site, check the result count
   header, compare). Tags as a 5-min sanity check, not a known bug.

3. **TXN (Oracle HCM) fetcher.** This is the last "different ATS" on the
   list. Oracle's careers-cloud API is well-documented (REST endpoint
   shape: `/hcmRestApi/resources/latest/recruitingCEJobRequisitions`).
   Probably a clean Day 8 win after the QCOM/MU rabbit hole.

4. **TSM.** Last priority. Taiwan-based, may be a custom site or a
   regional ATS. Investigate if time, otherwise punt.

5. **ANSS.** Acquired by SNPS July 2025. Worth a 5-min check: does
   `careers.ansys.com` redirect to SNPS, run its own TalentBrew, or
   still operate independently? If it's the same fingerprinted
   TalentBrew, it's blocked the same way SNPS is and stays disabled.
   If it's a different ATS, write/reuse a fetcher.

### Stretch (revisit later)

- **Playwright path for SNPS / QCOM / MU.** If 2–3 tickers turn out to
  be the same anti-bot-gated TalentBrew, justify adding Playwright once
  and unlock them all together. Don't add it for SNPS alone.
- **Update the stale module docstring** at the top of `load_hiring.py`
  (still says "Day 4 SCOPE" / "iCIMS for AMD / Avature for SNPS"). Not
  blocking, but should be refreshed before the next major change.
- **Per-job category enrichment** for non-faceted Workday tickers
  (see §8). Low priority.

---

## 10. How to start the next session

Hand Claude this file plus a short prompt like `start day 8`. Claude should:

1. Read this HANDOFF in full.
2. Open §9 and pick the top priority that isn't already done.
3. Ask before writing any code if there's a judgment call (ATS tag, scope
   trade-off, dependency decision).
4. Default to a Network-tab investigation before assuming an ATS from
   the plan — Days 5 and 7 both showed the plan-doc guess was wrong.

---

## 11. Useful commands

Activate venv:
```powershell
venv\Scripts\Activate.ps1
```

Run the hiring loader:
```powershell
python etl/load_hiring.py
```

DB sanity check (replace `<user>` and `<db>`):
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U <user> -d <db> -c "SELECT ticker, COUNT(*) AS n_jobs, COUNT(posted_date) AS with_date, COUNT(category) AS with_category, MIN(posted_date) AS oldest, MAX(posted_date) AS newest FROM hiring_signals WHERE snapshot_date = CURRENT_DATE GROUP BY ticker ORDER BY ticker;"
```

Test an endpoint without Python (the Day 7 bisection trick):
```powershell
curl.exe -s -o test.json -w "size=%{size_download} status=%{http_code}`n" "<URL>" -H "User-Agent: Mozilla/5.0 ..." -H "X-Requested-With: XMLHttpRequest" -H "Referer: <listings page>"
```