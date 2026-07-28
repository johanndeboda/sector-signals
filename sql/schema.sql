-- =====================================================================
-- Sector Signals — schema.sql
-- Creates the tables for the semiconductor signals pipeline and seeds the
-- companies table with the 12-company target universe.
-- Idempotent: safe to re-run (IF NOT EXISTS + ON CONFLICT DO NOTHING).
-- =====================================================================

-- ---------- companies ----------
-- Shared dimension table. Every signal table foreign-keys to this.
CREATE TABLE IF NOT EXISTS companies (
    ticker       TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    segment      TEXT NOT NULL,        -- EDA / Fabless / IDM / Foundry
    hq_country   TEXT
);

-- ---------- financials_quarterly ----------
-- Quarterly financials. Seeded from yfinance (load_financials.py), then
-- US-listed tickers are deleted and reloaded from SEC EDGAR
-- (edgar_backfill.py) — EDGAR is the source of record; yfinance remains
-- only for TSM (foreign filer). operating_margin stored as a fraction.
CREATE TABLE IF NOT EXISTS financials_quarterly (
    ticker            TEXT NOT NULL REFERENCES companies(ticker),
    quarter           DATE NOT NULL,        -- fiscal quarter-end date
    revenue           NUMERIC,
    rd_spend          NUMERIC,
    net_income        NUMERIC,
    operating_margin  NUMERIC,              -- fraction, e.g. -0.231 = -23.1%
    PRIMARY KEY (ticker, quarter)
);

-- ---------- stock_prices_daily ----------
-- Daily OHLCV from yfinance (load_financials.py). Not currently surfaced on
-- the dashboard; retained for future price-vs-signal analysis.
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
-- Patents signal (load_patents.py, PatentsView data). Populated but not yet
-- surfaced on the dashboard — cross-signal patent analysis is future work.
CREATE TABLE IF NOT EXISTS patents (
    patent_id         TEXT PRIMARY KEY,
    assignee_ticker   TEXT REFERENCES companies(ticker),
    grant_date        DATE,
    title             TEXT,
    cpc_class         TEXT,
    inventor_count    INTEGER
);

-- =====================================================================
-- Seed companies — 12-company target universe
-- (9 active in the hiring pipeline; SNPS/ANSS/TSM seeded for future work)
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

-- =====================================================================
-- hiring_signals — the active hiring table.
-- One row per (job_id, snapshot_date): the same posting seen on different
-- days gets multiple rows, enabling first-seen / last-seen / posting-age.
--   job_id        = ATS posting ID, ticker-prefixed (e.g. "AMD:87520") so it
--                   is globally unique — this is why (job_id, snapshot_date)
--                   is a safe PK across companies.
--   snapshot_date = the date WE scraped it
--   posted_date   = when the company listed it (best-effort)
--   category      = 13-bucket role classification (NULL on ingest, derived later)
--   ats           = which scraper produced the row (workday/jibe/eightfold/etc.)
-- =====================================================================
CREATE TABLE IF NOT EXISTS hiring_signals (
    job_id         TEXT        NOT NULL,     -- ticker-prefixed, e.g. "AMD:87520"
    ticker         TEXT        NOT NULL REFERENCES companies(ticker),
    snapshot_date  DATE        NOT NULL,
    title          TEXT        NOT NULL,
    location       TEXT,                     -- raw, e.g. "Santa Clara, CA, USA"
    posted_date    DATE,
    category       TEXT,                     -- derived later, NULL on ingest
    ats            TEXT        NOT NULL,
    job_url        TEXT,
    captured_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (job_id, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_hiring_ticker_date
    ON hiring_signals (ticker, snapshot_date);

CREATE INDEX IF NOT EXISTS idx_hiring_ticker
    ON hiring_signals (ticker);