"""Freeze rule for the full-experiment protocol: a frozen protocol cannot change
silently, a documented versioned amendment is allowed, and no LLM call is
allowed before freezing."""

from __future__ import annotations

import json
import pytest

from reflica_bench import protocol_lock as pl

DRAFT = "# Protocol\n\n**Status: DRAFT v0.1 — NOT FROZEN.**\n\nbody\n"
SUPERSEDED = "# Protocol\n\n**Status: SUPERSEDED — see PROTOCOL.v1.0.md.**\n"
FROZEN = "# Protocol\n\n**Status: FROZEN v1.0 (approved 2026-10-11).**\n\nbody\n"
AMENDED = "# Protocol\n\n**Status: FROZEN v1.1 (amendment 1).**\n\nbody, changed\n"


def _entry(d, file, version, supersedes=None, fps=None):
    sha = pl.sha256(d / file)
    return {"version": version, "file": file, "sha256": sha, "frozen_at": "2026-10-11",
            "approved_by": "owner", "supersedes": supersedes,
            "fingerprints": fps or {"protocol_sha256": sha}}


def _freeze(d, entries):
    (d / pl.LOCK_NAME).write_text(json.dumps({"versions": entries}))


@pytest.fixture
def frozen_dir(tmp_path):
    (tmp_path / "PROTOCOL.md").write_text(SUPERSEDED)
    (tmp_path / "PROTOCOL.v1.0.md").write_text(FROZEN)
    _freeze(tmp_path, [_entry(tmp_path, "PROTOCOL.v1.0.md", "1.0")])
    return tmp_path


# --- the real repository --------------------------------------------------

def test_existing_freeze_records_match_files_on_disk():
    assert pl.record_problems() == []


def test_b5_version_id_rule_reproduces_recorded_id():
    frozen = json.loads((pl.B5_DIR / "FROZEN.json").read_text())
    assert pl.b5_version_id(frozen["files"]) == frozen["version_id"] == "fc9524a4ea38cca5"


def test_repository_protocol_is_valid_draft_or_valid_frozen():
    assert pl.check_lock() == []


def test_no_llm_call_allowed_while_protocol_is_a_draft():
    if pl.active_version() is not None:
        pytest.skip("protocol frozen; covered by assert_ready tests")
    with pytest.raises(RuntimeError, match="not frozen"):
        pl.assert_ready_for_llm_calls()


# --- the rule itself, on temporary directories ------------------------------

def test_draft_must_be_marked(tmp_path):
    (tmp_path / "PROTOCOL.md").write_text(DRAFT)
    assert pl.check_lock(tmp_path) == []
    (tmp_path / "PROTOCOL.md").write_text("# Protocol\n\n**Status: v0.2**\n")
    assert pl.check_lock(tmp_path)


def test_frozen_protocol_passes(frozen_dir):
    assert pl.check_lock(frozen_dir) == []


def test_draft_must_be_marked_superseded_after_freezing(frozen_dir):
    (frozen_dir / "PROTOCOL.md").write_text(DRAFT)
    assert any("SUPERSEDED" in p for p in pl.check_lock(frozen_dir))


def test_editing_a_frozen_protocol_fails(frozen_dir):
    (frozen_dir / "PROTOCOL.v1.0.md").write_text(FROZEN + "one silent change\n")
    assert any("edited" in p for p in pl.check_lock(frozen_dir))


def test_deleting_a_frozen_protocol_fails(frozen_dir):
    (frozen_dir / "PROTOCOL.v1.0.md").unlink()
    assert any("missing" in p for p in pl.check_lock(frozen_dir))


def test_frozen_file_must_say_frozen(tmp_path):
    (tmp_path / "PROTOCOL.v1.0.md").write_text(DRAFT)
    _freeze(tmp_path, [_entry(tmp_path, "PROTOCOL.v1.0.md", "1.0")])
    assert any("FROZEN" in p for p in pl.check_lock(tmp_path))


def test_documented_amendment_passes(frozen_dir):
    v1 = json.loads((frozen_dir / pl.LOCK_NAME).read_text())["versions"][0]
    (frozen_dir / "PROTOCOL.v1.1.md").write_text(AMENDED)
    v2 = _entry(frozen_dir, "PROTOCOL.v1.1.md", "1.1", supersedes=v1["sha256"])
    (frozen_dir / "AMENDMENTS.md").write_text(
        f"## Amendment 1\nfrom {v1['sha256']}\nto {v2['sha256']}\nreason: ...\n")
    _freeze(frozen_dir, [v1, v2])
    assert pl.check_lock(frozen_dir) == []
    assert pl.active_version(frozen_dir)["version"] == "1.1"


