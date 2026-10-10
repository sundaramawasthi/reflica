"""Known-answer tests for the analysis' binary indicators and paired tables."""
from __future__ import annotations

import sys

import pytest

from reflica_bench import protocol_lock as pl

pytest.importorskip("ortools")
sys.path.insert(0, str(pl.FULL_RUN))
import analysis as A  # noqa: E402


def _c(correct, nodes, fc=0, fa=0, amb=0):
    return {"correct": correct, "nodes": nodes, "false_confident": fc, "false_abstained": fa,
            "ambiguous": amb, "determinable": nodes - amb, "primary": correct / nodes}


def test_indicator_uses_at_least_half_of_common_repeats():
    cells = {("B", "B5", "s"): [_c(3, 3), _c(2, 3), _c(2, 3)],     # fully correct in 1 of 3 -> 0
             ("B", "B5", "t"): [_c(3, 3), _c(3, 3), _c(2, 3)],     # 2 of 3 -> 1
             ("B", "B5", "u"): [_c(3, 3), _c(2, 3)],               # 1 of 2 (half) -> 1
             ("B", "B5", "v"): [_c(2, 3, fc=1, amb=1)],            # one repeat, falsely confident
             ("B", "B5", "w"): [_c(3, 3, fc=0, amb=1), _c(2, 3, fc=1, amb=1), _c(2, 3, fc=2, amb=2)]}
    assert [A.indicator(cells, ("B", "B5"), s, "fully_correct") for s in "stuv"] == [0, 1, 1, 0]
    assert A.indicator(cells, ("B", "B5"), "v", "any_false_confidence") == 1
    assert A.indicator(cells, ("B", "B5"), "w", "any_false_confidence") == 1   # 2 of 3 repeats


def test_paired_table_orientation_is_b5_first():
    cells = {}
    for i, (b5, b1) in enumerate([(1, 0), (1, 0), (1, 1), (0, 1), (0, 0)]):
        cells[("B", "B5", f"s{i}")] = [_c(3 if b5 else 2, 3)]
        cells[("direct", "B1", f"s{i}")] = [_c(3 if b1 else 2, 3)]
    t = A._paired(cells, [f"s{i}" for i in range(5)], "fully_correct", ("direct", "B1"))
    assert (t.both, t.only_first, t.only_second, t.neither) == (1, 2, 1, 1)
    assert t.difference == pytest.approx(0.2)  # B5 − B1
