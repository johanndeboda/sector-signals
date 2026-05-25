**Last updated:** end of Week 1, Day 6 (Monday, May 25, 2026)
**Project status:** On track. Plumbing week ~92% complete. Hiring ETL live for 6 of 12 tickers.

---

## 0. For next-session Claude: read this first

This document is the single source of truth for resuming the project. The candidate (Johan) will paste this at the start of the next session. Treat sections 1-3 as **non-negotiable context** — they shape *how* you respond, not just *what* you respond about.

**Key operating principle:** Johan drives interpretation, judgment, and business decisions. Claude drives plumbing, syntax, multi-step pipelines, and debugging. **Never write code Johan won't read.** When sending scripts, explicitly flag 2-3 sections worth focusing on; mark the rest as skim-only.

**This is a fresh rewrite of the handoff** (previous version ended at Day 3 with a Day 4 section appended). Days 4 and 5 are now folded into the main body. Structure and voice are unchanged so it stays consistent with how the project has been run.

---

## 1. Candidate background (Johan)

- **Year/major:** 2nd-year MIS major (Management Information Systems)
- **Programming experience:** "Slight" — can follow code logic from structure, doesn't know every library detail. Has working comfort with Python at the level of "I can see what a script is doing even if I don't recognize every function call." **This is the realistic baseline — don't overestimate or underestimate.**
- **Setup:** Dell XPS 15, Windows 11, VSCode as primary editor, PowerShell terminal, Postgres 18 installed locally
- **Domain context:** Has done consulting work on Cadence (CDNS) — has real knowledge of the EDA/semiconductor industry landscape. Don't talk down on semi-industry concepts; he knows the players and the business models.
- **Career goal:** Job search starting late 2026 (Aug-Dec). Sector Signals is portfolio centerpiece. Target roles: analyst-track positions where defending a data project in a 45-min interview is the bar.

### Working style preferences (observed across sessions)

- **Asks meta-questions about the work itself.** "Is this worth memorizing?" "Should I look through the code?" "Should I read the earlier message first?" These signal he's actively calibrating his learning approach. Take them seriously — they're not stalling, they're optimizing.
- **Wants reasoning, not just answers.** When Johan asks "why?" he means it. Brief explanations with concrete tradeoffs land better than hedged both-sides answers.
- **Prefers being given a recommendation when uncertain.** Asks "what's your recommendation?" rather than "give me options." When he says he's not sure, give a clear pick with reasoning — don't fence-sit.
- **Asks for "very briefly" when he just wants the answer.** Honor the request — give the short version first, then add context only if it serves him.
- **Reads code at "shape and logic" level, not line-by-line.** This is the correct level for a 2nd-year MIS student. Don't push for more rigor than the task requires; trust that repetition across the project locks in patterns.
- **Will paste error messages or terminal output for debugging.** Read carefully — every line matters. Identify the root cause before suggesting fixes. (On Day 5 he pasted SQL into PowerShell and got a `CommandNotFoundException` — the lesson there is that he may not always know which environment a command belongs in. Spell it out: "this goes in psql, not PowerShell.")
- **Honest about gaps.** Will say "not sure," "explain again," or "you are supposed to guide me." When this happens, slow down — don't pile on more material until the prior thing clicks. **He expects Claude to lead on planning** (e.g. "what is Day 6") rather than asking him to define the work.
- **Can be overwhelmed by long multi-part answers.** On Day 5 he explicitly said Claude was giving "so much information." Default to one step at a time. Don't dump the whole plan; give the next action, wait, then continue.

### Communication norms

- Plain prose works fine. Don't over-format with headers for simple replies.
- Markdown tables are good for tradeoff comparisons and decision matrices.
- Avoid emoji unless he uses them first.
- He's a good sport about mistakes (his or Claude's). Don't grovel over typos; acknowledge briefly and move on.
- Has a sense of humor but the project is serious work — match tone to context.
- **One question at a time.** When elicitation is needed, ask a single clear thing, ideally with `ask_user_input_v0`. Several questions at once causes friction.

