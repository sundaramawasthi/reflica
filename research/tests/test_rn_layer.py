"""R-N layer: freeze, deterministic rendering, leakage prevention, pilot."""

from __future__ import annotations

import json

import pytest

from reflica_bench import rn
from reflica_bench.adapters import NaturalLanguageAdapter_v1
from reflica_bench.linter import LintError, assert_no_forbidden_fields
from reflica_bench.loader import load_scenario
from reflica_bench.schema import GroundTruth


def _pilot():
    for sid in rn.PILOT_IDS:
        yield rn.load_rn(sid), load_scenario(rn.source_path(sid))


def test_canonical_benchmark_is_frozen_at_63_v0_2_0():
    m = json.loads(rn.MANIFEST.read_text())
    assert m["count"] == 63 and m["benchmark_version"] == "0.2.0"
    assert rn.verify_manifest() == []


def test_v0_1_0_manifest_preserved_and_differs_only_by_hygiene_fix():
    old = json.loads((rn.PKG / "frozen_manifest_v0.1.0.json").read_text())
    new = json.loads(rn.MANIFEST.read_text())
    assert old["benchmark_version"] == "0.1.0" and old["count"] == 63
    changed = [k for k in old["files"] if old["files"][k] != new["files"][k]]
    assert changed == ["scenarios/cat1/cat1_add_disconnected.json"]


def test_pilot_composition():
    ids = rn.PILOT_IDS
    assert len(ids) == len(set(ids)) == 16
    for prefix, n in (("cat1", 2), ("cat2", 2), ("cat3", 2), ("cat4", 2), ("cat5", 2), ("cat6a", 1), ("cat6b", 1), ("cat7", 4)):
        assert sum(i.startswith(prefix + "_") for i in ids) == n, prefix
    subs = {load_scenario(rn.source_path(i)).subcategory for i in ids if i.startswith("cat7")}
    assert subs == {"ambiguous", "false_ambiguous"}


def test_pilot_files_match_frozen_sources_and_rerender_identically():
    for r, sc in _pilot():
        assert r.source_sha256 == rn._sha(rn.source_path(sc.scenario_id))
        assert r.render_version == rn.RENDER_VERSION
        assert rn.render(sc, r.source_sha256) == r, sc.scenario_id


def test_pilot_is_leak_free():
    for r, sc in _pilot():
        assert rn.check_leakage(r, sc) == [], sc.scenario_id


def test_renderer_never_reads_ground_truth_or_labels():
    for _, sc in _pilot():
        blind = sc.model_copy(deep=True)
        blind.ground_truth = GroundTruth()
        blind.category, blind.subcategory, blind.template_id = 0, None, "X"
        blind.evaluation_annotations.attribute_types.clear()
        assert rn.render(blind, "s").method_input == rn.render(sc, "s").method_input


def test_labels_do_not_reuse_node_ids():
    for r, sc in _pilot():
        for label, nid in r.alias_map.items():
            assert label != nid or len(nid) <= 2, (sc.scenario_id, label)


@pytest.mark.parametrize(
    "inject",
    ["Note: E3 is MUST_CHANGE.", "This is ambiguous.", "Pathology P9 applies.", "Template T7.9.",
     "The office wifi is unrelated.", "Expected coverage 0.2."],
)
def test_leakage_checker_catches_injections(inject):
    r, sc = next(x for x in _pilot() if x[1].scenario_id == "cat7_ambiguous_referent_001")
    bad = r.model_copy(deep=True)
    bad.method_input.change_text += " " + inject
    assert rn.check_leakage(bad, sc)


def test_leakage_checker_catches_raw_node_ids():
    r, sc = next(_pilot())
    bad = r.model_copy(deep=True)
    nid = next(n for n in sc.canonical_input.graph.node_ids() if len(n) > 2)
    bad.method_input.plan_text += f" ({nid})"
    assert any("node id" in p for p in rn.check_leakage(bad, sc))


