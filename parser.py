def read_csv_file(filepath):
    # utf-8-sig strips a leading BOM (else it glues onto the first header name).
    # newline="" keeps raw \r\n / \r / \n intact so the parser can handle them itself.
    with open(filepath, encoding="utf-8-sig", newline="") as file:
        return file.read()

def parse_csv(text):
    rows = []              # finished rows, each a list of field strings
    row = []                # fields collected so far for the current row
    field = []              # characters collected so far for the current field
    inside_quotes = False   # True while between an opening and closing "
    index = 0

    # Walk char-by-char instead of splitting on "," / "\n" so a comma or newline
    # inside a quoted field (like "Smith, John") isn't mistaken for a separator.
    while index < len(text):
        character = text[index]

        if character == '"':
            if inside_quotes and index + 1 < len(text) and text[index + 1] == '"':
                # "" inside a quoted field is the CSV escape for a literal quote,
                # so add one " and skip past both quote characters.
                field.append('"')
                index += 1
            else:
                # A single " either opens a quoted field or closes the one we're in.
                inside_quotes = not inside_quotes
        elif character == "," and not inside_quotes:
            row.append("".join(field))
            field = []
        elif character in "\r\n" and not inside_quotes:
            # \r\n counts as one line break, so skip the \n if it follows a \r.
            if character == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
                index += 1

            if row or field:  # a truly blank line (no commas, no text) yields zero fields
                row.append("".join(field))
            rows.append(row)
            row = []
            field = []
        else:
            field.append(character)

        index += 1

    # No trailing newline means the loop above never flushed the last row.
    if field or row:
        row.append("".join(field))
        rows.append(row)

    if not rows:  # empty file: no header, so no records
        return []

    # First row is the header; every row after that is one record.
    # Blank lines produce a zero-field row, which we skip like csv.DictReader does.
    headers = rows[0]
    check_no_duplicate_headers(headers)
    return [row_to_dict(headers, values) for values in rows[1:] if values]

def check_no_duplicate_headers(headers):
    # Duplicate column names would silently overwrite each other's values in the
    # resulting dict, so fail fast instead of losing data quietly.
    seen = set()
    for index, header in enumerate(headers):
        if header in seen:
            raise ValueError(f"duplicate column name {header!r} at column {index}")
        seen.add(header)

def row_to_dict(headers, values):
    # zip() pairs headers with values 1-to-1, but real files can have "ragged"
    # rows (too few/many values), so patch those up to match csv.DictReader.
    record = dict(zip(headers, values))

    if len(values) < len(headers):
        # Too few values: zip() silently dropped the unmatched headers, so add
        # them back with None to show the column existed but was empty here.
        for header in headers[len(values):]:
            record[header] = None
    elif len(values) > len(headers):
        # Too many values: no header to attach them to, so keep them as a list
        # under the key None instead of losing them.
        record[None] = values[len(headers):]

    return record
