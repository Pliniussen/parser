
def read_csv_file(filepath):
    with open(filepath, encoding="utf-8") as file:
        return file.read()

def parse_csv(text):
    rows = []
    row = []
    field = []
    inside_quotes = False
    index = 0

    while index < len(text):
        character = text[index]

        if character == '"':
            if inside_quotes and index + 1 < len(text) and text[index + 1] == '"':
                field.append('"')
                index += 1
            else:
                inside_quotes = not inside_quotes
        elif character == "," and not inside_quotes:
            row.append("".join(field))
            field = []
        elif character in "\r\n" and not inside_quotes:
            if character == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
                index += 1

            row.append("".join(field))
            rows.append(row)
            row = []
            field = []
        else:
            field.append(character)

        index += 1

    if field or row:
        row.append("".join(field))
        rows.append(row)

    headers = rows[0]
    return [dict(zip(headers, values)) for values in rows[1:]]
