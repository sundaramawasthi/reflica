"""Offline preflight for the intended experiment machine (protocol §10, S4). No API.

    python experiments/full_run/preflight.py OUT.json      (run from research/)

Checks, in order, and records everything in OUT.json:
  1. this interpreter and packages vs requirements-experiment.lock
  2. existing freeze records vs disk (benchmark, B5, config v1.7, renders)
  3. protocol lock state (draft or frozen, and valid)
  4. the full offline test suite (includes the runner dry run with the network blocked
     and every model call replaced by a replay of the pilot's responses)
  5. the gate's answer right now (refuses while the protocol is a draft)
  6. the fingerprints a freeze on this machine would record, plus machine details
Exit code 0 only if 1–4 pass. Run it on the intended machine and send OUT.json to
the owner before freezing; a report from any other machine does not count.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RESEARCH))
from reflica_bench import protocol_lock as pl  # noqa: E402


def main(out: Path) -> int:
    report: dict = {"generated_at": datetime.now(timezone.utc).isoformat(),
                    "machine": pl.platform_info() | pl.environment(), "steps": {}}
    st = report["steps"]
    st["1_environment_lock"] = pl.environment_lock_problems()
    st["2_record_problems"] = pl.record_problems()
    st["3_lock_state"] = {"frozen": pl.active_version() is not None, "problems": pl.check_lock()}
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=RESEARCH,
                           capture_output=True, text=True)
    st["4_test_suite"] = {"exit_code": tests.returncode, "summary": tests.stdout.strip().splitlines()[-1:]}
    try:
        pl.assert_ready_for_llm_calls()
        st["5_gate"] = "READY (protocol frozen and all fingerprints match)"
    except RuntimeError as e:
        st["5_gate"] = f"REFUSED: {str(e).splitlines()[0]}"
    fp = pl.fingerprints(pl.FULL_RUN / pl.DRAFT_FILE)
    report["fingerprints_for_freeze"] = fp
    report["all_packages"] = pl.all_packages()
    ok = not st["1_environment_lock"] and not st["2_record_problems"] and not st["3_lock_state"]["problems"] \
        and tests.returncode == 0
    report["preflight_passed"] = ok
    out.write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: report[k] for k in ("machine", "steps", "preflight_passed")}, indent=1, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
