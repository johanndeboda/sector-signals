"""
load_hiring.py — Fetch current job postings from semi-12 careers sites
and insert them into hiring_signals.

DAY 4 SCOPE: Workday tenants only (NVDA, CDNS, MRVL). Other ATS platforms
(iCIMS for AMD, Avature for SNPS/ANSS, Oracle for TXN, plus unverified
TSM) are stubbed in the config but skipped at runtime. Day 5 work.

How Workday's job-search API works:
  POST https://{tenant}.{podN}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
  Body: {"appliedFacets": {}, "limit": 20, "offset": N, "searchText": ""}
  Response: {"jobPostings": [...], "total": <int>}
  We paginate by incrementing offset until we've fetched all `total` jobs.

This is the public API the company's own careers page uses — no auth,
no scraping HTML, just JSON. Same idempotency pattern as load_patents.py:
ON CONFLICT DO NOTHING on (job_id, snapshot_date) PK.
"""
import re
import os
import time
from datetime import date, datetime, timezone, timedelta
from typing import Iterator

import psycopg2
from psycopg2.extras import execute_values
import requests
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
    "QCOM": {"ats": "unknown", "enabled": False, "host": "careers.qualcomm.com", "tenant": None, "site": None},
    "INTC": {"ats": "workday", "enabled": True, "host": "intel.wd1.myworkdayjobs.com", "tenant": "intel", "site": "External"},
    "AVGO": {"ats": "workday", "enabled": True, "host": "broadcom.wd1.myworkdayjobs.com", "tenant": "broadcom", "site": "External_Career"},
    "MU":   {"ats": "unknown", "enabled": False, "host": "careers.micron.com", "tenant": None, "site": None},

    # ---- OTHER ATS (Day 5+) ----
    # AMD's public careers site (careers.amd.com) is a Jibe-fronted portal.
    # iCIMS is still the back-end ATS (apply_url + ats_code in the feed both
    # say icims), but the public job LISTINGS are served by Jibe's own API.
    # We fetch the Jibe feed because that's the source of truth for what AMD
    # actually advertises. Day 5 plan said "icims" before the migration was
    # known — see HANDOFF. ats tag = "jibe" (what the fetcher talks to).
    "AMD":  {"ats": "jibe", "enabled": True,
             "host": "careers.amd.com"},
    "SNPS": {"ats": "avature",    "enabled": False},
    "ANSS": {"ats": "skip",       "enabled": False, "note": "Acquired by SNPS Jul 2025"},
    "TXN":  {"ats": "oracle_hcm", "enabled": False},
    "TSM":  {"ats": "unknown",    "enabled": False},
}

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
PAGE_SIZE = 20  # Workday's default; some tenants cap at 20
SLEEP_BETWEEN_PAGES = 0.5  # be polite, avoid getting rate-limited
SLEEP_BETWEEN_FACETS = 1.0  # extra politeness when looping facets

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
    r = requests.post(url, headers=headers, json=body, timeout=30)
    r.raise_for_status()
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
        r = requests.post(url, headers=headers, json=body, timeout=30)
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
        r = requests.get(base, headers=headers, params=params, timeout=30)
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
    "workday": fetch_workday_jobs,
    "jibe":    fetch_jibe_jobs,   # AMD — added Day 5
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
