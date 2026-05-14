"""
download_patents.py

Downloads the 4 PatentsView TSV bulk files needed for the patents ETL.
- Streams downloads (chunks) — required for 1GB+ files
- Resume-safe: if interrupted, re-running picks up where it left off
- Idempotent: skips files already fully downloaded
- Shows progress per file

Notes:
- PatentsView migrated to USPTO Open Data Portal (data.uspto.gov) on March 20, 2026.
  Legacy S3 URLs below still serve files as of project start (Week 1 Day 2 verification).
  If any URL 404s, check https://data.uspto.gov/bulkdata/datasets/pvgpatdis for the
  current canonical location and update FILES below.

Usage:
    python etl/download_patents.py

Output:
    Files written to data/  (gitignored)
"""

from pathlib import Path
import requests
import sys
import time

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# Project root = parent of etl/ directory. When script lives in etl/, this
# resolves to sector-signals/, so data/ lands in sector-signals/data/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# PatentsView bulk download S3 base. New canonical home is data.uspto.gov, but
# these legacy S3 URLs still serve as of project start. If they 404, see
# transition guidance at data.uspto.gov/support/transition-guidance/patentsview.
S3_BASE = "https://s3.amazonaws.com/data.patentsview.org/download"

FILES = [
    "g_patent.tsv.zip",                  # ~1 GB    — patent_id, title, grant_date
    "g_assignee_disambiguated.tsv.zip",  # ~359 MB  — patent_id -> assignee org
    "g_inventor_disambiguated.tsv.zip",  # ~500 MB  — patent_id -> inventors
    "g_cpc_current.tsv.zip",             # ~600 MB  — patent_id -> CPC class
]

CHUNK_SIZE = 1024 * 1024  # 1 MB chunks — big enough to be efficient, small enough to show progress


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def human_size(num_bytes: int) -> str:
    """Format bytes as human-readable string. 1234567 -> '1.2 MB'."""
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def download_one(filename: str) -> bool:
    """
    Download one file from S3 to DATA_DIR, with resume + progress.
    Returns True on success (or already-downloaded), False on failure.
    """
    url = f"{S3_BASE}/{filename}"
    dest = DATA_DIR / filename
    tmp = dest.with_suffix(dest.suffix + ".part")  # write to .part, rename on success

    # HEAD request to learn the full file size before deciding whether to skip.
    try:
        head = requests.head(url, allow_redirects=True, timeout=30)
        head.raise_for_status()
    except requests.RequestException as e:
        print(f"  ✗ HEAD failed for {filename}: {e}")
        return False

    total_size = int(head.headers.get("Content-Length", 0))

    # Skip if already fully downloaded.
    if dest.exists() and dest.stat().st_size == total_size:
        print(f"  ✓ {filename} already complete ({human_size(total_size)}) — skipping")
        return True

    # Resume from partial download if .part file exists.
    resume_from = tmp.stat().st_size if tmp.exists() else 0
    headers = {"Range": f"bytes={resume_from}-"} if resume_from else {}

    print(f"  → {filename} ({human_size(total_size)}) ", end="", flush=True)
    if resume_from:
        print(f"[resuming from {human_size(resume_from)}] ", end="", flush=True)

    try:
        with requests.get(url, headers=headers, stream=True, timeout=60) as r:
            r.raise_for_status()
            # Append if resuming, otherwise fresh write.
            mode = "ab" if resume_from else "wb"
            downloaded = resume_from
            last_print = time.time()
            with open(tmp, mode) as f:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Throttle progress prints to every 2 seconds — otherwise
                    # terminal flushing becomes the bottleneck on fast connections.
                    if time.time() - last_print > 2:
                        pct = (downloaded / total_size * 100) if total_size else 0
                        print(f"\r  → {filename}: {human_size(downloaded)}/{human_size(total_size)} ({pct:.1f}%)    ", end="", flush=True)
                        last_print = time.time()
    except requests.RequestException as e:
        print(f"\n  ✗ Download failed mid-stream: {e}")
        print(f"     Partial file kept at {tmp} — re-run to resume.")
        return False

    # Atomic rename .part -> final. If anything above failed, .part stays for resume.
    tmp.rename(dest)
    print(f"\r  ✓ {filename} complete ({human_size(total_size)})                    ")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"Downloading {len(FILES)} PatentsView bulk files to {DATA_DIR}")
    print(f"Total expected: ~2.5 GB. Allow ~15 min on a 30 Mbps connection.\n")

    results = {fn: download_one(fn) for fn in FILES}

    print("\nSummary:")
    for fn, ok in results.items():
        print(f"  {'✓' if ok else '✗'} {fn}")

    failed = [fn for fn, ok in results.items() if not ok]
    if failed:
        print(f"\n{len(failed)} file(s) failed. Re-run the script to resume.")
        sys.exit(1)
    print("\nAll downloads complete.")


if __name__ == "__main__":
    main()
