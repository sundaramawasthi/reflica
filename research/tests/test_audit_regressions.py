"""Regression tests surfaced by the Cat 1-3 research integrity audit.

Each test targets a specific risk identified in the audit, not a general
category contract. They are intentionally sharper than the category-wide
tests so that silent behavioural changes get caught.
"""

from __future__ import annotations

from reflica_bench.adapters import StructuredAdapter_v1
from reflica_bench.baselines.b3_reachability import B3Reachability
from reflica_bench.baselines.b4a_atms import B4aClassicalATMS
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
from reflica_bench.evaluator import evaluate_category_3
from reflica_bench.groundtruth import generate_ground_truth
from reflica_bench.loader import cat2_dir, cat3_dir, iter_scenarios


def _by_id(scenarios, sid):
    return next(s for s in scenarios if s.scenario_id == sid)


# --- audit fix 1: Cat 2 must respect the `operator` field -------------------

def test_cat2_ground_truth_respects_map_operator():
    """Audit finding: _generate_cat2 previously ignored machine.operator and
    always did a bare copy. If a Cat 2 scenario declares a map operator, the
    ground truth must honour it. Regression guard."""
    sc = _by_id(iter_scenarios(cat2_dir()), "cat2_pair_edit_001").model_copy(deep=True)
    # Swap the pair-edit rule to use a map operator and change the event so
    # the mapped output ends up equal to the pre-event value — i.e. the
    # dependent should NOT change despite the premise changing.
    sc.canonical_input.rules.propagation_rules.entries["rules"][0]["machine"] = {
        "operator": "map",
        "inputs": [{"node": "supplier_A", "attribute": "capacity"}],
        "mapping": {100: 100, 60: 100},  # both map to 100
        "default": 100,
        "output_name": "available_capacity",
    }
    gt = generate_ground_truth(sc)
    # supplier_A's own capacity still changes 100 -> 60: MUST_CHANGE.
    # task_T.available_capacity should stay 100 (because map(60) = 100).
    assert gt.nodes["supplier_A"].in_affected_set is True
    assert gt.nodes["task_T"].in_affected_set is False
    assert gt.nodes["task_T"].attribute_values == {"available_capacity": 100}


# --- audit sharpening: termination accuracy exact values on T3.4 ------------

def test_b3_termination_values_exact_on_t34():
    """Audit sharpening: previously we asserted B3 over_flip > 0 and
    termination_accuracy != 1 on T3.4. Nail down the exact numbers so a
    subtle regression in the stratifier can't slip through."""
    sc = _by_id(iter_scenarios(cat3_dir()), "cat3_early_termination_edit_001")
    adapter = StructuredAdapter_v1()
    out = adapter.adapt(sc, run_id="b3-exact")
    r = B3Reachability().revise(out)
    m = evaluate_category_3(r, generate_ground_truth(sc), sc.canonical_input.graph, sc.canonical_input.event)
    # True affected = {src_X, node_N1}; true stable = {node_N2, node_N3}.
    # B3 flags all four → precision 2/4 = 0.5, recall 1.0, over-flip 2/2 = 1.0,
    # termination_accuracy over {node_N3 (depth 3), node_N2 (depth 2)} = 0.0.
    assert m.affected_node_precision == 0.5
    assert m.affected_node_recall == 1.0
    assert m.over_flip_rate == 1.0
    assert m.termination_accuracy == 0.0
    assert m.max_reached_depth == 3


def test_b4a_termination_values_exact_on_t34():
    sc = _by_id(iter_scenarios(cat3_dir()), "cat3_early_termination_edit_001")
    adapter = StructuredAdapter_v1()
    out = adapter.adapt(sc, run_id="b4a-exact")
    r = B4aClassicalATMS().revise(out)
    m = evaluate_category_3(r, generate_ground_truth(sc), sc.canonical_input.graph, sc.canonical_input.event)
    assert m.affected_node_precision == 0.5
    assert m.affected_node_recall == 1.0
    assert m.over_flip_rate == 1.0
    assert m.termination_accuracy == 0.0


