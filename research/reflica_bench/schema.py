"""Unified scenario schema.

Pydantic types that encode the frozen cross-category synthesis contract.
Only the subset needed for Category 1 floor cases is populated now; later
categories will fill in satisfaction_functions, aggregation_functions,
fixed_point_semantics, ground_truth.scenario.*, etc.

Invariants enforced here by the linter in `linter.py`:
    A.1  `declared_input` metadata is stripped from method_input.
    A.2  category / subcategory / template_id / scenario_id / ground_truth
         / evaluation_annotations are NEVER method-visible.
    Edge IDs are globally unique within a scenario.
    Operation target_kind disambiguates node-vs-edge targets.
    Every rule carries machine + human representations (added when rule
    blocks become non-empty from Cat 2 onward).
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums fixed by the design contract
# ---------------------------------------------------------------------------

class EdgeType(str, Enum):
    # Propagating
    REQUIRES = "requires"
    SUPPORTS = "supports"
    CAUSES = "causes"
    BLOCKS = "blocks"
    ENABLES = "enables"
    DERIVED_FROM = "derived_from"
    # Non-propagating
    INFORMS = "informs"
    REFERENCES = "references"


PROPAGATING_EDGE_TYPES: frozenset[EdgeType] = frozenset(
    {
        EdgeType.REQUIRES,
        EdgeType.SUPPORTS,
        EdgeType.CAUSES,
        EdgeType.BLOCKS,
        EdgeType.ENABLES,
        EdgeType.DERIVED_FROM,
    }
)


class Operation(str, Enum):
    ADD = "ADD"
    EDIT = "EDIT"
    DELETE = "DELETE"
    RELATIONSHIP_CHANGE = "RELATIONSHIP_CHANGE"


class TargetKind(str, Enum):
    NODE = "node"
    EDGE = "edge"


class Regime(str, Enum):
    R_S = "R-S"
    R_N = "R-N"


class OutcomeLabel(str, Enum):
    MUST_CHANGE = "MUST_CHANGE"
    MUST_STAY_STABLE = "MUST_STAY_STABLE"
    REQUIRES_REEVALUATION = "REQUIRES_REEVALUATION"
    UNCERTAIN = "UNCERTAIN"


class Determinability(str, Enum):
    DETERMINABLE = "DETERMINABLE"
    AMBIGUOUS = "AMBIGUOUS"


# ---------------------------------------------------------------------------
# Core graph types
# ---------------------------------------------------------------------------

class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: str | None = None
    timestamp: str | None = None


class Node(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: str = "generic"
    attributes: dict[str, Any] = Field(default_factory=dict)
    state: str | None = None
    provenance: Provenance | None = None
    confidence: float | None = None


class Edge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edge_id: str
    source: str
    target: str
    type: EdgeType
    justification_id: str | None = None
    weight: float | None = None

    @property
    def is_propagating(self) -> bool:
        return self.type in PROPAGATING_EDGE_TYPES


class Graph(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nodes: list[Node] = Field(default_factory=list)
    edges: list[Edge] = Field(default_factory=list)

    def node_ids(self) -> set[str]:
        return {n.id for n in self.nodes}

    def edge_ids(self) -> set[str]:
        return {e.edge_id for e in self.edges}

    def node(self, node_id: str) -> Node | None:
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def edge(self, edge_id: str) -> Edge | None:
        for e in self.edges:
            if e.edge_id == edge_id:
                return e
        return None


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

class RuleBlock(BaseModel):
    """A rule block with explicit method-visibility.

    declared_input=True   -> survives sanitisation into method_input.
    declared_input=False  -> stripped from method_input; evaluator-only.

    The linter must then strip the `declared_input` flag itself (invariant A.1).
    """

    model_config = ConfigDict(extra="forbid")
    declared_input: bool
    entries: dict[str, Any] = Field(default_factory=dict)


class Rules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Which attributes of each node are actually read by any rule.
    # In Cat 1 floor this is the only rule block we need: it lets us test
    # attribute-level irrelevance (template T1.3).
    read_attributes: RuleBlock = Field(
        default_factory=lambda: RuleBlock(declared_input=True, entries={})
    )

    # From Cat 2 onward: justifications, satisfaction_functions,
    # aggregation_functions, fixed_point_semantics, resolution_rules, defaults.
    # Omitted here; add fields as later categories are implemented.


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------

class EdgeChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edge_id: str | None = None  # existing edge for DELETE/RELATIONSHIP_CHANGE; None for ADD
    source: str | None = None
    target: str | None = None
    old_type: EdgeType | None = None
    new_type: EdgeType | None = None


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Operation
    target_kind: TargetKind
    target_id: str | None = None  # node_id or edge_id depending on target_kind
    attribute: str | None = None
    new_value: Any | None = None
    edge_change: EdgeChange | None = None
    new_node: Node | None = None


# ---------------------------------------------------------------------------
# Canonical input (hidden; evaluator-only)
# ---------------------------------------------------------------------------

class CanonicalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    graph: Graph
    rules: Rules
    event: Event


# ---------------------------------------------------------------------------
# Method input (what the baseline receives)
# ---------------------------------------------------------------------------

class MethodInputStructured(BaseModel):
    """R-S representation delivered to a baseline.

    Produced by the mechanical sanitiser from CanonicalInput: all RuleBlocks
    with declared_input=False are stripped, and the `declared_input` flag
    itself is removed. See invariants A.1 and A.2.
    """

    model_config = ConfigDict(extra="forbid")
    graph: Graph
    rules: dict[str, Any]  # sanitised, flag-stripped rule content
    event: Event


class MethodInputNaturalLanguage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str


class MethodInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    structured: MethodInputStructured | None = None
    natural_language: MethodInputNaturalLanguage | None = None


# ---------------------------------------------------------------------------
# Ground truth (evaluator-only)
# ---------------------------------------------------------------------------

class NodeGroundTruth(BaseModel):
    model_config = ConfigDict(extra="forbid")
    outcome_label: OutcomeLabel
    state_change: bool = False
    attribute_values: dict[str, Any] = Field(default_factory=dict)
    in_affected_set: bool = False
    determinability: Determinability = Determinability.DETERMINABLE
    pathology_codes: list[str] = Field(default_factory=list)


class ScenarioGroundTruth(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pathology_codes: list[str] = Field(default_factory=list)
    feasible_combinations: list[list[str]] = Field(default_factory=list)
    optimal_combination: dict[str, Any] | None = None
    fixed_point_analysis: dict[str, Any] = Field(default_factory=dict)
    consistent_completions: list[dict[str, Any]] = Field(default_factory=list)


class GroundTruth(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario: ScenarioGroundTruth = Field(default_factory=ScenarioGroundTruth)
    nodes: dict[str, NodeGroundTruth] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Evaluation annotations
# ---------------------------------------------------------------------------

class ToleranceBand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    absolute: float | None = None
    relative_pct: float | None = None


class EvaluationAnnotations(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attribute_types: dict[str, str] = Field(default_factory=dict)
    tolerance_bands: dict[str, ToleranceBand] = Field(default_factory=dict)
    escalation_policy: dict[str, str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Scenario (top-level record on disk)
# ---------------------------------------------------------------------------

class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Identity (never passed through to method_input — invariant A.2)
    scenario_id: str
    category: int
    subcategory: str | None = None
    template_id: str
    operation: Operation
    regime: Regime
    scenario_version: str
    generator_version: str

    natural_language_description: str | None = None  # required when regime == R_N

    canonical_input: CanonicalInput
    # method_input is computed on demand by the StructuredAdapter from canonical_input.
    # It is intentionally NOT stored in the scenario file so that no leakage can occur
    # between evaluator and method.

    ground_truth: GroundTruth
    evaluation_annotations: EvaluationAnnotations = Field(
        default_factory=EvaluationAnnotations
    )
    notes: str | None = None
