import requests

# Try the legacy S3 URL first (smallest file: g_assignee_disambiguated)
urls_to_test = [
    "https://s3.amazonaws.com/data.patentsview.org/download/g_assignee_disambiguated.tsv.zip",
    "https://data.uspto.gov/data/g_assignee_disambiguated.tsv.zip",
]

for url in urls_to_test:
    print(f"\nTesting: {url}")
    try:
        # HEAD request just checks if the file exists, doesn't download it
        r = requests.head(url, allow_redirects=True, timeout=10)
        print(f"  Status: {r.status_code}")
        size = r.headers.get("Content-Length")
        if size:
            print(f"  Size: {int(size) / 1_000_000:.1f} MB")
    except Exception as e:
        print(f"  Error: {e}")