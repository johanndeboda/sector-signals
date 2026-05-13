"""
load_financials.py
------------------
Pulls 5 years of quarterly financials and daily stock prices from yfinance
for all 12 target tickers, loads into Postgres.

Idempotent: safe to re-run. Uses ON CONFLICT DO NOTHING on composite PKs.
"""

import os
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
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

TICKERS = [
    "CDNS", "SNPS", "ANSS",                  # EDA
    "NVDA", "AMD", "QCOM", "AVGO", "MRVL",   # Fabless
    "INTC", "MU", "TXN",                     # IDM
    "TSM",                                   # Foundry
]

YEARS_BACK = 5
END_DATE = datetime.today().date()
START_DATE = END_DATE - timedelta(days=YEARS_BACK * 365)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def safe_get(df: pd.DataFrame, row_name: str, col):
    """
    yfinance financials come as a DataFrame indexed by line-item name.
    Different tickers expose slightly different row names, so we look up
    defensively and return None if missing.
    """
    if row_name in df.index and col in df.columns:
        val = df.loc[row_name, col]
        return None if pd.isna(val) else float(val)
    return None


def fetch_quarterly_financials(ticker: str) -> pd.DataFrame:
    """
    Returns a DataFrame with columns: ticker, quarter, revenue, rd_spend,
    net_income, operating_margin.
    """
    t = yf.Ticker(ticker)
    fin = t.quarterly_financials  # rows = line items, cols = quarter-end dates

    if fin is None or fin.empty:
        print(f"  ! no quarterly financials for {ticker}")
        return pd.DataFrame()

    rows = []
    for quarter_end in fin.columns:
        revenue = safe_get(fin, "Total Revenue", quarter_end)
        rd_spend = safe_get(fin, "Research And Development", quarter_end)
        net_income = safe_get(fin, "Net Income", quarter_end)
        op_income = safe_get(fin, "Operating Income", quarter_end)

        operating_margin = None
        if revenue and op_income is not None and revenue != 0:
            operating_margin = op_income / revenue

        rows.append({
            "ticker": ticker,
            "quarter": pd.Timestamp(quarter_end).date(),
            "revenue": revenue,
            "rd_spend": rd_spend,
            "net_income": net_income,
            "operating_margin": operating_margin,
        })

    return pd.DataFrame(rows)


def fetch_daily_prices(ticker: str) -> pd.DataFrame:
    """
    Returns a DataFrame with columns: ticker, date, open, high, low, close, volume.
    """
    t = yf.Ticker(ticker)
    hist = t.history(start=START_DATE, end=END_DATE, auto_adjust=False)

    if hist is None or hist.empty:
        print(f"  ! no price history for {ticker}")
        return pd.DataFrame()

    hist = hist.reset_index()
    hist["ticker"] = ticker
    hist["date"] = hist["Date"].dt.date

    return hist[["ticker", "date", "Open", "High", "Low", "Close", "Volume"]].rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )


# ---------------------------------------------------------------------------
# Loaders — idempotent inserts via ON CONFLICT DO NOTHING
# ---------------------------------------------------------------------------
FIN_INSERT_SQL = text("""
    INSERT INTO financials_quarterly
        (ticker, quarter, revenue, rd_spend, net_income, operating_margin)
    VALUES
        (:ticker, :quarter, :revenue, :rd_spend, :net_income, :operating_margin)
    ON CONFLICT (ticker, quarter) DO NOTHING
""")

PRICE_INSERT_SQL = text("""
    INSERT INTO stock_prices_daily
        (ticker, date, open, high, low, close, volume)
    VALUES
        (:ticker, :date, :open, :high, :low, :close, :volume)
    ON CONFLICT (ticker, date) DO NOTHING
""")


def load_df(engine, df: pd.DataFrame, sql) -> int:
    """Inserts rows; returns count attempted (not necessarily inserted — conflicts skipped)."""
    if df.empty:
        return 0
    records = df.to_dict(orient="records")
    with engine.begin() as conn:
        conn.execute(sql, records)
    return len(records)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    engine = create_engine(DB_URL)

    # Quick connectivity check
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(f"Connected to Postgres. Loading {len(TICKERS)} tickers...\n")

    fin_total, price_total = 0, 0

    for ticker in TICKERS:
        print(f"[{ticker}]")

        fin_df = fetch_quarterly_financials(ticker)
        n_fin = load_df(engine, fin_df, FIN_INSERT_SQL)
        print(f"  financials: {n_fin} rows attempted")
        fin_total += n_fin

        price_df = fetch_daily_prices(ticker)
        n_price = load_df(engine, price_df, PRICE_INSERT_SQL)
        print(f"  prices:     {n_price} rows attempted")
        price_total += n_price

    # Verification — counts in DB
    with engine.connect() as conn:
        fin_count = conn.execute(text("SELECT COUNT(*) FROM financials_quarterly")).scalar()
        price_count = conn.execute(text("SELECT COUNT(*) FROM stock_prices_daily")).scalar()

    print(f"\n--- Summary ---")
    print(f"Rows attempted this run: financials={fin_total}, prices={price_total}")
    print(f"Total rows in DB now:    financials={fin_count}, prices={price_count}")
    print("(Re-running will show 'rows attempted' unchanged but 'rows in DB' identical — that's idempotency working.)")


if __name__ == "__main__":
    main()
