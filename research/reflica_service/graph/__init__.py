"""graph@1 contract and impact analysis (preview -> fingerprint -> decision -> apply).

Pure Python + pydantic; no optional dependencies. See contract.py for the
meaning of kind, basis, certainty and edge direction.
"""
from .contract import VERSION, Graph, GraphError  # noqa: F401
