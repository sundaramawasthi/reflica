"""Schema linter + sanitiser tests."""

from __future__ import annotations

import pytest

from reflica_bench.linter import (
    LintError,
    assert_no_forbidden_fields,
    lint_scenario,
    method_metadata,
    sanitise_rules_for_method,
)
from reflica_bench.loader import cat1_dir, iter_scenarios


def test_all_cat1_scenarios_lint_clean():
    scenarios = iter_scenarios(cat1_dir())
    assert len(scenarios) >= 4, "expected at least 4 Category 1 floor scenarios"
    for s in scenarios:
        lint_scenario(s)


def test_sanitiser_strips_declared_input_flag():
    rules = {
        "read_attributes": {"declared_input": True, "entries": {"a": ["x"]}},
        "hidden_block": {"declared_input": False, "entries": {"secret": True}},
    }
    out = sanitise_rules_for_method(rules)
    assert "hidden_block" not in out
    assert "read_attributes" in out
    assert "declared_input" not in out["read_attributes"]
    assert out["read_attributes"]["entries"] == {"a": ["x"]}


def test_assert_no_forbidden_fields_catches_leaks():
    with pytest.raises(LintError):
        assert_no_forbidden_fields({"ok": 1, "category": 5})
    with pytest.raises(LintError):
        assert_no_forbidden_fields({"nested": {"ground_truth": {}}})
    # Clean payload passes.
    assert_no_forbidden_fields({"graph": {}, "rules": {}, "event": {}})


def test_method_metadata_exposes_only_safe_fields():
    scenarios = iter_scenarios(cat1_dir())
    md = method_metadata(scenarios[0], run_id="r-123")
    assert set(md.keys()) == {"operation", "regime", "run_id"}


def test_duplicate_edge_id_fails_lint():
    from reflica_bench.loader import load_scenario
    from reflica_bench.schema import Edge, EdgeType
    s = iter_scenarios(cat1_dir())[0].model_copy(deep=True)
    s.canonical_input.graph.edges.append(
        Edge(edge_id="E1", source=s.canonical_input.graph.nodes[0].id,
             target=s.canonical_input.graph.nodes[0].id, type=EdgeType.INFORMS)
    )
    s.canonical_input.graph.edges.append(
        Edge(edge_id="E1", source=s.canonical_input.graph.nodes[0].id,
             target=s.canonical_input.graph.nodes[0].id, type=EdgeType.INFORMS)
    )
    with pytest.raises(LintError, match="duplicate edge_id"):
        lint_scenario(s)
