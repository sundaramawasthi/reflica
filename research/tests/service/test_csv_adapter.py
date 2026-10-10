"""CSV ingestion: valid files, every rejection path and limits."""
from __future__ import annotations

import hashlib

import pytest

from reflica_service.csv_adapter import CSVValidationError, parse_csv
from reflica_service.models import ServiceConfig


def code_of(data: bytes, config: ServiceConfig | None = None) -> str:
    with pytest.raises(CSVValidationError) as e:
        parse_csv(data, config)
    return e.value.code


def test_valid_csv_types_and_hash():
    data = b"id,temp,material,ratio\n1,300,steel,0.5\n2,310.5,iron,1e-1\n3,320,steel,-2\n"
    ds = parse_csv(data)
    assert ds.row_count == 3
    assert ds.sha256 == hashlib.sha256(data).hexdigest()
    types = {c.name: (c.type, c.integer) for c in ds.columns}
    assert types == {"id": ("numeric", True), "temp": ("numeric", False),
                     "material": ("text", False), "ratio": ("numeric", False)}
    assert ds.columns[1].numbers == (300.0, 310.5, 320.0)


def test_bom_crlf_quotes_and_blank_lines():
    data = '﻿name,"note, with comma"\r\n\r\na,"x ""q"""\r\nb,y\r\n'.encode()
    ds = parse_csv(data)
    assert [c.name for c in ds.columns] == ["name", "note, with comma"]
    assert ds.columns[1].values == ('x "q"', "y")
    assert ds.row_count == 2


def test_missing_tokens_and_whitespace():
    ds = parse_csv(b"a,b\n1, NA \n,n/a\nnull,NaN\n4,None\n5,2\n")
    a, b = ds.columns
    assert a.values == ("1", None, None, "4", "5")
    assert a.type == "numeric" and a.numbers == (1.0, None, None, 4.0, 5.0)
    assert b.values == (None, None, None, None, "2")


def test_all_missing_column_is_empty():
    ds = parse_csv(b"a,b\n1,\n2,NA\n")
    assert ds.columns[1].type == "empty"


def test_mixed_and_text_columns():
    ds = parse_csv(b"m,t\n1,x\n2,y\nabc,3\n4,z\n")
    assert ds.columns[0].type == "mixed" and ds.columns[0].numbers == ()
    assert ds.columns[1].type == "text"


@pytest.mark.parametrize("cell", ["inf", "-inf", "1e999", "1,000", "1_000", "0x10", "--1", "1.2.3"])
def test_non_plain_numbers_are_not_numeric(cell):
    ds = parse_csv(f'v\n"{cell}"\n'.encode())
    assert ds.columns[0].type != "numeric"


def test_duplicate_rows_counted():
    assert parse_csv(b"a,b\n1,2\n1,2\n 1 ,2\n3,4\n").duplicate_rows == 2


@pytest.mark.parametrize("data,code", [
    (b"", "empty_file"),
    (b"   \n\n", "empty_file"),
    (b"a,b\n", "no_data_rows"),
    (b"a,b\n\n\n", "no_data_rows"),
    (b"a,\x00b\n1,2\n", "nul_byte"),
    (b"a,b\n\xff\xfe,1\n", "invalid_utf8"),
    (b"a,,c\n1,2,3\n", "empty_column_name"),
    (b"a,b,A\n1,2,3\n", "duplicate_columns"),
    (b"a, a\n1,2\n", "duplicate_columns"),
    (b"a,b\n1,2,3\n", "malformed_row"),
    (b"a,b\n1\n", "malformed_row"),
    (b'a,b\n"1,2\n', "malformed_csv"),
    (b'a,b\n"x"y,2\n', "malformed_csv"),
])
def test_rejections(data, code):
    assert code_of(data) == code


def test_malformed_row_reports_line():
    with pytest.raises(CSVValidationError) as e:
        parse_csv(b"a,b\n1,2\n3\n")
    assert e.value.detail == {"line": 3, "expected": 2, "found": 1}


def test_size_limit_checked_before_decoding():
    cfg = ServiceConfig(max_upload_bytes=10)
    assert code_of(b"a,b\n\xff\xff\xff\xff\xff\xff\xff", cfg) == "too_large"
    parse_csv(b"a\n1\n", cfg)


def test_row_limit():
    cfg = ServiceConfig(max_rows=3)
    parse_csv(b"a\n1\n2\n3\n", cfg)
    assert code_of(b"a\n1\n2\n3\n4\n", cfg) == "too_many_rows"


def test_column_limit():
    cfg = ServiceConfig(max_columns=2)
    assert code_of(b"a,b,c\n1,2,3\n", cfg) == "too_many_columns"


def test_formula_like_cells_are_plain_text():
    ds = parse_csv(b'f\n=SUM(A1:A2)\n"@cmd"\n+1+1\n')
    assert ds.columns[0].type == "text"
    assert ds.columns[0].values == ("=SUM(A1:A2)", "@cmd", "+1+1")
