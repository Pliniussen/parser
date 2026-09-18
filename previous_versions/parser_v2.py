
def read_csv_file(filepath):
    with open(filepath, encoding="utf-8-sig", newline="") as file:
        return file.read()

class CSVParseError(ValueError):
    pass

def parse_csv(text):
    rows = []
    row = []
    field = []
    inside_quotes = False
    after_closing_quote = False
    field_started = False
    index = 0
    line = 1

    while index < len(text):
        character = text[index]

        if inside_quotes:
            if character == '"':
                if index + 1 < len(text) and text[index + 1] == '"':
                    field.append('"')
                    index += 1
                else:
                    inside_quotes = False
                    after_closing_quote = True
            else:
                field.append(character)
                if character == "\n":
                    line += 1
        elif after_closing_quote:
            if character == ",":
                row.append("".join(field))
                field = []
                after_closing_quote = False
                field_started = False
            elif character == "\r" or character == "\n":
                row.append("".join(field))
                if row != [""]:
                    rows.append(row)
                row = []
                field = []
                after_closing_quote = False
                field_started = False
                if character == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
                    index += 1
                line += 1
            elif character == " " or character == "\t":
                pass
            else:
                raise CSVParseError(
                    f"Unexpected character after closing quote on line {line}"
                )
        elif (character == " " or character == "\t") and not field_started:
            pass
        elif character == '"':
            if field_started:
                raise CSVParseError(f"Unexpected quote on line {line}")
            inside_quotes = True
            field_started = True
        elif character == ",":
            row.append("".join(field))
            field = []
            field_started = False
        elif character == "\r" or character == "\n":
            row.append("".join(field))
            if row != [""]:
                rows.append(row)
            row = []
            field = []
            field_started = False
            if character == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
                index += 1
            line += 1
        else:
            field.append(character)
            field_started = True

        index += 1

    if inside_quotes:
        raise CSVParseError(f"Unclosed quote on line {line}")

    if field_started or row:
        row.append("".join(field))
        rows.append(row)

    if not rows:
        return []

    headers = rows[0]
    if any(header == "" for header in headers):
        raise CSVParseError("Headers must not be empty")
    if len(set(headers)) != len(headers):
        raise CSVParseError("Headers must be unique")

    data = []
    expected_width = len(headers)
    for row_number, values in enumerate(rows[1:], start=2):
        if len(values) != expected_width:
            raise CSVParseError(
                f"Line {row_number} has {len(values)} fields; "
                f"expected {expected_width}"
            )
        data.append(dict(zip(headers, values)))

    return data

