"""
load_patents.py

ETL loader for the patents table. Joins 4 PatentsView bulk TSVs to produce
one row per patent in our 5-year window (2021+) attributed to one of our 12
target semiconductor companies.

Pipeline:
  1. Read g_assignee_disambiguated.tsv → filter to mapped org names → resolve to ticker
  2. Deduplicate: one ticker per patent_id (handles co-assignee patents)
  3. Read g_patent.tsv → filter to grant_date >= 2021-01-01 → join
  4. Read g_cpc_current.tsv → take primary CPC class (sequence=0) per patent → join
  5. Read g_inventor_disambiguated.tsv → count distinct inventors per patent → join
  6. Insert into Postgres patents table with ON CONFLICT DO NOTHING (idempotent)

Usage:
    python etl/load_patents.py

Prerequisites:
  - download_patents.py has been run; 4 TSV zips exist in data/
  - companies table has all 12 tickers (verified via psql before running this)
  - .env has DB connection variables
"""

from pathlib import Path
import os
import sys
import time

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Import our mapping. Project-relative import works because we run this from
# the repo root: `python etl/load_patents.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assignee_mapping import ORG_TO_TICKER, TICKER_TO_ORGS


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

ASSIGNEE_FILE = DATA_DIR / "g_assignee_disambiguated.tsv.zip"
PATENT_FILE = DATA_DIR / "g_patent.tsv.zip"
CPC_FILE = DATA_DIR / "g_cpc_current.tsv.zip"
INVENTOR_FILE = DATA_DIR / "g_inventor_disambiguated.tsv.zip"

# Date floor: our 5-year analytical window. Patents granted before this are dropped.
GRANT_DATE_FLOOR = "2021-01-01"

# Batch size for inserts. Postgres `execute_values` can handle 1000+ at once;
# 500 is a safe middle ground (good throughput, won't time out on slow disks).
INSERT_BATCH_SIZE = 500


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_db_connection():
    """Load .env and connect to Postgres. Fails loudly if config is missing."""
    load_dotenv(PROJECT_ROOT / ".env")
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def log(msg: str, t_start: float | None = None):
    """Print a timestamped log line. Optionally show elapsed time since t_start."""
    elapsed = f" ({time.time() - t_start:.1f}s)" if t_start else ""
    print(f"  {msg}{elapsed}")


# ---------------------------------------------------------------------------
# Step 1: Resolve patents to tickers via the assignee mapping
# ---------------------------------------------------------------------------
def build_patent_to_ticker() -> pd.DataFrame:
    """
    Return a DataFrame with columns: patent_id, ticker.
    One row per patent (deduplicated across co-assignees).
    """
    log(f"Reading {ASSIGNEE_FILE.name}...")
    t0 = time.time()

    # Read just the 2 columns we need. Memory savings vs loading all 8 are
    # significant: ~70% reduction on a file that decompresses to ~1.5 GB.
    df = pd.read_csv(
        ASSIGNEE_FILE,
        sep="\t",
        compression="zip",
        usecols=["patent_id", "disambig_assignee_organization"],
        dtype={"patent_id": "string", "disambig_assignee_organization": "string"},
    )
    log(f"Loaded {len(df):,} assignee rows", t_start=t0)

    # Filter to rows whose org name is in our mapping. This is an exact-match
    # lookup on a dict, O(1) per row — fast even for millions of rows.
    df = df[df["disambig_assignee_organization"].isin(ORG_TO_TICKER)].copy()
    log(f"Filtered to {len(df):,} rows matching our 95 org names")

    # Map org name → ticker. Vectorized dict lookup via pandas .map().
    df["ticker"] = df["disambig_assignee_organization"].map(ORG_TO_TICKER)

    # Deduplicate: keep one row per patent_id.
    # WHY THIS MATTERS: A patent can have multiple assignees (e.g. company +
    # university co-filing). After our filter, both rows could survive if
    # both assignees mapped to tickers we track. Our patents table has
    # patent_id as PRIMARY KEY (singular), so we must pick one ticker per patent.
    #
    # Strategy: drop_duplicates keeps the first occurrence. Sort first by
    # patent_id so the choice is deterministic across re-runs.
    #
    # Trade-off being made here: a patent jointly filed by NVDA and a Stanford
    # researcher (not in our mapping) → fine, only NVDA row survives the
    # earlier filter. A patent jointly filed by NVDA and AMD → we keep one
    # arbitrary ticker. In the 2021+ window for our 12 companies, this is
    # extremely rare. We'll log how many duplicates we drop so we can audit.
    before = len(df)
    df = df.sort_values("patent_id").drop_duplicates(subset="patent_id", keep="first")
    dropped = before - len(df)
    if dropped:
        log(f"Dropped {dropped:,} duplicate (patent_id, ticker) rows — co-assigned patents")

    log(f"Unique patents mapped to tickers: {len(df):,}")
    return df[["patent_id", "ticker"]].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Step 2: Join with patent metadata (title, grant_date) and apply date filter
