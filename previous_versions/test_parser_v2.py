import csv
import io
import pytest
from previous_versions.parser_v2 import CSVParseError, read_csv_file, parse_csv

@pytest.mark.parametrize("filepath", [
    "data/sogne.dawa.csv",
    "data/employees.ascii.csv",
])

def test_fixture_matches_reference_parser(filepath):
    text = read_csv_file(filepath)
    expected = list(csv.DictReader(io.StringIO(text, newline="")))
    actual = parse_csv(text)

    assert actual == expected


def test_parse_csv_handles_commas_inside_quoted_fields():
    text = 'name,role\n"Ada Lovelace","Engineer, Analytical"\n'

    assert parse_csv(text) == [{
        "name": "Ada Lovelace",
        "role": "Engineer, Analytical",
    }]


def test_parse_csv_unescapes_doubled_quotes():
    text = 'name,note\n"Marcus ""GOAT"" Chen","Uses CSV ""safely"""\n'

    assert parse_csv(text) == [{
        "name": 'Marcus "GOAT" Chen',
        "note": 'Uses CSV "safely"',
    }]


def test_parse_csv_handles_crlf_and_newlines_inside_quoted_fields():
    text = 'name,note\r\n"Ada","first line\r\nsecond line"\r\n'

    assert parse_csv(text) == [{
        "name": "Ada",
        "note": "first line\r\nsecond line",
    }]


def test_parse_csv_handles_input_without_trailing_newline():
    text = 'name,role\n"Ada Lovelace","Engineer"'

    assert parse_csv(text) == [{
        "name": "Ada Lovelace",
        "role": "Engineer",
    }]


def test_parse_csv_handles_empty_and_header_only_input():
    assert parse_csv("") == []
    assert parse_csv("name,role\n") == []


def test_parse_csv_skips_blank_lines():
    text = "name,role\n\nAda,Engineer\n\n"

    assert parse_csv(text) == [{"name": "Ada", "role": "Engineer"}]


@pytest.mark.parametrize("text", [
    "name,role\nAda\n",
    "name,role\nAda,Engineer,Extra\n",
])
def test_parse_csv_rejects_rows_with_wrong_width(text):
    with pytest.raises(CSVParseError, match="expected 2"):
        parse_csv(text)


@pytest.mark.parametrize("column_count", [2, 3, 8])
def test_parse_csv_dynamically_validates_row_width(column_count):
    headers = [f"column_{index}" for index in range(column_count)]
    header_row = ",".join(headers)
    valid_row = ",".join(f"value_{index}" for index in range(column_count))

    assert parse_csv(f"{header_row}\n{valid_row}\n")

    missing_value = ",".join(
        f"value_{index}" for index in range(column_count - 1)
    )
    with pytest.raises(CSVParseError):
        parse_csv(f"{header_row}\n{missing_value}\n")

    extra_value = f"{valid_row},extra"
    with pytest.raises(CSVParseError):
        parse_csv(f"{header_row}\n{extra_value}\n")


@pytest.mark.parametrize("text", [
    'name,role\n"Ada,Engineer\n',
    'name,role\nAda" Lovelace,Engineer\n',
    'name,role\n"Ada" Lovelace,Engineer\n',
])
def test_parse_csv_rejects_malformed_quotes(text):
    with pytest.raises(CSVParseError):
        parse_csv(text)


@pytest.mark.parametrize("header", [",role", "name,", "name,name"])
def test_parse_csv_rejects_invalid_headers(header):
    with pytest.raises(CSVParseError):
        parse_csv(f"{header}\nAda,Engineer\n")


def test_read_csv_file_handles_utf8_bom(tmp_path):
    filepath = tmp_path / "bom.csv"
    filepath.write_bytes("name\nAda\n".encode("utf-8-sig"))

    assert parse_csv(read_csv_file(filepath)) == [{"name": "Ada"}]