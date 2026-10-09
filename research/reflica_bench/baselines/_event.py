"""Naive event-target resolution shared by the classical baselines.

None of B3 / B4a / B4b represents referent ambiguity (Cat 7 P9): when an
event names its target by `target_ref`, they take the first matching node
(by id) among those that reach `target_scope`, if a scope is given.
"""

from __future__ import annotations

from ..schema import PROPAGATING_EDGE_TYPES


def resolve_target(graph, ev) -> str | None:
    if ev.target_ref is None:
        return ev.target_id
    cands = sorted(n.id for n in graph.nodes if n.attributes.get("name") == ev.target_ref)
    if ev.target_scope:
        def reaches(start: str) -> bool:
            seen, stack = set(), [start]
            while stack:
                n = stack.pop()
                if n == ev.target_scope:
                    return True
                if n in seen:
                    continue
                seen.add(n)
                stack.extend(e.target for e in graph.edges if e.source == n and e.type in PROPAGATING_EDGE_TYPES)
            return False
        cands = [c for c in cands if reaches(c)]
    return cands[0] if cands else None
