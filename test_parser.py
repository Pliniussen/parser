import csv
import io
import pytest
from parser import read_csv_file, parse_csv

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


def test_parse_csv_fills_missing_fields_with_none():
    text = "name,role,age\nAda,Engineer\n"

    assert parse_csv(text) == [{
        "name": "Ada",
        "role": "Engineer",
        "age": None,
    }]


def test_parse_csv_collects_extra_fields_under_none_key():
    text = "name,role\nAda,Engineer,Extra1,Extra2\n"

    assert parse_csv(text) == [{
        "name": "Ada",
        "role": "Engineer",
        None: ["Extra1", "Extra2"],
    }]