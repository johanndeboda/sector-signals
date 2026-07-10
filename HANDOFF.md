# HANDOFF.md — Sector Signals

*Last updated: Day 13 session (2026-07-10). Financials analysis (`10_financials.ipynb`) complete; EDGAR YTD/Q4 backfill bug found and fixed at source; `financials_quarterly` now 215 clean rows. Appendices A–F hold reusable code/SQL so nothing here requires re-reading old chats.*

---

## §0 — How to use this handoff
- Johann pastes this at the start of each session; Claude reads it **fully** before acting.
- Claude opens by confirming state, naming any scope trade-offs **with a recommendation**, then works **one step at a time**.
- Claude closes each session with a day summary + drafted interview moments, unprompted.
- **Verify live state — don't trust this doc blindly.** The pipeline runs daily and tables change; a quick DB check (snapshot series, row counts) beats assuming. This doc has been stale before (it once claimed patents/financials weren't built).
- **Claude cannot run code, hit the DB, or reach the network from chat.** Claude writes cells/commands; Johann runs them and pastes output; Claude iterates.

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

## §2 — Domain foundation
Prior consulting engagement with **Cadence Design Systems** via the SJSU Marketing Association: competitive analysis, careers-page audits, Generative Engine Optimization (GEO) analysis. Direct narrative thread — CDNS is one of the 12 tickers, and the planned AI insight layer ties back to the GEO work.

## §3 — Environment & stack
- **OS/shell:** Windows 11, PowerShell (flag PS vs Python vs SQL explicitly in commands).
- **Editor:** VS Code; notebooks run in VS Code Jupyter.
- **Python:** venv at `C:\Users\Johan\sector-signals\venv`.
- **psql:** full path required — `C:\Program Files\PostgreSQL\18\bin\psql.exe`.
- **DB:** Neon cloud PostgreSQL; creds in `.env` (gitignored) at repo root. Neon SQL Editor is the quick way to run ad-hoc SQL.
- **Stack:** pandas, matplotlib, seaborn, SQLAlchemy, BeautifulSoup, requests; yfinance (prices only — deprecated as a financials source, see §6).
- **Secrets in `.env`:** DB creds, `ANTHROPIC_API_KEY`, `USPTO_ODP_API_KEY`, `SEC_USER_AGENT_EMAIL` (added this session). `.env.example` documents variables with placeholders. **Never commit `.env`.**
- **Kernel gotcha:** the SQLAlchemy `engine` holds open Neon sockets; a kernel that touched the DB can hang on restart. Run `engine.dispose()` before restarting, or `Get-Process python | Stop-Process -Force` to clear a stuck kernel. Run scripts from the **repo root** (not `etl/`) so `load_dotenv()` finds `.env`.
- **PowerShell quoting:** `python -c "..."` with nested quotes/braces fails in PS. Use a small script file (e.g. a throwaway `verify_*.py`) or single-quote-only one-liners.

