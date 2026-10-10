"""Builds the shared graph@1 example fixtures (used by the Python tests and, later, the app).

    python tests/service/data/graph/make_examples.py      (run from research/)

Offsets are computed from the text, so every quote is verbatim by construction.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from reflica_service.graph.contract import Edge, Graph, Node, Source, SourceSpan  # noqa: E402

TEXT = (
    "We hypothesise that higher soil moisture increases wheat yield in semi-arid plots. "
    "Our 2024 field trial measured grain yield in 40 plots. "
    "Plots irrigated weekly yielded 18% more grain than rain-fed plots. "
    "We assume that soil type is similar across plots. "
    "If the hypothesis holds, we plan to recommend weekly irrigation to farmers."
)


def span(quote: str, source: Source) -> SourceSpan:
    start = source.text.index(quote)
    return SourceSpan(source_id=source.id, start=start, end=start + len(quote), quote=quote)


def research_example() -> Graph:
    src = Source.from_text("s1", "Research problem (typed by the researcher)", TEXT)

    def quoted(id, kind, label, quote):
        return Node(id=id, kind=kind, label=label, basis="source_quoted", spans=(span(quote, src),))

    nodes = (
        quoted("h1", "hypothesis", "Higher soil moisture increases wheat yield in semi-arid plots",
               "higher soil moisture increases wheat yield in semi-arid plots"),
        quoted("m1", "method", "2024 field trial measuring grain yield in 40 plots",
               "Our 2024 field trial measured grain yield in 40 plots"),
        quoted("r1", "result", "Weekly irrigated plots yielded 18% more grain than rain-fed plots",
               "Plots irrigated weekly yielded 18% more grain than rain-fed plots"),
        quoted("a1", "assumption", "Soil type is similar across plots",
               "soil type is similar across plots"),
        quoted("t1", "task", "Recommend weekly irrigation to farmers",
               "recommend weekly irrigation to farmers"),
        Node(id="l1", kind="limitation", label="Only one growing season was measured",
             basis="llm_inferred"),
    )
    edges = (
        Edge(id="e1", source="m1", target="r1", type="derived_from", certainty="confirmed",
             basis="source_quoted", spans=(span("Our 2024 field trial measured grain yield", src),)),
        Edge(id="e2", source="r1", target="h1", type="supports", certainty="inferred",
             basis="llm_inferred"),
        Edge(id="e3", source="a1", target="r1", type="requires", certainty="inferred",
             basis="llm_inferred", note="Comparing plots assumes similar soil."),
        Edge(id="e4", source="h1", target="t1", type="enables", certainty="confirmed",
             basis="source_quoted",
             spans=(span("If the hypothesis holds, we plan to recommend", src),)),
        Edge(id="e5", source="l1", target="r1", type="informs", certainty="inferred",
             basis="llm_inferred"),
    )
    return Graph(sources=(src,), nodes=nodes, edges=edges)


EXAMPLES = {"research_example.json": research_example}

if __name__ == "__main__":
    here = Path(__file__).parent
    for name, build in EXAMPLES.items():
        (here / name).write_text(json.dumps(build().model_dump(mode="json"), indent=1) + "\n")
        print("wrote", name)
