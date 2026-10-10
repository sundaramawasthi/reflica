"""Fingerprints and freeze checks for the full-experiment protocol (§9–§10).

Two jobs:

1. `fingerprints()` hashes everything a full-run result depends on and
   `record_problems()` checks each existing freeze record against the files
   on disk (benchmark manifest, B5 FROZEN.json, LLM config v1.7).
2. `check_lock()` enforces the protocol's versioning rule:

   * no `protocol_lock.json`  -> DRAFT: PROTOCOL.md must say DRAFT / NOT FROZEN;
   * with a lock              -> every listed version file must still hash to
     its recorded value (a frozen file is never edited). A later version must
     be a new file whose entry names the previous hash in `supersedes` and
     appears in AMENDMENTS.md with both hashes.

`assert_ready_for_llm_calls()` is what the full-run runner calls before its
first API request; it raises unless the protocol is frozen and every
gate-checked fingerprint matches the active lock entry. `write_gate_record()`
calls it and stores the result in the run folder; `check_gate_record()` is
what the analysis calls, so data from a run that skipped the gate is refused.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import rn

ROOT = Path(rn.PKG).parent                       # research/
FULL_RUN = ROOT / "experiments" / "full_run"
PILOT = ROOT / "experiments" / "rn_pilot"
B5_DIR = Path(rn.PKG) / "b5"
ENV_LOCK = ROOT / "requirements-experiment.lock"
LOCK_NAME = "protocol_lock.json"
DRAFT_FILE = "PROTOCOL.md"
GATE_RECORD = "gate.json"

# Code that turns raw outputs into verdicts; frozen with the protocol.
ANALYSIS_FILES = ("evaluator.py", "endpoints.py", "stats.py", "schema.py", "loader.py",
                  "adapters.py", "baseline.py", "extraction_schema.py", "protocol_lock.py")
# Code that produces method outputs or the prompts' inputs at run time.
RUNTIME_FILES = ("rn.py", "linter.py", "gt_engine.py", "groundtruth.py", "groundtruth_quant.py")
# Pilot code the full runner reuses (call, render_prompt, from_direct, _remap).
PILOT_CODE = ("_api.py", "repeatability.py", "pilot.py")
# Packages whose version can change a result; checked exactly by the gate.
KEY_PACKAGES = ("pydantic", "pydantic-core", "ortools", "networkx", "protobuf", "numpy")
# Recorded in the lock for the record, but not compared by the gate.
RECORD_ONLY = ("environment_all_packages",)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def b5_version_id(files: dict[str, str]) -> str:
    """B5's id as recorded in b5/FROZEN.json: first 16 hex of
    sha256(json.dumps({file: sha256}, sort_keys=True))."""
    return _sha_text(json.dumps(files, sort_keys=True))[:16]


def rendered_texts_sha256() -> tuple[str, list[str]]:
    """Render all 63 canonical scenarios (deterministic, in memory) and hash
    the renders in scenario-id order. Also returns leakage problems."""
    from .loader import load_scenario

    parts, problems = [], []
    for p in rn.canonical_files():
        sc = load_scenario(p)
        r = rn.render(sc, rn._sha(p))
        problems += [f"{sc.scenario_id}: {x}" for x in rn.check_leakage(r, sc)]
        parts.append((sc.scenario_id, r.model_dump_json()))
    return _sha_text("\n".join(j for _, j in sorted(parts))), problems


def _version(pkg: str) -> str | None:
    try:
        return importlib.metadata.version(pkg)
    except importlib.metadata.PackageNotFoundError:
        return None


def environment() -> dict:
    return {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "packages": {p: _version(p) for p in KEY_PACKAGES},
    }


def all_packages() -> list[str]:
    return sorted(f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions())


def _all_packages_sha256() -> str:
    return _sha_text("\n".join(all_packages()))


def platform_info() -> dict:
    return {"system": platform.system(), "release": platform.release(), "machine": platform.machine(),
            "python_build": " ".join(platform.python_build())}


def _norm(name: str) -> str:
    return name.lower().replace("_", "-").replace(".", "-")


def environment_lock_problems(lock_path: Path | None = None) -> list[str]:
    """Compare this interpreter and its installed packages with the exact pins
    in requirements-experiment.lock (P3). Extra installed packages are allowed
    (they are recorded in the run folder); missing or different ones are not."""
    lock_path = Path(lock_path) if lock_path is not None else ENV_LOCK
    if not lock_path.exists():
        return [f"{Path(lock_path).name} missing"]
    out = []
    installed = {_norm(d.metadata["Name"]): d.version for d in importlib.metadata.distributions()}
    for line in Path(lock_path).read_text().splitlines():
        line = line.strip()
        if line.startswith("# python=="):
            want = line.split("==", 1)[1].strip()
            if sys.version.split()[0] != want:
                out.append(f"python {sys.version.split()[0]} != locked {want}")
        if not line or line.startswith("#"):
            continue
        name, _, version = line.partition("==")
        have = installed.get(_norm(name))
        if have != version:
            out.append(f"{name}: installed {have} != locked {version}")
    return out


def fingerprints(protocol_file: Path | None = None, heldout_manifest: Path | None = None,
                 full_run_dir: Path = FULL_RUN) -> dict:
    cfg_path = PILOT / "config.frozen.json"
    b5_files = {p.name: sha256(p) for p in sorted(B5_DIR.glob("*.py"))}
    rendered, _ = rendered_texts_sha256()
    fp = {
        "benchmark_manifest_sha256": sha256(rn.MANIFEST),
        "b5_files": b5_files,
        "b5_version_id": b5_version_id(b5_files),
        "llm_config_sha256": sha256(cfg_path),
        "prompts": {p.name: sha256(p) for p in sorted((PILOT / "prompts").glob("*.txt"))},
        "schemas": {p.name: sha256(p) for p in sorted(PILOT.glob("*.schema*.json"))},
        "client_sha256": sha256(PILOT / "_api.py"),
        "rendered_texts_sha256": rendered,
        "render_version": rn.RENDER_VERSION,
        "analysis_code": {f: sha256(Path(rn.PKG) / f) for f in ANALYSIS_FILES},
        "runtime_code": {f: sha256(Path(rn.PKG) / f) for f in RUNTIME_FILES},
        "baselines_code": {p.name: sha256(p) for p in sorted((Path(rn.PKG) / "baselines").glob("*.py"))},
        "pilot_code": {f: sha256(PILOT / f) for f in PILOT_CODE},
        # Any runner written under full_run/ is covered automatically: adding or
        # changing one after freezing makes the gate fail until an amendment.
        "full_run_code": {str(p.relative_to(full_run_dir)): sha256(p)
                          for p in sorted(Path(full_run_dir).rglob("*.py"))},
        "environment": environment(),
        "environment_lock_sha256": sha256(ENV_LOCK) if ENV_LOCK.exists() else None,
        "environment_all_packages": _all_packages_sha256(),
    }
    if protocol_file is not None:
        fp["protocol_sha256"] = sha256(protocol_file)
    if heldout_manifest is not None:
        fp["heldout_manifest_sha256"] = sha256(heldout_manifest)
    return fp


def record_problems() -> list[str]:
    """Check the existing freeze records against the files on disk."""
    out = [f"benchmark: {d}" for d in rn.verify_manifest()]
    frozen = json.loads((B5_DIR / "FROZEN.json").read_text())
    now = {p.name: sha256(p) for p in sorted(B5_DIR.glob("*.py"))}
    if now != frozen["files"]:
        out.append("B5: source files differ from b5/FROZEN.json")
    if b5_version_id(frozen["files"]) != frozen["version_id"]:
        out.append("B5: FROZEN.json version_id does not match its file hashes")
    cfg = json.loads((PILOT / "config.frozen.json").read_text())
    if cfg["benchmark_manifest_sha256"] != sha256(rn.MANIFEST):
        out.append("config: benchmark manifest hash differs")
    for name, digest in cfg["prompts"].items():
        if sha256(PILOT / "prompts" / name) != digest:
            out.append(f"config: prompt {name} differs")
    for name, digest in cfg["schemas"].items():
        if sha256(PILOT / name) != digest:
            out.append(f"config: schema {name} differs")
    if cfg["client_fingerprint"] != sha256(PILOT / "_api.py"):
        out.append("config: client (_api.py) differs")
    if cfg["extraction_schema_module_fingerprint"] != sha256(Path(rn.PKG) / "extraction_schema.py"):
        out.append("config: extraction_schema.py differs")
    _, leaks = rendered_texts_sha256()
    out += [f"render leakage: {x}" for x in leaks]
    return out


# ---------------------------------------------------------------------------
# Freeze / amendment rule
# ---------------------------------------------------------------------------

def _status_line(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("**Status:"):
            return line
    return ""


def check_lock(directory: Path = FULL_RUN) -> list[str]:
    directory = Path(directory)
    lock_path = directory / LOCK_NAME
    if not lock_path.exists():
        status = _status_line((directory / DRAFT_FILE).read_text())
        if "DRAFT" not in status or "NOT FROZEN" not in status:
            return [f"no {LOCK_NAME}, so {DRAFT_FILE} must be marked DRAFT / NOT FROZEN"]
        return []
    out: list[str] = []
    draft = directory / DRAFT_FILE
    if draft.exists() and "SUPERSEDED" not in _status_line(draft.read_text()):
        out.append(f"{DRAFT_FILE} must be marked SUPERSEDED once a frozen version exists")
    versions = json.loads(lock_path.read_text()).get("versions", [])
    if not versions:
        return [f"{LOCK_NAME} lists no versions"]
    amendments = (directory / "AMENDMENTS.md").read_text() if (directory / "AMENDMENTS.md").exists() else ""
    seen_files: set[str] = set()
    prev = None
    for i, v in enumerate(versions):
        f = directory / v["file"]
        tag = f"version {v.get('version')} ({v['file']})"
        if v["file"] in seen_files:
            out.append(f"{tag}: reuses a file of an earlier version; an amendment must be a new file")
        seen_files.add(v["file"])
        for key in ("version", "file", "sha256", "frozen_at", "approved_by", "fingerprints"):
            if not v.get(key):
                out.append(f"{tag}: missing '{key}'")
        if not f.exists():
            out.append(f"{tag}: file missing")
            continue
        if sha256(f) != v["sha256"]:
            out.append(f"{tag}: frozen file was edited (hash differs)")
        if "FROZEN" not in _status_line(f.read_text()) or "NOT FROZEN" in _status_line(f.read_text()):
            out.append(f"{tag}: status line must say FROZEN")
        if (v.get("fingerprints") or {}).get("protocol_sha256") not in (None, v["sha256"]):
            out.append(f"{tag}: fingerprints.protocol_sha256 differs from sha256")
        if i == 0:
            if v.get("supersedes"):
                out.append(f"{tag}: first version cannot supersede anything")
        else:
            if v.get("supersedes") != prev["sha256"]:
                out.append(f"{tag}: 'supersedes' must equal the previous version's sha256")
            if v["sha256"] not in amendments or prev["sha256"] not in amendments:
                out.append(f"{tag}: AMENDMENTS.md must record this amendment with both hashes")
        prev = v
    return out


def active_version(directory: Path = FULL_RUN) -> dict | None:
    lock_path = Path(directory) / LOCK_NAME
    if not lock_path.exists():
        return None
    return json.loads(lock_path.read_text())["versions"][-1]


def assert_ready_for_llm_calls(directory: Path = FULL_RUN) -> dict:
    """Raise unless the protocol is frozen, the lock is valid and every
    fingerprint matches the active version. Returns the active version."""
    problems = check_lock(directory)
    active = active_version(directory)
    if active is None:
        raise RuntimeError("protocol is not frozen (no protocol_lock.json); no LLM call may be made")
    problems += record_problems()
    problems += environment_lock_problems()
    heldout = active["fingerprints"].get("heldout_manifest_file")
    now = fingerprints(Path(directory) / active["file"],
                       Path(directory) / heldout if heldout else None, full_run_dir=Path(directory))
    for k, v in now.items():
        if k not in RECORD_ONLY and active["fingerprints"].get(k) != v:
            problems.append(f"fingerprint mismatch: {k}")
    if problems:
        raise RuntimeError("not ready for LLM calls:\n" + "\n".join(problems))
    return active


def write_gate_record(run_dir: Path, directory: Path = FULL_RUN) -> dict:
    """Run the gate and write its result to `run_dir/gate.json`. The runner
    must call this before its first request; it raises (and writes nothing)
    if the gate fails, and refuses to overwrite an existing record."""
    active = assert_ready_for_llm_calls(directory)
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / GATE_RECORD
    if path.exists():
        raise RuntimeError(f"{path} exists; a run folder is gated once")
    rec = {"passed_at": datetime.now(timezone.utc).isoformat(), "protocol_version": active["version"],
           "protocol_sha256": active["sha256"], "fingerprints": active["fingerprints"],
           "environment_all_packages_now": _all_packages_sha256()}
    path.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    return rec


def check_gate_record(run_dir: Path, directory: Path = FULL_RUN) -> list[str]:
    """Analysis-side check: a run folder is usable only if it holds a gate
    record matching a version in the lock (the version active when it ran)."""
    path = Path(run_dir) / GATE_RECORD
    if not path.exists():
        return [f"{path}: missing; this run did not pass the freeze gate"]
    rec = json.loads(path.read_text())
    lock = Path(directory) / LOCK_NAME
    versions = json.loads(lock.read_text())["versions"] if lock.exists() else []
    match = [v for v in versions if v["sha256"] == rec.get("protocol_sha256")]
    if not match:
        return [f"{path}: protocol {rec.get('protocol_sha256')} is not a frozen version"]
    if match[0]["fingerprints"] != rec.get("fingerprints"):
        return [f"{path}: fingerprints differ from lock version {match[0]['version']}"]
    return []