---

## 2. Project elevator pitch

**Sector Signals** is a Postgres-backed analytical project tracking 12 US-listed semiconductor companies (the "semi 12") across four data dimensions: financials, patents, hiring signals, and qualitative news. The deliverable is a defensible, well-instrumented analytical project that supports a job search in late 2026 — something Johan can defend in 45-minute case interviews.

**The "semi 12":** AMD, ANSS, AVGO, CDNS, INTC, MRVL, MU, NVDA, QCOM, SNPS, TSM, TXN.

**Time window:** patents and financials cover 2021-01-01 → present (5 years). Hiring is snapshot-forward only (today onward — see §6).

**Why these 12:** EDA (CDNS, SNPS, ANSS), GPU/AI (NVDA, AMD), wireless/IP-licensing (QCOM, AVGO, MRVL), CPU/IDM (INTC), memory (MU), analog/embedded (TXN), foundry (TSM). Covers the major business models in semis.

---

## 3. Working approach — non-negotiable principles

**Candidate drives on:** hypotheses, interpretation, business judgment, decisions about what to include/exclude, validation of outputs, picking which observations are interview-worthy.

**Claude drives on:** boilerplate code, SQL syntax, library quirks, multi-step pipelines, debugging plumbing, **and planning the next session's scope** (Johan expects Claude to propose what each day's work should be).

### Code-reading discipline (very important)

Johan reads every script before running it. Not line-by-line — at "what is this trying to do?" level, 5-10 min per script. **When generating code:**
- Add docstrings explaining the script's job
- Use section comments to break up logic
- Inline-comment any non-obvious choice or judgment call
- At the end of the response, explicitly flag 2-3 sections worth focused reading + 1-2 patterns the candidate will see again
- Mark pure plumbing as "skim only" so he doesn't waste effort

### Decision-making pattern

When a choice involves judgment, do this:
1. State the tradeoff briefly
2. Recommend a default with reasoning
3. Use `ask_user_input_v0` for the actual decision — let Johan choose with eyes open
4. If he says "your recommendation" or "I'm not sure," then *commit* to a pick with reasoning. Don't kick it back.
5. If he asks "what do the options even mean," explain plainly before re-asking — don't assume the choice is self-evident.

### Interview-moment framing

When the project surfaces something analytically interesting (a surprising number, a methodology choice, an anomaly, a lesson learned), name it explicitly as "interview-worthy" and draft 1-2 sentences he could use. The `interview_moments.md` file in the repo accumulates these. Suggest entries when relevant. **At the end of every session, run the end-of-day routine in §16** — the day summary plus drafted interview moments are produced then, as a standing habit, not something Johan has to remember to ask for.

---

## 4. Tech stack & environment

- **OS:** Windows 11 on Dell XPS 15
- **Editor:** VSCode (Python extension installed, venv auto-detected)
- **Terminal:** PowerShell (not WSL — decided against on D3; revisit if it becomes painful)
- **DB:** Postgres 18, local, port 5432, database name `sector_signals`, user `postgres`
  - Binary path: `C:\Program Files\PostgreSQL\18\bin\psql.exe`
  - PATH is **still not configured** — must use the full path to call `psql`. To run SQL from PowerShell:
    `& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d sector_signals -c "<SQL>"`
  - Note: raw SQL pasted directly into PowerShell will fail — it must go through `psql` or a GUI client.
- **Language:** Python 3.x in venv at project root (`venv\Scripts\Activate.ps1`)
- **Key libraries:** pandas, psycopg2-binary, sqlalchemy, requests, python-dotenv, yfinance
- **DB connection:** loaded from `.env` via python-dotenv. `load_financials.py` uses SQLAlchemy; `load_patents.py` and `load_hiring.py` use psycopg2 directly. Both styles fine.

### Critical environment notes

