"""Build data/processed/cpi_series_revised_<date>.csv from the raw API pages
saved by fetch_cpi_api.py (latest run per base year + series).

Keeps only All-India CPI General (headline) rows. Values are the API's latest
REVISED values: training use only, never first release (vintage=latest_revised).
The series label comes from the request URL in each run's manifest, because the
2012-base rows themselves do not say whether they are Current or Back series.

    python3 data/scripts/build_cpi_series.py
"""
import csv
import json
import pathlib
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "raw" / "cpi_api"
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}


def latest_runs():
    """{(base_year, series): run_dir}, latest run wins."""
    runs = {}
    for d in sorted(RAW.glob("base*_*")):
        man = json.loads((d / "manifest.json").read_text())
        q = urllib.parse.parse_qs(urllib.parse.urlparse(man[0]["url"]).query)
        runs[(q["base_year"][0], q.get("series", ["Current"])[0])] = (d, man)
    return runs


def main():
    out_rows, retrieved = {}, ""
    for (base, series), (d, man) in sorted(latest_runs().items()):
        for m in man:
            if m["status"] != 200:
                continue
            retrieved = max(retrieved, m["retrieved_at_utc"][:10])
            for r in json.loads((d / m["file"]).read_text()).get("data", []):
                if r.get("state") != "All India":
                    continue
                if base == "2024":
                    if r.get("division") != "CPI (General)" or r.get("group"):
                        continue
                elif r.get("group") != "General" or r.get("subgroup") != "General-Overall":
                    continue
                if r.get("index") in (None, ""):
                    continue
                ym = f"{int(r['year'])}-{MONTHS[r['month']]:02d}"
                key = (ym, f"{base}=100", series, r["sector"])
                out_rows[key] = [ym, f"{base}=100", series, r["sector"], r["index"], r.get("inflation") or "",
                                 r.get("status") or r.get("series") or "", m["url"].split("?")[0],
                                 m["retrieved_at_utc"][:10], "latest_revised"]
    path = ROOT / "processed" / f"cpi_series_revised_{retrieved}.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["reference_month", "base_year", "series", "sector", "index", "yoy_inflation", "api_status",
                    "source", "retrieved_at", "vintage"])
        w.writerows(out_rows[k] for k in sorted(out_rows))
    print(path, len(out_rows), "rows")


if __name__ == "__main__":
    main()
