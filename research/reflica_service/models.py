"""Typed configuration, dataset and analysis-result models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

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
    max_regress_predictors: int = Field(default=20, gt=0)
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


# ---------------------------------------------------------------------------
# regress@1: specification -> plan -> approval -> result
#
# The researcher states the question and chooses the target and predictors
# (RegressSpec). `prepare` validates them against the dataset and returns a
# RegressPlan describing exactly what would be fitted, identified by
# `plan_sha256`. Nothing is fitted until the researcher approves that plan
# (Approval naming the same hash); `run` re-derives the plan from the data and
# refuses if anything differs.
# ---------------------------------------------------------------------------


class AnalysisInputError(ValueError):
    """The request cannot be analysed as specified. `code` is stable; `message` is plain language."""

    def __init__(self, code: str, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail or {}


_Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class RegressSpec(BaseModel):
    """What the researcher asks for. Column names must match the CSV header exactly."""

    model_config = _STRICT

    target: str = Field(min_length=1)
    predictors: tuple[str, ...] = Field(min_length=1)
    intercept: bool = True
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.999)
    # True only if rows are in a meaningful order (e.g. time); enables the
    # independence check based on the Durbin-Watson statistic.
    row_order_meaningful: bool = False
    question: str | None = Field(default=None, max_length=2000)  # recorded, never interpreted


RegressWarningCode = Literal[
    "rows_dropped", "high_dropped_fraction", "few_observations_per_predictor",
    "small_residual_df", "binary_target", "precision_loss", "high_collinearity",
    "numerical_precision", "perfect_fit", "influential_rows", "high_leverage_rows",
    "outlier_rows", "heteroscedasticity", "non_normal_residuals", "nonlinearity",
    "autocorrelation"]


class RegressWarning(BaseModel):
    """Results are valid but need care for the stated reason."""

    model_config = _STRICT

    code: RegressWarningCode
    message: str
    columns: tuple[str, ...] = ()


class ColumnMissing(BaseModel):
    model_config = _STRICT

    column: str
    missing: int


class RegressPlan(BaseModel):
    """Exactly what would be run. Approve it by its `plan_sha256`."""

    model_config = _STRICT

    operation: Literal["regress"] = "regress"
    version: Literal["1"] = "1"
    service_version: str
    method: Literal["ols"] = "ols"
    dataset_sha256: str
    spec: RegressSpec
    formula: str
    summary: str
    rows_total: int
    rows_used: int
    rows_dropped: int
    missing_by_column: tuple[ColumnMissing, ...]
    parameters: int  # coefficients including the intercept
    df_resid: int
    diagnostics_planned: tuple[str, ...]
    warnings: tuple[RegressWarning, ...]
    plan_sha256: str


class Approval(BaseModel):
    """The researcher's approval of one specific plan."""

    model_config = _STRICT

    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    approved_by: _Text
    note: str | None = Field(default=None, max_length=2000)


class Coefficient(BaseModel):
    model_config = _STRICT

    term: str  # "(Intercept)" or a predictor name
    estimate: float
    std_error: float | None
    t: float | None
    p: float | None  # two-sided, for H0: coefficient = 0; not adjusted for multiple terms
    ci_low: float | None
    ci_high: float | None
    standardized: float | None = None  # estimate * sd(x) / sd(y); slopes with an intercept only
    vif: float | None = None


class FitStatistics(BaseModel):
    model_config = _STRICT

    n: int
    parameters: int
    df_model: int
    df_resid: int
    r_squared: float
    # "centred" with an intercept; "uncentred" (relative to zero) without one,
    # which is not comparable with a centred R^2
    r_squared_definition: Literal["centred", "uncentred"]
    adj_r_squared: float | None
    sigma: float  # residual standard error
    f_statistic: float | None
    f_df1: int
    f_df2: int
    f_p: float | None
    log_likelihood: float | None
    aic: float | None
    bic: float | None


class DiagnosticTest(BaseModel):
    model_config = _STRICT

    name: Literal["breusch_pagan", "jarque_bera", "reset"]
    checks: str
    statistic: float | None
    df: tuple[int, ...]
    p: float | None
    reason: str | None = None  # why statistic/p are None


class ResidualSummary(BaseModel):
    model_config = _STRICT

    min: float
    q1: float
    median: float
    q3: float
    max: float


class RowDiagnostics(BaseModel):
    """Per-row values for the rows used in the fit, in data order.

    `rows` are 1-based data-row numbers (the header is not counted). A None
    marks a value that is undefined for that row (e.g. leverage of 1).
    """

    model_config = _STRICT

    rows: tuple[int, ...]
    fitted: tuple[float, ...]
    residual: tuple[float, ...]
    leverage: tuple[float, ...]
    standardized_residual: tuple[float | None, ...]
    studentized_residual: tuple[float | None, ...]
    cooks_distance: tuple[float | None, ...]


class Diagnostics(BaseModel):
    model_config = _STRICT

    residuals: ResidualSummary
    durbin_watson: float | None
    tests: tuple[DiagnosticTest, ...]
    condition_number: float | None
    high_leverage_rows: tuple[int, ...]   # leverage > 2p/n
    influential_rows: tuple[int, ...]     # Cook's distance > 4/n, largest first
    outlier_rows: tuple[int, ...]         # |studentized residual| > 3


class PredictorRange(BaseModel):
    """Observed range of a predictor in the rows used; outside it is extrapolation."""

    model_config = _STRICT

    name: str
    min: float
    max: float
    mean: float


class Measured(BaseModel):
    """Values computed from the data. They depend on the assumptions listed separately."""

    model_config = _STRICT

    fit: FitStatistics
    coefficients: tuple[Coefficient, ...]
    covariance: tuple[tuple[float, ...], ...] | None  # of the coefficients, in their order
    diagnostics: Diagnostics
    predictor_ranges: tuple[PredictorRange, ...]
    rows: RowDiagnostics


class Assumption(BaseModel):
    model_config = _STRICT

    name: Literal["linearity", "independence", "constant_variance", "normal_errors",
                  "no_perfect_collinearity", "predictors_without_error",
                  "relevant_variables_included", "missing_data_ignorable"]
    statement: str
    check: Literal["not_contradicted", "contradicted", "not_checkable", "unavailable"]
    evidence: str


class Interpretation(BaseModel):
    """Plain-language reading generated from fixed templates. Associations only."""

    model_config = _STRICT

    statements: tuple[str, ...]
    next_steps: tuple[str, ...]  # suggestions for the researcher to decide on
    basis: str


class RunRecord(BaseModel):
    """Everything needed to reproduce the run."""

    model_config = _STRICT

    dataset_sha256: str
    plan_sha256: str
    spec: RegressSpec
    approved_by: str
    approval_note: str | None
    service_version: str
    analysis: Literal["regress@1"] = "regress@1"
    solver: str
    python_version: str
    numpy_version: str


class RegressResult(BaseModel):
    model_config = _STRICT

    operation: Literal["regress"] = "regress"
    version: Literal["1"] = "1"
    run: RunRecord
    measured: Measured
    assumptions: tuple[Assumption, ...]
    interpretation: Interpretation
    warnings: tuple[RegressWarning, ...]
    unavailable: dict[str, str]  # result name -> why it could not be computed
    limitations: tuple[str, ...]
