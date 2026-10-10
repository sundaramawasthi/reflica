"""Bounded execution of built-in analyses.

`run_describe`, `prepare_regress` and `run_regress` parse the CSV and run the
analysis in a separate process and kill that process if it exceeds
`config.analysis_timeout_s`. A wall-clock check
inside the same process cannot interrupt long pure-Python loops, so the
deadline is enforced from outside.

Only registered, built-in functions run here. Uploaded bytes are passed as
data; nothing in them is executed.
"""
from __future__ import annotations

import multiprocessing as mp
import time
from typing import Any, Callable

from .csv_adapter import CSVValidationError, parse_csv
from .models import (AnalysisInputError, Approval, DescribeResult, RegressPlan, RegressResult,
                     RegressSpec, ServiceConfig)


class AnalysisTimeout(RuntimeError):
    """The analysis was stopped because it exceeded the time limit."""

    code = "timeout"

    def __init__(self, timeout_s: float):
        super().__init__(f"Analysis exceeded the {timeout_s:g} s time limit and was stopped.")
        self.timeout_s = timeout_s


class AnalysisFailed(RuntimeError):
    """The analysis raised an unexpected error in the worker process."""

    code = "analysis_failed"


_CTX = mp.get_context("spawn")  # fresh interpreter: no inherited state or locks


def _worker(conn, fn: Callable[..., Any], args: tuple) -> None:
    try:
        conn.send(("ok", fn(*args)))
    except CSVValidationError as e:
        conn.send(("csv_error", (e.code, e.message, e.detail)))
    except AnalysisInputError as e:
        conn.send(("input_error", (e.code, e.message, e.detail)))
    except Exception as e:  # reported to the caller, never swallowed
        conn.send(("error", f"{type(e).__name__}: {e}"))
    finally:
        conn.close()


def run_with_timeout(fn: Callable[..., Any], args: tuple, timeout_s: float) -> Any:
    """Run a module-level function in a child process; kill it at the deadline.

    `fn` must be importable by name (spawn pickles it by reference).
    """
    parent, child = _CTX.Pipe(duplex=False)
    proc = _CTX.Process(target=_worker, args=(child, fn, args), daemon=True)
    deadline = time.monotonic() + timeout_s
    try:
        proc.start()
    except OSError as e:
        parent.close()
        child.close()
        raise AnalysisFailed(f"could not start the analysis worker: {e}") from None
    child.close()
    try:
        if not parent.poll(max(0.0, deadline - time.monotonic())):
            raise AnalysisTimeout(timeout_s)
        try:
            status, payload = parent.recv()
        except EOFError:
            raise AnalysisFailed(f"worker exited without a result (exit code {proc.exitcode})") from None
    finally:
        parent.close()
        if proc.is_alive():
            proc.terminate()
            proc.join(2)
            if proc.is_alive():
                proc.kill()
        proc.join()
    if status == "ok":
        return payload
    if status == "csv_error":
        raise CSVValidationError(*payload)
    if status == "input_error":
        raise AnalysisInputError(*payload)
    raise AnalysisFailed(payload)


def _describe_bytes(data: bytes, config: ServiceConfig) -> DescribeResult:
    from .analyses.describe import describe
    return describe(parse_csv(data, config), config)


def _check_size(data: bytes, config: ServiceConfig) -> None:
    if len(data) > config.max_upload_bytes:  # reject before starting a process
        raise CSVValidationError("too_large", "File exceeds the upload size limit.",
                                 {"bytes": len(data), "limit": config.max_upload_bytes})


def run_describe(data: bytes, config: ServiceConfig | None = None) -> DescribeResult:
    """Parse and describe CSV bytes within `config.analysis_timeout_s`.

    Raises CSVValidationError, AnalysisTimeout or AnalysisFailed.
    """
    config = config or ServiceConfig()
    _check_size(data, config)
    return run_with_timeout(_describe_bytes, (data, config), config.analysis_timeout_s)


def _prepare_regress_bytes(data: bytes, spec: RegressSpec, config: ServiceConfig) -> RegressPlan:
    from .analyses.regress import prepare
    return prepare(parse_csv(data, config), spec, config)


def _run_regress_bytes(data: bytes, plan: RegressPlan, approval: Approval,
                       config: ServiceConfig) -> RegressResult:
    from .analyses.regress import run
    return run(parse_csv(data, config), plan, approval, config)


def prepare_regress(data: bytes, spec: RegressSpec,
                    config: ServiceConfig | None = None) -> RegressPlan:
    """Validate a regression request and return the plan for the researcher to review.

    Nothing is fitted. Raises CSVValidationError, AnalysisInputError,
    AnalysisTimeout or AnalysisFailed.
    """
    config = config or ServiceConfig()
    _check_size(data, config)
    return run_with_timeout(_prepare_regress_bytes, (data, spec, config),
                            config.analysis_timeout_s)


def run_regress(data: bytes, plan: RegressPlan, approval: Approval,
                config: ServiceConfig | None = None) -> RegressResult:
    """Fit an approved regression plan on the same data it was prepared for.

    The approval is checked before any process starts; the worker then
    re-derives the plan from `data` and refuses if it differs. Raises
    CSVValidationError, AnalysisInputError (e.g. `approval_mismatch`,
    `plan_modified`, `plan_mismatch`), AnalysisTimeout or AnalysisFailed.
    """
    from .analyses.regress import check_approval
    config = config or ServiceConfig()
    check_approval(plan, approval)
    _check_size(data, config)
    return run_with_timeout(_run_regress_bytes, (data, plan, approval, config),
                            config.analysis_timeout_s)