def test_adapter_delivers_prose_only():
    for r, sc in _pilot():
        out = NaturalLanguageAdapter_v1().adapt(r, sc, run_id="t")
        assert out.structured is None and out.oracle_canonical is None
        assert set(out.natural_language.model_dump()) == {"plan_text", "change_text"}
        assert_no_forbidden_fields(out.natural_language.model_dump())
        assert out.metadata == {"operation": sc.operation.value, "regime": "R-N", "run_id": "t"}


def test_adapter_refuses_leaky_input():
    r, sc = next(_pilot())
    bad = r.model_copy(deep=True)
    bad.method_input.plan_text += " MUST_STAY_STABLE"
    with pytest.raises(LintError):
        NaturalLanguageAdapter_v1().adapt(bad, sc, run_id="t")


def test_ambiguity_survives_rendering():
    """P9: both suppliers keep the same name and the change names only that."""
    r = rn.load_rn("cat7_ambiguous_referent_001").method_input
    assert r.plan_text.count('name = "Supplier A"') == 2
    assert '"Supplier A"' in r.change_text and "feeds" not in r.change_text
    resolved = rn.load_rn("cat7_referent_resolved_001").method_input
    assert "feeds" in resolved.change_text


def test_all_63_scenarios_render_leak_free():
    """v0.2.0 fixed the one v0.1.0 leak (cat1_add_disconnected_001)."""
    for p in rn.canonical_files():
        sc = load_scenario(p)
        assert rn.check_leakage(rn.render(sc, "s"), sc) == [], sc.scenario_id


def test_no_api_key_material_in_repo_files():
    import re
    from pathlib import Path

    root = Path(rn.PKG).parent
    for p in list((root / "experiments").rglob("*")) + list(Path(rn.PKG).rglob("*.py")):
        if p.is_file() and p.suffix in {".py", ".json", ".txt", ".md"}:
            assert not re.search(r"(sk-[A-Za-z0-9_-]{20,}|AQ\.[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{20,})", p.read_text()), p


def test_frozen_config_matches_current_files():
    """Runner refuses without a frozen config; the frozen config's
    fingerprints must match the prompts, schemas and benchmark on disk."""
    import hashlib
    from pathlib import Path

    exp = Path(rn.PKG).parent / "experiments" / "rn_pilot"
    assert "No config.frozen.json" in (exp / "repeatability.py").read_text()
    cfg = json.loads((exp / "config.frozen.json").read_text())
    h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
    assert cfg["model_id"] == "nvidia/nemotron-3-ultra-550b-a55b"
    assert (cfg["temperature"], cfg["seed"], cfg["max_output_tokens"]) == (0, 20261008, 16384)
    assert cfg["benchmark_version"] == "0.2.0"
    assert cfg["benchmark_manifest_sha256"] == h(rn.MANIFEST)
    for name, digest in cfg["prompts"].items():
        assert h(exp / "prompts" / name) == digest, name
    for name, digest in cfg["schemas"].items():
        assert h(exp / name) == digest, name


def test_extraction_schema_is_operationally_sufficient_for_all_63_gold_inputs():
    """Typed extractor schema (v1.2) must carry every canonical structured input
    to B4b with identical results — no repair or interpretation layer."""
    from reflica_bench.adapters import AdapterOutput, StructuredAdapter_v1
    from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
    from reflica_bench.extraction_schema import ExtractionOutput

    for p in rn.canonical_files():
        sc = load_scenario(p)
        mi = StructuredAdapter_v1().adapt(sc, "g").structured
        mi2 = ExtractionOutput.model_validate(mi.model_dump(mode="json")).to_method_input()
        a = B4bWeightedCSP().revise(AdapterOutput(mi, None, {}))
        b = B4bWeightedCSP().revise(AdapterOutput(mi2, None, {}))
        assert (a.attribute_values, a.affected_set, a.determinability) == (
            b.attribute_values, b.affected_set, b.determinability), sc.scenario_id


def test_extraction_mirrors_match_downstream_models():
    from reflica_bench.extraction_schema import XEdge, XEdgeChange, XEvent, XGraph, XNode
    from reflica_bench.schema import Edge, EdgeChange, Event, Graph, Node

    for x, m in ((XNode, Node), (XEdge, Edge), (XGraph, Graph), (XEdgeChange, EdgeChange), (XEvent, Event)):
        assert set(x.model_fields) == set(m.model_fields), x.__name__