- DB password was rotated on D3. Connection verified working since.
- `.gitignore` correctly excludes `data/` and `.env`. Verified clean.
- **`requirements.txt` has a double extension on disk: `requirements.txt.txt`.** Almost certainly a Windows "Save As" slip. Minor, but rename to `requirements.txt` so the reproducibility steps and any `pip install -r` work without surprise.

---

## 5. Folder structure (as of D5)

```
sector-signals/
├── etl/
│   ├── load_financials.py        ← Day 1: yfinance → Postgres (SQLAlchemy)
│   ├── edgar_backfill.py         ← Day 2: SEC EDGAR XBRL → Postgres
│   ├── download_patents.py       ← Day 3: streaming downloads with resume support
│   ├── explore_assignees.py      ← Day 3: throwaway exploration tool — safe to delete
│   ├── assignee_mapping.py       ← Day 3: 95 org-name variants → 12 tickers
│   ├── load_patents.py           ← Day 3: 4-way TSV join → patents table
│   ├── detect_ats.py             ← Day 4: throwaway ATS-fingerprinting diagnostic
│   ├── load_hiring.py            ← Day 4-5: config-driven multi-ATS hiring loader
│   ├── load_hiring.day4.bak      ← Day 5: backup of pre-Jibe version — delete once D5 confirmed stable
│   ├── test_bulk_download.py     ← small test script (Day 3 era)
│   └── __pycache__/
├── sql/
│   └── schema.sql                ← all CREATE TABLE DDL
├── data/                         ← GITIGNORED, holds 4 patent TSVs (~1.7 GB)
├── notebooks/                    ← (empty / exploratory — Week 2 will populate)
├── venv/
├── .env                          ← DB credentials (gitignored)
├── .env.example                  ← template for .env
├── .gitignore
├── requirements.txt.txt          ← ⚠ double extension, rename to requirements.txt
├── interview_moments.md          ← running log of analytical findings
├── README.md
└── HANDOFF.md                    ← this file
```

Note: there are a few non-hiring loaders (`load_financials.py`, `edgar_backfill.py`) and Day-3 patent scripts. The Day 4 handoff mentioned a `load_companies.py`; no such file is on disk — companies were likely loaded via one of the existing scripts or directly. Treat the companies table as already populated and stable.

---

## 6. Database state (as of D5)

### Schema (`sql/schema.sql`)
- `companies (ticker, name, country, ...)` — 12 rows, all semi-12 tickers present
- `financials_quarterly (ticker, quarter, revenue, rd_spend, net_income, operating_margin)` — composite PK `(ticker, quarter)`
- `stock_prices_daily (ticker, trade_date, open, high, low, close, volume)` — composite PK `(ticker, trade_date)`
- `patents (patent_id PK, assignee_ticker FK→companies, grant_date, title, cpc_class, inventor_count)` — **61,519 rows**
- `hiring_signals (job_id, ticker, snapshot_date, title, location, posted_date, category, ats, job_url)` — composite PK `(job_id, snapshot_date)`. Same posting captured on different days = multiple rows, which lets us measure "days a job stays open" via `MAX - MIN`. Hiring is **snapshot-forward only** — historical hiring before the first run is not reconstructible.

### Per-ticker patent counts (sanity-check reference)

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
| **AVGO** | **350** | 🚩 ANOMALY — investigate Week 2 |
| ANSS | 132 | Acquired by SNPS July 2025 |
| **Total** | **61,519** | |

### Hiring signal counts (as of D6 run — verified in DB)

| Ticker | Count (D6) | ATS | Notes |
|---|---|---|---|
| NVDA | ~2,623 | Workday | Faceted on `jobFamilyGroup` to beat the 2000 cap |
| MRVL | ~656 | Workday | category NULL |
| CDNS | ~625 | Workday | category NULL |
| AMD | ~1,170 | Jibe | Exact ISO posted_date |
| INTC | ~743 | Workday | NEW on D6 — straight pagination, no cap |
| AVGO | ~380 | Workday | NEW on D6 — transient ConnectionError on first run, recovered via re-run |

