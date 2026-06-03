# Sector Signals

A data pipeline that scrapes and analyzes **hiring signals** across major semiconductor companies to reveal where the industry is actually investing — by company, geography, and role. The data model is architected for multiple signals (patents, financials); this build implements and demonstrates the **hiring** signal end-to-end.

> Demoed on the semiconductor industry. The data model seeds a 12-company target universe across EDA, fabless, IDM, and foundry segments; the hiring pipeline is currently active for **9 US-listed companies**.

## Thesis

What do hiring patterns reveal about a company's strategy — geographic expansion, R&D focus, operational scale — before it shows up in earnings? Public job postings are a free, structured, leading signal of corporate intent. This project collects, normalizes, stores, and analyzes them to find out.

## What's built

- **Multi-ATS scraper → normalized PostgreSQL store.** A single idempotent loader pulls open postings from **five different applicant-tracking systems** (each company uses a different one) and upserts them into a common schema. 11,573 postings in the current snapshot; 62,951 rows historically.
- **Workday cap handling.** Bypasses Workday's 2,000-result limit via faceted fetching (re-querying per location facet) with automatic facet detection.
- **Location normalization layer.** Real-world location strings are inconsistent across all five ATSes (different order, casing, spelling, granularity). A 3-pass classifier (country-token matching → US state detection → curated city overrides, plus accent-folding and multi-site handling) resolves **462 distinct raw formats to 100% country/region coverage** (~87% to a specific country; the rest flagged as multi-site, transparently).
- **Cross-company geographic analysis** (`analysis/02_hiring_geography.ipynb`): region mix per company, a concentration metric (regional HHI), and country-level breakdown.

<!-- TODO: add a screenshot of the geography stacked-bar chart, e.g. docs/geography_chart.png -->
<!-- ![Hiring geography by company](docs/geography_chart.png) -->

### Selected findings

- **Asia outweighs North America in open postings (≈5,140 vs ≈3,810)** even across these US-listed firms — the industry's hiring footprint is substantially Asian.
- **Micron is the most regionally concentrated** (≈74% of postings in Asia).
- **NVIDIA is the Middle East outlier** (≈17% of postings, ~3× any peer) — its Israel R&D base, originating from the 2020 Mellanox acquisition (verified against public reporting).
- **Broadcom is the most US-centric** (≈68% North America); **Intel is the most globally distributed.**

## Stack

- **Language:** Python 3.13
- **ETL / analysis:** pandas, SQLAlchemy + psycopg2, python-dotenv
- **Database:** PostgreSQL 18
- **Notebooks / viz:** Jupyter, matplotlib, seaborn (Tableau Public for the dashboard — in progress)

## Data sources

Open job postings, scraped from each company's public careers site via its ATS:

| ATS | Companies |
|-----|-----------|
| Workday | NVDA, CDNS, MRVL, INTC, AVGO |
| Jibe | AMD |
| Eightfold | QCOM, MU |
| Oracle HCM | TXN |
| TalentBrew | SNPS *(seeded but disabled — requires HTML scraping)* |

## Setup

1. Clone the repo, create a virtual environment, and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your PostgreSQL credentials.
3. Create the schema by running `sql/schema.sql` against your database.
4. Run the loader:
   ```bash
   python etl/load_hiring.py
   ```

## Repo structure

```
etl/                Scrapers/loaders for each data source (load_hiring.py)
analysis/           Jupyter notebooks (01_hiring_snapshot, 02_hiring_geography)
sql/                schema.sql — database schema
data/               Local raw data cache (gitignored)
requirements.txt    Python dependencies
.env.example        Template for DB credentials
```

## Roadmap

**Next (in scope):**
- **Category (role-type) analysis** — does the *kind* of role differ by region/company?
- **Time-series / snapshot deltas** — how hiring books change over time (the highest-value signal; depends on accumulating daily snapshots).
- **Interactive dashboard** (Tableau Public) — the public-facing capstone.
- **Lightweight AI insight layer** — an LLM-generated plain-English readout of the findings.

**Future (beyond current scope):**
- **Patents signal** (USPTO / PatentsView) — would enable cross-signal analysis.
- **Financials** (SEC EDGAR / market data).
- **Cross-signal analysis** — relating hiring to innovation and financial signals.

## Design notes

The schema is **architected for multiple signals** — it already defines tables for financials, stock prices, and patents alongside hiring, all keyed to a shared `companies` table. This build implements the hiring signal end-to-end; the others are scaffolding for future work. The loader is **config-driven by company + ATS mapping**, so extending the company list is mostly configuration rather than new code. Adapting to a non-semiconductor sector would require wiring each new company's ATS and classification codes — so it's built *for* extensibility, not yet a plug-and-play multi-sector tool.

## Status

Hiring pipeline and geographic analysis complete and committed with outputs. Category-mix and time-series analysis next, followed by a Tableau dashboard and a lightweight AI insight layer. Patents, financials, and cross-signal analysis are future work; the schema already accommodates them.