def test_undocumented_amendment_fails(frozen_dir):
    v1 = json.loads((frozen_dir / pl.LOCK_NAME).read_text())["versions"][0]
    (frozen_dir / "PROTOCOL.v1.1.md").write_text(AMENDED)
    _freeze(frozen_dir, [v1, _entry(frozen_dir, "PROTOCOL.v1.1.md", "1.1", supersedes=v1["sha256"])])
    assert any("AMENDMENTS.md" in p for p in pl.check_lock(frozen_dir))


def test_amendment_must_chain_and_be_a_new_file(frozen_dir):
    v1 = json.loads((frozen_dir / pl.LOCK_NAME).read_text())["versions"][0]
    (frozen_dir / "PROTOCOL.v1.1.md").write_text(AMENDED)
    bad_chain = _entry(frozen_dir, "PROTOCOL.v1.1.md", "1.1", supersedes="0" * 64)
    _freeze(frozen_dir, [v1, bad_chain])
    assert any("supersedes" in p for p in pl.check_lock(frozen_dir))
    reuse = dict(v1, version="1.1", supersedes=v1["sha256"])
    _freeze(frozen_dir, [v1, reuse])
    assert any("new file" in p for p in pl.check_lock(frozen_dir))


def _gated_dir(tmp_path):
    (tmp_path / "PROTOCOL.md").write_text(SUPERSEDED)
    (tmp_path / "PROTOCOL.v1.0.md").write_text(FROZEN)
    fps = pl.fingerprints(tmp_path / "PROTOCOL.v1.0.md", full_run_dir=tmp_path)
    _freeze(tmp_path, [_entry(tmp_path, "PROTOCOL.v1.0.md", "1.0", fps=fps)])
    return fps


def test_ready_gate_accepts_matching_fingerprints_and_rejects_any_mismatch(tmp_path):
    fps = _gated_dir(tmp_path)
    assert pl.assert_ready_for_llm_calls(tmp_path)["version"] == "1.0"
    for key in ("benchmark_manifest_sha256", "b5_version_id", "llm_config_sha256", "rendered_texts_sha256",
                "baselines_code", "pilot_code", "runtime_code", "analysis_code", "environment", "full_run_code",
                "environment_lock_sha256"):
        tampered = dict(fps, **{key: "x"})
        _freeze(tmp_path, [_entry(tmp_path, "PROTOCOL.v1.0.md", "1.0", fps=tampered)])
        with pytest.raises(RuntimeError, match=key):
            pl.assert_ready_for_llm_calls(tmp_path)


def test_record_only_fingerprints_are_not_gate_checked(tmp_path):
    fps = _gated_dir(tmp_path)
    _freeze(tmp_path, [_entry(tmp_path, "PROTOCOL.v1.0.md", "1.0", fps=dict(fps, environment_all_packages="x"))])
    assert pl.assert_ready_for_llm_calls(tmp_path)["version"] == "1.0"


def test_runner_added_or_changed_after_freezing_blocks_the_gate(tmp_path):
    _gated_dir(tmp_path)
    (tmp_path / "runner.py").write_text("print('hello')\n")
    with pytest.raises(RuntimeError, match="full_run_code"):
        pl.assert_ready_for_llm_calls(tmp_path)


def test_amended_version_becomes_the_gated_version(tmp_path):
    fps = _gated_dir(tmp_path)
    v1 = json.loads((tmp_path / pl.LOCK_NAME).read_text())["versions"][0]
    (tmp_path / "runner.py").write_text("print('hello')\n")          # the change the amendment documents
    (tmp_path / "PROTOCOL.v1.1.md").write_text(AMENDED)
    fps2 = pl.fingerprints(tmp_path / "PROTOCOL.v1.1.md", full_run_dir=tmp_path)
    v2 = _entry(tmp_path, "PROTOCOL.v1.1.md", "1.1", supersedes=v1["sha256"], fps=fps2)
    (tmp_path / "AMENDMENTS.md").write_text(f"from {v1['sha256']} to {v2['sha256']}: runner added\n")
    _freeze(tmp_path, [v1, v2])
    assert pl.check_lock(tmp_path) == []
    assert pl.assert_ready_for_llm_calls(tmp_path)["version"] == "1.1"
    assert fps != fps2


