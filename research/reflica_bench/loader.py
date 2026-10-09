"""Scenario loader + enumerator."""

from __future__ import annotations

import json
from pathlib import Path

from .schema import Scenario


def load_scenario(path: str | Path) -> Scenario:
    """Load a scenario from JSON into the typed Pydantic model."""
    p = Path(path)
    with p.open("r") as f:
        data = json.load(f)
    return Scenario.model_validate(data)


def iter_scenarios(root: str | Path) -> list[Scenario]:
    """Load every *.json scenario in `root` (recursively), sorted by filename."""
    r = Path(root)
    files = sorted(r.rglob("*.json"))
    return [load_scenario(p) for p in files]


def scenarios_dir() -> Path:
    return Path(__file__).parent / "scenarios"


def cat1_dir() -> Path:
    return scenarios_dir() / "cat1"


def cat2_dir() -> Path:
    return scenarios_dir() / "cat2"


def cat3_dir() -> Path:
    return scenarios_dir() / "cat3"


def cat4_dir() -> Path:
    return scenarios_dir() / "cat4"


def cat5_dir() -> Path:
    return scenarios_dir() / "cat5"


def cat6_dir() -> Path:
    return scenarios_dir() / "cat6"


def cat7_dir() -> Path:
    return scenarios_dir() / "cat7"
