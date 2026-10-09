"""Evaluator: compare a baseline's RevisionResult against ground truth.

Category 1 metrics (floor):
    - over_flip_rate            (primary)
    - unnecessary_revision_rate (primary)
    - affected_node_precision   (primary; recall is trivially 1.0 for Cat 1)
    - final_state_accuracy      (secondary — must be 100% for a correct method)
    - token_cost                (universal)
    - wall_time_ms              (universal)

Category 2 adds:
    - inertia_rate              (primary)
    - attribute_value_accuracy  (primary; N/A for baselines that don't
                                 compute attribute values)

Category 3 adds:
    - termination_accuracy      (primary; fraction of ground-truth MUST_STAY_
                                 STABLE nodes beyond a chain's termination
                                 that the method also marked stable — this
                                 is the signal where B3 and B4a lose by
                                 over-propagating past the point where rule
                                 output stops changing)
    - depth_stratified_precision_recall  (primary; precision/recall of the
                                 affected set per depth-from-event-target.
                                 Returned as a dict keyed by integer depth.)
    - max_reached_depth         (secondary diagnostic)

Unsupported dimensions (RevisionResult.* is None) are reported as N/A,
never as zero.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from .baseline import RevisionResult
from .schema import (
    PROPAGATING_EDGE_TYPES,
    Event,
    Graph,
    GroundTruth,
    Operation,
    OutcomeLabel,
    TargetKind,
)


# A sentinel for metrics the baseline does not support on this scenario.
NA = "N/A"


@dataclass
class Category1Metrics:
    over_flip_rate: float | str
    unnecessary_revision_rate: float | str
    affected_node_precision: float | str
    affected_node_recall: float | str
    final_state_accuracy: float | str
    token_cost: int
    wall_time_ms: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "over_flip_rate": self.over_flip_rate,
            "unnecessary_revision_rate": self.unnecessary_revision_rate,
            "affected_node_precision": self.affected_node_precision,
            "affected_node_recall": self.affected_node_recall,
            "final_state_accuracy": self.final_state_accuracy,
            "token_cost": self.token_cost,
            "wall_time_ms": self.wall_time_ms,
        }


@dataclass
class Category4Metrics:
    """Alternative-Justification Preservation metrics.

    Primary:
      - false_invalidation_rate: fraction of conclusions with surviving
        justification that the method marked as changed (lower is better).
      - discrimination_accuracy: binary accuracy classifying each conclusion
        as MUST_STAY_STABLE vs MUST_CHANGE.
      - preservation_precision: of conclusions the method marked stable,
        fraction truly stable.
    """

    false_invalidation_rate: float | str
    discrimination_accuracy: float | str
    preservation_precision: float | str
    over_flip_rate: float | str
    affected_node_precision: float | str
    affected_node_recall: float | str
    final_state_accuracy: float | str
    token_cost: int = 0
    wall_time_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "false_invalidation_rate": self.false_invalidation_rate,
            "discrimination_accuracy": self.discrimination_accuracy,
            "preservation_precision": self.preservation_precision,
            "over_flip_rate": self.over_flip_rate,
            "affected_node_precision": self.affected_node_precision,
            "affected_node_recall": self.affected_node_recall,
            "final_state_accuracy": self.final_state_accuracy,
            "token_cost": self.token_cost,
            "wall_time_ms": self.wall_time_ms,
        }


@dataclass
class Category3Metrics:
    over_flip_rate: float | str
    inertia_rate: float | str
    unnecessary_revision_rate: float | str
    affected_node_precision: float | str
    affected_node_recall: float | str
    final_state_accuracy: float | str
    attribute_value_accuracy: float | str
    termination_accuracy: float | str
    depth_stratified: dict[int, dict[str, float | str]] = field(default_factory=dict)
    max_reached_depth: int | str = "N/A"
    token_cost: int = 0
    wall_time_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "over_flip_rate": self.over_flip_rate,
            "inertia_rate": self.inertia_rate,
            "unnecessary_revision_rate": self.unnecessary_revision_rate,
            "affected_node_precision": self.affected_node_precision,
            "affected_node_recall": self.affected_node_recall,
            "final_state_accuracy": self.final_state_accuracy,
            "attribute_value_accuracy": self.attribute_value_accuracy,
            "termination_accuracy": self.termination_accuracy,
            "depth_stratified": self.depth_stratified,
            "max_reached_depth": self.max_reached_depth,
            "token_cost": self.token_cost,
            "wall_time_ms": self.wall_time_ms,
        }


@dataclass
class Category2Metrics:
    over_flip_rate: float | str
    inertia_rate: float | str
    unnecessary_revision_rate: float | str
    affected_node_precision: float | str
    affected_node_recall: float | str
    final_state_accuracy: float | str
    attribute_value_accuracy: float | str
    token_cost: int
    wall_time_ms: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "over_flip_rate": self.over_flip_rate,
            "inertia_rate": self.inertia_rate,
            "unnecessary_revision_rate": self.unnecessary_revision_rate,
            "affected_node_precision": self.affected_node_precision,
            "affected_node_recall": self.affected_node_recall,
            "final_state_accuracy": self.final_state_accuracy,
            "attribute_value_accuracy": self.attribute_value_accuracy,
            "token_cost": self.token_cost,
            "wall_time_ms": self.wall_time_ms,
        }


def evaluate_category_1(
    result: RevisionResult, ground_truth: GroundTruth
) -> Category1Metrics:
    """Compute Cat 1 metrics from a baseline result against ground truth.

    Only consumes the DETERMINABLE subset — in Cat 1 all nodes are
    DETERMINABLE, so this is the full ground_truth.nodes map.
    """

    true_affected: set[str] = {
        nid for nid, g in ground_truth.nodes.items() if g.in_affected_set
    }
    true_stable: set[str] = {
        nid for nid, g in ground_truth.nodes.items() if not g.in_affected_set
    }

    # ---- scope metrics ---------------------------------------------------
    if result.affected_set is None:
        affected_prec: float | str = NA
        affected_rec: float | str = NA
        unnecessary: float | str = NA
    else:
        predicted = set(result.affected_set)
        if predicted:
            affected_prec = len(predicted & true_affected) / len(predicted)
        else:
            # Supported-but-empty prediction: perfect precision iff true set empty.
            affected_prec = 1.0 if not true_affected else 0.0
        if true_affected:
            affected_rec = len(predicted & true_affected) / len(true_affected)
        else:
            affected_rec = 1.0 if not predicted else 0.0

        # unnecessary revisions: nodes flagged as affected that shouldn't be.
        if true_stable:
            unnecessary = len(predicted & true_stable) / len(true_stable)
        else:
            unnecessary = 0.0

    # ---- state over-flip (did the method change the state/attributes of a stable node?) --
    if result.outcome_labels is None and result.attribute_values is None:
        over_flip: float | str = NA
    else:
        over_flipped = 0
        considered = 0
        for nid in true_stable:
            considered += 1
            # outcome_label-based flip
            if result.outcome_labels is not None:
                lbl = result.outcome_labels.get(nid)
                if lbl is not None and lbl != OutcomeLabel.MUST_STAY_STABLE:
                    over_flipped += 1
                    continue
            # attribute-based flip (compared to ground-truth stable attribute values)
            if result.attribute_values is not None:
                predicted_attrs = result.attribute_values.get(nid)
                truth_attrs = ground_truth.nodes[nid].attribute_values
                if predicted_attrs is not None and predicted_attrs != truth_attrs:
                    over_flipped += 1
        over_flip = (over_flipped / considered) if considered else 0.0

    # ---- final-state accuracy -------------------------------------------
    if result.outcome_labels is None:
        final_state: float | str = NA
    else:
        correct = 0
        total = 0
        for nid, g in ground_truth.nodes.items():
            total += 1
            if result.outcome_labels.get(nid) == g.outcome_label:
                correct += 1
        final_state = correct / total if total else 0.0

    return Category1Metrics(
        over_flip_rate=over_flip,
        unnecessary_revision_rate=unnecessary,
        affected_node_precision=affected_prec,
        affected_node_recall=affected_rec,
        final_state_accuracy=final_state,
        token_cost=result.token_cost,
        wall_time_ms=result.wall_time_ms,
    )


def evaluate_category_2(
    result: RevisionResult, ground_truth: GroundTruth
) -> Category2Metrics:
    """Compute Cat 2 metrics from a baseline result against ground truth.

    Reuses Cat 1 primitives for scope/over-flip/final-state and adds:

    * inertia_rate: fraction of MUST_CHANGE nodes the method failed to mark
      as changed (via outcome_labels). N/A if outcome_labels is None.
    * attribute_value_accuracy: fraction of (MUST_CHANGE node, attribute)
      pairs where the baseline's reported attribute value matches ground
      truth exactly. N/A if attribute_values is None (baseline unsupported).
    """
    true_affected: set[str] = {
        nid for nid, g in ground_truth.nodes.items() if g.in_affected_set
    }
    true_stable: set[str] = {
        nid for nid, g in ground_truth.nodes.items() if not g.in_affected_set
    }

    # ---- scope precision / recall / unnecessary ----
    if result.affected_set is None:
        affected_prec: float | str = NA
        affected_rec: float | str = NA
        unnecessary: float | str = NA
    else:
        predicted = set(result.affected_set)
        if predicted:
            affected_prec = len(predicted & true_affected) / len(predicted)
        else:
            affected_prec = 1.0 if not true_affected else 0.0
        if true_affected:
            affected_rec = len(predicted & true_affected) / len(true_affected)
        else:
            affected_rec = 1.0 if not predicted else 0.0
        if true_stable:
            unnecessary = len(predicted & true_stable) / len(true_stable)
        else:
            unnecessary = 0.0

    # ---- over-flip (changed something that should have stayed) ----
    if result.outcome_labels is None and result.attribute_values is None:
        over_flip: float | str = NA
    else:
        over_flipped = 0
        considered = 0
        for nid in true_stable:
            considered += 1
            if result.outcome_labels is not None:
                lbl = result.outcome_labels.get(nid)
                if lbl is not None and lbl != OutcomeLabel.MUST_STAY_STABLE:
                    over_flipped += 1
                    continue
            if result.attribute_values is not None:
                predicted_attrs = result.attribute_values.get(nid)
                truth_attrs = ground_truth.nodes[nid].attribute_values
                if predicted_attrs is not None and predicted_attrs != truth_attrs:
                    over_flipped += 1
        over_flip = (over_flipped / considered) if considered else 0.0

    # ---- inertia (missed a required change) ----
    if result.outcome_labels is None:
        inertia: float | str = NA
    else:
        missed = 0
        considered = 0
        for nid in true_affected:
            considered += 1
            lbl = result.outcome_labels.get(nid)
            if lbl is None or lbl != OutcomeLabel.MUST_CHANGE:
                missed += 1
        inertia = (missed / considered) if considered else 0.0

    # ---- final-state accuracy ----
    if result.outcome_labels is None:
        final_state: float | str = NA
    else:
        correct = 0
        total = 0
        for nid, g in ground_truth.nodes.items():
            total += 1
            if result.outcome_labels.get(nid) == g.outcome_label:
                correct += 1
        final_state = correct / total if total else 0.0

    # ---- attribute-value accuracy (exact match per MUST_CHANGE node attr) ----
    if result.attribute_values is None:
        attr_acc: float | str = NA
    else:
        hits = 0
        tested = 0
        for nid in true_affected:
            truth_attrs = ground_truth.nodes[nid].attribute_values
            pred_attrs = result.attribute_values.get(nid)
            if pred_attrs is None:
                # supported-dim but no prediction for this node: all its
                # attributes count against accuracy.
                tested += len(truth_attrs)
                continue
            for attr, truth_v in truth_attrs.items():
                tested += 1
                if pred_attrs.get(attr) == truth_v:
                    hits += 1
        attr_acc = (hits / tested) if tested else 1.0

    return Category2Metrics(
        over_flip_rate=over_flip,
        inertia_rate=inertia,
        unnecessary_revision_rate=unnecessary,
        affected_node_precision=affected_prec,
        affected_node_recall=affected_rec,
        final_state_accuracy=final_state,
        attribute_value_accuracy=attr_acc,
        token_cost=result.token_cost,
        wall_time_ms=result.wall_time_ms,
    )


def _event_seed_nodes(ev: Event, graph: Graph) -> set[str]:
    """Return the set of node ids that act as the depth-0 seed for the
    event — used by depth-stratified metrics to compute hop distance."""
    seeds: set[str] = set()
    if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
        if ev.new_node is not None:
            seeds.add(ev.new_node.id)
    elif ev.operation == Operation.EDIT and ev.target_id is not None:
        seeds.add(ev.target_id)
    elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE and ev.target_id is not None:
        seeds.add(ev.target_id)
    elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.EDGE and ev.target_id is not None:
        edge = graph.edge(ev.target_id)
        if edge is not None:
            seeds.add(edge.source)
            seeds.add(edge.target)
    elif ev.operation == Operation.ADD and ev.target_kind == TargetKind.EDGE and ev.edge_change is not None:
        if ev.edge_change.source is not None:
            seeds.add(ev.edge_change.source)
        if ev.edge_change.target is not None:
            seeds.add(ev.edge_change.target)
    elif ev.operation == Operation.RELATIONSHIP_CHANGE and ev.edge_change is not None and ev.edge_change.edge_id is not None:
        edge = graph.edge(ev.edge_change.edge_id)
        if edge is not None:
            seeds.add(edge.source)
            seeds.add(edge.target)
    return seeds


def _node_depths_via_propagating_edges(graph: Graph, seeds: set[str]) -> dict[str, int]:
    """BFS from seeds through propagating edges; return hop depth per
    reachable node. Nodes not reachable are absent from the dict."""
    depth: dict[str, int] = {s: 0 for s in seeds if s in graph.node_ids() or s}
    # Include seeds even if not currently in graph (ADD edge target may exist pre-event).
    frontier: deque[str] = deque(seeds)
    adj: dict[str, list[str]] = {}
    for e in graph.edges:
        if e.type in PROPAGATING_EDGE_TYPES:
            adj.setdefault(e.source, []).append(e.target)
    while frontier:
        n = frontier.popleft()
        d = depth[n]
        for nxt in adj.get(n, ()):
            if nxt not in depth:
                depth[nxt] = d + 1
                frontier.append(nxt)
    return depth


def evaluate_category_3(
    result: RevisionResult, ground_truth: GroundTruth, graph: Graph, event: Event
) -> Category3Metrics:
    """Compute Cat 3 metrics by extending the Cat 2 primitives with
    depth-stratified scope accuracy and termination accuracy.

    The `graph` and `event` arguments carry pre-event structure needed to
    compute each node's hop distance from the event seed; without them the
    depth-stratified breakdown would require knowledge the evaluator
    otherwise doesn't need.
    """
    cat2 = evaluate_category_2(result, ground_truth)

    seeds = _event_seed_nodes(event, graph)
    depths = _node_depths_via_propagating_edges(graph, seeds)

    # Split ground-truth sets by depth.
    true_affected = {nid for nid, g in ground_truth.nodes.items() if g.in_affected_set}
    true_stable = {nid for nid, g in ground_truth.nodes.items() if not g.in_affected_set}

    predicted: set[str] = set(result.affected_set) if result.affected_set is not None else set()

    stratified: dict[int, dict[str, float | str]] = {}
    all_depths = sorted(set(depths.values()))
    for d in all_depths:
        ta = {n for n in true_affected if depths.get(n) == d}
        ts = {n for n in true_stable if depths.get(n) == d}
        pred_d = {n for n, dn in depths.items() if dn == d and n in predicted}
        prec = (
            len(pred_d & ta) / len(pred_d) if pred_d else (1.0 if not ta else 0.0)
        )
        rec = len(pred_d & ta) / len(ta) if ta else (1.0 if not pred_d else 0.0)
        # over-flip at this depth: predicted-stable fraction.
        over = len(pred_d & ts) / len(ts) if ts else 0.0
        stratified[d] = {
            "precision": prec,
            "recall": rec,
            "over_flip": over,
            "true_affected": len(ta),
            "true_stable": len(ts),
        }

    # Termination accuracy = fraction of MUST_STAY_STABLE nodes beyond
    # termination (i.e. at a depth where the chain ground-truth-terminates)
    # that the baseline correctly left stable. A method that keeps
    # propagating past the termination point will score low here.
    beyond_termination = _nodes_beyond_termination(ground_truth, depths, true_affected)
    if result.outcome_labels is None and result.affected_set is None:
        term_acc: float | str = NA
    elif not beyond_termination:
        term_acc = 1.0
    else:
        correct = 0
        for nid in beyond_termination:
            lbl = result.outcome_labels.get(nid) if result.outcome_labels else None
            in_pred_affected = nid in predicted
            if (
                (lbl is None or lbl == OutcomeLabel.MUST_STAY_STABLE)
                and not in_pred_affected
            ):
                correct += 1
        term_acc = correct / len(beyond_termination)

    max_reached: int | str
    if result.affected_set is None:
        max_reached = "N/A"
    else:
        depths_in_pred = [depths[n] for n in predicted if n in depths]
        max_reached = max(depths_in_pred) if depths_in_pred else 0

    return Category3Metrics(
        over_flip_rate=cat2.over_flip_rate,
        inertia_rate=cat2.inertia_rate,
        unnecessary_revision_rate=cat2.unnecessary_revision_rate,
        affected_node_precision=cat2.affected_node_precision,
        affected_node_recall=cat2.affected_node_recall,
        final_state_accuracy=cat2.final_state_accuracy,
        attribute_value_accuracy=cat2.attribute_value_accuracy,
        termination_accuracy=term_acc,
        depth_stratified=stratified,
        max_reached_depth=max_reached,
        token_cost=result.token_cost,
        wall_time_ms=result.wall_time_ms,
    )


def evaluate_category_4(
    result: RevisionResult,
    ground_truth: GroundTruth,
    conclusion_ids: set[str],
) -> Category4Metrics:
    """Compute Cat 4 metrics.

    `conclusion_ids` are the node ids declared as conclusions in
    rules.justifications.entries.conclusions — the only nodes against which
    the Cat 4 metrics operate. Non-conclusion nodes still contribute to
    over-flip / scope metrics but not to discrimination.
    """
    # Build the per-conclusion ground-truth outcome.
    conclusion_truth: dict[str, bool] = {}
    for cid in conclusion_ids:
        gt_node = ground_truth.nodes.get(cid)
        if gt_node is None:
            continue
        conclusion_truth[cid] = gt_node.outcome_label == OutcomeLabel.MUST_CHANGE

    # ---- false_invalidation_rate ----
    if result.outcome_labels is None and result.affected_set is None:
        false_inv: float | str = NA
    else:
        preservation_cases = {cid for cid, c in conclusion_truth.items() if not c}
        if not preservation_cases:
            false_inv = NA
        else:
            flagged = 0
            for cid in preservation_cases:
                marked_changed = False
                if result.outcome_labels is not None:
                    lbl = result.outcome_labels.get(cid)
                    if lbl == OutcomeLabel.MUST_CHANGE:
                        marked_changed = True
                if (
                    not marked_changed
                    and result.affected_set is not None
                    and cid in result.affected_set
                ):
                    marked_changed = True
                if marked_changed:
                    flagged += 1
            false_inv = flagged / len(preservation_cases)

    # ---- discrimination_accuracy ----
    if result.outcome_labels is None and result.affected_set is None:
        disc_acc: float | str = NA
    elif not conclusion_truth:
        disc_acc = NA
    else:
        correct = 0
        for cid, truly_changed in conclusion_truth.items():
            marked_changed = False
            if result.outcome_labels is not None:
                lbl = result.outcome_labels.get(cid)
                if lbl == OutcomeLabel.MUST_CHANGE:
                    marked_changed = True
            if (
                not marked_changed
                and result.affected_set is not None
                and cid in result.affected_set
            ):
                marked_changed = True
            if marked_changed == truly_changed:
                correct += 1
        disc_acc = correct / len(conclusion_truth)

    # ---- preservation_precision ----
    if result.outcome_labels is None and result.affected_set is None:
        pres_prec: float | str = NA
    else:
        marked_stable: set[str] = set()
        for cid in conclusion_truth:
            marked_changed = False
            if result.outcome_labels is not None:
                lbl = result.outcome_labels.get(cid)
                if lbl == OutcomeLabel.MUST_CHANGE:
                    marked_changed = True
            if (
                not marked_changed
                and result.affected_set is not None
                and cid in result.affected_set
            ):
                marked_changed = True
            if not marked_changed:
                marked_stable.add(cid)
        if not marked_stable:
            pres_prec = NA
        else:
            truly_stable = {cid for cid in marked_stable if not conclusion_truth[cid]}
            pres_prec = len(truly_stable) / len(marked_stable)

    # Scope / over-flip reuse Cat 1 primitives on the full node set.
    cat1 = evaluate_category_1(result, ground_truth)

    return Category4Metrics(
        false_invalidation_rate=false_inv,
        discrimination_accuracy=disc_acc,
        preservation_precision=pres_prec,
        over_flip_rate=cat1.over_flip_rate,
        affected_node_precision=cat1.affected_node_precision,
        affected_node_recall=cat1.affected_node_recall,
        final_state_accuracy=cat1.final_state_accuracy,
        token_cost=result.token_cost,
        wall_time_ms=result.wall_time_ms,
    )


def _nodes_beyond_termination(
    ground_truth: GroundTruth, depths: dict[str, int], true_affected: set[str]
) -> set[str]:
    """Identify MUST_STAY_STABLE nodes that sit beyond a chain's termination
    point — i.e. stable nodes whose depth is ≥ the maximum depth of any
    truly-affected node on their lineage. For simplicity we use the global
    maximum affected depth as a proxy, which captures the T3.4 early-
    termination test case cleanly."""
    if not true_affected:
        return set()
    max_affected_depth = max((depths.get(n, 0) for n in true_affected), default=0)
    return {
        n
        for n, g in ground_truth.nodes.items()
        if not g.in_affected_set
        and n in depths
        and depths[n] > max_affected_depth
    }


# ===========================================================================
# Categories 5, 6-A, 6-B, 7
# ===========================================================================
#
# Attribute-value accuracy is reported PER ATTRIBUTE TYPE, never collapsed:
#   discrete                       exact-match accuracy
#   continuous_bounded             MAE + within-ε accuracy (ε = 0.05 default)
#   continuous_unbounded_positive  MAPE (zero ground truth excluded and
#                                  counted) + within ±10% accuracy
#   signed_continuous              MAE + sign-match accuracy
# tolerance_bands in evaluation_annotations override the defaults per attribute.

_STATUS_PARTIAL = "PARTIAL"
_BINARY_EXTREMES = {"FULL", "INVALID"}
_ABSTAIN = {OutcomeLabel.UNCERTAIN, OutcomeLabel.REQUIRES_REEVALUATION}


def _is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _sign(x: float) -> int:
    return (x > 1e-9) - (x < -1e-9)


def _status_nodes(scenario) -> dict[str, str]:
    from .gt_engine import status_attributes_of

    return status_attributes_of(scenario.canonical_input.rules)


def per_type_attribute_accuracy(
    pairs: list[tuple[str, Any, Any]], annotations
) -> dict[str, dict[str, Any]]:
    """`pairs` = (attribute, truth, prediction); prediction None = missing."""
    out: dict[str, dict[str, Any]] = {}
    for attr, truth, pred in pairs:
        t = annotations.attribute_types.get(attr)
        if t is None:
            continue
        band = annotations.tolerance_bands.get(attr)
        d = out.setdefault(t, {"n": 0, "missing": 0, "_hits": 0, "_err": [], "_ape": [], "_zero": 0, "_sign": 0})
        d["n"] += 1
        if t == "discrete":
            d["_hits"] += int(pred == truth)
            if pred is None:
                d["missing"] += 1
            continue
        if not _is_num(pred) or not _is_num(truth):
            d["missing"] += 1
            continue
        err = abs(pred - truth)
        d["_err"].append(err)
        if t == "continuous_bounded":
            eps = band.absolute if band and band.absolute is not None else 0.05
            d["_hits"] += int(err <= eps + 1e-12)
        elif t == "continuous_unbounded_positive":
            rel = (band.relative_pct if band and band.relative_pct is not None else 10.0) / 100
            if truth == 0:
                d["_zero"] += 1
                d["_hits"] += int(err <= (band.absolute if band and band.absolute is not None else 1e-9))
            else:
                d["_ape"].append(err / abs(truth))
                d["_hits"] += int(err <= rel * abs(truth) + 1e-12)
        else:  # signed_continuous
            d["_sign"] += int(_sign(pred) == _sign(truth))
    for t, d in out.items():
        n = d["n"]
        if t == "discrete":
            d["exact_match"] = d["_hits"] / n if n else NA
        else:
            d["mae"] = sum(d["_err"]) / len(d["_err"]) if d["_err"] else NA
            if t == "signed_continuous":
                d["sign_match"] = d["_sign"] / n if n else NA
            else:
                d["within_tolerance"] = d["_hits"] / n if n else NA
            if t == "continuous_unbounded_positive":
                d["mape"] = sum(d["_ape"]) / len(d["_ape"]) if d["_ape"] else NA
                d["mape_excluded_zero_truth"] = d["_zero"]
        for k in [k for k in d if k.startswith("_")]:
            del d[k]
    return out


def _predicted_status(result: RevisionResult, node: str, attr: str) -> Any:
    if result.feasibility_status is not None and node in result.feasibility_status:
        return result.feasibility_status[node]
    if result.attribute_values is not None:
        return (result.attribute_values.get(node) or {}).get(attr)
    return None


def _status_supported(result: RevisionResult) -> bool:
    return result.feasibility_status is not None or result.attribute_values is not None


def _direction_rate(result, ground_truth, pre_attrs, nodes) -> float | str:
    if result.attribute_values is None:
        return NA
    hit = tot = 0
    for nid in nodes:
        pre = pre_attrs.get(nid)
        if pre is None:
            continue
        pred = result.attribute_values.get(nid) or {}
        for a, truth in ground_truth.nodes[nid].attribute_values.items():
            if not (_is_num(truth) and _is_num(pre.get(a))) or truth == pre[a]:
                continue
            tot += 1
            p = pred.get(a)
            hit += int(_is_num(p) and _sign(p - pre[a]) == _sign(truth - pre[a]))
    return hit / tot if tot else NA


def _pairs(result, ground_truth, nodes, attrs: set[str] | None = None):
    av = result.attribute_values or {}
    return [
        (a, t, (av.get(n) or {}).get(a))
        for n in sorted(nodes)
        for a, t in ground_truth.nodes[n].attribute_values.items()
        if attrs is None or a in attrs
    ]


@dataclass
class Category5Metrics:
    attribute_accuracy_by_type: dict[str, Any] | str
    partial_satisfaction_preservation_rate: float | str
    binarisation_error_rate: float | str
    state_change_precision: float | str
    state_change_recall: float | str
    affected_node_precision: float | str
    affected_node_recall: float | str
    direction_correctness: float | str
    over_flip_rate: float | str
    inertia_rate: float | str
    depth_stratified_attribute_accuracy: dict[int, float | str] | str
    token_cost: int = 0
    wall_time_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def evaluate_category_5(result: RevisionResult, ground_truth: GroundTruth, scenario) -> Category5Metrics:
    graph, event = scenario.canonical_input.graph, scenario.canonical_input.event
    pre_attrs = {n.id: dict(n.attributes) for n in graph.nodes}
    cat2 = evaluate_category_2(result, ground_truth)
    true_affected = {n for n, g in ground_truth.nodes.items() if g.in_affected_set}
    status = _status_nodes(scenario)

    if result.attribute_values is None:
        by_type: dict[str, Any] | str = NA
        depth_acc: dict[int, float | str] | str = NA
    else:
        by_type = per_type_attribute_accuracy(
            _pairs(result, ground_truth, true_affected), scenario.evaluation_annotations
        )
        depths = _node_depths_via_propagating_edges(graph, _event_seed_nodes(event, graph))
        depth_acc = {}
        for d in sorted({depths[n] for n in true_affected if n in depths}):
            at_d = {n for n in true_affected if depths.get(n) == d}
            acc = per_type_attribute_accuracy(_pairs(result, ground_truth, at_d), scenario.evaluation_annotations)
            hits = [v.get("exact_match", v.get("within_tolerance", v.get("sign_match"))) for v in acc.values()]
            hits = [h for h in hits if h != NA]
            depth_acc[d] = sum(hits) / len(hits) if hits else NA

    partial = [n for n, a in status.items() if ground_truth.nodes.get(n) and ground_truth.nodes[n].attribute_values.get(a) == _STATUS_PARTIAL]
    if not _status_supported(result) or not partial:
        preserve: float | str = NA
        binar: float | str = NA
    else:
        preds = [_predicted_status(result, n, status[n]) for n in partial]
        preserve = sum(p == _STATUS_PARTIAL for p in preds) / len(preds)
        binar = sum(p in _BINARY_EXTREMES for p in preds) / len(preds)

    if not _status_supported(result):
        sc_p: float | str = NA
        sc_r: float | str = NA
    else:
        truth_sc = {n for n in status if n in ground_truth.nodes and ground_truth.nodes[n].state_change}
        pred_sc = {
            n for n, a in status.items()
            if n in pre_attrs and _predicted_status(result, n, a) not in (None, pre_attrs[n].get(a))
        }
        sc_p = len(pred_sc & truth_sc) / len(pred_sc) if pred_sc else (1.0 if not truth_sc else 0.0)
        sc_r = len(pred_sc & truth_sc) / len(truth_sc) if truth_sc else (1.0 if not pred_sc else 0.0)

    return Category5Metrics(
        attribute_accuracy_by_type=by_type,
        partial_satisfaction_preservation_rate=preserve,
        binarisation_error_rate=binar,
        state_change_precision=sc_p,
        state_change_recall=sc_r,
        affected_node_precision=cat2.affected_node_precision,
        affected_node_recall=cat2.affected_node_recall,
        direction_correctness=_direction_rate(result, ground_truth, pre_attrs, true_affected),
        over_flip_rate=cat2.over_flip_rate,
        inertia_rate=cat2.inertia_rate,
        depth_stratified_attribute_accuracy=depth_acc,
        token_cost=result.token_cost,
        wall_time_ms=result.wall_time_ms,
    )


def monotonicity_rate(inputs: list[float], outputs: list[float | None]) -> float | str:
    """Across a family of scenarios varying one input, fraction of adjacent
    pairs (sorted by input) whose outputs move in a consistent direction.
    None outputs (unsupported) → N/A."""
    if any(o is None for o in outputs) or len(inputs) < 2:
        return NA
    pts = sorted(zip(inputs, outputs))
    steps = [_sign(b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    direction = max((1, -1), key=lambda s: steps.count(s))
    return sum(s in (0, direction) for s in steps) / len(steps)


@dataclass
class Category6AMetrics:
    aggregate_value_accuracy: dict[str, Any] | str
    shortfall_excess_accuracy: dict[str, Any] | str
    per_dimension: dict[str, Any] | str
    feasibility_classification_accuracy: float | str
    compensation_reasoning_accuracy: float | str
    direction_correctness: float | str
    affected_node_precision: float | str
    affected_node_recall: float | str
    over_flip_rate: float | str
    inertia_rate: float | str
    token_cost: int = 0
    wall_time_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def _roles(scenario) -> dict[str, set[str]]:
    from .gt_engine import computations_of

    roles: dict[str, set[str]] = {}
    for c in computations_of(scenario.canonical_input.rules):
        roles.setdefault(c.get("role", "derived"), set()).add(c["attribute"])
    return roles


def _compensation_answer(result, scenario, ground_truth) -> float | str:
    truth = ground_truth.scenario.compensation_viable
    if truth is None:
        return NA
    from .gt_engine import top_label_of

    rules = scenario.canonical_input.rules
    status = _status_nodes(scenario)
    if not _status_supported(result):
        return NA
    satisfied = [n for n, a in status.items() if (scenario.canonical_input.graph.node(n) or None)
                 and scenario.canonical_input.graph.node(n).attributes.get(a) == top_label_of(rules, n)]
    said = all(_predicted_status(result, n, status[n]) == top_label_of(rules, n) for n in satisfied)
    return float(said == truth)


def evaluate_category_6a(result: RevisionResult, ground_truth: GroundTruth, scenario) -> Category6AMetrics:
    pre_attrs = {n.id: dict(n.attributes) for n in scenario.canonical_input.graph.nodes}
    cat2 = evaluate_category_2(result, ground_truth)
    status = _status_nodes(scenario)
    roles = _roles(scenario)
    ann = scenario.evaluation_annotations
    concl = [n for n in status if n in ground_truth.nodes]
    if result.attribute_values is None:
        agg: dict[str, Any] | str = NA
        gap: dict[str, Any] | str = NA
        per_dim: dict[str, Any] | str = NA
    else:
        agg = per_type_attribute_accuracy(_pairs(result, ground_truth, concl, roles.get("aggregate", set())), ann)
        gap = per_type_attribute_accuracy(_pairs(result, ground_truth, concl, roles.get("gap", set())), ann)
        per_dim = {
            a: per_type_attribute_accuracy(_pairs(result, ground_truth, concl, {a}), ann)
            for a in sorted(roles.get("aggregate", set()) | roles.get("gap", set()))
        }
    if not _status_supported(result) or not concl:
        feas: float | str = NA
    else:
        feas = sum(
            _predicted_status(result, n, status[n]) == ground_truth.nodes[n].attribute_values.get(status[n])
            for n in concl
        ) / len(concl)
    affected = {n for n, g in ground_truth.nodes.items() if g.in_affected_set}
    return Category6AMetrics(
        aggregate_value_accuracy=agg,
        shortfall_excess_accuracy=gap,
        per_dimension=per_dim,
        feasibility_classification_accuracy=feas,
        compensation_reasoning_accuracy=_compensation_answer(result, scenario, ground_truth),
        direction_correctness=_direction_rate(result, ground_truth, pre_attrs, affected),
        affected_node_precision=cat2.affected_node_precision,
        affected_node_recall=cat2.affected_node_recall,
        over_flip_rate=cat2.over_flip_rate,
        inertia_rate=cat2.inertia_rate,
        token_cost=result.token_cost,
        wall_time_ms=result.wall_time_ms,
    )


@dataclass
class Category6BMetrics:
    feasible_combination_recall: float | str
    feasible_combination_precision: float | str
    optimal_combination_accuracy: float | str
    compensation_reasoning_accuracy: float | str
    combinatorial_search_cost: int | str
    affected_node_precision: float | str
    affected_node_recall: float | str
    token_cost: int = 0
    wall_time_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def evaluate_category_6b(result: RevisionResult, ground_truth: GroundTruth, scenario) -> Category6BMetrics:
    cat1 = evaluate_category_1(result, ground_truth)
    truth = {frozenset(c) for c in ground_truth.scenario.feasible_combinations}
    if result.feasible_combinations is None:
        rec: float | str = NA
        prec: float | str = NA
    else:
        pred = {frozenset(c) for c in result.feasible_combinations}
        rec = len(pred & truth) / len(truth) if truth else (1.0 if not pred else 0.0)
        prec = len(pred & truth) / len(pred) if pred else (1.0 if not truth else 0.0)
    opt = ground_truth.scenario.optimal_combination
    if not opt:
        opt_acc: float | str = NA
    elif result.attribute_values is None:
        opt_acc = NA
    else:
        opt_acc = sum(
            (result.attribute_values.get(n) or {}).get("selected") == v.get("members") for n, v in opt.items()
        ) / len(opt)
    if ground_truth.scenario.compensation_viable is None or result.feasible_combinations is None:
        comp: float | str = NA
    else:
        comp = float(bool(result.feasible_combinations) == ground_truth.scenario.compensation_viable)
    return Category6BMetrics(
        feasible_combination_recall=rec,
        feasible_combination_precision=prec,
        optimal_combination_accuracy=opt_acc,
        compensation_reasoning_accuracy=comp,
        combinatorial_search_cost=result.search_cost if result.search_cost is not None else NA,
        affected_node_precision=cat1.affected_node_precision,
        affected_node_recall=cat1.affected_node_recall,
        token_cost=result.token_cost,
        wall_time_ms=result.wall_time_ms,
    )


# ---------------------------------------------------------------------------
# Category 7 — abstention. Metrics pool node-level decisions over a list of
# (result, ground_truth) pairs so per-pathology rates are meaningful.
# False-confidence is reported first and never averaged with anything.
# ---------------------------------------------------------------------------

@dataclass
class Category7Metrics:
    false_confidence_rate: float | str
    false_abstention_rate: float | str
    correct_abstention_rate: float | str
    determinability_accuracy: float | str
    pathology_precision_recall: dict[str, dict[str, float | str]] | str
    escalation_accuracy: float | str
    coverage: float | str
    selective_risk: float | str
    selective_accuracy_coverage_area: float | str
    operating_point_tau_0_5: dict[str, float | str] | str

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def _abstained(result: RevisionResult, nid: str) -> bool:
    if result.determinability is not None and result.determinability.get(nid) == "AMBIGUOUS":
        return True
    lbl = (result.outcome_labels or {}).get(nid)
    return lbl in _ABSTAIN


def _node_correct(result: RevisionResult, nid: str, g) -> bool:
    if (result.outcome_labels or {}).get(nid) != g.outcome_label:
        return False
    if result.attribute_values is None:
        return True
    pred = result.attribute_values.get(nid) or {}
    for a, t in g.attribute_values.items():
        p = pred.get(a)
        if _is_num(t) and _is_num(p):
            if abs(p - t) > 1e-3:
                return False
        elif p != t:
            return False
    return True


def selective_accuracy_coverage_area(items: list[tuple[float, bool, bool]]) -> tuple[float | str, dict[str, float | str]]:
    """items = (confidence, correct, determinable) per node.

    Commit iff confidence ≥ τ, τ ∈ {0, 0.05, …, 1}. Coverage = committed /
    all; selective accuracy = correct / committed over the DETERMINABLE
    committed subset. Zero-coverage points are excluded; area by trapezoid
    over coverage. Returns (area, operating point at τ = 0.5).
    """
    if not items:
        return NA, NA
    pts: list[tuple[float, float]] = []
    op: dict[str, float | str] = {}
    for i in range(21):
        tau = i * 0.05
        committed = [it for it in items if it[0] >= tau - 1e-12]
        cov = len(committed) / len(items)
        det = [it for it in committed if it[2]]
        risk: float | str = NA if not det else 1 - sum(it[1] for it in det) / len(det)
        if i == 10:
            op = {"coverage": cov, "selective_risk": risk}
        if cov > 0 and risk != NA:
            pts.append((cov, 1 - risk))
    pts = sorted(set(pts))
    if len(pts) < 2:
        return NA, op
    area = sum((b[0] - a[0]) * (a[1] + b[1]) / 2 for a, b in zip(pts, pts[1:]))
    return area, op


def evaluate_category_7(pairs: list[tuple[RevisionResult, GroundTruth]]) -> Category7Metrics:
    if not pairs or any(r.determinability is None for r, _ in pairs):
        return Category7Metrics(NA, NA, NA, NA, NA, NA, NA, NA, NA, NA)
    amb = det = fc = fa = ca = right = esc_hit = esc_n = 0
    committed = committed_det = committed_wrong = total = 0
    tp: dict[str, int] = {}
    fp: dict[str, int] = {}
    fn: dict[str, int] = {}
    items: list[tuple[float, bool, bool]] = []
    native_conf = all(r.confidence_scores is not None for r, _ in pairs)
    for r, gt in pairs:
        for nid, g in gt.nodes.items():
            total += 1
            is_amb = g.determinability.value == "AMBIGUOUS"
            abst = _abstained(r, nid)
            right += int(abst == is_amb)
            if is_amb:
                amb += 1
                fc += int(not abst)
                ca += int(abst)
                if abst and r.outcome_labels is not None:
                    esc_n += 1
                    esc_hit += int(r.outcome_labels.get(nid) == g.outcome_label)
            else:
                det += 1
                fa += int(abst)
            if not abst:
                committed += 1
                if not is_amb:
                    committed_det += 1
                    committed_wrong += int(not _node_correct(r, nid, g))
            truth_codes = set(g.pathology_codes)
            pred_codes = set((r.pathology_flags or {}).get(nid, []))
            for c in truth_codes | pred_codes:
                tp[c] = tp.get(c, 0) + int(c in truth_codes and c in pred_codes)
                fp[c] = fp.get(c, 0) + int(c in pred_codes and c not in truth_codes)
                fn[c] = fn.get(c, 0) + int(c in truth_codes and c not in pred_codes)
            if native_conf:
                conf = 0.0 if abst else float(r.confidence_scores.get(nid, 1.0))
                items.append((conf, (not is_amb) and _node_correct(r, nid, g), not is_amb))
    if any(r.pathology_flags is None for r, _ in pairs):
        path: dict[str, dict[str, float | str]] | str = NA
    else:
        path = {
            c: {
                "precision": tp[c] / (tp[c] + fp[c]) if tp[c] + fp[c] else NA,
                "recall": tp[c] / (tp[c] + fn[c]) if tp[c] + fn[c] else NA,
            }
            for c in sorted(tp)
        }
    area, op = selective_accuracy_coverage_area(items) if native_conf else (NA, NA)
    return Category7Metrics(
        false_confidence_rate=fc / amb if amb else NA,
        false_abstention_rate=fa / det if det else NA,
        correct_abstention_rate=ca / amb if amb else NA,
        determinability_accuracy=right / total if total else NA,
        pathology_precision_recall=path,
        escalation_accuracy=esc_hit / esc_n if esc_n else NA,
        coverage=committed / total if total else NA,
        selective_risk=committed_wrong / committed_det if committed_det else NA,
        selective_accuracy_coverage_area=area,
        operating_point_tau_0_5=op,
    )
