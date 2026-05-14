"""
explore_assignees.py

Exploration script — NOT part of the production ETL.

Purpose: find the real organization name variants in g_assignee_disambiguated.tsv
for each of our 12 target companies. The output guides what we put in
assignee_mapping.py.

Why this matters: patent data has many name variants for the same company
("NVIDIA Corporation", "Nvidia Corp.", "NVIDIA Corp", etc). Guessing variants
silently drops patents. Grep, don't guess.

Usage:
    python etl/explore_assignees.py

What it prints: for each ticker, the top variants of org names containing our
search substring, with patent counts. You'll eyeball this and tell Claude which
variants look legitimate (vs noise — e.g. "Nvidia Healthcare" probably isn't NVDA).
"""

from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ASSIGNEE_FILE = DATA_DIR / "g_assignee_disambiguated.tsv.zip"

# Substrings to search for in disambig_assignee_organization.
# These are intentionally LOOSE — we want to see all variants, including ones
# we wouldn't have guessed. Lowercase comparison handles capitalization variants.
#
# Notes on choices:
# - "nvidia" catches NVIDIA, Nvidia, nVidia, etc.
# - "advanced micro" catches "Advanced Micro Devices" without false-positives from "AMD"
#   (which would match all kinds of unrelated companies)
# - "broadcom" — careful: there's an old Broadcom and a new Broadcom (post-Avago merger).
#   Both are AVGO ticker now, so we want both.
# - "marvell" catches Marvell Technology, Marvell Semiconductor, etc.
# - "ansys" already acquired by Synopsys (July 2025) but pre-acquisition patents matter
# - "taiwan semiconductor" is safer than "tsmc" because TSMC files patents under
#   the full name. We'll see in output whether "tsmc" appears too.
SEARCH_SUBSTRINGS = {
    "CDNS":  ["cadence design"],
    "SNPS":  ["synopsys"],
    "ANSS":  ["ansys"],
    "NVDA":  ["nvidia"],
    "AMD":   ["advanced micro"],
    "QCOM":  ["qualcomm"],
    "AVGO":  ["broadcom", "avago"],
    "MRVL":  ["marvell"],
    "INTC":  ["intel"],                # WILL have false positives — "Intellectual Property", "Intellistar". We'll filter.
    "MU":    ["micron technology"],    # NOT just "micron" — too generic
    "TXN":   ["texas instruments"],
    "TSM":   ["taiwan semiconductor"],
}

# How many top variants to show per ticker.
TOP_N = 15


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not ASSIGNEE_FILE.exists():
        print(f"ERROR: {ASSIGNEE_FILE} not found.")
        print("Run download_patents.py first, and make sure g_assignee_disambiguated.tsv.zip has finished downloading.")
        return

    print(f"Reading {ASSIGNEE_FILE.name}...")
    # pandas reads zipped TSVs directly — no manual unzip needed.
    # We only need 2 columns out of 8: patent_id (for counting) and the org name.
    # Loading just those keeps memory usage low and read time fast.
    df = pd.read_csv(
        ASSIGNEE_FILE,
        sep="\t",
        compression="zip",
        usecols=["patent_id", "disambig_assignee_organization"],
        dtype={"patent_id": "string", "disambig_assignee_organization": "string"},
    )

    print(f"  Loaded {len(df):,} assignee records")
    print(f"  Unique organizations: {df['disambig_assignee_organization'].nunique():,}\n")

    # Drop rows with no org name (these are individual inventors, not company-assigned patents).
    df = df.dropna(subset=["disambig_assignee_organization"])

    # Lowercase column for case-insensitive matching. Keep original for display.
    df["org_lower"] = df["disambig_assignee_organization"].str.lower()

    # For each ticker, find variants and count patents per variant.
    for ticker, substrings in SEARCH_SUBSTRINGS.items():
        print(f"\n{'=' * 70}")
        print(f"  {ticker}  — searching for: {substrings}")
        print(f"{'=' * 70}")

        # Match any row whose org name contains ANY of the substrings.
        mask = df["org_lower"].str.contains("|".join(substrings), regex=True, na=False)
        matches = df[mask]

        if matches.empty:
            print("  (no matches)")
            continue

        # Count distinct patents per org variant.
        # Using nunique on patent_id (rather than len) because the same patent can
        # have multiple assignee rows — we want distinct patents per org variant.
        counts = (
            matches.groupby("disambig_assignee_organization")["patent_id"]
            .nunique()
            .sort_values(ascending=False)
            .head(TOP_N)
        )

        for org, count in counts.items():
            print(f"  {count:>7,}  {org}")

    print("\n" + "=" * 70)
    print("Done. Paste this output back to Claude — we'll build assignee_mapping.py from it.")


if __name__ == "__main__":
    main()
