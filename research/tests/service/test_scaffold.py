"""Step 1 scaffold: imports, configuration and isolation from reflica_bench."""
from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest
from pydantic import ValidationError

import reflica_bench
import reflica_service
from reflica_service.models import OPERATIONS, ServiceConfig

SERVICE_DIR = Path(reflica_service.__file__).parent
BENCH_DIR = Path(reflica_bench.__file__).parent
OPTIONAL = {"fastapi", "uvicorn", "pandas", "numpy"}
MODULES = ["models", "store", "csv_adapter", "execution", "router", "app",
           "analyses", "analyses.describe", "analyses.regress", "analyses.sweep"]


def _top_level_imports(path: Path) -> set[str]:
    """Root package names imported at module level (not inside functions)."""
    names: set[str] = set()
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


def _all_imports(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    importlib.import_module(f"reflica_service.{name}")


def test_version():
    assert reflica_service.__version__ == "0.0.1"


def test_config_defaults():
    c = ServiceConfig()
    assert c.host == "127.0.0.1"
    assert c.max_upload_bytes == 10 * 1024 * 1024
    assert c.max_rows == 100_000
    assert c.max_sweep_points == 500
    assert c.analysis_timeout_s == 30.0
    assert c.operations == OPERATIONS == ("describe", "regress", "sweep")


def test_config_rejects_unknown_and_invalid_fields():
    with pytest.raises(ValidationError):
        ServiceConfig(debug=True)
    with pytest.raises(ValidationError):
        ServiceConfig(max_rows=0)


def test_config_is_immutable():
    with pytest.raises(ValidationError):
        ServiceConfig().max_rows = 5


@pytest.mark.parametrize("path", sorted(SERVICE_DIR.rglob("*.py")), ids=lambda p: p.name)
def test_optional_deps_not_imported_at_module_level(path):
    assert not (_top_level_imports(path) & OPTIONAL)


@pytest.mark.parametrize("path", sorted(SERVICE_DIR.rglob("*.py")), ids=lambda p: p.name)
def test_service_does_not_import_bench(path):
    assert "reflica_bench" not in _all_imports(path)


@pytest.mark.parametrize("path", sorted(BENCH_DIR.rglob("*.py")), ids=lambda p: p.name)
def test_bench_does_not_import_service(path):
    assert "reflica_service" not in _all_imports(path)


def test_only_the_runner_calls_analyses_directly():
    """Service code must reach analyses through execution.py, which enforces
    the time limit. Analyses may import each other; nothing else may."""
    allowed = {SERVICE_DIR / "execution.py"}
    for path in SERVICE_DIR.rglob("*.py"):
        if path in allowed or path.parent.name == "analyses":
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module and "analyses" in node.module:
                raise AssertionError(f"{path.name} imports {node.module}; use reflica_service.execution")
