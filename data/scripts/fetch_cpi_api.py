"""Download CPI data from the MoSPI e-Sankhyiki API (/api/cpi/getCPIData).

Run on your own computer (the cloud session cannot reach mospi.gov.in).
Needs MOSPI_USER / MOSPI_PASS in the environment (registered via
/api/users/usersignup, see docs/CPI API User Manual.pdf); without a login token
the API officially returns only the first 10 records. Credentials are never
written to disk by this script; the token lives only in memory (valid 30 min).

    python3 data/scripts/fetch_cpi_api.py --base-year 2012 --level group --from-year 2013 --to-year 2025
    python3 data/scripts/fetch_cpi_api.py --base-year 2024 --from-year 2025 --to-year 2026

Every raw API page is saved unchanged under data/raw/cpi_api/, together with a
manifest recording the request URL and the download time. Nothing is cleaned or
merged here. The values are the API's *current* (possibly revised) values, not
first releases.

If the base URL below is wrong, copy the "Request URL" shown by "Try it out" on
the API page and pass its host with --base-url.
"""

import argparse
import datetime
import json
import pathlib
import os
import subprocess
import time
import urllib.parse

DEFAULT_BASE_URL = "https://api.mospi.gov.in"  # confirmed 2026-10-16
OUT_DIR = pathlib.Path(__file__).resolve().parents[1] / "raw" / "cpi_api"


# curl, not urllib: the MoSPI server needs legacy TLS renegotiation, which
# Python's ssl module refuses (UNSAFE_LEGACY_RENEGOTIATION_DISABLED).
def _curl(args):
    out = subprocess.run(["curl", "-s", "-m", "120", "-w", "\n%{http_code}", *args],
                         capture_output=True, text=True, check=True).stdout
    body, _, code = out.rpartition("\n")
    return int(code or 0), body


def login(base_url):
    user, password = os.environ.get("MOSPI_USER"), os.environ.get("MOSPI_PASS")
    if not user or not password:
        raise SystemExit("Set MOSPI_USER and MOSPI_PASS in the environment.")
    status, body = _curl(["-X", "POST", f"{base_url}/api/users/login", "-H", "Content-Type: application/json",
                          "-d", json.dumps({"username": user, "password": password})])
    token = json.loads(body).get("response") if status == 200 else None
    if not isinstance(token, str) or not token:
        raise SystemExit(f"login failed (HTTP {status})")
    return token


def fetch(url, token):
    return _curl(["-H", "Accept: application/json", "-H", f"Authorization: {token}", url])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--base-year", type=int, required=True, choices=[2010, 2012, 2024])
    parser.add_argument("--level", choices=["group", "subgroup", "item"],
                        help="required for base years 2010 and 2012")
    parser.add_argument("--from-year", type=int, required=True)
    parser.add_argument("--to-year", type=int, required=True)
    parser.add_argument("--limit", type=int, default=100)  # API maximum is 100 (2026-10-16)
    parser.add_argument("--extra", nargs="*", default=[],
                        help="extra filters as key=value, e.g. sector_code=3")
    args = parser.parse_args()
    if args.base_year in (2010, 2012) and not args.level:
        parser.error("--level is required for base years 2010 and 2012")

    token, token_time = login(args.base_url), time.time()
    run_dir = OUT_DIR / f"base{args.base_year}_{datetime.datetime.now():%Y%m%dT%H%M%S}"
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = []

    for year in range(args.from_year, args.to_year + 1):
        page = 1
        while True:
            params = {"base_year": args.base_year, "year": year, "limit": args.limit, "page": page}
            if args.level:
                params["level"] = args.level.capitalize()  # API accepts "Group", rejects "group"
            params.update(dict(item.split("=", 1) for item in args.extra))
            url = f"{args.base_url}/api/cpi/getCPIData?{urllib.parse.urlencode(params)}"
            retrieved_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            if time.time() - token_time > 25 * 60:  # token valid 30 min
                token, token_time = login(args.base_url), time.time()
            status, body = fetch(url, token)
            path = run_dir / f"{year}_page{page:03d}.json"
            path.write_text(body, encoding="utf-8")
            manifest.append({"url": url, "status": status, "file": path.name,
                             "retrieved_at_utc": retrieved_at})
            print(status, url)
            if status != 200:  # 409 = no (more) data for this year
                break
            try:
                records = json.loads(body).get("data", [])
            except (ValueError, AttributeError):
                records = []
            if len(records) < args.limit:
                break
            page += 1
            time.sleep(0.5)

    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Saved {len(manifest)} responses to {run_dir}")


if __name__ == "__main__":
    main()
