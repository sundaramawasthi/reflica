"""Input adapter tests."""

from __future__ import annotations

import pytest

from reflica_bench.adapters import OracleEvaluatorAdapter, StructuredAdapter_v1
from reflica_bench.linter import LintError
from reflica_bench.loader import cat1_dir, iter_scenarios
from reflica_bench.schema import Regime


def test_structured_adapter_strips_metadata_and_hidden_rules():
    adapter = StructuredAdapter_v1()
    for s in iter_scenarios(cat1_dir()):
        assert s.regime == Regime.R_S
        out = adapter.adapt(s, run_id="run-1")
        assert out.structured is not None
        assert out.oracle_canonical is None
        assert set(out.metadata.keys()) == {"operation", "regime", "run_id"}
        # Rules dumped as dict — no declared_input anywhere.
        for block_name, block in out.structured.rules.items():
            assert isinstance(block, dict)
            assert "declared_input" not in block


def test_structured_adapter_rejects_rn_scenario():
    adapter = StructuredAdapter_v1()
    s = iter_scenarios(cat1_dir())[0].model_copy(deep=True)
    s.regime = Regime.R_N
    s.natural_language_description = "placeholder"
    with pytest.raises(LintError):
        adapter.adapt(s, run_id="run-x")


def test_oracle_adapter_returns_canonical_only():
    adapter = OracleEvaluatorAdapter()
    for s in iter_scenarios(cat1_dir()):
        out = adapter.adapt(s, run_id="orc-1")
        assert out.structured is None
        assert out.oracle_canonical is not None
        assert set(out.metadata.keys()) == {"operation", "regime", "run_id"}
