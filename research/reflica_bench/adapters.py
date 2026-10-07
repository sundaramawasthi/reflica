"""Input adapters.

Two concrete adapters in this version:

    StructuredAdapter_v1   — for R-S regime. Mechanically sanitises
                             canonical_input into method_input.structured.

    OracleEvaluatorAdapter — special adapter used ONLY by B6 (the scope
                             oracle). It reads canonical_input directly and
                             NEVER passes through NL extraction. B6 is the
                             single declared exception to the "ground truth
                             never exposed to methods" rule, justified
                             because B6 is evaluator-side.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .linter import (
    LintError,
    assert_no_forbidden_fields,
    method_metadata,
    sanitise_rules_for_method,
)
from .schema import (
    MethodInputStructured,
    Regime,
    Scenario,
)


@dataclass(frozen=True)
class AdapterOutput:
    """Everything a baseline receives from the adapter.

    `oracle_canonical` is only populated by OracleEvaluatorAdapter and is
    read exclusively by B6.
    """

    structured: MethodInputStructured | None
    oracle_canonical: Any | None  # kept as `Any` to avoid Scenario leakage via type
    metadata: dict[str, str]


class InputAdapter(Protocol):
    name: str
    version: str

    def adapt(self, scenario: Scenario, run_id: str) -> AdapterOutput: ...


# ---------------------------------------------------------------------------
# StructuredAdapter_v1
# ---------------------------------------------------------------------------

class StructuredAdapter_v1:
    name: str = "StructuredAdapter_v1"
    version: str = "1.0.0"

    def adapt(self, scenario: Scenario, run_id: str) -> AdapterOutput:
        if scenario.regime != Regime.R_S:
            raise LintError(
                f"StructuredAdapter_v1 only handles R-S scenarios; got {scenario.regime}"
            )

        # Rules → dict → sanitise → strip declared_input → forbidden-field assert.
        rules_dict = scenario.canonical_input.rules.model_dump()
        sanitised_rules = sanitise_rules_for_method(rules_dict)

        structured = MethodInputStructured(
            graph=scenario.canonical_input.graph,
            rules=sanitised_rules,
            event=scenario.canonical_input.event,
        )

        # Hard safety net: ensure no forbidden metadata leaked into method input.
        payload = structured.model_dump()
        assert_no_forbidden_fields(payload)

        return AdapterOutput(
            structured=structured,
            oracle_canonical=None,
            metadata=method_metadata(scenario, run_id),
        )


# ---------------------------------------------------------------------------
# OracleEvaluatorAdapter — used only by B6
# ---------------------------------------------------------------------------

class OracleEvaluatorAdapter:
    name: str = "OracleEvaluatorAdapter"
    version: str = "1.0.0"

    def adapt(self, scenario: Scenario, run_id: str) -> AdapterOutput:
        # B6 reads canonical scenario directly. Returned as `oracle_canonical`;
        # the normal `structured` field stays None so no baseline that is NOT
        # B6 could accidentally consume it (B6's revise() reads oracle_canonical
        # explicitly).
        return AdapterOutput(
            structured=None,
            oracle_canonical=scenario.canonical_input,
            metadata=method_metadata(scenario, run_id),
        )