Counts are per-snapshot and drift daily — `hiring_signals` is a forward-accumulating snapshot table. QCOM and MU are stubbed `ats="unknown"` (not Workday — see §8). SNPS, ANSS, TXN, TSM still stubbed.

## 7. What we built on Days 1-4 (carried forward)

### Days 1-3 — financials, EDGAR, and the patents pipeline
- **D1:** `load_financials.py` — yfinance → Postgres (companies + financials).
- **D2:** `edgar_backfill.py` — SEC EDGAR XBRL backfill; `schema.sql` created.
- **D3:** Four-script patents pipeline — `download_patents.py` (streaming bulk TSV downloads with resume), `explore_assignees.py` (throwaway discovery tool), `assignee_mapping.py` (95 org-name variants → 12 tickers), `load_patents.py` (4-way TSV join → 61,519 patents). Runtime ~22 min.

### Day 4 — Hiring signals ETL (Workday)
- `hiring_signals` table added to `schema.sql`.
- `etl/load_hiring.py` built as a **config-driven multi-ATS loader.** Each ticker has a config entry declaring its ATS platform; non-Workday entries were `enabled=False` stubs.
- `etl/detect_ats.py` — throwaway diagnostic that fingerprinted each careers site to identify its ATS.
- Ran 3 tickers (NVDA, CDNS, MRVL — confirmed Workday tenants).
- **The NVDA cap problem (biggest D4 learning):** Workday's job-search API silently caps `total` at 2000. NVDA returned exactly 2000 and the team almost shipped that. Fix: query per-facet and union. NVIDIA's tenant exposes no location facet, so faceting is done on `jobFamilyGroup` — which also populates `category` for free. Real NVDA total = 2,639 on D4 (2,655 on the D5 re-run).

### Patterns Johan has seen repeatedly (worth reinforcing)
- Substring for exploration, exact-match for production.
- Filter early, join late.
- Idempotency via `ON CONFLICT DO NOTHING` — every loader is safe to re-run.
- `nunique` vs `count` — distinct entities vs total rows.
- Streaming downloads + `.part` files for resumable, flat-memory fetches.

---

## 8. What we built on Day 5 (full detail) — Hiring ETL, AMD via Jibe

### The headline: the Day 4 plan said "iCIMS for AMD" — reality was more nuanced

The D4 plan listed AMD as an iCIMS site. On investigation, AMD's public careers site (`careers.amd.com`) had **migrated to a Jibe-fronted portal.** iCIMS is still the back-end ATS — every job record in the feed has `ats_code: "icims"` and an `apply_url` on `*.icims.com` — but the **public job listings are served by Jibe's own API**, not the classic iCIMS portal.

Decision made with Johan: target the **Jibe job feed**, because that is the source of truth for what AMD actually advertises publicly. The handler is tagged `ats="jibe"` (accurate to what the fetcher talks to), not `"icims"` (which would have been a stale label driving the data).

### What got built / changed in `load_hiring.py`

Four edits, ~140 lines added:

1. **AMD config entry** — flipped to `enabled: True`, `ats: "jibe"`, with `host: "careers.amd.com"` and an inline comment explaining the iCIMS-vs-Jibe situation.
2. **`fetch_jibe_jobs(ticker, cfg)`** — new fetcher. Hits `GET https://careers.amd.com/api/jobs?page=N&sortBy=relevance&descending=false&internal=false`, paginates by `page` (1-indexed, 10 jobs/page), and yields the same 9-key dict the Workday fetcher produces. Has a `JIBE_MAX_PAGES` safety ceiling.
3. **`FETCHERS` registry** — maps `ats` name → fetcher function (`{"workday": ..., "jibe": ...}`).
4. **`main()` dispatch fix** — see the architecture note below.

### Architecture note — the D4 handoff slightly overclaimed

