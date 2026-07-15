# HANDOFF.md — Sector Signals

*Last updated: Day 15 session (2026-07-15). Cross-signal notebook (`20_cross_signals.ipynb`) **complete** — three cuts landed (hiring tilt independent of financial ratios; role mix tracks business model; AI-titled hiring share by ticker). Committed `e1352a0`, pushed. **Dashboard de-risk spike RESOLVED and the architecture changed:** Tableau Public cannot connect to PostgreSQL by design — the path is now Neon → GH Actions → Google Sheet → Tableau Public (24h auto-refresh). Power BI evaluated and rejected for this phase. Appendices A–H hold reusable code/SQL/analysis so nothing here requires re-reading old chats.*

---

## §0 — How to use this handoff
- Johann pastes this at the start of each session; Claude reads it **fully** before acting.
- Claude opens by confirming state, naming any scope trade-offs **with a recommendation**, then works **one step at a time**.
- Claude closes each session with a day summary + drafted interview moments, unprompted.
- **Verify live state — don't trust this doc blindly.** The pipeline runs daily and tables change; a quick DB check (snapshot series, row counts) beats assuming. This doc has been stale before (it once claimed patents/financials weren't built; on Day 15 it claimed a notebook cell had been removed that hadn't been).
- **What Claude can and cannot do (corrected Day 15 — the old blanket "no network" line was wrong):**
  - **CAN:** web-search and fetch pages; read files attached to the chat or present in the Project tab; run Python/bash in its own sandbox.
  - **CANNOT:** reach Neon, run Johann's notebooks, or see his working directory. Claude writes cells/commands; Johann runs them and pastes output; Claude iterates.
  - **Practical rule:** any claim about a product, version, price, or recruiting timeline should be **searched, not recalled**. Day 15 caught three cases where recall would have been wrong (Tableau Public's connectors, Power BI's free-tier publishing, Marvell's business mix).

**How to WRITE the next handoff (same way every time):** re-read the current `HANDOFF.md` in full and **diff against it — never rebuild from memory** (a dropped-content incident established this rule; Day 15 re-read the on-disk file in four chunks before writing). Update the dynamic sections (§4 when repo changes, §6 data state, §9 progress log — append the new day, §10 roadmap, §12 open items, §13 next-session). Preserve and keep current the static sections (§0–§3, §5, §7, §8, §11 principles — append, don't trim). Keep `[CONFIRM]` markers honest. Never over-sharpen prior findings (§5.10). Record mistakes so they aren't repeated — **including Claude's** (§9 Day 15 logs one). Keep the section structure identical session to session. Johann replaces the repo's `HANDOFF.md` with the new version and commits it.

## §1 — Project purpose & thesis
Sector Signals is a portfolio data-engineering + analytics project to land a **data/business analyst internship** (target: **Summer 2027**). Core thesis: **hiring patterns, patent activity, and financial signals surface strategic shifts before they show up in earnings** — anchored in AI's reshaping of the semiconductor industry.
- **12 tickers:** 9 hiring-active (AMD, AVGO, CDNS, INTC, MRVL, MU, NVDA, QCOM, TXN) + SNPS, ANSS, TSM (seeded, hiring-inactive).
- **Recruiting:** Wave 1 = July–Oct 2026 (primary, **live now**); Wave 2 = Dec 2026–Feb 2027.
- **Repo:** github.com/johanndeboda/sector-signals
- **AI framing guardrail:** AI is the narrative backdrop, not a proven cause. Data can show *timing/correlation* aligned with the AI buildout — **never causation** (see §5.10).

### §1a — The 12 tickers at a glance (reference)
**Fabless** (design chips, outsource fab to TSMC):
- **NVDA (Nvidia)** — GPUs + CUDA software moat; dominant AI/datacenter accelerator. Highest *absolute* R&D ($5.5B) but *lowest* intensity (8.1%) because revenue outran it; margin ~65%.
- **AMD** — CPUs (Ryzen/EPYC) + GPUs (Instinct) + Xilinx adaptive SoCs; ROCm software stack chasing CUDA. Intensity 23.4%, margin 14.4%.
- **QCOM (Qualcomm)** — mobile SoCs (Snapdragon) + wireless/modem IP + automotive; on-device AI SDKs. Intensity 23.2%, margin 21.8%.
- **AVGO (Broadcom)** — networking + custom ASICs/XPUs for hyperscalers + high-margin infra software (VMware). Intensity 15.4%, margin 44.3%.
- **MRVL (Marvell)** — data-infra silicon (networking, storage, custom AI compute, optical DSPs/SerDes). Intensity 24.2%, margin 18.7% (but negative through much of 2022–24; see §9).

**IDM** (design *and* own fabs):
- **INTC (Intel)** — leading-edge logic (x86 CPUs) built in-house, mid-turnaround. High intensity (24.9%), thin margin (6.9%).
- **MU (Micron)** — memory (DRAM/NAND/HBM); competes on capex, not R&D-per-dollar. Lowest intensity (5.2%), highest *snapshot* margin (67.6%) — but cyclical (§9).
- **TXN (Texas Instruments)** — analog & embedded, huge catalog, owns fabs. Low intensity (10.6%), durable margin (37.8%).

**EDA** (software to design chips — Johann's Cadence turf):
- **CDNS (Cadence)** — design/verification software + IP. R&D *is* the product → **highest** intensity (34.5%), margin 29.3%.

**Inactive:** SNPS (Cadence's larger EDA rival; TalentBrew anti-bot) · ANSS (simulation; acquired by Synopsys, data ends Q1'25) · TSM (leading pure-play foundry; anti-bot + reports in TWD).

*(Fabless = design only; IDM = design + own fabs; EDA = design software; Foundry (TSM) = manufactures others' designs. Logic = "thinking" chips that compute; memory = stores data; analog = senses/controls the physical world. "Leading-edge logic" = compute chips on the smallest, most capital-intensive process nodes — INTC's cost problem.)*

*(Note: the intensity/margin figures above are the `10_financials` snapshot values, computed on each ticker's latest single quarter. The cross-signal notebook `20` uses a **trailing-4-quarter (TTM)** recompute for the join, so its per-ticker intensity/margin differ slightly — different metric, both correct. See §9 Day 14 and Appendix G.)*

**⚠ §1a figures are `10_financials` snapshot values and are NOT auto-updated.** They are point-in-time as of Day 13. Do not paste them into public prose without re-checking against the live table (§5.11). This is the same class of staleness §7's date-stamp rule exists to prevent.

### §1b — Business-model axis (HYPOTHESIS, Day 15 — not a finding)
An unproven framing that fits the `ai_pct` ordering but is **not established by this project's data**. Do not present as a result.
- The top-three AI-titled hirers (NVDA 18.7, QCOM 15.4, AMD 12.2) each sell a **developer-facing software platform** on top of silicon (CUDA / Snapdragon AI SDKs / ROCm).
- The bottom-two fabless (AVGO 3.0, MRVL 1.3) sell **custom silicon to a handful of hyperscalers** whose own engineers do the AI work.
- MU is the same shape from the IDM side: HBM is arguably the most AI-levered product in the panel, and memory hiring is process/fab engineering.
- **Proposed axis:** *sells an AI platform* vs. *sells hardware someone else's AI runs on*.
- **Why it stays a hypothesis:** testing it needs an AI-exposure measure independent of hiring language. The schema has no segment revenue and no AI-specific field. See §9 Day 15 for how a stronger version of this claim was tried and **refuted by Johann's own data**.

## §2 — Domain foundation
Prior consulting engagement with **Cadence Design Systems** via the SJSU Marketing Association: competitive analysis, careers-page audits, Generative Engine Optimization (GEO) analysis. Direct narrative thread — CDNS is one of the 12 tickers, and the planned AI insight layer ties back to the GEO work.

## §3 — Environment & stack
- **OS/shell:** Windows 11, PowerShell (flag PS vs Python vs SQL explicitly in commands).
- **Editor:** VS Code; notebooks run in VS Code Jupyter.
- **Python:** 3.13; venv at `C:\Users\Johan\sector-signals\venv`.
- **psql:** full path required — `C:\Program Files\PostgreSQL\18\bin\psql.exe`.
- **DB:** Neon cloud PostgreSQL; creds in `.env` (gitignored) at repo root. Neon SQL Editor is the quick way to run ad-hoc SQL.
- **Stack:** pandas, matplotlib, seaborn, SQLAlchemy, psycopg2, BeautifulSoup4, requests; yfinance (prices only — deprecated as a financials source, see §6).
- **scipy is NOT installed — and isn't needed for Spearman.** *(Corrected Day 15.)* `df.corr(method="spearman")` works natively in pandas (Cython `nancorr_spearman`, no scipy dependency) — `20` Cell 12 uses it and it runs clean. `.rank().corr()` is an equivalent alternative (Spearman = Pearson on ranks), not a required workaround. Install scipy only if stats get heavier (regressions, p-values) — it means a new dependency for a repo a recruiter might clone.
- **Secrets in `.env`:** DB creds, `ANTHROPIC_API_KEY`, `USPTO_ODP_API_KEY`, `SEC_USER_AGENT_EMAIL`. `.env.example` documents variables with placeholders. **Never commit `.env`.** (Known parse warning — see §12.)
- **Kernel gotcha:** the SQLAlchemy `engine` holds open Neon sockets; a kernel that touched the DB can hang on restart. Run `engine.dispose()` before restarting, or `Get-Process python | Stop-Process -Force` to clear a stuck kernel. **Neon drops idle pooled connections** → `PendingRollbackError` mid-session; the connection cell now uses `pool_pre_ping=True` + `pool_recycle=300` (Appendix A) — put this in **every** notebook's Cell 0, not just the loader. Run scripts from the **repo root** so `load_dotenv()` finds `.env`.
- **PowerShell quoting:** `python -c "..."` with nested quotes/braces fails in PS. Use a small script file (e.g. a throwaway `verify_*.py`) or single-quote-only one-liners.
- **Notebook↔script imports:** notebooks live in `analysis/`, scripts in `etl/`. To import a script from a notebook, add the etl folder to the path first: `sys.path.insert(0, os.path.abspath("../etl"))`. (Confirmed Day 14 — the repo root is empty of `.py` files; scripts are all under `etl/`.)
- **Coming (Day 16):** `gspread` or `google-api-python-client` + a Google service-account JSON as a **GitHub secret** for the Sheets bridge (§10). Not yet installed.

## §4 — Repo structure
- **`etl/`** — `load_hiring.py`, `load_financials.py` (yfinance; deprecated for financials), `edgar_backfill.py` (financials, authoritative — **concept-gather fix landed Day 14**), `load_patents.py`, `download_patents.py`, `assignee_mapping.py`, `explore_assignees.py`, `detect_ats.py`, `test_bulk_download.py`.
- **`analysis/`** — `01_hiring_snapshot.ipynb`, `02_hiring_geography.ipynb`, `03_hiring_category.ipynb`, `10_financials.ipynb`, **`20_cross_signals.ipynb` (COMPLETE as of Day 15 — note the PLURAL name)**, `04_hiring_trends.ipynb` (reserved/deferred — see §10). PNG exports live here (`rd_intensity_by_ticker.png`, `rd_vs_revenue.png`, `operating_margin_by_ticker.png`, `intensity_vs_margin.png`, `revenue_trends.png`, `margin_trends.png`, `role_mix_heatmap.png`, `role_mix_by_segment.png`, **`ai_pct_by_ticker.png`**).
- **`sql/`** — `schema.sql`.
- **`.github/`** — Actions workflow(s) (`scrape.yml`).
- **Root:** `.env`, `.env.example`, `HANDOFF.md`, `interview_moments.md`, `README.md`, `requirements.txt`, `.gitignore`. (No `.py` files at root — all scripts are under `etl/`.)
- **Notebook numbering convention:** `0x` = hiring (01 snapshot, 02 geography, 03 category, 04 trends-reserved); `1x` = financials (10); `2x` = cross-signal (**20 complete**).

## §5 — Working style / collaboration protocol
*(Subsection numbers below are reconstructed — cross-check against your on-disk copy if a specific §5.x reference matters; the content is complete.)*
- **§5.1 Session ritual:** paste handoff → read fully → confirm state → one step at a time → close with day summary + interview moments.
- **§5.2 Decision-making:** Johann defers to Claude's judgment when trade-offs aren't clear, but wants a **concise trade-off summary → a committed recommendation**, not balanced options.
- **§5.3 Surface judgment calls:** name scope trade-offs and decisions explicitly, with a recommendation; let Johann decide.
- **§5.4 Profile before you build:** for any new data work, run a profiling/coverage query first (per-entity counts, ranges, NULL-aware column counts) before analysis or charts.
- **§5.5 Build iteratively:** hand cells/changes in stages; Johann runs + pastes; refine from real output. No large blind notebooks.
- **§5.6 Claude can't reach the DB:** Johann executes and reports before proceeding. *(Claude CAN web-search — see §0.)*
- **§5.7 Don't pre-build** ahead of pending decisions (e.g., no notebook before the naming/approach is chosen).
- **§5.8 Observation ownership:** Johann writes observations in his own voice. Claude gives **guided prompts** (numbers + the question each is really asking) and **pressure-tests** — never ghostwrites. Shape: situation → finding → action → lesson.
- **§5.9 Teach as you go:** Johann reviews code at "shape and logic" level, does a secondary pass with ChatGPT. Do walkthroughs first when asked; explain design choices. **Preferred walkthrough shape (set Day 15):** *what was wrong → the fix → then line-by-line how it works.* Concise; no restating the question.
- **§5.10 Attribution guardrails:** don't sharpen observations into claims the data can't support. No AI causal claims from financials alone; no workforce-trend claims without time-series. Financials × AI = timing/correlation only. Three prior over-attribution errors logged as "do not repeat" — **one of them Claude's, Day 15** (§9).
- **§5.11 Primary-source verification:** any figure entering the public portfolio must be checked against 10-K/10-Q (or equivalent) before commit. **This applies to figures Claude supplies too** — Day 15, Johann correctly refused an externally-sourced revenue figure Claude had introduced. Verification runs on Claude's input, not just Johann's.
- **§5.12 Code-change & output conventions:** deliver changes as concise **before/after/why/logic** — exact old-and-new for substitutions, not full-file rewrites. **Keep notebook outputs intact** (charts render on GitHub for recruiters). Use explicit file paths. Flag PS vs Python vs SQL. Interview moments = **quick and simple** (Johann's stated preference — short reminders, not prose).
- **§5.13 Don't silently rescope:** when work would expand scope (e.g., folding cross-signal into another notebook), name it and get a decision.
- **§5.14 Claude re-reads before asserting file state (added Day 15).** Claude twice described `20`'s contents from a stale earlier read and was wrong (claimed a removed cell was still present). If Claude is going to make a claim about what's in a file, it re-reads the file first or says it's working from an earlier read.

## §6 — Data sources & database
- **Financials:** SEC EDGAR Company Facts API (`edgar_backfill.py`) is the **single source of truth** for the 11 US filers. yfinance is **deprecated as a financials source** — its calendar-month-end dating conflicts with EDGAR's fiscal-end dating and created upsert-invisible duplicate rows. TSM excluded from EDGAR (foreign filer, 20-F).
  - *How extraction works:* pull `companyfacts/CIK{cik}.json`, walk `facts.us-gaap.<concept>.units.USD`, and per metric **gather facts across ALL candidate XBRL concept names** (companies tag the same idea differently — and even tag it differently across filings). Bucket facts by period **duration** (80–100d = discrete quarter, 250–295d = 9-month YTD, 350–380d = full year), keep discrete quarters, derive Q4 = full-year − 9-month YTD matched on shared `start` date. **Concept candidates:** revenue → `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `...IncludingAssessedTax`, `SalesRevenueNet`; R&D → `ResearchAndDevelopmentExpense`, `...ExcludingAcquiredInProcessCost`, **`...SoftwareExcludingAcquiredInProcessCost`** (third variant added Day 14); net income → `NetIncomeLoss`, `ProfitLoss`; operating income → `OperatingIncomeLoss`. Operating margin = operating income ÷ revenue (a fraction; ×100 for display).
  - *Day 14 concept-gather fix:* the old extractor **returned on the first concept that had any data**, so an annual tagged under a sibling concept was never seen (CDNS files quarterlies under `ResearchAndDevelopmentExpense` but its 10-K annual under `...SoftwareExcludingAcquiredInProcessCost`). Now facts accumulate across **all** candidate concepts; candidates are tried in priority order and, on a period collision, **the earlier-listed concept wins — later ones only fill gaps** (so a subset tag can't override a real quarterly value). Full post-fix code in **Appendix B**.
- **Hiring:** ATS APIs — Workday, Jibe/iCIMS, Eightfold, Oracle HCM Cloud. SNPS (TalentBrew/Avature) and TSM disabled (anti-bot; Playwright not justified for 2 tickers).
- **Patents:** PatentsView bulk TSV (S3) + USPTO ODP API. *(PatentSearch API decommissioned March 2026 — bulk TSV is the path.)*
- **Stock prices:** yfinance (still used — only financials deprecated).
- **Tables & row counts:**
  - `hiring_signals` — daily snapshots, 9 tickers/day. **28 consecutive clean 9/9 days, 06-17 → 07-14** (verified Day 15; cron continues daily — re-verify at session start). Columns: `job_id, ticker, snapshot_date, title, location, posted_date, category, ats, job_url, captured_at`. PK `(job_id, snapshot_date)`. **No description/JD-text column** — confirmed Day 15. Any question needing JD body text (e.g. "which BI tool do these companies ask for?") requires a new scrape off `job_url`.
  - `financials_quarterly` — **215 rows** (208 EDGAR + 7 TSM), 12 tickers. Columns: `ticker, quarter (date-string, ISO), revenue, rd_spend, net_income, operating_margin`. Composite PK `(ticker, quarter)`. The 9 hiring-active tickers each have **18–20 clean discrete quarters**. **CDNS fiscal Q4 2025 R&D (`2025-12-31`) = 464,582,000, populated and verified Day 15.** Every hiring-active ticker has a complete trailing-4-quarter window. *(Primary-source check on the CDNS annual still open — §12.)*
  - `stock_prices_daily` — ~13,805 rows *(per prior handoff; verify)*. PK `(ticker, date)`.
  - `patents` — ~61,519 rows loaded *(per prior handoff; verify)*. Assignee normalization / entity resolution = future work.
  - `companies` — 12 seeded tickers with `segment` and `hq_country`.

## §7 — Chart conventions
- seaborn `whitegrid`; matplotlib. Full palette + facet pattern in **Appendix E**.
- Single-series bars: `steelblue`. **Segment palette (reuse everywhere):** Fabless = `steelblue`, IDM = `#e07b39`, EDA = `seagreen`.
- Data labels via `ax.text`/`annotate`; `figsize` sized to content; `plt.tight_layout()`.
- **Save before show:** `plt.savefig("name.png", dpi=150, bbox_inches="tight")` → `plt.show()`. PNGs into `analysis/`. *(`plt.show()` flushes the figure on some backends — saving after writes a blank file.)*
- **Log scale** for wide dynamic range (e.g., revenue across ~45×); prefer real-unit tick labels over bare powers of ten.
- **Facet** (3×3 small multiples with a grey backdrop of the other series) when >6 lines tangle on one axis — used for the financials trend charts.
- **Heatmaps** (role mix): `sns.heatmap`, `cmap='YlGnBu'`, `annot=True, fmt='.1f'`, black gridlines (`linewidths=0.7, linecolor='black'`) — used by `03`'s role-mix-by-ticker and `20`'s role-mix-by-segment so both render consistently on GitHub.
- **Date-stamp anything built on a live snapshot (added Day 15).** Put the snapshot date in the chart title, sourced **from the frame that built the chart** — never from a fresh `SELECT MAX(...)`, which would happily stamp today's date on yesterday's frame. Write the accompanying prose in **ordinal** terms ("NVDA leads, IDMs trail") and keep decimals date-anchored: the notebook re-runs daily and hardcoded decimals go stale on GitHub.
- **Weld caveats to the image, not the markdown cell (added Day 15).** A PNG travels to Tableau, the README, and a recruiter's screen without the surrounding prose. Use `fig.text(0.5, -0.02, ...)` (figure coords, sits outside the axes so two-line tick labels can't collide) + `bbox_inches="tight"` to pull it into the saved file.
- **Nothing hardcoded (added Day 15).** `ax.set_ylim(0, d[col].max() * 1.18)` — headroom scales with the data so labels keep clearing the legend when values move. Titles interpolate counts and dates from the frame.
- **Proxy legend for manually color-mapped bars (added Day 15).** `ax.bar()` with a color list makes *one* container of differently-colored bars — matplotlib doesn't know steelblue "means" Fabless, so `ax.legend()` alone renders nothing. Build invisible swatches: `[plt.Rectangle((0,0),1,1, color=c, ec="black", lw=0.5) for c in PALETTE.values()]`. The alternative (one labeled `ax.bar()` per segment) auto-legends but groups bars by segment and destroys a sorted run. Code in **Appendix H**.
- **Sort once, in one place (added Day 15).** Derive heights, colors, value labels, and tick labels all from the same sorted frame — they then physically cannot desync. Sorting separately lets a future edit put one ticker's bar under another's number, and it will look fine.

## §8 — Git workflow
- **Explicit file paths only — never `git add -A`.** Each workstream committed separately.
- Keep notebook outputs in commits.
- `.env` gitignored, never staged; `.env.example` (placeholders) committed.
- Descriptive, action-first commit messages. Pattern in **Appendix D**.
- **Before staging a re-run notebook:** `git diff --stat` it — a 1-line diff is usually just an `execution_count` bump (`git restore` it to keep noise out). Clean throwaway/diagnostic cells out of any notebook a recruiter will open (esp. `20`).
- **Confirm the commit landed** before treating it as done — `git log --oneline -1`. (Day 15: a commit was handed over, the session moved on, and it went unconfirmed for several exchanges.)

## §9 — Current state / progress log

**Pipeline (automation):**
- GitHub Actions cron daily 09:17 UTC + `workflow_dispatch`; Neon creds as repo secrets.
- Completeness guard live (`sys.exit(1)` on partial runs — won't write a partial snapshot).
- **28 consecutive clean 9/9 snapshots, 06-17 → 07-14**, zero intervention. Pre-guard partials (06-16 6/9, 06-11 6/9) predate the guard.

**Hiring notebooks — all complete:**
- `01_hiring_snapshot` — done.
- `02_hiring_geography` — done. 3-pass normalizer, 0.0% unknown / 87.1% fully resolved. Asia > NA in open postings even for US filers; MU 74% Asia; NVDA Middle East outlier ~17% (Mellanox/Israel); AVGO most US-centric; INTC most globally distributed.
- `03_hiring_category` — done. Native `category` field unusable cross-ticker (5/9 zero coverage). Built 13-bucket title-keyword classifier (first-match-wins), unclassified 29% → 4.4%, ~80% to a specific function, two honest catch-alls. `is_ai` ≈ 9.4% (~1,037 roles). **This notebook is the source of the classifier copied into `20` — keep `03` untouched.**

**`10_financials.ipynb` — complete (Day 13):**
- *Snapshot charts:* R&D-intensity ranked bar; revenue-vs-R&D-spend **log-log scatter** colored by segment (label = intensity); operating-margin ranked bar; **R&D-intensity-vs-margin scatter (Spearman ρ ≈ −0.80, n=9)** — strong negative rank correlation, business model as the third factor behind both.
- *Trend charts:* revenue indexed to each ticker's first quarter = 100 (log); operating margin (absolute %); both as **3×3 faceted small multiples** colored by segment, ordered so row 3 = the three IDMs (INTC, MU, TXN). Code in Appendix E.
- *Observations (Johann's, pressure-tested):* (1) **R&D intensity** driven by **product type, not segment** (CDNS 34.5% highest, MU 5.2% lowest, NVDA 8.1% low only because revenue outran the largest absolute budget; flat middle MRVL/AMD/QCOM/INTC ~23–25% and TXN 10.6% break any pure size story). (2) **NVDA** revenue breaks from the pack ~early/mid-2023, ~12× indexed by 2026, margin rising in the same window (pricing power); timing aligns with AI buildout, no causation. (3) **MU** margin −60% (2023) → ~80% (2026): commodity memory **cycle**, not a trend — its "highest margin" is a peak vs NVDA's steady ~65%. **Snapshot ranks, trend explains.** (4) **Row 3 (INTC/MU/TXN, all IDM)** three different margin shapes → segment label doesn't predict behavior; product type does.

**EDGAR backfill bug — found & fixed Day 13 (see also the Day 14 concept-gather fix below):**
- *Symptom:* faceted trend showed AMD revenue "collapsing" 54% during the AI boom.
- *Causes:* (1) duration-blindness — 9-month YTD stored under the same `fp` label as discrete quarters (AMD Q3'22 = $18B YTD vs $5.57B true quarter); (2) missing Q4 — 10-Ks report only the full year; (3) Q4 derivation keyed on `fy` (filing year, re-stamped by restatements) instead of period `start`; (4) yfinance/EDGAR date-mismatch near-duplicate rows.
- *Fixes:* duration-bucketing; Q4 = full-year − 9-month YTD matched on shared `start`; DELETE-before-reload making EDGAR the single source of truth; SEC email → `SEC_USER_AGENT_EMAIL`. Verified: AMD dry-run (2022-09 → $5.57B), reload → 215 rows, `MIN(quarter)` 2021-06-03 → 2021-07-31, zero non-standard gaps.

---

**Day 14 session (2026-07-14) — cross-signal built + CDNS source fix:**

*State verified live at start:* hiring 25 clean 9/9 days (06-17 → 07-11); `financials_quarterly` 215 rows / 7 TSM / oldest 2021-07-31.

- **`20_cross_signals.ipynb` built (PLURAL name; doc's earlier singular was wrong).** Stage-1: connection (with pre-ping) → `fin`/`core` load → current hiring snapshot → **classifier copied verbatim from `03`** (`ROLE_RULES` + `AI_PAT`) → per-ticker `ai_pct` + role mix. Classifier reconciled cleanly against `03`: **4.0% unclassified / 9.4% AI (1,025 jobs)** on the current 10,852-posting snapshot (03 was 4.4% / 9.4% — same ballpark confirms a faithful copy; exact match not expected, different snapshot day).
- **Financial smoothing decision → trailing-4-quarter (TTM), revenue-weighted** (Σ R&D ÷ Σ revenue, and Σ operating-income ÷ Σ revenue, *not* a mean of quarterly ratios — a low-revenue quarter can't distort a revenue-weighted ratio). Chosen over single-quarter (noisy; grabs a cyclical instant) and full-history (drags in stale years like MRVL's 2022–24 negatives / MU's trough). **MU caveat:** it's mid-recovery on the memory up-leg, so its 4Q mean sits *below* its latest quarter — the smoothed number understates its current position.
- **`signals` frame = 9 tickers × 20 cols** (Appendix G): `segment, n_jobs, ai_pct`, 14 role-mix % columns, `rd_intensity`, `rd_qtrs`, `operating_margin`. `rd_intensity`/`operating_margin` kept as **fractions** (×100 at plot time) to match `10`; `ai_pct` and role-mix are percents. Segment map: Fabless {NVDA,AMD,QCOM,AVGO,MRVL}, IDM {INTC,MU,TXN}, EDA {CDNS}.
- **CDNS fiscal-Q4 R&D null — root-caused and fixed (the main engineering work):** the TTM completeness guard flagged CDNS `rd_na=1` (one NULL `rd_spend` in its 4-quarter window, at `2025-12-31`). Q4 R&D is *derived* (annual − 9-month YTD) since 10-Ks report only the full year. First theory (fiscal-calendar start-date mismatch — Cadence runs a 52/53-week year) was **ruled out by pulling the raw EDGAR facts**: every period start matched `2025-01-01`. Real cause: Cadence tags full-year R&D under `ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost` while its quarterlies use `ResearchAndDevelopmentExpense` — and (a) that concept **wasn't in the candidate list** and (b) the extractor **returned on the first concept with data**, so the annual was never reached → no minuend → null Q4.
  - *DB patch (done):* idempotent one-row upsert, `UPDATE … SET rd_spend = 464582000 WHERE ticker='CDNS' AND quarter='2025-12-31' AND rd_spend IS NULL` (= annual 1,768,772k − 9mo 1,304,190k). CDNS now on a clean 4-quarter TTM (`rd_qtrs`=4).
  - *Source fix (done, committed `76c4315`):* two parts in `edgar_backfill.py` — added the Software concept to `CONCEPT_CANDIDATES["rd_spend"]`, and rewrote `extract_quarterly_series` to gather across **all** candidate concepts with a "primary-wins-on-collision, siblings-fill-gaps" rule (Appendix B). Verified non-destructively: reloaded module + ran the extractor on CDNS → `2025-12-31` present, value `464,582,000.0`. The one-row upsert is now **redundant** (next full backfill derives Q4 on its own) and was removed from the notebook; a markdown note in `20` records the fix.
  - *Merge robustness:* the merge computes `rd_intensity` over only the quarters where `rd_spend` is present (`rev_rd = last4[rd_spend.notna()]…`) and carries `rd_qtrs` to flag any <4-quarter basis — so even a future in-window null yields a correct ratio, not a silent 3-over-4 mismatch.
- **Neon stale-pool recurrence:** a `PendingRollbackError` hit mid-session (idle pooled connection dropped by Neon). Fixed by adding `pool_pre_ping=True` + `pool_recycle=300` to `20`'s Cell 0 (Appendix A). Belongs in every notebook's Cell 0.

**Findings (Johann's, pressure-tested) — the cross-signal arc:**
- **Q1 — hiring tilt vs financial ratios: independent.** Spearman across the 9 tickers: every hiring↔financial pair sits between **−0.10 and +0.25** — no meaningful correlation with `rd_intensity` or `operating_margin`. (`ai_pct` ↔ `Software & Firmware` is strong at **0.80 Spearman / 0.78 Pearson** — but both are *hiring* metrics, one software-forward posture showing up twice, not hiring predicting something independent.) n=9 → directional, not significance-grade. Correlation ≠ causation; `ai_pct` = the word "AI" in a title, not verified AI work.
- **Q2 — role mix vs business model (value-chain position): tracks sharply.** Segment × role-mix heatmap (`role_mix_by_segment.png`, raw %, YlGnBu). Two role types separate segments hard: **Manufacturing & Process** (IDM 29.4% vs Fabless/EDA ~10%, ~20pt spread — IDMs own fabs) and **Software & Firmware** (EDA 22.5% > Fabless 16.6% > IDM 5.1%, ~17pt — EDA sells software). Everything below the top three buckets is roughly flat across segments. **EDA = CDNS alone (n=1)** — every EDA cell is one company (the elevated Sales/Field share for EDA is CDNS-specific too); stated on-chart.
- **The result is the contrast:** financial *ratios* don't predict hiring tilt (Q1), but business *model* does (Q2). **Hiring encodes what kind of company you are, not how it's performing financially.** A predictor that fails next to one that works is a stronger finding than either alone.

**Decisions made Day 14:**
- **`04_hiring_trends` deferred on a timescale basis (not skipped):** 25–30 daily snapshots can't distinguish *strategic* hiring shifts (quarters-to-years, plus annual budget/new-grad cycles) from short-horizon noise. A month can support *operational* reads (velocity, mix drift, churn) but not the strategic-signal claim that would differentiate it. Unlocks at ≥1 quarter, ideally a year; the cron keeps banking dated snapshots so "future work" has a real mechanism. Good interview line as a *deferred-with-a-reason* item.
- **Sequencing set:** AI-pct cut → dashboard v1 (Tableau Public; **de-risk spike first**) → AI insight layer. Trends slots in when the window matures.

**Committed Day 14:** `etl/edgar_backfill.py` (concept-gather fix — `76c4315`, pushed); then `analysis/20_cross_signals.ipynb` + `analysis/role_mix_by_segment.png` + `interview_moments.md`. `03_hiring_category.ipynb` re-run churn reverted (kept untouched).

---

**Day 15 session (2026-07-15) — AI-hiring cut landed; `20` COMPLETE; dashboard architecture resolved:**

*State verified live at start (all three clean):* hiring **28** clean 9/9 days (06-17 → 07-14); `financials_quarterly` 215 rows / 7 TSM / oldest 2021-07-31; CDNS `2025-12-31` `rd_spend` = 464,582,000 populated. **Bonus cross-check:** CDNS's three 2025 quarters (439,102 + 442,057 + 423,031) sum to **1,304,190k — exactly the 9-month YTD that was subtracted** to derive Q4. The derivation validates against itself.

**Shipped:**
- **`ai_pct_by_ticker.png`** — sorted AI-share bar, segment-colored, `n=` on the axis, snapshot date in the title, caveat welded to the PNG. Code in **Appendix H**.
- **Cell 4 date fix** — the snapshot query now selects `snapshot_date`, asserts it's singular, exposes `SNAP_DATE`, and prints it (**Appendix H**).
- **Johann's read on the AI cut** written and pressure-tested. Two claims cut before commit (below).
- **Committed `e1352a0`** — `20_cross_signals.ipynb` + `ai_pct_by_ticker.png` + `role_mix_by_segment.png`. Verified on `origin/main`.

**Day 15 results — AI-titled hiring share (snapshot 2026-07-14, 10,859 postings):**

| Rank | Ticker | Segment | ai_pct | n_jobs |
|---|---|---|---|---|
| 1 | NVDA | Fabless | 18.7 | 2,553 |
| 2 | QCOM | Fabless | 15.4 | 1,738 |
| 3 | AMD | Fabless | 12.2 | 1,038 |
| 4 | INTC | IDM | 6.7 | 640 |
| 5 | CDNS | EDA | 5.4 | 598 |
| 6 | AVGO | Fabless | 3.0 | 337 |
| 7 | MU | IDM | 2.7 | 2,831 |
| 8 | TXN | IDM | 1.7 | 523 |
| 9 | MRVL | Fabless | 1.3 | 601 |

*Panel AI share ≈ 9.6% — consistent with `03`'s 9.4% (different snapshot day; ballpark is the check, not exact match).*

**Johann's read (his voice, pressure-tested):**
- **Segment does not predict AI tilt.** Fabless holds 1st, 2nd, 3rd — *and* 6th and 9th, spanning nearly the entire range (1.3 → 18.7). This **refutes the fabless-vs-IDM prediction** the Day 14 roadmap made. What the company actually produces matters more than its segment label — the same shape as `10`'s "product type, not segment" finding, now appearing in hiring data.
- **NVDA highest** — the company most driving the AI buildout, GPU focus for training/serving frontier models.
- **MRVL lowest** — differentiates on networking/data-infrastructure silicon. **But** `ai_pct` and Software & Firmware share correlate strongly (ρ=0.80), and MRVL is also near the bottom on Software & Firmware (5.8%) — so its low score is *consistent with the trend*, not an anomaly.
- *Note the contrast with Q2:* segment predicts **role mix** cleanly but **not** AI tilt. Two hiring metrics, two different answers about the same variable.

**The stale-frame catch (small bug, real lesson):**
`df` held **07-13** data while looking like 07-14 — caught by hand-summing `n_jobs` to exactly 10,893, the prior day's count. Cause was benign (Cell 4 ran before the 09:17 UTC cron landed). But it exposed a structural gap: the query pinned to `MAX(snapshot_date)` and **never carried the date out**, so nothing downstream could state which day it read. Two failure modes look identical from the output — *ran early* (nothing) vs. *snapshot selection silently pinned* (every dashboard tile frozen while claiming to be live). Fixed at the source; the `print` now makes it visible every run.

**Ranking stability (banked, not published):**
Ordering **identical** across 07-12 / 07-13 / 07-14. Decimals move a few tenths (NVDA 18.3→18.7, CDNS 5.0→5.4). This is the empirical basis for §7's date-stamp rule: ordinal prose survives the daily re-run, hardcoded decimals don't.

**Postings drifting down — banked, not read:** 11,187 (06-28) → 10,859 (07-14), ~−3% in 16 days, aggregate across 9 tickers. Exactly the timescale the trends deferral says can't separate signal from noise. Could be one company closing reqs. **Do not read this.**

**Three claims cut before commit — the analytical work of the session:**
1. **"`ai_pct` follows `n_jobs`"** *(Johann's, cut).* ρ≈0.48 — weak, and MU alone carries most of the rank distance (biggest poster in the panel at 2,831, 7th on AI share; AVGO the smallest at 337, 6th). Also **circular**: `ai_pct` *is* `ai_jobs ÷ n_jobs`, so the claim asserts a ratio tracks its own denominator. This is the **ratio-vs-absolute trap from `10`, second appearance.** It was the one claim on the list a recruiter could falsify from the chart's own `n=` labels.
2. **"The metric is blind to hardware-side AI"** *(**Claude's, refuted by Johann's data** — logged under §5.10).* Claude pushed the framing that a company could be heavily AI-exposed and score ~0 because its reqs are titled by chip discipline (SerDes, physical design, DSP). MRVL looked like proof. **Johann checked: MRVL is also near the bottom on Software & Firmware (5.8%)** — which puts it *on* the ρ=0.80 trend line, not off it. A confirming case shows nothing invisible. **A metric can only be proven blind to something you can independently measure**, and the schema has no AI-exposure ground truth. Downgraded from *blindness* (unsupported) to **confound** (supported): `ai_pct` cannot separate "does less AI" from "titles roles by hardware discipline."
3. **"MRVL datacenter revenue ≈76%"** *(Claude's, correctly refused by Johann).* Externally sourced (Zacks reporting Marvell Q1 FY2027); schema has no segment revenue. Johann's objection — *"i dont have anything in my analyses that says mrvl datacenter revenue is 76%"* — was right: dropping it in would launder an outside claim into looking like a finding. **§5.11 fired on Claude's input, which is the harder direction.**

**Dashboard de-risk spike — RESOLVED. Architecture changed.**
- **Tableau Public cannot connect to PostgreSQL. By design, not config.** Tableau's own support docs: Tableau Desktop Public Edition and Tableau Public (web) work with Microsoft Excel, multiple text file formats, statistical files, Google Sheets, and web data connectors. The error is explicit — *"The Tableau server you are publishing to does not permit external database connections."* Tableau Public **only supports extracts**; the Public edition won't even show a live-connection option. Also: 15M-row and 10GB-storage caps (irrelevant at this scale).
- **Google Sheets is the one auto-refreshing exception.** Tableau Public does not support scheduled updates unless the source is Google Sheets, in which case it **auto-refreshes every 24 hours**. This is a well-trodden pattern (Python → Sheets → Tableau Public), not an invention. **You do not control the refresh time** — the dashboard can trail Neon by up to a day.
- **Power BI evaluated and rejected for this phase.** Not a tool weakness — a fit problem. (a) Publish-to-web requires a **tenant admin setting**; Power BI needs a work/school account, so the tenant is SJSU's and SJSU IT owns the switch. Universities routinely leave it off. (b) The free-license question is **genuinely unsettled** — two Microsoft Learn pages contradict: the publish-to-web doc implies free works from My Workspace, while the free-user feature page (updated 2026-05-26) says flatly that creating embed codes requires Pro or PPU. (c) Service refresh against Neon likely needs an **on-prem gateway** on an always-on machine (moderate confidence, unverified). Pro is $14/mo; SJSU's M365 tier *may* include it — unchecked.
- **CHOSEN ARCHITECTURE:** `Neon → GH Actions (existing cron) → Google Sheet → Tableau Public (24h auto-refresh) → public URL`.
- **Framing: "daily-refreshed", never "real-time."** `SNAP_DATE` (Day 15) is what lets the dashboard state its own as-of date.
- **The reframe that makes this reversible:** the Sheets bridge is **not a Tableau workaround — it's a tool-agnostic publishing layer.** Power BI reads Google Sheets too, and Sheets being a *cloud* source sidesteps the gateway problem entirely. A Power BI version later costs zero pipeline changes. **The tool choice is not locked in; only the shipping order is.**

**Tool-choice reasoning (for the interview, and for future-Johann second-guessing this):**
- Claude initially argued "Tableau carries more resume weight than Power BI" — **retracted; that was a preference dressed as evidence.** Power BI likely appears on *more* analyst JDs overall. Confidence in either direction: low.
- **The real argument:** the tool is low-stakes for hiring; the artifact is high-stakes. No one rejects a sophomore for knowing Tableau over Power BI — both read as "BI tool," both are learnable in a week, interns get trained on the house tool. What's scarce in the applicant pool isn't a BI tool; it's an MIS student with a live automated pipeline, SEC XBRL extraction, and semiconductor domain knowledge from a real Cadence engagement. **So optimize for shipping, not for the logo.** Tableau Public is the only free path to a public, linkable, auto-refreshing artifact.
- **Empirical check attempted and failed:** could `hiring_signals` answer "which BI tool do these 9 companies ask for?" No — the table stores `title`, not JD body text (§6). Would need a new scrape off `job_url`. Not worth it for a tool decision, but now a known schema limit.

## §10 — Roadmap / what's next
1. **Sheets bridge — NEXT, ~1 day.** Google service-account JSON → GitHub secret; extend `scrape.yml` (or a sibling job) to write **pre-aggregated** frames to a Sheet after each scrape. **Aggregates, not raw** — raw is ~10.9k rows/day and pointless to ship; the `signals` frame is 9×20. One tab per dashboard view. This is the only genuinely new engineering left before the dashboard.
2. **Dashboard v1 (capstone), ~4–7 focused days.** Three tiles from work already done: segment role-mix heatmap, `ai_pct` bar, hiring-vs-financials scatter. Then polish + publish + wire into README. **Keep scope tight — a clean 3-view dashboard beats an elaborate one.** Main timeline risk.
3. **README rewrite — do NOT leave this last.** The README is what a recruiter reads first and possibly only; the dashboard gives it a hero link. Thesis framing, the three findings, the deferred-with-reasons items, the architecture diagram. Arguably higher leverage than anything below it.
4. **Visibility — NEW, flagged Day 15, currently missing from the plan.** A GitHub repo nobody visits is worth close to nothing. A LinkedIn post — *"I built a pipeline tracking semiconductor hiring daily; here's what the AI-hiring split actually looks like"* + the dashboard link + `ai_pct_by_ticker.png` — is how portfolio projects get seen. Low cost, plausibly the highest-leverage item on this list, and Wave 1 is live now. **Decide whether this happens; don't let it default to no.**
5. **Lightweight AI insight layer** — ~20–40 line Claude-API narrator turning real numbers → plain English. Ties to the GEO background. **Honest assessment (Day 15): this is the least differentiating item on the roadmap.** Everyone is bolting an LLM onto something; what's rare here is the pipeline discipline. Keep it *below* README polish. Its real argument is the Cadence/GEO narrative thread, not the tech.
- **`04_hiring_trends`** — **deferred on a timescale basis** (§9). 28 clean days banked; unlocks at ≥1 quarter (ideally a year). The pipeline is live and dated, so this is a real "future work" item, not a punt. Build a *velocity/mix-drift* v2 when the window earns it — do **not** claim strategic-shift detection on a month.
- **hiring × patents** — now has a **specific purpose beyond "more data":** AI-classified patents by assignee would be an **AI-exposure measure independent of hiring language** — i.e. the control that breaks the `ai_pct` ↔ software-share confound (§9 Day 15). Still gated on verifying assignee→ticker mapping quality; if messy, multi-session entity resolution → stretch/optional. No assignee data loaded yet.
- **`edgar_backfill.py` follow-up (minor):** the concept-gather fix is committed; if ever extended, keep the "primary-wins-on-collision" dedup so a subset concept can't override a real value.
- **Timing tension (Day 15):** Wave 1 is **live now** and the dashboard is ~1–2 weeks out. Applications going out this month can carry the GitHub link; the dashboard link follows. Don't hold applications for the dashboard.
- **Bottom line:** three cross-signal findings + dashboard + README = a complete, defensible Wave-1 portfolio. AI layer + trends are enhancements after. **With Wave 1 live now, a rougher dashboard up in a week beats a polished one in a month — ship a lean v1, iterate.**

## §11 — Key learnings & principles
- **Data smells catch bugs:** round numbers (exactly 2,000 NVDA jobs = Workday API cap) and suspiciously large figures → investigate before trusting. **Also: an exact match to a prior day's count** (10,893 = yesterday exactly) — Day 15.
- **A number that contradicts reality is a bug, not a finding** — sanity-check derived data against a primary source (the AMD "54% collapse" → YTD bug).
- **Key on data-intrinsic properties** (period duration, period start), **not record metadata** (fiscal labels, filing year). Both EDGAR bugs came from trusting metadata.
- **Duration-bucketing over label-filtering** for EDGAR quarters.
- **The same line item can be tagged under sibling XBRL concepts across filings** (CDNS: quarterlies under `ResearchAndDevelopmentExpense`, 10-K annual under `...SoftwareExcludingAcquiredInProcessCost`). Gather across **all** candidate concepts; don't return on the first with data. (Day 14.)
- **Single source of truth:** mixing yfinance/EDGAR date conventions creates upsert-invisible duplicates; fix at source, don't reconcile downstream.
- **Dry-run on one ticker first**, against a known public figure, before a full reload. Test source-code fixes **non-destructively** (reload the module + run the function) before touching the destructive DELETE-reload script.
- **Ratios are immune to period-length & unit errors; absolute values expose them** (intensity/margin survived the YTD bug; revenue levels didn't — same reason TSM's TWD doesn't break intensity).
- **Snapshot ranks companies; a trend explains them** (MU: highest snapshot margin, deepest series trough).
- **Product type, not segment,** explains the pattern — held for R&D intensity *and* margin (`10`), and **again for AI-titled hiring share** (Day 15: Fabless spans 1.3 → 18.7, both ends of the range).
- **Hiring encodes business model (structure), not financial performance** — role mix splits on manufacturing/software by value-chain position (Q2), while the financial ratios don't predict it (Q1). *The finding can be the contrast:* a predictor that fails next to one that works beats either alone. (Day 14.) **But it's metric-specific:** segment predicts role mix and does *not* predict AI tilt (Day 15). Don't generalize "segment predicts hiring."
- **Timescale gates trend analysis:** ~30 daily snapshots can't separate strategic hiring shifts from cyclical/seasonal noise — trends need ≥1 quarter, ideally a year. Defer with a reason, keep the pipeline banking. (Day 14.)
- **Classifier integrity over coverage:** honest catch-all buckets beat forced classification. Reconcile a copied classifier against its source (ballpark, not exact) to confirm a faithful copy.
- **NVDA framing:** sells GPU hardware; CUDA is the free software platform creating lock-in. The software/research hiring tilt is thesis *evidence*, not the business model.
- **Attribution guardrails:** no AI causal claims from financial/ratio data alone; no workforce-trend claims without time-series. `ai_pct` = the word "AI" in a title, not verified AI work — a correlation there could be *labeling*, not *doing*. n=9 → directional, not significance-grade.
- **Numbers require primary-source verification** before entering the public portfolio — **including numbers Claude supplies** (Day 15).
- **Verify with arithmetic that breaks if the code silently no-ops** (the 208+7=215 row check caught a DELETE that hadn't saved; the TTM completeness guard caught the CDNS null; hand-summing `n_jobs` caught the stale frame).
- **Serverless Postgres drops idle pooled connections** — `pool_pre_ping=True` + `pool_recycle=300` in every notebook's Cell 0, not just the loader.
- **Spearman needs no scipy** — `df.corr(method="spearman")` is native pandas; `.rank().corr()` is an equivalent alternative, not a required workaround. *(Corrected Day 15.)*
- **A frame filtered by `MAX(date)` still doesn't know its own date.** Pin the date **into the data**, not just the WHERE clause — and source any date stamp from the frame that built the output, never a fresh query. (Day 15.)
- **A metric can only be proven blind to something you can independently measure.** No AI-exposure ground truth in the schema → no *blindness* claim available, only a *confound* claim. This is what gives the patents pipeline a purpose: it's the control, not "more data." (Day 15.)
- **A ratio cannot "track" its own denominator.** `ai_pct = ai_jobs ÷ n_jobs`; claiming it follows `n_jobs` is circular. Ratio-vs-absolute, second appearance. (Day 15.)
- **Free BI tiers differ on publishing, not features.** Tableau Public: no DB connectors, free public link. Power BI free: full DB connectors, no free public link without an admin. **Check what a tool lets you *publish*, not what it lets you *build*.** (Day 15.)
- **De-risk the unknown before building on it.** Two searches killed a plan that would have cost a day of setup and then failed at the publish step. **The blocker was in the tier, not the tool** — exactly the thing that doesn't surface until you try to ship. (Day 15.)
- **Pressure-testing runs both ways.** Day 15's two best analytical outcomes were claims *killed* — one Johann's, one Claude's, each killed by the other. Neither was in the plan. (Day 15.)

## §12 — Housekeeping & known gotchas
- **`.env` parse warning:** `python-dotenv could not parse statement starting at line 17` prints on load (harmless — all vars still resolve). Fix before wiring `ANTHROPIC_API_KEY` for the narrator (a malformed line could later swallow a key). Usual culprit: an inline `#`, an unquoted value, or a line missing its `=`. Two minutes; open `.env`, look at line 17.
- **CDNS FY2025 annual R&D — primary-source check still open (§5.11):** confirm ~$1,768.8M against Cadence's FY2025 10-K "Research and development" line (EDGAR, CIK `0000813672`, filed 2026-02-19). **Close this before the dashboard publishes CDNS numbers, not after.** Blast radius is small (one cell of the Q1 correlation matrix; nothing in the hiring findings). Arithmetic already cross-checks twice: annual − 9mo = a plausible Q4, and the three 2025 quarters sum to exactly the 9-month YTD (Day 15).
- **scipy not installed** — not needed for Spearman (§3). Install only if stats get heavier.
- **`.env.example`** — clean template in **Appendix A** (Neon block, `SEC_USER_AGENT_EMAIL` placeholder, API keys). Confirm it's committed and current.
- **SEC fair-use** requires a real `SEC_USER_AGENT_EMAIL` in `.env` at runtime. The financials backfill is manual/local → **not** needed as a GitHub secret unless that script is ever automated.
- **TSM in TWD** (~31 TWD/$1): excluded from analysis; ratios still valid, only absolute levels inflated. `MAX(revenue)` returns NaN on TSM's sparse series — driver quirk, not a real problem.
- **ANSS** data ends Q1 2025 (Synopsys acquisition, closed Jul 2025).
- **SNPS/TSM hiring fetchers** disabled (anti-bot); revisit only if Playwright becomes justified.
- **Legacy check:** confirm actions are pinned (checkout/setup-python) in the Actions workflow (`scrape.yml`).
- **Project-tab file snapshots** (Claude Projects) are static — `20_cross_signals.ipynb` in the tab is now stale (pre-Day-15). Re-add it and `etl/edgar_backfill.py` if Claude needs current versions without pasting; GitHub is the live source (`e1352a0`).
- **Google service-account JSON (upcoming):** goes in a **GitHub secret**, never the repo, and belongs in `.gitignore` if a local copy exists.
- **§1a figures are Day-13 snapshot values and don't auto-update** — see the warning under §1a.
- Confirm `interview_moments.md` and this handoff are committed at session close.

## §13 — Next session: exact starting point
1. **Read this handoff fully**, then **verify live state** — `hiring_signals` snapshot-series check (cron still 9/9 past 07-14?) + `financials_quarterly` row-count/gap sanity check + CDNS Q4 populated (queries in **Appendix C**). Don't trust the doc blindly.
2. **Sheets bridge (~1 day)** — the only new engineering left:
   - Google Cloud project → service account → download JSON key → enable Sheets API → share the target Sheet with the service-account email.
   - JSON key → GitHub secret. `gspread` (or `google-api-python-client`) → `requirements.txt`.
   - Decide **what** goes in the Sheet: **pre-aggregated frames only, one tab per dashboard view.** Not raw postings.
   - Extend `scrape.yml` to write the Sheet after each successful scrape — **behind the completeness guard**, so a partial run can't publish a partial dashboard.
   - Verify end-to-end with one throwaway tab before wiring the real tiles.
3. **Then dashboard v1** — 3 tiles, tight scope, then polish + publish + README wire-up.
4. **Close the CDNS 10-K check** before any CDNS number goes public (§12).
5. **Decide on the LinkedIn/visibility item** (§10.4) — don't let it default to no.
6. **`04_hiring_trends`** — only once the snapshot window reaches ≥1 quarter (deferred with reason, §9/§10). Not yet.

---

# APPENDICES — reusable code & queries
*Kept here so you can rerun or rebuild without opening old chats. Appendix B and G reflect Day 14 code; Appendix H is Day 15.*

## Appendix A — Standard notebook setup & core dataframes

**Connection cell (restart-safe + Neon idle-drop-safe; run first in EVERY notebook):**
```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

load_dotenv(override=True)
engine = create_engine(
    f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}",
    pool_pre_ping=True,     # ping the pooled conn before use; silently replace dead ones
    pool_recycle=300,       # recycle anything older than 5 min (Neon drops idle sockets)
)
pd.read_sql("SELECT 1 AS ok", engine)   # sanity check
```

**Financials core frames (`fin` = all 12, `core` = 9 hiring-active, `latest` = most-recent single quarter each):**
```python
fin = pd.read_sql("SELECT * FROM financials_quarterly ORDER BY ticker, quarter", engine)
fin["quarter"] = pd.to_datetime(fin["quarter"])
fin["rd_intensity"] = fin["rd_spend"] / fin["revenue"]

HIRING_TICKERS = ["AMD","AVGO","CDNS","INTC","MRVL","MU","NVDA","QCOM","TXN"]
core = fin[fin["ticker"].isin(HIRING_TICKERS)].copy()

# `latest` = single latest quarter (used by 10_financials snapshots). The cross-signal
# notebook uses a trailing-4-quarter (TTM) collapse instead — see Appendix G.
latest = (core.sort_values("quarter").groupby("ticker").tail(1)
              .sort_values("rd_intensity", ascending=False))
```

**Clean `.env.example` template (placeholders only — real values live in `.env`):**
```
# --- Neon (PostgreSQL) ---
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

# --- SEC EDGAR (fair-use requires a real contact email at runtime) ---
SEC_USER_AGENT_EMAIL=your_email@example.com

# --- API keys ---
ANTHROPIC_API_KEY=
USPTO_ODP_API_KEY=
```

## Appendix B — Fixed EDGAR extraction (post Day-14 concept-gather fix)

`edgar_backfill.py` → `extract_quarterly_series` (post-fix, verbatim). Gathers facts across **all** candidate concepts (priority order, primary wins on period collision), duration-buckets, derives Q4 = full-year − 9-month YTD on shared `start`:
```python
def extract_quarterly_series(facts: dict, candidates: list[str]) -> dict:
    """
    Return {quarter_end_date: value} of DISCRETE quarterly values.
    Q1-Q3 come from 3-month facts; Q4 is derived as (full-year - 9-month YTD),
    because 10-Ks report only the full year, never a standalone Q4.

    Facts are gathered across ALL candidate concepts, not just the first with
    data: a company can tag the same line under sibling concepts across filings
    (e.g. CDNS files quarterlies under ResearchAndDevelopmentExpense but the 10-K
    annual under ...SoftwareExcludingAcquiredInProcessCost). Candidates are in
    priority order — on a period collision the earlier concept wins; later ones
    only fill periods the primary lacks. Within one concept, latest-filed wins.
    """
    us_gaap = facts.get("facts", {}).get("us-gaap", {})

    quarterly = {}   # end_date   -> {"val","filed","concept"}   3-month facts
    ytd9 = {}        # start_date -> {"end","val","filed","concept"}  9-month YTD
    annual = {}      # start_date -> {"end","val","filed","concept"}  full year

    for concept in candidates:                       # priority order
        if concept not in us_gaap:
            continue
        units = us_gaap[concept].get("units", {})
        if "USD" not in units:
            continue

        for e in units["USD"]:
            start_str, end_str, val = e.get("start"), e.get("end"), e.get("val")
            if not start_str or not end_str or val is None:
                continue
            start_d = date.fromisoformat(start_str)
            end_d = date.fromisoformat(end_str)
            if end_d < CUTOFF_DATE:
                continue
            days = (end_d - start_d).days
            filed = e.get("filed", "")

            # write if empty (any concept fills a gap), or newer fact from the SAME
            # concept (latest-filed). A different, higher-priority concept already
            # holding the slot is never overwritten.
            if 80 <= days <= 100:            # discrete quarter — key: end_date
                cur = quarterly.get(end_d)
                if cur is None or (cur["concept"] == concept and filed > cur["filed"]):
                    quarterly[end_d] = {"val": float(val), "filed": filed, "concept": concept}
            elif 250 <= days <= 295:         # 9-month YTD — key: start_date
                cur = ytd9.get(start_d)
                if cur is None or (cur["concept"] == concept and filed > cur["filed"]):
                    ytd9[start_d] = {"end": end_d, "val": float(val), "filed": filed, "concept": concept}
            elif 350 <= days <= 380:         # full fiscal year — key: start_date
                cur = annual.get(start_d)
                if cur is None or (cur["concept"] == concept and filed > cur["filed"]):
                    annual[start_d] = {"end": end_d, "val": float(val), "filed": filed, "concept": concept}

    if not quarterly and not annual:
        return {}

    series = {d: r["val"] for d, r in quarterly.items()}

    # Q4 = full year - 9-month YTD, matched on shared fiscal-year START date.
    for start_d, ann in annual.items():
        if ann["end"] in series:
            continue                     # a real 3-month Q4 was filed
        y9 = ytd9.get(start_d)
        if y9 is not None:
            series[ann["end"]] = ann["val"] - y9["val"]

    return series
```

**R&D concept candidates** (order matters — primary first):
```python
    "rd_spend": [
        "ResearchAndDevelopmentExpense",
        "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
        "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost",   # added Day 14 (CDNS annual)
    ],
```

`main()` — DELETE block making EDGAR the single source of truth (right after the `SELECT 1` check, before the first `print`). **This script is DESTRUCTIVE (full DELETE + reload) and DETERMINISTIC on unchanged data — never re-run it to "fix" a value; fix the derivation instead, then re-run.**
```python
    # Make EDGAR the single source of truth: clear these tickers first so old
    # yfinance rows (calendar-dated) can't linger as near-duplicate quarters.
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM financials_quarterly WHERE ticker = ANY(:tks)"),
            {"tks": list(TICKER_TO_CIK)},
        )
    print(f"Cleared existing rows for {len(TICKER_TO_CIK)} EDGAR tickers.\n")
```
Run reload from repo root: `python etl\edgar_backfill.py`. **Success = first line "Cleared existing rows for 11 EDGAR tickers." and summary "Total rows in DB: 215".**

## Appendix C — Reusable SQL (Neon SQL Editor)

**Pipeline health (cron still firing 9/9?):**
```sql
SELECT snapshot_date, COUNT(DISTINCT ticker) AS tickers, COUNT(*) AS rows
FROM hiring_signals
GROUP BY snapshot_date
ORDER BY snapshot_date DESC
LIMIT 20;
```

**Financials profiling (coverage per ticker; NULL-aware — CDNS `rd_n` should equal its quarter count):**
```sql
SELECT ticker, COUNT(*) AS quarters, MIN(quarter) AS first_q, MAX(quarter) AS last_q,
       COUNT(revenue) AS rev_n, COUNT(rd_spend) AS rd_n, COUNT(operating_margin) AS margin_n
FROM financials_quarterly
GROUP BY ticker ORDER BY ticker;
```

**Row-count / source integrity (expect 215 total, 7 TSM, oldest ≥ 2021-07-31):**
```sql
SELECT COUNT(*) AS total_rows,
       COUNT(*) FILTER (WHERE ticker = 'TSM') AS tsm_rows,
       MIN(quarter) AS oldest
FROM financials_quarterly;
```

**CDNS Q4 check (expect `2025-12-31` `rd_spend` = 464582000, not null):**
```sql
SELECT quarter, revenue, rd_spend, operating_margin
FROM financials_quarterly
WHERE ticker = 'CDNS' AND quarter >= '2025-01-01'
ORDER BY quarter;
```

**Duplicate detection (near-identical rows = the yfinance/EDGAR date-mismatch bug; expect none):**
```sql
SELECT a.ticker, a.quarter AS q1, b.quarter AS q2, (b.quarter - a.quarter) AS days_apart
FROM financials_quarterly a
JOIN financials_quarterly b
  ON a.ticker = b.ticker AND b.quarter > a.quarter AND b.quarter - a.quarter <= 5
ORDER BY a.ticker, a.quarter;
```

## Appendix D — Reusable Python & Git

**EDGAR dry-run harness (read-only; test extraction before any reload). Save as a throwaway `verify_amd.py` in `etl/`, run `python etl\verify_amd.py`:**
```python
from edgar_backfill import fetch_company_facts, build_quarter_rows, TICKER_TO_CIK

facts = fetch_company_facts(TICKER_TO_CIK["AMD"])
rows = sorted(build_quarter_rows("AMD", facts), key=lambda x: x["quarter"])
print(f"AMD quarters extracted: {len(rows)}")
for r in rows:
    print(f"{r['quarter']}  revenue={r['revenue']/1e9:6.2f}B")
# checkpoint: ~19-20 quarters, 2022-09 ≈ $5.57B, Dec quarters present, no 182-day gaps
```

**Non-destructive source-fix test from a notebook (reload module + run a function — how the Day-14 CDNS fix was verified):**
```python
import sys, os, importlib
sys.path.insert(0, os.path.abspath("../etl"))   # scripts live in etl/, notebooks in analysis/
import edgar_backfill
importlib.reload(edgar_backfill)                 # pick up edits without a kernel restart (save the file first!)

facts = edgar_backfill.fetch_company_facts("0000813672")   # CDNS
rd = edgar_backfill.extract_quarterly_series(facts, edgar_backfill.CONCEPT_CANDIDATES["rd_spend"])
from datetime import date
print("Q4 2025 present:", date(2025, 12, 31) in rd, "| value:", rd.get(date(2025, 12, 31)))
```

**Gap check across the 9 (missing = >120 days, duplicate = <80; expect none):**
```python
tmp = core.sort_values(["ticker","quarter"]).copy()
tmp["gap"] = tmp.groupby("ticker")["quarter"].diff().dt.days
flags = tmp[(tmp["gap"].notna()) & ((tmp["gap"] < 80) | (tmp["gap"] > 120))]
print(core.groupby("ticker").size().to_string())
print("none" if flags.empty else flags[["ticker","quarter","gap"]].to_string(index=False))
```

**Spearman + Pearson (native pandas — no scipy needed; report with n, NOT a percentage):**
```python
cols = ["ai_pct", "Software & Firmware", "rd_intensity", "operating_margin"]
spearman = signals[cols].corr(method="spearman")   # works without scipy (confirmed Day 15)
pearson  = signals[cols].corr()                    # Pearson (default)
# equivalent alternative: signals[cols].rank().corr()  # Spearman = Pearson on ranks
# 10_financials: core[["rd_intensity","operating_margin"]].corr(method="spearman").iloc[0,1]  # ≈ -0.80, n=9
```

**Find which frame holds a column (used Day 15 to hunt the snapshot-date frame):**
```python
print([k for k, v in globals().items()
       if isinstance(v, pd.DataFrame) and "snapshot_date" in v.columns])
```

**Git pattern (explicit paths, never `git add -A`):**
```powershell
git add analysis/<notebook>.ipynb etl/<script>.py interview_moments.md
git add analysis/<chart1>.png analysis/<chart2>.png
git commit -m "<action-first description>"
git push
git log --oneline -1        # CONFIRM it landed
```

## Appendix E — Signature chart code (faceted trends)

Palette + 3×3 faceted small multiples, colored by segment, grey backdrop of the other 8. Produces `revenue_trends.png` and `margin_trends.png`:
```python
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

order  = ["NVDA","AMD","QCOM","AVGO","MRVL","CDNS","INTC","MU","TXN"]   # rows group by segment
seg    = {"NVDA":"Fabless","AMD":"Fabless","QCOM":"Fabless","AVGO":"Fabless","MRVL":"Fabless",
          "INTC":"IDM","MU":"IDM","TXN":"IDM","CDNS":"EDA"}
colors = {"Fabless":"steelblue","IDM":"#e07b39","EDA":"seagreen"}

for metric, title, fname in [
    ("rev_idx", "Revenue Growth Since 2021 (indexed, first quarter = 100)", "revenue_trends.png"),
    ("operating_margin", "Operating Margin Over Time (%)", "margin_trends.png"),
]:
    d = core.sort_values("quarter").copy()
    d["rev_idx"] = d.groupby("ticker")["revenue"].transform(lambda s: s / s.iloc[0] * 100)
    if metric == "operating_margin":
        d[metric] = d[metric] * 100

    fig, axes = plt.subplots(3, 3, figsize=(18, 13), sharex=True, sharey=True)
    for ax, t in zip(axes.flat, order):
        for other in order:                       # grey backdrop = the other 8
            s = d[d["ticker"] == other]
            ax.plot(s["quarter"], s[metric], color="lightgrey", linewidth=0.9, zorder=1)
        s = d[d["ticker"] == t]
        ax.plot(s["quarter"], s[metric], color=colors[seg[t]], linewidth=2.0, zorder=3)
        ax.set_title(f"{t}  ·  {seg[t]}", fontsize=11)
        ax.tick_params(labelsize=9)
    if metric == "rev_idx":
        axes[0, 0].set_yscale("log")             # sharey propagates log to all
    fig.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.show()
```
*Snapshot charts (bars + the two scatters) live in `10_financials.ipynb`; the intensity-vs-margin scatter and revenue-vs-R&D scatter both use the same `seg`/`colors` dicts, `set_yscale("log")` on the revenue scatter, and hand-tuned label offsets to avoid overlap.*

## Appendix G — Cross-signal build (`20_cross_signals.ipynb`)

*The classifier (`ROLE_RULES` + `AI_PAT`, 13 buckets, first-match-wins) is copied verbatim from `03_hiring_category.ipynb` — see that notebook; keep `03` untouched. Reconciles at ~4% unclassified / ~9.4–9.6% AI depending on snapshot day.*

**Per-ticker hiring features** (after the classifier tags `df["role_bucket"]` and `df["is_ai"]` on the current snapshot):
```python
ai = (df.groupby("ticker")["is_ai"].agg(ai_jobs="sum", n_jobs="count"))
ai["ai_pct"] = (ai["ai_jobs"] / ai["n_jobs"] * 100).round(1)
ai = ai.sort_values("ai_pct", ascending=False)

mix = pd.crosstab(df["ticker"], df["role_bucket"], normalize="index").mul(100).round(1)
mix = mix[df["role_bucket"].value_counts().index]      # columns ordered by overall size
```

**TTM merge → the `signals` frame (9 × 20).** Collapses each ticker to one trailing-4-quarter row (revenue-weighted ratios), robust to any in-window R&D null via `rev_rd` + `rd_qtrs`:
```python
# Financial side: collapse each ticker to ONE trailing-4-quarter (TTM) row
core = core.sort_values(["ticker", "quarter"])
last4 = core.groupby("ticker").tail(4).copy()

# completeness guard — want q=4 and zero NaNs per ticker before trusting the sums
chk = last4.groupby("ticker").agg(
    q=("quarter", "size"),
    rev_na=("revenue", lambda s: s.isna().sum()),
    rd_na=("rd_spend", lambda s: s.isna().sum()),
    om_na=("operating_margin", lambda s: s.isna().sum()),
)
print("TTM window (want q=4, all *_na=0):"); print(chk.to_string())
print(f"\nwindow spans {last4['quarter'].min().date()} … {last4['quarter'].max().date()} "
      f"(fiscal calendars differ, so per-ticker windows vary slightly)\n")

last4["op_income"] = last4["operating_margin"] * last4["revenue"]   # margin stored as a fraction
g = last4.groupby("ticker")
rev_rd = last4.loc[last4["rd_spend"].notna()].groupby("ticker")["revenue"].sum()  # match rev to R&D availability
fin_ttm = pd.DataFrame({
    "rd_intensity":     g["rd_spend"].sum() / rev_rd,                    # numerator & denom over same quarters
    "rd_qtrs":          g["rd_spend"].apply(lambda s: s.notna().sum()),  # quarters backing it (4 = full)
    "operating_margin": g["op_income"].sum() / g["revenue"].sum(),       # fraction; ×100 for %
})

# Merge: hiring features + TTM financial profile, one row per ticker
SEGMENT = {"NVDA":"Fabless","AMD":"Fabless","QCOM":"Fabless","AVGO":"Fabless","MRVL":"Fabless",
           "INTC":"IDM","MU":"IDM","TXN":"IDM","CDNS":"EDA"}
signals = (ai[["n_jobs", "ai_pct"]].join(mix).join(fin_ttm))
signals.insert(0, "segment", signals.index.map(SEGMENT))
print(signals.shape, "→ 9 tickers ×", signals.shape[1], "cols")
signals.round(3)
```

**Q1 — correlations (hiring vs financials):**
```python
cols = ["ai_pct", "Software & Firmware", "rd_intensity", "operating_margin"]
print("Spearman:\n", signals[cols].corr(method="spearman").round(2))
print("\nPearson:\n",  signals[cols].corr().round(2))
# result: all hiring↔financial pairs in [-0.10, +0.25]; ai_pct↔software 0.80/0.78 (both hiring metrics). n=9.
```

**Q2 — segment role-mix heatmap (`role_mix_by_segment.png`, raw %):**
```python
import matplotlib.pyplot as plt
import seaborn as sns

non_role = ["segment", "n_jobs", "ai_pct", "rd_intensity", "operating_margin", "rd_qtrs"]
role_cols = [c for c in signals.columns if c not in non_role]

seg_mix = signals.groupby("segment")[role_cols].mean().round(1)
spread  = (seg_mix.max() - seg_mix.min()).sort_values(ascending=False)   # which buckets separate segments
seg_order = ["IDM", "Fabless", "EDA"]                                    # manufacturing pole -> software pole
seg_mix = seg_mix.loc[seg_order, spread.index]
seg_mix.index = [f"{s} (n={(signals['segment'] == s).sum()})" for s in seg_order]

plt.figure(figsize=(6.5, 8))
sns.heatmap(seg_mix.T, annot=True, fmt='.1f', cmap='YlGnBu',
            linewidths=0.7, linecolor='black',
            cbar_kws={'label': "% of segment's mean postings"})
plt.title("Role Mix by Segment — mean % of each segment's open roles\n(EDA = CDNS only, n=1)",
          fontsize=12, pad=12)
plt.xlabel(""); plt.ylabel("")
plt.tight_layout()
plt.savefig("role_mix_by_segment.png", dpi=150, bbox_inches="tight")
plt.show()
# result: Manufacturing ~20pt spread (IDM 29 vs ~10), Software ~17pt (EDA 22 > Fabless 17 > IDM 5); rest flat.
```

## Appendix H — AI-hiring cut (`20`, Day 15)

**Cell 4 — snapshot load with the date carried out** (the fix; see §9 Day 15). The `WHERE` was always right — it just never let the date escape:
```python
df = pd.read_sql("""
    SELECT snapshot_date, ticker, title
    FROM hiring_signals
    WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM hiring_signals)
""", engine)

assert df["snapshot_date"].nunique() == 1, "expected exactly one snapshot date"
SNAP_DATE = df["snapshot_date"].iloc[0]
print(df.shape, "|", df["ticker"].nunique(), "tickers | snapshot", SNAP_DATE)
```
- `assert` can't fail today (one `MAX()` = one date). It's for the day someone edits the WHERE to a date range and forgets that everything downstream assumes one day — fails at the source instead of silently averaging two days under one date stamp.
- `.iloc[0]` over `.max()`: identical result given the assert, but `.iloc[0]` **declares the assumption** (*I expect one value*) rather than implying many.

**`ai_pct_by_ticker.png`** — sorted bar, segment-colored, proxy legend, welded caveat:
```python
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
# SNAP_DATE comes from Cell 4 — must originate in the frame that BUILT signals,
# never a fresh SELECT MAX(), which would stamp today's date on a stale frame.

PALETTE = {"Fabless": "steelblue", "IDM": "#e07b39", "EDA": "seagreen"}
d = signals[["segment", "ai_pct", "n_jobs"]].sort_values("ai_pct", ascending=False)  # sort ONCE

fig, ax = plt.subplots(figsize=(9.5, 5.5))
bars = ax.bar(range(len(d)), d["ai_pct"],                       # ints, not strings: we own the axis
              color=[PALETTE[s] for s in d["segment"]], edgecolor="black", linewidth=0.5)

for b, pct in zip(bars, d["ai_pct"]):                           # value labels, positioned off the bars
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.25,
            f"{pct:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

# ticker + posting base on the axis — the denominator matters (MU posts most, leans AI least)
ax.set_xticks(range(len(d)))
ax.set_xticklabels([f"{t}\nn={n:,}" for t, n in zip(d.index, d["n_jobs"])], fontsize=9)

# proxy legend: ax.bar() with a color list makes ONE container — matplotlib doesn't know
# steelblue "means" Fabless, so ax.legend() alone renders nothing. These are swatches.
handles = [plt.Rectangle((0, 0), 1, 1, color=c, ec="black", lw=0.5) for c in PALETTE.values()]
ax.legend(handles, PALETTE.keys(), title="Segment", loc="upper right", frameon=True)

ax.set_ylabel("AI-titled roles (% of open postings)")
ax.set_ylim(0, d["ai_pct"].max() * 1.18)                        # headroom scales with the data
ax.set_title(f"AI-Titled Hiring Share by Ticker — snapshot {SNAP_DATE}\n"
             f"{d['n_jobs'].sum():,} open postings across 9 tickers",
             fontsize=13, pad=12)

# fig.text (figure coords), not ax.text — the two-line tick labels occupy the space
# under the axes. bbox_inches="tight" is what pulls this into the saved PNG.
fig.text(0.5, -0.02,
         "Share of open postings whose title matches an AI keyword — a measure of title language, not verified AI work.",
         ha="center", fontsize=8.5, style="italic", color="#444")

plt.tight_layout()
plt.savefig("ai_pct_by_ticker.png", dpi=150, bbox_inches="tight")
plt.show()
```

**Sanity check used to catch the stale frame** — `d["n_jobs"].sum()` must equal the current snapshot's row count from Appendix C's pipeline-health query. An exact match to *yesterday's* count is the smell.

## Appendix F — Most recent interview moments (quick form; full history in `interview_moments.md`)

**1. EDGAR backfill bug (Day 13):**
> Spotted AMD revenue "dropping" 54% during the AI boom — impossible. Traced it to EDGAR storing 9-month YTD totals under the same label as discrete quarters; my code grabbed the wrong one. Fixed by filtering on period *duration*, deriving Q4 = full-year − 9-month. Dry-ran on one ticker, reloaded to 215 clean rows. Lesson: sanity-check against the source; a number that contradicts reality is a bug.

**2. Snapshot vs. trend (Day 13):**
> Micron ranked #1 on margin (67.6%) in one quarter — but the 5-year trend showed it's a cyclical peak (−60% → 80%), while Nvidia holds ~65% steadily. Lesson: a snapshot ranks companies, a trend explains them. Product type, not segment label, drives the pattern.

**3. CDNS Q4 R&D — XBRL concept-fallback (Day 14):**
> CDNS Q4 2025 R&D came back null. Q4 is derived (annual − 9-month YTD) since 10-Ks report only the full year. First guessed a fiscal-calendar mismatch, but pulled the raw EDGAR facts and every period start matched — dead theory. Real cause: Cadence tags full-year R&D under a different XBRL concept (...SoftwareExcludingAcquiredInProcessCost) than its quarterlies, and the extractor returned on the first concept with data — plus that concept wasn't even in the candidate list. Fixed by adding the concept and gathering across all of them (primary wins on a period collision). Lesson: the same line can live under sibling concepts across filings; don't stop at the first tag, and diagnosing beat guessing.

**4. The correlation that wasn't / cross-signal contrast (Day 14):**
> Two cross-signal cuts. Q1: hiring tilt vs financial ratios (R&D intensity, margin) — Spearman across 9 tickers, all pairs −0.10 to +0.25, basically independent. Q2: role mix vs business model — Manufacturing splits IDMs (~29%) from fabless/EDA (~10%), Software splits EDA/fabless from IDMs. The result is the contrast: financial ratios don't predict hiring tilt, but structure does — hiring encodes what KIND of company you are, not how it's performing. Lesson: a predictor that fails next to one that works is a stronger finding than either alone. Caveats kept on-chart: n=9 directional; EDA = CDNS (n=1); ai_pct = the word "AI," not verified AI work.

**5. The chart that knew what day it was (Day 15):**
> My notebook pulled the latest hiring snapshot with `WHERE snapshot_date = (SELECT MAX(...))` — correct, but it only selected ticker and title. So the frame was a real snapshot of a real day with no record of *which* day. I ran it before my 09:17 cron landed, got yesterday's data, and it looked identical to today's. Only caught it because the job counts summed to exactly the prior day's total. Fix was one column: select the date, assert it's singular, print it. Now the date travels with the data — which matters more than it sounds, because the dashboard has to state its own as-of date and my chart titles are generated from that frame.

**6. The claim my own data killed (Day 15):**
> I thought I'd found something good: my AI-hiring metric only reads job titles, so a company could be heavily AI-exposed and still score near zero if it titles reqs by engineering discipline. Marvell looked like proof — custom AI silicon, dead last at 1.3%. Then I checked its software/firmware share: 5.8%, also near the bottom. Which puts it *on* my ρ=0.80 trend line, not off it. A metric can only be proven blind to something you can independently measure, and I have no AI-exposure ground truth in my schema. So I downgraded the claim from "my metric is blind" to "my metric is confounded with software staffing" — which is what the data supports. It also told me why the patents pipeline is worth building: AI-classified patents by assignee would be the independent measure that breaks the tie.

**7. The hypothesis my chart refuted (Day 15):**
> I predicted AI-titled hiring would split fabless from IDM. Sorted the bar chart and fabless held 1st, 2nd, 3rd — and 6th and 9th, spanning almost the whole range. Segment didn't predict it at all. That's the same result I'd found in the financials, where R&D intensity tracked product type rather than segment label — showing up again in a completely different dataset. The interesting part is the contrast with my other hiring cut: segment predicts *role mix* very cleanly, and predicts *AI tilt* not at all. Two hiring metrics, two different answers about the same variable, so "segment predicts hiring" is too coarse to be true.

**8. Finding the blocker before building on it (Day 15):**
> My plan was a live Tableau Public dashboard reading from my Postgres database. Before installing anything I checked whether that was even possible — it isn't. Tableau Public takes files, Google Sheets, and web data connectors, and publishes extracts only; external database connections are refused by design. I checked Power BI too and it was worse for my situation: publishing publicly needs a tenant admin setting, and I'd be on my university's tenant. So I extended my existing GitHub Actions cron to publish aggregates to a Google Sheet, which Tableau Public auto-refreshes every 24 hours. Two searches instead of a wasted day. The part I'd emphasize: the bridge is tool-agnostic — Power BI reads Sheets too, so if I want a Power BI version later it's the same pipeline. And the honest framing is "daily-refreshed," not "real-time," because I don't control Tableau's refresh clock.