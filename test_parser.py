import pytest
from parser import read_csv_file, parse_csv

@pytest.mark.parametrize("filepath", [
    "data/sogne.dawa.csv",
    "data/employees.ascii.csv",
])

def test_row_and_column_counts(filepath):
    text = read_csv_file(filepath)
    lines = text.splitlines()
    data = parse_csv(text)

    assert len(data) == len(lines) - 1, "Row count does not match"
    assert len(data[0]) == len(lines[0].split(",")), "Column count does not match"