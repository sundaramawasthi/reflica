"""Typed configuration, dataset and analysis-result models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

OPERATIONS: tuple[str, ...] = ("describe", "regress", "sweep")

_STRICT = ConfigDict(extra="forbid", frozen=True)


class ServiceConfig(BaseModel):
    """Service limits. Defaults are the v1 values recorded in PLATFORM_AUDIT.md."""

    model_config = _STRICT

    host: str = "127.0.0.1"
    port: int = Field(default=8765, ge=1, le=65535)
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, gt=0)
    max_rows: int = Field(default=100_000, gt=0)
    max_columns: int = Field(default=200, gt=0)
    max_correlation_columns: int = Field(default=50, ge=2)
    # total correlation work (pairs x rows); bounds run time independently of hardware
    max_correlation_work: int = Field(default=50_000_000, gt=0)
    # rows the exact per-pair correlation path may process in one analysis
    correlation_refine_budget_rows: int = Field(default=5_000_000, ge=0)
    max_sweep_points: int = Field(default=500, gt=0)
    analysis_timeout_s: float = Field(default=30.0, gt=0)
    operations: tuple[str, ...] = OPERATIONS


# ---------------------------------------------------------------------------
# Parsed dataset (internal; plain frozen dataclasses to keep memory and
# parse time low — these are never accepted from outside the service)
# ---------------------------------------------------------------------------

ColumnType = Literal["numeric", "mixed", "text", "empty"]


@dataclass(frozen=True, slots=True)
class Column:
    """One parsed column. Missing cells are None; others keep their trimmed text."""

    name: str
    type: ColumnType
    values: tuple[str | None, ...]
    integer: bool = False        # numeric and every value is a plain integer literal
    leading_zeros: bool = False  # text because integer-like values had leading zeros

    @property
    def numbers(self) -> tuple[float | None, ...]:
        """Float values for numeric columns; () otherwise. Computed on demand."""
        if self.type != "numeric":
            return ()
        return tuple(None if v is None else float(v) for v in self.values)


@dataclass(frozen=True, slots=True)
class Dataset:
    sha256: str
    row_count: int
    columns: tuple[Column, ...]
    duplicate_rows: int
    numeric_header: bool = False  # every column name looks like a number


# ---------------------------------------------------------------------------
# describe@1 result
# ---------------------------------------------------------------------------

IssueCode = Literal["constant_column", "all_missing", "high_missing",
                    "possible_id_column", "non_numeric_in_numeric", "duplicate_rows",
                    "precision_loss", "leading_zeros", "small_sample", "numeric_header",
                    "correlations_unrefined"]


class Issue(BaseModel):
    """A warning for review. The related statistics are still valid."""

    model_config = _STRICT

    code: IssueCode
    column: str | None = None  # None for dataset-level issues
    message: str


class NumericStats(BaseModel):
    model_config = _STRICT

    min: float
    max: float
    mean: float | None
    median: float | None
    sd: float | None  # sample SD (n - 1)
    # Statistics that could not be computed or represented, with the reason.
    # A statistic listed here is invalid, not merely uncertain.
    unavailable: dict[str, str] = Field(default_factory=dict)


class ColumnSummary(BaseModel):
    model_config = _STRICT

    name: str
    type: ColumnType
    integer: bool
    count: int
    missing: int
    missing_fraction: float
    unique: int  # exact for integer and text columns
    numeric: NumericStats | None = None


class Correlation(BaseModel):
    model_config = _STRICT

    x: str
    y: str
    method: Literal["pearson"] = "pearson"
    n: int  # rows where both values are present
    r: float | None
    reason: str | None = None  # why r is None (result invalid)
    warnings: tuple[str, ...] = ()  # r is valid but should be read with caution
    relationship: Literal["association"] = "association"


class CorrelationSkip(BaseModel):
    """Correlation work that was not done because of the configured limit."""

    model_config = _STRICT

    reason: Literal["column_limit", "work_limit"]
    limit: int  # number of numeric columns correlated
    computed_columns: tuple[str, ...]
    skipped_columns: tuple[str, ...]
    skipped_pairs: int


class DescribeResult(BaseModel):
    model_config = _STRICT

    operation: Literal["describe"] = "describe"
    version: Literal["1"] = "1"
    service_version: str
    dataset_sha256: str
    row_count: int
    column_count: int
    columns: tuple[ColumnSummary, ...]
    correlations: tuple[Correlation, ...]
    correlations_skipped: CorrelationSkip | None = None
    issues: tuple[Issue, ...]
    notes: tuple[str, ...]