# ---------------------------------------------------------------------------
def attach_metadata(patents: pd.DataFrame) -> pd.DataFrame:
    log(f"Reading {PATENT_FILE.name}...")
    t0 = time.time()

    df = pd.read_csv(
        PATENT_FILE,
        sep="\t",
        compression="zip",
        usecols=["patent_id", "patent_title", "patent_date"],
        dtype={"patent_id": "string", "patent_title": "string"},
        # Parse patent_date as a date column at read time. Faster than
        # post-hoc conversion, and gives us proper date comparison semantics.
        parse_dates=["patent_date"],
    )
    log(f"Loaded {len(df):,} patent metadata rows", t_start=t0)

    # Filter to our 5-year window BEFORE the join. Reduces join size dramatically.
    # ~8M total patents in the file → ~1.5M granted since 2021.
    df = df[df["patent_date"] >= pd.Timestamp(GRANT_DATE_FLOOR)]
    log(f"Filtered to {len(df):,} patents granted on or after {GRANT_DATE_FLOOR}")

    # Inner join: keep only patents present in both sets.
    # An inner join is what we want — patents pre-2021 are dropped (correct);
    # patents in our ticker set but with missing metadata are dropped (acceptable
    # data-quality decision: don't insert rows without grant_date).
    merged = patents.merge(df, on="patent_id", how="inner")
    log(f"Patents in window for our 12 companies: {len(merged):,}")

    # Rename to match Postgres column names.
    return merged.rename(columns={"patent_title": "title", "patent_date": "grant_date"})


# ---------------------------------------------------------------------------
# Step 3: Attach primary CPC class
# ---------------------------------------------------------------------------
def attach_cpc(patents: pd.DataFrame) -> pd.DataFrame:
    log(f"Reading {CPC_FILE.name}...")
    t0 = time.time()

    # The CPC file has multiple rows per patent (one per classification).
    # We only want the PRIMARY classification: cpc_sequence = 0.
    df = pd.read_csv(
        CPC_FILE,
        sep="\t",
        compression="zip",
        usecols=["patent_id", "cpc_sequence", "cpc_class"],
        dtype={"patent_id": "string", "cpc_class": "string", "cpc_sequence": "int64"},
    )
    log(f"Loaded {len(df):,} CPC rows", t_start=t0)

    df = df[df["cpc_sequence"] == 0]
    log(f"Filtered to {len(df):,} primary classifications")

    # Left join: keep patents even if missing CPC. (Some old patents lack
    # current CPC class. cpc_class will be NULL for those — acceptable.)
    merged = patents.merge(df[["patent_id", "cpc_class"]], on="patent_id", how="left")
    missing = merged["cpc_class"].isna().sum()
    if missing:
        log(f"Note: {missing:,} patents have no primary CPC class (left as NULL)")
    return merged


