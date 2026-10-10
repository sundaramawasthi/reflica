"""Per-scenario node outcomes for the full-experiment protocol (§4).

Built only from the evaluator's own node primitives (`_abstained`,
`_node_correct`) so the protocol endpoints cannot drift from the evaluator:

    determinable gold node  -> correct iff not abstained and `_node_correct`
    AMBIGUOUS gold node     -> correct iff abstained

A failed output (unparseable, schema-invalid, extraction or solver failure)
is passed as ``None`` and handles no node correctly: every node is incorrect
and counted as committed, so an ambiguous node counts as falsely confident.
A gold node with no prediction is likewise committed-and-wrong (evaluator
semantics); it is also counted in ``missing_prediction``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .baseline import RevisionResult
from .evaluator import _abstained, _node_correct
from .schema import Determinability, GroundTruth


@dataclass(frozen=True)
class NodeCounts:
    nodes: int
    ambiguous: int
    determinable: int
    correct: int                # primary endpoint numerator
    false_confident: int        # ambiguous and committed
    false_abstained: int        # determinable and abstained
    committed_wrong: int        # determinable, committed, not `_node_correct`
    label_correct: int          # determinable, committed, label == gold label (H3)
    missing_prediction: int     # gold node absent from the output
    failed_output: bool

    @property
    def primary(self) -> float:
        return self.correct / self.nodes

    def to_dict(self) -> dict:
        return asdict(self) | {"primary": self.primary}


def node_counts(result: RevisionResult | None, gt: GroundTruth) -> NodeCounts:
    n = amb = det = ok = fc = fa = cw = lab = miss = 0
    for nid, g in gt.nodes.items():
        n += 1
        is_amb = g.determinability == Determinability.AMBIGUOUS
        amb += is_amb
        det += not is_amb
        if result is None:
            fc += is_amb
            cw += not is_amb
            miss += 1
            continue
        labels = result.outcome_labels or {}
        miss += nid not in labels and nid not in (result.determinability or {})
        abst = _abstained(result, nid)
        if is_amb:
            ok += abst
            fc += not abst
        else:
            lab += (not abst) and labels.get(nid) == g.outcome_label
            if abst:
                fa += 1
            elif _node_correct(result, nid, g):
                ok += 1
            else:
                cw += 1
    return NodeCounts(n, amb, det, ok, fc, fa, cw, lab, miss, result is None)