The D4 handoff said "adding a platform is one new fetcher function, not a rewrite." That wasn't quite true: D4 had hardcoded `fetch_workday_jobs()` directly inside `main()`, so there was no dispatch layer — adding a platform would have meant editing `main()`. The D5 `FETCHERS` registry fixes this. **Now the claim holds:** the next platform genuinely is one new function + one registry line.

### Why no faceting workaround was needed for AMD

Unlike NVDA's suspicious 2000 cap, AMD's API returns a well-defined `totalCount` (1291) and the facet counts sum cleanly. Straight pagination returns the full set. The `JIBE_MAX_PAGES` ceiling exists only as a runaway guard.

### Verified

Syntax checked; transform tested offline against the real API response shape; then run live on Johan's machine. DB confirmed **AMD = 1,291 rows**, matching the API's `totalCount` exactly. End-to-end success.

### Interview moments from Day 5 (add these to `interview_moments.md`)

1. "AMD's careers plan said 'iCIMS' — but mid-build I found AMD had migrated to a Jibe-fronted careers site. The ATS label in the project config no longer matched reality. Verified the actual endpoint before writing the fetcher rather than trusting the plan."
2. "Jibe's posted_date is a real ISO timestamp — much higher quality than Workday's relative phrasing ('Posted 30+ Days Ago'). AMD's hiring data has precise posting dates; the Workday tickers don't."
3. "Refactored the loader to a fetcher registry so the original 'add a platform = one function' design goal actually became true — the Day 4 version still had the dispatch hardcoded."

### Known data-quality notes for hiring (carried forward + new)

- **Workday `posted_date` is approximate** — "Posted 30+ Days Ago" collapses to exactly 30 days. ~30% of Workday postings imprecise. AMD/Jibe postings, by contrast, have exact dates.
- **"N Locations" strings** appear in the Workday `location` column when a posting spans >5 cities. Not present in the AMD/Jibe data (Jibe gives a clean `full_location`).
- **CDNS and MRVL have NULL `category`** — never faceted, no classifier run yet.
- The `insert_jobs` function returns `len(rows)` not `cur.rowcount` — this sidesteps the same batched-insert rowcount bug noted for `load_patents.py` (see §10). "Submitted" counts rows sent to INSERT, not new rows after `ON CONFLICT` skips.

---

## 8b. What we built on Day 6 — enable INTC + AVGO

Config-only day, no new code. The Day 4 plan listed QCOM, INTC, AVGO, MU as "suspected Workday." Verified each against its live careers page:

- **INTC** — Workday. `intel.wd1.myworkdayjobs.com`, tenant `intel`, site `External`. Enabled. Straight pagination, total ~743, no 2000-cap issue.
- **AVGO** — Workday. `broadcom.wd1.myworkdayjobs.com`, tenant `broadcom`, site `External_Career` (singular — NOT `External_Careers`, which is CDNS). Enabled. First run hit a transient `ConnectionResetError`; idempotent re-run completed it cleanly (~380 rows).
- **QCOM** — NOT Workday. `careers.qualcomm.com` self-hosted/Appcast-style portal (pid + sort_by params). Stubbed `ats="unknown"`, disabled. Needs its own fetcher.
- **MU** — NOT Workday. `careers.micron.com`, same portal pattern as QCOM. Stubbed `ats="unknown"`, disabled. Needs its own fetcher.

Result: hiring data live for 6 of 12 tickers. The "suspected Workday" four split 50/50.
---

## 9. Judgment calls on Day 3 (still must defend in interviews)

Unchanged from prior handoff — kept here for completeness:

