"""Offline checks of the R-N pilot scoring harness (no API)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "experiments" / "rn_pilot"))

import pilot  # noqa: E402
from reflica_bench import rn  # noqa: E402
from reflica_bench.loader import load_scenario  # noqa: E402

DEC = {"MUST_CHANGE": "changed", "MUST_STAY_STABLE": "not_changed",
       "UNCERTAIN": "cannot_answer", "REQUIRES_REEVALUATION": "needs_human_review"}


def _perfect_b1(sid):
    sc = load_scenario(rn.source_path(sid))
    alias = rn.load_rn(sid).alias_map
    inv = {v: k for k, v in alias.items()}
    ents = [{"label": inv[n], "decision": DEC[g.outcome_label.value], "attributes": g.attribute_values,
             "confidence": 1.0} for n, g in sc.ground_truth.nodes.items()]
    return sc, alias, json.dumps({"entities": ents})


def test_perfect_direct_output_scores_perfectly():
    for sid in ("cat2_pair_edit_001", "cat4_diamond_delete_preservation_001", "cat7_conflicting_evidence_edit_001"):
        sc, alias, text = _perfect_b1(sid)
        m = pilot.metrics(pilot.from_direct("B1", text, sc, alias, {})[0], sc)
        for k in ("over_flip_rate", "inertia_rate", "false_confidence_rate", "false_abstention_rate"):
            assert m.get(k) in (None, 0.0, "N/A"), (sid, k, m[k])


def test_empty_delta_is_penalised():
    sid = "cat2_pair_edit_001"
    sc = load_scenario(rn.source_path(sid))
    r, _ = pilot.from_direct("B2", json.dumps({"entities": []}), sc, rn.load_rn(sid).alias_map, {})
    assert pilot.metrics(r, sc)["inertia_rate"] == 1.0
