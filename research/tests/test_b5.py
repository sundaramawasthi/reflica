"""B5 (Reflica) offline validation. Gold outputs are used ONLY as test
oracles here; B5 itself never sees them (see independence test)."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from reflica_bench import rn
from reflica_bench.adapters import AdapterOutput, StructuredAdapter_v1
from reflica_bench.b5.reflica import B5Reflica
from reflica_bench.loader import load_scenario
from reflica_bench.schema import MethodInputStructured

B5_DIR = Path(rn.PKG) / "b5"
FORBIDDEN = {"gt_engine", "groundtruth", "groundtruth_quant", "evaluator", "b4b_cpsat",
             "b4b_weighted_csp", "b4a_atms", "b3_reachability", "linter", "loader", "rn"}


def _run(sid):
    sc = load_scenario(rn.source_path(sid))
    return sc, B5Reflica().revise(StructuredAdapter_v1().adapt(sc, "t"))


def _close(a, b):
    num = (int, float)
    if isinstance(a, num) and isinstance(b, num) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) < 1e-6
    return a == b


# --- independence -------------------------------------------------------------

def test_b5_never_imports_ground_truth_or_other_baselines():
    for f in B5_DIR.glob("*.py"):
        for node in ast.walk(ast.parse(f.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""] + [a.name for a in node.names]
            for n in names:
                assert not (set(n.split(".")) & FORBIDDEN), (f.name, n)


def test_b5_input_contains_no_ground_truth():
    sc = load_scenario(rn.source_path("cat7_ambiguous_referent_001"))
    blob = json.dumps(StructuredAdapter_v1().adapt(sc, "t").structured.model_dump(mode="json"))
    assert "ground_truth" not in blob and "MUST_CHANGE" not in blob and "AMBIGUOUS" not in blob


# --- gold agreement on all 63 (oracle use only) -------------------------------

@pytest.mark.parametrize("path", rn.canonical_files(), ids=lambda p: p.stem)
def test_b5_agrees_with_gold(path):
    sc = load_scenario(path)
    r = B5Reflica().revise(StructuredAdapter_v1().adapt(sc, "t"))
    for n, g in sc.ground_truth.nodes.items():
        assert r.determinability[n] == g.determinability.value, n
        if g.determinability.value == "DETERMINABLE":
            assert r.outcome_labels[n] == g.outcome_label, n
            for k, v in g.attribute_values.items():
                assert _close(r.attribute_values[n].get(k), v), (n, k)
        else:
            assert sorted(r.pathology_flags[n]) == sorted(g.pathology_codes), n


# --- behaviour ----------------------------------------------------------------

def test_irrelevant_change_touches_nothing_else():
    sc, r = _run("cat1_edit_attribute_irrelevance_001")
    assert len(r.affected_set) == 1


def test_trace_records_scope_and_verification():
    _, r = _run("cat5_two_hop_propagation_001")
    tr = r.explanation["completions"][0]
    assert "plant_B.throughput" in tr["affected"] and "demand_C.coverage" in tr["affected"]
    assert tr["verified"] is True and tr["violations_outside_scope"] == []


def test_partial_status_not_binarised():
    _, r = _run("cat5_threshold_partial_partial_001")
    assert r.attribute_values["demand_C"]["status"] == "PARTIAL"


def test_conflict_without_rule_abstains():
    _, r = _run("cat7_conflicting_evidence_edit_001")
    assert r.determinability["demand_C"] == "AMBIGUOUS" and "P2" in r.pathology_flags["demand_C"]
    assert r.attribute_values["supplier_A"]["capacity"] is None


def test_valid_preference_rule_is_applied():
    _, r = _run("cat7_conflict_with_resolution_001")
    assert r.attribute_values["demand_C"]["status"] == "FULL"


def test_invented_preference_source_is_rejected_not_applied():
    sc = load_scenario(rn.source_path("cat7_conflict_with_resolution_001"))
    d = StructuredAdapter_v1().adapt(sc, "t").structured.model_dump(mode="json")
    d["rules"]["evidence"]["entries"]["resolution"]["supplier_A.capacity"]["source"] = "plan"
    r = B5Reflica().revise(AdapterOutput(MethodInputStructured.model_validate(d), None, {}))
    assert r.determinability["demand_C"] == "AMBIGUOUS"
    assert any("rejected preference" in n for n in r.explanation["completions"][0]["notes"])


def test_unknown_attribute_marker_abstains():
    sc = load_scenario(rn.source_path("cat5_capacity_edit_001"))
    d = StructuredAdapter_v1().adapt(sc, "t").structured.model_dump(mode="json")
    d["event"]["new_value"] = {"$unknown": "not stated"}
    r = B5Reflica().revise(AdapterOutput(MethodInputStructured.model_validate(d), None, {}))
    assert r.determinability["demand_C"] == "AMBIGUOUS" and "P1" in r.pathology_flags["demand_C"]


def test_inconsistent_state_outside_scope_is_reported_not_repaired():
    """Adversarial: corrupt a stored value the update cannot reach."""
    sc = load_scenario(rn.source_path("cat6a_shared_contributor_001"))
    d = StructuredAdapter_v1().adapt(sc, "t").structured.model_dump(mode="json")
    d["event"].update(target_id="S2", attribute="name", new_value="S2b")
    for n in d["graph"]["nodes"]:
        if n["id"] == "demand_C2":
            n["attributes"]["coverage"] = 9.9
    r = B5Reflica().revise(AdapterOutput(MethodInputStructured.model_validate(d), None, {}))
    tr = r.explanation["completions"][0]
    assert "demand_C2.coverage" in tr["violations_outside_scope"]
    assert r.attribute_values["demand_C2"]["coverage"] == 9.9


def test_boundary_coverage_exactly_one_is_full():
    sc = load_scenario(rn.source_path("cat5_capacity_edit_001"))
    d = StructuredAdapter_v1().adapt(sc, "t").structured.model_dump(mode="json")
    d["event"]["new_value"] = 80  # required = 80
    r = B5Reflica().revise(AdapterOutput(MethodInputStructured.model_validate(d), None, {}))
    assert r.attribute_values["demand_C"]["coverage"] == 1 and r.attribute_values["demand_C"]["status"] == "FULL"


def test_regression_pilot_t72_invented_rule_extraction():
    raw = Path(rn.PKG).parent / "experiments" / "rn_pilot" / "pilot_raw.jsonl"
    rec = next(json.loads(x) for x in raw.read_text().splitlines()
               if '"cat7_conflicting_evidence_edit_001", "call": "EXTRACT", "repeat": 1' in x)
    from reflica_bench.extraction_schema import ExtractionOutput

    r = B5Reflica().revise(AdapterOutput(ExtractionOutput.model_validate_json(rec["content"]).to_method_input(), None, {}))
    assert r.determinability["Supplier A"] == "AMBIGUOUS" and "P2" in r.pathology_flags["Supplier A"]