# ---------------------------------------------------------------------------
# Step 4: Attach inventor count
# ---------------------------------------------------------------------------
def attach_inventor_count(patents: pd.DataFrame) -> pd.DataFrame:
    log(f"Reading {INVENTOR_FILE.name}...")
    t0 = time.time()

    df = pd.read_csv(
        INVENTOR_FILE,
        sep="\t",
        compression="zip",
        usecols=["patent_id", "inventor_id"],
        dtype={"patent_id": "string", "inventor_id": "string"},
    )
    log(f"Loaded {len(df):,} inventor rows", t_start=t0)

    # Count DISTINCT inventors per patent. Same nunique() pattern as exploration:
    # we want unique people, not total row count (a patent can list the same
    # inventor multiple times across different files; nunique deduplicates).
    counts = df.groupby("patent_id")["inventor_id"].nunique().rename("inventor_count")
    merged = patents.merge(counts, on="patent_id", how="left")

    # Patents with no inventor records → inventor_count = 0 (clean default).
    merged["inventor_count"] = merged["inventor_count"].fillna(0).astype(int)
    return merged


# ---------------------------------------------------------------------------
# Step 5: Insert into Postgres
# ---------------------------------------------------------------------------
def insert_patents(patents: pd.DataFrame):
    """
    Insert into the patents table with conflict handling.
    Idempotent: re-running won't create duplicates.
    """
    log(f"Inserting {len(patents):,} rows into patents table...")
    t0 = time.time()

    # Build list of tuples in column order matching the INSERT.
    # Replace NaN/NaT with None — psycopg2 maps None → SQL NULL.
    rows = [
        (
            r.patent_id,
            r.ticker,
            None if pd.isna(r.grant_date) else r.grant_date.date(),
            r.title if pd.notna(r.title) else None,
            r.cpc_class if pd.notna(r.cpc_class) else None,
            int(r.inventor_count),
        )
        for r in patents.itertuples(index=False)
    ]

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # execute_values is psycopg2's fast batch-insert helper. Sends
            # all values in a single multi-row INSERT instead of one per row.
            # For 50k rows, this is the difference between ~3 seconds (batched)
            # and ~5 minutes (one-by-one). Same principle as bulk-loading in
            # any DB: round-trip cost dominates, so batch the round-trips.
            execute_values(
                cur,
                """
                INSERT INTO patents
                  (patent_id, assignee_ticker, grant_date, title, cpc_class, inventor_count)
                VALUES %s
                ON CONFLICT (patent_id) DO NOTHING
                """,
                rows,
                page_size=INSERT_BATCH_SIZE,
            )
            inserted = cur.rowcount  # number of rows actually inserted (excludes ON CONFLICT skips)
        conn.commit()
        log(f"Inserted {inserted:,} new rows (re-runs will show 0)", t_start=t0)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    overall_start = time.time()
    print(f"Loading patents into Postgres (window: {GRANT_DATE_FLOOR} onwards)")
    print(f"Tickers covered: {sorted(TICKER_TO_ORGS.keys())}\n")

    # Sanity-check files exist before we start.
    for f in (ASSIGNEE_FILE, PATENT_FILE, CPC_FILE, INVENTOR_FILE):
        if not f.exists():
            print(f"ERROR: {f} not found. Run download_patents.py first.")
            return

    patents = build_patent_to_ticker()
    patents = attach_metadata(patents)
    patents = attach_cpc(patents)
    patents = attach_inventor_count(patents)

    # Show per-ticker count before insert — useful for sanity-checking.
    print("\n  Per-ticker counts in 2021+ window:")
    for ticker, count in patents.groupby("ticker").size().sort_values(ascending=False).items():
        print(f"    {ticker:>5}: {count:>6,}")
    print()

    insert_patents(patents)

    total_elapsed = time.time() - overall_start
    print(f"\nDone in {total_elapsed:.1f}s.")


if __name__ == "__main__":
    main()
