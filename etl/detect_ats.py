"""
detect_ats.py — One-off diagnostic. Identifies which Applicant Tracking System
(ATS) each of the 12 semi companies uses.

Run once at the start of Day 4 to confirm what platforms we need to scrape.
Output is a printed table that becomes the basis for `etl/load_hiring.py` config.

This is a Day-3-style throwaway: useful for the decision, not production.
"""
import requests
from urllib.parse import urlparse

# Starting URLs — public careers landing pages. Some redirect to ATS subdomain,
# which is exactly the signal we want.
COMPANIES = {
    "AMD":  "https://careers.amd.com",
    "ANSS": "https://careers.ansys.com",       # ANSYS — but acquired by SNPS Jul 2025
    "AVGO": "https://www.broadcom.com/company/careers",
    "CDNS": "https://www.cadence.com/en_US/home/company/careers.html",
    "INTC": "https://jobs.intel.com",
    "MRVL": "https://www.marvell.com/company/careers.html",
    "MU":   "https://www.micron.com/careers",
    "NVDA": "https://www.nvidia.com/en-us/about-nvidia/careers/",
    "QCOM": "https://careers.qualcomm.com",
    "SNPS": "https://careers.synopsys.com",
    "TSM":  "https://www.tsmc.com/english/careers",
    "TXN":  "https://careers.ti.com",
}

# Substrings in the final URL or HTML that fingerprint each ATS.
# Order matters — more specific first.
ATS_SIGNATURES = [
    ("Workday",        ["myworkdayjobs.com", "wd1.myworkday", "wd5.myworkday"]),
    ("Greenhouse",     ["boards.greenhouse.io", "greenhouse.io/embed"]),
    ("Lever",          ["jobs.lever.co"]),
    ("SmartRecruiters",["smartrecruiters.com"]),
    ("iCIMS",          ["icims.com"]),
    ("Eightfold",      ["eightfold.ai", ".eightfold.ai"]),
    ("SuccessFactors", ["successfactors.com", "successfactors.eu"]),
    ("Taleo",          ["taleo.net"]),
    ("Phenom",         ["phenompeople.com"]),
    ("Avature",        ["avature.net"]),
]

def detect(ticker: str, url: str) -> dict:
    """Hit the URL, follow redirects, scan final URL + HTML for ATS signatures."""
    try:
        # Many career sites block default Python UA — pretend to be a browser.
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/120.0 Safari/537.36"}
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        final_url = r.url
        html = r.text.lower()
        # Combine final URL + first 50KB of HTML to scan. Most ATS embed scripts
        # live in the <head>, so 50KB is more than enough.
        haystack = final_url.lower() + " " + html[:50000]

        for ats_name, sigs in ATS_SIGNATURES:
            for sig in sigs:
                if sig in haystack:
                    return {"ats": ats_name, "final_url": final_url, "status": r.status_code}
        return {"ats": "UNKNOWN", "final_url": final_url, "status": r.status_code}
    except Exception as e:
        return {"ats": "ERROR", "final_url": "", "status": str(e)[:60]}

def main():
    print(f"{'Ticker':<8}{'ATS':<18}{'Status':<10}Final URL")
    print("-" * 100)
    for ticker, url in COMPANIES.items():
        result = detect(ticker, url)
        print(f"{ticker:<8}{result['ats']:<18}{str(result['status']):<10}{result['final_url'][:60]}")

if __name__ == "__main__":
    main()
