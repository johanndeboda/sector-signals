"""
assignee_mapping.py

Maps disambiguated assignee organization names (as they appear in
g_assignee_disambiguated.tsv) to our 12 ticker symbols.

Design choices:
  - EXACT-MATCH only (not substring). Substring matching is for exploration;
    production loads need predictable, auditable behavior.
  - Names are case-sensitive — they match the data EXACTLY as it appears in the
    PatentsView file. Do not "normalize" these strings.
  - Patent counts in comments are from g_assignee_disambiguated.tsv (full
    historical dataset, all years) at exploration time. Counts are reference
    only — the actual load filters to grant_date >= 2021-01-01.

Audit trail: every entry below was confirmed present in the source data via
etl/explore_assignees.py. See also Week 1 Day 3 entry in interview_moments.md.

Notable judgment calls:
  - AVGO: includes pre-2016 Avago Technologies entities (Singapore IP holding
    companies, etc.) because they share the AVGO ticker post-Broadcom merger.
    Date filter in load_patents.py handles the time-window aspect.
  - INTC: substring "intel" produced 16k+ false positives (AT&T Intellectual
    Property, Panasonic IP, etc.). Only Intel Corporation + 2 Intel-named
    subsidiaries included.
  - MRVL: includes Bermuda/Singapore/Israel subsidiaries. All corporate
    structuring entities for the same operating company.
  - ANSS: included despite July 2025 Synopsys acquisition. Project deliberately
    keeps ANSS as a separate ticker to capture the "company that disappeared
    mid-window" pattern as an analytical case study.
  - MU: includes the typo "Micron Technology, lnc." (lowercase L instead of
    capital I — real Micron patents miscategoried during data entry).
  - TSM: includes the typo "MTAIWANANUFACTURING" — same Taiwan Semiconductor
    Manufacturing Co., just garbled in PatentsView's source feed.

Usage:
    from etl.assignee_mapping import ORG_TO_TICKER, get_ticker

    ticker = get_ticker("NVIDIA Corporation")  # returns "NVDA"
    ticker = get_ticker("Some Unrelated Co.")  # returns None
"""

from typing import Optional