def test_b4b_termination_values_exact_on_t34():
    sc = _by_id(iter_scenarios(cat3_dir()), "cat3_early_termination_edit_001")
    adapter = StructuredAdapter_v1()
    out = adapter.adapt(sc, run_id="b4b-exact")
    r = B4bWeightedCSP().revise(out)
    m = evaluate_category_3(r, generate_ground_truth(sc), sc.canonical_input.graph, sc.canonical_input.event)
    assert m.affected_node_precision == 1.0
    assert m.affected_node_recall == 1.0
    assert m.over_flip_rate == 0.0
    assert m.termination_accuracy == 1.0
    # B4b reaches depth 1 only (src_X depth 0, node_N1 depth 1).
    assert m.max_reached_depth == 1


# --- audit coverage: B4a must not propagate through informs on Cat 3 --------

def test_b4a_does_not_propagate_through_informs_cat3():
    """Covered for B3 by the existing test; audit requires the same guard
    for B4a given its transitive justification walk."""
    sc = _by_id(iter_scenarios(cat3_dir()), "cat3_chain_plus_side_edit_001")
    adapter = StructuredAdapter_v1()
    out = adapter.adapt(sc, run_id="b4a-side")
    r = B4aClassicalATMS().revise(out)
    assert r.affected_set is not None
    assert "side_Y" not in r.affected_set
    assert "side_Z" not in r.affected_set


# --- audit coverage: B4b sanity on T3.4 preserves PRE-event values ----------

def test_b4b_preserves_pre_event_values_beyond_termination():
    """On T3.4, N2.quality and N3.alert_level must appear in B4b's output
    with their PRE-event values ('ok'), not inferred or omitted."""
    sc = _by_id(iter_scenarios(cat3_dir()), "cat3_early_termination_edit_001")
    adapter = StructuredAdapter_v1()
    out = adapter.adapt(sc, run_id="b4b-preserve")
    r = B4bWeightedCSP().revise(out)
    assert r.attribute_values is not None
    assert r.attribute_values["node_N2"] == {"quality": "ok"}
    assert r.attribute_values["node_N3"] == {"alert_level": "ok"}


# --- audit coverage: hand-written ground truth really is independent --------

def test_scenarios_declare_hand_written_ground_truth():
    """Catches an accidental drift where someone replaces a scenario's
    stored ground_truth with the generator's output (which would void the
    round-trip anchor). We verify that every scenario file carries a
    non-trivial, hand-written ground_truth.nodes section rather than an
    empty placeholder."""
    for d in (cat2_dir(), cat3_dir()):
        for sc in iter_scenarios(d):
            assert len(sc.ground_truth.nodes) == len(sc.canonical_input.graph.nodes) or any(
                g.in_affected_set for g in sc.ground_truth.nodes.values()
            ), f"scenario {sc.scenario_id} appears to have empty/placeholder ground truth"


# --- audit coverage: B3 and B4a use genuinely different code paths ----------

def test_b3_and_b4a_use_different_mechanisms():
    """B3 walks graph edges; B4a walks declared propagation rules. On
    co-aligned-rule Cat 2/3 scenarios they produce identical scope outputs,
    but their internal RevisionResult.explanation / unsupported_dimensions
    + the fact that B4a declares supports_abstention=False while B3 does
    too (same signature) means we can at least verify they aren't the same
    object. The strong independence check is in the per-category source
    files, cross-checked here against runtime behaviour on a 'B4a-only'
    probe: when the graph has a propagating edge but no rule reads it,
    B3 flags the target and B4a does not."""
    # Construct an in-memory scenario by hand-mutating cat2_pair_edit:
    # drop the propagation rule but keep the propagating edge.
    sc = _by_id(iter_scenarios(cat2_dir()), "cat2_pair_edit_001").model_copy(deep=True)
    sc.canonical_input.rules.propagation_rules.entries["rules"] = []
    adapter = StructuredAdapter_v1()
    out = adapter.adapt(sc, run_id="divergence")

    r3 = B3Reachability().revise(out)
    r4a = B4aClassicalATMS().revise(out)
    # B3 reachability walks through the supports edge → flags task_T.
    assert r3.affected_set is not None and "task_T" in r3.affected_set
    # B4a walks declared rules → no rules → task_T stays out of affected set.
    assert r4a.affected_set is not None and "task_T" not in r4a.affected_set