def _extraction(comp_extra: dict, ref_default="__omit__"):
    from reflica_bench.extraction_schema import ExtractionOutput

    ref = {"ref": "C.required"} if ref_default == "__omit__" else {"ref": "C.required", "default": ref_default}
    comp = {"node": "C", "attribute": "coverage", "human": "h",
            "machine": {"op": "div", "args": [{"src": "A.capacity", "default": 0}, ref]}, **comp_extra}
    return ExtractionOutput.model_validate({
        "graph": {"nodes": [{"id": "A", "attributes": {"capacity": 60, "note": None}},
                            {"id": "C", "attributes": {"required": 100}}],
                  "edges": [{"edge_id": "e1", "source": "A", "target": "C", "type": "supports"}]},
        "rules": {"satisfaction_functions": {"entries": {"computations": [comp], "status_functions": {
            "C": {"mapping": [{"label": "FULL", "when": {"op": "ge", "args": [{"ref": "C.coverage"}, 1]}},
                              {"label": "PARTIAL", "when": "otherwise"}], "human": None}}}}},
        "event": {"operation": "EDIT", "target_kind": "node", "target_id": "A",
                  "attribute": "capacity", "new_value": 40, "target_scope": None}})


def test_explicit_null_equals_omitted_downstream():
    a = _extraction({"when_linked": None, "role": None}, ref_default=None).to_method_input()
    b = _extraction({}).to_method_input()
    assert a == b
    comp = a.rules["satisfaction_functions"]["entries"]["computations"][0]
    assert "when_linked" not in comp and "role" not in comp and "default" not in comp["machine"]["args"][1]
    from reflica_bench.adapters import AdapterOutput
    from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP

    r = B4bWeightedCSP().revise(AdapterOutput(a, None, {}))
    assert r.attribute_values["C"]["coverage"] == 0.4


def test_null_normalisation_leaves_non_null_and_free_form_values_alone():
    mi = _extraction({"when_linked": ["A"], "role": "ratio"}, ref_default=1).to_method_input()
    comp = mi.rules["satisfaction_functions"]["entries"]["computations"][0]
    assert comp["when_linked"] == ["A"] and comp["role"] == "ratio"
    assert comp["machine"]["args"][1]["default"] == 1
    assert comp["machine"]["args"][0]["default"] == 0
    assert mi.graph.node("A").attributes == {"capacity": 60, "note": None}  # free-form null kept


def test_unknown_marker_in_fallback_equals_omitted_fallback():
    from reflica_bench.adapters import AdapterOutput
    from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP

    a = _extraction({}, ref_default={"$unknown": "undefined"}).to_method_input()
    b = _extraction({}).to_method_input()
    assert a == b
    ra, rb = (B4bWeightedCSP().revise(AdapterOutput(x, None, {})) for x in (a, b))
    assert (ra.attribute_values, ra.determinability, ra.pathology_flags) == (
        rb.attribute_values, rb.determinability, rb.pathology_flags)


def test_unknown_marker_rejected_outside_fallback_and_kept_in_attributes():
    import pytest
    from pydantic import ValidationError

    from reflica_bench.extraction_schema import ExtractionOutput

    good = _extraction({}).model_dump(mode="json", by_alias=True, exclude_unset=True)
    bad = json.loads(json.dumps(good))
    bad["rules"]["satisfaction_functions"]["entries"]["computations"][0]["machine"]["args"][1] = {"$unknown": "x"}
    with pytest.raises(ValidationError):
        ExtractionOutput.model_validate(bad)
    keep = json.loads(json.dumps(good))
    keep["graph"]["nodes"][0]["attributes"]["capacity"] = {"$unknown": "not stated"}
    mi = ExtractionOutput.model_validate(keep).to_method_input()
    assert mi.graph.node("A").attributes["capacity"] == {"$unknown": "not stated"}
