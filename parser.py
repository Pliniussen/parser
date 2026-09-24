import json


def read_csv_file(filepath, encoding="utf-8-sig"):
    # Remove a leading UTF-8 BOM before parsing the first field.
    # Preserve line endings; parse_csv handles CR, LF, and CRLF explicitly.
    try:
        with open(filepath, encoding=encoding, newline="") as file:
            return file.read()
    except UnicodeDecodeError as error:
        # Turn the decoding failure into a parser-level error.
        raise ValueError(
            f"could not decode {filepath!r} using encoding {encoding!r}; "
            "pass the correct encoding to read_csv_file"
        ) from error
    except OSError as error:
        # Keep file-system failures consistent with decoding failures.
        raise ValueError(f"could not read {filepath!r}: {error}") from error


def parse_csv(text):
    # These states keep separators inside quoted fields from ending the field or row.
    rows = []  # Completed rows.
    row = []  # Fields in the current row.
    field = []  # Characters in the current field.
    inside_quotes = False  # Whether the current field is quoted.
    after_closing_quote = False  # A delimiter or line break must follow.
    field_started = False  # Distinguishes an empty field from no field.
    index = 0

    # Scan one character at a time so quoted commas and line breaks stay in field data.
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
                # In a quoted field, two quotes represent one literal quote.
                field.append('"')
                index += 1
            elif not inside_quotes and field:
                # Unquoted text cannot contain a quote.
                raise ValueError(
                    f"unexpected quote in unquoted field at row {len(rows) + 1}, "
                    f"column {len(row) + 1}"
                )
            else:
                # Toggle quoted state; opening a quote marks the field as present.
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
            # Treat CRLF as one line break.
            if character == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
                index += 1

            # Ignore one final blank line, but reject empty rows elsewhere.
            if not (row or field or field_started):
                if index + 1 == len(text):
                    break
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
        # Validate row width before pairing fields with header names.
        if len(values) != len(headers):
            raise ValueError(
                f"row {index} has {len(values)} columns but expected "
                f"{len(headers)}"
            )
        records.append(row_to_dict(headers, values))
    return records


def parse_csv_json(text):
    # Serialize validated records at the JSON boundary.
    return json.dumps(parse_csv(text), ensure_ascii=False)

def check_no_duplicate_headers(headers):
    # Reject duplicates before dict construction could overwrite a value.
    seen = set()
    for index, header in enumerate(headers):
        if header in seen:
            raise ValueError(f"duplicate column name {header!r} at column {index + 1}")
        seen.add(header)

def row_to_dict(headers, values):
    # zip() pairs headers with values 1-to-1 after row width has been validated.
    record = dict(zip(headers, values))
    return record