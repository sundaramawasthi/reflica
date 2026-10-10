"""CSV parsing and validation.

Uses only the standard library, so it works without the `service` extra.
Uploaded content is treated strictly as data: nothing in it is evaluated.

Rules (documented in NOTES.md):
- Size is checked on the raw bytes before decoding.
- Encoding must be UTF-8 (an optional BOM is removed); NUL bytes are rejected.
- The first non-blank row is the header. Names are trimmed; blank names and
  duplicates (case-insensitive) are rejected; the column limit is checked
  immediately. A header whose names all look numeric (e.g. `2020,2021`) is
  accepted and flagged for review.
- A line is blank only if it has no fields, or a single whitespace-only field
  when the header has more than one column. Blank lines are skipped. A row of
  empty fields such as `,` is a data row whose cells are missing.
- Every data row must have exactly as many fields as the header.
- A cell is missing if, after trimming, it is empty or one of MISSING_TOKENS
  (case-insensitive).
- A column is numeric only if every non-missing value matches NUMBER and is
  finite as a float (no inf/nan, thousands separators, underscores or hex).
  If any value is an integer literal with a leading zero (`007`), the column
  is text: such values are usually codes. Otherwise, if at least half the
  values are numbers the column is "mixed", else "text". A column with no
  non-missing values is "empty".
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
import re

from .models import Column, ColumnType, Dataset, ServiceConfig

MISSING_TOKENS = frozenset({"", "na", "n/a", "nan", "null", "none"})
NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
INTEGER = re.compile(r"[+-]?\d+")
LEADING_ZERO = re.compile(r"[+-]?0\d+")


class CSVValidationError(ValueError):
    """A rejected upload. `code` is stable; `message` is for people."""

    def __init__(self, code: str, message: str, detail: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail or {}


def is_number(cell: str) -> bool:
    c = cell.strip()
    return NUMBER.fullmatch(c) is not None and math.isfinite(float(c))


def _blank(record: list[str], width: int) -> bool:
    return not record or (len(record) == 1 and width != 1 and not record[0].strip())


def parse_csv(data: bytes, config: ServiceConfig | None = None) -> Dataset:
    """Parse and validate CSV bytes; raise CSVValidationError on any problem."""
    config = config or ServiceConfig()

    if len(data) > config.max_upload_bytes:
        raise CSVValidationError("too_large", "File exceeds the upload size limit.",
                                 {"bytes": len(data), "limit": config.max_upload_bytes})
    if not data.strip():
        raise CSVValidationError("empty_file", "File is empty.")
    if b"\x00" in data:
        raise CSVValidationError("nul_byte", "File contains NUL bytes; it may not be a text CSV.")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise CSVValidationError("invalid_utf8", "File is not valid UTF-8.",
                                 {"byte_offset": e.start}) from None

    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    header: list[str] | None = None
    cells: list[list[str | None]] = []  # column-major, missing → None
    seen_rows: set[bytes] = set()
    duplicates = rows = 0
    try:
        for record in reader:
            if header is None:
                if not record or all(not c.strip() for c in record):
                    continue
                header = [c.strip() for c in record]
                _check_header(header, config)
                cells = [[] for _ in header]
                continue
            if _blank(record, len(header)):
                continue
            if len(record) != len(header):
                raise CSVValidationError(
                    "malformed_row", "Row has a different number of fields than the header.",
                    {"line": reader.line_num, "expected": len(header), "found": len(record)})
            if rows >= config.max_rows:
                raise CSVValidationError("too_many_rows", "File exceeds the row limit.",
                                         {"limit": config.max_rows})
            stripped = [c.strip() for c in record]
            # NUL cannot occur in a cell (rejected above), so the joined key is unambiguous
            key = hashlib.blake2b("\x00".join(stripped).encode(), digest_size=16).digest()
            duplicates += key in seen_rows
            seen_rows.add(key)
            for col, c in zip(cells, stripped):
                col.append(None if c.lower() in MISSING_TOKENS else c)
            rows += 1
    except csv.Error as e:
        raise CSVValidationError("malformed_csv", f"CSV could not be parsed: {e}",
                                 {"line": reader.line_num}) from None

    if header is None:
        raise CSVValidationError("empty_file", "File contains no rows.")
    if not rows:
        raise CSVValidationError("no_data_rows", "File has a header but no data rows.")

    columns = tuple(_column(name, col) for name, col in zip(header, cells))
    return Dataset(sha256=hashlib.sha256(data).hexdigest(), row_count=rows, columns=columns,
                   duplicate_rows=duplicates, numeric_header=all(is_number(c) for c in header))


def _check_header(header: list[str], config: ServiceConfig) -> None:
    if len(header) > config.max_columns:
        raise CSVValidationError("too_many_columns", "File exceeds the column limit.",
                                 {"columns": len(header), "limit": config.max_columns})
    blank = [i for i, c in enumerate(header) if not c]
    if blank:
        raise CSVValidationError("empty_column_name", "Every column needs a name.",
                                 {"positions": blank})
    lowered: set[str] = set()
    dupes: list[str] = []
    for c in header:
        if c.lower() in lowered:
            dupes.append(c)
        lowered.add(c.lower())
    if dupes:
        raise CSVValidationError("duplicate_columns", "Column names must be unique (case-insensitive).",
                                 {"duplicates": dupes})


def _column(name: str, raw: list[str | None]) -> Column:
    values = tuple(raw)
    present = [v for v in values if v is not None]
    if not present:
        return Column(name=name, type="empty", values=values)
    if any(LEADING_ZERO.fullmatch(v) for v in present):
        return Column(name=name, type="text", values=values, leading_zeros=True)
    numeric = sum(is_number(v) for v in present)
    ctype: ColumnType
    if numeric == len(present):
        ctype = "numeric"
    elif 2 * numeric >= len(present):
        ctype = "mixed"
    else:
        ctype = "text"
    integer = ctype == "numeric" and all(INTEGER.fullmatch(v) for v in present)
    return Column(name=name, type=ctype, values=values, integer=integer)