def test_gate_record_is_written_once_and_checked_by_analysis(tmp_path):
    proto = tmp_path / "proto"
    proto.mkdir()
    _gated_dir(proto)
    run = tmp_path / "run1"
    assert pl.check_gate_record(run, proto)                      # no record: refused
    pl.write_gate_record(run, proto)
    assert pl.check_gate_record(run, proto) == []
    with pytest.raises(RuntimeError, match="gated once"):
        pl.write_gate_record(run, proto)
    rec = json.loads((run / pl.GATE_RECORD).read_text())
    (run / pl.GATE_RECORD).write_text(json.dumps(dict(rec, protocol_sha256="0" * 64)))
    assert pl.check_gate_record(run, proto)                      # unknown protocol: refused
    tampered = dict(rec, fingerprints=dict(rec["fingerprints"], b5_version_id="x"))
    (run / pl.GATE_RECORD).write_text(json.dumps(tampered))
    assert any("fingerprints differ" in p for p in pl.check_gate_record(run, proto))


def test_gate_record_cannot_be_written_for_a_draft(tmp_path):
    with pytest.raises(RuntimeError, match="not frozen"):
        pl.write_gate_record(tmp_path / "run")
    assert not (tmp_path / "run" / pl.GATE_RECORD).exists()


# --- entry points ------------------------------------------------------------

NETWORK_MODULES = {"_api", "repeatability", "pilot_api", "urllib", "urllib.request", "http", "http.client",
                   "requests", "httpx", "openai", "google", "google.genai", "socket", "aiohttp"}


def _imports(path):
    import ast
    names = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_only_the_gated_runner_can_reach_a_model():
    """Under experiments/full_run only runner.py may import anything that can
    reach a model or the network; its requests are proven gated by
    tests/test_full_run.py (AST: transport called only in _request after
    self.gate(); runtime: a full gate before every request)."""
    for p in sorted(pl.FULL_RUN.rglob("*.py")):
        net = _imports(p) & NETWORK_MODULES
        if p.name != "runner.py":
            assert not net, f"{p}: imports {net}; only runner.py may reach a model"


def test_runner_default_transport_is_only_used_as_the_transport():
    import ast
    tree = ast.parse((pl.FULL_RUN / "runner.py").read_text())
    uses = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "default_transport"]
    assert len(uses) == 1  # `self.transport = transport or default_transport`
    init = next(f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and f.name == "__init__")
    assert any(u in list(ast.walk(init)) for u in uses)


def test_pilot_entry_points_cannot_address_the_full_run():
    """The pilot scripts are not gated (they predate the protocol and are
    fingerprinted as they are); they must stay limited to the pilot."""
    for name in ("pilot.py", "repeatability.py", "list_models.py", "gemini_models.py"):
        text = (pl.PILOT / name).read_text()
        assert "full_run" not in text, name
        assert "canonical_files" not in text, name


# --- environment lock (P3) -----------------------------------------------------

def test_this_environment_matches_the_lock():
    assert pl.environment_lock_problems() == []


def test_environment_lock_detects_differences(tmp_path):
    good = pl.ENV_LOCK.read_text()
    bad = tmp_path / "lock"
    bad.write_text(good.replace("# python==", "# python==0.0.0-was-") )
    assert any("python" in p for p in pl.environment_lock_problems(bad))
    first_pin = next(x for x in good.splitlines() if x and not x.startswith("#"))
    bad.write_text(good.replace(first_pin, first_pin.split("==")[0] + "==0.0.0"))
    assert any("0.0.0" in p for p in pl.environment_lock_problems(bad))
    bad.write_text(good + "a-package-that-is-not-installed==1.0\n")
    assert any("not-installed" in p for p in pl.environment_lock_problems(bad))
    assert pl.environment_lock_problems(tmp_path / "missing") == ["missing missing"]


def test_gate_refuses_when_the_environment_differs_from_the_lock(tmp_path, monkeypatch):
    bad = tmp_path / "lock"
    bad.write_text(pl.ENV_LOCK.read_text().replace("# python==", "# python==0.0.0-was-"))
    monkeypatch.setattr(pl, "ENV_LOCK", bad)
    _gated_dir(tmp_path)  # fingerprints record this lock file, so only the version check can object
    with pytest.raises(RuntimeError, match="python"):
        pl.assert_ready_for_llm_calls(tmp_path)
