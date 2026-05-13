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
SEC_USER_AGENT = "Johan (sector-signals project) johan@example.com"

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
    Given the full Company Facts JSON and a list of candidate concept names,
    return a dict {quarter_end_date: value} of QUARTERLY (10-Q) data points
    in USD from the past N years.

    Tries each candidate concept name; returns first one with data.
    """
    us_gaap = facts.get("facts", {}).get("us-gaap", {})

    for concept in candidates:
        if concept not in us_gaap:
            continue

        units = us_gaap[concept].get("units", {})
        # Most financial concepts are in USD; some (like share counts) aren't.
        if "USD" not in units:
            continue

        series = {}
        for entry in units["USD"]:
            # 'fp' = fiscal period: Q1/Q2/Q3/FY. We want quarterly only.
            # 'form' = filing type: 10-Q (quarterly) or 10-K (annual).
            # We accept quarterly data points from either form (10-K often
            # includes Q4 numbers via the FY total minus prior quarters,
            # but EDGAR pre-tags Q4 separately too).
            fp = entry.get("fp", "")
            form = entry.get("form", "")
            end_str = entry.get("end")
            val = entry.get("val")

            if not end_str or val is None:
                continue

            end_date = date.fromisoformat(end_str)
            if end_date < CUTOFF_DATE:
                continue

            # Keep quarterly data points only. fp in {Q1,Q2,Q3} are clean
            # quarter values. We skip FY (annual sum) to avoid double-counting.
            if fp not in ("Q1", "Q2", "Q3", "Q4"):
                continue

            # If multiple filings report the same quarter (amendments,
            # restatements), latest filed wins — sort by 'filed' date.
            existing = series.get(end_date)
            if existing is None or entry.get("filed", "") > existing["filed"]:
                series[end_date] = {"val": float(val), "filed": entry.get("filed", "")}

        if series:
            return {d: r["val"] for d, r in series.items()}

    return {}


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