1. **AVGO includes pre-2016 Avago Technologies entities** (legal continuity under the AVGO ticker post-merger).
2. **INTC excludes loose "intel" substring matches** (16,000+ false positives like "AT&T Intellectual Property"). Exact names only.
3. **ANSS kept in schema despite July 2025 Synopsys acquisition** — treated as a "company that disappeared mid-window" case study.
4. **MRVL lumps all 14 legal entities as one bucket** (pre-2018 IP-holding structure).
5. **MU includes the typo "Micron Technology, lnc."** (lowercase L — feed data-entry error).
6. **TSM includes a garbled "TAIWAN SEMICONDUCTOR MTAIWANANUFACTURING..." string** (feed corruption, real filing).
7. **Co-assignee deduplication** — 108 patents with ≥2 of our tickers get one ticker deterministically.
8. **Inner join for patent metadata** (drop rows with no grant_date); left join for CPC (NULL class is fine).
10. **QCOM and MU are not on Workday despite the plan's "suspected Workday" label.** Both run a non-Workday `careers.{company}.com` portal (Appcast-style). Tagged `ats="unknown"` and disabled rather than forced into a wrong label — same discipline as the AMD/Jibe call (#9).

### Day 5 judgment call (new)

9. **AMD hiring data is sourced from the Jibe public feed, not the iCIMS back-end API**, and tagged `ats="jibe"`. Rationale: the Jibe feed is what AMD shows the public; it's the correct source of truth for "what is AMD hiring for." The iCIMS label from the original plan describes the back-end applicant-tracking system, not the public listing layer.

---

## 10. Open questions / TODO

| Item | Status | Notes |
|---|---|---|
| **AVGO patent count anomaly** | 🚩 Open from D3 | Only 350 patents in window — implausibly low. Likely a post-2021 IP-holding entity missing from `assignee_mapping.py`. Investigate Week 2. |
| Q4 financials gap (10-K vs 10-Q) | Open from D2 | Q4 financials live in 10-K filings; EDGAR script only pulls 10-Q. Fix Week 2. |
| `requirements.txt.txt` double extension | New, trivial | Rename to `requirements.txt`. |
| Delete `load_hiring.day4.bak` | New cleanup | Backup of pre-Jibe loader. Safe to delete now that D5 is verified — or keep one more session, then remove. |
| `cur.rowcount` logging bug in `load_patents.py` | Cosmetic | After batched `execute_values`, `cur.rowcount` only reports the last batch. `load_hiring.py` already avoids this by logging `len(rows)`; `load_patents.py` still has it. Fix when convenient. |
| Add Postgres `bin` to PATH | Quality-of-life | Lets you call `psql` without the full path. 60-second fix. |
| Delete `explore_assignees.py` | Cleanup | Throwaway D3 exploration script. Remove in a Week 2 cleanup pass. |
| CDNS / MRVL NULL `category` | Open | Needs a keyword classifier, or fold into a later pass. Deferred from D4 and D5. |
| Co-assigned patents | Logged, not analyzed | 108 patents with ≥2 of our tickers as co-assignees. Possible Week 3 sidebar. |

---

## 11. Roadmap (remaining)

### Week 1 — plumbing (current, ~85% done)
- ✅ D1: Postgres + companies + financials loader
- ✅ D2: EDGAR backfill + patents schema
- ✅ D3: Patents ETL end-to-end
- ✅ D4: Hiring ETL — Workday handler, 3 tickers (NVDA, CDNS, MRVL)
- ✅ D5: Hiring ETL — Jibe handler, AMD enabled; fetcher-registry refactor
- ✅ D6: Hiring ETL — INTC + AVGO enabled (Workday); QCOM + MU found non-Workday
- ⏭ D7 (next session): SNPS hiring fetcher — Avature ATS (new fetcher, like Jibe). ANSS may roll in (Synopsys acquired it).
### Week 2 — analytical layer
- Reusable SQL views (e.g. `v_patents_quarterly`, `v_hiring_by_ticker`)
- First exploratory notebook: cross-source correlation checks
- Re-investigate AVGO patent gap
- Fix Q4 financials gap by parsing 10-Ks
- Cleanup pass: delete throwaway scripts, fix `requirements.txt` name
- **Write-it-yourself exercise:** have Johan write one small piece of code entirely himself (a SQL view is a good candidate) — Claude explains the approach, Johan writes it, Claude only reviews. See §16 for why. One or two reps is enough.

