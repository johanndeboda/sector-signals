"""
edgar_backfill.py
-----------------
Backfills 5 years of quarterly financials from SEC EDGAR Company Facts API
for US-listed tickers (skips TSM — foreign filer, 20-F not 10-Q).

EDGAR is authoritative, so this script UPDATES on conflict — overwriting any
existing rows from yfinance with EDGAR values for the same (ticker, quarter).

Requires a User-Agent header per SEC fair-use policy. Put your email below.
"""

import os
import time
from datetime import date, timedelta

import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

DB_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# SEC requires a User-Agent identifying you. Replace with your real email.
SEC_USER_AGENT = f"Johann (sector-signals project) {os.getenv('SEC_USER_AGENT_EMAIL')}"

# CIK = SEC's permanent ID per company. Padded to 10 digits in URL.
# Looked up from https://www.sec.gov/cgi-bin/browse-edgar
TICKER_TO_CIK = {
    "CDNS": "0000813672",
    "SNPS": "0000883241",
    "ANSS": "0001013462",   # still in EDGAR despite delisting
    "NVDA": "0001045810",
    "AMD":  "0000002488",
    "QCOM": "0000804328",
    "AVGO": "0001730168",
    "MRVL": "0001835632",
    "INTC": "0000050863",
    "MU":   "0000723125",
    "TXN":  "0000097210",
    # TSM intentionally excluded — foreign filer, files 20-F annually, different schema.
}

# Candidate XBRL concept names per metric. Companies tag the same idea
# differently, so we try each in order until one returns data.
CONCEPT_CANDIDATES = {
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueNet",
    ],
    "rd_spend": [
        "ResearchAndDevelopmentExpense",
        "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
        "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost",
    ],
    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
    ],
}

YEARS_BACK = 5
CUTOFF_DATE = date.today() - timedelta(days=YEARS_BACK * 365)


# ---------------------------------------------------------------------------
# EDGAR fetch
# ---------------------------------------------------------------------------
def fetch_company_facts(cik: str) -> dict:
    """Pull the full Company Facts JSON for one company."""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    resp = requests.get(url, headers={"User-Agent": SEC_USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.json()


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

            # write if empty (any concept fills a gap), or newer fact from the
            # SAME concept (latest-filed). A different, higher-priority concept
            # already holding the slot is never overwritten.
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


def build_quarter_rows(ticker: str, facts: dict) -> list[dict]:
    """
    Combine the 4 metric series into one row per quarter.
    A quarter is only emitted if at least revenue exists.
    """
    series = {
        metric: extract_quarterly_series(facts, candidates)
        for metric, candidates in CONCEPT_CANDIDATES.items()
    }

    # Union of all quarter dates we found
    all_quarters = set()
    for s in series.values():
        all_quarters.update(s.keys())

    rows = []
    for q in sorted(all_quarters):
        revenue = series["revenue"].get(q)
        if revenue is None:
            continue  # no revenue → skip, can't compute margin anyway

        rd_spend = series["rd_spend"].get(q)
        net_income = series["net_income"].get(q)
        op_income = series["operating_income"].get(q)

        op_margin = None
        if op_income is not None and revenue != 0:
            op_margin = op_income / revenue

        rows.append({
            "ticker": ticker,
            "quarter": q,
            "revenue": revenue,
            "rd_spend": rd_spend,
            "net_income": net_income,
            "operating_margin": op_margin,
        })

    return rows


# ---------------------------------------------------------------------------
# Load — UPSERT (EDGAR overwrites yfinance)
# ---------------------------------------------------------------------------
UPSERT_SQL = text("""
    INSERT INTO financials_quarterly
        (ticker, quarter, revenue, rd_spend, net_income, operating_margin)
    VALUES
        (:ticker, :quarter, :revenue, :rd_spend, :net_income, :operating_margin)
    ON CONFLICT (ticker, quarter) DO UPDATE SET
        revenue          = EXCLUDED.revenue,
        rd_spend         = EXCLUDED.rd_spend,
        net_income       = EXCLUDED.net_income,
        operating_margin = EXCLUDED.operating_margin
""")


def load_rows(engine, rows: list[dict]) -> int:
    if not rows:
        return 0
    with engine.begin() as conn:
        conn.execute(UPSERT_SQL, rows)
    return len(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    # Make EDGAR the single source of truth: clear these tickers first so old
    # yfinance rows (calendar-dated) can't linger as near-duplicate quarters.
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM financials_quarterly WHERE ticker = ANY(:tks)"),
            {"tks": list(TICKER_TO_CIK)},
        )
    print(f"Cleared existing rows for {len(TICKER_TO_CIK)} EDGAR tickers.\n")

    print(f"Backfilling EDGAR data for {len(TICKER_TO_CIK)} tickers...")
    print(f"Cutoff date: {CUTOFF_DATE} (~{YEARS_BACK} years back)\n")

    total = 0
    for ticker, cik in TICKER_TO_CIK.items():
        print(f"[{ticker}] CIK={cik}")
        try:
            facts = fetch_company_facts(cik)
        except requests.HTTPError as e:
            print(f"  ! HTTP error: {e}")
            continue

        rows = build_quarter_rows(ticker, facts)
        n = load_rows(engine, rows)
        if rows:
            min_q = min(r["quarter"] for r in rows)
            max_q = max(r["quarter"] for r in rows)
            print(f"  upserted {n} quarters ({min_q} → {max_q})")
        else:
            print(f"  ! no quarterly data extracted (concept names may not match)")
        total += n

        # SEC fair-use: max 10 req/sec. We're well under but be polite.
        time.sleep(0.2)

    # Verify
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM financials_quarterly")).scalar()
        oldest = conn.execute(text("SELECT MIN(quarter) FROM financials_quarterly")).scalar()
        newest = conn.execute(text("SELECT MAX(quarter) FROM financials_quarterly")).scalar()

    print(f"\n--- Summary ---")
    print(f"Rows upserted this run: {total}")
    print(f"Total rows in DB:       {count}")
    print(f"Date range in DB:       {oldest} → {newest}")


if __name__ == "__main__":
    main()
