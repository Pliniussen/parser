import csv
import io
import json
import pytest
from parser import read_csv_file, parse_csv, parse_csv_json

# Compare fixture output with Python's reference CSV parser.
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


def test_parse_csv_json_returns_valid_json():
    text = 'name,note\n"Ada","Uses, CSV"\n'

    assert json.loads(parse_csv_json(text)) == [{
        "name": "Ada",
        "note": "Uses, CSV",
    }]


def test_parse_csv_json_preserves_unicode():
    assert json.loads(parse_csv_json("name\nSøren\n")) == [{"name": "Søren"}]


def test_parse_csv_unescapes_doubled_quotes():
    text = 'name,note\n"Marcus ""GOAT"" Chen","Uses CSV ""safely"""\n'

    assert parse_csv(text) == [{
        "name": 'Marcus "GOAT" Chen',
        "note": 'Uses CSV "safely"',
    }]


def test_parse_csv_rejects_quotes_inside_unquoted_fields():
    # A quote must open a field or escape a quote inside one.
    text = 'name,role\nAda", Lovelace,Engineer\n'

    with pytest.raises(ValueError):
        parse_csv(text)


def test_parse_csv_rejects_text_after_a_closing_quote():
    # A closed quoted field must be followed immediately by a comma or line break.
    text = 'name,role\n"Ada" Lovelace",Engineer\n'

    with pytest.raises(ValueError):
        parse_csv(text)


def test_parse_csv_rejects_whitespace_after_closing_quote():
    text = 'name,role\n"Ada" ,"Engineer"\t\n'

    with pytest.raises(ValueError, match=r"unexpected text after closing quote at row 2, column 1"):
        parse_csv(text)


def test_parse_csv_rejects_unterminated_quoted_fields():
    # An opening quote must be closed before EOF.
    text = 'name,role\n"Ada,Engineer\n'

    with pytest.raises(ValueError):
        parse_csv(text)


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


def test_parse_csv_rejects_rows_with_missing_columns():
    text = "name,role,age\nAda,Engineer\n"

    with pytest.raises(ValueError, match=r"row 2 has 2 columns but expected 3"):
        parse_csv(text)


def test_parse_csv_rejects_rows_with_extra_columns():
    text = "name,role\nAda,Engineer,Extra1,Extra2\n"

    with pytest.raises(ValueError, match=r"row 2 has 4 columns but expected 2"):
        parse_csv(text)


def test_parse_csv_preserves_empty_fields():
    text = "name,role,age\nAda,,34\n"

    assert parse_csv(text) == [{"name": "Ada", "role": "", "age": "34"}]


def test_parse_csv_handles_empty_quoted_fields():
    assert parse_csv('name,role\n"",""\n') == [{"name": "", "role": ""}]


def test_parse_csv_rejects_empty_header_names():
    with pytest.raises(ValueError, match=r"empty column name at row 1, column 1"):
        parse_csv(",role\nAda,Engineer\n")


def test_parse_csv_handles_empty_text():
    assert parse_csv("") == []


def test_parse_csv_handles_header_only_text():
    assert parse_csv("name,role\n") == []


def test_parse_csv_rejects_empty_rows():
    text = "name,role\nAda,Engineer\n\nBob,Manager\n"

    with pytest.raises(ValueError, match=r"empty row at row 3"):
        parse_csv(text)


def test_parse_csv_allows_one_trailing_newline():
    text = "name,role\nAda,Engineer\n"

    assert parse_csv(text) == [{"name": "Ada", "role": "Engineer"}]


def test_parse_csv_rejects_duplicate_header_names():
    # Duplicate names would overwrite values in the result dictionary.
    text = "name,role,name\nAda,Engineer,Lovelace\n"

    with pytest.raises(ValueError, match=r"duplicate column name 'name' at column 3"):
        parse_csv(text)


def test_parse_csv_handles_carriage_return_line_endings():
    text = "name,role\rAda,Engineer\r"

    assert parse_csv(text) == [{"name": "Ada", "role": "Engineer"}]


def test_read_csv_file_reports_decoding_errors(tmp_path):
    filepath = tmp_path / "invalid.csv"
    filepath.write_bytes(b"name\n\xff\n")

    with pytest.raises(ValueError, match=r"could not decode .* using encoding 'utf-8-sig'"):
        read_csv_file(filepath)


def test_read_csv_file_reports_file_system_errors(tmp_path):
    filepath = tmp_path / "missing.csv"

    with pytest.raises(ValueError, match=r"could not read .*missing\.csv"):
        read_csv_file(filepath)


def test_read_csv_file_accepts_explicit_encoding(tmp_path):
    filepath = tmp_path / "cp1252.csv"
    filepath.write_bytes("name\nSøren\n".encode("cp1252"))

    assert parse_csv(read_csv_file(filepath, encoding="cp1252")) == [{"name": "Søren"}]


@pytest.mark.parametrize("encoding", ["cp037", "cp500"])
def test_read_csv_file_accepts_ebcdic_encodings(tmp_path, encoding):
    filepath = tmp_path / f"{encoding}.csv"
    text = 'name,note\n"Ada Lovelace","Engineer, Analytical"\n'
    filepath.write_bytes(text.encode(encoding))

    assert parse_csv(read_csv_file(filepath, encoding=encoding)) == [{
        "name": "Ada Lovelace",
        "note": "Engineer, Analytical",
    }]

def test_parse_csv_allows_a_trailing_blank_line():
    text = "name,role\nAda,Engineer\n\n"
    assert parse_csv(text) == [{"name": "Ada", "role": "Engineer"}]