### Week 3 — first analyses
- 3-5 driving analytical questions with clean charts
- Cross-source observations (e.g. "do hiring spikes precede patent surges?")

### Weeks 4-6
- Claude API integration for news summarization
- Comparative analyses across tickers
- GitHub Actions for nightly refresh (all loaders idempotent — designed for this)
- Public-ready write-up + portfolio README

### Remaining ATS handlers (one per future day, after D6)
- **SNPS — Avature.** Needs a new fetcher (like the Jibe work). ANSS may roll in here since it was acquired by Synopsys.
- **TXN — Oracle HCM.** Needs a new fetcher.
- **TSM — unknown ATS.** Needs investigation first (run `detect_ats.py` or the Network-tab method), then a fetcher.

---

## 12. Next session plan (Week 1 Day 6) — START HERE

## 12. Next session plan (Week 1 Day 7) — START HERE

**Theme:** SNPS hiring fetcher — Synopsys is on **Avature**, a different ATS needing a brand-new fetcher (like the Day 5 Jibe work, not config-only).

**Why this is next:** the remaining stubbed tickers (QCOM, MU, SNPS, ANSS, TXN, TSM) all need new fetchers. SNPS is the cleanest start — Avature is a well-documented ATS, and ANSS likely rolls in since Synopsys acquired it (its careers may now sit under the Synopsys Avature tenant).

**Plan (~2 hrs):**
1. Verify SNPS's careers page is Avature; read the endpoint (Network tab, like D5).
2. Write `fetch_avature_jobs()` — new fetcher, add to the `FETCHERS` registry (one function + one line, per the D5 architecture).
3. Check if ANSS is reachable via the same Synopsys tenant.
4. Run, verify in DB, end-of-day routine.

This is a code day, not a config day — budget reading time for the new fetcher.
---

## 13. Reproducibility checklist (for "rebuild from scratch" scenarios)

1. Clone repo
2. `python -m venv venv && venv\Scripts\Activate.ps1`
3. `pip install -r requirements.txt` (fix the `.txt.txt` filename first)
4. Create `.env` from `.env.example`
5. `& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d sector_signals -f sql/schema.sql`
6. `python etl/load_financials.py`
7. `python etl/edgar_backfill.py`
8. `python etl/download_patents.py` (~15 min download)
9. `python etl/load_patents.py` (~22 min load) — verify `SELECT COUNT(*) FROM patents;` ≈ 61,519
10. `python etl/load_hiring.py` (~2-3 min; AMD section alone is ~1 min) — verify per-ticker counts in `hiring_signals`

Note: hiring counts will differ from the figures in §6 on any later run, because job postings change daily. That's expected — `hiring_signals` is a forward-accumulating snapshot table.

---

## 14. Specific behaviors next-session Claude should NOT do

- ❌ Don't write code without flagging which sections matter to read. Johan will read everything otherwise — wastes 30-50 min.
- ❌ Don't fence-sit when Johan asks for a recommendation. If he says "your call," pick one with reasoning.
- ❌ Don't ask multiple clarifying questions at once. One at a time.
- ❌ Don't dump a whole multi-step plan in one message. Give the next step, wait, continue. (Johan flagged "so much information" on D5.)
- ❌ Don't use `ask_user_input_v0` for things Johan has already told you, or re-ask a question he hasn't actually answered yet (a tool may echo a selection back — confirm he really chose).
- ❌ Don't assume Johan knows which environment a command belongs to. Say explicitly "this is SQL, run it in psql" vs "this is a PowerShell command."
- ❌ Don't make Johan define the next day's scope — he expects Claude to propose it. Bring a plan; let him approve or adjust.
- ❌ Don't lecture about discipline more than once per issue.
- ❌ Don't predict runtimes too precisely. Give ranges.
- ❌ Don't bury the lede. When Johan asks "very briefly," answer in sentence 1.
- ❌ Don't write placeholder paths Johan will run verbatim. Use real paths or make the placeholder obvious.

---

