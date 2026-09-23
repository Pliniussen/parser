import json


def read_csv_file(filepath, encoding="utf-8-sig"):
    # utf-8-sig strips a leading BOM (else it glues onto the first header name).
    # newline="" keeps raw \r\n / \r / \n intact so the parser can handle them itself.
    try:
        with open(filepath, encoding=encoding, newline="") as file:
            return file.read()
    except UnicodeDecodeError as error:
        # Convert the low-level decoding failure into an actionable parser error.
        raise ValueError(
            f"could not decode {filepath!r} using encoding {encoding!r}; "
            "pass the correct encoding to read_csv_file"
        ) from error

def parse_csv(text):
    rows = []              # finished rows, each a list of field strings
    row = []                # fields collected so far for the current row
    field = []              # characters collected so far for the current field
    inside_quotes = False   # True while between an opening and closing "
    after_closing_quote = False  # True when only a delimiter or line break may follow
    field_started = False   # True when a field has been opened (even if empty)
    index = 0

    # Walk char-by-char instead of splitting on "," or "\n" so that a comma or newline
    # inside a quoted field (like "Smith, John") isn't mistaken for a separator.
    while index < len(text):
        character = text[index]

        # Once a quoted field closes, only its delimiter or line break may follow.
        if after_closing_quote and character not in ",\r\n":
            raise ValueError(
                f"unexpected text after closing quote at row {len(rows) + 1}, "
                f"column {len(row) + 1}"
            )

        if character == '"':
            if inside_quotes and index + 1 < len(text) and text[index + 1] == '"':
                # "" inside a quoted field is the CSV escape for a literal quote,
                # so add one " and skip past both quote characters.
                field.append('"')
                index += 1
            elif not inside_quotes and field:
                # A quote may open a field, but cannot appear inside unquoted text.
                raise ValueError(
                    f"unexpected quote in unquoted field at row {len(rows) + 1}, "
                    f"column {len(row) + 1}"
                )
            else:
                # A single " either opens a quoted field or closes the one we're in.
                inside_quotes = not inside_quotes
                after_closing_quote = not inside_quotes
                if inside_quotes:
                    field_started = True
        elif character == "," and not inside_quotes:
            row.append("".join(field))
            field = []
            field_started = False
            after_closing_quote = False
        elif character in "\r\n" and not inside_quotes:
            # \r\n counts as one line break, so skip the \n if it follows a \r.
            if character == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
                index += 1

            # A trailing newline follows a completed row; another newline means
            # that the input contains a completely empty row.
            if not (row or field or field_started):
                raise ValueError(f"empty row at row {len(rows) + 1}")

            row.append("".join(field))
            rows.append(row)
            row = []
            field = []
            field_started = False
            after_closing_quote = False
        else:
            field.append(character)

        index += 1

    # Reaching end-of-file while inside quotes leaves the current field incomplete.
    if inside_quotes:
        raise ValueError(
            f"unterminated quoted field at row {len(rows) + 1}, column {len(row) + 1}"
        )

    # No trailing newline means the loop above never flushed the last row.
    if field or row or field_started:  # field_started catches a trailing "" with no text
        row.append("".join(field))
        rows.append(row)

    if not rows:  # empty file: no header, so no records
        return []

    # First row is the header; every row after that is one record.
    headers = rows[0]
    for index, header in enumerate(headers):
        if header == "":
            raise ValueError(f"empty column name at row 1, column {index + 1}")

    check_no_duplicate_headers(headers)

    records = []

    for index, values in enumerate(rows[1:], start=2):
        # Empty fields are valid, but every row must still contain the same
        # number of columns as the header before it becomes a dictionary.
        if len(values) != len(headers):
            raise ValueError(
                f"row {index} has {len(values)} columns but expected "
                f"{len(headers)}"
            )
        records.append(row_to_dict(headers, values))
    return records


def parse_csv_json(text):
    # Serialize the validated Python records at the public JSON-output boundary.
    return json.dumps(parse_csv(text), ensure_ascii=False)

def check_no_duplicate_headers(headers):
    # Duplicate column names would silently overwrite each other's values in the
    # resulting dict, so fail fast instead of losing data quietly.
    seen = set()
    for index, header in enumerate(headers):
        if header in seen:
            raise ValueError(f"duplicate column name {header!r} at column {index + 1}")
        seen.add(header)

def row_to_dict(headers, values):
    # zip() pairs headers with values 1-to-1 after row width has been validated.
    record = dict(zip(headers, values))
    return record