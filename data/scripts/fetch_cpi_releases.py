"""Download original MoSPI CPI press releases (PDF) for a range of reference
months and save them unchanged as data/raw/cpi_releases/CPI_<YYYY-MM>_press_release.pdf
plus a text extraction (.txt) and a manifest (URL, HTTP status, download time).

The release URL is not published as a list, so candidate file names on the
usual pattern CPI_PR_<day><mon><yy>.pdf are tried for days 10-16 of the
following month. A file is accepted only if its text names the expected
reference month ("FOR THE MONTH OF <MONTH> <YEAR>"). Nothing is estimated:
dates/times are read from the release itself by parse_cpi_releases.py.

    research/.venv/bin/python data/scripts/fetch_cpi_releases.py 2024-01 2025-11
    # releases not on the pattern (found by web search), verified the same way:
    research/.venv/bin/python data/scripts/fetch_cpi_releases.py --urls 2025-07=https://... 2025-08=https://...
"""
import datetime
import json
import re
import pathlib
import subprocess
import sys

from pypdf import PdfReader

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "raw" / "cpi_releases"
BASE = "https://www.mospi.gov.in/sites/default/files/press_release/"
MON = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
FULL = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
        "OCTOBER", "NOVEMBER", "DECEMBER"]


def months(a, b):
    y, m = map(int, a.split("-"))
    while f"{y}-{m:02d}" <= b:
        yield y, m
        y, m = (y + (m == 12), m % 12 + 1)


def candidates(y, m):
    ry, rm = (y + (m == 12), m % 12 + 1)  # released the following month
    for d in range(10, 17):
        full = FULL[rm - 1].lower()
        for mon in (MON[rm - 1], MON[rm - 1].capitalize(), full, full.capitalize()):
            for day in (f"{d}", f"{d:02d}"):
                yield f"CPI_PR_{day}{mon}{str(ry)[2:]}.pdf"


def get(url, path):
    r = subprocess.run(["curl", "-s", "-m", "90", "-A", "Mozilla/5.0", "-o", str(path), "-w", "%{http_code}", url],
                       capture_output=True, text=True)
    return int(r.stdout or 0)


def main(a, b, explicit=None):
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "manifest_mospi_pdfs.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    for y, m in months(a, b):
        target = OUT / f"CPI_{y}-{m:02d}_press_release.pdf"
        if target.exists():
            print("have", target.name)
            continue
        tmp = OUT / "_tmp.pdf"
        found = None
        urls = [explicit[f"{y}-{m:02d}"]] if explicit else [BASE + n for n in candidates(y, m)]
        for url in urls:
            name = url
            code = get(url, tmp)
            if code != 200 or not tmp.read_bytes()[:4] == b"%PDF":
                continue
            text = "\n".join(p.extract_text() or "" for p in PdfReader(tmp).pages)
            if re.search(rf"MONTH OF {FULL[m - 1]},? {y}", " ".join(text.upper().split())):
                found = (name, text)
                break
        if not found:
            print("NOT FOUND", f"{y}-{m:02d}")
            manifest.append({"reference_month": f"{y}-{m:02d}", "status": "not_found"})
            continue
        tmp.rename(target)
        target.with_suffix(".txt").write_text(found[1])
        manifest.append({"reference_month": f"{y}-{m:02d}", "url": found[0], "file": target.name,
                         "retrieved_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        print("ok", f"{y}-{m:02d}", found[0])
    (OUT / "_tmp.pdf").unlink(missing_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "--urls":
        pairs = dict(a.split("=", 1) for a in sys.argv[2:])
        for ref, url in sorted(pairs.items()):
            main(ref, ref, {ref: url})
    else:
        main(*sys.argv[1:3])
