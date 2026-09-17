import pytest
from parser import read_csv_file, parse_csv

@pytest.mark.parametrize("filepath", [
    "data/sogne.dawa.csv",
    "data/employees.ascii.csv",
])

def test_row_and_column_counts(filepath):
    text = read_csv_file(filepath)
    lines = text.splitlines()
    headers = lines[0].split(",")
    data = parse_csv(text)

    assert len(data) == len(lines) - 1, (
        f"Expected {len(lines) - 1} rows, got {len(data)}"
    )

    for i, line in enumerate(lines[1:], start=2):
        count = len(line.split(","))
        assert count == len(headers), (
            f"Line {i}: expected {len(headers)} columns, got {count}"
        )


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