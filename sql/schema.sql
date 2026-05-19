-- =====================================================================
-- Sector Signals — schema.sql
-- Creates 5 tables and seeds the companies table with 12 target tickers.
-- Safe to re-run: uses IF NOT EXISTS and ON CONFLICT DO NOTHING.
-- =====================================================================

-- ---------- companies ----------
CREATE TABLE IF NOT EXISTS companies (
    ticker       TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    segment      TEXT NOT NULL,        -- EDA / Fabless / IDM / Foundry
    hq_country   TEXT
);

-- ---------- financials_quarterly ----------
CREATE TABLE IF NOT EXISTS financials_quarterly (
    ticker            TEXT NOT NULL REFERENCES companies(ticker),
    quarter           DATE NOT NULL,
    revenue           NUMERIC,
    rd_spend          NUMERIC,
    net_income        NUMERIC,
    operating_margin  NUMERIC,
    PRIMARY KEY (ticker, quarter)
);

-- ---------- stock_prices_daily ----------
CREATE TABLE IF NOT EXISTS stock_prices_daily (
    ticker  TEXT NOT NULL REFERENCES companies(ticker),
    date    DATE NOT NULL,
    open    NUMERIC,
    high    NUMERIC,
    low     NUMERIC,
    close   NUMERIC,
    volume  BIGINT,
    PRIMARY KEY (ticker, date)
);

-- ---------- patents ----------
CREATE TABLE IF NOT EXISTS patents (
    patent_id         TEXT PRIMARY KEY,
    assignee_ticker   TEXT REFERENCES companies(ticker),
    grant_date        DATE,
    title             TEXT,
    cpc_class         TEXT,
    inventor_count    INTEGER
);

-- ---------- job_postings ----------
CREATE TABLE IF NOT EXISTS job_postings (
    posting_id   TEXT PRIMARY KEY,
    ticker       TEXT REFERENCES companies(ticker),
    posted_date  DATE,
    title        TEXT,
    location     TEXT,
    function     TEXT,    -- LLM-classified, nullable
    seniority    TEXT,    -- LLM-classified, nullable
    signal_tag   TEXT     -- LLM-classified, nullable
);

-- =====================================================================
-- Seed companies — 12 target tickers
-- =====================================================================
INSERT INTO companies (ticker, name, segment, hq_country) VALUES
    ('CDNS', 'Cadence Design Systems', 'EDA',     'USA'),
    ('SNPS', 'Synopsys',               'EDA',     'USA'),
    ('ANSS', 'Ansys',                  'EDA',     'USA'),
    ('NVDA', 'NVIDIA',                 'Fabless', 'USA'),
    ('AMD',  'Advanced Micro Devices', 'Fabless', 'USA'),
    ('QCOM', 'Qualcomm',               'Fabless', 'USA'),
    ('AVGO', 'Broadcom',               'Fabless', 'USA'),
    ('MRVL', 'Marvell Technology',     'Fabless', 'USA'),
    ('INTC', 'Intel',                  'IDM',     'USA'),
    ('MU',   'Micron Technology',      'IDM',     'USA'),
    ('TXN',  'Texas Instruments',      'IDM',     'USA'),
    ('TSM',  'Taiwan Semiconductor',   'Foundry', 'Taiwan')
ON CONFLICT (ticker) DO NOTHING;

-- ============================================================
-- hiring_signals: one row per (job_posting, snapshot_date)
-- ============================================================
-- Why this shape:
-- - PK is (job_id, snapshot_date): same job posting captured on different days
--   gets multiple rows. Lets us track "first seen" / "last seen" / posting age.
-- - job_id comes from the ATS (Workday uses an externalPath like "R-12345").
--   Stable per company within one ATS, but NOT globally unique across companies,
--   so the PK includes ticker implicitly via job_id pattern (we'll prefix it).
-- - captured_date is when WE scraped it. posted_date is when the company listed it.
--   These differ when we discover a job that's been open for weeks.
-- - location stored as raw string for now; parsing into city/country is a Week 2 job.
-- - category is our derived bucket (engineering / sales / G&A / etc.) — populated
--   later by a keyword classifier. NULL on ingest is fine.
-- - ats column lets us know which scraper produced this row, useful for debugging
--   and for tracking if a company migrates ATS platforms mid-project.

CREATE TABLE IF NOT EXISTS hiring_signals (
    job_id         TEXT        NOT NULL,
    ticker         TEXT        NOT NULL REFERENCES companies(ticker),
    snapshot_date  DATE        NOT NULL,        -- the scrape date
    title          TEXT        NOT NULL,
    location       TEXT,                        -- raw, e.g. "Santa Clara, CA, USA"
    posted_date    DATE,                        -- when the company posted it (best-effort)
    category       TEXT,                        -- derived later, NULL on ingest
    ats            TEXT        NOT NULL,        -- 'workday', 'icims', 'avature', etc.
    job_url        TEXT,                        -- direct apply link, useful for spot-checks
    captured_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (job_id, snapshot_date)
);

-- Indexes for the queries we'll actually run:
-- - "How many openings did NVDA have on this date?" → ticker + snapshot_date
-- - "Show me all postings ever seen for AMD" → ticker
CREATE INDEX IF NOT EXISTS idx_hiring_ticker_date
    ON hiring_signals (ticker, snapshot_date);

CREATE INDEX IF NOT EXISTS idx_hiring_ticker
    ON hiring_signals (ticker);