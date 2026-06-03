# Interview Moments — Running log
Notes-to-self for interview anecdotes.
## Week 1
- [DAY 1]:

Set up Environment


## Week 1
- [Day 2] : 

Synopsys had closed acquisition of Ansys in July of 2025 hence why it was not found by yfinance. Dataset only contains companies that are still actively traded meaning that anything I conclude about industry trends is conditional on survival of the company.

Ran the financials loader and only got 5-7 quarters per ticker but had expected 5 years needed to sufficient analysis. Flagged SEC EDGAR backfill as the fix. LESSON: Verify shape of data before designing analysis around it.

Scoped EDGAR to US filers, TSM being international overcomplicates analysis and would add time having to parse XBRL filings, that isn't worth the tradeoff. 

EDGAR returns 3 quarters/year, not always 4 due to it being embedded in annual 10-K filings. ALSO, ANSS pre-acq data is in dataset giving angle on acquisition effects

Tested PatentsView API for patent ETL plan; turns out it migrated to USPTO Open Data Portal and the old endpoint redirects. Migration to ODP completed March 20, 2026. Saved myself a day of building against a dead API. Pivoting to ODP bulk downloads — stronger resume signal anyway since ODP is the new official source. Lesson: probe data sources before committing to them. Five minutes of testing > a day of debugging.

[Week 1, Day 2.2]
Built ETL targeting PatentsView PatentSearch API. First test call got DNS
resolution failure. Investigated and discovered the API was decommissioned
March 20, 2026, with data migrated to bulk TSV downloads on ODP.
Pivoted same session to bulk download approach. Confirmed S3 URLs return
200 with valid file sizes. Lesson: verify external API endpoints with a curl/HEAD request before architecting around them. Saved myself from writing a full ETL pointed at a dead host.

TOTAL: 2 pivots in 1 day, real data engineering means treating data sources as moving targets, not stationary fixed targets.

## Week 1
- [Day 3] : 

Built assignee mapping for 12 semi tickers. Found Marvell uses 14 distinct legal entity names across Bermuda, Singapore, Israel — typical of pre-2018 semi industry IP-holding structures designed for international tax optimization. Naive analysis treating "Marvell" as one name would have produced confused results; explicit subsidiary mapping handles it cleanly.

Made sure to run exploration on data to ensure than to guess, then query after

LOADERS utilize ON CONFLICT DO NOTHING

## Week 1
- [Day 4] : 

Scraped NVDA workday, but it maxed out at 2000 due to a pagination issue. Fixed by shrinking pagination to capture full scope of job lisings

Fix did not work, need to paginate by job category instead of location as NVDA does not have location filter.

## Week 1
- [Day 5] : 

First — ats_code inside every job says "icims", and apply_url points to *.icims.com. So AMD genuinely is iCIMS underneath, exactly as the Day 5 plan said — but the public listing layer is Jibe. Tagging ats="jibe" is correct (it's what the fetcher talks to), and the JSON itself confirms the Day 4 plan wasn't wrong, just incomplete.

Second — totalCount: 1291. Not a round number, no visible cap, and the facet counts sum cleanly (597+259+93+... = 1291 by country). So unlike the NVDA 2000-cap problem, no faceting workaround is needed here — straight pagination gets everything. I'll still add a safety check in case that changes.

ask if the loadhiring replacement what changes made and is it worth reviewing code

I verified the live site before coding and found it had migrated to a Jibe front-end. Lesson: a plan written weeks ago is a hypothesis, not a fact — re-verify before building

## Week 1
- [Day 6] : 

Before moving on to Qualcomm, I made sure to keep it disabled until I had finished the ones that were surely Workday ATS. This proved to be the right decision as a quick search into Qualcomm's careers page showed that it was an in-house careers page and not outsourced.

    SAME for Micron Technologies

Recovered AVGO from a transient ConnectionResetError by re-running the idempotent loader — confirmed config was already correct (the API had returned a valid count before the connection dropped).
    Re-running was safe due to ON CONFLICT DO NOTHING, to continue

Hiring data now live for 6 of 12 tickers


## Week 1
- [Day 7] : 

Looked into Synopsys careers page using DevTools and found out that it is not under Avature but instead Recruitics/Appcast-style meaning it might be able to be reused for QCOM and MU

    NEVERMIND, it is Avature as the backend but hidden by the frontend "with a custom front-end skin (similar to how AMD runs iCIMS behind Jibe — exact same pattern). Interview moment."
    
    TalentBrew Frontend





            To do:

## Week 1
- [Day 8] : 

Category will be null for TXN
ANSS redirects to SNPS (acquisition)
TSMC is also anti-bot similar to SNPS

Quick recap: 
    Workday — POST JSON, paginated, 2000-result cap, relative dates
    Jibe — GET JSON, clean ISO timestamps, straightforward
    Eightfold — GET JSON, Unix timestamps, department field gives free categories
    Oracle HCM — GET JSON, nested envelope, ISO dates, no per-job category
    TalentBrew — HTML inside JSON, needs session cookies

## Week 1
- [Day 9] : 

Jupyter notebook analyses on ipynb file

## Week 1
- [Day 10] : 