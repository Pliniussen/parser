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