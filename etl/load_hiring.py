"""
load_hiring.py — Fetch current job postings from the semi-12 careers sites
and insert them into hiring_signals.

ATS coverage (5 platforms, 9 of 12 tickers live as of Day 8):
  workday    — NVDA, CDNS, MRVL, INTC, AVGO  (POST JSON)
  jibe       — AMD                            (GET JSON)
  eightfold  — QCOM, MU                       (GET JSON)
  oracle_hcm — TXN                            (GET JSON)
  talentbrew — SNPS (disabled, anti-bot)      (GET JSON+HTML)
  unknown    — TSM  (disabled, SSR + 403)
  skip       — ANSS (redirects to SNPS)

Each fetcher returns an iterator of normalized 9-key dicts matching the
hiring_signals schema. Fetchers are registered in FETCHERS by `ats` name;
main() dispatches per-ticker via that registry.

Idempotent: ON CONFLICT DO NOTHING on (job_id, snapshot_date) means
re-running on the same day inserts only net-new rows. Page-level requests
are wrapped in _request_with_retry() for transient connection errors.
"""

import re
import os
import time
from datetime import date, datetime, timezone, timedelta
from typing import Iterator

import psycopg2
from psycopg2.extras import execute_values
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIG: per-ticker ATS endpoints
# ============================================================
# Each entry tells the loader which ATS to use and the platform-specific
# args. enabled=False means "skip for now" — we use this for non-Workday
# tickers so the config is complete but Day 4 only runs the verified ones.
#
# For Workday: tenant + site come from the URL pattern
#   https://{tenant}.{pod}.myworkdayjobs.com/{site}
# The pod (wd1, wd5, etc.) is part of the host. Get all three by visiting
# the careers page once and reading the URL.

COMPANIES_CONFIG = {
    # ---- WORKDAY (Day 4 targets) ----
    "NVDA": {
        "ats": "workday",
        "enabled": True,
        "host": "nvidia.wd5.myworkdayjobs.com",
        "tenant": "nvidia",
        "site": "NVIDIAExternalCareerSite",
        "force_faceted": True,
        "facet_param": "jobFamilyGroup",
    },
    "CDNS": {
        "ats": "workday",
        "enabled": True,
        "host": "cadence.wd1.myworkdayjobs.com",
        "tenant": "cadence",
        "site": "External_Careers",
    },
    "MRVL": {
        "ats": "workday",
        "enabled": True,
        "host": "marvell.wd1.myworkdayjobs.com",
        "tenant": "marvell",
        "site": "MarvellCareers",
    },

    # ---- WORKDAY (suspected, not yet verified) — Day 5 ----
    "QCOM": {"ats": "eightfold", "enabled": True,
        "host": "careers.qualcomm.com", "domain": "qualcomm.com", "ticker": "QCOM"},
    "INTC": {"ats": "workday", "enabled": True, "host": "intel.wd1.myworkdayjobs.com", "tenant": "intel", "site": "External"},
    "AVGO": {"ats": "workday", "enabled": True, "host": "broadcom.wd1.myworkdayjobs.com", "tenant": "broadcom", "site": "External_Career"},
    "MU": {"ats": "eightfold", "enabled": True,
       "host": "careers.micron.com", "domain": "micron.com", "ticker": "MU"},

    # ---- OTHER ATS (Day 5+) ----
    # AMD's public careers site (careers.amd.com) is a Jibe-fronted portal.
    # iCIMS is still the back-end ATS (apply_url + ats_code in the feed both
    # say icims), but the public job LISTINGS are served by Jibe's own API.
    # We fetch the Jibe feed because that's the source of truth for what AMD
    # actually advertises. Day 5 plan said "icims" before the migration was
    # known — see HANDOFF. ats tag = "jibe" (what the fetcher talks to).
    "AMD":  {"ats": "jibe", "enabled": True,
             "host": "careers.amd.com"},
    # Day 7: TalentBrew fetcher works structurally (headers + parser verified
    # against the response shape), but careers.synopsys.com sits behind
    # stateful anti-bot fingerprinting (likely Akamai/Imperva). curl with the
    # exact browser headers returns an empty envelope from the same IP, ruling
    # out User-Agent/Referer/X-Requested-With/session cookies as the gate.
    # Bypass would require a headless browser (Playwright) or curl-impersonate
    # — out of scope for Day 7. Leaving disabled; fetcher stays registered so
    # any non-fingerprinted TalentBrew site we encounter later works for free.
    "SNPS": {"ats": "talentbrew", "enabled": False,
             "host": "careers.synopsys.com",
             "note": "anti-bot gated; needs Playwright"},
    "ANSS": {"ats": "skip",       "enabled": False, "note": "Acquired by SNPS Jul 2025"},
    "TXN":  {"ats": "oracle_hcm", "enabled": True,
         "tenant_host": "edbz.fa.us2.oraclecloud.com",
         "public_host": "careers.ti.com"},
    "TSM": {"ats": "unknown", "enabled": False,
        "note": "SSR + anti-bot gated (403); needs Playwright"},
}

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
PAGE_SIZE = 20  # Workday's default; some tenants cap at 20
SLEEP_BETWEEN_PAGES = 0.5  # be polite, avoid getting rate-limited
SLEEP_BETWEEN_FACETS = 1.0  # extra politeness when looping facets

