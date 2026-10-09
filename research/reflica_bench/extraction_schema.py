"""Typed extractor output schema (experiment config v1.2).

The LLM extractor must emit exactly the structured representation the frozen
downstream pipeline consumes: `to_method_input()` turns it into the same
`MethodInputStructured` that StructuredAdapter_v1 builds from a canonical
scenario, with no interpretation layer. Rule blocks follow the benchmark's
formula grammar (gt_engine.py docstring), which B4b executes directly.

Graph / Event are mirrored here only to attach field descriptions for the
model; tests assert the field sets stay identical to schema.Graph / Event.
"""

from __future__ import annotations

from typing import Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from .schema import EdgeType, MethodInputStructured, Operation, TargetKind

_F = ConfigDict(extra="forbid")
Key = Field(description='"<node_id>.<attribute>", e.g. "E2.coverage"')


# ---------------------------------------------------------------------------
# Formula grammar
# ---------------------------------------------------------------------------

class UnknownMarker(BaseModel):
    """`{"$unknown": "<why>"}` — accepted ONLY as a fallback (Ref/Src default),
    where it means exactly "no fallback given" (v1.4)."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, serialize_by_alias=True)
    unknown: str = Field(alias="$unknown")


class Ref(BaseModel):
    model_config = _F
    ref: str = Field(description='Read attribute: "<node_id>.<attribute>"')
    default: UnknownMarker | Expr | None = Field(None, description="Value if the node/attribute is missing")


class Src(BaseModel):
    model_config = _F
    src: str = Field(description='Read "<node_id>.<attribute>" only while that node has an influencing link into the node this rule computes')
    default: UnknownMarker | Expr | None = Field(None, description="Value when there is no such link; omit if the text gives none")


class Agg(BaseModel):
    model_config = _F
    agg: Literal["sum", "max", "min", "count"] = Field(description="Combine over all nodes with an influencing link into the computed node")
    attribute: str
    empty: float | int = Field(0, description="Result when no node is linked")


class Op(BaseModel):
    model_config = _F
    op: Literal["add", "sub", "mul", "div", "min", "max", "ge", "gt", "le", "lt", "eq", "and", "or", "not"]
    args: list[Expr]


class CaseBranch(BaseModel):
    model_config = _F
    when: Union[Literal["otherwise"], Expr]
    then: str


class Case(BaseModel):
    model_config = _F
    case: list[CaseBranch] = Field(description='Ordered; first true "when" wins; last branch must be "otherwise"')


Expr = Union[float, int, bool, str, None, Ref, Src, Agg, Op, Case]
for _m in (Ref, Src, Op, CaseBranch, Case):
    _m.model_rebuild()


# ---------------------------------------------------------------------------
# Rule blocks (serialise to {"entries": ...} exactly as B4b reads them)
# ---------------------------------------------------------------------------

class Computation(BaseModel):
    model_config = _F
    node: str = Field(description="Node id whose attribute this rule sets")
    attribute: str
    machine: Expr = Field(description="The formula")
    human: str = Field(description="The rule as written in the text")
    role: str | None = None
    when_linked: list[str] | None = Field(None, description="Rule applies only while these nodes have an influencing link into `node`")


class StatusCase(BaseModel):
    model_config = _F
    label: str
    when: Union[Literal["otherwise"], Expr]


class StatusFunction(BaseModel):
    model_config = _F
    status_attribute: str = "status"
    mapping: list[StatusCase] = Field(description='Ordered; last entry must have when="otherwise"')
    human: str | None = None


class SatisfactionEntries(BaseModel):
    model_config = _F
    computations: list[Computation] = []
    status_functions: dict[str, StatusFunction] = Field({}, description="Keyed by node id")


class Constraint(BaseModel):
    model_config = _F
    attribute: str
    agg: Literal["sum", "max", "min"]
    op: Literal["ge", "gt", "le", "lt", "eq"]
    value: float | int


class Objective(BaseModel):
    model_config = _F
    attribute: str
    agg: Literal["sum", "max", "min"]
    sense: Literal["min", "max"] = "min"


class Problem(BaseModel):
    model_config = _F
    constraints: list[Constraint]
    objective: Objective | None = None
    status_attribute: str = "status"
    feasible_label: str = "FEASIBLE"
    infeasible_label: str = "INFEASIBLE"
    human: str | None = None


class PropMachine(BaseModel):
    model_config = _F
    operator: Literal["copy", "map"] = "copy"
    mapping: dict[str, Any] | None = None
    default: Any = None
    inputs: list[dict[str, str]] | None = None
    output_name: str | None = None


class PropRule(BaseModel):
    model_config = _F
    from_node: str
    from_attribute: str
    to_node: str
    to_attribute: str
    machine: PropMachine = PropMachine()
    human: str = ""


class Conclusion(BaseModel):
    model_config = _F
    status_attribute: str = "status"
    true_value: Any = True
    false_value: Any = False
    justifications: list[list[str]] = Field(description="Alternatives (OR); each is a list of premise node ids (AND)")


class Claim(BaseModel):
    model_config = _F
    source: str
    value: Any


class Resolution(BaseModel):
    model_config = _F
    policy: Literal["prefer_source"] = "prefer_source"
    source: str = Field(description='Source whose value wins; "graph" = the value recorded in the plan')


def _block(name: str, entries_type, default):
    return type(name, (BaseModel,), {
        "__annotations__": {"entries": entries_type},
        "entries": Field(default_factory=lambda: default),
        "model_config": _F,
    })


class _PropEntries(BaseModel):
    model_config = _F
    rules: list[PropRule] = []


class _JustEntries(BaseModel):
    model_config = _F
    conclusions: dict[str, Conclusion] = {}


class _ComboEntries(BaseModel):
    model_config = _F
    problems: dict[str, Problem] = Field({}, description="At most one, keyed by the node it decides")


class _EvidenceEntries(BaseModel):
    model_config = _F
    claims: dict[str, list[Claim]] = Field({}, description='Keyed "<node_id>.<attribute>"; separate reports of that value')
    resolution: dict[str, Resolution] = {}


class _UnitEntries(BaseModel):
    model_config = _F
    factors: dict[str, float | int] = Field({}, description="Unit -> factor to a common base, e.g. {kg: 1, tonne: 1000}")


class _FixedPointEntries(BaseModel):
    model_config = _F
    domains: dict[str, list[Any]] = Field({}, description='Keyed "<node_id>.<attribute>"; the only values it can take')


ReadAttributesBlock = _block("ReadAttributesBlock", dict[str, list[str]], {})
PropagationBlock = _block("PropagationBlock", _PropEntries, _PropEntries())
JustificationsBlock = _block("JustificationsBlock", _JustEntries, _JustEntries())
SatisfactionBlock = _block("SatisfactionBlock", SatisfactionEntries, SatisfactionEntries())
CombinationBlock = _block("CombinationBlock", _ComboEntries, _ComboEntries())
EvidenceBlock = _block("EvidenceBlock", _EvidenceEntries, _EvidenceEntries())
UnitsBlock = _block("UnitsBlock", _UnitEntries, _UnitEntries())
FixedPointBlock = _block("FixedPointBlock", _FixedPointEntries, _FixedPointEntries())
ReadAttributesBlock.model_rebuild(_types_namespace={"dict": dict, "list": list})


class TypedRules(BaseModel):
    model_config = _F
    read_attributes: ReadAttributesBlock = Field(default_factory=ReadAttributesBlock,
                                                  description='entries: {"<node_id>": [attributes any rule reads]}')
    propagation_rules: PropagationBlock = Field(default_factory=PropagationBlock,
                                                description="Copy/lookup an attribute along an influencing link")
    justifications: JustificationsBlock = Field(default_factory=JustificationsBlock,
                                                description="Conclusions true while at least one premise set is intact")
    satisfaction_functions: SatisfactionBlock = Field(default_factory=SatisfactionBlock,
                                                      description="Formula rules and status rules")
    combination_selection: CombinationBlock = Field(default_factory=CombinationBlock)
    evidence: EvidenceBlock = Field(default_factory=EvidenceBlock)
    units: UnitsBlock = Field(default_factory=UnitsBlock)
    fixed_point_semantics: FixedPointBlock = Field(default_factory=FixedPointBlock)


# ---------------------------------------------------------------------------
# Graph / Event mirrors with descriptions
# ---------------------------------------------------------------------------

class XNode(BaseModel):
    model_config = _F
    id: str = Field(description="The entity label exactly as written in the plan")
    type: str = "generic"
    attributes: dict[str, Any] = Field({}, description='Values as written; unknown -> {"$unknown": "<why>"}')
    state: str | None = Field(None, description='e.g. "unavailable" if the text says so')
    provenance: dict[str, Any] | None = None
    confidence: float | None = None


class XEdge(BaseModel):
    model_config = _F
    edge_id: str = Field(description="Any unique id, e.g. e1")
    source: str = Field(description="Node id")
    target: str = Field(description="Node id")
    type: EdgeType
    justification_id: str | None = None
    weight: float | None = None


class XGraph(BaseModel):
    model_config = _F
    nodes: list[XNode]
    edges: list[XEdge]


class XEdgeChange(BaseModel):
    model_config = _F
    edge_id: str | None = Field(None, description="Existing edge id (DELETE / RELATIONSHIP_CHANGE)")
    source: str | None = None
    target: str | None = None
    old_type: EdgeType | None = None
    new_type: EdgeType | None = Field(None, description="Omit if the text does not state the kind")
    candidate_types: list[EdgeType] | None = Field(None, description="Kinds the text allows when it does not state one")


class XEvent(BaseModel):
    model_config = _F
    operation: Operation
    target_kind: TargetKind
    target_id: str | None = Field(None, description="Node id (or edge id) the update names unambiguously; null if it names a shared name")
    target_ref: str | None = Field(None, description='The name used in the update when several entities share it, e.g. "Supplier A"')
    target_scope: str | None = Field(None, description="Node id the update restricts the name to (e.g. the plant it feeds); null if none stated")
    attribute: str | None = None
    new_value: Any | None = None
    edge_change: XEdgeChange | None = None
    new_node: XNode | None = None


class ExtractionOutput(BaseModel):
    """What the extractor returns. Do not apply the update."""

    model_config = _F
    graph: XGraph
    rules: TypedRules
    event: XEvent

    def to_method_input(self) -> MethodInputStructured:
        """Exactly the downstream input format; no repair or interpretation.

        v1.3: an explicit null in a typed field whose schema meaning is
        "not given" is represented downstream as an omitted key (see
        NULL_MEANS_ABSENT). Nothing is inferred; non-null values untouched."""
        m = self.model_copy(deep=True)
        _null_to_absent(m)
        d = m.model_dump(mode="json", exclude_unset=True)
        return MethodInputStructured.model_validate(d)


# Typed fields whose schema semantics define null as "not given". For the
# Ref/Src `default` (fallback) position only, an UnknownMarker means the same
# (v1.4); UnknownMarker is not accepted anywhere else in the formula grammar. Only these
# model fields are affected; free-form values (attributes, claim values,
# domains) are never touched.
NULL_MEANS_ABSENT: dict[type, frozenset[str]] = {
    Computation: frozenset({"when_linked", "role"}),
    Ref: frozenset({"default"}),
    Src: frozenset({"default"}),
    StatusFunction: frozenset({"human"}),
    Problem: frozenset({"human"}),
}


def _null_to_absent(obj: Any) -> None:
    if isinstance(obj, BaseModel):
        for f in NULL_MEANS_ABSENT.get(type(obj), ()):
            v = getattr(obj, f)
            if f in obj.model_fields_set and (v is None or isinstance(v, UnknownMarker)):
                obj.model_fields_set.discard(f)
        for name in type(obj).model_fields:
            _null_to_absent(getattr(obj, name))
    elif isinstance(obj, list):
        for v in obj:
            _null_to_absent(v)
    elif isinstance(obj, dict):
        for v in obj.values():
            _null_to_absent(v)
