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




## Week 2
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

## Week 2
- [Day 9] : 

Jupyter notebook analyses on ipynb file

## Week 2
- [Day 10] : 

Jupyter notebook analyses on ipynb file

## Week 2
- [Day 11-18] : 

Completed ETL script, took major pivots to reduce project length to ensure understanding, leave opening and flexibility for future expansions if time allows

Utilized CHATGPT to look over finished ETL scripts to ensure understanding of code, logic, purpose, and structure.

Scope limitations :
    - Covers only 9 of 12 intially planned companies, LIST EXCLUDED BELOW
        - SNPS
        - TSM
        - ANSS


## Week 2
- [Day 19] : 

De-Risk tested the cloud set up before doing to work to make sure it would be feasible by creating a github action to see if the scraper would run outside of a local run which ran good.

This cloud set up is to automate the scrape daily without needing to run it on my computer locally, venv prevents github from seeing account info so had to move it to github secrets

Given that my daily hiring snapshots were inconsistent in regards to how many companies were captured, I added a completeness check  to make sure the runs capture all 9 companies and not incomplete data



 (HALF 2)

Tweaked load_hiring.py to create a connection to postgres after jobs have been loaded instead of opening connection and keeping it open throughout the entire program, so a failed connection for one ticker doesn't affect the others also as Neon drops what it deems as idle connections 
    + a guard to make sure that it only saves the batch if all of it comes through.



## Week 2
- [Day 20] : 

Pivoted towards a title classifier approach in order to categorize the job listings that have been gathered via keywords as only 5 of 9 were scrapable with categories alongside an imbalance in the category count which could sway analyses.

Ran through ai thorughq quick iterations to quickly skim through data and classify as needed, goal was to go below 5% but not much lower to avoid uncessary time overfitting.
    Also audited inside of buckets through ai to ensure accuracy

Performed analyses on the hiring of the semiconductor companies while considering the companies and what they specialize in alongside prominence of AI roles.

## Week 2
- [Day 21] : 

Should note that some company financials have differing fiscal year-end dates

for scatterplots, company reveue differs greatly, so used log scale

Should've looked through financial data and verified completeness, found that there were 182-day gaps (missing Q1's) within each company with revenue that couldn't have been correct on a quarterly basis (eg: AMD - $18 Billion in one quarter)
    - Also had duplicates across all companies
    - Claude : "found mixed XBRL reporting periods in an EDGAR backfill by sanity-checking a trend against a known quarter."

    - My analysis: when using EDGAR, it stores several facts with different spans, not just on a quarterly basis, this meant that if there was a Q3 and 9-month YTD posting, it would be classified under the same category of being Q3 leading to a quarter duplication and misleading information.
        - Companies also usually don't post a Q4 in itself, posting a 10-K instead. 

    FIX :
        - Categorize by duration of posting rather than date-ends
        - Derive Q4 by subtracting full year by the 9-month YTD (3/4ths year)
        - Match by start of date rather than fiscal year filing date to get accurate faceting of financial dates
        - Deleted info from yfinance to avoid duplicates

        Ran AMD financials loader to verify and make sure it was correct running it through Claude to ensure verification

Analysis summary :
Looked into company financials to analyze their R&D expenditure against revenue within the latest quarter alongside their operating margins and revenue throguhout the last 5 years posted within their 10Q's

Halfway in, I realized EDGAR backfill did not Extract data correctly so had to do a redo to finish the ipynb.


## Week 2
- [Day 22] : 

    - Started cross-signal analysis between hiring and financials. Not as much insight as the other ipynb's as there wasn't much strong correlations across the board except for one
        - AI hiring percentage and the % of software/firmware jobs for companies.

    - BUG FIX
        - Cadence 4Q R&D was listed as being null thanks to a completeness guard check being done before indulging within the analysis.
        - Happened because CDNS has their R&D tagged as a different CBRL concept, had Claude look into it and fix the bug.

    