## 15. Things to do BEFORE next session (Johan)

- ⏭ Commit Day 5 work: `git add etl/ HANDOFF.md interview_moments.md && git commit -m "Week 1 Day 5: Hiring ETL — AMD via Jibe, fetcher registry" && git push`
- ⏭ Add the three Day 5 interview moments to `interview_moments.md` (text in §8).
- ⏭ (Optional, trivial) Rename `requirements.txt.txt` → `requirements.txt`.
- ⏭ (Optional) Delete `etl/load_hiring.day4.bak` now that D5 is verified.
- ⏭ (Optional) Add `C:\Program Files\PostgreSQL\18\bin` to PATH.

---

## 16. End-of-day routine (do this every session — Johan + Claude)

This is a **standing routine**, added on Day 5. Run it at the close of every working session, before committing. Its purpose: make sure the day's learning and progress are captured *while they're fresh*, since the project's memory lives entirely in these files — nothing carries over between sessions otherwise.

### Claude's job — produce an end-of-day summary

When Johan signals the session is wrapping up (or asks for the summary), Claude writes a short **Day Summary** with three parts:

1. **What got done** — 2-4 bullets, plain language. The concrete deliverables of the day.
2. **Interview moments** — drafted in *Johan's voice*, in the *situation → finding → action → lesson* shape, ready to paste into `interview_moments.md`. **Every moment must end with an explicit `Lesson:` line** — that single sentence is the interview-grade takeaway and the entries that lack one are the weak ones.
3. **What's next** — one line: what the next session's first task is.

Keep the summary tight. It is a recap, not a re-explanation — Johan was there for the work.

### Johan's job — update the logs

At end of day, Johan:
- Pastes the interview moments into `interview_moments.md`, **rewriting in his own words** if Claude's draft sounds like transcript rather than his voice. (Observed risk: Day 5's entry was pasted verbatim from chat and reads like a transcript with a leftover instruction-to-self in it. Own-voice + a `Lesson:` line is the standard.)
- Commits the day's work (code + `HANDOFF.md` + `interview_moments.md`).

### Notes on `interview_moments.md` format

- The strong existing entries (Day 2's API pivots, Day 3's Marvell-entities note) follow *situation → finding → action → lesson*. That is the template — match it.
- The file currently repeats `## Week 1` as a header six times. Minor, but a single `## Week 1` with `### Day N` subheadings underneath would read cleaner as it grows. Tidy when convenient.
- Halfway through the project and at the end, this file is what Johan rereads to reconstruct the whole arc — for his own memory and for "walk me through what you learned" interview questions. It only works if every day gets an honest entry with a real lesson line.

### On the learning-vs-reading question (raised Day 5)

Johan noted he's reading code fluently but not writing it from scratch, and asked if that's okay. For his target analyst-track roles it is — reading-level fluency to *defend* the pipeline is the actual goal. But it was agreed that **somewhere in Week 2-3 he should write one small piece entirely himself** (e.g. a SQL view or a small filter function): Claude explains the approach, Johan writes the code, Claude only reviews. The point is crossing once or twice from "I recognize this" to "I made this" so the understanding is load-bearing. Flagged here so a future session actually schedules it — see Week 2 in §11.

---

## Appendix — Suggested commit message for Day 5

```
Week 1 Day 5: Hiring ETL — AMD via Jibe + fetcher registry

- Discovered AMD's careers site migrated to a Jibe front-end;
  iCIMS remains the back-end ATS but Jibe serves public listings
- Add fetch_jibe_jobs() targeting careers.amd.com/api/jobs
- Add FETCHERS registry; main() now dispatches by ats name
  (Day 4 had the Workday fetcher hardcoded)
- AMD enabled: 1,291 postings loaded, matches API totalCount
- 7 non-Workday/Jibe tickers still stubbed
```

---

**End of handoff. Next session: paste this entire document at the start of the new chat. Day 6 = enable QCOM, INTC, AVGO, MU (Workday config only).**