## §4 — Repo structure
- **`etl/`** — `load_hiring.py`, `load_financials.py` (yfinance; deprecated for financials), `edgar_backfill.py` (financials, authoritative), `load_patents.py`, `download_patents.py`, `assignee_mapping.py`, `explore_assignees.py`, `detect_ats.py`, `test_bulk_download.py`.
- **`analysis/`** — `01_hiring_snapshot.ipynb`, `02_hiring_geography.ipynb`, `03_hiring_category.ipynb`, `10_financials.ipynb` (done this session), `04_hiring_trends.ipynb` (reserved/deferred). PNG exports live here (`rd_intensity_by_ticker.png`, `rd_vs_revenue.png`, `operating_margin_by_ticker.png`, `intensity_vs_margin.png`, `revenue_trends.png`, `margin_trends.png`, `role_mix_heatmap.png`).
- **`sql/`** — `schema.sql`.
- **`.github/`** — Actions workflow(s).
- **Root:** `.env`, `.env.example`, `HANDOFF.md`, `interview_moments.md`, `README.md`, `requirements.txt`, `.gitignore`.
- **Notebook numbering convention:** `0x` = hiring (01 snapshot, 02 geography, 03 category, 04 trends-reserved); `1x` = financials (10); `2x` = cross-signal (proposed next).

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
  - *How extraction works:* pull `companyfacts/CIK{cik}.json`, walk `facts.us-gaap.<concept>.units.USD`, and per metric try a list of candidate XBRL concept names in order (companies tag the same idea differently). Bucket facts by period **duration**, keep discrete quarters, derive Q4. Concept candidates: revenue → `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `...IncludingAssessedTax`, `SalesRevenueNet`; R&D → `ResearchAndDevelopmentExpense`, `...ExcludingAcquiredInProcessCost`; net income → `NetIncomeLoss`, `ProfitLoss`; operating income → `OperatingIncomeLoss`. Operating margin = operating income ÷ revenue (a fraction; ×100 for display).
- **Hiring:** ATS APIs — Workday, Jibe/iCIMS, Eightfold, Oracle HCM Cloud. SNPS (TalentBrew/Avature) and TSM disabled (anti-bot; Playwright not justified for 2 tickers).
- **Patents:** PatentsView bulk TSV (S3) + USPTO ODP API.
- **Stock prices:** yfinance (still used — only financials deprecated).
- **Tables & row counts:**
  - `hiring_signals` — daily snapshots, 9 tickers/day. **16 consecutive clean 9/9 days, 06-17 → 07-02** (verified this session).
  - `financials_quarterly` — **215 rows** (208 EDGAR + 7 TSM), 12 tickers. Columns: `ticker, quarter (date-string, ISO), revenue, rd_spend, net_income, operating_margin`. Composite PK `(ticker, quarter)`. Repaired this session (§9). The 9 hiring-active tickers each have **18–20 clean discrete quarters**.
  - `stock_prices_daily` — ~13,805 rows *(per prior handoff; verify)*. PK `(ticker, date)`.
  - `patents` — ~61,519 rows loaded *(per prior handoff; verify)*. Assignee normalization / entity resolution = future work.

## §7 — Chart conventions
- seaborn `whitegrid`; matplotlib. Full palette + facet pattern in **Appendix E**.
- Single-series bars: `steelblue`. **Segment palette (reuse everywhere):** Fabless = `steelblue`, IDM = `#e07b39`, EDA = `seagreen`.
- Data labels via `ax.text`/`annotate`; `figsize` sized to content; `plt.tight_layout()`.
- **Save before show:** `plt.savefig("name.png", dpi=150, bbox_inches="tight")` → `plt.show()`. PNGs into `analysis/`.
- **Log scale** for wide dynamic range (e.g., revenue across ~45×); prefer real-unit tick labels over bare powers of ten.
- **Facet** (3×3 small multiples with a grey backdrop of the other series) when >6 lines tangle on one axis — used for the financials trend charts.

## §8 — Git workflow
- **Explicit file paths only — never `git add -A`.** Each workstream committed separately.
- Keep notebook outputs in commits.
- `.env` gitignored, never staged; `.env.example` (placeholders) committed.
- Descriptive, action-first commit messages. Pattern in **Appendix D**.

## §9 — Current state / progress log

