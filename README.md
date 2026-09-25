# CSV Parser

A small, (almost) dependency-free CSV parser written from scratch in Python. It reads a
CSV-formatted text string, turns it into a list of Python dictionaries (one per
row, keyed by the header), and can optionally serialize that result to JSON.

The parser is intentionally **strict**: rather than guessing what malformed
input probably meant, it raises a descriptive `ValueError` (including the row
and column where applicable) and refuses to produce output.

## Why build this instead of using the `csv` module?

This project exists to get hands-on with the details that a library normally
hides: CSV quoting and escaping rules, encoding pitfalls, and what malformed
CSV looks like in practice. Python's built-in `csv` module is used only in the
test suite, as a reference implementation for cross-checking the hand-written
parser against the sample files.

## Requirements

- Python 3.10 or later (the current development environment uses Python 3.13.9)
- [pytest](https://pypi.org/project/pytest/) and
  [pytest-cov](https://pypi.org/project/pytest-cov/) for the test suite, pinned
  in `requirements.txt`

The parser itself has no third-party runtime dependencies. Install the test
dependencies into the project-local `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Project structure

```
.
├── parser.py         # the parser and its public functions
├── test_parser.py    # unit tests and reference-parser checks
├── requirements.txt  # pinned test dependencies
├── data/             # sample CSV fixtures used by the tests
│   ├── employees.ascii.csv
│   └── sogne.dawa.csv
└── README.md
```

## Running it

`parser.py` exposes three public functions:

- `read_csv_file(filepath, encoding="utf-8-sig")` reads a file from disk into
  a text string. The default encoding is UTF-8 with a leading BOM removed.
- `parse_csv(text)` parses a CSV text string into a `list[dict[str, str]]`.
- `parse_csv_json(text)` parses the CSV and returns the records as a JSON
  string.

Example:

```python
from parser import parse_csv, parse_csv_json, read_csv_file

text = read_csv_file("data/employees.ascii.csv")

records = parse_csv(text)
print(records[0])
# {'name': 'Marcus Chen', 'email': 'marcus.chen@example.com',
#  'department': 'Engineering', 'role': 'Senior Software Engineer',
#  'salary': '155000', 'start_date': '2019-03-15', 'office': 'San Francisco'}

json_output = parse_csv_json(text)
print(json_output)
```

Malformed input raises `ValueError` with a message describing what went wrong
and where:

```python
>>> parse_csv("name,role\nAda,Engineer,Extra\n")
Traceback (most recent call last):
    ...
ValueError: row 2 has 3 columns but expected 2
```

## Testing

Run the test suite with:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

To check code coverage:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=parser --cov-report=term-missing
```

The suite achieves 100% statement coverage of `parser.py`. It covers:

- correct parsing of quoted fields, embedded commas, embedded newlines, empty
  fields, and escaped (doubled) quotes
- CR, LF, and CRLF line endings
- explicit non-UTF-8 encodings, including legacy EBCDIC (`cp037`, `cp500`)
- decoding and file-system error reporting
- rejection of malformed input: unterminated quotes, text after a closing
  quote, quotes inside unquoted fields, empty rows, empty or duplicate header
  names, and rows with the wrong number of columns
- cross-checking parser output against Python's built-in `csv.DictReader` on
  the real sample files (`data/sogne.dawa.csv` and
  `data/employees.ascii.csv`)

## Architecture

The parser has two main layers, supported by two small validation helpers:

1. **`read_csv_file`** is a thin I/O wrapper around `open()`. It keeps raw line
   endings with `newline=""` and converts low-level decoding and file-system
   failures into descriptive `ValueError` exceptions, so callers only need to
   handle one exception type.
2. **`parse_csv`** is the core parser. It walks the input one character at a
   time instead of splitting on `,` or `\n`, because a comma or newline inside a
   quoted field (for example, `"Smith, John"`) is part of the field rather than
   a separator.

The state is tracked with a small set of flags:

- `inside_quotes` indicates that the cursor is between an opening and closing
  `"`.
- `after_closing_quote` indicates that only a delimiter or line break may
  legally follow a closed quoted field.
- `field_started` distinguishes an empty field from the absence of a field,
  which is needed to detect blank rows correctly.

After the character stream has been split into rows of raw field strings, a
second pass validates the header and each data row. Empty or duplicate header
names are rejected, every data row must have the same number of columns as the
header, and `row_to_dict` then pairs headers with values. Finally,
`parse_csv_json` calls `parse_csv` and serializes the validated records with
`json.dumps(ensure_ascii=False)`.

## Notes

- Duplicate column names are rejected rather than silently overwriting data.
- Empty fields are valid, but an empty column name is not.
- Empty input and header-only input produce an empty record list.
- A final line ending, and one blank line at the very end of the file, are
  accepted. A blank row in the middle of the file is treated as an error.

## To-do list
- A UML state diagram of the character-by-character state machine
- Make read_csv_file a native part of parse_csv and parse_csv_json
- Add encoding option to parser functions e.g. parse_csv(source, encoding=)