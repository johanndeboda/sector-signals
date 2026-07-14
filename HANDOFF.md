# HANDOFF.md — Sector Signals

*Last updated: Day 14 session (2026-07-14). Cross-signal notebook (`20_cross_signals.ipynb`) built — two findings landed (hiring tilt is independent of financial ratios; role mix tracks business model). CDNS fiscal-Q4 R&D null root-caused to an XBRL concept-fallback and fixed at source (committed `76c4315`). Trends deferred on a timescale basis; dashboard is the next major track after a short AI-hiring cut. Appendices A–G hold reusable code/SQL/analysis so nothing here requires re-reading old chats.*

---

## §0 — How to use this handoff
- Johann pastes this at the start of each session; Claude reads it **fully** before acting.
- Claude opens by confirming state, naming any scope trade-offs **with a recommendation**, then works **one step at a time**.
- Claude closes each session with a day summary + drafted interview moments, unprompted.
- **Verify live state — don't trust this doc blindly.** The pipeline runs daily and tables change; a quick DB check (snapshot series, row counts) beats assuming. This doc has been stale before (it once claimed patents/financials weren't built).
- **Claude cannot run code, hit the DB, or reach the network from chat.** Claude writes cells/commands; Johann runs them and pastes output; Claude iterates.

**How to WRITE the next handoff (same way every time):** re-read the current `HANDOFF.md` in full and **diff against it — never rebuild from memory** (a dropped-content incident established this rule). Update the dynamic sections (§4 when repo changes, §6 data state, §9 progress log — append the new day, §10 roadmap, §12 open items, §13 next-session). Preserve and keep current the static sections (§0–§3, §5, §7, §8, §11 principles — append, don't trim). Keep `[CONFIRM]` markers honest. Never over-sharpen prior findings (§5.10). Record mistakes so they aren't repeated. Keep the section structure identical session to session. Johann replaces the repo's `HANDOFF.md` with the new version and commits it.

## §1 — Project purpose & thesis
Sector Signals is a portfolio data-engineering + analytics project to land a **data/business analyst internship**. Core thesis: **hiring patterns, patent activity, and financial signals surface strategic shifts before they show up in earnings** — anchored in AI's reshaping of the semiconductor industry.
- **12 tickers:** 9 hiring-active (AMD, AVGO, CDNS, INTC, MRVL, MU, NVDA, QCOM, TXN) + SNPS, ANSS, TSM (seeded, hiring-inactive).
- **Recruiting:** Wave 1 = July–Oct 2026 (primary); Wave 2 = Dec 2026–Feb 2027.
- **Repo:** github.com/johanndeboda/sector-signals
- **AI framing guardrail:** AI is the narrative backdrop, not a proven cause. Data can show *timing/correlation* aligned with the AI buildout — **never causation** (see §5.10).

### §1a — The 12 tickers at a glance (reference)
**Fabless** (design chips, outsource fab to TSMC):
- **NVDA (Nvidia)** — GPUs + CUDA software moat; dominant AI/datacenter accelerator. Highest *absolute* R&D ($5.5B) but *lowest* intensity (8.1%) because revenue outran it; margin ~65%.
- **AMD** — CPUs (Ryzen/EPYC) + GPUs (Instinct); challenges Intel (x86) and Nvidia (AI GPU). Intensity 23.4%, margin 14.4%.
- **QCOM (Qualcomm)** — mobile SoCs (Snapdragon) + wireless/modem IP; pushing into datacenter. Intensity 23.2%, margin 21.8%.
- **AVGO (Broadcom)** — networking + custom ASICs + high-margin software (VMware). Intensity 15.4%, margin 44.3%.
- **MRVL (Marvell)** — data-infra silicon (networking, storage, custom compute, optical). Intensity 24.2%, margin 18.7% (but negative through much of 2022–24; see §9).

**IDM** (design *and* own fabs):
- **INTC (Intel)** — leading-edge logic (x86 CPUs) built in-house, mid-turnaround. High intensity (24.9%), thin margin (6.9%).
- **MU (Micron)** — memory (DRAM/NAND/HBM); competes on capex, not R&D-per-dollar. Lowest intensity (5.2%), highest *snapshot* margin (67.6%) — but cyclical (§9).
- **TXN (Texas Instruments)** — analog & embedded, huge catalog, owns fabs. Low intensity (10.6%), durable margin (37.8%).

**EDA** (software to design chips — Johann's Cadence turf):
- **CDNS (Cadence)** — design/verification software + IP. R&D *is* the product → **highest** intensity (34.5%), margin 29.3%.

**Inactive:** SNPS (Cadence's larger EDA rival; TalentBrew anti-bot) · ANSS (simulation; acquired by Synopsys, data ends Q1'25) · TSM (leading pure-play foundry; anti-bot + reports in TWD).

*(Fabless = design only; IDM = design + own fabs; EDA = design software; Foundry (TSM) = manufactures others' designs. Logic = "thinking" chips that compute; memory = stores data; analog = senses/controls the physical world. "Leading-edge logic" = compute chips on the smallest, most capital-intensive process nodes — INTC's cost problem.)*

*(Note: the intensity/margin figures above are the `10_financials` snapshot values, computed on each ticker's latest single quarter. The cross-signal notebook `20` uses a **trailing-4-quarter (TTM)** recompute for the join, so its per-ticker intensity/margin differ slightly — different metric, both correct. See §9 Day 14 and Appendix G.)*

## §2 — Domain foundation
Prior consulting engagement with **Cadence Design Systems** via the SJSU Marketing Association: competitive analysis, careers-page audits, Generative Engine Optimization (GEO) analysis. Direct narrative thread — CDNS is one of the 12 tickers, and the planned AI insight layer ties back to the GEO work.

## §3 — Environment & stack
- **OS/shell:** Windows 11, PowerShell (flag PS vs Python vs SQL explicitly in commands).
- **Editor:** VS Code; notebooks run in VS Code Jupyter.
- **Python:** venv at `C:\Users\Johan\sector-signals\venv`.
- **psql:** full path required — `C:\Program Files\PostgreSQL\18\bin\psql.exe`.
- **DB:** Neon cloud PostgreSQL; creds in `.env` (gitignored) at repo root. Neon SQL Editor is the quick way to run ad-hoc SQL.
- **Stack:** pandas, matplotlib, seaborn, SQLAlchemy, BeautifulSoup, requests; yfinance (prices only — deprecated as a financials source, see §6). **scipy is NOT installed** — get Spearman via `.rank().corr()` (Spearman = Pearson on ranks); install scipy only if the stats get heavier (see §12, Appendix D).
- **Secrets in `.env`:** DB creds, `ANTHROPIC_API_KEY`, `USPTO_ODP_API_KEY`, `SEC_USER_AGENT_EMAIL`. `.env.example` documents variables with placeholders. **Never commit `.env`.** (Known parse warning — see §12.)
- **Kernel gotcha:** the SQLAlchemy `engine` holds open Neon sockets; a kernel that touched the DB can hang on restart. Run `engine.dispose()` before restarting, or `Get-Process python | Stop-Process -Force` to clear a stuck kernel. **Neon drops idle pooled connections** → `PendingRollbackError` mid-session; the connection cell now uses `pool_pre_ping=True` + `pool_recycle=300` (Appendix A) — put this in **every** notebook's Cell 0, not just the loader. Run scripts from the **repo root** so `load_dotenv()` finds `.env`.
- **PowerShell quoting:** `python -c "..."` with nested quotes/braces fails in PS. Use a small script file (e.g. a throwaway `verify_*.py`) or single-quote-only one-liners.
- **Notebook↔script imports:** notebooks live in `analysis/`, scripts in `etl/`. To import a script from a notebook, add the etl folder to the path first: `sys.path.insert(0, os.path.abspath("../etl"))`. (Confirmed Day 14 — the repo root is empty of `.py` files; scripts are all under `etl/`.)

## §4 — Repo structure
- **`etl/`** — `load_hiring.py`, `load_financials.py` (yfinance; deprecated for financials), `edgar_backfill.py` (financials, authoritative — **concept-gather fix landed Day 14**), `load_patents.py`, `download_patents.py`, `assignee_mapping.py`, `explore_assignees.py`, `detect_ats.py`, `test_bulk_download.py`.
- **`analysis/`** — `01_hiring_snapshot.ipynb`, `02_hiring_geography.ipynb`, `03_hiring_category.ipynb`, `10_financials.ipynb`, **`20_cross_signals.ipynb` (built Day 14 — note the PLURAL name)**, `04_hiring_trends.ipynb` (reserved/deferred — see §10). PNG exports live here (`rd_intensity_by_ticker.png`, `rd_vs_revenue.png`, `operating_margin_by_ticker.png`, `intensity_vs_margin.png`, `revenue_trends.png`, `margin_trends.png`, `role_mix_heatmap.png`, **`role_mix_by_segment.png`**).
- **`sql/`** — `schema.sql`.
- **`.github/`** — Actions workflow(s) (`scrape.yml`).
- **Root:** `.env`, `.env.example`, `HANDOFF.md`, `interview_moments.md`, `README.md`, `requirements.txt`, `.gitignore`. (No `.py` files at root — all scripts are under `etl/`.)
- **Notebook numbering convention:** `0x` = hiring (01 snapshot, 02 geography, 03 category, 04 trends-reserved); `1x` = financials (10); `2x` = cross-signal (**20 built**).

## §5 — Working style / collaboration protocol
*(Subsection numbers below are reconstructed — cross-check against your on-disk copy if a specific §5.x reference matters; the content is complete.)*
- **§5.1 Session ritual:** paste handoff → read fully → confirm state → one step at a time → close with day summary + interview moments.
- **§5.2 Decision-making:** Johann defers to Claude's judgment when trade-offs aren't clear, but wants a **concise trade-off summary → a committed recommendation**, not balanced options.
- **§5.3 Surface judgment calls:** name scope trade-offs and decisions explicitly, with a recommendation; let Johann decide.
- **§5.4 Profile before you build:** for any new data work, run a profiling/coverage query first (per-entity counts, ranges, NULL-aware column counts) before analysis or charts.
- **§5.5 Build iteratively:** hand cells/changes in stages; Johann runs + pastes; refine from real output. No large blind notebooks.
- **§5.6 Claude can't run code:** no DB/network in chat. Johann executes and reports before proceeding.
- **§5.7 Don't pre-build** ahead of pending decisions (e.g., no notebook before the naming/approach is chosen).
- **§5.8 Observation ownership:** Johann writes observations in his own voice. Claude gives **guided prompts** (numbers + the question each is really asking) and **pressure-tests** — never ghostwrites. Shape: situation → finding → action → lesson.
- **§5.9 Teach as you go:** Johann reviews code at "shape and logic" level, does a secondary pass with ChatGPT. Do walkthroughs first when asked; explain design choices.
- **§5.10 Attribution guardrails:** don't sharpen observations into claims the data can't support. No AI causal claims from financials alone; no workforce-trend claims without time-series. Financials × AI = timing/correlation only. Two prior over-attribution errors logged as "do not repeat."
- **§5.11 Primary-source verification:** any figure entering the public portfolio must be checked against 10-K/10-Q (or equivalent) before commit.
- **§5.12 Code-change & output conventions:** deliver changes as concise **before/after/why/logic** — exact old-and-new for substitutions, not full-file rewrites. **Keep notebook outputs intact** (charts render on GitHub for recruiters). Use explicit file paths. Flag PS vs Python vs SQL. Interview moments = **quick and simple** (Johann's stated preference — short reminders, not prose).
- **§5.13 Don't silently rescope:** when work would expand scope (e.g., folding cross-signal into another notebook), name it and get a decision.

## §6 — Data sources & database
- **Financials:** SEC EDGAR Company Facts API (`edgar_backfill.py`) is the **single source of truth** for the 11 US filers. yfinance is **deprecated as a financials source** — its calendar-month-end dating conflicts with EDGAR's fiscal-end dating and created upsert-invisible duplicate rows. TSM excluded from EDGAR (foreign filer, 20-F).
  - *How extraction works:* pull `companyfacts/CIK{cik}.json`, walk `facts.us-gaap.<concept>.units.USD`, and per metric **gather facts across ALL candidate XBRL concept names** (companies tag the same idea differently — and even tag it differently across filings). Bucket facts by period **duration** (80–100d = discrete quarter, 250–295d = 9-month YTD, 350–380d = full year), keep discrete quarters, derive Q4 = full-year − 9-month YTD matched on shared `start` date. **Concept candidates:** revenue → `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `...IncludingAssessedTax`, `SalesRevenueNet`; R&D → `ResearchAndDevelopmentExpense`, `...ExcludingAcquiredInProcessCost`, **`...SoftwareExcludingAcquiredInProcessCost`** (third variant added Day 14); net income → `NetIncomeLoss`, `ProfitLoss`; operating income → `OperatingIncomeLoss`. Operating margin = operating income ÷ revenue (a fraction; ×100 for display).
  - *Day 14 concept-gather fix:* the old extractor **returned on the first concept that had any data**, so an annual tagged under a sibling concept was never seen (CDNS files quarterlies under `ResearchAndDevelopmentExpense` but its 10-K annual under `...SoftwareExcludingAcquiredInProcessCost`). Now facts accumulate across **all** candidate concepts; candidates are tried in priority order and, on a period collision, **the earlier-listed concept wins — later ones only fill gaps** (so a subset tag can't override a real quarterly value). Full post-fix code in **Appendix B**.
- **Hiring:** ATS APIs — Workday, Jibe/iCIMS, Eightfold, Oracle HCM Cloud. SNPS (TalentBrew/Avature) and TSM disabled (anti-bot; Playwright not justified for 2 tickers).
- **Patents:** PatentsView bulk TSV (S3) + USPTO ODP API.
- **Stock prices:** yfinance (still used — only financials deprecated).
- **Tables & row counts:**
  - `hiring_signals` — daily snapshots, 9 tickers/day. **25 consecutive clean 9/9 days, 06-17 → 07-11** (verified this session; cron continues daily — re-verify at session start).
  - `financials_quarterly` — **215 rows** (208 EDGAR + 7 TSM), 12 tickers. Columns: `ticker, quarter (date-string, ISO), revenue, rd_spend, net_income, operating_margin`. Composite PK `(ticker, quarter)`. The 9 hiring-active tickers each have **18–20 clean discrete quarters**. **CDNS fiscal Q4 2025 R&D (`2025-12-31`) was NULL; filled Day 14 = 464,582,000** (annual 1,768,772k − 9-month YTD 1,304,190k); every hiring-active ticker now has a complete trailing-4-quarter window (verified via the cross-signal completeness guard). *(Primary-source check on the CDNS annual still open — §12.)*
  - `stock_prices_daily` — ~13,805 rows *(per prior handoff; verify)*. PK `(ticker, date)`.
  - `patents` — ~61,519 rows loaded *(per prior handoff; verify)*. Assignee normalization / entity resolution = future work.

## §7 — Chart conventions
- seaborn `whitegrid`; matplotlib. Full palette + facet pattern in **Appendix E**.
- Single-series bars: `steelblue`. **Segment palette (reuse everywhere):** Fabless = `steelblue`, IDM = `#e07b39`, EDA = `seagreen`.
- Data labels via `ax.text`/`annotate`; `figsize` sized to content; `plt.tight_layout()`.
- **Save before show:** `plt.savefig("name.png", dpi=150, bbox_inches="tight")` → `plt.show()`. PNGs into `analysis/`.
- **Log scale** for wide dynamic range (e.g., revenue across ~45×); prefer real-unit tick labels over bare powers of ten.
- **Facet** (3×3 small multiples with a grey backdrop of the other series) when >6 lines tangle on one axis — used for the financials trend charts.
- **Heatmaps** (role mix): `sns.heatmap`, `cmap='YlGnBu'`, `annot=True, fmt='.1f'`, black gridlines (`linewidths=0.7, linecolor='black'`) — used by `03`'s role-mix-by-ticker and `20`'s role-mix-by-segment so both render consistently on GitHub.

## §8 — Git workflow
- **Explicit file paths only — never `git add -A`.** Each workstream committed separately.
- Keep notebook outputs in commits.
- `.env` gitignored, never staged; `.env.example` (placeholders) committed.
- Descriptive, action-first commit messages. Pattern in **Appendix D**.
- **Before staging a re-run notebook:** `git diff --stat` it — a 1-line diff is usually just an `execution_count` bump (`git restore` it to keep noise out). Clean throwaway/diagnostic cells out of any notebook a recruiter will open (esp. `20`).

## §9 — Current state / progress log

**Pipeline (automation):**
- GitHub Actions cron daily 09:17 UTC + `workflow_dispatch`; Neon creds as repo secrets.
- Completeness guard live (`sys.exit(1)` on partial runs — won't write a partial snapshot).
- **25 consecutive clean 9/9 snapshots, 06-17 → 07-11**, zero intervention. Pre-guard partials (06-16 6/9, 06-11 6/9) predate the guard.

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
- **Q1 — hiring tilt vs financial ratios: independent.** Spearman (via `.rank().corr()`, no scipy) across the 9 tickers: every hiring↔financial pair sits between **−0.10 and +0.25** — no meaningful correlation with `rd_intensity` or `operating_margin`. (`ai_pct` ↔ `Software & Firmware` is strong at **0.80 Spearman / 0.78 Pearson** — but both are *hiring* metrics, one software-forward posture showing up twice, not hiring predicting something independent.) n=9 → directional, not significance-grade. Correlation ≠ causation; `ai_pct` = the word "AI" in a title, not verified AI work.
- **Q2 — role mix vs business model (value-chain position): tracks sharply.** Segment × role-mix heatmap (`role_mix_by_segment.png`, raw %, YlGnBu). Two role types separate segments hard: **Manufacturing & Process** (IDM 29.4% vs Fabless/EDA ~10%, ~20pt spread — IDMs own fabs) and **Software & Firmware** (EDA 22.5% > Fabless 16.6% > IDM 5.1%, ~17pt — EDA sells software). Everything below the top three buckets is roughly flat across segments. **EDA = CDNS alone (n=1)** — every EDA cell is one company (the elevated Sales/Field share for EDA is CDNS-specific too); stated on-chart.
- **The result is the contrast:** financial *ratios* don't predict hiring tilt (Q1), but business *model* does (Q2). **Hiring encodes what kind of company you are, not how it's performing financially.** A predictor that fails next to one that works is a stronger finding than either alone.

**Decisions made this session:**
- **`04_hiring_trends` deferred on a timescale basis (not skipped):** 25–30 daily snapshots can't distinguish *strategic* hiring shifts (quarters-to-years, plus annual budget/new-grad cycles) from short-horizon noise. A month can support *operational* reads (velocity, mix drift, churn) but not the strategic-signal claim that would differentiate it. Unlocks at ≥1 quarter, ideally a year; the cron keeps banking dated snapshots so "future work" has a real mechanism. Good interview line as a *deferred-with-a-reason* item.
- **Sequencing set:** AI-pct cut (1–2 days, descriptive) → dashboard v1 (Tableau Public; **de-risk spike first**) → AI insight layer. Trends slots in when the window matures.
- **Dashboard reality flagged:** Tableau Public (free) almost certainly can't live-connect to Neon — plan a periodic **Neon → CSV/extract → Tableau Public** path; the "live system" stays the daily Actions scrape → Neon, with Tableau a refreshed snapshot. Confirm via the spike (Tableau tiers shift). Rough estimate: dashboard = **4–7 focused days** (0.5 spike / 1–1.5 data-prep / 2–3 build / 1 polish+publish+README) — swings on prior Tableau experience.

**Committed this session:** `etl/edgar_backfill.py` (concept-gather fix — `76c4315`, pushed) as its own commit; then `analysis/20_cross_signals.ipynb` + `analysis/role_mix_by_segment.png` + `interview_moments.md` as the cross-signal checkpoint. `03_hiring_category.ipynb` re-run churn reverted (kept untouched).

**Interview moments logged this session** (`interview_moments.md`; quick form in **Appendix F**): (3) CDNS Q4 XBRL concept-fallback; (4) the correlation that wasn't / cross-signal contrast.

## §10 — Roadmap / what's next
1. **AI-hiring cut (`20`, descriptive) — NEXT, 1–2 days.** Not a new notebook — same `signals` frame, same tools. The *statistical* question is already answered (Q1: `ai_pct` is flat vs financials). The cut is **descriptive**: who leans into AI-titled hiring — NVDA 18.3, QCOM 15.3, AMD 11.8 lead; IDMs (MU 2.5, TXN 1.5) trail — and the fabless-vs-IDM pattern in it. One viz (sorted `ai_pct` bar colored by segment) + Johann's read. Carry the caveat: `ai_pct` = the word "AI," not verified AI work. Adds a third dashboard tile; not a deep result, and that's fine.
2. **Dashboard v1 (capstone).** Build on the two cross-signal findings + the AI-pct cut (3 tiles: segment role-mix heatmap, `ai_pct` bar, the hiring-vs-financials scatter). **Step 1 = de-risk spike** (confirm Neon → CSV/extract → Tableau Public publish path end-to-end with one throwaway sheet — this is where the "can't live-connect to Postgres" wall surfaces). Then a data-prep export step (pre-aggregated CSVs per view), then build, then polish + publish + wire into README. Keep scope tight — a clean 3-view dashboard beats an elaborate one. Main timeline risk (4–7 days).
3. **Lightweight AI insight layer** — ~20–40 line Claude-API narrator turning real numbers → plain English. Ties to GEO background. After the dashboard.
- **`04_hiring_trends`** — **deferred on a timescale basis** (§9). 25+ clean days banked; unlocks at ≥1 quarter (ideally a year). The pipeline is live and dated, so this is a real "future work" item, not a punt. Build a *velocity/mix-drift* v2 when the window earns it — do **not** claim strategic-shift detection on a month.
- **hiring × patents** — richer, but **gated on verifying assignee→ticker mapping quality**; if messy, multi-session entity resolution → stretch/optional. No assignee data loaded yet.
- **`edgar_backfill.py` follow-up (minor):** the concept-gather fix is committed; if ever extended, keep the "primary-wins-on-collision" dedup so a subset concept can't override a real value.
- **Bottom line:** two cross-signal findings + AI-pct cut + dashboard = a complete, defensible Wave-1 portfolio. AI layer + trends are enhancements after. With Wave 1 live *now*, a rougher dashboard up in ~a week beats a polished one in a month — ship a lean v1, iterate.

## §11 — Key learnings & principles
- **Data smells catch bugs:** round numbers (exactly 2,000 NVDA jobs = Workday API cap) and suspiciously large figures → investigate before trusting.
- **A number that contradicts reality is a bug, not a finding** — sanity-check derived data against a primary source (the AMD "54% collapse" → YTD bug).
- **Key on data-intrinsic properties** (period duration, period start), **not record metadata** (fiscal labels, filing year). Both EDGAR bugs came from trusting metadata.
- **Duration-bucketing over label-filtering** for EDGAR quarters.
- **The same line item can be tagged under sibling XBRL concepts across filings** (CDNS: quarterlies under `ResearchAndDevelopmentExpense`, 10-K annual under `...SoftwareExcludingAcquiredInProcessCost`). Gather across **all** candidate concepts; don't return on the first with data. (Day 14.)
- **Single source of truth:** mixing yfinance/EDGAR date conventions creates upsert-invisible duplicates; fix at source, don't reconcile downstream.
- **Dry-run on one ticker first**, against a known public figure, before a full reload. Test source-code fixes **non-destructively** (reload the module + run the function) before touching the destructive DELETE-reload script.
- **Ratios are immune to period-length & unit errors; absolute values expose them** (intensity/margin survived the YTD bug; revenue levels didn't — same reason TSM's TWD doesn't break intensity).
- **Snapshot ranks companies; a trend explains them** (MU: highest snapshot margin, deepest series trough).
- **Product type, not segment,** explains the pattern — held for R&D intensity *and* margin (`10`).
- **Hiring encodes business model (structure), not financial performance** — role mix splits on manufacturing/software by value-chain position (Q2), while the financial ratios don't predict it (Q1). *The finding can be the contrast:* a predictor that fails next to one that works beats either alone. (Day 14.)
- **Timescale gates trend analysis:** ~30 daily snapshots can't separate strategic hiring shifts from cyclical/seasonal noise — trends need ≥1 quarter, ideally a year. Defer with a reason, keep the pipeline banking. (Day 14.)
- **Classifier integrity over coverage:** honest catch-all buckets beat forced classification. Reconcile a copied classifier against its source (ballpark, not exact) to confirm a faithful copy.
- **NVDA framing:** sells GPU hardware; CUDA is the free software platform creating lock-in. The software/research hiring tilt is thesis *evidence*, not the business model.
- **Attribution guardrails:** no AI causal claims from financial/ratio data alone; no workforce-trend claims without time-series. `ai_pct` = the word "AI" in a title, not verified AI work — a correlation there could be *labeling*, not *doing*. n=9 → directional, not significance-grade.
- **Numbers require primary-source verification** before entering the public portfolio.
- **Verify with arithmetic that breaks if the code silently no-ops** (the 208+7=215 row check caught a DELETE that hadn't saved; the TTM completeness guard caught the CDNS null).
- **Serverless Postgres drops idle pooled connections** — `pool_pre_ping=True` + `pool_recycle=300` in every notebook's Cell 0, not just the loader.
- **Spearman = Pearson on ranks:** `df.rank().corr()` gives Spearman with no scipy dependency — keeps the repo runnable from a clean clone.

## §12 — Housekeeping & known gotchas
- **`.env` parse warning:** `python-dotenv could not parse statement starting at line 17` prints on load (harmless — all vars still resolve). Fix before wiring `ANTHROPIC_API_KEY` for the narrator (a malformed line could later swallow a key). Usual culprit: an inline `#`, an unquoted value, or a line missing its `=`. Two minutes; open `.env`, look at line 17.
- **CDNS FY2025 annual R&D — primary-source check still open (§5.11):** confirm ~$1,768.8M against Cadence's FY2025 10-K "Research and development" line (EDGAR, CIK `0000813672`, filed 2026-02-19) before CDNS numbers go public. The `Software` concept name is almost certainly just Cadence's tagging (they're a software company), but the 10-K line is ground truth. Arithmetic already cross-checks (annual = Q1+Q2+Q3 + a plausible Q4, sits above the 3-quarter run-rate).
- **scipy not installed** — Spearman via `.rank().corr()`. Install only if stats get heavier (regressions, p-values); it means a re-run + a new dependency for a portfolio repo a recruiter might clone.
- **`.env.example`** — clean template in **Appendix A** (Neon block, `SEC_USER_AGENT_EMAIL` placeholder, API keys). Confirm it's committed and current.
- **SEC fair-use** requires a real `SEC_USER_AGENT_EMAIL` in `.env` at runtime. The financials backfill is manual/local → **not** needed as a GitHub secret unless that script is ever automated.
- **TSM in TWD** (~31 TWD/$1): excluded from analysis; ratios still valid, only absolute levels inflated. `MAX(revenue)` returns NaN on TSM's sparse series — driver quirk, not a real problem.
- **ANSS** data ends Q1 2025 (Synopsys acquisition, closed Jul 2025).
- **SNPS/TSM hiring fetchers** disabled (anti-bot); revisit only if Playwright becomes justified.
- **Legacy check:** confirm actions are pinned (checkout/setup-python) in the Actions workflow (`scrape.yml`).
- **Project-tab file snapshots** (Claude Projects) are static — after this session, `20_cross_signals.ipynb` and `etl/edgar_backfill.py` in the tab are stale (empty stub / pre-fix). Re-add those two if Claude needs to read current versions without pasting; GitHub is the live source (`76c4315`).
- Confirm `interview_moments.md` and this handoff are committed at session close.

## §13 — Next session: exact starting point
1. **Read this handoff fully**, then **verify live state** — quick `hiring_signals` snapshot-series check (cron still 9/9 past 07-11?) + a `financials_quarterly` row-count/gap sanity check (queries in Appendix C). Confirm CDNS `2025-12-31` `rd_spend` is populated. Don't trust the doc blindly.
2. **AI-hiring cut in `20` (descriptive, 1–2 days)** — the next piece:
   - Reuse the `signals` frame (Appendix G) — no re-derivation. The statistical question is answered (Q1 flat vs financials); this cut is **descriptive**.
   - One chart: `ai_pct` sorted bar, colored by segment (Fabless/IDM/EDA palette, §7). Optional: is the lean a fabless-vs-IDM pattern?
   - Johann writes the read in his voice; Claude pressure-tests. **Carry the caveat on-chart:** `ai_pct` = title keyword, not verified AI work.
   - Log an interview moment only if a real technical/analytical moment lands.
3. **Then dashboard v1** — start with the **de-risk spike** (Neon → CSV/extract → Tableau Public publish path, one throwaway sheet) before any build. Then data-prep export → build the 3 tiles → polish + publish + README wire-up. Keep scope tight.
4. **`04_hiring_trends`** — only once the snapshot window reaches ≥1 quarter (deferred with reason, §9/§10). Not yet.

---

# APPENDICES — reusable code & queries
*Kept here so you can rerun or rebuild without opening old chats. Appendix B and G reflect Day 14 code.*

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

**Financials profiling (coverage per ticker; NULL-aware — CDNS `rd_n` should now equal its quarter count):**
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

**CDNS Q4 check (expect one row, `rd_spend` = 464582000):**
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

**Spearman + Pearson without scipy (Spearman = Pearson on ranks; report with n, NOT a percentage):**
```python
cols = ["ai_pct", "Software & Firmware", "rd_intensity", "operating_margin"]
spearman = signals[cols].rank().corr()   # Spearman
pearson  = signals[cols].corr()          # Pearson (default)
# 10_financials: core[["rd_intensity","operating_margin"]].rank().corr().iloc[0,1]  # ≈ -0.80, n=9
```

**Git pattern (explicit paths, never `git add -A`):**
```powershell
git add analysis/<notebook>.ipynb etl/<script>.py interview_moments.md
git add analysis/<chart1>.png analysis/<chart2>.png
git commit -m "<action-first description>"
git push
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

*The classifier (`ROLE_RULES` + `AI_PAT`, 13 buckets, first-match-wins) is copied verbatim from `03_hiring_category.ipynb` — see that notebook; keep `03` untouched. Reconciles at 4.0% unclassified / 9.4% AI on the current snapshot.*

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

**Q1 — correlations (hiring vs financials; no scipy):**
```python
cols = ["ai_pct", "Software & Firmware", "rd_intensity", "operating_margin"]
print("Spearman:\n", signals[cols].rank().corr().round(2))
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

## Appendix F — Most recent interview moments (quick form; full history in `interview_moments.md`)

**1. EDGAR backfill bug (Day 13):**
> Spotted AMD revenue "dropping" 54% during the AI boom — impossible. Traced it to EDGAR storing 9-month YTD totals under the same label as discrete quarters; my code grabbed the wrong one. Fixed by filtering on period *duration*, deriving Q4 = full-year − 9-month. Dry-ran on one ticker, reloaded to 215 clean rows. Lesson: sanity-check against the source; a number that contradicts reality is a bug.

**2. Snapshot vs. trend (Day 13):**
> Micron ranked #1 on margin (67.6%) in one quarter — but the 5-year trend showed it's a cyclical peak (−60% → 80%), while Nvidia holds ~65% steadily. Lesson: a snapshot ranks companies, a trend explains them. Product type, not segment label, drives the pattern.

**3. CDNS Q4 R&D — XBRL concept-fallback (Day 14):**
> CDNS Q4 2025 R&D came back null. Q4 is derived (annual − 9-month YTD) since 10-Ks report only the full year. First guessed a fiscal-calendar mismatch, but pulled the raw EDGAR facts and every period start matched — dead theory. Real cause: Cadence tags full-year R&D under a different XBRL concept (...SoftwareExcludingAcquiredInProcessCost) than its quarterlies, and the extractor returned on the first concept with data — plus that concept wasn't even in the candidate list. Fixed by adding the concept and gathering across all of them (primary wins on a period collision). Lesson: the same line can live under sibling concepts across filings; don't stop at the first tag, and diagnosing beat guessing.

**4. The correlation that wasn't / cross-signal contrast (Day 14):**
> Two cross-signal cuts. Q1: hiring tilt vs financial ratios (R&D intensity, margin) — Spearman across 9 tickers, all pairs −0.10 to +0.25, basically independent. Q2: role mix vs business model — Manufacturing splits IDMs (~29%) from fabless/EDA (~10%), Software splits EDA/fabless from IDMs. The result is the contrast: financial ratios don't predict hiring tilt, but structure does — hiring encodes what KIND of company you are, not how it's performing. Lesson: a predictor that fails next to one that works is a stronger finding than either alone. Caveats kept on-chart: n=9 directional; EDA = CDNS (n=1); ai_pct = the word "AI," not verified AI work.