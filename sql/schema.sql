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
