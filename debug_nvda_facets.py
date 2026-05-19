"""Quick diagnostic: print all facets NVIDIA's Workday API returns
so we can see what parameter name to match on. Throwaway script."""
import requests
import json

url = "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
body = {"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""}

r = requests.post(url, headers=headers, json=body, timeout=30)
data = r.json()

print(f"Total jobs: {data.get('total')}")
print(f"\nAll facets returned by NVIDIA:")
print("-" * 60)
for f in data.get("facets", []):
    param = f.get("facetParameter", "<no param>")
    desc = f.get("descriptor", "<no descriptor>")
    n_values = len(f.get("values", []))
    print(f"  facetParameter='{param}'   descriptor='{desc}'   values={n_values}")

# Also dump the raw first facet so we can see the full structure
if data.get("facets"):
    print(f"\nFirst facet (full structure, first 3 values):")
    first = data["facets"][0]
    print(json.dumps({
        "facetParameter": first.get("facetParameter"),
        "descriptor": first.get("descriptor"),
        "values": first.get("values", [])[:3],
    }, indent=2))