# ---------------------------------------------------------------------------
# Mapping: organization name -> ticker
# ---------------------------------------------------------------------------
# Built as a dict-of-tickers-to-list-of-names for readability and audit,
# then flattened below into the lookup dict that the loader actually uses.
TICKER_TO_ORGS: dict[str, list[str]] = {
    "CDNS": [
        "Cadence Design Systems, Inc.",
        "Cadence Design (Israel) II Ltd.",
        "Cadence Design Systems Inc. of San Jose",
    ],
    "SNPS": [
        "SYNOPSYS, INC.",
        "Synopsys Taiwan Co., Ltd.",
        "Synopsys (Shanghai) Co., Ltd.",
        "Synopsys Switzerland LLC",
    ],
    "ANSS": [
        "ANSYS, INC.",
        "Ansys Technologies, Inc.",
        "ANSYS LUMERICAL IP, LLC",
        "ANSYS Germany GmbH",
        "Ansys Diagnostics, Inc.",
    ],
    "NVDA": [
        "NVIDIA Corporation",
        "NVIDIA International, Inc.",
        "Nvidia Technology UK Limited",
        "NVIDIA U.S. Investment Company",
        "NVIDIA Technologies, Inc.",
        "Nvidia Denmark ApS",
    ],
    "AMD": [
        "Advanced Micro Devices, Inc.",
        "ADVANCED MICRO DEVICES (SHANGHAI) CO., LTD.",
    ],
    "QCOM": [
        "QUALCOMM Incorporated",
        "QUALCOMM MEMS Technologies, Inc.",
        "QUALCOMM Technologies Inc.",
        "QUALCOMM ATHEROS INC.",
        "QUALCOMM TECHNOLOGIES INTERNATIONAL, LTD.",
        "QUALCOMM Innovation Center, Inc.",
        "QUALCOMM CONNECTED EXPERIENCES, INC.",
        "Qualcomm Auto Ltd.",
        "QUALCOMM SWITCH CORP.",
        "Qualcomm iSkoot, Inc.",
        "QUALCOMM Atheros Technology Ltd.",
        "Qualcomm Intelligent Solutions, Inc",  # no period — matches data as-is
        "QUALCOMM FYX, INC.",
        "QUALCOMM Cambridge Limited",
        "Qualcomm Incorporated Center, Inc.",
    ],
    "AVGO": [
        # Post-merger Broadcom entries
        "Broadcom Corporation",
        "BROADCOM EUROPE LIMITED",
        "Broadcom Homenetworking, Inc.",
        "Broadcom Innovision Limited",
        # Pre-merger Avago entities (now part of AVGO via 2016 acquisition)
        "Avago Technologies General IP (Singapore) Pte. Ltd.",
        "Avago Technologies International Sales Pte. Limited",
        "Avago Technologies ECBU IP (Singapore) Pte. Ltd.",
        "Avago Technologies Fiber IP (Singapore) Pte. Ltd.",
        "AVAGO TECHNOLOGIES WIRELESS IP (SINGAPORE) PTE. LTD.",
        "Avago Technologies General IP Pte. Ltd",
        "Avago Technologies ECBU IP Pte. Ltd.",
        "Avago Technologies Enterprise IP (Singapore) Pte. Ltd.",
        "Avago Technologies Fiber IP Pte. Ltd.",
        "Avago Technologies Wireless IP, Pte. Ltd.",
        "Avago Technologies Limited",
    ],
    "MRVL": [
        "Marvell International Ltd.",
        "Marvell World Trade Ltd.",
        "MARVELL ASIA PTE LTD",
        "Marvell Israel (M.I.S.L) Ltd.",
        "Marvell International Technology Ltd",
        "Marvell Semiconductor Israel Ltd.",
        "MARVELL HISPANIA, S.L.",
        "Marvell Technology Group Ltd.",
        "Marvell Semiconductor, Inc.",
        "Marvell Isreal (M.I.S.L.) Ltd.",       # typo: "Isreal"
        "MARVELL ISRAEL (M.l.S.L) LTD.",        # typo: lowercase 'l'
        "Marvell Israel (M.I.S.I.) Ltd.",       # typo: M.I.S.I. instead of M.I.S.L.
        "Marvell D.S.P.C. Ltd.",
        "Marvell International Technologies Ltd.",
    ],
    "INTC": [
        # Substring "intel" produces massive false-positive noise (AT&T IP,
        # Panasonic IP, etc.). Only including verified Intel-the-chip-company.
        "Intel Corporation",
        "Intel IP Corporation",
        "Intel Mobile Communications GmbH",
    ],
    "MU": [
        "Micron Technology, Inc.",
        "Micron Technology, P.C.",
        "Micron Technology Licensing, LLC",
        "Micron Technology, lnc.",   # typo: lowercase L instead of capital I
    ],
    "TXN": [
        "TEXAS INSTRUMENTS INCORPORATED",
        "TEXAS INSTRUMENTS DEUTSCHLAND GMBH",
        "Texas Instruments-Acer Incorporated",
        "Texas Instruments Japan, Ltd.",
        "TEXAS INSTRUMENTS (CORK) LIMITED",
        "Texas Instruments Northern Virginia Incorporated",
        "Texas Instruments Israel Ltd.",
        "Texas Instruments Tucson Corporation",
        "TEXAS INSTRUMENTS NORWAY",
        "Texas Instruments Holland B.V.",
        "Texas Instruments Denmark",
        "Texas Instruments Incorporated a Delaware Corporation",
        "Texas Instruments Incorp.",
        "Texas Instruments Lehigh Valley Incorporated",
        "Texas Instruments India Limited",
    ],
    "TSM": [
        "TAIWAN SEMICONDUCTOR MANUFACTURING COMPANY LTD.",
        "TAIWAN SEMICONDUCTOR CO., LTD.",
        "Taiwan Semiconductor Manufacturing Company Limited and National Taiwan University",
        "Taiwan Semiconductor Manufacturing Company Limited & National Chiao-Tung University",
        "Taiwan Semiconductor Manufactured Company, Ltd.",
        "Taiwan SemiConductor Manuf. Company",
        "TAIWAN SEMICONDUCTOR MTAIWANANUFACTURING CO., LTD.",  # garbled but real
        "TAIWAN SEMICONDUCTOR MANUFACTURING HSINCHU, CO., LTD.",
        "Taiwan Semiconductor Manufacturing Company, Ltd. Hsin-Chu, Taiwan",
        # Excluded: TAIWAN SEMICONDUCTOR MEMORY INC. (different company)
    ],
}


# ---------------------------------------------------------------------------
# Flattened lookup: org name -> ticker
# ---------------------------------------------------------------------------
# The loader uses this. Built from TICKER_TO_ORGS above so there's a single
# source of truth — editing TICKER_TO_ORGS automatically updates this.
ORG_TO_TICKER: dict[str, str] = {
    org: ticker
    for ticker, orgs in TICKER_TO_ORGS.items()
    for org in orgs
}


def get_ticker(org_name: str) -> Optional[str]:
    """
    Return the ticker for a given assignee organization name, or None if not mapped.

    Exact match only. Whitespace and case must match the source data.
    """
    return ORG_TO_TICKER.get(org_name)


# ---------------------------------------------------------------------------
# Self-check (runs only when this file is executed directly, not on import)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    total = sum(len(orgs) for orgs in TICKER_TO_ORGS.values())
    print(f"Loaded mapping: {len(TICKER_TO_ORGS)} tickers, {total} org-name variants")
    for ticker, orgs in TICKER_TO_ORGS.items():
        print(f"  {ticker}: {len(orgs)} variants")

    # Sanity check: no duplicate org names across tickers
    seen: dict[str, str] = {}
    for ticker, orgs in TICKER_TO_ORGS.items():
        for org in orgs:
            if org in seen:
                print(f"  WARNING: {org!r} mapped to both {seen[org]} and {ticker}")
            seen[org] = ticker
