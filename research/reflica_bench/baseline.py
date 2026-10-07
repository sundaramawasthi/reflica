"""Common baseline interface.

Separated from input adapters per the locked design:

    ExperimentRunner  ──▶  InputAdapter  ──▶  Baseline  ──▶  RevisionResult

Null-vs-empty rule (locked):

    None   → baseline did not produce this dimension; capability flag False;
             metric → N/A.
    [] / {} → baseline produced this dimension; result legitimately empty;
             metric computed numerically.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from .adapters import AdapterOutput
from .schema import Graph, OutcomeLabel


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class RevisionResult:
    """Universal result shape; unsupported dimensions are None."""

    affected_set: list[str] | None = None
    post_event_graph: Graph | None = None
    outcome_labels: dict[str, OutcomeLabel] | None = None
    attribute_values: dict[str, dict[str, Any]] | None = None
    feasibility_status: dict[str, str] | None = None
    determinability: dict[str, str] | None = None
    pathology_flags: dict[str, list[str]] | None = None
    confidence_scores: dict[str, float] | None = None
    feasible_combinations: list[list[str]] | None = None
    explanation: Any | None = None
    unsupported_dimensions: list[str] = field(default_factory=list)
    token_cost: int = 0
    wall_time_ms: int = 0


# ---------------------------------------------------------------------------
# Baseline protocol
# ---------------------------------------------------------------------------

class Baseline(Protocol):
    name: str
    version: str
    supports_scope_detection: bool
    supports_attribute_computation: bool
    supports_feasibility_classification: bool
    supports_abstention: bool

    def revise(self, adapter_output: AdapterOutput) -> RevisionResult: ...


# ---------------------------------------------------------------------------
# Helper: wall-time timing
# ---------------------------------------------------------------------------

class Timer:
    def __init__(self) -> None:
        self._t0 = 0.0
        self.elapsed_ms = 0

    def __enter__(self) -> "Timer":
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.elapsed_ms = int((time.perf_counter() - self._t0) * 1000)