# ============================================================
# NETWORK RETRY HELPER
# ============================================================
# Wraps a single HTTP request with retries on transient connection errors.
# Retries the request itself, NOT the surrounding pagination — a reset on
# page 47 retries page 47, not pages 1–46. HTTP errors (4xx/5xx) are NOT
# retried here; call .raise_for_status() after, same as before.
_RETRYABLE = (
    ConnectionResetError,
    requests.exceptions.ConnectionError,
    requests.exceptions.ChunkedEncodingError,
    requests.exceptions.Timeout,
)

def _request_with_retry(method: str, url: str, *, attempts: int = 3,
                        base_delay: float = 1.0, backoff: float = 2.0,
                        **kwargs):
    """requests.request() with exponential backoff on transient failures."""
    delay = base_delay
    for attempt in range(1, attempts + 1):
        try:
            return requests.request(method, url, **kwargs)
        except _RETRYABLE as e:
            if attempt == attempts:
                raise
            print(f"  [retry] {method} {url[:70]}... "
                  f"{type(e).__name__}; attempt {attempt}/{attempts}, "
                  f"waiting {delay:.0f}s")
            time.sleep(delay)
            delay *= backoff

# ============================================================
# WORKDAY FETCHER
# ============================================================
# ============================================================
# NEW: fetch the available location facets for a Workday tenant
# ============================================================
def fetch_workday_facets(cfg: dict) -> list[tuple[str, str, str, int]]:
    """Return (facet_param, value_id, descriptor, count) tuples.
 
    If cfg["facet_param"] is set, use that exact facet (e.g. "jobFamilyGroup"
    for NVIDIA which exposes no location facet). Otherwise try to find a
    location facet by name.
    """
    url = f"https://{cfg['host']}/wday/cxs/{cfg['tenant']}/{cfg['site']}/jobs"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json",
               "Content-Type": "application/json"}
    body = {"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""}
    r = _request_with_retry("POST", url, headers=headers, json=body, timeout=30)    r.raise_for_status()
    data = r.json()
    
 
    target_facet = None
    explicit_param = cfg.get("facet_param")
 
    if explicit_param:
        # Caller told us exactly which facet to use.
        for f in data.get("facets", []):
            if f.get("facetParameter") == explicit_param:
                target_facet = f
                break
        if not target_facet:
            available = [f.get("facetParameter") for f in data.get("facets", [])]
            raise ValueError(
                f"Configured facet_param '{explicit_param}' not found for "
                f"{cfg['tenant']}. Available: {available}"
            )
    else:
        # Auto-detect: look for any location-named facet.
        for f in data.get("facets", []):
            if f.get("facetParameter", "").lower() in ("locations", "location",
                                                       "locationcountry"):
                target_facet = f
                break
        if not target_facet:
            for f in data.get("facets", []):
                if "location" in f.get("descriptor", "").lower():
                    target_facet = f
                    break
        if not target_facet:
            raise ValueError(f"No location facet found for {cfg['tenant']}")
 
    facet_param = target_facet["facetParameter"]
    values = target_facet.get("values", [])
    return [(facet_param, v["id"], v["descriptor"], v.get("count", 0))
            for v in values]

# fetch workday jobs -------------------------

def fetch_workday_jobs(ticker: str, cfg: dict) -> Iterator[dict]:
    """Yield normalized job dicts from a Workday tenant.
 
    If cfg.force_faceted is True (or if first query returns total >= 2000),
    re-runs queries per-location-facet to bypass the global 2000 cap.
    """
    force = cfg.get("force_faceted", False)
 
    if force:
        print(f"  {ticker}: faceted mode enabled, fetching location facets...")
        facets = fetch_workday_facets(cfg)
        print(f"  {ticker}: {len(facets)} location facets found, "
              f"summed count = {sum(c for _,_,_,c in facets)}")
        for facet_param, facet_id, descriptor, expected_count in facets:
            applied = {facet_param: [facet_id]}
            # If we're faceting on jobFamilyGroup, the descriptor IS the category.
            # Pass it through so _paginate_workday can stamp it on each row.
            facet_category = descriptor if facet_param == "jobFamilyGroup" else None
            yield from _paginate_workday(ticker, cfg, applied,
                                        label=f"{descriptor} ({expected_count})",
                                        facet_category=facet_category)
            time.sleep(SLEEP_BETWEEN_FACETS)
    else:
        yield from _paginate_workday(ticker, cfg, {}, label="all")

# pagination

def _paginate_workday(ticker: str, cfg: dict, applied_facets: dict,
                      label: str, facet_category=None) -> Iterator[dict]:
    """Inner helper: paginate one specific query (faceted or not)."""
    url = f"https://{cfg['host']}/wday/cxs/{cfg['tenant']}/{cfg['site']}/jobs"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json",
               "Content-Type": "application/json"}
    snapshot = date.today()
    offset = 0
    total = None
 
    while True:
        body = {"appliedFacets": applied_facets, "limit": PAGE_SIZE,
                "offset": offset, "searchText": ""}
        r = _request_with_retry("POST", url, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
 
        if total is None:
            total = data.get("total", 0)
            if total >= 2000 and not applied_facets:
                # Cap hit and we're NOT already faceting — warn the caller.
                print(f"  {ticker}: WARNING — total={total} hit the 2000 cap. "
                      "Set force_faceted=True for this ticker.")
            print(f"    [{label}] total={total}")
 
        postings = data.get("jobPostings", [])
        if not postings:
            break
 
        for p in postings:
            posted = _parse_workday_posted(p.get("postedOn"), snapshot)
            ext = p.get("externalPath", "")
            raw_id = ext.rsplit("/", 1)[-1] or p.get("bulletFields", [""])[0]
            yield {
                "job_id":        f"{ticker}:{raw_id}",
                "ticker":        ticker,
                "snapshot_date": snapshot,
                "title":         (p.get("title") or "").strip()[:500],
                "location":      (p.get("locationsText") or "").strip()[:300],
                "posted_date":   posted,
                "ats":           "workday",
                "job_url":       f"https://{cfg['host']}{ext}",
                "category":      facet_category, # was: None
            }
 
        offset += PAGE_SIZE
        if offset >= total:
            break
        time.sleep(SLEEP_BETWEEN_PAGES)

def _parse_workday_posted(s, snapshot: date):
    """Workday's postedOn is a relative phrase, not a date.
    Returns the snapshot date minus the implied delta, or None if unparseable.

    Known formats:
      "Posted Today"          → snapshot
      "Posted Yesterday"      → snapshot - 1 day
      "Posted 5 Days Ago"     → snapshot - 5 days
      "Posted 30+ Days Ago"   → snapshot - 30 days (we lose precision past a month)
    """
    if not s:
        return None
    s = s.lower().strip()
    if "today" in s:
        return snapshot
    if "yesterday" in s:
        return snapshot - timedelta(days=1)
    m = re.search(r"(\d+)", s)
    if m:
        return snapshot - timedelta(days=int(m.group(1)))
    return None

# ============================================================
# JIBE FETCHER  (AMD — added Day 5)
# ============================================================
# Jibe powers careers.amd.com. The site's own job list comes from:
#   GET https://{host}/api/jobs?page=N&sortBy=relevance&descending=false&internal=false
# Response shape:
#   {"jobs": [{"data": {<job>}}, ...], "totalCount": <int>, "count": <int>}
# Pagination: `page` is 1-indexed; the site serves 10 jobs/page. Paginate
# until we've collected `totalCount` jobs (or a page comes back empty).
#
# No auth, no faceting workaround needed: totalCount (1291 at time of
# writing) is well-defined and not a suspicious round cap like Workday's
# 2000 — straight pagination returns the full set. We still guard against
# a runaway loop with a hard page ceiling.

JIBE_PAGE_SIZE = 10        # what the site itself requests
JIBE_MAX_PAGES = 1000      # safety ceiling: 1000 * 10 = 10k jobs

def _parse_jibe_posted(s, snapshot: date):
    """Jibe's posted_date is a real ISO timestamp, e.g.
    "2026-05-21T01:15:00+0000" — unlike Workday's relative phrases.
    Return just the date component, or None if unparseable."""
    if not s:
        return None
    try:
        # fromisoformat doesn't accept "+0000"; normalize to "+00:00".
        iso = s.strip()
        if len(iso) >= 5 and iso[-5] in "+-" and iso[-3] != ":":
            iso = iso[:-2] + ":" + iso[-2:]
        return datetime.fromisoformat(iso).date()
    except (ValueError, TypeError):
        return None

def fetch_jibe_jobs(ticker: str, cfg: dict) -> Iterator[dict]:
    """Yield normalized job dicts from a Jibe-fronted careers site.

    Same return contract as fetch_workday_jobs: dicts with keys
    job_id, ticker, snapshot_date, title, location, posted_date,
    category, ats, job_url.
    """
    host = cfg["host"]
    base = f"https://{host}/api/jobs"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    snapshot = date.today()
    params = {"sortBy": "relevance", "descending": "false", "internal": "false"}

    page = 1
    total = None
    seen = 0

    while page <= JIBE_MAX_PAGES:
        params["page"] = page
        r = _request_with_retry("GET", base, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()

        if total is None:
            total = data.get("totalCount", data.get("count", 0))
            print(f"    [all] totalCount={total}")

        jobs = data.get("jobs", [])
        if not jobs:
            break

        for item in jobs:
            # Each list item wraps the real job under a "data" key.
            j = item.get("data", {})
            raw_id = j.get("req_id") or j.get("slug") or ""
            if not raw_id:
                continue  # skip anything we can't key on

            # Prefer the cleaned categories[].name ("Engineering") over the
            # top-level `category` list whose values have a leading space.
            cats = j.get("categories") or []
            category = cats[0].get("name") if cats else None

            # job_url: the public careers.amd.com page, from canonical_url.
            url = (j.get("meta_data", {}) or {}).get("canonical_url")
            if not url:
                url = f"https://{host}/jobs/{raw_id}"

            yield {
                "job_id":        f"{ticker}:{raw_id}",
                "ticker":        ticker,
                "snapshot_date": snapshot,
                "title":         (j.get("title") or "").strip()[:500],
                "location":      (j.get("full_location") or "").strip()[:300],
                "posted_date":   _parse_jibe_posted(j.get("posted_date"), snapshot),
                "category":      (category or "").strip()[:200] or None,
                "ats":           "jibe",
                "job_url":       url,
            }
            seen += 1

        if total and seen >= total:
            break
        page += 1
        time.sleep(SLEEP_BETWEEN_PAGES)
    else:
        # Loop exited via the page ceiling, not a natural stop — warn.
        print(f"  {ticker}: WARNING — hit JIBE_MAX_PAGES ({JIBE_MAX_PAGES}). "
              "Job count may be incomplete.")

# ============================================================
# TALENTBREW FETCHER  (SNPS — added Day 7)
# ============================================================
# TalentBrew (a TMP Worldwide / Radancy product) powers careers.synopsys.com.
# The site's pagination AJAX endpoint is:
#   GET https://{host}/search-jobs/results?CurrentPage=N&RecordsPerPage=15&...
# Response shape:
#   {"results": "<HTML string>", "filters": "...", "hasJobs": bool, ...}
# The HTML inside "results" contains <li class="search-results-list__list-item">
# elements — one per job — which we parse with BeautifulSoup.
#
# Critical: the endpoint returns an EMPTY response unless the request includes
#   X-Requested-With: XMLHttpRequest   (marks it as a "real" AJAX call)
#   Referer: https://{host}/search-jobs
# Without those headers the server returns {"results": "", "hasJobs": true}.
# This is a deliberate anti-scrape — discovered Day 7 via cURL inspection.
#
# Total job count is reported in the HTML as <h1>NNN results</h1>, which we
# also use as the loop termination signal alongside an empty-page check.

TALENTBREW_PAGE_SIZE = 15        # TalentBrew default; matches what the site sends
TALENTBREW_MAX_PAGES = 500       # safety ceiling: 500 * 15 = 7,500 jobs

# regex pulls the integer out of the "<h1>NNN results</h1>" header on page 1.
_TB_TOTAL_RE = re.compile(r"^\s*([\d,]+)\s+results?\s*$", re.IGNORECASE)

def _parse_talentbrew_posted(s, snapshot: date):
    """TalentBrew renders posted_date as 'MM/DD/YYYY' inside
    <span class="job-date-posted"><strong>Posted: </strong>05/18/2026</span>.
    Caller passes the stripped value ('05/18/2026'). Return a date or None."""
    if not s:
        return None
    try:
        return datetime.strptime(s.strip(), "%m/%d/%Y").date()
    except (ValueError, TypeError):
        return None

def fetch_talentbrew_jobs(ticker: str, cfg: dict) -> Iterator[dict]:
    """Yield normalized job dicts from a TalentBrew careers site.

    Same return contract as fetch_workday_jobs / fetch_jibe_jobs: dicts with
    keys job_id, ticker, snapshot_date, title, location, posted_date,
    category, ats, job_url.
    """
    host = cfg["host"]
    base = f"https://{host}/search-jobs/results"
    # The AJAX endpoint requires a real session. TalentBrew gates it on
    # a session cookie issued only when you hit the HTML listings page first
    # — X-Requested-With + Referer alone returns an empty envelope.
    # We use a requests.Session to capture the cookies on the warm-up GET,
    # then reuse them for every paginated API call.
    session = requests.Session()
    session.headers.update({
        "User-Agent":      USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
    })
    # Warm-up: hit the listings page to acquire session cookies.
    warm = session.get(f"https://{host}/search-jobs", timeout=30)
    warm.raise_for_status()

    # Per-request headers for the AJAX endpoint.
    api_headers = {
        "Accept":           "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer":          f"https://{host}/search-jobs",
    }
    snapshot = date.today()
    page = 1
    total = None
    seen = 0

    while page <= TALENTBREW_MAX_PAGES:
        params = {
            "ActiveFacetID":   0,
            "CurrentPage":     page,
            "RecordsPerPage":  TALENTBREW_PAGE_SIZE,
            "Keywords":        "",
            "Location":        "",
            "IsPagination":    "True",
            "SearchType":      5,
            "SortCriteria":    0,
            "SortDirection":   0,
        }
        r = session.get(base, headers=api_headers, params=params, timeout=30)
        r.raise_for_status()
        envelope = r.json()
        

        html = envelope.get("results", "")
        if not html.strip():
            # Either the X-Requested-With unlock failed or we paginated past
            # the end. Stop and let the total check below catch the mismatch.
            break

        soup = BeautifulSoup(html, "html.parser")

        # Capture total once, from the page-1 "<h1>NNN results</h1>" header.
        if total is None:
            h1 = soup.find("h1")
            if h1:
                m = _TB_TOTAL_RE.match(h1.get_text())
                if m:
                    total = int(m.group(1).replace(",", ""))
                    print(f"    [all] total={total}")

        items = soup.select("li.search-results-list__list-item")
        if not items:
            break  # natural end of pagination

        for li in items:
            # job_id: the long numeric id on the anchor (e.g. 95675649328).
            # This is TalentBrew's internal id, NOT the human "Job ID: 17299"
            # the candidate sees on the page — that one is in <span class="jobId">
            # and we keep it in job_url instead. We key on the long id because
            # it's what the URL routes on and is guaranteed unique.
            a = li.find("a", class_="sr-job-link")
            if a is None:
                continue
            raw_id = a.get("data-job-id")
            if not raw_id:
                continue

            # title: <h2> contains the title plus a trailing <img>. Strip
            # nested tags so we keep just the visible text.
            h2 = a.find("h2")
            title = h2.get_text(strip=True) if h2 else ""

            # location: <span class="job-location"> has a leading <img> icon;
            # get_text(strip=True) drops it because img has no text.
            loc_span = li.find("span", class_="job-location")
            location = loc_span.get_text(strip=True) if loc_span else ""

            # category: "<strong>Category: </strong>Engineering"
            # — split off the label prefix.
            cat_span = li.find("span", class_="category")
            category = None
            if cat_span:
                cat_text = cat_span.get_text(strip=True)
                category = cat_text.split("Category:", 1)[-1].strip() or None

            # posted_date: "Posted: 05/18/2026"
            posted_span = li.find("span", class_="job-date-posted")
            posted_raw = None
            if posted_span:
                posted_raw = posted_span.get_text(strip=True).split("Posted:", 1)[-1].strip()

            # job_url: href is relative ("/job/hillsboro/...") — prepend host.
            href = a.get("href") or ""
            url = f"https://{host}{href}" if href.startswith("/") else href

            yield {
                "job_id":        f"{ticker}:{raw_id}",
                "ticker":        ticker,
                "snapshot_date": snapshot,
                "title":         title[:500],
                "location":      location[:300],
                "posted_date":   _parse_talentbrew_posted(posted_raw, snapshot),
                "category":      (category or "")[:200] or None,
                "ats":           "talentbrew",
                "job_url":       url,
            }
            seen += 1

        if total and seen >= total:
            break
        page += 1
        time.sleep(SLEEP_BETWEEN_PAGES)
    else:
        print(f"  {ticker}: WARNING — hit TALENTBREW_MAX_PAGES ({TALENTBREW_MAX_PAGES}). "
              "Job count may be incomplete.")

# ============================================================
# EIGHTFOLD FETCHER  (QCOM — added Day 8)
# ============================================================
# Eightfold AI powers careers.qualcomm.com. The search API is:
#   GET https://{host}/api/pcsx/search?domain=...&query=&location=&start=N&sort_by=timestamp
# Response: {"status": 200, "data": {"count": <int>, "positions": [...], ...}}
# Pagination: `start` is 0-indexed offset, page size = 10 (server-determined).
# No auth, no cookies, plain GET.

EIGHTFOLD_PAGE_SIZE = 10
EIGHTFOLD_MAX_PAGES = 500  # 500 * 10 = 5k jobs ceiling

def fetch_eightfold_jobs(ticker: str, cfg: dict) -> Iterator[dict]:
    base = f"https://{cfg['host']}/api/pcsx/search"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    params = {
        "domain":   cfg["domain"],
        "query":    "",
        "location": "",
        "sort_by":  "timestamp",
    }
    snapshot = date.today()
    start = 0
    total = None
    seen = 0

    for _ in range(EIGHTFOLD_MAX_PAGES):
        params["start"] = start
        r = _request_with_retry("GET", base, headers=headers, params=params, timeout=30)
        data = r.json()["data"]

        if total is None:
            total = data["count"]
            print(f"    [all] total={total}")

        positions = data.get("positions", [])
        if not positions:
            break

        for p in positions:
            posted = (datetime.fromtimestamp(p["postedTs"]).date()
                      if p.get("postedTs") else None)
            yield {
                "job_id":        f"{ticker}:{p['displayJobId']}",
                "ticker":        ticker,
                "snapshot_date": snapshot,
                "title":         (p.get("name") or "").strip()[:500],
                "location":      (p["locations"][0] if p.get("locations") else "")[:300] or None,
                "posted_date":   posted,
                "category":      (p.get("department") or "").strip()[:200] or None,
                "ats":           "eightfold",
                "job_url":       f"https://{cfg['host']}{p['positionUrl']}",
            }
            seen += 1

        start += EIGHTFOLD_PAGE_SIZE
        if total and seen >= total:
            break
        time.sleep(SLEEP_BETWEEN_PAGES)
    else:
        print(f"  {ticker}: WARNING — hit EIGHTFOLD_MAX_PAGES. Job count may be incomplete.")

# ============================================================
# ORACLE HCM FETCHER  (TXN — added Day 8)
# ============================================================
# Oracle HCM Cloud (Oracle Fusion Recruiting) powers careers.ti.com.
# The careers-cloud REST API is well-documented and follows a standard
# pattern across all Oracle HCM tenants:
#   GET https://{tenant_host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions
#       ?onlyData=true&finder=findReqs;siteNumber=CX,facetsList=...
#       &limit=25&offset=N&sortBy=POSTING_DATES_DESC
# Response envelope:
#   {"items": [{"TotalJobsCount": <int>, "requisitionList": [<job>, ...], ...}]}
# Pagination: `offset` += `limit` until offset >= TotalJobsCount.
# No auth, no cookies. The {tenant_host} (edbz.fa.us2.oraclecloud.com for TXN)
# is the company's Oracle Cloud tenant — find it via DevTools Network tab.
#
# Note: individual jobs don't carry a `Category` field. Categories live in
# the aggregated `categoriesFacet` only. Same quirk as non-faceted Workday —
# we leave category=NULL for Oracle HCM rows. Documented in HANDOFF §8.

ORACLE_PAGE_SIZE = 25
ORACLE_MAX_PAGES = 500  # 500 * 25 = 12.5k jobs ceiling

# The full finder param is verbose but the server requires its exact shape.
# Built once as a constant rather than f-strung per request.
_ORACLE_FINDER = (
    "findReqs;siteNumber=CX,"
    "facetsList=LOCATIONS;WORK_LOCATIONS;WORKPLACE_TYPES;TITLES;"
    "CATEGORIES;ORGANIZATIONS;POSTING_DATES;FLEX_FIELDS"
)
_ORACLE_EXPAND = (
    "requisitionList.workLocation,"
    "requisitionList.otherWorkLocations,"
    "requisitionList.secondaryLocations,"
    "flexFieldsFacet.values,"
    "requisitionList.requisitionFlexFields"
)

_ORACLE_FACETS = (
    "LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES"
    "%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS"
)

def _parse_oracle_posted(s):
    """Oracle returns PostedDate as ISO 'YYYY-MM-DD'. Parse to date or None."""
    if not s:
        return None
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def fetch_oracle_hcm_jobs(ticker: str, cfg: dict) -> Iterator[dict]:
    """Yield normalized job dicts from an Oracle HCM careers site.

    Same return contract as the other fetchers.
    """
    base = f"https://{cfg['tenant_host']}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    snapshot = date.today()
    offset = 0
    total = None
    seen = 0

    for _ in range(ORACLE_MAX_PAGES):
        url = (
            f"{base}?onlyData=true"
            f"&expand={_ORACLE_EXPAND}"
            f"&finder=findReqs;siteNumber=CX,"
            f"facetsList={_ORACLE_FACETS},"
            f"limit={ORACLE_PAGE_SIZE},"
            f"sortBy=POSTING_DATES_DESC,"
            f"offset={offset}"
        )
        r = _request_with_retry("GET", url, headers=headers, timeout=30)
        r.raise_for_status()
        envelope = r.json()

        items = envelope.get("items", [])
        if not items:
            break
        search_result = items[0]

        if total is None:
            total = search_result.get("TotalJobsCount", 0)
            print(f"    [all] total={total}")

        reqs = search_result.get("requisitionList", [])
        if not reqs:
            break

        for j in reqs:
            raw_id = j.get("Id")
            if not raw_id:
                continue
            yield {
                "job_id":        f"{ticker}:{raw_id}",
                "ticker":        ticker,
                "snapshot_date": snapshot,
                "title":         (j.get("Title") or "").strip()[:500],
                "location":      (j.get("PrimaryLocation") or "").strip()[:300],
                "posted_date":   _parse_oracle_posted(j.get("PostedDate")),
                "category":      None,  # Not present per-job; see header comment
                "ats":           "oracle_hcm",
                "job_url":       f"https://{cfg['public_host']}/en/sites/CX/jobs/preview/{raw_id}/",
            }
            seen += 1

        offset += ORACLE_PAGE_SIZE
        if total and seen >= total:
            break
        time.sleep(SLEEP_BETWEEN_PAGES)
    else:
        print(f"  {ticker}: WARNING — hit ORACLE_MAX_PAGES. Job count may be incomplete.")

# ============================================================
# DB INSERT
# ============================================================
def deduplicate_jobs(rows: list[dict]) -> list[dict]:
    """A job can appear under multiple location facets (e.g. a posting listing
    Santa Clara + Austin shows up in both facet queries). Keep first occurrence.
    Dedup key matches the DB PK: (job_id, snapshot_date).
    """
    seen = set()
    out = []
    for r in rows:
        key = (r["job_id"], r["snapshot_date"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out

def insert_jobs(conn, rows: list[dict]) -> int:
    """Batched insert with ON CONFLICT DO NOTHING.

    Conflict on (job_id, snapshot_date) means we already captured this job
    today — fine to skip, this script is safe to re-run.

    Returns the rowcount from the last batch (cosmetic — see HANDOFF §9 about
    the load_patents.py rowcount bug; same issue applies here. We log len(rows)
    submitted instead of trusting rowcount.)
    """
    if not rows:
        return 0
    cols = ["job_id", "ticker", "snapshot_date", "title", "location",
            "posted_date", "category", "ats", "job_url"]
    values = [tuple(r[c] for c in cols) for r in rows]
    sql = f"""
        INSERT INTO hiring_signals ({', '.join(cols)})
        VALUES %s
        ON CONFLICT (job_id, snapshot_date) DO NOTHING
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, values, page_size=500)
    conn.commit()
    return len(rows)


# ============================================================
# FETCHER DISPATCH
# ============================================================
# Day 4 hardcoded fetch_workday_jobs() inside main(), so "add a platform"
# really meant "edit main()". This registry makes the original intent real:
# a fetcher is registered by its `ats` name, main() looks it up. Adding a
# platform = write the function + add one line here. All fetchers share the
# same contract: fetch(ticker, cfg) -> iterator of 9-key job dicts.
FETCHERS = {
    "workday":    fetch_workday_jobs,
    "jibe":       fetch_jibe_jobs,         # AMD — added Day 5
    "talentbrew": fetch_talentbrew_jobs,   # SNPS — added Day 7
    "eightfold":  fetch_eightfold_jobs,    # QCOM — added Day 8
    "oracle_hcm": fetch_oracle_hcm_jobs,   # TXN — added Day 8
}

# ============================================================
# MAIN
# ============================================================
def main():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    total_submitted = 0
    started = datetime.now(timezone.utc)

    for ticker, cfg in COMPANIES_CONFIG.items():
        if not cfg.get("enabled"):
            print(f"  {ticker}: skipped (ats={cfg['ats']}, not yet implemented)")
            continue

        fetcher = FETCHERS.get(cfg["ats"])
        if fetcher is None:
            print(f"  {ticker}: no fetcher registered for ats='{cfg['ats']}' "
                  "— skipping")
            continue

        print(f"\nFetching {ticker} ({cfg['ats']})...")
        try:
            rows = list(fetcher(ticker, cfg))
            rows = deduplicate_jobs(rows)
            n = insert_jobs(conn, rows)
            total_submitted += n
            print(f"  {ticker}: submitted {n} rows")
        except requests.HTTPError as e:
            print(f"  {ticker}: HTTP error — {e}")
        except Exception as e:
            print(f"  {ticker}: failed — {type(e).__name__}: {e}")

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    print(f"\nDone. Submitted {total_submitted} rows in {elapsed:.1f}s.")
    print("(Note: 'submitted' counts what we sent to INSERT — actual new rows "
          "depends on ON CONFLICT skips. Query the table to confirm.)")
    conn.close()


if __name__ == "__main__":
    main()