**Pipeline (automation):**
- GitHub Actions cron daily 09:17 UTC + `workflow_dispatch`; Neon creds as repo secrets.
- Completeness guard live (`sys.exit(1)` on partial runs — won't write a partial snapshot).
- **16 consecutive clean 9/9 snapshots, 06-17 → 07-02**, zero intervention. Pre-guard partials (06-16 6/9, 06-11 6/9) predate the guard. Trends clock at 16+ clean days.

**Hiring notebooks — all complete:**
- `01_hiring_snapshot` — done.
- `02_hiring_geography` — done. 3-pass normalizer, 0.0% unknown / 87.1% fully resolved. Asia > NA in open postings even for US filers; MU 74% Asia; NVDA Middle East outlier ~17% (Mellanox/Israel); AVGO most US-centric; INTC most globally distributed.
- `03_hiring_category` — done. Native `category` field unusable cross-ticker (5/9 zero coverage). Built 13-bucket title-keyword classifier, unclassified 29% → 4.4%, ~80% to a specific function, two honest catch-alls. `is_ai` ≈ 9.4% (~1,037 roles).

**`10_financials.ipynb` — COMPLETE this session:**
- *Snapshot charts:* R&D-intensity ranked bar; revenue-vs-R&D-spend **log-log scatter** colored by segment (label = intensity); operating-margin ranked bar; **R&D-intensity-vs-margin scatter (Spearman ρ ≈ −0.80, n=9)** — strong negative rank correlation, business model as the third factor behind both.
- *Trend charts:* revenue indexed to each ticker's first quarter = 100 (log); operating margin (absolute %); both as **3×3 faceted small multiples** colored by segment, ordered so row 3 = the three IDMs (INTC, MU, TXN). Code in Appendix E.
- *Observations (Johann's, pressure-tested):*
  1. **R&D intensity** — driven by **product type, not segment**. CDNS/EDA highest (34.5%); MU/memory lowest (5.2%); NVDA 8.1% low only because revenue outran the largest absolute R&D budget. Ratio ≠ innovation commitment. Size only bites at the extremes (Spearman size↔intensity ≈ −0.7 — a tendency, not a law); the flat middle (MRVL/AMD/QCOM/INTC ~23–25% across ~6× revenue range) and TXN (small but 10.6%) break any pure size story.
  2. **NVDA** — revenue breaks from the pack ~early/mid-2023, ~12× indexed by 2026, with margin rising in the same window (selling more *and* keeping more per dollar = pricing power). Timing aligns with AI buildout; data can't prove causation (needs cross-signal).
  3. **MU** — margin −60% (2023) → ~80% (2026): commodity memory **cycle**, not a trend. Reframes the snapshot — MU's "highest margin" is a cycle *peak*; NVDA holds ~65% *steadily*. Same snapshot number, opposite stability. **Snapshot ranks, trend explains.**
  4. **Row 3 (INTC/MU/TXN, all IDM)** — three different margin shapes (INTC weak/volatile near-zero, leading-edge logic; MU cyclical memory; TXN stable ~30–40% analog). Segment label doesn't predict behavior; product type does — same principle as obs 1, now across a second metric.

**EDGAR backfill bug — found & fixed this session (the main engineering work):**
- *Symptom:* faceted trend showed AMD revenue "collapsing" 54% during the AI boom.
- *Cause 1 (duration-blindness):* EDGAR stores multiple facts per period-end — a 3-month discrete quarter and cumulative YTD (6-/9-month) — all under the same `fp` label. Old `extract_quarterly_series` filtered on `fp` and grabbed the 9-month YTD (AMD Q3'22 stored as $18B; true quarter = $5.57B, confirmed vs AMD's 10-Q).
- *Cause 2 (missing Q4):* 10-Ks report only the full year, never a standalone Q4 → `fp=Q4` matched nothing → recurring 182-day gaps.
- *Cause 3 (subtle):* first fix derived Q4 = full-year − 9-month YTD but keyed the match on `fy` — the *filing's* fiscal year, not the period's. Recent restatements re-stamp older facts with a newer `fy`, desyncing the dicts so the subtraction silently never ran (missing 2024-12, 2025-12).
- *Cause 4 (duplicates):* yfinance (calendar month-end) vs EDGAR (fiscal end) dating → 1–3 day near-duplicate rows the upsert never key-matched.
- *Fixes in `edgar_backfill.py`* (full code in **Appendix B**):
  - (a) Bucket facts by **duration**: 80–100 days = discrete quarter, 250–295 = 9-month YTD, 350–380 = full year; keep quarters.
  - (b) Derive **Q4 = full-year − 9-month YTD, matched on shared `start` date** (not `fy`).
  - (c) In `main()`, **DELETE the 11 EDGAR tickers before reload** to make EDGAR the single source of truth (TSM's 7 rows untouched).
  - (d) Moved the SEC contact email to `SEC_USER_AGENT_EMAIL` in `.env`.
- *Verification chain:* read-only dry run on AMD (2022-09-24 → $5.57B ✓, Dec quarters present, ~19 quarters) → reload → **215 rows** (208 + 7), `MIN(quarter)` moved 2021-06-03 → 2021-07-31 (stale yfinance rows gone) → gap check across all 9 tickers = **zero non-standard gaps**. (The row-count check also caught a first reload silently failing when the DELETE hadn't saved — 266 rows.)
- *Committed & pushed:* `10_financials.ipynb`, `edgar_backfill.py`, `interview_moments.md`, 6 PNGs; `.env.example` cleaned + committed separately. Dead file `revenue_margin_trends.png` removed.

**Interview moments logged this session** (`interview_moments.md`; verbatim in **Appendix F**): (1) EDGAR YTD/Q4 backfill catch; (2) snapshot-ranks-vs-trend-explains.

## §10 — Roadmap / what's next
1. **Cross-signal: hiring × financials** — NEXT, and cheap. Does `03`'s AI/software hiring tilt track `10`'s R&D profile? Data in hand, no new ingestion risk, short notebook. Proposed `2x` track (e.g., `20_cross_signal.ipynb`). **Keep it standalone — don't fold into `10` (§5.13).**
2. **Dashboard v1 (capstone)** — buildable on hiring (01–03) + financials alone. New skill: **Tableau Public vs Power BI undecided** — needs a quick free-tier/publishing-terms check when scoped. Main timeline risk.
3. **Lightweight AI insight layer** — ~20–40 line Claude-API narrator turning real numbers → plain English. Ties to GEO background.
- **hiring × patents** — richer, but **gated on verifying assignee→ticker mapping quality**; if messy, multi-session entity resolution → stretch/optional.
- **`04_hiring_trends`** — blocked by *time*, not effort. Needs ~3–4 weeks clean snapshots; 16+ banked (06-17 →), buildable **~mid-to-late July 2026**. Slots in when data matures, independent of the above.
- **Bottom line:** cross-signal → dashboard = a complete, defensible Wave-1 portfolio. AI layer + trends are enhancements after. Don't let optional pieces delay shipping the core.

## §11 — Key learnings & principles
- **Data smells catch bugs:** round numbers (exactly 2,000 NVDA jobs = Workday API cap) and suspiciously large figures → investigate before trusting.
- **A number that contradicts reality is a bug, not a finding** — sanity-check derived data against a primary source (the AMD "54% collapse" → YTD bug).
- **Key on data-intrinsic properties** (period duration, period start), **not record metadata** (fiscal labels, filing year). Both EDGAR bugs came from trusting metadata.
- **Duration-bucketing over label-filtering** for EDGAR quarters.
- **Single source of truth:** mixing yfinance/EDGAR date conventions creates upsert-invisible duplicates; fix at source, don't reconcile downstream.
- **Dry-run on one ticker first**, against a known public figure, before a full reload.
- **Ratios are immune to period-length & unit errors; absolute values expose them** (intensity/margin survived the YTD bug; revenue levels didn't — same reason TSM's TWD doesn't break intensity).
- **Snapshot ranks companies; a trend explains them** (MU: highest snapshot margin, deepest series trough).
- **Product type, not segment,** explains the pattern — held for R&D intensity *and* margin.
- **Classifier integrity over coverage:** honest catch-all buckets beat forced classification.
- **NVDA framing:** sells GPU hardware; CUDA is the free software platform creating lock-in. The software/research hiring tilt is thesis *evidence*, not the business model.
- **Attribution guardrails:** no AI causal claims from financial/ratio data alone; no workforce-trend claims without time-series.
- **Numbers require primary-source verification** before entering the public portfolio.
- **Verify with arithmetic that breaks if the code silently no-ops** (the 208+7=215 row check caught a DELETE that hadn't saved).

## §12 — Housekeeping & known gotchas
- **`.env.example`** — Johann to finish cleaning (add `SEC_USER_AGENT_EMAIL` placeholder, dedupe DB block, drop the invalid `<NEON_CONNECTION_STRING>` line); commit separately. Clean template in **Appendix A**.
- **SEC fair-use** requires a real `SEC_USER_AGENT_EMAIL` in `.env` at runtime. The financials backfill is manual/local → **not** needed as a GitHub secret unless that script is ever automated.
- **TSM in TWD** (~31 TWD/$1): excluded from analysis; ratios still valid, only absolute levels inflated. `MAX(revenue)` returns NaN on TSM's sparse series (NULL row) — driver quirk, not a real problem.
- **ANSS** data ends Q1 2025 (Synopsys acquisition, closed Jul 2025).
- **SNPS/TSM hiring fetchers** disabled (anti-bot); revisit only if Playwright becomes justified.
- **Legacy check:** confirm `@v6` is pinned for checkout/setup-python in the Actions workflow (`scrape.yml`).
- Confirm `interview_moments.md` and this handoff are committed at session close.

## §13 — Next session: exact starting point
1. **Read this handoff fully**, then **verify live state** — quick `hiring_signals` snapshot-series check (cron still 9/9 past 07-02?) + a `financials_quarterly` row-count/gap sanity check (queries in Appendix C). Don't trust the doc blindly.
2. **Start cross-signal (hiring × financials)** — the next core piece:
   - Confirm the notebook name (`20_cross_signal.ipynb` proposed).
   - **Profile first (§5.4):** the join is `03`'s per-ticker AI/function hiring mix against `10`'s per-ticker R&D-intensity/margin profile. All 9 hiring-active tickers have clean financials, so the overlap set is intact — confirm anyway.
   - Core question: does the AI/software hiring tilt line up with the R&D-intensity / software-research profile? **Timing/correlation only (§5.10)** — this step *begins* to test the AI thesis, still not causation.
3. **After cross-signal:** dashboard v1 scoping (Tableau vs Power BI check), then optionally the AI insight layer. `04_hiring_trends` whenever the snapshot window reaches ~3–4 weeks (~mid-to-late July).

---

# APPENDICES — reusable code & queries
*Everything below was built/verified this session. Kept here so you can rerun or rebuild without opening old chats.*

## Appendix A — Standard notebook setup & core dataframes

**Connection cell (restart-safe; run first in any notebook):**
```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

load_dotenv(override=True)
engine = create_engine(
    f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
)
pd.read_sql("SELECT 1 AS ok", engine)   # sanity check
```

**Financials core frames (`fin` = all 12, `core` = 9 hiring-active, `latest` = most-recent quarter each):**
```python
fin = pd.read_sql("SELECT * FROM financials_quarterly ORDER BY ticker, quarter", engine)
fin["quarter"] = pd.to_datetime(fin["quarter"])
fin["rd_intensity"] = fin["rd_spend"] / fin["revenue"]

HIRING_TICKERS = ["AMD","AVGO","CDNS","INTC","MRVL","MU","NVDA","QCOM","TXN"]
core = fin[fin["ticker"].isin(HIRING_TICKERS)].copy()

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

## Appendix B — Fixed EDGAR extraction (the crux of this session)

`edgar_backfill.py` → `extract_quarterly_series` (post-fix, verbatim). Duration-bucketing + Q4 derivation matched on shared `start` date:
```python
def extract_quarterly_series(facts: dict, candidates: list[str]) -> dict:
    """
    Return {quarter_end_date: value} of DISCRETE quarterly values.
    Q1-Q3 come from 3-month facts; Q4 is derived as (full-year - 9-month YTD),
    because 10-Ks report only the full year, never a standalone Q4.
    """
    us_gaap = facts.get("facts", {}).get("us-gaap", {})

    for concept in candidates:
        if concept not in us_gaap:
            continue
        units = us_gaap[concept].get("units", {})
        if "USD" not in units:
            continue

        quarterly = {}   # end_date   -> {"val","filed"}          3-month facts
        ytd9 = {}        # start_date -> {"end","val","filed"}    9-month YTD
        annual = {}      # start_date -> {"end","val","filed"}    full fiscal year

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

            if 80 <= days <= 100:            # discrete quarter
                cur = quarterly.get(end_d)
                if cur is None or filed > cur["filed"]:
                    quarterly[end_d] = {"val": float(val), "filed": filed}
            elif 250 <= days <= 295:         # 9-month YTD
                cur = ytd9.get(start_d)
                if cur is None or filed > cur["filed"]:
                    ytd9[start_d] = {"end": end_d, "val": float(val), "filed": filed}
            elif 350 <= days <= 380:         # full fiscal year
                cur = annual.get(start_d)
                if cur is None or filed > cur["filed"]:
                    annual[start_d] = {"end": end_d, "val": float(val), "filed": filed}

        if not quarterly and not annual:
            continue

        series = {d: r["val"] for d, r in quarterly.items()}

        # Q4 = full year - 9-month YTD, matched on shared fiscal-year START date.
        for start_d, ann in annual.items():
            if ann["end"] in series:
                continue                     # a real 3-month Q4 was filed
            y9 = ytd9.get(start_d)
            if y9 is not None:
                series[ann["end"]] = ann["val"] - y9["val"]

        if series:
            return series

    return {}
```

`main()` — DELETE block making EDGAR the single source of truth (insert right after the `SELECT 1` check, before the first `print`):
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

**Financials profiling (coverage per ticker; NULL-aware):**
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

**Gap check across the 9 (missing = >120 days, duplicate = <80; expect none):**
```python
tmp = core.sort_values(["ticker","quarter"]).copy()
tmp["gap"] = tmp.groupby("ticker")["quarter"].diff().dt.days
flags = tmp[(tmp["gap"].notna()) & ((tmp["gap"] < 80) | (tmp["gap"] > 120))]
print(core.groupby("ticker").size().to_string())
print("none" if flags.empty else flags[["ticker","quarter","gap"]].to_string(index=False))
```

**Spearman rank correlation (unitless coefficient −1..+1; report with n; NOT a percentage):**
```python
core[["rd_intensity","operating_margin"]].corr(method="spearman").iloc[0,1]   # ≈ -0.80
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

## Appendix F — Interview moments logged this session (verbatim, quick form)

**1. EDGAR backfill bug:**
> Spotted AMD revenue "dropping" 54% during the AI boom — impossible. Traced it to EDGAR storing 9-month YTD totals under the same label as discrete quarters; my code grabbed the wrong one. Fixed by filtering on period *duration*, deriving Q4 = full-year − 9-month. Dry-ran on one ticker, reloaded to 215 clean rows. Lesson: sanity-check against the source; a number that contradicts reality is a bug.

**2. Snapshot vs. trend:**
> Micron ranked #1 on margin (67.6%) in one quarter — but the 5-year trend showed it's a cyclical peak (−60% → 80%), while Nvidia holds ~65% steadily. Lesson: a snapshot ranks companies, a trend explains them. Product type, not segment label, drives the pattern.