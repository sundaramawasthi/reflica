"""Evaluator: compare a baseline's RevisionResult against ground truth.

Category 1 metrics only in this version:

    - over_flip_rate            (primary)
    - unnecessary_revision_rate (primary)
    - affected_node_precision   (primary; recall is trivially 1.0 for Cat 1
                                 single-affected-node scenarios and reported
                                 as 1.0 only when the affected set has size
                                 exactly 1)
    - final_state_accuracy      (secondary — must be 100% for a correct method)
    - token_cost                (universal)
    - wall_time_ms              (universal)

Unsupported dimensions (RevisionResult.* is None) are reported as N/A,
never as zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .baseline import RevisionResult
from .schema import GroundTruth, OutcomeLabel


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
