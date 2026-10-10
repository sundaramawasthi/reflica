"""Write graph@1.schema.json next to this file (tests check it is current).

    python -m reflica_service.graph.export_schema
"""
import json
from pathlib import Path

from .contract import json_schema

PATH = Path(__file__).with_name("graph@1.schema.json")


def render() -> str:
    return json.dumps(json_schema(), indent=1, sort_keys=True) + "\n"


if __name__ == "__main__":
    PATH.write_text(render())
    print("wrote", PATH)
