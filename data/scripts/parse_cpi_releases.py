"""Parse first-release values and release date/time from the original CPI
press releases (text extracted by fetch_cpi_releases.py) and add one row per
reference month to data/processed/cpi_release_calendar.csv.

Rules (data/README.md): date/time only as printed on the release (embargo line
"till <time> of <date>", or PIB "Posted On"); if no time is printed it stays
blank (never inferred from the usual schedule). Values are the Combined
All-India CPI (General) as first published (Provisional). Existing calendar
rows are never overwritten.

    python3 data/scripts/parse_cpi_releases.py 2024-01 2025-11
"""
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "raw" / "cpi_releases"
CAL = ROOT / "processed" / "cpi_release_calendar.csv"
MONTH = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                     "september", "october", "november", "december"], 1)}
N = r"(-?\d+\s?\.\s?\d+)"


def loose(word: str) -> str:
    """Regex for a word whose letters may be split by stray spaces in PDF text."""
    return r"\s?".join(re.escape(c) for c in word if c != " ").replace(r"\s?\ ", r"\s+")


def num(s: str) -> str:
    return s.replace(" ", "")


def parse(ref: str, text: str) -> dict:
    t = " ".join(text.split())
    out = {"time": "", "date": "", "how": ""}
    e = re.search(loose("till") + r"\s*([\d.:]+\s?[AP]\.?\s?M\.?)\s*of\s*(\d+)\s?(?:st|nd|rd|th)?\s*([A-Za-z]+),?\s*(\d{4})", t)
    if e:
        out.update(time=e.group(1).replace(".", ":").replace(" ", "").upper().replace("PM", " PM").replace("AM", " AM"),
                   date=f"{e.group(4)}-{MONTH[e.group(3).lower()]:02d}-{int(e.group(2)):02d}", how="embargo line")
    else:
        d = re.search(r"Dated(?: the)?\s+(\d+)(?:st|nd|rd|th)?\s+([A-Za-z]+),?\s+(\d{4})", t)
        if d:
            out.update(date=f"{d.group(3)}-{MONTH[d.group(2).lower()]:02d}-{int(d.group(1)):02d}",
                       how="'Dated' line only; no release time printed")
    gen = loose("CPI (General)")
    tab = re.search(loose("Inflation") + r"\s+(?:Rates?\s+)?(?:\(%\)\s+)?" + gen + r"\s+" + N + r"\s+" + N + r"\s+" + N, t)
    sen = re.search(r"Consumer Price Index \(CPI\) for the month of [A-Za-z]+,? \d{4} over [A-Za-z]+,? \d{4} is " + N + "%", t)
    idx = re.search(loose("Index") + r"\s+" + gen + r"\s+" + N + r"\s+" + N + r"\s+" + N, t)
    out["yoy"] = num(tab.group(3)) if tab else (num(sen.group(1)) if sen else "")
    out["yoy_check"] = "" if not (tab and sen) else ("agree" if num(tab.group(3)) == num(sen.group(1)) else "DISAGREE")
    out["index"] = num(idx.group(3)) if idx else ""
    out["base"] = "2024=100" if "2024=100" in t else "2012=100"
    return out


def time24(t: str) -> str:
    m = re.match(r"(\d{1,2}):(\d{2}) (AM|PM)", t)
    if not m:
        return ""
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "PM" else 0)
    return f"{h:02d}:{m.group(2)}"


def main(a: str, b: str) -> None:
    manifest = {m["reference_month"]: m for m in json.loads((RAW / "manifest_mospi_pdfs.json").read_text())
                if m.get("file")}
    rows = list(csv.DictReader(CAL.open()))
    have = {r["reference_month"] for r in rows}
    fields = list(rows[0].keys())
    added = []
    for ref, m in sorted(manifest.items()):
        if not (a <= ref <= b) or ref in have:
            continue
        p = parse(ref, (RAW / m["file"]).with_suffix(".txt").read_text())
        note = (f"Yes (original MoSPI/NSO release PDF; {p['how']}; values Provisional, "
                f"table/sentence check: {p['yoy_check'] or 'single source'})")
        added.append({**{k: "" for k in fields}, "reference_month": ref, "release_date": p["date"],
                      "release_time_ist": time24(p["time"]), "source_url": m["url"], "base_year": p["base"],
                      "status": "provisional", "headline_cpi_index": p["index"], "headline_yoy_inflation": p["yoy"],
                      "retrieved_at": m["retrieved_at_utc"][:10], "first_release_verified": note})
    rows = sorted(rows + added, key=lambda r: r["reference_month"])
    with CAL.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    for r in added:
        print(r["reference_month"], r["release_date"], r["release_time_ist"] or "(no time)", r["headline_cpi_index"],
              r["headline_yoy_inflation"], "|", r["first_release_verified"][-40:])


if __name__ == "__main__":
    main(*sys.argv[1:3])
