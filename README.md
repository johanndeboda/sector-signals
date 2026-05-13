# Sector Signals

A reusable intelligence pipeline that integrates financial, innovation, and hiring data to surface strategic signals before they appear in earnings. Demoed on the semiconductor industry (12 companies across EDA, fabless, IDM, and foundry segments).

## Thesis

What hiring and innovation signals predict strategic and financial shifts across an industry before they show up in earnings?

## Stack

- **Database:** PostgreSQL 16
- **ETL:** Python (pandas, sqlalchemy, yfinance)
- **AI/NLP:** Anthropic Claude API for structuring unstructured text (job postings, earnings transcripts)
- **Analysis:** Jupyter, pandas
- **Visualization:** Tableau Public

## Data sources

- Financials & stock prices: yfinance + SEC EDGAR
- Patents: USPTO
- Job postings: Greenhouse/Lever APIs + LLM classification
- Earnings transcripts (Phase 2): LLM-extracted structured signals

## Repo structure

```
etl/         Python scripts to pull and load each data source
sql/         Schema definitions and analytical queries
notebooks/   Jupyter notebooks for EDA and insight generation
data/        Local raw data cache (gitignored)
```

## Why this is sector-agnostic

The schema and ETL are config-driven by ticker list and sector taxonomy. Swap the company list and patent classification codes, and the same pipeline runs on biotech, fintech, or EVs.

## Status

Week 1 of 10 — environment setup and financials ingest.
